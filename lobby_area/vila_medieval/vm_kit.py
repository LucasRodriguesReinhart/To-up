# vm_kit.py - KIT DA VILA do lobby VILA MEDIEVAL (onda V1): casa enxaimel parametrica + pecas de rua. Meta visual =
# ref/ref_01_estilo_vila.jpg. Roblox SEM textura: a FORMA carrega o detalhe (pedra arredondada com junta recuada,
# vigas salientes, telha em fiadas com espessura, janela com caixilho/venezianas/floreira, paralelepipedo em geometria).
#
# ============================================================ CONVENCOES
#   F     fm_parts.Frame(ox, oy, oz, ang) - referencial LOCAL (coordenadas BLENDER; use frame_r() para montar a partir
#         de coordenadas Roblox). Casa: origem no CENTRO DA PLANTA do terreo, NO CHAO (z=0 = piso da rua), +y = FRENTE
#         (rua), +x ao longo da frente (para a DIREITA de quem esta DENTRO olhando a rua), z para cima.
#         Lados: "F" (+y), "B" (-y), "R" (+x), "L" (-x).
#   Ff    face de parede: origem no meio da parede, na base; y=0 = PLANO DA FACE (pedra / reboco), +y para fora.
#   mb    fm_lib.MB do chamador. O kit desenha DENTRO do MB que voce passar: 1 MB = 1 objeto = 1 MeshPart por material.
#         Casas de fundo podem dividir o MESMO MB (uma quadra = um objeto, <= 6 MeshParts). dmb = MB de "enfeites"
#         compartilhado (flores, toldo, placa, argola): materiais fora do orcamento da casa, 1 objeto por trecho/quadra.
#   Escala: avatar 5,2. Porta 4,6 x 6,0 (vao) + arco de 0,8; terreo 8,0; andar 6,0; balanco 0,8 / 0,6; degrau 0,32.
#   Z-fight: nada coplanar ou a menos de 0,12 entre materiais diferentes (vidro 0,15 a frente do miolo, vigas
#   0,18-0,26 a frente do reboco, juntas 0,42 atras da face da pedra); pecas do mesmo material se interpenetram.
#   Determinismo: so hash (h01/rng: crc32 + fmix32 do murmur3) - nada de hash() do Python nem random global.
#
# ============================================================ MATERIAIS (<= 6 por casa)
#   reboco (Plaster_VM_Cream|Ochre|Peach), madeira escura (Wood_VM_Timber: vigas, caixilhos, venezianas, portas,
#   beiral), pedra (Stone_VM_Base|Warm|Grey|Trim: terreo, chamine, arco), junta/vidro (Stone_VM_Mortar), telha A + telha B
#   (Roof_VM_Terracotta|_B|_C: 2 tons por fiada; B tambem na cumeeira). Flores/toldo/placa vao no dmb.
#
# ============================================================ API
# CASA
#   house(mb, F, spec, dmb=None) -> info      spec = dict(PRESETS[k], ...) ou dict com as chaves de DEFAULT:
#       W D floors(2|3) gh fh jetty=(j1, j2) ridge('x' cumeeira paralela a frente | 'y' oitao para a rua) pitch eave
#       gable(beiral do oitao) plaster stone roof=(A, B) chimney(None | dict(x, y) local | 'auto') dormers(0..2)
#       balcony(None | andar 1/2) shop(bool: vitrine + toldo + placa) party(lados geminados: sem vao, sem pedra
#       aparente no terreo, oitao sem beiral) door=dict(side, x) flowers(cor das floreiras) seed lod(0 heroi | 1 fundo)
#       info = dict(eave_z, ridge_z, top_y (frente do ultimo andar), footprint, lamp=[], door=(ponto mundo))
#   house_col(area, F, spec, info)             colisao: 1 caixa (fachada fechada, nao entravel) + degrau da porta
#   PRESETS: "A3" 3 andares, cumeeira na frente, 2 aguas-furtadas | "B2" oitao para a rua, sacada | "C2" estreita,
#            oitao | "D3" loja (vitrine, toldo, placa) | "E2" 2 andares, agua-furtada | "F2" oitao, balanco duplo
# PECAS DA CASA (Ff = face de parede)
#   stone_face(mb, Ff, x0, x1, z0, z1, m, holes, seed, lod)  pedra arredondada irregular em fiadas (junta = miolo)
#   upper_wall(...) enxaimel de um andar | window(mb, Ff, c, zs, ww, wh, ...) caixilho+vidro+venezianas+floreira
#   window_ground(...) | door(mb, Ff, c, dw, dh, ...) porta de tabuas com arco de aduelas | balcony(...)
#   roof(mb, RF, length, span, pitch, eave, og, A, B, seed) telha em fiadas (espessura, 2 tons), cumeeira com capa,
#        beiral grosso, cachorros, bordas do oitao | gable_wall(...) oitao enxaimel | chimney(...) | dormer(...)
# RUA E PROPS
#   cobbles(mb, F, x0, x1, prof, seed, ...) paralelepipedo arredondado em geometria; prof = [(y, z_topo)] ao longo
#        de y local (rampa da ponte); lod=1 = pedras longas (longe). curb(...) meio-fio. mureta(...) pedra seca.
#   lamp_post(mb, F) -> ponto da luz | barrel | crate | cart (roda raiada) | tuft (grama alta) | pebble (pedra solta)
#   flower_box_plants(dmb, ...) | awning(dmb, ...) | hanging_sign(dmb, ...) | medallion(mb, F, r, top)
# ESTUDIO
#   blender -b --factory-startup --python vm_kit.py -- studio <pasta> [--roblox]   closes de cada peca + boneco 5,2
import math, random, zlib, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy, bmesh
from mathutils import Vector
import vm_lib as VL
import fm_lib
from fm_lib import MB, S, MATS, col_box
from fm_parts import Frame

# ------------------------------------------------------------------ materiais novos do kit (cor = cor do Roblox)
# V2b: os tons de pedra/paralelepipedo foram esquentados no vm_lib.VMMATS (que vence este setdefault); numeros iguais aqui
KITMATS = {
    "Stone_VM_Mortar":       (S(72, 68, 66), 0.9, 0.0, 0, None, 0.0),     # junta recuada + vidraca (escuro azulado)
    "Stone_VM_Warm":         (S(160, 148, 130), 0.85, 0.0, 0, None, 0.0),  # pedra cinza quente (2o tom)
    "Stone_VM_Grey":         (S(140, 136, 128), 0.85, 0.0, 0, None, 0.0),  # pedra cinza neutra-azulada (3o tom)
    "Roof_VM_Terracotta_C":  (S(214, 126, 72), 0.75, 0.0, 0, None, 0.0),  # telha clara (3o tom)
    "Stone_Paving_VM_B":     (S(162, 150, 132), 0.85, 0.0, 0, None, 0.0), # paralelepipedo 2o tom
    "Stone_Paving_VM_Joint": (S(112, 100, 86), 0.9, 0.0, 0, None, 0.0),   # areia/junta da rua (quente)
    "Leaf_VM_Tuft":          (S(92, 168, 56), 0.85, 0.0, 0, None, 0.0),   # grama alta / folhas das floreiras
    "Flower_VM_Red":         (S(214, 62, 58), 0.6, 0.0, 0, None, 0.0),
    "Flower_VM_Yellow":      (S(240, 196, 72), 0.6, 0.0, 0, None, 0.0),
    "Flower_VM_Pink":        (S(232, 128, 168), 0.6, 0.0, 0, None, 0.0),
    "Cloth_VM_Cream":        (S(232, 220, 196), 0.85, 0.0, 0, None, 0.0), # listra do toldo
    "Window_VM_Lamp":        (S(238, 204, 146), 0.4, 0.0, 0, None, 0.0),  # vidro da lanterna de dia (a luz e NightOnly)
    "Stone_Paving_VM_Cob":   (S(198, 180, 150), 0.85, 0.0, 0, None, 0.0), # paralelepipedo bege quente (ref_01)
    "Stone_Paving_VM_CobB":  (S(174, 158, 132), 0.85, 0.0, 0, None, 0.0), # 2o tom
}
for _k, _v in KITMATS.items():
    MATS.setdefault(_k, _v)

T = "Wood_VM_Timber"
PLK = "Wood_VM_Plank"
MOR = "Stone_VM_Mortar"
IRON = "Metal_VM_Iron"
BRONZE = "Metal_VM_Bronze"
GLASS_LAMP = "Window_VM_Lamp"
TUFT = "Leaf_VM_Tuft"
PAVE_A, PAVE_B, PAVE_J, PAVE_E = "Stone_Paving_VM_Cob", "Stone_Paving_VM_CobB", "Stone_Paving_VM_Joint", \
    "Stone_Paving_VM_Edge"
FLOWERS = {"red": "Flower_VM_Red", "yellow": "Flower_VM_Yellow", "pink": "Flower_VM_Pink"}

DOOR_W, DOOR_H = 4.6, 6.0
CORE = 0.42          # recuo do miolo (junta / fundo do vao) atras do plano da face


# ------------------------------------------------------------------ hash deterministico (murmur3 fmix32 sobre crc32)
def _fmix(h):
    h &= 0xffffffff
    h ^= h >> 16
    h = (h * 0x85ebca6b) & 0xffffffff
    h ^= h >> 13
    h = (h * 0xc2b2ae35) & 0xffffffff
    h ^= h >> 16
    return h


def hseed(*k):
    return _fmix(zlib.crc32(repr(k).encode("utf-8")))


def h01(*k):
    return hseed(*k) / 4294967296.0


def rng(*k):
    return random.Random(hseed(*k))


# ------------------------------------------------------------------ geometria basica (local ao Frame)
def frame_r(x, z, y, fx, fz):
    """Frame de CASA a partir de coordenadas ROBLOX: origem (x, z) no piso y, +y local = direcao (fx, fz) Roblox"""
    F = VL.face_frame(x, z, y, fx, fz)
    return Frame(F.o.x, F.o.y, F.o.z, F.a - math.pi / 2)


def sub(F, x=0.0, y=0.0, z=0.0, ang=0.0):
    p = F.p(x, y, z)
    return Frame(p.x, p.y, p.z, F.a + ang)


def bx(mb, F, x, y, z, sx, sy, sz, m, rx=0.0, ry=0.0, rz=0.0):
    if sx <= 1e-3 or sy <= 1e-3 or sz <= 1e-3:
        return
    mb.box((sx, sy, sz), F.p(x, y, z), F.r(rx, ry, rz), m, 0.0)


def bb(mb, F, x0, x1, y0, y1, z0, z1, m):
    x0, x1 = min(x0, x1), max(x0, x1)
    y0, y1 = min(y0, y1), max(y0, y1)
    z0, z1 = min(z0, z1), max(z0, z1)
    bx(mb, F, (x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2, x1 - x0, y1 - y0, z1 - z0, m)


def loft(mb, F, rings, m, closed=True, caps=(True, True)):
    """aneis de pontos LOCAIS (mesma contagem) ligados em sequencia; tampas no primeiro e no ultimo"""
    bm = mb.bm
    V = [[bm.verts.new(F.p(*p)) for p in r] for r in rings]
    k = len(V[0])
    fs = []
    seg = k if closed else k - 1
    for a, b in zip(V, V[1:]):
        for j in range(seg):
            j2 = (j + 1) % k
            try:
                fs.append(bm.faces.new((a[j], a[j2], b[j2], b[j])))
            except ValueError:
                pass
    if closed and k >= 3:
        for vs, on in ((list(reversed(V[0])), caps[0]), (V[-1], caps[1])):
            if on:
                try:
                    fs.append(bm.faces.new(vs))
                except ValueError:
                    pass
    if fs:
        bmesh.ops.recalc_face_normals(bm, faces=fs)
    return mb._post([v for r in V for v in r], m, 0.0, 0, 1)


def ext(mb, F, poly, axis, a0, a1, m):
    """prisma: poligono 2D no plano perpendicular a 'axis', de a0 a a1 ('x': (y,z); 'y': (x,z); 'z': (x,y))"""
    if len(poly) < 3 or abs(a1 - a0) < 1e-4:
        return
    if axis == "x":
        R = lambda a: [(a, u, v) for u, v in poly]
    elif axis == "y":
        R = lambda a: [(u, a, v) for u, v in poly]
    else:
        R = lambda a: [(u, v, a) for u, v in poly]
    loft(mb, F, [R(a0), R(a1)], m)


def lathe(mb, F, c, prof, n, m, rot=0.0):
    rings = []
    for r, h in prof:
        r = max(r, 0.01)
        rings.append([(c[0] + r * math.cos(rot + 2 * math.pi * j / n), c[1] + r * math.sin(rot + 2 * math.pi * j / n),
                       c[2] + h) for j in range(n)])
    loft(mb, F, rings, m)


def beam(mb, F, a, b, depth, width, m=T):
    """viga de a ate b (pontos locais). Para viga num plano de parede: depth = espessura saliente (normal a parede),
    width = largura no plano (o MB orienta a secao com Z para cima)."""
    mb.beam(F.p(*a), F.p(*b), depth, width, m, 0.0)


def even(a, b, step):
    n = max(1, int(math.ceil((b - a) / step - 1e-6)))
    return [a + (b - a) * (i + 0.5) / n for i in range(n)]


def panel(mb, F, x0, x1, z0, z1, y0, y1, holes, m):
    """placa (x0..x1, z0..z1, espessura y0..y1) menos vaos retangulares [(a, b, za, zb)]"""
    hs = [(max(a, x0), min(b, x1), max(za, z0), min(zb, z1)) for a, b, za, zb in holes
          if b > x0 + 1e-3 and a < x1 - 1e-3 and zb > z0 + 1e-3 and za < z1 - 1e-3]
    xs = sorted(set([x0, x1] + [v for a, b, _, _ in hs for v in (a, b)]))
    for a, b in zip(xs, xs[1:]):
        if b - a < 1e-3:
            continue
        mid = (a + b) / 2
        cut = sorted((za, zb) for ha, hb, za, zb in hs if ha < mid < hb)
        zz = z0
        for za, zb in cut:
            if za > zz + 1e-3:
                bb(mb, F, a, b, y0, y1, zz, za, m)
            zz = max(zz, zb)
        if z1 > zz + 1e-3:
            bb(mb, F, a, b, y0, y1, zz, z1, m)


def _clip(poly, a, b, c):
    return VL.clip_half(poly, a, b, c)


def poly_minus_rect(poly, r):
    """poligono convexo (u, v) menos o retangulo r=(u0, u1, v0, v1) -> lista de poligonos convexos"""
    u0, u1, v0, v1 = r
    out = []
    below = _clip(poly, 0, -1, v0)                    # v <= v0
    above = _clip(poly, 0, 1, -v1)                    # v >= v1
    mid = _clip(_clip(poly, 0, 1, -v0), 0, -1, v1)    # v0 <= v <= v1
    left = _clip(mid, -1, 0, u0) if mid else []       # u <= u0
    right = _clip(mid, 1, 0, -u1) if mid else []      # u >= u1
    for p in (below, above, left, right):
        if len(p) >= 3:
            out.append(p)
    return out


# ------------------------------------------------------------------ pedras
def pillow(mb, F, x0, x1, z0, z1, yb, yf, m, c=0.3, jit=None, cut=None):
    """pedra de parede ARREDONDADA: contorno irregular (jit = 4 deslocamentos (dx, dz) dos cantos; cut = (diagonal
    0|1, k1, k2) corta 2 cantos opostos -> hexagono), FACE em +y = yf com chanfro em 2 degraus (le arredondada com
    sombreamento chapado), fundo em yb (dentro do miolo, sem tampa). 40 tris (hexagono) / 26 (retangulo)."""
    w, h = x1 - x0, z1 - z0
    c = max(0.08, min(c, 0.34 * w, 0.34 * h))
    base = [(x0, z0), (x1, z0), (x1, z1), (x0, z1)]
    if jit:
        base = [(px + jx, pz + jz) for (px, pz), (jx, jz) in zip(base, jit)]
    if cut:
        dg, k1, k2 = cut
        k1, k2 = k1 * min(w, h), k2 * min(w, h)
        pts = []
        for i, (px, pz) in enumerate(base):
            k = (k1 if i < 2 else k2) if i % 2 == dg else 0.0
            if k <= 0.02:
                pts.append((px, pz))
                continue
            prv, nxt = base[i - 1], base[(i + 1) % 4]
            for q in (prv, nxt):
                dx, dz = q[0] - px, q[1] - pz
                ln = math.hypot(dx, dz) or 1.0
                pts.append((px + dx / ln * k, pz + dz / ln * k))
            # ordem: o ponto em direcao ao anterior vem primeiro
        base = pts
    cx = sum(p[0] for p in base) / len(base)
    cz = sum(p[1] for p in base) / len(base)

    def ring(y, ins):
        out = []
        for px, pz in base:
            dx, dz = px - cx, pz - cz
            ln = math.hypot(dx, dz) or 1.0
            out.append((px - dx / ln * ins, y, pz - dz / ln * ins))
        return out
    loft(mb, F, [ring(yb, 0.0), ring(yf - c, 0.0), ring(yf - c * 0.32, c * 0.62), ring(yf, c * 1.45)], m,
         caps=(False, True))


def through_stone(mb, F, x0, x1, y0, y1, z0, z1, m, c=0.2, jit=None, zfn=None):
    """pedra de muro seco (as DUAS faces y0 e y1 chanfradas + topo plano): 28 tris. zfn(x) = desnivel da base
    em x (muro sobre rampa: a pedra acompanha a rampa)"""
    w, h = x1 - x0, z1 - z0
    c = max(0.06, min(c, 0.3 * w, 0.3 * h))
    cx, cz = (x0 + x1) / 2, (z0 + z1) / 2
    base = [(x0, z0), (x1, z0), (x1, z1), (x0, z1)]
    if jit:
        base = [(px + jx, pz + jz) for (px, pz), (jx, jz) in zip(base, jit)]

    def ring(y, ins):
        out = []
        for px, pz in base:
            qx = px - math.copysign(ins, px - cx)
            out.append((qx, y, pz - math.copysign(ins, pz - cz) + (zfn(qx) if zfn else 0.0)))
        return out
    loft(mb, F, [ring(y0, c), ring(y0 + c, 0.0), ring(y1 - c, 0.0), ring(y1, c)], m)


def cobble(mb, F, pts, ztop_fn, m, bed=0.2, c1=0.13, c2=0.36):
    """pedra de piso arredondada: contorno = 4 pontos locais (x, y); topo por vertice = ztop_fn(x, y) (rampas);
    3 aneis (base enterrada na junta, chanfro, topo) = 18 tris + tampas"""
    cx = sum(p[0] for p in pts) / 4
    cy = sum(p[1] for p in pts) / 4

    def ring(ins, dz):
        out = []
        for px, py in pts:
            dx, dy = px - cx, py - cy
            ln = math.hypot(dx, dy) or 1.0
            qx, qy = px - dx / ln * ins * 1.2, py - dy / ln * ins * 1.2
            out.append((qx, qy, ztop_fn(qx, qy) + dz))
        return out
    loft(mb, F, [ring(0.0, -bed), ring(c1, -0.07), ring(c2, 0.02)], m)


def pebble(mb, F, x, y, z, s, m, k=0):
    """pedra solta na borda da rua / grama (bloco chanfrado girado)"""
    r = rng("pebble", round(x, 2), round(y, 2), k)
    a = r.uniform(0, math.pi)
    Fp = sub(F, x, y, z, a)
    w, d, h = s * r.uniform(0.9, 1.4), s * r.uniform(0.7, 1.0), s * r.uniform(0.45, 0.7)
    through_stone(mb, Fp, -w / 2, w / 2, -d / 2, d / 2, -0.15, h, m, c=min(w, d, h) * 0.3)


def stone_face(mb, Ff, x0, x1, z0, z1, m, holes=(), seed=0, lod=0, course=(1.1, 1.75), length=(1.3, 3.0),
               back=-0.62, gap=0.14, proud=(-0.08, 0.1), m2=None, p2=0.0, zlim=None):
    """PEDRA ARREDONDADA IRREGULAR em fiadas no plano y=0 de Ff (a junta e o miolo escuro CORE atras). holes =
    vaos [(x0, x1, z0, z1)] (a fiada que pega o vao so em parte vira pedra baixa acima/abaixo dele; < 0,35 fica
    para o lintel/peitoril). m2/p2: 2o tom de pedra numa fracao p2 das pedras. lod=1: pedras maiores.
    zlim(x) -> (z_min, z_max) recorta a pedra por x (arco da ponte, rampa): pedra < 0,3 de altura e descartada."""
    r = rng("stoneface", seed)
    if lod == 1:
        course = (course[0] * 1.35, course[1] * 1.35)
        length = (length[0] * 1.5, length[1] * 1.6)
    elif lod >= 2:                                   # parede-meia / fundos de casa de fundo: blocos grandes
        course = (course[0] * 2.0, course[1] * 2.0)
        length = (length[0] * 2.6, length[1] * 2.6)
    z = z0
    ci = 0
    while z < z1 - 0.25:
        h = r.uniform(*course)
        if z1 - (z + h) < 0.75:
            h = z1 - z
        za, zb = z, z + h
        cuts = [hl for hl in holes if not (hl[3] <= za + 1e-3 or hl[2] >= zb - 1e-3)]
        xs = sorted(set([x0, x1] + [v for hl in cuts for v in (hl[0], hl[1]) if x0 < v < x1]))
        segs = []
        for a, b in zip(xs, xs[1:]):
            mid = (a + b) / 2
            cov = sorted((hl[2], hl[3]) for hl in cuts if hl[0] < mid < hl[1])
            if not cov:
                segs.append((a, b, za, zb))
                continue
            zz = za
            for ha, hb in cov:
                if ha - zz >= 0.35:
                    segs.append((a, b, zz, ha))
                zz = max(zz, hb)
            if zb - zz >= 0.35:
                segs.append((a, b, zz, zb))
        for a, b, sa, sb in segs:
            x = a
            first = True
            while x < b - 0.2:
                ln = r.uniform(*length) * (0.6 if first and ci % 2 else 1.0)
                first = False
                x2 = min(b, x + ln)
                if b - x2 < 0.9:
                    x2 = b
                g = gap / 2
                jit = [(r.uniform(-0.09, 0.09), r.uniform(-0.07, 0.07)) for _ in range(4)]
                # cantos da borda do trecho nao saem do contorno (quina da casa / borda do vao)
                for i, (px, pz) in enumerate(((x, sa), (x2, sa), (x2, sb), (x, sb))):
                    jx, jz = jit[i]
                    if abs(px - a) < 1e-6 or abs(px - b) < 1e-6:
                        jx = 0.0
                    if abs(pz - z0) < 1e-6 or abs(pz - z1) < 1e-6:
                        jz = 0.0
                    jit[i] = (jx, jz)
                mm = m2 if (m2 and r.random() < p2) else m
                za_, zb_ = sa + g + r.uniform(0.0, 0.1), sb - g - r.uniform(0.0, 0.1)
                if zlim is not None:
                    lims = [zlim(xx) for xx in (x, (x + x2) / 2, x2)]
                    za_ = max([za_] + [l[0] + g for l in lims])
                    zb_ = min([zb_] + [l[1] - g for l in lims])
                    if zb_ - za_ < 0.3:
                        x = x2
                        continue
                cut = (r.randint(0, 1), r.uniform(0.15, 0.4), r.uniform(0.15, 0.4)) if r.random() < 0.8 else None
                pillow(mb, Ff, x + g, x2 - g, za_, zb_, back, r.uniform(*proud), mm,
                       c=r.uniform(0.28, 0.42), jit=jit, cut=cut)
                x = x2
        z = zb
        ci += 1


# ------------------------------------------------------------------ janelas, porta
def window(mb, Ff, c, zs, ww, wh, dmb=None, shutters=True, box=True, flowers="red", mull=1, seed=0, sill=T):
    """janela de andar enxaimel no plano y=0 (reboco). O vao no reboco e do chamador (panel com holes).
    caixilho saliente, vidro (junta escura) 0,15 a frente do miolo, travessa e mainel, peitoril, venezianas
    abertas com travessas em Z e floreira com flores (dmb)."""
    hw = ww / 2
    fw = 0.26
    bb(mb, Ff, c - hw - fw, c - hw + 0.14, -0.36, 0.16, zs - fw, zs + wh + fw, T)
    bb(mb, Ff, c + hw - 0.14, c + hw + fw, -0.36, 0.16, zs - fw, zs + wh + fw, T)
    bb(mb, Ff, c - hw, c + hw, -0.36, 0.16, zs + wh - 0.14, zs + wh + fw, T)
    bb(mb, Ff, c - hw, c + hw, -0.36, 0.16, zs - fw, zs + 0.14, T)
    bb(mb, Ff, c - hw, c + hw, -CORE - 0.1, -CORE + 0.15, zs, zs + wh, MOR)               # vidraca
    for k in range(mull):
        xm = c - hw + ww * (k + 1) / (mull + 1)
        bb(mb, Ff, xm - 0.08, xm + 0.08, -0.3, -0.12, zs, zs + wh, T)
    zt = zs + wh * 0.62
    bb(mb, Ff, c - hw, c + hw, -0.3, -0.12, zt - 0.08, zt + 0.08, T)
    bb(mb, Ff, c - hw - 0.42, c + hw + 0.42, -0.3, 0.44, zs - fw - 0.22, zs - fw + 0.02, sill)   # peitoril
    if shutters:
        for s in (-1, 1):
            xa = c + s * (hw + fw + 0.04)
            xb = c + s * (hw + fw + 0.04 + hw * 0.92)
            x0, x1 = min(xa, xb), max(xa, xb)
            bb(mb, Ff, x0, x1, 0.22, 0.36, zs - 0.1, zs + wh + 0.1, T)
            for zz in (zs + 0.38, zs + wh - 0.38):
                bb(mb, Ff, x0 + 0.08, x1 - 0.08, 0.36, 0.48, zz - 0.11, zz + 0.11, T)
    if box:
        z0 = zs - fw - 1.0
        bb(mb, Ff, c - hw - 0.25, c + hw + 0.25, 0.05, 0.78, z0, zs - fw - 0.22, T)
        if dmb is not None:
            flower_box_plants(dmb, Ff, c, 0.42, zs - fw - 0.22, ww + 0.4, flowers, seed)


def window_ground(mb, Ff, c, zs, ww, wh, stone, dmb=None, shutters=True, flowers="red", seed=0, mull=1):
    """janela do terreo de pedra: caixilho recuado, verga de madeira grossa, peitoril de pedra, venezianas.
    Vao para o stone_face: (c-ww/2-0.32, c+ww/2+0.32, zs-0.45, zs+wh+0.72)"""
    hw = ww / 2
    bb(mb, Ff, c - hw - 0.3, c - hw + 0.14, -0.62, -0.06, zs - 0.1, zs + wh + 0.05, T)
    bb(mb, Ff, c + hw - 0.14, c + hw + 0.3, -0.62, -0.06, zs - 0.1, zs + wh + 0.05, T)
    bb(mb, Ff, c - hw - 0.75, c + hw + 0.75, -0.62, 0.14, zs + wh, zs + wh + 0.72, T)          # verga
    bb(mb, Ff, c - hw - 0.5, c + hw + 0.5, -0.62, 0.36, zs - 0.45, zs - 0.08, stone)           # peitoril
    bb(mb, Ff, c - hw, c + hw, -CORE - 0.2, -CORE + 0.15, zs - 0.1, zs + wh, MOR)
    for k in range(mull):
        xm = c - hw + ww * (k + 1) / (mull + 1)
        bb(mb, Ff, xm - 0.08, xm + 0.08, -0.3, -0.12, zs - 0.1, zs + wh, T)
    zt = zs + wh * 0.55
    bb(mb, Ff, c - hw, c + hw, -0.3, -0.12, zt - 0.08, zt + 0.08, T)
    if shutters:
        for s in (-1, 1):
            xa = c + s * (hw + 0.34)
            xb = c + s * (hw + 0.34 + hw * 0.9)
            x0, x1 = min(xa, xb), max(xa, xb)
            bb(mb, Ff, x0, x1, 0.14, 0.28, zs - 0.05, zs + wh, T)
            for zz in (zs + 0.35, zs + wh - 0.4):
                bb(mb, Ff, x0 + 0.08, x1 - 0.08, 0.28, 0.4, zz - 0.11, zz + 0.11, T)
    if dmb is not None and flowers:
        bb(mb, Ff, c - hw - 0.2, c + hw + 0.2, 0.0, 0.7, zs - 1.05, zs - 0.45, T)
        flower_box_plants(dmb, Ff, c, 0.36, zs - 0.45, ww + 0.3, flowers, seed)


def ground_window_hole(c, zs, ww, wh):
    return (c - ww / 2 - 0.32, c + ww / 2 + 0.32, zs - 0.45, zs + wh + 0.72)


def door_hole(c, dw=DOOR_W, dh=DOOR_H):
    return (c - dw / 2 - 0.95, c + dw / 2 + 0.95, -1.0, dh + 1.55)


def door(mb, Ff, c, stone, dw=DOOR_W, dh=DOOR_H, dmb=None, seed=0):
    """porta de tabuas recuada com ARCO de aduelas (topo reto no vao do stone_face, le como verga de pedra
    aparelhada), ombreiras alternadas, soleira/degrau e travessas. Vao do stone_face = door_hole(c)."""
    r = rng("door", seed)
    hw = dw / 2
    H = door_hole(c, dw, dh)
    ow = H[1] - c                                   # meia largura do vao do stone_face
    ztop = H[3]
    rise = 0.8
    R = (hw * hw + rise * rise) / (2 * rise)
    zc = dh + rise - R
    th0 = math.atan2(dh - zc, hw)
    yb, yf = -0.66, 0.14
    # ombreiras (do chao ate a nascenca do arco), pedras alternadas longas/curtas
    for s in (-1, 1):
        z = -0.3
        k = 0
        while z < dh - 0.2:
            h = 1.15 if k % 2 == 0 else 0.92
            z2 = min(dh, z + h)
            if dh - z2 < 0.5:
                z2 = dh
            wj = ow - hw if k % 2 == 0 else (ow - hw) * 0.72
            xa, xb = (c + s * hw, c + s * (hw + wj))
            pillow(mb, Ff, min(xa, xb) + 0.04, max(xa, xb) - 0.04, z + 0.05, z2 - 0.05, yb, yf + r.uniform(-0.02, 0.04),
                   stone, c=0.14)
            z = z2
            k += 1
    # aduelas: raios do centro do arco ate a borda do vao (topo reto), chave mais alta
    n = 7
    edges = [th0 + (math.pi - 2 * th0) * i / n for i in range(n + 1)]

    def hit(th):
        ct, st = math.cos(th), math.sin(th)
        t1 = (ztop - zc) / st if st > 1e-6 else 1e9
        t2 = (ow / abs(ct)) if abs(ct) > 1e-6 else 1e9
        t = min(t1, t2)
        return (c + ct * t, zc + st * t)
    for i in range(n):
        a, b = edges[i] + (0.012 if i > 0 else 0.0), edges[i + 1] - (0.012 if i < n - 1 else 0.0)
        pts = [(c + R * math.cos(a), zc + R * math.sin(a))]
        if i == 0:
            pts = [(c + hw, dh), (c + ow, dh)]
        hb, ha = hit(b), hit(a)
        if i == 0:
            pts.append((c + ow, ha[1]) if ha[0] >= c + ow - 1e-6 else ha)
        else:
            pts.append(ha)
        # canto superior entre os dois raios (quando um bate no lado e o outro no topo)
        if (abs(ha[0] - (c + ow)) < 1e-4 and abs(hb[1] - ztop) < 1e-4):
            pts.append((c + ow, ztop))
        if (abs(ha[1] - ztop) < 1e-4 and abs(hb[0] - (c - ow)) < 1e-4):
            pts.append((c - ow, ztop))
        if i == n - 1:
            pts.append(hb)
            pts.append((c - ow, dh))
            pts.append((c - hw, dh))
        else:
            pts.append(hb)
            pts.append((c + R * math.cos(b), zc + R * math.sin(b)))
        # poligono no plano (x, z) -> ext ao longo de y
        dz = 0.14 if i == n // 2 else 0.0
        ext(mb, Ff, [(px, pz) for px, pz in pts], "y", yb, yf + dz + 0.02, stone)
    # tabuas (topo seguindo o arco), juntas = miolo escuro
    nb = 4
    for k in range(nb):
        xa = c - hw + dw * k / nb + 0.04
        xb = c - hw + dw * (k + 1) / nb - 0.04

        def arc_z(x):
            dxx = x - c
            return zc + math.sqrt(max(0.0, R * R - dxx * dxx)) - 0.04
        y0, y1 = -0.62, -0.28 + (0.03 if k % 2 else 0.0)
        ext(mb, Ff, [(xa, -0.05), (xb, -0.05), (xb, arc_z(xb)), ((xa + xb) / 2, arc_z((xa + xb) / 2)), (xa, arc_z(xa))],
            "y", y0, y1, T)
    for zz in (1.3, dh - 1.3):
        bb(mb, Ff, c - hw + 0.15, c + hw - 0.15, -0.3, -0.16, zz - 0.18, zz + 0.18, T)
    bb(mb, Ff, c - hw - 0.7, c + hw + 0.7, -0.5, 1.1, -0.3, 0.32, stone)                           # soleira / degrau
    if dmb is not None:
        dmb.cyl(0.32, 0.12, Ff.p(c + hw * 0.55, -0.12, dh * 0.5), Ff.r(math.pi / 2, 0, 0), IRON, 8, bevel=0.0)


# ------------------------------------------------------------------ enxaimel de um andar
def bays_for(L, kind, rr, party=False):
    """divide a parede em vaos (~3,1) e escolhe o tipo de cada um: 'win' janela, 'X' cruz, 'Dl'/'Dr' diagonal,
    'M' figura do 'homem' (diagonais em V). kind = 'F' frente | 'B' fundos | 'S' lado"""
    n = max(2, int(round(L / 3.1)))
    xs = [-L / 2 + L * i / n for i in range(n + 1)]
    if party:
        ks = ["X" if 0 < i < n - 1 else ("Dl" if i == 0 else "Dr") for i in range(n)]
    elif kind == "F":
        if n == 2:
            ks = ["win", "win"]
        elif n == 3:
            ks = ["win", "win", "win"] if rr.random() < 0.5 else ["Dl", "win", "Dr"]
        else:
            ks = ["Dl"] + ["win" if (i % 2 == 1 or rr.random() < 0.35) else ("X" if rr.random() < 0.5 else "M")
                           for i in range(1, n - 1)] + ["Dr"]
            if ks.count("win") < 2:
                ks[1] = ks[-2] = "win"
    elif kind == "B":
        ks = ["win" if i % 2 == 1 else ("X" if rr.random() < 0.5 else "Dl" if i < n / 2 else "Dr") for i in range(n)]
    else:
        mid = n // 2
        ks = ["win" if (i == mid and n >= 3) else ("X" if 0 < i < n - 1 else ("Dl" if i == 0 else "Dr"))
              for i in range(n)]
        if n == 2:
            ks = ["Dl", "Dr"]
    return xs, ks


def upper_wall(mb, Ff, L, h, pl, xs, ks, dmb=None, flowers="red", seed=0, tall=False, lod=0, shutters=True):
    """um andar enxaimel no plano y=0: reboco (placa com vaos) + frechais, montantes, peitoril corrido, vergas,
    cruzes/diagonais e janelas. Vigas 0,16-0,26 a frente do reboco."""
    zr = 1.45                          # topo do peitoril corrido (Brustungsriegel)
    zs, wh = (1.65, 2.5) if not tall else (0.55, 3.75)
    wins = []
    for (a, b), k in zip(zip(xs, xs[1:]), ks):
        if k == "win":
            ww = min(2.0, (b - a) - 1.15)
            if ww >= 1.1:
                wins.append(((a + b) / 2, ww))
    holes = [(c - ww / 2, c + ww / 2, zs, zs + wh) for c, ww in wins]
    panel(mb, Ff, -L / 2, L / 2, 0.14, h - 0.14, -CORE, 0.0, holes, pl)
    bb(mb, Ff, -L / 2 - 0.03, L / 2 + 0.03, -0.32, 0.26, 0.0, 0.52, T)               # frechal de baixo (soleira)
    bb(mb, Ff, -L / 2 - 0.03, L / 2 + 0.03, -0.32, 0.2, h - 0.44, h, T)              # frechal de cima
    for i, x in enumerate(xs):
        w = 0.56 if i in (0, len(xs) - 1) else 0.42
        x0 = max(-L / 2, x - w / 2) if i == 0 else x - w / 2
        x1 = min(L / 2, x + w / 2) if i == len(xs) - 1 else x + w / 2
        if i == 0:
            x0, x1 = -L / 2, -L / 2 + w
        if i == len(xs) - 1:
            x0, x1 = L / 2 - w, L / 2
        bb(mb, Ff, x0, x1, -0.32, 0.2, 0.5, h - 0.42, T)
    yb = -0.06
    for (a, b), k in zip(zip(xs, xs[1:]), ks):
        a2, b2 = a + 0.21, b - 0.21
        if k != "X" and not (tall and k == "win"):
            bb(mb, Ff, a2, b2, -0.32, 0.17, zr - 0.36, zr, T)                       # peitoril corrido
        if k == "win":
            c = (a + b) / 2
            ww = min(2.0, (b - a) - 1.15)
            if ww < 1.1:
                continue
            bb(mb, Ff, a2, b2, -0.32, 0.17, zs + wh + 0.2, zs + wh + 0.56, T)        # verga
            if not tall and lod == 0 and (b2 - a2) > 1.5:                           # cruz sob a janela
                beam(mb, Ff, (a2 + 0.05, yb, 0.5), (b2 - 0.05, yb, zr - 0.36), 0.42, 0.3)
                beam(mb, Ff, (b2 - 0.05, yb, 0.5), (a2 + 0.05, yb, zr - 0.36), 0.42, 0.3)
            window(mb, Ff, c, zs, ww, wh, dmb=dmb, box=not tall and lod == 0, flowers=flowers,
                   seed=(seed, round(c, 2)), shutters=shutters and lod == 0)
        elif k == "X":
            beam(mb, Ff, (a2, yb, 0.5), (b2, yb, h - 0.44), 0.42, 0.38)
            beam(mb, Ff, (b2, yb, 0.5), (a2, yb, h - 0.44), 0.42, 0.38)
        elif k == "Dl":
            beam(mb, Ff, (a2, yb, 0.5), (b2, yb, h - 0.44), 0.42, 0.38)
        elif k == "Dr":
            beam(mb, Ff, (b2, yb, 0.5), (a2, yb, h - 0.44), 0.42, 0.38)
        elif k == "M":
            m_ = (a + b) / 2
            beam(mb, Ff, (a2, yb, 0.5), (m_, yb, zr - 0.2), 0.42, 0.36)
            beam(mb, Ff, (b2, yb, 0.5), (m_, yb, zr - 0.2), 0.42, 0.36)
            beam(mb, Ff, (m_, yb, zr), (a2, yb, h - 0.44), 0.42, 0.36)
            beam(mb, Ff, (m_, yb, zr), (b2, yb, h - 0.44), 0.42, 0.36)
            bb(mb, Ff, m_ - 0.2, m_ + 0.2, -0.32, 0.18, 0.5, h - 0.42, T)
    return wins


# ------------------------------------------------------------------ telhado
def roof(mb, RF, length, span, pitch, eave, og, A, B, seed=0, course=1.05, t=0.32, lod=0, pB=0.3, barge=True,
         rafters=True):
    """TELHADO de duas aguas no referencial RF (origem no meio do topo das paredes, cumeeira ao longo de +x local,
    aguas para +-y). span = largura entre os frechais, eave = beiral, og = (beiral do oitao em -x, em +x).
    Telha em FIADAS com espessura (cada fiada apoia a borda baixa na de baixo: degrau de t a cada 'course'),
    cada fiada em 2-5 pedacos com borda irregular e 2 tons (A / B), forro de tabuas por baixo (madeira), beiral grosso
    (testeira), cachorros sob o beiral, capa de cumeeira em telhas (B) e tabuas de borda nos oitoes."""
    r = rng("roof", seed)
    p = math.radians(pitch)
    tp, cp, sp = math.tan(p), math.cos(p), math.sin(p)
    half = span / 2.0
    rise = half * tp
    x0, x1 = -length / 2 - og[0], length / 2 + og[1]
    Ls = (half + eave) / cp
    if lod:
        course *= 1.3
    for s in (-1, 1):
        E = (s * (half + eave), -eave * tp)
        d = (-s * cp, sp)
        n = (s * sp, cp)

        def P(u, v):
            return (E[0] + d[0] * u + n[0] * v, E[1] + d[1] * u + n[1] * v)
        # forro (tabuas) por baixo das telhas
        ext(mb, RF, [P(-0.05, -0.26), P(Ls + 0.1, -0.26), P(Ls + 0.1, 0.0), P(-0.05, 0.0)], "x", x0, x1, T)
        # testeira grossa do beiral
        ext(mb, RF, [P(-0.12, -0.72), P(0.34, -0.72), P(0.34, -0.2), P(-0.12, -0.2)], "x", x0 - 0.02, x1 + 0.02, T)
        nC = int(math.ceil(Ls / course))
        seg_k = 1.6 if lod else 1.0
        for k in range(nC):
            a = k * course - (0.12 if k == 0 else 0.0)
            b = min(Ls + 0.22, k * course + course + 0.38)
            # pedacos ao longo da fiada
            xs = [x0]
            while xs[-1] < x1 - 0.5:
                xs.append(min(x1, xs[-1] + r.uniform(2.8, 5.6) * seg_k))
                if x1 - xs[-1] < 1.2:
                    xs[-1] = x1
            for i, (xa, xb) in enumerate(zip(xs, xs[1:])):
                ja = r.uniform(-0.07, 0.07)
                tt = t * r.uniform(0.92, 1.1)
                m = B if r.random() < pB else A
                ext(mb, RF, [P(a + ja, 0.9 * tt), P(b, 0.0), P(b, tt), P(a + ja, 1.9 * tt)], "x", xa, xb, m)
        # cachorros (pontas de caibro) sob o beiral, ao longo da parede
        if rafters and lod == 0:
            for x in even(-length / 2 + 0.3, length / 2 - 0.3, 1.75):
                u1 = eave / cp + 0.25
                ext(mb, RF, [P(0.1, -0.62), P(u1, -0.62), P(u1, -0.25), P(0.1, -0.25)], "x", x - 0.19, x + 0.19, T)
        # tabuas de borda (oitoes com beiral)
        if barge:
            for g, ov in ((-1, og[0]), (1, og[1])):
                if ov <= 0.05:
                    continue
                xe = x0 if g < 0 else x1
                ext(mb, RF, [P(-0.12, -0.62), P(Ls + 0.05, -0.62), P(Ls + 0.05, 2.15 * t), P(-0.12, 2.15 * t)], "x",
                    xe - 0.1 if g > 0 else xe - 0.26, xe + 0.26 if g > 0 else xe + 0.1, T)    # 0,26 alem das telhas
    # capa da cumeeira em telhas (B): meia-volta octogonal em segmentos alternados
    zc = rise + 0.26 / cp
    x = x0 - 0.15
    k = 0
    while x < x1 + 0.1:
        x2 = min(x1 + 0.15, x + 1.45)
        rr = 0.62 if k % 2 == 0 else 0.7
        prof = [(rr * math.cos(math.radians(a)), zc + rr * 0.85 * math.sin(math.radians(a))) for a in
                (-20, 20, 60, 90, 120, 160, 200)]
        ext(mb, RF, prof, "x", x, x2 + 0.03, B)
        x = x2
        k += 1
    return dict(rise=rise, ridge_z=zc + 0.6, half=half, tp=tp)


def roof_z(info, y):
    """altura (local RF) da superficie das telhas na distancia y da cumeeira"""
    return info["rise"] - abs(y) * info["tp"] + 0.55


def gable_wall(mb, Fg, span, rise, pl, party=False, window_=True, dmb=None, seed=0, z0=0.0):
    """OITAO no plano y=0 de Fg (base no topo das paredes): reboco triangular (com vao), linha (tie), pendural,
    colar, maos-francesas e janela pequena; party = so reboco + linha."""
    hw = span / 2
    top = rise - 0.32
    tri = [(-hw * (1 - 0.14 / top), z0 + 0.14), (hw * (1 - 0.14 / top), z0 + 0.14), (0.0, z0 + top)]
    win = None
    if window_ and not party and span >= 7.0:
        ww, wh = 1.5, 1.9
        zs = z0 + max(0.9, top * 0.18)
        if zs + wh < z0 + top * 0.62:
            win = (0.0, zs, ww, wh)
    pieces = poly_minus_rect(tri, (-win[2] / 2, win[2] / 2, win[1], win[1] + win[3])) if win else [tri]
    for pc in pieces:
        ext(mb, Fg, pc, "y", -CORE, 0.0, pl)
    ext(mb, Fg, [(-hw + 0.6, z0 + 0.14), (hw - 0.6, z0 + 0.14), (0.0, z0 + top - 0.5)], "y", -1.2, -CORE + 0.01,
        pl)                                                                                         # miolo
    bb(mb, Fg, -hw, hw, -0.32, 0.24, z0, z0 + 0.5, T)
    if party:
        return
    zc = z0 + top * 0.66
    wc = hw * (1 - (zc - z0) / top)
    bb(mb, Fg, -wc + 0.1, wc - 0.1, -0.32, 0.2, zc - 0.36, zc, T)                         # colar
    zk0 = (win[1] + win[3] + 0.3) if win else z0 + 0.5
    bb(mb, Fg, -0.22, 0.22, -0.32, 0.2, zk0, z0 + top - 0.2, T)                           # pendural
    for s in (-1, 1):
        beam(mb, Fg, (s * (hw - 0.9), -0.06, z0 + 0.5), (s * 1.3, -0.06, zc - 0.36), 0.42, 0.36)
        if win:
            bb(mb, Fg, s * (win[2] / 2 + 0.22) - 0.21, s * (win[2] / 2 + 0.22) + 0.21, -0.32, 0.2, z0 + 0.5,
               min(zc - 0.36, win[1] + win[3] + 0.3), T)
    if win:
        bb(mb, Fg, -win[2] / 2 - 0.2, win[2] / 2 + 0.2, -0.32, 0.18, win[1] + win[3] + 0.02, win[1] + win[3] + 0.34, T)
        window(mb, Fg, 0.0, win[1], win[2], win[3], dmb=dmb, shutters=False, box=False, seed=seed)


def chimney(mb, F, x, y, z0, z1, stone, seed=0, w=2.2, crown=MOR):
    """chamine de pedra: miolo de junta + fiadas de blocos levemente deslocados/girados (juntas recuadas), capa de
    pedra larga e coroa escura"""
    r = rng("chim", seed)
    bb(mb, F, x - w / 2 + 0.26, x + w / 2 - 0.26, y - w / 2 + 0.26, y + w / 2 - 0.26, z0, z1 - 0.2, MOR)
    z = z0
    while z < z1 - 0.9:
        h = r.uniform(0.75, 1.05)
        z2 = min(z1 - 0.6, z + h)
        a = r.uniform(-0.03, 0.03)
        bx(mb, F, x + r.uniform(-0.05, 0.05), y + r.uniform(-0.05, 0.05), (z + z2) / 2 + 0.03, w, w, z2 - z - 0.1,
           stone, rz=a)
        z = z2
    bb(mb, F, x - w / 2 - 0.3, x + w / 2 + 0.3, y - w / 2 - 0.3, y + w / 2 + 0.3, z1 - 0.62, z1 - 0.22, stone)
    if crown:
        bb(mb, F, x - w / 2 + 0.25, x + w / 2 - 0.25, y - w / 2 + 0.25, y + w / 2 - 0.25, z1 - 0.24, z1 + 0.3, crown)


def dormer(mb, RF, info, xd, pl, A, B, dmb=None, seed=0, dw=3.6, flowers="red"):
    """AGUA-FURTADA na agua +y do telhado RF (cumeeira em x): frente de reboco com caixilho e janela, laterais,
    telhadinho proprio em fiadas (cumeeira perpendicular) e oitao com pendural"""
    half, tp = info["half"], info["tp"]
    yd = half - 1.0
    zr = (half - yd) * tp + 0.35
    zde = zr + 2.9
    yback = half - (zde + 0.6) / tp
    bb(mb, RF, xd - dw / 2 + 0.05, xd + dw / 2 - 0.05, yback, yd - 0.6, zr - 1.0, zde, pl)  # corpo (entra no telhado)
    Ff = sub(RF, xd, yd, 0.0, 0.0)
    ww, wh = 1.5, 1.95
    zs = zr + 0.45
    panel(mb, Ff, -dw / 2, dw / 2, zr - 0.36, zde - 0.14, -0.14, 0.0, [(-ww / 2, ww / 2, zs, zs + wh)], pl)
    bb(mb, Ff, -dw / 2 + 0.2, dw / 2 - 0.2, -0.62, -0.5, zr - 0.5, zde, pl)                  # fundo atras do vidro
    for s in (-1, 1):
        bb(mb, Ff, s * dw / 2 - 0.25, s * dw / 2 + 0.25, -0.64, 0.32, zr - 0.5, zde, T)      # montantes de canto
    bb(mb, Ff, -dw / 2 - 0.1, dw / 2 + 0.1, -0.3, 0.32, zde - 0.4, zde, T)
    window(mb, Ff, 0.0, zs, ww, wh, dmb=dmb, shutters=False, box=dmb is not None, flowers=flowers, seed=seed)
    RFd = sub(RF, xd, (yd + yback) / 2 + 0.3, zde, math.pi / 2)        # +x do RFd = frente (+y do RF)
    Ld = yd - yback + 0.6
    di = roof(mb, RFd, Ld, dw, 50.0, 0.45, (0.0, 0.55), A, B, seed=(seed, "dormer"), course=0.95, t=0.28,
              rafters=False)
    Fg = sub(RFd, Ld / 2, 0.0, 0.0, -math.pi / 2)
    gable_wall(mb, Fg, dw, di["rise"], pl, window_=False)
    return zde


def balcony(mb, Ff, x0, x1, z, depth=1.7, rail_h=2.6, flowers=None, dmb=None, seed=0):
    """SACADA de madeira na face Ff (assoalho no piso do andar z): maos-francesas, balaustres recortados,
    corrimao e floreiras no corrimao (dmb)"""
    bb(mb, Ff, x0, x1, 0.0, depth, z - 0.05, z + 0.26, T)
    for x in even(x0 + 0.4, x1 - 0.4, 2.2) + [x0 + 0.25, x1 - 0.25]:
        beam(mb, Ff, (x, -0.3, z - 2.1), (x, depth - 0.25, z - 0.08), 0.32, 0.36)
    for x in [x0 + 0.15] + even(x0 + 0.5, x1 - 0.5, 1.7) + [x1 - 0.15]:
        bb(mb, Ff, x - 0.16, x + 0.16, depth - 0.34, depth - 0.02, z + 0.25, z + rail_h, T)
    bb(mb, Ff, x0, x1, depth - 0.42, depth + 0.06, z + rail_h - 0.05, z + rail_h + 0.24, T)   # corrimao
    bb(mb, Ff, x0, x1, depth - 0.3, depth - 0.06, z + 0.32, z + 0.6, T)
    xb = x0 + 0.45
    while xb < x1 - 0.4:
        bb(mb, Ff, xb, xb + 0.3, depth - 0.24, depth - 0.12, z + 0.6, z + rail_h - 0.05, T)
        xb += 0.5
    for s, xe in ((-1, x0), (1, x1)):
        bb(mb, Ff, xe - 0.12 if s > 0 else xe, xe if s > 0 else xe + 0.12, 0.0, depth, z + rail_h - 0.05,
           z + rail_h + 0.2, T)
        for yy in even(0.35, depth - 0.4, 0.5):
            bb(mb, Ff, xe - 0.12 if s > 0 else xe, xe if s > 0 else xe + 0.12, yy - 0.15, yy + 0.15, z + 0.3,
               z + rail_h - 0.05, T)
    if dmb is not None and flowers:
        for xc in (x0 + (x1 - x0) * 0.25, x0 + (x1 - x0) * 0.75):
            bb(mb, Ff, xc - 0.9, xc + 0.9, depth - 0.45, depth + 0.25, z + rail_h + 0.2, z + rail_h + 0.75, T)
            flower_box_plants(dmb, Ff, xc, depth - 0.1, z + rail_h + 0.75, 1.8, flowers, (seed, xc))


# ------------------------------------------------------------------ enfeites (dmb)
def flower_box_plants(dmb, Ff, c, y, z, L, color="red", seed=0):
    """folhas + flores sobre a floreira (dmb): icosaedros baixos, cores do SPEC (vermelho/amarelo/rosa)"""
    if dmb is None or not color:
        return
    r = rng("flowers", seed)
    fm = FLOWERS.get(color, FLOWERS["red"])
    n = max(2, int(L / 0.75))
    for i in range(n):
        x = c - L / 2 + L * (i + 0.5) / n + r.uniform(-0.1, 0.1)
        dmb.ico(0.32, Ff.p(x, y + r.uniform(-0.08, 0.08), z + 0.14), TUFT, 1, (1.0, 0.85, 0.7),
                rot=(0, 0, r.uniform(0, 3)), jitter=0.15)
    for i in range(n + 2):
        x = c - L / 2 + L * (i + 0.3) / (n + 1.6) + r.uniform(-0.12, 0.12)
        mm = fm if r.random() < 0.75 else FLOWERS["yellow" if color != "yellow" else "pink"]
        dmb.ico(0.15, Ff.p(x, y + r.uniform(-0.05, 0.3), z + 0.36 + r.uniform(0.0, 0.18)), mm, 1, (1.0, 1.0, 0.8),
                jitter=0.1)


def awning(dmb, Ff, x0, x1, z_top, depth=2.3, drop=1.0, stripe=0.9):
    """TOLDO listrado (vermelho/creme) com sanefa recortada e 2 tirantes de ferro"""
    n = max(2, int(round((x1 - x0) / stripe)))
    p = math.atan2(drop, depth)
    ln = math.hypot(depth, drop)
    for i in range(n):
        a = x0 + (x1 - x0) * i / n
        b = x0 + (x1 - x0) * (i + 1) / n
        m = "Cloth_VM_Red" if i % 2 == 0 else "Cloth_VM_Cream"
        bx(dmb, Ff, (a + b) / 2, depth / 2, z_top - drop / 2, b - a + 0.01, ln, 0.12, m, rx=-p)
        # sanefa recortada (aba vertical com ponta)
        ext(dmb, Ff, [(a, z_top - drop), (b, z_top - drop), (b, z_top - drop - 0.45), ((a + b) / 2, z_top - drop - 0.8),
                      (a, z_top - drop - 0.45)], "y", depth - 0.05, depth + 0.07, m)
    for xe in (x0 + 0.15, x1 - 0.15):
        dmb.rod(Ff.p(xe, 0.05, z_top - drop - 1.4), Ff.p(xe, depth - 0.1, z_top - drop + 0.05), 0.07, IRON, 6)


def hanging_sign(dmb, Ff, x, z, out=2.4, emblem="pick"):
    """PLACA pendurada num braco de ferro (com voluta) saindo da parede"""
    dmb.rod(Ff.p(x, 0.0, z), Ff.p(x, out, z), 0.09, IRON, 6)
    dmb.rod(Ff.p(x, 0.0, z - 1.2), Ff.p(x, out * 0.7, z - 0.03), 0.07, IRON, 6)
    # voluta (anel de 8 gomos)
    for i in range(8):
        a0, a1 = 2 * math.pi * i / 8, 2 * math.pi * (i + 1) / 8
        cy, cz, rr = out * 0.42, z - 0.42, 0.3
        dmb.rod(Ff.p(x, cy + rr * math.cos(a0), cz + rr * math.sin(a0)), Ff.p(x, cy + rr * math.cos(a1),
                                                                                cz + rr * math.sin(a1)), 0.05, IRON, 4)
    for yy in (out * 0.45, out - 0.25):
        dmb.rod(Ff.p(x, yy, z - 0.05), Ff.p(x, yy, z - 0.55), 0.04, IRON, 4)
    Fs = sub(Ff, x, (out * 0.45 + out - 0.25) / 2, z - 0.55, -math.pi / 2)
    w = out - 0.25 - out * 0.45 + 0.7
    bb(dmb, Fs, -w / 2, w / 2, -0.09, 0.09, -1.5, 0.0, PLK)
    bb(dmb, Fs, -w / 2 - 0.06, w / 2 + 0.06, -0.24, 0.24, -1.62, -1.42, T)
    bb(dmb, Fs, -w / 2 - 0.06, w / 2 + 0.06, -0.24, 0.24, -0.08, 0.1, T)
    for sgn in (-1, 1):                                      # emblema em relevo nas 2 faces (bronze)
        if emblem == "pick":
            beam(dmb, Fs, (-0.45, sgn * 0.12, -1.2), (0.45, sgn * 0.12, -0.3), 0.08, 0.14, BRONZE)
            ext(dmb, Fs, [(-0.05, -0.55), (0.45, -0.85), (0.62, -0.6), (0.4, -0.5), (0.1, -0.35)], "y",
                min(sgn * 0.08, sgn * 0.17), max(sgn * 0.08, sgn * 0.17), BRONZE)
        else:
            ext(dmb, Fs, [(-0.35, -1.1), (0.35, -1.1), (0.35, -0.5), (0.0, -0.3), (-0.35, -0.5)], "y",
                min(sgn * 0.08, sgn * 0.17), max(sgn * 0.08, sgn * 0.17), BRONZE)


# ------------------------------------------------------------------ casa inteira
DEFAULT = dict(W=12.0, D=10.0, floors=2, gh=8.0, fh=6.0, jetty=(0.8, 0.6), ridge="x", pitch=54.0, eave=1.3,
               gable=1.0, plaster="Plaster_VM_Cream", stone="Stone_VM_Base", stone2=None,
               roof=("Roof_VM_Terracotta", "Roof_VM_Terracotta_B"), chimney="auto", dormers=0, balcony=None,
               shop=False, party=(), door=dict(side="F", x=0.0), flowers="red", seed="casa", lod=0, sign=None)
PRESETS = {
    "A3": dict(W=13.0, D=11.0, floors=3, ridge="x", pitch=55.0, dormers=2, plaster="Plaster_VM_Cream",
               stone="Stone_VM_Grey", roof=("Roof_VM_Terracotta", "Roof_VM_Terracotta_B"), flowers="red"),
    "B2": dict(W=12.0, D=11.0, floors=2, ridge="y", pitch=56.0, balcony=1, jetty=(0.9, 0.0),
               plaster="Plaster_VM_Ochre", stone="Stone_VM_Warm", roof=("Roof_VM_Terracotta_B", "Roof_VM_Terracotta"),
               flowers="pink"),
    "C2": dict(W=8.6, D=10.0, floors=2, ridge="y", pitch=58.0, plaster="Plaster_VM_Peach", stone="Stone_VM_Base",
               roof=("Roof_VM_Terracotta_C", "Roof_VM_Terracotta"), flowers="yellow", chimney=None),
    "D3": dict(W=9.6, D=10.0, floors=3, ridge="x", pitch=56.0, shop=True, dormers=1, plaster="Plaster_VM_Cream",
               stone="Stone_VM_Warm", roof=("Roof_VM_Terracotta", "Roof_VM_Terracotta_C"), flowers="red",
               sign="pick"),
    "E2": dict(W=13.5, D=11.0, floors=2, ridge="x", pitch=52.0, dormers=1, plaster="Plaster_VM_Peach",
               stone="Stone_VM_Grey", roof=("Roof_VM_Terracotta_C", "Roof_VM_Terracotta_B"), flowers="yellow"),
    "F2": dict(W=12.0, D=11.0, floors=2, ridge="y", pitch=55.0, jetty=(0.8, 0.0), plaster="Plaster_VM_Cream",
               stone="Stone_VM_Warm", roof=("Roof_VM_Terracotta", "Roof_VM_Terracotta_B"), flowers="red"),
}


def spec_of(preset=None, **kw):
    s = dict(DEFAULT)
    if preset:
        s.update(PRESETS[preset])
    s.update(kw)
    return s


def _ground_openings(side, L, sp, rr):
    """vaos do terreo (porta e janelas) de um lado: [('door', c) | ('win', c, ww, wh, zs) | ('shop', ...)]"""
    out = []
    dside = sp["door"].get("side", "F")
    dx = sp["door"].get("x", 0.0)
    if side == dside:
        out.append(("door", dx))
        if sp.get("shop") and side == "F":
            sg = 1.0 if dx <= 0 else -1.0             # vitrine do lado oposto ao da porta
            a = dx + sg * (DOOR_W / 2 + 1.25)
            b = sg * (L / 2 - 0.9)
            avail = abs(b - a) - 0.7
            if avail >= 2.4:
                ww = min(4.4, avail)
                out.append(("win", (a + b) / 2, ww, 3.0, 2.2, 3))
        else:
            for s in (-1, 1):
                c = dx + s * (DOOR_W / 2 + 1.0 + 1.0 + 0.85)
                if abs(c) + 0.85 + 1.0 <= L / 2:
                    out.append(("win", c, 1.7, 2.3, 2.9, 1))
    else:
        if L >= 7.5:
            out.append(("win", rr.uniform(-0.6, 0.6) if L > 9 else 0.0, 1.7, 2.3, 2.9, 1))
    return out


def house(mb, F, spec, dmb=None):
    """CASA ENXAIMEL do kit (ver cabecalho). Desenha no mb (<= 6 materiais) + enfeites no dmb."""
    sp = dict(DEFAULT)
    sp.update(spec)
    seed = sp["seed"]
    rr = rng("house", seed)
    W, D, nf = sp["W"], sp["D"], sp["floors"]
    gh, fh = sp["gh"], sp["fh"]
    jet = list(sp["jetty"]) + [0.0, 0.0]
    PL, ST = sp["plaster"], sp["stone"]
    RA, RB = sp["roof"]
    party = set(sp["party"])
    lod = sp["lod"]
    fl = sp["flowers"]
    info = {"lamp": []}

    def wall_frame(side, yF, z0, d0=-D / 2):
        """Ff de um lado (plano da face) para um andar cuja frente esta em yF e fundos em d0"""
        if side == "F":
            return sub(F, 0.0, yF, z0, 0.0), W
        if side == "B":
            return sub(F, 0.0, d0, z0, math.pi), W
        yc = (yF + d0) / 2
        if side == "R":
            return sub(F, W / 2, yc, z0, -math.pi / 2), yF - d0
        return sub(F, -W / 2, yc, z0, math.pi / 2), yF - d0

    # ---------------- terreo de pedra
    bb(mb, F, -W / 2 + CORE, W / 2 - CORE, -D / 2 + CORE, D / 2 - CORE, -0.3, gh, MOR)
    for side in "FBRL":
        Ff, L = wall_frame(side, D / 2, 0.0)
        if side in party:
            stone_face(mb, Ff, -L / 2, L / 2, -0.3, gh - 0.02, ST, (), seed=(seed, side, "meia"), lod=2)
            continue
        holes = []
        for o in _ground_openings(side, L, sp, rr):
            if o[0] == "door":
                holes.append(door_hole(o[1]))
                door(mb, Ff, o[1], ST, dmb=dmb, seed=(seed, side))
                info["door"] = tuple(Ff.p(o[1], 1.0, 0.0))
            else:
                _, c, ww, wh, zs, mull = o
                holes.append(ground_window_hole(c, zs, ww, wh))
                window_ground(mb, Ff, c, zs, ww, wh, ST, dmb=dmb if lod == 0 else None,
                              flowers=(fl if side == "F" else None), seed=(seed, side, round(c, 2)), mull=mull,
                              shutters=mull == 1 and lod == 0 and side != "B")
        stone_face(mb, Ff, -L / 2 - (0.12 if side in "FB" else 0.0), L / 2 + (0.12 if side in "FB" else 0.0), -0.3,
                   gh - 0.02, ST, holes, seed=(seed, side), lod=(lod + 1) if side == "B" else lod,
                   m2=sp.get("stone2"), p2=0.3)
    # ---------------- andares enxaimel em balanco (frente)
    yF = D / 2
    z0 = gh
    for k in range(1, nf):
        yP = yF
        yF = yF + jet[k - 1]
        z1 = z0 + fh
        bb(mb, F, -W / 2 + CORE, W / 2 - CORE, -D / 2 + CORE, yF - CORE, z0, z1, PL)
        if yF - yP > 0.05:
            bb(mb, F, -W / 2, W / 2, yP - 0.3, yF, z0 - 0.26, z0 + 0.02, T)                    # forro do balanco
            for x in even(-W / 2 + 0.5, W / 2 - 0.5, 1.55 if lod == 0 else 2.6):               # cabecas de barrote
                bb(mb, F, x - 0.21, x + 0.21, yP - 0.3, yF + 0.16, z0 - 0.66, z0 - 0.2, T)
            for x in [-W / 2 + 0.35] + ([0.0] if W > 11.5 else []) + [W / 2 - 0.35]:           # maos-francesas
                beam(mb, F, (x, yP - 0.25, z0 - 2.3), (x, yF - 0.2, z0 - 0.5), 0.38, 0.4)
        tall = sp.get("balcony") == k
        for side in "FBRL":
            Ff, L = wall_frame(side, yF, z0)
            xs, ks = bays_for(L, "F" if side == "F" else ("B" if side == "B" else "S"), rng("bays", seed, side, k),
                              party=side in party)
            upper_wall(mb, Ff, L, fh, PL, xs, ks, dmb=dmb if side != "B" else None, flowers=fl,
                       seed=(seed, side, k), tall=tall and side == "F", lod=max(lod, 1) if side == "B" else lod)
            if tall and side == "F":
                balcony(mb, Ff, -L / 2 + 0.6, L / 2 - 0.6, 0.0, flowers=fl, dmb=dmb, seed=(seed, k))
        z0 = z1
    eave_z = z0
    info["eave_z"] = eave_z
    info["top_y"] = yF
    # ---------------- telhado
    yc = (yF + -D / 2) / 2
    Dt = yF + D / 2
    og = sp["gable"]
    if sp["ridge"] == "x":
        RF = sub(F, 0.0, yc, eave_z, 0.0)
        length, span = W, Dt
        ogs = (0.15 if "L" in party else og, 0.15 if "R" in party else og)
        gab = (("L", -1), ("R", 1))
    else:
        RF = sub(F, 0.0, yc, eave_z, math.pi / 2)
        length, span = Dt, W
        ogs = (0.15 if "B" in party else og, 0.15 if "F" in party else og)
        gab = (("B", -1), ("F", 1))
    ri = roof(mb, RF, length, span, sp["pitch"], sp["eave"], ogs, RA, RB, seed=seed, lod=lod, rafters=lod == 0)
    info["ridge_z"] = eave_z + ri["ridge_z"]
    for side, g in gab:
        Fg = sub(RF, g * length / 2, 0.0, 0.0, -g * math.pi / 2)
        gable_wall(mb, Fg, span, ri["rise"], PL, party=side in party, dmb=dmb if side == "F" else None,
                   seed=(seed, "gable", side))
    # ---------------- aguas-furtadas
    nd = sp.get("dormers", 0) if sp["ridge"] == "x" else 0
    if nd:
        pos = [0.0] if nd == 1 else [-length / 4 - 0.3, length / 4 + 0.3]
        for i, xd in enumerate(pos):
            dormer(mb, RF, ri, xd, PL, RA, RB, dmb=dmb, seed=(seed, "d", i), flowers=fl)
    # ---------------- chamine
    ch = sp.get("chimney")
    if ch:
        if ch == "auto":
            side = -1 if rr.random() < 0.5 else 1
            if sp["ridge"] == "x":
                cx, cy = side * (W / 2 - 2.0), yc - 1.4
                ytop = abs(cy - yc)
            else:
                cx, cy = side * (W / 4 + 0.2), -D / 2 + 2.6
                ytop = abs(cx)
        else:
            cx, cy = ch["x"], ch["y"]
            ytop = abs(cy - yc) if sp["ridge"] == "x" else abs(cx)
        zt = eave_z + ri["rise"] - ytop * ri["tp"] + 2.6
        zt = max(zt, info["ridge_z"] + 0.9)
        chimney(mb, F, cx, cy, eave_z - 1.0, zt, ST, seed=(seed, "ch"))
        info["chimney"] = (cx, cy, zt)
    # ---------------- loja: toldo + placa
    if sp.get("shop") and dmb is not None:
        Ff, L = wall_frame("F", D / 2, 0.0)
        dx = sp["door"].get("x", 0.0)
        awning(dmb, Ff, -L / 2 + 0.7, L / 2 - 0.7, DOOR_H + 2.55, depth=2.2, drop=0.95)
    if sp.get("sign") and dmb is not None:
        Ff, L = wall_frame("F", D / 2 + (jet[0] if nf > 1 else 0.0), 0.0)        # na parede do 1o andar
        hanging_sign(dmb, Ff, L / 2 - 0.9, gh + 1.7, out=2.4, emblem=sp["sign"])
    info["footprint"] = (W, D, yF)
    return info


def house_col(area, F, spec, info):
    """colisao simplificada: corpo inteiro (terreo + balancos ate o beiral) - fachada fechada"""
    sp = dict(DEFAULT)
    sp.update(spec)
    W, D = sp["W"], sp["D"]
    yF = info["top_y"]
    z1 = info["eave_z"] + 1.5
    c = F.p(0.0, (yF - D / 2) / 2, 0.0)
    col_box(area, (W + 0.2, yF + D / 2 + 0.2, z1 + 0.3), (c.x, c.y, F.o.z + z1 / 2 - 0.15), F.r())


# ------------------------------------------------------------------ RUA
def cobbles(mb, F, x0, x1, prof, seed=0, row=(1.15, 1.5), sw=(1.25, 1.95), gap=0.12, lod=0, keep=None, mats=None,
            bed_m=PAVE_J, pB=0.35, edge_skip=0.0):
    """PARALELEPIPEDO ARREDONDADO em geometria na faixa x0..x1 (local), ao longo de y pelos pontos de prof =
    [(y, z_topo), ...] (linear por trechos: rampa da ponte). Fiadas transversais (rows), pedras com contorno
    irregular e topo em domo chanfrado, juntas = leito escuro (bed_m) 0,14 abaixo do topo. keep(x, y) -> bool
    (coordenadas LOCAIS) recorta (ex.: borda da praca). lod=1: pedras longas (padrao simples de longe)."""
    r = rng("cobbles", seed)
    A, B_ = mats or (PAVE_A, PAVE_B)
    prof = sorted(prof)
    if lod:
        sw = (sw[0] * 2.6, sw[1] * 3.0)

    def ztop(x, y):
        if y <= prof[0][0]:
            return prof[0][1]
        for (ya, za), (yb, zb) in zip(prof, prof[1:]):
            if ya <= y <= yb:
                return za + (zb - za) * (y - ya) / max(1e-6, yb - ya)
        return prof[-1][1]
    # leito (junta) em pedacos lineares
    for (ya, za), (yb, zb) in zip(prof, prof[1:]):
        ext(mb, F, [(ya, za - 0.45), (yb, zb - 0.45), (yb, zb - 0.17), (ya, za - 0.17)], "x", x0, x1, bed_m)
    y = prof[0][0]
    y_end = prof[-1][0]
    k = 0
    while y < y_end - 0.3:
        h = r.uniform(*row)
        y2 = min(y_end, y + h)
        if y_end - y2 < 0.7:
            y2 = y_end
        x = x0 + (r.uniform(0.2, 0.9) if k % 2 else 0.0)
        xs = [x0]
        if x > x0 + 0.3:
            xs.append(x)
        while xs[-1] < x1 - 0.3:
            nx = xs[-1] + r.uniform(*sw)
            if x1 - nx < 0.8:
                nx = x1
            xs.append(min(nx, x1))
        for xa, xb in zip(xs, xs[1:]):
            if keep is not None and not keep((xa + xb) / 2, (y + y2) / 2):
                continue
            g = gap / 2
            pts = [(xa + g + r.uniform(-0.06, 0.06), y + g + r.uniform(-0.05, 0.05)),
                   (xb - g + r.uniform(-0.06, 0.06), y + g + r.uniform(-0.05, 0.05)),
                   (xb - g + r.uniform(-0.06, 0.06), y2 - g + r.uniform(-0.05, 0.05)),
                   (xa + g + r.uniform(-0.06, 0.06), y2 - g + r.uniform(-0.05, 0.05))]
            dz = r.uniform(-0.03, 0.04)
            m = B_ if r.random() < pB else A
            cobble(mb, F, pts, lambda qx, qy, dz=dz: ztop(qx, qy) + dz, m)
        y = y2
        k += 1
    return ztop


def curb(mb, F, x, y0, y1, ztop_fn, w=0.72, m=PAVE_E, seed=0, up=0.12):
    """MEIO-FIO: pedras longas aparelhadas (topo chanfrado) ao longo de y na posicao x (local)"""
    r = rng("curb", seed)
    y = y0
    while y < y1 - 0.2:
        y2 = min(y1, y + r.uniform(1.7, 2.6))
        if y1 - y2 < 0.9:
            y2 = y1
        pts = [(x - w / 2, y + 0.05), (x + w / 2, y + 0.05), (x + w / 2, y2 - 0.05), (x - w / 2, y2 - 0.05)]
        cobble(mb, F, pts, lambda qx, qy: ztop_fn(qx, qy) + up, m, bed=0.55, c1=0.07, c2=0.17)
        y = y2


def mureta(mb, F, L, h=1.25, w=1.1, m="Stone_VM_Base", m2="Stone_VM_Trim", seed=0, lod=0, cap=True, zfn=None,
           core=True):
    """MURETA DE PEDRA SECA ao longo de x local (-L/2..L/2), centrada em y=0, base em z=0 (enterrada 0,2):
    fiadas de pedras atravessadas (as 2 faces arredondadas) + capa de pedras chatas maiores (m2)"""
    r = rng("mureta", seed)
    hc = 0.34 if cap else 0.0
    nco = 2 if h - hc > 0.75 else 1
    z = -0.2
    for ci in range(nco):
        ch = (h - hc + 0.2) / nco
        x = -L / 2 + (r.uniform(0.3, 0.8) if ci % 2 else 0.0)
        xs = [-L / 2] + ([x] if x > -L / 2 + 0.2 else [])
        while xs[-1] < L / 2 - 0.2:
            nx = xs[-1] + r.uniform(0.95, 1.7) * (1.5 if lod else 1.0)
            if L / 2 - nx < 0.6:
                nx = L / 2
            xs.append(min(L / 2, nx))
        for xa, xb in zip(xs, xs[1:]):
            jit = [(r.uniform(-0.07, 0.07), r.uniform(-0.06, 0.06)) for _ in range(4)]
            dy = r.uniform(-0.06, 0.06)
            through_stone(mb, F, xa + 0.05, xb - 0.05, -w / 2 + dy, w / 2 + dy, z + 0.04, z + ch - 0.04, m, c=0.2,
                          jit=jit, zfn=zfn)
        z += ch
    if cap:
        x = -L / 2 - 0.1
        while x < L / 2 + 0.1 - 0.2:
            x2 = min(L / 2 + 0.1, x + r.uniform(1.2, 2.1))
            if L / 2 + 0.1 - x2 < 0.7:
                x2 = L / 2 + 0.1
            through_stone(mb, F, x + 0.04, x2 - 0.04, -w / 2 - 0.14, w / 2 + 0.14, z - 0.02,
                          z + hc + r.uniform(-0.03, 0.04), m2, c=0.14, zfn=zfn)
            x = x2
    if core:                                                                    # miolo escuro (frestas)
        if zfn is None:
            bb(mb, F, -L / 2 + 0.3, L / 2 - 0.3, -w / 2 + 0.3, w / 2 - 0.3, -0.2, h - 0.25, MOR)
        else:
            xa, xb = -L / 2 + 0.3, L / 2 - 0.3
            ext(mb, F, [(xa, -0.2 + zfn(xa)), (xb, -0.2 + zfn(xb)), (xb, h - 0.25 + zfn(xb)), (xa, h - 0.25 + zfn(xa))],
                "y", -w / 2 + 0.3, w / 2 - 0.3, MOR)


def tuft(mb, F, x, y, z, h=1.1, k=0, m=TUFT):
    """touceira de GRAMA ALTA: 5-7 laminas (cones de 3 lados) inclinadas para fora"""
    r = rng("tuft", round(x, 2), round(y, 2), k)
    n = r.randint(6, 9)
    for i in range(n):
        a = 2 * math.pi * i / n + r.uniform(-0.3, 0.3)
        tilt = r.uniform(0.15, 0.45)
        hh = h * r.uniform(0.6, 1.15)
        rot = (math.cos(a + math.pi / 2) * tilt, math.sin(a + math.pi / 2) * tilt * -1.0, 0.0)
        p = F.p(x + math.cos(a) * 0.12, y + math.sin(a) * 0.12, z + hh / 2 - 0.05)
        mb.cyl(0.17, hh, p, (rot[0], rot[1], F.a + a), m, 3, r2=0.0, bevel=0.0)


def lantern(mb, F, zb, hh=1.7, w=0.5):
    """LANTERNA de ferro: bandeja, vidro recuado (Window_VM_Lamp), 4 colunas e GRADE 0,12 a frente do vidro, chapeu
    piramidal e pinaculo. Retorna o ponto (mundo) da luz NightOnly."""
    o = w + 0.12
    mb.cyl(o + 0.33, 0.22, F.p(0, 0, zb), F.r(0, 0, math.pi / 4), IRON, 4, bevel=0.0)                  # bandeja
    bb(mb, F, -w, w, -w, w, zb + 0.1, zb + hh, GLASS_LAMP)
    for sx in (-1, 1):
        for sy in (-1, 1):
            bb(mb, F, sx * o - 0.08, sx * o + 0.08, sy * o - 0.08, sy * o + 0.08, zb + 0.1, zb + hh, IRON)
    for ang in range(4):
        Fa = sub(F, 0, 0, 0, ang * math.pi / 2)
        bb(mb, Fa, -0.05, 0.05, w, w + 0.14, zb + 0.1, zb + hh, IRON)
        bb(mb, Fa, -o, o, w, w + 0.14, zb + hh * 0.55 - 0.05, zb + hh * 0.55 + 0.05, IRON)
        bb(mb, Fa, -o - 0.04, o + 0.04, w, w + 0.2, zb + hh - 0.06, zb + hh + 0.1, IRON)
    mb.cyl(o + 0.43, 0.95, F.p(0, 0, zb + hh + 0.55), F.r(0, 0, math.pi / 4), IRON, 4, r2=0.14, bevel=0.0)
    mb.ico(0.2, F.p(0, 0, zb + hh + 1.15), IRON, 1)
    return F.p(0, 0, zb + 0.1 + hh / 2)


def lamp_post(mb, F, h=9.6, stone="Stone_VM_Base"):
    """POSTE DE FERRO com lanterna no topo: base de pedra, pe de ferro, fuste octogonal com aneis e a lantern().
    Retorna o ponto (mundo) da luz NightOnly."""
    through_stone(mb, F, -0.75, 0.75, -0.75, 0.75, -0.25, 0.55, stone, c=0.16)
    mb.cyl(0.46, 1.1, F.p(0, 0, 1.05), F.r(), IRON, 8, r2=0.3, bevel=0.0)
    mb.cyl(0.2, h - 2.6, F.p(0, 0, 1.6 + (h - 2.6) / 2), F.r(), IRON, 8, bevel=0.0)
    for z in (1.75, h - 1.25):
        mb.cyl(0.34, 0.22, F.p(0, 0, z), F.r(), IRON, 8, bevel=0.0)
    return lantern(mb, F, h - 1.0)


def barrel(mb, F, x, y, z=0.0, h=2.3, r=0.95, lying=False):
    """BARRIL: aduelas (lathe 10 lados com bojo), 3 aros de ferro salientes, tampo recuado"""
    Fb = sub(F, x, y, z)
    prof = [(r * 0.84, 0.0), (r * 0.96, h * 0.25), (r, h * 0.5), (r * 0.96, h * 0.75), (r * 0.84, h)]
    lathe(mb, Fb, (0, 0, 0), prof, 10, PLK)
    for f in (0.1, 0.5, 0.9):
        rr = r * (0.84 + 0.16 * math.sin(math.pi * f) ** 0.6) + 0.13
        lathe(mb, Fb, (0, 0, 0), [(rr, h * f - 0.09), (rr, h * f + 0.09)], 10, IRON)
    lathe(mb, Fb, (0, 0, 0), [(r * 0.72, h - 0.05), (r * 0.72, h + 0.12)], 10, T)


def crate(mb, F, x, y, z=0.0, s=2.0, a=0.0):
    """CAIXOTE: miolo de tabuas + moldura de ripas escuras nas arestas + travessa diagonal"""
    Fc = sub(F, x, y, z, a)
    bb(mb, Fc, -s / 2 + 0.14, s / 2 - 0.14, -s / 2 + 0.14, s / 2 - 0.14, 0.0, s - 0.14, PLK)
    e = 0.2
    for sx in (-1, 1):
        for sy in (-1, 1):
            bb(mb, Fc, sx * s / 2 - e if sx > 0 else -s / 2, sx * s / 2 if sx > 0 else -s / 2 + e,
               sy * s / 2 - e if sy > 0 else -s / 2, sy * s / 2 if sy > 0 else -s / 2 + e, 0.0, s, T)
    for zz in (0.0, s - e):
        for ang in (0, math.pi / 2):
            Fa = sub(Fc, 0, 0, 0, ang)
            bb(mb, Fa, -s / 2, s / 2, -s / 2, -s / 2 + e, zz, zz + e, T)
            bb(mb, Fa, -s / 2, s / 2, s / 2 - e, s / 2, zz, zz + e, T)
    for ang in (0, math.pi):
        Fa = sub(Fc, 0, 0, 0, ang)
        beam(mb, Fa, (-s / 2 + 0.2, s / 2 + 0.02, 0.2), (s / 2 - 0.2, s / 2 + 0.02, s - 0.2), 0.16, 0.22)


def wheel(mb, F, r=1.9, n=10, w=0.34):
    """RODA RAIADA no plano local x-z (eixo = y): aro em gomos, cubo e raios"""
    seg = 16
    for i in range(seg):
        a0, a1 = 2 * math.pi * i / seg, 2 * math.pi * (i + 1) / seg
        pts = []
        for a in (a0, a1):
            pts.append((r * math.cos(a), r * math.sin(a)))
        ri = r - 0.32
        poly = [(r * math.cos(a0), r * math.sin(a0)), (r * math.cos(a1), r * math.sin(a1)),
                (ri * math.cos(a1), ri * math.sin(a1)), (ri * math.cos(a0), ri * math.sin(a0))]
        ext(mb, F, poly, "y", -w / 2, w / 2, T)
    mb.cyl(0.38, w + 0.5, F.p(0, 0, 0), F.r(math.pi / 2, 0, 0), T, 8, bevel=0.0)
    mb.cyl(0.42, 0.12, F.p(0, w / 2 + 0.2, 0), F.r(math.pi / 2, 0, 0), IRON, 8, bevel=0.0)
    for i in range(n):
        a = 2 * math.pi * (i + 0.5) / n
        beam(mb, F, (0.3 * math.cos(a), 0.0, 0.3 * math.sin(a)), ((r - 0.25) * math.cos(a), 0.0,
                                                                    (r - 0.25) * math.sin(a)), 0.18, 0.2)


def cart(mb, F, load=True):
    """CARROCA de 2 rodas raiadas (ref_01): caixa de tabuas com fueiros, eixo, varais apoiados no chao, barril"""
    zb = 2.0
    bb(mb, F, -2.9, 2.9, -1.55, 1.55, zb, zb + 0.32, PLK)
    for s in (-1, 1):
        bb(mb, F, -2.9, 2.9, s * 1.55 - 0.12, s * 1.55 + 0.12, zb + 0.32, zb + 1.35, PLK)
        for x in (-2.6, -0.9, 0.9, 2.6):
            bb(mb, F, x - 0.13, x + 0.13, s * 1.55 - 0.2, s * 1.55 + 0.2, zb - 0.2, zb + 1.55, T)
        bb(mb, F, -2.9, 2.9, s * 1.55 - 0.18, s * 1.55 + 0.18, zb + 1.3, zb + 1.5, T)
        Fw = sub(F, -0.4, s * 2.05, 1.9)
        wheel(mb, Fw, 1.9)
        beam(mb, F, (2.6, s * 0.9, zb + 0.1), (6.3, s * 0.7, 0.35), 0.24, 0.26)          # varais ate o chao
    for x in (-2.9, 2.9):
        bb(mb, F, x - 0.12 if x > 0 else x, x if x > 0 else x + 0.12, -1.55, 1.55, zb + 0.32, zb + 1.1, PLK)
    mb.cyl(0.16, 4.6, F.p(-0.4, 0, 1.9), F.r(math.pi / 2, 0, 0), IRON, 8, bevel=0.0)
    if load:
        barrel(mb, F, -1.3, -0.45, zb + 0.32, h=1.9, r=0.75)
        crate(mb, F, 1.0, 0.3, zb + 0.32, s=1.5, a=0.2)


# ------------------------------------------------------------------ MEDALHAO da praca
def medallion(mb, F, r=9.0, top=0.0, seed=0):
    """MEDALHAO do piso (picareta cruzando a bigorna), REBAIXADO: o topo mais alto (bigorna) fica em top + 0,11 e o
    chamador passa top = topo da praca - 0,12. Camadas (cada uma >= 0,12 acima da que cobre): fundo das juntas
    (top-0,40) | lajes do disco claro em setores (top-0,27) | cabo e cabeca da PICARETA em bronze (top-0,14) |
    contorno de ferro da bigorna (top-0,01) | BIGORNA de perfil em bronze (top+0,11). Anel de aduelas em 2 tons
    (top-0,03 / -0,06) com filete de bronze e losangos de bronze nos 4 rumos (top+0,11).
    +x local = 'direita' do icone, +y local = 'cima' do icone (aponte para a forja: do spawn o icone le em pe).
    O chao por baixo precisa estar furado (sem face de topo) ou abaixo de top - 0,52."""
    r_in = r - 1.5
    disc = [(r * 0.998 * math.cos(2 * math.pi * i / 40), r * 0.998 * math.sin(2 * math.pi * i / 40)) for i in range(40)]
    ext(mb, F, disc, "z", top - 1.25, top - 0.40, PAVE_J)                        # fundo das juntas
    n = 28
    for i in range(n):
        a0, a1 = 2 * math.pi * i / n + 0.006, 2 * math.pi * (i + 1) / n - 0.006
        poly = [(r_in * math.cos(a0), r_in * math.sin(a0)), (r * math.cos(a0), r * math.sin(a0)),
                (r * math.cos(a1), r * math.sin(a1)), (r_in * math.cos(a1), r_in * math.sin(a1))]
        m = PAVE_E if i % 2 == 0 else "Stone_VM_Base"
        ext(mb, F, poly, "z", top - 0.6, top - (0.03 if i % 2 == 0 else 0.06), m)
    ring = [((r_in - 0.02) * math.cos(2 * math.pi * i / 48), (r_in - 0.02) * math.sin(2 * math.pi * i / 48))
            for i in range(48)]
    ring_i = [((r_in - 0.4) * math.cos(2 * math.pi * i / 48), (r_in - 0.4) * math.sin(2 * math.pi * i / 48))
              for i in range(48)]
    for i in range(48):
        j = (i + 1) % 48
        ext(mb, F, [ring_i[i], ring[i], ring[j], ring_i[j]], "z", top - 0.6, top - 0.05, BRONZE)
    inner = r_in - 0.42
    for i in range(12):
        a0, a1 = 2 * math.pi * i / 12 + 0.01, 2 * math.pi * (i + 1) / 12 - 0.01
        pts = [(0.0, 0.0)] + [(inner * math.cos(a0 + (a1 - a0) * t / 3), inner * math.sin(a0 + (a1 - a0) * t / 3))
                              for t in range(4)]
        ext(mb, F, pts, "z", top - 0.7, top - 0.27, "Stone_VM_Trim")
    for k in range(4):                                         # losangos de bronze nos 4 rumos
        a = k * math.pi / 2 + math.pi / 2
        cx, cy = (r - 0.75) * math.cos(a), (r - 0.75) * math.sin(a)
        ux, uy = math.cos(a), math.sin(a)
        vx, vy = -uy, ux
        ext(mb, F, [(cx - ux * 0.55, cy - uy * 0.55), (cx + vx * 0.3, cy + vy * 0.3), (cx + ux * 0.55, cy + uy * 0.55),
                    (cx - vx * 0.3, cy - vy * 0.3)], "z", top - 0.4, top + 0.11, BRONZE)
    # PICARETA (atras da bigorna): cabo diagonal + cabeca em crescente
    zp = top - 0.14
    u = (math.cos(math.radians(48)), math.sin(math.radians(48)))
    pv = (-u[1], u[0])
    a, b = (-5.2 * u[0], -5.2 * u[1]), (4.6 * u[0], 4.6 * u[1])
    hw = 0.36
    ext(mb, F, [(a[0] + pv[0] * hw, a[1] + pv[1] * hw), (a[0] - pv[0] * hw, a[1] - pv[1] * hw),
                (b[0] - pv[0] * hw, b[1] - pv[1] * hw), (b[0] + pv[0] * hw, b[1] + pv[1] * hw)], "z", top - 0.4, zp,
        BRONZE)
    H = (4.15 * u[0], 4.15 * u[1])
    top_e, bot_e = [], []
    for i in range(9):
        t = -1 + 2 * i / 8
        bulge = 1.05 * (1 - t * t)
        thick = 0.18 + 0.62 * (1 - t * t)
        top_e.append((H[0] + pv[0] * 3.6 * t + u[0] * bulge, H[1] + pv[1] * 3.6 * t + u[1] * bulge))
        bot_e.append((H[0] + pv[0] * 3.3 * t + u[0] * (bulge - thick), H[1] + pv[1] * 3.3 * t + u[1] * (bulge - thick)))
    for i in range(8):
        ext(mb, F, [bot_e[i], bot_e[i + 1], top_e[i + 1], top_e[i]], "z", top - 0.4, zp, BRONZE)
    # BIGORNA (perfil) em pedacos convexos: face, cintura, pe, chifre; contorno de ferro 0,22 maior
    parts = [[(-2.5, 1.9), (3.2, 1.9), (3.3, 0.75), (1.55, 0.45), (-1.25, 0.5), (-2.7, 0.75)],
             [(-1.25, 0.5), (1.55, 0.45), (0.95, -0.75), (-0.65, -0.75)],
             [(-0.65, -0.75), (0.95, -0.75), (2.35, -1.55), (2.6, -2.25), (-2.3, -2.25), (-2.05, -1.55)],
             [(-4.6, 1.35), (-2.5, 1.9), (-2.7, 0.75)]]
    for pc in parts:
        cxp = sum(p[0] for p in pc) / len(pc)
        cyp = sum(p[1] for p in pc) / len(pc)
        big = [(x + math.copysign(0.22, x - cxp), y + math.copysign(0.22, y - cyp)) for x, y in pc]
        ext(mb, F, big, "z", top - 0.4, top - 0.01, IRON)
        ext(mb, F, pc, "z", top - 0.4, top + 0.11, BRONZE)


# ------------------------------------------------------------------ ESTUDIO (closes de cada peca com boneco 5,2)
def studio(out, roblox=False):
    import vm_scene
    VL.reset_scene()
    fm_lib.make_materials()
    vm_scene.setup()
    g = MB("VM_Studio_Ground", "02_TERRAIN", detail="far", floor=-999)
    g.box2((-120, -60, -1.0), (160, 60, 0.0), "Grass_VM", 0.0)
    g.finish()
    cams = []
    x = 0.0
    names = ["A3", "B2", "C2", "D3", "E2", "F2"]
    for i, k in enumerate(names):
        sp = spec_of(k, seed="studio_" + k)
        W = sp["W"]
        x += W / 2 + 9.0
        F = Frame(x, 0.0, 0.0, 0.0)            # frente = +y Blender
        mb = MB("VM_House_Studio_" + k, "03_TOWN", detail="far", floor=-999)
        dmb = MB("VM_Town_StudioDress_" + k, "03_TOWN", detail="far", floor=-999)
        info = house(mb, F, sp, dmb=dmb)
        ob = mb.finish()
        dmb.finish()
        tris = sum(len(p.vertices) - 2 for p in ob.data.polygons)
        print("STUDIO %s: %d materiais, %d tris" % (k, len(ob.data.materials), tris))
        # boneco 3 studs a frente da casa (VL.dummy recebe ROBLOX: z = -y Blender), olhando a camera
        VL.dummy("SCALE_Studio_" + k, x + W / 2 - 1.5, -(info["top_y"] + 3.0), 0.0, 0, -1)
        fm_lib.camera("CAM_ST_%s" % k, Vector((x + 4.0, 31.0 + info["top_y"], 8.0)), Vector((x, 0.0, 11.5)), 26)
        fm_lib.camera("CAM_ST_%s_close" % k, Vector((x - W * 0.15, info["top_y"] + 7.5, 4.0)),
                      Vector((x - W * 0.1, 0.0, 6.5)), 20)
        x += W / 2
    # pecas de rua
    pm = MB("VM_Town_StudioProps", "03_TOWN", detail="far", floor=-999)
    F = Frame(20.0, -22.0, 0.0, 0.0)
    cobbles(pm, F, -9.0, 9.0, [(-8.0, 0.22), (0.0, 0.22), (6.0, 1.4)], seed="st")
    curb(pm, F, -9.4, -8.0, 0.0, lambda qx, qy: 0.22)
    for i in range(6):
        tuft(pm, F, -11.0 + (i % 2) * 0.6, -7.0 + i * 2.2, -0.2)
        pebble(pm, F, -10.6, -6.0 + i * 2.3, -0.1, 0.8, "Stone_VM_Base", i)
    mureta(pm, sub(F, 0.0, 9.0, 0.0), 16.0, seed="st")
    lp = lamp_post(pm, sub(F, 11.5, 0.0, 0.0))
    barrel(pm, F, 14.0, -4.0)
    barrel(pm, F, 15.8, -3.2)
    crate(pm, F, 14.6, -6.6, a=0.3)
    cart(pm, sub(F, 22.0, -2.0, 0.0, 0.4))
    pm.finish()
    fm_lib.light("L_VM_Lamp_Studio", "POINT", lp, 60.0, (1.0, 0.75, 0.45), 0.3)
    VL.dummy("SCALE_Studio_Rua", 22.0, 21.0, 0.0, 0, 1)          # Roblox (22, 21) = Blender (22, -21)
    mm = MB("VM_Town_StudioMedal", "03_TOWN", detail="far", floor=-999)
    medallion(mm, Frame(-20.0, -22.0, 0.3, 0.0), 9.0, 0.3)
    mm.finish()
    fm_lib.camera("CAM_ST_Rua", Vector((14.0, -36.0, 6.0)), Vector((22.0, -20.0, 1.5)), 22)
    fm_lib.camera("CAM_ST_Props", Vector((20.0, -34.0, 4.5)), Vector((18.0, -24.0, 2.5)), 26)
    fm_lib.camera("CAM_ST_Medal", Vector((-20.0, -40.0, 18.0)), Vector((-20.0, -22.0, 0.0)), 24)
    sc = bpy.context.scene
    if roblox:
        print("MODO roblox: %d materiais" % fm_lib.apply_preview("roblox"))
    import os
    os.makedirs(out, exist_ok=True)
    sc.render.resolution_x, sc.render.resolution_y = 960, 540
    sc.render.image_settings.file_format = "JPEG"
    sc.eevee.taa_render_samples = 16
    for ob in sorted([o for o in bpy.data.objects if o.type == "CAMERA" and o.name.startswith("CAM_ST_")],
                     key=lambda o: o.name):
        sc.camera = ob
        sc.render.filepath = os.path.join(out, ob.name + ".jpg")
        bpy.ops.render.render(write_still=True)
        print("RENDER", ob.name)


if __name__ == "__main__":
    import sys
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    if argv and argv[0] == "studio":
        from mathutils import noise as _noise
        _noise.seed_set(4402)
        studio(argv[1], roblox="--roblox" in argv)
