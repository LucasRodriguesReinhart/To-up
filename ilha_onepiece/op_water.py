# op_water - ZONA WATER da Ilha 5 (ONE PIECE / WANO), M4. build() substitui op_blockout.water. Prefixo OP_Water_ (o
# dono "water" do export_op.ER.OWNERS / studio_op.OWNERS / op_lib.OWNER_PREFIX; o "OP_Wat_" do pedido nao existe na
# tabela de donos e cairia fora do orcamento), colecao 07_WATER; peca movel VFX_OP_Wheel (12_VFX_HELPERS,
# pivot/axis/rpm -> tag IlhaMovel no export, como o VFX_DS_Wheel da Ilha 4). Sem luz. Sem colisao: canais e bacia sao
# BURACOS entre pisos e a guarda invisivel das margens e do op_col.
#
# A AGUA e do Roblox (laminas com textura rolando, espelho em poligono, nevoa - o contrato da Ilha 4, ver
# ilha_demonslayer/roblox/DemonSlayerIsland.lua 'agua'), feita a partir dos marcadores FX_Fall_* / WATER_*. Aqui so a
# PEDRA que contem e explica a agua, contando UMA historia por bacia (planta: op_layout 'AGUA'):
#   1. CASTELO: nascente na boca escura do rochedo (op_terrain) -> labio de pedra (0; 350,6; 132,05) -> CACHOEIRA DO
#      CASTELO (34,5) -> 2 DEGRAUS DE ESPUMA de pedra molhada no pe (98,5 / 97,9) -> BACIA do adro (97,6; contorno da
#      planta + faixa ate o pe da rocha, apron submerso que fecha a fresta do terreno, soleira molhada no pe da rocha,
#      revestimento de cantaria sob a mureta do op_castle) -> boca -> CANAL LESTE (cantaria, 97,6) -> DEGRAU (3 x 2 em
#      x 90,6..95,2) -> canal (91,6) pelo pe do rochedo NE -> curva para o sul -> BICA da QUEDA LESTE (labio 91,3) ->
#      enseada do porto (mar local 36) entre pedras de base.
#   2. OESTE: BICA de pedra no arrimo do terraco alto (97,2) -> cabeceira do CANAL OESTE (91,6) -> sob as 2 pontes do
#      plano (y 182 / 252; ver PONTES abaixo) -> DEGRAU (2 x 2 em y 118..120,8) -> canal do bairro (87,6) -> RODA
#      D'AGUA do moinho S4 (undershot: as pas de baixo mergulham 1,7 na correnteza) -> BICA da QUEDA OESTE (87,3) ->
#      mar (falesia SO) entre pedras de base.
# COTAS (agua = piso - 0,6; leito do op_terrain = agua - 2,2; CAPA da cantaria = agua + 0,9 = piso + 0,3, ou piso do
#   vizinho + 0,3 onde a margem e mais alta): bacia 97,6 / leito 95,4 / mureta (op_castle) 97,9..99,7; canal leste 97,6
#   e 91,6 / leitos 95,4 e 89,4 / capas 98,5 e 92,5; canal oeste 91,6 e 87,6 / leitos 89,4 e 85,4 / capas 92,5 e 88,5.
#   => superficie >= 0,3 abaixo de qualquer borda (0,9 da capa) e leito 2,2 abaixo da superficie.
# MEDIDA NA CENA (classe Ground, raios no que os outros modulos ja montaram): a capa de cada pedra da margem avanca ate
#   o piso vizinho ou a face de rocha (fecha as FRESTAS que o terreno deixa entre o buraco do canal e o piso: ate 3 de
#   largura no canal leste) e a face de fora desce ate o chao medido; a altura da capa sobe com a margem.
# MARCADORES: o op_core cria os FX_*/WATER_* (M1, estimados) e chama water_markers() deste modulo (acrescimo pontual
#   op_core._water_measured, como na DS): valores = as MESMAS constantes que desenham a pedra; o build() ainda confere
#   por raios (labios, leitos, folga das cortinas) e imprime 'WATER MEDIDA'.
# PONTES: as 2 pontes vermelhas do canal oeste (L.bridge_list CanalS/CanalN, y 182 e 252) existem so como COLISAO
#   (op_col); o visual e da capital (op_capital, M4) e NAO e feito aqui. A capa do canal passa a 92,5 sob elas: o
#   tabuleiro visual tem de passar >= 92,6 na faixa |x + 174| <= 4,8.
# Fora (de proposito): cachoeiras extras, agua decorativa, minerio/cristal.
import math, zlib
import bmesh
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
import op_lib as DL
from op_lib import MB, ccw, camera, yaw_to
import op_layout as L

C = "07_WATER"
T1, P, CF, CC, SEA = L.T1, L.P, L.CF, L.CC, L.SEA
WALL, CAP, WET = "Stone_OP_Wall", "Stone_OP_Path", "Stone_OP_Dark"
RDARK, RCOOL, MOSS = "Cliff_OP_Dark", "Cliff_OP_Cool", "Cliff_OP_Moss"
WOODD, WOOD, IRON = "Wood_OP_Dark", "Wood_OP_Mid", "Metal_OP_Iron"

# ------------------------------------------------------------------ cotas
LV_CF, LV_P, LV_T1 = CF - 0.6, P - 0.6, T1 - 0.6     # 97,6 / 91,6 / 87,6
BED_D = 2.2                  # leito do op_terrain (agua - 2,2)
FREE = 0.9                   # capa = agua + 0,9
IN = 0.25                    # frente da cantaria: 0,25 para DENTRO da borda do buraco (junta/corpo a 0,15: as faces
JNT = 0.10                   #   laterais dos corpos do terreno ficam na borda -> folga >= 0,12, sem z-fight)
CAP_T, CAP_OV = 0.45, 0.22   # capa: espessura, pingadeira sobre a agua (M6b: 0,12 a frente das pedras, que avancaram)
STONE_FWD = 0.10             # M6b (item 43): pedras 0,10 a frente de d_in -> miolo escuro 0,20 atras (era 0,10)
CAP_MAX = 4.6                # alcance maximo da capa para fora (fecha a fresta ate o piso vizinho)

# ------------------------------------------------------------------ canais (eixo da PEDRA = eixo da planta)
XM = 19.6                    # a agua do canal leste comeca na linha x = 19,6 (a da bacia vai ate ela: sem 2 laminas)
LIP_E_Y = 297.2              # ponta da bica leste (0,8 alem da face da garganta, medida em y 298,0)
LIP_W_Y = 46.2               # ponta da bica oeste (0,8 alem da face medida em y 47,0)
FACE_E_Y, FACE_W_Y = 298.0, 47.0
HEAD_W_Y = 299.75            # cabeceira do canal oeste: face do arrimo do terraco alto (medida 299,66..299,73)
CANALS = {
    # nome: eixo (x, y), nivel por TRECHO, meia largura do buraco do terreno, quebras (coordenada ao longo do eixo)
    "E": dict(pts=[(XM, 342.0), (92.0, 342.0), (100.0, 342.0), (188.0, 343.0), (248.0, 343.0), (248.5, 304.0),
                   (248.5, FACE_E_Y)],
              lv=[LV_CF, LV_P, LV_P, LV_P, LV_P, LV_P], hw=3.0, brk=[(97.0, 342.0)]),
    "W": dict(pts=[(-174.0, HEAD_W_Y), (-174.0, 250.0), (-174.0, 182.0), (-174.0, 120.8), (-174.0, 114.0),
                   (-174.0, 92.0), (-174.0, 58.0), (-174.0, FACE_W_Y)],
              lv=[LV_P, LV_P, LV_P, LV_T1, LV_T1, LV_T1, LV_T1], hw=4.0, brk=[(-174.0, 117.5)]),
}
# degraus (sentido da correnteza): (canal, inicio do degrau ao longo do eixo, [(comprimento, topo), ...]); a agua de
# cima passa 0,3 acima da soleira; cada degrau tem 2 de queda
WEIR_E = dict(x0=90.6, steps=[(1.6, LV_CF - 0.3), (1.5, LV_CF - 2.3), (1.5, LV_CF - 4.3)], y=342.0)   # -> 95,2
WEIR_W = dict(y0=120.8, steps=[(1.4, LV_P - 0.3), (1.4, LV_P - 2.3)], x=-174.0)                         # -> 118,0

# ------------------------------------------------------------------ bacia do adro (L.BASIN = buraco do terreno)
LV_B = LV_CF
BASIN_BACK = 351.15          # a agua vai ate o pe da rocha (lajes da proa em y 351,1..351,7; o buraco do terreno para em 350)
FALL_X = 0.0
LIP_FRONT = 350.6            # frente do labio de pedra do op_terrain (box -4,2..4,2 / 350,6..357,6, topo 132,05)
LIP_TOP = 132.05
STEP_A = dict(x=5.0, y0=348.6, y1=351.3, top=LV_B + 0.9)      # degrau de espuma de cima (98,5): a cortina bate aqui
STEP_B = dict(x=7.2, y0=346.5, y1=349.0, top=LV_B + 0.3)      # degrau de baixo (97,9): espalha e cai na bacia
MOUTH = ((19.0, 339.0), (18.3, 345.0))                         # boca do canal leste na borda da bacia (planta)
# marcos da boca: centrados nas pontas da mureta do op_castle (linha 0,65 fora da bacia, cortada em y 338,6 / 345,6,
# + 0,55 de prolongamento) -> as pontas da mureta e o comeco das margens do canal ficam DENTRO deles
MOUTH_POSTS = [((19.85, 338.55), 0.9), ((19.35, 345.75), 0.85)]

# ------------------------------------------------------------------ roda d'agua (moinho S4)
WX, WY = L.WHEEL[0], L.WHEEL[1]
WD, WW = L.WHEEL[2], L.WHEEL[3]
WR = WD / 2.0
AXZ = LV_T1 + WR - 1.7       # 92,4: as pas de baixo mergulham 1,7 (planta: T1 + 3,4 = 91,6 batia no leito 85,4)
RPM = 4.0
SUPPORT_X = (-178.9, -169.1)   # cavaletes sobre as capas oeste/leste

# ------------------------------------------------------------------ bica do arrimo (nascente do canal oeste)
SPRING = (-174.0, 298.3, L.SPRING_W[2])     # ponta da bica (1,4 a frente da face do arrimo), z 97,2


def _fmix(h):
    h ^= h >> 16
    h = (h * 0x85EBCA6B) & 0xFFFFFFFF
    h ^= h >> 13
    h = (h * 0xC2B2AE35) & 0xFFFFFFFF
    h ^= h >> 16
    return h


def hh(*a):
    s = "|".join(("%.2f" % v) if isinstance(v, float) else str(v) for v in a)
    return _fmix(zlib.crc32(s.encode("utf-8")) ^ 0x9E3779B9) / 4294967296.0


# ------------------------------------------------------------------ medida na cena
class Ground:
    """BVH do que os OUTROS modulos montaram (terreno, castelo, capital...): margens, frestas, faces de rocha"""

    def __init__(self):
        verts, polys = [], []
        for o in bpy.data.objects:
            if o.type != "MESH" or not o.name.startswith(("OP_", "GATE_")):
                continue
            if o.name.startswith(("OP_Water_", "OP_Plz_OreProxy")):
                continue
            if o.users_collection and o.users_collection[0].name in ("00_REFERENCE", "_SCALE_REFERENCE"):
                continue
            mw = o.matrix_world
            b = len(verts)
            verts += [mw @ v.co for v in o.data.vertices]
            polys += [[b + i for i in p.vertices] for p in o.data.polygons]
        self.t = BVHTree.FromPolygons(verts, polys)

    def down(self, x, y, z0, maxd=80.0):
        h = self.t.ray_cast(Vector((x, y, z0)), Vector((0.0, 0.0, -1.0)), maxd)
        return None if h[0] is None else h[0].z

    def dist(self, o, d, maxd):
        d = Vector(d).normalized()
        h = self.t.ray_cast(Vector(o), d, maxd)
        return None if h[0] is None else h[3]


GROUND = None
FACES = {}          # (id(mb), material) -> [faces]


def face(mb, pts, m, want):
    """face plana com a normal virada para 'want'; material explicito (sem sorteio de variante)"""
    bm = mb.bm
    try:
        f = bm.faces.new([bm.verts.new(p) for p in pts])
    except ValueError:
        return None
    f.normal_update()
    if Vector(want).dot(f.normal) < 0.0:
        f.normal_flip()
    FACES.setdefault((id(mb), m), []).append(f)
    return f


def flush(mb):
    for (k, m), fl in list(FACES.items()):
        if k != id(mb):
            continue
        mi = mb._mi(m)
        fl = [f for f in fl if f.is_valid]
        for f in fl:
            f.material_index = mi
            f[mb.tint] = 0.0
            f.smooth = False
        mb._uv(fl, m)
        del FACES[(k, m)]


def box(mb, x0, x1, y0, y1, z0, z1, m, top=None, bottom=False):
    """caixa alinhada (faces explicitas; topo com material proprio opcional; fundo so se pedido)"""
    p = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    face(mb, [(x, y, z1) for x, y in p], top or m, (0, 0, 1))
    if bottom:
        face(mb, [(x, y, z0) for x, y in p], m, (0, 0, -1))
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    for k in range(4):
        a, b = p[k], p[(k + 1) % 4]
        mx, my = (a[0] + b[0]) / 2 - cx, (a[1] + b[1]) / 2 - cy
        face(mb, [(a[0], a[1], z0), (b[0], b[1], z0), (b[0], b[1], z1), (a[0], a[1], z1)], m, (mx, my, 0))


def prism(mb, poly, z0, z1, m, top=None, bottom=False):
    pl = ccw(poly)
    face(mb, [(x, y, z1) for x, y in pl], top or m, (0, 0, 1))
    if bottom:
        face(mb, [(x, y, z0) for x, y in pl], m, (0, 0, -1))
    n = len(pl)
    for i in range(n):
        a, b = pl[i], pl[(i + 1) % n]
        dx, dy = b[0] - a[0], b[1] - a[1]
        face(mb, [(a[0], a[1], z0), (b[0], b[1], z0), (b[0], b[1], z1), (a[0], a[1], z1)], m, (dy, -dx, 0))


def chamfer_rect(x0, x1, y0, y1, c):
    return [(x0 + c, y0), (x1 - c, y0), (x1, y0 + c), (x1, y1 - c), (x1 - c, y1), (x0 + c, y1), (x0, y1 - c),
            (x0, y0 + c)]


# ------------------------------------------------------------------ eixo dos canais (quinas em meia-esquadria)
class Axis:
    def __init__(self, pts):
        self.v = [Vector((x, y, 0.0)) for x, y in pts]
        self.seg = []
        for a, b in zip(self.v, self.v[1:]):
            d = b - a
            ln = d.length
            u = d / ln
            self.seg.append((a, b, u, Vector((-u.y, u.x, 0.0)), ln))
        # meia-esquadria (normal ESQUERDA) em cada vertice interno
        self.mit = [None] * len(self.v)
        for i in range(1, len(self.v) - 1):
            na, nb = self.seg[i - 1][3], self.seg[i][3]
            d = 1.0 + na.dot(nb)
            self.mit[i] = (na + nb) / d if na.dot(nb) < 0.99999 else None

    def pt(self, i, s, o, z):
        a, b, u, n, ln = self.seg[i]
        if s <= 1e-6 and self.mit[i] is not None:
            p = a + self.mit[i] * o
        elif s >= ln - 1e-6 and self.mit[i + 1] is not None:
            p = b + self.mit[i + 1] * o
        else:
            p = a + u * s + n * o
        return (p.x, p.y, z)


def _pieces(ln, key, cuts):
    """quebra [0, ln] em pedras de 4..6,5 (comprimento DIRIGIDO), respeitando as quebras obrigatorias"""
    marks = sorted(set([0.0, ln] + [c for c in cuts if 0.5 < c < ln - 0.5]))
    out = []
    for a, b in zip(marks, marks[1:]):
        n = max(1, int(round((b - a) / 5.2)))
        ws = [0.75 + 0.5 * hh(key, a, k) for k in range(n)]
        tot = sum(ws)
        s = a
        for w in ws:
            e = s + (b - a) * w / tot
            out.append((s, e))
            s = e
        out[-1] = (out[-1][0], b)
    return out


def _measure_side(ax, i, s, side, hw, lv):
    """margem de UM lado num ponto do eixo: (alcance da capa para fora, cota da margem ou None, chao de fora)"""
    a, b, u, n, ln = ax.seg[i]
    nn = n * side
    base = a + u * s
    top0 = lv + FREE
    o_face, zface = None, None
    dh = GROUND.dist((base.x + nn.x * (hw - 0.4), base.y + nn.y * (hw - 0.4), top0 - 0.15), (nn.x, nn.y, 0.0),
                     CAP_MAX + 0.6)
    if dh is not None:
        o_face = hw - 0.4 + dh + 0.3
        # margem um pouco mais alta que a capa (rocha/berma ate +2,5): o muro do canal sobe ate ela (arrimo continuo);
        # face de rocha alta (rochedo NE, casas): a capa so encosta
        zf = GROUND.down(base.x + nn.x * (o_face + 0.3), base.y + nn.y * (o_face + 0.3), top0 + 3.0, 8.0)
        if zf is not None and top0 - 0.25 < zf <= top0 + 2.5:
            zface = zf
    o_bank, zbank = None, None
    d = hw + 0.25
    while d <= hw + CAP_MAX + 1e-6:
        z = GROUND.down(base.x + nn.x * d, base.y + nn.y * d, top0 + 0.5, 30.0)
        if z is not None and lv + 0.35 <= z <= top0 + 0.5:
            o_bank, zbank = d + 0.35, z
            break
        d += 0.25
    cands = [o for o in (o_face, o_bank) if o is not None]
    if cands:
        o_out = min(min(cands), hw + CAP_MAX)
        if o_face is not None and o_face == min(cands):
            zbank = zface if o_bank is None or o_bank > o_face else zbank
    else:
        o_out = hw + 1.4
    zg = GROUND.down(base.x + nn.x * (o_out + 0.25), base.y + nn.y * (o_out + 0.25), top0 + 0.5, 30.0)
    return o_out, zbank, zg


def canal_walls(mb, name):
    """margens de cantaria dos 2 lados: corpo/junta escuro molhado do leito ate a capa, fiada de pedras aparelhadas
    acima da linha d'agua, capa clara com pingadeira que avanca ate o piso vizinho, face de fora ate o chao medido"""
    spec = CANALS[name]
    ax = Axis(spec["pts"])
    hw = spec["hw"]
    d_in = hw - IN
    nseg = len(ax.seg)
    runs = {}          # (lado) -> lista de pedras (i, s0, s1, o_out, top, zg, lv)
    for side in (1, -1):
        out = []
        for i in range(nseg):
            a, b, u, n, ln = ax.seg[i]
            lv = spec["lv"][i]
            cuts = []
            for bx, by in spec["brk"]:
                t = (Vector((bx, by, 0.0)) - a).dot(u)
                if 0.0 < t < ln and abs((Vector((bx, by, 0.0)) - a).dot(n)) < 0.5:
                    cuts.append(t)
            for s0, s1 in _pieces(ln, "%s%d%d" % (name, side, i), cuts):
                oo, tops, zgs = [], [], []
                for f in (0.12, 0.5, 0.88):
                    o_out, zb, zg = _measure_side(ax, i, s0 + (s1 - s0) * f, side, hw, lv)
                    oo.append(o_out)
                    if zb is not None:
                        tops.append(zb + 0.3)
                    zgs.append(zg if zg is not None else lv - BED_D - 0.3)
                top = lv + FREE
                if tops and max(tops) > top + 0.25:
                    top = round(max(tops) / 0.05) * 0.05
                zg = min(max(z, lv - BED_D - 0.3) for z in zgs)
                out.append([i, s0, s1, max(oo), top, zg, lv])
        # capa sem dente: uma pedra mais estreita (ou mais baixa) que as 2 vizinhas acompanha a menor delas; alcance em
        # passos de 0,25
        for col in (3, 4):
            for k in range(1, len(out) - 1):
                if out[k - 1][6] == out[k][6] == out[k + 1][6]:
                    out[k][col] = max(out[k][col], min(out[k - 1][col], out[k + 1][col]))
        for p in out:
            p[3] = math.ceil(p[3] / 0.25 - 1e-6) * 0.25
        # quina em meia-esquadria: as 2 pedras que se encontram no vertice usam o MESMO alcance
        for k in range(len(out) - 1):
            p, q = out[k], out[k + 1]
            if p[0] != q[0] and ax.mit[q[0]] is not None:
                p[3] = q[3] = max(p[3], q[3])
        # M6b: a capa nao pode deitar RENTE (+-0,12) sobre um piso vizinho da mesma cota (quintal de terra do bairro a
        # 88,5 = capa: z-fight 0,0) -> recua o alcance ate a borda desse piso
        for p in out:
            i, s0, s1 = p[0], p[1], p[2]
            a_, b_, u_, n_, ln_ = ax.seg[i]
            nn_ = n_ * side
            while p[3] > hw + 0.5:
                hit = False
                for f in (0.1, 0.5, 0.9):
                    base = a_ + u_ * (s0 + (s1 - s0) * f)
                    for o in (p[3] - 0.1, p[3] - 0.45):
                        z = GROUND.down(base.x + nn_.x * o, base.y + nn_.y * o, p[4] + 0.6, 1.2)
                        if z is not None and abs(z - p[4]) < 0.12:
                            hit = True
                if not hit:
                    break
                p[3] -= 0.25
        runs[side] = out
    n_st = 0
    for side, out in runs.items():
        for k, (i, s0, s1, o_out, top, zg, lv) in enumerate(out):
            prev = out[k - 1] if k > 0 else None
            nxt = out[k + 1] if k + 1 < len(out) else None
            stone_piece(mb, ax, name, side, i, s0, s1, d_in, o_out, top, zg, lv, prev, nxt)
            n_st += 1
    return n_st


def stone_piece(mb, ax, name, side, i, s0, s1, d_in, o_out, top, zg, lv, prev, nxt):
    a, b, u, n, ln = ax.seg[i]
    nn = n * side
    win = (-nn.x, -nn.y, 0.0)             # para a agua
    wout = (nn.x, nn.y, 0.0)
    bed = lv - BED_D
    zb = bed - 0.3
    zc0 = top - CAP_T
    P_ = lambda s, o, z: ax.pt(i, s, o * side, z)
    oj = d_in + JNT
    oc = d_in - CAP_OV
    # corpo / junta (plano escuro molhado): do leito ate a capa. M6b: onde a face do terreno ja esta a < 0,15 do plano
    # da junta (canal leste x 39..45: 0,025), ela e o fundo da junta -> sem o plano escuro (z-fight)
    near = False
    for f in (0.15, 0.5, 0.85):
        q = Vector(P_(s0 + (s1 - s0) * f, 0.0, lv + 0.4))
        dd = GROUND.dist(q, wout, d_in + 2.0)
        if dd is not None and oj - 0.25 < dd < oj + 0.12:
            near = True
    if not near:
        face(mb, [P_(s0, oj, zb), P_(s1, oj, zb), P_(s1, oj, zc0), P_(s0, oj, zc0)], WET, win)
    # fiadas de pedra aparelhada acima da agua (da linha d'agua - 0,25 ate a capa)
    za = lv - 0.25
    if zc0 - za > 0.3:
        rows = max(1, int(round((zc0 - za) / 1.1)))
        hs = [0.8 + 0.4 * hh(name, side, i, round(s0, 1), r, "h") for r in range(rows)]
        tot = sum(hs)
        z = za
        for r in range(rows):
            z1 = zc0 if r == rows - 1 else z + (zc0 - za) * hs[r] / tot
            s = s0 - (0.0 if r % 2 == 0 else 0.9 * hh(name, side, i, round(s0, 1), r, "o"))
            q = 0
            while s < s1 - 0.05:
                w = 1.9 + 1.9 * hh(name, side, i, round(s0, 1), r, q, "w")
                e = min(s + w, s1)
                if s1 - e < 0.9:
                    e = s1
                sa = max(s, s0) + (0.07 if s > s0 + 0.01 or prev is not None else 0.0)
                sb = e - (0.07 if e < s1 - 0.01 or nxt is not None else 0.0)
                if sb - sa > 0.3:
                    oz = d_in - STONE_FWD + 0.03 * (hh(name, side, i, round(s0, 1), r, q, "f") - 0.5)
                    za_, zz = z + (0.06 if r > 0 else 0.0), z1 - 0.05
                    face(mb, [P_(sa, oz, za_), P_(sb, oz, za_), P_(sb, oz, zz), P_(sa, oz, zz)], WALL, win)
                    ud = (u.x, u.y, 0.0)
                    face(mb, [P_(sb, oz, za_), P_(sb, oj, za_), P_(sb, oj, zz), P_(sb, oz, zz)], WALL, ud)
                    face(mb, [P_(sa, oz, za_), P_(sa, oj, za_), P_(sa, oj, zz), P_(sa, oz, zz)], WALL, (-u.x, -u.y, 0))
                    if r > 0:
                        face(mb, [P_(sa, oz, za_), P_(sb, oz, za_), P_(sb, oj, za_), P_(sa, oj, za_)], WALL, (0, 0, -1))
                s = e
                q += 1
            z = z1
    # capa: frente (pingadeira), topo, barriga da pingadeira, face de fora ate o chao medido
    face(mb, [P_(s0, oc, zc0), P_(s1, oc, zc0), P_(s1, oc, top), P_(s0, oc, top)], CAP, win)
    face(mb, [P_(s0, oc, top), P_(s1, oc, top), P_(s1, o_out, top), P_(s0, o_out, top)], CAP, (0, 0, 1))
    face(mb, [P_(s0, oc, zc0), P_(s1, oc, zc0), P_(s1, oj, zc0), P_(s0, oj, zc0)], CAP, (0, 0, -1))
    zo = min(zg - 0.25, zc0)
    face(mb, [P_(s0, o_out, zo), P_(s1, o_out, zo), P_(s1, o_out, top), P_(s0, o_out, top)], WALL, wout)
    # tampas das pontas: onde a vizinha nao cobre (fim de trecho, degrau de capa, alcance diferente, ponta da bica)
    ud = Vector((u.x, u.y, 0.0))
    for s_, nb, sg in ((s0, prev, -1.0), (s1, nxt, 1.0)):
        if nb is not None and nb[0] != i and ax.mit[max(nb[0], i)] is not None:
            continue                        # meia-esquadria: a vizinha encosta face a face
        if nb is not None and abs(nb[4] - top) < 0.01 and abs(nb[3] - o_out) < 0.01 and abs(nb[6] - lv) < 0.01:
            continue
        lo = zb if nb is None or nb[6] != lv else min(zo, zc0)
        if nb is not None and nb[4] > top + 0.01:
            continue                        # a vizinha e mais alta: a tampa dela cobre
        w = (ud.x * sg, ud.y * sg, 0.0)
        face(mb, [P_(s_, oc, zc0), P_(s_, oj, zc0), P_(s_, oj, top), P_(s_, oc, top)], CAP, w)
        face(mb, [P_(s_, oj, lo), P_(s_, o_out, lo), P_(s_, o_out, top), P_(s_, oj, top)], WALL, w)


# ------------------------------------------------------------------ degraus (soleira + quedas curtas)
def weirs(mb):
    # leste: correnteza +x; os blocos encostam nas juntas dos 2 lados (y 339,15 / 344,85)
    y0, y1 = 342.0 - (3.0 - IN - JNT) - 0.04, 342.0 + (3.0 - IN - JNT) + 0.04
    x = WEIR_E["x0"]
    for k, (ln, top) in enumerate(WEIR_E["steps"]):
        box(mb, x, x + ln, y0, y1, LV_P - BED_D - 0.3, top, WET)
        # pingadeira escura na frente do degrau (aresta que a lamina contorna)
        x += ln
    # oeste: correnteza -y
    x0, x1 = -174.0 - (4.0 - IN - JNT) - 0.04, -174.0 + (4.0 - IN - JNT) + 0.04
    y = WEIR_W["y0"]
    for k, (ln, top) in enumerate(WEIR_W["steps"]):
        box(mb, x0, x1, y - ln, y, LV_T1 - BED_D - 0.3, top, WET)
        y -= ln


# ------------------------------------------------------------------ bicas das quedas da borda + cabeceira
def lips(mb):
    # OESTE: soleira (topo 87,3) em balanco 0,8 alem da face da garganta + 2 bochechas
    hw = 4.0 - IN - JNT
    box(mb, -174.0 - hw - 0.04, -174.0 + hw + 0.04, LIP_W_Y, FACE_W_Y + 4.6, LV_T1 - BED_D - 0.3, LV_T1 - 0.3, WET,
        bottom=True)
    for s in (-1, 1):
        xa = -174.0 + s * (hw - 0.25)      # M6b: bochecha 0,13 a frente da pingadeira da capa (era 0,07 atras: z-fight)
        xb = -174.0 + s * (hw + 1.7)
        box(mb, min(xa, xb), max(xa, xb), LIP_W_Y - 0.1, FACE_W_Y + 1.8, LV_T1 - BED_D - 0.6, LV_T1 + FREE + 0.2, WALL,
            top=CAP, bottom=True)
    # LESTE: soleira (91,3) + bochechas
    hw = 3.0 - IN - JNT
    box(mb, 248.5 - hw - 0.04, 248.5 + hw + 0.04, LIP_E_Y, FACE_E_Y + 4.0, LV_P - BED_D - 0.3, LV_P - 0.3, WET,
        bottom=True)
    for s in (-1, 1):
        xa = 248.5 + s * (hw - 0.25)       # M6b: idem (bochecha a frente da capa)
        xb = 248.5 + s * (hw + 1.6)
        box(mb, min(xa, xb), max(xa, xb), LIP_E_Y - 0.1, FACE_E_Y + 1.6, LV_P - BED_D - 0.6, LV_P + FREE + 0.2, WALL,
            top=CAP, bottom=True)
    # CABECEIRA do canal oeste: bloco submerso que fecha a fresta entre o buraco (299) e o arrimo (299,7)
    hw = 4.0 - IN - JNT
    box(mb, -174.0 - hw - 0.04, -174.0 + hw + 0.04, 298.9, HEAD_W_Y + 0.25, LV_P - BED_D - 0.3, LV_P - 0.35, WET)
    # BOCA do canal leste na bacia (mesmo nivel: sem soleira): 2 marcos de pedra que terminam a mureta do op_castle e
    # as margens do canal no mesmo gesto (sem pontas soltas de capa e mureta se cruzando na quina)
    for (cx, cy), r in MOUTH_POSTS:
        box(mb, cx - r, cx + r, cy - r, cy + r, LV_B - BED_D - 0.3, CF + 1.75, WALL, top=CAP)
        box(mb, cx - r - 0.15, cx + r + 0.15, cy - r - 0.15, cy + r + 0.15, CF + 1.75, CF + 2.1, CAP, bottom=True)
        box(mb, cx - r + 0.3, cx + r - 0.3, cy - r + 0.3, cy + r - 0.3, CF + 2.1, CF + 2.4, CAP)


def spring(mb):
    """bica de pedra no arrimo do terraco alto: moldura de pedra clara saliente + nicho escuro + bica com canaleta"""
    x, y, z = SPRING
    yf = HEAD_W_Y - 0.05           # face do arrimo
    # moldura (0,4 a frente da face) e nicho escuro recuado 0,2 dentro dela
    box(mb, x - 1.7, x + 1.7, yf - 0.4, yf + 0.25, z - 1.1, z + 1.9, CAP)
    face(mb, [(x - 1.05, yf - 0.53, z - 0.25), (x + 1.05, yf - 0.53, z - 0.25), (x + 1.05, yf - 0.53, z + 1.25),
              (x - 1.05, yf - 0.53, z + 1.25)], RDARK, (0, -1, 0))     # M6b: 0,13 a frente da moldura (era 0,02)
    # testeira da moldura (verga) mais saliente
    box(mb, x - 2.0, x + 2.0, yf - 0.6, yf + 0.2, z + 1.9, z + 2.35, CAP)
    # bica: calha de pedra em balanco (fundo + 2 abas), sai do nicho
    box(mb, x - 0.55, x + 0.55, y, yf - 0.3, z - 0.55, z - 0.15, WALL, bottom=True)
    for s in (-1, 1):
        box(mb, x + s * 0.55 - (0.18 if s > 0 else 0.0), x + s * 0.55 + (0.0 if s > 0 else 0.18), y, yf - 0.3,
            z - 0.15, z + 0.12, WALL, bottom=True)
    # pedra de apoio da bica (consola) sob ela
    box(mb, x - 0.45, x + 0.45, y + 0.5, yf - 0.3, z - 1.05, z - 0.55, WALL, bottom=True)


# ------------------------------------------------------------------ bacia do adro
def basin(mb):
    B = ccw(L.BASIN)
    n = len(B)
    TOPL = LV_B + 0.28                  # revestimento ate 97,88 (a mureta do op_castle comeca em 97,9)
    zb = LV_B - BED_D - 0.3
    nl = 0
    for k in range(n):
        a, b = Vector((*B[k], 0.0)), Vector((*B[(k + 1) % n], 0.0))
        if min(a.y, b.y) > 349.0:
            continue                    # lado da rocha: apron + degraus
        d = b - a
        ln = d.length
        u = d / ln
        no = Vector((u.y, -u.x, 0.0))   # para FORA (anti-horario)
        # boca do canal leste: corta y 339..345 nas 2 arestas do lado leste
        spans = [(0.0, ln)]
        if a.x > 15.0 or b.x > 15.0:
            ys = sorted((MOUTH[0][1] - 0.15, MOUTH[1][1] + 0.15))
            if abs(d.y) > 1e-3:
                t0 = (ys[0] - a.y) / d.y * ln
                t1 = (ys[1] - a.y) / d.y * ln
                lo_, hi_ = sorted((t0, t1))
                spans = [(s0, s1) for s0, s1 in ((0.0, min(lo_, ln)), (max(hi_, 0.0), ln)) if s1 - s0 > 0.3]
        for s0, s1 in spans:
            P_ = lambda s, o, z: tuple(a + u * s + no * o) [:2] + (z,)
            wi = (-no.x, -no.y, 0.0)
            # corpo/junta e fiada (frente 0,25 dentro do buraco), capa = a mureta do castelo
            oj, oz = -IN + JNT, -IN - STONE_FWD        # M6b (item 43): pedras 0,20 a frente do miolo
            face(mb, [P_(s0, oj, zb), P_(s1, oj, zb), P_(s1, oj, TOPL), P_(s0, oj, TOPL)], WET, wi)
            s = s0
            q = 0
            while s < s1 - 0.05:
                w = 1.8 + 1.6 * hh("basin", k, q)
                e = min(s + w, s1)
                if s1 - e < 0.8:
                    e = s1
                sa, sb = s + (0.07 if s > s0 else 0.0), e - (0.07 if e < s1 else 0.0)
                za_ = LV_B - 0.25
                face(mb, [P_(sa, oz, za_), P_(sb, oz, za_), P_(sb, oz, TOPL), P_(sa, oz, TOPL)], WALL, wi)
                for s_, sg in ((sa, -1), (sb, 1)):
                    face(mb, [P_(s_, oz, za_), P_(s_, oj, za_), P_(s_, oj, TOPL), P_(s_, oz, TOPL)], WALL,
                         (u.x * sg, u.y * sg, 0))
                face(mb, [P_(sa, oz, TOPL), P_(sb, oz, TOPL), P_(sb, oj, TOPL), P_(sa, oj, TOPL)], WALL, (0, 0, 1))
                s = e
                q += 1
            # tampo escondido sob o piso/mureta: fecha as frestas do terreno ate +1,3 para fora
            # M6b: ate +1,1 (a face de fora em +1,3 ficava 0,1 da face da mureta nova do adro, op_castle)
            face(mb, [P_(s0, oj, TOPL), P_(s1, oj, TOPL), P_(s1, 1.1, TOPL), P_(s0, 1.1, TOPL)], WALL, (0, 0, 1))
            face(mb, [P_(s0, 1.1, zb), P_(s1, 1.1, zb), P_(s1, 1.1, TOPL), P_(s0, 1.1, TOPL)], WALL, tuple(no))
            nl += 1
    # APRON submerso no fundo (fecha a fresta 350..351,3 entre o buraco e a rocha) - topo 0,7 abaixo da agua
    ap = [(-13.6, 348.9), (13.6, 348.9), (13.0, 351.9), (-13.0, 351.9)]
    prism(mb, ap, zb, LV_B - 0.7, WET)
    # soleira molhada no pe das lajes da proa (cobre a fresta entre a agua e a face; 0,15 acima da agua)
    for s in (-1, 1):
        xa, xb = s * 5.4, s * 12.95
        box(mb, min(xa, xb), max(xa, xb), BASIN_BACK - 0.15, 351.95, zb, LV_B + 0.15, WET)
    # DEGRAUS DE ESPUMA (a cortina bate no de cima, espalha e cai no de baixo e na bacia)
    sa, sb = STEP_A, STEP_B
    prism(mb, chamfer_rect(-sb["x"], sb["x"], sb["y0"], sb["y1"], 1.1), zb, sb["top"], WET)
    prism(mb, chamfer_rect(-sa["x"], sa["x"], sa["y0"], sa["y1"] + 1.2, 0.7), zb, sa["top"], WET)
    return nl


def rocks(mb):
    """pedras de base: pe das 2 quedas da borda no mar (36) e flancos do pe da cachoeira do castelo"""
    n = 0
    sets = [
        # (x, y, raio x, raio y, z base, z topo, material, chave)
        (-180.6, 43.6, 4.6, 3.6, 30.0, 40.6, RDARK, "w1"), (-167.4, 43.0, 4.0, 3.4, 30.0, 39.6, RDARK, "w2"),
        (-174.4, 40.4, 2.6, 2.0, 31.0, 37.2, RDARK, "w3"), (-186.0, 48.0, 3.6, 3.2, 30.0, 42.8, RCOOL, "w4"),
        (-162.2, 46.6, 3.2, 2.8, 30.0, 41.4, RCOOL, "w5"), (-177.8, 37.8, 1.8, 1.5, 31.0, 36.7, RDARK, "w6"),
        (242.4, 294.2, 3.6, 3.0, 30.0, 39.8, RDARK, "e1"), (254.8, 293.8, 3.8, 3.1, 30.0, 40.4, RDARK, "e2"),
        (248.6, 291.6, 2.3, 1.8, 31.0, 37.0, RDARK, "e3"), (237.8, 297.6, 3.0, 2.6, 30.0, 42.2, RCOOL, "e4"),
        (259.6, 297.0, 2.6, 2.3, 30.0, 41.0, RCOOL, "e5"),
        (-9.8, 348.6, 2.2, 1.7, LV_B - 2.4, LV_B + 1.15, RDARK, "c1"), (10.4, 349.0, 2.0, 1.6, LV_B - 2.4, LV_B + 0.85,
                                                                           RDARK, "c2"),
        (-6.6, 345.2, 1.1, 0.9, LV_B - 2.4, LV_B + 0.22, RDARK, "c3"),     # M6b (item 44): pe 0,2 enterrado no leito
    ]
    for x, y, rx, ry, z0, z1, m, key in sets:
        rock(mb, x, y, rx, ry, z0, z1, m, key)
        n += 1
    return n


def rock(mb, x, y, rx, ry, z0, z1, m, key, k=7):
    """pedra facetada: 3 aneis (pe largo, ombro, topo achatado) de k lados com raio/rumo DIRIGIDOS; topo com musgo so
    nas pedras secas (acima de 39)"""
    bm = mb.bm
    rot = 2 * math.pi * hh(key, "r")
    h = z1 - z0
    rings = [(1.0, z0), (0.92 + 0.08 * hh(key, "a"), z0 + h * 0.55), (0.55 + 0.15 * hh(key, "b"), z1 - h * 0.08),
             (0.0, z1)]
    vs = []
    for j, (sc, z) in enumerate(rings[:-1]):
        row = []
        for i in range(k):
            a = rot + 2 * math.pi * i / k
            f = sc * (0.82 + 0.3 * hh(key, j, i))
            row.append(bm.verts.new((x + math.cos(a) * rx * f, y + math.sin(a) * ry * f, z + (hh(key, j, i, "z") - 0.5)
                                     * h * 0.08 * (j > 0))))
        vs.append(row)
    top = bm.verts.new((x + (hh(key, "tx") - 0.5) * rx * 0.3, y + (hh(key, "ty") - 0.5) * ry * 0.3, z1))
    fl = []
    for j in range(len(vs) - 1):
        for i in range(k):
            q = (vs[j][i], vs[j][(i + 1) % k], vs[j + 1][(i + 1) % k], vs[j + 1][i])
            try:
                fl.append(bm.faces.new(q))
            except ValueError:
                pass
    tf = []
    for i in range(k):
        try:
            tf.append(bm.faces.new((vs[-1][i], vs[-1][(i + 1) % k], top)))
        except ValueError:
            pass
    for f in fl + tf:
        f.normal_update()
        c = f.calc_center_median()
        if (c - Vector((x, y, c.z))).dot(f.normal) < 0 and abs(f.normal.z) < 0.9:
            f.normal_flip()
        if f in tf and f.normal.z < 0:
            f.normal_flip()
    FACES.setdefault((id(mb), m), []).extend(fl)
    FACES.setdefault((id(mb), MOSS if z1 > 41.0 and z1 < 60 else m), []).extend(tf)


# ------------------------------------------------------------------ roda d'agua (VFX_OP_Wheel) + apoios estaticos
def wheel_static(mb):
    """cavaletes de madeira sobre sapatas de pedra nas 2 capas, mancais com cinta de ferro, chapa na parede do moinho"""
    mill_x = None
    d = GROUND.dist((-170.6, WY, AXZ), (1.0, 0.0, 0.0), 12.0)
    if d is not None:
        mill_x = -170.6 + d
    for k, sx in enumerate(SUPPORT_X):
        zc = GROUND.down(sx, WY, AXZ, 10.0) or (LV_T1 + FREE)
        # sapata de pedra sobre a capa
        box(mb, sx - 0.8, sx + 0.8, WY - 2.0, WY + 2.0, zc - 0.2, zc + 0.45, CAP)
        z0 = zc + 0.45
        # 2 pernas inclinadas (A) + travessa + mancal
        for s in (-1, 1):
            p0 = Vector((sx, WY + s * 1.55, z0))
            p1 = Vector((sx, WY + s * 0.42, AXZ - 0.95))
            beam(mb, p0, p1, 0.42, WOODD)
        zt = z0 + (AXZ - 0.95 - z0) * 0.45
        box(mb, sx - 0.24, sx + 0.24, WY - 1.15, WY + 1.15, zt - 0.2, zt + 0.2, WOODD, bottom=True)
        box(mb, sx - 0.5, sx + 0.5, WY - 0.75, WY + 0.75, AXZ - 1.05, AXZ - 0.3, WOOD, bottom=True)   # mancal
        # cinta de ferro sobre o eixo (3 lados)
        box(mb, sx - 0.32, sx + 0.32, WY - 0.62, WY + 0.62, AXZ + 0.48, AXZ + 0.62, IRON, bottom=True)
        for s in (-1, 1):
            box(mb, sx - 0.32, sx + 0.32, WY + s * 0.62 - (0.14 if s > 0 else 0.0), WY + s * 0.62 + (0.0 if s > 0 else 0.14),
                AXZ - 0.3, AXZ + 0.62, IRON, bottom=True)
    if mill_x is not None:
        # chapa de madeira + aro de ferro onde o eixo entra no moinho
        box(mb, mill_x - 0.18, mill_x + 0.05, WY - 1.2, WY + 1.2, AXZ - 1.2, AXZ + 1.2, WOODD)
    return mill_x


def beam(mb, p0, p1, w, m):
    d = p1 - p0
    ln = d.length
    u = d / ln
    a = Vector((1.0, 0.0, 0.0)) if abs(u.x) < 0.9 else Vector((0.0, 1.0, 0.0))
    s1 = u.cross(a).normalized() * (w / 2)
    s2 = u.cross(s1).normalized() * (w / 2)
    cs = [s1 + s2, -s1 + s2, -s1 - s2, s1 - s2]
    for k in range(4):
        c0, c1 = cs[k], cs[(k + 1) % 4]
        face(mb, [p0 + c0, p1 + c0, p1 + c1, p0 + c1], m, (c0 + c1))
    face(mb, [p1 + c for c in cs], m, u)
    face(mb, [p0 + c for c in cs], m, -u)


def wheel(mill_x):
    mw = MB("VFX_OP_Wheel", "12_VFX_HELPERS", None, detail="near", floor=-999)
    xr = (WX - WW / 2 + 0.25, WX + WW / 2 - 0.25)          # 2 aros
    n = 16
    r_rim = WR - 1.75                                      # aro em 4,75
    for k in range(n):
        a = 2 * math.pi * (k + 0.5) / n
        ch = 2 * r_rim * math.sin(math.pi / n) + 0.12
        for x in xr:
            mw.box((0.42, ch, 0.62), (x, WY + r_rim * math.cos(a), AXZ + r_rim * math.sin(a)), (a + math.pi / 2, 0, 0),
                   WOODD, 0.0)
    for k in range(n):                                     # pas: do aro ate a borda (raio 6,5), alem dos aros
        a = 2 * math.pi * k / n
        rp = (r_rim - 0.35 + WR) / 2
        mw.box((WW + 0.3, 0.24, WR - r_rim + 0.35), (WX, WY + rp * math.cos(a), AXZ + rp * math.sin(a)),
               (a + math.pi / 2, 0, 0), WOOD, 0.0)
    for k in range(8):                                     # raios (8 por aro), cubo octogonal
        a = 2 * math.pi * k / 8 + math.pi / 16
        rc = (0.95 + r_rim) / 2
        for x in xr:
            mw.box((0.34, 0.42, r_rim - 0.95 + 0.2), (x, WY + rc * math.cos(a), AXZ + rc * math.sin(a)),
                   (a + math.pi / 2, 0, 0), WOODD, 0.0)
    mw.cyl(1.0, WW - 0.1, (WX, WY, AXZ), (0, math.pi / 2, 0), m=WOODD, n=8, bevel=0.0)
    x_end = (mill_x + 0.3) if mill_x is not None else -165.0
    x_beg = SUPPORT_X[0] - 0.9
    mw.cyl(0.45, x_end - x_beg, ((x_end + x_beg) / 2, WY, AXZ), (0, math.pi / 2, 0), m=IRON, n=8, bevel=0.0)
    ob = mw.finish()
    ob["pivot"] = (WX, WY, AXZ)
    # correnteza para -Y (sul): as pas de BAIXO sao empurradas para -Y. Com eixo +X e rpm > 0 (mao direita) o ponto de
    # baixo andaria para +Y (contra a agua) -> eixo -X. A conversao do export (x, z, -y) e uma rotacao propria: o
    # sentido se preserva no Roblox (CFrame.fromAxisAngle).
    ob["axis"] = (-1.0, 0.0, 0.0)
    ob["rpm"] = RPM
    ob["vfx_zone"] = "canal"
    ob["Dist"] = 220.0
    return ob


# ------------------------------------------------------------------ marcadores (lidos pelo op_core.fx_markers)
def _wp(pts):
    return ";".join("%.2f,%.2f,%.2f" % p for p in pts)


def castle_curtain():
    """cortina da cachoeira do castelo: labio -> degrau A -> degrau B -> bacia (pares com cota diferente = queda curta)"""
    x = FALL_X
    ya = STEP_A["y0"]
    yb = STEP_B["y0"]
    pts = [(x, LIP_FRONT - 0.05, LIP_TOP + 0.14), (x, LIP_FRONT - 0.2, 127.0), (x, LIP_FRONT - 0.3, 112.0),
           (x, LIP_FRONT - 0.35, STEP_A["top"] + 0.15), (x, ya + 0.05, STEP_A["top"] + 0.12),
           (x, ya - 0.2, STEP_B["top"] + 0.12), (x, yb + 0.05, STEP_B["top"] + 0.1), (x, yb - 0.25, LV_B)]
    ws = [6.4, 7.0, 7.6, 8.2, 8.8, 9.4, 11.0, 12.0]
    return pts, ws


def sea_curtain(nm):
    if nm == "W":
        x, y, z = -174.0, LIP_W_Y, LV_T1 - 0.3
        pts = [(x, y - 0.05, z + 0.15), (x, y - 0.3, z - 2.5), (x, y - 0.8, 75.0), (x, y - 1.4, 60.0),
               (x, y - 1.9, 45.0), (x, y - 2.2, SEA)]
        ws = [7.4, 7.8, 8.4, 9.0, 9.6, 10.4]
    else:
        x, y, z = 248.5, LIP_E_Y, LV_P - 0.3
        pts = [(x, y - 0.05, z + 0.15), (x, y - 0.3, z - 2.5), (x, y - 0.8, 78.0), (x, y - 1.4, 62.0),
               (x, y - 1.9, 46.0), (x, y - 2.2, SEA)]
        ws = [5.4, 5.8, 6.4, 7.0, 7.6, 8.2]
    return pts, ws


def spring_curtain():
    x, y, z = SPRING
    return [(x, y - 0.02, z + 0.05), (x, y - 0.3, z - 1.6), (x, y - 0.45, LV_P + 1.0), (x, y - 0.5, LV_P)], \
        [1.0, 1.1, 1.3, 1.5]


def _canal_e_path():
    """caminho da agua do canal leste com o degrau de 3 x 2 (explicito: soleira 97,3 / 95,3 / 93,3)"""
    w = 5.7
    y = 342.0
    x0 = WEIR_E["x0"]
    (l1, t1), (l2, t2), (l3, t3) = WEIR_E["steps"]
    xa, xb, xc = x0 + l1, x0 + l1 + l2, x0 + l1 + l2 + l3
    pts = [(XM, y, LV_CF), (xa, y, LV_CF),
           (xa + 0.2, y, t2 + 0.15), (xb, y, t2 + 0.15),
           (xb + 0.2, y, t3 + 0.15), (xc, y, t3 + 0.15),
           (xc + 0.2, y, LV_P), (188.0, 343.0, LV_P), (248.0, 343.0, LV_P), (248.5, 304.0, LV_P),
           (248.5, FACE_E_Y, LV_P), (248.5, LIP_E_Y, LV_P - 0.15)]
    return pts, [w] * (len(pts) - 1) + [5.4]


def _canal_w_path():
    w = 7.7
    x = -174.0
    y0 = WEIR_W["y0"]
    (l1, t1), (l2, t2) = WEIR_W["steps"]
    pts = [(x, HEAD_W_Y - 0.2, LV_P), (x, 250.0, LV_P), (x, 182.0, LV_P), (x, y0 - l1, LV_P),
           (x, y0 - l1 - 0.2, t2 + 0.15), (x, y0 - l1 - l2, t2 + 0.15),
           (x, y0 - l1 - l2 - 0.2, LV_T1), (x, 92.0, LV_T1), (x, 58.0, LV_T1), (x, FACE_W_Y, LV_T1),
           (x, LIP_W_Y, LV_T1 - 0.15)]
    return pts, [w] * (len(pts) - 1) + [7.4]


def basin_poly():
    """contorno da AGUA da bacia (anti-horario, nivel 97,6): o buraco da planta 0,15 para dentro (junta da cantaria) e o
    fundo puxado ate o pe da rocha (y 351,15, sob a soleira molhada)"""
    B = ccw(DL.offset_poly(L.BASIN, -(IN - JNT)))
    out = []
    n = len(B)
    ya, yb = 342.0 - (3.0 - IN + JNT), 342.0 + (3.0 - IN + JNT)        # bordas da agua do canal (339,15 / 344,85)
    for i, (x, y) in enumerate(B):
        if y > 349.0:
            # empurra o canto de tras ao longo da diagonal ate y = BASIN_BACK
            out.append((x - math.copysign(1.0, x) * (BASIN_BACK - y) * (6.0 / 7.0), BASIN_BACK))
        elif x == max(p[0] for p in B):
            # quina leste -> BOCA retangular ate x = XM (o canal comeca nela)
            pa, pb = B[i - 1], B[(i + 1) % n]
            xa = pa[0] + (x - pa[0]) * (ya - pa[1]) / (y - pa[1])
            xb = x + (pb[0] - x) * (yb - y) / (pb[1] - y)
            out += [(xa, ya), (XM, ya), (XM, yb), (xb, yb)]
        else:
            out.append((x, y))
    return out


def water_markers():
    """nome -> (posicao, rumo, props) dos FX_*/WATER_*: as MESMAS constantes que desenham a pedra deste modulo. O
    op_core.fx_markers aplica por cima das estimativas do M1 (cria o que faltar, ex.: FX_Fall_Castle_Step)."""
    south = yaw_to(0, -1)
    east = yaw_to(1, 0)
    cpts, cws = castle_curtain()
    wpts, wws = sea_curtain("W")
    epts, ews = sea_curtain("E")
    spts, sws = spring_curtain()
    ce, cew = _canal_e_path()
    cwp, cww = _canal_w_path()
    bp = basin_poly()
    xs = [p[0] for p in bp]
    ys = [p[1] for p in bp]
    bed_b = LV_B - BED_D
    ma = ((XM, 342.0 - (3.0 - IN + JNT), LV_B), (XM, 342.0 + (3.0 - IN + JNT), LV_B))
    out = {
        "FX_Fall_Castle_Lip": ((FALL_X, LIP_FRONT, LIP_TOP), south, {
            "fx": "nevoa_borda", "kind": "cachoeira", "width": 6.4, "drop": round(LIP_TOP - LV_B, 2),
            "water_level_up": round(LIP_TOP + 0.14, 2), "waypoints": _wp(cpts),
            "widths": ",".join("%.1f" % w for w in cws),
            "spout_waypoints": _wp([(FALL_X, 357.4, LIP_TOP + 0.14), (FALL_X, LIP_FRONT, LIP_TOP + 0.14)]),
            "spout_width": 5.0, "source_pos": (FALL_X, 357.6, 131.2),
            "note": "frente do labio de pedra do op_terrain (topo medido 132,05; a lamina corre 0,14 acima, da boca escura "
                    "da nascente em y 357,6 - 'spout_waypoints' - ate a frente); cortina medida: labio -> degrau de "
                    "espuma A (98,5) -> degrau B (97,9) -> bacia (97,6); folga da rocha >= 0,3"}),
        "FX_Fall_Castle_Step": ((FALL_X, STEP_A["y0"], STEP_A["top"]), south, {
            "fx": "espuma_degrau", "width": 8.8, "jump": round(STEP_A["top"] - STEP_B["top"], 2),
            "step2_pos": (FALL_X, STEP_B["y0"], STEP_B["top"]),
            "note": "NOVO (op_water): borda da frente do degrau de espuma A; a cortina bate no topo, espalha e cai no "
                    "degrau B (step2_pos) e na bacia"}),
        "FX_Fall_Castle_Base": ((FALL_X, STEP_B["y0"] - 0.3, LV_B), south, {
            "fx": "nevoa_base", "width": 11.0, "level": LV_B,
            "note": "pe da cachoeira na bacia, na frente do degrau B, entre as pedras molhadas dos flancos"}),
        "FX_Mist_CastleFall": ((FALL_X, 347.6, LV_B + 1.2), 0.0, {
            "fx": "nevoa_baixa", "radius": 11.0, "note": "nevoa do pe da cachoeira (degraus de espuma + bacia)"}),
        "WATER_Basin": ((round(sum(xs) / len(xs), 2), round(sum(ys) / len(ys), 2), LV_B), yaw_to(0, 1), {
            "shape": "poligono", "level": LV_B, "floor": bed_b, "depth": round(LV_B - bed_b, 2), "rim_min": LV_B + 0.3,
            "sx": round(max(xs) - min(xs), 2), "sy": round(max(ys) - min(ys), 2),
            "waypoints": _wp([(x, y, LV_B) for x, y in bp]),
            "mouth_a_pos": ma[0], "mouth_b_pos": ma[1],
            "note": "contorno DESENHADO da agua: buraco do terreno 0,15 para dentro (junta da cantaria) + fundo puxado ate "
                    "o pe da rocha (351,15); a boca do canal leste (mouth_a/b) fica na borda leste; o leito e o do "
                    "terreno (95,4) com o apron (96,9) e os degraus de espuma no fundo"}),
        "WATER_CanalE": ((ce[0][0], ce[0][1], LV_CF), east, {
            "level": LV_CF, "level_low": LV_P, "floor": LV_CF - BED_D, "floor_low": LV_P - BED_D, "rim": LV_CF + FREE,
            "rim_low": LV_P + FREE, "waypoints": _wp(ce), "widths": ",".join("%.1f" % w for w in cew),
            "note": "canal de cantaria: boca da bacia -> degrau 3 x 2 (FX_Weir_E) -> pe do rochedo NE -> curva -> bica da "
                    "queda leste; pares de pontos com cota diferente = quedas curtas; ultimo ponto = ponta da bica"}),
        "WATER_CanalW": ((cwp[0][0], cwp[0][1], LV_P), south, {
            "level": LV_P, "level_low": LV_T1, "floor": LV_P - BED_D, "floor_low": LV_T1 - BED_D, "rim": LV_P + FREE,
            "rim_low": LV_T1 + FREE, "waypoints": _wp(cwp), "widths": ",".join("%.1f" % w for w in cww),
            "wheel_pos": (WX, WY, LV_T1),
            "note": "cabeceira no arrimo do terraco alto (bica FX_Spring_W) -> sob as pontes do plano (y 182, 252) -> "
                    "degrau 2 x 2 (FX_Weir_W) -> roda d'agua (wheel_pos: espuma onde as pas batem) -> bica da queda "
                    "oeste"}),
        "FX_Weir_E": ((WEIR_E["x0"] + WEIR_E["steps"][0][0], 342.0, LV_CF), east, {
            "fx": "degrau_agua", "drop": round(LV_CF - LV_P, 2), "steps": len(WEIR_E["steps"]), "width": 5.7,
            "tops": ",".join("%.2f" % t for _, t in WEIR_E["steps"]),
            "note": "borda da soleira (97,3) do degrau de 3 x 2 do canal leste; correnteza +X local"}),
        "FX_Weir_W": ((-174.0, WEIR_W["y0"] - WEIR_W["steps"][0][0], LV_P), south, {
            "fx": "degrau_agua", "drop": round(LV_P - LV_T1, 2), "steps": len(WEIR_W["steps"]), "width": 7.7,
            "tops": ",".join("%.2f" % t for _, t in WEIR_W["steps"]),
            "note": "borda da soleira (91,3) do degrau de 2 x 2 do canal oeste; correnteza -Y local"}),
        "FX_Spring_W": ((SPRING[0], SPRING[1], SPRING[2]), south, {
            "fx": "bica", "kind": "bica", "width": 1.0, "drop": round(SPRING[2] - LV_P, 2), "waypoints": _wp(spts),
            "widths": ",".join("%.1f" % w for w in sws),
            "note": "ponta da bica de pedra (calha com abas) que sai do nicho escuro no arrimo do terraco alto; cai na "
                    "cabeceira do canal oeste"}),
        "FX_Fall_W_Lip": ((-174.0, LIP_W_Y, LV_T1 - 0.3), south, {
            "fx": "nevoa_borda", "kind": "bica", "width": 7.4, "drop": round(LV_T1 - 0.3 - SEA, 2),
            "water_level_up": LV_T1, "waypoints": _wp(wpts), "widths": ",".join("%.1f" % w for w in wws),
            "face_y_local": FACE_W_Y,
            "note": "ponta da soleira (87,3) em balanco 0,8 alem da face da garganta SO (47,0), entre 2 bochechas; "
                    "cortina medida ate o mar (36)"}),
        "FX_Fall_W_Base": ((wpts[-1][0], wpts[-1][1], SEA), south, {
            "fx": "espuma_mar", "width": 10.0, "level": SEA,
            "note": "pe da queda oeste no mar local, entre as pedras de base"}),
        "FX_Fall_E_Lip": ((248.5, LIP_E_Y, LV_P - 0.3), south, {
            "fx": "nevoa_borda", "kind": "bica", "width": 5.4, "drop": round(LV_P - 0.3 - SEA, 2),
            "water_level_up": LV_P, "waypoints": _wp(epts), "widths": ",".join("%.1f" % w for w in ews),
            "face_y_local": FACE_E_Y,
            "note": "ponta da soleira (91,3) em balanco 0,8 alem da face da garganta NE (298,0); cai na enseada do porto "
                    "(rumo SUL medido na garganta; o M1 estimava SE)"}),
        "FX_Fall_E_Base": ((epts[-1][0], epts[-1][1], SEA), south, {
            "fx": "espuma_mar", "width": 8.2, "level": SEA,
            "note": "pe da queda leste na enseada, entre as pedras de base"}),
        "WATER_Sea": ((L.SEA_C[0], L.SEA_C[1], SEA), 0.0, {
            "shape": "quadrado", "level": SEA, "size": L.SEA_SIZE, "client_only": True, "area": 5,
            "color": "48,176,196",
            "falls": "FX_Fall_W_Base;FX_Fall_E_Base",
            "note": "mar LOCAL turquesa de Wano: so no cliente e so com o jogador na area 5 (como o mar de nuvens da "
                    "DS); esconde a quilha; vista de Wano, a DS aparece como ilha saindo do mar (topo da quilha DS "
                    "53,6 > 46). Conferido no op_water: as 2 quedas da borda terminam em 36 (pedras de base)"}),
    }
    return out


# ------------------------------------------------------------------ previa da agua (00_REFERENCE: fora do export)
def preview():
    pw = MB("PREVIEW_Water_OP", "00_REFERENCE", None, detail="far", floor=-999)
    M = water_markers()

    def parse(s):
        return [tuple(float(v) for v in p.split(",")) for p in s.split(";")]

    def ribbon(pts, ws, m):
        for (a, b), w0, w1 in zip(zip(pts, pts[1:]), ws, ws[1:]):
            dx, dy = b[0] - a[0], b[1] - a[1]
            ln = math.hypot(dx, dy) or 1.0
            nx, ny = -dy / ln, dx / ln
            if math.hypot(dx, dy) < 0.05:
                continue
            face(pw, [(a[0] + nx * w0 / 2, a[1] + ny * w0 / 2, a[2] - 0.04), (a[0] - nx * w0 / 2, a[1] - ny * w0 / 2, a[2] - 0.04),
                      (b[0] - nx * w1 / 2, b[1] - ny * w1 / 2, b[2] - 0.04), (b[0] + nx * w1 / 2, b[1] + ny * w1 / 2, b[2] - 0.04)],
                 m, (0, 0, 1))

    def curtain(pts, ws, fwd, m):
        fx, fy = fwd
        sx, sy = -fy, fx
        for (a, b), w0, w1 in zip(zip(pts, pts[1:]), ws, ws[1:]):
            face(pw, [(a[0] + sx * w0 / 2, a[1] + sy * w0 / 2, a[2]), (a[0] - sx * w0 / 2, a[1] - sy * w0 / 2, a[2]),
                      (b[0] - sx * w1 / 2, b[1] - sy * w1 / 2, b[2]), (b[0] + sx * w1 / 2, b[1] + sy * w1 / 2, b[2])],
                 m, (fx, fy, 0.3))
    for nm in ("WATER_CanalE", "WATER_CanalW"):
        p = M[nm][2]
        ribbon(parse(p["waypoints"]), [float(w) for w in p["widths"].split(",")], "PREVIEW_Sea")
    bp = parse(M["WATER_Basin"][2]["waypoints"])
    face(pw, [(x, y, z - 0.06) for x, y, z in bp], "PREVIEW_Sea", (0, 0, 1))
    for nm in ("FX_Fall_Castle_Lip", "FX_Fall_W_Lip", "FX_Fall_E_Lip", "FX_Spring_W"):
        p = M[nm][2]
        curtain(parse(p["waypoints"]), [float(w) for w in p["widths"].split(",")], (0.0, -1.0), "PREVIEW_Falls")
    flush(pw)
    ob = pw.finish(recalc=False)
    return ob


# ------------------------------------------------------------------ conferencia na cena (raios)
def measure(n_warn_only=False):
    warn = 0
    own = Ground.__new__(Ground)
    verts, polys = [], []
    for o in bpy.data.objects:
        if o.type == "MESH" and o.name.startswith(("OP_Water_",)):
            mw = o.matrix_world
            b = len(verts)
            verts += [mw @ v.co for v in o.data.vertices]
            polys += [[b + i for i in p.vertices] for p in o.data.polygons]
    own.t = BVHTree.FromPolygons(verts, polys)

    def chk(lab, got, want, tol):
        nonlocal warn
        bad = got is None or abs(got - want) > tol
        warn += bad
        print("%s WATER MEDIDA %-40s %s (projeto %.2f)" % ("AVISO" if bad else "OK   ", lab,
                                                            "nada" if got is None else "%.2f" % got, want))
    chk("labio do castelo (topo, terreno)", GROUND.down(FALL_X, LIP_FRONT + 0.4, 140.0), LIP_TOP, 0.06)
    chk("degrau de espuma A (topo)", own.down(FALL_X, STEP_A["y0"] + 0.5, 110.0), STEP_A["top"], 0.02)
    chk("degrau de espuma B (topo)", own.down(FALL_X, STEP_B["y0"] + 0.5, 110.0), STEP_B["top"], 0.02)
    chk("leito da bacia (terreno)", GROUND.down(0.0, 340.0, 110.0), LV_B - BED_D, 0.06)
    chk("leito do canal leste alto (terreno)", GROUND.down(60.0, 342.0, 110.0), LV_CF - BED_D, 0.06)
    chk("leito do canal leste baixo (terreno)", GROUND.down(150.0, 342.5, 110.0), LV_P - BED_D, 0.06)
    chk("leito do canal oeste alto (terreno)", GROUND.down(-174.0, 220.0, 110.0), LV_P - BED_D, 0.06)
    chk("leito do canal oeste baixo (terreno)", GROUND.down(-174.0, 75.0, 110.0), LV_T1 - BED_D, 0.06)
    chk("soleira da bica oeste (topo)", own.down(-174.0, LIP_W_Y + 0.4, 100.0), LV_T1 - 0.3, 0.02)
    chk("soleira da bica leste (topo)", own.down(248.5, LIP_E_Y + 0.4, 100.0), LV_P - 0.3, 0.02)
    chk("soleira do degrau leste (topo)", own.down(WEIR_E["x0"] + 0.8, 342.0, 110.0), WEIR_E["steps"][0][1], 0.02)
    chk("soleira do degrau oeste (topo)", own.down(-174.0, WEIR_W["y0"] - 0.7, 110.0), WEIR_W["steps"][0][1], 0.02)
    # capa das margens: borda >= agua + 0,3 em toda a extensao (raio no meio da capa)
    worst = 99.0
    for nm, lvs in (("E", CANALS["E"]["lv"]), ("W", CANALS["W"]["lv"])):
        ax = Axis(CANALS[nm]["pts"])
        hw = CANALS[nm]["hw"]
        for i, (a, b, u, n, ln) in enumerate(ax.seg):
            s = 0.5
            while s < ln - 0.5:
                for side in (1, -1):
                    p = a + u * s + n * side * (hw - IN + 0.2)
                    z = own.down(p.x, p.y, lvs[i] + 12.0, 14.0)
                    if z is not None:
                        worst = min(worst, z - lvs[i])
                s += 3.0
    print("%s WATER MEDIDA folga minima capa -> agua: %.2f (>= 0,30)" % ("OK   " if worst >= 0.3 else "AVISO", worst))
    warn += worst < 0.3
    # cortinas: folga ate a rocha atras (+y) em cada ponto
    allb = [GROUND, own]
    for lab, pts in (("castelo", castle_curtain()[0][1:4]), ("oeste", sea_curtain("W")[0][1:-1]),
                     ("leste", sea_curtain("E")[0][1:-1])):
        w = 99.0
        for x, y, z in pts:
            for g in allb:
                d = g.dist((x, y - 0.01, z - 0.2), (0.0, 1.0, 0.0), 8.0)
                if d is not None:
                    w = min(w, d)
        print("%s WATER MEDIDA folga cortina %-8s -> rocha atras: %.2f" % ("OK   " if w >= 0.25 else "AVISO", lab, w))
        warn += w < 0.25
    # roda: pas x leito, mergulho
    bed = GROUND.down(WX, WY, 90.0)
    chk("leito sob a roda (terreno)", bed, LV_T1 - BED_D, 0.06)
    print("%s WATER MEDIDA roda: pa mais baixa %.2f, agua %.2f (mergulho %.2f), folga ao leito %.2f" % (
        "OK   " if bed is not None and AXZ - WR - bed >= 0.3 else "AVISO", AXZ - WR, LV_T1, LV_T1 - (AXZ - WR),
        (AXZ - WR - bed) if bed is not None else -1))
    return warn


# ------------------------------------------------------------------ cameras de revisao da zona
CAMS = {
    "CAM_OPWat_FallPlaza": ((-6.0, 262.0, P + 5.5), (0.0, 350.0, 116.0), 24),
    "CAM_OPWat_FallPlazaHigh": ((10.0, 250.0, 128.0), (0.0, 350.0, 108.0), 28),
    "CAM_OPWat_Basin": ((13.0, 323.0, CF + 5.5), (0.0, 347.5, 100.5), 22),
    "CAM_OPWat_BasinHigh": ((-16.0, 334.0, 114.0), (2.0, 347.0, 97.6), 24),
    "CAM_OPWat_Wheel": ((-158.5, 66.0, T1 + 5.5), (-174.0, 90.0, 90.5), 24),
    "CAM_OPWat_WheelHigh": ((-150.0, 58.0, 108.0), (-174.0, 92.0, 89.0), 28),
    "CAM_OPWat_CanalW": ((-150.0, 240.0, 124.0), (-174.0, 160.0, 91.0), 26),
    "CAM_OPWat_WeirW": ((-160.0, 104.0, T1 + 5.5), (-174.0, 120.0, 90.0), 24),
    "CAM_OPWat_Spring": ((-166.0, 284.0, P + 5.5), (-174.0, 299.5, 95.5), 26),
    "CAM_OPWat_CanalE": ((58.0, 326.0, 106.0), (130.0, 343.0, 93.0), 24),
    "CAM_OPWat_WeirE": ((114.0, 333.0, P + 5.5), (92.0, 342.0, 95.5), 24),
    "CAM_OPWat_CornerE": ((272.0, 296.0, 138.0), (247.0, 334.0, 92.0), 26),
    "CAM_OPWat_Mouth": ((32.0, 328.0, 106.0), (17.0, 343.0, 97.6), 24),
    "CAM_OPWat_PH_Mouth": ((30.0, 333.0, CF + 5.5), (16.0, 343.0, 98.6), 24),
    "CAM_OPWat_SeaW": ((-200.0, -16.0, 40.0), (-174.0, 46.0, 58.0), 24),
    "CAM_OPWat_SeaE": ((262.0, 205.0, 96.0), (248.5, 297.0, 64.0), 32),
}


def cams():
    for n, (loc, tgt, lens) in CAMS.items():
        camera(n, loc, tgt, lens)


# ------------------------------------------------------------------ build
def build():
    global GROUND
    for o in [o for o in bpy.data.objects if o.name.startswith(("PREVIEW_Water", "OP_Water_", "VFX_OP_Wheel"))]:
        bpy.data.objects.remove(o, do_unlink=True)
    FACES.clear()
    bpy.context.view_layer.update()
    GROUND = Ground()
    mb = MB("OP_Water_Stone", C, None, detail="far", floor=-999)
    n_e = canal_walls(mb, "E")
    n_w = canal_walls(mb, "W")
    weirs(mb)
    lips(mb)
    spring(mb)
    n_b = basin(mb)
    n_r = rocks(mb)
    mill_x = wheel_static(mb)
    flush(mb)
    ob = mb.finish(recalc=False)
    wob = wheel(mill_x)
    preview()
    cams()
    bpy.context.view_layer.update()
    w = measure()
    tris = sum(len(p.vertices) - 2 for p in ob.data.polygons)
    wt = sum(len(p.vertices) - 2 for p in wob.data.polygons)
    print("op_water pedras canal leste=%d oeste=%d revestimento bacia=%d pedras soltas=%d moinho x=%s | tris pedra %d "
          "(%d materiais) roda %d | medidas com aviso=%d" % (n_e, n_w, n_b, n_r, "%.2f" % mill_x if mill_x else "-",
                                                             tris, len(ob.data.materials), wt, w))
