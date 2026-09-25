# db_entrance - Ilha 2 (Dragon Ball), zona ENTRADA (prefixo DB_Ent_, colecao 02_TERRAIN).
# Caminho do jogador: ponte da Ilha 1 (Naruto) -> PONTE DE CHEGADA (y -186..-130, tabuleiro DECK 16,2) -> ESCADARIA
# (10 x 0,8, y -130..-112) entre dois muros de arenito com bastioes e lanternas -> PORTAL CAPSULE (y -104, vao
# 18 x 16) -> PRACA DE ENTRADA (GROUND 24,2) -> promenade da arena (y ~ -74).
# Transicao GRADUAL de mundo (missao secao 10), ao longo da ponte (t = 0 na Ilha 1, 1 no pe da escada):
#   - calcamento: Stone_Paving_Warm (Konoha) -> Stone_Paving_DB, com uma faixa central de arenito que nasce no meio;
#   - corpo/aduelas/aparelho dos timpanos: pedra cinza-bege da Ilha 1 -> blocos de arenito DB;
#   - guarda-corpo: meio-fio cinza + cerca de madeira escura -> meio-fio de arenito + travessas laranja;
#   - lanternas: caixa de pedra (Konoha) -> hibrida -> lampiao Capsule (globo laranja, discos brancos, cupula azul);
#   - raizes dos pilares: rocha bege (Konoha) -> arenito laranja em estratos; rochas quentes nos bastioes;
#   - no alto: arquitetura Capsule (portal azul-marinho/branco com medalhao, floreiras brancas, piso com anel azul).
# Colisao: o andavel (ponte, escada, praca, guardas da ponte e da escada) e do db_col. Aqui so os volumes proprios:
#   pilares do portal, mureta dos muros da escadaria (lado do plato), bastioes, floreiras, bancos, troncos, postes.
import math, random
from mathutils import Vector
import fm_lib
import db_lib as DL
from db_lib import MB, col_box, col_box2, light, dome
import db_layout as L
import db_col
import fm_parts as FP
import fm_portal_kit as PK
import db_veg_kit as VG
from il_village_kit import VMB, lathe

C = "02_TERRAIN"
Z = L.DECK                      # 16,2
G = L.GROUND                    # 24,2
Y0, Y1 = L.BRIDGE_Y0, L.BRIDGE_Y1          # -186, -130
HWD = L.DECK_W / 2              # 9: meia largura andavel (guardas do db_col em 9..10,2)
HWB = 10.4                      # face externa do corpo da ponte
RAIL_X = 9.6                    # eixo do guarda-corpo (linha da guarda invisivel)
Z_TOP = Z - 0.35                # topo do corpo (sob o calcamento)
CROWN = Z - 3.0                 # intradorso no fecho dos arcos
SPANS = [(-183.0, -173.0), (-170.0, -160.0), (-157.0, -147.0), (-144.0, -134.0)]
PIERS = [(-186.0, -183.0, -6.0), (-173.0, -170.0, -10.0), (-160.0, -157.0, -10.0), (-147.0, -144.0, -8.0)]
R_ARCH = 5.0
ZS = CROWN - R_ARCH             # nascenca dos arcos (8,2)
Y_ABUT = -134.0                 # encontro: face do plato (borda da ilha)
STATIONS = [-184.4, -171.5, -158.5, -145.5, -131.5]      # postes com lanterna (~13 de passo)
GATE_Y = L.GATE_Y
GATE_PX = L.GATE_OPEN_W / 2 + 2.9   # 11,9: centro dos pilares do portal (plinto r 2,9 -> vao livre 18)
NOTCH_X = L.ENTRY_STAIR_W / 2 + 1.3  # 11,3: face interna dos muros da escadaria
BAST = (NOTCH_X, 16.8, -138.6, -132.0)      # bastiao (x0, x1 do lado +, y0, y1)
SPAWN = L.ENTRY_SPAWN

# ------------------------------------------------------------------ materiais novos da zona (2 de 5)
fm_lib.MATS.setdefault("Stone_DBEntSand", (fm_lib.S(212, 146, 94), 0.85, 0.0, 0, None, 0.12))   # arenito quente
fm_lib.MATS.setdefault("Wood_DBEntRail", (fm_lib.S(188, 100, 50), 0.6, 0.0, 0, None, 0.10))     # travessa laranja

SAND = "Stone_DBEntSand"
RAILW = "Wood_DBEntRail"

# ------------------------------------------------------------------ cameras de revisao (360 + altura do jogador)
CAMS = {
    # frente: vindo da Ilha 1 (sobre o vazio, eixo da ponte)
    "CAM_DBEnt_FromNaruto": ((0.0, -232.0, Z + 13.0), (0.0, -122.0, G + 5.0), 24),
    # altura do jogador na ponte (olho 5,2 acima do tabuleiro)
    "CAM_DBEnt_PlayerBridge": ((2.5, -176.0, Z + 5.2), (0.0, -104.0, G + 7.0), 22),
    # altura do jogador na escadaria (degrau 4) olhando o portal
    "CAM_DBEnt_PlayerStair": ((-3.0, -124.0, Z + 3.2 + 5.2), (0.0, -100.0, G + 11.0), 22),
    # tras: da praca olhando o portal e a ponte (o que o jogador ve quando volta)
    "CAM_DBEnt_PlazaBack": ((6.0, -80.0, G + 6.0), (0.0, -140.0, Z + 6.0), 20),
    # lados: arcos, pilares, raizes, bastioes, muros
    "CAM_DBEnt_SideW": ((-82.0, -176.0, 36.0), (0.0, -140.0, 8.0), 24),
    "CAM_DBEnt_SideE": ((72.0, -110.0, 46.0), (0.0, -128.0, 16.0), 24),
    # tras do portal: o medalhao visto da praca (o "C" tem que ler certo dos dois lados)
    "CAM_DBEnt_GateBack": ((4.0, -76.0, G + 7.0), (0.0, -104.0, G + 17.0), 22),
    # altura do jogador na praca: o portal com as duas palmeiras das floreiras (a primeira coisa depois do spawn)
    "CAM_DBEnt_PlayerPalms": ((0.0, -70.0, G + 5.2), (0.0, -104.0, G + 7.5), 20),
    # perto de uma palmeira da floreira (tronco curvo, pe alargado, coroa de 2 andares)
    "CAM_DBEnt_PlayerPalm": ((6.0, -84.0, G + 5.2), (17.0, -98.0, G + 6.5), 22),
}


# ------------------------------------------------------------------ util
def tpos(y):
    """0 na ponta da Ilha 1, 1 no pe da escadaria"""
    return max(0.0, min(1.0, (y - Y0) / (Y1 - Y0)))


def smooth(a, b, x):
    t = max(0.0, min(1.0, (x - a) / (b - a)))
    return t * t * (3.0 - 2.0 * t)


def p_db(y):
    """probabilidade de uma peca da ponte ja ser DB (arenito/calcamento claro) na posicao y"""
    return smooth(0.22, 0.82, tpos(y))


def arch_pts(a, b, n=14):
    yc, R = (a + b) / 2, (b - a) / 2
    return [(yc + R * math.cos(math.pi * (1 - i / n)), ZS + R * math.sin(math.pi * (1 - i / n))) for i in range(n + 1)]


def loft_y(mb, ys, zb, hw, z_top, m):
    """corpo macico da ponte entre secoes y (fundo zb[i] = intradorso, topo z_top, largura 2*hw)"""
    bm = mb.bm
    rings = []
    for y, z in zip(ys, zb):
        rings.append([bm.verts.new((-hw, y, z_top)), bm.verts.new((hw, y, z_top)), bm.verts.new((hw, y, z)),
                      bm.verts.new((-hw, y, z))])
    for r0, r1 in zip(rings, rings[1:]):
        for j in range(4):
            j2 = (j + 1) % 4
            bm.faces.new((r0[j], r0[j2], r1[j2], r1[j]))
    bm.faces.new(rings[0])
    bm.faces.new(list(reversed(rings[-1])))
    mb._post([v for r in rings for v in r], m, None, 0, 1)


def db_lamp(mb, x, y, z, s=1.0):
    """lampiao Capsule: pescoco azul-marinho, disco branco, globo laranja aceso, disco branco, cupula azul"""
    mb.cyl(0.36 * s, 0.7 * s, (x, y, z + 0.35 * s), m="Plaster_DB_Navy", n=10, bevel=0.0)
    mb.cyl(0.88 * s, 0.28 * s, (x, y, z + 0.84 * s), m="Plaster_DB_White", n=14, bevel=0.0)
    mb.cyl(0.62 * s, 1.35 * s, (x, y, z + 0.98 * s + 0.675 * s), m="Lantern_Glow", n=12, bevel=0.0)
    mb.cyl(0.92 * s, 0.28 * s, (x, y, z + 2.33 * s + 0.14 * s), m="Plaster_DB_White", n=14, bevel=0.0)
    dome(mb, (x, y), 0.66 * s, z + 2.61 * s, "Roof_DB_Blue", n=12, rings=3, squash=0.9)
    return Vector((x, y, z + 1.65 * s))


def konoha_lantern(mb, x, y, z, ped="Stone_Wall_Light", cap="Stone_Wall_Dark", s=1.0, ph=3.1):
    """poste de pedra com lanterna de caixa (a linguagem da ponte da Ilha 1); ph = altura do pedestal"""
    mb.box((1.4 * s, 1.4 * s, ph), (x, y, z + ph / 2), (0, 0, 0), ped, 0.12)
    mb.box((1.8 * s, 1.8 * s, 0.36), (x, y, z + ph + 0.18), (0, 0, 0), cap, 0.06)
    mb.box((1.05 * s, 1.05 * s, 1.25), (x, y, z + ph + 0.36 + 0.62), (0, 0, 0), "Lantern_Glow", 0.0)
    mb.box((1.55 * s, 1.55 * s, 0.26), (x, y, z + ph + 1.61 + 0.13), (0, 0, 0), cap, 0.0)
    mb.cyl(1.1 * s, 0.8, (x, y, z + ph + 1.87 + 0.4), (0, 0, math.pi / 4), cap, 4, r2=0.2, bevel=0.0)


def rect_circle(x0, y0, x1, y1, cx, cy, r):
    qx = min(max(cx, x0), x1)
    qy = min(max(cy, y0), y1)
    return math.hypot(qx - cx, qy - cy) < r


# ------------------------------------------------------------------ 1. ponte de chegada: corpo, arcos, pilares
def bridge_body(mb, rng):
    # pilares (topo = nascenca) e corpo sobre eles
    for i, (y0, y1, zb) in enumerate(PIERS):
        db = i >= 2
        body_m = "Stone_DB_Block" if db else "Stone_Wall_Light"
        band_m = SAND if db else "Stone_Wall_Dark"
        mb.box2((-HWB, y0, ZS), (HWB, y1, Z_TOP), body_m, 0.0)
        ln = y1 - y0
        yc = (y0 + y1) / 2
        h = (ZS - 0.6) - (zb + 0.8)
        FP.frustum(mb, (0.0, yc, zb + 0.8), 2 * (HWB + 1.1), ln + 1.4, 2 * (HWB + 0.35), ln + 0.3, h, body_m)
        mb.box((2 * HWB + 1.6, ln + 0.9, 0.6), (0.0, yc, ZS - 0.3), (0, 0, 0), band_m, 0.08)      # imposta
        mb.box((2 * HWB + 3.0, ln + 2.4, 1.0), (0.0, yc, zb + 0.5), (0, 0, 0), band_m, 0.1)       # sapata
        # cunhais alternados nas quinas da face do pilar (o tom da ponta seguinte ja aparece aqui)
        k = 0
        z = zb + 1.4
        while z < ZS - 1.4:
            tt = (z - (zb + 0.8)) / h
            face = HWB + 0.35 + 0.75 * (1.0 - tt)
            half = (ln + 0.3 + 1.1 * (1.0 - tt)) / 2
            for s in (-1, 1):
                for e in (-1, 1):
                    w = 1.5 if (k + (e > 0)) % 2 == 0 else 0.9
                    if db:
                        qm = SAND if w > 1.0 else "Stone_Paving_DB_B"
                    else:
                        qm = SAND if (i == 1 and w > 1.0 and rng.random() < 0.35) else "Stone_Paving_Warm"
                    mb.box((0.35, w, 1.0), (s * (face + 0.06), yc + e * (half - w / 2 + 0.06), z + 0.5), (0, 0, 0),
                           qm, 0.0)
            z += 1.7
            k += 1
    # arcos plenos: corpo com o intradorso por baixo
    for i, (a, b) in enumerate(SPANS):
        pts = arch_pts(a, b, 16)
        loft_y(mb, [p[0] for p in pts], [p[1] for p in pts], HWB, Z_TOP,
               "Stone_DB_Block" if i >= 2 else "Stone_Wall_Light")
    # encontro no plato (desce para dentro do penhasco da ilha, sob o pe da escada)
    mb.box2((-HWB, Y_ABUT, -12.0), (HWB, Y1 + 0.4, Z_TOP), "Stone_DB_Block", 0.0)
    mb.box((2 * HWB + 1.6, 0.9, 0.6), (0.0, Y_ABUT + 0.2, ZS - 0.3), (0, 0, 0), SAND, 0.08)
    # cornija continua nas duas faces, por trecho (cinza escuro -> arenito)
    cuts = [Y0] + [(a + b) / 2 for a, b in SPANS] + [Y1]
    for ya, yb in zip(cuts, cuts[1:]):
        m = SAND if p_db((ya + yb) / 2) > 0.5 else "Stone_Wall_Dark"
        for s in (-1, 1):
            mb.box((0.95, yb - ya, 1.15), (s * (HWB + 0.05), (ya + yb) / 2, Z - 0.725), (0, 0, 0), m, 0.1)
    voussoirs(mb, rng)
    spandrel_ashlar(mb, rng)


def voussoirs(mb, rng):
    """aduelas nas duas faces (extradorso em degraus, chave saliente); o arenito toma conta arco a arco"""
    n = 11
    for si, (a, b) in enumerate(SPANS):
        yc = (a + b) / 2
        for s in (-1, 1):
            for i in range(n):
                t0 = math.pi * (1 - i / n)
                t1 = math.pi * (1 - (i + 1) / n)
                tm = (t0 + t1) / 2
                key = i == n // 2
                rad = 1.9 if key else (1.45 if i % 2 else 1.15)
                dep = 1.25 if key else 0.95
                rm = R_ARCH + rad / 2 - 0.15
                y = yc + rm * math.cos(tm)
                z = ZS + rm * math.sin(tm)
                ln = R_ARCH * abs(t1 - t0) * (1.0 if key else 0.94)
                x = s * (HWB - dep / 2 + (0.32 if key else 0.16))
                if si == 0:
                    m = "Stone_Paving_Warm"
                elif si == 1:
                    m = "Stone_DB_Block" if i % 2 else "Stone_Paving_Warm"
                elif si == 2:
                    m = SAND if key else "Stone_DB_Block"
                else:
                    m = SAND
                mb.box((dep, ln, rad), (x, y, z), (tm - math.pi / 2, 0, 0), m, 0.0)


def spandrel_ashlar(mb, rng):
    """blocos salientes em fiadas nos timpanos; o tom sorteado pela posicao (cinza-bege -> arenito)"""
    z_hi = Z - 1.55

    def intr(pts, y):
        for (ya, za), (yb, zb) in zip(pts, pts[1:]):
            if ya <= y <= yb:
                return za + (zb - za) * (y - ya) / max(yb - ya, 1e-6)
        return 99.0
    for (a, b) in SPANS:
        pts = arch_pts(a, b, 30)
        for s in (-1, 1):
            z = z_hi - 0.55
            while z > ZS + 0.6:
                y = a + rng.uniform(0.0, 1.2)
                while y < b - 0.8:
                    ln = rng.uniform(1.6, 3.2)
                    ok = all(intr(pts, yy) + 1.9 < z - 0.55 for yy in (y, y + ln / 2, y + ln)) and y + ln < b
                    if ok and rng.random() < 0.55:
                        pdb = p_db(y + ln / 2)
                        if rng.random() < pdb:
                            m = SAND if rng.random() < 0.4 else "Stone_DB_Block"
                        else:
                            m = "Stone_Paving_Warm" if rng.random() < 0.35 else "Stone_Wall_Light"
                        mb.box((0.28, ln - 0.15, 1.05), (s * (HWB + 0.02), y + ln / 2, z), (0, 0, 0), m, 0.0)
                    y += ln + rng.uniform(0.2, 1.6)
                z -= 1.25


def ring_poly(cx, cy, rx, ry, n, rng, jit=0.1, rot=0.0):
    return [(cx + rx * (1 + rng.uniform(-jit, jit)) * math.cos(rot + 2 * math.pi * i / n),
             cy + ry * (1 + rng.uniform(-jit, jit)) * math.sin(rot + 2 * math.pi * i / n)) for i in range(n)]


def loft_band(mb, pa, za, pb, zb, m):
    """faixa de rocha: contorno pa em za (topo) ligado ao contorno pb em zb (base), mesmo numero de pontos"""
    bm = mb.bm
    va = [bm.verts.new((p[0], p[1], za)) for p in pa]
    vb = [bm.verts.new((p[0], p[1], zb)) for p in pb]
    n = len(va)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((vb[i], vb[j], va[j], va[i]))
    bm.faces.new(va)
    bm.faces.new(list(reversed(vb)))
    mb._post(va + vb, m, None, 0, 1)


def strata_root(mb, cx, cy, z_top, rx, ry, depth, mats, rng, n=9, bands=4, tip=0.14, lean=(0.0, 0.0), cap=None):
    """raiz de rocha em ESTRATOS: faixas que afinam para baixo, cada uma com uma pequena aba (o estrato pega luz);
    cap = material de um tampo fino iluminado no topo"""
    z = z_top
    k_hi = 1.0
    ox, oy = 0.0, 0.0
    if cap:
        pc = ring_poly(cx, cy, rx * 1.02, ry * 1.02, n, rng, 0.06, rng.uniform(0, 6.28))
        loft_band(mb, pc, z + 0.7, [(cx + (x - cx) * 1.05, cy + (y - cy) * 1.05) for x, y in pc], z, cap)
    for b in range(bands):
        f = (b + 1) / bands
        k_lo = 1.0 - (1.0 - tip) * (f ** 0.85)
        h = depth / bands * rng.uniform(0.85, 1.15)
        nx = ox + lean[0] / bands + rng.uniform(-0.5, 0.5)
        ny = oy + lean[1] / bands + rng.uniform(-0.3, 0.3)
        rot = rng.uniform(0, 6.28)
        top = ring_poly(cx + ox, cy + oy, rx * k_hi * 1.05, ry * k_hi * 1.05, n, rng, 0.08, rot)
        bot = ring_poly(cx + nx, cy + ny, rx * k_lo, ry * k_lo, n, rng, 0.14, rot)
        loft_band(mb, top, z, bot, z - h, mats[b % len(mats)])
        z -= h
        k_hi = k_lo
        ox, oy = nx, ny


def bridge_roots():
    """raizes de rocha em estratos sob os pilares (afinam para dentro das nuvens): bege da Ilha 1 -> arenito DB;
    rochas quentes sob e ao lado dos bastioes"""
    rng = random.Random(3102)
    mb = VMB("DB_Ent_Roots", C, rng, detail="far", vcap=1)
    mb.floor = -999.0
    DBR = ["Cliff_Rock_DB", "Cliff_Rock_DB_Dark"]
    for i, (y0, y1, zb) in enumerate(PIERS):
        yc = (y0 + y1) / 2
        mats = [["Cliff_Rock_Tan", "Cliff_Rock_Tan_Dark"], ["Cliff_Rock_Tan", "Cliff_Rock_DB_Dark"], DBR, DBR][i]
        ry = (y1 - y0) / 2 + 1.5
        if i == 0:
            yc += 0.9
            ry -= 0.9
        strata_root(mb, 0.0, yc, zb + 0.4, HWB + 1.9, ry, 30.0 - 2.0 * i, mats, rng, bands=4, tip=0.12,
                    lean=(rng.uniform(-3.0, 3.0), 0.0))
    # sob o encontro: arenito colado ao penhasco
    strata_root(mb, 0.0, -131.6, -11.4, HWB + 1.4, 3.4, 22.0, DBR, rng, bands=3, tip=0.3)
    # bastioes: raiz sob cada um + ombro de rocha para fora (sobre a borda do plato)
    x0, x1, by0, by1 = BAST
    for s in (-1, 1):
        cx = s * (x0 + x1) / 2
        cy = (by0 + by1) / 2
        strata_root(mb, cx + s * 0.4, cy - 0.3, 1.5, (x1 - x0) / 2 + 1.1, (by1 - by0) / 2 + 1.0, 17.0, DBR, rng,
                    bands=3, tip=0.2, lean=(s * 2.0, 1.0))
        # contraforte de arenito ao lado do bastiao: topo na cota do plato (a borda do penhasco vira rocha em
        # estratos), desce afinando pela face do penhasco
        strata_root(mb, s * (x1 + 3.8), cy + 1.2, G - 1.3, 4.6, 4.2, 22.0, DBR, rng, n=9, bands=3, tip=0.3,
                    lean=(s * 1.0, 2.0), cap="Cliff_Rock_DB_Top")
    mb.finish()


def bridge_deck():
    """calcamento do tabuleiro: fiadas transversais; Konoha -> DB com faixa central de arenito no fim"""
    rng = random.Random(3103)
    mb = MB("DB_Ent_Deck", C, rng, detail="near")
    x_in = HWD - 0.05
    mb.box((2 * x_in, Y1 - Y0, 0.3), (0.0, (Y0 + Y1) / 2, Z - 0.2), (0, 0, 0), "Stone_Paving_Warm_C", 0.0)
    y = Y0 + 0.05
    row = 0
    while y < Y1 - 0.4:
        t = tpos(y)
        db_pat = t > 0.46
        dep = rng.choice((1.7, 1.9, 2.1)) if not db_pat else rng.choice((2.3, 2.5))
        dep = min(dep, Y1 - y)
        if not db_pat:
            cuts = [-x_in] + ([-4.4, 0.0, 4.4] if row % 2 == 0 else [-2.2, 2.2]) + [x_in]
            cuts = [cuts[0]] + [c + rng.uniform(-0.45, 0.45) for c in cuts[1:-1]] + [cuts[-1]]
        else:
            cuts = [-x_in, -6.0 + rng.uniform(-0.3, 0.3), -3.0, 0.0, 3.0, 6.0 + rng.uniform(-0.3, 0.3), x_in]
            if row % 2:
                cuts = [-x_in, -6.0 + rng.uniform(-0.3, 0.3), -3.0, 3.0, 6.0 + rng.uniform(-0.3, 0.3), x_in]
        prun = smooth(0.46, 0.66, t)
        for xa, xb in zip(cuts, cuts[1:]):
            if xb - xa < 1.0:
                continue
            xm = (xa + xb) / 2
            if db_pat and abs(xm) < 3.0:
                m = SAND if rng.random() < prun * 0.8 else "Stone_Paving_DB_B"
            else:
                m = "Stone_Paving_DB" if rng.random() < p_db(y) else "Stone_Paving_Warm"
            hh = 0.4 + rng.uniform(-0.035, 0.035)
            mb.box((xb - xa - 0.2, dep - 0.2, hh), (xm, y + dep / 2, Z - 0.3 + hh / 2),
                   (0, 0, rng.uniform(-0.006, 0.006)), m, 0.0)
        y += dep
        row += 1
    mb.finish()


def bridge_rails(mb, rng):
    """guarda-corpo nas linhas das guardas do db_col: meio-fio + cerca + postes com lanterna a cada ~13"""
    stations = STATIONS
    bays = list(zip([Y0] + stations, stations + [Y1]))
    for s in (-1, 1):
        x = s * RAIL_X
        for ya, yb in bays:
            if yb - ya < 0.2:
                continue
            ym = (ya + yb) / 2
            db = p_db(ym) > 0.5
            mb.box((1.2, yb - ya, 0.8), (x, ym, Z_TOP + 0.4), (0, 0, 0), "Stone_DB_Block" if db else "Stone_Wall_Light",
                   0.1)
            mb.box((1.3, yb - ya, 0.18), (x, ym, Z_TOP + 0.89), (0, 0, 0), SAND if db else "Stone_Wall_Dark", 0.0)
        # cerca entre os postes
        for ya, yb in bays:
            a_, b_ = ya + 0.85, yb - 0.85
            if b_ - a_ < 2.0:
                continue
            db = p_db((ya + yb) / 2) > 0.5
            n = max(1, int(round((b_ - a_) / 3.2)))
            for k in range(1, n):
                yy = a_ + (b_ - a_) * k / n
                mb.box((0.62, 0.62, 2.5), (x, yy, Z + 0.55 + 1.25), (0, 0, 0), "Wood_Dark", 0.0)
            for zz, th in ((Z + 1.6, 0.34), (Z + 2.95, 0.42)):
                mb.box((0.38, b_ - a_ + 0.3, th), (x, (a_ + b_) / 2, zz), (0, 0, 0), RAILW if db else "Wood_Plank",
                       0.0)
        # estacoes: Konoha (2) -> hibrida (1) -> Capsule (2)
        for i, yy in enumerate(stations):
            xs = s * (RAIL_X + 0.05)
            if i <= 1:
                konoha_lantern(mb, xs, yy, Z_TOP, ph=3.9)
            elif i == 2:
                konoha_lantern(mb, xs, yy, Z_TOP, ped="Stone_DB_Block", cap=SAND, ph=3.9)
            else:
                sc = 1.15 if i == len(stations) - 1 else 1.0
                mb.box((1.45 * sc, 1.45 * sc, 3.6), (xs, yy, Z_TOP + 1.8), (0, 0, 0), "Stone_DB_Block", 0.12)
                mb.box((1.8 * sc, 1.8 * sc, 0.34), (xs, yy, Z_TOP + 3.6 + 0.17), (0, 0, 0), SAND, 0.06)
                db_lamp(mb, xs, yy, Z_TOP + 3.94, sc)


# ------------------------------------------------------------------ 2. escadaria + muros do recorte + bastioes
def stair_and_walls(mb, rng):
    for nm, base, ang, w, n, rise, tread, g in db_col.stair_list():
        if nm != "Entry":
            continue
        DL.vis_stairs(mb, base, ang, w, n, rise, tread, "Stone_Paving_DB", "Stone_DB_Block")
        # faixa central de arenito continua subindo (a mesma da ponte)
        for i in range(n):
            yy = base[1] + tread * i + tread / 2
            zt = base[2] + rise * (i + 1)
            mb.box((6.0, tread - 0.3, 0.14), (0.0, yy - 0.05, zt - 0.04), (0, 0, 0), SAND, 0.0)
    x0, x1, by0, by1 = BAST
    wy0, wy1 = by1 - 0.2, L.ENTRY_STAIR_Y1 - 0.3          # muro: do bastiao ate o topo da escada
    for s in (-1, 1):
        xc = s * (NOTCH_X + 0.8)
        # muro de arrimo em blocos (face interna em x = +-11,3), do plato (GROUND) ate abaixo do tabuleiro
        FP.masonry_wall(mb, (xc, wy0), (xc, wy1), Z - 2.4, G - 0.4, 1.6, rng, m="Stone_DB_Block", m2=SAND,
                        course=1.6, mix=0.1, blk=(2.4, 4.0), core=True, quoins=(False, True), core_m="Stone_DB_Block",
                        bevel=0.0)
        # capa + mureta do lado do plato + pedestais com lampiao
        mb.box((2.6, wy1 - wy0 + 0.4, 0.5), (s * (NOTCH_X + 1.2), (wy0 + wy1) / 2, G - 0.15), (0, 0, 0),
               "Stone_Paving_DB", 0.1)
        mb.box((1.0, wy1 - wy0, 1.3), (s * (NOTCH_X + 0.6), (wy0 + wy1) / 2, G + 0.1 + 0.65), (0, 0, 0),
               "Stone_DB_Block", 0.0)
        mb.box((1.3, wy1 - wy0 + 0.2, 0.3), (s * (NOTCH_X + 0.6), (wy0 + wy1) / 2, G + 1.4 + 0.15), (0, 0, 0), SAND,
               0.0)
        for py in (-123.0, L.ENTRY_STAIR_Y1 - 1.3):
            px = s * (NOTCH_X + 0.9)
            mb.box((2.2, 2.2, 2.4), (px, py, G + 0.1 + 1.2), (0, 0, 0), "Stone_DB_Block", 0.1)
            mb.box((2.6, 2.6, 0.36), (px, py, G + 2.5 + 0.18), (0, 0, 0), SAND, 0.06)
            db_lamp(mb, px, py, G + 2.86, 1.0)
        # bastiao na boca do recorte (sobe do penhasco, emoldura o pe da escada)
        bx0, bx1 = s * x0, s * x1
        xa, xb = min(bx0, bx1), max(bx0, bx1)
        zb, zt = 1.0, G - 0.6
        mb.box2((xa + 0.3, by0 + 0.4, zb), (xb - 0.3, by1, zt), "Stone_DB_Block", 0.0)          # nucleo
        # faces em blocos: frente (sul, para a ponte) e face interna (para a escada)
        FP.masonry_wall(mb, (xa, by0 + 0.5), (xb, by0 + 0.5), zb, zt, 1.0, rng, m="Stone_DB_Block", m2=SAND,
                        course=1.6, mix=0.08, blk=(1.8, 3.2), core=False, quoins=(True, True), bevel=0.0)
        xi = s * (x0 + 0.5)
        FP.masonry_wall(mb, (xi, by0 + 0.5), (xi, by1), zb, zt, 1.0, rng, m="Stone_DB_Block", m2=SAND,
                        course=1.6, mix=0.08, blk=(1.8, 3.2), core=False, quoins=(True, False), bevel=0.0)
        # cintas de arenito (na cota do tabuleiro e do plato) + coroamento + lampiao grande
        bi, bo = s * (x0 - 0.1), s * (x1 + 0.45)
        for zz, th in ((Z - 0.6, 0.9), (zt, 0.7)):
            mb.box2((min(bi, bo), by0 - 0.5, zz), (max(bi, bo), by1, zz + th), SAND, 0.1)
        zc = zt + 0.7
        mb.box((xb - xa - 0.6, by1 - by0 - 0.6, 2.0), ((xa + xb) / 2, (by0 + by1) / 2, zc + 1.0), (0, 0, 0),
               "Stone_DB_Block", 0.12)
        mb.box((xb - xa - 0.1, by1 - by0 - 0.1, 0.45), ((xa + xb) / 2, (by0 + by1) / 2, zc + 2.0 + 0.22), (0, 0, 0),
               "Stone_Paving_DB", 0.1)
        db_lamp(mb, (xa + xb) / 2, (by0 + by1) / 2, zc + 2.45, 1.45)
        # colisao: bastiao acima do plato + mureta do muro (o jogador do plato nao cai no recorte)
        col_box2("DB_EntWall", (xa, by0, G - 1.0), (xb, by1, zc + 2.4))
        col_box2("DB_EntWall", (min(s * NOTCH_X, s * (NOTCH_X + 1.9)), wy0 - 0.1, G - 0.5),
                 (max(s * NOTCH_X, s * (NOTCH_X + 1.9)), wy1, G + 3.4))


# ------------------------------------------------------------------ 3. portal Capsule
def stadium(hl, r, n=10):
    pts = []
    for i in range(n + 1):
        a = -math.pi / 2 + math.pi * i / n
        pts.append((hl + r * math.cos(a), r * math.sin(a)))
    for i in range(n + 1):
        a = math.pi / 2 + math.pi * i / n
        pts.append((-hl + r * math.cos(a), r * math.sin(a)))
    return pts


def gate():
    rng = random.Random(3301)
    mb = MB("DB_Ent_Gate", C, rng, detail="hero")
    gy = GATE_Y
    px = GATE_PX
    H = L.GATE_OPEN_H
    ux, uz = Vector((1, 0, 0)), Vector((0, 0, 1))
    for s in (-1, 1):
        c = (s * px, gy, G)
        # plinto branco arredondado, fuste azul-marinho (entase leve), aneis brancos, capitel branco "almofada"
        lathe(mb, c, [(0.4, -0.3), (2.9, -0.3), (2.9, 0.8), (2.72, 1.18), (2.42, 1.42), (0.4, 1.42)],
              "Plaster_DB_White", n=28)
        lathe(mb, c, [(0.4, 1.4), (2.3, 1.4), (2.38, 7.0), (2.3, 13.3), (0.4, 13.3)], "Plaster_DB_Navy", n=28)
        for zr in (3.0, 11.6):
            lathe(mb, c, [(2.2, zr), (2.52, zr), (2.52, zr + 0.5), (2.2, zr + 0.5)], "Plaster_DB_White", n=28)
        lathe(mb, c, [(2.25, 6.9), (2.46, 6.9), (2.46, 7.5), (2.25, 7.5)], "Roof_DB_Blue", n=28)
        lathe(mb, c, [(0.4, 13.2), (2.45, 13.2), (2.8, 13.55), (2.9, 14.2), (2.7, 15.1), (2.35, 15.6), (0.4, 15.6)],
              "Plaster_DB_White", n=28)
        # bloco de apoio do lintel sobre o capitel (ligacao limpa pilar -> viga)
        mb.box((4.4, 3.4, 1.3), (s * px, gy, G + H - 0.2), (0, 0, 0), "Plaster_DB_White", 0.2)
        # quarto-de-circulo branco nos cantos internos do vao (vao arredondado, livre de 18 x 16 no eixo)
        ri = 1.6
        xi = s * (px - 2.2)
        cc = (xi - s * ri, G + H - ri)
        pts = [(xi, G + H + 0.08), (xi, G + H - ri)]
        for k in range(1, 8):
            a = (0.0 if s > 0 else math.pi) + s * (math.pi / 2) * k / 8
            pts.append((cc[0] + ri * math.cos(a), cc[1] + ri * math.sin(a)))
        pts.append((xi - s * ri, G + H + 0.08))
        if s < 0:
            pts = list(reversed(pts))
        PK.plate(mb, pts, (0.0, gy, 0.0), ux, uz, 2.6, "Plaster_DB_White", 0.0)
        col_box("DB_EntGate", (5.8, 5.8, H + 0.4), (s * px, gy, G + (H + 0.4) / 2 - 0.2))
    # lintel: capsula branca deitada (pontas redondas sobre os pilares) com contorno azul-marinho recuado
    r = 2.4
    zc = G + H + 0.45 + r              # contorno azul-marinho (r + 0,42) fica 0,03 acima do vao de 16
    PK.plate(mb, stadium(px, r + 0.42, 12), (0.0, gy, zc), ux, uz, 3.0, "Plaster_DB_Navy", 0.12)
    PK.plate(mb, stadium(px, r, 12), (0.0, gy, zc), ux, uz, 3.9, "Plaster_DB_White", 0.3)
    # faixa azul Capsule nas duas faces do lintel
    for sy in (-1, 1):
        mb.box((2 * px - 1.0, 0.22, 0.8), (0.0, gy + sy * 2.0, zc - 0.1), (0, 0, 0), "Roof_DB_Blue", 0.0)
        mb.box((2 * px - 1.0, 0.16, 0.22), (0.0, gy + sy * 2.0, zc + 0.62), (0, 0, 0), "Plaster_DB_Navy", 0.0)
    # espiga azul-marinho no topo (friso escuro) com pontas arredondadas
    mb.box((2 * px - 4.0, 2.2, 0.55), (0.0, gy, zc + r + 0.2), (0, 0, 0), "Plaster_DB_Navy", 0.2)
    # medalhao: base branca, disco azul, aro branco, "C" branco (lido certo dos dois lados), anel ciano de energia
    zm = zc + r + 5.6
    cm = Vector((0.0, gy, zm))
    mb.box((3.6, 2.6, 1.3), (0.0, gy, zc + r + 0.3 + 0.65), (0, 0, 0), "Plaster_DB_White", 0.3)
    mb.cyl(1.0, 1.8, (0.0, gy, zc + r + 1.4 + 0.9), (0, 0, 0), "Plaster_DB_Navy", 16, bevel=0.1)
    R = 3.4
    mb.cyl(R, 1.3, cm, (math.pi / 2, 0, 0), "Roof_DB_Blue", 32, bevel=0.12)
    PK.ring(mb, cm, R + 0.25, ux, uz, 0.55, 1.7, "Plaster_DB_White", n=40)
    for sy, u in ((-1, ux), (1, -ux)):
        # face -Y (quem chega pela ponte): C abre para +X; face +Y (quem esta na praca): C abre para -X
        cf = cm + Vector((0.0, sy * 0.72, 0.0))
        PK.ring(mb, cf, 2.05, u, uz, 0.78, 0.3, "Plaster_DB_White", a0=48.0, a1=312.0, n=22)
        PK.ring(mb, cf, 0.95, u, uz, 0.52, 0.3, "Plaster_DB_White", a0=62.0, a1=298.0, n=14)
    PK.ring(mb, cm, R + 0.95, ux, uz, 0.32, 0.7, "DB_Cyan_Glow", n=40)
    mb.finish()
    light("L_DBEnt_Emblem", "POINT", (0.0, gy - 3.2, zm), 180, (0.55, 0.85, 1.0), 1.0)


# ------------------------------------------------------------------ 4. praca de entrada
def prom_cross(x, a_lo, a_hi, inset=0.0):
    """y do contorno externo do promenade (+ inset para fora) na vertical x (bisseccao em angulo)"""
    def f(a):
        return (L.prom_r(a) + inset) * math.cos(math.radians(a)) - x
    lo, hi = a_lo, a_hi
    for _ in range(50):
        mid = (lo + hi) / 2
        if (f(lo) < 0) == (f(mid) < 0):
            lo = mid
        else:
            hi = mid
    a = (lo + hi) / 2
    return (L.prom_r(a) + inset) * math.sin(math.radians(a))


def north_y(x, inset=0.0):
    return prom_cross(x, 200.0, 340.0, inset) if abs(x) > 1e-6 else -(L.prom_r(270.0) + inset)


def plaza_poly(inset=0.0, x_in=0.0, y_in=0.0):
    x0, y0, x1, y1 = L.ENTRY_PLAZA
    x0, x1, y0 = x0 + x_in, x1 - x_in, y0 + y_in
    pts = [(x0, y0), (x1, y0)]
    n = 16
    for i in range(n + 1):
        x = x1 - (x1 - x0) * i / n
        pts.append((x, north_y(x, inset)))
    return pts


# floreiras / bancos / postes da praca (fora do eixo): (x, y, raio)
PALM_PLANTERS = [(-19.2, -96.6), (19.2, -96.6)]
FLOWER_PLANTERS = [(-18.2, -82.0), (18.2, -82.0), (-14.2, -76.6), (14.2, -76.6)]
BENCHES = [(-19.3, -89.0), (19.3, -89.0)]
PLAZA_LAMPS = [(-8.8, -76.4), (8.8, -76.4)]
MED_R = 8.2


def plaza():
    rng = random.Random(3401)
    mb = MB("DB_Ent_Plaza", C, rng, detail="near")
    plaza_props(mb, random.Random(3402))
    x0, y0, x1, y1 = L.ENTRY_PLAZA
    # leito (aparece nas juntas) e faixa de borda de arenito em volta
    poly = DL.ccw(plaza_poly())
    mb.prism(poly, G - 0.3, G + 0.05, "Stone_DB_Block")
    inner = DL.ccw(plaza_poly(1.3, 1.3, 1.3))
    # borda: sul (topo da escada), laterais, norte (encontro com o promenade)
    mb.box((x1 - x0, 1.2, 0.36), (0.0, y0 + 0.6, G - 0.24 + 0.18), (0, 0, 0), SAND, 0.0)
    for s in (-1, 1):
        ya, yb = y0 + 1.2, north_y(s * (x1 - 0.6))
        mb.box((1.2, yb - ya, 0.36), (s * (x1 - 0.6), (ya + yb) / 2, G - 0.24 + 0.18), (0, 0, 0), SAND, 0.0)
    npts = [(x, north_y(x)) for x in [x1 - (x1 - x0) * i / 16 for i in range(17)]]
    for (xa, ya), (xb, yb) in zip(npts, npts[1:]):
        d = Vector((xb - xa, yb - ya, 0))
        nrm = Vector((-d.y, d.x, 0)).normalized()          # para o sul (para dentro da praca)
        c = Vector(((xa + xb) / 2, (ya + yb) / 2, 0)) + nrm * 0.6
        mb.box((d.length + 0.05, 1.2, 0.36), (c.x, c.y, G - 0.24 + 0.18), (0, 0, math.atan2(d.y, d.x)), SAND, 0.0)

    circles = [(SPAWN[0], SPAWN[1], MED_R + 0.3)] + [(s * GATE_PX, GATE_Y, 3.2) for s in (-1, 1)]
    circles += [(x, y, 3.0) for x, y in PALM_PLANTERS] + [(x, y, 2.5) for x, y in FLOWER_PLANTERS]
    circles += [(x, y, 0.9) for x, y in PLAZA_LAMPS]
    rects = [(-L.GATE_OPEN_W / 2 - 0.2, GATE_Y - 1.8, L.GATE_OPEN_W / 2 + 0.2, GATE_Y + 1.8)]
    rects += [(x - 1.1, y - 2.6, x + 1.1, y + 2.6) for x, y in BENCHES]

    def free(xa, ya, xb, yb):
        for cx, cy, r in circles:
            if rect_circle(xa, ya, xb, yb, cx, cy, r):
                return False
        for rx0, ry0, rx1, ry1 in rects:
            if xa < rx1 and xb > rx0 and ya < ry1 and yb > ry0:
                return False
        return all(L.point_in_poly(px, py, inner) for px, py in ((xa, ya), (xb, ya), (xa, yb), (xb, yb)))

    def put(xa, ya, xb, yb, m, depth=0):
        """laje; se esbarra num obstaculo ou na borda, divide em 4 (ate 2 niveis) em vez de deixar buraco"""
        if xb - xa < 0.8 or yb - ya < 0.8:
            return
        if free(xa, ya, xb, yb):
            hh = 0.36 + rng.uniform(-0.03, 0.03)
            mb.box((xb - xa - 0.24, yb - ya - 0.24, hh), ((xa + xb) / 2, (ya + yb) / 2, G - 0.26 + hh / 2),
                   (0, 0, rng.uniform(-0.004, 0.004)), m, 0.0)
        elif depth < 2:
            xm, ym = (xa + xb) / 2, (ya + yb) / 2
            for qa, qb, qc, qd in ((xa, ya, xm, ym), (xm, ya, xb, ym), (xa, ym, xm, yb), (xm, ym, xb, yb)):
                put(qa, qb, qc, qd, m, depth + 1)

    def field(xa0, xa1, tile_x, tile_y, m, bond=True):
        y = y0 + 1.3
        row = 0
        while y < y1 + 6.0:
            yb = y + tile_y
            x = xa0 - (tile_x / 2 if (bond and row % 2) else 0.0)
            while x < xa1 - 0.3:
                xa, xb = max(x, xa0), min(x + tile_x, xa1)
                put(xa, y, xb, yb, m)
                x += tile_x
            y = yb
            row += 1
    # eixo: lajes grandes (runner) entre frisos de arenito; laterais: lajes em amarracao
    field(-5.5, 5.5, 2.75, 3.0, "Stone_Paving_DB", bond=True)
    for s in (-1, 1):
        ya, yb = y0 + 1.3, north_y(s * 5.9, 1.3)
        segs = [(ya, GATE_Y - 1.8), (GATE_Y + 1.8, SPAWN[1] - math.sqrt(max(0.0, (MED_R + 0.3) ** 2 - 5.9 ** 2))),
                (SPAWN[1] + math.sqrt(max(0.0, (MED_R + 0.3) ** 2 - 5.9 ** 2)), yb)]
        for sa, sb in segs:
            if sb - sa > 0.5:
                mb.box((0.8, sb - sa, 0.36), (s * 5.9, (sa + sb) / 2, G - 0.26 + 0.18), (0, 0, 0), "Stone_DB_Block",
                       0.0)
        xa0, xa1 = (6.3, x1 - 1.3) if s > 0 else (x0 + 1.3, -6.3)
        field(xa0, xa1, 3.6, 3.2, "Stone_Paving_DB", bond=True)
    # soleira do portal: faixa de arenito com friso azul (a linha do "mundo Capsule")
    mb.box((L.GATE_OPEN_W + 0.4, 3.4, 0.36), (0.0, GATE_Y, G - 0.26 + 0.18), (0, 0, 0), SAND, 0.0)
    mb.box((L.GATE_OPEN_W + 0.4, 0.6, 0.38), (0.0, GATE_Y, G - 0.26 + 0.19), (0, 0, 0), "Roof_DB_Blue", 0.0)
    # medalhao do ponto de chegada (WORLD_ENTRY): disco + aneis radiais + anel azul + anel de arenito
    sx, sy = SPAWN
    mb.cyl(1.7, 0.36, (sx, sy, G - 0.26 + 0.18), (0, 0, 0), SAND, 16, bevel=0.0)
    FP.pave_ring(mb, sx, sy, 1.9, 6.3, G - 0.26, rng, ring_w=2.2, gap=0.22, h=0.36, m="Stone_Paving_DB")
    FP.pave_ring(mb, sx, sy, 6.4, 7.1, G - 0.26, rng, ring_w=0.7, gap=0.06, h=0.37, m="Roof_DB_Blue")
    FP.pave_ring(mb, sx, sy, 7.2, MED_R, G - 0.26, rng, ring_w=1.0, gap=0.2, h=0.36, m=SAND)
    mb.finish()


def plaza_props(mb, rng):
    """floreiras Capsule (brancas, faixa azul), palmeiras junto ao portal, bancos e postes na borda da praca"""
    for x, y in PALM_PLANTERS:
        mb.cyl(2.7, 0.5, (x, y, G + 0.25), (0, 0, 0), SAND, 20, bevel=0.0)
        lathe(mb, (x, y, G + 0.5), [(1.9, 0.0), (2.45, 0.0), (2.55, 0.9), (2.45, 1.25), (1.9, 1.25)],
              "Plaster_DB_White", n=24)
        lathe(mb, (x, y, G + 0.5), [(2.5, 0.35), (2.62, 0.35), (2.62, 0.75), (2.5, 0.75)], "Roof_DB_Blue", n=24)
        mb.cyl(2.0, 0.3, (x, y, G + 0.5 + 1.0), (0, 0, 0), "Grass_DB", 20, bevel=0.0)
        # palmeira do kit da ilha (tronco curvo afunilado de 5 lados, pe alargado, coroa de 2 andares), a mesma
        # familia das palmeiras do resto da ilha; inclina para fora do eixo (emoldura o portal, copa longe do pilar)
        lean_dir = math.atan2(0.3, 1.0) if x > 0 else math.pi - math.atan2(0.3, 1.0)
        VG.palm(mb, x, y, G + 1.1, rng.uniform(11.5, 13.0), rng, lean=0.16, lean_dir=lean_dir)
        for k in range(3):
            a = rng.uniform(0, 6.28)
            mb.ico(0.75, (x + 1.25 * math.cos(a), y + 1.25 * math.sin(a), G + 1.75), "Leaf_Palm", 1, (1, 1, 0.75),
                   jitter=0.2)
        col_box("DB_EntPlanter", (4.8, 4.8, 1.8), (x, y, G + 0.9))
        # tronco: a caixa acompanha a inclinacao (o tronco curvo sai ~0,5 para fora na altura da cabeca)
        col_box("DB_EntPlanter", (1.5, 1.5, 9.0), (x + 0.35 * math.cos(lean_dir), y + 0.35 * math.sin(lean_dir),
                                                   G + 5.5))
    for x, y in FLOWER_PLANTERS:
        lathe(mb, (x, y, G - 0.05), [(1.4, 0.0), (2.0, 0.0), (2.1, 0.8), (1.98, 1.1), (1.4, 1.1)], "Plaster_DB_White",
              n=20)
        lathe(mb, (x, y, G - 0.05), [(2.05, 0.3), (2.16, 0.3), (2.16, 0.62), (2.05, 0.62)], "Roof_DB_Blue", n=20)
        mb.cyl(1.55, 0.3, (x, y, G + 0.85), (0, 0, 0), "Grass_DB", 16, bevel=0.0)
        for k in range(4):
            a = rng.uniform(0, 6.28) + k * 1.57
            mb.ico(rng.uniform(0.55, 0.8), (x + 0.8 * math.cos(a), y + 0.8 * math.sin(a), G + 1.35), "Leaf_Palm", 1,
                   (1, 1, 0.8), jitter=0.22)
        col_box("DB_EntPlanter", (4.0, 4.0, 1.3), (x, y, G + 0.6))
    for x, y in BENCHES:
        s = -1 if x > 0 else 1                     # encosto do lado de fora, assento para o eixo
        for dy in (-1.8, 1.8):
            mb.box((1.2, 0.6, 1.0), (x, y + dy, G + 0.5), (0, 0, 0), "Plaster_DB_White", 0.0)
        mb.box((1.5, 4.8, 0.3), (x, y, G + 1.12), (0, 0, 0), "Plaster_DB_White", 0.08)
        mb.box((0.3, 4.8, 1.1), (x - s * 0.8, y, G + 1.9), (0, 0, 0), "Plaster_DB_Navy", 0.0)
        mb.box((0.4, 5.0, 0.3), (x - s * 0.8, y, G + 2.5), (0, 0, 0), "Roof_DB_Blue", 0.0)
        col_box("DB_EntBench", (1.8, 5.0, 1.3), (x, y, G + 0.65))
    for x, y in PLAZA_LAMPS:
        mb.cyl(0.75, 0.45, (x, y, G + 0.22), (0, 0, 0), "Plaster_DB_Navy", 12, bevel=0.0)
        mb.cyl(0.3, 3.4, (x, y, G + 0.45 + 1.7), (0, 0, 0), "Plaster_DB_White", 10, bevel=0.0)
        db_lamp(mb, x, y, G + 3.85, 0.95)
        col_box("DB_EntLamp", (0.9, 0.9, 5.5), (x, y, G + 2.75))


# ------------------------------------------------------------------ QA extra (db_qa roda)
EXTRA_ROUTES = {
    # a praca e circulavel pelas laterais (entre floreiras, bancos e palmeiras)
    "praca_lateral_O": ([(0.0, -109.5), (-16.0, -109.5), (-16.0, -100.4), (-14.2, -99.6), (-12.0, -92.0),
                         (-11.0, -82.0), (-5.0, -76.0)], G),
    "praca_lateral_L": ([(0.0, -109.5), (16.0, -109.5), (16.0, -100.4), (14.2, -99.6), (12.0, -92.0),
                         (11.0, -82.0), (5.0, -76.0)], G),
    # o plato ao lado do recorte da escada continua acessivel (mureta e pedestais nao fecham)
    "plato_lado_L": ([(0.0, -109.5), (17.0, -110.0), (18.0, -126.0)], G),
    "plato_lado_O": ([(0.0, -109.5), (-17.0, -110.0), (-18.0, -126.0)], G),
}
# o jogador do plato nao cai no recorte da escada (a mureta segura)
EXTRA_PROBES = [("ENT_mureta_recorte_O", -15.0, -122.0, G, 1.0, 0.0), ("ENT_mureta_recorte_L", 15.0, -122.0, G, -1.0, 0.0)]


def build():
    # ponte + guarda-corpo + escadaria + muros + bastioes: UM objeto (dividem pedra, arenito e os lampioes)
    mb = VMB("DB_Ent_Bridge", C, random.Random(3100), detail="near", vcap=1)
    bridge_body(mb, random.Random(3101))
    bridge_rails(mb, random.Random(3104))
    stair_and_walls(mb, random.Random(3201))
    mb.finish()
    light("L_DBEnt_BridgeLamps", "POINT", (0.0, -150.0, Z + 6.0), 260, (1.0, 0.64, 0.3), 1.5)
    light("L_DBEnt_StairLamps", "POINT", (0.0, -121.0, G + 4.0), 240, (1.0, 0.64, 0.3), 1.5)
    bridge_roots()
    bridge_deck()
    gate()
    plaza()
