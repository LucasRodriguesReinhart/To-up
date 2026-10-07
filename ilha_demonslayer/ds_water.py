# ds_water - ZONA WATER da Ilha 4 (DEMON SLAYER), onda 2c. build() substitui ds_blockout.water.
# Prefixo DS_Water_, colecao 07_WATER. Sem luz. A AGUA e do Roblox (paineis com textura rolando, espelhos, nevoa), feita
# a partir dos marcadores FX_Fall_* / WATER_*; aqui so a PEDRA estanque que conta UMA historia de agua:
#   nascente -> aqueduto de madeira -> roda d'agua e poco da roda (ds_forge, onda 2b: NAO sao daqui) -> CALHA de cantaria
#   no terraco da forja (TAILRACE da planta, comeca colada na saida do poco) -> LABIO no muro da forja entre 2
#   afloramentos de rocha, bica em balanco -> CASCATA unica de ~20 (FX_Fall_1) com 1 degrau de rocha no meio -> LAGOA no
#   canto nordeste da clareira (margem natural: barranco de terra baixo que nasce do chao de baixo (grama ou terra) +
#   pedras de 3 tamanhos, algumas meio afundadas; pedras grandes no pe da queda) -> CANAL de cantaria pela margem leste da
#   clareira, sob a pontezinha do summon (ds_summon) -> SANGRADOURO em degraus pela ravina leste (2 soleiras e 3 pocos de
#   pedra) -> bica em balanco na borda da ilha (FX_Fall_2, fino). Acento unico: tsukubai com kakehi na cabeceira da
#   pontezinha (ablucao antes do summon), transbordando no canal.
# COTAS (o leito e o do ds_terrain: corpo a piso - 0,5 onde ha agua; ver ds_terrain.bed_regions):
#   clareira: agua 60,32 (T1 + 0,12) sobre o leito 59,7 (0,62); borda (capa do canal / crista do barranco) >= 60,65;
#   terraco da forja: agua 80,64 (T4 + 0,44) sobre o leito 79,7 (0,94); capa 80,96. A agua do terraco fica 0,44 acima
#   do piso porque a soleira da bica tem de passar POR CIMA da pele do terreno (80,2) entre o fim do furo da calha e a
#   face do muro: soleira 80,36 -> lamina de 0,28 caindo. A calha le como canal de pedra elevado (0,76 acima do patio).
#   ravina: 3 pocos (leito medido 59,6 / 57,0 / 53,6 -> agua 60,32 / 57,62 / 54,22), soleiras 0,3 abaixo da agua.
# MARCADORES: o ds_core cria os FX_*/WATER_* (onda 0, estimados) e chama water_markers() deste modulo (acrescimo
#   pontual no ds_core.fx_markers): os valores daqui sao os da PEDRA deste modulo (as mesmas constantes que a desenham)
#   e o build() ainda MEDE na cena (raios) o labio, o degrau, o pe e a cortina do sangradouro e avisa se divergir.
# MEDIDA NA CENA (classe Ground): o contorno REAL do furo que o ds_terrain deixa para a agua (a pele e simplificada pelo
#   dissolve: no canal da clareira o furo chega a ~1,0 fora do eixo da planta) define a face externa de CADA bloco (sem
#   fresta escura no pe do muro) e a largura do barranco da lagoa; o chao embaixo define o material do barranco.
# UM objeto (DS_Water_Stone): 1 MeshPart por material. Fora (de proposito): agua decorativa, ilhotas, cachoeiras
#   extras. A guarda invisivel da lagoa e do ds_col; colisao propria so das 2 pedras altas da margem e do tsukubai.
import math, zlib
import bmesh
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
import ds_lib as DL
from ds_lib import MB, col_box, ccw, yaw_to
import ds_layout as L

T1, T3, T4 = L.T1, L.T3, L.T4
C = "07_WATER"
STONE, SDARK, CLIFF, MOSS = "Stone_DS", "Stone_DS_Dark", "Cliff_DS", "Cliff_DS_Moss"
WETDIRT, GRASS = "Dirt_DS_Dark", "Grass_DS"

# ------------------------------------------------------------------ cotas
BED_T1 = T1 - 0.5            # leito do ds_terrain na lagoa e no canal (59,7)
BED_T4 = T4 - 0.5            # leito da calha (79,7)
LEVEL = T1 + 0.12            # agua da lagoa e do canal (60,32)
LEVEL_T4 = T4 + 0.44         # agua da calha (80,64)
COPE = LEVEL + 0.33          # capa do canal (60,65): a pontezinha do summon passa >= 0,1 acima
COPE_T4 = LEVEL_T4 + 0.32    # capa da calha (80,96)
LIP_TOP = T4 + 0.16          # soleira da bica da cascata (80,36): 0,16 acima da pele do patio
CH_IN = 1.5                  # meia-largura da agua no canal e na calha (3,0)
CH_OUT = 2.65                # face externa do muro (projeto; furo da planta 2,5): cada bloco alarga ate cobrir o furo REAL
JOINT = 0.14                 # junta entre blocos
# ravina (leito MEDIDO no ds_terrain.ravine: 59,6 / 57,0 / 53,6; degraus em x 142,5 e 149,7; borda em x ~158,5)
RAV = [  # (pontos do eixo, cota do leito, nivel da agua)
    ([(133.0, 233.73), (137.6, 232.4), (141.9, 231.0)], 59.6, LEVEL),
    ([(142.9, 230.7), (146.2, 230.0), (149.0, 229.6)], 57.0, 57.62),
    ([(150.2, 229.5), (154.2, 229.1), (157.9, 228.6)], 53.6, 54.22),
]
RAV_IN = 1.2                 # meia-largura da agua no sangradouro (2,4) -> 0,8 na bica final
SILLS = [((141.9, 231.0), (142.9, 230.7), LEVEL - 0.3),          # soleira 1 (sobre o degrau 59,6 -> 57,0)
         ((149.0, 229.6), (150.2, 229.5), 57.62 - 0.3)]          # soleira 2 (57,0 -> 53,6)
SPILL_LIP = (160.4, 228.5)   # ponta da bica do sangradouro (em balanco 1,9 alem da borda de 53,6)
SPILL_TOP = 54.22 - 0.3      # topo da bica final (53,92)
SPILL_BASE_Z = 12.0          # pe da cortina do sangradouro (nevoa; abaixo dela so o mar de nuvens)
# cascata (muro da forja medido: face vertical em y ~428,1 de 60 a 80 entre x 106 e 118)
FACE_Y = 428.1
FALL_X = 116.0
LIP_EDGE = (FALL_X, FACE_Y - 1.2)            # ponta da bica (balanco de 1,2 alem da face)
STEP = (116.2, 426.7, 70.35)                  # degrau de rocha no meio da queda (centro, topo)
STEP_FRONT = 425.0                            # borda da frente do degrau
BASE = (FALL_X, 424.4)                        # pe da cortina na lagoa
# lagoa: contorno DESENHADO da agua (anti-horario), dentro do furo do terreno (POND + 0,6) com folga; a boca do canal
# (x 116,4..119,4) fica FORA do poligono (a agua do canal comeca na linha da boca: sem 2 laminas sobrepostas)
MOUTH_Y = 381.2
POND_W = [(98.6, 382.2), (103.0, 381.6), (108.0, 380.4), (112.5, 380.2), (116.4, 379.4), (116.4, MOUTH_Y),
          (119.4, MOUTH_Y), (119.4, 378.9), (122.3, 378.9), (124.6, 384.5), (126.9, 391.5), (127.6, 397.5),
          (127.2, 405.0), (126.0, 412.5), (125.9, 419.0), (124.2, 425.2), (120.0, 425.9), (114.5, 426.3),
          (109.0, 426.4), (106.4, 422.0), (104.0, 415.5), (100.6, 407.4), (97.0, 400.0), (95.9, 395.0), (96.9, 389.0),
          (97.7, 384.6)]
CHAN = [(117.91, MOUTH_Y), L.CHANNEL[1], L.CHANNEL[2], L.CHANNEL[3], L.CHANNEL[4], (133.0, 233.73)]
# cabeca da calha = a SAIDA do poco da roda do ds_forge (vao no muro leste do poco, x 95,2 +- 0,62 de capa, y 482 +-
# 1,75): os blocos comecam cortados na vertical x = TAIL_CUT_X, colados no muro do poco (sem bloco de cabeceira)
TAIL_CUT_X = 95.9
TAIL_HEAD = (L.TAILRACE[0][0] - TAIL_CUT_X) / 0.7593 + 0.02   # recua o eixo ate a linha do corte
TAIL = [L.TAILRACE[0], L.TAILRACE[1], L.TAILRACE[2], (FALL_X, 431.3)]   # o fim do TAILRACE (116, 432) fica dentro

# ------------------------------------------------------------------ cameras de revisao (o studio_ds as cria)
CAMS = {
    "CAM_DSWat_PondPH": ((66.0, 346.0, T1 + 5.5), (112.0, 410.0, T1 + 6.0), 22),
    "CAM_DSWat_Pond": ((92.0, 368.0, T1 + 7.0), (112.0, 402.0, T1 + 0.5), 24),
    "CAM_DSWat_Cascade": ((106.0, 392.0, T1 + 8.0), (116.0, 427.0, T1 + 10.5), 20),
    "CAM_DSWat_CascadeBase": ((108.0, 410.0, T1 + 4.0), (116.0, 425.5, T1 + 2.0), 24),
    "CAM_DSWat_Lip": ((104.0, 446.0, T4 + 5.5), (116.0, 430.0, T4 + 0.5), 24),
    "CAM_DSWat_Tailrace": ((124.0, 456.0, T4 + 5.5), (102.0, 478.0, T4 + 0.5), 24),
    "CAM_DSWat_TailHead": ((105.0, 473.0, T4 + 5.0), (95.5, 482.0, T4 + 0.5), 26),
    "CAM_DSWat_Bridge": ((121.5, 284.0, T1 + 2.4), (121.0, 300.0, T1 + 0.8), 24),
    "CAM_DSWat_BridgePH": ((106.0, 286.0, T1 + 5.5), (121.0, 300.0, T1 + 1.0), 24),
    "CAM_DSWat_Channel": ((113.0, 352.0, T1 + 5.5), (121.0, 318.0, T1 + 0.5), 24),
    "CAM_DSWat_Ravine": ((126.0, 225.0, T1 + 7.0), (148.0, 230.5, 56.5), 24),
    "CAM_DSWat_Spill": ((205.0, 229.0, 62.0), (160.0, 228.6, 50.0), 26),
    "CAM_DSWat_RavTop": ((150.0, 208.0, 92.0), (150.0, 230.0, 55.0), 30),
    "CAM_DSWat_Top": ((60.0, 330.0, 170.0), (115.0, 360.0, 60.0), 26),
    "CAM_DSWat_Tsukubai": ((114.6, 284.2, T1 + 3.6), (116.8, 291.0, T1 + 1.0), 26),
    "CAM_DSWat_LipBelow": ((103.0, 418.0, T3 + 5.5), (116.0, 427.5, 78.5), 24),
    "CAM_DSWat_SpillNear": ((167.0, 229.5, 66.0), (159.8, 228.6, 50.0), 26),
}


# ------------------------------------------------------------------ variacao DIRIGIDA (hash estavel)
def hh(*a):
    s = "|".join("%.2f" % v if isinstance(v, float) else str(v) for v in a)
    h = zlib.crc32(s.encode("utf-8")) & 0xffffffff
    # 6c: o crc32 e LINEAR (chaves vizinhas -> valores correlacionados: pedras vizinhas do canal/ravina saiam parecidas);
    # finalizador do murmur3 espalha os bits (o mesmo do ds_forge._hh). Os marcadores FX_*/WATER_* nao usam o hash
    # (saem das constantes em water_markers) e as caixas de colisao das pedras da lagoa saem de POND_STONES
    h ^= h >> 16
    h = (h * 0x85EBCA6B) & 0xffffffff
    h ^= h >> 13
    h = (h * 0xC2B2AE35) & 0xffffffff
    h ^= h >> 16
    return h / 4294967296.0


def cyc(seq, i):
    return seq[i % len(seq)]


# ------------------------------------------------------------------ o terreno REAL (medido na cena)
class Ground:
    """BVH do terreno (DS_Ter_/DS_Clr_) com o material de cada face: topo, material do chao e EXTENSAO REAL do furo que
    o ds_terrain deixa para a agua (o contorno do furo e simplificado pelo dissolve da pele: no canal da clareira ele
    chega a 1,0 fora do eixo da planta). Sem terreno detalhado (blockout): nada medido, valores de projeto."""

    def __init__(self):
        verts, polys, mats = [], [], []
        for o in bpy.data.objects:
            if o.type != "MESH" or not o.name.startswith(("DS_Ter_", "DS_Clr_")):
                continue
            me = o.data
            mw = o.matrix_world
            vs = [mw @ v.co for v in me.vertices]
            base = len(verts)
            verts += vs
            for p in me.polygons:
                xs = [vs[i].x for i in p.vertices]
                ys = [vs[i].y for i in p.vertices]
                if max(xs) > 70.0 and min(xs) < 190.0 and max(ys) > 200.0 and min(ys) < 500.0:
                    polys.append([base + i for i in p.vertices])
                    mats.append(o.material_slots[p.material_index].name if o.material_slots else "")
        self.t = BVHTree.FromPolygons(verts, polys) if polys else None
        self.mats = mats

    def hit(self, x, y, z0):
        if self.t is None:
            return None, ""
        h = self.t.ray_cast(Vector((x, y, z0)), Vector((0, 0, -1)), 40.0)
        return (h[0].z, self.mats[h[2]]) if h[0] is not None else (None, "")

    def ground_mat(self, x, y):
        z, m = self.hit(x, y, T1 + 4.0)
        return GRASS if m.startswith("Grass") else "Dirt_DS"

    def hole_ext(self, x, y, nx, ny, bed, d0=1.0, d1=4.0):
        """distancia (no rumo (nx, ny)) ate onde o chao volta a ficar acima do leito: a borda REAL do furo"""
        if self.t is None:
            return None
        d = d0
        while d < d1:
            z, m = self.hit(x + nx * d, y + ny * d, bed + 4.0)
            if z is None or z > bed + 0.15:
                return d
            d += 0.05
        return d1


GROUND = None


def _outer_fn(bed, keep=None, cap=None, lo=CH_OUT, hi=3.7):
    """face externa de cada bloco: cobre a borda REAL do furo do terreno + 0,22 (sem fresta escura no pe do muro).
    keep(x, y) -> True: fica no valor de projeto; cap(x, y) -> limite (p.ex. sob a pontezinha)"""
    def f(side, pts, n):
        x, y = pts[1]
        if GROUND is None or GROUND.t is None or (keep and keep(x, y)):
            return lo
        ext = max(GROUND.hole_ext(px, py, n[0] * side, n[1] * side, bed) or 0.0 for px, py in pts)
        d = max(lo, min(hi, ext + 0.3))
        if cap:
            d = min(d, cap(x, y) or hi)
        return d
    return f


# ------------------------------------------------------------------ pecas
def stone(mb, cx, cy, zt, zb, a, b, ang, key, m=STONE, cap=None, n=None, top_s=0.78, ch=None, tilt=None, bottom=False,
          foot=1.06):
    """pedra talhada pela agua: pegada de n lados (raios dirigidos pela chave), topo menor com chanfro largo (cap = o
    material do topo, p.ex. musgo), lados ate zb (enterrado: sem fundo). tilt = (dx, dy, queda por stud)"""
    if zt - zb < 0.2:
        return
    if n is None:
        n = (5, 6, 7, 6)[int(hh(key, "n") * 4) % 4]
    ca, sa = math.cos(ang), math.sin(ang)
    rr = [0.80 + 0.36 * hh(key, k) for k in range(n)]
    r0 = (hh(key, "r") - 0.5) * 0.6
    base = [(a * rr[k] * math.cos(r0 + 2 * math.pi * k / n), b * rr[k] * math.sin(r0 + 2 * math.pi * k / n))
            for k in range(n)]
    ch = min(ch if ch is not None else 0.22 + 0.18 * min(a, b), (zt - zb) * 0.45)
    bm = mb.bm

    def ring(s, zs):
        return [bm.verts.new((cx + u * s * ca - v * s * sa, cy + u * s * sa + v * s * ca, z))
                for (u, v), z in zip(base, zs)]
    if tilt:
        dx, dy, sl = tilt
        pr = [(u * ca - v * sa) * dx + (u * sa + v * ca) * dy for u, v in base]
        pm = min(pr)
        zts = [zt - sl * (p - pm) * top_s for p in pr]
    else:
        zts = [zt] * n
    top = ring(top_s, zts)
    mid = ring(1.0, [z - ch for z in zts])
    bm.faces.new(top)
    for k in range(n):
        j = (k + 1) % n
        bm.faces.new((mid[k], mid[j], top[j], top[k]))
    if cap and cap != m:                # topo de outro material (musgo): vertices proprios (a cor nao vaza)
        mb._post(top + mid, cap, None, 0, 1)
        up = ring(1.0, [z - ch for z in zts])
    else:                               # mesma pedra: 1 primitiva so (menos variantes = menos MeshParts)
        up = mid
    lo = ring(foot, [zb] * n)
    for k in range(n):
        j = (k + 1) % n
        bm.faces.new((lo[k], lo[j], up[j], up[k]))
    if bottom:                          # pedra em balanco (vista de baixo): fecha o fundo
        bm.faces.new(list(reversed(lo)))
    mb._post(up + lo + ([] if (cap and cap != m) else top), m, None, 0, 1)


def block(mb, quad, zb, zt, key, m=STONE, ch=0.12):
    """bloco de cantaria: quadrilatero (anti-horario visto de cima) de zb ate zt, chanfro so nas arestas de cima (nada
    de fundo: assenta no leito/no chao). Topo com variacao dirigida de +-0,03 (pedra assentada a mao)"""
    bm = mb.bm
    zt = zt + (hh(key, "z") - 0.5) * 0.06
    cx = sum(p[0] for p in quad) / 4
    cy = sum(p[1] for p in quad) / 4
    lo = [bm.verts.new((x, y, zb)) for x, y in quad]
    mid = [bm.verts.new((x, y, zt - ch)) for x, y in quad]
    ins = []
    for x, y in quad:
        dx, dy = cx - x, cy - y
        d = math.hypot(dx, dy) or 1.0
        k = min(ch * 1.35, d * 0.4) / d
        ins.append((x + dx * k, y + dy * k))
    top = [bm.verts.new((x, y, zt)) for x, y in ins]
    for k in range(4):
        j = (k + 1) % 4
        bm.faces.new((lo[k], lo[j], mid[j], mid[k]))
        bm.faces.new((mid[k], mid[j], top[j], top[k]))
    bm.faces.new(top)
    mb._post(lo + mid + top, m, None, 0, 1)


# ------------------------------------------------------------------ eixo + offsets com meia-esquadria
def _normals(P):
    out = []
    for a, b in zip(P, P[1:]):
        dx, dy = b[0] - a[0], b[1] - a[1]
        ln = math.hypot(dx, dy) or 1.0
        out.append((-dy / ln, dx / ln))          # esquerda do sentido
    return out


def _off(P, N, i, t, d):
    """ponto no segmento i (t em 0..1) deslocado d para a esquerda; nas pontas internas usa a meia-esquadria"""
    a, b = P[i], P[i + 1]
    x, y = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
    nx, ny = N[i]
    if t <= 1e-6 and i > 0:
        mx, my = N[i - 1][0] + nx, N[i - 1][1] + ny
        ml = math.hypot(mx, my)
        mx, my = mx / ml, my / ml
        k = d / (mx * nx + my * ny)
        return (x + mx * k, y + my * k)
    if t >= 1 - 1e-6 and i < len(N) - 1:
        mx, my = N[i + 1][0] + nx, N[i + 1][1] + ny
        ml = math.hypot(mx, my)
        mx, my = mx / ml, my / ml
        k = d / (mx * nx + my * ny)
        return (x + mx * k, y + my * k)
    return (x + nx * d, y + ny * d)


LENS = (2.6, 3.4, 2.9, 3.7, 2.4, 3.1, 3.5, 2.7)


def _corner(P, N, i, t, d, shift):
    """canto de bloco: offset d (meia-esquadria nas dobras internas) deslocado 'shift' ao longo do segmento i"""
    x, y = _off(P, N, i, t, d)
    a, b = P[i], P[i + 1]
    ln = math.dist(a, b) or 1.0
    return (x + (b[0] - a[0]) / ln * shift, y + (b[1] - a[1]) / ln * shift)


def channel_walls(mb, P, zb, zt, key, d_in=CH_IN, d_out=CH_OUT, skip=None, m=STONE, start_k=0, outer_fn=None,
                  cut_x=None):
    """muros de cantaria dos dois lados do eixo P: blocos de comprimento DIRIGIDO (ciclo LENS, desencontrado entre os
    lados), junta de 0,14, meia-esquadria nas dobras (os 2 blocos da dobra terminam na bissetriz, junta entre eles).
    skip(x, y) -> True pula o bloco"""
    N = _normals(P)
    last = len(P) - 2
    n = 0
    for side in (1, -1):
        k = start_k + (0 if side > 0 else 3)
        for i in range(len(P) - 1):
            ln = math.dist(P[i], P[i + 1])
            if ln < 0.3:
                continue
            nb = max(1, int(round(ln / 3.05)))
            ws = [cyc(LENS, k + j) for j in range(nb)]
            tot = sum(ws)
            t0 = 0.0
            for j in range(nb):
                t1 = 1.0 if j == nb - 1 else t0 + ws[j] / tot
                s0 = JOINT / 2 if (j > 0 or i > 0) else 0.0
                s1 = -JOINT / 2 if (j < nb - 1 or i < last) else 0.0
                do = d_out
                if outer_fn:
                    ax = [(P[i][0] + (P[i + 1][0] - P[i][0]) * t, P[i][1] + (P[i + 1][1] - P[i][1]) * t)
                          for t in (t0 + 0.05, (t0 + t1) / 2, t1 - 0.05)]
                    do = outer_fn(side, ax, N[i])
                pa_i, pa_o = _corner(P, N, i, t0, side * d_in, s0), _corner(P, N, i, t0, side * do, s0)
                pb_i, pb_o = _corner(P, N, i, t1, side * d_in, s1), _corner(P, N, i, t1, side * do, s1)
                if cut_x is not None and i == 0 and j == 0:
                    # inicio cortado na vertical x = cut_x (encosta num muro paralelo a Y), ao longo do segmento
                    ux_ = (P[1][0] - P[0][0]) / ln
                    uy_ = (P[1][1] - P[0][1]) / ln
                    pa_i = (cut_x, pa_i[1] + (cut_x - pa_i[0]) / ux_ * uy_)
                    pa_o = (cut_x, pa_o[1] + (cut_x - pa_o[0]) / ux_ * uy_)
                q = [pa_i, pb_i, pb_o, pa_o]
                cx, cy = sum(p[0] for p in q) / 4, sum(p[1] for p in q) / 4
                if not (skip and skip(cx, cy)):
                    block(mb, ccw(q), zb, zt, (key, side, i, j), m=m)
                    n += 1
                t0 = t1
                k += 1
    return n


def extend_back(P, d):
    a, b = P[0], P[1]
    ln = math.dist(a, b)
    return [(a[0] - (b[0] - a[0]) / ln * d, a[1] - (b[1] - a[1]) / ln * d)] + list(P[1:])


# ------------------------------------------------------------------ 1. calha do terraco da forja + labio da cascata
def tailrace(mb):
    P = extend_back(TAIL, TAIL_HEAD)
    # ONDA 6b (item 43): os blocos descem 0,25 (BED - 0,35): ficavam 0,2 acima do leito real do furo
    nb = channel_walls(mb, P, BED_T4 - 0.35, COPE_T4, "tr", start_k=2, cut_x=TAIL_CUT_X,
                       outer_fn=_outer_fn(BED_T4, keep=lambda x, y: y < FACE_Y + 4.0 or x < TAIL_CUT_X + 3.0))
    # LABIO: 2 afloramentos da rocha do muro (topo com musgo, a face rente a face do muro e enterrados nele) sobem dos 2
    # lados da calha na borda: a agua so tem a fresta entre eles - por isso cai ali; a soleira de pedra escura molhada
    # avanca 1,2 alem da face
    fx = FALL_X
    stone(mb, fx - 4.3, FACE_Y + 1.85, T4 + 1.6, T4 - 5.0, 2.2, 1.6, 0.2, "lipW", m=CLIFF, cap=MOSS, n=7,
          tilt=(0.3, -1.0, 0.16))
    stone(mb, fx + 4.2, FACE_Y + 1.75, T4 + 1.2, T4 - 5.0, 2.0, 1.5, -0.25, "lipE", m=CLIFF, cap=MOSS, n=6,
          tilt=(-0.3, -1.0, 0.18))
    stone(mb, fx + 6.4, FACE_Y + 1.9, T4 + 0.9, T4 - 0.6, 1.1, 0.9, 0.6, "lipE2", m=CLIFF, n=5)
    # soleira: laje que assenta no leito da calha, passa sobre a pele do patio (80,2) e fica em balanco alem da face
    y0, y1 = TAIL[-1][1] - 0.1, LIP_EDGE[1]
    # ONDA 6b (item 42): a soleira ABRE para a borda (3,5 -> 3,8; era 3,5 -> 2,5) e a cortina sai larga
    q = [(fx - 1.75, y0), (fx + 1.75, y0), (fx + 1.9, y1), (fx - 1.9, y1)]
    block(mb, ccw(q), LIP_TOP - 0.62, LIP_TOP, "lipslab", m=SDARK, ch=0.1)
    # labio: 2 pedras salientes 0,4 alem da borda, nas pontas da soleira (a agua se abre entre elas)
    for s in (-1, 1):
        stone(mb, fx + s * 2.15, y1 + 0.05, LIP_TOP + 0.38, LIP_TOP - 0.9, 0.62, 0.5, 0.3 * s, ("lipnose", s), m=SDARK,
              n=5, bottom=True, foot=0.95)
    # bochechas da bica (pedras baixas dos 2 lados da soleira, entre ela e as pedras-guarda)
    for s in (-1, 1):
        yb = TAIL[-1][1] - JOINT
        q = [(fx + s * 1.8, yb), (fx + s * 2.55, yb), (fx + s * 2.75, FACE_Y - 0.55),
             (fx + s * 1.95, FACE_Y - 0.55)]
        block(mb, ccw(q), LIP_TOP - 0.9, LIP_TOP + 0.62, ("lipcheek", s), m=SDARK, ch=0.12)
    return nb


def cascade(mb):
    # degrau de rocha no meio da queda (enterrado na face): onde a cortina bate e quebra (FX_Fall_1_Step). Mais largo que
    # a cortina (le dos 2 lados dela), topo com musgo caindo para a frente, fundo fechado (visto da lagoa, de baixo)
    sx, sy, sz = STEP
    stone(mb, sx, sy, sz, sz - 3.6, 4.3, 1.75, 0.0, "step", m=CLIFF, cap=MOSS, n=7, top_s=0.88, ch=0.4,
          tilt=(0.0, -1.0, 0.12), bottom=True, foot=0.92)
    # a rocha continua: lascas menores escalonadas dos 2 lados (o degrau nao e um bloco solto)
    stone(mb, sx + 5.2, sy + 0.6, sz - 1.6, sz - 4.8, 1.7, 1.25, 0.4, "step2", m=CLIFF, cap=MOSS, n=6, bottom=True,
          foot=0.9)
    stone(mb, sx - 4.9, sy + 0.8, sz - 2.7, sz - 5.6, 1.3, 1.05, -0.3, "step3", m=CLIFF, n=5, bottom=True, foot=0.9)


# ------------------------------------------------------------------ 2. lagoa: barranco baixo + pedras de margem
# (x, y, raio, topo, material, chave) - pedras GRANDES no pe da queda e na quina sudoeste (vista da clareira), medias
# no barranco, pequenas meio afundadas na agua (topo 0,1..0,2 acima da lamina)
POND_STONES = [
    # quina sudoeste (vista da clareira e da rota do pe da subida): grupo de 3, grande-media-molhada
    (99.6, 381.3, 2.3, 62.35, CLIFF, "S1"), (102.5, 379.8, 1.1, 61.2, CLIFF, "S2"),
    (102.7, 382.6, 0.7, 60.56, SDARK, "S3"),
    # margem sul: laje baixa + pedra molhada; ao lado da boca do canal
    (109.4, 379.5, 1.25, 60.98, CLIFF, "S4"), (111.9, 381.7, 0.75, 60.52, SDARK, "S5"),
    (113.5, 379.0, 1.0, 61.05, CLIFF, "S6"),
    # leste (a boca e o pe do barranco nordeste)
    (123.3, 379.7, 1.6, 61.7, CLIFF, "E1"), (125.6, 382.8, 0.8, 60.9, CLIFF, "E2"),
    (126.5, 390.2, 1.0, 61.0, CLIFF, "E3"), (124.9, 394.9, 0.7, 60.52, SDARK, "E4"),
    (128.3, 402.6, 1.3, 61.4, CLIFF, "E5"), (127.7, 415.0, 0.9, 60.9, CLIFF, "E6"),
    # pe da cascata: 2 rochas grandes enquadram o impacto, molhada perto do jato
    (111.3, 425.0, 2.0, 62.3, CLIFF, "N1"), (120.9, 424.6, 1.75, 61.85, CLIFF, "N2"),
    (124.0, 422.3, 0.9, 60.9, CLIFF, "N3"), (114.0, 421.9, 0.8, 60.55, SDARK, "N4"),
    (107.1, 424.3, 1.1, 61.1, CLIFF, "N5"),
    # oeste (pe da berma)
    (104.8, 418.4, 0.9, 60.9, CLIFF, "W1"), (101.6, 409.6, 1.3, 61.3, CLIFF, "W2"),
    (99.9, 403.1, 0.7, 60.52, SDARK, "W3"), (97.2, 396.6, 1.5, 61.6, CLIFF, "W4"),
    (97.3, 390.2, 0.8, 60.8, CLIFF, "W5"),
]
# pedras altas em chao andavel (fora do anel da guarda da lagoa): colisao propria
POND_STONE_COL = ("S1", "E1")


def pond(mb):
    """barranco de terra BAIXO ao longo da agua (faixa molhada escura -> crista -> grama que some no chao), aberto na boca
    do canal, com largura e altura DIRIGIDAS (senoides): nao e borda de piscina. As pedras quebram a linha."""
    W = POND_W
    n = len(W)
    # o barranco e uma faixa ABERTA: do lado leste da boca (indice 7) ate o lado oeste (indice 4), dando a volta
    idx = list(range(7, n)) + list(range(0, 5))
    pts = [W[i] for i in idx]
    # sub-divide (curvas mais macias)
    P = []
    for a, b in zip(pts, pts[1:]):
        P.append(a)
        if math.dist(a, b) > 3.2:
            P.append(((a[0] + b[0]) / 2, (a[1] + b[1]) / 2))
    P.append(pts[-1])
    # pontas do barranco encostadas na face externa dos muros do canal
    P[0] = (117.91 + CH_OUT + 0.15, 378.75)
    P[-1] = (117.91 - CH_OUT - 0.15, 379.55)
    bm = mb.bm
    rows = {"in": [], "c1": [], "c2": [], "out": []}
    m = len(P)
    for i, (x, y) in enumerate(P):
        a = P[max(0, i - 1)]
        b = P[min(m - 1, i + 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        ln = math.hypot(dx, dy) or 1.0
        ox, oy = dy / ln, -dx / ln                # para fora (o contorno e anti-horario)
        s = i / (m - 1)
        wv = 0.5 + 0.3 * math.sin(s * 13.0 + 0.6) + 0.2 * math.sin(s * 31.0 + 2.0)
        cw = 0.35 + 1.25 * max(0.0, min(1.0, wv)) + 0.15 * hh(i, "cw")
        hv = 0.5 + 0.5 * math.sin(s * 9.0 + 2.1) * math.cos(s * 4.0)
        cz = COPE + 0.02 + 0.34 * max(0.0, min(1.0, hv)) + 0.05 * hh(i, "cz")
        ow = 1.1 + 1.0 * (0.5 + 0.5 * math.sin(s * 7.0 + 1.0))
        if i in (0, m - 1):
            cw, ow = 0.6, 0.9
        elif GROUND is not None and GROUND.t is not None:
            ext = GROUND.hole_ext(x, y, ox, oy, BED_T1, 0.0, 5.0)
            ow = max(ow, ext - cw + 0.35)
        rows["in"].append(bm.verts.new((x - ox * 0.7, y - oy * 0.7, LEVEL - 0.36)))
        rows["c1"].append(bm.verts.new((x + ox * cw, y + oy * cw, cz)))
        rows["c2"].append(bm.verts.new((x + ox * cw, y + oy * cw, cz)))
        rows["out"].append(bm.verts.new((x + ox * (cw + ow), y + oy * (cw + ow), T1 - 0.12)))
    for i in range(m - 1):
        bm.faces.new((rows["in"][i], rows["in"][i + 1], rows["c1"][i + 1], rows["c1"][i]))
    mb._post(rows["in"] + rows["c1"], WETDIRT, None, 0, 1)
    # faixa de fora: o MESMO chao que esta embaixo (grama onde o terreno e grama, terra onde e terra) - o barranco nasce
    # do chao em vez de desenhar um anel verde em volta da agua; trechos seguidos do mesmo chao = 1 primitiva
    gm = GROUND.ground_mat if GROUND is not None else (lambda x, y: "Dirt_DS")
    runs = []
    for i in range(m - 1):
        a, b = rows["out"][i].co, rows["out"][i + 1].co
        g = gm((a.x + b.x) / 2, (a.y + b.y) / 2)
        if runs and runs[-1][0] == g:
            runs[-1][1].append(i)
        else:
            runs.append((g, [i]))
    for g, ids in runs:
        c2 = {i: bm.verts.new(rows["c2"][i].co) for i in ids + [ids[-1] + 1]}
        ot = {i: bm.verts.new(rows["out"][i].co) for i in ids + [ids[-1] + 1]}
        for i in ids:
            bm.faces.new((c2[i], c2[i + 1], ot[i + 1], ot[i]))
        mb._post(list(c2.values()) + list(ot.values()), g, None, 0, 1)
    for v in rows["c2"] + rows["out"]:
        bm.verts.remove(v)
    for x, y, r, zt, mt, key in POND_STONES:
        big = r > 1.4
        stone(mb, x, y, zt, BED_T1 - 0.25, r, r * (0.68 + 0.2 * hh(key, "b")), hh(key, "a") * math.pi, key, m=mt,
              cap=(MOSS if big and mt == CLIFF else None), n=(7 if big else 6), top_s=(0.74 if mt == SDARK else 0.8),
              tilt=(hh(key, "tx") - 0.5, hh(key, "ty") - 0.5, 0.14) if mt != SDARK else None)
        if key in POND_STONE_COL:
            col_box("DS_WaterStone", (r * 1.6, r * 1.3, zt - T1 + 0.4), (x, y, (zt + T1 - 0.4) / 2))


# ------------------------------------------------------------------ 3. canal da clareira (sob a pontezinha) + ravina
def channel(mb):
    # sob a pontezinha (y 293..307) a face externa fica no projeto (2,65): as vigas do arco passam >= 0,2 acima da capa
    # e o tabuleiro cobre a fresta do furo; na boca (lagoa) e na entrada da ravina o barranco/as pedras cobrem
    nb = channel_walls(mb, CHAN, BED_T1 - 0.35, COPE, "ch",          # ONDA 6b (item 43): era BED - 0,1
                       outer_fn=_outer_fn(BED_T1, keep=lambda x, y: y > MOUTH_Y - 4.5,
                                          cap=lambda x, y: CH_OUT if 293.0 < y < 307.0 else (3.2 if y < 240.0 else None)))
    # cabeca do canal na lagoa: 2 pedras-cunha maiores onde o barranco encosta (a boca le como obra, nao como corte)
    for s, key in ((-1, "mouthW"), (1, "mouthE")):
        stone(mb, 117.91 + s * (CH_OUT + 0.25), MOUTH_Y + 0.5, COPE + 0.42, BED_T1 - 0.2, 0.95, 0.8, 0.3 * s, key,
              m=STONE, n=6, top_s=0.84)
    return nb


def ravine(mb):
    """sangradouro: runa estreita de pedras brutas sobre o leito em degraus do ds_terrain; 3 pocos, 2 soleiras de pedra
    escura molhada (a agua passa 0,3 por cima e cai no poco de baixo), bica final em balanco na borda da ilha"""
    n = 0
    for k, (P, bed, lev) in enumerate(RAV):
        N = _normals(P)
        for side in (1, -1):
            for i in range(len(P) - 1):
                ln = math.dist(P[i], P[i + 1])
                nb = max(1, int(round(ln / 2.3)))
                for j in range(nb):
                    key = ("rv", k, side, i, j)
                    t = (j + 0.5 + (0.25 if side > 0 else -0.15)) / nb
                    t = max(0.12, min(0.88, t))
                    big = hh(key, "big") > 0.62
                    r = (1.15 if big else 0.85) + 0.2 * hh(key, "r")
                    d = RAV_IN + r * 0.78 + 0.1 * hh(key, "d")
                    x, y = _off(P, N, i, t, side * d)
                    ang = math.atan2(P[i + 1][1] - P[i][1], P[i + 1][0] - P[i][0]) + (hh(key, "ang") - 0.5) * 0.8
                    zt = lev + 0.36 + (0.75 if big else 0.3) * hh(key, "z")
                    stone(mb, x, y, zt, bed - 0.3, r, r * 0.8, ang, key, m=SDARK, cap=(MOSS if big else None),
                          n=(7 if big else 6), top_s=0.8, tilt=(side * N[i][0], side * N[i][1], 0.1))
                    n += 1
    for k, (a, b, top) in enumerate(SILLS):
        ux, uy = b[0] - a[0], b[1] - a[1]
        ln = math.hypot(ux, uy)
        ux, uy = ux / ln, uy / ln
        nx, ny = -uy, ux
        c = ((a[0] + b[0]) / 2 + ux * 0.2, (a[1] + b[1]) / 2 + uy * 0.2)
        w = RAV_IN + 0.75
        hl = 0.75
        q = [(c[0] - ux * hl + nx * w, c[1] - uy * hl + ny * w), (c[0] - ux * hl - nx * w, c[1] - uy * hl - ny * w),
             (c[0] + ux * hl - nx * w, c[1] + uy * hl - ny * w), (c[0] + ux * hl + nx * w, c[1] + uy * hl + ny * w)]
        block(mb, ccw(q), RAV[k + 1][1] - 0.3, top, ("sill", k), m=SDARK, ch=0.1)
        n += 1
    # bica final: laje longa em balanco (1,2 apoiada no leito de 53,6, 2 alem da borda), afinando para a ponta
    P = RAV[2][0]
    a = P[-1]
    ux, uy = SPILL_LIP[0] - a[0], SPILL_LIP[1] - a[1]
    ln = math.hypot(ux, uy)
    ux, uy = ux / ln, uy / ln
    nx, ny = -uy, ux
    back = (a[0] - ux * 1.4, a[1] - uy * 1.4)
    q = [(back[0] + nx * 1.6, back[1] + ny * 1.6), (back[0] - nx * 1.6, back[1] - ny * 1.6),
         (SPILL_LIP[0] - nx * 1.05, SPILL_LIP[1] - ny * 1.05), (SPILL_LIP[0] + nx * 1.05, SPILL_LIP[1] + ny * 1.05)]
    block(mb, ccw(q), SPILL_TOP - 0.7, SPILL_TOP, "spill", m=SDARK, ch=0.1)
    for s in (-1, 1):
        stone(mb, a[0] + nx * s * 1.75 + ux * 0.6, a[1] + ny * s * 1.75 + uy * 0.6, SPILL_TOP + 0.75, 52.8, 0.95, 0.7,
              math.atan2(uy, ux), ("spillcheek", s), m=SDARK, cap=MOSS, n=6)
    return n


# ------------------------------------------------------------------ 4. tsukubai (acento unico)
TSUKUBAI = (116.5, 290.6)       # margem oeste do canal, 4 ao sul da pontezinha: a ablucao antes de subir ao summon
BAMBOO = "Bamboo_DS_Dry"


def tsukubai(mb):
    """bacia de pedra natural baixa (chozubachi: rocha de 7 faces irregulares, mais larga embaixo, bacia escavada no
    topo com a agua parada num rebaixo escuro), pedra de pisar na frente (lado da clareira), 2 pedras de apoio; bica de
    bambu seco (kakehi) num esteio de bambu entre a bacia e o canal; o transbordo escorre por uma calha de pedra curta ate
    o canal. A agua parada da bacia e lida pela pedra escura (sem marcador)."""
    x, y = TSUKUBAI
    bm = mb.bm
    n = 7
    rr = [1.0 + 0.16 * (hh("tk", k) - 0.5) for k in range(n)]

    def ring(r, z, sx=1.0):
        return [bm.verts.new((x + r * rr[k] * sx * math.cos(0.35 + 2 * math.pi * k / n),
                              y + r * rr[k] * math.sin(0.35 + 2 * math.pi * k / n), z)) for k in range(n)]
    h = 0.92
    lo, mid = ring(1.12, T1 - 0.2, 1.08), ring(1.0, T1 + h - 0.2, 1.06)
    top, inn, deep = ring(0.84, T1 + h, 1.04), ring(0.5, T1 + h - 0.02, 1.0), ring(0.42, T1 + h - 0.3, 1.0)
    for k in range(n):
        j = (k + 1) % n
        bm.faces.new((lo[k], lo[j], mid[j], mid[k]))
        bm.faces.new((mid[k], mid[j], top[j], top[k]))
        bm.faces.new((top[k], top[j], inn[j], inn[k]))
        bm.faces.new((inn[k], inn[j], deep[j], deep[k]))
    mb._post(lo + mid + top + inn + deep, CLIFF, None, 0, 1)
    pool = ring(0.42, T1 + h - 0.3, 1.0)
    bm.faces.new(pool)
    mb._post(pool, SDARK, None, 0, 1)
    col_box("DS_WaterTsukubai", (2.2, 2.0, h + 0.3), (x, y, T1 + (h + 0.3) / 2 - 0.15))
    # pedra de pisar (mae-ishi) do lado da clareira e as 2 de apoio
    stone(mb, x - 2.05, y + 0.1, T1 + 0.36, T1 - 0.3, 0.9, 0.62, 0.15, "tk_mae", m=CLIFF, n=6, top_s=0.86)
    stone(mb, x - 0.45, y + 1.6, T1 + 0.55, T1 - 0.3, 0.55, 0.42, 0.9, "tk_te", m=CLIFF, n=5)
    stone(mb, x - 0.35, y - 1.55, T1 + 0.42, T1 - 0.3, 0.5, 0.4, -0.6, "tk_yu", m=CLIFF, n=5)
    # calha de transbordo (2 pedras baixas com fundo escuro) da bacia ate o muro do canal
    ex = 121.47 - CH_OUT - 0.05
    for s_ in (-1, 1):
        q = [(x + 0.8, y + s_ * 0.3), (ex, y + s_ * 0.3), (ex, y + s_ * 0.6), (x + 0.8, y + s_ * 0.6)]
        block(mb, ccw(q), T1 - 0.3, T1 + 0.56, ("tk_g", s_), m=STONE, ch=0.06)
    q = [(x + 0.8, y - 0.3), (ex, y - 0.3), (ex, y + 0.3), (x + 0.8, y + 0.3)]
    block(mb, ccw(q), T1 - 0.3, T1 + 0.32, "tk_gb", m=SDARK, ch=0.02)
    # kakehi: esteio de bambu seco (nos marcados por aneis, topo cortado) + bica que avanca sobre a bacia e desce um
    # pouco (a agua cai no meio da bacia), travada por um pino atravessado
    px, py = x + 1.4, y + 1.0
    mb.rod((px, py, T1 - 0.2), (px, py, T1 + 2.05), 0.2, BAMBOO, n=7, caps=True)
    for zz in (T1 + 0.7, T1 + 1.45):
        mb.cyl(0.23, 0.1, (px, py, zz), m=BAMBOO, n=7, bevel=0.0)
    sz = T1 + 1.78
    tip = (x + 0.05, y + 0.12, T1 + 1.52)
    mb.rod((px + 0.25, py + 0.12, sz + 0.06), tip, 0.13, BAMBOO, n=6, caps=True)
    mb.rod((px - 0.05, py - 0.35, sz - 0.05), (px - 0.05, py + 0.35, sz - 0.05), 0.05, BAMBOO, n=5)


# ------------------------------------------------------------------ marcadores (lidos pelo ds_core.fx_markers)
def _wp(pts):
    return ";".join("%.2f,%.2f,%.2f" % p for p in pts)


def _cascade_curtain():
    x = FALL_X
    return ([(x, LIP_EDGE[1], LIP_TOP + 0.14), (x, LIP_EDGE[1] - 0.25, 77.5), (x, 426.15, STEP[2] + 0.1),
             (x, STEP_FRONT - 0.05, STEP[2] - 0.2), (x, STEP_FRONT - 0.45, 66.0), (x, BASE[1], LEVEL)],
            [3.0, 3.6, 4.2, 4.6, 5.0, 5.6])     # ONDA 6b (item 42): era 2,6 .. 5,0


def _spill_curtain():
    x, y = SPILL_LIP
    return ([(x, y, SPILL_TOP + 0.12), (x + 0.7, y, SPILL_TOP - 1.4), (x + 1.2, y, 47.0), (x + 1.5, y, 38.0),
             (x + 1.7, y, 26.0), (x + 1.8, y, SPILL_BASE_Z)], [1.4, 1.5, 1.6, 1.8, 2.0, 2.3])


def _channel_path():
    """eixo da agua do canal + sangradouro (x, y, z) e larguras: da boca da lagoa ate a bica final; em cada soleira a
    lamina passa por cima (nivel do poco de cima) e o ponto seguinte, 0,6 adiante, ja esta no nivel do poco de baixo
    (painel curto e ingreme = queda curta)"""
    pts, ws = [], []
    for x, y in CHAN:
        pts.append((x, y, LEVEL))
        ws.append(2 * CH_IN)
    for k, (P, bed, lev) in enumerate(RAV):
        for j, (x, y) in enumerate(P):
            if k == 0 and j == 0:
                continue
            if k > 0 and j == 0:
                a, b, top = SILLS[k - 1]
                pts.append((b[0], b[1], RAV[k - 1][2]))
                ws.append(2 * RAV_IN)
                ux, uy = P[1][0] - x, P[1][1] - y
                ln = math.hypot(ux, uy)
                x, y = x + ux / ln * 0.6, y + uy / ln * 0.6
            pts.append((x, y, lev))
            ws.append(2 * RAV_IN)
    pts.append((SPILL_LIP[0], SPILL_LIP[1], SPILL_TOP + 0.12))
    ws.append(1.6)
    return pts, ws


def water_markers():
    """nome -> (posicao, rumo, props) dos FX_*/WATER_* da agua: as MESMAS constantes que desenham a pedra deste modulo.
    O ds_core.fx_markers aplica (por cima das estimativas da onda 0). WATER_Flume (aqueduto de madeira) e do ds_forge."""
    south = yaw_to(0, -1)
    cw, cws = _cascade_curtain()
    sw, sws = _spill_curtain()
    east = yaw_to(1.0, 0.0)
    cpts, cws2 = _channel_path()
    xs = [p[0] for p in POND_W]
    ys = [p[1] for p in POND_W]
    pc = (sum(xs) / len(xs), sum(ys) / len(ys))
    tail = extend_back(TAIL, TAIL_HEAD + 0.6)        # a agua comeca dentro do vao do poco da roda (ds_forge)
    tail_pts = [(x, y, LEVEL_T4) for x, y in tail[:-1]] + [(FALL_X, FACE_Y + 0.6, LEVEL_T4),
                                                         (FALL_X, LIP_EDGE[1], LIP_TOP + 0.14)]
    out = {
        "FX_Fall_1_Lip": ((FALL_X, LIP_EDGE[1], LIP_TOP), south, {
            "fx": "nevoa_borda", "kind": "bica", "width": 3.0, "drop": round(LIP_TOP - LEVEL, 2),
            "water_level_up": LEVEL_T4, "face_y_local": FACE_Y, "waypoints": _wp(cw),
            "widths": ",".join("%.1f" % w for w in cws),
            "note": "ponta da soleira de pedra escura (no nivel da PEDRA; a lamina de 0,28 corre por cima) entre as 2 "
                    "pedras-guarda do muro da forja; cortina medida: bica -> degrau de rocha (70,35) -> lagoa (60,32)"}),
        "FX_Fall_1_Step": ((FALL_X, STEP_FRONT, STEP[2]), south, {
            "fx": "espuma_degrau", "width": 4.6, "jump": 1.3,
            "note": "degrau de rocha no meio da queda: a cortina bate no topo e passa por cima da borda da frente"}),
        "FX_Fall_1_Base": ((BASE[0], BASE[1], LEVEL), south, {
            "fx": "nevoa_base", "width": 6.5, "level": LEVEL,
            "note": "pe da cascata na lagoa, entre as pedras grandes N1/N2"}),
        "FX_Fall_2_Lip": ((SPILL_LIP[0], SPILL_LIP[1], SPILL_TOP), east, {
            "fx": "nevoa_borda", "kind": "bica", "width": 1.4, "drop": round(SPILL_TOP - SPILL_BASE_Z, 2),
            "water_level_up": RAV[2][2], "waypoints": _wp(sw), "widths": ",".join("%.1f" % w for w in sws),
            "note": "sangradouro fino: ponta da bica em balanco na borda leste (ravina); unica queda para fora"}),
        "FX_Fall_2_Base": ((sw[-1][0], sw[-1][1], SPILL_BASE_Z), east, {
            "fx": "nevoa_base", "width": 3.2,
            "note": "a cortina some na nevoa (abaixo so o mar de nuvens); medida contra a quilha no build"}),
        "FX_Mist_Ravine": ((149.0, 229.8, 56.5), 0.0, {"fx": "nevoa_baixa", "radius": 14.0,
                                                        "note": "nevoa dos 3 pocos do sangradouro"}),
        "WATER_Pond": ((round(pc[0], 2), round(pc[1], 2), LEVEL), yaw_to(0, 1), {
            "shape": "poligono", "level": LEVEL, "floor": BED_T1, "depth": round(LEVEL - BED_T1, 2),
            "rim_min": round(COPE, 2), "sx": round(max(xs) - min(xs), 2), "sy": round(max(ys) - min(ys), 2),
            "waypoints": _wp([(x, y, LEVEL) for x, y in POND_W]),
            "mouth": "%.2f,%.2f;%.2f,%.2f" % (116.4, MOUTH_Y, 119.4, MOUTH_Y),
            "note": "contorno DESENHADO da agua (dentro do barranco e das pedras); a boca do canal fica fora (o canal "
                    "comeca na linha da boca)"}),
        "WATER_Tailrace": ((tail_pts[0][0], tail_pts[0][1], LEVEL_T4), 0.0, {
            "level": LEVEL_T4, "floor": BED_T4, "depth": round(LEVEL_T4 - BED_T4, 2), "rim": COPE_T4,
            "waypoints": _wp(tail_pts), "widths": ",".join("%.1f" % (2 * CH_IN) for _ in tail_pts[:-1]) + ",2.4",
            "note": "calha de cantaria do terraco da forja: cabeca em TAILRACE[0] (a agua da roda chega ali) -> bica "
                    "da cascata (o ultimo trecho desce para a soleira)"}),
        "WATER_Channel": ((cpts[0][0], cpts[0][1], LEVEL), 0.0, {
            "level": LEVEL, "floor": BED_T1, "depth": round(LEVEL - BED_T1, 2), "rim": COPE,
            "waypoints": _wp(cpts), "widths": ",".join("%.1f" % w for w in cws2),
            "pools": ";".join("%.2f/%.2f" % (lev, bed) for P, bed, lev in RAV),
            "note": "canal de cantaria pela margem leste da clareira (sob a pontezinha do summon) + sangradouro em 3 "
                    "pocos na ravina; os pares de pontos com cota diferente sao as soleiras (queda curta)"}),
    }
    return out


# ------------------------------------------------------------------ previa da agua (00_REFERENCE: fora do export)
def preview():
    pw = MB("PREVIEW_Water_DS", "00_REFERENCE", None, detail="far", floor=-999)
    pw.prism(ccw(POND_W), LEVEL - 0.25, LEVEL, "PREVIEW_Water")
    M = water_markers()

    def ribbon(pts, ws):
        for (a, b), w0, w1 in zip(zip(pts, pts[1:]), ws, ws[1:]):
            ax, ay, az = a
            bx, by, bz = b
            dx, dy = bx - ax, by - ay
            ln = math.hypot(dx, dy) or 1.0
            nx, ny = -dy / ln, dx / ln
            bm = pw.bm
            vs = [bm.verts.new((ax + nx * w0 / 2, ay + ny * w0 / 2, az)), bm.verts.new((ax - nx * w0 / 2, ay - ny * w0 / 2, az)),
                  bm.verts.new((bx - nx * w1 / 2, by - ny * w1 / 2, bz)), bm.verts.new((bx + nx * w1 / 2, by + ny * w1 / 2, bz))]
            bm.faces.new(vs)
            pw._post(vs, "PREVIEW_Water", None, 0, 1)

    def curtain(pts, ws, fwd):
        fx, fy = fwd
        for (a, b), w0, w1 in zip(zip(pts, pts[1:]), ws, ws[1:]):
            sx, sy = -fy, fx
            bm = pw.bm
            vs = [bm.verts.new((a[0] + sx * w0 / 2, a[1] + sy * w0 / 2, a[2])), bm.verts.new((a[0] - sx * w0 / 2, a[1] - sy * w0 / 2, a[2])),
                  bm.verts.new((b[0] - sx * w1 / 2, b[1] - sy * w1 / 2, b[2])), bm.verts.new((b[0] + sx * w1 / 2, b[1] + sy * w1 / 2, b[2]))]
            bm.faces.new(vs)
            pw._post(vs, "PREVIEW_Water", None, 0, 1)

    def parse(s):
        return [tuple(float(v) for v in p.split(",")) for p in s.split(";")]
    for nm in ("WATER_Tailrace", "WATER_Channel"):
        p = M[nm][2]
        ribbon(parse(p["waypoints"]), [float(w) for w in p["widths"].split(",")])
    for nm, fwd in (("FX_Fall_1_Lip", (0.0, -1.0)), ("FX_Fall_2_Lip", (1.0, 0.0))):
        p = M[nm][2]
        curtain(parse(p["waypoints"]), [float(w) for w in p["widths"].split(",")], fwd)
    ob = pw.finish()
    for o in (ob,):
        for poly in o.data.polygons:
            poly.use_smooth = False
    return ob


# ------------------------------------------------------------------ medida na cena (confere a pedra x marcadores)
def _bvh(prefixes, near, R):
    verts, polys = [], []
    for o in bpy.data.objects:
        if o.type != "MESH" or not o.name.startswith(prefixes):
            continue
        me = o.data
        mw = o.matrix_world
        base = len(verts)
        vs = [mw @ v.co for v in me.vertices]
        verts += vs
        for p in me.polygons:
            if any(math.hypot(vs[i].x - near[0], vs[i].y - near[1]) < R for i in p.vertices):
                polys.append([base + i for i in p.vertices])
    return BVHTree.FromPolygons(verts, polys) if polys else None


def measure():
    """raios na cena: topo da soleira da cascata, topo do degrau, folga da cortina na face do muro, leitos da lagoa e do
    canal, cortina do sangradouro contra a quilha. Imprime WATER MEDIDA ... e AVISO quando passa da tolerancia"""
    warn = 0
    own = _bvh(("DS_Water_",), (FALL_X, 420.0), 400.0)
    ter = _bvh(("DS_Ter_", "DS_Clr_"), (FALL_X, 400.0), 400.0)

    def down(t, x, y, z0=120.0):
        h = t.ray_cast(Vector((x, y, z0)), Vector((0, 0, -1)), 400.0) if t else (None,)
        return h[0].z if h[0] is not None else None

    def chk(lab, got, want, tol):
        nonlocal warn
        bad = got is None or abs(got - want) > tol
        warn += bad
        print("%s WATER MEDIDA %-34s %s (projeto %.2f)" % ("AVISO" if bad else "OK   ", lab,
                                                            "nada" if got is None else "%.2f" % got, want))
    chk("soleira da cascata (topo)", down(own, FALL_X, LIP_EDGE[1] + 0.4), LIP_TOP, 0.08)
    chk("degrau da cascata (topo, frente)", down(own, FALL_X, STEP_FRONT + 0.9, 75.0), STEP[2] - 0.2, 0.35)
    chk("leito da lagoa (terreno)", down(ter, 112.0, 404.0, 70.0), BED_T1, 0.06)
    chk("leito do canal sob a pontezinha", down(ter, 121.0, 300.0, 70.0), BED_T1, 0.06)
    chk("leito da calha (terreno)", down(ter, 113.0, 458.0, 90.0), BED_T4, 0.06)
    for k, (P, bed, lev) in enumerate(RAV):
        x, y = P[1]
        chk("leito do poco %d do sangradouro" % (k + 1), down(ter, x, y, lev + 1.0), bed, 0.2)
    chk("bica do sangradouro (topo)", down(own, SPILL_LIP[0] - 0.4, SPILL_LIP[1], 60.0), SPILL_TOP, 0.08)
    # cortina da cascata: folga horizontal ate a face do muro/degrau em cada cota (para dentro: +y)
    allb = [t for t in (own, ter) if t]
    worst = 99.0
    for x, y, z in _cascade_curtain()[0][1:-1]:
        for t in allb:
            h = t.ray_cast(Vector((x, y - 0.01, z - 0.3)), Vector((0, 1, 0)), 6.0)
            if h[0] is not None:
                worst = min(worst, h[0].y - y)
    print("%s WATER MEDIDA folga minima cortina 1 -> rocha atras: %.2f" % ("OK   " if worst >= 0.15 else "AVISO", worst))
    # sangradouro: cortina livre ate o pe (raio para baixo em cada largura)
    ter2 = _bvh(("DS_Ter_",), SPILL_LIP, 60.0)
    hit = None
    pts = _spill_curtain()[0]
    for (a, b) in zip(pts, pts[1:]):
        for s in (-0.7, 0.0, 0.7):
            o = Vector((a[0], a[1] + s, a[2] - 0.2))
            d = Vector((b[0] - a[0], b[1] - a[1], b[2] - a[2]))
            h = ter2.ray_cast(o, d.normalized(), d.length) if ter2 else (None,)
            if h[0] is not None and (hit is None or h[0].z > hit):
                hit = h[0].z
    print("%s WATER MEDIDA cortina do sangradouro bate em rocha: %s" % ("OK   " if hit is None else "AVISO",
                                                                         "nao (livre ate %.1f)" % SPILL_BASE_Z
                                                                         if hit is None else "z %.1f" % hit))
    warn += hit is not None
    return warn


# ------------------------------------------------------------------ build
def build():
    for o in [o for o in bpy.data.objects if o.name.startswith("PREVIEW_Water")]:
        bpy.data.objects.remove(o, do_unlink=True)
    global GROUND
    GROUND = Ground()
    # UM objeto so (a pedra da agua inteira): MeshParts = 1 por material (o export ainda fatia por celula de 128)
    mb = MB("DS_Water_Stone", C, None, detail="hero", floor=-999)
    n_tr = tailrace(mb)
    cascade(mb)
    pond(mb)
    n_ch = channel(mb)
    n_rv = ravine(mb)
    tsukubai(mb)
    mb.finish()
    preview()
    bpy.context.view_layer.update()
    w = measure()
    print("ds_water calha=%d blocos canal=%d blocos ravina=%d pecas medidas_com_aviso=%d" % (n_tr, n_ch, n_rv, w))
