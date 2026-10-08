# op_plaza.py - M4 da Ilha 5 (ONE PIECE / WANO): PRACA DE MINERACAO (PLANO_OP secoes 5 e 14; PROMPT_USUARIO secao 6).
# Roda DEPOIS do op_m2_praca (build_op.ZONE_MODULES["plaza"] = ["op_m2_praca", "op_plaza"]): a FAIXA SUL (y 118..170:
# borda, eixo de chegada, campos 7,2, arrimo, mureta, toro e estandartes da chegada) e o EMBLEMA rebaixado em (0, 216)
# ficam INTACTOS; aqui so sai o piso PROVISORIO liso (OP_Plz_M2_PisoProvisorio) e entra o resto.
#
# CRITICA DO LEAD: "a praca e um grande vazio bege". O centro continua LIVRE (mineracao: 72 ORE_, unidades/pets), entao
# o acabamento e DESENHO NO CHAO + BORDA COM INTENCAO, nunca objeto no meio:
#   PISO (OP_Plz_Piso, tudo a piso + 0,15 = topo das lajes do trecho; corpo ate piso - 0,3; JUNTA REBAIXADA = chanfro
#   0,07 de cada laje, sem fresta; nada acima de +0,15 dentro da MiningZone):
#     - MEDALHAO: lajes radiais do quadro 30 x 30 do emblema ate o circulo r 24 + ANEL de pedra 24..25,2.
#     - ARENA de ANEIS concentricos em volta do emblema ate r 85,6 (como a concept): fiadas de ~4 de largura em lajes de
#       arco ~7,5 com juntas desencontradas (todas as fiadas usam a MESMA grade angular de 144: aneis vizinhos emendam
#       vertice a vertice), 2 fiadas mais claras (ritmo de tom), anel de pedra media em 46..47,2 e BORDA DUPLA da arena
#       (pedra 80..81,2 + fiada clara 81,2..84,4 + pedra 84,4..85,6). Cortada em reta pela SOLEIRA de pedra y 170..171,2
#       (o fim da faixa sul vira limiar desenhado, nao corte).
#     - EIXO norte-sul (lajes claras |x| <= 8 + guias de pedra 8..9,2, continuacao exata do eixo do trecho) do fim da
#       faixa sul ate o medalhao e do medalhao ate o pe da escada Adro (sob o portao vermelho do castelo): atravessa os
#       aneis.
#     - MARGEM (fora da arena): campos de lajes 7,2 alinhados com os campos do trecho (x a partir de +-9,2).
#     - BORDA de lajes claras 3,4 ao longo de todo o contorno da praca (chanfros inclusive), recortada nas escadas.
#   BORDA (fora da MiningZone + 8; nada no centro; nenhum pedestal/fonte/estatua/arvore):
#     - LESTE (queda de 4 para o terraco do summon; arrimo e capa do op_terrain): MURETA de cantaria h 2,3 (mesma da
#       faixa sul, continua a partir do pilarete final dela) em 2 setores com o VAO da escada Summon (y 205..227),
#       2 ESTANDARTES brancos com o brasao flanqueando a entrada (como na concept), bancos e postes de andon.
#     - OESTE (mesmo nivel da rua do quarteirao): MURETA BAIXA de assento (h 1,5) em 2 setores com vaos nas portas das
#       casas W2/W3/W4, banco encostado em cada setor, postes de andon nos vaos.
#     - NORTE (arrimo do adro): bancos encostados ao muro (vista para a praca e o castelo).
#     - CANTOS NO/NE (entradas para o terraco alto e o quarteirao NE): poste de andon marcando cada entrada (os
#       estandartes de canto do trecho ja estao la).
# DONOS / PREFIXOS: OP_Plz_Piso*, OP_Plz_Mureta (dono plaza; teto do lead 34k), OP_Prop_Plz_* (estandartes, postes, bancos:
#   dono props, ver relatorio). Luzes so NightOnly (L_OPProp_Lamp_Plz_*). Colisoes: mureta (OP_PlzMureta), postes
#   (OP_PropLamp), estandartes (OP_PropBanner), bancos (OP_PropBench) - todas fora da MiningZone e das rotas do QA.
# CAMERAS: CAM_OP_Plz_* (criadas no build, fora do export).
import math, random
import bpy
import op_lib as DL
from op_lib import MB, Frame, ccw, col_box
import op_layout as L
import op_kit as K
import op_m2_trecho as T

P = L.P
ZT, ZB = P + T.Z_OFF, P - 0.3                  # topo das lajes (= trecho) / fundo
EYE = P + 5.65
CX, CY = L.EMBLEM_C
NG = 48                                        # grade angular unica (7,5 graus): aneis emendam vertice a vertice
XA = 9.2                                       # borda externa das guias do eixo
Y0 = T.STRIP_Y1                                # 170: fim da faixa sul
YS = Y0 + 1.2                                  # 171,2: topo da soleira de pedra
R_MED, R_MEDB = 24.0, 25.2                     # medalhao e anel de pedra dele
R_ARENA = 85.6
EDGE_W = 3.4                                   # borda de lajes do contorno
SENT = "OP_Plz_Piso"


def _h01(*a):
    return K._h01("plz", *a)


# ------------------------------------------------------------------ geometria 2D
def gp(r, i):
    a = 2.0 * math.pi * i / NG
    return (CX + r * math.cos(a), CY + r * math.sin(a))


def _clean(poly, eps=1e-4):
    out = []
    for p in poly:
        if not out or abs(p[0] - out[-1][0]) > eps or abs(p[1] - out[-1][1]) > eps:
            out.append(p)
    while len(out) > 1 and abs(out[0][0] - out[-1][0]) <= eps and abs(out[0][1] - out[-1][1]) <= eps:
        out.pop()
    return out


def _seg_x(p, q, a, b):
    """intersecao dos segmentos p-q e a-b: (t em p-q, u em a-b) ou None (t e u em [0, 1))"""
    rx, ry = q[0] - p[0], q[1] - p[1]
    sx, sy = b[0] - a[0], b[1] - a[1]
    den = rx * sy - ry * sx
    if abs(den) < 1e-12:
        return None
    qx, qy = a[0] - p[0], a[1] - p[1]
    t = (qx * sy - qy * sx) / den
    u = (qx * ry - qy * rx) / den
    if 0.0 <= t < 1.0 and 0.0 <= u < 1.0:
        return t, u
    return None


def minus_disc(S, R):
    """poligono S (convexo, ccw) MENOS o disco de raio R (o 144-gono da grade, centro no emblema): lista de poligonos
    (Weiler-Atherton simplificado). O contorno do disco usa os MESMOS vertices dos aneis (emenda exata)."""
    S = ccw(_clean(S))
    D = [gp(R, i) for i in range(NG)]
    n = len(S)
    xs = []                                     # (pos em S, ponto, pos em D, entra?)
    for k in range(n):
        p, q = S[k], S[(k + 1) % n]
        for j in range(NG):
            a, b = D[j], D[(j + 1) % NG]
            r = _seg_x(p, q, a, b)
            if r is None:
                continue
            t, u = r
            # entra no disco se a direcao de S aponta contra a normal externa da aresta j do disco (ccw)
            ex, ey = b[0] - a[0], b[1] - a[1]
            dx, dy = q[0] - p[0], q[1] - p[1]
            enter = (dx * ey - dy * ex) < 0.0
            xs.append((k + t, (p[0] + dx * t, p[1] + dy * t), j + u, enter))
    if not xs:
        c = (sum(p[0] for p in S) / n, sum(p[1] for p in S) / n)
        return [] if L.point_in_poly(c[0], c[1], D) else [S]
    xs.sort(key=lambda x: x[0])
    leaves = [x for x in xs if not x[3]]
    out, used = [], set()
    for start in leaves:
        if id(start) in used:
            continue
        poly, cur, guard = [], start, 0
        while guard < 50:
            guard += 1
            used.add(id(cur))
            poly.append(cur[1])
            # anda em S ate o proximo cruzamento (deve ser uma entrada)
            i0 = xs.index(cur)
            nxt = xs[(i0 + 1) % len(xs)]
            s0, s1 = cur[0], nxt[0] if nxt[0] > cur[0] else nxt[0] + n
            v = math.floor(s0) + 1
            while v <= s1 - 1e-9:
                poly.append(S[int(v) % n])
                v += 1
            A = nxt
            poly.append(A[1])
            # anda no disco em sentido horario ate a saida mais proxima
            sA = A[2]
            best, bd = None, 1e9
            for x in leaves:
                d_ = (sA - x[2]) % NG
                if 1e-9 < d_ < bd:
                    best, bd = x, d_
            m = math.floor(sA)
            if sA - m < 1e-9:
                m -= 1
            while (sA - m) % NG < bd - 1e-9:
                poly.append(D[m % NG])
                m -= 1
            cur = best
            if cur is start:
                break
        poly = _clean(poly)
        if len(poly) >= 3 and L.area(poly) > 0.3:
            out.append(ccw(poly))
    return out


def ring_piece(r0, r1, i0, i1):
    return [gp(r0, i) for i in range(i0, i1 + 1)] + [gp(r1, i) for i in range(i1, i0 - 1, -1)]


def sq(i):
    a = 2.0 * math.pi * i / NG
    e = T.EMBLEM_SQ / max(abs(math.cos(a)), abs(math.sin(a)))
    return (CX + e * math.cos(a), CY + e * math.sin(a))


def stair_rects():
    """retangulos das escadas que encostam na praca (pisada + banzos + 0,3): o piso nao entra nelas"""
    out = []
    for nm in ("Adro", "OesteAlta", "Summon"):
        foot, deg, w, n, tread, g = L.stair_frame(nm)
        a = math.radians(deg)
        ux, uy = round(math.cos(a)), round(math.sin(a))
        hw = w / 2 + 1.5
        x0, y0 = foot[0] - ux * (tread / 2 + 0.2), foot[1] - uy * (tread / 2 + 0.2)
        x1, y1 = foot[0] + ux * tread * n, foot[1] + uy * tread * n
        if ux:
            out.append((min(x0, x1), foot[1] - hw, max(x0, x1), foot[1] + hw))
        else:
            out.append((foot[0] - hw, min(y0, y1), foot[0] + hw, max(y0, y1)))
    return out


STAIR_R = stair_rects()


def cut_stairs(polys):
    for r in STAIR_R:
        nxt = []
        for p in polys:
            xs_ = [q[0] for q in p]
            ys_ = [q[1] for q in p]
            if max(xs_) <= r[0] or min(xs_) >= r[2] or max(ys_) <= r[1] or min(ys_) >= r[3]:
                nxt.append(p)
            else:
                nxt += [ccw(q) for q in L.subtract_rect(p, r) if len(q) >= 3]
        polys = nxt
    return polys


def clip_halves(poly, side):
    """lado leste (side +1: x >= 9,2) ou oeste (-1: x <= -9,2) e acima da soleira (y >= 171,2)"""
    p = DL.clip_half(poly, side, 0.0, -XA)
    if len(p) < 3:
        return []
    p = DL.clip_half(p, 0.0, 1.0, -YS)
    return p if len(p) >= 3 else []


# ------------------------------------------------------------------ piso
class Paver:
    def __init__(self, mb):
        self.mb = mb
        self.n = 0

    def slab(self, poly, m, sides=False):
        poly = _clean(poly)
        if len(poly) < 3 or L.area(poly) < 0.2:
            return
        for p in cut_stairs([ccw(poly)]):
            p = _clean(p)
            if len(p) >= 3 and L.area(p) > 0.2:
                K.slab_poly(self.mb, ccw(p), ZB, ZT, 0.07, m, sides)
                self.n += 1

    def pave(self, regions, x0, x1, y0, y1, rows, m, along="x", key="pv", mats=None, bond=0.5, sides=False):
        """lajes em fiadas (mesma regra do op_kit.pave: profundidade, comprimento sorteado em [L0, L1], juntas
        desencontradas) recortadas nas regioes. sides=False: a praca e um tapete continuo (toda laje tem vizinha:
        so chanfro + topo, a junta em V fecha sem fresta); a borda externa usa sides=True."""
        prof, L0, L1 = rows
        regs = [r for r in cut_stairs([ccw(r) for r in regions]) if len(r) >= 3 and L.area(r) > 0.3]
        u0, u1, v0, v1 = (x0, x1, y0, y1) if along == "x" else (y0, y1, x0, x1)
        v, r = v0, 0
        while v < v1 - 1e-3:
            dv = prof[r % len(prof)]
            vb = min(v1, v + dv)
            if v1 - vb < 0.6:
                vb = v1
            u, k = u0 - (L0 * bond * K._h01(key, r, "o")), 0
            while u < u1 - 1e-3:
                ub = min(u1, u + L0 + (L1 - L0) * K._h01(key, r, k))
                if u1 - ub < 0.6:
                    ub = u1
                ua = max(u, u0)
                if ub - ua > 0.05:
                    rect = (ua, v, ub, vb) if along == "x" else (v, ua, vb, ub)
                    mm = _pick(mats, key, r, k) if mats else m
                    for reg in regs:
                        piece = _clean(L.clip_rect(reg, rect))
                        if len(piece) >= 3 and L.area(piece) > 0.25:
                            K.slab_poly(self.mb, ccw(piece), ZB, ZT, 0.07, mm, sides)
                            self.n += 1
                u, k = ub, k + 1
            v, r = vb, r + 1


def _pick(mats, *key):
    tot = sum(w for _, w in mats)
    x = _h01(*key) * tot
    for m, w in mats:
        x -= w
        if x <= 0:
            return m
    return mats[-1][0]


# fiadas da arena: (r0, r1, arco alvo, materiais) - de dentro para fora
MIX = [(K.STZ, 14), (K.STP, 1)]                 # fiada corrente: tom da praca (1 laje clara em ~15)
LIGHT = [(K.STP, 1)]                            # fiada clara (ritmo dos aneis)
FIELD = [(K.STZ, 7), (K.STP, 1)]                # campos da margem (variacao pequena de tom)
BAND = [(K.ST, 1)]
WALLB = [(K.ST, 1)]


def courses():
    out = [(R_MED, R_MEDB, 6.0, BAND)]
    r = R_MEDB
    inner = [(5.2, MIX), (5.2, LIGHT), (5.2, MIX), (5.2, MIX)]
    for w, mt in inner:
        out.append((r, r + w, 8.5, mt))
        r += w
    out.append((r, r + 1.2, 8.0, WALLB))          # 46..47,2
    r += 1.2
    outer = [(32.8 / 7, mt) for mt in (MIX, MIX, LIGHT, MIX, MIX, LIGHT, MIX)]
    for w, mt in outer:
        out.append((r, r + w, 8.8, mt))
        r += w
    out.append((r, r + 1.2, 9.5, BAND))           # 80..81,2
    out.append((r + 1.2, r + 4.4, 9.0, LIGHT))     # fiada clara da borda da arena
    out.append((r + 4.4, r + 5.6, 9.5, BAND))     # 84,4..85,6
    return out


def _divide(lo, hi, k, key):
    """divide [lo, hi] (indices da grade) em pedacos de ~k passos com junta desencontrada (minimo k/2)"""
    k = max(1, k)
    mn = max(1, k // 2)
    cuts = [lo]
    i = lo + max(mn, int(round(k * (0.25 + 0.75 * _h01(key, "off")))))
    j = 0
    while hi - i >= mn:
        cuts.append(i)
        h = _h01(key, j)
        i += k + (1 if h > 0.7 else (-1 if h < 0.25 and k > 3 else 0))
        j += 1
    cuts.append(hi)
    return list(zip(cuts, cuts[1:]))


def build_arena(pv):
    # medalhao: lajes radiais do quadro 30 x 30 ate o circulo r 24 (16 setores; os cantos do quadro caem na grade)
    q = NG // 8                                                         # 45 graus: cantos do quadro na grade
    for s in range(8):
        i0, i1 = s * q, (s + 1) * q
        poly = [sq(i0), sq(i1)] + [gp(R_MED, i) for i in range(i1, i0 - 1, -1)]   # lado do quadro e reto
        pv.slab(poly, _pick(MIX, "med", s))
    for ci, (r0, r1, arc, mats) in enumerate(courses()):
        rm = (r0 + r1) / 2
        k = int(round(arc / (rm * 2 * math.pi / NG)))
        full = r1 <= R_MEDB + 1e-6                                      # anel do medalhao: volta inteira
        halves = [(0, NG, 0)] if full else [(-NG // 4, NG // 4, 1), (NG // 4, 3 * NG // 4, -1)]
        for lo, hi, side in halves:
            for i0, i1 in _divide(lo, hi, k, "c%d_%d" % (ci, side)):
                poly = ring_piece(r0, r1, i0, i1)
                if not full:
                    poly = clip_halves(poly, side)
                    if not poly:
                        continue
                pv.slab(poly, _pick(mats, "m", ci, i0))


def build_axis(pv):
    for (ya, yb) in ((Y0, CY), (CY, 314.0)):
        regs = minus_disc([(-XA, ya), (XA, ya), (XA, yb), (-XA, yb)], R_MEDB)
        regs = [r for r in regs]
        pv.pave(regs, -8.0, 8.0, Y0 + 0.0, 314.0, ((3.6,), 4.4, 6.0), K.STP, key="eixo",
                mats=[(K.STP, 5), (K.STZ, 1)])
        for s in (-1, 1):
            xa, xb = (8.0, XA) if s > 0 else (-XA, -8.0)
            pv.pave(regs, xa, xb, Y0, 314.0, ((1.2,), 4.4, 6.4), K.ST, along="y", key="guia%d" % s)


def plaza_in():
    Pp = ccw(L.PLAZA)
    return Pp, DL.offset_poly(Pp, -EDGE_W)


def build_sill(pv):
    """soleira de pedra y 170..171,2 de lado a lado (fim da faixa sul -> arena/margem)"""
    Pp = ccw(L.PLAZA)
    for s in (-1, 1):
        x0, x1 = (XA, 130.0) if s > 0 else (-130.0, -XA)
        reg = L.clip_rect(Pp, (x0, Y0, x1, YS))
        if len(reg) >= 3:
            pv.pave([reg], x0, x1, Y0, YS, ((1.2,), 4.0, 6.0), K.ST, along="x", key="sol%d" % s,
                    mats=None)


def build_margin(pv):
    Pp, Pin = plaza_in()
    QS = T.QS
    for s in (-1, 1):
        reg = clip_halves(Pin, s)
        regs = minus_disc(reg, R_ARENA)
        # campos alinhados com os do trecho: colunas a partir de +-9,2 a cada 7,2; fiadas a partir da soleira
        if s > 0:
            pv.pave(regs, XA, 130.0, YS, 320.0, ((QS,), QS, QS), K.STZ, key="mg1", mats=FIELD, bond=0.0)
        else:
            # espelho: lajes contadas a partir do eixo para fora (mesma grade do lado leste)
            m = int((130.0 - XA) // QS)
            edges = [-XA - QS * j for j in range(m + 1)]
            for u0, u1 in zip(edges[1:], edges[:-1]):
                pv.pave(regs, u0, u1, YS, 320.0, ((QS,), 30.0, 30.0), K.STZ, key="mg0_%d" % int(u0), mats=FIELD,
                        bond=0.0)


def build_edge(pv):
    """borda de lajes claras ao longo do contorno da praca (acima da soleira), mitrada nos cantos"""
    Pp, Pin = plaza_in()
    n = len(Pp)
    for i in range(n):
        a, b = Pp[i], Pp[(i + 1) % n]
        ai, bi = Pin[i], Pin[(i + 1) % n]
        ln = math.hypot(b[0] - a[0], b[1] - a[1])
        if max(a[1], b[1]) < YS:
            continue
        m = max(1, int(round(ln / 4.3)))
        ts = [0.0]
        for j in range(1, m):
            ts.append((j + 0.35 * (_h01("eb", i, j) - 0.5)) / m)
        ts.append(1.0)
        lerp = lambda p, q, t: (p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t)
        for j, (t0, t1) in enumerate(zip(ts, ts[1:])):
            poly = [lerp(a, b, t0), lerp(a, b, t1), lerp(ai, bi, t1), lerp(ai, bi, t0)]
            poly = DL.clip_half(poly, 0.0, 1.0, -YS)
            if len(poly) < 3:
                continue
            pieces = [poly]
            if a[1] > 300.0 and b[1] > 300.0:                             # o eixo segue ate a escada
                pieces = [q for p in pieces for q in L.subtract_rect(ccw(p), (-XA, 300.0, XA, 320.0))]
            for p in pieces:
                pv.slab(p, _pick([(K.STP, 4), (K.ST, 1)], "eb", i, j), sides=True)


def remove_fallback():
    ob = bpy.data.objects.get("OP_Plz_M2_PisoProvisorio")
    if ob:
        me = ob.data
        bpy.data.objects.remove(ob, do_unlink=True)
        if me and me.users == 0:
            bpy.data.meshes.remove(me)
        return True
    return False


def build_floor():
    mb = MB(SENT, "03_PLAZA", random.Random(401), detail="hero", floor=-999)
    pv = Paver(mb)
    tri = lambda: sum(len(f.verts) - 2 for f in mb.bm.faces)
    rep = []
    for nm, fn in (("arena", build_arena), ("eixo", build_axis), ("soleira", build_sill), ("margem", build_margin),
                   ("borda", build_edge)):
        t0, n0 = tri(), pv.n
        fn(pv)
        rep.append("%s %d lajes %d tris" % (nm, pv.n - n0, tri() - t0))
    print("op_plaza piso: " + " | ".join(rep))
    mb.finish()
    return pv.n


# ------------------------------------------------------------------ borda
EAST_X = 116.0 - 0.95 - 0.2                    # linha da mureta leste (recuo da faixa sul + 0,2: M6b item 23, a
                                               # mureta encravava 0,2 no arrimo/capa do op_terrain em x 115,3)
WEST_X = -116.0 + 1.0
EAST_SECT = [(169.23, 205.0), (227.0, 262.0)]   # 1o setor comeca no pilarete final da mureta do trecho (115,0; 169,7)
WEST_SECT = [(185.0, 203.0), (221.0, 239.0)]    # vaos: viela/W2 (y < 185), pavilhao W3 (203..221), W4 (239..)


def _mureta(mb, x, ya, yb, h, th, key, col=True):
    ln = yb - ya
    F = Frame(x, (ya + yb) / 2, ZT, -math.pi / 2 if x > 0 else math.pi / 2)   # +y local = para FORA da praca
    K.parapet(mb, F, ln + 0.6, h, th, key=key, post_every=12.0)
    if col:
        col_box("OP_PlzMureta", (th + 0.3, ln + 0.6, h + 0.6), (x, (ya + yb) / 2, P + (h + 0.6) / 2))


# estandartes no EIXO TRANSVERSAL do emblema (y ~216): entrada do summon (leste) <-> vao do pavilhao W3 (oeste)
BANNERS_E = [(110.6, 201.4), (110.6, 230.6), (-112.6, 200.8), (-112.6, 223.2)]
LAMPS = [(111.6, 186.0), (111.6, 246.0),       # leste: meio dos setores (encostados na mureta)
         (-112.4, 181.0), (-112.4, 243.0),     # oeste: nos vaos da viela/W2 e de W4
         (108.0, 270.0), (-106.0, 258.0),      # cantos NE / NO (entradas do quarteirao NE e do terraco alto)
         (-48.0, 311.2), (48.0, 311.2)]        # norte: ritmo banco - poste - banco ao pe do arrimo do adro
BENCHES = [(-112.9, 194.0, 9.0, math.pi / 2), (-112.9, 230.0, 9.0, math.pi / 2),       # oeste, encostados na mureta
           (112.3, 177.0, 7.0, math.pi / 2), (112.3, 255.0, 7.0, math.pi / 2),         # leste
           (-36.0, 311.4, 7.0, 0.0), (-60.0, 309.4, 7.0, 0.0), (36.0, 311.4, 7.0, 0.0), (60.0, 309.4, 7.0, 0.0),  # norte
           (-94.2, 297.5, 7.0, math.atan2(18.0, 22.0)), (94.2, 297.5, 7.0, -math.atan2(18.0, 22.0))]   # chanfros NO/NE


def build_border():
    mw = MB("OP_Plz_Mureta", "03_PLAZA", random.Random(402), detail="hero")
    for i, (a, b) in enumerate(EAST_SECT):
        _mureta(mw, EAST_X, a, b, 2.3, 1.3, "plzE%d" % i)
    for i, (a, b) in enumerate(WEST_SECT):
        _mureta(mw, WEST_X, a, b, 1.5, 1.1, "plzW%d" % i)
    K.cull_hidden(mw)                                        # M6b: faces que ninguem ve (orcamento)
    mw.finish()
    mp = MB("OP_Prop_Plz_Borda", "09_PROPS", random.Random(403), detail="hero")
    F0 = Frame(0.0, 0.0, 0.0, 0.0)
    for i, (x, y) in enumerate(BANNERS_E):
        ang = -math.pi / 2 if y < 216 else math.pi / 2   # pano para FORA do vao, face para a praca
        K.banner(mp, Frame(x, y, ZT - 0.05, ang), 16.0, K.CWHITE, K.INDIGO, 2.6, 1)
        col_box("OP_PropBanner", (1.9, 1.9, 16.0), (x, y, P + 8.0))
    for i, (x, y) in enumerate(LAMPS):
        K.lantern_box_post(mp, Frame(x, y, ZT - 0.05, 0.0), 7.6, "L_OPProp_Lamp_Plz_%d" % i, 35.0)
        col_box("OP_PropLamp", (1.1, 1.1, 7.6), (x, y, P + 3.8))
    for i, (x, y, ln, ang) in enumerate(BENCHES):
        K.bench(mp, F0, x, y, ln, 1.8, 1.7, ang, ZT - 0.05)
        col_box("OP_PropBench", (ln, 1.8, 1.7), (x, y, P + 0.85), (0.0, 0.0, ang))
    K.cull_hidden(mp)                                        # M6b
    mp.finish()


# ------------------------------------------------------------------ cameras
CAMS = {
    # geral
    "CAM_OP_Plz_Aerea": ((0.0, 40.0, 250.0), (0.0, 222.0, P), 24),
    "CAM_OP_Plz_Zenite": ((0.0, 214.0, 470.0), (0.0, 216.0, P), 32),
    "CAM_OP_Plz_Aerea_NE": ((175.0, 345.0, 190.0), (-10.0, 205.0, P), 24),
    # altura do jogador no centro olhando cada borda
    "CAM_OP_Plz_Centro_N": ((0.0, 226.0, EYE), (0.0, 330.0, P + 9.0), 22),
    "CAM_OP_Plz_Centro_S": ((0.0, 206.0, EYE), (0.0, 100.0, P + 3.0), 22),
    "CAM_OP_Plz_Centro_L": ((10.0, 216.0, EYE), (130.0, 216.0, P + 4.0), 22),
    "CAM_OP_Plz_Centro_O": ((-10.0, 216.0, EYE), (-130.0, 216.0, P + 4.0), 22),
    # bordas na altura do jogador
    "CAM_OP_Plz_Borda_L": ((84.0, 186.0, EYE), (118.0, 236.0, P + 2.0), 22),
    "CAM_OP_Plz_Borda_O": ((-84.0, 244.0, EYE), (-118.0, 196.0, P + 2.0), 22),
    "CAM_OP_Plz_Canto_NO": ((-60.0, 268.0, EYE), (-104.0, 304.0, P + 4.0), 22),
    "CAM_OP_Plz_Canto_NE": ((60.0, 268.0, EYE), (104.0, 300.0, P + 4.0), 22),
    # closes
    "CAM_OP_Plz_Close_Piso": ((30.0, 262.0, P + 3.2), (44.0, 280.0, P), 24),
    "CAM_OP_Plz_Close_Emblema": ((0.0, 186.0, P + 14.0), (0.0, 214.0, P), 26),
    "CAM_OP_Plz_Close_Eixo": ((4.0, 236.0, P + 4.0), (0.0, 262.0, P), 24),
    "CAM_OP_Plz_Close_Mureta": ((96.0, 254.0, P + 4.0), (112.0, 266.0, P + 1.5), 24),
    "CAM_OP_Plz_Close_Estandarte": ((96.0, 188.0, P + 4.0), (111.0, 203.0, P + 9.5), 24),
}


def cams():
    for n, (loc, tgt, lens) in CAMS.items():
        if bpy.data.objects.get(n) is None:
            DL.camera(n, loc, tgt, lens)


def build():
    if bpy.data.objects.get(SENT):
        return
    gone = remove_fallback()
    n = build_floor()
    build_border()
    cams()
    print("op_plaza: %d lajes (piso provisorio removido=%s), mureta %d+%d setores, %d postes, %d bancos, %d estandartes"
          % (n, gone, len(EAST_SECT), len(WEST_SECT), len(LAMPS), len(BENCHES), len(BANNERS_E)))
