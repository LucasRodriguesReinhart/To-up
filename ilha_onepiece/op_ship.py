# op_ship - ZONA SHIP da Ilha 5 (ONE PIECE / WANO), M3 (PLANO_OP secoes 0.8, 4.3 e 9; PROMPT_USUARIO secoes 11, 15-17).
# Substitui op_blockout.ship. Prefixo OP_Ship_ (dono "ship" no export_op/studio_op/op_lib), colecao 16_HARBOR. Sem luz.
# NAVIO CENOGRAFICO atracado no pier do porto, proa para o SUL (saida da enseada). SEM conducao, combate ou viagem (sem
# canhoes, sem leme funcional): e marco visual com convés ACESSIVEL pela prancha.
#
# CASCO DE VERDADE (nao caixas): estacoes ao longo do comprimento (y 106 roda de proa .. 192 painel de popa) com secao
#   de porao arredondado (afina em V na proa), roda de proa lancada (a linha d'agua fica em y ~112 e o convés avanca ate
#   106), tosado (borda sobe na proa e vira CASTELO DE POPA de y 176 em diante). Costado em TABUAS TRINCADAS (clinker):
#   cada fiada tem a aresta de baixo 0,12 para fora -> linha de sombra por fiada, sem textura. Fiadas abaixo de 37 em
#   madeira escura (faixa d'agua/fundo). Borda falsa (amurada) com espessura 0,45, face interna clara, capa escura e
#   guarda-corpo vermelho vazado por cima (concept). Cintas (wales): vermelha na base da amurada, escura 4 abaixo.
#   Roda de proa, gurupes com cabo de estai, ancora no turco (lado do mar), leme com ferragens no cadaste.
# CONVÉS: tabuas ao comprido sobre sub-convés escuro (as frestas leem escuras), topo = colisao (46,2, op_col congelado).
#   Portinhola da PRANCHA no lado do pier (amurada cortada na largura da prancha, y 149,5..154,5): a prancha chega RENTE
#   ao convés (as tabuas do convés recuam ate x 241,6, onde a colisao da prancha encontra a do convés).
#   Escotilha com braçola e grade (proa), cabrestante (antes da camara), barris/caixas/rolos de cabo junto a amurada,
#   malaguetas nas enxarcias. Nada solto no caminho prancha -> meio do convés.
# CASTELO DE POPA: camara (frente com pilares, tabuas, porta FECHADA, 2 janelas de papel aceso recuadas 0,25, 2 chochin),
#   tombadilho em cima (cenografico, nao acessivel: colisao da camara com 10 de altura) com guarda-corpo vermelho,
#   roda do leme; painel de popa com 3 janelas acesas recuadas, cinta vermelha, friso dourado, 2 lanternas de popa.
# MASTROS: traquete (y 136) e grande (y 162) com mastro real + mastaréu, colar, cintas de ferro, cesto da gavea (grande)
#   e plataforma (traquete), vergas afinando para os lacos, 4 VELAS REDONDAS APOIADAS nas vergas: superficie curva
#   (bojo para a proa, maximo a 60% da altura, panos verticais marcados, esteira arqueada), casca de 0,18 (2 faces) com
#   tralha de cabo nas bordas; escotas ate a verga de baixo/amurada. CORDAME: ovéns com enfrechates e bigotas nas mesas
#   de enxarcia, estais (traquete -> gurupes, grande -> traquete), brandais, amantilhos.
# ICONOGRAFIA: a vela grande leva o Jolly Roger dos Chapeus de Palha (iconografia APROVADA da concept ref_01: caveira +
#   ossos cruzados + chapeu de palha) em PECAS PLANAS RECORTADAS sobre a vela, nas 2 faces (sem textura): contorno preto,
#   ossos e caveira brancos, olhos/nariz/dentes pretos, chapeu de palha com fita vermelha; camadas 0,12 entre si
#   (regra do z-fight). Bandeira preta pequena no topo do grande; flamula vermelha no traquete. OP_SAIL_EMBLEM=0 -> vela
#   neutra (fallback registrado caso o lead reprove).
# COLISAO (poucas, simples): camara do castelo de popa (OP_ShipCabin, area da camera no export), 2 mastros
#   (OP_ShipMast), escotilha, cabrestante e 2 grupos de carga (OP_ShipProp). Piso do convés, prancha e guardas da
#   amurada sao do op_col (congelado). Nada prende o jogador: o convés fica livre de y 128 a 170 entre as amuradas.
# NORMAIS: o casco, as velas e os emblemas sao faces abertas com ORIENTACAO CALCULADA (o MB fecha com recalc=False; o
#   check normals() no build confere e acusa qualquer face virada para dentro).
import math, os, random
import bpy, bmesh
from mathutils import Vector, geometry
import op_lib as DL
from op_lib import MB, Frame, col_box, camera
import op_layout as L
import op_kit as K

COLL = "16_HARBOR"
SX, SY = L.SHIP_C                     # (248, 152)
DECK = L.SHIP                         # 46,2 (topo da colisao do convés)
SEA = L.SEA
HB = L.SHIP_BEAM / 2.0                # 8
Y_STEM, Y_STERN, Y_CAB = 106.0, 192.0, 178.0
POOP = DECK + 7.6                     # tombadilho (castelo de popa)
KEEL = 31.0
NH = 10                               # fiadas do costado (convés -> quilha): 7 acima da agua, 3 no fundo
LIP = 0.12                            # ressalto das tabuas trincadas
BW_T = 0.45                           # espessura da amurada
FORE_Y, MAIN_Y = SY - 16.0, SY + 10.0  # traquete 136, grande 162
HULL, WD, WM, LAC, GOLD, IRON = "Wood_OP_Hull", "Wood_OP_Dark", "Wood_OP_Mid", "Wood_OP_Lacquer", "Metal_OP_Gold", \
    "Metal_OP_Iron"
SAIL, CW, CB, CST, CR, ROPE = "Cloth_OP_Sail", "Cloth_OP_White", "Cloth_OP_Black", "Cloth_OP_Straw", "Cloth_OP_Red", "Rope"
LIT, GLOW = "Window_OP_Warm", "Glass_OP_Lantern"
EMBLEM = os.environ.get("OP_SAIL_EMBLEM", "1") != "0"
F0 = Frame(0.0, 0.0, 0.0, 0.0)


def _gangway():
    for nm, a, b, w in L.bridge_list():
        if nm == "Gangway":
            return a, b, w
    raise KeyError("Gangway")


GW_A, GW_B, GW_W = _gangway()                     # (230,152,42.2) -> (241.6,152,46.2), largura 5
GAP = (GW_A[1] - GW_W / 2.0, GW_A[1] + GW_W / 2.0)   # portinhola (lado do pier = oeste, x < SX)


def ss(t):
    t = min(1.0, max(0.0, t))
    return t * t * (3.0 - 2.0 * t)


# ================================================================== FORMA DO CASCO
def hb(y):
    """meia boca no convés (face externa)"""
    if y < 132.0:
        t = (132.0 - y) / (132.0 - Y_STEM)
        return max(0.06, HB * math.sqrt(max(0.0, 1.0 - t * t)))
    if y > 170.0:
        t = (y - 170.0) / (Y_STERN - 170.0)
        return HB - 0.9 * t ** 1.6
    return HB


def kz(y):
    """cota da quilha: sobe na proa (pe de roda curvo) ate o convés"""
    if y >= 120.0:
        return KEEL
    t = (120.0 - y) / (120.0 - Y_STEM)
    return KEEL + (DECK - 1.2 - KEEL) * t ** 1.8


def zb(y, s):
    """topo da amurada (s = -1 lado do pier/oeste, +1 lado do mar): tosado na proa, castelo de popa, portinhola"""
    if s < 0 and GAP[0] <= y <= GAP[1]:
        return DECK - 0.8
    z = DECK + 2.0 + 2.6 * max(0.0, (126.0 - y) / 20.0) ** 1.7
    k = ss((y - 175.5) / 2.8)
    return z * (1.0 - k) + (POOP + 0.35) * k


def wid(y, z):
    """meia largura externa do casco na cota z"""
    h = hb(y)
    if z >= DECK:
        return h * (1.0 - 0.012 * (z - DECK))          # amurada levemente para dentro (tumblehome)
    k = kz(y)
    s = min(1.0, max(0.0, (DECK - z) / max(0.01, DECK - k)))
    bow = min(1.0, max(0.0, (130.0 - y) / 24.0))
    p = 2.6 - 1.2 * bow
    return h * (1.0 - s ** p) ** 0.5 * (1.0 + 0.05 * math.sin(math.pi * s))


def stations():
    ys = [106.0, 106.5, 107.3, 108.3, 109.5, 111.0, 112.6, 114.4, 116.4, 118.6, 121.0, 124.0, 127.5, 131.5, 137.0,
          143.0, GAP[0] - 0.25, GAP[0] + 0.05, GAP[1] - 0.05, GAP[1] + 0.25, 160.0, 166.0, 171.0, 174.0, 175.6, 176.6,
          177.4, 178.2, 179.5, 183.0, 187.0, 190.0, Y_STERN]
    return sorted(ys)


def side_pts(y, s):
    """(u, z) da face externa de um bordo, do topo da amurada ate a ultima fiada (sem a quilha), em tabuas trincadas"""
    top = zb(y, s)
    k = kz(y)
    if top > DECK + 0.3:
        bnd = [top, (top + DECK) / 2.0]
        h0 = DECK
    else:
        bnd = [top, top - 0.03]
        h0 = top - 0.06
    zw = max(k + 1.0, min(h0 - 3.0, SEA - 0.4))           # linha d'agua (o fundo leva 3 fiadas largas)
    bnd += [h0 + (zw - h0) * i / 7.0 for i in range(7)] + [zw + (k - zw) * i / 3.0 for i in range(4)]
    pts = []
    n = len(bnd) - 1
    lip = LIP * min(1.0, 0.08 + max(0.0, y - Y_STEM - 2.0) / 12.0)     # tabuas convergem na roda: ressalto some
    for i in range(n):
        za, zz = bnd[i], bnd[i + 1]
        pts.append((wid(y, za), za))
        if i < n - 1:
            pts.append((wid(y, zz) + lip, zz))
    return pts, top


def inner(y, s, top):
    w0 = wid(y, top)
    wt = max(w0 * 0.35, w0 - BW_T)
    zd = min(top, DECK)
    wd = wid(y, zd)
    return (max(wd * 0.35, wd - BW_T), min(DECK - 0.7, top - 0.3)), (wt, top)


def ring(y):
    """anel da estacao: ib_p, it_p, costado bombordo (cima->baixo), QUILHA, costado boreste (baixo->cima), it_s, ib_s"""
    pp, tp = side_pts(y, -1)
    ps, ts = side_pts(y, 1)
    ibp, itp = inner(y, -1, tp)
    ibs, its = inner(y, 1, ts)
    R = [(SX - ibp[0], y, ibp[1]), (SX - itp[0], y, itp[1])]
    R += [(SX - u, y, z) for u, z in pp]
    R.append((SX, y, kz(y)))
    R += [(SX + u, y, z) for u, z in reversed(ps)]
    R += [(SX + its[0], y, its[1]), (SX + ibs[0], y, ibs[1])]
    return R


def hull(mb):
    bm = mb.bm
    ys = stations()
    rings = [[bm.verts.new(p) for p in ring(y)] for y in ys]
    n = len(rings[0])
    faces = []
    mats = []
    for A, Bv in zip(rings, rings[1:]):
        for j in range(n - 1):
            f = bm.faces.new((A[j], Bv[j], Bv[j + 1], A[j + 1]))
            faces.append(f)
            zc = (A[j].co.z + A[j + 1].co.z + Bv[j].co.z + Bv[j + 1].co.z) / 4.0
            if j == 0 or j == n - 2:
                mats.append(WM)                            # face interna da amurada
            elif j == 1 or j == n - 3:
                mats.append(WD)                            # topo da amurada (sob a capa)
            elif zc < 37.0:
                mats.append(WD)                            # faixa d'agua e fundo
            else:
                mats.append(HULL)
    # painel de popa (poligono concavo: casco + paredes da amurada), normal +y
    last = rings[-1]
    co2 = [Vector((v.co.x, v.co.z, 0.0)) for v in last]
    tris = geometry.tessellate_polygon([co2])
    for a, b, c in tris:
        if geometry.area_tri(last[a].co, last[b].co, last[c].co) < 1e-4:
            continue                                       # lasca colinear do ressalto das tabuas: nao cobre nada
        f = bm.faces.new((last[a], last[b], last[c]))
        f.normal_update()
        if f.normal.y < 0:
            f.normal_flip()
        faces.append(f)
        mats.append(HULL)
    allv = [v for r in rings for v in r]
    mb._post(allv, HULL, None, 0, 1)
    bad = 0
    for f, m in zip(faces, mats):
        f.material_index = mb._mi_for(m)
        f.normal_update()
        c = f.calc_center_median()
        r = c.x - SX
        if m != WM and abs(r) > 0.8 and c.z < DECK - 0.5 and f.normal.x * r < -0.2 * abs(r) / max(abs(r), 1e-6):
            bad += 1                                        # costado com a normal virada para dentro
    HULL_BAD[0] = bad
    return rings


HULL_BAD = [0]


# ------------------------------------------------------------------ helpers de geometria
def spar(mb, a, b, r0, r1, m, n=10):
    """verga/mastro/gurupes afinando de r0 (em a) a r1 (em b), eixo arbitrario"""
    a, b = Vector(a), Vector(b)
    d = (b - a).normalized()
    up = Vector((0, 0, 1)) if abs(d.z) < 0.95 else Vector((1, 0, 0))
    e1 = d.cross(up).normalized()
    e2 = d.cross(e1).normalized()
    rings = []
    for p, r in ((a, r0), (b, r1)):
        rings.append([tuple(p + (e1 * math.cos(2 * math.pi * j / n) + e2 * math.sin(2 * math.pi * j / n)) * r)
                      for j in range(n)])
    K.loft(mb, F0, rings, m)


def yard(mb, x0, x1, y, z, r, m=WD):
    xc = (x0 + x1) / 2.0
    spar(mb, (xc, y, z), (x0, y, z), r, r * 0.55, m, 8)
    spar(mb, (xc, y, z), (x1, y, z), r, r * 0.55, m, 8)
    for x in (x0, x1):                                   # lais (ponteira escura)
        spar(mb, (x, y, z), (x - 0.5 if x < xc else x + 0.5, y, z), r * 0.55, r * 0.45, IRON, 6)


def rope(mb, a, b, r=0.1, m=ROPE):
    mb.rod(Vector(a), Vector(b), r, m, 4, caps=False)


def rope_sag(mb, a, b, sag=0.6, r=0.12, n=8, m=ROPE):
    a, b = Vector(a), Vector(b)
    pts = [a + (b - a) * (i / n) - Vector((0, 0, sag * 4.0 * (i / n) * (1 - i / n))) for i in range(n + 1)]
    mb.tube(pts, r, m, n=4)


def sweep_x(mb, pts, prof, m):
    """varredura com o 'lado' preso em +x (roda de proa, cadaste): sem torcao quando o caminho fica vertical"""
    pts = [Vector(p) for p in pts]
    rings = []
    side = Vector((1.0, 0.0, 0.0))
    for i, p in enumerate(pts):
        t = (pts[min(i + 1, len(pts) - 1)] - pts[max(i - 1, 0)]).normalized()
        sd = (side - t * side.dot(t)).normalized()
        vv = t.cross(sd).normalized()
        rings.append([tuple(p + sd * a + vv * b) for a, b in prof])
    K.loft(mb, F0, rings, m)


def lite_rail(mb, pts, base, h=2.2, step=3.0, gold=True, m=LAC):
    """guarda-corpo vermelho leve (mesma linguagem do kit: pilaretes, corrimao que passa das pontas, travessa media,
    giboshi dourado SO nas pontas) - pts = [(x, y)] mundo, base = cota"""
    P = [Vector((p[0], p[1], base)) for p in pts]
    nodes = []
    for i, (a, b) in enumerate(zip(P, P[1:])):
        d = b - a
        ln = d.length
        nseg = max(1, int(math.ceil(ln / step)))
        ang = math.atan2(d.y, d.x)
        c = (a + b) / 2
        mb.box((ln + 0.3, 0.38, 0.28), (c.x, c.y, base + h - 0.14), (0, 0, ang), m, 0.0)
        mb.box((ln, 0.16, 0.2), (c.x, c.y, base + h * 0.5), (0, 0, ang), m, 0.0)
        for j in range(nseg + (1 if i == len(P) - 2 else 0)):
            nodes.append(a + d * (j / nseg))
    for k, q in enumerate(nodes):
        mb.box((0.4, 0.4, h), (q.x, q.y, base + h / 2), (0, 0, 0), m, 0.0)
        if gold and k in (0, len(nodes) - 1):
            K.giboshi(mb, F0, q.x, q.y, base + h, 0.85)


def rect_prof(w, h, cx=0.0, cy=0.0):
    return [(cx - w / 2, cy - h / 2), (cx + w / 2, cy - h / 2), (cx + w / 2, cy + h / 2), (cx - w / 2, cy + h / 2)]


def fan(mb, pts, m, normal_hint, center=None):
    """poligono convexo em leque (centro + anel) com a normal virada para normal_hint; center = centro do leque (na
    superficie curva: a media do anel afunda/sobe a flecha da vela e encostava camadas vizinhas)"""
    bm = mb.bm
    c = Vector(center) if center is not None else sum((Vector(p) for p in pts), Vector()) / len(pts)
    vc = bm.verts.new(c)
    vs = [bm.verts.new(p) for p in pts]
    hint = Vector(normal_hint)
    fs = []
    for i in range(len(vs)):
        f = bm.faces.new((vc, vs[i], vs[(i + 1) % len(vs)]))
        f.normal_update()
        if f.normal.dot(hint) < 0:
            f.normal_flip()
        fs.append(f)
    mb._post([vc] + vs, m, 0.0, 0, 1)
    for f in fs:
        f.normal_update()


def oriented_quad(mb, a, b, c, d, m, hint):
    bm = mb.bm
    vs = [bm.verts.new(p) for p in (a, b, c, d)]
    f = bm.faces.new(vs)
    f.normal_update()
    if f.normal.dot(Vector(hint)) < 0:
        f.normal_flip()
    mb._post(vs, m, None, 0, 1)
    f.normal_update()


# ================================================================== AMURADA: capa, guarda-corpo vermelho, cintas
def sweep_ys():
    """estacoes para as varreduras (o meio do casco e reto: so as pontas e a portinhola)"""
    return [y for y in stations() if not (132.0 < y < 170.0) or abs(y - GAP[0]) < 0.6 or abs(y - GAP[1]) < 0.6]


def rail_line(s, y0, y1, off, dz=0.0, n=None):
    ys = [y for y in sweep_ys() if y0 - 1e-6 <= y <= y1 + 1e-6]
    if not ys or ys[0] > y0 + 1e-6:
        ys = [y0] + ys
    if ys[-1] < y1 - 1e-6:
        ys.append(y1)
    out = []
    for y in ys:
        t = zb(y, s)
        out.append(Vector((SX + s * (wid(y, t) - off), y, t + dz)))
    return out if s > 0 else out


def bulwark_trim(mb):
    for s in (-1, 1):
        runs = [(Y_STEM + 0.4, Y_STERN)] if s > 0 else [(Y_STEM + 0.4, GAP[0] - 0.3), (GAP[1] + 0.3, Y_STERN)]
        for y0, y1 in runs:
            pts = rail_line(s, y0, y1, BW_T / 2.0)
            if s < 0:
                pts = list(reversed(pts))
            # capa da amurada (escura, 0,9 x 0,28)
            sweep_x_free(mb, pts, rect_prof(0.9, 0.28, 0.0, 0.14), WD)
        # guarda-corpo vermelho vazado (pilaretes + corrimao) ate o castelo de popa
        rruns = [(Y_STEM + 3.0, 175.2)] if s > 0 else [(Y_STEM + 3.0, GAP[0] - 0.6), (GAP[1] + 0.6, 175.2)]
        for y0, y1 in rruns:
            pts = rail_line(s, y0, y1, BW_T / 2.0, 0.28)
            if s < 0:
                pts = list(reversed(pts))
            top = [p + Vector((0, 0, 1.25)) for p in pts]
            sweep_x_free(mb, top, rect_prof(0.42, 0.3, 0.0, 0.15), LAC)
            # pilaretes a cada ~2,2 ao longo do caminho
            acc, last = 0.0, None
            marks = []
            for i, p in enumerate(pts):
                if last is not None:
                    acc += (p - last).length
                if i == 0 or i == len(pts) - 1 or acc >= 2.6:
                    marks.append(p)
                    acc = 0.0
                last = p
            for p in marks:
                mb.box((0.36, 0.36, 1.62), (p.x, p.y, p.z + 0.81), (0, 0, 0), LAC, 0.0)
        # cintas (wales): vermelha na base da amurada, escura 4 abaixo do convés
        for zw, m, prof in ((DECK + 0.15, LAC, rect_prof(0.42, 0.6, 0.12, 0.0)),
                            (DECK - 3.6, WD, rect_prof(0.5, 0.75, 0.16, 0.0))):
            ys = [y for y in sweep_ys() if kz(y) < zw - 0.3 and y >= Y_STEM + 0.5]
            pts = [Vector((SX + s * wid(y, zw), y, zw)) for y in ys]
            if s < 0:
                pts = list(reversed(pts))
            if zw > DECK and s < 0:                       # a cinta vermelha acompanha a portinhola: corta
                a = [p for p in pts if p.y > GAP[1] + 0.2]
                b = [p for p in pts if p.y < GAP[0] - 0.2]
                for run in (a, b):
                    if len(run) >= 2:
                        sweep_side_out(mb, run, prof, m, s)
            else:
                sweep_side_out(mb, pts, prof, m, s)
    # pilares da portinhola (onde a amurada abre para a prancha) com remate dourado
    for y in (GAP[0] - 0.25, GAP[1] + 0.25):
        x = SX - wid(y, DECK) + BW_T / 2.0
        mb.box((0.6, 0.6, 4.2), (x, y, DECK + 1.7), (0, 0, 0), LAC, 0.0)
        K.giboshi(mb, F0, x, y, DECK + 3.8, 0.95)
    # soleira da portinhola (topo da amurada cortada, abaixo da prancha)
    mb.box((1.2, GAP[1] - GAP[0], 0.3), (SX - wid(152.0, DECK) + 0.5, 152.0, DECK - 0.95), (0, 0, 0), WD, 0.0)


def sweep_x_free(mb, pts, prof, m):
    """varredura com o lado horizontal perpendicular ao caminho (caminho ~horizontal ao longo do casco)"""
    pts = [Vector(p) for p in pts]
    if len(pts) < 2:
        return
    rings = []
    for i, p in enumerate(pts):
        t = (pts[min(i + 1, len(pts) - 1)] - pts[max(i - 1, 0)])
        th = Vector((t.x, t.y, 0.0))
        if th.length < 1e-6:
            th = Vector((0, 1, 0))
        th.normalize()
        sd = Vector((-th.y, th.x, 0.0))
        rings.append([tuple(p + sd * a + Vector((0, 0, b))) for a, b in prof])
    K.loft(mb, F0, rings, m)


def sweep_side_out(mb, pts, prof, m, s):
    """cinta no costado: a coordenada 'a' do perfil cresce para FORA do casco (bordo s)"""
    pts = [Vector(p) for p in pts]
    rings = []
    for i, p in enumerate(pts):
        t = (pts[min(i + 1, len(pts) - 1)] - pts[max(i - 1, 0)])
        th = Vector((t.x, t.y, 0.0)).normalized()
        sd = Vector((-th.y, th.x, 0.0))
        if sd.x * s < 0:
            sd = -sd
        rings.append([tuple(p + sd * a + Vector((0, 0, b))) for a, b in prof])
    K.loft(mb, F0, rings, m)


# ================================================================== CONVÉS
def inner_poly(z, y0, y1):
    ys = [y for y in stations() if y0 <= y <= y1]
    if ys[0] > y0:
        ys = [y0] + ys
    if ys[-1] < y1:
        ys.append(y1)
    right = [(SX + max(0.05, wid(y, z) - BW_T), y) for y in ys]
    left = [(SX - max(0.05, wid(y, z) - BW_T), y) for y in reversed(ys)]
    return right + left


def planks(mb, poly, z, y0, y1, cut_gap=False):
    poly = DL.ccw(poly)
    x = GW_B[0] - 9.0
    while x < SX + HB:
        xa, xb = x, x + 1.0
        rects = [(xa + 0.04, y0, xb - 0.04, y1)]
        if cut_gap and xa < GW_B[0] - 0.01:
            rects = [(xa + 0.04, y0, xb - 0.04, GAP[0]), (xa + 0.04, GAP[1], xb - 0.04, y1)]
        for r in rects:
            pc = L.clip_rect(poly, r)
            if len(pc) >= 3:
                mb.prism(DL.ccw(pc), z - 0.3, z, WM)
        x += 1.0
    pd = L.clip_rect(poly, (SX - 20, y0, SX + 20, y1))
    if len(pd) >= 3:
        mb.prism(DL.ccw(pd), z - 0.55, z - 0.3, WD)


def deck(mb):
    y_first = next(y for y in stations() if wid(y, DECK) - BW_T > 0.4)
    planks(mb, inner_poly(DECK, y_first, Y_CAB + 0.1), DECK, y_first - 1.0, Y_CAB + 0.1, cut_gap=True)
    # tombadilho (castelo de popa) com beiral de 0,6 sobre a frente da camara
    planks(mb, inner_poly(POOP, Y_CAB - 0.6, Y_STERN - 0.1), POOP, Y_CAB - 0.6, Y_STERN - 0.1)


# ================================================================== CASTELO DE POPA
def cabin(mb):
    yf = Y_CAB
    hw = wid(yf, DECK) - BW_T
    zt = POOP - 0.3
    # parede de tabuas horizontais (face em yf) entre pilares; porta e janelas recuadas
    posts = [-hw + 0.25, -2.0, 2.0, hw - 0.25]
    for x in posts:
        mb.box((0.55, 0.55, zt - DECK + 0.3), (SX + x, yf - 0.05, (DECK + zt) / 2.0), (0, 0, 0), WD, 0.0)
    mb.box((2 * hw, 0.7, 0.6), (SX, yf - 0.1, zt - 0.3), (0, 0, 0), WD, 0.0)            # verga
    mb.box((2 * hw + 0.2, 0.3, 0.6), (SX, Y_CAB - 0.55, POOP - 0.45), (0, 0, 0), WD, 0.0)  # testeira do beiral
    # fundo escuro (atras das frestas das tabuas)
    mb.box((2 * hw, 0.3, zt - DECK), (SX, yf + 0.62, (DECK + zt) / 2.0), (0, 0, 0), WD, 0.0)
    mb.box((3.45, 0.2, zt - 0.6 - (DECK + 5.8)), (SX, yf + 0.1, (DECK + 5.8 + zt - 0.6) / 2.0), (0, 0, 0), HULL, 0.0)
    bays = [(-hw + 0.5, -2.3), (2.3, hw - 0.5)]
    nrow = 6
    hrow = (zt - 0.6 - DECK) / nrow
    for xa, xb in bays:
        xm = (xa + xb) / 2.0
        for i in range(nrow):
            z0 = DECK + i * hrow
            z1 = z0 + hrow - 0.06
            zc = (z0 + z1) / 2.0
            if DECK + 2.5 < zc < DECK + 4.7:                 # janela no meio do vao
                for xx0, xx1 in ((xa, xm - 1.1), (xm + 1.1, xb)):
                    mb.box((xx1 - xx0, 0.2, z1 - z0), (SX + (xx0 + xx1) / 2, yf + 0.1, zc), (0, 0, 0), HULL, 0.0)
            else:
                mb.box((xb - xa, 0.2, z1 - z0), (SX + xm, yf + 0.1, zc), (0, 0, 0), HULL, 0.0)
        # janela: moldura, papel aceso 0,25 atras, grade
        z0, z1 = DECK + 2.5, DECK + 4.7
        mb.box((2.2, 0.12, z1 - z0), (SX + xm, yf + 0.35, (z0 + z1) / 2), (0, 0, 0), LIT, 0.0)
        for xx in (xm - 1.15, xm + 1.15):
            mb.box((0.3, 0.4, z1 - z0 + 0.6), (SX + xx, yf - 0.05, (z0 + z1) / 2), (0, 0, 0), WD, 0.0)
        for zz in (z0 - 0.15, z1 + 0.15):
            mb.box((2.6, 0.4, 0.3), (SX + xm, yf - 0.05, zz), (0, 0, 0), WD, 0.0)
        mb.box((0.12, 0.12, z1 - z0), (SX + xm, yf + 0.2, (z0 + z1) / 2), (0, 0, 0), WD, 0.0)
        mb.box((2.2, 0.12, 0.12), (SX + xm, yf + 0.2, (z0 + z1) / 2), (0, 0, 0), WD, 0.0)
    # porta FECHADA de 2 folhas almofadadas, recuada 0,25 na moldura
    dz = DECK + 5.4
    mb.box((3.4, 0.2, dz - DECK), (SX, yf + 0.3, (DECK + dz) / 2), (0, 0, 0), WM, 0.0)
    mb.box((0.14, 0.12, dz - DECK - 0.2), (SX, yf + 0.12, (DECK + dz) / 2), (0, 0, 0), WD, 0.0)    # M6b: 0,14 a frente
    for xx in (-0.85, 0.85):
        for zz in (DECK + 1.5, DECK + 3.9):
            mb.box((1.2, 0.12, 1.9), (SX + xx, yf + 0.13, zz), (0, 0, 0), HULL, 0.0)           # M6b: 0,13 a frente
    mb.box((3.9, 0.45, 0.4), (SX, yf - 0.05, dz + 0.2), (0, 0, 0), WD, 0.0)
    mb.box((3.9, 0.6, 0.18), (SX, yf - 0.1, DECK + 0.09), (0, 0, 0), WD, 0.0)            # soleira baixa
    for x in (-2.75, 2.75):                                 # chochin ao lado da porta
        K.lantern_wall(mb, Frame(SX + x, yf - 0.32, DECK + 6.1, math.pi), None, 0.0, 1.0)
    # guarda-corpo vermelho do tombadilho: frente (sem amurada) + lados/popa sobre a amurada
    hwp = wid(Y_CAB, POOP) - BW_T
    lite_rail(mb, [(SX - hwp + 0.2, Y_CAB - 0.35), (SX + hwp - 0.2, Y_CAB - 0.35)], POOP, 2.4)
    for s in (-1, 1):
        pts = [(SX + s * (wid(y, POOP + 0.35) - BW_T / 2.0), y) for y in (Y_CAB + 0.5, 183.0, 187.0, Y_STERN - 0.3)]
        lite_rail(mb, pts, POOP + 0.63, 1.9, 3.4, gold=False)
    hwb = wid(Y_STERN - 0.3, POOP + 0.35) - BW_T / 2.0
    lite_rail(mb, [(SX + hwb, Y_STERN - 0.3), (SX - hwb, Y_STERN - 0.3)], POOP + 0.63, 1.9, 3.4, gold=False)
    # roda do leme (cenografica) no tombadilho
    wy, wz = Y_CAB + 3.4, POOP + 3.0
    mb.box((0.9, 0.7, 2.4), (SX, wy + 0.4, POOP + 1.2), (0, 0, 0), WD, 0.0)
    K.lathe_y(mb, F0, (SX, wy, wz), [(1.55, -0.12), (1.55, 0.12)], 12, WM, caps=(False, False))
    K.lathe_y(mb, F0, (SX, wy, wz), [(1.3, 0.12), (1.3, -0.12)], 12, WM, caps=(False, False))
    K.lathe_y(mb, F0, (SX, wy, wz), [(1.3, 0.12), (1.55, 0.12)], 12, WM, caps=(False, False))
    K.lathe_y(mb, F0, (SX, wy, wz), [(1.55, -0.12), (1.3, -0.12)], 12, WM, caps=(False, False))
    K.lathe_y(mb, F0, (SX, wy, wz), [(0.35, -0.3), (0.35, 0.35)], 8, WD)
    for k in range(8):
        a = k * math.pi / 4
        mb.rod(Vector((SX, wy, wz)), Vector((SX + 2.05 * math.cos(a), wy, wz + 2.05 * math.sin(a))), 0.1, WD, 4)
    # PAINEL DE POPA: parede entre as amuradas com 3 janelas acesas recuadas, cinta vermelha, friso dourado
    yb = Y_STERN
    hwt = wid(yb, DECK) - BW_T
    z0w, z1w = DECK + 2.3, DECK + 4.9
    wins = [-4.4, 0.0, 4.4]
    ww = 2.4
    # faixas horizontais + montantes (sem face coplanar com o vidro)
    mb.box((2 * hwt, 0.4, z0w - (DECK - 0.7)), (SX, yb - 0.2, (DECK - 0.7 + z0w) / 2), (0, 0, 0), HULL, 0.0)
    mb.box((2 * hwt, 0.4, POOP - 0.3 - z1w), (SX, yb - 0.2, (z1w + POOP - 0.3) / 2), (0, 0, 0), HULL, 0.0)
    xs = [-hwt] + [w for c in wins for w in (c - ww / 2, c + ww / 2)] + [hwt]
    for i in range(0, len(xs), 2):
        xa, xb = xs[i], xs[i + 1]
        if xb - xa > 0.05:
            mb.box((xb - xa, 0.4, z1w - z0w), (SX + (xa + xb) / 2, yb - 0.2, (z0w + z1w) / 2), (0, 0, 0), HULL, 0.0)
    for c in wins:
        mb.box((ww, 0.12, z1w - z0w), (SX + c, yb - 0.35, (z0w + z1w) / 2), (0, 0, 0), LIT, 0.0)
        mb.box((0.12, 0.12, z1w - z0w), (SX + c, yb - 0.2, (z0w + z1w) / 2), (0, 0, 0), WD, 0.0)
        mb.box((ww, 0.12, 0.12), (SX + c, yb - 0.2, (z0w + z1w) / 2 + 0.3), (0, 0, 0), WD, 0.0)
        for xx in (c - ww / 2 - 0.15, c + ww / 2 + 0.15):
            mb.box((0.3, 0.3, z1w - z0w + 0.5), (SX + xx, yb + 0.12, (z0w + z1w) / 2), (0, 0, 0), WD, 0.0)
        mb.box((ww + 0.6, 0.45, 0.3), (SX + c, yb + 0.16, z1w + 0.25), (0, 0, 0), WD, 0.0)
        mb.box((ww + 0.8, 0.6, 0.25), (SX + c, yb + 0.22, z0w - 0.2), (0, 0, 0), WD, 0.0)
    mb.box((2 * hwt + 0.6, 0.35, 0.45), (SX, yb + 0.15, DECK + 1.35), (0, 0, 0), LAC, 0.0)    # cinta vermelha
    mb.box((2 * hwt + 0.6, 0.3, 0.3), (SX, yb + 0.15, POOP - 0.55), (0, 0, 0), GOLD, 0.0)    # friso dourado
    K.lathe_y(mb, F0, (SX, yb + 0.05, z1w + 1.05), [(0.0, 0.42), (0.55, 0.36), (0.62, 0.15), (0.62, 0.0)], 12, GOLD)
    # lanternas de popa em bracos de ferro (papel recuado: so o meio aceso)
    for s in (-1, 1):
        x = SX + s * (hwt - 0.4)
        mb.box((0.25, 1.7, 0.25), (x, yb + 0.65, POOP + 2.7), (0, 0, 0), IRON, 0.0)
        mb.rod(Vector((x, yb, POOP + 1.4)), Vector((x, yb + 1.25, POOP + 2.6)), 0.08, IRON, 4)
        mb.rod(Vector((x, yb + 1.35, POOP + 2.6)), Vector((x, yb + 1.35, POOP + 2.2)), 0.05, IRON, 4)
        K.chochin(mb, F0, (x, yb + 1.35, POOP + 0.6), 0.5, 1.6)
    # M6b (item 41): topo da colisao = TOMBADILHO (POOP), nao 2,6 acima dele (o jogador que subisse flutuava)
    col_box("OP_ShipCabin", (2 * hw + 0.4, Y_STERN - Y_CAB + 0.8, POOP - DECK), (SX, (Y_CAB + Y_STERN) / 2.0 - 0.2,
                                                                                 (DECK + POOP) / 2.0))


def rudder(mb):
    y0 = Y_STERN
    rings = []
    for z, ch in ((32.6, 3.6), (36.0, 3.4), (43.0, 2.2), (47.2, 1.4)):
        rings.append([(SX - 0.35, y0 + 0.1, z), (SX + 0.35, y0 + 0.1, z), (SX + 0.25, y0 + ch, z),
                      (SX - 0.25, y0 + ch, z)])
    K.loft(mb, F0, rings, WD)
    spar(mb, (SX, y0 + 0.5, 47.0), (SX, y0 + 0.5, DECK + 3.0), 0.5, 0.45, WD, 8)
    for z in (35.2, 39.2, 43.2):
        mb.box((0.95, 2.4, 0.35), (SX, y0 + 0.9, z), (0, 0, 0), IRON, 0.0)
    # cadaste
    # M6b: cadaste 0,22 fora do painel de popa (era 0,10)
    sweep_x(mb, [(SX, y0 - 0.08, KEEL - 0.3), (SX, y0 - 0.08, DECK - 0.5)], rect_prof(0.7, 0.6), WD)


def stem(mb):
    """roda de proa: pe curvo pela quilha da proa, sobe lancada e termina na cabeca acima da borda"""
    pts = []
    for y in (126.0, 120.0, 116.0, 113.0, 110.5, 108.5, 107.0, 106.1):
        pts.append((SX, y - 0.15, kz(y) - 0.25))
    top = zb(Y_STEM, 1)
    pts += [(SX, Y_STEM - 0.35, DECK + 0.4), (SX, Y_STEM - 0.6, top + 0.4), (SX, Y_STEM - 1.4, top + 1.8),
            (SX, Y_STEM - 2.3, top + 2.4)]
    sweep_x(mb, pts, rect_prof(0.85, 1.0), WD)
    K.lathe(mb, F0, (SX, Y_STEM - 2.35, top + 2.35), [(0.4, 0.0), (0.42, 0.25), (0.15, 0.6), (0.05, 0.75)], 8, GOLD)
    # quilha
    sweep_x(mb, [(SX, 125.0, KEEL - 0.25), (SX, Y_STERN + 0.2, KEEL - 0.25)], rect_prof(0.8, 0.8), WD)


def bowsprit(mb):
    a = Vector((SX, Y_STEM + 6.0, zb(Y_STEM + 6.0, 1) - 0.6))
    d = Vector((0.0, -math.cos(math.radians(20)), math.sin(math.radians(20))))
    tip = a + d * 22.0
    spar(mb, a, tip, 0.75, 0.38, WD, 10)
    for k in (0.42, 0.62):
        p = a + d * (22.0 * k)
        K.lathe(mb, F0, (p.x, p.y, p.z - 0.5), [(0.82 - k * 0.5, 0.0), (0.82 - k * 0.5, 0.25)], 10, IRON)
    rope(mb, tip, (SX, Y_STEM + 3.0, 38.0), 0.14)          # cabresto
    return a, tip


def anchor(mb):
    """ancora no turco do lado do MAR (leste): haste, bracos, unhas, cepo, argola e cabo ate o escovem"""
    y = 118.0
    s = 1
    xw = SX + s * wid(y, DECK + 1.0)
    mb.box((2.6, 0.7, 0.7), (xw + s * 0.9, y, DECK + 1.9), (0, 0, 0), WD, 0.0)            # turco
    xa = xw + s * 1.9
    zt = DECK + 0.2
    spar(mb, (xa, y, zt), (xa, y, zt - 6.0), 0.24, 0.2, IRON, 6)
    mb.box((0.35, 3.4, 0.35), (xa, y, zt - 0.4), (0, 0, 0), WD, 0.0)                       # cepo
    for sy in (-1, 1):
        p0 = Vector((xa, y, zt - 6.0))
        p1 = Vector((xa, y + sy * 1.3, zt - 5.4))
        p2 = Vector((xa, y + sy * 1.9, zt - 4.2))
        spar(mb, p0, p1, 0.22, 0.2, IRON, 6)
        spar(mb, p1, p2, 0.2, 0.16, IRON, 6)
        mb.box((0.18, 0.9, 1.0), (xa, y + sy * 1.95, zt - 4.0), (0.0, 0.0, 0.0), IRON, 0.0)   # unha
    K.lathe_y(mb, F0, (xa, y, zt + 0.3), [(0.42, -0.08), (0.42, 0.08)], 8, IRON)
    rope(mb, (xa, y, zt + 0.1), (xw + s * 0.2, y + 1.5, DECK + 0.6), 0.12)


# ================================================================== MASTROS, VERGAS, VELAS, CORDAME
MASTS = {
    # y, mastro real (altura), mastareu (altura), verga baixa (z rel, comp), verga alta (z rel, comp), cesto
    "fore": dict(y=FORE_Y, low=29.0, top=13.0, ly=(25.8, 23.0), uy=(39.2, 18.5), nest=False),
    "main": dict(y=MAIN_Y, low=33.0, top=14.0, ly=(29.8, 28.0), uy=(43.4, 22.0), nest=True),
}


def mast(mb, d):
    y = d["y"]
    zl = DECK + d["low"]
    zt = zl - 2.2 + d["top"]
    K.lathe(mb, F0, (SX, y, DECK - 0.3), [(1.45, 0.0), (1.45, 0.42), (1.1, 0.6)], 8, WD, math.pi / 8)  # colar (fogonadura)
    spar(mb, (SX, y, DECK), (SX, y, zl), 0.95, 0.74, WD, 12)
    for k in range(1, int(d["low"] / 6.0)):
        z = DECK + k * 6.0
        r = 0.95 - (0.21 * (z - DECK) / d["low"]) + 0.15        # M6b: aro 0,15 fora do mastro (era 0,09: z-fight)
        K.lathe(mb, F0, (SX, y, z - 0.2), [(r, 0.0), (r, 0.4)], 12, IRON, caps=(False, False))
    # cesto da gavea (grande) ou plataforma (traquete) logo abaixo do topo do mastro real
    if d["nest"]:
        zn = zl - 1.8
        K.lathe(mb, F0, (SX, y, zn), [(1.2, -0.5), (2.05, 0.0), (2.15, 0.1), (2.15, 2.0), (2.25, 2.1), (2.25, 2.3),
                                     (1.95, 2.3), (1.95, 0.35), (0.8, 0.35)], 14, WM)
        # (M6b: sem os 7 balaustres de 0,18 que ficavam DENTRO do aro de 0,3 e so vazavam 0,04 - z-fight com o aro)
        top_z = zn + 2.3
    else:
        zn = zl - 1.6
        K.lathe(mb, F0, (SX, y, zn), [(0.9, -0.6), (2.3, -0.05), (2.3, 0.35), (0.9, 0.35)], 12, WM)
        for k in range(6):
            a = k * math.pi / 3
            mb.box((0.2, 0.2, 1.4), (SX + 2.15 * math.cos(a), y + 2.15 * math.sin(a), zn + 1.0), (0, 0, 0), WD, 0.0)
        K.lathe(mb, F0, (SX, y, zn + 1.6), [(2.2, 0.0), (2.2, 0.18)], 12, WD)
        top_z = zn + 1.8
    # pega (cap); M6b: 2,8 de comprimento (com 3,2 a frente ficava 0,05 do aro do cesto)
    mb.box((1.7, 2.8, 0.9), (SX, y - 0.55, zl + 0.2), (0, 0, 0), WD, 0.0)
    spar(mb, (SX, y - 0.9, zl - 2.2), (SX, y - 0.9, zt), 0.55, 0.33, WD, 10)               # mastareu (avante)
    K.lathe(mb, F0, (SX, y - 0.9, zt), [(0.45, 0.0), (0.5, 0.25), (0.3, 0.55)], 8, WD)    # topo (calcez)
    col_box("OP_ShipMast", (2.2, 2.2, 9.0), (SX, y, DECK + 4.5))
    return dict(y=y, zl=zl, zt=zt, top_z=top_z, ym=y - 0.9)


def sail_surface(cx, y_top, z_top, H, Wt, Wb, belly, roach, npan):
    def S(u, v):
        W = Wt + (Wb - Wt) * v
        x = cx + u * W / 2.0
        z = z_top - v * H + roach * (1.0 - u * u) * v ** 3
        g = math.sin(0.8 * math.pi * v)
        seam = 0.07 * (0.3 + g) * math.cos(u * npan * math.pi)
        y = y_top - belly * g * (1.0 - 0.55 * u * u) - seam
        return Vector((x, y, z))
    return S


def sail(mb, cx, y_top, z_top, H, Wt, Wb, emblem=False, belly_k=0.11, roach=0.7):
    """VELA REDONDA presa na verga: casca de 2 faces (frente -y = convexa, verso +y), panos verticais, esteira
    arqueada, tralha de cabo nas 4 bordas. Devolve (S, clews)"""
    npan = 6
    nu, nv = 2 * npan, 6
    t = 0.18
    S = sail_surface(cx, y_top, z_top, H, Wt, Wb, belly_k * H, roach, npan)
    bm = mb.bm
    for side in (1, -1):                       # 1 = frente (-y), -1 = verso (+y)
        G = [[bm.verts.new(S(-1.0 + 2.0 * i / nu, j / nv) + Vector((0, -side * t / 2, 0))) for j in range(nv + 1)]
             for i in range(nu + 1)]
        fs = []
        for i in range(nu):
            for j in range(nv):
                if side > 0:
                    f = bm.faces.new((G[i][j], G[i][j + 1], G[i + 1][j + 1], G[i + 1][j]))
                else:
                    f = bm.faces.new((G[i][j], G[i + 1][j], G[i + 1][j + 1], G[i][j + 1]))
                fs.append(f)
        mb._post([v for col in G for v in col], SAIL, None, 0, 1)
        for f in fs:
            f.normal_update()
    # tralha (cabo) nas bordas
    # tralha (cabo) nos lados e na esteira (o gratil fica sob a verga)
    edges = [[S(-1.0 + 2.0 * i / nu, 1.0) for i in range(0, nu + 1, 2)],
             [S(-1.0, j / nv) for j in range(nv + 1)], [S(1.0, j / nv) for j in range(nv + 1)]]
    for e in edges:
        mb.tube(e, 0.14, ROPE, n=4)
    # faixa de rizes (cabo fino na frente) - leitura de vela de verdade
    pts = [S(-1.0 + 2.0 * i / nu, 0.16) + Vector((0, -t / 2 - 0.02, 0)) for i in range(0, nu + 1, 2)]
    mb.tube(pts, 0.06, ROPE, n=4)
    if emblem and EMBLEM:
        jolly_roger(mb, S, cx, z_top, H, Wt, Wb, t)
    return S, (S(-1.0, 1.0), S(1.0, 1.0))


# ------------------------------------------------------------------ JOLLY ROGER (pecas planas recortadas)
def _circle(cx, cz, r, n=28, rz=None):
    rz = r if rz is None else rz
    return [(cx + r * math.cos(2 * math.pi * i / n), cz + rz * math.sin(2 * math.pi * i / n)) for i in range(n)]


def _bar(a, b, hw):
    ax, az = a
    bx_, bz = b
    dx, dz = bx_ - ax, bz - az
    ln = math.hypot(dx, dz)
    nx, nz = -dz / ln * hw, dx / ln * hw
    return [(ax - nx, az - nz), (bx_ - nx, bz - nz), (bx_ + nx, bz + nz), (ax + nx, az + nz)]


def _rrect(cx, cz, w, h, r, n=4):
    out = []
    for qx, qz, a0 in ((1, -1, -math.pi / 2), (1, 1, 0.0), (-1, 1, math.pi / 2), (-1, -1, math.pi)):
        ccx, ccz = cx + qx * (w / 2 - r), cz + qz * (h / 2 - r)
        for k in range(n + 1):
            a = a0 + (math.pi / 2) * k / n
            out.append((ccx + r * math.cos(a), ccz + r * math.sin(a)))
    return out


def _dome(cx, z0, hw, h, n=14):
    return [(cx + hw * math.cos(math.pi * i / n), z0 + h * math.sin(math.pi * i / n)) for i in range(n + 1)]


def emblem_shapes(k=1.0):
    """camadas (indice, material, poligono convexo CCW em (x, z) com centro da caveira na origem)"""
    S = []
    sc = lambda P: [(x * k, z * k) for x, z in P]
    bones = []
    for sgn in (1, -1):
        a = math.radians(32.0) * sgn
        ux, uz = math.cos(a), math.sin(a)
        c = (0.0, -1.3)
        A = (c[0] - ux * 6.4, c[1] - uz * 6.4)
        Bp = (c[0] + ux * 6.4, c[1] + uz * 6.4)
        knobs = []
        for e, sg in ((A, -1), (Bp, 1)):
            for o in (-0.66, 0.66):
                knobs.append((e[0] + ux * sg * 0.45 - uz * o, e[1] + uz * sg * 0.45 + ux * o))
        bones.append((A, Bp, knobs))
    for A, Bp, knobs in bones:                                     # contorno preto dos ossos
        S.append((1, CB, sc(_bar(A, Bp, 0.55 + 0.3))))
        for q in knobs:
            S.append((1, CB, sc(_circle(q[0], q[1], 0.86 + 0.3, 12))))
    for A, Bp, knobs in bones:                                     # ossos brancos
        S.append((2, CW, sc(_bar(A, Bp, 0.55))))
        for q in knobs:
            S.append((2, CW, sc(_circle(q[0], q[1], 0.86, 12))))
    S.append((3, CB, sc(_circle(0.0, 0.9, 3.1 + 0.32, 26))))       # contorno da caveira
    S.append((3, CB, sc(_rrect(0.0, -1.75, 3.6 + 0.64, 2.6 + 0.64, 0.9))))
    S.append((4, CW, sc(_circle(0.0, 0.9, 3.1, 26))))              # cranio + mandibula
    S.append((4, CW, sc(_rrect(0.0, -1.75, 3.6, 2.6, 0.6))))
    for sx in (-1, 1):                                             # orbitas
        S.append((5, CB, sc(_circle(sx * 1.25, 0.15, 0.88, 14, 1.02))))
    S.append((5, CB, sc([(0.0, -1.45), (0.36, -0.75), (-0.36, -0.75)])))  # nariz
    S.append((5, CB, sc(_bar((-1.3, -2.15), (1.3, -2.15), 0.08))))   # boca
    for x in (-0.65, 0.0, 0.65):
        S.append((5, CB, sc(_bar((x, -2.8), (x, -1.6), 0.08))))      # dentes
    # chapeu de palha: contorno, aba, copa, fita vermelha
    S.append((5, CB, sc(_circle(0.0, 2.75, 4.5 + 0.28, 24, 0.8 + 0.28))))
    S.append((5, CB, sc(_dome(0.0, 2.75, 2.55 + 0.28, 2.35 + 0.28))))
    S.append((6, CST, sc(_circle(0.0, 2.75, 4.5, 24, 0.8))))
    S.append((6, CST, sc(_dome(0.0, 2.75, 2.55, 2.35))))
    hw = lambda z: 2.55 * math.sqrt(max(0.0, 1.0 - ((z - 2.75) / 2.35) ** 2))
    za, zz = 3.0, 3.75
    S.append((7, CR, sc([(-hw(za), za), (hw(za), za), (hw(zz), zz), (-hw(zz), zz)])))
    return S


def jolly_roger(mb, S, cx, z_top, H, Wt, Wb, t, k=None, vc=0.5):
    k = k or H / 14.5
    zc = z_top - vc * H
    gap = 0.2           # M6b (item 42): 0,12 no eixo y virava 0,08..0,116 na normal da vela curva -> >= 0,12 medido

    def on_sail(ex, ez, side, layer):
        exs = ex * side                                # verso: espelhado (le certo de tras)
        z = zc + ez
        v = (z_top - z) / H
        W = Wt + (Wb - Wt) * v
        p = S(exs / (W / 2.0), v)
        p.y -= side * (t / 2.0 + gap * layer)
        return p

    def pieces(poly):
        """barra longa (4 pontos) em pedacos de <= 1,6: a corda reta de um osso de 13 cortava a curva da vela 0,2 e
        encostava as camadas vizinhas no verso"""
        if len(poly) != 4:
            return [poly]
        a, b, c, d = [Vector((x, z, 0.0)) for x, z in poly]
        ln = (b - a).length
        n = int(math.ceil(ln / (1.6 * k)))
        if n <= 1:
            return [poly]
        out = []
        for i in range(n):
            t0, t1 = i / n, (i + 1) / n
            q = [a.lerp(b, t0), a.lerp(b, t1), d.lerp(c, t1), d.lerp(c, t0)]
            out.append([(v.x, v.y) for v in q])
        return out
    for side in (1, -1):
        for layer, m, poly0 in emblem_shapes(k):
            for poly in pieces(poly0):
                pts = [on_sail(ex, ez, side, layer) for ex, ez in poly]
                ce = (sum(q[0] for q in poly) / len(poly), sum(q[1] for q in poly) / len(poly))
                fan(mb, pts, m, (0.0, -side, 0.0), on_sail(ce[0], ce[1], side, layer))   # M6b: centro NA vela


def flag(mb, x, y, z, w, h, cloth, waves=3, amp=0.45, emblem=False, pennant=False):
    """bandeira/flamula ondulada (casca fina 2 faces) presa ao mastro em (x, y, z) (canto de cima), flutuando para +x"""
    nu = 6
    nv = 2
    t = 0.1

    def P(u, v):
        hh = h * (1.0 - 0.85 * u) if pennant else h
        return Vector((x + 0.2 + u * w, y + amp * math.sin(u * waves * math.pi) * u, z - v * hh))
    bm = mb.bm
    for side in (1, -1):
        G = [[bm.verts.new(P(i / nu, j / nv) + Vector((0, -side * t / 2, 0))) for j in range(nv + 1)]
             for i in range(nu + 1)]
        for i in range(nu):
            for j in range(nv):
                if side > 0:
                    f = bm.faces.new((G[i][j], G[i][j + 1], G[i + 1][j + 1], G[i + 1][j]))
                else:
                    f = bm.faces.new((G[i][j], G[i + 1][j], G[i + 1][j + 1], G[i][j + 1]))
                f.normal_update()
        mb._post([v for c in G for v in c], cloth, None, 0, 1)
    if emblem:
        # caveira + ossos brancos e chapeu (miniatura) nas 2 faces
        for side in (1, -1):
            for layer, m, poly in ((1, CW, _bar((-0.9, -0.75), (0.9, 0.25), 0.13)),
                                   (1, CW, _bar((-0.9, 0.25), (0.9, -0.75), 0.13)),
                                   (2, CW, _circle(0.0, 0.05, 0.5, 14)),
                                   (3, CST, _circle(0.0, 0.42, 0.62, 12, 0.14))):
                pts = []
                for ex, ez in poly:
                    u = (0.5 * w + ex * side) / w
                    p = P(u, 0.5) + Vector((0, 0, ez))
                    p.y -= side * (t / 2.0 + 0.1 * layer)
                    pts.append(p)
                fan(mb, pts, m, (0.0, -side, 0.0))


def rigging(mb, M):
    """ovéns com enfrechates e bigotas (mesas de enxarcia), estais, brandais, amantilhos"""
    out = {}
    for nm, d in M.items():
        y, zl = d["y"], d["zl"]
        for s in (-1, 1):
            # mesa de enxarcia (prancha fora do casco na altura da amurada)
            yc = y - 0.5
            xw = SX + s * wid(yc, DECK + 1.3)
            mb.box((1.0, 8.6, 0.32), (xw + s * 0.5, yc, DECK + 1.1), (0, 0, 0), WD, 0.0)
            feet = []
            for dy in (-3.6, -0.9, 1.8):
                p = Vector((xw + s * 0.85, y + dy, DECK + 1.6))
                K.lathe_y(mb, F0, (p.x, p.y, p.z), [(0.32, -0.12), (0.32, 0.12)], 6, WD)   # bigota
                rope(mb, (p.x, p.y, p.z - 0.3), (p.x - s * 0.1, p.y, DECK - 1.2), 0.07, IRON)   # chapa
                feet.append(p)
            head = Vector((SX + s * 0.75, y, zl - 1.4))
            for p in feet:
                rope(mb, p + Vector((0, 0, 0.3)), head, 0.11)
            # enfrechates (degraus de cabo) entre os ovens
            z = DECK + 3.4
            while z < zl - 4.0:
                q = []
                for p in feet:
                    t = (z - p.z) / (head.z - p.z)
                    q.append(p.lerp(head, t))
                for a, b in zip(q, q[1:]):
                    rope(mb, a, b, 0.06)
                z += 2.6
            # brandal (para a popa) do topo do mastareu
            yb = y + 12.0
            pb = Vector((SX + s * (wid(yb, zb(yb, s)) - 0.3), yb, zb(yb, s) + 0.2))
            rope(mb, (SX + s * 0.4, d["ym"], d["zt"] - 0.8), pb, 0.1)
            # ovens do mastareu ate a borda do cesto/plataforma
            rope(mb, (SX + s * 0.4, d["ym"], d["zt"] - 1.0), (SX + s * 2.0, y - 0.3, d["top_z"] - 0.1), 0.09)
            rope(mb, (SX + s * 0.4, d["ym"], d["zt"] - 1.0), (SX + s * 1.6, y + 1.4, d["top_z"] - 0.1), 0.09)
        out[nm] = d
    return out


def build_rig(mb):
    M = {nm: mast(mb, d) for nm, d in MASTS.items()}
    rigging(mb, M)
    a, tip = bowsprit(mb)
    f, mn = M["fore"], M["main"]
    # estais
    rope(mb, (SX, f["y"] - 0.6, f["zl"] - 1.0), a.lerp(tip, 0.55), 0.13)
    rope(mb, (SX, f["ym"] - 0.4, f["zt"] - 0.6), tip, 0.11)
    rope(mb, (SX, mn["y"] - 0.7, mn["zl"] - 1.0), (SX, f["y"] + 1.0, DECK + 2.6), 0.13)
    rope(mb, (SX, mn["ym"] - 0.4, mn["zt"] - 0.6), (SX, f["y"] + 0.4, f["zl"] - 0.3), 0.11)
    # vergas e velas
    for nm, d in MASTS.items():
        m = M[nm]
        y = m["y"]
        lz, ll = DECK + d["ly"][0], d["ly"][1]
        uz, ul = DECK + d["uy"][0], d["uy"][1]
        ly_y, uy_y = y - 1.15, m["ym"] - 0.75
        yard(mb, SX - ll / 2, SX + ll / 2, ly_y, lz, 0.46)
        yard(mb, SX - ul / 2, SX + ul / 2, uy_y, uz, 0.36)
        mb.box((1.2, 1.0, 0.9), (SX, ly_y + 0.45, lz), (0, 0, 0), WD, 0.0)                 # troço (parrel)
        mb.box((0.9, 0.8, 0.7), (SX, uy_y + 0.4, uz), (0, 0, 0), WD, 0.0)
        # amantilhos (pega -> lais da verga baixa)
        for s in (-1, 1):
            rope(mb, (SX + s * 0.6, y - 0.6, m["zl"] + 0.4), (SX + s * (ll / 2 - 0.6), ly_y, lz + 0.3), 0.08)
            rope(mb, (SX + s * 0.4, m["ym"], m["zt"] - 0.3), (SX + s * (ul / 2 - 0.5), uy_y, uz + 0.25), 0.07)
        # pano redondo (curso) e gavea; a gavea passa por cima do cesto
        zc_top = lz - 0.38
        foot = DECK + 12.0
        S1, cl1 = sail(mb, SX, ly_y - 0.15, zc_top, zc_top - foot, ll - 2.0, ll + 0.4, emblem=(nm == "main"))
        zt_top = uz - 0.32
        foot2 = m["top_z"] + 0.9
        S2, cl2 = sail(mb, SX, uy_y - 0.12, zt_top, zt_top - foot2, ul - 1.6, ll - 4.0, belly_k=0.1, roach=0.35)
        # escotas: gavea -> lais da verga baixa; curso -> amurada atras do mastro
        for c, s in zip(cl2, (-1, 1)):
            rope(mb, c, (SX + s * (ll / 2 - 1.6), ly_y, lz + 0.2), 0.09)
        for c, s in zip(cl1, (-1, 1)):
            yr = y + 6.5
            rope(mb, c, (SX + s * (wid(yr, zb(yr, s)) - 0.3), yr, zb(yr, s) + 0.3), 0.1)
    # bandeiras: Jolly Roger preta no topo do grande, flamula vermelha no traquete
    flag(mb, SX, mn["ym"], mn["zt"] + 0.4, 4.6, 3.0, CB, emblem=EMBLEM)
    mb.rod(Vector((SX, mn["ym"], mn["zt"])), Vector((SX, mn["ym"], mn["zt"] + 1.2)), 0.12, WD, 6)
    flag(mb, SX, f["ym"], f["zt"] + 0.3, 7.0, 1.3, CR, waves=2, amp=0.6, pennant=True)
    mb.rod(Vector((SX, f["ym"], f["zt"])), Vector((SX, f["ym"], f["zt"] + 0.9)), 0.1, WD, 6)
    return M


# ================================================================== CONVÉS: escotilha, cabrestante, carga, malaguetas
def deck_gear(mb):
    # escotilha de proa: braçola + grade sobre fundo escuro
    x0, x1, y0, y1 = SX - 2.0, SX + 2.0, 120.6, 125.6
    for (a, b, c, d) in ((x0, x1, y0, y0 + 0.35), (x0, x1, y1 - 0.35, y1), (x0, x0 + 0.35, y0, y1),
                         (x1 - 0.35, x1, y0, y1)):
        mb.box((b - a, d - c, 0.7), ((a + b) / 2, (c + d) / 2, DECK + 0.35), (0, 0, 0), WD, 0.0)
    mb.box((x1 - x0 - 0.7, y1 - y0 - 0.7, 0.2), (SX, (y0 + y1) / 2, DECK + 0.1), (0, 0, 0), WD, 0.0)
    gx = x0 + 0.35
    while gx < x1 - 0.4:
        mb.box((0.16, y1 - y0 - 0.7, 0.18), (gx + 0.25, (y0 + y1) / 2, DECK + 0.55), (0, 0, 0), WM, 0.0)
        gx += 0.55
    gy = y0 + 0.35
    while gy < y1 - 0.4:
        mb.box((x1 - x0 - 0.7, 0.16, 0.14), (SX, gy + 0.25, DECK + 0.4), (0, 0, 0), WM, 0.0)
        gy += 0.55
    col_box("OP_ShipProp", (x1 - x0, y1 - y0, 0.7), (SX, (y0 + y1) / 2, DECK + 0.35))
    # cabrestante antes da camara
    cy = 173.0
    K.lathe(mb, F0, (SX, cy, DECK), [(1.35, 0.0), (1.35, 0.35), (0.85, 0.5), (0.75, 1.5), (1.25, 1.65), (1.25, 2.15),
                                    (0.6, 2.3)], 12, WM)
    for k in range(6):
        a = k * math.pi / 3 + 0.26
        mb.box((0.95, 0.12, 1.0), (SX + 0.85 * math.cos(a), cy + 0.85 * math.sin(a), DECK + 1.0), (0, 0, a), WD, 0.0)
    for k in range(4):
        a = k * math.pi / 2
        mb.box((0.34, 0.34, 0.34), (SX + 1.25 * math.cos(a), cy + 1.25 * math.sin(a), DECK + 1.9), (0, 0, a), IRON, 0.0)
    col_box("OP_ShipProp", (2.8, 2.8, 2.3), (SX, cy, DECK + 1.15))
    # carga junto a amurada do MAR (leste): barris e caixas amarrados; e rolos de cabo nas malaguetas
    xe = SX + wid(140.0, DECK) - BW_T
    for (x, y, h) in ((xe - 0.9, 140.0, 1.6), (xe - 0.9, 141.7, 1.6)):
        K.barrel(mb, F0, x, y, DECK, 0.75, h)
    K.crate(mb, F0, xe - 1.1, 144.2, DECK, 1.8, 1.6, 1.3, 0.0)
    K.crate(mb, F0, xe - 1.1, 144.2, DECK + 1.3, 1.4, 1.2, 0.9, 0.3)
    rope(mb, (xe - 0.1, 139.0, DECK + 1.5), (xe - 0.1, 145.6, DECK + 1.5), 0.08)
    col_box("OP_ShipProp", (3.4, 7.0, 2.4), (xe - 1.6, 142.6, DECK + 1.2))
    for (x, y) in ((SX + 1.8, FORE_Y + 2.2), (SX - 2.0, MAIN_Y + 2.4), (SX + 2.1, MAIN_Y - 2.3)):
        K.lathe(mb, F0, (x, y, DECK), [(0.35, 0.0), (0.95, 0.0), (1.0, 0.14), (0.95, 0.28), (0.35, 0.28),
                                      (0.3, 0.14)], 8, ROPE)
    # malaguetas (pin rails) por dentro da amurada, na altura dos ovens
    for y in (FORE_Y, MAIN_Y):
        for s in (-1, 1):
            if s < 0 and GAP[0] - 3 < y < GAP[1] + 3:
                continue
            xi = SX + s * (wid(y, DECK + 1.4) - BW_T - 0.3)
            mb.box((0.55, 4.0, 0.25), (xi, y, DECK + 1.4), (0, 0, 0), WD, 0.0)
            for k in range(4):
                yy = y - 1.5 + k
                mb.rod(Vector((xi, yy, DECK + 1.1)), Vector((xi, yy, DECK + 1.95)), 0.07, WD, 4)
    # defensas de cabo penduradas do lado do pier
    for y in (128.0, 166.0, 184.0):
        x = SX - wid(y, DECK - 1.6) - 0.5
        K.lathe(mb, F0, (x, y, DECK - 3.6), [(0.3, 0.0), (0.5, 0.25), (0.5, 1.75), (0.3, 2.0)], 8, ROPE)
        rope(mb, (x, y, DECK - 1.6), (SX - wid(y, zb(y, -1)) + 0.1, y, zb(y, -1) + 0.2), 0.06)


# ================================================================== PRANCHA (pier -> convés)
def gangway(mb):
    a, b = Vector(GW_A), Vector(GW_B)
    d = b - a
    ln = d.length
    u = d.normalized()
    pitch = math.atan2(d.z, d.x)
    n = Vector((-u.z, 0.0, u.x))                          # normal do tampo (para cima)
    half = GW_W / 2.0 - 0.15
    # tampo de tabuas transversais (topo = a reta da colisao a -> b)
    k = int(ln / 0.6)
    for i in range(k):
        t0, t1 = i / k, (i + 1) / k
        c = a + d * ((t0 + t1) / 2) - n * 0.15
        mb.box((ln / k - 0.06, 2 * half, 0.3), tuple(c), (0, -pitch, 0), WM, 0.0)
    # longarinas e travessas antiderrapantes
    for s in (-1, 1):
        c = a + d * 0.5 - n * 0.45 + Vector((0, s * (half - 0.2), 0))
        mb.box((ln + 0.6, 0.4, 0.6), tuple(c), (0, -pitch, 0), WD, 0.0)
    for i in range(1, int(ln / 1.1)):
        c = a + d * (i * 1.1 / ln) + n * 0.06
        mb.box((0.22, 2 * half - 0.8, 0.12), tuple(c), (0, -pitch, 0), WD, 0.0)
    # sapata no pier
    mb.box((0.8, 2 * half + 0.4, 0.35), (a.x - 0.2, a.y, a.z + 0.05), (0, 0, 0), WD, 0.0)
    # corrimao: balaustres + cabo (dentro da guarda invisivel do op_col)
    for s in (-1, 1):
        posts = []
        for i in range(4):
            p = a + d * (0.05 + 0.9 * i / 3) + Vector((0, s * (half + 0.15), 0))
            mb.box((0.3, 0.3, 3.4), (p.x, p.y, p.z + 1.6), (0, 0, 0), WD, 0.0)
            posts.append(p + Vector((0, 0, 3.2)))
        for p, q in zip(posts, posts[1:]):
            rope_sag(mb, p, q, 0.25, 0.12, 6)
        rope_sag(mb, posts[-1], Vector((SX - wid(GAP[0] if s < 0 else GAP[1], DECK) + 0.2,
                                        GAP[0] - 0.25 if s < 0 else GAP[1] + 0.25, DECK + 3.4)), 0.15, 0.12, 4)


# ================================================================== cameras de revisao
EYE = L.EYE
CAMS = {
    "CAM_OPShip_PH_Prancha": ((228.6, 151.0, L.HARBOR + EYE), (250.0, 156.0, DECK + 6.0), 22),
    "CAM_OPShip_PH_Conves": ((245.0, 127.0, DECK + EYE), (249.0, 176.0, DECK + 8.0), 22),
    "CAM_OPShip_PH_ConvesProa": ((246.5, 170.0, DECK + EYE), (248.0, 112.0, DECK + 4.0), 22),
    "CAM_OPShip_PH_Mastros": ((244.0, 150.0, DECK + EYE), (248.0, 158.0, DECK + 34.0), 20),
    "CAM_OPShip_Casco": ((282.0, 136.0, SEA + 6.0), (248.0, 150.0, DECK - 2.0), 24),
    "CAM_OPShip_Proa": ((266.0, 92.0, DECK + 2.0), (248.0, 114.0, DECK - 1.0), 26),
    "CAM_OPShip_Popa": ((268.0, 216.0, DECK + 8.0), (248.0, 188.0, DECK + 2.0), 26),
    "CAM_OPShip_Velas": ((262.0, 48.0, 80.0), (248.0, 150.0, 72.0), 24),
    "CAM_OPShip_Geral": ((312.0, 96.0, 84.0), (248.0, 152.0, 62.0), 24),
}


def cams():
    for n, (loc, tgt, lens) in CAMS.items():
        camera(n, loc, tgt, lens)


def build():
    rnd = random.Random(8301)
    mb = MB("OP_Ship_Navio", COLL, rnd, detail="far", floor=-999)
    parts = []

    def tri():
        return sum(len(f.verts) - 2 for f in mb.bm.faces)
    for fn in (hull, stem, rudder, bulwark_trim, deck, cabin, anchor, deck_gear, build_rig, gangway):
        t0 = tri()
        fn(mb)
        parts.append("%s %d" % (fn.__name__, tri() - t0))
    print("op_ship: tris por parte: " + ", ".join(parts))
    # M6b: os CABOS (tubos varridos) saiam com a normal para DENTRO em parte do cordame (o Roblox so desenha a frente):
    # normais recalculadas SO nos tubos de cabo (ilhas fechadas no perimetro); o resto segue com orientacao calculada
    ri = {i for i, k in enumerate(mb.mats) if (k[1] if isinstance(k, tuple) else k) == ROPE}
    rf = [f for f in mb.bm.faces if f.material_index in ri]
    if rf:
        bmesh.ops.recalc_face_normals(mb.bm, faces=rf)
    ob = mb.finish(recalc=False)
    cams()
    bad = HULL_BAD[0]
    tris = sum(len(p.vertices) - 2 for p in ob.data.polygons)
    print("op_ship: navio %d tris, %d materiais, emblema=%s, normais suspeitas no costado=%d" % (
        tris, len(ob.data.materials), EMBLEM, bad))
    return ob
