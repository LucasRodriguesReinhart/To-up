# ds_props - PROPS da Ilha 4 (DEMON SLAYER), onda 3b (PLANO_DS secoes 5, 7 e 12 - fase 11; PROMPT_USUARIO secoes 18,
# 19, 25, 26, 33, 34, 37 e 41). Prefixo DS_Prop_ (dono "props"), colecao 09_PROPS. Luzes L_DSProp_Lamp_* (NightOnly).
#
# REGRA: poucos TIPOS, bem feitos, repetidos (cada tipo e UMA funcao; as instancias variam so por escala/rumo/estado).
#   taru (barril de aduelas com aros de bambu trancado e tampa rebaixada) | oke (tina baixa com agua) | kame (pote
#   de agua vidrado com tampa de tabuas) | hachi (vaso com planta de folhas laminadas) | tawara (fardo de palha com
#   tampas sandawara e amarras: ARROZ na vila, CARVAO na forja) | monohoshi (varal: 2 cavaletes de bambu em X, vara,
#   yukata em T e tenugui dobrado) | hatake (horta: canteiros em monte com borda de tabua, fileiras de folhas, trelica
#   de bambu em A) | toishi-guruma (rebolo de pedra com manivela sobre cocho d'agua) | daihachi (carrinho de mao de 2
#   rodas raiadas, parado com os varais no chao) | makiba (lenha rachada entre mouroes com coberta de tabuas) |
#   zaru/kago (peneira e cesto de bambu) | nodate-gasa (guarda-sol de papel da chaya) | tora (vagonete de madeira VAZIO,
#   cintas de ferro) | tsuruhashi/shaberu (picareta e pa encostadas) | kui (estacas de marcacao com corda e fita) |
#   tamahagane-bako (caixote de barras de aco forjado - BARRAS chatas, nada de pepita/cristal) | togi-dai (cavalete de
#   afiar com pedras e balde) | pedras de jardim (a lingua das pedras de borda do ds_terrain).
# Kit (ds_kit, SO LEITURA): bench (shogi), railing (cerca baixa de borda da clareira), lantern_post (lanternas de no).
#
# ONDE (intencao, PLANO secao 5 - densidade da vila media-alta, clareira VAZIA no meio e media na borda):
#   VILA  nos PROP_ANCHORS do ds_village (horta e varal do V2, cestos na engawa, rebolo/tabuas/barril da oficina V3,
#         banco + guarda-sol na frente da chaya V1, arroz/barris/carrinho do kura V4, vasos e pote do V5, varal dos
#         fundos do V5, pedras do jardim do V6, banco do mirante do T2) + lenha sob o beiral norte do V2.
#   CLAREIRA  so a BORDA: cerca baixa em 4 SETORES (bambuzal dos 2 lados da rampa, junto da vila - aberta perto do
#         oratorio -, pe da SubidaA dos 2 lados), canto dos mineiros junto do poco (vagonete vazio, picareta, pa, balde,
#         cesto), estacas de marcacao nos 4 cantos da MiningZone (fora dela). Nada colidivel na zona; nada que leia
#         minerio. A cerca do blockout (DS_Clr_Edges) sai daqui.
#   FORJA patio de trabalho: pilha de carvao em tawara, caixote de tamahagane e cavalete de afiar a leste (junto da
#         estacao de polimento), bancos virados para a boca; a oeste banco + fardos junto da oficina. Rotas livres.
#   NOS   lanternas de poste do kit nos nos da clareira (topo da Trilha, antecampo, pe da subida, pe da escada do
#         summon, bambuzal): as do blockout nao existem no build detalhado.
# ONDA 4b (4b-PROPS): lanternas de caminho em fileira, cercas baixas em setores e vida - secao "ONDA 4b: DENSIDADE".
# Colisao: so no que bloqueia (barris, potes, fardos, carrinhos, rebolo, lenha, caixote, cercas e postes); props
# pequenos sem colisao; nada dentro de rota/porta (ver PROP_KEEP_OUT e o QA de rotas).
import math, os, zlib
import bpy, bmesh
from mathutils import Vector, Matrix
import ds_lib as DL
from ds_lib import MB, Frame, light, col_box
import ds_layout as L
import ds_kit as K
from ds_kit import sub, bb, bx, lathe, ext, loft, beam, even, rock_base

T0, T1, T2, T3, T4 = L.T0, L.T1, L.T2, L.T3, L.T4
C = "09_PROPS"
WD, WM = K.WD, K.WM
BD, BG = "Bamboo_DS_Dry", "Bamboo_DS"
STRAW = "Rope_DS_Straw"
SOOT = "Stone_DS_Soot"
IRON = K.IRON
ST, STD = K.ST, K.STD
DIRTD = "Dirt_DS_Dark"
LEAF = "Leaf_DS_Shrub"
LINEN, AI = "Cloth_DS_Linen", "Cloth_DS_Ai"
WATER = "Water_DS_Trough"
AREA = "DS_Prop"
LOW_BEVEL = (0.07, 0.5)          # mesmo opt-in da vila para as pecas do kit (cerca/banco/lanterna): chanfro < 0,07 sai


def hh(*a):
    s = "|".join("%.2f" % v if isinstance(v, float) else str(v) for v in a)
    return (zlib.crc32(s.encode("utf-8")) & 0xffffffff) / 4294967296.0


# ================================================================== chao (raycast) e geometria orientada
GROUND_PRE = ("DS_Ter_", "DS_Clr_", "DS_Vil_", "DS_Frg_Ground", "DS_Ent_Court", "DS_Exit_Path", "DS_Water_")


def ground(x, y, z_hint, up=3.0, down=6.0):
    """topo do chao VISUAL em (x, y) (pele do terreno, grama, lajes, tabuado da engawa); z_hint se nada"""
    dg = bpy.context.evaluated_depsgraph_get()
    sc = bpy.context.scene
    o = Vector((x, y, z_hint + up))
    d = Vector((0.0, 0.0, -1.0))
    for _ in range(16):
        hit, loc, nrm, idx, ob, mtx = sc.ray_cast(dg, o, d, distance=up + down)
        if not hit:
            return z_hint
        if ob.name.startswith(GROUND_PRE) and nrm.z > 0.6:
            return loc.z
        o = loc + d * 0.02
    return z_hint


def gz(x, y, z_hint, up=3.0):
    """chao para assentar um prop: um pouco abaixo da superficie (base enterrada 0,06: sem fresta, sem z-fight)"""
    return ground(x, y, z_hint, up) - 0.06


def obox(mb, c, A, N, size, m, bev=0.0):
    """caixa orientada: centro c, eixo A (comprimento = size[0]) e normal N (espessura = size[2])"""
    A = Vector(A).normalized()
    N = Vector(N)
    N = (N - A * N.dot(A)).normalized()
    Bv = N.cross(A)
    M = Matrix((A, Bv, N)).transposed()
    mb.box(size, tuple(c), tuple(M.to_euler()), m, bev)


def bar(mb, pts, wf, hf, up, m, tip=False):
    """barra de secao retangular ao longo de pts (mundo); largura wf(t) e altura hf(t), t 0..1; tip = ponta em leque"""
    P = [Vector(p) for p in pts]
    n = len(P)
    up = Vector(up)
    bm = mb.bm
    rings = []
    for i, p in enumerate(P):
        t = (P[min(i + 1, n - 1)] - P[max(i - 1, 0)]).normalized()
        s = t.cross(up).normalized()
        v = s.cross(t).normalized()
        k = i / (n - 1)
        w, h = wf(k) / 2, hf(k) / 2
        rings.append([p - s * w - v * h, p + s * w - v * h, p + s * w + v * h, p - s * w + v * h])
    V = [[bm.verts.new(tuple(q)) for q in r] for r in rings[:-1 if tip else None]]
    fs = []
    for a, b in zip(V, V[1:]):
        for j in range(4):
            fs.append(bm.faces.new((a[j], a[(j + 1) % 4], b[(j + 1) % 4], b[j])))
    fs.append(bm.faces.new(list(reversed(V[0]))))
    extra = []
    if tip:
        vt = bm.verts.new(tuple(P[-1]))
        extra = [vt]
        for j in range(4):
            fs.append(bm.faces.new((V[-1][j], V[-1][(j + 1) % 4], vt)))
    else:
        fs.append(bm.faces.new(V[-1]))
    bmesh.ops.recalc_face_normals(bm, faces=fs)
    mb._post([v for r in V for v in r] + extra, m, None, 0, 1)


def leaf(mb, base, yaw, pitch, ln, w, m=LEAF, droop=0.35, th=0.06):
    """folha laminada (losango com espessura, ponta caida): base (mundo), rumo, inclinacao, comprimento, largura"""
    d = Vector((math.cos(yaw) * math.cos(pitch), math.sin(yaw) * math.cos(pitch), math.sin(pitch)))
    s = Vector((-math.sin(yaw), math.cos(yaw), 0.0))
    b = Vector(base)
    dz = Vector((0.0, 0.0, -droop * ln))
    pts = [b, b + d * ln * 0.45 + s * w / 2 + dz * 0.25, b + d * ln + dz, b + d * ln * 0.45 - s * w / 2 + dz * 0.25]
    nv = s.cross(d).normalized() * th
    bm = mb.bm
    top = [bm.verts.new(tuple(p + nv)) for p in pts]
    bot = [bm.verts.new(tuple(p)) for p in pts]
    fs = [bm.faces.new(top), bm.faces.new(list(reversed(bot)))]
    for j in range(4):
        fs.append(bm.faces.new((bot[j], bot[(j + 1) % 4], top[(j + 1) % 4], top[j])))
    bmesh.ops.recalc_face_normals(bm, faces=fs)
    mb._post(top + bot, m, None, 0, 1)


def rosette(mb, x, y, z, s=1.0, key=0, n=6, m=LEAF):
    """planta de horta/vaso: n folhas laminadas em roseta (rumo e inclinacao dirigidos por hash, nada de esfera)"""
    for i in range(n):
        a = 2 * math.pi * (i + 0.37 * hh(key, i, "a")) / n
        p = math.radians(38.0 + 30.0 * hh(key, i, "p"))
        leaf(mb, (x, y, z), a, p, s * (0.95 + 0.45 * hh(key, i, "l")), s * 0.55, m, 0.3)


# ================================================================== RECIPIENTES DE MADEIRA (taru / oke)
def _hoop(mb, F, x, y, z, r, m=BD, hw=0.12, out=0.13, n=14):        # 6b (item 54): aro 0,13 fora (era 0,07)
    lathe(mb, F, (x, y, z), [(r - 0.05, -hw), (r + out, -hw * 0.8), (r + out, hw * 0.8), (r - 0.05, hw)], n, m,
          0.0, (False, False))


def taru(mb, F, x, y, s=1.0, top="lid", n=14):
    """barril de aduelas (a faceta plana de cada lado do 14-gono e uma aduela), 3 aros de bambu trancado (taga),
    borda das aduelas 0,2 acima da tampa; tampa de tabuas com 2 travessas (top='lid') ou agua parada ('water')"""
    prof = [(0.9, 0.0), (0.98, 0.5), (1.0, 1.15), (0.97, 1.8), (0.9, 2.35)]
    prof = [(r * s, z * s) for r, z in prof]
    rt, zt = prof[-1]
    inner = rt - 0.14 * s
    zl = zt - (0.2 if top == "lid" else 0.45) * s
    rings = [[(x + r * math.cos(2 * math.pi * j / n), y + r * math.sin(2 * math.pi * j / n), z) for j in range(n)]
             for r, z in prof]
    rings += [[(x + inner * math.cos(2 * math.pi * j / n), y + inner * math.sin(2 * math.pi * j / n), z)
               for j in range(n)] for z in (zt, zl)]
    loft(mb, F, rings, WM, caps=(True, top == "lid"))
    if top == "water":
        lathe(mb, F, (x, y, zl + 0.08 * s), [(inner + 0.03, 0.0), (inner + 0.03, 0.05)], n, WATER)
    else:
        for k in (-1, 1):
            bb(mb, F, x - inner * 0.82, x + inner * 0.82, y + k * inner * 0.42 - 0.09, y + k * inner * 0.42 + 0.09,
               zl - 0.04, zl + 0.08, WD)
    for zz in (0.42, 1.15, 1.92):
        rz = (0.98 if zz < 1.0 else (1.0 if zz < 1.5 else 0.96)) * s
        _hoop(mb, F, x, y, zz * s, rz, BD, 0.12 * s, 0.13, n)


def oke(mb, F, x, y, s=1.0, n=14):
    """tina baixa de aduelas (tarai) com 2 aros e agua 0,3 abaixo da borda"""
    prof = [(1.08 * s, 0.0), (1.2 * s, 0.85 * s)]
    inner = prof[-1][0] - 0.12 * s
    zt = prof[-1][1]
    rings = [[(x + r * math.cos(2 * math.pi * j / n), y + r * math.sin(2 * math.pi * j / n), z) for j in range(n)]
             for r, z in prof]
    rings += [[(x + inner * math.cos(2 * math.pi * j / n), y + inner * math.sin(2 * math.pi * j / n), z)
               for j in range(n)] for z in (zt, zt - 0.32 * s)]
    loft(mb, F, rings, WM, caps=(True, False))           # sem tampa interna: a agua e o unico plano ali
    lathe(mb, F, (x, y, zt - 0.32 * s), [(inner + 0.03, -0.02), (inner + 0.03, 0.03)], n, WATER)
    for zz, rr in ((0.2, 1.11), (0.66, 1.17)):
        _hoop(mb, F, x, y, zz * s, rr * s, BD, 0.09 * s, 0.13, n)


def kame(mb, F, x, y, s=1.0, n=12):
    """pote de agua vidrado escuro (kame): ombro largo, gargalo curto com labio, tampa de 2 tabuas e pegador"""
    prof = [(0.55, 0.0), (0.82, 0.3), (1.05, 0.85), (1.08, 1.2), (0.92, 1.62), (0.66, 1.86), (0.62, 1.94),
            (0.72, 2.0), (0.7, 2.1), (0.56, 2.1)]
    lathe(mb, F, (x, y, 0.0), [(r * s, z * s) for r, z in prof], n, STD)
    zt = 2.1 * s
    for k in (-1, 1):
        bb(mb, F, x - 0.82 * s, x + 0.82 * s, y + k * 0.36 * s - 0.33 * s, y + k * 0.36 * s + 0.33 * s, zt - 0.04,
           zt + 0.12, WM, 0.03)
    bb(mb, F, x - 0.1, x + 0.1, y - 0.5 * s, y + 0.5 * s, zt + 0.1, zt + 0.32, WD, 0.03)


def hachi(mb, F, x, y, s=1.0, key=0):
    """vaso de ceramica escura com terra e planta de folhas laminadas"""
    lathe(mb, F, (x, y, 0.0), [(0.42 * s, 0.0), (0.56 * s, 0.78 * s), (0.64 * s, 0.84 * s), (0.62 * s, 0.94 * s),
                               (0.5 * s, 0.94 * s), (0.48 * s, 0.7 * s)], 8, STD, 0.0, (True, False))
    lathe(mb, F, (x, y, 0.0), [(0.52 * s, 0.7 * s), (0.52 * s, 0.82 * s)], 8, DIRTD)      # terra 0,12 abaixo da boca
    p = F.p(x, y, 0.8 * s)
    rosette(mb, p.x, p.y, p.z, 1.15 * s, key, 7)


# ================================================================== FARDO DE PALHA (tawara): arroz / carvao
def tawara(mb, F, x, y, z, ang, s=1.0, charcoal=False, n=8):
    """fardo de palha deitado (eixo ao longo de 'ang'): corpo em barril, tampas sandawara (disco de palha mais
    largo), 2 amarras de corda e a costura de cima; carvao: miolo preto aparecendo nas tampas"""
    Fa = sub(F, x, y, z, ang)
    R = 0.62 * s

    def ring(u, r, dz=0.0):
        return [(u, r * math.cos(2 * math.pi * j / n + math.pi / n), R + dz + r * math.sin(2 * math.pi * j / n + math.pi / n))
                for j in range(n)]
    prof = [(-0.86, 0.5), (-0.72, 0.6), (-0.36, 0.64), (0.0, 0.66), (0.36, 0.64), (0.72, 0.6), (0.86, 0.5)]
    loft(mb, Fa, [ring(u * s, r * s) for u, r in prof], STRAW)
    for e in (-1, 1):                                   # tampas (sandawara): disco mais largo, levemente saliente
        u0 = e * 0.84 * s
        loft(mb, Fa, [ring(u0, 0.54 * s), ring(u0 + e * 0.12 * s, 0.56 * s), ring(u0 + e * 0.18 * s, 0.46 * s)],   # 6b: 0,16
             BD if not charcoal else STRAW)
        if charcoal:
            loft(mb, Fa, [ring(u0 + e * 0.2 * s, 0.34 * s), ring(u0 + e * 0.32 * s, 0.3 * s)], SOOT)    # 6b: 0,14 fora
    for u in (-0.42, 0.42):                             # amarras
        u *= s
        r = 0.65 * s
        loft(mb, Fa, [ring(u - 0.08, r - 0.03), ring(u - 0.05, r + 0.05), ring(u + 0.05, r + 0.05),
                      ring(u + 0.08, r - 0.03)], WM if charcoal else STRAW, caps=(False, False))
    bx(mb, Fa, 0.0, 0.0, R + 0.66 * s, 1.7 * s, 0.12, 0.08, WM if charcoal else STRAW)   # costura de cima


def tawara_pile(mb, F, x, y, ang, rows=(3, 2, 1), s=1.0, charcoal=False, key=0):
    """pilha em piramide (fardos de lado a lado); devolve (largura, altura) da pilha"""
    d = 1.3 * s
    for k, nrow in enumerate(rows):
        for i in range(nrow):
            off = (i - (nrow - 1) / 2) * d
            jit = (hh(key, k, i) - 0.5) * 0.25
            px = x + math.cos(ang + math.pi / 2) * off + math.cos(ang) * jit
            py = y + math.sin(ang + math.pi / 2) * off + math.sin(ang) * jit
            tawara(mb, F, px, py, k * 1.08 * s, ang + (hh(key, k, i, "r") - 0.5) * 0.12, s, charcoal)
    return d * rows[0], len(rows) * 1.08 * s + 0.2


# ================================================================== VARAL (monohoshi)
def monohoshi(mb, F, L_=7.0, key=0, cloths=("yukata", "tenugui", "tenugui2")):
    """2 cavaletes de bambu em X amarrados, vara de bambu com nos, yukata em T pendurado pelas mangas e tenugui
    dobrados sobre a vara (pano com espessura, dobra redonda por cima). F no meio, vara ao longo de x"""
    zt = 5.3
    for sx in (-1, 1):
        x = sx * L_ / 2
        for sy in (-1, 1):
            mb.rod(F.p(x, sy * 1.35, -0.1), F.p(x, -sy * 0.32, zt + 0.55), 0.12, BD, 6)
        mb.rod(F.p(x - 0.2, 0.0, zt - 0.02), F.p(x + 0.2, 0.0, zt - 0.02), 0.2, STRAW, 6)     # amarra da cruz
    mb.rod(F.p(-L_ / 2 - 0.7, 0.0, zt + 0.16), F.p(L_ / 2 + 0.7, 0.0, zt + 0.16), 0.13, BD, 6)
    for xx in (-L_ / 4, L_ / 4):                                                          # nos da vara
        mb.rod(F.p(xx - 0.05, 0.0, zt + 0.16), F.p(xx + 0.05, 0.0, zt + 0.16), 0.16, BD, 6)
    zp = zt + 0.16
    x = -L_ / 2 + 0.8
    for c in cloths:
        if c == "yukata":                               # T: mangas + corpo, gola em V, 0,1 de espessura
            w, sl = 2.4, 4.4
            poly = [(-sl / 2, 0.0), (sl / 2, 0.0), (sl / 2, -1.5), (w / 2, -1.5), (w / 2 + 0.12, -3.9), (-w / 2 - 0.12, -3.9),
                    (-w / 2, -1.5), (-sl / 2, -1.5)]
            cx = x + sl / 2
            Fy = sub(F, cx, 0.0, zp - 0.12)
            ext(mb, Fy, poly, "y", -0.06, 0.06, AI)
            # gola (eri) clara: desce do pescoco cruzando para a esquerda (okumi), so nas 2 faces
            for sy in (-1, 1):
                y0, y1 = (0.06, 0.2) if sy > 0 else (-0.2, -0.06)          # 6b (item 54): 0,14 a frente (era 0,04)
                ext(mb, Fy, [(-0.42, 0.02), (-0.12, 0.02), (0.52, -1.6), (0.38, -3.85), (0.16, -3.85), (0.3, -1.6)],
                    "y", y0, y1, LINEN)
                ext(mb, Fy, [(0.12, 0.02), (0.42, 0.02), (0.08, -0.7), (-0.12, -0.55)], "y", y0, y1, LINEN)
                for xs in (-1, 1):                    # bainha da manga (furi) e barra: tom claro estreito
                    bb(mb, Fy, xs * sl / 2 - (0.0 if xs > 0 else -0.0) - (1.0 if xs > 0 else 0.0),
                       xs * sl / 2 + (0.0 if xs > 0 else 1.0), y0, y1, -1.5, -1.36, LINEN)
            x += sl + 0.5
        else:                                           # tenugui dobrado sobre a vara
            w = 1.1 if c == "tenugui" else 1.4
            la, lb = (1.7, 1.3) if c == "tenugui" else (1.4, 1.9)
            r0, r1 = 0.15, 0.25
            poly = [(-r1, -la), (-r1, 0.0)] + [(-r1 * math.cos(a), r1 * math.sin(a))
                                               for a in (math.radians(v) for v in (40, 90, 140))] + \
                   [(r1, 0.0), (r1, -lb), (r0, -lb), (r0, 0.0)] + \
                   [(r0 * math.cos(a), r0 * math.sin(a)) for a in (math.radians(v) for v in (40, 90, 140))] + \
                   [(-r0, 0.0), (-r0, -la)]
            ext(mb, sub(F, 0.0, 0.0, zp), poly, "x", x, x + w, LINEN if c == "tenugui" else AI)
            x += w + 0.45


# ================================================================== HORTA (hatake)
def hatake(mb, F, n_beds=2, Lb=7.0, Wb=2.2, key=0, trellis=True):
    """canteiros em monte de terra escura com borda de tabua baixa, 2 fileiras de folhas por canteiro; trelica de
    bambu em A (feijao) no ultimo canteiro, com folhas subindo; F no meio, canteiros ao longo de x"""
    gap = 1.3
    for b in range(n_beds):
        yc = (b - (n_beds - 1) / 2) * (Wb + gap)
        ext(mb, F, [(yc - Wb / 2, -0.1), (yc + Wb / 2, -0.1), (yc + Wb / 2, 0.38), (yc + Wb / 2 - 0.35, 0.58),
                    (yc - Wb / 2 + 0.35, 0.58), (yc - Wb / 2, 0.38)], "x", -Lb / 2, Lb / 2, DIRTD)
        for s in (-1, 1):                                       # tabuas de borda (6b: 0,16 fora do monte)
            bb(mb, F, -Lb / 2 - 0.16, Lb / 2 + 0.16, yc + s * (Wb / 2 + 0.1) - 0.08, yc + s * (Wb / 2 + 0.1) + 0.08,
               -0.12, 0.42, WM)
        for s in (-1, 1):
            bb(mb, F, s * (Lb / 2 + 0.08) - 0.08, s * (Lb / 2 + 0.08) + 0.08, yc - Wb / 2 - 0.14, yc + Wb / 2 + 0.14,
               -0.12, 0.42, WM)
        last = b == n_beds - 1 and trellis
        if not last:
            for r in (-0.5, 0.5):
                for i, xx in enumerate(even(-Lb / 2 + 0.3, Lb / 2 - 0.3, 1.35)):
                    p = F.p(xx + (hh(key, b, r, i) - 0.5) * 0.3, yc + r, 0.52)
                    rosette(mb, p.x, p.y, p.z, 0.62 + 0.18 * hh(key, b, r, i, "s"), (key, b, r, i), 5)
        else:                                                   # trelica em A (2 fileiras de varas cruzadas no topo)
            xs = even(-Lb / 2 + 0.2, Lb / 2 - 0.2, 1.4)
            for i, xx in enumerate(xs):
                for s in (-1, 1):
                    mb.rod(F.p(xx, yc + s * 0.75, 0.3), F.p(xx, yc - s * 0.22, 3.6), 0.07, BD, 5)
                for k in range(3):                              # folhas subindo pela vara
                    p = F.p(xx + 0.1, yc + 0.55 - k * 0.22, 0.9 + k * 0.85)
                    leaf(mb, (p.x, p.y, p.z), F.a + math.pi / 2 * (1 if k % 2 else -1) + 0.3 * hh(key, i, k),
                         math.radians(25), 0.75, 0.45, LEAF, 0.2)
            mb.rod(F.p(xs[0] - 0.5, yc, 3.35), F.p(xs[-1] + 0.5, yc, 3.35), 0.08, BD, 5)


# ================================================================== CESTOS (zaru / kago) e GUARDA-SOL
def zaru(mb, F, x, y, z, s=1.0, tilt=0.0):
    """peneira rasa de bambu (zaru) com aro de bambu escuro"""
    lathe(mb, F, (x, y, z), [(0.25 * s, 0.0), (0.7 * s, 0.1 * s), (0.9 * s, 0.24 * s), (0.82 * s, 0.24 * s),
                             (0.64 * s, 0.14 * s), (0.2 * s, 0.06 * s)], 10, BD)
    lathe(mb, F, (x, y, z + 0.2 * s), [(0.86 * s, 0.0), (0.95 * s, 0.03), (0.95 * s, 0.09), (0.86 * s, 0.1)], 10, WM,
          0.0, (False, False))


def kago(mb, F, x, y, z=0.0, s=1.0):
    """cesto alto de costas (seoi-kago): corpo conico de bambu trancado (faixas em 2 tons), boca com aro, alcas"""
    lathe(mb, F, (x, y, z), [(0.42 * s, 0.0), (0.55 * s, 0.5 * s), (0.7 * s, 1.5 * s), (0.76 * s, 1.62 * s),
                             (0.64 * s, 1.62 * s), (0.6 * s, 1.35 * s)], 10, BD)
    for zz, rr in ((0.12, 0.45), (0.85, 0.61)):
        lathe(mb, F, (x, y, z + zz * s), [(rr * s - 0.03, -0.08), (rr * s + 0.04, -0.06), (rr * s + 0.04, 0.06),
                                          (rr * s - 0.03, 0.08)], 10, WM, 0.0, (False, False))
    for k in (-1, 1):
        mb.rod(F.p(x - 0.3 * s, y + k * 0.5 * s, z + 1.5 * s), F.p(x - 0.36 * s, y + k * 0.42 * s, z + 0.4 * s),
               0.06, STRAW, 5)


def nodate_gasa(mb, F, x, y, z=0.0, r=2.9, h=6.4):
    """guarda-sol de papel da casa de cha (nodate-gasa): pe em pedra, haste de bambu, cupula de papel aizome em 16
    gomos com borda viva, 8 varetas por baixo ate o anel, ponteira"""
    rock_base(mb, F, x, y, z, 0.7, 0.35)
    mb.rod(F.p(x, y, z + 0.2), F.p(x, y, z + h + 0.9), 0.13, BD, 6)
    n = 16
    ring = lambda rr, zz: [(x + rr * math.cos(2 * math.pi * j / n), y + rr * math.sin(2 * math.pi * j / n), z + zz)
                           for j in range(n)]
    loft(mb, F, [ring(0.22, h + 0.92), ring(r * 0.55, h + 0.66), ring(r, h), ring(r - 0.06, h - 0.1),
                 ring(r * 0.55, h + 0.54), ring(0.22, h + 0.8)], AI)
    for j in range(8):
        a = 2 * math.pi * (j + 0.5) / 8
        mb.rod(F.p(x + math.cos(a) * 0.2, y + math.sin(a) * 0.2, z + h - 1.1),
               F.p(x + math.cos(a) * r * 0.62, y + math.sin(a) * r * 0.62, z + h + 0.46), 0.04, BD, 4)
    lathe(mb, F, (x, y, z + h - 1.25), [(0.24, 0.0), (0.24, 0.3)], 6, WD)
    lathe(mb, F, (x, y, z + h + 0.9), [(0.16, 0.0), (0.12, 0.25), (0.02, 0.45)], 6, WD)


# ================================================================== OFICINA: rebolo, tabuas encostadas, lenha
def toishi_guruma(mb, F):
    """rebolo de pedra: 2 soleiras e 2 montantes com chapeu, mo de pedra (14 lados, chanfro nas 2 faces) num eixo de
    ferro com manivela e cabo de madeira; o mo mergulha no cocho de agua (tabuas com cintas); banquinho do afiador"""
    for s in (-1, 1):
        bb(mb, F, -1.6, 1.6, s * 0.75 - 0.22, s * 0.75 + 0.22, -0.05, 0.4, WD, 0.07)
        bb(mb, F, -0.2, 0.2, s * 0.75 - 0.2, s * 0.75 + 0.2, 0.35, 2.55, WD, 0.07)
        bb(mb, F, -0.32, 0.32, s * 0.75 - 0.3, s * 0.75 + 0.3, 2.55, 2.75, WD, 0.07)
    bb(mb, F, -1.25, -0.95, -0.8, 0.8, 0.1, 0.34, WD)
    za = 1.75
    n = 14
    rg = lambda yy, rr: [(rr * math.cos(2 * math.pi * j / n), yy, za + rr * math.sin(2 * math.pi * j / n))
                         for j in range(n)]
    loft(mb, F, [rg(-0.2, 0.98), rg(-0.15, 1.1), rg(0.15, 1.1), rg(0.2, 0.98)], ST)
    mb.rod(F.p(0.0, -1.15, za), F.p(0.0, 1.25, za), 0.07, IRON, 6)
    bb(mb, F, -0.07, 0.07, 1.18, 1.28, za - 0.85, za + 0.07, IRON)
    mb.rod(F.p(0.0, 1.23, za - 0.78), F.p(0.0, 1.75, za - 0.78), 0.09, WD, 6)
    # cocho: 4 tabuas + fundo + agua (o mo entra 0,3 na agua); cintas de ferro
    x0, x1, y0, y1, zt = -1.0, 1.0, -0.5, 0.5, 0.95
    bb(mb, F, x0, x1, y0 - 0.12, y0, 0.0, zt, WM)
    bb(mb, F, x0, x1, y1, y1 + 0.12, 0.0, zt, WM)
    for xe in (x0 - 0.12, x1):
        bb(mb, F, xe, xe + 0.12, y0 - 0.12, y1 + 0.12, 0.0, zt, WM)
    bb(mb, F, x0, x1, y0, y1, 0.0, 0.62, WATER)
    for xe in (-0.6, 0.6):
        bb(mb, F, xe - 0.07, xe + 0.07, y0 - 0.16, y1 + 0.16, 0.12, zt - 0.06, IRON)
    # banquinho
    Fs = sub(F, -2.4, 0.2, 0.0, 0.2)
    bb(mb, Fs, -0.55, 0.55, -0.45, 0.45, 1.0, 1.18, WM, 0.04)
    for sx in (-1, 1):
        for sy in (-1, 1):
            bb(mb, Fs, sx * 0.38 - 0.08, sx * 0.38 + 0.08, sy * 0.3 - 0.08, sy * 0.3 + 0.08, 0.0, 1.02, WD)


def planks_leaning(mb, base, wall_dir, along, n=5, key=0, h=7.0):
    """tabuas encostadas numa parede: pe a ~1,3 da parede, topo encostado; base = ponto no chao junto da parede,
    wall_dir = vetor horizontal PARA a parede, along = ao longo da parede"""
    b = Vector(base)
    wd = Vector(wall_dir).normalized()
    al = Vector(along).normalized()
    pos = 0.0
    for i in range(n):
        w = 0.9 + 0.35 * hh(key, i, "w")
        ln = h * (0.82 + 0.25 * hh(key, i, "l"))
        foot = b + al * (pos + w / 2) - wd * (1.15 + 0.35 * hh(key, i, "f")) - wd * 0.12 * i
        top = b + al * (pos + w / 2) - wd * 0.12 * (i + 1) + Vector((0, 0, ln * 0.99))
        A = (top - foot).normalized()
        c = (foot + top) / 2
        obox(mb, c, A, -wd, (ln, w, 0.16), WM if i % 3 else WD, 0.0)
        pos += w + 0.06


def makiba(mb, F, L_=6.0, h=3.6, key=0):
    """lenha rachada empilhada entre 2 pares de mouroes, sobre 2 dormentes, com coberta de tabuas inclinada; F no
    meio, pilha ao longo de x; achas de 6 lados (rachadas: o perfil le meia-lua)"""
    for x in (-L_ / 2 - 0.3, L_ / 2 + 0.3):
        for y in (-0.75, 0.75):
            bb(mb, F, x - 0.18, x + 0.18, y - 0.18, y + 0.18, -0.1, h + 0.7, WD, 0.04)
    for y in (-0.5, 0.5):
        bb(mb, F, -L_ / 2, L_ / 2, y - 0.2, y + 0.2, -0.05, 0.3, WD)
    rows = int((h - 0.3) / 0.62)
    for r in range(rows):
        k = int(L_ / 0.7)
        for i in range(k):
            x = -L_ / 2 + 0.35 + i * (L_ - 0.7) / (k - 1) + (0.17 if r % 2 else 0.0)
            if x > L_ / 2 - 0.3:
                continue
            rr = 0.3 + 0.06 * hh(key, r, i)
            rot = hh(key, r, i, "r") * 6.28
            Fl = sub(F, x, 0.0, 0.3 + rr + r * 0.6)
            ring = lambda yy: [(rr * math.cos(rot + 2 * math.pi * j / 6) * (0.7 if j in (0, 1) else 1.0), yy,
                                rr * math.sin(rot + 2 * math.pi * j / 6)) for j in range(6)]
            loft(mb, Fl, [ring(-0.85 - 0.12 * hh(key, r, i, "a")), ring(0.85 + 0.12 * hh(key, r, i, "b"))],
                 WM if (r + i) % 4 else BD)
    ext(mb, F, [(-1.25, h + 0.6), (1.25, h + 0.3), (1.25, h + 0.48), (-1.25, h + 0.78)], "x", -L_ / 2 - 0.8,
        L_ / 2 + 0.8, WD, 0.0)


# ================================================================== CARRINHOS
def _wheel(mb, F, x, y, z, r, w, spokes=8, n=16, m=WD, rim_m=WM, iron=True):
    """roda de madeira raiada no plano xz do referencial (eixo ao longo de y): aro de secao retangular (n lados),
    raios, cubo, cinta de ferro no aro"""
    def ring(rr, yy):
        return [(x + rr * math.cos(2 * math.pi * j / n), y + yy, z + rr * math.sin(2 * math.pi * j / n)) for j in range(n)]
    t = 0.22 * r / 1.45
    loft(mb, F, [ring(r - t, -w / 2), ring(r, -w / 2), ring(r, w / 2), ring(r - t, w / 2), ring(r - t, -w / 2)],
         rim_m, caps=(False, False))
    if iron:
        loft(mb, F, [ring(r - 0.02, -w / 2 + 0.04), ring(r + 0.05, -w / 2 + 0.04), ring(r + 0.05, w / 2 - 0.04),
                     ring(r - 0.02, w / 2 - 0.04)], IRON, caps=(False, False))
    nh = 8
    hub = lambda rr, yy: [(x + rr * math.cos(2 * math.pi * j / nh), y + yy, z + rr * math.sin(2 * math.pi * j / nh))
                          for j in range(nh)]
    loft(mb, F, [hub(0.2 * r, -w * 0.9), hub(0.26 * r, -w * 0.4), hub(0.26 * r, w * 0.4), hub(0.2 * r, w * 0.9)], m)
    for k in range(spokes):
        a = 2 * math.pi * (k + 0.5) / spokes
        p0 = F.p(x + math.cos(a) * 0.22 * r, y, z + math.sin(a) * 0.22 * r)
        p1 = F.p(x + math.cos(a) * (r - t + 0.03), y, z + math.sin(a) * (r - t + 0.03))
        mb.beam(p0, p1, 0.13 * r / 1.45 + 0.04, 0.2 * r / 1.45 + 0.04, m, 0.0)


def daihachi(mb, F):
    """carrinho de mao de 2 rodas (daihachi-guruma) PARADO: rodas raiadas de 1,45, eixo sob o leito, leito de tabuas
    sobre 2 varais compridos que descem ate o chao na frente (+x), travessa de puxar na ponta; F no eixo, no chao"""
    r = 1.45
    for s in (-1, 1):
        _wheel(mb, F, 0.0, s * 1.55, r, r, 0.3)
    mb.rod(F.p(0.0, -1.85, r), F.p(0.0, 1.85, r), 0.09, IRON, 6)
    bb(mb, F, -0.3, 0.3, -1.25, 1.25, r - 0.05, r + 0.3, WD, 0.04)          # mancal (travessa do eixo)
    zb = r + 0.3                                                         # face de baixo do leito sobre o mancal
    xr, xf = -1.6, 5.4                                                   # fundo do leito / pe dos varais
    zf = 0.32
    ang = math.atan2(zb - zf, xf - 0.0)
    A = Vector((math.cos(F.a) * math.cos(ang), math.sin(F.a) * math.cos(ang), -math.sin(ang)))
    up = Vector((math.cos(F.a) * math.sin(ang), math.sin(F.a) * math.sin(ang), math.cos(ang)))

    def P(u, v, w):      # u ao longo do leito (a partir do eixo), v lateral, w acima da face de baixo do leito
        o = Vector(F.p(0.0, v, zb))
        return o + A * u + up * w
    side = Vector((-math.sin(F.a), math.cos(F.a), 0.0))
    for s in (-1, 1):                                                    # varais (vao de 1,9: entra a pessoa)
        obox(mb, (P(-1.7, s * 0.95, 0.12) + P(xf + 0.4, s * 0.95, 0.12)) / 2, A, up, (xf + 2.1, 0.26, 0.24), WD, 0.0)
    obox(mb, P(xf + 0.2, 0.0, 0.12), side, up, (2.3, 0.22, 0.2), WD, 0.0)                # travessa de puxar
    k = 7
    for i in range(k):                                                   # tabuas do leito (atravessadas)
        u = xr + 0.1 + i * (3.6 / k)
        obox(mb, P(u + 0.22, 0.0, 0.32), side, up, (2.5, 0.44, 0.12), WM, 0.0)
    for s in (-1, 1):                                                    # guardas laterais baixas
        obox(mb, (P(xr, s * 1.22, 0.62) + P(xr + 3.6, s * 1.22, 0.62)) / 2, A, up, (3.7, 0.12, 0.42), WM, 0.0)
    obox(mb, P(xr - 0.02, 0.0, 0.62), side, up, (2.56, 0.12, 0.42), WM, 0.0)


def tora(mb, F, key=0):
    """vagonete de madeira VAZIO parado: caixa em tronco de piramide (tabuas, cintas de ferro nos cantos e na borda),
    chassi de 2 longarinas, 2 eixos de ferro, 4 rodas de ferro com friso, alca de empurrar; F no meio, ao longo de x"""
    zb, zt = 1.05, 2.55
    bx0, by0, tx0, ty0 = 1.3, 0.86, 1.52, 1.02                # meias medidas embaixo / em cima
    th = 0.16
    ro = lambda hx, hy, z: [(-hx, -hy, z), (hx, -hy, z), (hx, hy, z), (-hx, hy, z)]
    loft(mb, F, [ro(bx0, by0, zb), ro(tx0, ty0, zt), ro(tx0 - th, ty0 - th, zt), ro(bx0 - th, by0 - th, zb + th)], WM)
    # tabuas: frisos escuros (juntas) nos 4 lados, na inclinacao da parede
    for k in (0.36, 0.68):
        z = zb + (zt - zb) * k
        hx, hy = bx0 + (tx0 - bx0) * k, by0 + (ty0 - by0) * k
        for sy in (-1, 1):
            bb(mb, F, -hx + 0.08, hx - 0.08, sy * hy - 0.04, sy * hy + 0.04, z - 0.04, z + 0.04, WD)
        for sx in (-1, 1):
            bb(mb, F, sx * hx - 0.04, sx * hx + 0.04, -hy + 0.08, hy - 0.08, z - 0.04, z + 0.04, WD)
    # cintas de ferro: borda de cima e os 4 cantos (seguindo o talude)
    for sy in (-1, 1):
        bb(mb, F, -tx0 - 0.05, tx0 + 0.05, sy * ty0 - 0.07, sy * ty0 + 0.07, zt - 0.22, zt + 0.02, IRON)
    for sx in (-1, 1):
        bb(mb, F, sx * tx0 - 0.07, sx * tx0 + 0.07, -ty0 - 0.05, ty0 + 0.05, zt - 0.22, zt + 0.02, IRON)
    for sx in (-1, 1):
        for sy in (-1, 1):
            a = F.p(sx * (bx0 + 0.02), sy * (by0 + 0.02), zb + 0.02)
            b = F.p(sx * (tx0 + 0.02), sy * (ty0 + 0.02), zt - 0.2)
            mb.beam(a, b, 0.2, 0.2, IRON, 0.0)
    # chassi, eixos, rodas de ferro (friso para dentro)
    for sy in (-1, 1):
        bb(mb, F, -1.55, 1.55, sy * 0.55 - 0.16, sy * 0.55 + 0.16, 0.62, zb, WD, 0.05)
    for sx in (-1, 1):
        mb.rod(F.p(sx * 0.9, -1.0, 0.5), F.p(sx * 0.9, 1.0, 0.5), 0.07, IRON, 6)
        for sy in (-1, 1):
            n = 10
            rg = lambda rr, yy: [(sx * 0.9 + rr * math.cos(2 * math.pi * j / n), sy * yy, 0.5 + rr * math.sin(2 * math.pi * j / n))
                                 for j in range(n)]
            loft(mb, F, [rg(0.42, 0.98), rg(0.5, 0.92), rg(0.5, 0.82), rg(0.58, 0.78), rg(0.58, 0.72), rg(0.2, 0.7)],
                 IRON)
    # alca de empurrar (2 bracos + travessa)
    for sy in (-1, 1):
        mb.beam(F.p(-tx0 + 0.05, sy * 0.7, zt - 0.4), F.p(-tx0 - 0.95, sy * 0.7, zt + 0.25), 0.16, 0.16, WD, 0.0)
    mb.rod(F.p(-tx0 - 0.95, -0.85, zt + 0.25), F.p(-tx0 - 0.95, 0.85, zt + 0.25), 0.1, WD, 6)


# ================================================================== FERRAMENTAS
def tsuruhashi(mb, foot, top, up_side):
    """picareta (tsuruhashi): cabo de madeira com o olho de ferro no topo e cabeca curva de 2 pontas (uma ponta, uma
    lamina estreita) - encostada: foot (chao) -> top (cabeca). up_side: para onde a cabeca 'abre'"""
    foot, top = Vector(foot), Vector(top)
    A = (top - foot).normalized()
    side = Vector(up_side)
    side = (side - A * side.dot(A)).normalized()
    nrm = A.cross(side)
    mb.beam(foot, top + A * 0.15, 0.17, 0.2, WM, 0.0)
    obox(mb, top, nrm, A, (0.34, 0.36, 0.5), IRON, 0.0)               # olho
    for s, ln, tip_w in ((1, 1.25, 0.04), (-1, 1.0, 0.24)):
        pts = [top + side * s * (0.15 + 1.0 * t) * ln - A * (0.42 * t * t) * ln for t in (0.0, 0.35, 0.7, 1.0)]
        bar(mb, pts, lambda k, tw=tip_w: 0.3 - (0.3 - tw) * k, lambda k: 0.26 - 0.18 * k, nrm, IRON, tip=(s > 0))


def shaberu(mb, foot, top, face):
    """pa: cabo com punho em T, encaixe (alvado) conico e lamina com ombros; foot = ponta da lamina no chao"""
    foot, top = Vector(foot), Vector(top)
    A = (top - foot).normalized()
    fc = Vector(face)
    fc = (fc - A * fc.dot(A)).normalized()
    side = A.cross(fc)
    bc = foot + A * 0.45
    obox(mb, bc, A, fc, (0.9, 0.72, 0.06), IRON, 0.0)                # lamina
    obox(mb, foot + A * 0.9, A, fc, (0.08, 0.72, 0.16), IRON, 0.0)   # ombro dobrado
    bar(mb, [foot + A * 0.88, foot + A * 1.3], lambda k: 0.28 - 0.12 * k, lambda k: 0.18 - 0.05 * k, fc, IRON)
    mb.beam(foot + A * 1.2, top, 0.15, 0.15, WM, 0.0)
    obox(mb, top, side, A, (0.85, 0.16, 0.16), WM, 0.0)
    mb.beam(top - A * 0.55 + side * 0.12, top + side * 0.3, 0.07, 0.07, WM, 0.0)
    mb.beam(top - A * 0.55 - side * 0.12, top - side * 0.3, 0.07, 0.07, WM, 0.0)


def kuwa(mb, foot, top):
    """enxada (kuwa) de horta encostada como se encosta de verdade: lamina de ferro EMBAIXO, apoiada no chao, cabo
    subindo ate o apoio; foot = ponta de baixo do cabo (~0,65 acima do chao), top = ponta de cima"""
    foot, top = Vector(foot), Vector(top)
    A = (top - foot).normalized()
    mb.beam(foot - A * 0.1, top, 0.14, 0.14, WM, 0.0)
    away = -Vector((A.x, A.y, 0.0)).normalized()                         # para fora do apoio
    blade_dir = (Vector((0, 0, -1)) * 0.82 + away * 0.57).normalized()
    nrm = A - blade_dir * A.dot(blade_dir)                                 # face da lamina no plano cabo-lamina
    obox(mb, foot + blade_dir * 0.42, blade_dir, nrm, (0.78, 0.6, 0.06), IRON, 0.0)
    obox(mb, foot, A, blade_dir, (0.32, 0.24, 0.22), IRON, 0.0)        # olho/encaixe


def kui_corner(mb, x, y, z, ax, ay, key=0, arm=3.2):
    """canto de marcacao: 3 estacas de madeira (ponta de 4 aguas, faixa de tinta escura) num L ao longo dos eixos
    (ax, ay) para FORA da zona, corda de palha caida entre elas e fita de algodao amarrada na estaca do canto"""
    pts = [(x + ax * arm, y), (x, y), (x, y + ay * arm)]
    tops = []
    for i, (px, py) in enumerate(pts):
        h = 2.2 if i == 1 else 1.7
        lathe(mb, Frame(px, py, z, 0.3 * hh(key, i)), (0, 0, -0.3), [(0.17, 0.0), (0.17, h), (0.0, h + 0.3)], 4, WM,
              math.pi / 4)
        lathe(mb, Frame(px, py, z, 0.3 * hh(key, i)), (0, 0, h - 0.5), [(0.19, 0.0), (0.19, 0.22)], 4, WD, math.pi / 4)
        tops.append(Vector((px, py, z + h - 0.75)))
    for a, b in zip(tops, tops[1:]):
        m = (a + b) / 2 + Vector((0, 0, -0.35))
        mb.rod(a, m, 0.05, STRAW, 4)
        mb.rod(m, b, 0.05, STRAW, 4)
    c = tops[0 + 1] + Vector((0, 0, 0.3))
    for k in range(2):                                               # fita: 2 pontas caidas
        d = Vector((ax * (0.3 + 0.25 * k), ay * (0.25 - 0.2 * k), 0.0))
        obox(mb, c + d * 0.5 + Vector((0, 0, -0.55)), Vector((d.x * 0.3, d.y * 0.3, -1.0)), Vector((-d.y, d.x, 0.0)),
             (1.1, 0.3, 0.04), LINEN, 0.0)


# ================================================================== FORJA: caixote de tamahagane, cavalete de afiar
def hagane_bako(mb, F, key=0):
    """caixote de tabuas (3 tabuas por lado com junta, montantes nos cantos, alcas de corda) cheio de BARRAS de aco
    forjado chatas em 2 camadas cruzadas logo abaixo da borda (ferro escuro, arestas vivas, nada de pepita) e a tampa
    de tabuas encostada"""
    hx, hy, h = 1.45, 0.95, 1.95
    zp = [0.12, 0.72, 1.32, 1.92]
    for sy in (-1, 1):
        for k in range(3):
            bb(mb, F, -hx, hx, sy * hy - (0.14 if sy > 0 else 0.0), sy * hy + (0.0 if sy > 0 else 0.14),
               zp[k] + 0.03, zp[k + 1] - 0.03, WM)
    for sx in (-1, 1):
        for k in range(3):
            bb(mb, F, sx * hx - (0.14 if sx > 0 else 0.0), sx * hx + (0.0 if sx > 0 else 0.14), -hy + 0.14, hy - 0.14,
               zp[k] + 0.03, zp[k + 1] - 0.03, WM)
        mb.rod(F.p(sx * (hx + 0.12), -0.35, 1.45), F.p(sx * (hx + 0.12), 0.35, 1.45), 0.07, STRAW, 5)
        for sy in (-1, 1):
            bb(mb, F, sx * (hx + 0.08) - 0.08, sx * (hx + 0.08) + 0.08, sy * 0.38 - 0.06, sy * 0.38 + 0.06, 1.3, 1.6,
               WD)
    for sx in (-1, 1):
        for sy in (-1, 1):
            bb(mb, F, sx * hx - 0.21, sx * hx + 0.21, sy * hy - 0.21, sy * hy + 0.21, 0.0, h + 0.06, WD, 0.04)
    bb(mb, F, -hx + 0.16, hx - 0.16, -hy + 0.16, hy - 0.16, 0.12, h - 0.62, WD)      # falso fundo (6b: atras das tabuas)
    z = h - 0.62
    for layer in range(2):
        nb = 6 if layer == 0 else 5
        for i in range(nb):
            t = (i - (nb - 1) / 2)
            jit = (hh(key, layer, i) - 0.5) * 0.12
            if layer == 0:
                bb(mb, F, -1.12 + jit, 1.12 + jit, t * 0.29 - 0.12, t * 0.29 + 0.12, z, z + 0.15, IRON)
            else:
                Fb = sub(F, t * 0.45 + jit, 0.0, 0.0, math.pi / 2 + (hh(key, i, "r") - 0.5) * 0.12)
                bb(mb, Fb, -0.72, 0.72, -0.16, 0.16, z + 0.15, z + 0.31, IRON)
    p0 = F.p(hx + 1.15, 0.15, 0.0)
    p1 = F.p(hx + 0.3, 0.15, h + 0.75)
    A = Vector(p1) - Vector(p0)
    side = Vector(F.p(0, 1, 0)) - Vector(F.p(0, 0, 0))
    nrm = A.cross(side)
    for k in (-1, 0, 1):
        obox(mb, (Vector(p0) + Vector(p1)) / 2 + side * k * 0.62, A, nrm, (A.length, 0.58, 0.13), WM, 0.0)
    for t in (0.25, 0.8):
        obox(mb, Vector(p0) + A * t - nrm.normalized() * 0.14, side, nrm, (1.9, 0.26, 0.1), WD, 0.0)   # 6b: 0,125


def togi_dai(mb, F):
    """cavalete de afiar: tampo grosso sobre 2 cavaletes em A, 2 pedras de afiar (grossa escura, fina clara) em
    berco de madeira com calcos, balde de agua com concha ao lado"""
    for sx in (-1, 1):
        for sy in (-1, 1):
            mb.beam(F.p(sx * 1.2, sy * 0.75, 0.0), F.p(sx * 1.2, sy * 0.22, 1.6), 0.2, 0.2, WD, 0.0)
        bb(mb, F, sx * 1.2 - 0.12, sx * 1.2 + 0.12, -0.7, 0.7, 0.55, 0.75, WD)
    bb(mb, F, -1.75, 1.75, -0.48, 0.48, 1.55, 1.85, WM, 0.07)
    for k, (x, m, w) in enumerate(((-0.75, STD, 0.5), (0.55, ST, 0.42))):
        bb(mb, F, x - 0.62, x + 0.62, -0.32, 0.32, 1.83, 1.98, WD)
        for s in (-1, 1):
            bb(mb, F, x + s * 0.6 - 0.07, x + s * 0.6 + 0.07, -0.34, 0.34, 1.95, 2.18, WD)
        bb(mb, F, x - 0.5, x + 0.5, -w / 2, w / 2, 1.96, 2.24, m, 0.04)
    oke(mb, F, 2.6, 0.3, 0.45)
    p = F.p(2.6, 0.3, 0.42)
    mb.rod(F.p(2.35, 0.25, 0.3), F.p(3.4, 0.0, 0.9), 0.04, WM, 4)       # concha (hishaku): cabo
    lathe(mb, F, (2.45, 0.25, 0.22), [(0.14, 0.0), (0.16, 0.16)], 6, WM)


# ================================================================== COLOCACAO
def _vframe(nm):
    import ds_village as V
    return V.house_frame(nm), V.full_spec(nm)


def village(mb):
    import ds_village as V
    out = []
    # --- V1 chaya: banco externo + guarda-sol, do lado esquerdo da frente (o vao do meio e a lateral do portao livres)
    F1, s1 = _vframe("V1")
    D1, W1 = s1["D"], s1["W"]
    fz = lambda F_, x, y, zh: Frame(F_.p(x, y, 0).x, F_.p(x, y, 0).y, gz(F_.p(x, y, 0).x, F_.p(x, y, 0).y, zh), F_.a)
    Fb = fz(F1, -W1 / 2 + 3.4, D1 / 2 + s1.get("engawa_d", 2.6) + 2.3, T1)
    K.bench(mb, Fb, 0.0, 0.0, 4.6, 1.7, 1.6)
    # guarda-sol junto da quina da casa (a cupula fica fora do eixo da rua: nada tampa a visada de quem sobe)
    Fg = fz(F1, -W1 / 2 + 0.6, D1 / 2 + s1.get("engawa_d", 2.6) + 1.2, T1)
    nodate_gasa(mb, Fg, 0.0, 0.0, 0.0, 2.4, 6.0)
    out.append(("V1", Fb))
    # --- V2 minka: horta no fundo-sul, cestos na engawa (lado R = sul), lenha sob o beiral norte, varal ao norte
    F2, s2 = _vframe("V2")
    W2, D2 = s2["W"], s2["D"]
    ax, ay = -101.0, 138.0
    Fh = Frame(ax, ay, gz(ax, ay, T1), F2.a + math.pi / 2)
    hatake(mb, Fh, 2, 7.2, 2.2, 21)
    kuwa(mb, Fh.p(4.7, 2.75, 0.62), Fh.p(3.95, 2.15, 3.9))
    oke(mb, Frame(*Fh.p(-4.7, -2.3, 0.0)[:2], Fh.o.z, 0.0), 0.0, 0.0, 0.5)
    ze = ground(*F2.p(W2 / 2 + 1.5, -2.0, 0.0)[:2], T1 + 1.5, up=1.6)
    Fe = Frame(*F2.p(W2 / 2 + 1.5, 0.0, 0.0)[:2], ze - 0.02, F2.a)
    zaru(mb, Fe, 0.0, -3.4, 0.0, 1.0)
    zaru(mb, Fe, 0.3, -1.6, 0.0, 0.85)
    kago(mb, Frame(*F2.p(W2 / 2 + 4.2, 2.6, 0.0)[:2], gz(*F2.p(W2 / 2 + 4.2, 2.6, 0.0)[:2], T1), F2.a), 0.0, 0.0)
    Fw = fz(F2, -W2 / 2 - 2.0, -3.0, T1)                              # 6b (item 52): era -1,5 (entrava no ishigaki)
    Fw = Frame(Fw.o.x, Fw.o.y, Fw.o.z, F2.a + math.pi / 2)
    makiba(mb, Fw, 6.0, 3.4, 22)
    p = Fw.p(0, 0, 0)
    col_box(AREA, (6.8, 2.0, 4.0), (p.x, p.y, Fw.o.z + 2.0), (0, 0, Fw.a))
    vx, vy = -104.0, 176.0
    Fv = Frame(vx, vy, gz(vx, vy, T1), F2.a)
    monohoshi(mb, Fv, 7.0, 23)
    # --- V3 oficina: rebolo na frente-direita, tabuas encostadas na parede direita, barril d'agua
    F3, s3 = _vframe("V3")
    W3, D3 = s3["W"], s3["D"]
    Fr = fz(F3, W3 / 2 + 3.3, D3 / 2 + 1.6, T1)
    Fr = Frame(Fr.o.x, Fr.o.y, Fr.o.z, F3.a + 0.25)
    toishi_guruma(mb, Fr)
    p = Fr.p(0, 0, 0)
    col_box(AREA, (2.4, 2.4, 2.8), (p.x, p.y, Fr.o.z + 1.4), (0, 0, Fr.a))
    wall0 = F3.p(W3 / 2 + 1.05, -1.0, 0.0)                              # 6b (item 52): era 0,75 (entrava na parede)
    zw = gz(wall0.x, wall0.y, T1)
    planks_leaning(mb, (wall0.x, wall0.y, zw), F3.p(-1, 0, 0) - F3.p(0, 0, 0), F3.p(0, -1, 0) - F3.p(0, 0, 0), 5, 31, 7.4)
    Ft = fz(F3, W3 / 2 + 3.6, D3 / 2 - 1.6, T1)
    taru(mb, Ft, 0.0, 0.0, 1.0, "water")
    col_box(AREA, (2.0, 2.0, 2.4), (Ft.o.x, Ft.o.y, Ft.o.z + 1.2))
    # --- V4 kura (frente sul): fardos de arroz num estrado a oeste da porta, barris e carrinho a leste
    F4, s4 = _vframe("V4")
    bx_, by_ = -117.5, 239.5
    Fs = Frame(bx_, by_, gz(bx_, by_, T2), F4.a)
    for i in range(4):                                                    # estrado (sunoko)
        bb(mb, Fs, -2.4, 2.4, -1.2 + i * 0.62, -1.2 + i * 0.62 + 0.5, 0.0, 0.25, WM)
    tawara_pile(mb, Frame(bx_, by_, Fs.o.z + 0.25, 0.0), 0.0, 0.0, F4.a, (3, 2), 1.0, False, 41)
    col_box(AREA, (5.0, 2.6, 2.6), (bx_, by_, Fs.o.z + 1.3), (0, 0, F4.a))
    for i, (x, y, top) in enumerate(((-98.6, 241.6, "lid"), (-96.4, 242.4, "lid"), (-97.4, 240.0, "water"))):
        Fk = Frame(x, y, gz(x, y, T2), 0.4 * i)
        taru(mb, Fk, 0.0, 0.0, 0.92 if i < 2 else 0.8, top)
        col_box(AREA, (1.9, 1.9, 2.2), (x, y, Fk.o.z + 1.1))
    cx, cy = -91.5, 236.6
    Fc = Frame(cx, cy, gz(cx, cy, T2), math.radians(168.0))
    daihachi(mb, Fc)
    p = Fc.p(1.8, 0.0, 0.0)
    col_box(AREA, (8.0, 3.6, 2.6), (p.x, p.y, Fc.o.z + 1.3), (0, 0, Fc.a))
    # --- V5 sobrado: vasos + pote junto da porta (lado norte), varal nos fundos
    F5, s5 = _vframe("V5")
    W5, D5 = s5["W"], s5["D"]
    for i, (lx, s_) in enumerate(((-5.0, 1.0), (-6.4, 0.8))):
        Fp = fz(F5, lx, D5 / 2 + 1.7, T2)                               # 6b (item 52): +0,5 (soco em talude)
        hachi(mb, Fp, 0.0, 0.0, s_, 50 + i)
    Fk = fz(F5, -8.2, D5 / 2 + 2.0, T2)
    kame(mb, Fk, 0.0, 0.0, 0.95)
    col_box(AREA, (2.0, 2.0, 2.2), (Fk.o.x, Fk.o.y, Fk.o.z + 1.1))
    Fo = fz(F5, 5.6, D5 / 2 + 1.9, T2)
    oke(mb, Fo, 0.0, 0.0, 0.75)
    vx, vy = -117.0, 306.5
    monohoshi(mb, Frame(vx, vy, gz(vx, vy, T2), math.radians(4.0)), 6.0, 24, ("tenugui", "tenugui2", "yukata"))
    # --- V6 jardim: grupo de 3 pedras (uma de pe) - a lingua das pedras de borda do terreno
    import ds_terrain as TR
    for i, (x, y, r, hgt) in enumerate(((-97.0, 327.5, 1.25, 2.4), (-94.6, 326.0, 1.0, 0.8), (-98.6, 324.8, 0.8, 0.55))):
        TR.boulder(mb, x, y, ground(x, y, T2) + 0.0, r, hgt, ("v6g", i), ST, ang=hh(i, "g6") * 3.0)
    # --- mirante do T2: banco virado para a clareira
    mx, my = -61.5, 300.0
    K.bench(mb, Frame(mx, my, gz(mx, my, T2), math.pi / 2), 0.0, 0.0, 5.0, 1.8, 1.7)
    return out


# ------------------------------------------------------------------ clareira: cercas em setores, mineiros, estacas
FENCE_SECTORS = [
    # (nome, pontos (x, y)) - cerca baixa (guarda-corpo do kit, 2,9) SO em setores; abertas nas chegadas
    ("Bambuzal_O", [(32.0, 136.0), (43.0, 138.4), (55.0, 141.6)]),           # bambuzal, a oeste da rampa
    ("Bambuzal_L", [(77.0, 147.4), (87.0, 151.8), (97.0, 157.6)]),           # bambuzal, a leste da rampa
    ("Vila", [(-42.6, 222.0), (-43.2, 236.0), (-44.0, 250.0)]),             # junto da vila: abre 15 antes do oratorio
    ("PeSubida_O", [(-12.0, 367.6), (2.6, 371.3)]),                          # pe da SubidaA, dos 2 lados
    ("PeSubida_L", [(27.5, 375.0), (44.0, 375.6)]),
]
MINERS = (-37.6, 181.0)                 # canto dos mineiros (borda oeste, entre a pedra de borda e o poco)


def fence_sectors(mb):
    for nm, pts in FENCE_SECTORS:
        z = T1
        F = Frame(0.0, 0.0, z - 0.06, 0.0)
        K.railing(mb, F, pts, 2.9, 0.0, 3.2)
        for a, b in zip(pts, pts[1:]):
            d = Vector((b[0] - a[0], b[1] - a[1]))
            col_box(AREA, (d.length + 0.4, 0.5, 3.0), ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2, z + 1.5),
                    (0, 0, math.atan2(d.y, d.x)))


def clearing(mb):
    fence_sectors(mb)
    # canto dos mineiros: vagonete vazio ao longo da borda, picareta e pa encostadas nele (lado da clareira),
    # balde e cesto; 1 pedra assentada fazendo de apoio
    x, y = MINERS
    Fc = Frame(x, y, gz(x, y, T1), math.radians(96.0))
    tora(mb, Fc, 61)
    col_box(AREA, (5.4, 2.6, 2.8), (x, y, Fc.o.z + 1.4), (0, 0, Fc.a))
    e = Vector(Fc.p(0, -1, 0)) - Vector(Fc.p(0, 0, 0))                 # para a clareira (-y do vagonete)
    al = Vector(Fc.p(1, 0, 0)) - Vector(Fc.p(0, 0, 0))
    zc = Fc.o.z
    top_side = Vector(Fc.p(0.0, -1.12, 2.5))
    f1 = top_side + e * 1.25 + al * 0.4
    tsuruhashi(mb, (f1.x, f1.y, zc + 0.05), tuple(Vector(Fc.p(0.4, -1.2, 2.75))), al)
    f2 = Vector(Fc.p(-0.9, -1.12, 0.0)) + e * 1.15
    shaberu(mb, (f2.x, f2.y, zc + 0.04), tuple(Vector(Fc.p(-1.2, -1.16, 2.85))), e)
    p = Fc.p(2.8, -0.9, 0.0)
    oke(mb, Frame(p.x, p.y, gz(p.x, p.y, T1), 0.0), 0.0, 0.0, 0.55)
    p = Fc.p(3.0, 0.8, 0.0)
    kago(mb, Frame(p.x, p.y, gz(p.x, p.y, T1), Fc.a), 0.0, 0.0, 0.0, 0.9)
    # estacas de marcacao nos 4 cantos da MiningZone, 2,5 para fora (nada dentro da zona)
    x0, y0, x1, y1 = L.MINE_RECT
    for i, (cx, cy, ax, ay) in enumerate(((x0 - 2.5, y0 - 2.5, 1, 1), (x1 + 2.5, y0 - 2.5, -1, 1),
                                          (x1 + 2.5, y1 + 2.5, -1, -1), (x0 - 2.5, y1 + 2.5, 1, -1))):
        kui_corner(mb, cx, cy, gz(cx, cy, T1), ax, ay, 70 + i)


# ------------------------------------------------------------------ forja: patio de trabalho
def forge(mb):
    z = lambda x, y: gz(x, y, T4)
    # leste: pilha de carvao em tawara (3-2-1) + fardo solto, caixote de tamahagane, cavalete de afiar
    px, py = 71.0, 452.0
    tawara_pile(mb, Frame(px, py, z(px, py), 0.0), 0.0, 0.0, math.radians(90.0), (4, 3, 2), 1.1, True, 81)
    col_box(AREA, (2.6, 6.4, 3.8), (px, py, z(px, py) + 1.9))
    tawara_pile(mb, Frame(55.2, 459.6, z(55.2, 459.6), 0.0), 0.0, 0.0, math.radians(98.0), (2, 1), 1.05, True, 85)
    col_box(AREA, (2.4, 3.0, 2.4), (55.2, 459.6, z(55.2, 459.6) + 1.2))
    tawara(mb, Frame(0, 0, 0, 0), 72.6, 448.0, z(72.6, 448.0), math.radians(70.0), 1.0, True)
    tawara(mb, Frame(0, 0, 0, 0), 66.4, 449.6, z(66.4, 449.6), math.radians(-20.0), 1.0, True)
    col_box(AREA, (3.6, 2.6, 1.4), (69.5, 448.8, z(69.5, 448.8) + 0.7))
    cx, cy = 50.0, 459.0
    Fk = Frame(cx, cy, z(cx, cy), math.radians(8.0))
    hagane_bako(mb, Fk, 82)
    col_box(AREA, (3.4, 2.4, 2.0), (cx, cy, Fk.o.z + 1.0), (0, 0, Fk.a))
    tx, ty = 65.5, 463.4
    Ft = Frame(tx, ty, z(tx, ty), math.radians(-6.0))
    togi_dai(mb, Ft)
    # bancos virados para a boca: um a leste do sando, um a oeste junto da oficina
    for bx_, by_, a in ((36.5, 466.4, 0.0), (-50.0, 466.0, 0.0)):
        K.bench(mb, Frame(bx_, by_, z(bx_, by_), a), 0.0, 0.0, 5.0, 1.8, 1.7)
    # lenha da forja encostada na cerca sul (canto sudeste do patio, longe das rotas que cruzam o meio)
    Fm = Frame(58.0, 441.6, z(58.0, 441.6), 0.0)
    makiba(mb, Fm, 6.0, 3.2, 84)
    col_box(AREA, (6.8, 2.0, 3.8), (58.0, 441.6, Fm.o.z + 1.9))
    # oeste: fardos de carvao junto do banco
    tawara_pile(mb, Frame(-57.5, 461.0, z(-57.5, 461.0), 0.0), 0.0, 0.0, math.radians(0.0), (2, 1), 1.0, True, 83)
    col_box(AREA, (2.4, 3.0, 2.4), (-57.5, 461.0, z(-57.5, 461.0) + 1.2))


# ------------------------------------------------------------------ lanternas de no (kit) - NightOnly
NODE_LAMPS = [
    # (nome, x, y, z, rumo do braco em graus: a lanterna pende para o caminho)
    ("Trilha", -20.2, 58.4, T1, 0.0),
    ("Antecampo", 22.0, 138.0, T1, 150.0),
    ("PeSubida", 4.6, 371.2, T1, -60.0),
    ("SummonFoot", 124.6, 292.4, T1, 70.0),          # 6b (item 53): 1,0 para oeste (a base entrava na bochecha)
    ("Bambuzal", 40.5, 44.0, None, 200.0),
]


def node_lamps(mb):
    for nm, x, y, z, deg in NODE_LAMPS:
        zz = L.bamboo_z(x, y) if z is None else z
        g = ground(x, y, zz)
        if abs(g - zz) > 0.8:
            print("ds_props AVISO lanterna %s sem chao (%.2f vs %.2f)" % (nm, g, zz))
        F = Frame(x, y, g - 0.06, math.radians(deg) - math.pi / 2)
        K.MIN_BEVEL = 0.09                                # o mesmo poste da saida (sem chanfro na pedra e no poste)
        K.lantern_post(mb, F, 8.6, 1.9, "L_DSProp_Lamp_%s" % nm, 40.0)
        K.MIN_BEVEL = LOW_BEVEL[0]
        col_box(AREA, (1.0, 1.0, 8.6), (x, y, g + 4.3))


# ================================================================== ONDA 4b: DENSIDADE (luz de caminho, cercas, vida)
# Critica do lead (renders/onda4/folha_referencias.jpg): nas refs FILEIRAS de lanternas acesas marcam todos os caminhos
# (um ponto quente a cada ~10-14), cercas baixas de madeira acompanham trilhas e bordas de terraco e o caminho le como
# uma linha de luz a noite; aqui so havia lanterna nos nos. Esta secao (agente 4b-PROPS):
#  - LANTERNAS DE CAMINHO em fileira em TODOS os caminhos (trilha, rampa do bambuzal, rua baixa e alta da vila, borda
#    da clareira, patio da forja e do carvao, caminho de saida): passo 10-14 dirigido (mais curto nas curvas), lados
#    alternados. 3 tipos LEVES da linguagem do kit (~125-175 tris cada; o lantern_post do kit tem 620):
#      andon (poste com caixa) | toro baixo de caminho (oki) | tsuri (poste curto com lanterna pendurada no braco).
#    PERFORMANCE: quase todas SEM PointLight - a camara de papel (Glass_DS_Lantern -> Neon) fica RECUADA 0,15 dentro de
#    4 montantes com 2 cintas de travessas na frente (le como ponto de luz sem custo de luz; neon so dentro de armacao).
#    So as de PATH_LIT (<= 12, curvas / pes de escada / frente de portao) ganham luz NightOnly L_DSProp_Lamp_* (o
#    ds_lights trata pelo nome: posto 5 caminho; as 'Toro' no posto 6).
#  - CERCAS baixas (K.railing) em SETORES ao longo de trechos de trilha/rampa e da borda do terraco T3 sobre a clareira;
#    cortadas onde passam rotas, escadas, acessos, colisoes existentes e onde ha lanterna.
#  - VIDA: 3 bancos, 3 placas de direcao, 3 pilhas pequenas de lenha.
# Posicionamento por RAYCAST no build (o ds_terrain e o ds_veg rodam ANTES): cada peca escorrega ao longo do caminho ate
# achar chao livre (grama/terra, sem tronco/casa/prop/colisao), fora das rotas do QA (ROUTE_CLR), da MiningZone (+6),
# das escadas e do cone da PlayerHeight da forja. Colisao so no poste/pedestal (DS_PropPath) e nas cercas (DS_PropFence).
import ds_terrain as _TR
import ds_forge as _FRG
# trilha do patio da forja ate o caminho de saida: TRAIL_W (lajes do ds_forge, de leste para oeste) + a trilha 'Patio'
# do ds_terrain (que continua dela para oeste)
_FRG_PATIO = list(reversed(_FRG.TRAIL_W)) + [p for p in _TR.T4_TRAILS["Patio"][0] if p[0] < _FRG.TRAIL_W[0][0] - 1.0]

ROUTE_CLR = 3.3          # folga das polilinhas de rota do QA (corpo 1,1 + a largura 3,4 do teste de largura)
LAMP_GAP = 6.5           # distancia minima entre lanternas (novas e as que ja existem: luzes L_*)
MINE_PAD = 6.0
GROUND_OK = ("DS_Ter_", "DS_Clr_", "DS_Vil_Street", "DS_Frg_Ground", "DS_Ent_Court", "DS_Exit_Path")
PATH_SURF = ("DS_Vil_Street", "DS_Ter_Paving", "DS_Exit_Path", "DS_Ent_Court")
PATH_MATS = ("Stone_DS_Path", "Stone_DS_Laje", "Stone_DS_Slab")
LGLOW = K.LGLOW
PST = "Stone_DS_Path"     # pedra das lanternas novas: sem familia de variantes (o Stone_DS dobra as MeshParts)
PWARM = K.LIT             # 6b (item 50): papel quente FOSCO (Window_DS_Warm, SmoothPlastic) nas faixas de cima/baixo
PH_FORGE = ((16.0, 352.0), (10.0, 470.0), 6.0)     # cone da CAM_DS_PlayerHeight_Forge (nada de lanterna na frente)

# caminhos: (nome, regiao, polilinha, meia-largura do piso, tipos alternados, lado inicial, modo, s0, s1, folga)
#   modo "alt" = lados alternados (afastadas meia-largura + folga do eixo); "on" = sobre a linha (borda da clareira,
#   com jitter lateral de +-1)
PATHS = [
    ("Trilha", "Sul", _TR.TRAIL_PATH, _TR.TRAIL_HW, ("andon", "toro"), -1, "alt", 6.0, None, 1.1),
    ("Bambu", "Sul", L.BAMBOO_RAMP, 2.8, ("toro", "tsuri", "andon"), 1, "alt", 8.0, None, 1.2),
    ("VilRua", "Vila", L.VILLAGE_STREET, 4.2, ("tsuri", "andon"), 1, "alt", 6.0, None, 1.0),
    ("VilAlta", "Vila", L.VILLAGE_STREET_HIGH, 4.2, ("andon", "tsuri"), -1, "alt", 6.0, None, 1.0),
    ("ClrS", "Sul", [(-26.0, 150.0), (0.0, 153.0), (30.0, 157.0), (56.0, 161.0), (80.0, 167.0), (97.0, 175.0)],
     0.0, ("toro", "andon"), 1, "on", 22.0, None, 0.0),
    ("ClrO", "Clareira", [(-34.0, 162.0), (-36.0, 200.0), (-37.0, 250.0), (-37.0, 300.0), (-35.0, 340.0),
                          (-28.0, 358.0)], 0.0, ("andon", "toro"), 1, "on", 4.0, None, 0.0),
    ("ClrL", "Clareira", [(102.0, 180.0), (109.0, 205.0), (111.0, 240.0), (110.0, 275.0), (110.0, 320.0),
                          (108.0, 350.0), (100.0, 366.0)], 0.0, ("toro", "andon"), -1, "on", 4.0, None, 0.0),
    ("ClrN", "Clareira", [(-20.0, 362.0), (2.0, 366.0), (30.0, 368.0), (52.0, 370.0), (74.0, 372.0), (90.0, 376.0)],
     0.0, ("andon", "toro"), 1, "on", 2.0, None, 0.0),
    # 6c (integracao): o T4 oeste ganhou TRILHAS na 6b (ds_forge.TRAIL_W de lajes no patio + ds_terrain.T4_TRAILS
    # 'Patio' e 'Carvao'); as lanternas seguem a BORDA delas (meia-largura da trilha + folga), nao mais a linha antiga
    # que cortava o patio e caia sobre as manchas de pisoteio do ds_forge
    ("FrgPatio", "Forja", _FRG_PATIO, 1.5, ("andon", "tsuri"), 1, "alt", 4.0, None, 1.2),
    ("Carvao", "Forja", _TR.T4_TRAILS["Carvao"][0], _TR.T4_TRAILS["Carvao"][1], ("tsuri", "andon"), -1, "alt", 6.0,
     None, 1.2),
    ("Saida", "Forja", L.EXIT_PATH, 3.4, ("toro", "tsuri"), 1, "alt", 10.0, None, 1.4),
]
# as <= 12 PointLights novas (NightOnly): ancora (x, y) -> a lanterna nova mais proxima (<= 10) ganha a luz
PATH_LIT = [("TrilhaMeio", -6.0, 96.0),     # 6c: era "Trilha" = mesmo nome da lanterna de no (Lamp_Trilha.001)
            ("Bambu", 54.0, 98.0), ("VilRua", -72.0, 186.0), ("VilAlta", -80.0, 300.0),
            ("ClrSO", 2.0, 154.0), ("ClrO", -37.0, 250.0), ("ClrNO", -26.0, 356.0), ("ClrN", 60.0, 371.0),
            ("ClrL", 110.0, 250.0), ("ClrSE", 92.0, 172.0), ("FrgOeste", -55.0, 448.0), ("Carvao", -60.0, 400.0)]
LIT_E = {"andon": 120.0, "tsuri": 120.0, "toro": 70.0}

# cercas em SETORES ao longo dos caminhos: caminho -> [(lado, s0, s1)] (lado 0 = sobre a linha: borda da clareira).
#   A cerca fica a FENCE_OFF alem da meia-largura (dentro da faixa de ~2 que o ds_veg deixa livre entre a borda do
#   caminho e os troncos) e a lanterna desse lado entra NA LINHA da cerca: a colisao da cerca (continua) segura a
#   lanterna tambem - sem caixa propria (orcamento de COL da ilha: 1300). Os setores evitam as cercas que ja existem
#   (Bambuzal_O/L, Vila, PeSubida_O/L do FENCE_SECTORS: nada de cerca dupla paralela).
FENCE_OFF = 1.5
FENCED = {
    "Trilha": [(-1, 8.0, 40.0), (-1, 52.0, 92.0), (1, 64.0, 92.0)],
    "Bambu": [(-1, 12.0, 42.0), (-1, 70.0, 104.0), (1, 40.0, 66.0)],
    "Saida": [(-1, 84.0, 128.0)],
    "ClrO": [(0, 8.0, 36.0), (0, 100.0, 130.0), (0, 146.0, 178.0)],
    "ClrL": [(0, 6.0, 36.0), (0, 60.0, 90.0), (0, 146.0, 180.0)],
    "ClrN": [(0, 74.0, 112.0)],
}
# bordas de terraco (sem lanterna): o T3 da berma sobre a clareira, dos 2 lados do pe da SubidaA
FENCE_LINES = [
    ("BermaO", [(-44.0, 374.2), (-22.0, 372.2), (5.0, 377.6)]),
    ("BermaL", [(28.0, 379.4), (54.0, 381.6), (74.0, 383.6), (88.0, 398.0)]),
]
LIFE = [
    # (tipo, nome, [(x, y) candidatos em ordem], rumo em graus (frente / seta principal))
    ("bench", "ClrO", [(-42.0, 268.0), (-44.0, 318.0)], 0.0),
    ("bench", "Bambu", [(64.0, 112.0), (60.0, 84.0)], 180.0),
    ("bench", "Saida", [(-122.0, 528.0), (-118.0, 556.0)], 0.0),
    ("sign", "Trilha", [(-18.0, 60.0), (-2.0, 62.0)], 0.0),
    ("sign", "PeSubida", [(34.0, 368.0), (-2.0, 366.0)], 0.0),
    ("sign", "Patio", [(-94.0, 442.0), (-20.0, 438.0), (-14.0, 443.0)], 0.0),
    ("pile", "VilRua", [(-52.0, 190.0), (-70.0, 162.0), (-48.0, 236.0)], 60.0),
    ("pile", "VilAlta", [(-62.0, 318.0), (-60.0, 300.0)], 80.0),
    ("pile", "Carvao", [(-74.0, 404.0), (-90.0, 420.0)], 80.0),
]

_ROUTES = None
_STAIRS = None
_COLB = None


def _routes():
    global _ROUTES, _STAIRS
    if _ROUTES is None:
        _ROUTES = [pts for pts, z0 in L.routes().values()] + [L.gate_open_route()]
        _STAIRS = []
        for nm, foot, deg, w, n, tread, g in L.STAIRS:
            a = math.radians(deg)
            ux, uy = math.cos(a), math.sin(a)
            t = L.stair_top(nm)
            _STAIRS.append(L.ribbon([(foot[0] - ux * 3.0, foot[1] - uy * 3.0), (t[0] + ux * 3.0, t[1] + uy * 3.0)],
                                    w / 2 + 1.6))
    return _ROUTES, _STAIRS


def _col_bvh():
    """BVH de todas as colisoes COL_ ja criadas (pisos, guardas, cercas, postes, casas, troncos)"""
    global _COLB
    from mathutils.bvhtree import BVHTree
    verts, polys = [], []
    for o in bpy.data.objects:
        if o.type != "MESH" or not o.name.startswith("COL_"):
            continue
        mw = o.matrix_world
        b = len(verts)
        verts += [mw @ v.co for v in o.data.vertices]
        polys += [[b + i for i in p.vertices] for p in o.data.polygons]
    _COLB = BVHTree.FromPolygons(verts, polys) if polys else None
    return _COLB


def _col_hit(x, y, z0, z1, r):
    """True se a caixa (x+-r, y+-r, z0..z1) cruza ou esta DENTRO de uma colisao existente"""
    if _COLB is None:
        return False
    from mathutils.bvhtree import BVHTree
    vs = [(x + sx * r, y + sy * r, z) for z in (z0, z1) for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    fs = [(0, 1, 2, 3), (4, 7, 6, 5), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)]
    if _COLB.overlap(BVHTree.FromPolygons(vs, fs)):
        return True
    for dx, dy in ((0.0, 0.0), (r, r), (-r, -r)):
        hit = _COLB.ray_cast(Vector((x + dx, y + dy, (z0 + z1) / 2)), Vector((0, 0, 1)), 400.0)
        if hit[0] is not None and hit[1].z > 0.0:                # saiu por uma face virada para cima: esta dentro
            return True
    return False


def _top(x, y, zexp):
    """primeiro objeto VISUAL de cima em (x, y): (nome, material, z, nz) - pula colisao, previa, VFX, copa alta e a
    forracao baixa da vegetacao (grama/samambaia: a lanterna fica no meio dela)"""
    dg = bpy.context.evaluated_depsgraph_get()
    sc = bpy.context.scene
    o = Vector((x, y, zexp + 30.0))
    d = Vector((0.0, 0.0, -1.0))
    for _ in range(24):
        hit, loc, nrm, idx, ob, mtx = sc.ray_cast(dg, o, d, distance=60.0)
        if not hit:
            return None
        nm = ob.name
        skip = nm.startswith(("COL_", "PREVIEW_", "SCALE_", "VFX_", "DS_Prop_Path"))
        if nm.startswith("DS_Veg_") and (loc.z > zexp + 7.0 or loc.z < zexp + 0.9):
            skip = True
        if skip:
            o = loc + d * 0.02
            continue
        mt = "-"
        try:
            me = ob.data
            mt = me.materials[me.polygons[idx].material_index].name
        except Exception:
            pass
        return nm, mt, loc.z, nrm.z
    return None


def _spot(x, y, r=0.8, h=4.5):
    """chao livre para uma peca de raio r: devolve (z do chao, sobre_o_piso_do_caminho) ou None"""
    zexp = L.zone_of(x, y)
    if zexp is None:
        return None
    zs, on = [], False
    for k, (dx, dy) in enumerate(((0.0, 0.0), (r, 0.0), (-r, 0.0), (0.0, r), (0.0, -r))):
        t = _top(x + dx, y + dy, zexp)
        if t is None:
            return None
        nm, mt, z, nz = t
        if not nm.startswith(GROUND_OK) or abs(z - zexp) > 1.0 or nz < 0.75:
            return None
        if nm.startswith("DS_Frg_") and z > zexp + 0.08:     # 6c: no chao da forja so na terra nua (nao em mancha/laje)
            return None
        if k == 0 and (nm.startswith(PATH_SURF) or mt in PATH_MATS):
            on = True
        zs.append(z)
    if max(zs) - min(zs) > 0.6:
        return None
    if _col_hit(x, y, min(zs) + 0.6, min(zs) + h, r):
        return None
    if _side_hit(x, y, min(zs), r + 0.35, h):
        return None
    return min(zs), on


def _side_hit(x, y, z, r, h):
    """raios horizontais (8 rumos, 2 alturas) do eixo da peca: bate em colmo de bambu, tronco, arbusto, parede?"""
    dg = bpy.context.evaluated_depsgraph_get()
    sc = bpy.context.scene
    for zz in (z + 1.0, z + min(h, 3.2)):
        for k in range(8):
            a = k * math.pi / 4
            d = Vector((math.cos(a), math.sin(a), 0.0))
            o = Vector((x, y, zz))
            for _ in range(4):
                hit, loc, nrm, idx, ob, mtx = sc.ray_cast(dg, o, d, distance=r)
                if not hit:
                    break
                if ob.name.startswith(("COL_", "PREVIEW_", "SCALE_", "VFX_", "DS_Prop_Path")):
                    o = loc + d * 0.02
                    continue
                return True
    return False


def _xy_ok(x, y, clr=ROUTE_CLR):
    """fora das rotas, escadas, MiningZone (+6) e do cone da PlayerHeight da forja"""
    x0, y0, x1, y1 = L.MINE_RECT
    if x0 - MINE_PAD < x < x1 + MINE_PAD and y0 - MINE_PAD < y < y1 + MINE_PAD:
        return False
    R, S = _routes()
    if any(L.polyline_dist(x, y, pts) < clr for pts in R):
        return False
    if any(L.point_in_poly(x, y, poly) for poly in S):
        return False
    (ax, ay), (bx_, by_), w = PH_FORGE
    if L.seg_dist(x, y, ax, ay, bx_, by_)[0] < w:
        return False
    return True


def _at(pts, s):
    """ponto, tangente e curvatura (mudanca de rumo em +-5) na estacao s da polilinha"""
    def pos(ss):
        ss = max(0.0, ss)
        for a, b in zip(pts, pts[1:]):
            ln = math.hypot(b[0] - a[0], b[1] - a[1])
            if ss <= ln or b is pts[-1]:
                t = min(1.0, ss / ln) if ln else 0.0
                return a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, (b[0] - a[0]) / ln, (b[1] - a[1]) / ln
            ss -= ln
    x, y, dx, dy = pos(s)
    _, _, ax, ay = pos(s - 5.0)
    _, _, bx2, by2 = pos(s + 5.0)
    turn = abs(math.atan2(ax * by2 - ay * bx2, ax * bx2 + ay * by2))
    return x, y, dx, dy, turn


def _near_lights(x, y, d):
    for o in bpy.data.objects:
        if o.type == "LIGHT" and o.name.startswith("L_"):
            p = o.matrix_world.translation
            if math.hypot(p.x - x, p.y - y) < d:
                return True
    return False


def _fenced(nm, side, s):
    """o trecho (caminho, lado, estacao) tem setor de cerca?"""
    return any(sd == side and s0 - 0.5 <= s <= s1 + 0.5 for sd, s0, s1 in FENCED.get(nm, ()))


def plan_lamps():
    """posiciona as lanternas de todos os caminhos; devolve [(regiao, tipo, x, y, z, rumo, caminho, i, na_cerca)]
    passo: 10-14 nos caminhos e 12-16 na borda da clareira (borda, nao rua), 2 a menos nas curvas; lados alternados.
    Do lado com setor de cerca a lanterna entra na LINHA da cerca (e so escorrega ao longo dela)."""
    out = []
    trunks = _trunks()
    for nm, reg, pts, hw, kinds, side0, mode, s0, s1, off in PATHS:
        if len(kinds) == 2:                                  # 6b (item 51): ritmo A-A-B (nao mais A/B estrito)
            kinds = (kinds[0], kinds[0], kinds[1])
        total = L.plen(pts)
        s1 = total - 2.0 if s1 is None else s1
        # 6b (item 51): estacoes OBRIGATORIAS = a mais proxima de cada ancora de luz (PATH_LIT) a <= 12 da polilinha -
        # com o passo maior a lanterna da luz nao pode cair num vao
        must = sorted(_station_near(pts, ax, ay) for _, ax, ay in PATH_LIT if L.polyline_dist(ax, ay, pts) <= 12.0)
        s, side, i, k = s0, side0, 0, 0
        while s < s1:
            x, y, dx, dy, turn = _at(pts, s)
            got = None
            kind = kinds[k % len(kinds)]
            for ds in (0.0, 1.5, -1.5, 3.0, -3.0, 4.5, -4.5):
                ss = min(max(s + ds, 0.0), total)
                xs, ys, dxs, dys, _ = _at(pts, ss)
                nxs, nys = -dys, dxs                                 # normal a ESQUERDA de quem segue a polilinha
                fen = _fenced(nm, 0 if mode == "on" else side, ss)
                for push in ((0.0,) if fen else (0.0, 0.6, 1.2, 1.8)):
                    if fen:
                        o_ = 0.0 if mode == "on" else side * (hw + FENCE_OFF)
                    elif mode == "on":
                        o_ = side * (0.6 + push) * (1.0 if hh(nm, i, "j") > 0.35 else -1.0)
                    else:
                        o_ = side * (hw + off + push)
                    px, py = xs + nxs * o_, ys + nys * o_
                    if not _xy_ok(px, py):
                        continue
                    if any(math.hypot(px - q[2], py - q[3]) < LAMP_GAP for q in out) or _near_lights(px, py, LAMP_GAP):
                        continue
                    if any(math.hypot(px - tx, py - ty) < TRUNK_CLR + tr for tx, ty, tr in trunks):   # 6b (item 51)
                        continue
                    if any(math.hypot(px - kx, py - ky) < kr for kx, ky, kr in LAMP_KEEP_OUT):
                        continue
                    sp = _spot(px, py, 0.95 if kind == "toro" else 0.8)
                    if sp is None or sp[1]:                          # nunca em cima da laje do caminho
                        continue
                    sgn = side if mode != "on" else 1.0
                    got = (px, py, sp[0], math.atan2(-nys * sgn, -nxs * sgn), fen)   # frente virada para o caminho
                    break
                if got:
                    break
            if got:
                out.append((reg, kind, got[0], got[1], got[2], got[3], nm, i, got[4]))
                k += 1
            side = -side
            # 6b (item 51): passo 16-20 nos caminhos e 18-22 na borda da clareira (era 10,5-14 / 13-17: 6-10 lanternas
            # por quadro); nas curvas 3 a menos (os nos, as escadas e os portoes continuam marcados)
            g = (18.0 if mode == "on" else 16.0) + 4.0 * hh(nm, i, "g")
            if turn > 0.3:
                g -= 3.0
            if not got:
                g = 4.0                                              # nao achou: tenta logo adiante (nao abre buraco)
            nxt = [m for m in must if s + 3.0 < m < s + g - 3.0]
            if nxt:
                g = nxt[0] - s
            s += g
            i += 1
    return out


# 6b (lead): pontos livres de lanterna de caminho - glicinia da pergola (52; 112) a >= 4 e o ponto das cameras
# C_Bam_Rampa / VFXPREV_Bambu (40; 66) a >= 2,5
LAMP_KEEP_OUT = ((52.0, 112.0, 4.0), (40.0, 66.0, 2.5))
TRUNK_CLR = 2.5          # 6b (item 51/44): lanterna a >= 2,5 da caixa de tronco (COL_DS_VegTrunk) do ds_veg


def _trunks():
    """(x, y, meia-largura) das colisoes de tronco do ds_veg (ja criadas: o ds_veg roda antes)"""
    out = []
    for o in bpy.data.objects:
        if o.type == "MESH" and o.name.startswith("COL_DS_VegTrunk"):
            bb_ = [o.matrix_world @ Vector(c) for c in o.bound_box]
            xs, ys = [v.x for v in bb_], [v.y for v in bb_]
            out.append(((min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2, max(max(xs) - min(xs), max(ys) - min(ys)) / 2))
    return out


def _station_near(pts, x, y, step=0.5):
    """estacao (comprimento ao longo da polilinha) do ponto mais proximo de (x, y)"""
    best, s = (1e9, 0.0), 0.0
    for a, b in zip(pts, pts[1:]):
        ln = math.hypot(b[0] - a[0], b[1] - a[1])
        n = max(1, int(ln / step))
        for j in range(n + 1):
            t = j / n
            d = math.hypot(a[0] + (b[0] - a[0]) * t - x, a[1] + (b[1] - a[1]) * t - y)
            if d < best[0]:
                best = (d, s + ln * t)
        s += ln
    return best[1]


def _sq(o, z):
    return [(-o, -o, z), (o, -o, z), (o, o, z), (-o, o, z)]


def lamp_box(mb, F, z0, hw=0.55, hz=1.15, frame=WD, cap=WD):
    """caixa de lanterna LEVE (andon) - 6b (item 50, mesma linguagem do ds_kit._box_lantern): 4 montantes de canto
    0,2, travessa de baixo e de cima, 2 cintas de 0,16 + montante central de 0,12 por face (grade 2 x 3), papel RECUADO
    0,16 atras da grade em 3 faixas - SO a do meio em Neon (Glass_DS_Lantern, 1/3 da area), as de cima e de baixo em
    papel quente fosco (Window_DS_Warm: le papel iluminado sem estourar no bloom) - e chapeu de 4 aguas com beiral de
    0,35 e botao. F no eixo; z0 = base da armacao. ~190 tris"""
    # volta 2: faixa acesa do meio com 50% da altura (~45% da face), faixas foscas estreitas, armacao mais fina
    t, rb = 0.17, 0.14
    za, zb = z0 + rb, z0 + hz - rb
    z1, z2 = za + 0.25 * (zb - za), za + 0.75 * (zb - za)
    p = hw - 0.17
    bb(mb, F, -p, p, -p, p, za, z1, PWARM)                           # papel: as emendas ficam dentro das cintas
    bb(mb, F, -p, p, -p, p, z1, z2, LGLOW)
    bb(mb, F, -p, p, -p, p, z2, zb, PWARM)
    for sx in (-1, 1):
        for sy in (-1, 1):
            cx, cy = sx * (hw - t / 2), sy * (hw - t / 2)
            bb(mb, F, cx - t / 2, cx + t / 2, cy - t / 2, cy + t / 2, z0, z0 + hz, frame)
    q = hw - 0.02
    bb(mb, F, -q, q, -q, q, z0, za, frame)                           # travessas de baixo e de cima
    bb(mb, F, -q, q, -q, q, zb, z0 + hz, frame)
    q = hw - 0.03
    for zz in (z1, z2):                                              # cintas (0,14)
        bb(mb, F, -q, q, -q, q, zz - 0.07, zz + 0.07, frame)
    bb(mb, F, -0.05, 0.05, -q, q, za, zb, frame)                     # montante central (as 4 faces)
    bb(mb, F, -q, q, -0.05, 0.05, za, zb, frame)
    zc = z0 + hz - 0.03                                              # (a travessa de baixo faz a vez da bandeja)
    o = hw + 0.35                                                    # beiral 0,35: sombreia o topo do papel
    loft(mb, F, [_sq(o, zc), _sq(o, zc + 0.11), _sq(0.16, zc + 0.5), _sq(0.05, zc + 0.74)], cap)
    return F.p(0.0, 0.0, z0 + hz * 0.5)


def stone_base(mb, F, key, r=0.8, top=0.36, n=6):
    """6b (item 50): pedra-base natural sob o poste (6 lados irregulares, ombro chanfrado, enterrada 0,3, sem tampa
    embaixo) - a lanterna ASSENTA numa pedra, nao sai do chao. 28 tris"""
    rot = 6.283 * hh(key, "pb")
    ks = [0.84 + 0.3 * hh(key, "pk", j) for j in range(n)]
    ring = lambda f, z: [(r * f * ks[j] * math.cos(rot + 2 * math.pi * j / n),
                          r * f * ks[j] * math.sin(rot + 2 * math.pi * j / n), z) for j in range(n)]
    loft(mb, F, [ring(1.08, -0.3), ring(1.0, top - 0.12), ring(0.78, top)], PST, caps=(False, True))


def andon_post(mb, F, key=0):
    """poste com caixa: pedra-base natural, poste de 0,46, caixa de lanterna no topo (luz ~4 acima do chao). ~260 tris"""
    stone_base(mb, F, key, 0.78, 0.42)
    h0 = 3.3 + 0.3 * hh(key, "h")
    bb(mb, F, -0.23, 0.23, -0.23, 0.23, 0.3, h0 + 0.02, WD)
    c = lamp_box(mb, F, h0, 0.7, 1.45)
    return c, h0 + 2.0, 0.7


def toro_low(mb, F, key=0):
    """toro baixo de caminho (oki-doro): soco de pedra, fuste, plataforma, camara de papel recuado entre 4 pilaretes de
    pedra, chapeu de 4 aguas com joia (hoju). 6b (item 50): a camara ganha 2 travessas de pedra (0,16 a frente do papel)
    e SO a faixa do meio fica em Neon (as de cima/baixo em papel quente fosco). ~190 tris"""
    s = 0.95 + 0.12 * hh(key, "s")
    loft(mb, F, [_sq(0.78 * s, -0.2), _sq(0.78 * s, 0.32 * s), _sq(0.6 * s, 0.42 * s)], PST)
    bb(mb, F, -0.27 * s, 0.27 * s, -0.27 * s, 0.27 * s, 0.4 * s, 1.36 * s, PST)
    bb(mb, F, -0.74 * s, 0.74 * s, -0.74 * s, 0.74 * s, 1.34 * s, 1.58 * s, PST)
    z0, z1 = 1.58 * s, 2.82 * s
    p = 0.44 * s
    za, zb = z0 + 0.25 * (z1 - z0), z0 + 0.75 * (z1 - z0)
    bb(mb, F, -p, p, -p, p, z0 - 0.04, za, PWARM)
    bb(mb, F, -p, p, -p, p, za, zb, LGLOW)
    bb(mb, F, -p, p, -p, p, zb, z1 + 0.04, PWARM)
    t = 0.22 * s
    q = 0.58 * s                                                     # pilaretes: face de fora 0,69 (plataforma 0,74)
    for sx in (-1, 1):
        for sy in (-1, 1):
            bb(mb, F, sx * q - t / 2, sx * q + t / 2, sy * q - t / 2, sy * q + t / 2, z0, z1, PST)
    w = 0.6 * s + 0.0                                                # travessas de pedra (frente 0,6s: 0,16s do papel)
    for zz in (za, zb):
        bb(mb, F, -w, w, -w, w, zz - 0.08, zz + 0.08, PST)
    loft(mb, F, [_sq(0.98 * s, z1 - 0.02), _sq(0.98 * s, z1 + 0.14 * s), _sq(0.3 * s, z1 + 0.56 * s),
                 _sq(0.17 * s, z1 + 0.6 * s), _sq(0.19 * s, z1 + 0.78 * s), _sq(0.02, z1 + 1.0 * s)], PST)
    return F.p(0.0, 0.0, (z0 + z1) / 2), z1 + 1.0 * s, 0.9


def tsuri_post(mb, F, key=0):
    """poste curto com braco e lanterna pendurada (tsuri-doro): pedra-base natural, poste, braco em balanco para +y
    (o caminho), gancho e caixa pendurada. ~280 tris"""
    h = 5.9 + 0.5 * hh(key, "h")
    stone_base(mb, F, key, 0.74, 0.4)
    bb(mb, F, -0.22, 0.22, -0.22, 0.22, 0.3, h, WD)
    bb(mb, F, -0.14, 0.14, -0.3, 1.82, h - 0.62, h - 0.34, WD)
    beam(mb, F, (0.0, 0.18, h - 1.7), (0.0, 1.0, h - 0.6), 0.14, 0.16, WD)
    bb(mb, F, -0.045, 0.045, 1.5, 1.6, h - 1.12, h - 0.6, WD)
    c = lamp_box(mb, sub(F, 0.0, 1.55, 0.0), h - 2.8, 0.56, 1.18)
    return c, h + 0.1, 0.6


LAMP_FN = {"andon": andon_post, "toro": toro_low, "tsuri": tsuri_post}


def signpost(mb, F, arrows=((0.0, 0.0), (65.0, 0.6), (-110.0, 1.2))):
    """placa de direcao: poste com chapeu de 2 aguas e 2-3 tabuas em seta (rumo relativo em graus, altura extra)"""
    bb(mb, F, -0.62, 0.62, -0.62, 0.62, -0.2, 0.3, PST)
    bb(mb, F, -0.2, 0.2, -0.2, 0.2, 0.25, 5.4, WD)
    ext(mb, F, [(-0.5, 5.35), (0.5, 5.35), (0.0, 5.75)], "x", -0.42, 0.42, WD)
    for deg, dz in arrows:
        Fa = sub(F, 0.0, 0.0, 0.0, math.radians(deg))
        z = 3.2 + dz
        ext(mb, Fa, [(0.16, z), (1.9, z), (2.35, z + 0.32), (1.9, z + 0.64), (0.16, z + 0.64)], "y", -0.07, 0.07, WM)


def wood_pile(mb, F, key=0):
    """pilha pequena de lenha rachada sobre 2 dormentes (6 achas de 6 lados)"""
    for y in (-0.55, 0.55):
        bb(mb, F, -1.3, 1.3, y - 0.16, y + 0.16, -0.05, 0.38, WD)        # 6b: dormente 0,2 acima da grama (era 0,07)
    for r, (n, z) in enumerate(((3, 0.55), (2, 1.12), (1, 1.66))):
        for i in range(n):
            x = (i - (n - 1) / 2) * 0.66 + (hh(key, r, i) - 0.5) * 0.12
            rr = 0.3 + 0.04 * hh(key, r, i, "r")
            rot = hh(key, r, i, "a") * 6.28
            ring = lambda yy: [(x + rr * math.cos(rot + 2 * math.pi * j / 6), yy, z + rr * math.sin(rot + 2 * math.pi * j / 6))
                               for j in range(6)]
            loft(mb, F, [ring(-1.0 - 0.15 * hh(key, r, i, "u")), ring(1.0 + 0.15 * hh(key, r, i, "v"))],
                 WM if (r + i) % 3 else BD)


def path_lamps(plan):
    """constroi as lanternas planejadas (1 objeto por regiao) e as luzes de PATH_LIT; devolve (luzes, alturas)"""
    lit = {}
    for lnm, ax, ay in PATH_LIT:
        best = None
        for j, q in enumerate(plan):
            d = math.hypot(q[2] - ax, q[3] - ay) + (6.0 if q[1] == "toro" else 0.0)
            if d < 15.0 and j not in lit.values() and (best is None or d < best[0]):
                best = (d, j)
        if best:
            lit[lnm] = best[1]
        else:
            print("ds_props AVISO luz de caminho %s sem lanterna perto de (%.0f, %.0f)" % (lnm, ax, ay))
    lit_of = {j: n for n, j in lit.items()}
    # 6b: 2 objetos em vez de 4 (Sul+Clareira | Vila+Forja): o papel quente fosco (Window_DS_Warm) e 1 material a mais
    # por objeto - a juncao devolve as MeshParts
    # 6c: "SulClareira" -> "SulClr": com o sufixo do export (__Stone_DS_Path_g1_7) o nome chegava a 49 caracteres (o
    # importador do Studio trunca perto de 50). A semente do MB continua a do nome antigo (mesmo sorteio)
    REG = {"Sul": "SulClr", "Clareira": "SulClr", "Vila": "VilaForja", "Forja": "VilaForja"}
    SEED = {"SulClr": "DS_Prop_PathLamps_SulClareira"}
    mbs = {}
    for r in sorted({q[0] for q in plan}):
        g = REG.get(r, r)
        if g not in mbs:
            import random as _rnd
            nm0 = SEED.get(g, "DS_Prop_PathLamps_%s" % g)
            mbs[g] = MB("DS_Prop_PathLamps_%s" % g, C, _rnd.Random(zlib.crc32(nm0.encode("utf-8")) & 0xffff), detail="hero")
        mbs[r] = mbs[g]
    lights, dims = [], []
    for j, (reg, kind, x, y, z, yaw, nm, i, fen) in enumerate(plan):
        F = Frame(x, y, z - 0.06, yaw - math.pi / 2)                    # +y local do tsuri = para o caminho
        c, h, r = LAMP_FN[kind](mbs[reg], F, (nm, i))
        dims.append((h, r, F.a))
        if j in lit_of:
            ln = "L_DSProp_Lamp_%s%s" % (lit_of[j], "Toro" if kind == "toro" else "")
            light(ln, "POINT", tuple(c), LIT_E[kind], K.WARM, 0.2)
            lights.append(ln)
    for mb in {id(m): m for m in mbs.values()}.values():
        mb.finish()
    return lights, dims


def lamp_cols(plan, dims, fence_cols):
    """caixa de colisao SO no toro (pedestal de pedra de 1,5): os postes finos (andon/tsuri, 0,46) ficam sem colisao,
    como os props pequenos (orcamento de COL da ilha: 1300); a lanterna NA linha de uma cerca (<= 0,8) usa a dela"""
    n = 0
    for (reg, kind, x, y, z, yaw, nm, i, fen), (h, r, a) in zip(plan, dims):
        if kind != "toro":
            continue
        if fen and any(L.seg_dist(x, y, p0[0], p0[1], p1[0], p1[1])[0] <= 0.8 for p0, p1 in fence_cols):
            continue
        col_box("DS_PropPath", (r * 1.6, r * 1.6, h), (x, y, z + h / 2), (0, 0, a))
        n += 1
    return n


def low_fence(mb, pts, z, h=2.5, step=3.6):
    """cerca baixa de caminho LEVE (~10 tris por stud; o K.railing tem ~23): mouroes 0,36 com a capa (kasagi) passando
    por cima e uma travessa no meio - a mesma silhueta do guarda-corpo do kit, sem a travessa baixa e os montantes"""
    P = [Vector((p[0], p[1], 0.0)) for p in pts]
    posts = []
    for i, (a, b) in enumerate(zip(P, P[1:])):
        d = b - a
        ln = d.length
        if ln < 0.3:
            continue
        n = max(1, int(math.ceil(ln / step)))
        posts += [a + d * (j / n) for j in range(n)]
        if i == len(P) - 2:
            posts.append(b)
        ang = math.atan2(d.y, d.x)
        e0 = 0.3 if i == 0 else 0.0
        e1 = 0.3 if i == len(P) - 2 else 0.0
        c = (a + b) / 2 + d.normalized() * (e1 - e0) / 2
        mb.box((ln + e0 + e1 + 0.02, 0.34, 0.2), (c.x, c.y, z + h - 0.1), (0, 0, ang), WD, 0.0)
        c = (a + b) / 2
        mb.box((ln, 0.16, 0.2), (c.x, c.y, z + h * 0.52), (0, 0, ang), WD, 0.0)
    for q in posts:
        mb.box((0.36, 0.36, h - 0.1), (q.x, q.y, z + (h - 0.1) / 2), (0, 0, 0), WD, 0.0)


def _fence_lines():
    """(nome, polilinha) de todos os setores: os dos caminhos (FENCED) e as bordas de terraco (FENCE_LINES)"""
    out = []
    for nm, reg, pts, hw, kinds, side0, mode, s0_, s1_, off in PATHS:
        for side, s0, s1 in FENCED.get(nm, ()):
            o_ = 0.0 if side == 0 else side * (hw + FENCE_OFF)
            line = []
            s = s0
            while s <= min(s1, L.plen(pts)) + 1e-6:
                x, y, dx, dy, _ = _at(pts, s)
                line.append((x - dy * o_, y + dx * o_))
                s += 1.0
            if len(line) >= 2:
                out.append(("%s%s" % (nm, "L" if side < 0 else ("O" if side > 0 else "")), line))
    return out + list(FENCE_LINES)


def _chords(p, tol=0.45):
    """polilinha densa -> menos cordas (desvio <= tol): as caixas de colisao da cerca"""
    out = []
    i = 0
    while i < len(p) - 1:
        j = i + 1
        while j + 1 < len(p):
            a, b = p[i], p[j + 1]
            if all(L.seg_dist(q[0], q[1], a[0], a[1], b[0], b[1])[0] <= tol for q in p[i + 1:j + 1]):
                j += 1
            else:
                break
        out.append((p[i], p[j]))
        i = j
    return out


def path_fences(mb, lamps):
    """cercas baixas em setores; cada linha e amostrada a cada ~1 e quebrada onde nao pode (rota, escada, colisao
    existente, chao fora de cota ou laje do caminho); trechos >= 6 viram K.railing (base = o chao mais baixo - 0,06,
    trechos de rampa cortados a cada 0,5 de desnivel). A COLISAO e continua no trecho (poucas caixas, por cordas); o
    VISUAL abre 1,0-1,2 em volta de cada lanterna que esta na linha. Devolve as cordas de colisao."""
    n_runs, total, cols = 0, 0.0, []
    for nm, line in _fence_lines():
        dense = []
        for a, b in zip(line, line[1:]):
            ln = math.hypot(b[0] - a[0], b[1] - a[1])
            k = max(1, int(ln / 1.0))
            dense += [(a[0] + (b[0] - a[0]) * t / k, a[1] + (b[1] - a[1]) * t / k) for t in range(k)]
        dense.append(line[-1])
        runs, cur = [], []
        for x, y in dense:
            ok = _xy_ok(x, y, ROUTE_CLR)
            z = None
            if ok:
                zexp = L.zone_of(x, y)
                t = _top(x, y, zexp) if zexp is not None else None
                ok = bool(t) and t[0].startswith(GROUND_OK) and abs(t[2] - zexp) < 1.0 and not \
                    t[0].startswith(PATH_SURF) and t[1] not in PATH_MATS
                if ok:
                    z = t[2]
                    ok = not _col_hit(x, y, z + 0.7, z + 2.4, 0.3) and not _side_hit(x, y, z, 0.45, 2.4)
            if ok:
                cur.append((x, y, z))
            elif cur:
                runs.append(cur)
                cur = []
        if cur:
            runs.append(cur)
        for r in runs:
            pieces = [r]
            if max(q[2] for q in r) - min(q[2] for q in r) > 0.5:      # rampa: trechos com desnivel <= 0,5
                pieces, cur = [], [r[0]]
                for q in r[1:]:
                    if q[2] - min(c[2] for c in cur) > 0.5 or max(c[2] for c in cur) - q[2] > 0.5:
                        pieces.append(cur)
                        cur = [cur[-1], q]
                    else:
                        cur.append(q)
                pieces.append(cur)
            for p in pieces:
                ln = sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(p, p[1:]))
                if ln < 6.0:
                    continue
                z = min(q[2] for q in p) - 0.06
                for a, b in _chords(p):
                    d = Vector((b[0] - a[0], b[1] - a[1]))
                    if d.length > 0.3:
                        col_box("DS_PropFence", (d.length + 0.4, 0.5, 3.0), ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2,
                                z + 1.5), (0, 0, math.atan2(d.y, d.x)))
                        cols.append((a, b))
                # visual: abre em volta das lanternas da linha
                vis, cur = [], []
                for q in p:
                    near = any(math.hypot(q[0] - l[2], q[1] - l[3]) < (1.25 if l[1] == "toro" else 1.05) for l in lamps)
                    if near:
                        if cur:
                            vis.append(cur)
                        cur = []
                    else:
                        cur.append(q)
                if cur:
                    vis.append(cur)
                for v in vis:
                    if len(v) < 2 or math.hypot(v[-1][0] - v[0][0], v[-1][1] - v[0][1]) < 3.0:
                        continue
                    simp = [v[0]]
                    for q in v[1:-1]:
                        if math.hypot(q[0] - simp[-1][0], q[1] - simp[-1][1]) >= 3.4:
                            simp.append(q)
                    simp.append(v[-1])
                    low_fence(mb, [(q[0], q[1]) for q in simp], z, 2.5, 3.6)
                n_runs += 1
                total += ln
    print("ds_props cercas de caminho: %d trechos, %.0f studs, %d caixas de colisao" % (n_runs, total, len(cols)))
    return cols


def path_life(mb, lamps):
    """bancos, placas e pilhas: cada um procura chao livre num raio de ate 4 em volta do ponto pedido"""
    n = 0
    for kind, nm, cands, deg in LIFE:
        r = {"bench": 2.6, "sign": 0.8, "pile": 1.5}[kind]
        got = None
        for x0, y0 in cands:
            for dd in (0.0, 1.5, 3.0, 4.5):
                for k in range(1 if dd == 0 else 8):
                    a = k * math.pi / 4
                    x, y = x0 + math.cos(a) * dd, y0 + math.sin(a) * dd
                    if not _xy_ok(x, y, ROUTE_CLR + 0.5) or any(math.hypot(x - q[2], y - q[3]) < r + 1.4 for q in lamps):
                        continue
                    sp = _spot(x, y, r, 3.0)
                    if sp and not sp[1]:
                        got = (x, y, sp[0])
                        break
                if got:
                    break
            if got:
                break
        if not got:
            print("ds_props AVISO %s %s sem lugar perto de %s" % (kind, nm, cands))
            continue
        x, y, z = got
        F = Frame(x, y, z - 0.06, math.radians(deg))
        if kind == "bench":
            K.bench(mb, F, 0.0, 0.0, 5.0, 1.8, 1.7)
            col_box("DS_PropPath", (5.0, 1.8, 1.8), (x, y, z + 0.9), (0, 0, F.a))
        elif kind == "sign":
            signpost(mb, F)
            col_box("DS_PropPath", (0.6, 0.6, 5.6), (x, y, z + 2.8))
        else:
            wood_pile(mb, F, (nm, "p"))
            col_box("DS_PropPath", (2.8, 2.4, 2.2), (x, y, z + 1.1), (0, 0, F.a))
        n += 1
    print("ds_props vida de caminho: %d pecas" % n)
    return n


def density():
    _col_bvh()
    plan = plan_lamps()
    by = {}
    for q in plan:
        by[q[6]] = by.get(q[6], 0) + 1
    print("ds_props lanternas de caminho: %d (na cerca %d) %s" % (len(plan), sum(1 for q in plan if q[8]),
                                                                   sorted(by.items())))
    lights, dims = path_lamps(plan)
    print("ds_props luzes NightOnly novas: %d %s" % (len(lights), lights))
    mf = MB("DS_Prop_PathFences", C, None, detail="hero")
    fcols = path_fences(mf, plan)
    mf.finish()
    nl = lamp_cols(plan, dims, fcols)
    _col_bvh()                                    # agora com os postes e cercas novos
    ml = MB("DS_Prop_PathLife", C, None, detail="hero")
    nv = path_life(ml, plan)
    ml.finish()
    print("ds_props COL novas da densidade: cercas %d + lanternas %d + vida %d = %d" % (len(fcols), nl, nv,
                                                                                      len(fcols) + nl + nv))
    out = os.environ.get("DS_PROP_PLAN")                 # planta das pecas novas (folha de conferencia)
    if out:
        import json
        json.dump({"lamps": [[q[1], q[2], q[3], q[8], q[4], q[6]] for q in plan], "lights": lights,
                   "fences": [[list(a[:2]), list(b[:2])] for a, b in fcols]}, open(out, "w"))
    return plan


# ================================================================== limpeza e build
def drop_blockout():
    """a cerca em setores do blockout (DS_Clr_Edges, so restam as cercas depois do ds_terrain) sai: e deste modulo"""
    ob = bpy.data.objects.get("DS_Clr_Edges")
    if ob:
        bpy.data.objects.remove(ob, do_unlink=True)


def _cams():
    import ds_village as V
    c = {
        "CAM_DSProp_PH_Clearing": ((-24.0, 160.0, T1 + L.EYE), (-38.0, 200.0, T1 + 2.4), 22),
        "CAM_DSProp_Miners": ((-30.0, 174.0, T1 + 4.2), (-37.6, 181.0, T1 + 1.6), 28),
        "CAM_DSProp_Stakes": ((-6.0, 170.0, T1 + 4.0), (-13.5, 177.5, T1 + 1.2), 30),
        "CAM_DSProp_FenceVila": ((-30.0, 214.0, T1 + L.EYE), (-43.0, 236.0, T1 + 1.8), 24),
        "CAM_DSProp_FenceBamboo": ((48.0, 160.0, T1 + L.EYE), (66.0, 140.0, T1 + 2.0), 22),
        "CAM_DSProp_PeSubida": ((16.0, 352.0, T1 + L.EYE), (16.0, 378.0, T1 + 4.0), 24),
        "CAM_DSProp_PH_VilLow": ((-52.0, 150.0, T1 + L.EYE), (-90.0, 185.0, T1 + 2.6), 22),
        "CAM_DSProp_PH_VilHigh": ((-82.0, 248.0, T2 + L.EYE), (-108.0, 236.0, T2 + 2.0), 22),
        "CAM_DSProp_Horta": ((-92.0, 128.0, T1 + 5.0), (-101.0, 138.0, T1 + 1.2), 26),
        "CAM_DSProp_Varal": ((-114.5, 172.0, T1 + 5.0), (-104.0, 176.0, T1 + 3.4), 26),
        "CAM_DSProp_Rebolo": ((-72.0, 182.0, T1 + 4.2), (-81.0, 188.0, T1 + 1.8), 28),
        "CAM_DSProp_Chaya": ((-44.0, 128.0, T1 + 4.6), (-56.5, 135.5, T1 + 2.6), 26),
        "CAM_DSProp_Kura": ((-104.0, 228.0, T2 + 4.8), (-108.0, 240.0, T2 + 1.6), 24),
        "CAM_DSProp_Cart": ((-84.0, 240.0, T2 + 4.2), (-91.5, 236.6, T2 + 1.3), 28),
        "CAM_DSProp_V5": ((-80.0, 300.0, T2 + 4.8), (-89.0, 295.0, T2 + 1.4), 28),
        "CAM_DSProp_Engawa": ((-72.0, 142.0, T1 + 5.0), (-79.0, 146.0, T1 + 2.0), 28),
        "CAM_DSProp_Lenha": ((-100.0, 180.0, T1 + 4.6), (-96.0, 170.0, T1 + 2.0), 26),
        "CAM_DSProp_ForgeE": ((44.0, 444.0, T4 + L.EYE), (64.0, 456.0, T4 + 1.6), 22),
        "CAM_DSProp_ForgeCrate": ((45.5, 453.0, T4 + 4.6), (50.5, 459.0, T4 + 1.4), 30),
        "CAM_DSProp_ForgeTogi": ((61.0, 457.0, T4 + 4.2), (65.5, 463.4, T4 + 2.0), 30),
        "CAM_DSProp_ForgeW": ((-36.0, 450.0, T4 + L.EYE), (-54.0, 464.0, T4 + 1.6), 24),
        "CAM_DSProp_PH_ForgeYard": ((20.0, 440.0, T4 + L.EYE), (40.0, 462.0, T4 + 2.0), 22),
        "CAM_DSProp_Tools": ((-31.0, 177.0, T1 + 3.4), (-36.5, 181.0, T1 + 1.4), 30),
        "CAM_DSProp_ForgeSE": ((49.0, 447.5, T4 + 4.5), (58.0, 441.6, T4 + 1.8), 28),
        "CAM_DSProp_LampNode": ((14.0, 146.0, T1 + 4.6), (22.0, 138.0, T1 + 6.0), 26),
        # entrada / saida: as pecas do kit no lugar das locais (antes x depois)
        "CAM_DSProp_EntToro": ((-6.0, 9.0, T0 + 5.0), (-12.0, 16.0, T0 + 4.0), 32),
        "CAM_DSProp_EntCourt": ((14.0, 36.0, T0 + 5.5), (-3.0, 2.0, T0 + 3.0), 22),
        "CAM_DSProp_EntFence": ((-12.0, 10.0, T0 + 4.5), (-21.0, 2.0, T0 + 1.4), 26),
        "CAM_DSProp_EntBridgeLamp": ((-6.4, -58.0, L.DECK + 6.8), (-9.3, -50.0, L.DECK + 5.4), 26),
        "CAM_DSProp_EntBridge": ((0.0, -78.0, L.DECK + 1.3 + L.EYE), (0.0, -20.0, L.DECK + 3.0), 22),
        "CAM_DSProp_ExitPath": ((-120.0, 470.0, T4 + 5.5), (-104.0, 560.0, T4 + 4.0), 22),
        "CAM_DSProp_ExitLamp": ((-106.0, 462.0, T4 + 5.2), (-112.0, 468.0, T4 + 5.5), 28),
    }
    return c


CAMS = _cams()


def build():
    drop_blockout()
    bpy.context.view_layer.update()
    old = (K.MIN_BEVEL, K.MIN_BEVEL_SIZE)
    K.MIN_BEVEL, K.MIN_BEVEL_SIZE = LOW_BEVEL
    try:
        mv = MB("DS_Prop_Village", C, None, detail="hero")
        village(mv)
        mv.finish()
        mc = MB("DS_Prop_Clearing", C, None, detail="hero")
        clearing(mc)
        mc.finish()
        mf = MB("DS_Prop_Forge", C, None, detail="hero")
        forge(mf)
        mf.finish()
        ml = MB("DS_Prop_Lamps", C, None, detail="hero")
        node_lamps(ml)
        ml.finish()
        bpy.context.view_layer.update()
        density()                                   # ONDA 4b: luz de caminho, cercas e vida (raycast no que ja existe)
    finally:
        K.MIN_BEVEL, K.MIN_BEVEL_SIZE = old
