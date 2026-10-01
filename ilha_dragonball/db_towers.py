# db_towers - ZONA TOWERS da Ilha 2 (Dragon Ball): a silhueta tech da ilha (prefixo DB_Twr_, colecao 05_TECH_VILLAGE).
# Planta: db_layout (TOWER_SITES, SAT_BRIDGES, GROUND_LOTS "landing_pad", CAPSULE_ANNEX). Tres torres DIFERENTES:
#   comm    (-104,150) HUB: mastro de comunicacao (topo ~67 = ~95 abs., passa da cupula): pe alargado, casulo de
#           acoplamento da passarela (z CAP+10), pratos parabolicos, 3 discos azuis empilhados e espacados,
#           plataforma de servico, RADAR GIRANDO (VFX_DBTWR_Radar) e 2 antenas com farol vermelho no topo.
#   lookout (100,140)  HUB: mirante com topo "disco voador" (~61; disco em ~CAP+55, acima da cupula): tambor de base com
#           escotilhas, fuste com colar de acoplamento, fuste alongado com colar, disco menor, disco envidracado
#           (faixa de vidro com montantes brancos + fundo opaco) e cupula azul.
#   energy  (74,118)   HUB: estacao de energia (~30): base octogonal, tambor com frisos ciano, 3 bobinas Tesla de cobre,
#           coluna escura, taca branca, ORBE ciano que flutua (VFX_DBTWR_EnergyOrb, bob) dentro de ANEL que gira
#           (VFX_DBTWR_EnergyRing, rpm) e gaiola de 3 arcos brancos.
#   2 passarelas de vidro (Glass_DB_Blue, costelas brancas, faixa de piso azul-marinho opaca, quilha e espinha brancas)
#           da porta redonda de cada anexo do Capsule (SKYWALK_PORT_Cap*) ate o casulo/colar da torre (anel de
#           acoplamento no lado da torre), em pilares finos. So visual; colisao so nos pilares.
#   satelites pad_sw / pad_se: plataforma redonda andavel (calcamento em aneis, medalhao, coroamento branco/azul) sobre
#           pilar de rocha pendurado em estratos (mesma costela do terreno), ponte curta com vigas brancas e escoras
#           ASSENTADAS na rocha (>= 2,0 do eixo dentro dela, sapata azul-marinho), guarda-corpo Capsule nas linhas das
#           guardas do db_col, pilones com lampiao nas cabeceiras, TORRE-DISCO esbelta na borda de fora (topo ~G+45,
#           o lobulo com torre da vista superior da concept), banco e luneta. Cabeceira do
#           lado da ilha: soleira branca (topo G+0,28, colisao propria) sobre a ponta do caminho do terreno que avanca
#           na ponte, e encontros brancos (topo G+0,1) que tapam o corte da crista ao lado da ponte.
#   heliponto Capsule (landing_pad, GROUND): laje azul-ardosia com borda branca, marcacoes (aneis + chevrons, sem texto),
#           luzes de pouso, 2 postes de holofote e uma aeronave-capsula estacionada (casco arredondado, canopi de vidro,
#           asas curtas com motores, deriva azul + estabilizadores, trem de pouso). Colisao justa ao casco e asas.
# Colisao: so dos volumes proprios (DB_Twr*). Piso, pontes e guardas dos satelites sao do db_col (congelado).
# Dependencias de modulos de OUTRAS zonas (so leitura; se a assinatura mudar, as torres quebram):
#   db_capsule_kit (K): CMB, lathe, ring, torus, porthole, sphere, cyl_axis, extrude_uz, rot_to, _smooth;
#   db_terrain_rock (TR): hang, STRATA, ROCK (o pilar pendurado dos satelites = a costela do terreno).
#   O db_col._runs (privado) foi COPIADO aqui (_runs) para nao depender dele.
import math, random
import bmesh
from mathutils import Vector, Matrix, Euler
from mathutils.bvhtree import BVHTree
import bpy
import fm_lib
import fm_parts as FP
import db_lib as DL
from db_lib import col_box, light, octo_col, Frame
import db_layout as L
import db_capsule_kit as K
import db_terrain_rock as TR

S_ = fm_lib.S
# ------------------------------------------------------------------ materiais novos (2 de 5)
NEW_MATS = {
    "Stone_DBTwrPad": (S_(92, 104, 128), 0.8, 0.0, 0, None, 0.06),      # laje do heliponto (azul-ardosia)
    "Metal_DBTwrCoil": (S_(206, 118, 60), 0.35, 0.85, 0, None, 0.04),   # espiras de cobre das bobinas Tesla
}
for _k, _v in NEW_MATS.items():
    fm_lib.MATS.setdefault(_k, _v)

COLL = "05_TECH_VILLAGE"
VFXC = "12_VFX_HELPERS"
G, HB, CAP = L.GROUND, L.HUB, L.CAP
D2R = math.pi / 180.0
WHITE, NAVY, BLUE, GLASS = "Plaster_DB_White", "Plaster_DB_Navy", "Roof_DB_Blue", "Glass_DB_Blue"
STEEL, DARK, CYAN, RED, LAMP = "Metal_DB_Steel", "Metal_DB_Dark", "DB_Cyan_Glow", "P_Red_Glow", "Lantern_Glow"
PAVE = "Stone_Paving_DB"
PAD, COIL = "Stone_DBTwrPad", "Metal_DBTwrCoil"
ROCK = TR.ROCK

SITES = {k: (x, y, r) for x, y, r, k, w in L.TOWER_SITES}
TUBE_R = 2.4                    # raio do tubo de vidro (<= 2,6; o colar r 3,7 e do Capsule)
TUBE_Z = CAP + 10.0             # eixo das portas redondas dos anexos (44,2)
DOCK_R = {"comm": 4.6, "lookout": 3.7}     # raio do casulo/colar da torre na cota do tubo
LK_RISE = 20.0                  # fuste acrescentado no mirante (acima do colar da passarela): disco em ~CAP+55
CM_RISE = (4.0, 8.0, 12.0, 14.0)   # alongamento do mastro: 1o, 2o, 3o disco e plataforma de servico (topo ~95)
PILLAR_T = {"comm": (0.46, 0.76), "lookout": (0.52, 0.8)}   # posicao dos pilares ao longo do tubo (porta -> torre)
HEAD_PLATE = (-0.6, 5.6)        # soleira da cabeceira (ao longo da ponte a partir de a0): cobre o caminho do terreno
HEAD_TOP = 0.28                 # topo da soleira acima de G (meio-fio do caminho em G+0,23; colisao propria nessa cota)
WING_IN, WING_OUT = 3.2, 7.2    # lateral de dentro (minima) e de fora dos encontros da cabeceira
STRUT_BURY = 2.2                # quanto do eixo de cada escora entra na rocha da plataforma
STRUTS = {}                     # (pe, topo) de cada escora, por satelite (auditoria)
SAT_TWR_D = 8.0                 # torre-disco do satelite: centro a 8,0 do centro do deck (ocupa a borda de fora)
SAT_TWR_R = 2.6                 # raio do pedestal octogonal (= octo_col); fuste r 1,8; disco r 6,1; topo ~G+45
LANDING = [(x, y, r) for x, y, r, k in L.GROUND_LOTS if k == "landing_pad"][0]
PAD_HDG = math.atan2(54.0 - LANDING[1], -128.0 - LANDING[0])   # nariz da aeronave: para o fim da trilha do heliponto


# ------------------------------------------------------------------ portas da passarela (do Capsule)
def ports():
    """(tipo_torre, ponto da face da porta) - o marcador SKYWALK_PORT_Cap* quando existe, senao a mesma conta do
    db_capsule (anexo -> torre, face em ar + 1,45, z CAP + 10)"""
    out = {}
    for (ax, ay, ar), side, tk in zip(L.CAPSULE_ANNEX, ("W", "E"), ("comm", "lookout")):
        ob = bpy.data.objects.get("SKYWALK_PORT_Cap%s" % side)
        if ob is not None:
            out[tk] = Vector(ob.location)
            continue
        tx, ty, tr = SITES[tk]
        t = math.atan2(ty - ay, tx - ax)
        out[tk] = Vector((ax + (ar + 1.45) * math.cos(t), ay + (ar + 1.45) * math.sin(t), TUBE_Z))
    return out


# ------------------------------------------------------------------ satelites: referencial
def sat_frame(kind):
    x, y, r = SITES[kind]
    a0, a1 = L.SAT_BRIDGES[kind]
    ux, uy = x - a1[0], y - a1[1]
    ln = math.hypot(ux, uy)
    return (x, y, r), a0, a1, (ux / ln, uy / ln)


def rot2(v, ang):
    c, s = math.cos(ang), math.sin(ang)
    return (v[0] * c - v[1] * s, v[0] * s + v[1] * c)


def sat_props(kind):
    """posicoes da torre-disco, do banco e da luneta no deck (angulo polar a partir do eixo de fora)"""
    (x, y, r), a0, a1, u = sat_frame(kind)
    sgn = 1.0 if kind == "pad_sw" else -1.0
    db = rot2(u, sgn * 100.0 * D2R)
    dt = rot2(u, -sgn * 96.0 * D2R)
    return {"tower": (x + u[0] * SAT_TWR_D, y + u[1] * SAT_TWR_D, u),
            "bench": (x + db[0] * 6.9, y + db[1] * 6.9, db),
            "scope": (x + dt[0] * 7.1, y + dt[1] * 7.1, dt)}


# ------------------------------------------------------------------ cameras de revisao (360 + altura do jogador)
CAMS = {
    "CAM_DBTwr_Comm": ((-60.0, 108.0, HB + 34.0), (-100.0, 152.0, HB + 24.0), 22),
    "CAM_DBTwr_CommBack": ((-182.0, 238.0, 100.0), (-104.0, 150.0, 64.0), 24),
    "CAM_DBTwr_CommWest": ((-118.0, 136.0, HB + 5.2), (-104.0, 150.0, 48.0), 20),
    "CAM_DBTwr_Lookout": ((90.0, 104.0, HB + 12.0), (100.0, 140.0, HB + 24.0), 22),
    "CAM_DBTwr_LookoutBackNE": ((128.0, 166.0, 74.0), (100.0, 140.0, 78.0), 22),
    "CAM_DBTwr_Energy": ((95.0, 101.0, HB + 8.0), (73.0, 119.0, HB + 14.0), 20),
    "CAM_DBTwr_Skywalks": ((0.0, 70.0, 98.0), (0.0, 158.0, 46.0), 18),
    "CAM_DBTwr_PlayerHub": ((-83.0, 172.0, HB + 5.2), (-104.0, 150.0, HB + 16.0), 22),
    "CAM_DBTwr_PlayerLookout": ((118.0, 117.0, HB + 5.2), (100.0, 140.0, HB + 21.0), 20),
    "CAM_DBTwr_PortW": ((-36.0, 150.0, CAP + 14.0), (-66.0, 170.0, CAP + 9.0), 22),
    "CAM_DBTwr_SatSW_Player": ((-111.0, -68.0, G + 5.2), (-148.0, -98.0, G + 5.0), 22),
    "CAM_DBTwr_SatSW_Deck": ((-144.5, -94.5, G + 5.2), (-153.7, -103.7, G + 30.0), 18),
    "CAM_DBTwr_SatSW_Out": ((-222.0, -146.0, G + 14.0), (-148.0, -98.0, G + 10.0), 24),
    "CAM_DBTwr_SatSE_Player": ((104.0, -49.0, G + 5.2), (140.0, -76.0, G + 5.0), 22),
    "CAM_DBTwr_SatSE_Out": ((216.0, -132.0, G + 14.0), (140.0, -76.0, G + 10.0), 24),
    "CAM_DBTwr_SatSE_Under": ((153.0, -45.0, G - 9.0), (125.0, -65.0, G - 3.0), 22),
    "CAM_DBTwr_SatSE_Bench": ((143.5, -70.5, G + 5.2), (134.5, -81.5, G + 1.2), 22),
    "CAM_DBTwr_LookoutFull": ((36.0, 124.0, CAP + 18.0), (100.0, 140.0, HB + 32.0), 18),
    "CAM_DBTwr_Pad": ((-106.0, 34.0, G + 16.0), (-140.0, 58.0, G + 3.0), 22),
    "CAM_DBTwr_PadPlayer": ((-123.0, 48.0, G + 5.2), (-140.0, 59.0, G + 3.5), 22),
    "CAM_DBTwr_PadSide": ((-133.0, 34.0, G + 6.0), (-140.0, 58.0, G + 3.0), 22),
}


# ------------------------------------------------------------------ rotas e sondas extras (db_qa)
def _sat_route(kind):
    (x, y, r), a0, a1, u = sat_frame(kind)
    P = sat_props(kind)
    bx, by, db = P["bench"]
    sx, sy, dt = P["scope"]
    bd = (a1[0] - a0[0], a1[1] - a0[1])
    bl = math.hypot(*bd)
    start = (a1[0] + bd[0] / bl * 1.5, a1[1] + bd[1] / bl * 1.5)
    return [start, (x, y), (x + db[0] * 4.3, y + db[1] * 4.3), (x, y), (x + dt[0] * 4.3, y + dt[1] * 4.3), (x, y),
            (x + u[0] * 2.8, y + u[1] * 2.8)]


def _ring(cx, cy, r, a0, a1, step=30.0):
    n = max(1, int(abs(a1 - a0) / step))
    return [(cx + r * math.cos((a0 + (a1 - a0) * i / n) * D2R), cy + r * math.sin((a0 + (a1 - a0) * i / n) * D2R))
            for i in range(n + 1)]


EXTRA_ROUTES = {
    "TWR_SAT_SW_DECK": (_sat_route("pad_sw"), G),
    "TWR_SAT_SE_DECK": (_sat_route("pad_se"), G),
    "TWR_HELIPONTO_VOLTA": ([(-127.0, 54.0)] + _ring(LANDING[0], LANDING[1], 10.6, -30.0, -330.0) + [(-127.0, 60.0)],
                            G),
    "TWR_ENERGIA_RUA": ([(88.0, 90.0), (86.0, 102.0), (81.0, 110.5), (84.0, 116.0), (83.0, 124.0)], HB),
    "TWR_MIRANTE_RUA": ([(80.0, 121.0), (88.0, 129.0), (91.0, 136.0), (92.0, 146.0), (98.0, 151.0)], HB),
    "TWR_COMM_ACESSO": ([(-80.0, 150.0), (-88.0, 146.0), (-93.0, 144.0), (-96.0, 150.0), (-97.0, 157.0),
                         (-104.0, 161.0), (-112.0, 158.0)], HB),
}


def _probes():
    """props solidos: o nariz da aeronave (vindo da trilha) e a torre-disco de cada satelite (vindo do centro do
    deck: a face de dentro do pedestal fica a SAT_TWR_D - SAT_TWR_R do centro)"""
    out = []
    x, y, r = LANDING
    hx, hy = math.cos(PAD_HDG), math.sin(PAD_HDG)
    # o raio da sonda sai a z + 2,0: com z = G + 1,0 ele passa na cintura do nariz (a colisao comeca em ~2,0 acima
    #   do piso; o trem de pouso e o vao sob a barriga ficam livres)
    out.append(("TWR_AERONAVE_nariz", x + hx * 13.0, y + hy * 13.0, G + 1.0, -hx, -hy, 8.0))
    for kind in ("pad_sw", "pad_se"):
        (sx, sy, sr), a0, a1, u = sat_frame(kind)
        out.append(("TWR_TORRE_%s" % kind, sx, sy, G, u[0], u[1], SAT_TWR_D - SAT_TWR_R + 1.0))
    return out


EXTRA_PROBES = _probes()


# ------------------------------------------------------------------ geometria generica
def lathe_pts(mb, c, pts, n, a0=0.0, a1=360.0, smooth=True):
    """torno do K.lathe a partir de [(r, z, material_da_aresta_seguinte[, liso])]: arestas ingremes (paredes) lisas"""
    prof = [(p[0], p[1]) for p in pts]
    mats = [p[2] for p in pts]
    k = len(pts)
    sm = []
    for j in range(k - 1 if smooth else 0):
        (r0, z0), (r1, z1) = prof[j], prof[j + 1]
        force = len(pts[j]) > 3 and pts[j][3]
        if force or (abs(z1 - z0) > 1.5 * abs(r1 - r0) and abs(z1 - z0) > 0.3):
            sm.append(j)
    return K.lathe(mb, c, prof, mats[0], n, a0, a1, smooth=sm, mats=mats)


def lathe_axis(mb, c, axis, prof, m, n=20, mats=None, smooth=True, sq=(1.0, 1.0)):
    """torno em volta de um eixo QUALQUER: perfil fechado [(raio, h)] (h ao longo do eixo a partir de c).
    sq = (escala lateral, escala vertical) da secao (casco achatado)"""
    ax = Vector(axis).normalized()
    if abs(ax.z) < 0.9:
        u = Vector((0.0, 0.0, 1.0)).cross(ax).normalized()
    else:
        u = ax.orthogonal().normalized()
    v = ax.cross(u)
    u = u * sq[0]
    v = v * sq[1]
    c = Vector(c)
    bm = mb.bm
    k = len(prof)
    rings = []
    for i in range(n):
        a = 2 * math.pi * i / n
        d = u * math.cos(a) + v * math.sin(a)
        rings.append([bm.verts.new(c + d * r + ax * h) for r, h in prof])
    by_edge = {}
    for i in range(n):
        r0, r1 = rings[i], rings[(i + 1) % n]
        for j in range(k):
            j2 = (j + 1) % k
            try:
                by_edge.setdefault(j, []).append(bm.faces.new((r0[j], r0[j2], r1[j2], r1[j])))
            except ValueError:
                pass
    mb._post([vv for rr in rings for vv in rr], m, None, 0, 1)
    if mats:
        for j, fs in by_edge.items():
            mj = mats[j] if j < len(mats) and mats[j] else m
            if mj != m:
                mi = mb._mi_for(mj)
                for f in fs:
                    f.material_index = mi
                mb._uv(fs, mj)
    if smooth:
        for j, fs in by_edge.items():
            if j < k - 1:
                K._smooth(fs)
    return by_edge


def dish(mb, c, axis, R, depth, th, m, n=20, k=4):
    """prato parabolico (casca com espessura), concavo para +axis, centro do fundo em c"""
    f = R * R / (4.0 * depth)
    front = [(max(0.2, R * i / k), (max(0.2, R * i / k)) ** 2 / (4 * f)) for i in range(k + 1)]
    back = [(r, h - th) for r, h in reversed(front)]
    return lathe_axis(mb, c, axis, front + back, m, n)


def ellipsoid(mb, c, radii, rot, m, sub=2):
    M = Matrix.LocRotScale(Vector(c), Euler(rot), Vector(radii))
    res = bmesh.ops.create_icosphere(mb.bm, subdivisions=sub, radius=1.0, matrix=M)
    fs = mb._post(res["verts"], m, None, 0, 1)
    K._smooth(fs)
    return fs


def poly_prism(mb, pts, z0, z1, m):
    mb.prism(DL.ccw([(p[0], p[1]) for p in pts]), z0, z1, m)


def _runs(pts, keep, step=1.0, closed=True):
    """copia do db_col._runs (privado): divide a polilinha em trechos continuos onde keep(p) e verdadeiro"""
    runs, run = [], []
    n = len(pts)
    for i in range(n if closed else n - 1):
        a = Vector((*pts[i], 0))
        b = Vector((*pts[(i + 1) % n], 0))
        d = b - a
        ns = max(1, int(d.length / step))
        for k in range(ns):
            p = a + d * (k / ns)
            if keep(p.x, p.y):
                run.append(p)
            else:
                if len(run) > 1:
                    runs.append(run)
                run = []
    if len(run) > 1:
        runs.append(run)
    return runs


def simplify(pts):
    """tira os pontos colineares de uma polilinha de Vector"""
    if len(pts) < 3:
        return list(pts)
    out = [pts[0]]
    for i in range(1, len(pts) - 1):
        a, b, c = out[-1], pts[i], pts[i + 1]
        d1, d2 = (b - a), (c - b)
        if d1.length < 1e-6 or d2.length < 1e-6:
            continue
        if d1.normalized().dot(d2.normalized()) < 0.9995:
            out.append(b)
    out.append(pts[-1])
    return out


def capsule_rail(mb, pl, z, posts=True):
    """guarda-corpo Capsule (o mesmo da vila no db_terrain): mureta branca, balaustres brancos, corrimao azul e
    pilares maiores a cada ~9,6 com capa azul. pl: Vector (x, y) na linha da guarda invisivel; z = piso."""
    pl = simplify([Vector((p.x, p.y, 0.0)) for p in pl])
    if len(pl) < 2:
        return
    path = [Vector((p.x, p.y, z)) for p in pl]
    mb.sweep(path, [(-0.42, 0.18), (0.42, 0.18), (0.42, 0.6), (-0.42, 0.6)], WHITE, True)
    mb.sweep(path, [(-0.42, 1.52), (0.42, 1.52), (0.42, 1.82), (-0.42, 1.82)], BLUE, True)
    total = sum((b - a).length for a, b in zip(pl, pl[1:]))
    kk = max(1, int(round(total / 3.2)))
    marks = [total * i / kk for i in range(kk + 1)]
    acc = 0.0
    mi = 0
    for a, b in zip(pl, pl[1:]):
        ln = (b - a).length
        ang = math.atan2(b.y - a.y, b.x - a.x)
        while mi < len(marks) and marks[mi] <= acc + ln + 1e-6:
            t = (marks[mi] - acc) / ln if ln > 1e-6 else 0.0
            q = a + (b - a) * t
            if posts and (mi % 3 == 0 or mi == len(marks) - 1):
                mb.box((0.95, 0.95, 1.95), (q.x, q.y, z + 0.16 + 0.975), (0, 0, ang), WHITE, 0.08)
                mb.box((1.15, 1.15, 0.3), (q.x, q.y, z + 2.11 + 0.15), (0, 0, ang), BLUE, 0.08)
            else:
                mb.box((0.5, 0.5, 0.95), (q.x, q.y, z + 0.6 + 0.475), (0, 0, ang), WHITE, 0.0)
            mi += 1
        acc += ln


def pave_ring(mb, cx, cy, r0, r1, z0, rng, a0=0.0, a1=360.0, ring_w=2.1, gap=0.2, h=0.35, m=PAVE):
    """calcamento radial em aneis de lajes em arco (fm_parts.pave_ring sem chanfro: metade dos triangulos)"""
    r = r0
    ring_i = 0
    full = (a1 - a0) >= 359.0
    while r < r1 - 0.3:
        rr = min(r + ring_w, r1)
        circ = math.radians(a1 - a0) * (r + rr) / 2
        n = max(2, int(circ / 2.8))
        da = (a1 - a0) / n
        off = 0.5 * da if (ring_i % 2 and full) else 0.0
        g = gap / max(r, 1.0)
        for i in range(n):
            aa = math.radians(a0 + da * i + off)
            ab = math.radians(a0 + da * (i + 1) + off)
            pts = []
            for k in range(3):
                t = aa + g + (ab - aa - 2 * g) * k / 2
                pts.append((cx + math.cos(t) * (rr - gap / 2), cy + math.sin(t) * (rr - gap / 2)))
            for k in range(2, -1, -1):
                t = aa + g + (ab - aa - 2 * g) * k / 2
                pts.append((cx + math.cos(t) * (r + gap / 2), cy + math.sin(t) * (r + gap / 2)))
            mb.prism(pts, z0, z0 + h + rng.uniform(-0.03, 0.03), m)
        r = rr
        ring_i += 1


def capsule_lamp(mb, x, y, z, s=1.0):
    """lampiao Capsule (a linguagem da entrada): pescoco azul-marinho, disco branco, globo aceso, disco, cupula azul"""
    mb.cyl(0.36 * s, 0.7 * s, (x, y, z + 0.35 * s), m=NAVY, n=10, bevel=0.0)
    mb.cyl(0.88 * s, 0.28 * s, (x, y, z + 0.84 * s), m=WHITE, n=14, bevel=0.0)
    mb.cyl(0.62 * s, 1.35 * s, (x, y, z + 0.98 * s + 0.675 * s), m=LAMP, n=12, bevel=0.0)
    mb.cyl(0.92 * s, 0.28 * s, (x, y, z + 2.33 * s + 0.14 * s), m=WHITE, n=14, bevel=0.0)
    DL.dome(mb, (x, y), 0.66 * s, z + 2.61 * s, BLUE, n=12, rings=3, squash=0.9)


def plinth(mb, c, r, z, band=0.55):
    """base octogonal (vertices em 0, 45, ... = o octogono EXATO do octo_col de raio r): faixa azul-marinho + topo
    branco em z + 1,0 (a mesma cota da colisao)"""
    lathe_pts(mb, c, [(0.3, z - 0.5, NAVY), (r, z - 0.5, NAVY), (r, z + band, WHITE), (r, z + 1.0, WHITE),
                      (0.3, z + 1.0, WHITE)], 8, smooth=False)


# ------------------------------------------------------------------ passarela de vidro
def skywalk(mb, tk, port):
    tx, ty, tr = SITES[tk]
    P0 = Vector((port.x, port.y, port.z))
    d = Vector((tx - P0.x, ty - P0.y, 0.0))
    dist = d.length
    d.normalize()
    P1 = P0 + d * (dist - DOCK_R[tk])
    Ln = (P1 - P0).length
    mid = (P0 + P1) / 2
    yaw = math.atan2(d.y, d.x)
    up = Vector((0.0, 0.0, 1.0))
    # tubo de vidro (35% transparente no Roblox) + faixa de piso opaca por dentro
    K.cyl_axis(mb, TUBE_R, Ln, mid, d, GLASS, 20)
    mb.box((Ln - 0.4, 3.2, 0.3), mid - up * 1.55, (0, 0, yaw), NAVY, 0.0)
    # quilha (viga branca por baixo) e espinha (por cima): o tubo le mesmo transparente
    mb.box((Ln, 1.5, 0.9), mid - up * (TUBE_R + 0.3), (0, 0, yaw), WHITE, 0.0)
    mb.box((Ln, 0.9, 0.4), mid + up * (TUBE_R + 0.05), (0, 0, yaw), WHITE, 0.0)
    # costelas brancas (aneis) a cada ~3,2
    nr = max(2, int(round(Ln / 3.6)))
    for i in range(1, nr):
        K.torus(mb, P0 + d * (Ln * i / nr), TUBE_R + 0.14, 0.2, WHITE, axis=tuple(d), n=12, k=4, smooth=False)
    K.torus(mb, P0 + d * 0.35, TUBE_R + 0.12, 0.28, WHITE, axis=tuple(d), n=20, k=4, smooth=False)
    # anel de acoplamento no lado da torre: colar azul-marinho + flange branco
    R = DOCK_R[tk]
    emb = R - math.sqrt(R * R - 3.1 * 3.1) + 0.2          # o colar entra no casulo curvo ate cobrir as bordas
    K.cyl_axis(mb, 3.1, 1.4 + emb, P1 + d * ((emb - 1.4) / 2), d, NAVY, 24)
    K.torus(mb, P1 - d * 1.55, 2.85, 0.34, WHITE, axis=tuple(d), n=24, k=6, smooth=True)
    # pilares finos (Y de apoio sob a quilha)
    zk = P0.z - TUBE_R - 0.75
    for t in PILLAR_T[tk]:
        q = P0 + d * (Ln * t)
        zf = L.zone_of(q.x, q.y)
        h = zk - zf
        mb.cyl(0.75, h, (q.x, q.y, zf + h / 2), m=WHITE, n=12, bevel=0.0)
        mb.cyl(1.15, 1.1, (q.x, q.y, zf + 0.55), m=NAVY, n=12, bevel=0.0)
        mb.cyl(0.95, 0.5, (q.x, q.y, zf + 1.35), m=WHITE, n=12, bevel=0.0)
        mb.cyl(0.9, 0.45, (q.x, q.y, zk - 3.2), m=NAVY, n=12, bevel=0.0)
        mb.box((3.0, 2.0, 0.6), (q.x, q.y, zk - 0.3), (0, 0, yaw), WHITE, 0.0)
        for s in (-1, 1):
            a = Vector((q.x, q.y, zk - 3.0))
            b = Vector((q.x, q.y, zk - 0.5)) + d * (1.35 * s)
            mb.beam(a, b, 0.4, 0.4, WHITE, 0.0)
        octo_col("DB_TwrSkywalk", q.x, q.y, 1.3, zf, zf + 1.6)      # colar r 1,15 (faces em 1,2)
        col_box("DB_TwrSkywalk", (1.6, 1.6, h - 1.6), (q.x, q.y, zf + 1.6 + (h - 1.6) / 2), (0, 0, yaw))
    return P1


# ------------------------------------------------------------------ torre de comunicacao (mastro + radar)
def comm_tower(port):
    x, y, r = SITES["comm"]
    z = L.zone_of(x, y)
    c = (x, y)
    mb = K.CMB("DB_Twr_Comm", COLL, detail="near")
    plinth(mb, c, 6.2, z)
    Z = lambda h: z + h
    Z1, Z2, Z3, Z4 = [(lambda h, d=d: z + h + d) for d in CM_RISE]
    pts = [
        (0.3, Z(1.0), NAVY), (4.2, Z(1.0), NAVY), (4.2, Z(2.0), WHITE), (3.9, Z(2.0), WHITE), (3.3, Z(3.4), WHITE, 1),
        (2.8, Z(5.2), WHITE, 1), (2.45, Z(7.4), WHITE), (2.3, Z(11.0), WHITE), (3.4, Z(11.6), WHITE, 1),
        (4.3, Z(12.6), NAVY), (4.6, Z(13.4), WHITE), (4.6, Z(18.6), NAVY), (4.3, Z(19.4), WHITE, 1),
        (3.2, Z(20.4), WHITE, 1), (2.1, Z(21.0), WHITE),
        # 3 discos azuis empilhados (os "aneis" da concept), afastados (CM_RISE): o mastro passa da cupula
        (2.1, Z1(26.4), WHITE), (5.4, Z1(26.9), NAVY), (5.4, Z1(27.35), BLUE), (5.0, Z1(27.7), BLUE),
        (2.0, Z1(28.2), WHITE),
        (2.0, Z2(30.3), WHITE), (4.8, Z2(30.75), NAVY), (4.8, Z2(31.15), BLUE), (4.4, Z2(31.45), BLUE),
        (1.9, Z2(31.9), WHITE),
        (1.9, Z3(34.1), WHITE), (4.2, Z3(34.5), NAVY), (4.2, Z3(34.85), BLUE), (3.8, Z3(35.15), BLUE),
        (1.8, Z3(35.6), WHITE),
        # plataforma de servico
        (1.8, Z4(39.6), WHITE), (5.3, Z4(40.3), NAVY), (5.3, Z4(41.0), WHITE), (1.7, Z4(41.0), WHITE),
        (1.6, Z4(43.4), NAVY), (2.3, Z4(43.5), NAVY), (2.3, Z4(44.0), WHITE), (0.3, Z4(44.0), WHITE),
    ]
    lathe_pts(mb, c, pts, 20)
    # mureta da plataforma de servico
    K.ring(mb, c, 4.85, 5.15, Z4(41.0), Z4(42.0), WHITE, 32)
    K.ring(mb, c, 4.8, 5.2, Z4(42.0), Z4(42.25), BLUE, 32)
    # faixa de janelas do casulo: cinta azul-marinho saliente com 16 escotilhas pequenas de aro BRANCO (fileira de
    #   janelas vista de qualquer lado). Antes: 8 escotilhas grandes de aro escuro no casulo branco - do oeste, 2
    #   delas sobre a faixa de baixo liam como um rosto (olhos + boca). Interrompida no colar do tubo (r 3,1 = +-42 gr).
    t_port = math.degrees(math.atan2(port.y - y, port.x - x))
    K.ring(mb, c, 4.5, 4.72, Z(15.0), Z(17.0), NAVY, 36, t_port + 36.0, t_port + 324.0)
    for i in range(16):
        th = 11.25 + 22.5 * i
        if abs((th - t_port + 180.0) % 360.0 - 180.0) < 52.0:           # livre do colar r 3,1
            continue
        K.porthole(mb, x, y, 4.72, th, Z(16.0), rr=0.55, frame_m=WHITE, glass_m=GLASS, n=10, proud=0.22)
    # pratos parabolicos em bracos (virados para fora da ilha, subindo 18 graus)
    for hd, zz, R in ((168.0, 23.6, 2.1), (238.0, 22.4, 1.7)):
        a = hd * D2R
        dvec = Vector((math.cos(a) * math.cos(18 * D2R), math.sin(a) * math.cos(18 * D2R), math.sin(18 * D2R)))
        base = Vector((x + math.cos(a) * 2.0, y + math.sin(a) * 2.0, Z(zz)))
        pc = Vector((x + math.cos(a) * 3.6, y + math.sin(a) * 3.6, Z(zz) + 0.4))
        mb.beam(base, pc, 0.5, 0.5, STEEL, 0.0)
        dish(mb, pc, dvec, R, R * 0.32, 0.25, WHITE, n=16, k=3)
        mb.rod(pc, pc + dvec * (R * 0.95), 0.12, STEEL, 6)
        mb.box((0.45, 0.45, 0.45), tuple(pc + dvec * (R * 0.95)), (0, 0, a), NAVY, 0.0)
    # antenas com farol vermelho (a mais alta e o topo da torre, ~66 acima do piso = ~95 absoluto)
    tops = []
    for hd, h1 in ((104.0, 52.2), (284.0, 48.6)):
        a = hd * D2R
        p0 = Vector((x + math.cos(a) * 4.4, y + math.sin(a) * 4.4, Z4(41.0)))
        p1 = Vector((p0.x, p0.y, Z4(h1)))
        mb.cyl(0.5, 0.8, (p0.x, p0.y, Z4(41.4)), m=NAVY, n=8, bevel=0.0)
        mb.rod(p0, p1, 0.2, STEEL, 6)
        for f in (0.45, 0.75):
            q = p0 + (p1 - p0) * f
            mb.box((1.6, 0.25, 0.25), (q.x, q.y, q.z), (0, 0, a + math.pi / 2), STEEL, 0.0)
        K.sphere(mb, (p1.x, p1.y, p1.z + 0.35), 0.5, RED, sub=1)
        tops.append(Vector((p1.x, p1.y, p1.z + 0.35)))
    P1 = skywalk(mb, "comm", port)
    mb.finish()
    # radar giratorio no topo do mastro (peca movel)
    rv = K.CMB("VFX_DBTWR_Radar", VFXC, detail="near")
    zt = Z4(44.0)
    rv.cyl(1.35, 0.7, (x, y, zt + 0.35), m=STEEL, n=16, bevel=0.0)
    rv.cyl(0.55, 1.9, (x, y, zt + 1.6), m=WHITE, n=10, bevel=0.0)
    hd = 25.0 * D2R
    dv = Vector((math.cos(hd) * math.cos(16 * D2R), math.sin(hd) * math.cos(16 * D2R), math.sin(16 * D2R)))
    hv = Vector((math.cos(hd), math.sin(hd), 0.0))
    dc = Vector((x, y, zt + 3.2)) + hv * 0.7
    rv.beam(Vector((x, y, zt + 2.4)), dc - dv * 0.2, 0.5, 0.5, STEEL, 0.0)
    dish(rv, dc, dv, 2.6, 0.85, 0.28, WHITE, n=18, k=4)
    rv.rod(dc, dc + dv * 2.3, 0.14, STEEL, 6)
    rv.box((0.55, 0.55, 0.55), tuple(dc + dv * 2.3), (0, 0, hd), STEEL, 0.0)
    rv.box((1.2, 1.0, 0.9), (x - hv.x * 1.3, y - hv.y * 1.3, zt + 2.3), (0, 0, hd), WHITE, 0.0)
    ob = rv.finish()
    ob["pivot"] = (x, y, zt)
    ob["axis"] = (0.0, 0.0, 1.0)
    ob["rpm"] = 10.0
    ob["note"] = "radar do mastro de comunicacao: gira em volta do eixo do mastro"
    # colisao: base (degrau walkable) + fuste ate o casulo (o resto fica fora do alcance)
    octo_col("DB_TwrComm", x, y, 6.2, z - 0.5, Z(1.0))
    octo_col("DB_TwrComm", x, y, 4.6, Z(1.0), Z(21.0))          # faces em 4,25 >= pe r 4,2
    light("L_DBTwr_CommBeacon", "POINT", tuple(tops[0]), 320, (1.0, 0.16, 0.12), 0.5)
    return ob


# ------------------------------------------------------------------ mirante (disco voador envidracado)
def lookout_tower(port):
    x, y, r = SITES["lookout"]
    z = L.zone_of(x, y)
    c = (x, y)
    Z = lambda h: z + h
    U = lambda h: z + h + LK_RISE             # cota de tudo o que fica ACIMA do trecho de fuste acrescentado
    mb = K.CMB("DB_Twr_Lookout", COLL, detail="near")
    plinth(mb, c, 6.4, z)
    dome_pts = []
    a, b, zc = 8.6, 3.8, U(36.9)
    for i, ph in enumerate((0.0, 16.0, 32.0, 48.0, 62.0, 76.0)):
        dome_pts.append((a * math.cos(ph * D2R), zc + b * math.sin(ph * D2R), BLUE, 1))
    zm = Z(19.4) + LK_RISE * 0.52              # colar intermediario do fuste alongado (quebra a coluna comprida)
    pts = [
        (0.3, Z(1.0), NAVY), (4.3, Z(1.0), NAVY), (4.3, Z(1.8), WHITE), (4.3, Z(5.6), BLUE), (4.6, Z(5.9), BLUE),
        (4.6, Z(6.4), WHITE), (2.7, Z(7.4), WHITE), (2.6, Z(12.6), NAVY), (3.7, Z(13.0), WHITE), (3.7, Z(19.0), NAVY),
        (2.5, Z(19.4), WHITE),
        # fuste alongado (+LK_RISE): o disco sobe acima da cupula do Capsule (skyline da concept)
        (2.5, zm - 0.9, NAVY), (3.25, zm - 0.5, NAVY), (3.25, zm + 0.1, BLUE), (3.0, zm + 0.4, BLUE),
        (2.48, zm + 0.7, WHITE),
        (2.45, U(23.6), WHITE), (4.6, U(24.0), NAVY), (4.6, U(24.5), BLUE), (4.2, U(24.8), BLUE),
        (2.4, U(25.2), WHITE),
        # disco voador: bojo de baixo branco, faixa azul-marinho, vidro, beiral branco, cupula azul
        (2.4, U(29.6), WHITE, 1), (4.6, U(30.6), WHITE, 1), (6.9, U(31.6), WHITE, 1), (8.7, U(32.4), NAVY),
        (9.3, U(32.9), NAVY), (9.3, U(33.4), GLASS), (9.6, U(35.9), WHITE), (10.1, U(36.2), WHITE),
        (10.1, U(36.8), WHITE),
    ] + dome_pts + [(1.6, U(40.7), WHITE), (1.6, U(41.2), WHITE), (0.3, U(41.2), WHITE)]
    lathe_pts(mb, c, pts, 28)
    # fundo opaco atras do vidro + montantes brancos
    K.ring(mb, c, 8.5, 8.9, U(33.2), U(36.2), NAVY, 32)
    for i in range(20):
        t = (9.0 + 18.0 * i) * D2R
        mb.box((0.34, 0.32, 2.7), (x + 9.5 * math.cos(t), y + 9.5 * math.sin(t), U(34.65)), (0, 0.12, t), WHITE, 0.0)
    # escotilhas do tambor de base (sem porta: nao entravel)
    for i in range(8):
        K.porthole(mb, x, y, 4.3, 22.5 + 45.0 * i, Z(3.9), rr=0.9, frame_m=NAVY, glass_m=GLASS, n=10)
    # antena curta com ponta ciano
    mb.rod((x, y, U(41.2)), (x, y, U(44.2)), 0.16, STEEL, 6)
    K.sphere(mb, (x, y, U(44.5)), 0.42, CYAN, sub=2)
    # friso de luz ciano sob o disco (le de baixo) + nervuras radiais azul-marinho no bojo
    K.ring(mb, c, 8.9, 9.05, U(32.25), U(32.6), CYAN, 40)
    for i in range(12):
        t = (15.0 + 30.0 * i) * D2R
        ct, st = math.cos(t), math.sin(t)
        a = Vector((x + 3.2 * ct, y + 3.2 * st, U(29.96) - 0.1))
        b = Vector((x + 8.3 * ct, y + 8.3 * st, U(32.2) - 0.1))
        mb.beam(a, b, 0.42, 0.36, NAVY, 0.0)
    # poco do elevador envidracado no fuste (virado para a vila), com moldura azul-marinho atras do vidro;
    #   interrompido no colar intermediario e nos discos
    t = math.atan2(100.0 - y, 0.0 - x)
    ct, st = math.cos(t), math.sin(t)
    zm0, zm1 = zm - 0.9 - z, zm + 0.7 - z
    for za, zb in ((7.7, 12.4), (19.6, zm0 - 0.2), (zm1 + 0.2, 23.4 + LK_RISE), (25.4 + LK_RISE, 29.4 + LK_RISE)):
        h = zb - za
        mb.box((0.36, 1.7, h + 0.3), (x + 2.42 * ct, y + 2.42 * st, Z((za + zb) / 2)), (0, 0, t), NAVY, 0.0)
        mb.box((0.3, 1.2, h), (x + 2.6 * ct, y + 2.6 * st, Z((za + zb) / 2)), (0, 0, t), GLASS, 0.0)
    skywalk(mb, "lookout", port)
    ob = mb.finish()
    octo_col("DB_TwrLookout", x, y, 6.4, z - 0.5, Z(1.0))
    octo_col("DB_TwrLookout", x, y, 5.0, Z(1.0), Z(20.0))       # faces em 4,62 >= beiral r 4,6
    return ob


# ------------------------------------------------------------------ estacao de energia (bobinas + orbe + anel)
def energy_station():
    x, y, r = SITES["energy"]
    z = L.zone_of(x, y)
    c = (x, y)
    Z = lambda h: z + h
    mb = K.CMB("DB_Twr_Energy", COLL, detail="near")
    plinth(mb, c, 6.0, z)
    pts = [
        (0.3, Z(1.0), NAVY), (3.8, Z(1.0), NAVY), (3.8, Z(2.2), WHITE), (3.5, Z(2.6), WHITE), (3.5, Z(6.4), NAVY),
        (3.9, Z(6.8), NAVY), (3.9, Z(7.3), WHITE), (1.6, Z(8.0), DARK), (1.3, Z(18.0), WHITE),
        (2.2, Z(18.6), WHITE, 1), (3.0, Z(19.6), WHITE, 1), (3.2, Z(20.6), WHITE), (2.7, Z(20.8), NAVY),
        (2.3, Z(20.2), NAVY, 1), (1.0, Z(19.7), NAVY), (0.3, Z(19.7), NAVY),
    ]
    lathe_pts(mb, c, pts, 24)
    for zz in (10.6, 14.6):
        K.ring(mb, c, 1.3, 1.85, Z(zz), Z(zz + 0.5), WHITE, 20)
    # frisos ciano no tambor
    for i in range(6):
        t = (30.0 + 60.0 * i) * D2R
        mb.box((0.3, 0.55, 3.0), (x + 3.52 * math.cos(t), y + 3.52 * math.sin(t), Z(4.5)), (0, 0, t), CYAN, 0.0)
    # 3 bobinas Tesla (cobre) em volta
    coils = []
    for i in range(3):
        t = (90.0 + 120.0 * i) * D2R
        px, py = x + 4.8 * math.cos(t), y + 4.8 * math.sin(t)
        coils.append((px, py, t))
        mb.box((1.3, 1.3, 1.3), (px, py, Z(1.65)), (0, 0, t), NAVY, 0.0)
        mb.cyl(0.4, 11.8, (px, py, Z(2.3 + 5.9)), m=STEEL, n=8, bevel=0.0)
        for k in range(9):
            mb.cyl(0.8, 0.4, (px, py, Z(3.5 + 0.9 * k)), m=COIL, n=10, bevel=0.0)
        mb.cyl(0.6, 0.5, (px, py, Z(12.0)), m=WHITE, n=10, bevel=0.0)
        K.torus(mb, (px, py, Z(14.4)), 0.95, 0.36, WHITE, axis=(0, 0, 1), n=16, k=6)
        K.sphere(mb, (px, py, Z(15.25)), 0.5, CYAN, sub=2)
        # cabo escuro da bobina ate o tambor
        mb.beam(Vector((px, py, Z(1.9))), Vector((x + 3.4 * math.cos(t), y + 3.4 * math.sin(t), Z(3.4))), 0.45, 0.45,
                DARK, 0.0)
    # gaiola: 3 arcos brancos da borda da taca ate o topo (livres do anel que gira)
    orb_c = Vector((x, y, Z(23.6)))
    # arco: do aro da taca (r 3,0) ao anel do topo (r 1,35), barriga em r 4,9 na cota do orbe
    arch = []
    for k in range(13):
        ph = -60.0 + 150.0 * k / 12.0
        if ph >= 0.0:
            rr = 1.35 + (4.9 - 1.35) * math.cos(ph * D2R)
            hh = 23.6 + (28.4 - 23.6) * math.sin(ph * D2R)
        else:
            f = ph / -60.0
            rr = 4.9 - (4.9 - 3.0) * f ** 1.6
            hh = 23.6 - (23.6 - 20.5) * f ** 1.2
        arch.append((rr, hh))
    for i in range(3):
        t = (30.0 + 120.0 * i) * D2R
        path = [Vector((x + rr * math.cos(t), y + rr * math.sin(t), z + hh)) for rr, hh in arch]
        mb.sweep(path, [(-0.24, -0.22), (0.24, -0.22), (0.24, 0.22), (-0.24, 0.22)], WHITE, True)
    K.ring(mb, c, 1.0, 1.6, Z(28.2), Z(28.75), WHITE, 18)
    mb.cyl(1.0, 0.5, (x, y, Z(28.95)), m=NAVY, n=14, bevel=0.0)
    DL.dome(mb, (x, y), 0.9, Z(29.2), BLUE, n=14, rings=3, squash=0.8)
    mb.rod((x, y, Z(29.9)), (x, y, Z(31.2)), 0.14, STEEL, 6)
    K.sphere(mb, (x, y, Z(31.4)), 0.36, CYAN, sub=2)
    ob = mb.finish()
    # orbe (flutua) e anel (gira) - pecas moveis
    ov = K.CMB("VFX_DBTWR_EnergyOrb", VFXC, detail="near")
    K.sphere(ov, tuple(orb_c), 2.0, CYAN, sub=3)
    oo = ov.finish()
    oo["pivot"] = tuple(orb_c)
    oo["axis"] = (0.0, 0.0, 1.0)
    oo["rpm"] = 3.0
    oo["bob"] = 0.6
    oo["note"] = "orbe de energia: flutua 0,6 dentro do anel"
    rg = K.CMB("VFX_DBTWR_EnergyRing", VFXC, detail="near")
    tilt = 18.0 * D2R
    ax = (math.sin(tilt), 0.0, math.cos(tilt))
    K.torus(rg, tuple(orb_c), 3.6, 0.26, CYAN, axis=ax, n=40, k=6)
    axv = Vector(ax)
    uu = axv.orthogonal().normalized()
    vv = axv.cross(uu)
    for i in range(4):
        a = math.pi / 2 * i
        dd = uu * math.cos(a) + vv * math.sin(a)
        rg.box((0.6, 0.6, 0.6), tuple(orb_c + dd * 3.6), tuple(K.rot_to(axv)), NAVY, 0.0)
    ro = rg.finish()
    ro["pivot"] = tuple(orb_c)
    ro["axis"] = (0.0, 0.0, 1.0)
    ro["rpm"] = 14.0
    ro["note"] = "anel de energia inclinado 18 graus: gira em volta do eixo vertical do orbe"
    octo_col("DB_TwrEnergy", x, y, 6.0, z - 0.5, Z(1.0))
    octo_col("DB_TwrEnergy", x, y, 4.3, Z(1.0), Z(20.8))        # faces em 3,97 >= tambor r 3,9
    for px, py, t in coils:
        col_box("DB_TwrEnergy", (1.7, 1.7, 14.4), (px, py, Z(1.0 + 7.2)), (0, 0, t))
    light("L_DBTwr_EnergyOrb", "POINT", tuple(orb_c), 900, (0.45, 0.85, 1.0), 1.5)
    return ob


# ------------------------------------------------------------------ satelites andaveis
def sat_rock(mb, rng, x, y, u):
    """pilar de rocha pendurado sob a plataforma: coluna principal + 2 companheiras (a costela do terreno)"""
    strata = [(zz - th / 2, zz + th / 2) for zz, th, amp in TR.STRATA if th > 1.0]
    rot = rng.uniform(0, math.tau)
    ca, sa = math.cos(rot), math.sin(rot)
    wp = [(px * ca - py * sa, px * sa + py * ca) for px, py in FP._rock_poly(9.6, 8.9, 10, rng, ex=2.4, jit=0.06)]
    TR.hang(mb, Vector((x, y, 0.0)), wp, G - 2.25, G - 50.0, rng, m=ROCK, tip=0.16, pw=1.5,
            lean=(u[0] * 3.0, u[1] * 3.0), lid=False, band=0.0, strata=strata, mids=(0.25, 0.5, 0.72),
            dark_from=0.62, jitter=0.06, top_jit=0.02, chamfer=0.3)
    for k, (du, dv, a, b, zt, zb) in enumerate(((4.8, 3.2, 5.2, 4.2, G - 9.0, G - 62.0),
                                                 (-1.5, -5.4, 4.2, 3.6, G - 6.5, G - 34.0))):
        cx = x + u[0] * du - u[1] * dv
        cy = y + u[1] * du + u[0] * dv
        rot = rng.uniform(0, math.tau)
        ca, sa = math.cos(rot), math.sin(rot)
        wp = [(px * ca - py * sa, px * sa + py * ca) for px, py in FP._rock_poly(a, b, 7, rng, ex=2.2, jit=0.08)]
        TR.hang(mb, Vector((cx, cy, 0.0)), wp, zt, zb, rng, m=ROCK, tip=0.14, pw=1.4,
                lean=(u[0] * 2.0, u[1] * 2.0), lid=False, band=0.0, strata=strata, mids=(0.35, 0.65),
                dark_from=0.5, jitter=0.07, top_jit=0.03, chamfer=0.4)


def sat_tower(mb, tx, ty, u):
    """torre-disco esbelta na borda de fora do satelite (a linguagem do mirante, em ponto menor): pedestal octogonal,
    tambor branco com escotilhas e faixa azul-marinho (topo G+7,95 = topo da colisao: fora do alcance do pulo, sem
    beiral onde subir), fuste r 1,8 com colares azuis, disco com bojo branco, faixa azul-marinho, VIDRO com montantes
    e fundo opaco, beiral branco, cupula azul e antena de ponta vermelha (topo ~G+45,4). Sem porta: nao entravel."""
    c = (tx, ty)
    Z = lambda h: G + h
    plinth(mb, c, SAT_TWR_R, G)
    dome_pts = []
    a, b, zc = 5.3, 2.9, Z(38.8)
    for ph in (0.0, 22.0, 44.0, 66.0):
        dome_pts.append((a * math.cos(ph * D2R), zc + b * math.sin(ph * D2R), BLUE, 1))
    pts = [
        (0.3, Z(1.0), WHITE), (2.3, Z(1.0), WHITE), (2.3, Z(7.2), NAVY), (2.45, Z(7.35), NAVY), (2.45, Z(7.95), WHITE),
        (1.8, Z(8.6), WHITE), (1.8, Z(19.9), NAVY), (2.4, Z(20.2), NAVY), (2.4, Z(20.9), BLUE), (1.8, Z(21.2), WHITE),
        (1.75, Z(31.4), NAVY), (2.5, Z(31.7), NAVY), (2.5, Z(32.2), WHITE),
        # disco: bojo branco, faixa azul-marinho, vidro, beiral, cupula
        (2.0, Z(32.8), WHITE, 1), (3.6, Z(33.9), WHITE, 1), (5.1, Z(34.9), NAVY), (5.6, Z(35.4), NAVY),
        (5.6, Z(35.9), GLASS), (5.8, Z(37.9), WHITE), (6.2, Z(38.15), WHITE), (6.2, Z(38.8), WHITE),
    ] + dome_pts + [(1.0, Z(41.6), WHITE), (1.0, Z(42.0), WHITE), (0.3, Z(42.0), WHITE)]
    lathe_pts(mb, c, pts, 16)
    # fundo opaco atras do vidro + montantes brancos + friso ciano sob o beiral
    K.ring(mb, c, 4.9, 5.2, Z(35.7), Z(38.0), NAVY, 16)
    for i in range(8):
        t = (22.5 + 45.0 * i) * D2R
        mb.box((0.3, 0.3, 2.1), (tx + 5.72 * math.cos(t), ty + 5.72 * math.sin(t), Z(36.9)), (0, 0.1, t), WHITE, 0.0)
    K.ring(mb, c, 5.2, 5.35, Z(34.75), Z(35.05), CYAN, 16)
    # nervuras radiais azul-marinho no bojo (o que o jogador ve do deck, olhando para cima; a mesma do mirante):
    #   da gola r 2,3 (bojo em z 33,0) ate r 4,8 (bojo em z 34,7), 0,22 salientes
    for i in range(8):
        t = (22.5 + 45.0 * i) * D2R
        ct, st = math.cos(t), math.sin(t)
        a = Vector((tx + 2.3 * ct, ty + 2.3 * st, Z(33.0) - 0.05))
        b = Vector((tx + 4.8 * ct, ty + 4.8 * st, Z(34.7) - 0.05))
        mb.beam(a, b, 0.36, 0.34, NAVY, 0.0)
    # poco de elevador envidracado virado para o deck (a linguagem do mirante), interrompido nos colares; sem
    #   escotilhas em par no tambor (vistas do deck, 2 escotilhas sob a faixa liam como olhos)
    t = math.atan2(-u[1], -u[0])
    ct, st = math.cos(t), math.sin(t)
    for za, zb, rr, w in ((1.7, 6.9, 2.3, 1.5), (9.2, 19.6, 1.8, 1.3), (21.5, 31.1, 1.78, 1.3)):
        h = zb - za
        mb.box((0.36, w, h + 0.3), (tx + (rr - 0.03) * ct, ty + (rr - 0.03) * st, Z((za + zb) / 2)), (0, 0, t), NAVY,
               0.0)
        mb.box((0.3, w - 0.4, h), (tx + (rr + 0.15) * ct, ty + (rr + 0.15) * st, Z((za + zb) / 2)), (0, 0, t), GLASS,
               0.0)
    # antena com farol vermelho (sinalizacao)
    mb.rod((tx, ty, Z(42.0)), (tx, ty, Z(44.9)), 0.14, STEEL, 6)
    K.sphere(mb, (tx, ty, Z(45.05)), 0.36, RED, sub=1)
    octo_col("DB_TwrSat", tx, ty, SAT_TWR_R, G - 0.5, G + 7.95)   # pedestal + tambor (faces 2,40 ~ tambor 2,3/2,45)


def bench(mb, bx, by, z, d):
    """banco Capsule: assento branco em 2 pes azul-marinho, encosto branco; o sentado olha para d (para fora)"""
    yaw = math.atan2(d[1], d[0]) - math.pi / 2
    F = Frame(bx, by, z, yaw)
    for sx in (-1.25, 1.25):
        mb.box((0.55, 1.0, 1.15), F.p(sx, 0.0, 0.575), F.r(), NAVY, 0.0)
    mb.box((3.6, 1.2, 0.32), F.p(0.0, 0.05, 1.3), F.r(), WHITE, 0.0)
    mb.box((3.6, 0.28, 1.05), F.p(0.0, -0.62, 2.0), F.r(), WHITE, 0.0)
    mb.box((3.7, 0.36, 0.24), F.p(0.0, -0.62, 2.6), F.r(), BLUE, 0.0)
    col_box("DB_TwrSat", (3.6, 1.3, 1.6), F.p(0.0, 0.0, 0.8), F.r())


def telescope(mb, sx, sy, z, d):
    """luneta de mirante num pedestal (aponta para fora, subindo)"""
    mb.cyl(0.95, 0.3, (sx, sy, z + 0.15), m=WHITE, n=14, bevel=0.0)
    mb.cyl(0.42, 2.6, (sx, sy, z + 1.6), m=NAVY, n=10, bevel=0.0)
    mb.box((0.8, 0.8, 0.6), (sx, sy, z + 3.1), (0, 0, math.atan2(d[1], d[0])), WHITE, 0.0)
    el = 14.0 * D2R
    dv = Vector((d[0] * math.cos(el), d[1] * math.cos(el), math.sin(el)))
    hc = Vector((sx, sy, z + 3.55))
    K.cyl_axis(mb, 0.42, 3.4, hc + dv * 0.5, dv, WHITE, 12)
    K.cyl_axis(mb, 0.55, 0.45, hc + dv * 2.1, dv, BLUE, 12)
    K.cyl_axis(mb, 0.26, 0.7, hc - dv * 1.45, dv, NAVY, 8)
    col_box("DB_TwrSat", (1.1, 1.1, 3.6), (sx, sy, z + 1.8), (0, 0, 0))


def _path_into(a0):
    """(direcao unitaria, meia-largura) do ultimo trecho do caminho do terreno (L.GROUND_PATHS) que chega em a0"""
    for pts, w in L.GROUND_PATHS:
        if math.hypot(pts[-1][0] - a0[0], pts[-1][1] - a0[1]) < 0.5:
            dv = Vector((pts[-1][0] - pts[-2][0], pts[-1][1] - pts[-2][1], 0.0)).normalized()
            return dv, w / 2.0
    return None, 0.0


def head_plate(mb, A0, bu, bn, yaw):
    """soleira da cabeceira (lado da ilha). O caminho do terreno (DB_Ter_Paths: lajes G+0,11, meio-fio G+0,23) avanca
    ate ~5,2 sobre a boca da ponte: a soleira branca cobre essa ponta com o topo ACIMA do meio-fio (sem 2 topos
    coplanares) e tem colisao propria na mesma cota (degrau de 0,17 a partir do caminho)."""
    x0, x1 = HEAD_PLATE
    zp = G + HEAD_TOP
    c = A0 + bu * ((x0 + x1) / 2)
    mb.box((x1 - x0, 7.8, zp - (G - 0.4)), (c.x, c.y, (zp + G - 0.4) / 2), (0, 0, yaw), WHITE, 0.0)   # entre as vigas
    # faixas azuis na entrada e na saida da soleira + 2 setas azul-marinho apontando para a plataforma
    for xx in (x0 + 0.6, x1 - 0.55):
        q = A0 + bu * xx
        mb.box((0.6, 7.4, 0.06), (q.x, q.y, zp + 0.03), (0, 0, yaw), BLUE, 0.0)
    for xx in (1.0, 2.6):
        # chevron de bracos com espessura constante = 2 paralelogramos convexos (sem ngon concavo)
        for s in (-1, 1):
            arm = [A0 + bu * xx + bn * (1.6 * s), A0 + bu * (xx + 0.6) + bn * (1.6 * s),
                   A0 + bu * (xx + 1.7), A0 + bu * (xx + 1.1)]
            poly_prism(mb, [tuple(p)[:2] for p in arm], zp, zp + 0.06, NAVY)
    col_box("DB_TwrSat", (x1 - x0, 8.0, zp - (G - 0.4)), (c.x, c.y, (zp + G - 0.4) / 2), (0, 0, yaw))


def head_wings(mb, A0, bu, bn, a0):
    """encontros (abutments) brancos dos 2 lados da cabeceira, topo G+0,1 sobre o chao G: tapam o corte da crista
    do terreno ao lado da ponte (buraco ate a face de baixo, z 22, onde o jogador anda). A borda de dentro segue o
    meio-fio do caminho que chega (sem cobrir as lajes dele); o lado por onde o caminho chega e pulado."""
    pd, hw = _path_into(a0)
    pa_ = pd.dot(bu) if pd is not None else 1.0
    pl_ = pd.dot(bn) if pd is not None else 0.0
    als = [-5.4 + (5.1 * i / 5.0) for i in range(6)]          # de -5,4 ate -0,3 (os pilones cobrem a ponta)
    for s in (-1, 1):
        inner = []
        for al in als:
            li = WING_IN
            if pd is not None and abs(pa_) > 0.2:
                lat_c = s * al * pl_ / pa_                     # lado s: lateral do eixo do caminho nessa cota
                li = max(WING_IN, lat_c + (hw - 0.4) / abs(pa_))   # entra 0,4 sob o meio-fio (ele fica por cima)
            inner.append(li)
        if max(inner) > WING_OUT - 1.2:
            continue                                           # o caminho chega por este lado: sem encontro
        pts = [tuple(A0 + bu * al + bn * (s * li))[:2] for al, li in zip(als, inner)]
        pts += [tuple(A0 + bu * al + bn * (s * WING_OUT))[:2] for al in reversed(als)]
        poly_prism(mb, pts, G - 2.1, G + 0.1, WHITE)             # o fundo fica acima da face de baixo (z 22)
        # friso azul no topo, ao longo da borda de fora (amarra o encontro ao corrimao azul da ponte)
        edge = [tuple(A0 + bu * al + bn * (s * (WING_OUT - 0.5)))[:2] for al in (als[0], als[-1])]
        edge += [tuple(A0 + bu * al + bn * (s * WING_OUT))[:2] for al in (als[-1], als[0])]
        poly_prism(mb, edge, G + 0.1, G + 0.15, BLUE)
        # faixa azul-marinho nas faces de fora (aparece onde o corte do terreno expoe o bloco)
        ext = [als[0] - 0.06] + als[1:-1] + [als[-1] + 0.06]
        out = [tuple(A0 + bu * al + bn * (s * (li + 0.1)))[:2] for al, li in zip(ext, inner)]
        out += [tuple(A0 + bu * al + bn * (s * (WING_OUT + 0.06)))[:2] for al in reversed(ext)]
        poly_prism(mb, out, G - 1.0, G - 0.55, NAVY)


def seat_struts(mb, rock, A0, bu, bn, d, kind):
    """escoras brancas sob a ponte, ASSENTADAS na rocha da plataforma: o eixo entra na rocha (BVH do pilar) e segue
    STRUT_BURY por dentro; sapata azul-marinho no ponto de entrada"""
    out = []
    for s in (-1, 1):
        pb = A0 + bu * (d * 0.5) + bn * (2.6 * s)
        top = Vector((pb.x, pb.y, G - 2.1))
        aim = A0 + bu * (d + 4.5) + bn * (2.4 * s)
        aim = Vector((aim.x, aim.y, G - 15.0))
        dv = (aim - top).normalized()
        hit = rock.ray_cast(top, dv, 60.0)
        entry = hit[0] if hit[0] is not None else aim
        foot = entry + dv * STRUT_BURY
        mb.beam(foot, top, 0.9, 0.9, WHITE, 0.0)
        mb.beam(entry - dv * 0.45, entry + dv * 0.35, 1.5, 1.5, NAVY, 0.0)
        mb.beam(Vector((pb.x, pb.y, G - 2.6)) + bu * 1.2, Vector((pb.x, pb.y, G - 2.6)) - bu * 1.2, 0.7, 0.7, NAVY, 0.0)
        out.append((tuple(foot), tuple(top)))
    STRUTS[kind] = out


def satellite(kind):
    seed = {"pad_sw": 6101, "pad_se": 6102}[kind]
    rng = random.Random(seed)
    (x, y, r), a0, a1, u = sat_frame(kind)
    name = {"pad_sw": "DB_Twr_SatSW", "pad_se": "DB_Twr_SatSE"}[kind]
    mb = K.CMB(name, COLL, detail="near")
    # o pilar de rocha vem PRIMEIRO (semente propria): a BVH dele assenta as escoras da ponte
    sat_rock(mb, random.Random(seed + 500), x, y, u)
    rock = BVHTree.FromBMesh(mb.bm)
    zf = G + 0.1                       # topo do calcamento (colisao em G)
    c = (x, y)
    th_open = math.degrees(math.atan2(a1[1] - y, a1[0] - x))
    half = math.degrees(2.0 * math.asin((L.SAT_BRIDGE_W / 2 + 1.2) / (2.0 * r)))
    # corpo da plataforma: faixa azul, fascia azul-marinho; topo do leito do calcamento (rejunte escuro) em G - 0,25
    lathe_pts(mb, c, [(0.3, G - 2.4, NAVY), (9.9, G - 2.4, NAVY), (10.9, G - 1.6, NAVY), (10.9, G - 0.75, BLUE),
                      (10.9, G - 0.25, NAVY), (9.3, G - 0.25, NAVY), (0.3, G - 0.25, NAVY)], 28)
    # coroamento branco sob o guarda-corpo (aberto na ponte)
    lathe_pts(mb, c, [(9.3, G - 0.3, WHITE), (10.95, G - 0.3, WHITE), (10.95, zf + 0.2, WHITE),
                      (9.3, zf + 0.2, WHITE)], 30, th_open + half, th_open + 360.0 - half)
    # calcamento em aneis + medalhao central (disco branco, anel azul, 4 setas azul-marinho)
    pave_ring(mb, x, y, 3.05, 9.3, G - 0.25, rng, ring_w=2.1, gap=0.2, h=0.35, m=PAVE)
    pave_ring(mb, x, y, 9.3, 10.9, G - 0.25, rng, th_open - half, th_open + half, ring_w=2.0, gap=0.2, h=0.35, m=PAVE)
    mb.cyl(2.35, 0.4, (x, y, zf - 0.2), m=WHITE, n=24, bevel=0.0)
    K.ring(mb, c, 2.35, 3.0, zf - 0.4, zf, BLUE, 24)
    ang0 = math.atan2(u[1], u[0])
    for i in range(4):
        a = ang0 + math.pi / 2 * i
        tip = (x + math.cos(a) * 2.2, y + math.sin(a) * 2.2)
        l1 = (x + math.cos(a + 0.42) * 0.9, y + math.sin(a + 0.42) * 0.9)
        l2 = (x + math.cos(a - 0.42) * 0.9, y + math.sin(a - 0.42) * 0.9)
        poly_prism(mb, [tip, l1, l2], zf - 0.1, zf + 0.04, NAVY)
    # ponte curta: laje, vigas de borda brancas (linha azul por fora), calcamento, guarda-corpo, escoras
    bd = Vector((a1[0] - a0[0], a1[1] - a0[1], 0.0))
    d = bd.length
    bu = bd / d
    bn = Vector((-bu.y, bu.x, 0.0))
    yaw = math.atan2(bu.y, bu.x)
    A0 = Vector((a0[0], a0[1], 0.0))
    xa, xb = -0.2, d + 1.6
    xt = d - 1.0                       # fim do calcamento da ponte (o anel de lajes da boca da plataforma continua)
    cm = A0 + bu * ((xa + xb) / 2)
    mb.box((xb - xa, 8.0, 1.75), (cm.x, cm.y, G - 2.0 + 0.875), (0, 0, yaw), NAVY, 0.0)
    for s in (-1, 1):
        q = A0 + bu * (d / 2) + bn * (4.6 * s)
        mb.box((d + 0.6, 1.4, 2.5), (q.x, q.y, G - 2.2 + 1.25), (0, 0, yaw), WHITE, 0.0)
        q2 = A0 + bu * (d / 2) + bn * (5.33 * s)
        mb.box((d + 0.6, 0.12, 0.6), (q2.x, q2.y, G - 1.1), (0, 0, yaw), BLUE, 0.0)
    # cabeceira do lado da ilha: soleira (cobre a ponta do caminho do terreno) + encontros laterais
    head_plate(mb, A0, bu, bn, yaw)
    head_wings(mb, A0, bu, bn, a0)
    # calcamento da ponte: comeca DEPOIS da soleira (nenhuma laje sob/sobre as do terreno)
    xx = HEAD_PLATE[1] + 0.05
    row = 0
    while xx < xt - 0.3:
        dep = min(2.0, xt - xx)
        cuts = [-3.9, -1.3, 1.3, 3.9] if row % 2 == 0 else [-3.9, 0.0, 3.9]
        for ya, yb in zip(cuts, cuts[1:]):
            q = A0 + bu * (xx + dep / 2) + bn * ((ya + yb) / 2)
            hh = 0.35 + rng.uniform(-0.03, 0.03)
            mb.box((dep - 0.2, yb - ya - 0.2, hh), (q.x, q.y, G - 0.25 + hh / 2), (0, 0, yaw + rng.uniform(-0.01, 0.01)),
                   PAVE, 0.0)
        xx += dep
        row += 1
    for s in (-1, 1):
        capsule_rail(mb, [A0 + bn * (4.6 * s), A0 + bu * d + bn * (4.6 * s)], zf, posts=False)
    # pilones das cabeceiras com lampiao (colisao propria: ficam na ponta das guardas); o pe entra no encontro/viga
    for xx in (0.0, d):
        for s in (-1, 1):
            q = A0 + bu * xx + bn * (4.6 * s)
            zb = G - 0.4
            mb.box((1.5, 1.5, zf + 3.5 - zb), (q.x, q.y, (zf + 3.5 + zb) / 2), (0, 0, yaw), WHITE, 0.08)
            mb.box((1.8, 1.8, 0.35), (q.x, q.y, zf + 3.5 + 0.175), (0, 0, yaw), BLUE, 0.06)
            mb.box((1.55, 0.12, 0.5), (q.x + bn.x * 0.72 * s, q.y + bn.y * 0.72 * s, zf + 1.4), (0, 0, yaw), NAVY, 0.0)
            capsule_lamp(mb, q.x, q.y, zf + 3.85, 0.95)
            col_box("DB_TwrSat", (1.5, 1.5, 4.2), (q.x, q.y, G + 2.0), (0, 0, yaw))
    # escoras sob a ponte: o pe entra >= STRUT_BURY na rocha da plataforma (medido na BVH do pilar)
    seat_struts(mb, rock, A0, bu, bn, d, kind)
    # guarda-corpo da plataforma: as mesmas linhas das guardas do db_col (16-gono r, aberto na ponte)
    pad = [(x + r * math.cos(t * math.pi / 8), y + r * math.sin(t * math.pi / 8)) for t in range(16)]

    P = sat_props(kind)
    tx, ty, _ = P["tower"]

    def keep_pad(px, py):
        # aberto na ponte e na torre-disco (o guarda-corpo morre no pedestal dela)
        return (math.hypot(px - a1[0], py - a1[1]) > L.SAT_BRIDGE_W / 2 + 1.2 and
                math.hypot(px - tx, py - ty) > SAT_TWR_R + 0.1)
    runs = _runs(DL.ccw(pad), keep_pad)
    if len(runs) > 1 and (runs[0][0] - runs[-1][-1]).length < 1.5:
        runs[0] = runs[-1] + runs[0]
        runs.pop()
    for run in runs:
        capsule_rail(mb, run, zf)
    # torre-disco na borda de fora, banco e luneta
    sat_tower(mb, tx, ty, u)
    b2x, b2y, db = P["bench"]
    bench(mb, b2x, b2y, zf, db)
    sx, sy, dt = P["scope"]
    telescope(mb, sx, sy, zf, dt)
    return mb.finish()


# ------------------------------------------------------------------ heliponto Capsule + aeronave estacionada
def aircraft(mb, F, hdg):
    fw = Vector((math.cos(hdg), math.sin(hdg), 0.0))
    zc = 3.45
    hull = [(0.06, -7.0), (0.9, -6.75), (1.6, -6.1), (2.05, -4.9), (2.3, -3.2), (2.35, -2.5), (2.35, 1.0),
            (2.25, 2.8), (1.95, 4.4), (1.5, 5.6), (0.95, 6.5), (0.45, 7.0), (0.06, 7.2)]
    hm = [NAVY, WHITE, WHITE, WHITE, NAVY, WHITE, WHITE, WHITE, WHITE, WHITE, BLUE, BLUE, WHITE]
    lathe_axis(mb, F.p(0, 0, zc), fw, hull, WHITE, n=22, mats=hm, sq=(1.0, 0.82))
    # canopi (bolha na frente, como a aeronave Capsule da concept)
    ellipsoid(mb, F.p(2.9, 0, zc + 1.35), (3.1, 1.75, 1.45), (0, 0, hdg), GLASS, sub=2)
    # asas curtas + motores nas pontas
    for s in (-1, 1):
        wing = [(1.0, 1.6 * s), (-3.0, 1.6 * s), (-4.2, 5.9 * s), (-2.3, 6.3 * s)]
        poly_prism(mb, [tuple(F.p(px, py, 0))[:2] for px, py in wing], F.o.z + 2.55, F.o.z + 3.1, WHITE)
        K.cyl_axis(mb, 0.66, 3.6, F.p(-3.1, 6.2 * s, 2.85), fw, BLUE, 14)
        K.cyl_axis(mb, 0.48, 0.4, F.p(-5.0, 6.2 * s, 2.85), fw, NAVY, 12)
        # estabilizadores horizontais
        stab = [(-5.2, 0.3 * s), (-6.9, 0.3 * s), (-7.5, 2.9 * s), (-6.5, 3.0 * s)]
        poly_prism(mb, [tuple(F.p(px, py, 0))[:2] for px, py in stab], F.o.z + 3.95, F.o.z + 4.3, WHITE)
        # trem de pouso principal
        p = F.p(-1.6, 1.9 * s, 0.0)
        mb.rod((p.x, p.y, F.o.z + 0.25), (p.x, p.y, F.o.z + 2.4), 0.2, NAVY, 6)
        mb.cyl(0.62, 0.25, (p.x, p.y, F.o.z + 0.125), m=NAVY, n=12, bevel=0.0)
    # deriva central azul
    fin = [(-3.8, 5.0), (-6.0, 8.0), (-7.4, 8.0), (-6.8, 3.9)]
    K.extrude_uz(mb, fin, Frame(F.o.x, F.o.y, F.o.z, hdg), -0.22, 0.22, BLUE)
    p = F.p(4.2, 0.0, 0.0)
    mb.rod((p.x, p.y, F.o.z + 0.25), (p.x, p.y, F.o.z + 2.0), 0.2, NAVY, 6)
    mb.cyl(0.55, 0.25, (p.x, p.y, F.o.z + 0.125), m=NAVY, n=12, bevel=0.0)
    # bocal traseiro
    K.cyl_axis(mb, 1.05, 0.8, F.p(-6.75, 0, zc), fw, NAVY, 16)
    K.cyl_axis(mb, 0.7, 0.3, F.p(-7.2, 0, zc), fw, CYAN, 12)


def aircraft_col(F, hdg):
    """colisao da aeronave justa ao visual (no referencial F: x para o nariz, y lateral, z acima do piso zf).
    Antes: 1 caixa 14,4 x 5 x 5,9 + 1 caixa de asa 5 x 13 retangular (sobrava 1,5..4,6 alem do casco e das asas na
    altura do peito). Agora 15 caixas que seguem o casco, o canopi, a deriva, as asas (enflechadas, afinando para a
    ponta), os motores e os estabilizadores. Sem colisao abaixo de ~2,0: o trem de pouso e o vao sob a barriga ficam
    livres (as pernas do jogador passam por baixo da barriga, o tronco bate na cintura do casco; ninguem cabe sob ela)."""
    def fbox(x0, x1, hw, z0, z1):
        col_box("DB_TwrPad", (x1 - x0, 2.0 * hw, z1 - z0), F.p((x0 + x1) / 2, 0.0, (z0 + z1) / 2), (0, 0, hdg))
    # casco (secao eliptica: eixo z 3,45, meia-largura r(x) ate 2,35, meia-altura 0,82 r): cintura 2,3..4,3 (casco
    #   r 1,90..2,35..2,11) e dorso 4,3..5,4 (r 2,11..0; topo do casco 5,38 = topo da caixa: quem pula em cima pisa
    #   no casco)
    fbox(-4.9, 4.4, 2.3, 2.3, 4.3)
    fbox(-4.9, 4.4, 1.75, 4.3, 5.4)
    # nariz: x 4,4..5,6 (r 1,95..1,5; casco 1,85..5,05) e ponta x 5,6..6,9 (r 1,5..0,45; casco 2,22..4,68)
    fbox(4.4, 5.6, 1.75, 2.0, 5.1)
    fbox(5.6, 6.9, 1.1, 2.5, 4.4)
    # cauda: x -6,1..-4,9 (r 1,6..2,05; casco 1,77..5,13) e bocal x -7,2..-6,1 (r 1,6..0,9, bocal r 1,05: 2,4..4,5)
    fbox(-6.1, -4.9, 2.0, 2.0, 5.1)
    fbox(-7.2, -6.1, 1.3, 2.4, 4.6)
    # canopi (elipsoide centro x 2,9, z 4,8, raios 3,1 x 1,75 x 1,45: topo 6,25): x 1,0..5,4 (topo do canopi
    #   5,66..6,25), meia-largura 1,3, a partir do topo do nariz (5,1)
    fbox(1.0, 5.4, 1.3, 5.1, 6.2)
    # deriva (x -7,4..-3,8, z 3,9..8,0, espessura 0,44): caixa fina no meio da flecha, acima da cauda
    col_box("DB_TwrPad", (1.9, 0.5, 2.9), F.p(-5.95, 0.0, 5.1 + 1.45), (0, 0, hdg))
    # estabilizadores horizontais (x -5,2..-7,5, y ate +-3,0, z 3,95..4,3 = altura da cabeca): 1 laje fina
    fbox(-7.3, -5.6, 2.9, 3.9, 4.35)
    # asas: caixas finas NA COTA da asa (2,5..3,15; asa 2,55..3,1) ao longo da linha de meia-corda, da raiz (-1,0; 1,6)
    #   ate a ponta (-3,25; 6,3), em 2 trechos que afinam com a corda (perpendicular a linha: 3,6 na raiz, 2,7 no
    #   meio, 1,7 na ponta -> caixas de 3,45 e 2,3). Motores: caixa propria (r 0,66, x -4,9..-1,3; o bocal r 0,48
    #   sobra atras), secao 1,16 (quase inscrita no cilindro: o canto nao sobra no ar)
    sw = math.atan2(4.5, -2.25)              # rumo da linha de meia-corda no referencial da aeronave
    dl = Vector((math.cos(sw), math.sin(sw)))
    t1 = (6.3 - 1.6) / dl.y
    for s in (-1, 1):
        for f0, wd in ((0.0, 3.45), (0.5, 2.3)):
            tm = t1 * (f0 + 0.25)
            cx, cy = -1.0 + dl.x * tm, (1.6 + dl.y * tm) * s
            col_box("DB_TwrPad", (t1 / 2 + 0.02, wd, 0.65), F.p(cx, cy, 2.825), (0, 0, hdg + sw * s))
        col_box("DB_TwrPad", (3.6, 1.16, 1.16), F.p(-3.1, 6.2 * s, 2.85), (0, 0, hdg))      # nacela x -4,9..-1,3


def landing_pad():
    x, y, r = LANDING
    z = G
    zf = G + 0.1
    c = (x, y)
    mb = K.CMB("DB_Twr_LandingPad", COLL, detail="near")
    # laje: borda branca com fascia azul-marinho, miolo azul-ardosia (topo zf = G + 0,1: colisao do chao em G)
    lathe_pts(mb, c, [(0.3, z - 0.6, PAD), (12.2, z - 0.6, NAVY), (12.2, z - 0.1, WHITE), (11.9, zf, WHITE),
                      (10.7, zf, PAD), (0.3, zf, PAD)], 40)
    # marcacoes (sem texto): anel branco, anel azul, disco central, 4 chevrons
    K.ring(mb, c, 9.2, 9.8, zf - 0.05, zf + 0.04, WHITE, 40)
    K.ring(mb, c, 5.6, 6.2, zf - 0.05, zf + 0.04, BLUE, 32)
    mb.cyl(1.4, 0.09, (x, y, zf - 0.005), m=WHITE, n=20, bevel=0.0)
    for i in range(4):
        a = (45.0 + 90.0 * i) * D2R
        for s in (-1, 1):
            p0 = Vector((x + math.cos(a) * 7.1, y + math.sin(a) * 7.1, zf))
            b = a + s * 0.19
            p1 = Vector((x + math.cos(b) * 8.9, y + math.sin(b) * 8.9, zf))
            mid = (p0 + p1) / 2
            ln = (p1 - p0).length
            mb.box((ln + 0.3, 0.6, 0.09), (mid.x, mid.y, zf - 0.005), (0, 0, math.atan2(p1.y - p0.y, p1.x - p0.x)),
                   WHITE, 0.0)
    # luzes de pouso na borda: lente redonda RASA (cupula baixa, topo zf + 0,14) num aro azul-marinho rente ao
    #   piso - le como lampada de pista, nao como gema
    for i in range(12):
        a = (15.0 + 30.0 * i) * D2R
        px, py = x + 11.3 * math.cos(a), y + 11.3 * math.sin(a)
        mb.cyl(0.55, 0.14, (px, py, zf + 0.01), m=NAVY, n=12, bevel=0.0)
        DL.dome(mb, (px, py), 0.36, zf, CYAN, n=12, rings=3, squash=0.38)
    # 2 postes de holofote atras da aeronave (lado oposto a trilha)
    posts = []
    for hd in (150.0, 222.0):
        a = hd * D2R
        px, py = x + 13.4 * math.cos(a), y + 13.4 * math.sin(a)
        zg = L.zone_of(px, py)
        mb.cyl(0.8, 0.9, (px, py, zg + 0.45), m=NAVY, n=10, bevel=0.0)
        mb.cyl(0.32, 7.6, (px, py, zg + 0.9 + 3.8), m=WHITE, n=10, bevel=0.0)
        hv = Vector((x - px, y - py, 0.0)).normalized()
        yaw = math.atan2(hv.y, hv.x)
        mb.box((1.5, 0.45, 0.45), tuple(Vector((px, py, zg + 8.3)) + hv * 0.55), (0, 0, yaw), NAVY, 0.0)
        head = Vector((px, py, zg + 8.3)) + hv * 1.35
        tilt = 28.0 * D2R
        mb.box((1.0, 1.9, 1.2), tuple(head), (0, tilt, yaw), WHITE, 0.05)
        fdir = Vector((hv.x * math.cos(tilt), hv.y * math.cos(tilt), -math.sin(tilt)))
        mb.box((0.14, 1.6, 0.95), tuple(head + fdir * 0.52), (0, tilt, yaw), CYAN, 0.0)
        lz = Vector((hv.x * math.sin(tilt), hv.y * math.sin(tilt), math.cos(tilt)))
        mb.box((1.2, 2.1, 0.22), tuple(head + lz * 0.71), (0, tilt, yaw), BLUE, 0.0)
        col_box("DB_TwrPad", (0.9, 0.9, 8.6), (px, py, zg + 4.3), (0, 0, a))
        posts.append(head)
    # aeronave-capsula estacionada (nariz para a trilha)
    hdg = PAD_HDG
    fx, fy = x - math.cos(hdg) * 0.6, y - math.sin(hdg) * 0.6
    F = Frame(fx, fy, zf, hdg)
    aircraft(mb, F, hdg)
    ob = mb.finish()
    aircraft_col(F, hdg)
    light("L_DBTwr_PadFlood", "POINT", tuple(posts[0] + Vector((0, 0, -1.2))), 260, (0.55, 0.88, 1.0), 0.8)
    return ob


# ------------------------------------------------------------------ build
def _stats():
    import os
    if not os.environ.get("DBTWR_STATS"):
        return
    for ob in bpy.data.objects:
        if ob.type != "MESH" or not ob.name.startswith(("DB_Twr_", "VFX_DBTWR_")):
            continue
        per = {}
        for p in ob.data.polygons:
            m = ob.data.materials[p.material_index].name
            per[m] = per.get(m, 0) + len(p.vertices) - 2
        print("TWRSTATS %s %d %s" % (ob.name, sum(per.values()), sorted(per.items(), key=lambda t: -t[1])))


def _audit():
    """DBTWR_AUDIT=1: raios horizontais contra o visual e contra a colisao propria (aeronave e torres-disco)"""
    import os
    if not os.environ.get("DBTWR_AUDIT"):
        return
    bpy.context.view_layer.update()

    def bvh_of(obs):
        verts, polys = [], []
        for o in obs:
            mw = o.matrix_world
            b0 = len(verts)
            verts += [mw @ v.co for v in o.data.vertices]
            polys += [[b0 + i for i in p.vertices] for p in o.data.polygons]
        return BVHTree.FromPolygons(verts, polys)

    def cmp(tag, vis, col, cx, cy, zs, r0=11.0, n=16):
        for zz in zs:
            worst = short = 0.0
            rows = []
            for i in range(n):
                a = 2 * math.pi * (i + 0.19) / n      # fora das arestas dos tornos (raio rente a vertice falha)
                d = Vector((-math.cos(a), -math.sin(a), 0.0))
                o = Vector((cx + math.cos(a) * r0, cy + math.sin(a) * r0, zz))
                hv = vis.ray_cast(o, d, r0)[3]
                hc = col.ray_cast(o, d, r0)[3]
                hv = r0 if hv is None else hv
                hc = r0 if hc is None else hc
                worst = max(worst, hv - hc)
                short = max(short, hc - hv)
                rows.append("%d:%.1f/%.1f" % (round(math.degrees(a)), hc, hv))
            print("TWRAUDIT %s z=%.1f col_antes_do_visual=%.2f visual_antes_da_col=%.2f  %s" %
                  (tag, zz, worst, short, " ".join(rows)))
    x, y, r = LANDING
    hx, hy = math.cos(PAD_HDG), math.sin(PAD_HDG)
    fx, fy = x - hx * 0.6, y - hy * 0.6
    vis = bvh_of([bpy.data.objects["DB_Twr_LandingPad"]])
    col = bvh_of([o for o in bpy.data.objects if o.name.startswith("COL_DB_TwrPad")])
    cmp("aeronave", vis, col, fx, fy, [G + 0.1 + h for h in (1.0, 2.0, 2.4, 2.85, 3.45, 4.0, 4.6, 5.0, 5.8, 6.8)])
    for kind, nm in (("pad_sw", "DB_Twr_SatSW"), ("pad_se", "DB_Twr_SatSE")):
        tx, ty, _ = sat_props(kind)["tower"]
        vis = bvh_of([bpy.data.objects[nm]])
        col = bvh_of([o for o in bpy.data.objects if o.name.startswith("COL_DB_TwrSat")])
        cmp("torre_%s" % kind, vis, col, tx, ty, (G + 2.0, G + 6.0), r0=4.0, n=8)
    for nm in ("DB_Twr_Comm", "DB_Twr_Lookout", "DB_Twr_SatSW", "DB_Twr_SatSE"):
        ob = bpy.data.objects[nm]
        print("TWRAUDIT topo %s = %.2f" % (nm, max((ob.matrix_world @ v.co).z for v in ob.data.vertices)))


def build():
    pp = ports()
    comm_tower(pp["comm"])
    lookout_tower(pp["lookout"])
    energy_station()
    satellite("pad_sw")
    satellite("pad_se")
    landing_pad()
    _stats()
    _audit()
