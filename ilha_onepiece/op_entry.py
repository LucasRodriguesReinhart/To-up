# op_entry - ENTRADA da Ilha 5 (ONE PIECE / WANO), vindo da Demon Slayer (M2; PLANO_OP secoes 3, 4.2, 4.3, 6 e 7;
# PROMPT_USUARIO secoes 2, 5, 14 e 16). Substitui op_blockout.entry. Prefixo OP_Ent_, colecao 18_ENTRY.
# A narrativa, da ancora da DS para dentro (eixo local +Y; a ponte vai de y -120 a 0, sobe 80,2 -> 84,2):
#   PONTE RETA DE 120 (a primeira coisa da concept): tabuado escuro de tabuas atravessadas sobre 4 longarinas, testeira
#   VERMELHA continua dos 2 lados (le como a borda vermelha da concept), GUARDA-CORPO vermelho completo (pilaretes com
#   cinta de ouro, corrimao largo kasagi, travessa media e baixa, postes-mestre com giboshi de ouro nas linhas dos
#   pilares e nas pontas), 2 postes-lanterna no meio e 2 na cabeca da ponte (lanterna de caixa com chapeu), 2 nobori
#   vermelhos na partida. APOIOS VISIVEIS sobre o mar: viaduto de PEDRA em ARCOS (5 pilares com talhamar, impostas e
#   fiadas, abobadas de berco com aduelas escuras, cornija continua sob a testeira) e ENCONTRO de pedra com alas na
#   falesia da ilha (o patamar). Nada copia a ponte de madeira da DS.
#   GRANDE TORII (myojin, maior e mais ornamentado que o da DS): base de pedra escura, nemaki preto com cinta de ouro,
#   hashira vermelho inclinado, nuki passante com cunhas e ponteiras de ouro, gakuzuka com placa escura de moldura e
#   brasao redondo de ouro (sem texto), shimaki vermelho e KASAGI PRETO CURVO de pontas levantadas com capa de telha
#   (canais + cumeeira + onigawara), CHOCHIN pendurados nas pontas do nuki e nos pilares, 2 NOBORI vermelhos ao lado.
#   PATIO DO TORII (T0 84,2): lajes (sando claro da ponte a escada, lajes medias no resto, berco escuro nas juntas),
#   muro baixo de pedra na borda sul, 4 toro de pedra, arbustos podados nos cantos; ESCADARIA de pedra (Chegada) do
#   kit (pisadas desencontradas, focinho, espelho recuado, banzos com capa).
# Colisao: tabuleiro, guardas da ponte, piso do patio, escada e guardas de borda sao do op_col (congelado). Aqui so torii,
# toro e nobori. Os nos/postes do guarda-corpo ficam DENTRO da faixa da guarda invisivel (x 9..10,2).
# KIT: toro, nobori do patio e a escada Chegada sao do op_kit (M2). Ficam LOCAIS so as pecas proprias de ponte/torii
# que o kit nao tem: guarda-corpo INCLINADO com postes-mestre/andon (rail_run), chochin de papel do torii, nobori
# preso ao pilar do viaduto. TODO(op_kit): se o kit ganhar guarda-corpo inclinado, trocar rail_run por ele.
import math, random
from mathutils import Vector
import op_lib as DL
from op_lib import MB, col_box, light, Frame, ccw
import op_layout as L
import fm_portal_kit as PK
import op_kit as K

C = "18_ENTRY"
T0, T1, DECK = L.T0, L.T1, L.DECK
BL = L.BRIDGE_IN_LEN
Y0 = L.PREV_Y                         # -120: WORLD_FROM_PREV (borda do tabuleiro na ancora da DS)
WARM = (1.0, 0.66, 0.36)
ZZ = Vector((0.0, 0.0, 1.0))

# paleta OPMATS (0 materiais novos)
LAC, BLK, GOLD = "Wood_OP_Lacquer", "Roof_OP_Ridge", "Metal_OP_Gold"
WD, WM = "Wood_OP_Dark", "Wood_OP_Mid"
ST, STD, STP = "Stone_OP", "Stone_OP_Dark", "Stone_OP_Path"
TILE, PAPER, IRON = "Roof_OP_Blue", "Glass_OP_Lantern", "Metal_OP_Iron"
RED, WHITE = "Cloth_OP_Red", "Cloth_OP_White"
LEAF = "Leaf_OP"

# ponte
HWD = L.DECK_W / 2.0                  # 9: face interna das guardas invisiveis (o piso util)
FAS = (9.45, 10.2)                    # testeira vermelha (x de dentro, x de fora)
RAIL_X = 9.82                         # eixo do guarda-corpo (dentro da guarda invisivel 9,0..10,2)
PLANK_T = 0.3
PIERS = [-114.4, -92.4, -70.4, -48.4, -26.4]   # pilares do viaduto (y); vao 22
PIER_HD = 2.6                         # meia espessura do pilar (y) na imposta
ABUT_Y = (-7.0, -1.0)                 # encontro de pedra (face sul, fundo dentro da falesia)
FACE_X = 9.55                         # face do viaduto de pedra (a testeira vermelha passa 0,65 por fora)
SEA_BOT = 26.0                        # pe dos pilares (abaixo do mar local 36: nunca aparece solto)


def zf(y):
    """cota da colisao do tabuleiro (rampa 80,2 -> 84,2, igual ao op_col)"""
    t = max(0.0, min(1.0, (y - Y0) / BL))
    return DECK + (T0 - DECK) * t


PITCH = math.atan2(T0 - DECK, BL)


# ================================================================== primitivas
def loft(mb, rings, m, caps=(True, True), closed=True):
    """superficie entre aneis de pontos (anel de 1 ponto = apice); fecha as pontas"""
    bm = mb.bm
    V = [[bm.verts.new(Vector(p)) for p in r] for r in rings]
    for a, b in zip(V, V[1:]):
        if len(a) == 1 or len(b) == 1:
            if len(a) == 1 and len(b) == 1:
                continue
            apex, ring = (a[0], b) if len(a) == 1 else (b[0], a)
            n = len(ring)
            for i in range(n if closed else n - 1):
                try:
                    bm.faces.new((ring[i], ring[(i + 1) % n], apex))
                except ValueError:
                    pass
            continue
        n = len(a)
        for i in range(n if closed else n - 1):
            j = (i + 1) % n
            try:
                bm.faces.new((a[i], a[j], b[j], b[i]))
            except ValueError:
                pass
    for k, flag in ((0, caps[0]), (-1, caps[1])):
        if flag and len(V[k]) > 2:
            try:
                bm.faces.new(V[k] if k else list(reversed(V[k])))
            except ValueError:
                pass
    mb._post([v for r in V for v in r], m, None, 0, 1)


def lathe(mb, c, prof, m, n=12, rot=0.0, caps=(True, True), sx=1.0, sy=1.0):
    """perfil [(r, z)] girado em volta do eixo vertical por c = (x, y, z0)"""
    rings = []
    for r, z in prof:
        if r <= 1e-4:
            rings.append([(c[0], c[1], c[2] + z)])
        else:
            rings.append([(c[0] + sx * r * math.cos(rot + 2 * math.pi * i / n),
                           c[1] + sy * r * math.sin(rot + 2 * math.pi * i / n), c[2] + z) for i in range(n)])
    loft(mb, rings, m, caps)


def ring_at(F, cx, cy, z, r, n, rot=0.0):
    return [tuple(F.p(cx + r * math.cos(rot + 2 * math.pi * i / n), cy + r * math.sin(rot + 2 * math.pi * i / n), z))
            for i in range(n)]


def side_prism(mb, Fr, prof, y0, y1, m):
    """poligono CONVEXO (x, z) no plano vertical do referencial Fr, extrudado na lateral de y0 a y1"""
    bm = mb.bm
    a = [bm.verts.new(Fr.p(x, y0, z)) for x, z in prof]
    b = [bm.verts.new(Fr.p(x, y1, z)) for x, z in prof]
    n = len(prof)
    bm.faces.new(a)
    bm.faces.new(list(reversed(b)))
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((a[j], a[i], b[i], b[j]))
    mb._post(a + b, m, None, 0, 1)


def hsh(*k):
    """hash murmur (finalizador fmix32) -> [0, 1): variacao sem correlacao entre chaves vizinhas"""
    h = 0x9747b28c
    for v in k:
        x = int(round(v * 1000.0)) & 0xffffffff
        x = (x * 0xcc9e2d51) & 0xffffffff
        x = ((x << 15) | (x >> 17)) & 0xffffffff
        h ^= (x * 0x1b873593) & 0xffffffff
        h = ((h << 13) | (h >> 19)) & 0xffffffff
        h = (h * 5 + 0xe6546b64) & 0xffffffff
    h ^= h >> 16
    h = (h * 0x85ebca6b) & 0xffffffff
    h ^= h >> 13
    h = (h * 0xc2b2ae35) & 0xffffffff
    h ^= h >> 16
    return h / 4294967296.0


# ================================================================== pecas Wano (TODO(op_kit))
def giboshi(mb, c, s=1.0, m=GOLD):
    """remate em cebola (giboshi) de ouro sobre colar: o poste-mestre do guarda-corpo vermelho"""
    x, y, z = c
    lathe(mb, (x, y, z), [(0.42 * s, 0.0), (0.44 * s, 0.14 * s), (0.3 * s, 0.2 * s)], m, 8)
    lathe(mb, (x, y, z + 0.18 * s), [(0.26 * s, 0.0), (0.46 * s, 0.24 * s), (0.44 * s, 0.46 * s), (0.26 * s, 0.68 * s),
                                     (0.08 * s, 0.9 * s), (0.0, 1.1 * s)], m, 10)


def chochin(mb, top, s=1.0, drop=0.6, paper=PAPER):
    """lanterna de papel cilindrica (chochin) pendurada de 'top': gancho, tampa e fundo pretos (aro grosso), corpo em
    barril de papel aceso com 3 frisos escuros (as costelas) POR FORA do papel. Devolve o centro (a luz)."""
    t = Vector(top)
    mb.rod(t, t - ZZ * drop, 0.07 * s, IRON, 6)
    zc = t.z - drop - 0.25 * s - 1.0 * s
    c = (t.x, t.y, zc)
    lathe(mb, (t.x, t.y, zc - 1.0 * s), [(0.52 * s, 0.0), (0.74 * s, 0.25 * s), (0.86 * s, 0.6 * s), (0.88 * s, 1.0 * s),
                                         (0.86 * s, 1.4 * s), (0.74 * s, 1.75 * s), (0.52 * s, 2.0 * s)], paper, 10)
    for zz in (0.62, 1.0, 1.38):
        r = (0.86 if zz != 1.0 else 0.88) * s + 0.13 * s
        lathe(mb, (t.x, t.y, zc - 1.0 * s + zz * s - 0.05 * s), [(r, 0.0), (r, 0.1 * s)], BLK, 10, caps=(True, True))
    for z0, z1 in ((-1.22, -0.92), (0.92, 1.22)):
        lathe(mb, (t.x, t.y, zc + z0 * s), [(0.6 * s, 0.0), (0.64 * s, 0.05 * s), (0.64 * s, (z1 - z0) * s),
                                            (0.5 * s, (z1 - z0) * s + 0.06 * s)], BLK, 10)
    return Vector(c)


def andon(mb, c, rot=0.0, s=1.0):
    """lanterna de caixa no topo de um poste: bandeja preta, 4 cantoneiras, papel aceso RECUADO 0,14 atras da trelica,
    quadro de cima e chapeu de 4 aguas preto com remate de ouro. c = topo do poste. Devolve o centro do papel."""
    x, y, z = c
    R = (0, 0, rot)
    ca, sa = math.cos(rot), math.sin(rot)

    def P(a, b, h):
        return (x + (a * ca - b * sa) * s, y + (a * sa + b * ca) * s, z + h * s)
    mb.box((1.7 * s, 1.7 * s, 0.22 * s), P(0, 0, 0.11), R, BLK, 0.0)
    for a in (-1, 1):
        for b in (-1, 1):
            mb.box((0.2 * s, 0.2 * s, 1.5 * s), P(a * 0.68, b * 0.68, 0.97), R, WD, 0.0)
    mb.box((1.06 * s, 1.06 * s, 1.36 * s), P(0, 0, 0.92), R, PAPER, 0.0)
    for k in range(4):
        c_, s_ = math.cos(k * math.pi / 2), math.sin(k * math.pi / 2)
        mb.box((0.08 * s, 0.1 * s, 1.36 * s), P(c_ * 0.68, s_ * 0.68, 0.92), (0, 0, rot + k * math.pi / 2), WD, 0.0)
        mb.box((0.08 * s, 1.24 * s, 0.1 * s), P(c_ * 0.68, s_ * 0.68, 0.92), (0, 0, rot + k * math.pi / 2), WD, 0.0)
    mb.box((1.76 * s, 1.76 * s, 0.18 * s), P(0, 0, 1.78), R, BLK, 0.0)
    lathe(mb, P(0, 0, 1.86), [(1.6 * s, 0.0), (1.62 * s, 0.12 * s), (1.0 * s, 0.46 * s), (0.3 * s, 0.82 * s),
                              (0.2 * s, 0.9 * s)], BLK, 4, rot + math.pi / 4)
    lathe(mb, P(0, 0, 2.7), [(0.22 * s, 0.0), (0.26 * s, 0.12 * s), (0.14 * s, 0.32 * s), (0.0, 0.42 * s)], GOLD, 8)
    return Vector(P(0, 0, 0.92))


def rail_run(mb, a, b, h=3.3, step=4.0, nodes=(0.0, 1.0), node_up=0.85, post=0.5, node_post=0.8, lamps=(),
             lamp_s=0.9, top_w=0.8, gold=GOLD):
    """GUARDA-CORPO VERMELHO (koran Wano) de a ate b (pontos 3D da BASE: o tabuleiro/piso pode ser inclinado):
    pilaretes laqueados a ~step com cinta de ouro (0,13 para fora: sem z-fight) logo abaixo do corrimao, corrimao largo
    (kasagi) que passa 0,45 das pontas, travessa media (nuki) e baixa; postes-mestre mais grossos e mais altos com
    cinta dupla e giboshi de ouro nos 't' de 'nodes'; em 'lamps' (t) o poste-mestre leva uma lanterna de caixa (andon).
    Devolve os centros das lanternas."""
    a, b = Vector(a), Vector(b)
    d = b - a
    ln = d.xy.length
    if ln < 0.5:
        return []
    u = Vector((d.x / ln, d.y / ln, 0.0))
    rz = math.atan2(u.y, u.x)
    k = max(1, int(round(ln / step)))
    big = sorted(set([round(t, 4) for t in nodes] + [round(t, 4) for t in lamps]))
    for i in range(k + 1):
        t = i / k
        if any(abs(t - tn) * ln < step * 0.45 for tn in big):
            continue
        p = a + d * t
        mb.box((post, post, h - 0.3), (p.x, p.y, p.z + (h - 0.3) / 2), (0, 0, rz), LAC, 0.0)
        mb.box((post + 0.26, post + 0.26, 0.22), (p.x, p.y, p.z + h - 0.62), (0, 0, rz), gold, 0.0)
    ext = u * 0.45
    slope = d.z / ln
    for zz, w, hh, m in ((h - 0.17, top_w, 0.34, LAC), (h * 0.56, 0.32, 0.34, LAC), (0.5, 0.36, 0.3, LAC)):
        a2 = a - ext - ZZ * (0.45 * slope) + ZZ * zz
        b2 = b + ext + ZZ * (0.45 * slope) + ZZ * zz
        if zz < h - 0.3:
            a2, b2 = a + ZZ * zz, b + ZZ * zz
        mb.beam(a2, b2, w, hh, m, 0.0)
    out = []
    for tn in big:
        p = a + d * tn
        lamp = tn in [round(t, 4) for t in lamps]
        top = h + (0.25 if lamp else node_up)
        mb.box((node_post, node_post, top + 0.1), (p.x, p.y, p.z + (top + 0.1) / 2 - 0.1), (0, 0, rz), LAC, 0.0)
        for zb in (0.55, top - 0.75):
            mb.box((node_post + 0.26, node_post + 0.26, 0.24), (p.x, p.y, p.z + zb), (0, 0, rz), gold, 0.0)
        if lamp:
            out.append(andon(mb, (p.x, p.y, p.z + top), rz, lamp_s))
        else:
            giboshi(mb, (p.x, p.y, p.z + top), 1.0, gold)
    return out


def nobori(mb, x, y, z, face, h=13.0, w=2.6, cloth=RED, crest=WHITE, col_area=None, flip=False):
    """estandarte vertical (nobori) de Wano: base de pedra, mastro preto com ponteira de ouro, verga no alto, pano
    vermelho preso ao mastro por alcas (chichi) e a verga, BRASAO redondo branco nas 2 faces (0,13 para fora do pano) e
    barra de peso embaixo. face = rumo (rad) para onde o pano olha."""
    F = Frame(x, y, z, face - math.pi / 2)              # +y local = frente do pano
    if flip:                                             # pano do outro lado do mastro (espelho em x local)
        F0 = F

        class _Fm:
            a = F0.a

            def p(self, xx, yy, zz=0.0):
                return F0.p(-xx, yy, zz)

            def r(self, rx=0.0, ry=0.0, rz=0.0):
                return F0.r(rx, ry, rz)
        F = _Fm()
    lathe(mb, tuple(F.p(0, 0, 0)), [(0.95, -0.2), (0.95, 0.45), (0.7, 0.6), (0.45, 0.7)], STD, 8)
    mb.cyl(0.2, h, F.p(0, 0, h / 2 + 0.3), m=BLK, n=8, bevel=0.0)
    lathe(mb, tuple(F.p(0, 0, h + 0.3)), [(0.26, 0.0), (0.26, 0.2), (0.14, 0.5), (0.0, 0.9)], GOLD, 8)
    mb.beam(F.p(-0.15, 0, h - 0.4), F.p(w + 0.55, 0, h - 0.4), 0.18, 0.2, BLK, 0.0)
    top, bot = h - 0.7, h - 0.7 - h * 0.62
    x0, x1 = 0.55, 0.55 + w
    mb.box((w, 0.14, top - bot), F.p((x0 + x1) / 2, 0, (top + bot) / 2), F.r(), cloth, 0.0)
    for zz in [bot + (top - bot) * (i + 0.5) / 6 for i in range(6)]:
        mb.box((0.5, 0.42, 0.3), F.p(0.38, 0, zz), F.r(), cloth, 0.0)
    mb.box((w + 0.2, 0.3, 0.22), F.p((x0 + x1) / 2, 0, bot - 0.08), F.r(), BLK, 0.0)
    cz = top - (top - bot) * 0.22
    for sy in (-1, 1):
        mb.cyl(w * 0.34, 0.12, F.p((x0 + x1) / 2, sy * 0.13, cz), (math.pi / 2, 0, F.a), m=crest, n=16, bevel=0.0)
        mb.cyl(w * 0.16, 0.08, F.p((x0 + x1) / 2, sy * 0.21, cz), (math.pi / 2, 0, F.a), m=cloth, n=12, bevel=0.0)
    if col_area:
        col_box(col_area, (1.6, 1.6, h), F.p(0, 0, h / 2), F.r())


# ================================================================== ponte: tabuleiro + guarda-corpo vermelho
def bridge_deck():
    mb = MB("OP_Ent_Bridge", C, random.Random(5101), detail="near")
    y_a, y_b = Y0, 0.0
    # tabuas atravessadas (0,9 + junta 0,12): topo 0,06 acima da colisao; entram 0,15 na testeira (sem face coplanar)
    y = y_a + 0.06
    while y < y_b - 0.3:
        w = min(0.9, y_b - y)
        yc = y + w / 2
        z = zf(yc) + 0.06
        mb.box((2 * FAS[0] + 0.3, w, PLANK_T), (0.0, yc, z - PLANK_T / 2), (PITCH, 0, 0), WD, 0.0)
        y += w + 0.12
    # longarinas (4) e travessas sob o tabuado (a cada 5,5): aparecem entre os arcos, vistas de baixo
    for x in (-6.4, -2.2, 2.2, 6.4):
        mb.beam((x, y_a, zf(y_a) - PLANK_T - 0.45), (x, y_b, zf(y_b) - PLANK_T - 0.45), 0.8, 0.9, WD, 0.0)
    # M6b (item 10): CONTRATABUADO continuo sob as tabuas (tabua de 0,06 entre o tabuado e as longarinas, de testeira a
    # testeira): as tabuas da cabeceira (y -120..-113) assentam nele e a junta de 0,12 mostra madeira escura, nao o
    # viaduto claro la embaixo
    mb.beam((0.0, y_a, zf(y_a) + 0.06 - PLANK_T - 0.03), (0.0, y_b, zf(y_b) + 0.06 - PLANK_T - 0.03), 2 * FAS[0] + 0.3,
            0.06, WD, 0.0)
    # testeira vermelha continua (le como a borda vermelha da concept): meio-fio 0,35 acima do tabuado
    for s in (-1, 1):
        xc = s * (FAS[0] + FAS[1]) / 2
        hh = 1.6
        mb.beam((xc, y_a, zf(y_a) + 0.35 - hh / 2), (xc, y_b, zf(y_b) + 0.35 - hh / 2), FAS[1] - FAS[0], hh, LAC, 0.0)
        # friso de ouro no pe da testeira (0,13 para fora) - a linha fina que a concept marca sob o vermelho
        mb.beam((s * (FAS[1] + 0.07), y_a, zf(y_a) - 1.1), (s * (FAS[1] + 0.07), y_b, zf(y_b) - 1.1), 0.14, 0.16, GOLD, 0.0)
    # guarda-corpo: nos nas linhas dos pilares do viaduto, postes-lanterna no meio (pilar central) e na cabeca
    lamps_out = {}
    ra, rb = y_a + 0.5, y_b - 0.6
    tn = [(py - ra) / (rb - ra) for py in PIERS if abs(py - PIERS[2]) > 1.0]
    tl = [(PIERS[2] - ra) / (rb - ra), 1.0]
    for s in (-1, 1):
        a = (s * RAIL_X, ra, zf(ra) + 0.35)
        b = (s * RAIL_X, rb, zf(rb) + 0.35)
        lamps_out[s] = rail_run(mb, a, b, h=3.35, step=4.0, nodes=[0.0] + tn, lamps=tl, lamp_s=0.95)
    mb.finish()
    names = {-1: ("L_OPProp_Lamp_Bridge_L", "L_OPProp_Lamp_BridgeHead_L"),
             1: ("L_OPProp_Lamp_Bridge_R", "L_OPProp_Lamp_BridgeHead_R")}
    for s in (-1, 1):
        for nm, c in zip(names[s], lamps_out[s]):
            light(nm, "POINT", tuple(c), 140.0, WARM, 0.4)


# ================================================================== ponte: viaduto de pedra em arcos
def _arch_pts(ya, yb, za, zb, n=12):
    """intradorso semicircular (levemente esconso: as impostas acompanham a rampa) de ya ate yb"""
    r = (yb - ya) / 2
    out = []
    for i in range(n + 1):
        t = i / n
        a = math.pi * (1 - t)
        y = (ya + yb) / 2 + r * math.cos(a)
        zs = za + (zb - za) * (y - ya) / (yb - ya)
        out.append((y, zs + r * math.sin(a)))
    return out


def viaduct():
    mb = MB("OP_Ent_Viaduct", C, random.Random(5201), detail="near")
    rng = random.Random(52)
    top_off = 1.3                        # topo do timpano = zf - 1,3 (sob as longarinas)
    # vaos: entre pilares consecutivos e do ultimo pilar ate o encontro
    faces = [(PIERS[i] + PIER_HD, PIERS[i + 1] - PIER_HD) for i in range(len(PIERS) - 1)]
    faces.append((PIERS[-1] + PIER_HD, ABUT_Y[0]))
    spans = []
    for ya, yb in faces:
        r = (yb - ya) / 2
        za = zf(ya) - 4.3 - r
        zb = zf(yb) - 4.3 - r
        spans.append((ya, yb, za, zb, r))
    # --- timpanos (2 faces) + intradorso (abobada de berco) de cada vao
    for ya, yb, za, zb, r in spans:
        pts = _arch_pts(ya, yb, za, zb, 12)
        for s in (-1, 1):
            x = s * FACE_X
            for (y0, z0), (y1, z1) in zip(pts, pts[1:]):
                q = [(x, y0, z0), (x, y1, z1), (x, y1, zf(y1) - top_off), (x, y0, zf(y0) - top_off)]
                if s < 0:
                    q = q[::-1]
                bm = mb.bm
                vs = [bm.verts.new(p) for p in q]
                bm.faces.new(vs)
                mb._post(vs, ST, None, 0, 1)
        rings = [[(-FACE_X, y_, z_), (FACE_X, y_, z_)] for y_, z_ in pts]
        bm = mb.bm
        V = [[bm.verts.new(p) for p in rr] for rr in rings]
        for p0, p1 in zip(V, V[1:]):
            bm.faces.new((p0[0], p0[1], p1[1], p1[0]))
        mb._post([v for rr in V for v in rr], STD, None, 0, 1)
        # aduelas (arco de pedra escura 0,22 saliente da face) com fecho mais alto
        nv = 13
        for s in (-1, 1):
            for i in range(nv):
                a0 = math.pi * (1 - (i + 0.06) / nv)
                a1 = math.pi * (1 - (i + 0.94) / nv)
                am = (a0 + a1) / 2
                ym = (ya + yb) / 2 + (r + 0.45) * math.cos(am)
                zs = za + (zb - za) * (ym - ya) / (yb - ya)
                zm = zs + (r + 0.45) * math.sin(am)
                ln = 2 * (r + 0.45) * math.sin((a0 - a1) / 2)
                key = i == nv // 2
                dep = 1.6 if key else 1.3            # 0,2 abaixo do intradorso: sem fresta clara na junta
                mb.box((0.62, ln, dep), (s * (FACE_X + 0.2), ym, zm + (0.2 if key else 0.0)),
                       (am - math.pi / 2, 0, 0), STD, 0.06)
    # --- cornija continua sob a testeira (pedra escura, 0,5 para fora da face). M6b (item 11): o lado de dentro dela
    # ficava 0,07 dentro do timpano (coplanar visto por dentro do vao); agora encosta por fora (0,02)
    for s in (-1, 1):
        mb.beam((s * (FACE_X + 0.27), Y0 + 3.0, zf(Y0 + 3.0) - 1.85),
                (s * (FACE_X + 0.27), ABUT_Y[0] + 0.6, zf(ABUT_Y[0] + 0.6) - 1.85), 0.5, 0.6, STD, 0.0)
    # --- pilares: talhamar nas 2 pontas (x), talude, fiadas (faixas alternadas recuadas), imposta e soco na agua
    for k, py in enumerate(PIERS):
        zi = spans[k][2] if k == 0 else min(spans[k - 1][3], spans[k][2])
        zt = zf(py) - top_off

        def plan(sc, grow):
            hx, hy = FACE_X + grow, PIER_HD * sc + grow * 0.6
            nose = 2.6 + grow * 0.5
            return [(hx + nose, py), (hx, py + hy), (-hx, py + hy), (-hx - nose, py), (-hx, py - hy), (hx, py - hy)]
        # miolo acima da imposta (entre os timpanos vizinhos), sem talhamar
        mb.prism(ccw([(FACE_X, py - PIER_HD), (FACE_X, py + PIER_HD), (-FACE_X, py + PIER_HD),
                      (-FACE_X, py - PIER_HD)]), zi, zt, ST)
        # imposta (faixa escura saliente) + capa sextavada do talhamar
        mb.prism(ccw(plan(1.0, 0.25)), zi - 0.7, zi, STD)
        for s in (-1, 1):                                    # capa inclinada do talhamar (prisma triangular)
            bm = mb.bm
            hx = FACE_X + 0.25
            nose = 2.6 + 0.125
            hy = PIER_HD + 0.15
            co = [(s * (hx + nose), py, zi), (s * hx, py + hy, zi), (s * hx, py - hy, zi), (s * hx, py, zi + 2.0)]
            vs = [bm.verts.new(c) for c in co]
            for f in ((0, 1, 3), (0, 3, 2), (1, 2, 3), (0, 2, 1)):
                try:
                    bm.faces.new([vs[i] for i in f])
                except ValueError:
                    pass
            mb._post(vs, STD, None, 0, 1)
        # fuste em fiadas: faixa DURA (alta, face reta) + junta MOLE (fina, recuada 0,14) -> linhas de sombra
        z = zi - 0.7
        j = 0
        while z > SEA_BOT + 0.2:
            hard = j % 2 == 0
            hh = (1.9 + 0.7 * hsh(k, j)) if hard else 0.32
            zb_ = max(SEA_BOT, z - hh)
            grow_t = (zi - z) / max(1.0, zi - 36.0) * 0.9
            grow_b = (zi - zb_) / max(1.0, zi - 36.0) * 0.9
            g0 = 0.0 if hard else -0.14
            loft(mb, [[(p[0], p[1], zb_) for p in plan(1.0, grow_b + g0)],
                      [(p[0], p[1], z) for p in plan(1.0, grow_t + g0)]], ST if hard else STD, caps=(True, True))
            z = zb_
            j += 1
        # soco na linha d'agua (pedra escura, mais largo). M6b (item 11): fundo 0,2 abaixo do pe do fuste (era o mesmo
        # plano z 26, visto da DS por baixo)
        mb.prism(ccw(plan(1.0, 1.6)), SEA_BOT - 0.2, 37.4, STD)
    # --- encontro de pedra na falesia (o patamar): bloco + 2 alas abertas a 35 graus, fiadas e capa
    y0, y1 = ABUT_Y
    zt = zf(y0) - top_off
    hx = 12.2
    mb.prism(ccw([(hx, y0), (hx, y1 + 3.0), (-hx, y1 + 3.0), (-hx, y0)]), SEA_BOT + 6.0, zt, ST)
    # imposta do ultimo arco no encontro
    r_last = spans[-1][4]
    zi = spans[-1][3]
    mb.box((2 * FACE_X + 0.5, 0.5, 0.7), (0.0, y0 - 0.25, zi - 0.35), (0, 0, 0), STD, 0.0)
    # fiadas na face do encontro (junta recuada: faixas escuras finas 0,1 a frente nao; aqui recuadas = prisma por tras)
    z = zt - 2.4
    j = 0
    while z > 40.0:
        mb.box((2 * hx + 0.3, 0.28, 0.3), (0.0, y0 - 0.02, z), (0, 0, 0), STD, 0.0)
        z -= 2.2 + 0.6 * hsh(9, j)
        j += 1
    for s in (-1, 1):                                        # alas: muro em talude encostando na falesia
        a = Vector((s * hx, y0, 0))
        dirv = Vector((s * math.sin(math.radians(35.0)), math.cos(math.radians(35.0)), 0)).normalized()
        b = a + dirv * 9.0
        mid = (a + b) / 2
        ang = math.atan2(dirv.y, dirv.x)
        mb.box((9.0, 2.2, zt - (SEA_BOT + 8.0)), (mid.x, mid.y, (zt + SEA_BOT + 8.0) / 2), (0, 0, ang), ST, 0.0)
        mb.box((9.4, 2.6, 0.6), (mid.x, mid.y, zt + 0.3), (0, 0, ang), STD, 0.0)
    # capa do encontro sob a ponta da ponte (berco das longarinas)
    mb.box((2 * hx + 0.6, y1 + 3.0 - y0 + 0.4, 0.6), (0.0, (y0 + y1 + 3.0) / 2, zt + 0.3), (0, 0, 0), STD, 0.0)
    ob = mb.finish()
    # M6b (item 11): o recalc do finish virava para DENTRO ~26 quadros dos timpanos (cascas abertas): no Roblox (face
    # unica) eles sumiam vistos de fora. Timpano = face no plano x = +-FACE_X: normal sempre para fora
    if ob is not None:
        n = 0
        for p in ob.data.polygons:
            c = p.center
            if abs(p.normal.x) > 0.9 and abs(abs(c.x) - FACE_X) < 0.03 and p.normal.x * c.x < 0:
                p.flip()
                n += 1
        ob.data.update()
        print("op_entry: timpanos virados para fora: %d" % n)


def bridge_banners():
    """2 nobori vermelhos na PARTIDA da ponte (concept: bandeiras vermelhas na cabeceira de baixo), presos por fora da
    testeira no primeiro pilar (o mastro nasce da imposta do pilar, fora do piso)"""
    mb = MB_LAMPS
    for s in (-1, 1):
        py = PIERS[0]
        x = s * (FAS[1] + 0.9)
        zb = zf(py) - 1.3
        # console de pedra para o mastro (sai da face do pilar)
        mb.box((1.9, 2.0, 1.0), (s * (FACE_X + 0.9), py, zb - 0.5), (0, 0, 0), STD, 0.0)
        nobori(mb, x, py, zb, -math.pi / 2, h=13.5, w=2.4, flip=(s > 0))


# ================================================================== grande torii
TOR_PX0, TOR_PX1 = 11.9, 11.5           # centro do pilar no pe / no topo (uchikorobi: inclina para dentro)
TOR_R0, TOR_R1 = 1.8, 1.5
TOR_HP = 25.0                            # topo do pilar = base do shimaki (no centro)
TOR_NUKI = L.TORII_H                     # base do nuki = vao livre de 22
TOR_KL = 2 * (TOR_PX1 + 7.6)             # comprimento do kasagi (34,8)


def _sori(x, amp=2.1):
    t = max(0.0, (abs(x) - 3.0) / (TOR_KL / 2 - 3.0))
    return amp * t ** 2.0


def grand_torii():
    x0, y0 = L.TORII_IN
    mb = MB("OP_Ent_Torii", C, random.Random(5401), detail="hero")
    F = Frame(x0, y0, T0, 0.0)                     # +x local = atravessado; +y = quem atravessa (norte)
    area = "OP_EntTorii"

    def pcx(zz):
        t = (zz - 1.0) / (TOR_HP - 1.0)
        return TOR_PX0 + (TOR_PX1 - TOR_PX0) * t, TOR_R0 + (TOR_R1 - TOR_R0) * t
    for s in (-1, 1):
        c0 = F.p(s * TOR_PX0, 0, 0)
        # dai-ishi: placa octogonal de pedra escura enterrada 0,3 + kamebara
        lathe(mb, (c0.x, c0.y, c0.z), [(2.9, -0.3), (2.9, 0.4), (2.55, 0.56)], STD, 8, math.pi / 8)
        lathe(mb, (c0.x, c0.y, c0.z), [(2.25, 0.54), (2.15, 0.8), (1.75, 1.0), (TOR_R0 + 0.2, 1.08)], STD, 12)
        ztop = TOR_HP + _sori(TOR_PX1) + 0.15
        loft(mb, [ring_at(F, s * TOR_PX0, 0, 0.95, TOR_R0, 16), ring_at(F, s * TOR_PX1, 0, ztop, TOR_R1, 16)], LAC)
        # nemaki preto (0,18 para fora) com labio, e a cinta de ouro no labio
        xa, ra = pcx(0.95)
        xb, rb = pcx(3.3)
        loft(mb, [ring_at(F, s * xa, 0, 0.9, ra + 0.18, 16), ring_at(F, s * xb, 0, 3.3, rb + 0.18, 16)], BLK)
        xc, rc = pcx(3.55)
        loft(mb, [ring_at(F, s * xb, 0, 3.26, rb + 0.32, 16), ring_at(F, s * xc, 0, 3.55, rc + 0.32, 16)], GOLD)
        # daiwa preto + cinta de ouro sob o shimaki
        xd, rd = pcx(TOR_HP - 0.8)
        loft(mb, [ring_at(F, s * xd, 0, TOR_HP - 0.82, rd + 0.18, 16),
                  ring_at(F, s * TOR_PX1, 0, TOR_HP + _sori(TOR_PX1) + 0.02, TOR_R1 + 0.18, 16)], BLK)
        xe, re_ = pcx(TOR_HP - 1.2)
        loft(mb, [ring_at(F, s * xe, 0, TOR_HP - 1.22, re_ + 0.3, 16), ring_at(F, s * xd, 0, TOR_HP - 0.86, rd + 0.3, 16)],
             GOLD)
        col_box(area, (3.7, 3.7, TOR_HP + 1.0), F.p(s * TOR_PX0, 0, (TOR_HP + 1.0) / 2), F.r())
    # nuki passante (sai 3,1 de cada lado) com cunhas (kusabi) e ponteira de ouro
    xn, rn = pcx(TOR_NUKI + 0.75)
    half = xn + rn + 3.1
    nh = 1.5
    mb.box((2 * half, 1.1, nh), F.p(0, 0, TOR_NUKI + nh / 2), F.r(), LAC, 0.06)
    for s in (-1, 1):
        mb.box((0.42, 1.36, nh + 0.34), F.p(s * (xn + rn + 0.3), 0, TOR_NUKI + nh / 2), F.r(), LAC, 0.05)
        mb.box((0.3, 1.36, nh + 0.26), F.p(s * (half + 0.12), 0, TOR_NUKI + nh / 2), F.r(), GOLD, 0.0)
    # gakuzuka (montante do meio) + placa (gaku): quadro de ouro, campo escuro, brasao redondo de ouro (sem texto)
    gz0, gz1 = TOR_NUKI + nh, TOR_HP
    mb.box((1.1, 0.8, gz1 - gz0), F.p(0, 0, (gz0 + gz1) / 2), F.r(), LAC, 0.05)
    pw, ph = 3.2, 2.9
    pz = (gz0 + gz1) / 2 + 0.1
    mb.box((pw + 0.5, 0.5, ph + 0.5), F.p(0, -0.55, pz), F.r(), GOLD, 0.05)
    mb.box((pw, 0.5, ph), F.p(0, -0.72, pz), F.r(), BLK, 0.0)
    mb.cyl(0.95, 0.3, F.p(0, -1.0, pz), (math.pi / 2, 0, 0), m=GOLD, n=16, bevel=0.0)
    mb.cyl(0.5, 0.3, F.p(0, -1.18, pz), (math.pi / 2, 0, 0), m=BLK, n=12, bevel=0.0)
    mb.box((pw + 0.5, 0.5, ph + 0.5), F.p(0, 0.55, pz), F.r(), GOLD, 0.05)       # verso (quem volta tambem ve)
    mb.box((pw, 0.5, ph), F.p(0, 0.72, pz), F.r(), BLK, 0.0)
    # shimaki vermelho (verga de baixo) com o sori
    SL = 2 * (TOR_PX1 + 4.4)
    secs = []
    for i in range(17):
        xx = -SL / 2 + SL * i / 16
        zb = TOR_HP + _sori(xx)
        secs.append([tuple(F.p(xx, yy, zz)) for yy, zz in ((-0.62, zb), (0.62, zb), (0.62, zb + 1.2), (-0.62, zb + 1.2))])
    loft(mb, secs, LAC)
    # kasagi preto: mais alto e mais fundo nas pontas, ponta cortada (hana) inclinada
    secs = []
    n = 18
    for i in range(n + 1):
        xx = -TOR_KL / 2 + TOR_KL * i / n
        t = abs(xx) / (TOR_KL / 2)
        zb = TOR_HP + 1.2 + _sori(xx)
        h = 1.35 + 0.35 * t * t
        d = 1.9 + 0.3 * t * t
        xb_ = xx - math.copysign(0.6, xx) if i in (0, n) else xx
        secs.append([tuple(F.p(xb_, -d / 2, zb)), tuple(F.p(xb_, d / 2, zb)),
                     tuple(F.p(xx, d / 2 + 0.08, zb + h)), tuple(F.p(xx, -d / 2 - 0.08, zb + h))])
    loft(mb, secs, BLK)

    def zk(xx):
        t = min(1.0, abs(xx) / (TOR_KL / 2))
        return TOR_HP + 1.2 + _sori(max(-TOR_KL / 2, min(TOR_KL / 2, xx))) + 1.35 + 0.35 * t * t
    # capa de telha (2 aguas finas com beiral 1,75) acompanhando o sori, canais e cumeeira com onigawara
    E, R = 1.75, 0.55
    KR = TOR_KL / 2 + 0.3
    secs = []
    for i in range(n + 1):
        xx = -KR + 2 * KR * i / n
        z0 = zk(xx) - 0.04 + (0.06 if i in (0, n) else 0.0)
        secs.append([tuple(F.p(xx, -E, z0)), tuple(F.p(xx, -E, z0 + 0.22)), tuple(F.p(xx, 0, z0 + 0.22 + R)),
                     tuple(F.p(xx, E, z0 + 0.22)), tuple(F.p(xx, E, z0)), tuple(F.p(xx, 0, z0 + R - 0.05))])
    loft(mb, secs, TILE)
    k = int((2 * KR - 0.8) / 0.82)
    for i in range(k + 1):
        xx = -KR + 0.4 + (2 * KR - 0.8) * i / k
        z0 = zk(xx) - 0.04
        for s in (-1, 1):
            a = F.p(xx, s * (E - 0.08), z0 + 0.22 + R * 0.08 / E + 0.06)
            b = F.p(xx, s * 0.36, z0 + 0.22 + R * (1 - 0.36 / E) + 0.06)
            mb.beam(a, b, 0.28, 0.17, TILE, 0.0)
    secs = []
    for i in range(n + 1):
        xx = -(KR - 0.2) + 2 * (KR - 0.2) * i / n
        zr = zk(xx) - 0.04 + 0.22 + R
        secs.append([tuple(F.p(xx, 0.36 * math.cos(a), zr + 0.05 + 0.3 * math.sin(a)))
                     for a in (math.radians(dd) for dd in (0, 50, 90, 130, 180, 270))])
    loft(mb, secs, BLK)
    for s in (-1, 1):
        xx = s * (KR - 0.1)
        zr = zk(xx) - 0.04 + 0.22 + R
        mb.box((0.6, 1.0, 1.05), F.p(xx, 0, zr + 0.3), F.r(0, s * 0.25, 0), BLK, 0.06)
        mb.box((0.66, 1.06, 0.2), F.p(xx, 0, zr + 0.86), F.r(0, s * 0.25, 0), GOLD, 0.0)
        # ponteira de ouro na ponta do kasagi (kanamono)
        zt_ = zk(s * TOR_KL / 2)
        mb.box((0.5, 2.5, 0.7), F.p(s * (TOR_KL / 2 - 0.55), 0, zt_ - 0.6), F.r(0, s * 0.18, 0), GOLD, 0.0)
    # CHOCHIN: 2 nas pontas do nuki (por fora) e 2 nos pilares (lado de dentro, acima da cabeca)
    lamps = []
    for s in (-1, 1):
        lamps.append(chochin(mb, F.p(s * (half - 0.9), 0, TOR_NUKI - 0.02), 1.15, drop=0.7))
        xp, rp = pcx(12.5)
        br0 = F.p(s * (xp - rp + 0.05), 0, 12.6)
        br1 = F.p(s * (xp - rp - 1.35), 0, 12.6)
        mb.beam(br0, br1, 0.22, 0.22, IRON, 0.0)
        mb.box((0.5, 0.5, 0.12), br0 + Vector((s * -0.05, 0, -0.35)), (0, 0, 0), IRON, 0.0)
        lamps.append(chochin(mb, br1 - ZZ * 0.05, 0.95, drop=0.35))
    mb.finish()
    return lamps


# ================================================================== patio T0
COURT_HOLES = []                                  # (x, y, raio) preenchido em court()
TORO_COURT = [(-15.6, 3.6, 1.15), (15.6, 3.6, 1.15), (-13.4, 29.0, 1.0), (13.4, 29.0, 1.0)]
NOBORI_AT = [(-19.8, 7.0), (19.8, 7.0)]


def _paving(mb):
    """lajes do patio: SANDO claro (Stone_OP_Path, lajes grandes) da ponte a escada, lajes de pedra media (Stone_OP) no
    resto, em fiadas desencontradas; berco escuro por baixo (as juntas leem escuras). Topo T0 + 0,32 (berco T0 + 0,14:
    0,14 acima do tampo do terreno -> sem z-fight)."""
    court = DL.offset_poly(ccw(L.ENTRY_COURT), -0.35)
    mb.prism(ccw(DL.offset_poly(court, -0.05)), T0 - 0.1, T0 + 0.14, STD)
    holes = [(L.TORII_IN[0] + s * TOR_PX0, L.TORII_IN[1], 3.1) for s in (-1, 1)]
    holes += [(x, y, 1.9 * s) for x, y, s in TORO_COURT]
    holes += [(x, y, 1.25) for x, y in NOBORI_AT]
    stair = (-9.4, 33.6, 9.4, 40.0)
    z = T0 + 0.32
    y = 0.25
    row = 0
    while y < 34.0:
        h = (2.1, 1.7, 1.9, 2.3)[row % 4]
        if y + h > 33.75:
            h = 33.75 - y
        if h < 0.6:
            break
        # sando: 3 lajes largas (x -5..5) com junta desencontrada; lados: lajes de 1,8..3,2
        cuts = [-5.0, -1.6 + 1.1 * (hsh(row, 1) - 0.5), 1.8 + 1.1 * (hsh(row, 2) - 0.5), 5.0]
        for xa, xb in zip(cuts, cuts[1:]):
            cx, cy = (xa + xb) / 2, y + h / 2
            mb.box((xb - xa - 0.16, h - 0.16, 0.42), (cx, cy, z - 0.21), (0, 0, 0), STP, 0.06)
        for sgn in (-1, 1):
            x = 5.0
            j = 0
            while x < 28.0:
                w = 1.8 + 1.4 * hsh(row, j, sgn)
                if row % 2:
                    w *= 0.8 if j == 0 else 1.0
                xa, xb = x, x + w
                cx, cy = sgn * (xa + xb) / 2, y + h / 2
                corners = [(sgn * (xa + 0.1), y + 0.1), (sgn * (xb - 0.1), y + 0.1), (sgn * (xa + 0.1), y + h - 0.1),
                           (sgn * (xb - 0.1), y + h - 0.1)]
                inside = all(L.point_in_poly(px, py_, court) for px, py_ in corners)
                hole = any(math.hypot(cx - hx, cy - hy) < hr + max(w, h) * 0.42 for hx, hy, hr in holes)
                st = stair[0] <= cx <= stair[2] and cy >= stair[1]
                par = abs(cx) > 10.4 and y < 1.45
                if inside and not hole and not st and not par:
                    mb.box((w - 0.16, h - 0.16, 0.42), (cx, cy, z - 0.21), (0, 0, (hsh(row, j, sgn, 3) - 0.5) * 0.02),
                           ST, 0.06)
                x = xb
                j += 1
        y += h
        row += 1
    # rodelas de pedra escura em volta das bases (pilares do torii, toro, nobori): o furo do lajeado vira desenho
    for hx, hy, hr in holes[2:]:
        lathe(mb, (hx, hy, T0 + 0.1), [(hr + 0.1, 0.0), (hr + 0.1, 0.32), (hr - 0.25, 0.38)], STD, 12)


def court():
    mb = MB("OP_Ent_Court", C, random.Random(5501), detail="near")
    _paving(mb)
    # muro baixo de pedra (tamagaki) na borda sul do patio, das cabeceiras da ponte ate as rochas dos ombros
    for s in (-1, 1):
        xa, xb = s * 11.0, s * 25.4
        cx = (xa + xb) / 2
        ln = abs(xb - xa)
        mb.box((ln, 1.1, 1.39), (cx, 0.75, T0 + 0.495), (0, 0, 0), ST, 0.06)
        mb.box((ln + 0.3, 1.5, 0.3), (cx, 0.75, T0 + 1.34), (0, 0, 0), STD, 0.05)
        for x in (xa, xa + (xb - xa) * 0.5, xb):
            mb.box((1.5, 1.5, 2.04), (x, 0.75, T0 + 0.82), (0, 0, 0), STD, 0.06)
            lathe(mb, (x, 0.75, T0 + 1.84), [(1.0, 0.0), (1.02, 0.12), (0.55, 0.42), (0.0, 0.6)], ST, 4, math.pi / 4)
    # escadaria Chegada (patio -> rua de chegada): escada de pedra do op_kit no envelope do op_col
    foot, deg, w, ns, tread, g = L.stair_frame("Chegada")
    K.stair_stone(mb, Frame(foot[0], foot[1], foot[2], math.radians(deg) - math.pi / 2), w, ns,
                  rise=L.stair_rise("Chegada"), tread=tread, z_floor=-0.3)
    for sx in (-1, 1):                          # pilaretes de arranque do kit (fora da faixa da guarda da escada)
        col_box("OP_EntStair", (1.7, 1.5, 2.2), (foot[0] + sx * (w / 2 + 0.6), foot[1] - 0.55, foot[2] + 1.1))
    mb.finish()
    # toro de pedra do kit: 2 na cabeca da ponte (concept) e 2 no pe da escada; nobori do kit (vermelho, brasao branco)
    mt = MB_LAMPS
    names = ("L_OPProp_Toro_In_L", "L_OPProp_Toro_In_R", None, None)
    for (x, y, s), nm in zip(TORO_COURT, names):
        K.toro(mt, Frame(x, y, T0 + 0.1, 0.0), s, nm, 60.0)
        col_box("OP_EntToro", (2.8 * s, 2.8 * s, 7.6 * s), (x, y, T0 + 3.8 * s))
    for x, y in NOBORI_AT:
        K.banner(mt, Frame(x, y, T0 + 0.1, 0.0), h=14.0, cloth=RED, crest=WHITE, cw=2.6, side=(1 if x > 0 else -1))
        col_box("OP_EntBanner", (1.9, 1.9, 14.0), (x, y, T0 + 7.0))
    # arbustos podados (karikomi) nos cantos do patio, junto das rochas dos ombros: massas arredondadas em 2 tons
    for x, y, r in ((-23.2, 4.0, 1.7), (-21.6, 2.4, 1.2), (23.0, 4.4, 1.8), (21.4, 2.6, 1.15), (-23.0, 30.4, 1.6),
                    (23.4, 30.0, 1.6), (-24.6, 18.0, 1.3), (24.8, 17.0, 1.3)):
        mt.ico(r, (x, y, T0 + 0.14 + r * 0.55), LEAF, 1, scale=(1.25, 1.1, 0.8))
        mt.ico(r * 0.62, (x + r * 0.4, y - r * 0.2, T0 + 0.14 + r * 1.05), "Leaf_OP_Pine", 1, scale=(1.2, 1.1, 0.75))


# ================================================================== cameras de estudio (closes da zona)
def _c(a, b, lens):
    return (tuple(round(c, 2) for c in a), tuple(round(c, 2) for c in b), lens)


EYE = L.EYE
CAMS = {
    "CAM_OPEnt_BridgeHead": _c((0.0, Y0 + 4.0, zf(Y0 + 4.0) + EYE), (0.0, 10.0, T0 + 15.0), 22),
    "CAM_OPEnt_UnderTorii": _c((2.0, 9.0, T0 + EYE), (0.0, 60.0, T1 + 9.0), 22),
    "CAM_OPEnt_ToriiBack": _c((-4.0, 30.0, T0 + EYE), (0.0, -20.0, T0 + 14.0), 22),
    "CAM_OPEnt_Stair": _c((3.0, 38.0, T0 + 2.0 + EYE), (0.0, 120.0, T1 + 12.0), 22),
    "CAM_OPEnt_StairTop": _c((-5.0, 47.0, T1 + EYE), (0.0, -30.0, T0 + 6.0), 24),
    "CAM_OPEnt_ToriiTop": _c((9.0, -9.0, T0 + 21.0), (3.0, 10.0, T0 + 25.5), 30),
    "CAM_OPEnt_ToriiBase": _c((-3.0, 1.0, T0 + 3.2), (-10.6, 10.0, T0 + 2.4), 30),
    "CAM_OPEnt_Rail": _c((-4.0, -78.0, zf(-78.0) + EYE), (RAIL_X, -68.0, zf(-68.0) + 3.0), 28),
    "CAM_OPEnt_Side": _c((-95.0, -80.0, 66.0), (0.0, -58.0, 60.0), 24),
    "CAM_OPEnt_Under": _c((34.0, -40.0, 44.0), (0.0, -66.0, 70.0), 24),
    "CAM_OPEnt_Abutment": _c((-36.0, -40.0, 72.0), (0.0, -6.0, 66.0), 24),
    "CAM_OPEnt_Court": _c((18.0, 34.0, T0 + 9.0), (-4.0, 0.0, T0 + 3.0), 24),
}


MB_LAMPS = None


def build():
    global MB_LAMPS
    MB_LAMPS = MB("OP_Ent_Lamps", C, random.Random(5502), detail="near")   # toro + nobori + arbustos (1 objeto)
    bridge_deck()
    viaduct()
    bridge_banners()
    lamps = grand_torii()
    court()
    MB_LAMPS.finish()
    MB_LAMPS = None
    return lamps
