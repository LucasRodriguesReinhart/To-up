# sg_exit - SAIDA da Ilha 3 (Shadow Garden) para a Ilha Demon Slayer: 6a na hierarquia (marca o caminho, nao compete
# com castelo, salao, entrada, dungeon e craft). Substitui sg_blockout.exit_. Prefixo SG_Exit_, colecao 08_NEXT_ISLAND.
# A narrativa, de dentro para fora (eixo y = -38, rumo leste):
#   CABECEIRA na borda leste do P2 (2 pilares-marco de pedra escura com lanterna de ferro pendurada para o eixo, sobre
#   um adro de lajes que alarga a rua de 12 para os 18 da ponte) -> PONTE gotica escura (tabuleiro de lajes frias em
#   44,2 exato, parapeito baixo com remate claro, cornija sobre mesa de cachorros, 2 pilares com talha-mar descendo em
#   ponta ate as nuvens, 3 arcos ogivais com aduelas claras) -> MARCO no ultimo pilar antes da ilhota (pilaretes altos com
#   cinta de laca vermelha e capacete de ferro preto + faixa clara atravessada no piso): a paleta Demon Slayer (guarda-
#   corpo de madeira laqueada vermelha sobre base de pedra, ferragens pretas) comeca NESSE ponto, nunca em mosaico ->
#   ILHOTA do portao (lajes, borda de cantaria, rocha em colunas de basalto pendendo em cone; o portao DS aprovado e a
#   sua base de familia sao do sg_core: aqui so o chao que os apoia) -> PLATAFORMA DA ANCORA (10 x 18) com a guarda
#   PROVISORIA visual (SG_Exit_AnchorGuard, next_island_guard=True: sai quando a ilha Demon Slayer encostar).
# Colisao: tabuleiro, ilhota, plataforma e guardas sao do sg_col (congelado). Aqui so os pilares-marco da cabeceira.
import math, random
from mathutils import Vector
import sg_lib as SL
import fm_parts as FP
from sg_lib import MB, col_box, light, Frame
import sg_layout as L

Z = L.EXIT_Z                                  # 44,2: tabuleiro, ilhota e ancora
C = "08_NEXT_ISLAND"
ANG = math.radians(L.EXIT_DEG)
F = Frame(L.EXIT_START[0], L.EXIT_START[1], 0.0, ANG)     # local: u ao longo da ponte (0 = borda do P2), v para a esquerda
BL = L.EXIT_BRIDGE_LEN                        # 64
HW = L.EXIT_W / 2.0                           # 9: face interna das guardas invisiveis
UC = BL + L.GATE_ISLET_R - 4.0                # 82: centro da ilhota
UG = BL + L.GATE_DS_OFF                       # 76: eixo do portao DS
UA = BL + L.ANCHOR_OFF                        # 104: ISLAND_NEXT_ANCHOR_DemonSlayer
RI = L.GATE_ISLET_R                           # 22

BODY = 10.2                                   # meia-largura do corpo do tabuleiro (face externa do parapeito)
SOFFIT = Z - 2.8                              # fundo do tabuleiro
PIERS = (19.2, 41.9)                          # eixos dos 2 pilares (u); o 2o e o MARCO da transicao
PIER_HU = 3.5
ABUT_E = 61.0                                 # pe do arco leste (face da rocha da ilhota)
PAVE_END = 58.0                               # fim das lajes da ponte = inicio do piso da ilhota (junta reta)
ANCHOR_U0 = UA - 10.0                         # 94: inicio da plataforma da ancora
# base de familia do portao DS (referencial do portao: vao +-8, plintos ate +-18, de 10,2 antes a 7,8 depois do eixo)
GATE_RECT = (UG - 10.8, UG + 8.6, 18.8)       # (u0, u1, meia-largura v) - nada meu acima do piso ali dentro

STONE, CASTLE, TRIM, PAVE, FLOOR = "Stone_SG_Block", "Stone_SG_Castle", "Stone_SG_Trim", "Stone_Paving_SG", "Stone_SG_Floor"
ROCK, DARK, TOP = "Cliff_Rock_SG", "Cliff_Rock_SG_Dark", "Cliff_Rock_SG_Top"
IRON, SILVER, SLATE = "Metal_SG_Iron", "Metal_SG_Silver", "Roof_SG_Slate"
RED, BLACK = "Wood_Lacquer_Red", "P_DS_Black"            # a mesma laca e o mesmo preto do portao aprovado (0 novos)
GLOW = "Lantern_Glow"
WARM = (1.0, 0.64, 0.34)


def P(u, v, z):
    return F.p(u, v, z)


def PW(u, v):
    p = F.p(u, v, 0.0)
    return (p.x, p.y)


R0 = F.r()


def _cam(u0, v0, z0, u1, v1, z1, lens):
    a, b = P(u0, v0, z0), P(u1, v1, z1)
    return (tuple(round(c, 2) for c in a), tuple(round(c, 2) for c in b), lens)


CAMS = {
    # cabeceira: da rua do P2, altura do jogador, olhando a ponte e o portao
    "CAM_SGExit_PlayerHead": _cam(-26.0, 0.0, Z + 5.2, UG, 0.0, Z + 9.0, 22),
    # de lado (sul): a ponte inteira, a ilhota e a ancora
    "CAM_SGExit_SideS": _cam(52.0, -118.0, Z + 6.0, 54.0, 0.0, Z - 12.0, 24),
    # de lado (norte, 360)
    "CAM_SGExit_SideN": _cam(46.0, 104.0, Z + 18.0, 52.0, 0.0, Z - 8.0, 24),
    # de baixo: arcos, pilares com talha-mar e a rocha em colunas da ilhota
    "CAM_SGExit_Under": _cam(28.0, -64.0, Z - 52.0, 50.0, 0.0, Z - 14.0, 22),
    # da ancora, altura do jogador, olhando para tras (costas do portao, guarda DS, ponte ao fundo)
    "CAM_SGExit_PlayerAnchorBack": _cam(UA - 1.5, 7.0, Z + 5.2, UG - 20.0, -14.0, Z + 5.0, 22),
    # de fora da ancora (onde a ilha Demon Slayer vai encostar): plataforma, pilaretes-ponta e a guarda provisoria
    "CAM_SGExit_AnchorOut": _cam(UA + 22.0, -12.0, Z + 7.0, UA - 6.0, 0.0, Z + 2.0, 22),
    # altura do jogador no marco (a troca de paleta)
    "CAM_SGExit_PlayerMarco": _cam(30.0, -5.0, Z + 5.2, 50.0, 3.0, Z + 4.0, 22),
    # tras: da ponte olhando de volta para a cabeceira e a vila
    # de cima: planta da ilhota (guarda DS x base de familia do portao x ancora) e a junta ponte/ilhota
    "CAM_SGExit_Top": _cam(UC - 30.0, -34.0, Z + 58.0, UC - 4.0, 0.0, Z, 22),
    "CAM_SGExit_Junction": _cam(PAVE_END - 4.0, -22.0, Z + 12.0, PAVE_END + 6.0, -9.0, Z, 22),
    "CAM_SGExit_HeadFromBridge": _cam(22.0, -4.0, Z + 6.0, -8.0, 0.0, Z + 7.0, 22),
}

# rotas extras: o P2 continua andavel atras dos pilares-marco; a beira da ponte e a volta da ilhota ficam livres
EXTRA_ROUTES = {
    "CABECEIRA_ATRAS_DOS_PILARES": ([PW(-9.0, -15.0), PW(-9.0, 15.0)], Z),
    "PONTE_BEIRA_S": ([PW(1.0, -7.6), PW(PAVE_END + 2.0, -7.6)], Z),
    "PONTE_BEIRA_N": ([PW(1.0, 7.6), PW(PAVE_END + 2.0, 7.6)], Z),
}
EXTRA_PROBES = [
    ("ILHOTA_borda_NE",) + PW(UC + 20.0 * math.cos(math.radians(55)), 20.0 * math.sin(math.radians(55))) + (Z,) +
    tuple(round(c, 4) for c in (Vector(PW(1, 0)) - Vector(PW(0, 0))).normalized() * math.cos(math.radians(55)) +
          (Vector(PW(0, 1)) - Vector(PW(0, 0))).normalized() * math.sin(math.radians(55)))[:2],
    ("ANCORA_lado_S",) + PW(UA - 5.0, -7.0) + (Z,) + tuple((Vector(PW(0, -1)) - Vector(PW(0, 0))).normalized())[:2],
]


# ------------------------------------------------------------------ geometria auxiliar (referencial da ponte)
def bx(mb, u0, v0, z0, u1, v1, z1, m, bev=0.0):
    """caixa alinhada ao referencial da ponte por cantos"""
    mb.box((abs(u1 - u0), abs(v1 - v0), abs(z1 - z0)), P((u0 + u1) / 2, (v0 + v1) / 2, (z0 + z1) / 2), R0, m, bev)


def beam_uv(mb, a, b, w, h, m, bev=0.0):
    mb.beam(P(*a), P(*b), w, h, m, bev)


def prism_uv(mb, pts, z0, z1, m, top_m=None, side_m=None):
    """prisma fechado de um poligono (u, v); tampo e lados com material proprio"""
    w = SL.ccw([PW(u, v) for u, v in pts])
    bm = mb.bm
    vb = [bm.verts.new((x, y, z0)) for x, y in w]
    vt = [bm.verts.new((x, y, z1)) for x, y in w]
    bm.faces.new(list(reversed(vb)))
    ft = bm.faces.new(vt)
    n = len(w)
    sides = []
    for i in range(n):
        j = (i + 1) % n
        sides.append(bm.faces.new((vb[i], vb[j], vt[j], vt[i])))
    mb._post(vb + vt, m, None, 0, 1)
    if top_m:
        ft.material_index = mb._mi_for(top_m)
    if side_m:
        mi = mb._mi_for(side_m)
        for f in sides:
            f.material_index = mi


def loft_uv(mb, poly0, z0, poly1, z1, m, caps=(True, True)):
    """tronco entre dois poligonos (u, v) com o mesmo numero de vertices (anti-horario em mundo)"""
    bm = mb.bm
    v0 = [bm.verts.new((*PW(u, v), z0)) for u, v in poly0]
    v1 = [bm.verts.new((*PW(u, v), z1)) for u, v in poly1]
    n = len(v0)
    if caps[0]:
        bm.faces.new(list(reversed(v0)))
    if caps[1]:
        bm.faces.new(v1)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((v0[i], v0[j], v1[j], v1[i]))
    mb._post(v0 + v1, m, None, 0, 1)


def point_down(mb, poly, z, apex, m):
    bm = mb.bm
    ring = [bm.verts.new((*PW(u, v), z)) for u, v in poly]
    tip = bm.verts.new(P(*apex))
    n = len(ring)
    bm.faces.new(ring)
    for i in range(n):
        bm.faces.new((ring[(i + 1) % n], ring[i], tip))
    mb._post(ring + [tip], m, None, 0, 1)


def pier_poly(cu, hv, hu, tip):
    """planta do pilar: retangulo (hu ao longo da ponte, hv atravessado) com talha-mar em ponta nos 2 lados (+-v)"""
    return [(cu, -hv - tip), (cu + hu, -hv), (cu + hu, hv), (cu, hv + tip), (cu - hu, hv), (cu - hu, -hv)]


def ogive(u0, u1, zs, n=6):
    """intradorso de arco ogival equilatero de u0 a u1 (nascencas em zs): [(u, z)] do pe oeste ao pe leste"""
    r = u1 - u0
    pts = []
    for k in range(n + 1):
        t = math.pi - (math.pi / 3.0) * k / n
        pts.append((u1 + r * math.cos(t), zs + r * math.sin(t)))
    for k in range(1, n + 1):
        t = math.pi / 3.0 - (math.pi / 3.0) * k / n
        pts.append((u0 + r * math.cos(t), zs + r * math.sin(t)))
    return pts


def spandrel(mb, v0, v1, arc, ztop, m):
    """timpano macico entre o intradorso 'arc' [(u, z)] e ztop, de v0 a v1 (faixas convexas)"""
    bm = mb.bm
    A = [(bm.verts.new(P(u, v0, z)), bm.verts.new(P(u, v0, ztop))) for u, z in arc]
    B = [(bm.verts.new(P(u, v1, z)), bm.verts.new(P(u, v1, ztop))) for u, z in arc]
    for i in range(len(arc) - 1):
        bm.faces.new((A[i][0], A[i][1], A[i + 1][1], A[i + 1][0]))
        bm.faces.new((B[i][0], B[i + 1][0], B[i + 1][1], B[i][1]))
        bm.faces.new((A[i][0], A[i + 1][0], B[i + 1][0], B[i][0]))
        bm.faces.new((A[i][1], B[i][1], B[i + 1][1], A[i + 1][1]))
    for k, s in ((0, 1), (-1, -1)):
        f = (A[k][0], B[k][0], B[k][1], A[k][1]) if s > 0 else (A[k][0], A[k][1], B[k][1], B[k][0])
        bm.faces.new(f)
    mb._post([v for p in A + B for v in p], m, None, 0, 1)


# ------------------------------------------------------------------ ponte
SPANS = [(0.0, PIERS[0] - PIER_HU), (PIERS[0] + PIER_HU, PIERS[1] - PIER_HU), (PIERS[1] + PIER_HU, ABUT_E)]


def bridge(mb, rng):
    # corpo do tabuleiro: de dentro do P2 ate dentro da ilhota (as pontas ficam escondidas sob os pisos)
    bx(mb, -1.5, -BODY, SOFFIT, 63.0, BODY, Z - 0.35, STONE)
    # encontros: oeste (entra no penhasco do P2) e leste (entra na rocha da ilhota)
    bx(mb, -5.0, -BODY - 0.4, 14.0, 0.0, BODY + 0.4, SOFFIT, STONE)
    ce = ABUT_E + 2.6
    zsp = SOFFIT - 1.3 - (SPANS[2][1] - SPANS[2][0]) * 0.866
    prism_uv(mb, pier_poly(ce, 9.4, 2.6, 3.2), zsp - 1.0, SOFFIT - 0.8, STONE)
    loft_uv(mb, pier_poly(ce, 9.4, 2.6, 3.2), SOFFIT - 0.8, pier_poly(ce, 9.4, 2.6, 0.9), SOFFIT + 0.5, TRIM)
    prism_uv(mb, pier_poly(ce, 9.8, 2.95, 3.5), zsp - 1.8, zsp - 1.0, TRIM)
    low = pier_poly(ce, 7.0, 2.2, 2.2)
    loft_uv(mb, low, zsp - 16.0, pier_poly(ce, 9.2, 2.5, 3.0), zsp - 1.8, STONE)
    point_down(mb, low, zsp - 16.0, (ce, 0.0, zsp - 34.0), DARK)
    # cornija + mesa de cachorros nos 2 lados (gotico: le a linha da ponte de longe)
    for s in (-1, 1):
        v0, v1 = sorted((s * (BODY - 0.4), s * (BODY + 0.55)))
        bx(mb, -0.5, v0, SOFFIT + 0.5, 62.0, v1, SOFFIT + 1.35, TRIM)
        u = 1.2
        while u < 61.0:
            if all(abs(u - pc) > PIER_HU + 0.6 for pc in PIERS):
                mb.box((0.8, 0.7, 1.0), P(u, s * (BODY + 0.2), SOFFIT), R0, TRIM, 0.0)
            u += 2.4
    # pilares com talha-mar: 3 estagios com ressalto (friso claro) e ponta escura pendendo para as nuvens
    for cu in PIERS:
        top = pier_poly(cu, 9.4, PIER_HU, 3.2)
        prism_uv(mb, top, 24.0, SOFFIT - 0.8, STONE)
        loft_uv(mb, top, SOFFIT - 0.8, pier_poly(cu, 9.4, PIER_HU, 0.9), SOFFIT + 0.5, TRIM)    # capeamento
        prism_uv(mb, pier_poly(cu, 9.8, PIER_HU + 0.35, 3.5), 23.2, 24.0, TRIM)
        loft_uv(mb, pier_poly(cu, 8.2, 3.0, 2.7), 2.0, pier_poly(cu, 9.2, PIER_HU - 0.1, 3.0), 23.2, STONE)
        prism_uv(mb, pier_poly(cu, 8.6, 3.3, 3.0), 1.2, 2.0, TRIM)
        low = pier_poly(cu, 6.2, 2.4, 2.1)
        loft_uv(mb, low, -18.0, pier_poly(cu, 7.9, 2.9, 2.6), 1.2, STONE)
        point_down(mb, low, -18.0, (cu + 0.4, 0.0, -44.0), DARK)
        # quina clara no bico do talha-mar (le a ponta gotica de longe)
        for sv in (-1, 1):
            beam_uv(mb, (cu, sv * 12.45, 2.0), (cu, sv * 12.45, 23.2), 0.5, 0.5, TRIM)
            beam_uv(mb, (cu, sv * 12.45, 24.0), (cu, sv * 12.45, SOFFIT - 0.8), 0.5, 0.5, TRIM)
    # 3 arcos ogivais: timpano + aduelas claras salientes + fecho
    band = 1.2
    for ua, ub in SPANS:
        span = ub - ua
        zs = SOFFIT - 1.3 - span * 0.866
        arc = ogive(ua, ub, zs, 6)
        spandrel(mb, -9.4, 9.4, arc, SOFFIT + 0.2, STONE)
        cA, cB = (ub, zs), (ua, zs)
        for i in range(len(arc) - 1):
            (u0, z0), (u1, z1) = arc[i], arc[i + 1]
            c = cA if i < 6 else cB
            mu, mz = (u0 + u1) / 2 - c[0], (z0 + z1) / 2 - c[1]
            ln = math.hypot(mu, mz)
            nu, nz = mu / ln, mz / ln
            off = band / 2 - 0.1
            du, dz = u1 - u0, z1 - z0
            dl = math.hypot(du, dz)
            sh = (du / dl * 0.07, dz / dl * 0.07)
            a = (u0 + nu * off + sh[0], 0.0, z0 + nz * off + sh[1])
            b = (u1 + nu * off - sh[0], 0.0, z1 + nz * off - sh[1])
            # beam ao longo do arco: largura = atravessado (v), altura = espessura radial
            mb.beam(P(*a), P(*b), 19.6, band, TRIM, 0.0, roll=0.0)
        ap = arc[6]
        bx(mb, ap[0] - 0.65, -10.0, ap[1] - 0.25, ap[0] + 0.65, 10.0, ap[1] + 1.65, TRIM)          # fecho
    deck(mb, rng)


def deck(mb, rng):
    """lajes frias (fiadas atravessadas, juntas escuras), meio-fio claro, faixa clara do MARCO; topo = Z exato"""
    bx(mb, 0.0, -HW, Z - 0.75, PAVE_END, HW, Z - 0.25, FLOOR)
    CURB = 1.1
    for s in (-1, 1):
        u = 0.0
        while u < PAVE_END - 0.05:
            ue = min(u + 4.3, PAVE_END)
            v0, v1 = sorted((s * HW, s * (HW - CURB)))
            bx(mb, u + 0.07, v0, Z - 0.35, ue - 0.07, v1, Z, TRIM)
            u = ue
    mk0, mk1 = PIERS[1] - 0.6, PIERS[1] + 0.6          # faixa do marco (atravessada, rente)
    bx(mb, mk0, -HW + CURB, Z - 0.35, mk1, HW - CURB, Z, TRIM)
    row = 2.9
    u = 0.0
    k = 0
    while u < PAVE_END - 0.05:
        ue = min(u + row, PAVE_END)
        if u < mk1 and ue > mk0:                         # a fiada que cruza o marco encosta nele
            segs = [(u, mk0), (mk1, ue)]
        else:
            segs = [(u, ue)]
        for a0, a1 in segs:
            if a1 - a0 < 0.5:
                continue
            v = -HW + CURB - (1.4 if k % 2 else 0.0)
            while v < HW - CURB - 0.05:
                w = rng.choice((2.8, 3.4, 4.0))
                va, vb = max(v, -HW + CURB), min(v + w, HW - CURB)
                if vb - va > 0.6:
                    bx(mb, a0 + 0.09, va + 0.09, Z - 0.35, a1 - 0.09, vb - 0.09, Z, PAVE)
                v += w
        u = ue
        k += 1


# ------------------------------------------------------------------ guardas visuais
PAR_Z = Z - 0.35
PAR_H = 2.0


def sg_post(mb, u, v, size=1.6, h=PAR_H + 0.8, z=PAR_Z):
    mb.box((size, size, h), P(u, v, z + h / 2), R0, STONE, 0.12)
    mb.box((size + 0.3, size + 0.3, 0.35), P(u, v, z + h + 0.175), R0, TRIM, 0.08)
    SL.spire(mb, PW(u, v), (size - 0.1) / math.sqrt(2.0), z + h + 0.35, 0.6, TRIM, n=4)


def sg_parapet(mb, u0, u1, s):
    """parapeito baixo de pedra escura com remate claro (face interna = guarda invisivel, |v| = 9)"""
    vc = s * (HW + 0.6)
    beam_uv(mb, (u0, vc, PAR_Z + PAR_H / 2), (u1, vc, PAR_Z + PAR_H / 2), 1.2, PAR_H, STONE, 0.1)
    beam_uv(mb, (u0, vc, PAR_Z + PAR_H + 0.22), (u1, vc, PAR_Z + PAR_H + 0.22), 1.55, 0.45, TRIM, 0.08)


def ds_rail(mb, pts, z=PAR_Z, post_step=3.0, end_posts=True):
    """guarda-corpo Demon Slayer (so depois do MARCO): base de pedra, pilaretes de laca vermelha com capacete de ferro
    preto, corrimao (kasagi) e travessa de laca. pts [(u, v)] na linha da guarda invisivel."""
    base_h = 1.1
    n = len(pts)
    for i in range(n - 1):
        a, b = Vector((*pts[i], 0)), Vector((*pts[i + 1], 0))
        d = (b - a)
        if d.length < 0.2:
            continue
        dn = d.normalized()
        ea = a - dn * (0.5 if i > 0 else 0.0)
        eb = b + dn * (0.5 if i < n - 2 else 0.0)
        beam_uv(mb, (ea.x, ea.y, z + base_h / 2), (eb.x, eb.y, z + base_h / 2), 1.0, base_h, STONE, 0.08)
        beam_uv(mb, (ea.x, ea.y, z + base_h + 0.1), (eb.x, eb.y, z + base_h + 0.1), 1.2, 0.2, TRIM, 0.0)
        beam_uv(mb, (a.x, a.y, z + 3.05), (b.x, b.y, z + 3.05), 0.42, 0.3, RED, 0.0)          # kasagi
        beam_uv(mb, (a.x, a.y, z + 2.2), (b.x, b.y, z + 2.2), 0.24, 0.24, RED, 0.0)            # travessa
    # pilaretes ao longo da polilinha (passo ~3)
    tot = []
    acc = 0.0
    for i in range(n - 1):
        ln = (Vector(pts[i + 1]) - Vector(pts[i])).length
        tot.append((acc, ln, i))
        acc += ln
    k = max(1, int(round(acc / post_step)))
    for j in range(k + 1):
        if not end_posts and j in (0, k):
            continue
        t = acc * j / k
        for a0, ln, i in tot:
            if t <= a0 + ln + 1e-6:
                f = (t - a0) / ln if ln > 1e-9 else 0.0
                p = Vector(pts[i]).lerp(Vector(pts[i + 1]), f)
                break
        zb = z + base_h + 0.2
        mb.box((0.46, 0.46, 3.2 - base_h - 0.2 + 0.25), P(p.x, p.y, (zb + z + 3.45) / 2), R0, RED, 0.0)
        mb.box((0.62, 0.62, 0.22), P(p.x, p.y, z + 3.31), R0, BLACK, 0.0)
        mb.cyl(0.36, 0.42, P(p.x, p.y, z + 3.63), R0, BLACK, 4, r2=0.06, bevel=0.0)


def ds_post(mb, u, v, sz=2.2, lantern_s=0, drop=None):
    """pilarete da familia do portao DS: fuste de pedra escura ate a altura da guarda, pilar OCTOGONAL de ferro/laca
    preta com 2 aneis de laca vermelha (o mesmo desenho dos pilares do portao aprovado) e capacete preto de 4 aguas.
    lantern_s != 0: lanterna de papel num braco preto voltado para o eixo (so no MARCO); drop: a base desce ate essa
    cota pela face do tabuleiro (pilastra sobre o pilar da ponte)"""
    if drop is not None:
        mb.box((sz + 0.4, sz + 0.4, PAR_Z - drop), P(u, v, (PAR_Z + drop) / 2), R0, STONE, 0.0)
    mb.box((sz + 0.4, sz + 0.4, 0.6), P(u, v, PAR_Z + 0.3), R0, TRIM, 0.08)
    mb.box((sz, sz, 2.6), P(u, v, PAR_Z + 0.6 + 1.3), R0, CASTLE, 0.12)
    mb.box((sz + 0.3, sz + 0.3, 0.35), P(u, v, PAR_Z + 3.375), R0, TRIM, 0.06)
    z0 = PAR_Z + 3.55
    ro = sz * 0.4
    mb.cyl(ro, 2.9, P(u, v, z0 + 1.45), (0, 0, ANG + math.pi / 8), BLACK, 8, bevel=0.0)
    for zz in (z0 + 0.45, z0 + 2.2):
        mb.cyl(ro + 0.12, 0.32, P(u, v, zz), (0, 0, ANG + math.pi / 8), RED, 8, bevel=0.0)
    mb.box((sz + 0.2, sz + 0.2, 0.26), P(u, v, z0 + 3.03), R0, BLACK, 0.0)
    mb.cyl((sz + 0.35) / math.sqrt(2.0), 1.0, P(u, v, z0 + 3.16 + 0.5), (0, 0, ANG + math.pi / 4), BLACK, 4, r2=0.1,
           bevel=0.0)
    mb.box((0.3, 0.3, 0.3), P(u, v, z0 + 4.3), (0, 0, ANG + math.pi / 4), RED, 0.0)
    if lantern_s:
        s = lantern_s
        arm_z = z0 + 2.7
        va = s * (HW - 0.8)
        beam_uv(mb, (u, v - s * ro, arm_z), (u, va, arm_z), 0.2, 0.2, BLACK)
        beam_uv(mb, (u, va, arm_z), (u, va, arm_z - 0.5), 0.1, 0.1, BLACK)
        mb.cyl(0.46, 1.3, P(u, va, arm_z - 1.3), R0, GLOW, 8, bevel=0.0)
        for dz in (-0.72, 0.72):
            mb.cyl(0.32, 0.16, P(u, va, arm_z - 1.3 + dz), R0, BLACK, 8, bevel=0.0)


def parapets(mb):
    ub = PIERS[1] - 1.1                       # o parapeito de pedra termina no marco
    for s in (-1, 1):
        sg_parapet(mb, 0.0, ub, s)
        sg_post(mb, PIERS[0], s * (HW + 0.8))
        # depois do marco: guarda Demon Slayer ate a junta com a ilhota (e segue pela ilhota, ver islet)
        ds_rail(mb, [(PIERS[1] + 1.1, s * (HW + 0.5)), (_islet_meet(), s * (HW + 0.5))], end_posts=False)
    for s in (-1, 1):
        ds_post(mb, PIERS[1], s * (HW + 1.3), 2.2, lantern_s=s, drop=SOFFIT + 0.5)          # o MARCO da transicao


def _islet_meet():
    """u onde a linha da guarda (|v| = 9,5) encontra o circulo da ilhota"""
    return UC - math.sqrt(RI * RI - (HW + 0.5) ** 2)


# ------------------------------------------------------------------ cabeceira (P2)
HEAD_U = -2.7
HEAD_V = 12.0


def head_pylon(mb, s):
    u, v = HEAD_U, s * HEAD_V
    # plinto (assentado no grama/adro) + chanfro
    mb.box((4.2, 4.2, 1.6), P(u, v, Z + 0.3), R0, STONE, 0.12)
    mb.box((4.45, 4.45, 0.3), P(u, v, Z + 1.25), R0, TRIM, 0.08)
    FP.frustum(mb, P(u, v, Z + 1.4), 3.7, 3.7, 3.1, 3.1, 0.5, TRIM, ang=ANG)
    H = 9.6
    z0 = Z + 1.9
    mb.box((3.1, 3.1, H), P(u, v, z0 + H / 2), R0, CASTLE, 0.15)
    mb.box((3.5, 3.5, 0.45), P(u, v, z0 + H * 0.42), R0, TRIM, 0.08)
    zt = z0 + H
    mb.box((4.0, 4.0, 0.8), P(u, v, zt + 0.4), R0, TRIM, 0.12)
    mb.box((2.8, 2.8, 1.5), P(u, v, zt + 0.8 + 0.75), R0, CASTLE, 0.1)
    zc = zt + 2.3
    mb.box((3.3, 3.3, 0.3), P(u, v, zc + 0.15), R0, TRIM, 0.05)
    mb.cyl(3.3 / math.sqrt(2.0), 4.2, P(u, v, zc + 0.3 + 2.1), (0, 0, ANG + math.pi / 4), SLATE, 4, r2=0.08, bevel=0.0)
    ztip = zc + 0.3 + 4.2
    mb.cyl(0.12, 1.2, P(u, v, ztip + 0.45), R0, IRON, 6, bevel=0.0)
    mb.cyl(0.36, 0.6, P(u, v, ztip + 1.2), R0, IRON, 4, r2=0.02, bevel=0.0)
    # janela cega ogival em relevo nas 2 faces que se veem (para a ponte e para fora)
    for fu, fv, nd in ((1, 0, 1.55), (0, s, 1.55)):
        for zz0, zz1 in ((z0 + 0.9, z0 + H * 0.42 - 1.6), (z0 + H * 0.42 + 1.0, zt - 1.6)):
            w = 1.25
            if fu:
                for sg in (-1, 1):
                    bx(mb, u + nd - 0.12, v + sg * w / 2 - 0.15, zz0, u + nd + 0.12, v + sg * w / 2 + 0.15, zz1, TRIM)
                    beam_uv(mb, (u + nd, v + sg * w / 2, zz1 - 0.1), (u + nd, v, zz1 + w * 0.8), 0.24, 0.3, TRIM)
            else:
                for sg in (-1, 1):
                    bx(mb, u + sg * w / 2 - 0.15, v + s * nd - 0.12, zz0, u + sg * w / 2 + 0.15, v + s * nd + 0.12, zz1,
                       TRIM)
                    beam_uv(mb, (u + sg * w / 2, v + s * nd, zz1 - 0.1), (u, v + s * nd, zz1 + w * 0.8), 0.3, 0.24,
                            TRIM)
    # braco de ferro com lanterna pendurada para o eixo da ponte (a luz da cabeceira)
    za = z0 + 7.2
    vi = v - s * 1.55
    ve = v - s * 3.6
    beam_uv(mb, (u, vi, za), (u, ve, za), 0.24, 0.24, IRON)
    beam_uv(mb, (u, vi, za - 1.3), (u, v - s * 2.6, za - 0.05), 0.16, 0.16, IRON)
    beam_uv(mb, (u, ve, za), (u, ve, za - 0.55), 0.1, 0.1, IRON)
    zl = za - 1.45
    mb.box((1.1, 1.1, 0.18), P(u, ve, zl + 0.72), R0, IRON, 0.0)
    mb.box((0.8, 0.8, 1.2), P(u, ve, zl), R0, GLOW, 0.0)
    for su in (-1, 1):
        for sv in (-1, 1):
            mb.box((0.14, 0.14, 1.36), P(u + su * 0.47, ve + sv * 0.47, zl), R0, IRON, 0.0)
    mb.box((1.0, 1.0, 0.16), P(u, ve, zl - 0.7), R0, IRON, 0.0)
    mb.cyl(0.85, 0.6, P(u, ve, zl + 1.1), (0, 0, ANG + math.pi / 4), IRON, 4, r2=0.14, bevel=0.0)
    light("L_SGExit_Head_%s" % ("N" if s > 0 else "S"), "POINT", tuple(P(u, ve, zl)), 320.0, WARM, 0.4)
    # colisao propria: plinto + fuste (o braco fica acima de 6,5 do piso)
    col_box("SG_ExitHead", (4.2, 4.2, zc + 0.3 - Z), tuple(P(u, v, Z + (zc + 0.3 - Z) / 2)), R0)


def head():
    mb = MB("SG_Exit_Head", C, random.Random(3804), detail="hero")
    for s in (-1, 1):
        head_pylon(mb, s)
    # adro da cabeceira: lajes que alargam a rua (12) para a boca da ponte (18); rente (a rua do P2 passa por cima)
    ma = mb
    u0 = -9.5
    bx(ma, u0, -HEAD_V - 1.1, Z - 0.3, 0.0, HEAD_V + 1.1, Z + 0.03, PAVE)
    bx(ma, u0 - 0.7, -HEAD_V - 1.8, Z - 0.3, u0, HEAD_V + 1.8, Z + 0.04, TRIM)
    for s in (-1, 1):
        v0, v1 = sorted((s * (HEAD_V + 1.1), s * (HEAD_V + 1.8)))
        bx(ma, u0, v0, Z - 0.3, 0.0, v1, Z + 0.04, TRIM)
    return mb.finish()


# ------------------------------------------------------------------ ilhota do portao + plataforma da ancora
TONGUE = (PAVE_END - UC, 0.0, HW)                      # (du0, du1, meia-v) relativo ao centro
SHOULDER = (GATE_RECT[0] - 1.2 - UC, 0.0, 18.6)       # apoio da base de familia do portao
ANCHOR = (ANCHOR_U0 - UC, UA - UC, HW + 2.4)               # visual: leva a guarda e os pilaretes-ponta


def _rect_exit(ca, sa, rect, rmax=None):
    """distancia do centro ate a saida do raio (ca, sa) do retangulo [du0, du1] x [-hv, hv] (0 se nao cruza)"""
    du0, du1, hv = rect
    t0, t1 = 0.0, 1e9
    if abs(ca) < 1e-9:
        if not (du0 <= 0.0 <= du1):
            return 0.0
    else:
        a, b = du0 / ca, du1 / ca
        t0, t1 = max(t0, min(a, b)), min(t1, max(a, b))
    if abs(sa) > 1e-9:
        t1 = min(t1, hv / abs(sa))
    if t1 <= t0 + 1e-6:
        return 0.0
    if rmax is not None and t0 > rmax:
        return 0.0
    return t1


def islet_r(th):
    ca, sa = math.cos(th), math.sin(th)
    r = RI
    for rect in (TONGUE, SHOULDER):
        if ca < 0:
            r = max(r, _rect_exit(ca, sa, rect))
    r = max(r, _rect_exit(ca, sa, ANCHOR, rmax=RI))
    return r


def islet_angles():
    angs = {round(math.radians(a), 6) for a in range(0, 360, 5)}
    for du, hv in ((TONGUE[0], TONGUE[2]), (SHOULDER[0], SHOULDER[2]), (ANCHOR[1], ANCHOR[2])):
        for s in (-1, 1):
            angs.add(round(math.atan2(s * hv, du) % (2 * math.pi), 6))
    for du, hv in ((TONGUE[0], TONGUE[2]), (SHOULDER[0], SHOULDER[2]), (ANCHOR[1], ANCHOR[2])):
        for s in (-1, 1):
            # onde as bordas dos retangulos cruzam o circulo (antes e depois do vertice)
            if abs(hv) < RI:
                uu = math.sqrt(RI * RI - hv * hv) * (1 if du > 0 else -1)
                angs.add(round(math.atan2(s * hv, uu) % (2 * math.pi), 6))
            if abs(du) < RI:
                vv = math.sqrt(RI * RI - du * du)
                angs.add(round(math.atan2(s * vv, du) % (2 * math.pi), 6))
    return sorted(angs)


def islet_poly(shrink=0.0):
    out = []
    for th in islet_angles():
        r = islet_r(th) - shrink
        out.append((UC + r * math.cos(th), r * math.sin(th)))
    return out


def in_gate_rect(u, v, pad=0.0):
    return GATE_RECT[0] - pad <= u <= GATE_RECT[1] + pad and abs(v) <= GATE_RECT[2] + pad


def col_keep(u, v):
    """o mesmo corte das guardas invisiveis da ilhota no sg_col (aberto na ponte e no corredor da ancora)"""
    t = u - BL
    d = abs(v)
    if d < HW + 0.6 and (t < 3.0 or t > L.ANCHOR_OFF - 14.0):
        return False
    return True


def hexcol(mb, cu, cv, r, zt, zb, rng, m=ROCK, tip=0.0, strata=None):
    """coluna de basalto hexagonal pendente (topo escondido sob a borda de cantaria), ponta opcional"""
    rot = rng.uniform(0, math.pi / 3)
    bm = mb.bm

    def ring(rr, z, ou=0.0, ov=0.0):
        return [bm.verts.new((*PW(cu + ou + rr * math.cos(rot + k * math.pi / 3),
                                  cv + ov + rr * math.sin(rot + k * math.pi / 3)), z)) for k in range(6)]
    seq = [ring(r, zt)]
    mats = []
    if strata and zb + 1.0 < strata[0] < zt - 1.0:
        zs, fs = strata
        seq.append(ring(r, zs))
        mats.append(m)
        seq.append(ring(r * fs, zs))
        mats.append(DARK)
        seq.append(ring(r * fs * 0.92, zb))
        mats.append(DARK)
    else:
        seq.append(ring(r * 0.9, zb))
        mats.append(m)
    allv = [v for rg in seq for v in rg]
    bm.faces.new(seq[0])
    groups = {}
    for (a, b), mm in zip(zip(seq, seq[1:]), mats):
        for k in range(6):
            k2 = (k + 1) % 6
            groups.setdefault(mm, []).append(bm.faces.new((a[k2], a[k], b[k], b[k2])))
    last = seq[-1]
    lm = mats[-1]
    if tip > 0:
        c = sum((v.co for v in last), Vector()) / 6
        apex = bm.verts.new((c.x, c.y, zb - tip))
        allv.append(apex)
        for k in range(6):
            groups.setdefault(lm, []).append(bm.faces.new((last[(k + 1) % 6], last[k], apex)))
    else:
        groups.setdefault(lm, []).append(bm.faces.new(list(reversed(last))))
    mb._post(allv, m, None, 0, 1)
    for mm, fs_ in groups.items():
        if mm != m:
            mi = mb._mi_for(mm)
            for f in fs_:
                f.material_index = mi


def islet(mb, rng):
    poly = islet_poly()
    # piso de lajes (topo = Z exato) com a quina clara; borda de cantaria escura recuada; soco
    prism_uv(mb, poly, Z - 0.6, Z, TRIM, top_m=PAVE)
    prism_uv(mb, islet_poly(0.35), Z - 3.9, Z - 0.6, STONE)
    prism_uv(mb, islet_poly(0.1), Z - 4.5, Z - 3.9, TRIM)
    # junta reta com a ponte (faixa clara atravessada) e faixa da ancora (onde a ponte seguinte encosta)
    bx(mb, PAVE_END, -HW, Z - 0.3, PAVE_END + 1.0, HW, Z + 0.03, TRIM)
    bx(mb, ANCHOR_U0 - 0.5, -HW, Z - 0.3, ANCHOR_U0 + 0.5, HW, Z + 0.03, TRIM)
    bx(mb, UA - 1.0, -HW, Z - 0.6, UA, HW, Z + 0.04, TRIM)
    # corredor do eixo (portao -> ancora): 2 frisos claros rentes que levam o olho ate a ancora
    for s in (-1, 1):
        bx(mb, GATE_RECT[1] + 0.2, s * 7.6 - 0.3, Z - 0.3, ANCHOR_U0 - 0.5, s * 7.6 + 0.3, Z + 0.03, TRIM)
        bx(mb, PAVE_END + 1.0, s * 7.6 - 0.3, Z - 0.3, GATE_RECT[0] - 0.2, s * 7.6 + 0.3, Z + 0.03, TRIM)
    # juntas das lajes em aneis e raios (faixas escuras rentes) dos 2 lados do corredor do eixo; o corredor
    # (entre os frisos claros), a base do portao e a plataforma da ancora ficam lisos
    def joint_ok(u, v):
        return (abs(v) > 8.3 and not in_gate_rect(u, v, 0.3) and u > PAVE_END + 1.5
                and not (u > ANCHOR_U0 - 1.0 and abs(v) < HW + 1.0))
    rings = (8.5, 13.0, 17.4)
    for rr in rings:
        n2 = int(2 * math.pi * rr / 2.6)
        for k2 in range(n2):
            a0, a1 = 2 * math.pi * k2 / n2, 2 * math.pi * (k2 + 1) / n2
            p0 = (UC + rr * math.cos(a0), rr * math.sin(a0))
            p1 = (UC + rr * math.cos(a1), rr * math.sin(a1))
            if joint_ok(*p0) and joint_ok(*p1):
                beam_uv(mb, (p0[0], p0[1], Z - 0.04), (p1[0], p1[1], Z - 0.04), 0.16, 0.12, FLOOR)
    for (ra, rb), stepl, off in (((8.5, 13.0), 3.4, 0.0), ((13.0, 17.4), 3.6, 0.5), ((17.4, 20.9), 3.8, 0.0)):
        rm = (ra + rb) / 2
        n2 = int(2 * math.pi * rm / stepl)
        for k2 in range(n2):
            a = 2 * math.pi * (k2 + off) / n2
            p0 = (UC + (ra + 0.08) * math.cos(a), (ra + 0.08) * math.sin(a))
            p1 = (UC + (rb - 0.08) * math.cos(a), (rb - 0.08) * math.sin(a))
            if joint_ok(*p0) and joint_ok(*p1):
                beam_uv(mb, (p0[0], p0[1], Z - 0.04), (p1[0], p1[1], Z - 0.04), 0.16, 0.12, FLOOR)
    # mesa de cachorros sob a quina (a mesma linha gotica da ponte continua em volta da ilhota)
    ring = islet_poly(0.35)
    n = len(ring)
    per = []
    for i in range(n):
        a_, b_ = Vector(ring[i]), Vector(ring[(i + 1) % n])
        per.append((a_, b_, (b_ - a_).length))
    tot = sum(x[2] for x in per)
    k = int(tot / 2.5)
    acc, si = 0.0, 0
    for j in range(k):
        t = tot * j / k
        while si < n - 1 and acc + per[si][2] < t:
            acc += per[si][2]
            si += 1
        a_, b_, ln = per[si]
        q = a_.lerp(b_, (t - acc) / ln if ln > 1e-9 else 0.0)
        if q.x < ABUT_E + 5.5 and abs(q.y) < BODY + 1.0:
            continue
        if q.x > UA - 0.8:
            continue
        d = (b_ - a_).normalized()
        nrm = Vector((d.y, -d.x)) if SL.area([PW(*p) for p in ring]) > 0 else Vector((-d.y, d.x))
        c = q + nrm * 0.25
        mb.box((0.8, 0.7, 1.0), P(c.x, c.y, Z - 1.25), (0, 0, ANG + math.atan2(d.y, d.x)), TRIM, 0.0)
    # rocha em colunas embaixo (cone invertido de basalto): massa primaria (5 colunas grossas e fundas no meio),
    # secundaria (grade de colunas medias que afinam para a borda) e quebra pequena (colunetas curtas na quina)
    zt = Z - 3.7
    prim = []
    for k2 in range(5):
        a2 = math.radians(k2 * 72.0 + 20.0 + rng.uniform(-12, 12))
        rr = rng.uniform(5.0, 8.5)
        pu, pv = UC + 2.0 + rr * math.cos(a2), rr * math.sin(a2)
        pr = rng.uniform(4.3, 5.2)
        prim.append((pu, pv, pr))
        depth = rng.uniform(46.0, 58.0)
        hexcol(mb, pu, pv, pr, zt, zt - depth, rng, m=ROCK, tip=rng.uniform(6.0, 10.0),
               strata=(zt - rng.uniform(8.0, 16.0), 0.84))
    step = 5.2
    rows = int(2 * 30 / (step * 0.866)) + 2
    for j in range(-rows // 2, rows // 2 + 1):
        dv = j * step * 0.866
        off = step / 2 if j % 2 else 0.0
        for i in range(-8, 9):
            du = i * step + off + rng.uniform(-0.6, 0.6)
            dvj = dv + rng.uniform(-0.6, 0.6)
            dist = math.hypot(du, dvj)
            th = math.atan2(dvj, du)
            Rl = islet_r(th)
            r = rng.uniform(2.4, 3.2)
            if dist > Rl - r * 0.8:
                continue
            u, v = UC + du, dvj
            if u < ABUT_E + 5.5 and abs(v) < BODY + 1.6:
                continue                                     # encontro leste da ponte
            if u + r > UA - 0.4:
                continue                                     # nada passa da ancora (a ponte seguinte encosta)
            if any(math.hypot(u - pu, v - pv) < pr + r * 0.5 for pu, pv, pr in prim):
                continue
            f = 1.0 - dist / Rl
            depth = 6.0 + 36.0 * f ** 1.35 + rng.uniform(-3.0, 3.0)
            strata = (zt - rng.uniform(3.0, 6.0), 0.86) if rng.random() < 0.45 else None
            hexcol(mb, u, v, r, zt, zt - depth, rng, m=ROCK if rng.random() < 0.7 else DARK,
                   tip=rng.uniform(2.5, 6.0) if depth > 14.0 else rng.uniform(0.8, 2.0), strata=strata)
    for k2 in range(14):
        th = rng.uniform(0, 2 * math.pi)
        Rl = islet_r(th)
        u, v = UC + (Rl - 1.6) * math.cos(th), (Rl - 1.6) * math.sin(th)
        if (u < ABUT_E + 5.5 and abs(v) < BODY + 1.6) or u > UA - 2.2:
            continue
        hexcol(mb, u, v, rng.uniform(1.1, 1.6), zt, zt - rng.uniform(3.0, 8.0), rng, m=DARK, tip=rng.uniform(0.8, 2.2))


def islet_rails(mb):
    """guarda Demon Slayer na borda da ilhota (so onde o sg_col tem guarda e fora da base do portao) + lados da ancora"""
    rv = RI + 0.5                                       # linha da guarda invisivel (parede de 1 centrada no circulo)
    pts = []
    n = 360
    for k in range(n + 1):
        th = 2 * math.pi * k / n
        u, v = UC + (RI - 0.5) * math.cos(th), (RI - 0.5) * math.sin(th)
        pts.append((u, v, col_keep(UC + RI * math.cos(th), RI * math.sin(th)) and not in_gate_rect(u, v, 0.4)
                    and not (u > ANCHOR_U0 - 1.0 and abs(v) < HW + 1.2)))
    runs, run = [], []
    for u, v, ok in pts:
        if ok:
            run.append((u, v))
        else:
            if len(run) > 2:
                runs.append(run)
            run = []
    if len(run) > 2:
        runs.append(run)
    # junta o ultimo com o primeiro se o corte cair no angulo 0
    for run in runs:
        simp = run[::6] + ([run[-1]] if (len(run) - 1) % 6 else [])
        ds_rail(mb, simp)
    # lados da plataforma da ancora (da borda do circulo ate a ponta) - pilaretes-ponta onde a ponte seguinte encosta
    for s in (-1, 1):
        u_c = UC + math.sqrt(max(0.0, (RI - 0.5) ** 2 - (HW + 0.5) ** 2))
        ds_rail(mb, [(min(u_c, ANCHOR_U0), s * (HW + 0.5)), (UA - 0.6, s * (HW + 0.5))])
        ds_post(mb, UA - 1.1, s * (HW + 1.1), 1.8)                   # pilaretes-ponta (onde a ponte seguinte encosta)


def anchor_guard():
    """guarda PROVISORIA visual da ancora: grade baixa de ferro preto entre os pilaretes-ponta (removivel: objeto
    proprio, next_island_guard=True; a colisao provisoria e a COL_SGAnchorGuard do sg_col)"""
    mb = MB("SG_Exit_AnchorGuard", C, random.Random(3808), detail="near")
    u = UA - 0.4
    z = Z
    for s in (-1, 1):
        mb.box((0.36, 0.36, 3.0), P(u, s * (HW - 0.2), z + 1.5), R0, BLACK, 0.0)
    for zz in (z + 0.35, z + 2.75):
        mb.box((0.26, 2 * HW - 0.2, 0.22), P(u, 0.0, zz), R0, BLACK, 0.0)
    vv = -HW + 1.2
    while vv < HW - 1.0:
        mb.box((0.14, 0.14, 2.5), P(u, vv, z + 1.55), R0, BLACK, 0.0)
        vv += 1.1
    ob = mb.finish()
    if ob is not None:
        ob["next_island_guard"] = True
        ob["note"] = "PROVISORIO: sai junto com COL_SGAnchorGuard_* quando a ilha Demon Slayer encostar na ancora"
    return ob


def build():
    head()
    rng = random.Random(3801)
    mb = MB("SG_Exit_Bridge", C, rng, detail="near")          # ponte + ilhota + rocha (mesmos materiais)
    bridge(mb, rng)
    islet(mb, rng)
    mb.finish()
    mr = MB("SG_Exit_Rails", C, random.Random(3802), detail="near")   # parapeito SG, marco, guarda DS, pilaretes-ponta
    parapets(mr)
    islet_rails(mr)
    mr.finish()
    anchor_guard()
