# sg_entry - ENTRADA da Ilha 3 (Shadow Garden), 3a na hierarquia: a primeira impressao de quem chega da Ilha 2.
# ONDA 1 (planta v4, plano mestre 2026-09-30, renders/plano_mestre/PLANO.md): o modulo roda DIRETO na v4 (saiu do
# sg_relocate). Da ancora da Ilha 2 ao spawn:
#   PONTE DE CHEGADA CURVA de 234 na polilinha da onda 0 (L.BRIDGE_PATH: 2 retos tangentes ao rumo da Ilha 2, arco de
#   33 graus com raio 160, 140 retos ate o patio baixo), no idioma da ponte aprovada: tabuleiro de LAJES com junta
#   rebaixada (2 tons alternando pela variante), meio-fio de obsidiana, parapeito de CANTARIA (plinto, blocos com junta
#   escura, pingadeira, capa segmentada), cornija sobre mesa de cachorros, 7 ARCOS ogivais com ADUELAS por baixo e
#   PILARES com talha-mar ASSENTADOS EM ROCHAS FLUTUANTES (plato + colunas de basalto pendentes). Tudo e varrido no
#   referencial da curva (s ao longo do eixo, v para a esquerda): a curva e analitica, as juntas acompanham o raio.
#   LANTERNAS SO NOS 3 NOS: comeco (pilaretes da ancora), CURVA (pilar-marco sobre o pilar do fim do arco, com misula)
#   e FIM (pilaretes do canto do patio baixo).
#   -> patio baixo (DECK) -> escadaria (sg_lib.plan_stair "Entry" + muretas de cantaria) -> calcada alta (P1) com o
#   PORTICO DE CHEGADA MONUMENTAL (o portico B aprovado, escalado: fuste 5,2, 30 de altura, agulha octogonal de 14, verga
#   de obsidiana, estandarte da ordem sem espada), a 10 do spawn. O portico A do patio SAIU (orcamento da ponte de 234 e
#   um portico so, monumental; as lanternas acesas dele foram para o no do fim da ponte).
# Colisao PROPRIA so dos pilares do portico. Piso, escada, ponte e guardas: sg_col (congelado).
# Historico da v3 (sg_entry aprovado): refinamentos v1-v3 e overhauls 01/12 (lanternas so nos nos, cantaria de remate
# Stone_SG_TrimLow, agulha octogonal sem piramide, estandarte da ordem so no portico de cima). Os ajudantes de cantaria
# (parapet_run, _post, arcade, lancet, pinnacle, chamfer_sq, finial, yz_block...) sao usados por sg_exit, sg_castle,
# sg_court, sg_village, sg_summon e sg_terrain: a API nao muda.
import math, random
import bmesh
from mathutils import Vector
import sg_lib as SL
import fm_parts as FP
from sg_lib import MB, col_box2, light, Frame, fm_lib
import sg_layout as L
import sg_emblem as EM
if L.__name__ != "sg_layout":
    # importado DENTRO do sg_relocate (um modulo da v3 usa os ajudantes de cantaria daqui, com sys.modules['sg_layout']
    # = sg_layout_v3): este modulo e da planta v4 sempre -> carrega a v4 a parte (fica fora da troca do sg_relocate)
    import importlib.util as _ilu, os as _os
    _sp = _ilu.spec_from_file_location("sg_layout", _os.path.join(_os.path.dirname(_os.path.abspath(__file__)),
                                                                  "sg_layout.py"))
    L = _ilu.module_from_spec(_sp)
    _sp.loader.exec_module(L)

DECK, P1 = L.DECK, L.P1
Y0, Y1 = L.BRIDGE_Y0, L.BRIDGE_Y1          # compat (v4: a ponte e a polilinha L.BRIDGE_PATH; Y1 = -334 fim da ponte)
HW = L.DECK_W / 2.0                        # 9: face interna dos parapeitos / guardas
PAR_Z = DECK - 0.35                        # base dos parapeitos (assentados no corpo do tabuleiro)
PAR_H = 2.0                                # parede do parapeito (+ capa 0,45)
WARM = (1.0, 0.64, 0.34)
# OVERHAUL 01 (2026-09-29): cantaria de REMATE perto do jogador um valor abaixo do Stone_SG_Trim (164 lia plastico
# branco no Roblox; auditoria 14.01): capas, capiteis, molduras e remates. O Stone_SG_Trim fica so no que e alto/longe.
CAP_M = "Stone_SG_TrimLow"
fm_lib.MATS.setdefault(CAP_M, (fm_lib.S(132, 128, 134), 0.8, 0.0, 0, None, 0.06))

# (x do eixo do pilar, secao do fuste, altura do fuste, agulha, largura e altura do estandarte)
PORTICO_A = dict(y=L.PORTICO_A_Y, z=DECK, xc=11.3, s=3.2, H=16.0, spire=7.0, bw=2.6, bh=9.0, name="A")   # (fora: v4)
# ONDA 1: o portico B aprovado, MONUMENTAL (era s 4, H 22, agulha 10): face interna do fuste em 9,8 (colisao 9,5 >= 9,2)
PORTICO_B = dict(y=L.PORTICO_B_Y, z=P1, xc=12.4, s=5.2, H=30.0, spire=14.0, bw=3.4, bh=15.0, name="B")


# ------------------------------------------------------------------ eixo da ponte curva (referencial s, v)
class _Path:
    """eixo analitico da ponte de chegada, reconstruido da polilinha da onda 0: reto P0->P1, arco de raio
    BRIDGE_ARC_R ate o penultimo ponto, reto ate (0, Y_ENTRY). pt(s, v): ponto a s do inicio e v a esquerda."""

    def __init__(self):
        P = L.BRIDGE_PATH
        p0, p1 = Vector((P[0][0], P[0][1], 0.0)), Vector((P[1][0], P[1][1], 0.0))
        pe, pf = Vector((P[-2][0], P[-2][1], 0.0)), Vector((P[-1][0], P[-1][1], 0.0))
        self.p0 = p0
        self.t0 = (p1 - p0).normalized()
        self.s1 = (p1 - p0).length
        t1 = (pf - pe).normalized()
        self.h0 = math.atan2(self.t0.y, self.t0.x)
        self.h1 = math.atan2(t1.y, t1.x)
        d = (self.h1 - self.h0 + math.pi) % (2 * math.pi) - math.pi
        self.sg = 1.0 if d > 0 else -1.0
        self.R = L.BRIDGE_ARC_R
        self.c = p1 + Vector((-self.t0.y, self.t0.x, 0.0)) * self.R * self.sg
        self.a0 = math.atan2(p1.y - self.c.y, p1.x - self.c.x)
        self.s2 = self.s1 + self.R * abs(d)
        a2 = self.a0 + d
        self.pe = self.c + Vector((math.cos(a2), math.sin(a2), 0.0)) * self.R
        self.t1 = t1
        self.S = self.s2 + (pf - self.pe).length

    def head(self, s):
        if s <= self.s1:
            return self.h0
        if s <= self.s2:
            return self.h0 + self.sg * (s - self.s1) / self.R
        return self.h1

    def pt(self, s, v=0.0):
        h = self.head(s)
        if s <= self.s1:
            c = self.p0 + self.t0 * s
        elif s <= self.s2:
            a = self.a0 + self.sg * (s - self.s1) / self.R
            c = self.c + Vector((math.cos(a), math.sin(a), 0.0)) * self.R
        else:
            c = self.pe + self.t1 * (s - self.s2)
        return c + Vector((-math.sin(h), math.cos(h), 0.0)) * v

    def stations(self, sa, sb, step=4.0):
        """estacoes de sa a sb: quebras nos pontos de tangencia; o trecho em arco subdividido a <= step"""
        cuts = sorted({sa, sb} | {x for x in (self.s1, self.s2) if sa < x < sb})
        out = [cuts[0]]
        for a, b in zip(cuts, cuts[1:]):
            n = max(1, int(math.ceil((b - a) / step))) if (a >= self.s1 - 1e-6 and b <= self.s2 + 1e-6) else 1
            out += [a + (b - a) * k / n for k in range(1, n + 1)]
        return out


BP = _Path()
SLEN = BP.S                                  # ~234,1


def W(s, v, z):
    p = BP.pt(s, v)
    return Vector((p.x, p.y, z))


def FR(s, v=0.0):
    """Frame rigido em (s, v): local x ao longo do eixo, y para a esquerda"""
    p = BP.pt(s, v)
    return Frame(p.x, p.y, 0.0, BP.head(s))


# ------------------------------------------------------------------ CAMERAS (v4)
def _cam_sv(s0, v0, z0, s1, v1, z1, lens):
    a, b = W(s0, v0, z0), W(s1, v1, z1)
    return (tuple(round(c, 2) for c in a), tuple(round(c, 2) for c in b), lens)


PIER_S = []                      # preenchido abaixo (eixos dos pilares ao longo de s)
NODE_S = 0.0


def _layout():
    """pilares: 4 tramos iguais antes do no da curva (fim do arco, s2) e 4 depois ate o encontro na falesia"""
    global NODE_S
    NODE_S = BP.s2
    s_first = 4.0
    d0 = (NODE_S - s_first) / 3.0
    out = [s_first + d0 * k for k in range(4)]
    # tramos depois do no: 3 pilares + encontro; vao livre igual (d1 - 2 PIER_HU) em todos, o ultimo ate ABUT_S
    d1 = (ABUT_S - NODE_S + PIER_HU) / 4.0
    out += [NODE_S + d1 * k for k in range(1, 4)]
    return out


PIER_HU = 3.5                    # meia-espessura do pilar ao longo do eixo
ABUT_S = SLEN - 2.2              # face do encontro (falesia) no fim da ponte
PIER_S = _layout()

CAMS = {
    # CHEGADA: da ancora da Ilha 2 (um pouco atras e acima do olho), a ponte curva e o castelo ao fundo
    "CAM_SGEnt_FromAnchor": (tuple(round(c, 2) for c in W(-10.0, 1.5, DECK + 7.5)), (4.0, -400.0, DECK + 20.0), 20),
    # NO MEIO DA CURVA (s 47), altura do jogador pelo lado de fora: o resto do arco virando ate o no e a ilha
    "CAM_SGEnt_MidCurve": _cam_sv(47.0, -5.0, DECK + 5.2, 90.0, 6.0, DECK + 5.0, 20),
    # a CURVA inteira: do comeco, pelo lado de dentro, a ponte virando para a ilha
    "CAM_SGEnt_Curve": _cam_sv(10.0, -3.0, DECK + 6.0, 70.0, 9.0, DECK + 2.0, 20),
    # o no da curva: pilar-marco com a lanterna
    "CAM_SGEnt_Node": _cam_sv(NODE_S - 16.0, -3.0, DECK + 5.2, NODE_S, 10.0, DECK + 3.4, 24),
    # lateral de fora da curva: arcos, pilares e rochas flutuantes
    "CAM_SGEnt_SideCurve": ((96.0, -600.0, 34.0), (-8.0, -470.0, -6.0), 22),
    # de baixo: aduelas, talha-mar e o plato das rochas
    "CAM_SGEnt_Under": ((34.0, -430.0, -34.0), (0.0, -404.0, 14.0), 20),
    # lajes e parapeito de perto (altura do jogador)
    "CAM_SGEnt_Deck": _cam_sv(150.0, -4.5, DECK + 5.2, 162.0, 9.2, DECK + 1.2, 24),
    # fim da ponte: no do fim, patio, escadaria e o portico monumental
    "CAM_SGEnt_End": _cam_sv(200.0, 0.0, DECK + 5.2, 260.0, 0.0, DECK + 16.0, 22),
    # o PORTICO DE CHEGADA: do patio baixo e do pe da escada
    "CAM_SGEnt_Portico": ((6.0, -332.0, DECK + 5.2), (0.0, -282.0, P1 + 24.0), 20),
    "CAM_SGEnt_PorticoNear": ((-5.0, -300.0, P1 + 3.0), (0.0, -282.0, P1 + 16.0), 18),
    # tras: do spawn olhando de volta para a ponte (a curva ao longe)
    "CAM_SGEnt_Back": ((4.0, -262.0, P1 + 6.0), (-10.0, -420.0, DECK + 2.0), 22),
}

# rotas extras: o jogador contorna o pilar do portico por dentro do vao; beiras da ponte (curva inteira) livres
EXTRA_ROUTES = {
    "CALCADA_PORTICO_B_LATERAL": ([(0.0, -292.0), (7.6, -288.0), (7.6, -276.0), (0.0, -270.0)], P1),
    "PONTE_BEIRA_E": ([tuple(BP.pt(s, -7.6))[:2] for s in BP.stations(2.0, SLEN - 1.0, 12.0)], DECK),
    "PONTE_BEIRA_W": ([tuple(BP.pt(s, 7.6))[:2] for s in BP.stations(2.0, SLEN - 1.0, 12.0)], DECK),
}
EXTRA_PROBES = []


# ------------------------------------------------------------------ parapeitos / balaustradas (so visual: guardas no sg_col)
# OVERHAUL 01 (2026-09-29): o parapeito deixa de ser viga + viga. Linguagem unica de cantaria perto do jogador:
#   plinto (base mais larga, 0,45 acima do piso) -> corpo recuado -> ARCADA CEGA na face que o jogador ve (colunelos e
#   timpanos ogivais em relevo de 0,14, um valor acima do corpo) -> pingadeira -> CAPA segmentada (pecas de ~2,4 com
#   junta, cantaria um valor abaixo do Stone_SG_Trim). Pilarete = plinto + toro, fuste de quinas chanfradas, capitel em
#   2 degraus e remate do kit (bola com colar) ou a lanterna da ordem so nos NOS (comeco/fim da ponte e topo da escada).
PAR_M = "Stone_SG_Castle_B"    # corpo dos parapeitos / muretas / pilaretes (um valor abaixo do Stone_SG_Block)
REL_M = "Stone_SG_Block_B"     # relevo (arcada cega, plinto, rodape): um valor acima do corpo
LAN_S = 0.85                   # escala das lanternas nos pilaretes


def _lathe(mb, c, prof, m, n=8, rot=0.0, closed=False):
    EM._lathe(mb, c, prof, m, n, rot, closed)


def finial(mb, x, y, z, r=0.42, m=CAP_M, n=8):
    """remate do kit: bola com colar (torno de 8 lados) assentada em z"""
    prof = [(0.95, 0.0), (0.95, 0.12), (0.48, 0.32), (0.92, 0.56), (1.0, 0.86), (0.70, 1.20), (0.0, 1.40)]
    _lathe(mb, (x, y, z), [(a * r, b * r) for a, b in prof], m, n, math.pi / n)


def chamfer_sq(x, y, hs, c):
    """quadrado de meia-aresta hs com as quinas chanfradas em c (octogono irregular, anti-horario)"""
    return [(x - hs + c, y - hs), (x + hs - c, y - hs), (x + hs, y - hs + c), (x + hs, y + hs - c),
            (x + hs - c, y + hs), (x - hs + c, y + hs), (x - hs, y + hs - c), (x - hs, y - hs + c)]


def _post(mb, x, y, z, size=1.6, h=PAR_H + 0.8, lamp=False, lmb=None, lamp_s=LAN_S):
    """pilarete: plinto + toro, fuste de quinas chanfradas, capitel em 2 degraus (topo em z + h + 0,35) e remate do kit
    (bola com colar) ou a LANTERNA da ordem assentada num prato de obsidiana (onda 1: lmb = objeto da lanterna,
    lamp_s = escala; devolve o centro do vidro)"""
    sp = size + 0.34
    mb.box((sp, sp, 0.55), (x, y, z + 0.275), (0, 0, 0), REL_M, 0.08)
    FP.frustum(mb, (x, y, z + 0.55), sp, sp, size + 0.04, size + 0.04, 0.16, REL_M)
    mb.prism(chamfer_sq(x, y, size / 2, 0.16), z + 0.71, z + h - 0.02, PAR_M)
    mb.box((size + 0.12, size + 0.12, 0.16), (x, y, z + h + 0.06), (0, 0, 0), CAP_M, 0.04)
    mb.box((size + 0.38, size + 0.38, 0.21), (x, y, z + h + 0.245), (0, 0, 0), CAP_M, 0.06)
    zt = z + h + 0.35
    if lamp:
        mb.box((1.12 * lamp_s + 0.1, 1.12 * lamp_s + 0.1, 0.16), (x, y, zt + 0.08), (0, 0, 0), "Stone_SG_Obsidian", 0.04)
        return EM.lantern_head(lmb or mb, lmb or mb, (x, y, zt + 0.16 + EM.LH_BASE * lamp_s), 0.0, lamp_s)
    finial(mb, x, y, zt, 0.44, n=6)
    return None


def face_spandrel(mb, org, d, nrm, arc, ztop, off0, off1, m):
    """timpano em relevo numa face: regiao entre o intradorso 'arc' [(t, z)] e ztop, em faixas convexas; t ao longo
    de d a partir de org, espessura de off0 a off1 ao longo da normal nrm"""
    bm = mb.bm

    def P(t, zz, o):
        return (org.x + d.x * t + nrm.x * o, org.y + d.y * t + nrm.y * o, zz)
    A = [(bm.verts.new(P(t, zz, off0)), bm.verts.new(P(t, ztop, off0))) for t, zz in arc]
    B = [(bm.verts.new(P(t, zz, off1)), bm.verts.new(P(t, ztop, off1))) for t, zz in arc]
    faces = []
    for i in range(len(arc) - 1):
        faces.append(bm.faces.new((A[i][0], A[i + 1][0], A[i + 1][1], A[i][1])))
        faces.append(bm.faces.new((B[i][0], B[i][1], B[i + 1][1], B[i + 1][0])))
        faces.append(bm.faces.new((A[i][0], B[i][0], B[i + 1][0], A[i + 1][0])))
        faces.append(bm.faces.new((A[i][1], A[i + 1][1], B[i + 1][1], B[i][1])))
    for k in (0, -1):
        faces.append(bm.faces.new((A[k][0], A[k][1], B[k][1], B[k][0])))
    import bmesh
    bmesh.ops.recalc_face_normals(bm, faces=faces)
    mb._post([v for p in A + B for v in p], m, None, 0, 1)


def pointed_arc(t0, t1, zs, rise, n=3):
    """intradorso ogival abatido de t0 a t1 (nascencas em zs, fecho em zs + rise): 2 arcos de raio 0,6 do vao
    achatados na vertical"""
    span = t1 - t0
    R = 0.6 * span
    phi = math.acos((0.5 * span - R) / R)
    k = rise / (R * math.sin(phi))
    left = []
    for i in range(n + 1):
        th = math.pi - (math.pi - phi) * i / n
        left.append((t0 + R + R * math.cos(th), zs + k * R * math.sin(th)))
    right = [(t0 + t1 - t, zz) for t, zz in reversed(left[:-1])]
    left[-1] = ((t0 + t1) / 2, zs + rise)
    return left + right


def arcade(mb, pa, pb, nrm, z, th, clear=()):
    """arcada cega em relevo na face 'nrm' do trecho pa->pb (eixo do muro): colunelos + timpanos ogivais.
    clear = [(t0, t1)] trechos ocupados por pilaretes (a arcada se divide entre eles)"""
    d = (pb - pa)
    Ltot = d.length
    d.normalize()
    off0, dep = th / 2 - 0.02, 0.14
    zp, zt = z + 0.8, z + PAR_H - 0.02
    free = []
    cur = 0.0
    for c0, c1 in sorted(clear):
        if c0 > cur + 0.6:
            free.append((cur, c0))
        cur = max(cur, c1)
    if Ltot > cur + 0.6:
        free.append((cur, Ltot))
    rib = 0.22
    for f0, f1 in free:
        nb = max(1, int(round((f1 - f0) / 2.3)))
        w = (f1 - f0) / nb
        ang = math.atan2(d.y, d.x)
        for k in range(nb + 1):
            t = f0 + k * w
            t = min(max(t, f0 + rib / 2), f1 - rib / 2)
            c = pa + d * t + nrm * (off0 + dep / 2)
            mb.box((rib, dep, zt - zp), (c.x, c.y, (zp + zt) / 2), (0, 0, ang), REL_M, 0.0)
        for k in range(nb):
            t0, t1 = f0 + k * w + rib / 2, f0 + (k + 1) * w - rib / 2
            if k == 0:
                t0 = max(t0, f0 + rib)
            if k == nb - 1:
                t1 = min(t1, f1 - rib)
            if t1 - t0 < 0.5:
                continue
            arc = pointed_arc(t0, t1, zt - 0.62, 0.46, 2)
            face_spandrel(mb, pa, d, nrm, arc, zt, off0, off0 + dep, REL_M)


def parapet_run(mb, pts, z, th=1.2, extra=(), skip=(), post=1.6, lit=()):
    """parapeito de cantaria ao longo da polilinha (eixos alinhados): plinto, corpo, arcada cega na face vista (a do
    eixo nos trechos ao longo de Y; as duas nos trechos curtos ao longo de X), pingadeira e capa segmentada. Pilaretes
    SO nos vertices (pontas e cantos) e nos pontos 'extra'. 'lit' = indices dos vertices cujo pilarete leva lanterna;
    extra = [(x, y)] ou [(x, y, lamp)]. As pontas NAO passam do primeiro/ultimo ponto (a ponta sul da ponte fica em
    y -262 exato). O topo da capa fica em z + PAR_H + 0,445 (o mesmo de antes)."""
    n = len(pts)
    zc = z + PAR_H
    posts = []
    for i, p in enumerate(pts):
        pv = Vector((p[0], p[1], 0))
        if any((pv - Vector((q[0], q[1], 0))).length < r for q, r in skip):
            continue
        q = Vector(pv)
        if i == 0:
            q += (Vector((*pts[1], 0)) - Vector((*pts[0], 0))).normalized() * (post / 2 + 0.16)
        elif i == n - 1:
            q += (Vector((*pts[-2], 0)) - Vector((*pts[-1], 0))).normalized() * (post / 2 + 0.16)
        posts.append((q, i in lit))
    for p in extra:
        posts.append((Vector((p[0], p[1], 0)), len(p) > 2 and p[2]))
    for i in range(n - 1):
        a, b = Vector((*pts[i], 0)), Vector((*pts[i + 1], 0))
        d = (b - a).normalized()
        ea = a - d * (th / 2 if i > 0 else 0.0)
        eb = b + d * (th / 2 if i < n - 2 else 0.0)
        mb.beam((ea.x, ea.y, z + PAR_H / 2), (eb.x, eb.y, z + PAR_H / 2), th, PAR_H, PAR_M, 0.0)
        mb.beam((ea.x, ea.y, z + 0.4), (eb.x, eb.y, z + 0.4), th + 0.34, 0.8, REL_M, 0.06)        # plinto
        mb.beam((ea.x, ea.y, zc + 0.06), (eb.x, eb.y, zc + 0.06), th + 0.16, 0.12, CAP_M, 0.0)   # pingadeira
        Ls = (eb - ea).length
        k = max(1, int(round(Ls / 2.4)))
        for j in range(k):
            pa_ = ea + d * (Ls * j / k + (0.03 if j else 0.0))
            pb_ = ea + d * (Ls * (j + 1) / k - (0.03 if j < k - 1 else 0.0))
            mb.beam((pa_.x, pa_.y, zc + 0.285), (pb_.x, pb_.y, zc + 0.285), th + 0.42, 0.33, CAP_M, 0.07)
        # arcada: trechos ocupados pelos pilaretes deste trecho
        clear = []
        for q, _ in posts:
            t = (q - ea).dot(d)
            dist = (q - (ea + d * t)).length
            if dist < 0.8 and -1.5 < t < Ls + 1.5:
                clear.append((t - (post + 0.34) / 2 - 0.05, t + (post + 0.34) / 2 + 0.05))
        nrm = Vector((-d.y, d.x, 0.0))
        if abs(d.x) < 0.3:
            faces = [nrm if nrm.x * a.x < 0 else -nrm]
        else:
            faces = [nrm, -nrm]
        for f in faces:
            arcade(mb, ea, eb, f, z, th, clear)
    for q, lamp in posts:
        _post(mb, q.x, q.y, z, post, lamp=lamp)


def yz_block(mb, x0, x1, pts, m, bevel=0.0):
    """poligono CONVEXO no plano YZ [(y, z)] extrudado de x0 a x1 (com chanfro opcional)"""
    bm = mb.bm
    va = [bm.verts.new((x0, y, z)) for y, z in pts]
    vb = [bm.verts.new((x1, y, z)) for y, z in pts]
    n = len(pts)
    faces = [bm.faces.new(list(reversed(va))), bm.faces.new(vb)]
    for i in range(n):
        j = (i + 1) % n
        faces.append(bm.faces.new((va[i], va[j], vb[j], vb[i])))
    import bmesh
    bmesh.ops.recalc_face_normals(bm, faces=faces)
    mb._post(va + vb, m, None, bevel, 1)


def _dedupe(poly, eps=1e-3):
    out = []
    for p in poly:
        if not out or abs(p[0] - out[-1][0]) + abs(p[1] - out[-1][1]) > eps:
            out.append((p[0], p[1]))
    while len(out) > 1 and abs(out[0][0] - out[-1][0]) + abs(out[0][1] - out[-1][1]) <= eps:
        out.pop()
    return out


def _clip_y(poly, ya, yb):
    p = SL.clip(poly, 1.0, 0.0, yb)
    return SL.clip(p, -1.0, 0.0, -ya)


def stair_wall(mb, mh, s):
    """banzo da escadaria (mureta inclinada de cada lado, face interna em |x| = 9 = guarda do sg_col):
    paramento de CANTARIA em fiadas horizontais alternadas (1,2 / 0,9) com juntas desencontradas e chanfro (a junta le
    rebaixada), rodape inclinado na face da escada (acompanha os focinhos), capa inclinada em pecas com junta e
    pingadeira, e os pilaretes de arranque (pe: remate do kit; topo: lanterna)"""
    ya, yb = L.ENTRY_STAIR[1], L.ENTRY_STAIR_Y1          # -206 .. -188
    ta, tb = PAR_Z + PAR_H + 0.35, P1 - 0.35 + PAR_H + 0.35
    k = (tb - ta) / (yb - ya)
    x0, x1 = sorted((s * HW, s * (HW + 1.4)))
    zb = DECK - 1.5
    hs = (1.2, 0.9)
    c0, ci = zb, 0
    while c0 < tb - 0.05:
        c1 = min(c0 + hs[ci % 2], tb)
        # fiada: faixa [c0, c1] sob a linha inclinada z = ta + k (y - ya)
        if c1 <= ta:
            poly = [(ya, c0), (yb, c0), (yb, c1), (ya, c1)]
        else:
            ys0 = ya + max(0.0, (c0 - ta) / k)
            ys1 = ya + (c1 - ta) / k
            poly = [(ys0, c0), (yb, c0), (yb, c1), (ys1, c1)]
            if c0 < ta:
                poly.append((ya, ta))
        # blocos de ~2,6 com juntas desencontradas fiada a fiada
        L0 = 2.6
        off = (0.0, 1.3)[ci % 2]
        cuts = [ya] + [ya + off + L0 * j for j in range(1, 9) if ya + off + L0 * j < yb - 0.8] + [yb]
        for u0, u1 in zip(cuts, cuts[1:]):
            bp = _dedupe(_clip_y(poly, u0 + 0.03, u1 - 0.03))
            if len(bp) >= 3 and abs(SL.area(bp)) > 0.2 and max(p[0] for p in bp) - min(p[0] for p in bp) > 0.3:
                yz_block(mh, x0, x1, bp, PAR_M, 0.07)
        c0, ci = c1, ci + 1
    # rodape inclinado na face da escada: a aresta de baixo passa 0,08 acima dos focinhos
    foot, deg, w, n, tread, g = L.stair_frame("Entry")
    rise = (L.STAIR_TOP_Z["Entry"] - foot[2]) / n

    def zn(y):
        return foot[2] + rise + (y - ya) * rise / tread
    xr = s * (HW - 0.08)
    ra, rb = ya + 0.1, yb - 0.1
    mb.beam((xr, ra, zn(ra) + 0.42), (xr, rb, zn(rb) + 0.42), 0.2, 0.62, REL_M, 0.04)

    # capa inclinada em pecas (junta a cada ~2,5) + pingadeira
    def zl(y):
        return ta + k * (y - ya)
    xm = s * (HW + 0.7)
    A = Vector((xm, ya - 0.2, zl(ya - 0.2)))
    B = Vector((xm, yb + 0.2, zl(yb + 0.2)))
    dd = B - A
    nseg = max(1, int(round(dd.length / 2.5)))
    for j in range(nseg):
        p0 = A + dd * (j / nseg) + dd.normalized() * (0.03 if j else 0.0)
        p1 = A + dd * ((j + 1) / nseg) - dd.normalized() * (0.03 if j < nseg - 1 else 0.0)
        mb.beam((p0.x, p0.y, p0.z + 0.28), (p1.x, p1.y, p1.z + 0.28), 1.8, 0.36, CAP_M, 0.07)
    mb.beam((xm, A.y + 0.1, A.z + 0.1 * k + 0.04), (xm, B.y - 0.1, B.z - 0.1 * k + 0.04), 1.58, 0.14, CAP_M, 0.0)
    # arranque (pe e topo: dado com remate do kit). OVERHAUL 12 (12.04): a lanterna do topo SAIU - a 9 studs dela a
    # lanterna baixa do portico B ja marca o mesmo no (2 lanternas por lado lia cacho)
    _post(mb, s * (HW + 0.8), ya + 0.4, PAR_Z, 1.6, PAR_H + 1.3, lamp=False)
    _post(mb, s * (HW + 0.8), yb - 0.6, P1 - 0.35, 1.6, PAR_H + 1.3, lamp=False)



# ------------------------------------------------------------------ ONDA 1: PONTE CURVA (geometria no referencial s, v)
BODY = 10.2                     # meia-largura do corpo do tabuleiro (= face externa do parapeito)
SOFFIT = 25.4                   # fundo do tabuleiro
BTOP = DECK - 0.45              # topo do corpo = LEITO escuro das juntas (0,45 abaixo das lajes)
PZ = BTOP                       # base do parapeito da ponte (plinto embute 0,05 no corpo)
ZS = 4.0                        # nascenca de TODOS os arcos (arco de 2 centros: a flecha e fixa, o vao muda)
ZK = SOFFIT - 1.3               # intradorso no fecho
ZTOP_SP = SOFFIT + 0.2          # topo do timpano (dentro do corpo)
CURB = 1.1
BED_M, PAVE_M, CURB_M = "Stone_SG_Floor", "Stone_Paving_SG", "Stone_SG_Obsidian"
BODY_M, ROCK_M, ROCKD_M = "Stone_SG_Block", "Cliff_Rock_SG", "Cliff_Rock_SG_Dark"
# rochas flutuantes: cota do plato sob cada pilar (variacao DIRIGIDA: sobe para o meio do vao grande e desce nas pontas)
ROCK_Z = (-8.0, -13.0, -10.5, -15.0, -11.0, -14.0, -9.5)


def quad_sv(mb, pts, m):
    """face solta a partir de [(s, v, z)]"""
    vs = [mb.bm.verts.new(W(*p)) for p in pts]
    mb.bm.faces.new(vs)
    mb._post(vs, m, None, 0, 1)


def box_sv(mb, s0, s1, v0, v1, z0, z1, m, bottom=False, top=True, ends=(True, True), bev=0.0, top_m=None):
    """caixa 'curva' entre as estacoes s0..s1 (curtas: cantos no eixo curvo), v0..v1, z0..z1. Sem fundo por padrao
    (sempre assentada em alguma coisa). ends = faces em s0 / s1."""
    bm = mb.bm
    c = [(s0, v0), (s1, v0), (s1, v1), (s0, v1)]
    lo = [bm.verts.new(W(s, v, z0)) for s, v in c]
    hi = [bm.verts.new(W(s, v, z1)) for s, v in c]
    fs = []
    if top:
        fs.append(bm.faces.new(hi))
    if bottom:
        fs.append(bm.faces.new(list(reversed(lo))))
    for i in range(4):
        j = (i + 1) % 4
        if (i == 3 and not ends[0]) or (i == 1 and not ends[1]):
            continue
        fs.append(bm.faces.new((lo[i], lo[j], hi[j], hi[i])))
    bmesh.ops.recalc_face_normals(bm, faces=fs)
    mb._post(lo + hi, m, None, bev, 1)
    if top and top_m:
        fs[0].material_index = mb._mi_for(top_m)


def sweep_sv(mb, sa, sb, prof, m, mats=None, caps=(True, True), step=6.0):
    """varre o perfil fechado [(v, z)] de sa a sb pelo eixo curvo; mats[i] = material da face do lado i -> i+1"""
    bm = mb.bm
    rings = [[bm.verts.new(W(s, v, z)) for v, z in prof] for s in BP.stations(sa, sb, step)]
    n = len(prof)
    per = {}
    fs = []
    for r0, r1 in zip(rings, rings[1:]):
        for i in range(n):
            j = (i + 1) % n
            f = bm.faces.new((r0[i], r0[j], r1[j], r1[i]))
            fs.append(f)
            if mats:
                per.setdefault(mats[i], []).append(f)
    if caps[0]:
        fs.append(bm.faces.new(list(reversed(rings[0]))))
    if caps[1]:
        fs.append(bm.faces.new(rings[-1]))
    bmesh.ops.recalc_face_normals(bm, faces=fs)
    mb._post([v for r in rings for v in r], m, None, 0, 1)
    for mm, ff in per.items():
        if mm != m:
            mi = mb._mi_for(mm)
            for f in ff:
                f.material_index = mi


def prism_f(mb, F, pts, z0, z1, m, top=True, bottom=False):
    """prisma vertical de um poligono local [(u, v)] no Frame F"""
    bm = mb.bm
    w = SL.ccw([tuple(F.p(u, v, 0.0))[:2] for u, v in pts])
    lo = [bm.verts.new((x, y, z0)) for x, y in w]
    hi = [bm.verts.new((x, y, z1)) for x, y in w]
    fs = []
    if top:
        fs.append(bm.faces.new(hi))
    if bottom:
        fs.append(bm.faces.new(list(reversed(lo))))
    n = len(w)
    for i in range(n):
        j = (i + 1) % n
        fs.append(bm.faces.new((lo[i], lo[j], hi[j], hi[i])))
    mb._post(lo + hi, m, None, 0, 1)


def loft_f(mb, F, poly0, z0, poly1, z1, m, top=False):
    """tronco entre 2 poligonos locais (mesmo numero de vertices, anti-horario)"""
    bm = mb.bm
    v0 = [bm.verts.new(F.p(u, v, z0)) for u, v in poly0]
    v1 = [bm.verts.new(F.p(u, v, z1)) for u, v in poly1]
    n = len(v0)
    fs = []
    if top:
        fs.append(bm.faces.new(v1))
    for i in range(n):
        j = (i + 1) % n
        fs.append(bm.faces.new((v0[i], v0[j], v1[j], v1[i])))
    bmesh.ops.recalc_face_normals(bm, faces=fs)
    mb._post(v0 + v1, m, None, 0, 1)


def pier_poly(hv, hu, tip):
    """planta do pilar no Frame do eixo: retangulo (hu ao longo, hv atravessado) com talha-mar em ponta nos 2 lados"""
    return [(0.0, -hv - tip), (hu, -hv), (hu, hv), (0.0, hv + tip), (-hu, hv), (-hu, -hv)]


def ogive2(t0, t1, zs, rise, n=6):
    """arco ogival de 2 centros de t0 a t1 com nascenca zs e FLECHA fixa 'rise' (o vao muda, a altura nao):
    [(t, z)] do pe t0 ao pe t1 e os 2 centros"""
    w = t1 - t0
    R = (rise * rise + w * w / 4.0) / w
    tha = math.acos(max(-1.0, min(1.0, (w / 2.0 - R) / R)))
    left = [(t0 + R + R * math.cos(math.pi - (math.pi - tha) * k / n),
             zs + R * math.sin(math.pi - (math.pi - tha) * k / n)) for k in range(n + 1)]
    left[-1] = ((t0 + t1) / 2.0, zs + rise)
    right = [(t0 + t1 - t, z) for t, z in reversed(left[:-1])]
    return left + right, (t0 + R, zs), (t1 - R, zs)


def arch(mb, t0, t1):
    """timpano macico (intradorso + 2 faces a |v| 9,4) e ADUELAS radiais salientes nas 2 faces + fecho"""
    n = 5
    arc, cL, cR = ogive2(t0, t1, ZS, ZK - ZS, n)
    bm = mb.bm
    A = [(bm.verts.new(W(t, -9.4, z)), bm.verts.new(W(t, -9.4, ZTOP_SP))) for t, z in arc]
    B = [(bm.verts.new(W(t, 9.4, z)), bm.verts.new(W(t, 9.4, ZTOP_SP))) for t, z in arc]
    fs = []
    for i in range(len(arc) - 1):
        fs.append(bm.faces.new((A[i][0], A[i + 1][0], A[i + 1][1], A[i][1])))
        fs.append(bm.faces.new((B[i][0], B[i][1], B[i + 1][1], B[i + 1][0])))
        fs.append(bm.faces.new((A[i][0], B[i][0], B[i + 1][0], A[i + 1][0])))
    bmesh.ops.recalc_face_normals(bm, faces=fs)
    mb._post([v for p in A + B for v in p], BODY_M, None, 0, 1)
    band = 1.3
    for sd in (-1, 1):
        va, vb = sorted((sd * 9.3, sd * 9.8))
        for i in range(len(arc) - 1):
            (u0, z0), (u1, z1) = arc[i], arc[i + 1]
            c = cL if i < n else cR
            du, dz = u1 - u0, z1 - z0
            dl = math.hypot(du, dz)
            eu, ez = du / dl * 0.05, dz / dl * 0.05
            n0 = ((u0 - c[0]), (z0 - c[1]))
            n1 = ((u1 - c[0]), (z1 - c[1]))
            l0, l1 = math.hypot(*n0), math.hypot(*n1)
            n0, n1 = (n0[0] / l0, n0[1] / l0), (n1[0] / l1, n1[1] / l1)
            q = [(u0 + eu - n0[0] * 0.08, z0 + ez - n0[1] * 0.08), (u1 - eu - n1[0] * 0.08, z1 - ez - n1[1] * 0.08),
                 (u1 - eu + n1[0] * band, z1 - ez + n1[1] * band), (u0 + eu + n0[0] * band, z0 + ez + n0[1] * band)]
            # a aduela de arranque entra no pilar: a face de tras fica 0,15 DENTRO dele (nunca rente a face do pilar)
            q = [(max(t0 - 0.15, min(t1 + 0.15, t)), z) for t, z in q]
            _tz_block(mb, q, va, vb, CAP_M)
        ap = arc[n]
        _tz_block(mb, [(ap[0] - 0.6, ap[1] - 0.3), (ap[0] + 0.6, ap[1] - 0.3), (ap[0] + 0.85, ap[1] + band + 0.5),
                       (ap[0] - 0.85, ap[1] + band + 0.5)], va - 0.06, vb + 0.06, CAP_M)          # fecho


def _tz_block(mb, q, v0, v1, m):
    """poligono CONVEXO [(s, z)] no plano do arco, extrudado de v0 a v1 (atravessado) sobre o eixo curvo"""
    bm = mb.bm
    va = [bm.verts.new(W(t, v0, z)) for t, z in q]
    vb = [bm.verts.new(W(t, v1, z)) for t, z in q]
    fs = [bm.faces.new(va), bm.faces.new(list(reversed(vb)))]
    k = len(q)
    for i in range(k):
        j = (i + 1) % k
        fs.append(bm.faces.new((va[i], va[j], vb[j], vb[i])))
    bmesh.ops.recalc_face_normals(bm, faces=fs)
    mb._post(va + vb, m, None, 0, 1)


def hexcol_f(mb, F, cu, cv, r, zt, zb, rot, m, tip=0.0, band=None):
    """coluna de basalto hexagonal pendente no Frame F; band = (z, fator, material) estrato com ressalto"""
    bm = mb.bm

    def ring(rr, z):
        return [bm.verts.new(F.p(cu + rr * math.cos(rot + k * math.pi / 3), cv + rr * math.sin(rot + k * math.pi / 3),
                                 z)) for k in range(6)]
    seq, mats = [ring(r, zt)], []
    if band and zb + 1.0 < band[0] < zt - 1.0:
        seq.append(ring(r, band[0]))
        mats.append(m)
        seq.append(ring(r * band[1], band[0]))
        mats.append(band[2])
        seq.append(ring(r * band[1] * 0.93, zb))
        mats.append(band[2])
    else:
        seq.append(ring(r * 0.9, zb))
        mats.append(m)
    groups = {}
    for (a, b), mm in zip(zip(seq, seq[1:]), mats):
        for k in range(6):
            k2 = (k + 1) % 6
            groups.setdefault(mm, []).append(bm.faces.new((a[k2], a[k], b[k], b[k2])))
    last, lm = seq[-1], mats[-1]
    allv = [v for rg in seq for v in rg]
    if tip > 0:
        c = sum((v.co for v in last), Vector()) / 6
        apex = bm.verts.new((c.x, c.y, zb - tip))
        allv.append(apex)
        for k in range(6):
            groups.setdefault(lm, []).append(bm.faces.new((last[(k + 1) % 6], last[k], apex)))
    else:
        groups.setdefault(lm, []).append(bm.faces.new(list(reversed(last))))
    fs = [f for ff in groups.values() for f in ff]
    bmesh.ops.recalc_face_normals(bm, faces=fs)
    mb._post(allv, m, None, 0, 1)
    for mm, ff in groups.items():
        if mm != m:
            mi = mb._mi_for(mm)
            for f in ff:
                f.material_index = mi


def rock(mb, F, zr, k):
    """ROCHA FLUTUANTE sob o pilar: plato de basalto (topo em zr, lobos dirigidos) e colunas hexagonais pendentes -
    3 grossas e fundas no miolo (com estrato escuro) e um anel de colunas medias que afinam para a borda"""
    ph = 0.9 * k
    ru, rv = 8.6, 16.2
    poly = []
    for i in range(10):
        a = 2 * math.pi * i / 10 + ph * 0.2
        kk = 1.0 + 0.10 * math.sin(3 * a + ph) + 0.05 * math.sin(5 * a + 2 * ph)
        poly.append((ru * kk * math.cos(a), rv * kk * math.sin(a)))
    prism_f(mb, F, poly, zr - 2.6, zr, ROCK_M)
    prim = [(0.0, 0.0, 4.6, 30.0 + 4.0 * math.sin(ph), 8.0), (0.6, 7.6, 3.9, 22.0 + 3.0 * math.cos(ph), 6.0),
            (-0.6, -7.4, 4.0, 25.0 - 3.0 * math.sin(ph * 1.3), 7.0)]
    for j, (cu, cv, r, dep, tip) in enumerate(prim):
        hexcol_f(mb, F, cu, cv, r, zr - 2.2, zr - 2.2 - dep, 0.3 * j + ph, ROCK_M, tip,
                 band=(zr - 2.2 - dep * 0.45, 0.84, ROCKD_M))
    for i in range(6):
        a = 2 * math.pi * (i + 0.5) / 6 + ph * 0.2
        cu, cv = 0.62 * ru * math.cos(a), 0.66 * rv * math.sin(a)
        r = 2.3 + 0.5 * math.sin(2 * a + ph)
        dep = 9.0 + 5.0 * abs(math.sin(a)) + 3.0 * math.sin(3 * a + ph)
        hexcol_f(mb, F, cu, cv, r, zr - 2.2, zr - 2.2 - dep, a + ph, ROCKD_M if i % 3 == 0 else ROCK_M,
                 2.0 + 1.5 * abs(math.cos(a + ph)))


def pier(mb, s, zr, k):
    """pilar com talha-mar nos 2 lados, em 4 estagios (base sobre a rocha, fuste que alarga ate a IMPOSTA na nascenca
    dos arcos, fuste reto e capeamento das pontas sob a cornija) + quinas claras nos bicos"""
    F = FR(s)
    prism_f(mb, F, pier_poly(8.9, 3.9, 3.2), zr - 0.4, zr + 0.8, CAP_M)                     # base (embute no plato)
    loft_f(mb, F, pier_poly(8.4, 3.3, 2.8), zr + 0.8, pier_poly(9.2, 3.4, 3.1), ZS - 0.8, BODY_M)
    prism_f(mb, F, pier_poly(9.8, 3.85, 3.5), ZS - 0.8, ZS, CAP_M)                           # imposta
    prism_f(mb, F, pier_poly(9.4, PIER_HU, 3.2), ZS, SOFFIT - 0.8, BODY_M, top=False)
    loft_f(mb, F, pier_poly(9.4, PIER_HU, 3.2), SOFFIT - 0.8, pier_poly(9.4, PIER_HU, 0.9), SOFFIT + 0.5, CAP_M)
    for sv in (-1, 1):
        a, b = F.p(0.0, sv * (8.4 + 2.8 - 0.2), zr + 0.8), F.p(0.0, sv * (9.2 + 3.1 - 0.2), ZS - 0.8)
        mb.beam(a, b, 0.5, 0.5, CAP_M, 0.0)
        mb.beam(F.p(0.0, sv * (9.4 + 3.2 - 0.15), ZS), F.p(0.0, sv * (9.4 + 3.2 - 0.15), SOFFIT - 0.8), 0.5, 0.5, CAP_M,
                0.0)
    rock(mb, F, zr, k)


def abutment(mb):
    """encontro na falesia: bloco do fundo do ultimo arco ate dentro do penhasco (a face dele recebe o arco)"""
    box_sv(mb, ABUT_S, SLEN + 4.0, -BODY - 0.4, BODY + 0.4, ZS - 6.0, SOFFIT + 0.3, BODY_M, bottom=True, ends=(True, False))
    box_sv(mb, ABUT_S - 0.3, ABUT_S + 0.9, -BODY - 0.6, BODY + 0.6, ZS - 0.8, ZS, CAP_M, ends=(True, False))


def deck(mb, rng):
    """corpo (topo = leito escuro das juntas), cornija corrida, meio-fio de obsidiana e as LAJES em
    fiadas atravessadas com juntas desencontradas (fiada de 2,6; pecas de 3,2 / 3,8 / 4,4; junta de 0,18)"""
    sweep_sv(mb, 0.0, SLEN + 2.0, [(-BODY, SOFFIT), (BODY, SOFFIT), (BODY, BTOP), (-BODY, BTOP)], BODY_M,
             mats=[BODY_M, BODY_M, BED_M, BODY_M], caps=(True, False))
    for sd in (-1, 1):
        v0, v1 = sorted((sd * (BODY - 0.1), sd * (BODY + 0.55)))
        sweep_sv(mb, 0.0, SLEN + 2.0, [(v0, 25.9), (v1, 25.9), (v1, 26.75), (v0, 26.75)], CAP_M, caps=(True, False))
        s = 0.0
        while s < SLEN - 0.05:
            se = min(s + 5.2, SLEN)
            va, vb = sorted((sd * HW, sd * (HW - CURB)))
            box_sv(mb, s + 0.07, se - 0.07, va, vb, DECK - 0.55, DECK, CURB_M)
            s = se
    hwp = HW - CURB
    row = 2.6
    s, k = 0.0, 0
    while s < SLEN - 0.05:
        se = min(s + row, SLEN)
        v = -hwp - (1.5 if k % 2 else 0.0)
        while v < hwp - 0.05:
            w = rng.choice((3.2, 3.8, 4.4))
            va, vb = max(v, -hwp), min(v + w, hwp)
            if vb - va > 0.6:
                h = rng.uniform(-0.02, 0.015)
                box_sv(mb, s + 0.09, se - 0.09, va + 0.09, vb - 0.09, DECK - 0.55, DECK + h, PAVE_M)
            v += w
        s, k = se, k + 1


def post_sv(mb, lmb, s, v, z, size=1.6, h=PAR_H + 0.8, lamp=0.0, bracket=False):
    """pilarete do kit (plinto + toro, fuste de quinas chanfradas, capitel em 2 degraus) alinhado ao eixo curvo; remate
    do kit ou a LANTERNA da ordem (lamp = escala; a lanterna vai no objeto lmb). bracket: misula sob a parte que sai do
    corpo do tabuleiro (pilar-marco). Devolve o centro do vidro (ou None)."""
    F = FR(s, v)
    sp = size + 0.34
    mb.box((sp, sp, 0.55), F.p(0, 0, z + 0.275), F.r(), REL_M, 0.08)
    FP.frustum(mb, F.p(0, 0, z + 0.55), sp, sp, size + 0.04, size + 0.04, 0.16, REL_M, ang=F.a)
    mb.prism([tuple(F.p(x, y, 0.0))[:2] for x, y in chamfer_sq(0.0, 0.0, size / 2, 0.16)], z + 0.71, z + h - 0.02, PAR_M)
    mb.box((size + 0.12, size + 0.12, 0.16), F.p(0, 0, z + h + 0.06), F.r(), CAP_M, 0.04)
    mb.box((size + 0.38, size + 0.38, 0.21), F.p(0, 0, z + h + 0.245), F.r(), CAP_M, 0.06)
    zt = z + h + 0.35
    if bracket:
        # pilar-MARCO: friso no meio do fuste (le o no de longe) e misula sob a parte que sai do corpo
        mb.box((size + 0.3, size + 0.3, 0.34), F.p(0, 0, z + 0.71 + (h - 0.71) * 0.55), F.r(), CAP_M, 0.05)
        sgn = 1.0 if v > 0 else -1.0
        vo = abs(v) + sp / 2 - BODY                            # quanto o plinto sai do corpo
        q = [(0.0, z + 0.02), (vo + 0.1, z + 0.02), (vo + 0.1, z - 0.7), (0.0, 26.75 - 0.02)]
        Fb = FR(s, sgn * BODY)
        bm = mb.bm
        va = [bm.verts.new(Fb.p(-sp / 2 + 0.1, sgn * (dv - 0.1), zz)) for dv, zz in q]
        vb = [bm.verts.new(Fb.p(sp / 2 - 0.1, sgn * (dv - 0.1), zz)) for dv, zz in q]
        fs = [bm.faces.new(va), bm.faces.new(list(reversed(vb)))]
        for i in range(4):
            j = (i + 1) % 4
            fs.append(bm.faces.new((va[i], va[j], vb[j], vb[i])))
        bmesh.ops.recalc_face_normals(bm, faces=fs)
        mb._post(va + vb, CAP_M, None, 0, 1)
    if lamp:
        c = F.p(0, 0, 0)
        mb.box((1.12 * lamp + 0.1, 1.12 * lamp + 0.1, 0.16), F.p(0, 0, zt + 0.08), F.r(), "Stone_SG_Obsidian", 0.04)
        return EM.lantern_head(lmb, lmb, (c.x, c.y, zt + 0.16 + EM.LH_BASE * lamp), F.a + math.pi / 2, lamp)
    c = F.p(0, 0, 0)
    finial(mb, c.x, c.y, zt, 0.44, n=6)
    return None


def bridge_parapet(mb, sa, sb, sd):
    """parapeito de CANTARIA de sa a sb num lado: plinto e pingadeira varridos, miolo escuro recuado 0,15 e BLOCOS
    de ~3 com junta de 0,1 na frente dele, capa em pecas de ~3 com junta (topo no mesmo z da cantaria da v3)"""
    zp1, zc = DECK + 0.45, DECK + 1.65
    vc = HW + 0.6

    def V(a, b):
        return sorted((sd * (vc + a), sd * (vc + b)))
    a_, b_ = V(-0.77, 0.77)
    sweep_sv(mb, sa, sb, [(a_, PZ - 0.05), (b_, PZ - 0.05), (b_, zp1), (a_, zp1)], REL_M, caps=(False, False))
    a_, b_ = V(-0.45, 0.45)
    sweep_sv(mb, sa, sb, [(a_, zp1 - 0.02), (b_, zp1 - 0.02), (b_, zc - 0.03), (a_, zc - 0.03)], CURB_M,
             caps=(False, False))                   # miolo: topo 0,15 abaixo do topo da pingadeira (z-fight)
    a_, b_ = V(-0.68, 0.68)
    sweep_sv(mb, sa, sb, [(a_, zc), (b_, zc), (b_, zc + 0.12), (a_, zc + 0.12)], CAP_M, caps=(False, False))
    n = max(1, int(round((sb - sa) / 3.0)))
    ln = (sb - sa) / n
    a_, b_ = V(-0.6, 0.6)
    for j in range(n):
        box_sv(mb, sa + ln * j + (0.05 if j else 0.0), sa + ln * (j + 1) - (0.05 if j < n - 1 else 0.0), a_, b_, zp1,
               zc, PAR_M, top=False)
    n = max(1, int(round((sb - sa) / 3.0)))
    ln = (sb - sa) / n
    a_, b_ = V(-0.81, 0.81)
    for j in range(n):
        box_sv(mb, sa + ln * j + (0.03 if j else 0.0), sa + ln * (j + 1) - (0.03 if j < n - 1 else 0.0), a_, b_,
               zc + 0.12, zc + 0.445, CAP_M, bev=0.05)


def bridge(mb, lmb):
    rng = random.Random(3101)
    deck(mb, rng)
    for k, s in enumerate(PIER_S):
        pier(mb, s, ROCK_Z[k % len(ROCK_Z)], k)
    faces = [s + PIER_HU for s in PIER_S] + [ABUT_S]
    for a, b in zip(faces, [s - PIER_HU for s in PIER_S[1:]] + [ABUT_S]):
        if b - a > 4.0:
            arch(mb, a, b)
    abutment(mb)
    # parapeitos: trechos entre os pilaretes. Nos (lanterna): COMECO (ancora), CURVA (pilar-marco) e FIM (canto do
    # patio, pilaretes feitos no parapets() do patio). Os outros pilaretes ficam sobre os pilares, com remate do kit.
    s_start, s_end = 1.3, SLEN - 0.6
    posts = [(s_start, 2.0, 1.0, False)] + [(s, 1.6, 0.0, False) for s in PIER_S[1:] if abs(s - NODE_S) > 1.0]
    posts += [(NODE_S, 2.4, 1.15, True)]
    posts.sort()
    glass = []
    for sd in (-1, 1):
        cuts = [(s, sz) for s, sz, lp, br in posts] + [(s_end, 2.0)]
        prev = 0.0
        for s, sz in cuts:
            if s - sz / 2 - prev > 0.5:
                bridge_parapet(mb, prev, s - sz / 2 + 0.12, sd)
            prev = s + sz / 2 - 0.12
        for s, sz, lp, br in posts:
            v = sd * (HW + 0.6 + (0.4 if br else 0.0))
            h = PAR_H + (3.6 if br else (1.2 if lp else 0.8))
            g = post_sv(mb, lmb, s, v, PZ, sz, h, lamp=lp, bracket=br)
            if g is not None:
                glass.append((s, g))
    # luz real SO no no da curva (1): no eixo, na altura das lanternas do pilar-marco
    c = W(NODE_S, 0.0, DECK + 7.0)
    light("L_SGEnt_CurveNode", "POINT", tuple(c), 480.0, WARM, 0.6)
    return glass


# ------------------------------------------------------------------ patio baixo e calcada alta (parapeitos da v3)
def parapets(mb, mh, lmb):
    """patio baixo: do canto do fim da ponte (NO do fim: pilarete com lanterna acesa) ate o pe da escada; muretas da
    escadaria; calcada alta ate a praca, interrompida pelo plinto do portico monumental"""
    xh = L.ENTRY_HIGH[2]                   # 12
    xl = L.ENTRY_LOW[2]                    # 13
    yc = L.BRIDGE_Y1 - 0.6                 # -334,6: canto do patio (fim da ponte)
    P = PORTICO_B
    pl = P["s"] + 0.8
    yb0, yb1 = P["y"] - pl / 2 - 2.2 - 0.15, P["y"] + pl / 2 + 0.15      # plinto + avental do portico
    for s in (-1, 1):
        parapet_run(mb, [(s * (HW + 0.6), yc), (s * (xl + 0.6), yc), (s * (xl + 0.6), L.ENTRY_STAIR[1] + 0.5),
                         (s * (HW + 1.4), L.ENTRY_STAIR[1] + 0.5)], PAR_Z,
                    skip=[((s * (HW + 0.6), yc), 1.0), ((s * (HW + 1.4), L.ENTRY_STAIR[1] + 0.5), 1.0)])
        # NO DO FIM DA PONTE: pilarete de canto com a lanterna da ordem (luz real; eram as do portico A)
        c = _post(mb, s * (HW + 0.6), yc, PAR_Z, 2.0, PAR_H + 1.2, lamp=True, lmb=lmb, lamp_s=1.0)
        light("L_SGEnt_EndNode_%s" % ("W" if s < 0 else "E"), "POINT", c, 320.0, WARM, 0.4)
        stair_wall(mb, mh, s)
        skipB = [((s * (HW + 1.4), L.ENTRY_STAIR_Y1 - 0.6), 1.0), ((s * (xh + 0.6), yb0), 1.0)]
        parapet_run(mb, [(s * (HW + 1.4), L.ENTRY_STAIR_Y1 - 0.6), (s * (xh + 0.6), L.ENTRY_STAIR_Y1 - 0.6),
                         (s * (xh + 0.6), yb0)], P1 - 0.35, skip=skipB)
        parapet_run(mb, [(s * (xh + 0.6), yb1), (s * (xh + 0.6), L.P1_POLY[3][1])], P1 - 0.35,
                    skip=[((s * (xh + 0.6), yb1), 1.0)])


def stair(mb):
    # overhaul 01: degraus de PEDRA (sg_lib.plan_stair com pisadas partidas em 4-5 pedras de juntas desencontradas,
    # focinho saliente 0,12 chanfrado e mais claro, espelho recuado e mais escuro)
    SL.plan_stair(mb, "Entry", m="Stone_SG_Block_B", side_m="Stone_SG_Castle_B", stringers=False,
                  riser_m="Stone_SG_Castle_B")


# ------------------------------------------------------------------ porticos
def arch_band(mb, F, yo0, yo1, cx, zs, w, band, m, nseg=4):
    """arco ogival EQUILATERO de espessura real: faixa entre o intradorso (vao w, nascencas em zs) e o extradorso
    (+band), no plano local XZ de F, de yo0 a yo1 ao longo de +Y local. Cada meio arco tem o centro no pe oposto."""
    import bmesh
    ai = math.radians(60.0)
    ao = math.acos((w / 2) / (w + band))
    for sg in (-1, 1):
        inn = [(cx + sg * (-w / 2 + w * math.cos(ai * i / nseg)), zs + w * math.sin(ai * i / nseg))
               for i in range(nseg + 1)]
        out = [(cx + sg * (-w / 2 + (w + band) * math.cos(ao * i / nseg)), zs + (w + band) * math.sin(ao * i / nseg))
               for i in range(nseg + 1)]
        inn[-1] = (cx, inn[-1][1])
        out[-1] = (cx, out[-1][1])
        for i in range(nseg):
            q = [inn[i], inn[i + 1], out[i + 1], out[i]]
            bm = mb.bm
            va = [bm.verts.new(F.p(px, yo0, pz)) for px, pz in q]
            vb = [bm.verts.new(F.p(px, yo1, pz)) for px, pz in q]
            faces = [bm.faces.new(va), bm.faces.new(list(reversed(vb)))]
            for a in range(4):
                b = (a + 1) % 4
                faces.append(bm.faces.new((va[a], va[b], vb[b], vb[a])))
            bmesh.ops.recalc_face_normals(bm, faces=faces)
            mb._post(va + vb, m, None, 0, 1)


def lancet(mb, F, yo, w, z0, z1, m=CAP_M, void="Stone_SG_Obsidian"):
    """janela cega ogival de verdade numa face do fuste (local +Y = normal da face, yo = face): vazio escuro rente a
    face, moldura saliente 0,3 (ombreiras + arco com espessura real) e peitoril com pingadeira. O fecho do arco fica
    onde ficava o antigo (z1 + 0,85 w)."""
    import bmesh
    band, dep = 0.26, 0.3
    zs = max(z1 + 0.85 * w - (0.866 * w + band * 0.9), z0 + 0.8)
    pts = [(-w / 2, z0), (w / 2, z0), (w / 2, zs)]
    pts += [(-w / 2 + w * math.cos(math.radians(a)), zs + w * math.sin(math.radians(a))) for a in (20.0, 40.0)]
    pts += [(0.0, zs + 0.866 * w)]
    pts += [(w / 2 - w * math.cos(math.radians(a)), zs + w * math.sin(math.radians(a))) for a in (40.0, 20.0)]
    pts += [(-w / 2, zs)]
    bm = mb.bm
    # ONDA 1 (z-fight): o vazio escuro fica 0,14 NA FRENTE da face do fuste (era +0,02: pintado na pedra); a moldura
    # (ombreiras e arco, ate +0,2) continua mais saliente que ele
    va = [bm.verts.new(F.p(px, yo - 0.1, pz)) for px, pz in pts]
    vb = [bm.verts.new(F.p(px, yo + 0.14, pz)) for px, pz in pts]
    faces = [bm.faces.new(va), bm.faces.new(list(reversed(vb)))]
    for i in range(len(pts)):
        j = (i + 1) % len(pts)
        faces.append(bm.faces.new((va[i], va[j], vb[j], vb[i])))
    bmesh.ops.recalc_face_normals(bm, faces=faces)
    mb._post(va + vb, void, None, 0, 1)
    # ombreiras + arco com espessura (faixa entre intradorso e extradorso)
    for sg in (-1, 1):
        mb.box((band, dep, zs - z0), F.p(sg * (w / 2 + band / 2), yo + dep / 2 - 0.1, (z0 + zs) / 2), F.r(), m, 0.0)
    arch_band(mb, F, yo - 0.1, yo + dep - 0.1, 0.0, zs, w, band, m, 3)
    # peitoril com pingadeira
    mb.box((w + 2 * band + 0.3, dep + 0.16, 0.2), F.p(0, yo + dep / 2 - 0.02, z0 - 0.1), F.r(), m, 0.0)
    mb.box((w + 2 * band + 0.1, dep, 0.1), F.p(0, yo + dep / 2 - 0.1, z0 - 0.25), F.r(), m, 0.0)


def lantern(mb, x, y, z, tag):
    """lanterna baixa ao pe do portico: BALAUSTRE torneado curto de pedra + a lanterna da ordem (kit); a luz real fica
    no centro do vidro"""
    prof = [(0.66, 0.0), (0.66, 0.18), (0.50, 0.26), (0.38, 0.42), (0.32, 0.62), (0.44, 0.92), (0.32, 1.18),
            (0.38, 1.28), (0.62, 1.34), (0.62, 1.50)]
    _lathe(mb, (x, y, z), prof, "Stone_SG_Castle_B", 8, math.pi / 8)
    c = EM.lantern_head(mb, mb, (x, y, z + 1.5 + EM.LH_BASE * 0.95), 0.0, 0.95)
    light("L_SGEnt_Portico%s_Lantern" % tag, "POINT", c, 320.0, WARM, 0.4)


def spire8(mb, x, y, r, z0, h, m="Roof_SG_Navy", ring_m="Metal_SG_Silver"):
    """agulha octogonal do portico (a mesma leitura das agulhas das torres do castelo): beiral alargado 10 %, cone
    ingreme, anel de prata a 0,36 h, florao de prata torneado (colar, bulbo, gola, ponta) no topo"""
    rot = math.pi / 8
    _lathe(mb, (x, y, z0), [(r * 1.1, 0.0), (r * 0.9, h * 0.08), (0.12, h - 0.02), (0.0, h)], m, 8, rot)
    zf = h * 0.36

    def rad(z):
        return r * 0.9 + (0.12 - r * 0.9) * (z - h * 0.08) / (h * 0.92 - 0.02)
    _lathe(mb, (x, y, z0), [(rad(zf - 0.22) - 0.05, zf - 0.22), (rad(zf - 0.22) + 0.13, zf - 0.16),
                            (rad(zf + 0.16) + 0.13, zf + 0.16), (rad(zf + 0.22) - 0.05, zf + 0.22)], ring_m, 8, rot)
    prof = [(0.17, 0.0), (0.24, 0.1), (0.14, 0.22), (0.3, 0.46), (0.22, 0.68), (0.09, 0.84), (0.13, 0.96),
            (0.0, 1.45)]
    k = 1.3
    _lathe(mb, (x, y, z0 + h - 0.35), [(a * k, b * k) for a, b in prof], ring_m, 6, math.pi / 6)


def pinnacle(mb, px, py, z0, h, r=0.34, m=CAP_M):
    """pinaculo do kit (altos): fuste octogonal, colar, agulha de 8 lados e botao"""
    mb.prism(chamfer_sq(px, py, r, r * 0.29), z0, z0 + 0.8, m)
    mb.box((2 * r + 0.16, 2 * r + 0.16, 0.14), (px, py, z0 + 0.87), (0, 0, 0), m, 0.03)
    SL.spire(mb, (px, py), r * 1.02, z0 + 0.94, h, m, n=8)
    _lathe(mb, (px, py, z0 + 0.94 + h - 0.1), [(0.07, 0.0), (0.13, 0.08), (0.10, 0.18), (0.0, 0.26)], m, 6)


def pylon(mb, P, side):
    """um pilar do portico P no lado side (-1 oeste, +1 leste)"""
    xc, y, z, s, H = side * P["xc"], P["y"], P["z"], P["s"], P["H"]
    pl = s + 0.8
    apron = 2.2
    deep = 3.0 if P["name"] == "A" else 8.0               # o B passa da borda da calcada: base desce ate o terreno
    # plinto com avental na frente (sul) que leva a lanterna
    mb.box2((xc - pl / 2, y - pl / 2 - apron, z - deep), (xc + pl / 2, y + pl / 2, z + 0.7), "Stone_SG_Block", 0.12)
    mb.box2((xc - pl / 2 - 0.12, y - pl / 2 - apron - 0.12, z + 0.7), (xc + pl / 2 + 0.12, y + pl / 2 + 0.12, z + 1.0),
            CAP_M, 0.08)
    # base + chanfro de assento
    mb.box((s + 0.6, s + 0.6, 2.4), (xc, y, z + 2.2), (0, 0, 0), "Stone_SG_Castle_B", 0.15)
    FP.frustum(mb, (xc, y, z + 3.4), s + 0.6, s + 0.6, s, s, 0.6, CAP_M)
    zt = z + 4.0 + H
    zm = z + 4.0 + H * 0.4
    ch = 0.34                                             # chanfro das quinas do fuste
    # fuste de quinas CHANFRADAS: terco de baixo em fiadas de cantaria (juntas chanfradas), o resto inteiro
    zc_ = z + 4.0
    for hh in (1.3, 1.1, 1.3):
        mb.prism(chamfer_sq(xc, y, s / 2, ch), zc_, zc_ + hh, "Stone_SG_Castle_B", bevel=0.06)
        zc_ += hh
    mb.prism(chamfer_sq(xc, y, s / 2, ch), zc_, zt, "Stone_SG_Castle_B")
    # colunelos nos chanfros (do assento ate o friso e do friso ate a cornija)
    for sx in (-1, 1):
        for sy in (-1, 1):
            cxp, cyp = xc + sx * (s / 2 - ch * 0.5), y + sy * (s / 2 - ch * 0.5)
            mb.rod((cxp, cyp, z + 4.0), (cxp, cyp, zm - 0.25), 0.13, CAP_M, 6)
            mb.rod((cxp, cyp, zm + 0.25), (cxp, cyp, zt), 0.13, CAP_M, 6)
    # frisos (meio e topo) + cornija
    mb.box((s + 0.4, s + 0.4, 0.5), (xc, y, zm), (0, 0, 0), CAP_M, 0.08)
    mb.box((s + 1.2, s + 1.2, 0.9), (xc, y, zt + 0.45), (0, 0, 0), CAP_M, 0.12)
    # coroa: bloco + gabletes com espessura, cimalha nas vertentes e florao + pinaculos do kit + agulha navy
    cs = s - 0.2
    mb.box((cs, cs, 2.2), (xc, y, zt + 0.9 + 1.1), (0, 0, 0), "Stone_SG_Castle_B", 0.1)
    zc = zt + 0.9 + 2.2
    gh = cs * 0.55
    for k in range(4):
        a = k * math.pi / 2
        F = Frame(xc, y, 0.0, a)
        pts = [(-cs / 2, 0.0), (cs / 2, 0.0), (0.0, gh)]
        bm = mb.bm
        yo0, yo1 = cs / 2 - 0.45, cs / 2 + 0.12
        v0 = [bm.verts.new(F.p(px, yo0, zc - 0.6 + pz)) for px, pz in pts]
        v1 = [bm.verts.new(F.p(px, yo1, zc - 0.6 + pz)) for px, pz in pts]
        bm.faces.new(v0)
        bm.faces.new(list(reversed(v1)))
        for i in range(3):
            j = (i + 1) % 3
            bm.faces.new((v0[i], v0[j], v1[j], v1[i]))
        mb._post(v0 + v1, "Stone_SG_Castle_B", None, 0, 1)
        # cimalha: as 2 vertentes em cantaria saliente + florao no vertice
        for sg in (-1, 1):
            pa_ = F.p(sg * (cs / 2 + 0.1), (yo0 + yo1) / 2 + 0.06, zc - 0.6 - 0.02)
            pb_ = F.p(0.0, (yo0 + yo1) / 2 + 0.06, zc - 0.6 + gh + 0.06)
            mb.beam(pa_, pb_, 0.72, 0.24, CAP_M, 0.04)
        fp = F.p(0.0, yo1 - 0.1, zc - 0.6 + gh + 0.12)
        finial(mb, fp.x, fp.y, fp.z, 0.2, n=6)
    for sx in (-1, 1):
        for sy in (-1, 1):
            px, py = xc + sx * (cs / 2 - 0.1), y + sy * (cs / 2 - 0.1)
            pinnacle(mb, px, py, zc, 1.3 + s * 0.25)
    # OVERHAUL 12 (12.12): a piramide de 4 lados (+ losango de prata de 4) virou a AGULHA OCTOGONAL da familia das
    # torres do castelo (beiral alargado, anel de prata a 1/3) com o florao de prata torneado no topo
    spire8(mb, xc, y, cs / 2 * 0.92, zc, P["spire"])
    Fi = Frame(xc, y, 0.0, math.pi / 2 if side > 0 else -math.pi / 2)     # local +Y -> mundo -side*X (eixo)
    Fn = Frame(xc, y, 0.0, 0.0)
    Fs = Frame(xc, y, 0.0, math.pi)
    if P["name"] == "B":
        # face SUL do portico B (o portao da ordem): estandarte da ordem numa verga presa ao fuste por 2 bracos.
        # O portico A ficou SEM estandarte (16.02: metade dos estandartes da entrada; o sinal fica no portao)
        yb = y - (s / 2 + 0.55)
        EM.banner(mb, mb, mb, mb, (xc, yb, zt - 0.9), -math.pi / 2, P["bw"], P["bh"], trim=EM.BRONZE)
        for sg in (-1, 1):
            mb.beam((xc + sg * (P["bw"] / 2 + 0.1), y - s / 2 + 0.1, zt - 0.9),
                    (xc + sg * (P["bw"] / 2 + 0.1), yb, zt - 0.9), 0.22, 0.22, "Metal_SG_BlackIron", 0.0)
    else:
        lancet(mb, Fs, s / 2, s * 0.42, zm + 1.2, zt - 2.4 - s * 0.36)
    # face interna (para o eixo) e face norte: janela cega ogival
    lancet(mb, Fi, s / 2, s * 0.42, zm + 1.2, zt - 2.4 - s * 0.36)
    lancet(mb, Fi, s / 2, s * 0.42, z + 5.0 + 0.6, zm - 1.4 - s * 0.36)
    lancet(mb, Fn, s / 2, s * 0.42, zm + 1.2, zt - 2.4 - s * 0.36)
    # lanterna baixa quente ao pe (no avental do plinto)
    lantern(mb, xc, y - pl / 2 - apron / 2 - 0.1, z + 1.0, P["name"] + ("_W" if side < 0 else "_E"))
    # colisao propria: fuste (inteiro) + plinto/lanterna (baixo). Face interna >= 9,2 do eixo
    col_box2("SG_EntPortico", (xc - (s + 0.6) / 2, y - (s + 0.6) / 2, z), (xc + (s + 0.6) / 2, y + (s + 0.6) / 2,
                                                                          zt + 1.0))
    col_box2("SG_EntPortico", (xc - pl / 2, y - pl / 2 - apron, z), (xc + pl / 2, y + pl / 2, z + 5.2))


def lintel_b(mb):
    """verga do portico B (o portao da ordem): viga de obsidiana entre os fustes com PERFIL (filete + cavete + cimalha
    em cima, filete embaixo), campo rebaixado entre as faixas e um FECHO esculpido no meio das 2 faces (sem emblema:
    o emblema monumental da fachada esta no mesmo eixo). Vao livre de 23,7."""
    P = PORTICO_B
    y, z, s = P["y"], P["z"], P["s"]
    xi = P["xc"] - s / 2 + 0.1                        # entra 0,1 no fuste
    zt = z + 4.0 + P["H"]
    z0, z1 = zt - 2.3, zt - 0.05
    dep = s * 0.6
    # ONDA 1 (z-fight): o corpo de obsidiana fica 0,1 dentro das faixas de baixo e de cima (fundo e topo nao rentes)
    mb.box2((-xi, y - dep / 2, z0 + 0.1), (xi, y + dep / 2, z1 - 0.1), "Stone_SG_Obsidian", 0.0)
    # faixas que emolduram o campo (o campo fica rebaixado 0,14 entre elas)
    mb.box2((-xi, y - dep / 2 - 0.14, z0 - 0.02), (xi, y + dep / 2 + 0.14, z0 + 0.3), CAP_M, 0.04)
    mb.box2((-xi, y - dep / 2 - 0.14, z1 - 0.42), (xi, y + dep / 2 + 0.14, z1 - 0.12), CAP_M, 0.04)
    # cimalha: filete + cavete (talude) + laje
    mb.box2((-xi, y - dep / 2 - 0.2, z1 - 0.12), (xi, y + dep / 2 + 0.2, z1 + 0.04), CAP_M, 0.0)
    FP.frustum(mb, (0.0, y, z1 + 0.04), 2 * xi, dep + 0.4, 2 * xi, dep + 0.9, 0.3, CAP_M)
    mb.box2((-xi, y - dep / 2 - 0.5, z1 + 0.34), (xi, y + dep / 2 + 0.5, z1 + 0.54), CAP_M, 0.05)
    # fecho esculpido (trapezio: mais largo em cima) nas 2 faces
    for sgn in (-1, 1):
        F = Frame(0.0, y, 0.0, 0.0 if sgn > 0 else math.pi)
        bm = mb.bm
        q = [(-0.55, z0 + 0.3), (0.55, z0 + 0.3), (0.8, z1 - 0.12), (-0.8, z1 - 0.12)]
        va = [bm.verts.new(F.p(px, dep / 2 - 0.05, pz)) for px, pz in q]
        vb = [bm.verts.new(F.p(px, dep / 2 + 0.3, pz)) for px, pz in q]
        import bmesh
        faces = [bm.faces.new(va), bm.faces.new(list(reversed(vb)))]
        for a in range(4):
            b = (a + 1) % 4
            faces.append(bm.faces.new((va[a], va[b], vb[b], vb[a])))
        bmesh.ops.recalc_face_normals(bm, faces=faces)
        mb._post(va + vb, CAP_M, None, 0.05, 1)


def porticos():
    """o PORTICO DE CHEGADA monumental (B). Devolve o MB ABERTO: as lanternas da ordem dos 3 nos da ponte entram nele
    (mesmos materiais das lanternas do portico: nenhuma MeshPart a mais)"""
    mb = MB("SG_Ent_Porticos", "18_ENTRY", random.Random(3104), detail="hero")
    for side in (-1, 1):
        pylon(mb, PORTICO_B, side)
    lintel_b(mb)
    return mb


def build():
    mp = porticos()
    mb = MB("SG_Ent_Bridge", "18_ENTRY", random.Random(3102), detail="near")   # ponte + patio + escada (1 objeto)
    mh = MB("SG_Ent_StairWalls", "18_ENTRY", random.Random(3105), detail="hero")
    bridge(mb, mp)
    stair(mb)
    parapets(mb, mh, mp)
    mh.finish()
    mb.finish()
    mp.finish()
