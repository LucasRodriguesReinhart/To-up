# db_exit - SAIDA da Ilha 2 (Dragon Ball) em arte final: prefixo DB_Exit_, colecao 08_NEXT_ISLAND.
# Substitui db_blockout.exit_(). A narrativa, de dentro para fora:
#   DRAGON BALL -> TRILHA -> ARCO -> PONTE -> PORTAO DE COMPRA SHADOW GARDEN (asset aprovado, do db_core) -> ANCORA
#   - escada "Exit" (visual das medidas do db_col) com pilares-lanterna de arenito no topo, e a PRATELEIRA da saida
#     (L.EXIT_PATH hw 9 + L.HUB_EXIT_LINK hw 7, topo EXIT_Z): lajes claras em fileiras atravessadas, muro de arrimo de
#     arenito em blocos do GROUND ate EXIT_Z (o terreno nao faz). Guardas EXATAMENTE nas linhas das guardas invisiveis
#     do db_col: na TRILHA parapeito de arenito (blocos + capa de laje) com pilares e lanternas quentes de pedra a cada
#     ~16 e coroamento de arenito quente; so na LIGACAO (junto da vila) a guarda Capsule (mureta branca, balaustres,
#     corrimao azul) e o coroamento Capsule da vila. Nas quinas (ligacao x vila, ligacao x trilha) guarda e coroamento
#     vao ate a quina, sem pilar duplicado, e o trecho sem guarda invisivel ganha colisao propria (DB_ExitGuard);
#     nada de muro/coroamento dentro do terraco da vila (o DB_Ter_HubWalls faz aquela borda). A ponta da ligacao
#     dentro da vila: se o terraco recortar a meia-lua da fita, ela e calcada aqui (link_cap, adaptativo);
#   - ARCO NATURAL de arenito sobre a trilha (L.EXIT_ARCH): uma aleta de rocha so (loft continuo pe -> arco -> pe,
#     secao de rocha facetada e irregular, pernas que alargam no chao, lintel de topo achatado e assimetrico),
#     estratos escuros horizontais, topo iluminado com grama na crista, contrafortes e ombro de quebra; o vao livre
#     (>= 18 x 22) e medido no build por raios; colisao das pernas: octogonos (G+6..Z+10) e, no pe, faixas ajustadas a
#     rocha REAL (raios na malha, G+1..G+6, recuo 0,35) - nada de caixa passando da rocha;
#   - transicao SHADOW GARDEN sutil DEPOIS do arco (ultimos 20 da trilha): lajes de pedra crepuscular misturadas,
#     muro crepuscular, 1 lanterninha roxa por lado no fim, 2 arvores secas; o resto continua Dragon Ball;
#   - PONTE de saida (EXIT_START, rumo EXIT_DEG, 64 x 18, tabuleiro EXIT_Z) sobre 3 pilares de rocha pendurados
#     (agulhas de arenito que somem nas nuvens; o ultimo ja crepuscular); parapeito de blocos nas linhas das guardas;
#     arenito + capa de laje clara + coroamento de arenito no comeco, pedra crepuscular + capa negra-violeta e
#     lanternas roxas perto da ilhota (manchas continuas por ruido, nada de xadrez);
#   - ILHOTA do portao (L.islet_center() r 22): massa de rocha crepuscular pendurada em tambores + estalactites,
#     calcamento escuro em volta do portao (o portao GATE_ShadowGarden* e do db_core e nao e tocado), parapeito nas
#     guardas do db_col, bastiao da ancora e a guarda PROVISORIA DB_Exit_AnchorGuard (2 pilones + correntes,
#     next_island_guard=True).
# Colisao: o piso, as escadas e as guardas sao do db_col (congelado); aqui so as pernas do arco, contrafortes,
# troncos das arvores secas, os pilones da guarda da ancora e os trechos de guarda das quinas.
# Pos-critica: material do arco pela ESTRUTURA do loft (sofito escuro, crista clara/grama) + estratos horizontais por
# planos de corte (nada de xadrez) e UV em caixa no referencial do arco; lajes recortadas (clip_planes/slab_out) na
# juncao ligacao/trilha, na cunha trilha/ponte e em volta do portao/borda da ilhota; muro de arrimo misturado bloco a
# bloco; coroamento da ponte no perfil do da trilha; tambores da ilhota com estratos; correntes dentro da parede
# invisivel da ancora.
# Malhas (orcamento de MeshParts): DB_Exit_Trail, DB_Exit_Arch (+ arvores secas), DB_Exit_Bridge (+ pilares e as
# lanterninhas da trilha), DB_Exit_Islet (+ rocha), DB_Exit_AnchorGuard.
import math, random
import bmesh
from mathutils import Vector, noise
from mathutils.bvhtree import BVHTree
import db_lib as DL
from db_lib import MB, FP, col_box, light, ccw, octo_col
import db_layout as L
import db_col
import fm_lib
import fm_portal_kit as PK
import fm_veg_kit as VK

C = "08_NEXT_ISLAND"
Z = L.EXIT_Z
G = L.GROUND

PAVE, BLOCK, BLOCK_B = "Stone_Paving_DB", "Stone_DB_Block", "Stone_DB_Block_B"
DUSK = "Stone_DB_Dusk"
ROCK, DARK, TOP, RDUSK = "Cliff_Rock_DB", "Cliff_Rock_DB_Dark", "Cliff_Rock_DB_Top", "Cliff_Rock_DB_Dusk"
SHADOW, GLOW = "P_Shadow_Stone", "P_Shadow_Glow"
WHITE, BLUE = "Plaster_DB_White", "Roof_DB_Blue"
GRASS, IRON, DEAD = "Grass_DB", "Metal_DB_Dark", "Bark_Dead"
LAMP, ORANGE = "Lantern_Glow", "Roof_DB_Orange"
POLY_PATH, POLY_LINK = 0, 1                  # indices de DL.exit_shelf_polys(): trilha, ligacao com a vila
GUARD_H = db_col.GUARD_H
# coroamento do muro de arrimo (perfil lateral, vertical em volta da linha da borda, + = para fora):
# ligacao (junto da vila) = o Capsule da vila (capa branca + faixa azul); trilha = arenito quente (capa de laje clara +
# faixa de bloco escuro), um pouco maior que o da ligacao para as quinas trilha/ligacao nao terem faces coplanares
COPING = {POLY_LINK: (([(-1.25, -0.5), (0.5, -0.5), (0.5, 0.13), (-1.25, 0.13)], WHITE),
                      ([(0.18, -0.98), (0.62, -0.98), (0.62, -0.5), (0.18, -0.5)], BLUE)),
          POLY_PATH: (([(-1.3, -0.52), (0.56, -0.52), (0.56, 0.15), (-1.3, 0.15)], PAVE),
                      ([(0.2, -1.0), (0.68, -1.0), (0.68, -0.46), (0.2, -0.46)], BLOCK_B))}
# parapeito de arenito da trilha (nas linhas das guardas do db_col): corpo, capa e pilares
PAR_W, PAR_H, PAR_CAP = 1.0, 1.35, 0.26
PAR_POST = 8.0                               # pilar a cada ~8; lanterna quente em pilares alternados (~16)

# ------------------------------------------------------------------ referenciais
UX, UY = L.exit_dir()
U = Vector((UX, UY, 0.0))
N = Vector((-UY, UX, 0.0))                 # esquerda de quem sai (lado norte)
YAW = math.atan2(UY, UX)
S0 = Vector((L.EXIT_START[0], L.EXIT_START[1], 0.0))
D_ISLET = L.EXIT_BRIDGE_LEN + L.GATE_ISLET_R - 4.0          # centro da ilhota (d do inicio da ponte)
D_GATE = L.EXIT_BRIDGE_LEN + L.GATE_SG_OFF
D_ANCHOR = L.EXIT_BRIDGE_LEN + L.ANCHOR_OFF
R_ISLET = L.GATE_ISLET_R
# pegada do portao aprovado (il_gate_sg + il_gates_kit, referencial do portao: x lateral, y ao longo):
# soleira |x| <= 11, y -5..5 (topo +0,15); plintos |x| 11..18, y -10,2..2,9; contraforte de tras |x| 8,45..11,3,
# y 2,5..7,35. Nada do calcamento/parapeito entra aqui; o corredor da frente e o de tras continuam calcados.
GATE_RECTS = [(0.0, 11.0, -5.0, 5.0), (11.0, 18.0, -10.2, 2.9), (8.45, 11.3, 2.5, 7.35)]


def in_gate(dd, lat, pad=0.3):
    y = dd - D_GATE
    x = abs(lat)
    return any(x0 - pad <= x <= x1 + pad and y0 - pad <= y <= y1 + pad for x0, x1, y0, y1 in GATE_RECTS)


def ep(d, lat=0.0, z=0.0):
    """ponto no referencial da ponte: d ao longo (do inicio da ponte), lat para a esquerda (norte)"""
    return Vector((S0.x + UX * d - UY * lat, S0.y + UY * d + UX * lat, z))


def to_dl(x, y):
    dx, dy = x - S0.x, y - S0.y
    return dx * UX + dy * UY, -dx * UY + dy * UX


def smooth(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3.0 - 2.0 * t)


def patch(x, y, seed=0.0, f=0.08):
    """0..1 suave no espaco: manchas continuas (escolha de material sem xadrez)"""
    return max(0.0, min(1.0, 0.5 + 0.9 * noise.noise(Vector((x * f, y * f, seed)))))


class Path:
    """polilinha aberta parametrizada pelo comprimento"""

    def __init__(self, pts):
        self.p = [Vector((x, y, 0.0)) for x, y in pts]
        self.acc = [0.0]
        for a, b in zip(self.p, self.p[1:]):
            self.acc.append(self.acc[-1] + (b - a).length)
        self.total = self.acc[-1]

    def at(self, s):
        s = max(0.0, min(self.total, s))
        for i in range(len(self.p) - 1):
            if s <= self.acc[i + 1] + 1e-9 or i == len(self.p) - 2:
                a, b = self.p[i], self.p[i + 1]
                t = (b - a).normalized()
                return a + t * (s - self.acc[i]), t

    def param(self, x, y):
        best = (1e18, 0.0)
        q = Vector((x, y, 0.0))
        for i in range(len(self.p) - 1):
            a, b = self.p[i], self.p[i + 1]
            d = b - a
            l2 = d.length_squared
            t = max(0.0, min(1.0, (q - a).dot(d) / l2))
            dd = (a + d * t - q).length_squared
            if dd < best[0]:
                best = (dd, self.acc[i] + t * math.sqrt(l2))
        return best[1]


PATH = Path(L.EXIT_PATH)
LINK = Path(L.HUB_EXIT_LINK)
S_TOT = PATH.total
S_ARCH = PATH.param(L.EXIT_ARCH[0], L.EXIT_ARCH[1])
S_SG = S_TOT - L.SG_TRANSITION_D                 # comeco da paleta Shadow Garden (20 antes da ponte)
HW, HWL = L.EXIT_PATH_HW, L.HUB_EXIT_LINK_HW


def k_trail(s):
    """fracao de pedra crepuscular na trilha (0 = Dragon Ball puro) - sutil: 0,3 no inicio da ponte"""
    return 0.3 * smooth((s - S_SG) / L.SG_TRANSITION_D)


def k_bridge(d):
    """fracao crepuscular na ponte: 0,3 no comeco (igual ao fim da trilha), 1 junto da ilhota"""
    return 0.3 + 0.7 * smooth((d - 12.0) / 46.0)


def dp_path(x, y):
    return L.polyline_dist(x, y, L.EXIT_PATH)


def dp_link(x, y):
    return L.polyline_dist(x, y, L.HUB_EXIT_LINK)


# ------------------------------------------------------------------ arco natural: referencial e perfil
AX, AY, ADEG = L.EXIT_ARCH
AC = Vector((AX, AY, 0.0))
AU = Vector((math.cos(math.radians(ADEG)), math.sin(math.radians(ADEG)), 0.0))    # ao longo da trilha
AN = Vector((-AU.y, AU.x, 0.0))                                                   # lateral (norte = +)
# estratos escuros (cota absoluta): os 2 de baixo sao aneis do loft das pernas (sulco recuado); os 2 de cima cortam
# o arco (ombros e lintel) por planos horizontais - faixas continuas de arenito, nunca teste por face
ARCH_BANDS = [(25.8, 27.2), (35.2, 36.8), (46.2, 47.6), (58.3, 59.6)]
Z_SPRING = Z + 13.0
INTRA = (10.8, 13.5, 3.0)            # intradorso: meia-largura, flecha, expoente (superelipse: vao "quadrado")
EXTRA = {-1: (20.8, 23.6, 3.3), 1: (19.8, 22.2, 3.3)}     # extradorso por lado (sul mais grosso e mais alto)
ARCH_CLEAR = (9.0, 22.0)             # vao livre exigido: |lat| <= 9 (a trilha) ate EXIT_Z + 22


def apt(lat, z, along=0.0):
    return AC + AN * lat + AU * along + Vector((0.0, 0.0, z))


# ------------------------------------------------------------------ cameras de revisao
def _cams():
    p8, t8 = PATH.at(8.0)
    return {
        # arco visto da trilha na altura do jogador (olho 5,2 acima do piso)
        "CAM_DBExit_PlayerArch": ((p8.x, p8.y, Z + 5.2), tuple(apt(0.0, Z + 12.0, 16.0)), 20),
        # pe da escada da saida (promenade), olhando a escada, a prateleira e o arco
        "CAM_DBExit_PlayerStair": ((66.0, 20.0, G + 5.2), tuple(apt(0.0, Z + 14.0)), 20),
        # o arco como marco, de longe (3/4 do promenade leste)
        "CAM_DBExit_ArchFar": ((58.0, 8.0, G + 26.0), tuple(apt(0.0, Z + 12.0)), 24),
        # bolsao de chao ao norte da prateleira: muro de arrimo, perna norte, ligacao com a vila
        "CAM_DBExit_PlayerPocket": ((72.0, 57.0, G + 5.2), tuple(apt(10.0, Z + 8.0, 2.0)), 22),
        # da vila (terraco leste) para o arco e a ligacao
        "CAM_DBExit_FromHub": ((92.0, 96.0, L.HUB + 5.2), tuple(apt(0.0, Z + 10.0)), 22),
        # chao ao sul da trilha (costas do arco, pe sul, muro, arvore seca)
        "CAM_DBExit_PlayerSouth": ((141.0, 14.0, G + 5.2), tuple(apt(-8.0, Z + 8.0, 4.0)), 22),
        # planta de cima da prateleira (juncao trilha/ligacao, muros, arco, comeco da ponte)
        "CAM_DBExit_Top": ((122.0, 60.0, 190.0), (122.0, 61.0, Z), 24),
        # encontro da prateleira com a ponte (lado sul, de fora da ilha)
        "CAM_DBExit_BridgeStart": (tuple(ep(8.0, -34.0, Z + 8.0)), tuple(ep(-6.0, 0.0, Z - 3.0)), 22),
        # ponte de lado (sul), pilares nas nuvens, ilhota ao fundo
        "CAM_DBExit_BridgeSide": (tuple(ep(26.0, -98.0, Z - 4.0)), tuple(ep(36.0, 0.0, Z - 16.0)), 22),
        # ilhota por baixo (massa pendurada)
        "CAM_DBExit_IsletBelow": (tuple(ep(52.0, -62.0, Z - 52.0)), tuple(ep(D_ISLET, 0.0, Z - 16.0)), 22),
        # de tras (alem da ancora) olhando de volta: guarda provisoria, ilhota, ponte, arco
        "CAM_DBExit_Back": (tuple(ep(D_ANCHOR + 46.0, 26.0, Z + 22.0)), tuple(ep(30.0, 0.0, Z + 2.0)), 22),
        # jogador no comeco da ponte olhando de volta para o arco (transicao)
        "CAM_DBExit_PlayerBack": (tuple(ep(14.0, 3.0, Z + 5.2)), tuple(apt(0.0, Z + 12.0)), 20),
        # jogador atras do portao, na ilhota, olhando a ancora e a guarda
        "CAM_DBExit_PlayerAnchor": (tuple(ep(D_GATE + 11.0, -7.0, Z + 5.2)), tuple(ep(D_ANCHOR, 2.0, Z + 2.0)), 22),
    }


CAMS = _cams()


# ------------------------------------------------------------------ utilidades
def simplify(pts, tol=0.04):
    if len(pts) < 3:
        return list(pts)
    out = [pts[0]]
    for i in range(1, len(pts) - 1):
        a, b, c = out[-1], pts[i], pts[i + 1]
        d1, d2 = b - a, c - b
        if d1.length < 1e-6:
            continue
        cr = abs(d1.x * d2.y - d1.y * d2.x) / max(1e-6, d1.length * d2.length)
        if cr > tol:
            out.append(b)
    out.append(pts[-1])
    return out


def run_marks(pl, step):
    """pontos a cada ~step ao longo da polilinha pl (Vector): [(ponto, angulo, s)]"""
    total = sum((b - a).length for a, b in zip(pl, pl[1:]))
    k = max(1, int(round(total / step)))
    marks = [total * i / k for i in range(k + 1)]
    out = []
    acc = 0.0
    mi = 0
    for a, b in zip(pl, pl[1:]):
        ln = (b - a).length
        ang = math.atan2(b.y - a.y, b.x - a.x)
        while mi < len(marks) and marks[mi] <= acc + ln + 1e-6:
            t = (marks[mi] - acc) / ln if ln > 1e-6 else 0.0
            out.append((a + (b - a) * t, ang, marks[mi]))
            mi += 1
        acc += ln
    return out


def clip_planes(P, planes):
    """recorta o poligono 2D P (anti-horario) pelos semiplanos [(nx, ny, c)] (mantem nx*x + ny*y <= c).
    Retorna (poligono ou None, mudou?)"""
    changed = False
    for nx, ny, c in planes:
        if all(nx * x + ny * y <= c + 1e-6 for x, y in P):
            continue
        P = DL.clip(P, nx, ny, c)
        changed = True
        if len(P) < 3:
            return None, True
    if changed:
        Q = []
        for p in P:
            if not Q or math.hypot(p[0] - Q[-1][0], p[1] - Q[-1][1]) > 0.03:
                Q.append(p)
        if len(Q) > 2 and math.hypot(Q[0][0] - Q[-1][0], Q[0][1] - Q[-1][1]) <= 0.03:
            Q.pop()
        P = Q
        if len(P) < 3:
            return None, True
    return P, changed


def poly_ok(P, amin=0.25, wmin=0.22):
    """a laje recortada ainda e laje (nada de lasca fina: area e largura media minimas)"""
    ar = abs(DL.area(P))
    edge = max(math.hypot(P[i][0] - P[i - 1][0], P[i][1] - P[i - 1][1]) for i in range(len(P)))
    return ar >= amin and ar / max(edge, 1e-6) >= wmin


def slab_out(mb, c, t, nrm, ln, wd, hh, ang, m, planes, tint=None):
    """laje retangular (centro c, eixo t, meia-largura em nrm) recortada pelos semiplanos: caixa quando inteira,
    prisma quando recortada, nada quando some ou vira lasca. Topo sempre em Z + 0,1."""
    pts = [c + t * (sx * ln / 2) + nrm * (sy * wd / 2) for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    P, changed = clip_planes([(p.x, p.y) for p in pts], planes)
    if P is None:
        return False
    if not changed:
        mb.box((ln, wd, hh), (c.x, c.y, Z + 0.1 - hh / 2), (0, 0, ang), m, 0.0, 1, tint)
        return True
    if not poly_ok(P):
        return False
    mb.prism(ccw(P), Z + 0.1 - hh, Z + 0.1, m, 0.0, 1, tint)
    return True


def ribbon_plane(x, y, pts, hw, gap):
    """semiplano 'fora da fita' (pts, hw) do lado de (x, y), pelo trecho mais proximo: (nx, ny, c)"""
    best = None
    for a, b in zip(pts, pts[1:]):
        dx, dy = b[0] - a[0], b[1] - a[1]
        ln = math.hypot(dx, dy)
        ux, uy = dx / ln, dy / ln
        tt = max(0.0, min(ln, (x - a[0]) * ux + (y - a[1]) * uy))
        dd = math.hypot(x - a[0] - ux * tt, y - a[1] - uy * tt)
        if best is None or dd < best[0]:
            best = (dd, a[0], a[1], ux, uy)
    _, ax, ay, ux, uy = best
    nx, ny = -uy, ux
    sg = 1.0 if (x - ax) * nx + (y - ay) * ny >= 0.0 else -1.0
    return (-sg * nx, -sg * ny, -sg * (nx * ax + ny * ay) - (hw + gap))


def assign(mb, faces, m, variant=True):
    faces = [f for f in faces if f.is_valid]
    if not faces:
        return
    mi = mb._mi_for(m) if variant else mb._mi(m)
    t = mb.rng.uniform(-1.0, 1.0)
    for f in faces:
        f.material_index = mi
        f[mb.tint] = t
        f.smooth = False
        f.normal_update()
    mb._uv(faces, m)


def box_uv(mb, faces, m, c0, ax, ay):
    """UV em caixa no referencial (ax, ay, Z) em volta de c0: faces vizinhas de normal parecida usam a MESMA
    projecao (textura continua na rocha do arco; a UV por face do MB, em coordenada de mundo, fazia retalhos)"""
    tk = fm_lib.tex_key(m)
    if tk is None:
        return
    inv = 1.0 / fm_lib.tex_tile(tk)
    uvl = mb.uvl
    zv = Vector((0.0, 0.0, 1.0))
    for f in faces:
        if not f.is_valid:
            continue
        n = f.normal
        a, b, cz = abs(n.dot(ax)), abs(n.dot(ay)), abs(n.z)
        if cz >= a and cz >= b:
            pu, pv = ax, ay
        elif a >= b:
            pu, pv = ay, zv
        else:
            pu, pv = ax, zv
        for lp in f.loops:
            q = lp.vert.co - c0
            lp[uvl].uv = (q.dot(pu) * inv, q.dot(pv) * inv)


def new_verts(mb, n0):
    mb.bm.verts.ensure_lookup_table()
    return [mb.bm.verts[i] for i in range(n0, len(mb.bm.verts))]


def nverts(mb):
    mb.bm.verts.ensure_lookup_table()
    return len(mb.bm.verts)


def dusk_lamp(mb, p, yaw, s=1.0):
    """lanterninha Shadow Garden: camara roxa (P_Shadow_Glow) com 4 montantes, prato e chapeu negro-violeta"""
    z = p.z
    mb.box((1.15 * s, 1.15 * s, 0.26), (p.x, p.y, z + 0.13), (0, 0, yaw), SHADOW, 0.0)
    mb.box((0.72 * s, 0.72 * s, 0.95 * s), (p.x, p.y, z + 0.26 + 0.47 * s), (0, 0, yaw), GLOW, 0.0)
    c, sn = math.cos(yaw), math.sin(yaw)
    for sx in (-1, 1):
        for sy in (-1, 1):
            ox, oy = sx * 0.42 * s, sy * 0.42 * s
            mb.box((0.17, 0.17, 0.98 * s), (p.x + ox * c - oy * sn, p.y + ox * sn + oy * c, z + 0.26 + 0.47 * s),
                   (0, 0, yaw), SHADOW, 0.0)
    zt = z + 0.26 + 0.95 * s
    mb.box((1.05 * s, 1.05 * s, 0.2), (p.x, p.y, zt + 0.1), (0, 0, yaw), SHADOW, 0.0)
    mb.cyl(0.95 * s, 0.75 * s, (p.x, p.y, zt + 0.2 + 0.37 * s), (0, 0, yaw + math.pi / 4), SHADOW, 4, r2=0.12,
           bevel=0.0)
    return Vector((p.x, p.y, z + 0.26 + 0.47 * s))


def stone_lantern(mb, x, y, z, yaw, s=1.0):
    """lanterna quente de pedra (o caminho da concept ate o portao): prato de laje, camara ambar acesa, tampa de laje
    e chapeu laranja em piramide (acento marcial). Peca pequena repetida: sem chanfro."""
    mb.box((1.3 * s, 1.3 * s, 0.2), (x, y, z + 0.1), (0, 0, yaw), PAVE, 0.0)
    mb.box((0.8 * s, 0.8 * s, 0.9 * s), (x, y, z + 0.2 + 0.45 * s), (0, 0, yaw), LAMP, 0.0)
    zt = z + 0.2 + 0.9 * s
    mb.box((1.22 * s, 1.22 * s, 0.18), (x, y, zt + 0.09), (0, 0, yaw), PAVE, 0.0)
    mb.cyl(1.06 * s, 0.58 * s, (x, y, zt + 0.18 + 0.29 * s), (0, 0, yaw + math.pi / 4), ORANGE, 4, r2=0.14 * s,
           bevel=0.0)


# ------------------------------------------------------------------ prateleira: linhas das guardas e dos muros
def _near_stair_top(x, y, z_top, stairs):
    for nm, base, ang, w, n, rise, tread, g in stairs:
        if abs(base[2] + rise * n - z_top) > 0.3:
            continue
        tx = base[0] + math.cos(ang) * tread * n
        ty = base[1] + math.sin(ang) * tread * n
        dx, dy = x - tx, y - ty
        along = abs(-dx * math.sin(ang) + dy * math.cos(ang))
        depth = abs(dx * math.cos(ang) + dy * math.sin(ang))
        if along < w / 2 + 0.8 and depth < 3.0:
            return True
    return False


def shelf_guard_runs():
    """as MESMAS linhas das guardas invisiveis da prateleira (db_col.terrace_guards, poligonos Exit0/Exit1):
    [(indice do poligono, trecho)]. Nada dentro do terraco da vila (a borda dele e do db_terrain)."""
    stairs = db_col.stair_list()
    out = []
    for k, rp in enumerate(DL.exit_shelf_polys()):
        pts = ccw(rp)
        cx = sum(p[0] for p in pts) / len(pts)
        cy = sum(p[1] for p in pts) / len(pts)

        def keep(x, y, cx=cx, cy=cy):
            d = Vector((x - cx, y - cy, 0))
            if d.length < 1e-3:
                return False
            d.normalize()
            ox, oy = x + d.x * 1.6, y + d.y * 1.6
            if not L.point_in_poly(ox, oy, L.ISLAND_RIM):
                return False
            if Z - L.zone_of(ox, oy) <= 2.3:
                return False
            if db_col._opening(ox, oy, strict=True):     # igual ao db_col.terrace_guards
                return False
            if L.point_in_poly(x, y, L.HUB_POLY):
                return False
            return not _near_stair_top(x, y, Z, stairs)
        out += [(k, r) for r in db_col._runs(pts, keep, step=1.0)]
    return out


# ------------------------------------------------------------------ quinas: onde a borda da prateleira encontra a
# borda da vila (db_terrain) ou a outra fita. Os trechos das guardas/muros param ~1-2 antes da quina (amostragem do
# db_col); a guarda e o coroamento daqui vao ATE a quina (sem pilar duplicado ao lado do pilar do vizinho)
def _poly_segs(P):
    return [(P[i], P[(i + 1) % len(P)]) for i in range(len(P))]


def _seg_hit(p, d, segs, tmax):
    """menor t em (0, tmax] em que o raio p + t d cruza um dos segmentos"""
    best = None
    for a, b in segs:
        ex, ey = b[0] - a[0], b[1] - a[1]
        den = d.x * ey - d.y * ex
        if abs(den) < 1e-9:
            continue
        wx, wy = a[0] - p.x, a[1] - p.y
        t = (wx * ey - wy * ex) / den
        s = (wx * d.y - wy * d.x) / den
        if 1e-4 < t <= tmax and -1e-6 <= s <= 1.0 + 1e-6 and (best is None or t < best):
            best = t
    return best


_TARGETS = {}


def _targets(k):
    if not _TARGETS:
        polys = DL.exit_shelf_polys()
        _TARGETS[POLY_PATH] = [("link", _poly_segs(ccw(polys[POLY_LINK])))]
        _TARGETS[POLY_LINK] = [("hub", _poly_segs(list(L.HUB_POLY))), ("path", _poly_segs(ccw(polys[POLY_PATH])))]
    return _TARGETS[k]


def corner_of(run, k, at_end, tmax=3.0):
    """(tag, C) se a ponta do trecho (continuada pela borda) encontra a vila ('hub') ou a outra fita ('path'/'link')
    ate tmax adiante; C = a quina. None nas pontas comuns (escada, ponte, fim da queda)."""
    if len(run) < 2:
        return None
    p, q = (run[-1], run[-2]) if at_end else (run[0], run[1])
    d = Vector((p.x - q.x, p.y - q.y, 0.0))
    if d.length < 1e-6:
        return None
    d.normalize()
    best = None
    for tag, segs in _targets(k):
        t = _seg_hit(p, d, segs, tmax)
        if t is not None and (best is None or t < best[0]):
            best = (t, tag)
    if best is None:
        return None
    return best[1], Vector((p.x + d.x * best[0], p.y + d.y * best[0], 0.0))


_TER_ENDS = []


def terrain_guard_ends():
    """pontas das guardas da vila (db_terrain.guard_runs, as mesmas linhas do db_col): a guarda da ligacao encosta
    nelas nas quinas com a vila"""
    if not _TER_ENDS:
        try:
            import db_terrain
            for r in db_terrain.guard_runs():
                for p in (r[0], r[-1]):
                    _TER_ENDS.append(Vector((p.x, p.y, 0.0)))
        except Exception as e:                        # modulo do vizinho indisponivel: para na quina
            print("DB_EXIT AVISO: guardas do db_terrain indisponiveis (%s)" % e)
            _TER_ENDS.append(Vector((1e9, 1e9, 0.0)))
    return _TER_ENDS


def guard_plan():
    """guardas da prateleira com as pontas levadas ate as quinas: [(k, pontos, tags, extensoes)]. Na quina com a vila a
    guarda da ligacao continua pela borda da vila ate a ponta da guarda dela (se estiver a < 3). As extensoes sao
    trechos SEM guarda invisivel no db_col (a amostragem dele abre 1-3 studs em cada quina): viram colisao propria."""
    stairs = db_col.stair_list()
    out = []
    for k, run in shelf_guard_runs():
        run = [Vector((p.x, p.y, 0.0)) for p in run]
        if len(run) < 2:
            continue
        tags = [None, None]
        ext = []
        for at_end in (False, True):
            c = corner_of(run, k, at_end)
            if c is None:
                p = run[-1] if at_end else run[0]
                if _near_stair_top(p.x, p.y, Z, [(nm, b, a, w + 2.8, n, r, t, g)
                                                 for nm, b, a, w, n, r, t, g in stairs]):
                    tags[1 if at_end else 0] = "stair"
                continue
            tag, C = c
            add = [C]
            p = run[-1] if at_end else run[0]
            ext.append((p, C, 0.3, 0.0))              # entra 0,3 na guarda invisivel do db_col (lado da ponta)
            if tag == "hub":
                te = sorted(terrain_guard_ends(), key=lambda e: (e - C).length)
                if te and 0.5 < (te[0] - C).length < 3.0:
                    add.append(te[0].copy())
                    ext.append((C, te[0].copy(), 0.0, 0.3))     # entra 0,3 na guarda da vila
            if at_end:
                run = run + add
            else:
                run = list(reversed(add)) + run
            tags[1 if at_end else 0] = tag
        out.append((k, run, tags, ext))
    return out


def guard_ext_col(ext):
    """colisao das extensoes (a mesma parede do db_col: espessura 1, de Z-0,5 ate Z+GUARD_H), entrando ga/gb na guarda
    invisivel vizinha pelo lado que encosta nela (nunca alem da quina: nada de toco no piso)"""
    n = 0
    for a, b, ga, gb in ext:
        d = b - a
        ln = d.length
        if ln < 1.0:
            continue                                  # fresta < 1 entre guardas de 1 de espessura: ninguem passa
        u = d / ln
        a2, b2 = a - u * ga, b + u * gb
        c = (a2 + b2) / 2
        col_box("DB_ExitGuard", ((b2 - a2).length, 1.0, GUARD_H + 0.5), (c.x, c.y, Z - 0.5 + (GUARD_H + 0.5) / 2),
                (0, 0, math.atan2(u.y, u.x)))
        n += 1
    return n


def on_bridge(x, y):
    """(x, y) cai no tabuleiro da ponte de saida (que o zone_of nao conhece)"""
    d, lat = to_dl(x, y)
    return d >= -2.5 and abs(lat) <= L.EXIT_W / 2 + 1.4


def exit_stair():
    return [s for s in db_col.stair_list() if s[0] == "Exit"][0]


def stair_lamp_pts():
    """pilares-lanterna do topo da escada da saida (as pontas do parapeito junto deles ficam sem lanterna)"""
    nm, base, ang, w, nn, rise, tread, g = exit_stair()
    F = DL.Frame(base[0], base[1], base[2], ang)
    return [Vector((F.p(tread * nn - tread / 2, sg * (w / 2 + 0.6), 0.0).x,
                    F.p(tread * nn - tread / 2, sg * (w / 2 + 0.6), 0.0).y, Z)) for sg in (-1, 1)]


def wall_runs():
    """trechos das bordas da prateleira que dao para o chao GROUND (queda de 4): muro de arrimo + coroamento.
    [(indice do poligono, trecho)]. Nenhum trecho com o meio dentro do terraco da vila (o DB_Ter_HubWalls faz aquela
    borda: nada de muro/coroamento duplicado nas quinas da ligacao)."""
    nm, base, ang, w, n, rise, tread, g = exit_stair()
    sd = Vector((math.cos(ang), math.sin(ang), 0.0))
    sn = Vector((-sd.y, sd.x, 0.0))
    top = Vector((base[0], base[1], 0.0)) + sd * (tread * n)
    runs = []
    for kp, rp in enumerate(DL.exit_shelf_polys()):
        P = ccw(rp)
        m = len(P)
        pr = []
        run = []
        for i in range(m):
            a = Vector((P[i][0], P[i][1], 0.0))
            b = Vector((P[(i + 1) % m][0], P[(i + 1) % m][1], 0.0))
            d = b - a
            ln = d.length
            if ln < 1e-6:
                continue
            u = d / ln
            nout = Vector((u.y, -u.x, 0.0))
            k = max(1, int(ln / 1.0))
            for j in range(k):
                p = a + d * (j / k)
                q = p + nout * 1.6
                mid = p + d * (0.5 / k)
                ok = (L.point_in_poly(q.x, q.y, L.ISLAND_RIM) and L.zone_of(q.x, q.y) < Z - 2.3
                      and not on_bridge(q.x, q.y) and not L.point_in_poly(mid.x, mid.y, L.HUB_POLY))
                rel = p - top
                if abs(rel.dot(sn)) < w / 2 + 0.3 and abs(rel.dot(sd)) < 1.5:
                    ok = False
                if ok:
                    run.append(p)
                else:
                    if len(run) > 1:
                        pr.append(run)
                    run = []
        if len(run) > 1:
            pr.append(run)
        if len(pr) > 1 and (pr[0][0] - pr[-1][-1]).length < 1.5:
            pr[0] = pr[-1] + pr[0]
            pr.pop()
        runs += [(kp, r) for r in pr]
    return runs


# ------------------------------------------------------------------ prateleira: calcamento
def row_side(p, nrm, sg, hw):
    """o que ha do lado sg da fileira: 'open' (piso igual: vila/outra fita), 'wall' (muro + coroamento) ou 'rim'"""
    q = p + nrm * (sg * (hw + 1.3))
    if on_bridge(q.x, q.y):
        return "open"
    if not L.point_in_poly(q.x, q.y, L.ISLAND_RIM):
        return "rim"
    if L.zone_of(q.x, q.y) >= Z - 0.1:
        return "open"
    return "wall"


def pave_ribbon(mb, path, hw, rng, kfn, other=None):
    """lajes em fileiras atravessadas (2-4 por fileira, juntas desencontradas) ao longo da fita. As lajes param no
    coroamento (muro) ou num meio-fio (borda da ilha); do lado aberto vao ate a borda. other: (polilinha, hw) de
    outra fita que tem prioridade: as lajes que entram nela sao RECORTADAS na borda dela (sem cunha de leito)."""
    total = path.total
    s = 0.0
    n = 0
    while s < total - 0.3:
        Ls = min(rng.uniform(2.3, 3.1), total - s)
        if total - s - Ls < 0.9:
            Ls = total - s
        sm = s + Ls / 2
        p, t = path.at(sm)
        nrm = Vector((-t.y, t.x, 0.0))
        ang = math.atan2(t.y, t.x)
        lim = {}
        for sg in (1, -1):
            side = row_side(p, nrm, sg, hw)
            if side == "wall":
                # fileira na quina de uma boca (ligacao/ponte): se uma ponta ja da no piso aberto, a laje vai ate a
                # borda (sob o coroamento ela fica escondida; na boca ela fecha o piso)
                for ds in (-Ls / 2 + 0.25, Ls / 2 - 0.25):
                    pe, te = path.at(sm + ds)
                    ne = Vector((-te.y, te.x, 0.0))
                    if row_side(pe, ne, sg, hw) == "open":
                        side = "open"
            lim[sg] = hw - (1.3 if side == "wall" else (1.0 if side == "rim" else 0.05))
            if side == "rim":
                c = p + nrm * (sg * (hw - 0.5))
                mb.box((Ls - 0.08, 0.9, 0.6), (c.x, c.y, Z + 0.14 - 0.3), (0, 0, ang), BLOCK, 0.0)
        field = lim[1] + lim[-1]
        k = max(2, int(round(field / 2.9)))
        cuts = sorted([(q + rng.uniform(-0.2, 0.2)) / k for q in range(1, k)])
        edges = [0.0] + cuts + [1.0]
        kk = kfn(sm)
        for a0, a1 in zip(edges, edges[1:]):
            u0 = -lim[-1] + field * a0
            u1 = -lim[-1] + field * a1
            c = p + nrm * ((u0 + u1) / 2)
            wd = (u1 - u0) - 0.18
            ln = Ls - 0.18
            planes = []
            if other is not None:
                pts, ohw = other
                planes.append(ribbon_plane(c.x, c.y, pts, ohw, 0.09))
            hh = 0.3 + rng.uniform(-0.03, 0.03)
            m = DUSK if (0.45 * rng.random() + 0.55 * patch(c.x, c.y, 7.7, 0.22)) < kk * 1.15 else PAVE
            if slab_out(mb, c, t, nrm, ln, wd, hh, ang + rng.uniform(-0.012, 0.012), m, planes):
                n += 1
        s += Ls
    return n


def capsule_guard(mb, run, z, lamp_fn=None, lamp_mb=None, post_ends=(True, True)):
    """guarda Capsule da vila (a mesma do db_terrain): mureta branca baixa, balaustres brancos, corrimao azul e
    pilares maiores a cada ~9,6; lamp_fn(x, y) -> True poe a lanterninha roxa (no objeto lamp_mb) no pilar.
    post_ends: sem pilar/balaustre na ponta que encosta no pilar do vizinho (quina com a vila ou com a trilha)"""
    pl = simplify([Vector((p.x, p.y, z)) for p in run])
    if len(pl) < 2:
        return 0
    mb.sweep(pl, [(-0.42, 0.13), (0.42, 0.13), (0.42, 0.6), (-0.42, 0.6)], WHITE, True)
    mb.sweep(pl, [(-0.42, 1.52), (0.42, 1.52), (0.42, 1.82), (-0.42, 1.82)], BLUE, True)
    marks = run_marks(pl, 3.2)
    lamps = 0
    for i, (q, ang, s) in enumerate(marks):
        if (i == 0 and not post_ends[0]) or (i == len(marks) - 1 and not post_ends[1]):
            continue
        if i % 3 == 0 or i == len(marks) - 1:
            mb.box((0.95, 0.95, 1.98), (q.x, q.y, z + 0.13 + 0.99), (0, 0, ang), WHITE, 0.08)
            if lamp_fn is not None and lamp_mb is not None and lamp_fn(q.x, q.y):
                dusk_lamp(lamp_mb, Vector((q.x, q.y, z + 2.11)), ang, 0.8)
                lamps += 1
            else:
                mb.box((1.15, 1.15, 0.3), (q.x, q.y, z + 2.11 + 0.15), (0, 0, ang), BLUE, 0.08)
        else:
            mb.box((0.5, 0.5, 0.95), (q.x, q.y, z + 0.6 + 0.475), (0, 0, ang), WHITE, 0.0)
    return lamps


def wall_k(x, y):
    """fracao crepuscular do muro de arrimo aqui (a mesma rampa das lajes da trilha)"""
    return k_trail(PATH.param(x, y)) if dp_path(x, y) < HW + 2.0 else 0.0


def trail_parapet(mt, mlamp, run, rng, tags):
    """parapeito de ARENITO da trilha (a concept leva o caminho ate o portao em pedra quente com lanternas): blocos de
    arenito sobre nucleo de rejunte, capa continua de laje clara, pilares a cada ~8 com lanterna quente de pedra em
    pilares alternados (~16; nenhuma junto dos pilares-lanterna da escada). Transicao Shadow Garden (ultimos 20) como
    antes: blocos crepusculares em manchas (wall_k) e a lanterninha roxa no ultimo pilar antes da ponte, 1 por lado.
    Na quina com a ligacao o pilar fica NA quina (a guarda Capsule da ligacao morre nele); junto da ponte o parapeito
    entra no 1o pilar da ponte (sem pilar duplo: a lanterninha roxa da ponta vai nele, no bridge())."""
    pts = [Vector((p.x, p.y, Z)) for p in run]
    on_br = [False, False]
    bps = bridge_post0()
    for e, j in ((0, 0), (1, -1)):
        nb = min(bps, key=lambda b: (b - pts[j]).length)
        if (nb - pts[j]).length < 2.5:
            on_br[e] = True
            if e == 0:
                pts.insert(0, nb.copy())
            else:
                pts.append(nb.copy())
    pl = simplify(pts, 0.02)
    if len(pl) < 2:
        return 0, 0
    hw = PAR_W / 2
    mt.sweep(pl, [(-hw + 0.08, 0.0), (hw - 0.08, 0.0), (hw - 0.08, PAR_H), (-hw + 0.08, PAR_H)], BLOCK_B, True)
    marks = run_marks(pl, 2.4)
    for (a, _, sa), (b, _, sb) in zip(marks, marks[1:]):
        mid = (a + b) / 2
        ln = (b - a).length
        an = math.atan2(b.y - a.y, b.x - a.x)
        k = wall_k(mid.x, mid.y)
        if k > 0.0 and (0.35 * rng.random() + 0.65 * patch(mid.x, mid.y, 5.1, 0.2)) < k * 1.25:
            m = DUSK
        else:
            m = BLOCK_B if rng.random() < 0.14 else BLOCK
        mt.box((ln - 0.09, PAR_W, PAR_H - 0.04), (mid.x, mid.y, Z + (PAR_H - 0.04) / 2), (0, 0, an), m, 0.0)
    cw = hw + 0.13
    mt.sweep(pl, [(-cw, PAR_H - 0.02), (cw, PAR_H - 0.02), (cw, PAR_H + PAR_CAP), (-cw, PAR_H + PAR_CAP)], PAVE, True)
    posts = run_marks(pl, PAR_POST)
    warm = dusk = 0
    zp = Z + PAR_H + 0.5
    for i, (q, ang, s) in enumerate(posts):
        last = i == len(posts) - 1
        if (i == 0 and (tags[0] == "stair" or on_br[0])) or (last and (tags[1] == "stair" or on_br[1])):
            continue
        sp = PATH.param(q.x, q.y)
        near_stair = min((q - p).length for p in stair_lamp_pts()) < 4.5
        mt.box((1.5, 1.5, zp - Z), (q.x, q.y, (Z + zp) / 2), (0, 0, ang), BLOCK_B, 0.0)
        if sp > S_TOT - 7.0 and not any(on_br):
            dusk_lamp(mlamp, Vector((q.x, q.y, zp)), ang, 0.8)
            dusk += 1
        elif i % 2 == 0 and sp < S_SG and abs(sp - S_ARCH) > 4.0 and not near_stair:
            stone_lantern(mt, q.x, q.y, zp, ang)
            warm += 1
        else:
            mt.box((1.74, 1.74, 0.24), (q.x, q.y, zp + 0.12), (0, 0, ang), PAVE, 0.0)
    return warm, dusk


def _terrain_cut(pts):
    """para cada ponto: o terraco da vila (db_terrain) deixou este chao SEM piso por causa da prateleira da saida?
    (a mesma conta do DB_Ter_HubTop: regiao R >= 0 dominada pelo termo 'exit', fora dos lotes). None = indisponivel"""
    try:
        import numpy as np
        import db_terrain as T
        X = np.array([p.x for p in pts], dtype=float)
        Y = np.array([p.y for p in pts], dtype=float)
        F = T.terms(X, Y)
        R = T.hub_region(F)[0]
        return [bool(R[i] > -0.05 and F["exit"][i] < 0.0 and F["lots"][i] > 0.0) for i in range(len(pts))]
    except Exception as e:
        print("DB_EXIT AVISO: recorte do terraco da vila indisponivel (%s): calca a ponta da ligacao" % e)
        return None


def link_cap(mt, rng):
    """a ligacao comeca DENTRO da vila (100, 88). Se o terraco da vila recorta o piso com a ponta ARREDONDADA da fita
    (meia-lua de raio HUB_EXIT_LINK_HW atras da ponta reta daqui), a meia-lua ganha leito + lajes nas mesmas fileiras
    da ligacao, recortadas no circulo (sem buraco ate o DB_Ter_Underside). Se o recorte e o poligono de ponta reta (o
    mesmo leito daqui), o terraco ja cobre: nada (sem piso duplicado)."""
    c0 = Vector((L.HUB_EXIT_LINK[0][0], L.HUB_EXIT_LINK[0][1], 0.0))
    u0 = Vector((L.HUB_EXIT_LINK[1][0] - c0.x, L.HUB_EXIT_LINK[1][1] - c0.y, 0.0)).normalized()
    n0 = Vector((-u0.y, u0.x, 0.0))

    def back(a, r):
        return c0 + (-u0 * math.cos(a) + n0 * math.sin(a)) * r
    probe = [back(math.pi * (j / 8.0 - 0.5), r) for r in (1.0, 3.0, 5.0, 6.2) for j in range(9)]
    need = _terrain_cut(probe)
    frac = 1.0 if need is None else sum(need) / float(len(need))
    if frac < 0.2:
        print("DB_EXIT ligacao: o terraco da vila ja cobre a ponta (recorte reto, %.0f%% sem piso) - sem meia-lua" % (
            100.0 * frac))
        return 0
    R = HWL
    half = [c0 + u0 * 0.5 + n0 * (R + 0.5)] + [back(math.pi * (0.5 - j / 16.0), R + 0.5) for j in range(17)] + \
           [c0 + u0 * 0.5 - n0 * (R + 0.5)]
    DL.prism(mt, ccw([(p.x, p.y) for p in half]), G - 0.6, Z - 0.12, BLOCK, top_m=BLOCK_B)
    planes = [(math.cos(t), math.sin(t), math.cos(t) * c0.x + math.sin(t) * c0.y + R - 0.05)
              for t in (math.tau * (k + 0.5) / 48 for k in range(48))]
    planes.append((u0.x, u0.y, u0.x * c0.x + u0.y * c0.y - 0.09))      # para antes da 1a fileira da ligacao
    ang = math.atan2(u0.y, u0.x)
    n = 0
    s = 0.0
    while s > -R + 0.2:
        Ls = min(rng.uniform(2.3, 3.1), s + R)
        if s - Ls < -R + 0.9:
            Ls = s + R
        sm = s - Ls / 2
        p = c0 + u0 * sm
        k = 5
        cuts = sorted([(q + rng.uniform(-0.2, 0.2)) / k for q in range(1, k)])
        edges = [0.0] + cuts + [1.0]
        for a0, a1 in zip(edges, edges[1:]):
            u_0, u_1 = -R + 2 * R * a0, -R + 2 * R * a1
            c = p + n0 * ((u_0 + u_1) / 2)
            hh = 0.3 + rng.uniform(-0.03, 0.03)
            if slab_out(mt, c, u0, n0, Ls - 0.18, (u_1 - u_0) - 0.18, hh, ang + rng.uniform(-0.012, 0.012), PAVE,
                        planes):
                n += 1
        s -= Ls
    print("DB_EXIT ligacao: meia-lua calcada na ponta da vila (%d lajes, %.0f%% sem piso no terraco)" % (n, 100 * frac))
    return n


def mixed_wall(mb, a, b, z0, z1, thick, rng, course=1.3, blk=(3.0, 5.2), bevel=0.1):
    """o fm_parts.masonry_wall (nucleo de rejunte + fiadas desencontradas + base/cunhais escuros), mas com o
    material escolhido BLOCO a BLOCO: arenito, e pedra crepuscular em manchas continuas onde wall_k sobe (a mesma
    mistura gradual das lajes e do paramento da ponte, nada de trecho que vira todo roxo de uma vez)"""
    a = Vector((a.x, a.y, z0))
    b = Vector((b.x, b.y, z0))
    Ln = (b - a).length
    dv = (b - a).normalized()
    ang = math.atan2(dv.y, dv.x)
    FP._masonry_core(mb, a, dv, ang, Ln, z0, z1, max(0.25, thick - 0.35), (), BLOCK_B)
    z = z0
    row = 0
    while z < z1 - 0.05:
        h = min(course, z1 - z)
        s = -rng.uniform(0, 1.2) if row % 2 else 0.0
        while s < Ln - 0.05:
            w = rng.uniform(*blk)
            sa, sb = max(s, 0.0), min(s + w, Ln)
            c = a + dv * ((sa + sb) / 2)
            k = wall_k(c.x, c.y)
            dusk = k > 0.0 and (0.35 * rng.random() + 0.65 * patch(c.x, c.y, 5.1, 0.2)) < k * 1.25
            edge = (row == 0 and z1 - z0 > course * 1.5) or sa <= 0.01 or sb >= Ln - 0.01
            if dusk:
                m = DUSK
            else:
                m = BLOCK_B if (edge or rng.random() < 0.12) else BLOCK
            FP._block(mb, a, dv, ang, sa, sb, z, h, thick, rng, m, BLOCK_B, 0.0, m, None, bevel)
            s += w
        z += h
        row += 1


def trail(mt, mlamp, rng):
    """prateleira (leito + lajes), escada, muro de arrimo, coroamento, parapeito de arenito (trilha) e guarda Capsule
    (so na ligacao, junto da vila)"""
    for rp in DL.exit_shelf_polys():
        DL.prism(mt, rp, G - 0.6, Z - 0.12, BLOCK, top_m=BLOCK_B)
    n = pave_ribbon(mt, PATH, HW, rng, k_trail)
    n += pave_ribbon(mt, LINK, HWL, rng, lambda s: 0.0, other=(L.EXIT_PATH, HW))
    n += link_cap(mt, rng)
    # escada da saida (visual das medidas do db_col): pilaretes de arenito no pe e pilares-lanterna no topo (a entrada
    # do caminho quente ate o portao; as pontas do parapeito encostam neles)
    nm, base, ang, w, nn, rise, tread, g = exit_stair()
    DL.vis_stairs(mt, base, ang, w, nn, rise, tread, PAVE, BLOCK)
    F = DL.Frame(base[0], base[1], base[2], ang)
    for sg in (-1, 1):
        p = F.p(0.6, sg * (w / 2 + 0.6), rise + 1.2)
        mt.cyl(0.62, 1.5, (p.x, p.y, p.z + 0.75), m=BLOCK_B, n=8, bevel=0.0)
        mt.cyl(0.8, 0.3, (p.x, p.y, p.z + 1.65), m=PAVE, n=8, bevel=0.0)
        p = F.p(tread * nn - tread / 2, sg * (w / 2 + 0.6), rise * nn + 1.2)
        mt.box((1.5, 1.5, 1.4), (p.x, p.y, p.z + 0.7), (0, 0, ang), BLOCK_B, 0.0)
        stone_lantern(mt, p.x, p.y, p.z + 1.4, ang, 1.1)
    # muro de arrimo em blocos de arenito (blocos crepusculares em manchas no fim da trilha) + coroamento: Capsule na
    # ligacao (o mesmo da vila), arenito quente na trilha. Nas quinas o coroamento vai ate a quina; o muro vai ate 0,45
    # antes da quina com a vila (o DB_Ter_HubWalls fecha a quina: sem muro dentro do muro dela) e 0,8 alem da quina
    # entre trilha e ligacao (os dois sao daqui)
    TH = 1.5
    off = 0.35 - TH / 2

    def ext_len(c, p):
        if c is None:
            return 0.8
        dd = (Vector((c[1].x, c[1].y, 0.0)) - Vector((p.x, p.y, 0.0))).length
        return max(0.1, dd - 0.45) if c[0] == "hub" else dd + 0.8
    for k, run in wall_runs():
        pl = simplify(run)
        if len(pl) < 2:
            continue
        c0, c1 = corner_of(pl, k, False), corner_of(pl, k, True)
        e0, e1 = ext_len(c0, pl[0]), ext_len(c1, pl[-1])
        segs = list(zip(pl, pl[1:]))
        for i, (a, b) in enumerate(segs):
            d = b - a
            if d.length < 0.5:
                continue
            u = d.normalized()
            nout = Vector((u.y, -u.x, 0.0))
            a2 = a + nout * off - u * (e0 if i == 0 else 0.8)
            b2 = b + nout * off + u * (e1 if i == len(segs) - 1 else 0.8)
            mixed_wall(mt, a2, b2, G - 0.5, Z - 0.78, TH, rng)
        cp = list(pl)
        if c0 and (c0[1] - cp[0]).length > 0.1:
            cp = [c0[1]] + cp
        if c1 and (c1[1] - cp[-1]).length > 0.1:
            cp = cp + [c1[1]]
        path = [Vector((p.x, p.y, Z)) for p in cp]
        for prof, m in COPING[k]:
            mt.sweep(path, prof, m, True)
    # guardas nas linhas do db_col (pontas levadas ate as quinas + colisao propria nesses trechos sem guarda)
    warm = dusk = cols = 0
    for k, run, tags, ext in guard_plan():
        if k == POLY_LINK:
            capsule_guard(mt, run, Z, post_ends=(tags[0] is None, tags[1] is None))
        else:
            w_, d_ = trail_parapet(mt, mlamp, run, rng, tags)
            warm += w_
            dusk += d_
        cols += guard_ext_col(ext)
    print("DB_EXIT guardas: lanternas quentes=%d roxas=%d (+1 por lado no 1o pilar da ponte) colisoes nas quinas=%d" % (
        warm, dusk, cols))
    return n, dusk


# ------------------------------------------------------------------ arco natural
def _need(v):
    """folga horizontal da rocha do arco ate as fitas da prateleira (muro, guarda e vao)"""
    if v.z > Z + 22.6:
        return None
    if v.z < Z - 1.0:
        return HW + 0.5, HWL + 0.5
    if v.z < Z + 0.4:
        return HW + 0.8, HWL + 0.8
    return HW + 1.4, HWL + 1.4


def clear_ok(v):
    nd = _need(v)
    if nd is None:
        return True
    return dp_path(v.x, v.y) >= nd[0] and dp_link(v.x, v.y) >= nd[1]


def clamp_verts(verts, center):
    """encolhe (na horizontal, para o centro da peca) os vertices que invadem a trilha/ligacao"""
    for v in verts:
        if clear_ok(v.co):
            continue
        c = Vector((center.x, center.y, v.co.z))
        d = v.co - c
        s = 1.0
        for _ in range(60):
            s *= 0.95
            q = c + d * s
            if clear_ok(q):
                break
        v.co = c + d * s


def fit_scale(c, r, z0, z1):
    """escala (<= 1) para uma peca de raio r em volta de c caber fora da trilha/ligacao entre z0 e z1"""
    k = 1.0
    for z in (z0, min(z1, Z - 1.1), min(z1, Z + 0.3), z1):
        nd = _need(Vector((0.0, 0.0, z)))
        if nd is None:
            continue
        avail = min(dp_path(c.x, c.y) - nd[0], dp_link(c.x, c.y) - nd[1])
        k = min(k, avail / r)
    return k


def _sgnpow(x, e):
    return math.copysign(abs(x) ** e, x)


def arch_stations():
    """estacoes do loft: (I, E, meia-profundidade, sulco) com I/E = (lat, z) do intradorso e do extradorso.
    Pernas: intradorso quase a prumo, extradorso e profundidade abrem para o chao (pe largo, contraforte natural).
    Arco: superelipses (vao quadrado, lintel achatado) com ombro mais alto no lado sul (assimetria)."""
    st = []
    zs = [G - 2.5, G, ARCH_BANDS[0][0], ARCH_BANDS[0][1], Z + 3.2, ARCH_BANDS[1][0], ARCH_BANDS[1][1], Z_SPRING]
    grooves = {b for bb in ARCH_BANDS for b in bb}

    def leg(s, z):
        f = (Z_SPRING - z) / (Z_SPRING - zs[0])
        li = s * (INTRA[0] + 0.45 * f)
        le = s * (EXTRA[s][0] + 5.2 * f ** 1.7)
        return ((li, z), (le, z), 6.6 + 3.4 * f ** 1.5, 0.95 if z in grooves else 1.0)
    for z in zs:
        st.append(leg(-1, z))
    nA = 24
    for i in range(1, nA):
        th = math.pi * (1.0 - i / nA)
        c, sn = math.cos(th), math.sin(th)
        side = -1 if c < 0 else 1
        W, Hh, e = EXTRA[side]
        li = INTRA[0] * _sgnpow(c, 2.0 / INTRA[2])
        zi = Z_SPRING + INTRA[1] * abs(sn) ** (2.0 / INTRA[2])
        le = W * _sgnpow(c, 2.0 / e)
        ze = Z_SPRING + Hh * abs(sn) ** (2.0 / e)
        ze += 1.7 * math.exp(-((c + 0.42) / 0.26) ** 2) - 0.9 * math.exp(-((c - 0.45) / 0.22) ** 2)
        st.append(((li, zi), (le, ze), 5.3 + 1.9 * abs(c) ** 0.7, 1.0))
    for z in reversed(zs):
        st.append(leg(1, z))
    return st


def arch_clearance(bm):
    """menor altura livre (acima de EXIT_Z) sob o arco, por raios verticais na faixa da trilha"""
    bvh = BVHTree.FromBMesh(bm)
    low = 1e9
    lat = -ARCH_CLEAR[0]
    while lat <= ARCH_CLEAR[0] + 1e-6:
        al = -11.0
        while al <= 11.0 + 1e-6:
            o = apt(lat, Z + 0.5, al)
            hit = bvh.ray_cast(o, Vector((0.0, 0.0, 1.0)), 80.0)
            if hit[0] is not None:
                low = min(low, hit[0].z - Z)
            al += 0.5
        lat += 0.5
    return low


def arch(ma, rng):
    st = arch_stations()
    nS = len(st)
    NV = 12
    E_SUP = 3.2
    seed = Vector((17.3, 4.1, 9.7))
    rings = []
    centers = []
    ups = []                                 # por estacao: componente z da direcao intradorso -> extradorso
    nL = (nS - 23) // 2                      # estacoes de cada perna (o resto e o arco)
    for i, ((li, zi), (le, ze), a, gs) in enumerate(st):
        I = apt(li, zi)
        E = apt(le, ze)
        if nL <= i < nS - nL:
            # espessura e profundidade variam ao longo do arco (so para fora: o intradorso guarda o vao)
            fa = (i - nL) / max(1, nS - 2 * nL - 1)
            E = I + (E - I) * (1.0 + 0.13 * math.sin(2.6 * math.pi * fa + 0.9))
            a *= 1.0 + 0.15 * math.sin(1.9 * math.pi * fa + 2.1)
        ups.append((E - I).normalized().z)
        M = (I + E) / 2
        R = (E - I) / 2
        f = i / (nS - 1)
        sh = 1.3 * math.sin(1.7 * math.pi * f + 0.5) * (0.35 + 0.65 * math.sin(math.pi * f))
        Mc = M + AU * sh
        ring = []
        for k in range(NV):
            ph = math.tau * k / NV + 0.26
            c, s = math.cos(ph), math.sin(ph)
            rr = (abs(c) ** E_SUP + abs(s) ** E_SUP) ** (-1.0 / E_SUP)
            v = Mc + R * (c * rr) + AU * (a * s * rr)
            dv = v - Mc
            # o lado de fora (extradorso) e mais irregular que o intradorso (que guarda o vao); o sofito quase liso
            # (sombreado coeso de baixo, sem facetas alternando claro/escuro)
            amp = 0.7 + 0.6 * max(0.0, c) - 0.4 * max(0.0, -c) ** 2
            nz = amp * (0.12 * noise.noise(v * 0.075 + seed) + 0.055 * noise.noise(v * 0.25 + seed * 2.0))
            v = Mc + dv * ((1.0 + nz) * gs)
            ring.append(ma.bm.verts.new(v))
        rings.append(ring)
        centers.append(Mc)
    # a rocha nao invade a trilha/ligacao (muro, guarda, vao): ajuste radial so onde precisa
    for ring, Mc in zip(rings, centers):
        clamp_verts(ring, Mc)
    seg = {}
    for i in range(nS - 1):
        r0, r1 = rings[i], rings[i + 1]
        cc = (centers[i] + centers[i + 1]) / 2
        for k in range(NV):
            j = (k + 1) % NV
            f = ma.bm.faces.new((r0[k], r0[j], r1[j], r1[k]))
            f.normal_update()
            if f.normal.dot(f.calc_center_median() - cc) < 0:
                f.normal_flip()
            seg[f] = (i, k)
    # material pela ESTRUTURA do loft (nunca pela normal/centro de cada face: era o xadrez do lintel).
    # Anel: face k centrada na fase 30k + 30 graus -> k 10/11/0 = extradorso (crista), 4/5/6 = intradorso (sofito),
    # 1/2/3 e 7/8/9 = as faces da frente e de tras.
    groups = {ROCK: [], DARK: [], TOP: [], GRASS: []}
    arc_rock = []
    zst = [s_[0][1] for s_ in st]
    for f, (i, k) in seg.items():
        if i < nL - 1 or i >= nS - nL:
            # perna: aneis horizontais nas cotas dos estratos -> faixa = um segmento inteiro do loft
            za, zb = sorted((zst[i], zst[i + 1]))
            if zb <= G + 1e-6 or any(abs(za - b0) < 1e-6 and abs(zb - b1) < 1e-6 for b0, b1 in ARCH_BANDS):
                groups[DARK].append(f)
            else:
                groups[ROCK].append(f)
            continue
        u = 0.5 * (ups[i] + ups[i + 1])
        if k in (4, 5, 6) and u > 0.35:
            groups[DARK].append(f)                      # sofito (o intradorso virado para baixo)
        elif k in (10, 11, 0) and u > 0.5:
            groups[GRASS if (k == 11 and u > 0.8) else TOP].append(f)      # crista: grama no meio, borda clara
        else:
            arc_rock.append(f)
    # estratos do arco: planos horizontais cortam as faces de arenito (ombros e lintel) -> faixas retas continuas
    geom_f = arc_rock
    for zc in sorted({b for bb in ARCH_BANDS[2:] for b in bb}):
        geom_f = [f for f in geom_f if f.is_valid]
        ed = {e for f in geom_f for e in f.edges}
        vs = {v for f in geom_f for v in f.verts}
        res = bmesh.ops.bisect_plane(ma.bm, geom=list(vs) + list(ed) + geom_f, dist=0.1,
                                     plane_co=(0.0, 0.0, zc), plane_no=(0.0, 0.0, 1.0))
        geom_f = [g for g in res["geom"] if isinstance(g, bmesh.types.BMFace)]
    for f in geom_f:
        if not f.is_valid:
            continue
        f.normal_update()
        zc = f.calc_center_median().z
        groups[DARK if any(b0 <= zc <= b1 for b0, b1 in ARCH_BANDS[2:]) else ROCK].append(f)
    for m, fs in groups.items():
        assign(ma, fs, m, variant=(m == ROCK))
        box_uv(ma, fs, m, AC + Vector((0.0, 0.0, Z)), AU, AN)
    clear = arch_clearance(ma.bm)
    print("DB_EXIT arco: vao livre sobre a trilha (|lat| <= %.1f) = %.2f acima de EXIT_Z (exigido %.1f)" % (
        ARCH_CLEAR[0], clear, ARCH_CLEAR[1]))
    # massas secundarias: contrafortes no pe (primario + secundario + quebra), ombro na perna sul, degrau na crista
    pieces = [
        # (lat, along, a (ao longo), b (lateral), z0, z1, material, banda, tampa de grama)
        (-25.2, 3.4, 4.6, 3.4, G - 1.0, G + 10.0, ROCK, True, False),
        (-17.8, -9.6, 3.6, 2.6, G - 1.0, G + 6.4, ROCK, True, False),
        (-23.4, -3.2, 3.2, 2.6, G - 1.0, Z + 7.5, ROCK, True, False),
        (23.6, -4.2, 3.9, 2.8, G - 1.0, G + 8.2, ROCK, True, False),
        (22.4, -10.6, 3.2, 2.3, G - 1.0, Z + 4.0, ROCK, True, False),
        (14.6, -10.8, 3.0, 2.2, G - 1.0, G + 4.8, DARK, False, False),
    ]
    n_loft = nverts(ma)
    piece_rng = []                            # (primeiro vertice, fim, lado, topo) de cada contraforte
    for lat, al, a, b, z0, z1, m, band, lid in pieces:
        c = apt(lat, 0.0, al)
        k = fit_scale(c, max(a, b) * 1.1, z0, z1)
        if k < 0.45:
            continue                  # nao cabe fora da trilha/ligacao: sem lasca fina solta
        a, b = a * min(1.0, k), b * min(1.0, k)
        n0 = nverts(ma)
        poly = FP._to_world(FP._rock_poly(a, b, 7, rng, ex=2.3, jit=0.12), AU, AN)
        # as pecas altas encostam na perna (o topo inclina para ela): massa secundaria, nao pilar solto
        leg_c = apt(math.copysign((INTRA[0] + EXTRA[1 if lat > 0 else -1][0]) / 2, lat), 0.0, 0.0)
        lv = Vector((leg_c.x - c.x, leg_c.y - c.y, 0.0))
        lean = tuple((lv.normalized() * min(2.2, 0.12 * (z1 - z0))).xy) if lv.length > 1e-3 else None
        FP.rock_column(ma, Vector((c.x, c.y, 0.0)), poly, z0, z1, rng, m, taper=0.78, rings=2, jitter=0.1,
                       tilt=0.12, lean=lean, chamfer=0.4, rim=False, band=((1.1, TOP) if band else None),
                       bottom=False)
        clamp_verts(new_verts(ma, n0), c)
        piece_rng.append((n0, nverts(ma), 1 if lat > 0 else -1, z1))
    # degrau quebrado na crista (lado sul, onde o lintel e mais alto) com tampa de grama
    top_v = max((v.co.copy() for ring in rings[nS // 2 - 5:nS // 2 - 1] for v in ring), key=lambda q: q.z)
    poly = FP._to_world(FP._rock_poly(4.8, 3.3, 7, rng, ex=2.2, jit=0.1), AU, AN)
    FP.rock_column(ma, Vector((top_v.x, top_v.y, 0.0)) + AU * 1.0, poly, top_v.z - 2.4, top_v.z + 2.2, rng, ROCK,
                   taper=0.85, rings=1, jitter=0.08, tilt=0.06, top_m=GRASS, lip=0.5, rim=False,
                   tongues=(2, GRASS, (0.8, 1.8), None), bottom=False)
    # pedras de quebra no pe (encostadas, meio enterradas)
    for lat, al, sz in ((-27.4, -3.0, 2.2), (17.4, -9.8, 1.8), (-13.2, 9.6, 1.6)):
        c = apt(lat, G - 0.2, al)
        if fit_scale(c, sz * 0.9, G - 1.0, G + sz) < 1.0:
            continue
        n0 = nverts(ma)
        ma.rock((c.x, c.y, c.z + sz * 0.2), (sz * 1.5, sz * 1.1, sz * 0.9), ROCK, 1, (0, 0, rng.uniform(0, 6.28)),
                jitter=0.25)
        clamp_verts(new_verts(ma, n0), c)
    # colisao do pe de cada perna: faixas ajustadas a rocha REAL (medida por raios na malha do loft + contrafortes
    # entre G+1 e G+6, recuadas 0,4); as caixas grandes de antes passavam 2,6-6,5 da rocha (paredes invisiveis)
    nb = arch_foot_cols(ma, n_loft, piece_rng)
    for s in (-1, 1):
        lat = s * (INTRA[0] + EXTRA[s][0] + 1.6) / 2
        for al in (-2.7, 2.7):
            c = apt(lat, 0.0, al)
            r = min(5.8, dp_path(c.x, c.y) - (HW + 0.55), dp_link(c.x, c.y) - (HWL + 0.55))
            if r > 1.0:
                octo_col("DB_ExitArch", c.x, c.y, r, G + 6.0, Z + 10.0)
    # face de dentro da perna norte acima da caixa do pe (G+7..G+10, lat ~12-16): octogono extra
    c = apt(14.2, 0.0, 2.4)
    r = min(3.0, dp_path(c.x, c.y) - (HW + 0.55), dp_link(c.x, c.y) - (HWL + 0.55))
    if r > 1.0:
        octo_col("DB_ExitArch", c.x, c.y, r, G + 6.0, Z + 10.0)
    # contrafortes altos (acima de G+6, fora dos octogonos): faixas ajustadas a cada um
    nb += arch_buttress_cols(ma, piece_rng)
    print("DB_EXIT arco: colisao do pe ajustada a rocha = %d caixas" % nb)
    return clear


# ------------------------------------------------------------------ colisao do arco ajustada a rocha
# pe das pernas em 2 andares (o pe alarga para o chao: um andar so, medido na cota mais estreita, deixava o jogador
# entrar ~2 na rocha embaixo): (z0, z1 da caixa, cotas medidas)
FOOT_TIERS = [(G - 1.0, G + 6.3, [G + 1.0 + i for i in range(6)])]
FOOT_W = 2.4


def _hits_along(bvh, o, d, maxd):
    ts = []
    t = 0.0
    while t < maxd and len(ts) < 32:
        h = bvh.ray_cast(o + d * t, d, maxd - t)
        if h[0] is None:
            break
        t += h[3]
        ts.append(t)
        t += 1e-3
    return ts


def _iv_union(iv):
    out = []
    for a, b in sorted(iv):
        if out and a <= out[-1][1] + 1e-6:
            out[-1] = (out[-1][0], max(out[-1][1], b))
        else:
            out.append((a, b))
    return out


def _iv_inter(A, B):
    out = []
    i = j = 0
    while i < len(A) and j < len(B):
        a, b = max(A[i][0], B[j][0]), min(A[i][1], B[j][1])
        if b > a:
            out.append((a, b))
        if A[i][1] < B[j][1]:
            i += 1
        else:
            j += 1
    return out


def _piece_bvhs(mb, ranges):
    """uma BVH por peca (faixa de vertices): dentro/fora por paridade vale por peca fechada; a uniao e feita depois"""
    bm = mb.bm
    bm.verts.index_update()
    co = [v.co.copy() for v in bm.verts]
    polys = [[] for _ in ranges]
    for f in bm.faces:
        i0 = min(v.index for v in f.verts)
        for k, (a, b) in enumerate(ranges):
            if a <= i0 < b:
                polys[k].append([v.index for v in f.verts])
                break
    return [BVHTree.FromPolygons(co, p) if p else None for p in polys]


def _solid(bvhs, lats, heights, a_lo=-40.0, a_len=80.0):
    """por linha lateral (lat): intervalos ao longo do arco (AU) com rocha em TODAS as cotas (uniao das pecas; entrada/
    saida por pares de acertos - os raios horizontais nunca passam pelas bocas abertas, que ficam abaixo de G)"""
    out = {}
    for lt in lats:
        acc = None
        for z in heights:
            o = apt(lt, z, a_lo)
            ivs = []
            for bv in bvhs:
                if bv is None:
                    continue
                ts = _hits_along(bv, o, AU, a_len)
                ivs += [(a_lo + ts[i], a_lo + ts[i + 1]) for i in range(0, len(ts) - 1, 2)]
            u = _iv_union(ivs)
            acc = u if acc is None else _iv_inter(acc, u)
            if not acc:
                break
        out[lt] = acc or []
    return out


def _fit_strips(lines, lats, inset=0.35, W=2.4, minW=0.8, amin=0.9):
    """faixas (lat_a, lat_b, along_a, along_b) DENTRO da rocha: cada faixa usa a intersecao das linhas que cobre (+ o
    recuo dos lados), recuada 'inset' nas pontas; faixa larga que perde muito na ponta arredondada e dividida"""
    rock = [lt for lt in lats if lines[lt]]
    if not rock:
        return []
    lo, hi = min(rock), max(rock)

    def strip(la, lb):
        acc = None
        for lt in lats:
            if la - inset - 1e-6 <= lt <= lb + inset + 1e-6:
                acc = lines[lt] if acc is None else _iv_inter(acc, lines[lt])
                if not acc:
                    return []
        return [(a + inset, b - inset) for a, b in (acc or []) if b - a - 2 * inset >= amin]

    def tot(iv):
        return sum(b - a for a, b in iv)
    out = []

    def fit(la, lb):
        iv = strip(la, lb)
        if lb - la >= 2 * minW:
            m = (la + lb) / 2
            i1, i2 = strip(la, m), strip(m, lb)
            if tot(iv) < 0.8 * max(tot(i1), tot(i2)):
                fit(la, m)
                fit(m, lb)
                return
        out.extend((la, lb, a, b) for a, b in iv)
    la = lo + inset
    while la < hi - inset - 0.3:
        lb = min(la + W, hi - inset)
        fit(la, lb)
        la = lb
    # junta faixas vizinhas quase iguais (menos caixas)
    out.sort()
    merged = []
    for bx in out:
        for i, m in enumerate(merged):
            if abs(m[1] - bx[0]) < 1e-6 and abs(m[2] - bx[2]) < 0.45 and abs(m[3] - bx[3]) < 0.45:
                merged[i] = (m[0], bx[1], max(m[2], bx[2]), min(m[3], bx[3]))
                break
        else:
            merged.append(bx)
    return merged


def _clear_box(la, lb, a0, a1, amin=0.9):
    """encolhe a faixa (ao longo) ate nenhum canto/meio de lado entrar na trilha/ligacao (+0,55); None se nao da"""
    def ok(a, b):
        for lt in (la, (la + lb) / 2, lb):
            for al in (a, (a + b) / 2, b):
                q = apt(lt, 0.0, al)
                if dp_path(q.x, q.y) < HW + 0.55 or dp_link(q.x, q.y) < HWL + 0.55:
                    return False
        return True
    while a1 - a0 >= amin:
        if ok(a0, a1):
            return a0, a1
        a0 += 0.25
        if ok(a0, a1):
            return a0, a1
        a1 -= 0.25
    return None


def _emit(strips, z0, z1):
    rot = (0, 0, math.atan2(AU.y, AU.x))
    n = 0
    for la, lb, a0, a1 in strips:
        r = _clear_box(la, lb, a0, a1)
        if r is None:
            continue
        a0, a1 = r
        c = apt((la + lb) / 2, (z0 + z1) / 2, (a0 + a1) / 2)
        col_box("DB_ExitArch", (a1 - a0, lb - la, z1 - z0), (c.x, c.y, c.z), rot)
        n += 1
    return n


def arch_foot_cols(ma, n_loft, piece_rng):
    """pe de cada perna (G-1 .. G+6,3, encosta nos octogonos que comecam em G+6): faixas ajustadas a rocha (loft + os
    contrafortes do lado) medida em G+1..G+6"""
    bv = _piece_bvhs(ma, [(0, n_loft)] + [(a, b) for a, b, s, z1 in piece_rng])
    n = 0
    for s in (-1, 1):
        lats = [s * 8.0 + s * 0.25 * i for i in range(105)]
        lats.sort()
        for z0, z1, heights in FOOT_TIERS:
            # uniao das pecas, cada uma medida nas cotas que ela alcanca (o contraforte afina e inclina para a perna
            # perto do topo: medido junto com a perna, ele sumia da colisao)
            lines = _solid([bv[0]], lats, heights)
            for i, (a, b, ss, zt) in enumerate(piece_rng):
                if ss != s or zt < G + 6.3:
                    continue
                hs = [h for h in heights if h <= zt - 0.8] or [heights[0]]
                pl = _solid([bv[i + 1]], lats, hs)
                lines = {lt: _iv_union(lines[lt] + pl[lt]) for lt in lats}
            n += _emit(_fit_strips(lines, lats, W=FOOT_W), z0, z1)
        # contraforte baixo (topo < G+6,3): caixa propria ate 0,4 abaixo do topo dele (nada de parede acima da rocha)
        for i, (a, b, ss, z1) in enumerate(piece_rng):
            if ss != s or z1 >= G + 6.3 or z1 < G + 2.5:
                continue
            ma.bm.verts.ensure_lookup_table()
            lat_c = sum(AN.dot(ma.bm.verts[j].co - AC) for j in range(a, b)) / max(1, b - a)
            pl = [lat_c - 6.0 + 0.25 * j for j in range(49)]
            hs = [G + 1.0 + 0.8 * j for j in range(8) if G + 1.0 + 0.8 * j <= z1 - 0.6]
            n += _emit(_fit_strips(_solid([bv[i + 1]], pl, hs), pl, W=3.0), G - 1.0, z1 - 0.4)
    return n


def arch_buttress_cols(ma, piece_rng):
    """contrafortes altos (topo >= G+9): faixas de G+6 ate perto do topo, ajustadas a cada um (acima do pe)"""
    n = 0
    for i, (a, b, s, z1) in enumerate(piece_rng):
        if z1 < G + 9.0:
            continue
        bv = _piece_bvhs(ma, [(a, b)])
        ma.bm.verts.ensure_lookup_table()
        lat_c = sum(AN.dot(ma.bm.verts[j].co - AC) for j in range(a, b)) / max(1, b - a)
        lats = [lat_c - 7.0 + 0.25 * j for j in range(57)]
        heights = []
        z = G + 6.5
        while z <= z1 - 1.2 + 1e-6:
            heights.append(z)
            z += 1.0
        if not heights:
            continue
        lines = _solid(bv, lats, heights)
        n += _emit(_fit_strips(lines, lats, W=3.0), G + 6.0, heights[-1] + 0.4)
    return n


# ------------------------------------------------------------------ transicao: arvores secas
# (x, y, altura); o build afasta a arvore da trilha se algum galho entrar na prateleira (tree_clear)
DRY_TREES = [(137.0, 88.0, 13.5), (145.0, 55.0, 11.5)]


def tree_clear(verts):
    """nenhum vertice de galho acima de Z-0,5 dentro da prateleira/ligacao (+0,4 de folga alem da guarda)"""
    return all(v.co.z <= Z - 0.5 or (dp_path(v.co.x, v.co.y) > HW + 0.4 and dp_link(v.co.x, v.co.y) > HWL + 0.4)
               for v in verts)


def dry_trees(ma, rng):
    for x, y, h in DRY_TREES:
        # afasta da trilha (direcao do centro da trilha para a arvore) ate os galhos ficarem fora do piso
        pq, _ = PATH.at(PATH.param(x, y))
        away = Vector((x - pq.x, y - pq.y, 0.0)).normalized()
        for step in range(6):
            tx, ty = x + away.x * 1.5 * step, y + away.y * 1.5 * step
            st = rng.getstate()
            n0 = nverts(ma)
            VK.dead_tree(ma, (tx, ty, G), h, rng, lod=0)
            nv = new_verts(ma, n0)
            if tree_clear(nv) or step == 5:
                if step == 5:
                    print("DB_EXIT AVISO: arvore seca em (%.1f, %.1f) ainda invade a prateleira" % (tx, ty))
                break
            bmesh.ops.delete(ma.bm, geom=nv, context="VERTS")
            rng.setstate(st)
        x, y = tx, ty
        # pedras de pe (o tronco nao nasce da areia lisa)
        for k in range(3):
            a = rng.uniform(0, math.tau)
            r = rng.uniform(1.4, 2.4)
            sz = rng.uniform(0.9, 1.5)
            ma.rock((x + math.cos(a) * r, y + math.sin(a) * r, G + sz * 0.15), (sz * 1.5, sz * 1.2, sz * 0.8),
                    DARK if k % 2 else ROCK, 1, (0, 0, a), jitter=0.25)
        col_box("DB_ExitTree", (1.8, 1.8, 7.0), (x, y, G + 3.5))


# ------------------------------------------------------------------ ponte
PIERS = [17.0, 37.0]
POSTS = [0.6, 11.0, 21.5, 32.0, 42.5, 53.0, 62.4]
LAT_G = L.EXIT_W / 2 + 0.6               # linha da guarda da ponte (db_col)
D_BR1 = 62.0                              # fim do calcamento da ponte (a ilhota cobre dai para frente)


def bridge_post0():
    """os 2 primeiros pilares do parapeito da ponte (d = POSTS[0]): o parapeito da trilha termina dentro deles"""
    return [ep(POSTS[0], sg * LAT_G, Z) for sg in (-1, 1)]


def dusk_at(d, lat, bias=0.0):
    """pedra crepuscular aqui? manchas continuas cujo tamanho cresce com k_bridge(d); junto da ilhota (d > 50,
    k >= 0,94) e sempre crepuscular (o patch satura em 1: sobravam blocos de arenito ao lado da ilhota)"""
    if d > 50.0:
        return True
    q = ep(d, lat)
    return patch(q.x, q.y, 3.3, 0.11) < k_bridge(d) + bias


def bridge(mb, rng):
    d0 = -3.0
    # corpo do tabuleiro (nucleo escuro) + fundo
    ln = D_BR1 - d0
    c = ep((d0 + D_BR1) / 2, 0.0, Z - 1.37)
    mb.box((ln, 20.2, 2.5), (c.x, c.y, c.z), (0, 0, YAW), BLOCK_B, 0.0)
    # encontro no penhasco (o tabuleiro entra na ilha): bloco de alvenaria descendo, recuado atras do plano do
    # paramento (nao salta para fora sob a faixa azul)
    c = ep(-2.5, 0.0, Z - 8.0)
    mb.box((7.0, 19.4, 11.0), (c.x, c.y, c.z), (0, 0, YAW), BLOCK, 0.1)
    # paramento em blocos nas duas faces (Z-2,62 .. Z-0,5): arenito -> crepuscular em manchas
    for s in (-1, 1):
        for zc, hh in ((Z - 2.09, 1.06), (Z - 1.03, 1.06)):
            d = d0 + (rng.uniform(0.6, 1.6) if zc > Z - 1.5 else 0.0)
            while d < D_BR1 - 0.3:
                bl = min(rng.uniform(2.8, 4.6), D_BR1 - d)
                m = DUSK if dusk_at(d + bl / 2, s * 10.25, -0.1) else BLOCK
                q = ep(d + bl / 2, s * 10.25, zc)
                mb.box((bl - 0.12, 0.55, hh - 0.1), (q.x, q.y, q.z), (0, 0, YAW), m, 0.08)
                d += bl
        # coroamento no MESMO perfil do da trilha (capa de laje clara Z-0,52..Z+0,15 + faixa de bloco escuro
        # Z-1,0..Z-0,46): a borda da prateleira e a da ponte leem como uma linha so, em arenito quente (o Capsule
        # branco/azul fica so na ligacao com a vila); crepuscular depois de d 24
        for da, db_, m in ((d0, 24.0, PAVE), (24.0, D_BR1, DUSK)):
            q = ep((da + db_) / 2, s * 9.8, Z - 0.185)
            mb.box((db_ - da, 1.86, 0.67), (q.x, q.y, q.z), (0, 0, YAW), m, 0.0)
        q = ep((d0 + 24.0) / 2, s * 10.6, Z - 0.73)
        mb.box((24.0 - d0, 0.48, 0.54), (q.x, q.y, q.z), (0, 0, YAW), BLOCK_B, 0.0)
    # calcamento: fileiras atravessadas (juntas desencontradas), arenito claro -> pedra crepuscular.
    # A primeira fileira comeca antes da borda (d -2, onde comeca o piso da ponte) e e recortada na ultima fileira
    # da trilha (rumo 31 x 22 graus): a cunha entre as duas fica calcada, sem leito a vista.
    te = Vector((L.EXIT_PATH[-1][0] - L.EXIT_PATH[-2][0], L.EXIT_PATH[-1][1] - L.EXIT_PATH[-2][1], 0.0)).normalized()
    end_plane = (-te.x, -te.y, -(te.x * S0.x + te.y * S0.y) - 0.09)
    d = -2.0
    row = 0
    while d < D_BR1 - 0.4:
        dep = min(rng.choice((1.8, 2.0, 2.2)), D_BR1 - d)
        cuts = [-9.0] + ([-4.5, 0.0, 4.5] if row % 2 == 0 else [-3.0, 3.0]) + [9.0]
        cuts = [cuts[0]] + [cc + rng.uniform(-0.4, 0.4) for cc in cuts[1:-1]] + [cuts[-1]]
        kk = k_bridge(d + dep / 2)
        for la, lb in zip(cuts, cuts[1:]):
            hh = 0.3 + rng.uniform(-0.03, 0.03)
            q = ep(d + dep / 2, (la + lb) / 2, Z + 0.1 - hh / 2)
            dk = (0.2 * rng.random() + 0.8 * patch(q.x, q.y, 7.7, 0.09)) < kk
            m = DUSK if (dk or d + dep / 2 > 50.0) else PAVE
            slab_out(mb, q, U, N, dep - 0.18, lb - la - 0.18, hh, YAW + rng.uniform(-0.01, 0.01), m,
                     [end_plane] if d < 3.0 else [])
        d += dep
        row += 1
    # parapeito nas linhas da guarda (db_col: +-9,6, d 1..63): blocos + capa + pilares
    for s in (-1, 1):
        for pa, pb in zip(POSTS, POSTS[1:]):
            a, b = pa + 0.95, pb - 0.95
            nb = max(1, int(round((b - a) / 2.5)))
            for i in range(nb):
                da = a + (b - a) * i / nb
                db_ = a + (b - a) * (i + 1) / nb
                q = ep((da + db_) / 2, s * LAT_G, Z + 0.72)
                m = DUSK if dusk_at((da + db_) / 2, s * LAT_G) else BLOCK
                mb.box((db_ - da - 0.1, 1.15, 1.44), (q.x, q.y, q.z), (0, 0, YAW), m, 0.1)
            kk = k_bridge((a + b) / 2)
            cap = PAVE if kk < 0.6 else (DUSK if kk < 0.86 else SHADOW)
            q = ep((a + b) / 2, s * LAT_G, Z + 1.44 + 0.15)
            mb.box((b - a + 0.1, 1.45, 0.3), (q.x, q.y, q.z), (0, 0, YAW), cap, 0.06)
        for d in POSTS:
            kk = k_bridge(d)
            body = BLOCK if kk < 0.6 else DUSK
            q = ep(d, s * LAT_G, 0.0)
            mb.box((1.9, 1.9, 0.5), (q.x, q.y, Z + 0.25), (0, 0, YAW), BLOCK_B if kk < 0.6 else SHADOW, 0.06)
            mb.box((1.6, 1.6, 2.0), (q.x, q.y, Z + 0.5 + 1.0), (0, 0, YAW), body, 0.12)
            if d > 60.0:
                lc = dusk_lamp(mb, Vector((q.x, q.y, Z + 2.5)), YAW, 1.0)
                light("L_DBExit_DuskLamp_%s" % ("N" if s > 0 else "S"), "POINT", lc + Vector((0, 0, 0.3)), 90.0,
                      (0.62, 0.32, 1.0), 0.4)
            elif d == POSTS[0]:
                # a lanterninha roxa do fim da trilha (transicao Shadow Garden): o parapeito da trilha entra neste pilar
                dusk_lamp(mb, Vector((q.x, q.y, Z + 2.5)), YAW, 0.8)
            else:
                mb.box((1.95, 1.95, 0.3), (q.x, q.y, Z + 2.65), (0, 0, YAW), PAVE if kk < 0.6 else DUSK, 0.06)
    # consoles sob a cornija (ritmo embaixo do tabuleiro)
    for s in (-1, 1):
        d = 2.0
        while d < D_BR1 - 1.0:
            if all(abs(d - p) > 4.6 for p in PIERS):
                q = ep(d, s * 9.9, Z - 3.1)
                mb.box((0.9, 1.1, 1.0), (q.x, q.y, q.z), (0, 0, YAW), DUSK if dusk_at(d, s * 10.0) else BLOCK, 0.0)
            d += 4.0


def piers(mb, rng):
    """pilares de rocha pendurados (agulhas de arenito que somem nas nuvens), capitel de alvenaria sob o tabuleiro,
    tambores com ressalto (barriga) e sulcos de estrato, lascas laterais; o ultimo ja na pedra crepuscular"""
    for i, d in enumerate(PIERS):
        kk = k_bridge(d)
        dusk = kk > 0.62
        m, groove, band = (RDUSK, SHADOW, DUSK) if dusk else (ROCK, BLOCK_B, BLOCK)
        cap_m = DUSK if dusk else BLOCK
        q = ep(d, 0.0, 0.0)
        # capitel (2 lajes em degrau)
        mb.box((7.4, 18.8, 0.9), (q.x, q.y, Z - 2.62 - 0.45), (0, 0, YAW), cap_m, 0.1)
        mb.box((6.4, 16.2, 0.8), (q.x, q.y, Z - 3.52 - 0.4), (0, 0, YAW), cap_m, 0.1)
        base = FP._to_world(FP._rock_poly(7.8, 5.2, 10, rng, ex=2.5, jit=0.09, a0=0.1), N, U)
        z_top = Z - 4.3
        # (cota de baixo, escala de cima, escala de baixo): afunila sempre para baixo (so um leve ressalto na
        # junta), com o eixo derivando de lado a cada tambor (agulha torta, nao pilha de funis)
        tiers = [(z_top - 13.0 - i * 2.0, 1.0, 0.9), (z_top - 27.0 - i * 3.0, 0.92, 0.76),
                 (z_top - 40.0 - i * 4.0, 0.78, 0.56), (z_top - 56.0 - i * 5.0, 0.58, 0.1)]
        zc = z_top
        c = Vector((q.x, q.y, 0.0))
        drift = [Vector((0.0, 0.0, 0.0)), U * 0.9 + N * 0.5, U * 1.4 - N * 0.3, U * 0.8 - N * 1.0]
        for k, (zb, s_top, s_bot) in enumerate(tiers):
            ck = c + drift[k]
            poly = [(x * s_bot, y * s_bot) for x, y in base]
            FP.rock_column(mb, ck, poly, zb, zc, rng, m, taper=s_top / s_bot, rings=1, jitter=0.08, tilt=0.0,
                           chamfer=0.0, rim=False, band=((1.4, band) if k < 2 else None),
                           bottom=(k == len(tiers) - 1))
            if k < len(tiers) - 1:
                FP.rock_column(mb, ck, [(x * s_bot * 0.96, y * s_bot * 0.96) for x, y in base], zb - 1.3, zb + 0.2,
                               rng, groove, taper=1.0, rings=1, jitter=0.04, tilt=0.0, chamfer=0.0, rim=False,
                               bottom=False)
            zc = zb - 1.0
        # lascas penduradas nas faces largas (quebram o fuste)
        for sg in (-1, 1):
            cc = c + N * (sg * 6.4) + U * rng.uniform(-1.2, 1.2)
            poly = FP._to_world(FP._rock_poly(2.4, 1.8, 6, rng, ex=2.2, jit=0.1), U, N)
            zt = z_top - rng.uniform(5.0, 9.0)
            FP.rock_column(mb, cc, poly, zt - rng.uniform(12.0, 18.0), zt, rng, m, taper=2.6, rings=1, jitter=0.1,
                           tilt=0.05, chamfer=0.3, rim=False, band=(0.8, band), bottom=True)


# ------------------------------------------------------------------ ilhota do portao
def islet_guard_runs():
    """as MESMAS linhas da guarda da ilhota (db_col.bridges: 24-gono r 22, aberta na ponte e no corredor da
    ancora), menos o trecho dentro da pegada do portao (os plintos dele fazem a borda ali)"""
    ic = L.islet_center()
    isl = [(ic[0] + R_ISLET * math.cos(t * math.pi / 12), ic[1] + R_ISLET * math.sin(t * math.pi / 12))
           for t in range(24)]
    bs = L.exit_point(L.EXIT_BRIDGE_LEN)

    def keep(x, y):
        t = (x - bs[0]) * UX + (y - bs[1]) * UY
        d = abs(-(x - bs[0]) * UY + (y - bs[1]) * UX)
        if d < L.EXIT_W / 2 + 0.6 and (t < 3.0 or t > L.ANCHOR_OFF - 14.0):
            return False
        dd, lat = to_dl(x, y)
        return not in_gate(dd, lat, 0.9)
    return db_col._runs(ccw(isl), keep, step=1.0)


def stone_parapet(mb, run, z, mfn, cap_fn, post_step=9.0, lamp_fn=None, h=1.5, w=1.15):
    """parapeito de blocos + capa + pilares (lanterninha roxa onde lamp_fn manda)"""
    pl = simplify([Vector((p.x, p.y, z)) for p in run], 0.02)
    marks = run_marks(pl, 2.5)
    for (a, ang, sa), (b, _, sb) in zip(marks, marks[1:]):
        mid = (a + b) / 2
        ln = (b - a).length
        an = math.atan2(b.y - a.y, b.x - a.x)
        mb.box((ln - 0.1, w, h), (mid.x, mid.y, z + h / 2), (0, 0, an), mfn(mid.x, mid.y), 0.1)
        mb.box((ln + 0.02, w + 0.28, 0.28), (mid.x, mid.y, z + h + 0.14), (0, 0, an), cap_fn(mid.x, mid.y), 0.0)
    lamps = 0
    for q, ang, s in run_marks(pl, post_step):
        mb.box((1.7, 1.7, h + 0.7), (q.x, q.y, z + (h + 0.7) / 2), (0, 0, ang), mfn(q.x, q.y), 0.12)
        if lamp_fn is not None and lamp_fn(q.x, q.y):
            dusk_lamp(mb, Vector((q.x, q.y, z + h + 0.7)), ang, 0.9)
            lamps += 1
        else:
            mb.box((1.95, 1.95, 0.3), (q.x, q.y, z + h + 0.85), (0, 0, ang), cap_fn(q.x, q.y), 0.05)
    return lamps


def islet(mi, rng):
    ic = L.islet_center()
    # leito escuro (rejunte negro-violeta entre as lajes) sobre corpo crepuscular
    circ = [(ic[0] + (R_ISLET + 0.4) * math.cos(t * math.pi / 16), ic[1] + (R_ISLET + 0.4) * math.sin(t * math.pi / 16))
            for t in range(32)]
    DL.prism(mi, circ, Z - 1.6, Z - 0.12, DUSK, top_m=SHADOW)
    # bastiao da ancora (plataforma 10 x 18 da planta + ombros onde assentam os pilones da guarda)
    BW = 12.8
    da, db_ = D_ANCHOR - 12.0, D_ANCHOR
    corners = [ep(da, -BW), ep(db_, -BW), ep(db_, BW), ep(da, BW)]
    DL.prism(mi, [(p.x, p.y) for p in corners], Z - 7.0, Z - 0.12, DUSK, top_m=SHADOW)
    # o bastiao assenta numa massa de rocha que sai da ilhota (nada de alvenaria pendurada no vazio)
    q = ep(db_ - 6.5, 0.0, 0.0)
    poly = FP._to_world(FP._rock_poly(7.2, 12.6, 9, rng, ex=2.6, jit=0.06, a0=0.0), U, N)
    FP.rock_column(mi, Vector((q.x, q.y, 0.0)), [(x * 0.55, y * 0.55) for x, y in poly], Z - 24.0, Z - 6.9, rng,
                   RDUSK, taper=1.0 / 0.55, rings=2, jitter=0.06, tilt=0.0, lean=(-U.x * 5.0, -U.y * 5.0),
                   chamfer=0.0, rim=False, band=(1.0, DUSK), bottom=True)
    # face da cabeceira (d = ancora) em blocos, com o miolo liso (onde encosta a proxima ponte)
    for k, zc in enumerate((Z - 1.0, Z - 2.25, Z - 3.5, Z - 4.75, Z - 6.0)):
        lat = -BW + (0.0 if k % 2 == 0 else 1.3)
        while lat < BW - 0.6:
            ln = min(rng.uniform(2.2, 3.8), BW - lat)
            if (lat + ln < -9.8 or lat > 9.8 or zc < Z - 3.2) and ln > 0.9:
                p = ep(db_ + 0.02, lat + ln / 2, zc)
                mi.box((0.3, ln - 0.16, 1.05), (p.x, p.y, p.z), (0, 0, YAW), SHADOW if rng.random() < 0.3 else DUSK, 0.0)
            lat += ln
    # lajes em grade (juntas desencontradas) alinhadas com a saida. As lajes que encostam na pegada do portao, na
    # ponte ou na borda NAO saem inteiras: sao recortadas (retangulos do portao/ponte no referencial (d, lat), circulo
    # por semiplanos tangentes) - o leito so aparece como rejunte, inclusive na frente da soleira.
    tile = 2.9
    d = L.EXIT_BRIDGE_LEN - 4.2
    row = 0
    n = 0
    RC = R_ISLET - 0.75
    LP = LAT_G - 0.62                                   # meia-largura calcada da plataforma da ancora
    DP1 = D_ANCHOR - 0.15
    holes = [(-1e9, D_BR1 + 0.05, -10.5, 10.5)]         # a ponte (o calcamento dela vai ate D_BR1)
    for x0, x1, y0, y1 in GATE_RECTS:
        for sg in (1, -1):
            la, lb = sorted((sg * (x0 - 0.15), sg * (x1 + 0.15)))
            holes.append((D_GATE + y0 - 0.15, D_GATE + y1 + 0.15, la, lb))
    NC = 72
    circ_all = []
    for k in range(NC):
        a = math.tau * (k + 0.5) / NC
        circ_all.append((math.cos(a), math.sin(a), math.cos(a) * D_ISLET + RC))
    # na faixa |lat| <= LP a ilhota continua na plataforma da ancora: so a metade de tras do circulo + d <= DP1
    circ_low = [p for p in circ_all if p[0] < 0.0] + [(1.0, 0.0, DP1)]

    def rect_minus(r, q):
        d0, d1, l0, l1 = r
        e0, e1, m0, m1 = q
        if e0 >= d1 or e1 <= d0 or m0 >= l1 or m1 <= l0:
            return [r]
        out = []
        if d0 < e0:
            out.append((d0, e0, l0, l1))
        if e1 < d1:
            out.append((e1, d1, l0, l1))
        md0, md1 = max(d0, e0), min(d1, e1)
        if l0 < m0:
            out.append((md0, md1, l0, m0))
        if m1 < l1:
            out.append((md0, md1, m1, l1))
        return out

    while d < D_ANCHOR - 0.2:
        dep = min(2.6, D_ANCHOR - 0.15 - d)
        lat = -R_ISLET - 1.0 + (tile / 2 if row % 2 else 0.0)
        while lat < R_ISLET + 1.0:
            wd = tile * rng.uniform(0.85, 1.15)
            hh = 0.3 + rng.uniform(-0.03, 0.03)
            yaw_j = rng.uniform(-0.01, 0.01)
            tint = rng.uniform(-1.0, 1.0)
            r0 = (d + 0.1, d + dep - 0.1, lat + 0.1, lat + wd - 0.1)
            pieces = [r0]
            for q in holes:
                pieces = [pp for p_ in pieces for pp in rect_minus(p_, q)]
            split = []
            for p_ in pieces:
                cutsl = [p_[2]] + [c for c in (-LP, LP) if p_[2] + 0.05 < c < p_[3] - 0.05] + [p_[3]]
                split += [(p_[0], p_[1], a_, b_) for a_, b_ in zip(cutsl, cutsl[1:])]
            placed = False
            for d0, d1, l0, l1 in split:
                if d1 - d0 < 0.25 or l1 - l0 < 0.25:
                    continue
                planes = circ_low if (l0 >= -LP - 1e-6 and l1 <= LP + 1e-6) else circ_all
                P, changed = clip_planes([(d0, l0), (d1, l0), (d1, l1), (d0, l1)], planes)
                if P is None or (changed and not poly_ok(P)):
                    continue
                if not changed and (d0, d1, l0, l1) == r0:
                    p = ep((d0 + d1) / 2, (l0 + l1) / 2, Z + 0.1 - hh / 2)
                    mi.box((d1 - d0, l1 - l0, hh), (p.x, p.y, p.z), (0, 0, YAW + yaw_j), DUSK, 0.0, 1, tint)
                else:
                    W = [ep(dd, ll) for dd, ll in P]
                    mi.prism(ccw([(w.x, w.y) for w in W]), Z + 0.1 - hh, Z + 0.1, DUSK, 0.0, 1, tint)
                placed = True
            n += 1 if placed else 0
            lat += wd
        d += dep
        row += 1

    # parapeito crepuscular nas guardas da ilhota e nas laterais da plataforma da ancora
    def mfn(x, y):
        return DUSK

    def cap_fn(x, y):
        return SHADOW

    def lamp_fn(x, y):
        dd, ll = to_dl(x, y)
        return dd > D_GATE + 12.0 and abs(ll) > 11.0
    lamps = 0
    for run in islet_guard_runs():
        lamps += stone_parapet(mi, run, Z - 0.12, mfn, cap_fn, 8.5, lamp_fn)
    for s in (-1, 1):
        run = [ep(D_ANCHOR - 10.0, s * LAT_G), ep(D_ANCHOR - 0.4, s * LAT_G)]
        stone_parapet(mi, run, Z - 0.12, mfn, cap_fn, 9.6, None)
    islet_rock(mi, rng)
    return n, lamps


def strata_drum(mb, c, base, rings, rng, off, top_m=None, jitter=0.06):
    """tambor de rocha em loft de aneis horizontais: rings = [(z, escala, material do segmento abaixo, recuo)] de
    cima para baixo; o recuo (< 1) encolhe o anel (sulco do estrato escuro). Jitter por vertice so no raio."""
    n = len(base)
    vs = []
    for z, sc, m, rec in rings:
        ring = []
        for px, py in base:
            j = (1.0 + rng.uniform(-jitter, jitter)) * sc * rec
            ring.append(mb.bm.verts.new((c.x + off.x + px * j, c.y + off.y + py * j, z)))
        vs.append(ring)
    groups = {}
    for k in range(len(vs) - 1):
        up, lo = vs[k], vs[k + 1]
        m = rings[k][2]
        for i in range(n):
            j = (i + 1) % n
            groups.setdefault(m, []).append(mb.bm.faces.new((lo[i], lo[j], up[j], up[i])))
    if top_m:
        groups.setdefault(top_m, []).append(mb.bm.faces.new(vs[0]))
    for m, fs in groups.items():
        for f in fs:
            f.normal_update()
        assign(mb, fs, m, variant=(m == RDUSK))


def islet_rock(mb, rng):
    """massa pendurada da ilhota: tambor de topo (assenta os plintos do portao, r ~24,6), tambores que afinam,
    estalactites grandes de comprimentos diferentes (silhueta quebrada, nada de cone unico), costelas na borda
    (menos sob a ponte), sulcos negro-violeta"""
    ic = L.islet_center()
    c = Vector((ic[0], ic[1], 0.0))
    nv = 24
    base = []
    # tambor de topo justo na ilhota (r ~23,3: 0,9 alem do leito) com 2 bojos onde os plintos do portao passam do
    # raio 22 (cantos a ~132 graus da saida, r 24,2)
    for i in range(nv):
        a = math.tau * i / nv + 0.13
        rel = (a - YAW + math.pi) % math.tau - math.pi
        bulge = sum(math.exp(-((abs(rel) - math.radians(132.0)) / 0.3) ** 2) for _ in (0,))
        r = (23.3 + 2.0 * bulge) * (1.0 + 0.025 * math.sin(5 * a + 1.3)) * rng.uniform(0.99, 1.02)
        base.append((math.cos(a) * r, math.sin(a) * r))
    # tambores encaixados (o topo de cada um entra 1 no de cima: sem fresta, sem anel continuo de sulco) e com o
    # eixo derivando para lados diferentes (silhueta torta, nada de cone concentrico). Os 2 de cima sao lofts com
    # ESTRATOS: faixas claras (Stone_DB_Dusk) e escuras recuadas (P_Shadow_Stone) na rocha crepuscular - a mesma
    # leitura em camadas do arenito da ilha, na paleta Shadow Garden.
    # aneis (cota, escala, material do segmento ABAIXO do anel, recuo); o ultimo anel nao tem segmento
    drum0 = [(Z - 0.45, 1.0, DUSK, 1.0), (Z - 1.75, 0.985, RDUSK, 1.0), (Z - 4.4, 0.962, SHADOW, 0.975),
             (Z - 5.5, 0.952, RDUSK, 0.975), (Z - 8.2, 0.925, DUSK, 1.0), (Z - 9.6, 0.91, RDUSK, 1.0),
             (Z - 12.0, 0.86, None, 1.0)]
    drum1 = [(Z - 11.0, 0.83, RDUSK, 1.0), (Z - 14.6, 0.77, SHADOW, 0.97), (Z - 15.9, 0.745, RDUSK, 0.97),
             (Z - 19.5, 0.68, DUSK, 1.0), (Z - 20.8, 0.655, RDUSK, 1.0), (Z - 25.0, 0.581, None, 1.0)]
    strata_drum(mb, c, base, drum0, rng, Vector((0.0, 0.0, 0.0)), top_m=DUSK)
    strata_drum(mb, c, base, drum1, rng, U * 2.2 + N * 0.6, top_m=None)
    tiers = [(Z - 24.0, Z - 36.0, 0.57, 0.56, None, N * 3.0 - U * 0.4),
             (Z - 35.0, Z - 48.0, 0.31, 0.18, None, -U * 2.4 + N * 1.2)]
    for k, (zt, zb, sc, taper, band, off) in enumerate(tiers):
        poly = [(x * sc, y * sc) for x, y in base]
        small = [(x * taper, y * taper) for x, y in poly]
        FP.rock_column(mb, c + off, small, zb, zt, rng, RDUSK, taper=1.0 / taper, rings=1,
                       jitter=0.07, tilt=0.0, chamfer=0.0, rim=False, band=band, bottom=(k == len(tiers) - 1))
    # estalactites (massas penduradas sob o tambor, em volta do nucleo): comprimentos e larguras bem diferentes
    for k, (ang, rr, zb, w) in enumerate(((0.5, 12.5, Z - 60.0, 6.4), (1.7, 15.0, Z - 36.0, 4.2),
                                          (2.6, 13.0, Z - 48.0, 5.4), (3.6, 10.5, Z - 42.0, 4.6),
                                          (4.6, 14.5, Z - 54.0, 5.8), (5.6, 12.0, Z - 30.0, 4.0))):
        v = Vector((math.cos(ang), math.sin(ang), 0.0))
        cc = c + v * (rr - 3.0)                  # ponta de baixo 3 para dentro: o topo (inclinado) fica em rr
        t = Vector((-v.y, v.x, 0.0))
        poly = FP._to_world(FP._rock_poly(w, w * 0.72, 7, rng, ex=2.3, jit=0.1), t, v)     # pegada do TOPO
        zt = Z - 11.0
        kb = 0.18                                                  # a ponta de baixo tem 18% da pegada do topo
        FP.rock_column(mb, cc, [(x * kb, y * kb) for x, y in poly], zb, zt, rng, RDUSK if k % 2 else DUSK,
                       taper=1.0 / kb, rings=3, jitter=0.1, tilt=0.0, lean=(v.x * 3.0, v.y * 3.0), chamfer=0.0,
                       rim=False, bottom=True)
        # sulco negro-violeta a 40% da altura (acompanha a inclinacao e o afunilamento da estalactite)
        f = 0.4
        sg = kb * (1.0 + (1.0 / kb - 1.0) * f ** 1.3) * 0.95
        cg = cc + v * (3.0 * f ** 1.6)
        zg = zb + (zt - zb) * f
        FP.rock_column(mb, cg, [(x * sg, y * sg) for x, y in poly], zg - 0.8, zg + 0.6, rng, SHADOW, taper=1.0,
                       rings=1, jitter=0.03, tilt=0.0, chamfer=0.0, rim=False, bottom=False)
    # costelas penduradas na borda (fraturas verticais que leem de longe), fora do lado da ponte. O topo de cada uma
    # e um plano INCLINADO para fora (~50 graus) que nasce de dentro do tambor: a borda de dentro fica enterrada e so
    # a cunha de fora sai da parede - fratura, nao prateleira horizontal saindo do tambor.
    for k in range(9):
        a = math.tau * (k + 0.5) / 9 + rng.uniform(-0.15, 0.15)
        v = Vector((math.cos(a), math.sin(a), 0.0))
        if v.dot(-U) > 0.72:
            continue
        b = rng.uniform(2.4, 3.4)
        t = Vector((-v.y, v.x, 0.0))
        poly = FP._to_world(FP._rock_poly(rng.uniform(3.4, 5.2), b, 6, rng, ex=2.3, jit=0.1), t, v)
        zt = Z - rng.uniform(4.5, 6.5)
        zb = Z - rng.uniform(20.0, 30.0)
        lean = 1.5
        cc = c + v * (23.0 - 0.85 * b - lean)          # base; o topo fica em 23 - 0,85 b (borda de fora ~ 23)
        kb = 0.3
        slope = tuple((-v * (1.2 / kb)).xy)            # o rock_column inclina o topo nas coords da base (x kb)
        # costela pendurada: larga no topo (poly), ponta estreita embaixo
        FP.rock_column(mb, cc, [(x * kb, y * kb) for x, y in poly], zb, zt, rng, RDUSK if k % 3 else DUSK,
                       taper=1.0 / kb, rings=2, jitter=0.1, tilt=0.0, lean=(v.x * lean, v.y * lean), chamfer=0.4,
                       rim=False, slope=slope, bottom=True)


def anchor_guard(rng):
    """guarda PROVISORIA da ancora: 2 pilones (nos ombros do bastiao, fora da largura andavel) + 2 correntes na
    frente da parede invisivel COL_DBAnchorGuard (db_col). A integracao da Ilha 3 remove tudo (next_island_guard)."""
    g = MB("DB_Exit_AnchorGuard", C, rng, detail="near")
    dpy = D_ANCHOR - 1.1
    xl = 11.5
    for s in (-1, 1):
        p = ep(dpy, s * xl, 0.0)
        g.box((2.5, 2.5, 0.7), (p.x, p.y, Z + 0.23), (0, 0, YAW), SHADOW, 0.1)
        g.box((1.8, 1.8, 4.6), (p.x, p.y, Z + 0.58 + 2.3), (0, 0, YAW), DUSK, 0.14)
        g.box((2.1, 2.1, 0.32), (p.x, p.y, Z + 3.0), (0, 0, YAW), SHADOW, 0.05)
        dusk_lamp(g, Vector((p.x, p.y, Z + 4.88)), YAW, 1.0)
        cb = col_box("DB_ExitAnchorPylon", (2.2, 2.2, 7.4), (p.x, p.y, Z + 3.7), (0, 0, YAW))
        cb["next_island_guard"] = True
    # correntes DENTRO da espessura da parede invisivel (d 104..105,2): quem encosta nela nao atravessa os elos.
    # Cada ponta pende de um braco de ferro que sai da face do pilone (o pilone fica no ombro do bastiao).
    dch = D_ANCHOR + 0.45
    for zz, sag in ((Z + 3.5, 1.1), (Z + 2.0, 0.6)):
        a = ep(dch, xl - 0.95, zz)
        b = ep(dch, -(xl - 0.95), zz)
        PK.chain(g, a, b, sag=sag, link=1.0, m=IRON, t=0.3, w=0.66)
        for s in (-1, 1):
            p = ep((dpy + 0.9 + dch + 0.35) / 2, s * (xl - 0.7), zz + 0.05)
            g.box((dch + 0.35 - (dpy + 0.9) + 0.2, 0.55, 0.42), (p.x, p.y, p.z), (0, 0, YAW), IRON, 0.05)
    ob = g.finish()
    ob["next_island_guard"] = True
    ob["removed_by"] = "integracao da Ilha 3 (a ponte seguinte encosta em ISLAND_NEXT_ANCHOR_ShadowGarden)"
    return ob


# ------------------------------------------------------------------ rotas e sondas extras (db_qa)
def _extra():
    routes = {}
    for sg, nm in ((1, "N"), (-1, "S")):
        pts = []
        for s in (S_ARCH - 14.0, S_ARCH - 6.0, S_ARCH, S_ARCH + 6.0, S_ARCH + 14.0):
            p, t = PATH.at(s)
            nrm = Vector((-t.y, t.x, 0.0))
            q = p + nrm * (sg * 7.2)
            pts.append((round(q.x, 2), round(q.y, 2)))
        routes["ARCO_borda_%s" % nm] = (pts, Z)
    # vila (ligacao) -> juncao -> sob o arco -> trilha (volta pelo lado de dentro da guarda, junto do pe norte)
    routes["LIGACAO->ARCO"] = ([L.HUB_EXIT_LINK[0], L.HUB_EXIT_LINK[1], L.HUB_EXIT_LINK[2],
                                (L.EXIT_ARCH[0] + 3.0, L.EXIT_ARCH[1] + 2.0), (L.EXIT_PATH[1][0], L.EXIT_PATH[1][1])], Z)
    probes = []
    p, t = PATH.at(S_ARCH)
    nrm = Vector((-t.y, t.x, 0.0))
    for sg, nm in ((1, "N"), (-1, "S")):
        q = p + nrm * (sg * 7.6)
        probes.append(("ARCO_guarda_%s" % nm, round(q.x, 2), round(q.y, 2), Z, round(nrm.x * sg, 4),
                       round(nrm.y * sg, 4)))
    for dd, ll in ((D_ISLET + 8.0, 19.0), (D_ISLET + 8.0, -19.0)):
        q = ep(dd, ll)
        w = ep(dd, ll * 1.2) - q
        w.normalize()
        probes.append(("ILHOTA_borda_%s" % ("N" if ll > 0 else "S"), round(q.x, 2), round(q.y, 2), Z, round(w.x, 4),
                       round(w.y, 4)))
    return routes, probes


EXTRA_ROUTES, EXTRA_PROBES = _extra()


# ------------------------------------------------------------------ build
def build():
    fm_lib.MATS.setdefault(DEAD, ((0.230, 0.195, 0.160), 0.9, 0.0, 0, None, 0.12))
    mt = MB("DB_Exit_Trail", C, random.Random(9101), detail="near", floor=-999)
    ma = MB("DB_Exit_Arch", C, random.Random(9103), detail="near", floor=-999)
    mb = MB("DB_Exit_Bridge", C, random.Random(9105), detail="near", floor=-999)
    mi = MB("DB_Exit_Islet", C, random.Random(9106), detail="near", floor=-999)
    nslab, lamps = trail(mt, mb, random.Random(9102))
    clear = arch(ma, random.Random(9104))
    dry_trees(ma, random.Random(9107))
    bridge(mb, random.Random(9108))
    piers(mb, random.Random(9109))
    nisl, lamps2 = islet(mi, random.Random(9110))
    for m in (mt, ma, mb, mi):
        m.finish()
    anchor_guard(random.Random(9111))
    print("DB_EXIT lajes prateleira=%d ilhota=%d lanterninhas roxas: trilha=%d ilhota=%d vao_arco=%.2f" % (
        nslab, nisl, lamps, lamps2, clear))
