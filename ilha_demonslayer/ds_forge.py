# ds_forge - ZONA FORGE da Ilha 4 (DEMON SLAYER), onda 2b. build() substitui ds_blockout.forge.
# A FORJA e o heroi da ilha: ferraria ARTESANAL de katana no terraco T4 (80,2), no alto do muro de arrimo.
# Prefixo DS_Frg_ (dono "forge"), colecao 04_FORGE; peca movel VFX_DS_Wheel (12_VFX_HELPERS, pivot/axis/rpm ->
# tag IlhaMovel no export). Usa o kit (ds_kit, SO LEITURA) para a arquitetura - a forja fala a lingua da vila - e um
# kit PROPRIO de forja (fornalha, fole de caixa, bigorna, cocho, estantes, espadas, roda, aqueduto, pilao).
# ONDA 3c (agente 3c): os piloes e o eixo do moinho tambem sao pecas moveis (VFX_DS_Kine_A/_B bob+rate,
# VFX_DS_KineAxle girando com a roda) - ver mill(); o resto do modulo nao foi tocado.
#
# ANTI-COPIA da Forja do Ignis (lobby, PLANO 1.2): nada de alto-forno redondo, chapa rebitada, tubo ou coifa de ferro.
#   Aqui: boca em ARCO de tijolo refratario num bloco de alvenaria escura (o calor fica DENTRO da moldura), salao de
#   madeira escura + reboco com irimoya de telha e lanternim de fumaca, torre QUADRADA de pedra (ishigaki) + reboco
#   ocre com telhado-chapeu e chamine de pedra, roda d'agua japonesa (mizuguruma: aros de tabua, raios em pares, pas
#   em caçamba, cubo de madeira com cunhas - sem ferro) alimentada por calha de madeira sobre cavaletes, e PILOES de
#   madeira (kine) erguidos por cames no eixo. Shimenawa com shide sobre a boca (a forja e lugar consagrado).
#
# Partes (planta travada ds_layout.FORGE / FURNACE_MOUTH / CHIMNEY / WHEEL / FLUME / SPRING):
#   salao da fornalha (44 x 32) + bloco da boca (alvenaria, arco 10,5 x 10,9) + empena sobre a boca + lanternim
#   interior: hodo (fornalha de tijolo com brasas e chamas recuadas), coifa de barro, fuigo (fole de caixa), bigorna
#   baixa sobre toco com a lamina em brasa, cocho de tempera, caixa de carvao, katana-kake com espadas, estante de
#   parede, ferramentas
#   torre-chamine (base ishigaki 16, 2 pisos de reboco ocre com mokoshi, telhado-chapeu, chamine de pedra ate 152,2)
#   oficina-residencia (sobrado do kit, sacada, 2 noren vermelhos) e ala leste (polimento: frentes de loja)
#   moinho: eixo + 2 piloes (kine) + pilares + telheiro; poco da roda (muro de pedra, saida para o tailrace em
#   (96, 482) - o canal a partir dai e do ds_water); aqueduto da nascente (100, 552, 104) ate o topo da roda
#   patio de trabalho (lajes + sando no eixo), 2 katana-kake no patio, estacao de polimento, bigorna de pedra
#   escadas SubidaA / SubidaB + patamar-mirante (lajes, toro, banco); cercas e mureta na borda do terraco
#   patio do carvao: forno de carvao (sumigama) com telheiro, lenha empilhada, sacos de carvao (tawara)
# Luzes de dia (L_DSFrg_*, 6): fornalha (interior), boca, torre, oficina, ala leste, forno de carvao.
# Noite (L_DSProp_Lamp_Frg*): lanternas de parede da boca, postes do topo da subida, toro do patamar, poste do carvao.
# Colisao: so dos proprios predios/props (o chao, as escadas e as guardas sao do ds_col).
import math, os, sys, random, zlib
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import ds_lib as DL
import bpy, bmesh
from mathutils import Vector, Matrix
from ds_lib import MB, Frame, light, col_box, fm_lib
import ds_layout as L
import ds_kit as K
from ds_kit import sub, bx, bb, ext, lathe, strip, even, stone, rock_base, loft

T1, T3, T4 = L.T1, L.T3, L.T4
WD, WM, PL, PLK, RT, RR = K.WD, K.WM, K.PL, K.PLK, K.RT, K.RR
ST, STD, STP, IRON, LIT, PAPER, LGLOW = K.ST, K.STD, K.STP, K.IRON, K.LIT, K.PAPER, K.LGLOW
BRICK, SOOT = "Stone_DS_Brick", "Stone_DS_Soot"
STEEL, HAMON, BRASS = "Metal_DS_Steel", "Metal_DS_Hamon", "Metal_DS_Brass"
LACQ, STRAW, WATER = "Lacquer_DS_Black", "Rope_DS_Straw", "Water_DS_Trough"
FIRE, EMBER = "Fire_DS_Glow", "Ember_DS_Glow"
RED, INDIGO = "Cloth_DS_Red", "Cloth_DS_Indigo"
LAJE, DIRTD = "Stone_DS_Laje", "Dirt_DS_Dark"
OCHRE, ASH, CLAY = "Plaster_DS_Ochre", "Plaster_DS_Ash", "Plaster_DS_Clay"
WARM = (1.0, 0.62, 0.30)
FIREC = (1.0, 0.45, 0.14)
C = "04_FORGE"
W0 = Frame(0.0, 0.0, 0.0, 0.0)

# ------------------------------------------------------------------ medidas da forja (sobre a planta travada)
HX0, HY0, HX1, HY1 = L.FORGE["hall"][:4]          # salao -22..22 x 470..502
HW, HD = HX1 - HX0, HY1 - HY0                      # 44 x 32
HC = ((HX0 + HX1) / 2, (HY0 + HY1) / 2)            # (0, 486)
PLINTH = 1.2                                       # soco de pedra escura do salao
ZB = T4 + PLINTH                                   # topo do soco = base das paredes (81,4)
HH = 15.0                                          # topo da viga de beiral (keta) acima do soco -> 95,4
DOMA = T4 + 0.4                                    # chao de terra batida (doma) do salao
MX = L.FURNACE_MOUTH[0]                            # eixo da boca (x = 0)
BLK = (-10.0, 10.0)                                # bloco de alvenaria da boca (x)
BFY = HY0 - 3.0                                    # face do bloco (467): (0, 466) da rota fica FORA do tunel
BBY = HY0 + 1.4                                    # fundo do bloco (471,4)
BTOP = T4 + 19.6                                   # topo do bloco (99,8)
AW = 10.5                                          # vao livre da boca
AR0 = AW / 2                                       # raio do intradorso
AR1 = AR0 + 1.5                                    # raio do extradorso (aduelas de tijolo)
ASPR = DOMA + 5.6                                  # nascenca do arco (86,2) -> fecho em 91,45
TX, TY = L.CHIMNEY[0], L.CHIMNEY[1]                # torre (37, 493)
TB = 16.0                                          # base de pedra da torre
TS1, TS2 = 16.8, 17.2                              # pisos de reboco (beiral em +50)
WX, WY, WDIA, WWID = L.WHEEL                       # roda (92, 488), D 20, largura 4
WAZ = L.WHEEL_AXLE_Z
WR = WDIA / 2
KINE_RPM = 3.0                                     # = rpm do VFX_DS_Wheel (o ds_vfx confere)
KINE_LIFT = 1.6                                    # curso do pilao (bob do IlhaMovel)
KINE_CAM0 = math.radians(50.0)                     # angulo do 1o ressalto do came (modelado)


def _flume_pts():
    """os 3 pontos do marcador WATER_Flume (ds_core) + o bico sobre o topo da roda (extensao desta zona)"""
    f = L.FLUME
    zs = [L.SPRING[2] - 0.5, L.SPRING[2] - 1.6, WAZ + WR + 0.6]
    pts = [Vector((x, y, z)) for (x, y), z in zip(f, zs)]
    d = (pts[-1] - pts[-2])
    d.z = 0.0
    d.normalize()
    end = Vector((WX + 0.4, WY + 4.2, 0.0))           # bico: 4,2 ao norte do topo da roda (a agua cai na pa de cima)
    end.z = pts[-1].z - 0.2
    return pts + [end]


# ------------------------------------------------------------------ helpers
def stone(mb, F, x0, x1, z0, z1, yb, yf0, yf1, c=0.12, m=ST):
    """= ds_kit.stone (bloco com a face em y, chanfro c so na face) SEM a tampa de tras: aqui ela sempre encosta no
    miolo da alvenaria e nunca se ve (ONDA 6b: -2 tris por bloco no salao e no soco)"""
    yz = lambda z: yf0 + (yf1 - yf0) * (z - z0) / max(1e-6, z1 - z0)
    r0 = [(x0, yb, z0), (x1, yb, z0), (x1, yb, z1), (x0, yb, z1)]
    r1 = [(x0, yz(z0) - c, z0), (x1, yz(z0) - c, z0), (x1, yz(z1) - c, z1), (x0, yz(z1) - c, z1)]
    r2 = [(x0 + c, yz(z0 + c), z0 + c), (x1 - c, yz(z0 + c), z0 + c), (x1 - c, yz(z1 - c), z1 - c),
          (x0 + c, yz(z1 - c), z1 - c)]
    loft(mb, F, [r0, r1, r2], m, caps=(False, True))


def wbb(mb, x0, x1, y0, y1, z0, z1, m, bev=0.0):
    bb(mb, W0, x0, x1, y0, y1, z0, z1, m, bev)


def axes(F):
    o = F.p(0.0, 0.0, 0.0)
    return o, F.p(1.0, 0.0, 0.0) - o, F.p(0.0, 1.0, 0.0) - o, Vector((0.0, 0.0, 1.0))


def obox(mb, c, A, Cn, size, m, bev=0.0):
    """caixa orientada: centro c, eixo A (comprimento) e normal Cn (espessura); B = Cn x A"""
    A = Vector(A).normalized()
    Cn = Vector(Cn)
    Cn = (Cn - A * Cn.dot(A)).normalized()
    Bv = Cn.cross(A)
    M = Matrix((A, Bv, Cn)).transposed()
    mb.box(size, tuple(c), tuple(M.to_euler()), m, bev)


def rings_solid(mb, rings, m, cap0=True, cap1=True, tip=None, mats=None, closed=True):
    """solido por aneis (listas de Vector MUNDO, mesma contagem); tip = ponta em leque no fim; mats(i, j) -> material
    da face entre o anel i e i+1, segmento j (None = m). Normais orientadas para fora (solido fechado)."""
    bm = mb.bm
    V = [[bm.verts.new(tuple(p)) for p in r] for r in rings]
    k = len(V[0])
    fs, fm = [], []
    seg = k if closed else k - 1
    for i in range(len(V) - 1):
        for j in range(seg):
            j2 = (j + 1) % k
            try:
                fs.append(bm.faces.new((V[i][j], V[i][j2], V[i + 1][j2], V[i + 1][j])))
                fm.append(mats(i, j) if mats else None)
            except ValueError:
                pass
    if cap0:
        fs.append(bm.faces.new(list(reversed(V[0]))))
        fm.append(None)
    vt = None
    if tip is not None:
        vt = bm.verts.new(tuple(tip))
        for j in range(k):
            j2 = (j + 1) % k
            fs.append(bm.faces.new((V[-1][j], V[-1][j2], vt)))
            fm.append(mats(len(V) - 1, j) if mats else None)
    elif cap1:
        fs.append(bm.faces.new(V[-1]))
        fm.append(None)
    bmesh.ops.recalc_face_normals(bm, faces=fs)
    allv = [v for r in V for v in r] + ([vt] if vt is not None else [])
    if not (cap0 and (cap1 or tip is not None)):
        # ONDA 6b: casca ABERTA (sem fundo): confere que as normais ficaram para fora (o Roblox nao desenha o verso)
        cen = sum((v.co for v in allv), Vector()) / len(allv)
        s = 0.0
        for f in fs:
            f.normal_update()
            s += f.normal.dot(f.calc_center_median() - cen) * f.calc_area()
        if s < 0.0:
            for f in fs:
                f.normal_flip()
    mb._post(allv, m, None, 0, 1)
    for f, mm in zip(fs, fm):
        if mm and f.is_valid:
            f.material_index = mb._mi_for(mm)


def shell(mb, rings, m, mats=None):
    """superficie fechada em anel de aneis (ultimo liga no primeiro): casca com espessura (coifa, bacia)"""
    bm = mb.bm
    V = [[bm.verts.new(tuple(p)) for p in r] for r in rings]
    k = len(V[0])
    fs, fm = [], []
    n = len(V)
    for i in range(n):
        a, b = V[i], V[(i + 1) % n]
        for j in range(k):
            j2 = (j + 1) % k
            fs.append(bm.faces.new((a[j], a[j2], b[j2], b[j])))
            fm.append(mats(i) if mats else None)
    bmesh.ops.recalc_face_normals(bm, faces=fs)
    mb._post([v for r in V for v in r], m, None, 0, 1)
    for f, mm in zip(fs, fm):
        if mm and f.is_valid:
            f.material_index = mb._mi_for(mm)


def rect_ring(cx, cy, z, hx, hy):
    return [Vector((cx - hx, cy - hy, z)), Vector((cx + hx, cy - hy, z)), Vector((cx + hx, cy + hy, z)),
            Vector((cx - hx, cy + hy, z))]


def slab(mb, x0, y0, x1, y1, ztop, th=0.5, c=0.08, m=LAJE):
    """laje com chanfro no topo (18 tris). ONDA 6b: sem a face de baixo (assenta na terra/no leito: nunca se ve)"""
    r0 = rect_ring((x0 + x1) / 2, (y0 + y1) / 2, ztop - th, (x1 - x0) / 2, (y1 - y0) / 2)
    r1 = rect_ring((x0 + x1) / 2, (y0 + y1) / 2, ztop - c, (x1 - x0) / 2, (y1 - y0) / 2)
    r2 = rect_ring((x0 + x1) / 2, (y0 + y1) / 2, ztop, (x1 - x0) / 2 - c, (y1 - y0) / 2 - c)
    rings_solid(mb, [r0, r1, r2], m, cap0=False)
    PAVED.append([(x0, y0), (x1, y0), (x1, y1), (x0, y1)])


def ground_z(x, y, top=220.0):
    """cota do terreno (malhas DS_Ter* / colisao do piso) por raio vertical"""
    dg = bpy.context.evaluated_depsgraph_get()
    sc = bpy.context.scene
    o = Vector((x, y, top))
    d = Vector((0.0, 0.0, -1.0))
    for _ in range(16):
        hit, loc, nrm, idx, ob, mtx = sc.ray_cast(dg, o, d)
        if not hit:
            return None
        if ob.name.startswith(("DS_Ter", "COL_DS_Terrain")):
            return loc.z
        o = loc + d * 0.02
    return None


# ================================================================== ONDA 6b (6b-C, finesse): chao do patio
def _hh(*a):
    """hash estavel 0..1 (variacao dirigida, igual em todo build)"""
    s = "|".join(("%.3f" % v) if isinstance(v, float) else str(v) for v in a)
    h = zlib.crc32(s.encode("utf-8")) & 0xffffffff
    # o crc32 e LINEAR (chaves vizinhas dao valores vizinhos): finalizador do murmur3 espalha os bits
    h ^= h >> 16
    h = (h * 0x85EBCA6B) & 0xffffffff
    h ^= h >> 13
    h = (h * 0xC2B2AE35) & 0xffffffff
    h ^= h >> 16
    return h / 4294967296.0


def _pin(x, y, P):
    """ponto dentro do poligono P (x, y)"""
    ins = False
    n = len(P)
    for i in range(n):
        (x0, y0), (x1, y1) = P[i], P[(i + 1) % n]
        if (y0 > y) != (y1 > y) and x < x0 + (x1 - x0) * (y - y0) / (y1 - y0):
            ins = not ins
    return ins


PAVED = []          # pegadas (poligonos) do que ja esta pavimentado no patio: as manchas ficam fora delas


def flag(mb, poly, ztop, th=0.42, c=0.07, m=LAJE):
    """laje IRREGULAR (poligono convexo em (x, y)): chanfro no topo, sem fundo (assenta na terra). 5n-2 tris"""
    P = DL.ccw(poly)
    Pi = DL.offset_poly(P, -c)
    r0 = [Vector((x, y, ztop - th)) for x, y in P]
    r1 = [Vector((x, y, ztop - c)) for x, y in P]
    r2 = [Vector((x, y, ztop)) for x, y in Pi]
    rings_solid(mb, [r0, r1, r2], m, cap0=False)
    PAVED.append(P)


def flag_lattice(C, nu, nv, key, put, keep=None, merge=0.3, gap=0.2):
    """lajes sobre um reticulado deformado de cantos PARTILHADOS C[i][j] (i ao longo, j atravessado): juntas
    continuas e desencontradas como num ishidatami; merge = chance de juntar 2 celulas em i (laje maior);
    keep(i, j) -> False tira a celula (borda rasgada); put(poly, i, j) desenha a laje ja recuada de gap/2"""
    n = 0
    for j in range(nv):
        i = 0
        while i < nu:
            if keep and not keep(i, j):
                i += 1
                continue
            span = 2 if (i + 1 < nu and _hh(key, "m", i, j) < merge and (keep is None or keep(i + 1, j))) else 1
            poly = [C[i + k][j] for k in range(span + 1)] + [C[i + k][j + 1] for k in range(span, -1, -1)]
            poly = DL.offset_poly(DL.ccw(poly), -gap / 2)
            put(poly, i, j)
            n += 1
            i += span
    return n


def _smooth(pts, it=2):
    """Chaikin: curva a polilinha (a trilha nao quebra em quina)"""
    for _ in range(it):
        q = [pts[0]]
        for a, b in zip(pts, pts[1:]):
            q.append((0.75 * a[0] + 0.25 * b[0], 0.75 * a[1] + 0.25 * b[1]))
            q.append((0.25 * a[0] + 0.75 * b[0], 0.25 * a[1] + 0.75 * b[1]))
        q.append(pts[-1])
        pts = q
    return pts


def _along(pts, s):
    """ponto e tangente unitaria a distancia s ao longo da polilinha"""
    acc = 0.0
    for k, (a, b) in enumerate(zip(pts, pts[1:])):
        dx, dy = b[0] - a[0], b[1] - a[1]
        ln = math.hypot(dx, dy) or 1e-6
        if acc + ln >= s or k == len(pts) - 2:
            t = max(0.0, min(1.0, (s - acc) / ln))
            return (a[0] + dx * t, a[1] + dy * t), (dx / ln, dy / ln)
        acc += ln


def _plen(pts):
    return sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(pts, pts[1:]))


def trail_flags(mb, pts, hw, ztop, key, step=1.55, cols=2, m=LAJE, rag=0.3):
    """trilha de lajes irregulares (largura 2*hw) ao longo de pts: reticulado (ao longo x atravessado) com cantos
    sacudidos, bordas rasgadas (celulas de borda caem) e lajes maiores aqui e ali"""
    pts = _smooth(pts)
    Ln = _plen(pts)
    nu = max(2, int(round(Ln / step)))
    C = []
    for i in range(nu + 1):
        s = Ln * i / nu
        (x, y), (tx, ty) = _along(pts, s)
        nx, ny = -ty, tx
        row = []
        for j in range(cols + 1):
            v = -hw + 2 * hw * j / cols
            ju = (_hh(key, "u", i, j) - 0.5) * 0.42 * step * (0.0 if i in (0, nu) else 1.0)
            jv = (_hh(key, "v", i, j) - 0.5) * (0.5 if j in (0, cols) else 0.32) * (2 * hw / cols)
            row.append((x + tx * ju + nx * (v + jv), y + ty * ju + ny * (v + jv)))
        C.append(row)

    def keep(i, j):
        edge = j in (0, cols - 1)
        return not (edge and _hh(key, "k", i, j) < rag and 0 < i < nu - 1)

    def put(poly, i, j):
        flag(mb, poly, ztop + (_hh(key, "z", i, j) - 0.5) * 0.05, m=m)
    return flag_lattice(C, nu, cols, key, put, keep, merge=0.25)


def patch(mb, x, y, r, ztop, key, m, sx=1.0, rot=0.0, n=12, base=None, sat=True):
    """mancha de chao (terra pisada clara, cinza, respingo da tempera): placa fina IRREGULAR com chanfro, 0,12 acima
    da terra (nada coplanar). Fica FORA do que ja esta pavimentado (PAVED): encolhe ate caber ou some"""
    base = T4 if base is None else base
    for k in range(4):
        rr = r * (1.0 - 0.18 * k)
        P = DL.ccw(DL.blob_poly(x, y, rr, n, rng=random.Random(zlib.crc32(("%s" % key).encode("utf-8"))), amp=0.3,
                                rot=rot, sx=sx))
        big = DL.offset_poly(P, 0.25)
        bx0, bx1 = min(q[0] for q in big), max(q[0] for q in big)
        by0, by1 = min(q[1] for q in big), max(q[1] for q in big)
        near = [Q for Q in PAVED if min(q[0] for q in Q) < bx1 and max(q[0] for q in Q) > bx0 and
                min(q[1] for q in Q) < by1 and max(q[1] for q in Q) > by0]
        mids = [((a[0] + b[0]) / 2, (a[1] + b[1]) / 2) for a, b in zip(big, big[1:] + big[:1])]
        if not any(_pin(px, py, Q) for px, py in big + mids + [(x, y)] for Q in near) and \
                not any(_pin(qx, qy, big) for Q in near for qx, qy in Q):
            break
    else:
        print("ds_forge AVISO mancha %s sem lugar (encosta no pavimento)" % key)
        return False
    Pi = DL.offset_poly(P, -0.06)
    r0 = [Vector((px, py, base - 0.08)) for px, py in P]
    r1 = [Vector((px, py, ztop - 0.06)) for px, py in P]
    r2 = [Vector((px, py, ztop)) for px, py in Pi]
    rings_solid(mb, [r0, r1, r2], m, cap0=False)
    if sat:
        # satelite menor encostado (mesma cota e material: contorno organico, nada coplanar de outra cor)
        a = rot + math.tau * _hh(key, "sat")
        d = rr * (0.75 + 0.25 * _hh(key, "sd")) * (1.0 + 0.4 * (sx - 1.0))
        patch(mb, x + d * math.cos(a), y + d * math.sin(a), rr * 0.55, ztop, "%s_s" % key, m, 1.2, a, 10, base, False)
    return True


# ================================================================== ESPADAS (katana: lamina com shinogi, kissaki,
# hamon, habaki, tsuba, fuchi, tsuka com ito em losango sobre o same, kashira; saya de laca)
SW = dict(Lb=3.9, wb0=0.30, wb1=0.22, th=0.052, kl=0.42, sori=0.15)
UA = -1.86                                          # ponta do kashira (u)


def _sw_curve():
    Lb = SW["Lb"]
    um, hh = (UA + Lb) / 2, (Lb - UA) / 2
    return lambda u: SW["sori"] * (1.0 - ((u - um) / hh) ** 2)


def sword_half(u, kind):
    """meia-altura (lado do fio/costas) da espada em u: para apoiar no suporte"""
    Lb, wb0, wb1, kl = SW["Lb"], SW["wb0"], SW["wb1"], SW["kl"]
    if u < -0.36:
        return 0.17
    w = wb0 + (wb1 - wb0) * min(1.0, max(0.0, u) / (Lb - kl))
    return w / 2 + (0.08 if kind == "saya" else 0.0)


def sword(mb, o, U, V, W, kind="bare", ito=LACQ, tsuba=IRON, fit=BRASS, lod=0):
    """katana. o = base da lamina (habaki); U = para a ponta; V = lado do fio (ha); W = espessura.
    kind: 'bare' (lamina nua), 'saya' (embainhada), 'blank' (lamina em brasa, sem guarnicao)"""
    U, V, W = Vector(U).normalized(), Vector(V).normalized(), Vector(W).normalized()
    Lb, wb0, wb1, th, kl = SW["Lb"], SW["wb0"], SW["wb1"], SW["th"], SW["kl"]
    c = _sw_curve()
    P = lambda u, v, w: o + U * u + V * (c(u) + v) + W * w
    uy = Lb - kl
    wd = lambda u: wb0 + (wb1 - wb0) * min(1.0, max(0.0, u) / uy)

    def ring(u, vb, ve, f):
        w_ = ve - vb
        vs, vh = vb + 0.30 * w_, vb + 0.70 * w_
        t = th * f
        pts = [(vb - 0.022 * f, 0.0), (vb, 0.62 * t), (vs, t), (vh, 0.5 * t), (ve, 0.0), (vh, -0.5 * t), (vs, -t),
               (vb, -0.62 * t)]
        return [P(u, v, w) for v, w in pts]
    if kind in ("bare", "blank"):
        rings = []
        nb = 7
        for i in range(nb + 1):
            u = uy * i / nb
            rings.append(ring(u, -wd(u) / 2, wd(u) / 2, 1.0))
        wy = wd(uy)
        vby, vey = -wy / 2, wy / 2
        vtip = vby + 0.18 * wy
        for q in (0.3, 0.55, 0.75, 0.9):
            vb = vby + (vtip - vby) * q ** 3
            ve = vtip + (vey - vtip) * math.sqrt(max(0.0, 1.0 - q * q))
            rings.append(ring(uy + kl * q, vb, ve, 1.0 - q ** 1.6))
        tip = P(Lb, vtip, 0.0)
        if kind == "blank":
            rings_solid(mb, rings, EMBER, cap0=True, tip=tip)
            obox(mb, P(-0.8, 0.0, 0.0), U, W, (1.6, 0.2, 0.08), SOOT)          # espiga (nakago), mais fria
            return
        nk = nb + 1                                                    # primeiro anel do kissaki = nb + 1

        def mats(i, j):
            if i >= nb:                                                # kissaki: boshi (hira + fio claros)
                return HAMON if j in (2, 3, 4, 5) else None
            return HAMON if j in (3, 4) else None
        rings_solid(mb, rings, STEEL, cap0=True, tip=tip, mats=mats)
        # habaki (latao), mais grosso nas costas
        r0 = [P(-0.27, -wb0 / 2 - 0.045, th + 0.04), P(-0.27, wb0 / 2 + 0.03, th * 0.5 + 0.035),
              P(-0.27, wb0 / 2 + 0.03, -th * 0.5 - 0.035), P(-0.27, -wb0 / 2 - 0.045, -th - 0.04)]
        r1 = [P(0.04, -wb0 / 2 - 0.035, th + 0.025), P(0.04, wb0 / 2 + 0.015, th * 0.5 + 0.02),
              P(0.04, wb0 / 2 + 0.015, -th * 0.5 - 0.02), P(0.04, -wb0 / 2 - 0.035, -th - 0.025)]
        rings_solid(mb, [r0, r1], fit)
    else:                                                              # saya de laca
        rs = []
        for i in range(9):
            u = -0.02 + (Lb + 0.22) * i / 8
            hv = wd(min(u, uy)) / 2 + 0.075 - (0.03 * ((u - uy) / (Lb + 0.2 - uy)) if u > uy else 0.0)
            hw = th + 0.065
            rs.append(_rr8(P, u, hv, hw))
        rings_solid(mb, rs, LACQ)
        rings_solid(mb, [_rr8(P, -0.02, wb0 / 2 + 0.105, th + 0.09), _rr8(P, 0.12, wb0 / 2 + 0.1, th + 0.085)], LACQ)
        u = Lb + 0.2
        rings_solid(mb, [_rr8(P, u - 0.12, wb1 / 2 + 0.06, th + 0.07), _rr8(P, u + 0.04, wb1 / 2 + 0.045, th + 0.06)],
                    fit)                                               # kojiri
    # tsuba (mokko: 4 lobulos) + seppa
    pts = []
    for i in range(16):
        a = 2 * math.pi * i / 16
        r = 1.0 - 0.12 * abs(math.sin(2 * a)) ** 2
        pts.append((0.44 * r * math.cos(a), 0.37 * r * math.sin(a)))
    rings_solid(mb, [[P(-0.37, v, w) for v, w in pts], [P(-0.28, v, w) for v, w in pts]], tsuba)
    if lod == 0:
        for u0, u1 in ((-0.28, -0.25), (-0.40, -0.37)):
            rings_solid(mb, [_rr8(P, u0, 0.19, 0.095), _rr8(P, u1, 0.19, 0.095)], fit)
    # fuchi + tsuka (same branco) + ito em losango + kashira
    rings_solid(mb, [_rr8(P, -0.40, 0.18, 0.13), _rr8(P, -0.54, 0.175, 0.125)], fit)
    us = [-0.53, -0.95, -1.35, -1.74]
    hvs = [0.165, 0.158, 0.153, 0.157]
    hws = [0.115, 0.11, 0.106, 0.11]
    rings_solid(mb, [_rr8(P, u, hv, hw) for u, hv, hw in zip(us, hvs, hws)], PLK)
    n = 5 if lod == 0 else 4
    a0, a1 = -0.56, -1.72
    seg = (a1 - a0) / n
    for k in range(n):
        ua, ub = a0 + seg * k, a0 + seg * (k + 1)
        um = (ua + ub) / 2
        hv, hw = 0.16, 0.112
        for s in (1, -1):
            for sgn in (1, -1):
                d = U * (ub - ua) + V * (sgn * 2 * hv)
                obox(mb, P(um, 0.0, s * (hw + 0.012)), d, W * s, (d.length + 0.04, 0.085, 0.04), ito)
        if lod == 0:
            for sgn in (1, -1):
                obox(mb, P(ua, sgn * (hv + 0.015), 0.0), U, V * sgn, (0.1, 2 * hw + 0.07, 0.045), ito)
    rings_solid(mb, [_rr8(P, -1.72, 0.172, 0.122), _rr8(P, UA, 0.16, 0.112)], LACQ if tsuba != LACQ else IRON)


def _rr8(P, u, hv, hw):
    """anel retangulo arredondado (8 pontos) em u, meia-altura hv (fio/costas) e meia-espessura hw"""
    pts = [(hv, hw * 0.55), (hv * 0.72, hw), (-hv * 0.72, hw), (-hv, hw * 0.55), (-hv, -hw * 0.55), (-hv * 0.72, -hw),
           (hv * 0.72, -hw), (hv, -hw * 0.55)]
    return [P(u, v, w) for v, w in pts]


SWORD_SETS = {
    "patio_W": [("bare", INDIGO, IRON), ("bare", LACQ, BRASS), ("saya", RED, IRON)],
    "patio_E": [("bare", RED, BRASS), ("bare", LACQ, IRON), ("saya", INDIGO, BRASS)],
    "salao": [("bare", LACQ, IRON), ("bare", INDIGO, BRASS), ("bare", RED, IRON)],
}


def kake(mb, F, swords, H=2.9, lod=0, wall=False, z0=0.0):
    """suporte de katanas (katana-kake): 2 montantes com bracos em berco e labio, pes e travessa. F no chao (ou na
    parede, wall=True), +y = quem olha, espadas ao longo de x com o FIO PARA CIMA e o cabo a ESQUERDA de quem olha"""
    zs = [z0 + 0.95 + 0.72 * i for i in range(len(swords))]
    xs = (-1.25, 1.25)
    for x in xs:
        if not wall:
            bb(mb, F, x - 0.3, x + 0.3, -0.95, 0.95, 0.0, 0.3, WD, 0.05)
            bb(mb, F, x - 0.13, x + 0.13, -0.32, 0.22, 0.28, H, WD, 0.04)
        else:
            bb(mb, F, x - 0.16, x + 0.16, -0.32, 0.24, z0 + 0.4, z0 + H, WD, 0.04)
        bb(mb, F, x - 0.19, x + 0.19, -0.42, 0.34, z0 + H if wall else H, (z0 + H if wall else H) + 0.18, WD, 0.04)
        for za in zs:
            ext(mb, F, [(0.2, za - 0.2), (0.98, za - 0.2), (1.06, za + 0.24), (0.9, za + 0.27), (0.84, za + 0.02),
                        (0.2, za + 0.02)], "x", x - 0.1, x + 0.1, WD, 0.03)
    if not wall:
        bb(mb, F, -1.25, 1.25, -0.11, 0.11, 0.06, 0.26, WD)
    o_, ex, ey, ez = axes(F)
    U, V, Wv = -ex, ez, ey
    c = _sw_curve()
    for za, (kind, ito, tsuba) in zip(zs, swords):
        x0 = 0.7
        sup = [(x0 - 1.25, None), (x0 + 1.25, None)]          # u nos apoios (montante esquerdo = cabo)
        us = [-(1.25 - x0), x0 + 1.25]
        low = min(c(u) - sword_half(u, kind) for u in us)
        zc = za + 0.03 - low
        o = F.p(x0, 0.62, zc)
        sword(mb, o, U, V, Wv, kind, ito, tsuba, BRASS, lod)


# ================================================================== SALAO DA FORNALHA
def plinth_band(mb, F, W, D, h, gap_x=None):
    """soco do salao: pedra escura em blocos com face chanfrada e junta funda, so na faixa das paredes. F no centro,
    +y = frente; gap_x = (x0, x1) do vao na frente (sem soco)"""
    pat = (3.1, 2.4, 3.6, 2.7, 2.2, 3.3)
    faces = {"F": (0.0, W, D), "B": (math.pi, W, D), "R": (-math.pi / 2, D, W), "L": (math.pi / 2, D, W)}
    for key, (ang, Lf, Df) in faces.items():
        Ff = sub(F, 0.0, 0.0, 0.0, ang)
        Ff = sub(Ff, 0.0, Df / 2)
        k = {"F": 0, "B": 2, "R": 4, "L": 1}[key]
        x = -Lf / 2 - 0.3
        while x < Lf / 2 + 0.3 - 0.2:
            x2 = min(Lf / 2 + 0.3, x + pat[k % len(pat)])
            if Lf / 2 + 0.3 - x2 < 0.9:
                x2 = Lf / 2 + 0.3
            k += 1
            skip = key == "F" and gap_x and not (x2 <= gap_x[0] or x >= gap_x[1])
            if not skip:
                stone(mb, Ff, x + 0.04, x2 - 0.04, -0.1, h, -1.35, 0.3, 0.3, 0.1, STD)
            x = x2
        spans = [(-Lf / 2, Lf / 2)] if not (key == "F" and gap_x) else [(-Lf / 2, gap_x[0]), (gap_x[1], Lf / 2)]
        for a, b in spans:
            bb(mb, Ff, a, b, -1.6, -0.05, -0.1, h - 0.05, SOOT)


def hall_block(mb, mi):
    """bloco de alvenaria da boca: miolo escuro, faces de cantaria com junta funda, ARCO de tijolo refratario
    (aduelas + fecho), ombreiras e intradorso de tijolo em fiadas, impostas, fuligem acima do fecho"""
    x0, x1 = BLK
    zc = ASPR
    zk = ZB + HH - 0.3                                       # acima da keta o bloco recua ate y 475,2 (apoia a empena)
    yback = HY0 + 5.2
    # miolo (fundo escuro das juntas): pilares, faixa sobre o arco, rins (entre o intradorso e o retangulo), massa alta
    for a, b in ((x0 + 0.15, -AR0 - 0.6), (AR0 + 0.6, x1 - 0.15)):
        wbb(mb, a, b, BFY + 0.25, BBY, T4 - 0.1, BTOP - 0.3, SOOT)
    # ONDA 6b (item 41): o miolo termina 0,3 abaixo do topo (era 0,1: o topo dele ficava 0,06 sob o das pedras da
    # face, Stone_DS_Dark x Soot paralelos); a empena cobre o vao
    wbb(mb, -AR0 - 0.6, AR0 + 0.6, BFY + 0.25, BBY, zc + AR0 + 0.6, BTOP - 0.3, SOOT)
    n = 10
    for s in (-1, 1):
        r = AR0 + 0.6
        arc = [(s * r * math.cos(math.pi / 2 * i / n), zc + r * math.sin(math.pi / 2 * i / n)) for i in range(n + 1)]
        poly = [(s * r, zc + r), (0.0, zc + r)] + arc[::-1][1:-1] + [(s * r, zc)]
        poly = [(s * r, zc)] + [(s * r, zc + r), (0.0, zc + r)] + list(reversed(arc))[1:-1]
        if s > 0:
            poly = list(reversed(poly))
        ext(mb, W0, poly, "y", BFY + 0.3, BBY - 0.05, SOOT)
    wbb(mb, x0 + 0.15, x1 - 0.15, BBY - 0.05, yback, zk, BTOP - 0.3, SOOT)                    # massa alta que recua
    # cantaria da face sul (com o corte do extradorso) e das ilhargas
    FF = Frame(0.0, BFY + 0.25, 0.0, math.pi)              # face sul: +y local = sul; x local = -x mundo
    hc = (BTOP - T4) / 14.0
    pat = (2.6, 3.4, 2.2, 3.0, 2.8, 3.6, 2.4)

    def xr(z):
        if z <= zc:
            return AR1 + 0.06
        if z >= zc + AR1:
            return 0.0
        return math.sqrt(AR1 ** 2 - (z - zc) ** 2) + 0.06

    def soot(z0, xm):
        return z0 >= zc + AR1 - 1.2 and abs(xm) < 2.4 + (z0 - (zc + AR1 - 1.2)) * 0.55

    def rect(xa, xb, z0, z1, m):
        a, b = sorted((-xa, -xb))
        stone(mb, FF, a + 0.04, b - 0.04, z0 + 0.04, z1 - 0.04, -0.4, 0.25, 0.25, 0.1, m)
    for i in range(14):
        z0 = T4 + hc * i
        z1 = z0 + hc
        k = i * 3
        if z1 <= zc + 0.05:
            e0 = e1 = AR0 + 0.62
        else:
            e0, e1 = xr(z0), xr(z1)
        if e0 <= 0.0:                                        # acima do fecho: uma fiada inteira
            x = -10.25
            first = True
            while x < 10.25 - 0.25:
                x2 = min(10.25, x + pat[k % len(pat)] * (0.6 if first and i % 2 else 1.0))
                first = False
                if 10.25 - x2 < 0.8:
                    x2 = 10.25
                k += 1
                rect(x, x2, z0, z1, SOOT if soot(z0, (x + x2) / 2) else STD)
                x = x2
            continue
        for sgn in (1, -1):
            x = e0
            first = True
            while x < 10.25 - 0.25:
                x2 = min(10.25, x + pat[k % len(pat)] * (0.85 if i % 2 else 1.0))
                if 10.25 - x2 < 0.8:
                    x2 = 10.25
                k += 1
                m = SOOT if soot(z0, (x + x2) / 2) else STD
                if first and z1 > zc + 0.05:
                    poly = [(e0, z0 + 0.04), (x2 - 0.04, z0 + 0.04), (x2 - 0.04, z1 - 0.04), (max(e1, 0.04), z1 - 0.04)]
                    if sgn < 0:
                        poly = [(-u, v) for u, v in reversed(poly)]
                    ext(mb, W0, poly, "y", BFY, BFY + 0.65, m)
                elif sgn > 0:
                    rect(x, x2, z0, z1, m)
                else:
                    rect(-x2, -x, z0, z1, m)
                first = False
                x = x2
        # ilhargas (x = +-10,25): 2 blocos por fiada; acima da keta seguem ate o fundo da massa alta
    for i in range(14):
        z0 = T4 + hc * i
        z1 = z0 + hc
        yend = yback if z0 >= zk - 0.05 else BBY
        ysp = BFY + 0.7 + (3.1 if i % 2 else 4.3)
        cuts = [(BFY + 0.7, ysp), (ysp, yend)]
        if yend > BBY + 1.0:
            cuts = [(BFY + 0.7, ysp), (ysp, (ysp + yend) / 2), ((ysp + yend) / 2, yend)]
        for s in (-1, 1):
            Fs = Frame(s * x1, 0.0, 0.0, -s * math.pi / 2)
            for ya, yb in cuts:
                la, lb = sorted(((-ya if s > 0 else ya), (-yb if s > 0 else yb)))
                stone(mb, Fs, la + 0.04, lb - 0.04, z0 + 0.04, z1 - 0.04, -0.6, 0.25, 0.25, 0.1, STD)
    zkt = ZB + HH
    wbb(mb, x0 - 0.95, x1 + 0.95, BFY - 0.45, BFY + 0.4, zkt - 1.05, zkt, WD, 0.08)
    for s in (-1, 1):
        wbb(mb, s * x1 - 0.4, s * x1 + 0.4, BFY + 0.3, BBY + 0.6, zkt - 1.05, zkt, WD, 0.06)
        K.bracket(mb, Frame(s * (x1 - 1.2), BFY + 0.3, 0.0, math.pi), 0.0, 0.0, zkt - 1.05, 1.1, 0.5, 1.2)
    # ARCO: 13 aduelas de tijolo refratario + fecho saliente
    n = 13
    for i in range(n):
        a0 = math.pi * i / n + 0.012
        a1 = math.pi * (i + 1) / n - 0.012
        key = i == n // 2
        r1 = AR1 + (0.55 if key else (0.12 if i % 2 else 0.0))
        poly = [(AR0 * math.cos(a0), zc + AR0 * math.sin(a0)), (r1 * math.cos(a0), zc + r1 * math.sin(a0)),
                (r1 * math.cos(a1), zc + r1 * math.sin(a1)), (AR0 * math.cos(a1), zc + AR0 * math.sin(a1))]
        poly = list(reversed(poly))
        ext(mb, W0, poly, "y", BFY - (0.32 if key else 0.18), BFY + 1.1, BRICK if not key else STD, 0.04)
    for s in (-1, 1):                                        # impostas (pedra) na nascenca
        wbb(mb, s * (AR0 - 0.15), s * (AR1 + 0.55), BFY - 0.22, BFY + 1.2, zc - 0.55, zc + 0.02, STD, 0.05)
    # ombreiras: tijolo em fiadas alternadas (testa na face + junta funda) ate a nascenca
    nz = 8
    hz = (zc - 0.55 - DOMA) / nz
    for i in range(nz):
        z0 = DOMA + hz * i
        z1 = z0 + hz
        for s in (-1, 1):
            lw = 1.25 if i % 2 == 0 else 0.8
            wbb(mb, min(s * AR0, s * (AR0 + lw)), max(s * AR0, s * (AR0 + lw)), BFY - 0.12, BFY + 0.9,
                z0 + 0.03, z1 - 0.03, BRICK, 0.04)
            # parede do tunel: tijolos ao longo de y
            y = BFY + 0.9
            k = i % 2
            while y < BBY - 0.1:
                y2 = min(BBY, y + (1.9 if k % 2 == 0 else 1.3))
                wbb(mb, min(s * AR0, s * (AR0 + 0.6)), max(s * AR0, s * (AR0 + 0.6)), y + 0.03, y2 - 0.03,
                    z0 + 0.03, z1 - 0.03, BRICK)
                y = y2
                k += 1
    # intradorso (abobada do tunel): aneis de tijolo de ~1 com junta e amarracao alternada
    y = BFY + 1.1
    ring = 0
    while y < BBY - 0.05:
        y2 = min(BBY, y + 0.98)
        nn = 11
        off = 0.5 if ring % 2 else 0.0
        for i in range(nn + 1):
            a0 = math.pi * max(0.0, (i - off)) / nn + 0.01
            a1 = math.pi * min(1.0 * nn, (i + 1 - off)) / nn - 0.01
            if a1 <= a0 + 0.02:
                continue
            poly = [(AR0 * math.cos(a0), zc + AR0 * math.sin(a0)), ((AR0 + 0.55) * math.cos(a0), zc + (AR0 + 0.55) * math.sin(a0)),
                    ((AR0 + 0.55) * math.cos(a1), zc + (AR0 + 0.55) * math.sin(a1)), (AR0 * math.cos(a1), zc + AR0 * math.sin(a1))]
            mid = (a0 + a1) / 2
            m = SOOT if (abs(mid - math.pi / 2) < 0.55 and ring < 3) else BRICK
            ext(mb, W0, list(reversed(poly)), "y", y + 0.03, y2 - 0.03, m)
        y = y2
        ring += 1
    # soleira e piso do tunel (pedra), degrau de laje na frente
    slab(mb, -AR0 - 0.7, BFY - 1.1, AR0 + 0.7, BBY + 0.0, DOMA, 0.7, 0.08, ST)
    # SHIMENAWA com shide sobre a boca (corda de palha torcida pendurada em 2 cavilhas de madeira)
    zr = zc + AR1 + 1.3
    yr = BFY - 0.55
    for s in (-1, 1):
        wbb(mb, s * 7.6 - 0.22, s * 7.6 + 0.22, BFY - 0.75, BFY + 0.3, zr - 0.12, zr + 0.32, WD, 0.04)
    pts = []
    for i in range(17):
        t = i / 16
        x = -7.4 + 14.8 * t
        pts.append(Vector((x, yr, zr - 0.95 * math.sin(math.pi * t))))
    for k in range(2):                                       # 2 cabos torcidos
        prof = [(0.34 * math.cos(2 * math.pi * j / 6), 0.34 * math.sin(2 * math.pi * j / 6)) for j in range(6)]
        tw = [p + Vector((0.0, 0.21 * math.cos(i * 1.1 + k * math.pi), 0.21 * math.sin(i * 1.1 + k * math.pi)))
              for i, p in enumerate(pts)]
        mb.sweep(tw, prof, STRAW)
    for x in (-4.6, -1.6, 1.6, 4.6):                         # shide (papel em zigue-zague) e franjas de palha
        t = (x + 7.4) / 14.8
        z = zr - 0.95 * math.sin(math.pi * t) - 0.2
        zz = z
        for j in range(4):
            dx = 0.16 if j % 2 == 0 else -0.16
            wbb(mb, x - 0.28 + dx, x + 0.28 + dx, yr - 0.05, yr + 0.03, zz - 0.5, zz, PLK)
            zz -= 0.5
        wbb(mb, x - 0.1, x + 0.1, yr - 0.02, yr + 0.08, z - 2.3, z, STRAW)
    # lanternas de parede ladeando a boca (luz SO a noite)
    for s, nm in ((-1, "L"), (1, "R")):
        K.lantern_wall(mi, Frame(s * 8.4, BFY, ASPR + 1.6, math.pi), "L_DSProp_Lamp_FrgMouth_%s" % nm, 34.0, 1.2)


def hall(mb, mi):
    """salao: soco, cantos, fachadas do kit (frente em 2 vaos laterais + bloco da boca), irimoya, empena da boca,
    lanternim de fumaca"""
    F = Frame(HC[0], HC[1], T4, math.pi)                     # +y local = sul (frente para a clareira)
    plinth_band(mb, F, HW, HD, PLINTH, gap_x=BLK)
    Fb = sub(F, z=PLINTH)
    K.corner_posts(mb, Fb, HW, HD, 0.7, HH - 1.0)
    # frente: 2 trechos de 12 (oeste/leste do bloco), janelas koshi acesas ladeando a boca
    for s, bays in ((1, ["plain", "koshi"]), (-1, ["koshi", "plain"])):
        cx = s * (BLK[1] + (HW / 2 - BLK[1]) / 2)
        Ff = sub(Fb, cx, HD / 2)
        K.facade(mb, Ff, HW / 2 - BLK[1], HH, bays, True, plaster=CLAY, lit=True)
        xp = s * (BLK[1] + 0.45)
        bb(mb, Fb, xp - 0.45, xp + 0.45, HD / 2 - 0.9, HD / 2 + 0.02, 0.7, HH - 1.0, WD, K.B)
    # laterais e fundos
    K.facade(mb, sub(Fb, HW / 2, 0.0, 0.0, -math.pi / 2), HD, HH, ["plain", "koshi", "plaster", "koshi", "plain"],
             False, plaster=CLAY, lit=True)
    K.facade(mb, sub(Fb, -HW / 2, 0.0, 0.0, math.pi / 2), HD, HH, ["plain", "koshi", "itado", "koshi", "plain"],
             False, plaster=CLAY, lit=True)
    K.facade(mb, sub(Fb, 0.0, -HD / 2, 0.0, math.pi), HW, HH, ["plain", "koshi", "plaster", "plaster", "koshi", "plain"],
             True, plaster=CLAY, lit=False, lod=1)
    r = K.roof_hip(mb, Fb, HW, HD, HH, "irimoya", pitch=0.58, over=3.6, gable=0.64, g_over=1.5, lift=1.0, tv=0.5,
                   gable_m=WD, gable_style="board", back_lod=1)
    zr = Fb.o.z + r["zr"]
    # empena sobre a boca (kirizuma de cumeeira norte-sul, morre dentro do telhado principal)
    Wg = 486.5 - 1.8 - BFY                                 # o fim de tras morre sob a cumeeira
    FG = Frame(0.0, BFY + Wg / 2, BTOP, -math.pi / 2)
    K.roof_gable(mb, FG, Wg, BLK[1] - BLK[0] - 0.3, 0.0, pitch=0.62, over=1.7, g_over=1.8, lift=0.45, tv=0.45,
                 gable_m=CLAY, gable_style="timber", lod=1)
    # lanternim de fumaca (kemuri-dashi) na cumeeira: ripas verticais sobre fundo de fuligem + kirizuma proprio
    lx, ly = 7.0, 1.9
    for s in (-1, 1):
        ys = HC[1] + s * ly
        wbb(mb, -lx, lx, ys - 0.25, ys + 0.25, zr - 1.9, zr - 1.0, WD, 0.05)               # frechal sobre o telhado
        wbb(mb, -lx + 0.3, lx - 0.3, ys - s * 0.65 - 0.1, ys - s * 0.65 + 0.1, zr - 1.2, zr + 2.3, SOOT)
        for x in even(-lx + 0.4, lx - 0.4, 0.75):
            wbb(mb, x - 0.16, x + 0.16, ys - 0.14, ys + 0.14, zr - 1.0, zr + 2.4, WD)
        wbb(mb, -lx, lx, ys - 0.25, ys + 0.25, zr + 2.3, zr + 2.75, WD, 0.04)
    for s in (-1, 1):
        wbb(mb, s * lx - 0.3, s * lx + 0.3, HC[1] - ly - 0.25, HC[1] + ly + 0.25, zr - 1.9, zr + 2.75, WD, 0.04)
        wbb(mb, s * (lx - 0.35) - 0.15, s * (lx - 0.35) + 0.15, HC[1] - ly + 0.3, HC[1] + ly - 0.3, zr - 1.0, zr + 2.3, PL)
    K.roof_gable(mb, Frame(0.0, HC[1], zr + 2.75, 0.0), 2 * lx + 0.6, 2 * ly + 0.5, 0.0, pitch=0.6, over=1.3, g_over=0.9,
                 lift=0.35, tv=0.35, lod=1, gable_m=WD, gable_style="board", rafters=False, ridge_w=1.4, oni_s=0.7)
    hall_block(mb, mi)
    return zr


def hall_interior(mi, mw, zr):
    """doma, hodo (fornalha de tijolo com brasas e chamas recuadas), coifa de barro, fuigo, bigorna sobre toco com a
    lamina em brasa, cocho de tempera, carvao, katana-kake, estante de parede, ferramentas, pilares e vigas"""
    # doma (terra batida) e pilares/vigas aparentes
    wbb(mw, HX0 + 0.9, HX1 - 0.9, BBY - 0.05, HY1 - 0.9, T4 - 0.2, DOMA, DIRTD)
    for x in (-11.0, 11.0):
        K.post(mw, W0, x, 482.0, DOMA, ZB + HH - 1.0, 1.1, True)
        wbb(mw, x - 0.55, x + 0.55, HY0 + 0.5, HY1 - 0.5, ZB + HH - 1.9, ZB + HH - 0.7, WD, 0.06)
    wbb(mw, HX0 + 0.5, HX1 - 0.5, 481.4, 482.6, ZB + HH - 1.6, ZB + HH - 0.2, WD, 0.06)
    # HODO: corpo de tijolo, borda de pedra escura em moldura, cova com brasas, carvao e chamas; boca de cinzas acesa
    hx0, hx1, hy0, hy1 = -4.2, 4.2, 490.6, 498.6
    zt = DOMA + 2.6
    wbb(mi, hx0, hx1, hy0, hy1, DOMA - 0.1, zt - 0.8, BRICK, 0.06)
    px0, px1, py0, py1 = -2.3, 2.3, 492.2, 497.0
    for a, b, c_, d in ((hx0, px0, hy0, hy1), (px1, hx1, hy0, hy1), (px0, px1, hy0, py0), (px0, px1, py1, hy1)):
        wbb(mi, a, b, c_, d, zt - 0.85, zt, BRICK)
    for a, b, c_, d in ((hx0 - 0.15, px0 - 0.05, hy0 - 0.15, hy1 + 0.15), (px1 + 0.05, hx1 + 0.15, hy0 - 0.15, hy1 + 0.15),
                        (px0 - 0.05, px1 + 0.05, hy0 - 0.15, py0 - 0.05), (px0 - 0.05, px1 + 0.05, py1 + 0.05, hy1 + 0.15)):
        wbb(mi, a, b, c_, d, zt - 0.05, zt + 0.3, STD, 0.06)
    wbb(mi, px0 + 0.05, px1 - 0.05, py0 + 0.05, py1 - 0.05, zt - 0.9, zt - 0.45, EMBER)        # leito de brasas
    rng = random.Random(311)
    for i in range(16):                                                                        # carvao sobre as brasas
        cx, cy = rng.uniform(px0 + 0.4, px1 - 0.4), rng.uniform(py0 + 0.4, py1 - 0.4)
        s = rng.uniform(0.35, 0.6)
        mi.box((s, s * rng.uniform(0.7, 1.2), s * 0.7), (cx, cy, zt - 0.45 + s * 0.2),
               (rng.uniform(-0.4, 0.4), rng.uniform(-0.4, 0.4), rng.uniform(0, 3)), SOOT, 0.0)
    for cx, cy, h, a in ((-0.7, 494.2, 1.9, 0.2), (0.6, 495.0, 1.5, -0.3), (0.0, 493.4, 1.2, 0.5), (1.3, 493.9, 1.0, 1.0)):
        z0 = zt - 0.5
        r0 = rect_ring(cx, cy, z0, 0.42, 0.3)
        r1 = rect_ring(cx + 0.12, cy - 0.05, z0 + h * 0.45, 0.3, 0.2)
        r2 = rect_ring(cx - 0.05, cy + 0.05, z0 + h * 0.8, 0.13, 0.09)
        rings_solid(mi, [r0, r1, r2], FIRE, tip=Vector((cx + 0.12, cy, z0 + h)))
    # boca de cinzas na frente do hodo: arco pequeno em tijolo com fundo aceso recuado
    wbb(mi, -1.1, 1.1, hy0 - 0.05, hy0 + 0.6, DOMA + 0.05, DOMA + 1.15, SOOT)
    wbb(mi, -0.95, 0.95, hy0 + 0.55, hy0 + 0.72, DOMA + 0.1, DOMA + 1.05, EMBER)
    for s in (-1, 1):
        wbb(mi, s * 1.1 - 0.35, s * 1.1 + 0.35, hy0 - 0.18, hy0 + 0.2, DOMA - 0.05, DOMA + 1.45, BRICK, 0.04)
    wbb(mi, -1.5, 1.5, hy0 - 0.18, hy0 + 0.2, DOMA + 1.4, DOMA + 1.85, BRICK, 0.04)
    # peito de chamine (tijolo) atras do hodo ate a coifa
    wbb(mi, -5.0, 5.0, 498.4, 499.9, DOMA - 0.1, DOMA + 8.2, BRICK, 0.05)
    # COIFA de barro (casca com espessura) + duto ate o lanternim
    zb_, zt_ = DOMA + 7.9, ZB + HH + 0.1
    o0 = rect_ring(0.0, 494.3, zb_, 5.7, 5.5)
    o1 = rect_ring(0.0, 494.9, zt_, 2.5, 2.4)
    i1 = rect_ring(0.0, 494.9, zt_, 2.15, 2.05)
    i0 = rect_ring(0.0, 494.3, zb_, 5.35, 5.15)
    shell(mi, [o0, o1, i1, i0], CLAY, mats=lambda i: SOOT if i in (2, 3) else None)
    for s in (-1, 1):                                                   # moldura de madeira na borda da coifa
        wbb(mi, -5.95, 5.95, 494.3 + s * 5.5 - 0.25, 494.3 + s * 5.5 + 0.25, zb_ - 0.35, zb_ + 0.45, WD, 0.04)
        wbb(mi, s * 5.7 - 0.25, s * 5.7 + 0.25, 494.3 - 5.75, 494.3 + 5.75, zb_ - 0.35, zb_ + 0.45, WD, 0.04)
    p0 = Vector((0.0, 494.9, zt_ - 0.6))                      # duto de barro inclinado ate o lanternim (sob o forro)
    p1 = Vector((0.0, HC[1] + 0.4, zr - 1.6))
    d = p1 - p0
    obox(mi, (p0 + p1) / 2, d, Vector((0, 0, 1)), (d.length, 4.0, 3.4), CLAY)
    for t in (0.2, 0.75):
        obox(mi, p0 + d * t, d, Vector((0, 0, 1)), (0.5, 4.3, 3.7), WD)
    # shimenawa pequena na frente da coifa
    pts = [Vector((-4.6 + 9.2 * i / 10, 488.6, zb_ - 0.2 - 0.6 * math.sin(math.pi * i / 10))) for i in range(11)]
    mi.sweep(pts, [(0.16 * math.cos(2 * math.pi * j / 6), 0.16 * math.sin(2 * math.pi * j / 6)) for j in range(6)], STRAW)
    for x in (-2.3, 0.0, 2.3):
        z = zb_ - 0.2 - 0.6 * math.sin(math.pi * (x + 4.6) / 9.2) - 0.1
        for j in range(3):
            dx = 0.1 if j % 2 == 0 else -0.1
            wbb(mi, x - 0.2 + dx, x + 0.2 + dx, 488.56, 488.62, z - 0.38 * (j + 1), z - 0.38 * j, PLK)
    # FUIGO (fole de caixa): quadro de madeira escura, paineis de tabua, tampa com travessas, haste com punho em T,
    # duto de tijolo ate o hodo
    fx0, fx1, fy0, fy1 = -8.6, -6.4, 487.0, 493.2
    fz0, fz1 = DOMA + 0.35, DOMA + 2.7
    for x in (fx0 + 0.3, fx1 - 0.3):
        for y in (fy0 + 0.4, fy1 - 0.4):
            wbb(mw, x - 0.22, x + 0.22, y - 0.22, y + 0.22, DOMA - 0.05, fz0 + 0.05, WD)
    wbb(mw, fx0 + 0.08, fx1 - 0.08, fy0 + 0.08, fy1 - 0.08, fz0, fz1, WM)
    for x in (fx0, fx1 - 0.22):
        for y in (fy0, fy1 - 0.22):
            wbb(mw, x, x + 0.22, y, y + 0.22, fz0 - 0.05, fz1 + 0.05, WD, 0.03)
    for z in (fz0, fz1 - 0.2):
        wbb(mw, fx0 - 0.02, fx1 + 0.02, fy0, fy0 + 0.22, z, z + 0.2, WD)
        wbb(mw, fx0 - 0.02, fx1 + 0.02, fy1 - 0.22, fy1, z, z + 0.2, WD)
    for y in even(fy0 + 0.5, fy1 - 0.5, 1.6):
        wbb(mw, fx0 - 0.05, fx1 + 0.05, y - 0.13, y + 0.13, fz1 - 0.02, fz1 + 0.14, WD)
    mw.rod((fx0 + 1.1, fy0 + 0.1, fz0 + 1.1), (fx0 + 1.1, fy0 - 1.7, fz0 + 1.1), 0.1, WD, 8)
    mw.rod((fx0 + 0.45, fy0 - 1.7, fz0 + 1.1), (fx0 + 1.75, fy0 - 1.7, fz0 + 1.1), 0.12, WD, 8)
    wbb(mi, fx1 - 0.1, hx0 + 0.1, 493.1, 494.5, DOMA - 0.05, DOMA + 1.0, BRICK, 0.04)
    # assento do ferreiro (tabua sobre pedras) entre o fuigo e o hodo
    wbb(mw, -5.9, -4.7, 486.6, 489.4, DOMA + 0.5, DOMA + 0.7, WM, 0.03)
    for y in (486.9, 489.1):
        K.rock_base(mw, W0, -5.3, y, DOMA, 0.45, 0.45)
    # BIGORNA baixa (kanatoko) sobre toco, com a lamina em brasa e a tenaz; martelos
    ax, ay = MX, 487.0
    mw.cyl(1.0, 1.25, (ax, ay, DOMA + 0.5), m="Bark_DS", n=12, bevel=0.0)
    mw.cyl(0.92, 0.1, (ax, ay, DOMA + 1.12), m=WM, n=12, bevel=0.0)
    wbb(mi, ax - 1.15, ax + 1.15, ay - 0.6, ay + 0.6, DOMA + 1.15, DOMA + 1.95, IRON, 0.08)
    sword(mi, Vector((ax - 1.05, ay + 0.1, DOMA + 1.95 + 0.05)), (1, 0, 0), (0, -1, 0), (0, 0, 1), "blank")
    for s in (-1, 1):
        mi.rod((ax - 1.2, ay + 0.1 + s * 0.06, DOMA + 2.05), (ax - 3.4, ay + 0.5 + s * 0.35, DOMA + 2.3), 0.06, IRON, 6)
    for (hx, hy, a, ln) in ((1.6, 485.6, 0.4, 2.1), (-1.4, 485.4, -0.5, 2.8)):
        p0 = Vector((ax + hx, hy, DOMA + 0.05))
        d = Vector((math.cos(a) * 0.35, -0.3, 1.0)).normalized()
        p1 = p0 + d * ln
        mi.rod(p0, p1, 0.09, WM, 6)
        obox(mi, p1 + d * 0.1, Vector((math.cos(a + 1.57), math.sin(a + 1.57), 0.0)), d, (0.75 if ln > 2.5 else 0.5,
             0.34, 0.34), IRON, 0.04)
    # COCHO de tempera (mizubune): tabuas, cantoneiras de madeira, agua parada recuada
    qx0, qx1, qy0, qy1 = 4.6, 10.0, 484.2, 486.6
    qz = DOMA + 1.35
    for a, b, c_, d in ((qx0, qx1, qy0, qy0 + 0.25), (qx0, qx1, qy1 - 0.25, qy1), (qx0, qx0 + 0.25, qy0, qy1),
                        (qx1 - 0.25, qx1, qy0, qy1)):
        wbb(mw, a, b, c_, d, DOMA + 0.05, qz, WM)
    for x in (qx0 - 0.08, qx1 - 0.22):
        for y in (qy0 - 0.08, qy1 - 0.22):
            wbb(mw, x, x + 0.3, y, y + 0.3, DOMA, qz + 0.12, WD, 0.03)
    wbb(mi, qx0 + 0.2, qx1 - 0.2, qy0 + 0.2, qy1 - 0.2, DOMA + 0.1, qz - 0.3, WATER)
    # CARVAO: caixa baixa de tabuas com monte de carvao e 3 sacos de palha
    cx0, cx1, cy0, cy1 = 5.4, 9.8, 491.0, 497.4
    for a, b, c_, d in ((cx0, cx1, cy0, cy0 + 0.22), (cx0, cx1, cy1 - 0.22, cy1), (cx0, cx0 + 0.22, cy0, cy1),
                        (cx1 - 0.22, cx1, cy0, cy1)):
        wbb(mw, a, b, c_, d, DOMA - 0.05, DOMA + 1.0, WM)
    for (x, y, r) in ((7.0, 493.0, 1.3), (8.3, 495.4, 1.1), (6.6, 496.0, 0.9)):
        mi.rock((x, y, DOMA + 0.75), (r * 2.0, r * 1.7, r * 1.2), SOOT, 1, jitter=0.3)
    for i, (x, y) in enumerate(((12.5, 497.5), (14.2, 497.5), (13.35, 497.5))):
        tawara(mw, mi, x, y, DOMA + (0.0 if i < 2 else 0.95), 0.0)
    # KATANA-KAKE (3 laminas nuas) na diagonal da boca, + estante de parede (3 embainhadas) e ferramentas
    kake(mi, Frame(12.6, 477.4, DOMA, math.pi + 0.25), SWORD_SETS["salao"], lod=1)
    kake(mi, Frame(HX0 + 1.0, 480.5, DOMA, -math.pi / 2), [("saya", LACQ, IRON), ("saya", RED, BRASS)], H=3.0,
         lod=1, wall=True, z0=2.6)
    for i, y in enumerate((486.0, 487.4, 488.8, 490.2)):                 # tenazes e martelos na parede leste
        wbb(mw, HX1 - 1.15, HX1 - 0.85, y - 0.12, y + 0.12, DOMA + 5.6, DOMA + 5.9, WD)
        if i % 2 == 0:
            for s in (-1, 1):
                mi.rod((HX1 - 1.2, y + s * 0.08, DOMA + 5.7), (HX1 - 1.25, y + s * 0.3, DOMA + 3.1), 0.05, IRON, 6)
        else:
            mi.rod((HX1 - 1.2, y, DOMA + 5.75), (HX1 - 1.2, y, DOMA + 3.6), 0.08, WM, 6)
            wbb(mi, HX1 - 1.45, HX1 - 0.95, y - 0.3, y + 0.3, DOMA + 3.25, DOMA + 3.65, IRON, 0.03)
    wbb(mw, HX1 - 1.1, HX1 - 0.85, 485.0, 491.2, DOMA + 5.9, DOMA + 6.3, WD, 0.03)


def tawara(mw, mi, x, y, z, ang, s=1.0, lod=0):
    """saco de carvao de palha (sumidawara): cilindro de palha com 2 amarras, carvao aparecendo nas pontas.
    ONDA 6b: a tampa de carvao salta 0,14 da ponta da palha (saltava 0,06: Rope x Soot coplanar); lod=1 = 6 lados e
    1 amarra (os sacos do patio do carvao)"""
    r, ln = 0.5 * s, 1.6 * s
    n = 8 if lod == 0 else 6
    a = Vector((math.cos(ang), math.sin(ang), 0.0))
    c = Vector((x, y, z + r))
    rot = (0.0, math.pi / 2, ang)
    mw.cyl(r, ln, tuple(c), rot, STRAW, n, bevel=0.0)
    for t in ((-0.28, 0.28) if lod == 0 else (0.06,)):
        mw.cyl(r + 0.05, 0.14, tuple(c + a * ln * t), rot, STRAW, n, bevel=0.0)
    for t in (-0.5, 0.5):
        mi.cyl(r * 0.7, 0.16, tuple(c + a * (ln * t + 0.06 * (1 if t > 0 else -1))), rot, SOOT, n, bevel=0.0)


# ================================================================== TORRE-CHAMINE
def tower(mb, mi):
    F = Frame(TX, TY, T4, math.pi)
    K.foundation(mb, F, 15.0, 15.0, TB, "ishigaki", batter=3.0, lod=1)
    # boca de fogo da torre (kama-guchi): caixa de tijolo saliente na face sul da base, arco de 7 aduelas, laje de
    # coroamento, fundo de fuligem e brasas baixas RECUADAS 0,5 atras da frente do arco
    yb, yf = 7.9, 9.5
    for sx in (-1, 1):
        bb(mi, F, sx * 1.15, sx * 2.3, yb, yf, -0.1, 2.05, BRICK, 0.05)
    for i in range(7):
        a0, a1 = math.pi * i / 7 + 0.02, math.pi * (i + 1) / 7 - 0.02
        r0, r1 = 1.15, 2.3 + (0.25 if i == 3 else 0.0)
        poly = [(r0 * math.cos(a0), 2.05 + r0 * math.sin(a0)), (r1 * math.cos(a0), 2.05 + r1 * math.sin(a0)),
                (r1 * math.cos(a1), 2.05 + r1 * math.sin(a1)), (r0 * math.cos(a1), 2.05 + r0 * math.sin(a1))]
        ext(mi, F, list(reversed(poly)), "y", yb, yf + (0.12 if i == 3 else 0.0), BRICK if i != 3 else STD, 0.03)
    for sx in (-1, 1):                                    # cheios entre o extradorso e o retangulo
        ext(mi, F, [(sx * 2.3, 2.05), (sx * 2.3, 4.35), (sx * 0.4, 4.35)] +
            [(sx * 2.32 * math.cos(math.pi / 2 * (1 - k / 6)), 2.05 + 2.32 * math.sin(math.pi / 2 * (1 - k / 6))) for k in range(1, 6)],
            "y", yb, yf - 0.1, BRICK)
    bb(mi, F, -2.75, 2.75, yb, yf + 0.25, 4.35, 4.85, STD, 0.06)
    bb(mi, F, -1.2, 1.2, yb, yb + 0.6, -0.1, 3.3, SOOT)
    bb(mi, F, -1.0, 1.0, yb + 0.6, yb + 0.85, 0.0, 0.75, EMBER)
    for k, x in enumerate((-0.6, 0.1, 0.65)):
        mi.box((0.45, 0.4, 0.3), tuple(F.p(x, yb + 0.95, 0.3 + 0.05 * k)), F.r(0.0, 0.0, 0.4 * k), SOOT, 0.0)
    c = F.p(0.0, 8.8, 2.4)
    col_box("DS_FrgTower", (5.6, 2.0, 4.9), (c.x, c.y, c.z), F.r())
    Fb = sub(F, z=TB)
    W = 14.0
    K.corner_posts(mb, Fb, W, W, 0.7, TS1 - 1.0)
    for i, (ang, bays) in enumerate(((0.0, ["plaster", {"t": "shoji", "ww": 1.8, "wh": 3.6, "z": 6.0}, "plaster"]),
                                     (math.pi, ["plaster", "plaster", "plaster"]),
                                     (-math.pi / 2, ["plaster", {"t": "shoji", "ww": 1.6, "wh": 3.2, "z": 6.0}, "plaster"]),
                                     (math.pi / 2, ["plaster", {"t": "shoji", "ww": 1.6, "wh": 3.2, "z": 6.0}, "plaster"]))):
        Ff = sub(sub(Fb, 0.0, 0.0, 0.0, ang), 0.0, W / 2)
        K.facade(mb, Ff, W, TS1, bays, i < 2, plaster=CLAY, lit=True, lod=0 if i != 1 else 1)
    K.roof_hip(mb, sub(F, z=TB - 2.2), W, W, 2.2, "yosemune", pitch=0.42, over=2.2, lift=0.5, tv=0.4, lod=1,
               rafters=False)
    for ang in (0.0, math.pi, math.pi / 2, -math.pi / 2):     # cinta entre os pisos (sem telhado no meio)
        Ff = sub(sub(Fb, 0.0, 0.0, 0.0, ang), 0.0, W / 2)
        bb(mb, Ff, -W / 2 - 0.5, W / 2 + 0.5, -0.4, 0.45, TS1 - 0.2, TS1 + 0.75, WD, 0.06)
    Fb2 = sub(F, z=TB + TS1)
    K.corner_posts(mb, Fb2, W, W, 0.7, TS2 - 1.0)
    for i, (ang, bays) in enumerate(((0.0, [{"t": "shoji", "ww": 1.6, "wh": 3.4, "z": 7.0}, "plaster",
                                            {"t": "shoji", "ww": 1.6, "wh": 3.4, "z": 7.0}]),
                                     (math.pi, ["plaster", {"t": "shoji", "ww": 1.6, "wh": 3.4, "z": 7.0}, "plaster"]),
                                     (-math.pi / 2, ["plaster", {"t": "shoji", "ww": 1.6, "wh": 3.4, "z": 7.0}, "plaster"]),
                                     (math.pi / 2, ["plaster", {"t": "shoji", "ww": 1.6, "wh": 3.4, "z": 7.0}, "plaster"]))):
        Ff = sub(sub(Fb2, 0.0, 0.0, 0.0, ang), 0.0, W / 2)
        K.facade(mb, Ff, W, TS2, bays, i < 2, plaster=CLAY, lit=True, lod=1)
    # misulas sob o beiral do chapeu
    for ang in (0.0, math.pi, math.pi / 2, -math.pi / 2):
        Ff = sub(sub(Fb2, 0.0, 0.0, 0.0, ang), 0.0, W / 2)
        for x in (-4.6, 0.0, 4.6):
            K.bracket(mb, Ff, x, 0.1, TS2 - 1.0, 1.6, 0.5, 1.0)
    r = K.roof_hip(mb, Fb2, W, W, TS2, "yosemune", pitch=1.0, over=3.0, lift=1.1, tv=0.45, lod=1, rafters=True)
    chimney(mb, Fb2.o.z + TS2 - 1.0)
    return Fb2.o.z + r["zr"]


def chimney(mb, z0):
    """chamine de pedra quadrada: fiadas de 2 blocos por face sobre miolo escuro, cinta em balanco, coroa de fuligem
    com o topo aberto (fundo escuro recuado). Topo = CHIMNEY_TOP"""
    cx, cy = L.CHIMNEY[0], L.CHIMNEY[1]
    s = 5.2
    ztop = L.CHIMNEY_TOP
    zc = ztop - 2.3
    wbb(mb, cx - s / 2 + 0.12, cx + s / 2 - 0.12, cy - s / 2 + 0.12, cy + s / 2 - 0.12, z0, zc, SOOT)
    n = int(round((zc - 0.7 - z0) / 1.05))
    hc = (zc - 0.7 - z0) / n
    for i in range(n):
        za, zb = z0 + hc * i + 0.03, z0 + hc * (i + 1) - 0.03
        m = SOOT if zb > zc - 3.0 else ST
        for k, (dx, dy, ax_) in enumerate(((0, -1, "x"), (0, 1, "x"), (-1, 0, "y"), (1, 0, "y"))):
            sp = 0.6 if (i + k) % 2 else -0.7
            for a, b in ((-s / 2 - 0.02, sp - 0.04), (sp + 0.04, s / 2 + 0.02)):
                if ax_ == "x":
                    wbb(mb, cx + a, cx + b, cy + dy * s / 2 - 0.3, cy + dy * s / 2 + 0.3, za, zb, m)
                else:
                    wbb(mb, cx + dx * s / 2 - 0.3, cx + dx * s / 2 + 0.3, cy + a, cy + b, za, zb, m)
    zb_ = zc - 0.7
    wbb(mb, cx - s / 2 - 0.45, cx + s / 2 + 0.45, cy - s / 2 - 0.45, cy + s / 2 + 0.45, zb_, zb_ + 0.6, STD, 0.06)
    wbb(mb, cx - s / 2 - 0.25, cx + s / 2 + 0.25, cy - s / 2 - 0.25, cy + s / 2 + 0.25, zc - 0.1, ztop - 1.1, SOOT, 0.06)
    for a, b, c_, d in ((-s / 2 - 0.35, s / 2 + 0.35, -s / 2 - 0.35, -s / 2 + 0.55), (-s / 2 - 0.35, s / 2 + 0.35, s / 2 - 0.55, s / 2 + 0.35),
                        (-s / 2 - 0.35, -s / 2 + 0.55, -s / 2 + 0.55, s / 2 - 0.55), (s / 2 - 0.55, s / 2 + 0.35, -s / 2 + 0.55, s / 2 - 0.55)):
        wbb(mb, cx + a, cx + b, cy + c_, cy + d, ztop - 1.1, ztop, SOOT, 0.05)
    wbb(mb, cx - s / 2 + 0.5, cx + s / 2 - 0.5, cy - s / 2 + 0.5, cy + s / 2 - 0.5, ztop - 1.6, ztop - 1.3, SOOT)


# ================================================================== OFICINA-RESIDENCIA E ALA LESTE (kit)
WORKSHOP_SPEC = dict(K.PRESETS["V5"], W=30.0, D=21.0, h=9.8, plinth=("ishigaki", 1.2), pitch=0.48, over=3.2, lod=1,
                     gable=0.66, plaster="ash",
                     front=["plain", {"t": "door", "noren": RED}, "koshi", {"t": "door", "noren": RED}, "plain"],
                     back="auto", left="auto", right="auto",
                     upper=dict(h=7.8, front=["plaster", "shoji", "shoji", "shoji", "plaster"], balcony=True))
EAST_SPEC = dict(W=22.0, D=22.0, h=11.0, lod=1, plinth=("soco", 1.0), roof="kirizuma", ridge="y", pitch=0.6, over=3.0,
                 g_over=1.8, door_h=7.4, front=["plaster", "shop", "shop", "plaster"],
                 left=["plaster", "koshi", "plaster"], right=["plain", "itado", "plain"], back="auto",
                 plaster=CLAY, hisashi_front=True, hisashi_z=10.4)


def workshop(mb):
    x0, y0, x1, y1 = L.FORGE["workshop"][:4]
    F = Frame((x0 + x1) / 2, (y0 + y1) / 2, T4, math.pi)
    info = K.house(mb, F, WORKSHOP_SPEC, "L_DSFrg_Workshop", 110.0)
    K.house_cols("DS_FrgWorkshop", F, WORKSHOP_SPEC, info)
    return info


def east_wing(mb):
    x0, y0, x1, y1 = L.FORGE["east"][:4]
    F = Frame((x0 + x1) / 2, (y0 + y1) / 2, T4, math.pi)
    info = K.house(mb, F, EAST_SPEC, "L_DSFrg_East", 90.0)
    K.house_cols("DS_FrgEast", F, EAST_SPEC, info)
    return info


# ================================================================== RODA D'AGUA, POCO, MOINHO (piloes), AQUEDUTO
def wheel():
    """mizuguruma de caçambas: 2 aros de tabua (24 segmentos), fundo (sole) e pas inclinadas entre os aros, 8 raios
    por lado, cubo oitavado de madeira com cunhas. Peca movel (gira no eixo leste-oeste)"""
    mw = MB("VFX_DS_Wheel", "12_VFX_HELPERS", random.Random(2201), detail="near", floor=-999)
    n = 24
    xs = (WX - WWID / 2 + 0.2, WX + WWID / 2 - 0.2)
    P = lambda x, r, a: Vector((x, WY + r * math.cos(a), WAZ + r * math.sin(a)))
    for x in xs:                                            # aros
        ro, ri = WR, WR - 1.25
        rings = []
        for x_, r_ in ((x - 0.2, ri), (x - 0.2, ro), (x + 0.2, ro), (x + 0.2, ri)):
            rings.append([P(x_, r_, 2 * math.pi * k / n) for k in range(n)])
        bm = mw.bm
        V = [[bm.verts.new(tuple(p)) for p in r] for r in rings]
        fs = []
        for i in range(4):
            a, b = V[i], V[(i + 1) % 4]
            for k in range(n):
                k2 = (k + 1) % n
                fs.append(bm.faces.new((a[k], a[k2], b[k2], b[k])))
        bmesh.ops.recalc_face_normals(bm, faces=fs)
        mw._post([v for r in V for v in r], WD, None, 0, 1)
        for k in range(n):                                  # juntas dos segmentos do aro (talas)
            a = 2 * math.pi * (k + 0.5) / n
            obox(mw, P(x, WR - 0.62, a), Vector((0.0, -math.sin(a), math.cos(a))), Vector((1, 0, 0)), (0.5, 1.15, 0.5),
                 WD) if k % 3 == 0 else None
    for k in range(n):                                      # fundo (sole) e pas em caçamba
        a0, a1 = 2 * math.pi * k / n, 2 * math.pi * (k + 1) / n
        am = (a0 + a1) / 2
        tang = Vector((0.0, -math.sin(am), math.cos(am)))
        rad = Vector((0.0, math.cos(am), math.sin(am)))
        rs = WR - 1.2
        obox(mw, P(WX, rs, am), tang, rad, (2 * rs * math.sin(math.pi / n) + 0.05, WWID - 0.75, 0.22), WM)
        d = (rad * 1.15 + tang * 0.55)
        c = P(WX, rs, a1) + d * 0.5 + rad * 0.05
        obox(mw, c, d, d.cross(Vector((1, 0, 0))), (d.length, WWID - 0.75, 0.2), WM)
    for x in xs:                                            # raios em pares (8 por lado), cubo e cunhas
        for k in range(8):
            a = 2 * math.pi * k / 8 + math.pi / 16
            rad = Vector((0.0, math.cos(a), math.sin(a)))
            for off in (-0.28, 0.28):
                tang = Vector((0.0, -math.sin(a), math.cos(a)))
                c = P(x, (1.3 + WR - 1.2) / 2, a) + tang * off
                obox(mw, c, rad, Vector((1, 0, 0)), (WR - 1.2 - 1.25, 0.32, 0.36), WD)
    mw.cyl(1.55, WWID + 0.4, (WX, WY, WAZ), (0, math.pi / 2, 0), WD, 8, bevel=0.0)
    for k in range(8):
        a = 2 * math.pi * k / 8
        for x in (xs[0] - 0.45, xs[1] + 0.45):
            obox(mw, P(x, 1.25, a), Vector((0.0, math.cos(a), math.sin(a))), Vector((1, 0, 0)), (0.6, 0.3, 0.3), WM)
    ob = mw.finish()
    ob["pivot"] = (WX, WY, WAZ)
    ob["axis"] = (1.0, 0.0, 0.0)
    ob["rpm"] = 3.0
    ob["vfx_zone"] = "forge"
    ob["Dist"] = 220.0
    return ob


def stone_wall(mb, p0, p1, z0, z1, th, key=0, m=ST):
    """muro de pedra baixo: blocos em 2 fiadas com junta e capa de lajes"""
    a, b = Vector((p0[0], p0[1], 0.0)), Vector((p1[0], p1[1], 0.0))
    d = b - a
    ln = d.length
    F = Frame(a.x, a.y, 0.0, math.atan2(d.y, d.x))
    pat = (2.2, 1.7, 2.6, 1.9, 2.4)
    nc = 2
    hc = (z1 - 0.3 - z0) / nc
    for c in range(nc):
        x = 0.0
        k = key + c * 2
        while x < ln - 0.2:
            x2 = min(ln, x + pat[k % len(pat)])
            if ln - x2 < 0.7:
                x2 = ln
            k += 1
            bb(mb, F, x + 0.04, x2 - 0.04, -th / 2, th / 2, z0 + hc * c + 0.03, z0 + hc * (c + 1) - 0.03, m, 0.06)
            x = x2
    x = 0.0
    k = key + 1
    while x < ln - 0.2:
        x2 = min(ln, x + (2.9, 2.3, 3.4)[k % 3])
        if ln - x2 < 0.8:
            x2 = ln
        k += 1
        bb(mb, F, x + 0.03, x2 - 0.03, -th / 2 - 0.12, th / 2 + 0.12, z1 - 0.3, z1, ST, 0.06)
        x = x2


def mill(mb, mr):
    """poco da roda (muro de pedra com a saida do tailrace), pilares de pedra e mancais, eixo, 2 piloes (kine) com
    guias e cames, pilao/almofariz, telheiro do moinho"""
    yS, yN = WY - 11.8, WY + 11.8
    xW, xE = WX - 3.2, WX + 3.2
    ty = L.TAILRACE[0][1]                                    # saida (96, 482): vao no muro leste
    stone_wall(mr, (xW, yS), (xW, yN), T4 - 0.8, T4 + 0.75, 1.0, 0)
    stone_wall(mr, (xE, yN), (xE, ty + 1.75), T4 - 0.8, T4 + 0.75, 1.0, 2)
    stone_wall(mr, (xE, ty - 1.75), (xE, yS), T4 - 0.8, T4 + 0.75, 1.0, 1)
    stone_wall(mr, (xE + 0.5, yS), (xW - 0.5, yS), T4 - 0.8, T4 + 0.75, 1.0, 3)
    stone_wall(mr, (xW - 0.5, yN), (xE + 0.5, yN), T4 - 0.8, T4 + 0.75, 1.0, 4)
    # pilares de pedra (mancais) dos 2 lados da roda
    for x in (xW - 0.2, xE + 0.2):
        y = WY
        hz = WAZ - 0.9 - (T4 - 0.8)
        nc = 6
        for i in range(nc):
            z0 = T4 - 0.8 + hz * i / nc
            w = 1.7 if i % 2 == 0 else 1.5
            wbb(mr, x - 0.75, x + 0.75, y - w, y + w, z0 + 0.03, z0 + hz / nc - 0.03, ST, 0.06)
        wbb(mb, x - 0.6, x + 0.6, y - 1.2, y + 1.2, WAZ - 0.9, WAZ - 0.3, WD, 0.05)            # mancal
        wbb(mb, x - 0.6, x + 0.6, y - 1.2, y - 0.75, WAZ - 0.3, WAZ + 0.75, WD, 0.04)
        wbb(mb, x - 0.6, x + 0.6, y + 0.75, y + 1.2, WAZ - 0.3, WAZ + 0.75, WD, 0.04)
    # eixo de madeira (oitavado) do mancal oeste do moinho ate o mancal leste da roda
    xa = L.FORGE["east"][2] + 2.6
    # ONDA 3c (agente 3c / ds_vfx - unica parte do ds_forge editada por ele): o eixo com os cames e as cabecas, hastes
    # e ressaltos dos 2 piloes viram PECAS MOVEIS (VFX_ -> tag IlhaMovel no export). O cliente ILHA_NARUTO_Movel ja tem o
    # modo pilao (atributos bob + rate: sobe em 70% do ciclo e cai em 30%) e o giro (rpm em volta de pivot/axis):
    #   VFX_DS_KineAxle gira com a roda (MESMO pivo, eixo e rpm do VFX_DS_Wheel);
    #   VFX_DS_Kine_A (came de 2 ressaltos) e VFX_DS_Kine_B (came de 3): rate = rpm / 60 x ressaltos = 0,10 e 0,15
    #   batida/s a 3 rpm -> os dois nao batem juntos (coincidem a cada 20 s), cada um no ritmo do proprio came.
    # Os 2 sao modelados na posicao BAIXA (o bob do cliente vai de 0 a +KINE_LIFT); os cames ficam a 50 graus (o
    # ressalto mais proximo ainda nao encosta no tucho). O ds_vfx confere rpm/rate pela roda no build.
    ax_mb = MB("VFX_DS_KineAxle", "12_VFX_HELPERS", random.Random(2203), detail="near", floor=-999)
    ax_mb.cyl(0.62, (xE + 0.6) - xa, ((xa + xE + 0.6) / 2, WY, WAZ), (0, math.pi / 2, 0), WD, 8, bevel=0.0)
    for x in (xa + 0.4, WX - 6.5):
        ax_mb.cyl(0.72, 0.3, (x, WY, WAZ), (0, math.pi / 2, 0), WM, 8, bevel=0.0)
    # piloes (kine): 2 vigas verticais guiadas, ressalto (tappet) sobre o eixo, came no eixo
    sy = WY - 2.4
    zm = T4 + 1.7                                            # topo do almofariz
    for nm, x, lobes in (("A", xa + 3.9, 2), ("B", xa + 7.6, 3)):
        rock_base(mb, W0, x, sy, T4, 1.5, 0.3)
        wbb(mr, x - 1.1, x + 1.1, sy - 1.1, sy + 1.1, T4 + 0.2, zm, ST, 0.08)                   # almofariz de pedra
        wbb(mr, x - 0.6, x + 0.6, sy - 0.6, sy + 0.6, zm - 0.5, zm - 0.12, SOOT)
        km = MB("VFX_DS_Kine_" + nm, "12_VFX_HELPERS", random.Random(2210 + lobes), detail="near", floor=-999)
        zb_ = zm - 0.45
        wbb(km, x - 0.55, x + 0.55, sy - 0.55, sy + 0.55, zb_, zb_ + 1.5, WD, 0.06)            # cabeca
        wbb(km, x - 0.4, x + 0.4, sy - 0.4, sy + 0.4, zb_ + 1.45, WAZ + 5.6, WM, 0.05)         # haste
        zt = WAZ + 0.9
        wbb(km, x - 0.22, x + 0.22, sy + 0.3, WY + 0.7, zt, zt + 0.45, WD, 0.04)                # ressalto
        for k in range(lobes):                                                                   # came (no eixo)
            a = KINE_CAM0 + 2 * math.pi * k / lobes
            c = Vector((x, WY + 0.85 * math.cos(a), WAZ + 0.85 * math.sin(a)))
            obox(ax_mb, c, Vector((0.0, math.cos(a), math.sin(a))), Vector((1, 0, 0)), (1.6, 0.4, 0.42), WD, 0.03)
        ob = km.finish()
        ob["pivot"] = (x, sy, zm)
        ob["axis"] = (0.0, 0.0, 1.0)
        ob["rpm"] = 0.0
        ob["bob"] = KINE_LIFT
        ob["lobes"] = lobes
        ob["rate"] = round(KINE_RPM / 60.0 * lobes, 4)
        ob["vfx_zone"] = "forge"
    ob = ax_mb.finish()
    ob["pivot"] = (WX, WY, WAZ)
    ob["axis"] = (1.0, 0.0, 0.0)
    ob["rpm"] = KINE_RPM
    ob["vfx_zone"] = "forge"
    for x in (xa + 2.2, xa + 5.75, xa + 9.4):                # pilares das guias
        K.post(mb, W0, x, sy, T4, T4 + 17.4, 0.75, True)
    for z in (T4 + 5.2, T4 + 15.4):                          # guias (par de travessas)
        for dy in (-0.6, 0.6):
            wbb(mb, xa + 1.8, xa + 9.8, sy + dy - 0.2, sy + dy + 0.2, z - 0.35, z + 0.35, WD, 0.04)
    # telheiro do moinho: 4 pilares, frechais e kirizuma de tabuas
    x0, x1 = xa + 1.2, WX - 4.1
    y0, y1 = WY - 7.2, WY + 7.0
    for x in (x0, x1):
        for y in (y0, y1):
            K.post(mb, W0, x, y, T4, T4 + 17.6, 0.8, True)
        wbb(mb, x - 0.4, x + 0.4, y0 - 0.6, y1 + 0.6, T4 + 16.7, T4 + 17.6, WD, 0.05)
    for y in (y0, y1):
        wbb(mb, x0 - 0.6, x1 + 0.6, y - 0.4, y + 0.4, T4 + 16.7, T4 + 17.6, WD, 0.05)
        beam_ = (Vector((x0 + 0.3, y, T4 + 13.6)), Vector((x0 + 2.4, y, T4 + 16.7)))
        mb.beam(beam_[0], beam_[1], 0.28, 0.32, WD, 0.03)
        mb.beam(Vector((x1 - 0.3, y, T4 + 13.6)), Vector((x1 - 2.4, y, T4 + 16.7)), 0.28, 0.32, WD, 0.03)
    K.roof_gable(mb, Frame((x0 + x1) / 2, (y0 + y1) / 2, T4, 0.0), x1 - x0 + 0.8, y1 - y0 + 0.8, 17.6, pitch=0.58,
                 over=1.6, g_over=1.1, lift=0.35, tv=0.42, lod=1, gable_m=WD, gable_style="board")
    col_box("DS_FrgMill", (xE - xW + 1.4, yN - yS + 1.4, WAZ + WR - T4), ((xW + xE) / 2, WY, (T4 + WAZ + WR) / 2))
    col_box("DS_FrgMill", (x1 - x0 + 1.2, 3.6, 16.0), ((x0 + x1) / 2, sy, T4 + 8.0))
    for x in (x0, x1):
        for y in (y0, y1):
            col_box("DS_FrgMill", (1.0, 1.0, 17.6), (x, y, T4 + 8.8))


def flume(mb, ms):
    """calha de madeira (fundo + 2 tabuas laterais + travessas) sobre cavaletes (2 pernas inclinadas, chapeu, travessas
    e mao-francesa em X nos altos, sapatas de pedra) da nascente ate o bico sobre a roda; caixa de pedra na nascente"""
    pts = _flume_pts()
    info = []
    tops = []
    for a, b in zip(pts, pts[1:]):
        d = b - a
        hd = Vector((d.x, d.y, 0.0))
        ln = hd.length
        u = hd.normalized()
        nv = Vector((-u.y, u.x, 0.0))
        e = d.normalized()
        a2, b2 = a - e * 0.2, b + e * 0.2
        mb.beam(a2 - Vector((0, 0, 0.7)), b2 - Vector((0, 0, 0.7)), 2.6, 0.32, WM, 0.03)                    # fundo
        for s in (-1, 1):
            o = nv * s * 1.15
            mb.beam(a2 + o - Vector((0, 0, 0.2)), b2 + o - Vector((0, 0, 0.2)), 0.26, 1.3, WM, 0.03)      # laterais
            mb.beam(a2 + o * 1.12 + Vector((0, 0, 0.42)), b2 + o * 1.12 + Vector((0, 0, 0.42)), 0.3, 0.2, WD, 0.03)
        k = max(1, int(ln / 2.6))
        for i in range(k + 1):
            p = a + d * (i / k)
            obox(mb, p + Vector((0, 0, 0.55)), nv, Vector((0, 0, 1)), (2.95, 0.22, 0.16), WD)                # travessa
            for s in (-1, 1):
                obox(mb, p + nv * s * 1.42 - Vector((0, 0, 0.3)), Vector((0, 0, 1)), u, (1.35, 0.2, 0.2), WD)   # estaca
        info.append((a, b, u, nv, ln))
    # cavaletes
    for idx, (a, b, u, nv, ln) in enumerate(info):
        if idx == len(info) - 1:
            continue                                          # o bico (ultimo trecho) vai no portico sobre a roda
        k = max(1, int(round(ln / 6.5)))
        for i in range(k + (1 if idx == len(info) - 2 else 0)):
            t = i / k
            p = a + (b - a) * t
            zc = p.z - 0.9
            zg = ground_z(p.x, p.y)
            if zg is None or zc - zg < 1.4:
                continue
            h = zc - zg
            spread = 1.5
            for sd in (-1, 1):
                f = p + nv * sd * spread
                mb.beam(Vector((f.x, f.y, zg - 0.3)), Vector((f.x, f.y, zc - 0.3)), 0.55, 0.55, WD, 0.05)
                ms.box((1.25, 1.25, 0.7), (f.x, f.y, zg + 0.05), (0, 0, math.atan2(u.y, u.x)), ST, 0.08)
            obox(mb, Vector((p.x, p.y, zc - 0.05)), nv, Vector((0, 0, 1)), (5.0, 0.6, 0.5), WD, 0.05)          # chapeu
            nt = max(1, int(h / 5.0)) if h > 3.0 else 0
            for j in range(1, nt + 1):                                                                   # nuki
                zt = zc - 0.4 - (h - 0.6) * j / (nt + 1)
                obox(mb, Vector((p.x, p.y, zt)), nv, Vector((0, 0, 1)), (2 * spread + 1.3, 0.24, 0.42), WD, 0.03)
            if h > 4.0:
                for sd in (-1, 1):                                                                       # mao-francesa
                    q0 = Vector((p.x, p.y, zc - 1.9)) + nv * sd * spread
                    q1 = Vector((p.x, p.y, zc - 0.35)) + nv * sd * 0.4
                    mb.beam(q0, q1, 0.26, 0.3, WD, 0.03)
            tops.append(p)
            if zg < T4 + 1.0:
                col_box("DS_FrgFlume", (2 * spread + 0.8, 1.0, min(h, 6.0)), (p.x, p.y, zg + min(h, 6.0) / 2),
                        (0, 0, math.atan2(nv.y, nv.x)))
    # portico sobre a roda (sobre os muros do poco) que segura o bico
    a, b, u, nv, ln = info[-1]
    py = WY + 7.6
    zc = pts[-2].z + (pts[-1].z - pts[-2].z) * 0.45 - 0.9
    for x in (WX - 3.2, WX + 3.2):
        K.post(mb, W0, x, py, T4 + 0.75, zc - 0.4, 0.6, False)
        mb.beam(Vector((x, py - 1.6, zc - 3.2)), Vector((x, py - 0.2, zc - 0.6)), 0.24, 0.28, WD, 0.03)
    wbb(mb, WX - 3.8, WX + 3.8, py - 0.3, py + 0.3, zc - 0.5, zc, WD, 0.04)
    # caixa de pedra da nascente
    s0 = pts[0]
    sx, sy = s0.x, s0.y + 2.4
    zg = ground_z(sx, sy) or (s0.z - 1.0)
    zb_ = min(zg, s0.z - 2.0)
    ms.box((3.8, 3.8, s0.z - 0.4 - zb_), (sx, sy, (s0.z - 0.4 + zb_) / 2), (0, 0, 0.0), ST, 0.08)
    for a, b, c_, d in ((-1.9, 1.9, -1.9, -1.3), (-1.9, 1.9, 1.3, 1.9), (-1.9, -1.3, -1.3, 1.3), (1.3, 1.9, -1.3, 1.3)):
        wbb(ms, sx + a, sx + b, sy + c_, sy + d, s0.z - 0.5, s0.z + 0.6, ST, 0.06)
    wbb(ms, sx - 1.32, sx + 1.32, sy - 1.32, sy + 1.32, s0.z - 0.65, s0.z - 0.4, SOOT)
    return tops


# ================================================================== PATIO, ESCADAS, PATAMAR, CERCAS
def pave_rect(mb, x0, y0, x1, y1, ztop, rows, cols, key=0, m=LAJE, skip=None, gap=0.22):
    """lajes em fiadas (amarracao deslocada) cobrindo o retangulo; o leito escuro aparece nas juntas"""
    y = y0
    r = key
    while y < y1 - 0.3:
        dy = rows[r % len(rows)]
        y2 = min(y1, y + dy)
        if y1 - y2 < 1.2:
            y2 = y1
        x = x0
        k = r * 2 + key
        first = True
        while x < x1 - 0.3:
            dx = cols[k % len(cols)] * (0.55 if first and r % 2 else 1.0)
            first = False
            x2 = min(x1, x + dx)
            if x1 - x2 < 1.2:
                x2 = x1
            k += 1
            cx, cy = (x + x2) / 2, (y + y2) / 2
            if not (skip and skip(cx, cy)):
                slab(mb, x + gap / 2, y + gap / 2, x2 - gap / 2, y2 - gap / 2, ztop, 0.5, 0.08, m)
            x = x2
        y = y2
        r += 1


def yard(mg):
    """patio de trabalho em TERRA BATIDA (o leito do terreno fica 0,5 abaixo: o chao e daqui) com caminhos de laje:
    sando no eixo ate a soleira da boca, calcada ao longo das fachadas, avental no topo da SubidaB"""
    x0, y0, x1, y1 = L.FORGE_YARD
    zt = T4 + 0.14
    # ONDA 4 (z-fight): a ultima pisada da SubidaB (topo em T4, ate y 437,42) entrava 1,8 no patio e ficava COPLANAR
    # com a terra (24 studs2 em (30; 436,5; 80,2)). A faixa da terra sobre a pisada desce 0,3 (piso sobre piso: o de
    # baixo fica >= 0,3 abaixo); o resto do patio nao muda.
    sf, sdeg, sw, sn, stread, _g = L.stair_frame("SubidaB")
    sy1 = sf[1] + stread * sn + 0.02
    sxa, sxb = sf[0] - sw / 2 - 0.02, sf[0] + sw / 2 + 0.02
    if y0 - 0.35 < sy1 and x0 - 0.35 < sxa and sxb < x1 + 0.35:
        wbb(mg, x0 - 0.35, x1 + 0.35, sy1, y1 + 0.35, T4 - 0.45, T4, DIRTD)
        wbb(mg, x0 - 0.35, sxa, y0 - 0.35, sy1, T4 - 0.45, T4, DIRTD)
        wbb(mg, sxb, x1 + 0.35, y0 - 0.35, sy1, T4 - 0.45, T4, DIRTD)
        wbb(mg, sxa, sxb, y0 - 0.35, sy1, T4 - 0.75, T4 - 0.3, DIRTD)
    else:
        wbb(mg, x0 - 0.35, x1 + 0.35, y0 - 0.35, y1 + 0.35, T4 - 0.45, T4, DIRTD)
    sando = (-3.6, 3.6)
    y = y0 + 0.4                                               # sando: lajes grandes no eixo ate a soleira da boca
    while y < BFY - 1.2:
        y2 = min(BFY - 1.1, y + 2.4)
        slab(mg, sando[0], y + 0.11, sando[1], y2 - 0.11, zt + 0.06, 0.6, 0.1, STP)
        y = y2
    for s in (-1, 1):                                          # meio-fio do sando
        wbb(mg, s * (sando[1] + 0.15) - 0.32, s * (sando[1] + 0.15) + 0.32, y0 + 0.4, BFY - 1.1, T4 - 0.4, zt + 0.02,
            STD)
    yw = BFY - 4.6                                             # calcada ao longo das fachadas (oeste e leste do sando)
    pave_rect(mg, x0 + 1.0, yw, sando[0] - 0.5, HY0 - 0.6, zt, (2.4, 2.0), (3.6, 4.2, 3.0, 3.8), 3)
    pave_rect(mg, sando[1] + 0.5, yw, x1 - 1.0, HY0 - 0.6, zt, (2.4, 2.0), (3.8, 3.0, 4.2, 3.6), 4)
    st = L.stair_top("SubidaB")                                # avental no topo da escada + caminho ate a calcada
    pave_rect(mg, st[0] - 7.6, y0 + 1.6, st[0] + 7.6, y0 + 7.4, zt, (2.8, 3.0), (3.8, 4.4, 3.4), 5)
    pave_rect(mg, st[0] - 3.2, y0 + 7.4, st[0] + 3.2, yw, zt, (2.2, 2.6, 2.4), (3.2, 3.2), 6)


TRAIL_W = [(-59.6, 446.3), (-47.0, 446.8), (-34.0, 449.3), (-21.8, 454.0), (-13.6, 457.4)]   # trilha oeste (lajes)
ADRO = (4.45, 12.6, 452.6, 461.7)          # adro de lajes irregulares nos 2 lados do sando: |x| de/ate, y de/ate
GUTTER_Y = (461.85, 462.38)                # sulco de drenagem (canal) entre a terra e a calcada das fachadas
GUTTER_RUNS = [(-55.6, -12.9, True), (-12.9, -4.3, False), (4.3, 12.9, False), (12.9, 26.5, True),
               (33.5, 82.6, True)]         # (x de, x ate, meio-fio do lado da terra)


def yard_dressing(mg, mi):
    """ONDA 6b (6b-C, item 33): o patio de trabalho em volta do heroi deixa de ser terra chapada de uma cor:
    - ADRO de lajes irregulares (reticulado deformado, juntas desencontradas) dos 2 lados do sando na frente da boca,
      com a borda RASGADA (a pedra acaba na terra aos poucos) e as lajes mais perto da boca manchadas de carvao;
    - TRILHA de lajes irregulares do topo oeste do patio ate o adro: continua o caminho de terra do ds_terrain em
      (-60, 446) e acompanha a rota FORGE->ONE_PIECE_GATE;
    - SULCO de drenagem (amamizo) de pedra ao longo da calcada das fachadas: canal escuro + meio-fio do lado da
      terra (a transicao terra -> calcada deixa de ser a quina crua da laje);
    - MANCHAS: terra pisada clara nos caminhos de passagem, cinza/carvao na borda do adro, respingo escuro da tempera
      em volta do cocho da bigorna do patio (todas 0,12 acima da terra e fora do pavimento: nada coplanar)."""
    zt = T4 + 0.17                    # lajes 0,15-0,2 acima da terra (com 0,14 o topo da terra ficava a 0,12 delas)
    # --- adro
    xa, xb, ya, yb = ADRO
    nu, nv = 4, 5
    for sgn in (-1, 1):
        key = "adro%d" % sgn
        C = []
        for i in range(nu + 1):
            row = []
            for j in range(nv + 1):
                x = xa + (xb - xa) * i / nu + (0.0 if i == 0 else (_hh(key, "x", i, j) - 0.5) * 0.55)
                y = ya + (yb - ya) * j / nv + (0.0 if j == nv else (_hh(key, "y", i, j) - 0.5) * 0.5)
                row.append((sgn * x, y))
            C.append(row)

        def keep(i, j, key=key):
            xc = xa + (xb - xa) * (i + 0.5) / nu
            yc = ya + (yb - ya) * (j + 0.5) / nv
            d = math.hypot(xc / 11.5, (yc - yb) / 8.6)
            return d < 0.93 + 0.3 * _hh(key, "k", i, j)

        def put(poly, i, j, key=key):
            cx = sum(p[0] for p in poly) / len(poly)
            cy = sum(p[1] for p in poly) / len(poly)
            sooty = math.hypot(cx, (cy - 466.0) * 1.3) < 7.6 and _hh(key, "s", i, j) < 0.6
            flag(mi if sooty else mg, poly, zt + (_hh(key, "z", i, j) - 0.5) * 0.05, m=SOOT if sooty else LAJE)
        flag_lattice(C, nu, nv, key, put, keep, merge=0.28)
    # --- trilha oeste
    trail_flags(mg, TRAIL_W, 1.45, zt, "trilhaW", rag=0.14)
    # --- sulco de drenagem + meio-fio
    g0, g1 = GUTTER_Y
    for xa_, xb_, curb in GUTTER_RUNS:
        wbb(mg, xa_, xb_, g0, g1, T4 - 0.1, T4 + 0.14, STD)
        if curb:
            x = xa_
            k = 0
            while x < xb_ - 0.3:
                x2 = min(xb_, x + 2.2 + 0.9 * _hh("meiofio", round(xa_, 1), k))
                if xb_ - x2 < 1.0:
                    x2 = xb_
                wbb(mg, x + 0.04, x2 - 0.04, g0 - 0.46, g0 - 0.01, T4 - 0.1, T4 + 0.27 + 0.03 * _hh("mfz", k), ST)
                PAVED.append([(x, g0 - 0.46), (x2, g0 - 0.46), (x2, g1), (x, g1)])
                x = x2
                k += 1
        else:
            PAVED.append([(xa_, g0), (xb_, g0), (xb_, g1), (xa_, g1)])
    # --- manchas (claras na terra pisada; cinza e respingo da tempera em Stone_DS_Soot, no objeto que ja tem fuligem)
    zp = T4 + 0.14
    # 6c (integracao): a mancha grande na frente da boca (15,5; 448,5; r 2,9 x 1,6) e a de (7; 441,8) liam "adesivo" de
    # perto: viraram grupos de 2-3 manchas menores, deslocadas e com rumos diferentes (terra pisada em retalhos)
    for k, (x, y, r, sx, rot) in enumerate(((12.9, 447.7, 1.25, 1.45, -0.5), (16.6, 449.9, 1.0, 1.6, 0.45),
                                            (19.0, 447.0, 0.8, 1.3, 1.15), (6.2, 442.7, 1.0, 1.4, 0.3),
                                            (8.6, 440.8, 0.75, 1.5, -0.7),
                                            (42.6, 446.3, 1.35, 1.4, 0.35), (46.4, 448.2, 0.95, 1.5, -0.45),
                                            (-22.5, 448.6, 1.9, 1.5, 0.4),
                                            (-45.0, 452.9, 2.0, 1.4, 0.1), (-52.0, 441.0, 2.2, 1.6, -0.2),
                                            (61.5, 447.5, 1.7, 1.5, 0.2), (38.0, 456.5, 1.8, 1.3, 0.9))):
        patch(mg, x, y, r * 0.78, zp, "pisada%d" % k, "Dirt_DS", sx, rot)
    for k, (x, y, r, sx, rot) in enumerate(((-13.6, 460.6, 0.9, 1.3, 0.3), (13.6, 455.6, 1.0, 1.4, -0.4),
                                            (10.2, 451.2, 0.75, 1.2, 0.2))):
        patch(mi, x, y, r, zp, "cinza%d" % k, SOOT, sx, rot)
    for k, (x, y, r, sx, rot) in enumerate(((-31.7, 460.3, 0.8, 1.5, 0.15), (-33.5, 457.6, 0.6, 1.3, -0.3))):
        patch(mi, x, y, r * 0.8, zp, "poca%d" % k, WATER, sx, rot)


def stairs_and_landing(mg, mp):
    for nm in ("SubidaA", "SubidaB"):
        foot, deg, w, n, tread, g = L.stair_frame(nm)
        F = Frame(foot[0], foot[1], foot[2], math.radians(deg) - math.pi / 2)
        K.stair_stone(mg, F, w, n, L.stair_rise(nm), tread, True)
    x0, y0, x1, y1 = L.CLIMB_LAND
    pave_rect(mg, x0 + 0.2, y0 + 0.55, x1 - 0.2, y1 - 0.15, T3 + 0.14, (3.0, 3.6, 2.6), (4.6, 3.8, 5.2), 5)
    # patamar-mirante: toro e banco
    K.toro(mp, Frame(-11.5, 411.6, T3, math.pi / 2), "kasuga", 0.9, "L_DSProp_Lamp_FrgPatamar", 30.0)
    col_box("DS_FrgProp", (2.4, 2.4, 6.0), (-11.5, 411.6, T3 + 3.0))
    K.bench(mp, Frame(-1.5, 411.0, T3, math.pi), 0.0, 0.0, 5.0, 1.8, 1.7)
    col_box("DS_FrgProp", (5.2, 2.0, 1.8), (-1.5, 411.0, T3 + 0.9))
    # postes de lanterna no topo da SubidaB (luz a noite)
    for s, nm in ((-1, "L"), (1, "R")):
        x = 30.0 + s * 10.4
        y = 436.4 if s < 0 else 438.6                          # o da esquerda sai da rota que segue a borda para oeste
        K.lantern_post(mp, Frame(x, y, T4, s * math.pi / 2), 8.6, 1.9, "L_DSProp_Lamp_FrgSubida_%s" % nm, 40.0)
        col_box("DS_FrgProp", (1.0, 1.0, 8.6), (x, y, T4 + 4.3))


def fence_run(mb, pts, h=2.6, step=3.6, curb=None):
    """cerca baixa ao longo de pts (x, y, z; na ordem do contorno: o lado de FORA fica a direita): mouroes de madeira
    escura, travessa (nuki) PREGADA na face de fora dos mouroes e corrimao (kasagi) ASSENTADO no topo deles, com
    balanco. ONDA 6b (item 37): as 2 travessas atravessavam o mourao a 0,1 da face dele (257 faces WD x WM a 0,1,
    a cerca sul vista da clareira inteira); agora nenhuma face da travessa fica paralela a < 0,15 de uma do mourao.
    curb = (x_min, x_max): meio-fio de pedra sob os mouroes nesse trecho de x (borda sul do patio)"""
    PH = 0.46
    for i, (a, b) in enumerate(zip(pts, pts[1:])):
        a, b = Vector(a), Vector(b)
        d = b - a
        ln = Vector((d.x, d.y)).length
        if ln < 0.4:
            continue
        ang = math.atan2(d.y, d.x)
        t = Vector((d.x, d.y, 0.0)) / ln
        out = Vector((t.y, -t.x, 0.0))                        # direita do sentido = fora do terraco
        nseg = max(1, int(math.ceil(ln / step)))
        top = h - 0.2
        for j in range(nseg + (1 if i == len(pts) - 2 else 0)):
            q = a + d * (j / nseg)
            mb.box((PH, PH, h), (q.x, q.y, q.z + top - h / 2), (0, 0, ang), WD, 0.0)
        c = (a + b) / 2
        n0 = c + out * (PH / 2 + 0.005 + 0.11)                 # nuki: face de dentro encosta na face de fora do mourao
        mb.box((ln + PH + 0.2, 0.22, 0.26), (n0.x, n0.y, c.z + h * 0.42), (0, 0, ang), WM, 0.0)
        mb.box((ln + PH + 0.5, 0.64, 0.24), (c.x, c.y, c.z + top + 0.12), (0, 0, ang), WM, 0.03)   # kasagi
        if curb:
            # meio-fio: blocos de pedra de 2,2-3,0 sob os mouroes (o mourao nasce dentro dele), 0,47 acima da terra
            # (0,17 acima da capa do ishigaki do ds_terrain, que ele cobre em parte)
            s0 = 0.0
            k = 0
            while s0 < ln - 0.3:
                s1 = min(ln, s0 + 2.2 + 0.8 * _hh("curb", round(a.x, 1), k))
                if ln - s1 < 1.0:
                    s1 = ln
                pa = a + d * (s0 / ln)
                pb = a + d * (s1 / ln)
                m_ = (pa + pb) / 2
                if curb[0] <= m_.x <= curb[1]:
                    obox(mb, (m_.x, m_.y, T4 + 0.16), t, Vector((0, 0, 1)), (s1 - s0 - 0.08, 0.8, 0.62),
                         ST if k % 3 else STD)
                s0 = s1
                k += 1


def edges(mf, mg):
    """cercas na borda do terraco (abertas no topo das escadas) e mureta de pedra no trecho do eixo (a boca le limpa
    da clareira)"""
    zt = T4 + 0.14
    P = DL.offset_poly(DL.ccw(L.FORGE_TERR), -0.8)
    Q = DL.ccw(L.FORGE_TERR)

    def near(pt):
        return min(range(len(Q)), key=lambda i: (Q[i][0] - pt[0]) ** 2 + (Q[i][1] - pt[1]) ** 2)
    # trechos: borda sul (-20,436)->(118,428) com vao da SubidaB e mureta no eixo; diagonal oeste (-36,392)->(-20,436);
    # borda do patio do carvao (-148,380)->(-60,372) com vao da OesteForja; leste (130,440)->(128,478)->(118,512)
    i_sw, i_se = near((-20, 436)), near((118, 428))
    a, b = Vector(P[i_sw]), Vector(P[i_se])

    def along(t):
        return a + (b - a) * t
    lnS = (b - a).length
    st_top = L.stair_top("SubidaB")
    hw = 14.0 / 2 + 1.6
    tA = ((st_top[0] - hw) - a.x) / (b.x - a.x)
    tB = ((st_top[0] + hw) - a.x) / (b.x - a.x)
    tM0 = ((-16.0) - a.x) / (b.x - a.x)
    tM1 = ((16.0) - a.x) / (b.x - a.x)
    tE = ((108.0) - a.x) / (b.x - a.x)

    def pz(v):
        return (v.x, v.y, zt)
    yx0, _, yx1, _ = L.FORGE_YARD                              # ONDA 6b: meio-fio so na borda do patio de trabalho
    fence_run(mf, [pz(along(0.0)), pz(along(tM0))], curb=(yx0, yx1))
    fence_run(mf, [pz(along(tM1)), pz(along(tA))], curb=(yx0, yx1))
    fence_run(mf, [pz(along(tB)), pz(along(tE))], curb=(yx0, yx1))
    # mureta de pedra (eixo): blocos + capa
    m0, m1 = along(tM0), along(tM1)
    stone_wall(mg, (m0.x, m0.y), (m1.x, m1.y), T4 - 0.3, T4 + 1.25, 0.9, 7, STD)
    # diagonal oeste
    i_w = near((-36, 392))
    fence_run(mf, [pz(Vector(P[i_w])), pz(a)])
    # patio do carvao
    i_c0, i_c1 = near((-148, 380)), near((-60, 372))
    c0, c1 = Vector(P[i_c0]), Vector(P[i_c1])
    ot = L.stair_top("OesteForja")
    gx0, gx1 = ot[0] - 6.6, ot[0] + 6.6
    t0 = (gx0 - c0.x) / (c1.x - c0.x)
    t1 = (gx1 - c0.x) / (c1.x - c0.x)
    fence_run(mf, [pz(c0), pz(c0 + (c1 - c0) * t0)])
    if t1 < 1.0:
        fence_run(mf, [pz(c0 + (c1 - c0) * t1), pz(c1), pz(Vector(P[i_w]))])
    # leste
    i_e0, i_e1, i_e2 = near((130, 440)), near((128, 478)), near((118, 512))
    fence_run(mf, [pz(Vector(P[i_e0]) + (Vector(P[i_e1]) - Vector(P[i_e0])) * 0.25), pz(Vector(P[i_e1])),
                   pz(Vector(P[i_e1]) + (Vector(P[i_e2]) - Vector(P[i_e1])) * 0.8)])


# ================================================================== PATIO: kake, polimento, bigorna de pedra
def estrado(mw, F, L=6.0, D=3.0):
    """estrado de madeira (ONDA 6b): 3 dormentes escuros + 5 tabuas com fresta, sobre a calcada; devolve a cota do
    topo das tabuas (relativa a F)"""
    for x in (-L / 2 + 0.45, 0.0, L / 2 - 0.45):
        bb(mw, F, x - 0.16, x + 0.16, -D / 2, D / 2, 0.0, 0.28, WD)
    nb = 5
    w = (D - 0.08 * (nb - 1)) / nb
    for k in range(nb):
        y0 = -D / 2 + k * (w + 0.08)
        bb(mw, F, -L / 2 - 0.08 * (k % 2), L / 2 + 0.08 * ((k + 1) % 2), y0 + 0.02, y0 + w, 0.28, 0.42, WM)
    return 0.42


def yard_anvil(mi, x, y, ang):
    """ONDA 6b (item 34): BIGORNA do patio - kanatoko baixa de ferro (pe, cintura, aba, mesa de aco temperado, chifre
    curto e calcanhar) encaixada no topo de um CEPO de madeira (casca, topo de veio claro, 2 aros de ferro saltados
    0,14), martelo deitado no cepo, tenaz e marreta encostadas, COCHO de tempera de tabuas ao lado (agua recuada).
    F local: +x = comprimento da bigorna (o chifre aponta para o cocho)"""
    F = Frame(x, y, T4, ang)
    o_, ex, ey, ez = axes(F)
    P = lambda a, b, c: F.p(a, b, c)
    # cepo
    mi.cyl(0.92, 0.88, P(0.0, 0.0, 0.36), (0, 0, ang), "Bark_DS", 10, bevel=0.0)
    mi.cyl(0.84, 0.14, P(0.0, 0.0, 0.86), (0, 0, ang), WM, 10, bevel=0.0)
    mi.cyl(1.06, 0.16, P(0.0, 0.0, 0.58), (0, 0, ang), IRON, 10, bevel=0.0)
    z0 = 0.93
    # bigorna: aneis retangulares (meia-largura em x, meia-largura em y, z)
    prof = [(0.56, 0.36, z0 - 0.14), (0.56, 0.36, z0 + 0.12), (0.4, 0.25, z0 + 0.32), (0.6, 0.33, z0 + 0.54),
            (0.63, 0.34, z0 + 0.68)]
    rings = [[P(sx * hx, sy * hy, z) for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))] for hx, hy, z in prof]
    rings_solid(mi, rings, IRON)
    bb(mi, F, -0.6, 0.6, -0.31, 0.31, z0 + 0.68, z0 + 0.8, STEEL)                          # mesa de aco
    hr = [P(0.63, sy * hy, z) for sy, hy, z in ((-1, 0.22, z0 + 0.4), (1, 0.22, z0 + 0.4), (1, 0.27, z0 + 0.67),
                                                (-1, 0.27, z0 + 0.67))]
    hm = [P(0.95, sy * hy, z) for sy, hy, z in ((-1, 0.14, z0 + 0.5), (1, 0.14, z0 + 0.5), (1, 0.17, z0 + 0.67),
                                                (-1, 0.17, z0 + 0.67))]
    rings_solid(mi, [hr, hm], IRON, cap0=False, tip=P(1.25, 0.0, z0 + 0.63))              # chifre curto
    bb(mi, F, -0.84, -0.6, -0.26, 0.26, z0 + 0.46, z0 + 0.67, IRON)                        # calcanhar
    # martelo deitado no cepo (cabo ao longo de x, cabeca atravessada) e tenaz + marreta encostadas no cepo
    mi.rod(P(-0.62, 0.62, 0.99), P(0.25, 0.56, 0.99), 0.06, WM, 6)
    obox(mi, P(0.34, 0.56, 1.03), ey, ez, (0.46, 0.19, 0.19), IRON)
    for dy in (-0.06, 0.06):
        mi.rod(P(-1.05, -0.35 + dy, 0.02), P(-0.66, -0.52 + dy * 2.5, 1.05), 0.045, IRON, 5)
    mi.rod(P(-0.2, -1.15, 0.02), P(-0.15, -0.72, 1.12), 0.07, WM, 6)
    obox(mi, P(-0.21, -1.17, 0.14), ex, ez, (0.5, 0.26, 0.26), IRON)
    # cocho de tempera (mizubune): 4 tabuas + pes, agua 0,16 abaixo da borda
    Fq = sub(F, 1.95, 0.25)
    qx, qy, qh = 0.78, 0.4, 0.62
    for a, b, c_, d in ((-qx, qx, -qy, -qy + 0.12), (-qx, qx, qy - 0.12, qy), (-qx, -qx + 0.12, -qy, qy),
                        (qx - 0.12, qx, -qy, qy)):
        bb(mi, Fq, a, b, c_, d, 0.12, qh, WM)
    for sx in (-1, 1):
        bb(mi, Fq, sx * (qx - 0.22) - 0.13, sx * (qx - 0.22) + 0.13, -qy - 0.06, qy + 0.06, -0.02, 0.16, WD)
    bb(mi, Fq, -qx + 0.14, qx - 0.14, -qy + 0.14, qy - 0.14, 0.14, qh - 0.16, WATER)
    col_box("DS_FrgProp", (1.9, 1.9, 1.8), (x, y, T4 + 0.9))
    c = Fq.p(0.0, 0.0, 0.0)
    col_box("DS_FrgProp", (1.7, 1.0, 0.8), (c.x, c.y, T4 + 0.4), (0, 0, ang))


def yard_props(mi, mw):
    for s, key in ((-1, "patio_W"), (1, "patio_E")):
        x = s * 15.2
        F = Frame(x, HY0 - 3.9, T4 + 0.14, math.pi)
        # ONDA 6b: as 2 estantes de laminas sobre um estrado de madeira de 6 x 3 (nao direto na calcada)
        ze = estrado(mi, F)
        kake(mi, sub(F, z=ze), SWORD_SETS[key])
        col_box("DS_FrgProp", (6.2, 3.2, 3.6), (x, HY0 - 3.9, T4 + 1.8))
    # estacao de polimento (togi) na frente da ala leste: estrado, cavalete inclinado com a pedra, tina d'agua
    F = Frame(56.5, 469.8, T4 + 0.14, math.pi)
    bb(mw, F, -2.2, 2.2, -1.4, 1.4, 0.0, 0.5, WM, 0.04)
    for x in (-1.9, 1.9):
        for y in (-1.1, 1.1):
            bb(mw, F, x - 0.18, x + 0.18, y - 0.18, y + 0.18, -0.05, 0.45, WD)
    ext(mw, F, [(-0.8, 0.5), (0.8, 0.5), (0.8, 1.45), (-0.8, 1.05)], "x", -0.7, 0.7, WD, 0.03)
    bb(mw, F, -0.55, 0.55, -0.55, 0.55, 1.0, 1.5, ST, 0.05)
    mw.cyl(0.7, 0.8, tuple(F.p(1.4, 0.6, 0.9)), (0, 0, 0), WM, 10, bevel=0.0)
    mi.cyl(0.58, 0.05, tuple(F.p(1.4, 0.6, 1.12)), (0, 0, 0), WATER, 10, bevel=0.0)
    col_box("DS_FrgProp", (4.6, 3.0, 1.6), (56.5, 469.8, T4 + 0.8))
    # bigorna do patio a oeste (ONDA 6b: era bloco de pedra + caixa preta) - ver yard_anvil
    bx_, by_ = -30.0, 459.0
    yard_anvil(mi, bx_, by_, 0.15 + math.pi)
    # (ONDA 6b: os 3 sacos sobem para a calcada - em y 462 ficavam sobre o sulco de drenagem novo)
    for i, (x, y) in enumerate(((-34.0, 463.5), (-35.7, 463.3), (-34.8, 463.4))):
        tawara(mw, mi, x, y, T4 + 0.14 + (0.0 if i < 2 else 0.95), 0.1)
    col_box("DS_FrgProp", (3.6, 1.4, 2.0), (-34.9, 463.4, T4 + 1.0))


# ================================================================== PATIO DO CARVAO
# ONDA 6b (6b-C, itens 35-36): o domo liso de barro ("iglu") vira um SUMIGAMA de barro feito a mao, em 4 FIADAS
# (cada uma salta 0,12-0,15 sobre a de cima: as camadas pegam luz) + coroa de terra, raio com variacao dirigida, base
# de pedra, remendos de tijolo, 2 rachaduras e mancha de fuligem sobre a boca, BOCA em arco de tijolo com soleira e
# capa de pedra (brasa recuada atras), 2 respiros na base, chamine de tijolo atras com o duto, lenha encostada; e o
# patio ganha uma AREA DE TRABALHO com sentido: lenha crua a oeste (3 pilhas + cepo de rachar), carvao pronto a
# sudeste (2 pilhas de tawara, cestos, bancada de ensacar) e o carrinho de levar o carvao para a forja.
KILN = (-112.0, 400.0)
KILN_BANDS = [(0.55, 1.45, 5.30, 5.10), (1.40, 2.25, 5.24, 4.70), (2.20, 2.95, 4.84, 3.96), (2.90, 3.45, 4.10, 2.95)]
KILN_CAP = (3.47, 4.04, 3.08, 0.45)          # coroa de terra (z0, z1, r0, r1)


def kiln_r(z):
    """raio da casca do forno na cota z (relativa a T4), pelo LADO DE FORA: o maior das fiadas que passam por z
    (com a barriga de 0,05) - as cascas de remendo/fuligem/rachadura assentam a partir dele"""
    r = 0.0
    for k, (zb, zt, rb, rt) in enumerate(KILN_BANDS):
        zb2 = zb - (0.05 if k else 0.0)
        if zb2 - 1e-6 <= z <= zt + 0.04:
            t = max(0.0, min(1.0, (z - zb2) / (zt - zb2)))
            r = max(r, rb + 0.05 + (rt - rb - 0.05) * t)
    z0, z1, r0, r1 = KILN_CAP
    if z0 <= z <= z1:
        zm = z0 + 0.44
        rc = r0 + (0.62 * r0 - r0) * (z - z0) / 0.44 if z <= zm else 0.62 * r0 * (z1 - z) / (z1 - zm)
        r = max(r, rc)
    if r == 0.0:
        r = 5.3 if z < 0.55 else 0.3
    return r


def _kband(mb, c, n, zb, zt, rb, rt, key, m, bulge=0.05):
    """uma fiada do forno: 3 aneis (pe, barriga, topo) com o raio e a borda de cima sacudidos (feita a mao)"""
    rings = []
    for k, (z, r) in enumerate(((zb, rb), (zb + 0.22, rb + bulge), (zt, rt))):
        ring = []
        for j in range(n):
            a = 0.13 + math.tau * j / n
            rr = r * (1.0 + (_hh(key, k, j) - 0.5) * 0.035)
            zz = z + ((_hh(key, "z", j) - 0.5) * 0.08 if k == 2 else 0.0)
            ring.append(Vector((c[0] + rr * math.cos(a), c[1] + rr * math.sin(a), c[2] + zz)))
        rings.append(ring)
    rings_solid(mb, rings, m)


def _kshell(mb, pts_az_z, m, lift=0.24, width=None):
    """casca sobre o forno (remendo / mancha / rachadura): pts_az_z = grade [linhas][colunas] de (azimute, z) na
    superficie; a face de fora fica 'lift' acima da casca nominal (acima da variacao de +-0,09) e as laterais descem
    0,3 para dentro dela. width: rachadura - 1 linha de pontos vira uma fita dessa largura"""
    kx, ky = KILN
    bm = mb.bm

    def P(az, z, d):
        r = kiln_r(z) + d
        return Vector((kx + r * math.cos(az), ky + r * math.sin(az), T4 + z))
    if width is not None:
        line = pts_az_z
        pts_az_z = [[(az + s_ * width / max(1.0, kiln_r(z)), z) for az, z in line] for s_ in (-0.5, 0.5)]
    R = len(pts_az_z)
    Cc = len(pts_az_z[0])
    O = [[bm.verts.new(P(az, z, lift)) for az, z in row] for row in pts_az_z]
    I = [[bm.verts.new(P(az, z, -0.3)) for az, z in row] for row in pts_az_z]
    fs = []
    for i in range(R - 1):
        for j in range(Cc - 1):
            fs.append(bm.faces.new((O[i][j], O[i][j + 1], O[i + 1][j + 1], O[i + 1][j])))
    nfront = len(fs)
    idx = [(0, j) for j in range(Cc)] + [(i, Cc - 1) for i in range(1, R)] + \
          [(R - 1, j) for j in range(Cc - 2, -1, -1)] + [(i, 0) for i in range(R - 2, 0, -1)]
    nb = len(idx)
    for k in range(nb):
        (a, b), (a2, b2) = idx[k], idx[(k + 1) % nb]
        fs.append(bm.faces.new((O[a][b], I[a][b], I[a2][b2], O[a2][b2])))
    # normais para FORA do forno (a casca e aberta por dentro: o verso nunca se ve)
    bmesh.ops.recalc_face_normals(bm, faces=fs)
    c0 = Vector((kx, ky, T4 + 1.0))
    if sum(f.normal.dot(f.calc_center_median() - c0) * f.calc_area() for f in fs[:nfront]) < 0:
        for f in fs:
            f.normal_flip()
    mb._post([v for r in O for v in r] + [v for r in I for v in r], m, None, 0, 1)


def kiln(mb, mi):
    """o forno de carvao (sumigama) - ver o cabecalho do patio do carvao. Boca a sul (-y), chamine a norte"""
    kx, ky = KILN
    c = (kx, ky, T4)
    n = 16
    # base de pedra escura (16 lados) - o barro nasce dela
    ring = [(kx + 5.62 * math.cos(0.13 + math.tau * j / n), ky + 5.62 * math.sin(0.13 + math.tau * j / n))
            for j in range(n)]
    mb.prism(DL.ccw(ring), T4 - 0.1, T4 + 0.55, STD)
    for k, (zb, zt, rb, rt) in enumerate(KILN_BANDS):
        _kband(mb, c, n, zb - (0.05 if k else 0.0), zt, rb, rt, "kiln%d" % k, CLAY)
    z0, z1, r0, r1 = KILN_CAP                                                  # coroa de terra (so no topo)
    ring0 = [Vector((kx + r0 * math.cos(0.13 + math.tau * j / 12), ky + r0 * math.sin(0.13 + math.tau * j / 12),
                     T4 + z0)) for j in range(12)]
    ring1 = [Vector((kx + (r0 * 0.62) * math.cos(0.4 + math.tau * j / 12),
                     ky + (r0 * 0.62) * math.sin(0.4 + math.tau * j / 12), T4 + z0 + 0.38 + 0.06 * _hh("coroa", j)))
             for j in range(12)]
    rings_solid(mi, [ring0, ring1], DIRTD, tip=Vector((kx + 0.2, ky - 0.1, T4 + z1)))
    # remendos de tijolo nos flancos, mancha de fuligem sobre a boca, 2 rachaduras
    for az0, az1, za, zb_ in ((-0.42, -0.2, 1.0, 1.9), (3.42, 3.66, 1.6, 2.5)):
        _kshell(mb, [[(az0 + (az1 - az0) * i / 2, za + (zb_ - za) * j / 2) for i in range(3)] for j in range(3)],
                BRICK, lift=0.22)
    _kshell(mb, [[(-math.pi / 2 - 0.27 + 0.54 * i / 3 + 0.04 * j * (1 if i % 2 else -1), 3.0 + 0.55 * j)
                  for i in range(4)] for j in range(3)], SOOT, lift=0.26)
    for pts in ([(0.55, 0.75), (0.6, 1.2), (0.53, 1.55), (0.62, 2.05)],
                [(2.45, 1.0), (2.38, 1.5), (2.47, 1.85), (2.4, 2.3), (2.46, 2.6)]):
        _kshell(mb, pts, SOOT, lift=0.22, width=0.17)
    # BOCA (sul): ombreiras de tijolo, arco de 7 aduelas com fecho de pedra saliente, cheios, capa de pedra, soleira
    yf = ky - 5.55
    zs = T4 + 1.5
    r0_, r1_ = 0.95, 1.62
    for s in (-1, 1):
        wbb(mb, kx + s * r0_, kx + s * 1.78, yf, yf + 1.45, T4 - 0.1, zs, BRICK, 0.04)
    for i in range(7):
        a0, a1 = math.pi * i / 7 + 0.02, math.pi * (i + 1) / 7 - 0.02
        key = i == 3
        rr = r1_ + (0.22 if key else 0.0)
        poly = [(kx + r0_ * math.cos(a0), zs + r0_ * math.sin(a0)), (kx + rr * math.cos(a0), zs + rr * math.sin(a0)),
                (kx + rr * math.cos(a1), zs + rr * math.sin(a1)), (kx + r0_ * math.cos(a1), zs + r0_ * math.sin(a1))]
        ext(mb, W0, list(reversed(poly)), "y", yf - (0.14 if key else 0.0), yf + 2.2, STD if key else BRICK, 0.03)
    ztop = zs + 1.75
    for sx in (-1, 1):
        pts = [(kx + sx * 1.78, zs), (kx + sx * 1.78, ztop), (kx + sx * 0.3, ztop)] + \
              [(kx + sx * 1.64 * math.cos(math.pi / 2 * (1 - k / 6)), zs + 1.64 * math.sin(math.pi / 2 * (1 - k / 6)))
               for k in range(1, 6)]
        if sx > 0:
            pts = list(reversed(pts))
        ext(mb, W0, pts, "y", yf + 0.02, yf + 2.2, BRICK)
    wbb(mb, kx - 2.1, kx + 2.1, yf - 0.16, yf + 2.4, ztop, ztop + 0.34, STD, 0.05)          # capa de pedra
    wbb(mb, kx - 1.3, kx + 1.3, yf - 0.42, yf + 1.3, T4 - 0.1, T4 + 0.62, STD, 0.05)        # soleira
    wbb(mb, kx - r0_ - 0.05, kx + r0_ + 0.05, yf + 1.25, yf + 1.6, T4 + 0.5, zs + r0_ + 0.1, SOOT)   # fundo
    wbb(mi, kx - 0.82, kx + 0.82, yf + 1.02, yf + 1.12, T4 + 0.66, T4 + 1.12, EMBER)           # brasa recuada
    for k, (dx, dy, sz) in enumerate(((-0.45, 0.85, 0.34), (0.2, 0.7, 0.28), (0.55, 0.9, 0.3))):
        mb.box((sz, sz * 0.9, sz * 0.7), (kx + dx, yf + dy, T4 + 0.62 + sz * 0.3), (0.3 * k, 0.2, 0.7 * k), SOOT, 0.0)
    # 2 respiros na base de pedra, ladeando a boca (furo escuro saltado + verga de tijolo)
    for az in (-math.pi / 2 - 0.78, -math.pi / 2 + 0.78):
        t_ = Vector((-math.sin(az), math.cos(az), 0.0))
        p = Vector((kx + 5.62 * math.cos(az), ky + 5.62 * math.sin(az), T4 + 0.27))
        obox(mb, p, t_, Vector((0, 0, 1)), (0.6, 0.3, 0.36), SOOT)
        obox(mb, p + Vector((0, 0, 0.3)) + Vector((math.cos(az), math.sin(az), 0)) * 0.05, t_, Vector((0, 0, 1)),
             (0.95, 0.42, 0.22), BRICK)
    # chamine de tijolo atras (norte), conica, com cinta, coroa de pedra e boca de fuligem; duto baixo ate a casca
    cx_, cy_ = kx, ky + 5.95
    rings = [rect_ring(cx_, cy_, T4 - 0.1, 0.78, 0.78), rect_ring(cx_, cy_, T4 + 3.9, 0.6, 0.6),
             rect_ring(cx_, cy_, T4 + 3.9, 0.74, 0.74), rect_ring(cx_, cy_, T4 + 4.32, 0.74, 0.74)]
    rings_solid(mb, rings, BRICK)
    wbb(mb, cx_ - 0.86, cx_ + 0.86, cy_ - 0.86, cy_ + 0.86, T4 + 4.32, T4 + 4.6, STD, 0.04)
    wbb(mb, cx_ - 0.5, cx_ + 0.5, cy_ - 0.5, cy_ + 0.5, T4 + 4.5, T4 + 4.74, SOOT)
    wbb(mb, kx - 0.55, kx + 0.55, ky + 4.4, cy_ - 0.6, T4 - 0.1, T4 + 1.25, BRICK, 0.03)
    # lenha encostada no flanco oeste (5 toros)
    for k in range(5):
        az = math.pi * (0.88 + 0.06 * k) + (_hh("encost", k) - 0.5) * 0.05
        zt_ = 1.7 + 0.35 * _hh("encost", "z", k)
        top = Vector((kx + (kiln_r(zt_) + 0.24) * math.cos(az), ky + (kiln_r(zt_) + 0.24) * math.sin(az), T4 + zt_))
        bot = Vector((kx + 6.55 * math.cos(az + 0.03), ky + 6.55 * math.sin(az + 0.03), T4 + 0.12))
        mb.rod(bot, top, 0.19 + 0.04 * _hh("encost", "r", k), WM, 6)
    col_box("DS_FrgCoal", (10.6, 10.6, 4.8), (kx, ky, T4 + 2.4))
    col_box("DS_FrgCoal", (3.6, 1.2, 3.6), (kx, yf + 0.4, T4 + 1.8))
    light("L_DSFrg_Kiln", "POINT", (kx, ky - 6.7, T4 + 1.2), 140.0, FIREC, 0.4)


def woodpile(mb, F, ln=6.4, rows=4, key="lenha", sp=0.74):
    """lenha rachada empilhada entre 2 pares de mouroes (os topos dos toros nos 2 lados compridos, fiadas
    desencontradas) com cobertura de 2 tabuas inclinadas. F no chao, +x ao longo da pilha"""
    zc = 0.66 * rows + 0.3
    for x in (-ln / 2 - 0.28, ln / 2 + 0.28):
        for y in (-0.82, 0.82):
            bb(mb, F, x - 0.17, x + 0.17, y - 0.17, y + 0.17, 0.0, zc + 0.25, WD)
    for r_ in range(rows):
        off = sp / 2 if r_ % 2 else 0.0
        k = 0
        x = -ln / 2 + sp / 2 + off
        while x < ln / 2 - 0.25:
            rr = 0.3 + 0.06 * _hh(key, r_, k)
            mb.cyl(rr, 2.0 - 0.18 * _hh(key, "l", r_, k), tuple(F.p(x, (_hh(key, "y", r_, k) - 0.5) * 0.22,
                                                                    0.33 + r_ * 0.62)),
                   F.r(math.pi / 2, 0.0, 0.0), WM, 5, bevel=0.0)
            x += sp
            k += 1
    ext(mb, F, [(-1.3, zc), (1.3, zc - 0.22), (1.3, zc + 0.04), (-1.3, zc + 0.26)], "x", -ln / 2 - 0.6, ln / 2 + 0.6,
        WD, 0.04)


def basket(mb, x, y, z, r=0.55, h=0.62):
    """cesto de palha (kago) com parede de espessura e carvao amontoado dentro (o monte sai pela boca)"""
    n = 7
    prof = [(r * 0.78, 0.0), (r * 0.98, h * 0.55), (r, h), (r - 0.08, h), (r - 0.08, h - 0.12)]
    rings = [[Vector((x + rr * math.cos(0.3 + math.tau * j / n), y + rr * math.sin(0.3 + math.tau * j / n), z + zz))
              for j in range(n)] for rr, zz in prof]
    rings_solid(mb, rings, STRAW, tip=Vector((x + 0.05, y - 0.04, z + h + 0.06)),
                mats=lambda i, j: SOOT if i >= len(prof) - 1 else None)


def cart(mb, x, y, ang):
    """carrinho de 2 rodas (daihachi-guruma) estacionado: carroceria de tabuas, guardas, varais que descem ate o chao
    (a frente encosta na terra), rodas com raios saltados 0,14 e cubo de ferro, 2 sacos de carvao em cima"""
    zA = 1.05
    tilt = math.asin((zA + 0.12 - 0.1) / 3.7)
    ca, sa = math.cos(ang), math.sin(ang)
    ct, st_ = math.cos(tilt), math.sin(tilt)

    def W(lx, ly, lz):
        dz = lz - zA
        lx2, lz2 = lx * ct + dz * st_, -lx * st_ + dz * ct + zA
        return Vector((x + lx2 * ca - ly * sa, y + lx2 * sa + ly * ca, T4 + lz2))
    ex_ = W(1, 0, zA) - W(0, 0, zA)
    ez_ = W(0, 0, zA + 1) - W(0, 0, zA)
    ey_ = Vector((-sa, ca, 0.0))
    obox(mb, W(0.15, 0.0, zA + 0.24), ex_, ez_, (2.9, 1.8, 0.14), WM)
    for s in (-1, 1):
        obox(mb, W(0.15, s * 0.86, zA + 0.44), ex_, ez_, (2.9, 0.14, 0.3), WD)
        obox(mb, W(2.45, s * 0.62, zA + 0.12), ex_, ez_, (2.6, 0.17, 0.17), WD)
    obox(mb, W(3.62, 0.0, zA + 0.12), ey_, ez_, (1.5, 0.15, 0.15), WD)
    rot = (math.pi / 2, 0.0, ang)
    for s in (-1, 1):
        cw = Vector((x - sa * s * 1.08, y + ca * s * 1.08, T4 + zA))
        mb.cyl(1.05, 0.15, tuple(cw), rot, WD, 12, bevel=0.0)
        mb.cyl(0.22, 0.46, tuple(cw + ey_ * s * 0.08), rot, IRON, 8, bevel=0.0)
        for k in range(2):
            a = 0.35 + k * math.pi / 2
            dirv = Vector((math.cos(a) * ca, math.cos(a) * sa, math.sin(a)))
            obox(mb, cw + ey_ * s * 0.16, dirv, ey_, (1.9, 0.15, 0.13), WM)
    mb.rod(W(0.0, -1.2, zA), W(0.0, 1.2, zA), 0.1, WD, 6)
    for lx in (-0.55, 0.5):
        p = W(lx, 0.0, zA + 0.31 + 0.475)
        tawara(mb, mb, p.x, p.y, p.z - 0.475, ang + math.pi / 2, 0.95, lod=1)


def chopping_block(mb, x, y, ang):
    """cepo de rachar lenha (makiwari-dai) com o machado cravado e achas espalhadas"""
    F = Frame(x, y, T4, ang)
    mb.cyl(0.56, 0.78, tuple(F.p(0, 0, 0.29)), F.r(), WD, 8, bevel=0.0)
    mb.cyl(0.5, 0.14, tuple(F.p(0, 0, 0.73)), F.r(), WM, 8, bevel=0.0)
    mb.rod(F.p(0.08, 0.0, 0.76), F.p(0.62, 0.1, 1.55), 0.055, WM, 6)
    obox(mb, F.p(0.06, 0.0, 0.84), F.p(1, 0, 0) - F.p(0, 0, 0), Vector((0, 0, 1)), (0.12, 0.42, 0.3), IRON)
    for k, (dx, dy, a) in enumerate(((0.95, 0.35, 0.4), (-0.85, 0.6, 1.9), (0.2, -1.0, -0.6), (-0.6, -0.7, 2.6))):
        p = F.p(dx, dy, 0.2)
        d = Vector((math.cos(F.a + a), math.sin(F.a + a), 0.0)) * 0.45
        mb.rod(p - d, p + d, 0.2, WM, 5)


def coal_yard(mb, mi):
    kx, ky = KILN
    kiln(mb, mi)
    # telheiro do forno: 4 pilares, frechais, kirizuma
    tx0, tx1, ty0, ty1 = kx - 8.0, kx + 8.0, ky - 7.5, ky + 8.5
    for x in (tx0, tx1):
        for y in (ty0, ty1):
            K.post(mb, W0, x, y, T4, T4 + 9.4, 0.75, True)
            col_box("DS_FrgCoal", (0.9, 0.9, 9.4), (x, y, T4 + 4.7))
        wbb(mb, x - 0.4, x + 0.4, ty0 - 0.6, ty1 + 0.6, T4 + 8.6, T4 + 9.4, WD, 0.05)
    for y in (ty0, ty1):
        wbb(mb, tx0 - 0.6, tx1 + 0.6, y - 0.4, y + 0.4, T4 + 8.6, T4 + 9.4, WD, 0.05)
    K.roof_gable(mb, Frame(kx, ky + 0.5, T4, 0.0), tx1 - tx0 + 0.8, ty1 - ty0 + 0.8, 9.4, pitch=0.55, over=1.8,
                 g_over=1.2, lift=0.35, tv=0.42, lod=1, gable_m=WD, gable_style="board")
    # LENHA CRUA (oeste): 3 pilhas + cepo de rachar
    for (wx, wy, ang, ln, rows, key) in ((-132.0, 424.0, -0.4, 7.6, 4, "lenhaA"),
                                        (-139.6, 405.0, math.pi / 2, 7.0, 3, "lenhaB"),
                                        (-103.0, 427.0, 0.25, 6.0, 3, "lenhaC")):
        F = Frame(wx, wy, T4, ang)
        woodpile(mb, F, ln, rows, key)
        col_box("DS_FrgCoal", (ln + 1.2, 2.4, 0.66 * rows + 0.6), (wx, wy, T4 + (0.66 * rows + 0.6) / 2), (0, 0, ang))
    chopping_block(mb, -127.0, 414.5, 0.5)
    col_box("DS_FrgCoal", (1.4, 1.4, 1.2), (-127.0, 414.5, T4 + 0.6))
    # CARVAO PRONTO (sudeste da boca): 2 pilhas de tawara (3-2-1, deitados lado a lado), cestos, bancada de ensacar
    # (a trilha do ds_terrain chega na boca vindo de sudeste por (-68, 376) -> (-106, 390): nada fica sobre ela)
    for (sx_, sy_, key, rows_) in ((-91.5, 392.6, "pilhaA", (3, 2, 1)), (-111.8, 385.8, "pilhaB", (2, 1))):
        for row, cnt in enumerate(rows_):
            for i in range(cnt):
                xx = sx_ + (i - (cnt - 1) / 2) * 1.04
                tawara(mb, mb, xx, sy_ + (_hh(key, row, i) - 0.5) * 0.25, T4 + row * 0.9,
                       math.pi / 2 + 0.05 * (_hh(key, "a", row, i) - 0.5), lod=1)
        col_box("DS_FrgCoal", (3.4, 1.8, 2.7), (sx_, sy_, T4 + 1.35))
    for (bx_, by_, s_) in ((-114.6, 391.5, 1.0), (-116.4, 392.4, 0.85), (-96.0, 397.6, 0.8)):
        basket(mb, bx_, by_, T4, 0.55 * s_, 0.62 * s_)
    # bancada de ensacar (tampo de tabua, 4 pes, travessas) com um cesto e um saco aberto em cima
    F = Frame(-97.5, 399.8, T4, 0.0)
    bb(mb, F, -1.5, 1.5, -0.5, 0.5, 0.95, 1.08, WM)
    for sx in (-1.3, 1.3):
        for sy in (-0.36, 0.36):
            bb(mb, F, sx - 0.09, sx + 0.09, sy - 0.09, sy + 0.09, 0.0, 0.95, WD)
        bb(mb, F, sx - 0.06, sx + 0.06, -0.36, 0.36, 0.3, 0.42, WD)
    bb(mb, F, -1.3, 1.3, -0.05, 0.05, 0.3, 0.42, WD)
    basket(mb, -98.3, 399.8, T4 + 1.08, 0.42, 0.5)
    tawara(mb, mb, -96.7, 399.9, T4 + 1.08, 0.0, 0.85, lod=1)
    col_box("DS_FrgCoal", (3.2, 1.2, 1.4), (-97.5, 399.8, T4 + 0.7))
    # carrinho de levar o carvao para a forja (varais para nordeste, no chao)
    cart(mb, -88.0, 403.5, 0.6)
    col_box("DS_FrgCoal", (4.4, 2.6, 2.4), (-88.0 + 1.0 * math.cos(0.6), 403.5 + 1.0 * math.sin(0.6), T4 + 1.2),
            (0, 0, 0.6))
    K.lantern_post(mb, Frame(-92.0, 410.0, T4, math.pi), 8.0, 1.8, "L_DSProp_Lamp_FrgCoal", 36.0)
    col_box("DS_FrgCoal", (1.6, 1.6, 8.0), (-92.0, 410.0, T4 + 4.0))


# ================================================================== COLISAO DO SALAO E LUZES
def hall_cols():
    A = "DS_FrgHall"
    zt = ZB + HH
    col_box(A, (1.6, HD + 1.2, zt - T4), (HX0 + 0.2, HC[1], (T4 + zt) / 2))
    col_box(A, (1.6, HD + 1.2, zt - T4), (HX1 - 0.2, HC[1], (T4 + zt) / 2))
    col_box(A, (HW + 1.2, 1.6, zt - T4), (HC[0], HY1 - 0.2, (T4 + zt) / 2))
    for s in (-1, 1):
        a, b = sorted((s * BLK[1], s * (HW / 2 + 0.6)))
        col_box(A, (b - a, 1.6, zt - T4), ((a + b) / 2, HY0 + 0.2, (T4 + zt) / 2))
        a, b = sorted((s * (AR0 + 0.05), s * BLK[1]))
        col_box(A, (b - a, BBY - BFY + 0.3, BTOP - T4), ((a + b) / 2, (BFY + BBY) / 2, (T4 + BTOP) / 2))
    col_box(A, (AW, BBY - BFY + 0.3, BTOP - (ASPR + AR0 - 0.4)), (0.0, (BFY + BBY) / 2, (ASPR + AR0 - 0.4 + BTOP) / 2))
    col_box(A, (HW - 1.6, HY1 - BFY + 0.6, DOMA - T4 + 0.4), (0.0, (HY1 + BFY) / 2 - 0.8, (T4 - 0.4 + DOMA) / 2))
    col_box(A, (8.8, 8.4, 3.2), (0.0, 494.6, DOMA + 1.4))                  # hodo
    col_box(A, (10.2, 1.6, 8.0), (0.0, 499.2, DOMA + 4.0))
    col_box(A, (2.6, 6.6, 2.8), (-7.5, 490.1, DOMA + 1.4))                 # fuigo
    col_box(A, (2.4, 2.0, 2.0), (MX, 487.0, DOMA + 1.0))                   # bigorna
    col_box(A, (5.6, 2.6, 1.5), (7.3, 485.4, DOMA + 0.75))                 # cocho
    col_box(A, (4.6, 6.6, 1.4), (7.6, 494.2, DOMA + 0.7))                  # carvao
    col_box(A, (3.6, 1.6, 2.0), (13.35, 497.5, DOMA + 1.0))
    for x in (-11.0, 11.0):
        col_box(A, (1.3, 1.3, HH), (x, 482.0, DOMA + HH / 2))
    col_box(A, (3.4, 2.6, 3.4), (12.6, 477.4, DOMA + 1.7), (0, 0, 0.25))   # kake
    col_box("DS_FrgTower", (17.2, 17.2, TB + TS1 + TS2), (TX, TY, T4 + (TB + TS1 + TS2) / 2))


def lights():
    light("L_DSFrg_Furnace", "POINT", (0.0, 494.4, DOMA + 3.6), 2600.0, FIREC, 1.0)
    light("L_DSFrg_FurnaceMouth", "POINT", (0.0, HY0 + 1.5, ASPR + 1.5), 700.0, (1.0, 0.5, 0.2), 0.8)
    light("L_DSFrg_TowerWin", "POINT", (TX, TY, T4 + TB + TS1 + 8.0), 320.0, WARM, 0.6)


# ================================================================== CAMERAS da zona (folhas da onda 2b)
CAMS = {
    "CAM_DSFrg_Hero": ((70.0, 372.0, 128.0), (2.0, 488.0, 100.0), 26),
    "CAM_DSFrg_HeroLow": ((-46.0, 404.0, 86.0), (6.0, 486.0, 104.0), 24),
    "CAM_DSFrg_PH_Yard": ((4.0, 440.0, T4 + L.EYE), (0.0, 486.0, 89.0), 24),
    "CAM_DSFrg_Mouth": ((5.0, 452.0, T4 + 6.2), (0.0, 470.0, 89.5), 30),
    "CAM_DSFrg_Interior": ((-11.5, 474.0, DOMA + 5.0), (1.5, 493.5, DOMA + 2.6), 22),
    "CAM_DSFrg_Hodo": ((3.8, 484.5, DOMA + 4.6), (-1.0, 494.5, DOMA + 2.6), 26),
    "CAM_DSFrg_Swords": ((13.6, 459.0, T4 + 3.2), (15.4, 466.1, T4 + 2.0), 34),
    "CAM_DSFrg_SwordTsuka": ((13.0, 463.2, T4 + 2.2), (13.7, 465.5, T4 + 1.55), 40),
    "CAM_DSFrg_SwordKissaki": ((17.2, 463.0, T4 + 2.2), (17.9, 465.5, T4 + 1.5), 40),
    "CAM_DSFrg_Tower": ((70.0, 432.0, 96.0), (37.0, 493.0, 122.0), 24),
    "CAM_DSFrg_Wheel": ((116.0, 462.0, 88.0), (88.0, 490.0, 92.0), 24),
    "CAM_DSFrg_Mill": ((83.0, 463.0, 87.5), (82.5, 487.0, 89.5), 26),
    "CAM_DSFrg_Aqueduct": ((128.0, 484.0, 108.0), (96.0, 520.0, 98.0), 26),
    "CAM_DSFrg_Coal": ((-84.0, 422.0, 94.0), (-112.0, 400.0, 83.0), 26),
    "CAM_DSFrg_West": ((-38.0, 448.0, 88.0), (-52.0, 488.0, 94.0), 24),
}


# ================================================================== BUILD
def flume_marker():
    """WATER_Flume e desta zona (ds_core cria, ds_water nao toca): os 3 pontos da planta + o BICO sobre o topo da roda
    (a agua cai na pa de cima); o poco da roda fica com a agua no nivel da calha de pedra do ds_water (80,64)"""
    o = bpy.data.objects.get("WATER_Flume")
    if o is None:
        return
    pts = _flume_pts()
    o["waypoints"] = ";".join("%.2f,%.2f,%.2f" % tuple(p) for p in pts)
    o["widths"] = ",".join("2.0" for _ in pts)
    o["pit_level"] = round(T4 + 0.44, 2)
    o["pit_rect"] = "%.1f,%.1f,%.1f,%.1f" % (WX - 2.7, WY - 11.3, WX + 2.7, WY + 11.3)
    o["note"] = ("aqueduto de madeira: nascente -> bico 4,2 ao norte do topo da roda (a agua cai nas cacambas); "
                 "poco da roda (pit_rect, agua pit_level) -> saida no muro leste x 95,2, y 482 +- 1,75 -> calha ds_water")


def drop_blockout_forge():
    for o in [o for o in bpy.data.objects if o.name.startswith(("DS_Frg_Blockout", "COL_DS_Frg"))]:
        bpy.data.objects.remove(o, do_unlink=True)


def build():
    """objetos agrupados por familia de material (cada material de cada objeto vira 1 MeshPart no export)"""
    drop_blockout_forge()
    PAVED.clear()
    bpy.context.view_layer.update()
    mh = MB("DS_Frg_Hall", C, random.Random(4401), detail="hero")       # salao + bloco da boca + empenas + lanternim
    mi = MB("DS_Frg_Smithy", C, random.Random(4402), detail="hero")     # fornalha, ferro, aco, brasas, espadas, moveis
    zr = hall(mh, mi)
    hall_interior(mi, mi, zr)
    yard_props(mi, mi)
    hall_cols()
    mh.finish()
    mb = MB("DS_Frg_Houses", C, random.Random(4404), detail="near")     # torre-chamine + oficina-residencia
    tower(mb, mi)
    workshop(mb)
    mb.finish()
    mm = MB("DS_Frg_Mill", C, random.Random(4406), detail="near")       # ala leste + moinho + poco + aqueduto
    east_wing(mm)
    mill(mm, mm)
    flume(mm, mm)
    mm.finish()
    wheel()
    mg = MB("DS_Frg_Ground", C, random.Random(4409), detail="near")     # patio, escadas, patamar, cercas, lanternas
    yard(mg)
    yard_dressing(mg, mi)                                               # ONDA 6b: adro, trilha, sulco, manchas
    stairs_and_landing(mg, mg)
    edges(mg, mg)
    mg.finish()
    mc = MB("DS_Frg_Coal", C, random.Random(4412), detail="near")
    coal_yard(mc, mi)
    mc.finish()
    mi.finish()
    lights()
    flume_marker()
