# ds_exit - SAIDA da Ilha 4 (DEMON SLAYER) para ONE PIECE (onda 1c; PLANO_DS secoes 3.5, 4.2 e 12; PROMPT_USUARIO
# secao 14). Substitui ds_blockout.exit_. Prefixo DS_Exit_, colecao 08_NEXT_ISLAND. Usa as pecas do ds_entry (mesma
# familia: torii, guarda-corpo koran, giboshi, andon, ishigaki, coluna de rocha) para a saida ler como a mesma ilha.
# A narrativa (densidade BAIXA, "promessa"):
#   CAMINHO de lajes (sobre berco escuro) que sai do patio do carvao por tras da oficina, curva para o oeste e endireita
#   no eixo do torii; 3 POSTES-LANTERNA nos nos (as 3 luzes da saida) -> TORII DE SAIDA (o 2o e ultimo, igual ao da
#   entrada) -> ISLAND_EXIT -> PONTE REAL de 56 a 80,2 (mesma madeira e guarda-corpo da chegada, apoiada no encontro de
#   ishigaki do nariz NO, numa coluna de rocha no meio com cavalete e maos-francesas, e no muro da cabeceira) ->
#   CABECEIRA de pedra (ishigaki em talude com quinas sangi-zumi sobre a coluna de rocha que some nas nuvens; 39 de largo
#   onde o portao assenta, 33 atras dele; capa de pedra, lajes, guarda-corpo koran) -> PORTAO ONE PIECE aprovado
#   (il_gate_op, posto pelo ds_core em u 68: aqui NADA dele e redesenhado, so o chao que o apoia, sem laje por baixo) ->
#   BORDA DA ANCORA (u 86, ceu aberto, rumo 105 local = 15 graus do radial lobby -> fora) com os 2 postes-ponta onde a
#   ponte da One Piece encosta e a GUARDA PROVISORIA (shimenawa de palha com shide entre os postes; objeto proprio
#   DS_Exit_AnchorGuard, next_island_guard=True; a colisao COL_DSAnchorGuard_* e do ds_col).
# Colisao: caminho (piso T4), ponte, cabeceira, guardas e a guarda da ancora sao do ds_col (congelado). Aqui so o torii
# e os postes-lanterna.
# ONDA 3b (ds_props): poste-lanterna = ds_kit.lantern_post; guarda-corpo = ds_entry.koran, que agora e o railing do
# kit (com inclinacao, giboshi nos nos); mesmas posicoes, rotas e nomes de luz.
import math, random
from mathutils import Vector
from mathutils.bvhtree import BVHTree
import bpy
import ds_lib as DL
from ds_lib import MB, col_box, light, Frame, ccw
import ds_layout as L
import ds_entry as E
import ds_kit as K
from ds_entry import fbox, fbeam, loft, lathe, WD, WM, ST, STD, STP, CLM, BRZ, FERN

T4 = L.T4
C = "08_NEXT_ISLAND"
UX, UY = L.exit_dir()
ANG = math.atan2(UY, UX)
FX = Frame(L.EXIT_START[0], L.EXIT_START[1], 0.0, ANG)  # u ao longo da ponte (0 = ISLAND_EXIT), v = esquerda
BL = L.EXIT_BRIDGE_LEN                                  # 56
PU0, PU1 = BL, BL + L.PIER[1]                           # cabeceira: u 56..86
GATE_U = BL + L.GATE_OP_OFF                             # 68: eixo do portao One Piece (ds_core)
ANCHOR_U = BL + L.ANCHOR_OP_OFF                         # 86: ISLAND_NEXT_ANCHOR_OnePiece
WIDE_U, WIDE_V, NARROW_V = 77.0, 19.5, 16.4             # cabeceira em cruz: larga onde o portao assenta (+-18)
PAVE_Z = T4 + 0.15                                      # topo das lajes (= piso do portao, 80,35)
COPE_Z = T4 + 0.42                                      # topo da capa de pedra (onde o guarda-corpo pousa)
MID_U = BL / 2                                          # coluna de rocha no meio da ponte
SEA = E.SEA

# caminho de saida (visual): sai do patio do carvao, curva por tras da oficina e ENDIREITA no eixo do torii (rumo 105)
PATH = [(-104.0, 452.0), (-112.5, 478.0), (-114.0, 503.0), (-110.5, 530.0), (-103.5, 552.0), (-96.5, 565.0),
        (-91.8, 575.0), (-94.0, 586.0), (-95.4, 593.6)]


def zf_b(u):
    return T4 + 0.1


def P(u, v, z=0.0):
    return FX.p(u, v, z)


def PW(u, v):
    p = FX.p(u, v, 0.0)
    return (p.x, p.y)


# ================================================================== ponte de 56 (mesma familia da chegada)
def exit_bridge(mb, mr):
    E.sides(mb, FX, -1.0, BL + 0.8, zf_b)
    E.deck(mb, FX, -0.6, BL + 0.2, zf_b)
    for s in (-1, 1):
        E.koran(mb, FX, 0.6, BL + 0.6, s * E.RAIL_V, zf_b, nodes=(MID_U,))
    E._bents(mb, FX, zf_b, MID_U, zf_b(MID_U) - 10.5, struts=(-1, 1), strut_reach=12.5)
    E.rock_column(mr, FX, MID_U, 0.0, zf_b(MID_U) - 10.5, 6.2, 11.8, random.Random(51))
    # encontro de ishigaki no nariz NO da ilha (u -8,5..-0,4), aberto para o lado da ilha
    seat = zf_b(0) - E.PLANK_T - 1.0
    abut = [PW(u, v) for u, v in ((-0.4, -10.9), (-0.4, 10.9), (-9.0, 10.9), (-9.0, -10.9))]
    o = Vector(PW(-9.0, 0.0))
    E.ishigaki(mr, abut, seat - 0.5, seat - 13.0, random.Random(52),
               open_test=lambda x, y: (Vector((x, y)) - o).length < 2.0)
    fbox(mr, FX, -9.0, -11.0, seat - 0.55, 0.2, 11.0, seat, ST, 0.08)


# ================================================================== cabeceira (30 x 30 funcional; em cruz no visual)
def pier_poly():
    return [PW(u, v) for u, v in ((PU0, -WIDE_V), (WIDE_U, -WIDE_V), (WIDE_U, -NARROW_V), (PU1, -NARROW_V),
                                  (PU1, NARROW_V), (WIDE_U, NARROW_V), (WIDE_U, WIDE_V), (PU0, WIDE_V))]


def _gate_bvh():
    """BVH do portao aprovado (so para NAO por laje nem capa onde ele assenta)"""
    verts, polys = [], []
    for o in bpy.data.objects:
        if o.type != "MESH" or not o.name.startswith("GATE_OnePiece"):
            continue
        mw = o.matrix_world
        base = len(verts)
        verts += [mw @ v.co for v in o.data.vertices]
        polys += [[base + i for i in p.vertices] for p in o.data.polygons]
    return BVHTree.FromPolygons(verts, polys) if polys else None


def _gate_at(bvh, u, v, hu, hv):
    """o portao ocupa o retangulo (u +- hu, v +- hv) perto do piso?"""
    if bvh is None:
        return False
    for du, dv in ((0, 0), (-hu, -hv), (hu, -hv), (hu, hv), (-hu, hv), (0, -hv), (0, hv), (-hu, 0), (hu, 0)):
        p = P(u + du, v + dv, T4 + 2.6)
        hit = bvh.ray_cast(p, Vector((0, 0, -1)), 3.6)
        if hit[0] is not None:
            return True
    return False


def pier(mb, mr):
    rng = random.Random(5201)
    poly = pier_poly()
    E.ishigaki(mr, poly, T4 - 0.15, T4 - 12.5, random.Random(53), depth=1.1, ls_range=(2.6, 4.4), h_range=(1.8, 2.6))
    E.rock_column(mr, FX, 71.0, 0.0, T4 - 12.3, 22.5, 28.0, random.Random(54), flare=0.22)
    bvh = _gate_bvh()
    # capa de pedra (kasa-ishi) na borda: pedras de 2,2..3,4 com junta; aberta no vao da ponte (frente) e da ancora
    edges = [((PU0, -WIDE_V), (WIDE_U, -WIDE_V)), ((WIDE_U, -WIDE_V), (WIDE_U, -NARROW_V)),
             ((WIDE_U, -NARROW_V), (PU1, -NARROW_V)), ((PU1, -NARROW_V), (PU1, NARROW_V)),
             ((PU1, NARROW_V), (WIDE_U, NARROW_V)), ((WIDE_U, NARROW_V), (WIDE_U, WIDE_V)),
             ((WIDE_U, WIDE_V), (PU0, WIDE_V)), ((PU0, WIDE_V), (PU0, -WIDE_V))]
    for (ua, va), (ub, vb) in edges:
        ln = math.hypot(ub - ua, vb - va)
        du, dv = (ub - ua) / ln, (vb - va) / ln
        nu, nv = dv, -du                                  # para fora (contorno anti-horario em (u, v))
        t = 0.0
        while t < ln - 0.2:
            ls = min(rng.uniform(2.2, 3.4), ln - t)
            if ln - t - ls < 1.0:
                ls = ln - t
            tm = t + ls / 2
            cu, cv = ua + du * tm - nu * 0.6, va + dv * tm - nv * 0.6
            t += ls
            if abs(cu - PU0) < 1.0 and abs(cv) < 10.1:
                continue                                  # vao da ponte
            if abs(cu - PU1) < 1.0 and abs(cv) < 10.1:
                continue                                  # vao da ancora (a ponte da One Piece encosta aqui)
            if _gate_at(bvh, cu, cv, abs(du) * (ls / 2 - 0.2) + abs(nu) * 0.6, abs(dv) * (ls / 2 - 0.2) + abs(nv) * 0.6):
                continue
            mb.box((ls - 0.16, 1.2, 0.58), P(cu, cv, COPE_Z - 0.29), FX.r(0, 0, math.atan2(dv, du)), ST, 0.08)
    # soleiras nos vaos (pedra comprida, rente as lajes)
    for u in (PU0 + 0.6, PU1 - 0.6):
        fbox(mb, FX, u - 0.6, -9.9, PAVE_Z - 0.4, u + 0.6, 9.9, PAVE_Z, STD, 0.06)
    # lajes (grade com fiadas desencontradas), fora do portao
    u = PU0 + 1.25
    row = 0
    while u < PU1 - 1.3:
        h = rng.choice((1.6, 2.0, 2.4))
        h = min(h, PU1 - 1.25 - u)
        vmax = (WIDE_V if u + h <= WIDE_U else NARROW_V) - 1.25
        v = -vmax + (rng.uniform(0.0, 1.0) if row % 2 else 0.0)
        while v < vmax - 0.3:
            w = min(rng.uniform(2.0, 3.4), vmax - v)
            cu, cv = u + h / 2, v + w / 2
            if not _gate_at(bvh, cu, cv, h / 2, w / 2) and w > 0.6 and h > 0.6:
                mb.box((h - 0.18, w - 0.18, 0.4), P(cu, cv, PAVE_Z - 0.2), FX.r(), STP, 0.06)
            v += w
        u += h
        row += 1
    # guarda-corpo koran na capa: frente (dos 2 lados da ponte), lados de tras do portao, ombros da ancora
    def run(a, b, **kw):
        du, dv = b[0] - a[0], b[1] - a[1]
        ln = math.hypot(du, dv)
        F2 = Frame(*P(a[0], a[1])[:2], 0.0, ANG + math.atan2(dv, du))
        E.koran(mb, F2, 0.0, ln, 0.0, lambda uu: COPE_Z - 0.38, **kw)
    for s in (-1, 1):
        run((PU0 + 0.6, s * E.RAIL_V), (PU0 + 0.6, s * (WIDE_V - 0.6)), ends=(False, True))
        run((WIDE_U + 0.6, s * (NARROW_V - 0.6)), (PU1 - 0.6, s * (NARROW_V - 0.6)), ends=(True, False))
        run((PU1 - 0.6, s * (NARROW_V - 0.6)), (PU1 - 0.6, s * 10.1), ends=(True, True))


# ================================================================== guarda provisoria da ancora (shimenawa)
def anchor_guard():
    """corda de palha (shimenawa) torcida entre os 2 postes-ponta, com 3 shide de papel e 2 borlas: 'passagem ainda
    fechada'. Objeto proprio (next_island_guard=True): sai junto com COL_DSAnchorGuard_* quando a ponte da One Piece
    encostar"""
    mb = MB("DS_Exit_AnchorGuard", C, random.Random(5301), detail="near")
    u = PU1 - 0.6
    z0 = COPE_Z + 2.7
    sag = 1.1
    pts = []
    n = 16
    for i in range(n + 1):
        t = i / n
        v = -9.7 + 19.4 * t
        pts.append(P(u, v, z0 - sag * (1 - (2 * t - 1) ** 2)))
    for k in range(2):                                   # 2 cordoes torcidos, mais grossos no meio (shimenawa)
        rings = []
        for i, p in enumerate(pts):
            t = i / n
            r = 0.17 + 0.17 * math.sin(math.pi * t)
            a = k * math.pi + i * 1.1
            c = p + Vector((0, 0, r * 0.62 * math.sin(a))) + Vector((UX, UY, 0)) * r * 0.62 * math.cos(a)
            tan = (pts[min(i + 1, n)] - pts[max(i - 1, 0)]).normalized()
            sv = tan.cross(Vector((0, 0, 1))).normalized()
            up = sv.cross(tan).normalized()
            rings.append([tuple(c + (sv * math.cos(b) + up * math.sin(b)) * r) for b in
                          (2 * math.pi * j / 6 for j in range(6))])
        loft(mb, rings, "Bamboo_DS_Dry")
    for i, t in enumerate((0.25, 0.5, 0.75)):           # shide (papel em zigue-zague)
        v = -9.7 + 19.4 * t
        zt = z0 - sag * (1 - (2 * t - 1) ** 2) - 0.2
        for j in range(4):
            dv = 0.22 if j % 2 == 0 else -0.22
            mb.box((0.04, 0.5, 0.42), P(u + 0.05, v + dv, zt - 0.25 - j * 0.42), FX.r(0, 0, 0), "Plaster_DS_Kura", 0.0)
    for s in (-1, 1):                                    # borlas de palha junto aos postes
        p = P(u, s * 8.6, z0 - 0.35)
        lathe(mb, (p.x, p.y, p.z - 1.3), [(0.0, 0.0), (0.34, 0.12), (0.28, 0.9), (0.16, 1.3)], "Bamboo_DS_Dry", 8)
    ob = mb.finish()
    if ob is not None:
        ob["next_island_guard"] = True
        ob["note"] = ("PROVISORIO: shimenawa entre os postes-ponta da ancora One Piece; sai junto com COL_DSAnchorGuard_* "
                      "quando a ponte da One Piece encostar")
    return ob


# ================================================================== caminho de saida + postes-lanterna
def _path_frames(pts, step=0.25):
    """amostra a polilinha: (s, x, y, dx, dy)"""
    out = []
    s = 0.0
    for a, b in zip(pts, pts[1:]):
        dx, dy = b[0] - a[0], b[1] - a[1]
        ln = math.hypot(dx, dy)
        k = max(1, int(ln / step))
        for i in range(k):
            t = i / k
            out.append((s + ln * t, a[0] + dx * t, a[1] + dy * t, dx / ln, dy / ln))
        s += ln
    out.append((s, pts[-1][0], pts[-1][1], out[-1][3], out[-1][4]))
    return out


def _width(s, total):
    """meia-largura: 2,6 no caminho, abre para 4,6 na aproximacao do torii e da ponte"""
    t = max(0.0, min(1.0, (s - (total - 30.0)) / 14.0))
    return 2.6 + 2.0 * t * t * (3 - 2 * t)


def _rects_hit(r, placed):
    """SAT entre retangulos (4 cantos)"""
    for q in placed:
        if abs(q[4][0] - r[4][0]) > 6 or abs(q[4][1] - r[4][1]) > 6:
            continue
        sep = False
        for poly in (r[:4], q[:4]):
            for i in range(4):
                a, b = poly[i], poly[(i + 1) % 4]
                nx, ny = b[1] - a[1], a[0] - b[0]
                pa = [nx * p[0] + ny * p[1] for p in r[:4]]
                pb = [nx * p[0] + ny * p[1] for p in q[:4]]
                if max(pa) <= min(pb) or max(pb) <= min(pa):
                    sep = True
                    break
            if sep:
                break
        if not sep:
            return True
    return False


def _corridor_fill(mb):
    """o ds_terrain (onda 1a) deixa SEM pele (leito 0,5 abaixo) a faixa de meia-largura 5,2 em volta de L.EXIT_PATH,
    para o caminho de saida. Aqui ela vira o CAMINHO DE TERRA batida: enchimento ate a cota do piso, no MESMO material
    da pele vizinha (Dirt_DS_Dark no terraco da forja, Dirt_DS no ExitLand: no Roblox a cor e a mesma -> a costura com
    a pele nao aparece), com as lajes por cima"""
    fr = _path_frames(L.EXIT_PATH, 1.0)
    hw = 5.25
    secs = []
    for s_, x, y, dx, dy in fr[::2] + [fr[-1]]:
        secs.append(((x - dy * hw, y + dx * hw), (x + dy * hw, y - dx * hw), (x, y)))
    for a, b in zip(secs, secs[1:]):
        cx, cy = (a[2][0] + b[2][0]) / 2, (a[2][1] + b[2][1]) / 2
        m = "Dirt_DS_Dark" if L.floor_name(cx, cy) == "Forge" else "Dirt_DS"
        mb.prism(ccw([a[0], b[0], b[1], a[1]]), T4 - 0.62, T4, m, tint=0.0)
    for (s_, x, y, dx, dy), sg in ((fr[0], -1.0), (fr[-1], 1.0)):          # pontas redondas (o campo e uma capsula)
        a0 = math.atan2(dy, dx)
        pts = [(x, y)] + [(x + hw * math.cos(a0 + sg * (math.pi / 2 - math.pi * k / 8)),
                           y + hw * math.sin(a0 + sg * (math.pi / 2 - math.pi * k / 8))) for k in range(9)]
        m = "Dirt_DS_Dark" if L.floor_name(x, y) == "Forge" else "Dirt_DS"
        mb.prism(ccw(pts), T4 - 0.62, T4, m, tint=0.0)


def exit_path():
    rng = random.Random(5401)
    mb = MB("DS_Exit_Path", C, rng, detail="near")
    fr = _path_frames(PATH)
    total = fr[-1][0]
    terrain = bpy.data.objects.get("DS_Ter_Ground") is not None
    if terrain:
        _corridor_fill(mb)
        top = T4 + 0.14                                    # lajes 0,14 acima do piso, junta = terra (como o ds_terrain)
    else:
        # terreno em blockout (estudio da zona): berco escuro proprio sob as lajes
        left, right = [], []
        for s, x, y, dx, dy in fr[::8] + [fr[-1]]:
            hw = _width(s, total) + 0.35
            left.append((x - dy * hw, y + dx * hw))
            right.append((x + dy * hw, y - dx * hw))
        mb.prism(ccw(left + list(reversed(right))), T4 + 0.04, T4 + 0.12, STD)
        top = T4 + 0.22
    # lajes em fiadas ao longo do caminho (2 a 3 por fiada), sem sobrepor nas curvas
    placed = []
    s = 0.6
    idx = 0
    while s < total - 0.8:
        while idx < len(fr) - 1 and fr[idx + 1][0] < s:
            idx += 1
        _, x, y, dx, dy = fr[idx]
        hl = rng.uniform(1.3, 2.0)
        hw = _width(s, total)
        n = 2 if hw < 3.2 else 3
        cuts = sorted([-hw] + [-hw + 2 * hw * (k + rng.uniform(0.3, 0.7)) / n for k in range(n - 1)] + [hw])
        for va, vb in zip(cuts, cuts[1:]):
            vm = (va + vb) / 2
            w = vb - va - 0.18
            l = hl - 0.18
            cx, cy = x + dx * hl / 2 - dy * vm, y + dy * hl / 2 + dx * vm
            cr = [(cx + dx * a * l / 2 - dy * b * w / 2, cy + dy * a * l / 2 + dx * b * w / 2)
                  for a, b in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
            r = cr + [(cx, cy)]
            if _rects_hit(r, placed):
                continue
            placed.append(r)
            mb.box((l, w, 0.4), (cx, cy, top - 0.2), (0, 0, math.atan2(dy, dx) + rng.uniform(-0.03, 0.03)), STP, 0.0)
        s += hl
    # 3 postes-lanterna nos nos (as 3 luzes da saida): saida do patio do carvao e curva por tras da oficina (lado
    # oeste, borda do vazio) e o ultimo antes do torii do lado leste (o andador do QA passa pelo oeste ali)
    for i, (sl, side) in enumerate(((14.0, 1), (70.0, 1), (total - 30.0, -1))):
        k = min(range(len(fr)), key=lambda j: abs(fr[j][0] - sl))
        _, x, y, dx, dy = fr[k]
        off = (_width(sl, total) + 2.2) * side
        lx, ly = x - dy * off, y + dx * off
        lamp_post(mb, lx, ly, T4, math.atan2(dy, dx), "L_DSProp_Lamp_Exit_%d" % i, side)
    mb.finish()


def lamp_post(mb, x, y, z, rot, light_name, side=1):
    """poste-lanterna de caminho = ds_kit.lantern_post (pedra-base, poste chanfrado com chapeu, braco com mao-francesa
    e caixa de papel pendurada), com o braco virado PARA o caminho (rot = rumo do caminho; side = lado do poste)"""
    arm = rot + math.pi / 2 + (math.pi if side > 0 else 0.0)
    old = (K.MIN_BEVEL, K.MIN_BEVEL_SIZE)
    K.MIN_BEVEL, K.MIN_BEVEL_SIZE = 0.09, 0.5               # sem chanfro na pedra-base e no poste (orcamento)
    try:
        K.lantern_post(mb, Frame(x, y, z - 0.06, arm - math.pi / 2), 8.6, 1.9, light_name, 140.0)
    finally:
        K.MIN_BEVEL, K.MIN_BEVEL_SIZE = old
    col_box("DS_ExitLamp", (0.9, 0.9, 8.6), (x, y, z + 4.3))


def vegetation():
    rng = random.Random(5501)
    mv = MB("DS_Exit_Ferns", C, rng, detail="near")
    seat = zf_b(0) - E.PLANK_T - 1.0
    for u, v, z, s in ((-2.0, -10.4, seat, 0.9), (-4.5, 10.2, seat, 1.05), (MID_U + 2.5, -9.8, zf_b(0) - 10.5, 0.9),
                       (MID_U - 2.0, 10.0, zf_b(0) - 10.5, 0.8)):
        p = P(u, v)
        E.fern(mv, p.x, p.y, z, s, rng)
    mv.finish()


# ================================================================== cameras de estudio
def _c(a, b, lens):
    return (tuple(round(c, 2) for c in a), tuple(round(c, 2) for c in b), lens)


def _p(u, v, z):
    return tuple(P(u, v, z))


CAMS = {
    "CAM_DSExit_Path": _c((-120.0, 470.0, T4 + 5.5), (-104.0, 560.0, T4 + 4.0), 22),
    "CAM_DSExit_Torii": _c((-90.5, 566.0, T4 + 5.5), (-94.5, 590.0, T4 + 11.0), 22),
    "CAM_DSExit_Bridge": _c(_p(-14.0, 2.0, T4 + 5.5), _p(GATE_U, 0.0, T4 + 10.0), 22),
    "CAM_DSExit_SideL": _c(_p(40.0, 90.0, T4 + 8.0), _p(44.0, 0.0, T4 - 10.0), 24),
    "CAM_DSExit_SideR": _c(_p(52.0, -92.0, T4 + 14.0), _p(50.0, 0.0, T4 - 12.0), 24),
    "CAM_DSExit_Under": _c(_p(30.0, -40.0, T4 - 34.0), _p(50.0, 0.0, T4 - 6.0), 22),
    "CAM_DSExit_PierTop": _c(_p(50.0, -14.0, T4 + 18.0), _p(78.0, 0.0, T4), 24),
    "CAM_DSExit_Anchor": _c(_p(78.0, -6.0, T4 + 5.5), _p(PU1, 0.0, T4 + 2.5), 26),
    "CAM_DSExit_AnchorOut": _c(_p(PU1 + 30.0, 10.0, T4 + 9.0), _p(PU1 - 6.0, 0.0, T4 + 4.0), 22),
    "CAM_DSExit_PierWall": _c(_p(64.0, -42.0, T4 - 4.0), _p(70.0, -18.0, T4 - 7.0), 24),
}


def build():
    exit_path()
    E.torii("DS_Exit_Torii", L.TORII_OUT[0], L.TORII_OUT[1], T4, ANG, "DS_ExitTorii", C, 8)
    mb = MB("DS_Exit_Bridge", C, random.Random(5101), detail="near")      # madeira + capa/lajes/guarda da cabeceira
    mr = MB("DS_Exit_Rock", C, random.Random(5102), detail="near")        # rocha + ishigaki (mesmos materiais)
    exit_bridge(mb, mr)
    pier(mb, mr)
    mr.finish()
    mb.finish()
    anchor_guard()
    vegetation()
