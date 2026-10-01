# sg_castle - CASTELO 2x da Ilha 3 (Shadow Garden), planta v4 (PLANO MESTRE 2026-09-30, secao 2.2). Substitui
# sg_blockout.castle. ONDA 1 / agente 1a: CASCA do castelo (o interior do salao e do presbiterio e do sg_hall; o poco
# da escada abaixo de z 44 e do sg_cave).
#   MURALHA nova (x +-172, y -23..-13, passeio P3+24) com mata-caes e ameias, PORTAO 24 x 32 ogival entre 2 torres R 12
#   (topo P3+44), grade levadica recolhida (dentes a vista) e folhas 12 x 26 abertas DENTRO dos rebaixos da passagem,
#   torres de canto/intermediarias, passagem leste (x 150) com 2 torrinhas, escadas Gate/EastP3 com banzos.
#   NAVE 2x: paredes de 5 (face interna = salao 184 x 196), perfil de BASILICA por fora: naves laterais ate a cornija
#   146,2 com meia-agua, CLERESTORIO em x +-44 ate 188,2 e telhado ingreme ate a cumeeira 240; contrafortes com
#   ressaltos, pilar intermediario sobre a meia-agua e ARCOBOTANTES DUPLOS com pinaculos; 8 janelas altas (10 x 34) por
#   lado (vao de verdade, vidro de luar e rendilhado; o vitral e do sg_hall); teto opaco e colidivel em 136,2.
#   FACHADA: corpo central de 88 (face y 58,5) com a PORTA 28 x 34 (verga reta), timpano ogival ate 46 com o emblema,
#   4 ARQUIVOLTAS de 2,5 com colunelos (moldura externa 48 x ~56) num PORCHE de 14,5 de fundo com wimperg; NARTEX de
#   22 com as 2 FOLHAS de 14 x 34 abertas e RECOLHIDAS em rebaixos das paredes da passagem (vao livre continua 28);
#   galeria de nichos, ROSACEA R 17 com o crescente da ordem no centro, galeria alta, tela com empena ate 252 e 2
#   torrinhas. Naves laterais da fachada com janela escura funda.
#   TORRES DA FACHADA R 20 em (+-116, 72): 4 andares, janelas escuras em recuo, 2 JANELAS ACESAS por torre (as unicas
#   quentes do castelo alem das torres do portao), campanario com venezianas, coroamento com mata-caes, pinaculos e
#   agulha ate 300.
#   TORRE-COROA: base 76 x 82 (presbiterio com paredes, BOLSO do trono na parede leste com o baluarte que o acusa por
#   fora, muro do retabulo com o arco secreto 12 x 18, tetos), CASCA do poco da escada ACIMA de z 44 (16-gono igual a
#   Torre do Poco do sg_cave; degraus/nucleo/corrimao da escada inteira sao do sg_cave), fuste octogonal R 30 ate 311
#   (campanario com 4 lancetas violeta acesas), coroa de torrinhas e agulha ate 376.
# JANELAS (regra da onda 1, familia F1 do relatorio de z-fight): janela ACESA so em VAO de verdade (comodo aceso 0,86
# atras da face, vidro ambar 0,36 na frente dele, chumbo na frente do vidro); as outras sao ESCURAS (fundo de obsidiana
# + vidro de luar, em recuo ou na frente da face com as camadas a >= 0,12) ou CEGAS com moldura.
# LADRILHADO pela geometria: silhar fino (PL 3,3) ate +8, medio (PL 4,8) ate +26, fiadas grandes (PL 11) ate +60;
# acima, cordoes e remates. Mesmo idioma da ponte de entrada (cantaria chanfrada, capa em pecas, obsidiana nos socos).
# Colisao propria: muralha, torres, portao, paredes da nave com a porta e o arco triunfal, teto, porche, folhas,
# contrafortes, torres da fachada, base da coroa com o presbiterio/bolso/retabulo. Nada dentro de MINE_RECT.
import math, random
import sg_lib as SL
import fm_lib
from sg_lib import MB, col_box, col_box2, light, ngon_col, box_walls_col
import sg_layout as L
import fm_parts as FP
if not hasattr(L, "HALL_TYMPANUM_H"):
    # importado pelo kit de um modulo da v3 (sg_craft pelo sg_relocate, com a planta v3 no lugar): as medidas do castelo
    # sao SEMPRE as da planta v4 (arquivo sg_layout.py), numa copia privada
    import importlib.util as _ilu, os as _os
    _spec = _ilu.spec_from_file_location("sg_layout_v4_castle", _os.path.join(_os.path.dirname(_os.path.abspath(__file__)),
                                                                            "sg_layout.py"))
    L = _ilu.module_from_spec(_spec)
    _spec.loader.exec_module(L)

# ------------------------------------------------------------------ materiais
fm_lib.MATS.setdefault("Stone_SGCasInterior", (fm_lib.S(104, 104, 120), 0.8, 0.0, 0, None, 0.08))  # pele interna
fm_lib.MATS.setdefault("Glass_SGHallMoon", (fm_lib.S(96, 124, 186), 0.4, 0.0, 0.4, fm_lib.S(110, 145, 220), 0.0))
import sg_emblem as EM

OB = "Stone_SG_Obsidian"
VI = "Stone_SG_Violet"
SV = "Metal_SG_Silver"
BI = "Metal_SG_BlackIron"
VG_EMB = "SG_VioletDeep_Glow"         # SO o crescente do emblema
VS = "SG_VioletSoft_Glow"             # campanario da coroa (4 lancetas violeta, em vao)
WD = "Wood_SG_Dark"
ROOM = "SG_VilRoom_Glow"              # comodo aceso (Neon medio quente) - so no fundo de VAO de verdade
fm_lib.MATS.setdefault(ROOM, (fm_lib.S(178, 96, 40), 0.5, 0.0, 1.25, fm_lib.S(178, 96, 40), 0.0))
MOON = "Glass_SGHallMoon"             # vidro de luar (Glass 0,3): janelas escuras
AMBER = "Glass_SG_LampAmber"          # vidro ambar (Glass 0,3) na frente do comodo aceso
ROSE_G = "Glass_SG_Rose"              # vitral violeta (rosacea e campanario)
CM_ = "Stone_SG_Castle"
IM = "Stone_SGCasInterior"
ASH = "Stone_SG_Block_B"              # silhar (um valor acima do corpo: as juntas chanfradas leem mais escuras)
CAPL = "Stone_SG_TrimLow"             # remate perto do jogador
fm_lib.MATS.setdefault(CAPL, (fm_lib.S(132, 128, 134), 0.8, 0.0, 0, None, 0.06))
TRIM = "Stone_SG_Trim"                # remate alto/longe
NAVY = "Roof_SG_Navy"
COURSES = (1.05, 0.78)

WARM = (1.0, 0.72, 0.45)
VIOLET = (0.62, 0.45, 1.0)

# ------------------------------------------------------------------ medidas v4
Z = L.P3                               # 52,2
Z2 = L.P2                              # 44,2
ZB = Z - 0.4
HX0, HY0, HX1, HY1 = L.HALL_X0, L.HALL_Y0, L.HALL_X1, L.HALL_Y1      # -92, 66, 92, 262
TW = L.HALL_WALL                        # 5
OX0, OY0, OX1, OY1 = HX0 - TW, HY0 - TW, HX1 + TW, HY1 + TW          # -97, 61, 97, 267
CEIL = L.HALL_CEIL                      # 136,2
EAVE = Z + 94.0                         # 146,2 cornija das naves laterais
CLR = 44.0                              # face externa do clerestorio = meia largura do corpo central
CLR_T = 2.6
LEAN_HI = Z + 114.0                     # 166,2 a meia-agua encosta no clerestorio
CLR_EAVE = Z + 136.0                    # 188,2 beiral do telhado da nave
RIDGE = 240.0                           # cumeeira (PLANO: ~228; +12 para o telhado ingreme de 49 graus)
FAC_Y = OY0 - 2.5                       # 58,5 face do corpo central da fachada
FAC_TOP = Z + 150.0                     # 202,2 cornija do corpo central (tela)
GABLE_TOP = 252.0                       # empena-tela da fachada
DW, DH = L.HALL_DOOR_W, L.HALL_DOOR_H   # 28 x 34
TYMP = L.HALL_TYMPANUM_H                # 46
YD = 52.0                               # plano da porta (timpano + dobradicas das folhas)
NORD, ORD_W, ORD_D = 4, 2.5, 2.0        # arquivoltas: 4 ordens de 2,5 (largura) x 2 (fundo)
YP = YD - NORD * ORD_D                  # 44 frente do porche
PX = DW / 2 + NORD * ORD_W + 6.0        # 30 meia largura do porche
POCK = 0.8                              # fundo do rebaixo das folhas na parede da passagem
LEAF_T = 0.55
WIN_A, WIN_SILL, WIN_SPRING, WIN_RISE = 5.0, Z + 30.0, Z + 56.0, 8.0     # janelas altas 10 x 34 (apice Z+64)
WIN_Y = [y + 11.25 for y in L.ARCADE_Y]                                   # 89,25 .. 246,75 (1 por tramo)
WIN_OUT = WIN_Y                                                           # 8 por lado (= sg_hall)
BUTT_Y = L.ARCADE_Y[1:]                                                   # 100,5 .. 235,5 (78 cai dentro da torre)
FT_TOP = 226.0                          # parapeito das torres da fachada (PLANO 214: sobe com a cumeeira)
FT_SPIRE_TIP = 300.0
BTOP = Z + 100.0                        # 152,2 topo da base da torre-coroa
CR_X, CR_Y, CR_R, CR_TOP = L.CROWN_TOWER                             # (0, 303, 30, 311)
WALL_TOP = L.WALL_TOP                   # 76,2 passeio da muralha
WFRONT = L.WALL_Y0 - 0.6                # -23,6 face externa da muralha (0,6 NA FRENTE do arrimo do P3: F3)
GW = L.GATEHOUSE_W                      # 24
GSPR, GRISE = Z + 18.0, 14.0            # arco do portao: nascenca e flecha (apice Z+32)
GPW = GW / 2 + POCK                     # 12,8 meia largura da passagem (rebaixo das folhas)
GVSPR, GVRISE = Z + 27.0, 9.0           # abobada da passagem (acima das folhas de 26)
GH_TOP = Z + 38.0                       # topo da portaria
GT_TOP = L.GATEHOUSE_TOWER_TOP          # 96,2
EG_X, EG_W = L.EAST_WALL_GAP            # 150, 18
WALL_TOWERS = [(-165.0, -18.0, 8.0, Z + 34.0, 20.0), (-92.0, -18.0, 7.0, Z + 32.0, 18.0),
               (92.0, -18.0, 7.0, Z + 32.0, 18.0), (166.5, -18.0, 7.0, Z + 34.0, 18.0),
               (136.0, -18.0, 4.5, Z + 26.0, 13.0)]     # (x, y, r, topo, agulha)

P1, P2, P3 = L.P1, L.P2, L.P3
# cameras da onda 1 (renders pedidos): fachada da praca e do eixo na altura do jogador, porta de perto com avatar,
# longe da vila e da ponte de chegada, lateral, coroa com o bolso por fora, close de janela acesa
CAMS = {
    "CAM_SGCas_Fachada_Praca": ((10.0, -198.0, P1 + 5.2), (0.0, 110.0, P3 + 88.0), 20),
    "CAM_SGCas_Fachada_Eixo": ((0.0, -6.0, P3 + 5.2), (0.0, 61.0, P3 + 70.0), 14),
    "CAM_SGCas_Porta": ((7.0, 36.0, P3 + 5.6), (-2.0, 54.0, P3 + 15.0), 16),
    "CAM_SGCas_Longe_Vila": ((24.0, -104.0, P2 + 5.2), (0.0, 170.0, P3 + 125.0), 20),
    "CAM_SGCas_Longe_Ponte": ((-14.0, -470.0, L.DECK + 5.2), (0.0, 200.0, P3 + 150.0), 24),
    "CAM_SGCas_Lateral": ((148.0, 118.0, P3 + 5.2), (90.0, 190.0, P3 + 52.0), 18),
    "CAM_SGCas_LateralLonge": ((360.0, 110.0, P3 + 80.0), (0.0, 190.0, P3 + 140.0), 22),
    "CAM_SGCas_Coroa_Bolso": ((104.0, 318.0, P3 + 6.0), (36.0, 296.0, P3 + 62.0), 18),
    "CAM_SGCas_Janela_Acesa": ((109.0, 30.0, Z + 72.0), (116.0, 54.0, Z + 80.0), 26),
    "CAM_SGCas_Portao": ((-10.0, -58.0, P2 + 5.2), (0.0, -18.0, P3 + 20.0), 20),
    "CAM_SGCas_Muralha": ((-60.0, -44.0, P2 + 5.2), (-40.0, -20.0, P2 + 14.0), 20),
}

# rota extra: patio -> contorno da torre oeste da fachada -> beco oeste -> terraco norte (atras da coroa)
EXTRA_ROUTES = {
    "PATIO->PORCHE->PORTA": ([(0.0, 20.0), (0.0, 40.0), (0.0, YD - 1.0), (0.0, YD + 1.0), (0.0, 60.0), (0.0, 70.0)], P3),
    "PATIO->PORCHE_LADO": ([(-10.0, 30.0), (-10.0, 46.0), (-10.0, 56.0), (-10.0, 64.0), (-10.0, 72.0)], P3),
}
EXTRA_PROBES = []


# ------------------------------------------------------------------ geometria base (kit do castelo)
def _fin(mb):
    """finish + limpeza das lascas de area nula que o tubo fechado do sg_emblem deixa na emenda do anel"""
    import bmesh
    ob = mb.finish()
    if ob is None:
        return ob
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    bad = [f for f in bm.faces if f.calc_area() < 1e-5]
    if bad:
        bmesh.ops.delete(bm, geom=bad, context="FACES_ONLY")
        loose = [v for v in bm.verts if not v.link_faces]
        if loose:
            bmesh.ops.delete(bm, geom=loose, context="VERTS")
        bm.to_mesh(ob.data)
        ob.data.update()
    bm.free()
    return ob


def _P(W, u, t, z):
    (ox, oy), (ux, uy), (nx, ny) = W
    return (ox + ux * u + nx * t, oy + uy * u + ny * t, z)


def _dedupe(poly):
    out = []
    for p in poly:
        if not out or abs(p[0] - out[-1][0]) > 1e-4 or abs(p[1] - out[-1][1]) > 1e-4:
            out.append(p)
    if len(out) > 2 and abs(out[0][0] - out[-1][0]) < 1e-4 and abs(out[0][1] - out[-1][1]) < 1e-4:
        out.pop()
    return out


def panel(mb, W, poly, t0, t1, m, inner_m=None):
    """prisma de um poligono no plano (u, z) da parede W, de t0 a t1 (t = normal). inner_m: material da face t0"""
    poly = _dedupe(poly)
    if len(poly) < 3:
        return
    bm = mb.bm
    a = [bm.verts.new(_P(W, u, t0, z)) for u, z in poly]
    b = [bm.verts.new(_P(W, u, t1, z)) for u, z in poly]
    n = len(poly)
    fa = bm.faces.new(a)
    bm.faces.new(list(reversed(b)))
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((a[j], a[i], b[i], b[j]))
    mb._post(a + b, m, None, 0, 1)
    if inner_m:
        fa.material_index = mb._mi_for(inner_m)


def rect(u0, u1, z0, z1):
    return [(u0, z0), (u1, z0), (u1, z1), (u0, z1)]


def ogive(uc, a, zr, rise, d=0.0, n=6):
    """arco apontado (2 arcos) de (uc-a-d, zr) pelo apice ate (uc+a+d, zr); d = afastamento (moldura).
    v4: flecha menor que a meia largura = arco ABATIDO apontado (centros dentro do vao), p.ex. o timpano 28 x 12"""
    rise = max(rise, 0.3 * a)
    c = (rise * rise - a * a) / (2.0 * a)
    R = a + c + d
    th1 = math.acos(max(-1.0, min(1.0, -c / R)))
    left = [(uc + c + R * math.cos(th), zr + R * math.sin(th)) for th in
            [math.pi + (th1 - math.pi) * k / n for k in range(n + 1)]]
    left[-1] = (uc, left[-1][1])
    right = [(2 * uc - u, z) for (u, z) in reversed(left[:-1])]
    return left + right


def apex_of(a, rise, d=0.0):
    rise = max(rise, 0.3 * a)
    c = (rise * rise - a * a) / (2.0 * a)
    R = a + c + d
    return math.sqrt(max(0.0, R * R - c * c))


def opening(uc, a, zs, zr, rise, n=6):
    """contorno fechado do vao (peitoril reto + arco)"""
    if rise <= 0.0:
        return rect(uc - a, uc + a, zs, zr)
    return [(uc - a, zs), (uc + a, zs)] + list(reversed(ogive(uc, a, zr, rise, n=n)))


def wall_run(mb, W, u0, u1, zb, zt, t0, t1, opens, m, inner_m=None):
    """parede de u0 a u1 com vaos: opens = [(uc, a, peitoril, nascenca, flecha)]; flecha 0 = verga reta em 'nascenca'"""
    cur = u0
    for uc, a, zs, zr, rise in sorted(opens):
        l, r = uc - a, uc + a
        if l - cur > 0.01:
            panel(mb, W, rect(cur, l, zb, zt), t0, t1, m, inner_m)
        if zs - zb > 0.01:
            panel(mb, W, rect(l, r, zb, zs), t0, t1, m, inner_m)
        if rise <= 0.0:
            if zt - zr > 0.01:
                panel(mb, W, rect(l, r, zr, zt), t0, t1, m, inner_m)
        else:
            panel(mb, W, [(r, zt), (l, zt)] + ogive(uc, a, zr, rise), t0, t1, m, inner_m)
        cur = r
    if u1 - cur > 0.01:
        panel(mb, W, rect(cur, u1, zb, zt), t0, t1, m, inner_m)


def ngon_pts(cx, cy, r, n, rot0=None):
    rot0 = 180.0 / n if rot0 is None else rot0
    return [(cx + r * math.cos(math.radians(rot0 + 360.0 * k / n)), cy + r * math.sin(math.radians(rot0 + 360.0 * k / n)))
            for k in range(n)]


def frustum(mb, cx, cy, r0, r1, n, z0, z1, m, rot0=None, top=True):
    bm = mb.bm
    a = [bm.verts.new((x, y, z0)) for x, y in ngon_pts(cx, cy, r0, n, rot0)]
    b = [bm.verts.new((x, y, z1)) for x, y in ngon_pts(cx, cy, r1, n, rot0)]
    bm.faces.new(list(reversed(a)))
    if top:
        bm.faces.new(b)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((a[i], a[j], b[j], b[i]))
    mb._post(a + b, m, None, 0, 1)


def shaft(mb, cx, cy, r, n, z0, z1, m, rot0=None):
    mb.prism(ngon_pts(cx, cy, r, n, rot0), z0, z1, m)


def spire(mb, cx, cy, r, n, z0, h, m, rot0=None, flare=0.1, rings=(0.36,), ring_m=SV):
    """agulha gotica: beiral levemente alargado + cone ingreme; aneis de prata no beiral e ao longo do cone.
    F2 (z-fight): o anel do beiral sobe ate z0+0,2 (0,16 acima do tampo do parapeito, que foi a z0+0,04)"""
    bm = mb.bm
    e = [bm.verts.new((x, y, z0)) for x, y in ngon_pts(cx, cy, r * (1.0 + flare), n, rot0)]
    k = [bm.verts.new((x, y, z0 + h * 0.08)) for x, y in ngon_pts(cx, cy, r * 0.9, n, rot0)]
    top = bm.verts.new((cx, cy, z0 + h))
    bm.faces.new(list(reversed(e)))
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((e[i], e[j], k[j], k[i]))
        bm.faces.new((k[i], k[j], top))
    mb._post(e + k + [top], m, None, 0, 1)
    if ring_m and r > 1.6:
        rr = r * (1.0 + flare)
        frustum(mb, cx, cy, rr + 0.12, rr + 0.12, n, z0 - 0.35, z0 + 0.2, ring_m, rot0)

        def rad(z):
            return r * 0.9 * (1.0 - ((z - z0) / h - 0.08) / 0.92)
        for f in rings:
            zf = z0 + h * f
            dz = 0.28 if h < 20 else 0.4
            frustum(mb, cx, cy, rad(zf - dz) + 0.16, rad(zf + dz) + 0.16, n, zf - dz, zf + dz, ring_m, rot0)


def ring(mb, C, U, V, N, r0, r1, t0, t1, m, n=24, a0=0.0):
    """anel (coroa circular) no plano (U, V) com espessura ao longo de N: rosacea, aneis de tracaria"""
    bm = mb.bm

    def p(r, ang, t):
        return tuple(C[i] + U[i] * r * math.cos(ang) + V[i] * r * math.sin(ang) + N[i] * t for i in range(3))
    angs = [a0 + 2 * math.pi * k / n for k in range(n)]
    fi = [bm.verts.new(p(r0, a, t0)) for a in angs]
    fo = [bm.verts.new(p(r1, a, t0)) for a in angs]
    bi = [bm.verts.new(p(r0, a, t1)) for a in angs]
    bo = [bm.verts.new(p(r1, a, t1)) for a in angs]
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((fi[i], fo[i], fo[j], fi[j]))
        bm.faces.new((bi[j], bo[j], bo[i], bi[i]))
        bm.faces.new((fo[i], bo[i], bo[j], fo[j]))
        bm.faces.new((fi[j], bi[j], bi[i], fi[i]))
    mb._post(fi + fo + bi + bo, m, None, 0, 1)


def disc(mb, C, U, V, N, r, t0, t1, m, n=24):
    bm = mb.bm

    def p(ang, t):
        return tuple(C[i] + U[i] * r * math.cos(ang) + V[i] * r * math.sin(ang) + N[i] * t for i in range(3))
    angs = [2 * math.pi * k / n for k in range(n)]
    f = [bm.verts.new(p(a, t0)) for a in angs]
    b = [bm.verts.new(p(a, t1)) for a in angs]
    bm.faces.new(f)
    bm.faces.new(list(reversed(b)))
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((f[j], f[i], b[i], b[j]))
    mb._post(f + b, m, None, 0, 1)


def WUVN(W):
    (ox, oy), (ux, uy), (nx, ny) = W
    return (ux, uy, 0.0), (0.0, 0.0, 1.0), (nx, ny, 0.0)


def face_frame(cx, cy, ap, phi_deg):
    """referencial de parede na face de um poligono (centro da face, u tangente, t para fora)"""
    ph = math.radians(phi_deg)
    return ((cx + ap * math.cos(ph), cy + ap * math.sin(ph)), (-math.sin(ph), math.cos(ph)), (math.cos(ph), math.sin(ph)))


def louvers(mb, W, u0, u1, z0, z1, t, m=None):
    """venezianas de madeira (campanario / quarto fechado): fundo escuro + palhetas inclinadas (t = plano do fundo)"""
    m = m or WD
    panel(mb, W, rect(u0, u1, z0, z1), t - 0.1, t + 0.04, OB)
    n = max(2, int((z1 - z0) / 1.25))
    for k in range(n):
        zc = z0 + (k + 0.6) * (z1 - z0) / (n + 0.2)
        panel(mb, W, [(u0, zc - 0.2), (u1, zc - 0.2), (u1, zc + 0.14), (u0, zc + 0.14)], t + 0.18, t + 0.38, m)


def arch_band(mb, W, uc, a, zs, zr, rise, fw, t0, t1, m, n=4):
    """moldura em U (ombreiras + arco numa peca so) em volta de um vao (uc, a, zs, zr, rise)"""
    if rise <= 0.0:
        band_ = [(uc - a, zs), (uc - a, zr), (uc + a, zr), (uc + a, zs), (uc + a + fw, zs), (uc + a + fw, zr + fw),
                 (uc - a - fw, zr + fw), (uc - a - fw, zs)]
        panel(mb, W, band_, t0, t1, m)
        return
    arc = ogive(uc, a, zr, rise, n=n)
    outer = ogive(uc, a, zr, rise, d=fw, n=n)
    band_ = [(uc - a, zs), (uc - a, zr)] + arc[1:-1] + [(uc + a, zr), (uc + a, zs), (uc + a + fw, zs),
                                                        (uc + a + fw, zr)] + list(reversed(outer))[1:-1] + \
            [(uc - a - fw, zr), (uc - a - fw, zs)]
    panel(mb, W, band_, t0, t1, m)


def lancet_win(mb, W, uc, z0, h, w=1.0, t=0.0, glass="dark", frame_m=OB, dp=0.5, fw=0.26, bar=True, sill=True):
    """janela pequena NUMA FACE CHEIA (sem vao). Regra da onda 1 (familia F1): NADA aceso aqui. Tudo na frente da face
    com camadas a >= 0,12: fundo de obsidiana a +0,14, vidro de luar a +0,28..0,34, chumbo a +0,36, moldura saliente ate
    'dp' (>= 0,5: esconde as camadas no rasante), peitoril com pingadeira.
    glass: 'dark' (fundo + luar), 'slit' (so o fundo escuro: seteira), 'louver' (venezianas), 'blind' (so a moldura)"""
    a = w / 2
    rise = a * 1.4
    zr = z0 + h - rise
    poly = opening(uc, a, z0, zr, rise, n=3)
    if glass == "louver":
        louvers(mb, W, uc - a, uc + a, z0, zr, t + 0.1)
        panel(mb, W, [(uc - a, zr), (uc + a, zr)] + list(reversed(ogive(uc, a, zr, rise, n=3)))[1:-1], t - 0.05,
              t + 0.14, OB)
    elif glass in ("dark", "slit"):
        panel(mb, W, poly, t - 0.05, t + 0.14, OB)
        if glass == "dark":
            panel(mb, W, poly, t + 0.28, t + 0.34, MOON)
    arch_band(mb, W, uc, a, z0, zr, rise, fw, t - 0.05, t + dp, frame_m, n=3)
    if sill:
        panel(mb, W, rect(uc - a - fw - 0.18, uc + a + fw + 0.18, z0 - 0.34, z0 + 0.02), t - 0.05, t + dp + 0.22,
              frame_m)
    if bar and glass == "dark" and w >= 1.2:
        zb = z0 + (zr - z0) * 0.55
        panel(mb, W, rect(uc - a, uc + a, zb - 0.07, zb + 0.07), t + 0.36, t + 0.44, BI)


def slit(mb, W, z0, h, w=0.9, glass="slit"):
    """seteira das torres: fenda escura com moldura e peitoril (sem luz)"""
    lancet_win(mb, W, 0.0, z0, h, w, 0.0, glass=glass)


def rwin(mb, W, uc, a, zs, zr, rise, tf, d, kind="dark", frame_m=CAPL, fw=0.8, dp=0.5, sill=True, mull=False,
         lead=True, tracery=False, hood=False):
    """JANELA EM RECUO: o vao (uc, a, zs, zr, rise) ja foi cortado na pele da parede de tf-d ate tf (t para fora).
    kind 'lit': comodo aceso (Neon) no fundo a tf-d+0,14 (0,86+ atras da face), vidro AMBAR 0,26 na frente dele, chumbo
    na frente do vidro -> nunca coplanar com a pedra (F1). 'dark': fundo de obsidiana + vidro de luar. 'violet': fundo
    violeta suave (Neon escuro) + vitral violeta. 'void': so o fundo escuro (nicho/arcada cega)."""
    poly = opening(uc, a, zs, zr, rise)
    back, glass = {"lit": (ROOM, AMBER), "dark": (OB, MOON), "violet": (VS, ROSE_G), "void": (OB, None)}[kind]
    tb = tf - d
    panel(mb, W, poly, tb - 0.05, tb + 0.14, back)
    tg = tb + 0.4
    if glass:
        panel(mb, W, poly, tg, tg + 0.08, glass)
        if lead:
            step = 1.8 if a > 1.5 else 1.3
            top = zr if rise > 0 else zr - 0.2
            nz = int((top - zs - 0.4) / step)
            for k in range(1, nz + 1):
                zz = zs + (top - zs) * k / (nz + 1)
                panel(mb, W, rect(uc - a, uc + a, zz - 0.06, zz + 0.06), tg + 0.1, tg + 0.18, BI)
    if mull:
        mw = 0.26 if a < 3.0 else 0.4
        panel(mb, W, rect(uc - mw, uc + mw, zs, zr + (rise * 0.45 if rise > 0 else 0.0)), tb + 0.14, tf - 0.1,
              frame_m)
        if tracery and rise > 0:
            sub = (a - mw) / 2.0
            for s in (-1, 1):
                c_ = uc + s * (mw + sub)
                i0 = ogive(c_, sub, zr - 0.2, sub * 1.5, n=3)
                i1 = ogive(c_, sub, zr - 0.2, sub * 1.5, d=0.32, n=3)
                panel(mb, W, i0 + list(reversed(i1)), tb + 0.14, tf - 0.2, frame_m)
            ro = min(a * 0.42, rise * 0.34)
            zc = zr + rise * 0.62
            Cc = _P(W, uc, 0.0, zc)
            U, V, N = WUVN(W)
            ring(mb, Cc, U, V, N, ro, ro + 0.3, tb + 0.14, tf - 0.2, frame_m, 10)
    if frame_m:
        arch_band(mb, W, uc, a, zs, zr, rise, fw, tf - 0.05, tf + dp, frame_m)
    if hood and rise > 0:
        h0 = ogive(uc, a, zr, rise, d=fw, n=4)
        h1 = ogive(uc, a, zr, rise, d=fw + 0.45, n=4)
        panel(mb, W, h0 + list(reversed(h1)), tf - 0.05, tf + dp + 0.3, OB)
        for s in (-1, 1):
            u0_, u1_ = sorted((uc + s * (a + fw - 0.05), uc + s * (a + fw + 0.7)))
            panel(mb, W, rect(u0_, u1_, zr - 0.9, zr + 0.02), tf - 0.05, tf + dp + 0.35, OB)
    if sill:
        panel(mb, W, rect(uc - a - fw - 0.3, uc + a + fw + 0.3, zs - 0.6, zs), tf - 0.05, tf + dp + 0.35, frame_m)


def hip_roof(mb, x0, y0, x1, y1, z0, h, m, ridge_frac=0.5):
    bm = mb.bm
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    base = [bm.verts.new(p) for p in ((x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0))]
    if (x1 - x0) >= (y1 - y0):
        hw = (x1 - x0) / 2 * ridge_frac
        r = [bm.verts.new((cx - hw, cy, z0 + h)), bm.verts.new((cx + hw, cy, z0 + h))]
        fs = [(base[0], base[1], r[1], r[0]), (base[1], base[2], r[1]), (base[2], base[3], r[0], r[1]),
              (base[3], base[0], r[0])]
    else:
        hw = (y1 - y0) / 2 * ridge_frac
        r = [bm.verts.new((cx, cy - hw, z0 + h)), bm.verts.new((cx, cy + hw, z0 + h))]
        fs = [(base[0], base[1], r[0]), (base[1], base[2], r[1], r[0]), (base[2], base[3], r[1]),
              (base[3], base[0], r[0], r[1])]
    bm.faces.new(list(reversed(base)))
    for f in fs:
        bm.faces.new(f)
    mb._post(base + r, m, None, 0, 1)


def socle(mb, x, y, r, n, z0, z1, rot, e=0.9):
    """soco de obsidiana (base alargada) + cordao de prata no topo: a BASE de tudo o que e castelo"""
    frustum(mb, x, y, r + e, r + 0.25, n, z0, z1, OB, rot)
    frustum(mb, x, y, r + 0.42, r + 0.42, n, z1 - 0.05, z1 + 0.4, SV, rot)


def band(mb, x, y, r, n, z, rot, m=OB, h=1.2, e=0.5):
    """cordao com perfil em volta de um fuste: recorte por baixo (pingadeira), face e topo em talude"""
    rr = 180.0 / n if rot is None else rot
    EM._lathe(mb, (x, y, z), [(r + 0.05, 0.0), (r + e, h * 0.28), (r + e, h * 0.7), (r + 0.1, h)], m, n,
              math.radians(rr), caps=(False, False))


def _faces_ok(mb, fs):
    import bmesh
    bmesh.ops.recalc_face_normals(mb.bm, faces=[f for f in fs if f is not None])


def ledge(mb, W, u0, u1, prof, m):
    """perfil [(t, z)] (poligono simples no plano t-z da parede W) extrudado de u0 a u1"""
    bm = mb.bm
    prof = _dedupe(prof)
    a = [bm.verts.new(_P(W, u0, t, z)) for t, z in prof]
    b = [bm.verts.new(_P(W, u1, t, z)) for t, z in prof]
    n = len(prof)
    fs = [bm.faces.new(a), bm.faces.new(list(reversed(b)))]
    for i in range(n):
        j = (i + 1) % n
        fs.append(bm.faces.new((a[i], a[j], b[j], b[i])))
    _faces_ok(mb, fs)
    mb._post(a + b, m, None, 0, 1)


def block(mb, W, u0, u1, z0, z1, t0, t1, ch, m):
    """bloco de cantaria: face de tras (u0..u1, z0..z1) em t0, face da frente recuada 'ch' nas 4 arestas em t1"""
    bm = mb.bm
    ch = min(ch, (u1 - u0) * 0.3, (z1 - z0) * 0.3)
    back = [bm.verts.new(_P(W, u, t0, z)) for u, z in ((u0, z0), (u1, z0), (u1, z1), (u0, z1))]
    fr = [bm.verts.new(_P(W, u, t1, z)) for u, z in ((u0 + ch, z0 + ch), (u1 - ch, z0 + ch), (u1 - ch, z1 - ch),
                                                     (u0 + ch, z1 - ch))]
    fs = [bm.faces.new(list(reversed(fr)))]              # sem a face de tras (embutida 0,03 na parede)
    for i in range(4):
        j = (i + 1) % 4
        fs.append(bm.faces.new((back[i], fr[i], fr[j], back[j])))
    for f in fs:
        f.normal_update()
    mb._post(back + fr, m, None, 0, 1)


def _cut(rects, e0, e1, ez0, ez1):
    out = []
    for a, b, ra, rb in rects:
        if e1 <= a or e0 >= b or ez1 <= ra or ez0 >= rb:
            out.append((a, b, ra, rb))
            continue
        if e0 - a > 0.35:
            out.append((a, e0 - 0.06, ra, rb))
        if b - e1 > 0.35:
            out.append((e1 + 0.06, b, ra, rb))
        m0, m1 = max(a, e0 - 0.06), min(b, e1 + 0.06)
        if ez0 - ra > 0.3:
            out.append((m0, m1, ra, ez0 - 0.05))
        if rb - ez1 > 0.3:
            out.append((m0, m1, ez1 + 0.05, rb))
    return out


def ashlar(mb, W, u0, u1, z0, z1, t=0.0, excl=(), m=ASH, PL=3.1, dep=0.12, ch=0.07, phase=0.0, gap=0.08,
           hs=COURSES):
    """paramento de CANTARIA em relevo raso na face (plano externo em t): fiadas de 2 alturas escaladas para fechar
    z0..z1, blocos de ~PL com juntas desencontradas fiada a fiada; excl = [(u0, u1, z0, z1)] vaos (janela + moldura)"""
    if z1 - z0 < 0.5 or u1 - u0 < 0.5:
        return
    per = hs[0] + hs[1]
    npair = max(1, int(round((z1 - z0) / per)))
    sc = (z1 - z0) / (npair * per)
    zz, k = z0, 0
    while zz < z1 - 0.05:
        h = hs[k % 2] * sc
        rects = [(u0, u1, zz + gap / 2, zz + h - gap / 2)]
        for e in excl:
            rects = _cut(rects, *e)
        off = phase + (k % 2) * PL * 0.5
        for a, b, ra, rb in rects:
            cuts = [a] + [u0 + off + PL * j for j in range(-1, int((u1 - u0) / PL) + 3)
                          if a + 0.7 < u0 + off + PL * j < b - 0.7] + [b]
            for c0, c1 in zip(cuts, cuts[1:]):
                p0 = c0 + (gap / 2 if c0 > a else 0.0)
                p1 = c1 - (gap / 2 if c1 < b else 0.0)
                if p1 - p0 > 0.2 and rb - ra > 0.2:
                    block(mb, W, p0, p1, ra, rb, t - 0.03, t + dep, ch, m)
        zz += h
        k += 1


# 3 escalas de silhar (ladrilhado pela geometria): 0 = zona do olho, 1 = medio, 2 = fiadas grandes (Tier B)
TIERS = {0: dict(PL=4.2, hs=(1.5, 1.15), dep=0.13, ch=0.08, gap=0.09),
         1: dict(PL=6.4, hs=(2.2, 1.8), dep=0.15, ch=0.1, gap=0.11),
         2: dict(PL=14.0, hs=(3.6, 3.0), dep=0.17, ch=0.13, gap=0.13)}


def coursed(mb, W, u0, u1, z0, z1, excl=(), tier=0, phase=0.0, t=0.0, m=ASH):
    k = TIERS[tier]
    ashlar(mb, W, u0, u1, z0, z1, t, excl, m=m, PL=k["PL"], dep=k["dep"], ch=k["ch"], phase=phase, gap=k["gap"],
           hs=k["hs"])


def strip(mb, W, lo, hi, t0, t1, m):
    """casca fechada entre a curva de baixo 'lo' e a de cima 'hi' (listas [(u, z)] com o mesmo numero de pontos), de t0
    a t1: arcobotante (intradorso curvo + extradorso reto), aduela, arquinho do mata-caes"""
    bm = mb.bm
    L0 = [(bm.verts.new(_P(W, u, t0, z)), bm.verts.new(_P(W, u, t1, z))) for u, z in lo]
    H0 = [(bm.verts.new(_P(W, u, t0, z)), bm.verts.new(_P(W, u, t1, z))) for u, z in hi]
    fs = []
    for i in range(len(lo) - 1):
        fs.append(bm.faces.new((L0[i][0], L0[i + 1][0], H0[i + 1][0], H0[i][0])))
        fs.append(bm.faces.new((L0[i][1], H0[i][1], H0[i + 1][1], L0[i + 1][1])))
        fs.append(bm.faces.new((L0[i][0], L0[i][1], L0[i + 1][1], L0[i + 1][0])))
        fs.append(bm.faces.new((H0[i][0], H0[i + 1][0], H0[i + 1][1], H0[i][1])))
    for k in (0, -1):
        fs.append(bm.faces.new((L0[k][0], H0[k][0], H0[k][1], L0[k][1])))
    _faces_ok(mb, fs)
    mb._post([v for p in L0 + H0 for v in p], m, None, 0, 1)


def sq_ch(x, y, hw, c, rot=0.0):
    """quadrado de meia-aresta hw com quinas chanfradas em c (octogono irregular anti-horario), girado de rot"""
    pts = [(-hw + c, -hw), (hw - c, -hw), (hw, -hw + c), (hw, hw - c), (hw - c, hw), (-hw + c, hw), (-hw, hw - c),
           (-hw, -hw + c)]
    ca, sa = math.cos(rot), math.sin(rot)
    return [(x + px * ca - py * sa, y + px * sa + py * ca) for px, py in pts]


def finial(mb, x, y, z, s=1.0, m=SV):
    """FLORAO de prata (torno de 6): colar, bulbo, gola e ponta, assentado em z"""
    prof = [(0.17, 0.0), (0.24, 0.1), (0.14, 0.22), (0.3, 0.46), (0.22, 0.68), (0.09, 0.84), (0.13, 0.96),
            (0.0, 1.45)]
    if s < 1.2:
        prof = [(0.2, 0.0), (0.14, 0.2), (0.3, 0.46), (0.1, 0.82), (0.0, 1.45)]
    EM._lathe(mb, (x, y, z), [(r * s, h * s) for r, h in prof], m, 6, math.pi / 6)


def pinnacle(mb, x, y, z0, s=1.0, hb=3.0, hn=None, body_m=CM_, spire_m=NAVY, gab=True, crock=True, rot=0.0,
             ring_m=SV, cap_m=OB):
    """PINACULO do kit: corpo quadrado de quinas chanfradas com cornija e GABLETE nas 4 faces, agulha OCTOGONAL com
    colar, 1 anel de prata, crochés e florao. s = escala. Devolve o topo."""
    hn = 5.6 * s if hn is None else hn
    hw = 1.0 * s
    zt = z0 + hb
    mb.prism(sq_ch(x, y, hw, 0.24 * s, rot), z0, zt, body_m)
    rr = hw * 1.08
    frustum(mb, x, y, rr + 0.1 * s, rr - 0.05 * s, 8, zt - 0.04, zt + 0.22 * s, cap_m, math.degrees(rot) + 22.5)
    if gab and s >= 0.8:
        bm = mb.bm
        for k in range(4):
            a = rot + k * math.pi / 2
            ca, sa = math.cos(a), math.sin(a)
            tx, ty = -sa, ca

            def P(u, t, zz):
                return (x + ca * t + tx * u, y + sa * t + ty * u, zz)
            gw, gh, g0, g1 = 0.72 * s, 1.35 * s, hw * 0.55, hw + 0.14 * s
            pts = ((-gw, zt), (gw, zt), (0.0, zt + gh))
            A = [bm.verts.new(P(u, g0, zz)) for u, zz in pts]
            B = [bm.verts.new(P(u, g1, zz)) for u, zz in pts]
            fs = [bm.faces.new(A), bm.faces.new(list(reversed(B)))]
            for i in range(3):
                j = (i + 1) % 3
                fs.append(bm.faces.new((A[i], A[j], B[j], B[i])))
            _faces_ok(mb, fs)
            mb._post(A + B, body_m, None, 0, 1)
    rn = 0.8 * s
    SL.spire(mb, (x, y), rn, zt + 0.2 * s, hn, spire_m, n=8)
    zr = zt + 0.2 * s + hn * 0.42
    rad = rn * (1.0 - 0.42) + 0.1 * s
    if ring_m and s >= 1.0:
        frustum(mb, x, y, rad + 0.06 * s, rad - 0.04 * s, 8, zr - 0.14 * s, zr + 0.14 * s, ring_m)
    if crock and s >= 1.0:
        bm = mb.bm
        zc = zt + 0.2 * s + hn * 0.66
        rc = rn * (1.0 - 0.66)
        for k in range(4):
            a = math.pi / 8 + k * math.pi / 2
            ca, sa = math.cos(a), math.sin(a)
            tx, ty = -sa, ca
            base = [(x + ca * rc * 0.8 - tx * 0.14 * s, y + sa * rc * 0.8 - ty * 0.14 * s, zc - 0.3 * s),
                    (x + ca * rc * 0.8 + tx * 0.14 * s, y + sa * rc * 0.8 + ty * 0.14 * s, zc - 0.3 * s),
                    (x + ca * rc * 0.7, y + sa * rc * 0.7, zc + 0.25 * s)]
            tip = (x + ca * (rc + 0.42 * s), y + sa * (rc + 0.42 * s), zc + 0.18 * s)
            V = [bm.verts.new(p) for p in base] + [bm.verts.new(tip)]
            fs = [bm.faces.new((V[0], V[2], V[1])), bm.faces.new((V[0], V[1], V[3])),
                  bm.faces.new((V[1], V[2], V[3])), bm.faces.new((V[2], V[0], V[3]))]
            _faces_ok(mb, fs)
            mb._post(V, spire_m, None, 0, 1)
    top = zt + 0.2 * s + hn
    if s >= 0.8:
        finial(mb, x, y, top - 0.45 * s, 0.9 * s)
    return top + 0.95 * s


def drip(z, e=0.5, h=0.62, back=-0.1):
    """perfil de CORDAO com pingadeira (t, z)"""
    return [(back, z - h * 0.45), (e * 0.55, z - h * 0.45), (e, z - h * 0.18), (e, z + h * 0.12),
            (e * 0.45, z + h * 0.55), (back, z + h * 0.55)]


def plinth(zb, z1, e0=0.85, e1=0.4, back=-0.1):
    """perfil de SOCO: fiada de base saliente e0 e talude (45 graus) ate a saliencia e1 no topo z1"""
    zt = z1 - (e0 - e1)
    return [(back, zb), (e0, zb), (e0, zt), (e1, z1), (back, z1)]


def cornice(z, e=1.1, h=1.6, back=-0.2):
    """cornija de coroamento: filete, cavete e testa saliente (t, z)"""
    z += 0.06                                   # F4: o tampo da cornija nunca no plano do topo do corpo
    return [(back, z - h), (0.25, z - h), (0.25, z - h * 0.72), (e * 0.7, z - h * 0.45), (e, z - h * 0.3),
            (e, z), (back, z)]


SOC = Z + 2.6                           # topo do soco de obsidiana (cordao de prata logo acima)


def wall_skin(mb, W, u0, u1, t=0.0, excl=(), zb=ZB, soc=True, tiers=((Z + 8.0, 0), (Z + 22.0, 1), (Z + 42.0, 2)),
              phase=0.0, cords=True):
    """o LADRILHADO de uma face do castelo (W em t = face, t cresce para fora): soco de obsidiana em talude + filete
    de prata, silhar em 3 escalas ate o topo de cada faixa e cordao com pingadeira entre as faixas."""
    Wt = (_P(W, 0.0, t, 0.0)[:2], W[1], W[2])
    z0 = zb
    if soc:
        ledge(mb, Wt, u0, u1, plinth(zb, SOC, 0.85, 0.42), OB)
        ledge(mb, Wt, u0 - 0.02, u1 + 0.02, [(-0.1, SOC), (0.62, SOC), (0.62, SOC + 0.3), (-0.1, SOC + 0.3)], SV)
        z0 = SOC + 0.34
    for i, (ztop, tier) in enumerate(tiers):
        coursed(mb, Wt, u0, u1, z0, ztop - 0.35, excl, tier, phase + 0.37 * i)
        if cords:
            ledge(mb, Wt, u0, u1, drip(ztop, 0.5 if tier < 2 else 0.6), OB)
        z0 = ztop + 0.4


def parapet_ring(mb, cx, cy, r, n, z0, h, m, rot0=None, corbel_m=OB, merlons=True, cap_m=VI):
    """parapeito com mata-caes: fiada de misulas + anel saliente + ameias.
    F2 (z-fight): o corpo do anel SEM tampo e o remate sobe 0,04 acima dele (antes os 2 tampos no mesmo plano)"""
    ap = r * math.cos(math.pi / n)
    side = 2 * r * math.sin(math.pi / n)
    rot0 = 180.0 / n if rot0 is None else rot0
    nc = 3 if side > 12 else (2 if side > 5 else 1)
    for k in range(n):
        phi = rot0 + 360.0 * k / n + 180.0 / n
        W = face_frame(cx, cy, ap, phi)
        for f in [((i + 0.5) / nc - 0.5) for i in range(nc)]:
            ledge(mb, W, f * side - 0.4, f * side + 0.4, [(-0.2, z0 - 2.4), (0.35, z0 - 2.4), (0.9, z0 - 1.2),
                                                         (0.9, z0 + 0.02), (-0.2, z0 + 0.02)], corbel_m)
    frustum(mb, cx, cy, r + 0.9, r + 0.9, n, z0, z0 + h, m, rot0, top=cap_m is None)
    if cap_m:
        frustum(mb, cx, cy, r + 1.1, r + 1.1, n, z0 + h - 0.45, z0 + h + 0.04, cap_m, rot0)
    if merlons:
        for k in range(n):
            phi = rot0 + 360.0 * k / n + 180.0 / n
            W = face_frame(cx, cy, ap + 0.9 * math.cos(math.pi / n), phi)
            nm = max(1, int(side / 3.2))
            for i in range(nm):
                f = (i + 0.5) / nm - 0.5
                if nm > 1 and i % 2:
                    continue
                panel(mb, W, rect(f * side - 0.65, f * side + 0.65, z0 + h + 0.04, z0 + h + 1.5), -1.0, 0.05, m)
                panel(mb, W, rect(f * side - 0.78, f * side + 0.78, z0 + h + 1.5, z0 + h + 1.72), -1.1, 0.16, OB)


def shaft_band(mb, cx, cy, r, n, rot, z0, z1, m, face_opens, d=1.4, core=True):
    """faixa de um fuste poligonal com VAOS de verdade: cada face vira uma parede de espessura d (wall_run com os
    vaos da face) + nucleo cheio atras. face_opens = {indice_da_face: [(uc, a, peitoril, nascenca, flecha)]}.
    Devolve [(W, fase)] das faces (W com t = 0 na face externa)."""
    ap = r * math.cos(math.pi / n)
    side = 2 * r * math.sin(math.pi / n)
    out = []
    for k in range(n):
        phi = rot + 360.0 * k / n + 180.0 / n
        W = face_frame(cx, cy, ap, phi)
        wall_run(mb, W, -side / 2, side / 2, z0, z1, -d, 0.0, face_opens.get(k, []), m)
        out.append((W, phi))
    if core:
        rc = (ap - d) / math.cos(math.pi / n)
        mb.prism(ngon_pts(cx, cy, rc, n, rot), z0, z1, m)
    return out


def face_index(n, rot, phi_want):
    """indice da face cujo rumo e o mais proximo de phi_want"""
    best, bk = 1e9, 0
    for k in range(n):
        phi = rot + 360.0 * k / n + 180.0 / n
        dd = abs(((phi - phi_want + 180.0) % 360.0) - 180.0)
        if dd < best:
            best, bk = dd, k
    return bk


def face_phi(n, rot, k):
    return (rot + 360.0 * k / n + 180.0 / n) % 360.0


def tower_skin(mb, x, y, r, n, rot, zb, tiers, phis=None, soc=True, hide=None, phase=0.0, zmin_fn=None, excl=None):
    """ladrilhado das faces de um fuste poligonal (soco em talude + silhar em escalas + cordoes)"""
    ap = r * math.cos(math.pi / n)
    side = 2 * r * math.sin(math.pi / n)
    if soc:
        socle(mb, x, y, r, n, zb, SOC if zb < SOC - 0.5 else zb + 2.6, rot, e=0.9)
    z_s = (SOC if zb < SOC - 0.5 else zb + 2.6) + 0.45
    for k in range(n):
        phi = face_phi(n, rot, k)
        if phis is not None and not any(abs(((phi - p + 180.0) % 360.0) - 180.0) < 1.0 for p in phis):
            continue
        W = face_frame(x, y, ap, phi)
        cx_, cy_ = _P(W, 0.0, 0.6, 0.0)[:2]
        if hide and hide(cx_, cy_):
            continue
        z0 = z_s if zmin_fn is None else max(z_s, zmin_fn(cx_, cy_))
        for i, (ztop, tier) in enumerate(tiers):
            if ztop - 0.35 > z0 + 0.5:
                coursed(mb, W, -side / 2 + 0.04, side / 2 - 0.04, z0, ztop - 0.35,
                        (excl or {}).get(int(round(phi)) % 360, ()), tier, phase + 0.6 * (k % 2) + 0.3 * i)
            z0 = max(z0, ztop + 0.4)
    zc = z_s - 0.45
    for ztop, tier in tiers:
        if ztop > zc + 1.0:
            band(mb, x, y, r, n, ztop - 0.25, rot, h=0.8, e=0.42)


def dormer_roof(mb, x, y, z0, w, d, h, a):
    """telhadinho de lucarna em 2 aguas com a cumeeira PARA FORA e testeira de obsidiana"""
    ca, sa = math.cos(a), math.sin(a)
    tx, ty = -sa, ca

    def P(u, t, zz):
        return (x + ca * t + tx * u, y + sa * t + ty * u, zz)
    bm = mb.bm
    hw, hd = w / 2 + 0.2, d / 2 + 0.25
    V = [bm.verts.new(P(u, t, zz)) for u, t, zz in ((-hw, -hd, z0), (hw, -hd, z0), (hw, hd, z0), (-hw, hd, z0),
                                                    (0.0, -hd, z0 + h), (0.0, hd, z0 + h))]
    fs = [bm.faces.new((V[0], V[1], V[2], V[3])), bm.faces.new((V[0], V[3], V[5], V[4])),
          bm.faces.new((V[1], V[4], V[5], V[2])), bm.faces.new((V[0], V[4], V[1])), bm.faces.new((V[3], V[2], V[5]))]
    _faces_ok(mb, fs)
    mb._post(V, NAVY, None, 0, 1)
    for sg in (-1, 1):
        mb.beam(P(sg * (hw + 0.05), hd + 0.02, z0 - 0.05), P(0.0, hd + 0.02, z0 + h + 0.12), 0.36, 0.3, OB, 0.0)
    pt = P(0.0, hd - 0.1, 0.0)
    finial(mb, pt[0], pt[1], z0 + h - 0.1, 0.7)


def dormers(mb, x, y, rs, n_, zbase, h_sp, phis, s=1.0):
    """lucarnas numa agulha: caixa de pedra, janela ESCURA (venezianas) e telhadinho de 2 aguas"""
    for phi in phis:
        a = math.radians(phi)
        d = rs * 0.62
        lz = zbase + h_sp * 0.18
        lx, ly = x + d * math.cos(a), y + d * math.sin(a)
        mb.box((2.0 * s, 2.6 * s, 4.2 * s), (lx, ly, lz + 2.1 * s), (0, 0, a), CM_, 0.0)
        lancet_win(mb, face_frame(lx, ly, 1.0 * s, phi), 0.0, lz + 0.7 * s, 2.8 * s, 1.1 * s, 0.0, glass="louver",
                   dp=0.3, fw=0.2 * s)
        dormer_roof(mb, lx, ly, lz + 4.2 * s, 2.6 * s, 2.0 * s, 2.6 * s, a)


def tower_crown(mb, x, y, r, n, rot, top, h_sp, n_pin=True, pin_s=0.7, sp_r=None, dorm=None, fin=2.4):
    """coroamento de torre: mata-caes + parapeito (F2 corrigido) + pinaculos nos vertices + agulha com aneis"""
    parapet_ring(mb, x, y, r, n, top, 2.4, OB, rot)
    if n_pin:
        for k in range(n):
            if k % 2:
                continue
            a = math.radians(rot + 360.0 * k / n)
            px, py = x + (r + 0.5) * math.cos(a), y + (r + 0.5) * math.sin(a)
            pinnacle(mb, px, py, top + 2.44, pin_s, hb=2.4 * pin_s / 0.7, hn=(9.0 if k % 4 == 0 else 7.0) * pin_s / 0.7,
                     body_m=OB, crock=False, rot=a)
    rs = sp_r or r - 1.2
    spire(mb, x, y, rs, n, top + 2.44, h_sp, NAVY, rot, rings=(0.3, 0.62))
    if dorm:
        dormers(mb, x, y, rs, n, top + 2.44, h_sp, dorm, s=max(0.8, rs / 12.0))
    finial(mb, x, y, top + 2.44 + h_sp - 0.3, fin)


# ------------------------------------------------------------------ helpers do banzo das escadas (sem importar sg_entry)
def yz_block(mb, x0, x1, pts, m, bevel=0.0):
    bm = mb.bm
    va = [bm.verts.new((x0, y, z)) for y, z in pts]
    vb = [bm.verts.new((x1, y, z)) for y, z in pts]
    n = len(pts)
    faces = [bm.faces.new(list(reversed(va))), bm.faces.new(vb)]
    for i in range(n):
        j = (i + 1) % n
        faces.append(bm.faces.new((va[i], va[j], vb[j], vb[i])))
    _faces_ok(mb, faces)
    mb._post(va + vb, m, None, bevel, 1)


def _clip_y(poly, ya, yb):
    p = SL.clip(poly, 1.0, 0.0, yb)
    return SL.clip(p, -1.0, 0.0, -ya)


def banzo(mb, name, s, yb_max):
    """banzo continuo da escada 'name' (mesma receita da entrada): fiadas de cantaria sob a linha inclinada, rodape,
    capa inclinada em pecas com pingadeira"""
    foot, deg, w, n, tread, g = L.stair_frame(name)
    rise = (L.STAIR_TOP_Z[name] - foot[2]) / n
    ya, yb = foot[1], min(foot[1] + tread * n, yb_max)
    ta = foot[2] + 1.25
    k = rise / tread
    tb = ta + k * (yb - ya)
    xc = foot[0]
    x0, x1 = sorted((xc + s * (w / 2), xc + s * (w / 2 + 1.4)))
    zb = foot[2] - 0.3
    c0, ci = zb, 0
    while c0 < tb - 0.05:
        c1 = min(c0 + (1.0, 0.8)[ci % 2], tb)
        if c1 <= ta:
            poly = [(ya, c0), (yb, c0), (yb, c1), (ya, c1)]
        else:
            ys0 = ya + max(0.0, (c0 - ta) / k)
            ys1 = min(yb, ya + (c1 - ta) / k)
            poly = [(ys0, c0), (yb, c0), (yb, c1), (ys1, c1)]
            if c0 < ta:
                poly.append((ya, ta))
        off = (0.0, 1.7)[ci % 2]
        cuts = [ya] + [ya + off + 3.4 * j for j in range(1, 12) if ya + off + 3.4 * j < yb - 0.8] + [yb]
        for u0, u1 in zip(cuts, cuts[1:]):
            bp = _dedupe(_clip_y(poly, u0 + 0.04, u1 - 0.04))
            if len(bp) >= 3 and abs(SL.area(bp)) > 0.2 and max(p[0] for p in bp) - min(p[0] for p in bp) > 0.3:
                yz_block(mb, x0, x1, bp, CM_, 0.0)
        c0, ci = c1, ci + 1
    from mathutils import Vector
    xm = xc + s * (w / 2 + 0.7)
    A = Vector((xm, ya - 0.2, ta - 0.2 * k))
    B = Vector((xm, yb, tb))
    dd = B - A
    nseg = max(1, int(round(dd.length / 2.5)))
    for j in range(nseg):
        p0 = A + dd * (j / nseg) + dd.normalized() * (0.03 if j else 0.0)
        p1 = A + dd * ((j + 1) / nseg) - dd.normalized() * (0.03 if j < nseg - 1 else 0.0)
        mb.beam((p0.x, p0.y, p0.z + 0.26), (p1.x, p1.y, p1.z + 0.26), 1.75, 0.32, CAPL, 0.06)
    mb.beam((xm, A.y + 0.1, A.z + 0.1 * k + 0.04), (xm, B.y - 0.1, B.z - 0.1 * k + 0.04), 1.56, 0.12, CAPL, 0.0)
    # pilarete de arranque (plinto, fuste chanfrado, capitel, remate de bola)
    px, py = xc + s * (w / 2 + 0.7), ya - 0.4
    mb.box((2.0, 2.0, 0.55), (px, py, foot[2] + 0.275), (0, 0, 0), ASH, 0.08)
    mb.prism(sq_ch(px, py, 0.8, 0.16), foot[2] + 0.55, foot[2] + 2.9, CM_)
    mb.box((1.9, 1.9, 0.22), (px, py, foot[2] + 3.0), (0, 0, 0), CAPL, 0.05)
    finial(mb, px, py, foot[2] + 3.1, 1.0, CAPL)


def stairs():
    mb = MB("SG_Cas_Escadas", "04_CASTLE", random.Random(5103), detail="near")
    SL.plan_stair(mb, "Gate", stringers=False)
    SL.plan_stair(mb, "EastP3", stringers=False)
    for s in (-1, 1):
        banzo(mb, "Gate", s, WFRONT - 0.6)
        banzo(mb, "EastP3", s, WFRONT - 0.6)
    mb.finish()



# ------------------------------------------------------------------ 1. MURALHA, PORTAO 24 x 32, torres, passagem leste
def _near_play(x):
    """trecho da muralha onde o jogador chega perto pelo lado do P2 (escadas do portao e da passagem leste)"""
    return abs(x) < 50.0 or x > 118.0


def machicolations(mb, Wo, a, b, zt, m=CM_):
    """MATA-CAES no topo de uma face (W com t para fora, face em t = 0): fundo escuro, misulas em 3 degraus, arquinhos
    entre elas, parapeito, capa chanfrada (acima do corpo: F4) e merloes em 2 larguras com seteira"""
    ledge(mb, Wo, a, b, [(-0.05, zt - 3.35), (0.14, zt - 3.35), (0.14, zt - 1.5), (-0.05, zt - 1.5)], OB)
    n = max(1, int(round((b - a) / 4.2)))
    step = (b - a) / n
    cx = [a + (k + 0.5) * step for k in range(n)]
    for x in cx:
        ledge(mb, Wo, x - 0.38, x + 0.38, [(-0.05, zt - 3.35), (0.36, zt - 3.35), (0.36, zt - 2.6), (0.92, zt - 2.1),
                                           (0.92, zt - 1.55), (-0.05, zt - 1.55)], OB)
    for x0_, x1_ in zip([a] + cx, cx + [b]):
        u0_, u1_ = x0_ + (0.38 if x0_ > a else 0.0), x1_ - (0.38 if x1_ < b else 0.0)
        if u1_ - u0_ < 0.6:
            continue
        uc, ha = (u0_ + u1_) / 2, (u1_ - u0_) / 2
        zs = zt - 2.25
        arc = [(uc - ha * math.cos(math.pi * i / 4), zs + 0.5 * math.sin(math.pi * i / 4)) for i in range(5)]
        panel(mb, Wo, [(u0_, zt - 1.5)] + arc + [(u1_, zt - 1.5)], 0.26, 0.74, m)
    panel(mb, Wo, rect(a, b, zt - 1.6, zt), -0.2, 0.76, m)
    ledge(mb, Wo, a - 0.05, b + 0.05, [(-0.6, zt - 0.3), (0.9, zt - 0.3), (0.9, zt + 0.1), (0.62, zt + 0.36),
                                       (-0.6, zt + 0.36)], OB)
    for k, x in enumerate(cx):
        if k % 2:
            continue
        wide = (k // 2) % 2 == 0
        w = min(2.4 if wide else 1.5, step * 0.95)
        panel(mb, Wo, rect(x - w / 2, x + w / 2, zt + 0.3, zt + 2.3), -0.7, 0.62, m)
        ledge(mb, Wo, x - w / 2 - 0.12, x + w / 2 + 0.12, [(-0.82, zt + 2.24), (0.74, zt + 2.24), (0.74, zt + 2.4),
                                                           (-0.04, zt + 2.66), (-0.82, zt + 2.66)], OB)
        if wide and (b - a) < 60.0:
            panel(mb, Wo, rect(x - 0.11, x + 0.11, zt + 0.9, zt + 1.95), 0.62, 0.76, OB)
            panel(mb, Wo, rect(x - 0.21, x + 0.21, zt + 0.62, zt + 0.94), 0.62, 0.76, OB)


def wall_tower(mb, x, y, r, top, sph, lit=False, banners=None, bw=3.8):
    """torre octogonal da muralha: soco no P2, fuste com ladrilhado (face do P2 e do patio), seteiras escuras, uma
    janela ACESA em vao (so nas torres do portao), parapeito com mata-caes e agulha"""
    rot, n = 22.5, 8
    ap = r * math.cos(math.pi / n)

    def in_wall(cx_, cy_):
        return WFRONT - 0.3 < cy_ < L.WALL_Y1 + 0.3 and L.WALL_X[0] - 1 < cx_ < L.WALL_X[1] + 1

    socle(mb, x, y, r, n, Z2 - 0.6, Z2 + 3.4, rot, e=1.0)
    if lit:
        zl = Z + 26.0
        shaft(mb, x, y, r, n, Z2 + 3.4, zl, CM_, rot)
        k_s = face_index(n, rot, 270.0)
        op = (0.0, 1.6, zl + 1.4, zl + 7.6, 2.6)
        faces = shaft_band(mb, x, y, r, n, rot, zl, zl + 12.0, CM_, {k_s: [op]}, d=1.4)
        W = faces[k_s][0]
        rwin(mb, W, *op, 0.0, 1.4, kind="lit", frame_m=CAPL, fw=0.55, dp=0.5, hood=True)
        panel(mb, W, rect(-1.7, 1.7, zl + 5.1, zl + 5.4), -1.2, -0.3, CAPL)          # travessa de pedra (pontas embutidas)
        shaft(mb, x, y, r, n, zl + 12.0, top, CM_, rot)
    else:
        shaft(mb, x, y, r, n, Z2 + 3.4, top, CM_, rot)
    s = 1 if x > 0 else -1
    out_phi = 0.0 if s > 0 else 180.0
    slits = [(p % 360.0, zz, h, w) for p, zz, h, w in ((270.0, Z + 4.0, 4.2, 1.0), (270.0 + s * 45.0, Z + 11.0, 3.8, 0.9),
                                                     (out_phi, Z + 20.0, 3.8, 0.9), (90.0, Z + 12.0, 3.6, 0.9))
             if top - zz >= 8.0]
    ex = {}
    for phi, zz, h, w in slits:
        ex.setdefault(int(round(phi)) % 360, []).append((-w / 2 - 0.8, w / 2 + 0.8, zz - 0.9, zz + h + 0.5))
    tower_skin(mb, x, y, r, n, rot, Z2 - 0.6, ((Z2 + 10.0, 0), (Z + 14.0, 1)), soc=False, hide=in_wall,
               phis=(225.0, 270.0, 315.0), excl=ex)
    if abs(x) < 60.0:
        tower_skin(mb, x, y, r, n, rot, Z - 0.3, ((Z + 8.0, 0 if abs(x) < 60 else 1),), soc=False, hide=in_wall,
                   phis=(45.0, 90.0, 135.0), excl=ex)
    band(mb, x, y, r, n, WALL_TOP - 1.4, rot, h=1.4, e=0.4)
    for phi, zz, h, w in slits:
        slit(mb, face_frame(x, y, ap, phi), zz, h, w)
    tower_crown(mb, x, y, r, n, rot, top, sph, n_pin=r >= 9.0, pin_s=0.7, fin=1.6 if r > 6 else 1.1)
    if banners is not None:
        W = face_frame(x, y, ap, 270.0)
        banners.append((_P(W, 0.0, 0.5, Z + 22.0), -math.pi / 2, bw, 16.0, 0.5))
    ngon_col("SG_CasTower", x, y, n, r, Z2 - 0.5, top, rot)


def muralha(banners):
    """muralha nova (PLANO 2.2): 10 de espessura, passeio P3+24, mata-caes e ameias, face do P2 com talude de
    obsidiana e silhar em 3 escalas; F3: a face externa fica 0,6 NA FRENTE do arrimo do P3 e desce ate o P2 (a base
    nao e vestida duas vezes - o terreno nao precisa vestir a face y -23 atras da muralha); F4: capas acima do corpo."""
    rng = random.Random(5101)
    mb = MB("SG_Cas_Muralha", "04_CASTLE", rng, detail="near")
    wy1 = L.WALL_Y1
    segs = [(L.WALL_X[0] - 0.3, -GPW), (GPW, EG_X - EG_W / 2), (EG_X + EG_W / 2, L.WALL_X[1] + 0.3)]
    Wo = ((0.0, WFRONT), (1.0, 0.0), (0.0, -1.0))
    Wi = ((0.0, wy1), (1.0, 0.0), (0.0, 1.0))
    towers = [(x, r) for x, y, r, t_, s_ in WALL_TOWERS] + [(x, 12.0) for x, y, r in L.GATEHOUSE_TOWERS]

    def excl(z0, z1):
        return [(x - r - 1.6, x + r + 1.6, z0 - 1.0, z1 + 1.0) for x, r in towers]

    def vis_spans(a, b):
        out = [(a, b)]
        for x, r in towers:
            e0, e1 = x - r * 0.92 + 0.6, x + r * 0.92 - 0.6
            nxt = []
            for u0, u1 in out:
                if e1 <= u0 or e0 >= u1:
                    nxt.append((u0, u1))
                    continue
                if e0 - u0 > 1.2:
                    nxt.append((u0, e0))
                if u1 - e1 > 1.2:
                    nxt.append((e1, u1))
            out = nxt
        return out
    for a0, b0 in segs:
        mb.box2((a0, WFRONT, Z2 - 0.6), (b0, wy1, WALL_TOP), CM_, 0.0)
        col_box2("SG_CasWall", (a0, WFRONT, Z2 - 0.5), (b0, wy1, WALL_TOP))
        for a, b in vis_spans(a0, b0):
            a, b = a - 0.06, b + 0.06
            # face do P2: talude + filete, silhar (fino perto das escadas), cordao no nivel do P3, fiadas medias
            ledge(mb, Wo, a, b, [(-0.05, Z2 - 0.6), (1.1, Z2 - 0.6), (1.1, Z2 + 0.9), (0.2, Z2 + 3.2), (-0.05, Z2 + 3.2)],
                  OB)
            ledge(mb, Wo, a, b, [(-0.05, Z2 + 3.2), (0.34, Z2 + 3.2), (0.34, Z2 + 3.5), (-0.05, Z2 + 3.5)], SV)
            cuts = sorted({a, b} | {c for c in (-50.0, 50.0, 118.0) if a < c < b})
            for c0, c1 in zip(cuts, cuts[1:]):
                fine = _near_play((c0 + c1) / 2)
                coursed(mb, Wo, c0 + 0.05, c1 - 0.05, Z2 + 3.56, Z - 0.8, excl(Z2, Z), 0 if fine else 1, 0.3)
            ledge(mb, Wo, a, b, drip(Z - 0.3, 0.6, 0.9), OB)
            coursed(mb, Wo, a + 0.05, b - 0.05, Z + 0.4, WALL_TOP - 3.7, excl(Z, WALL_TOP), 2, 1.1)
            machicolations(mb, Wo, a, b, WALL_TOP)
            # face do PATIO: rodape em talude, silhar (fino perto do portao), cordao, fiadas grandes, parapeito do passeio
            ledge(mb, Wi, a, b, plinth(Z - 0.3, Z + 1.25, 0.5, 0.22), OB)
            cuts = sorted({a, b} | {c for c in (-60.0, 60.0) if a < c < b})
            for c0, c1 in zip(cuts, cuts[1:]):
                coursed(mb, Wi, c0 + 0.05, c1 - 0.05, Z + 1.3, Z + 7.7, excl(Z, Z + 8.0),
                        0 if abs((c0 + c1) / 2) < 60 else 1, 1.4)
            ledge(mb, Wi, a, b, drip(Z + 8.0, 0.45), OB)
            if abs((a + b) / 2) < 100.0:
                coursed(mb, Wi, max(a, -100.0) + 0.05, min(b, 100.0) - 0.05, Z + 8.4, WALL_TOP - 0.4,
                        excl(Z, WALL_TOP), 2, 0.7)
            mb.box2((a, wy1 - 0.8, WALL_TOP), (b, wy1, WALL_TOP + 1.1), CM_, 0.0)
            ledge(mb, Wi, a - 0.02, b + 0.02, [(-0.95, WALL_TOP + 0.8), (0.14, WALL_TOP + 0.8), (0.14, WALL_TOP + 1.16),
                                               (-0.2, WALL_TOP + 1.4), (-0.95, WALL_TOP + 1.4)], OB)
    # testas da muralha na passagem leste (o jogador passa colado): silhar medio nas 2 faces do vao
    for xe, sg in ((EG_X - EG_W / 2, 1.0), (EG_X + EG_W / 2, -1.0)):
        We = ((xe, 0.0), (0.0, 1.0), (sg, 0.0))
        coursed(mb, We, WFRONT + 0.1, wy1 - 0.1, Z - 0.3, WALL_TOP - 3.6, (), 1, 0.4)
    # ---------------------------------------------------------------- PORTAO 24 x 32
    # anel da frente (0,6 saliente) com o vao ogival; portaria entre as torres ate Z+38; abobada da passagem (Z+27,
    # flecha 9) acima das folhas; aduelas alternando pedra violeta e obsidiana com fecho, arco-capa com pingadeira
    Wg = ((0.0, WFRONT), (1.0, 0.0), (0.0, -1.0))
    wall_run(mb, Wg, -GPW, GPW, Z2 - 0.6, GH_TOP, -2.2, 0.6, [(0.0, GW / 2, Z2 - 0.6, GSPR, GRISE)], CM_)
    for s in (-1, 1):
        a_, b_ = sorted((s * GPW, s * 24.0))
        mb.box2((a_, WFRONT, WALL_TOP), (b_, wy1, GH_TOP - 0.05), CM_, 0.0)
    Wv = ((0.0, 0.0), (1.0, 0.0), (0.0, 1.0))
    panel(mb, Wv, [(GPW, GH_TOP), (-GPW, GH_TOP)] + ogive(0.0, GPW, GVSPR, GVRISE, n=8), WFRONT + 2.2, wy1, CM_)
    # aduelas (voussoirs) radiais no anel da frente
    nv = 13
    arc_i = ogive(0.0, GW / 2, GSPR, GRISE, n=13)
    arc_o = ogive(0.0, GW / 2, GSPR, GRISE, d=2.4, n=13)
    per = (len(arc_i) - 1) / nv
    for k in range(nv):
        i0, i1 = int(round(k * per)), int(round((k + 1) * per))
        lo = arc_i[i0:i1 + 1]
        hi = arc_o[i0:i1 + 1]
        key = k == nv // 2
        panel(mb, Wg, lo + list(reversed(hi)), 0.62, 1.25 if key else 0.98, VI if (key or k % 2 == 0) else OB)
    for s in (-1, 1):
        u0_, u1_ = sorted((s * GW / 2, s * (GW / 2 + 2.4)))
        panel(mb, Wg, rect(u0_, u1_, Z - 1.0, GSPR), 0.62, 0.98, VI)
        panel(mb, Wg, rect(u0_ - 0.2, u1_ + 0.2, GSPR - 1.1, GSPR), 0.62, 1.3, OB)     # imposta
    h0 = ogive(0.0, GW / 2, GSPR, GRISE, d=2.4, n=13)
    h1 = ogive(0.0, GW / 2, GSPR, GRISE, d=3.1, n=13)
    panel(mb, Wg, h0 + list(reversed(h1)), 0.55, 1.4, OB)
    # machicolagem da portaria + parapeito com ameias sobre o portao
    Wgf = ((0.0, WFRONT - 0.6), (1.0, 0.0), (0.0, -1.0))
    machicolations(mb, Wgf, -24.0, 24.0, GH_TOP)
    Wgb = ((0.0, wy1), (1.0, 0.0), (0.0, 1.0))
    ledge(mb, Wgb, -24.0, 24.0, [(-0.95, GH_TOP - 0.3), (0.3, GH_TOP - 0.3), (0.3, GH_TOP + 0.36),
                                 (-0.95, GH_TOP + 0.36)], OB)
    # arco de tras (patio): moldura em U na face do patio
    arch_band(mb, Wgb, 0.0, GPW, Z - 0.3, GVSPR, GVRISE, 1.6, -0.05, 0.6, VI, n=8)
    # grade levadica recolhida: dentes a vista sob o fecho, no sulco do anel
    c_ = (GRISE * GRISE - (GW / 2) ** 2) / GW
    R_ = GW / 2 + c_
    for k in range(7):
        x = -3.6 + 1.2 * k
        zi = GSPR + math.sqrt(max(0.0, R_ * R_ - (abs(x) + c_) ** 2))
        mb.box2((x - 0.13, WFRONT + 0.85, zi - 0.7), (x + 0.13, WFRONT + 1.15, GSPR + GRISE + 1.0), BI, 0.0)
        mb.cyl(0.16, 0.5, (x, WFRONT + 1.0, zi - 0.95), (math.pi, 0, math.pi / 4), BI, n=4, r2=0.0, bevel=0.0)
    # FOLHAS 12 x 26 abertas DENTRO do rebaixo da passagem (vao livre continua 24)
    for s in (-1, 1):
        xa, xb = s * (GW / 2 + 0.12), s * (GW / 2 + 0.62)
        y0_, y1_ = WFRONT + 2.3, WFRONT + 2.3 + 12.0
        lz0, lz1 = Z + 0.1, Z + 26.0
        nb = 5
        for i in range(nb):
            ya_ = y0_ + i * 12.0 / nb + (0.03 if i else 0.0)
            yb_ = y0_ + (i + 1) * 12.0 / nb - (0.03 if i < nb - 1 else 0.0)
            mb.box2((min(xa, xb), ya_, lz0), (max(xa, xb), yb_, lz1), WD, 0.0)
        xf = xa - s * 0.08
        for zz in (lz0 + 2.0, lz0 + 9.0, lz0 + 17.0, lz1 - 2.0):
            mb.box2((min(xf, xa), y0_ + 0.3, zz - 0.22), (max(xf, xa), y1_ - 0.3, zz + 0.22), BI, 0.0)
            for q in range(6):
                yy = y0_ + 0.9 + q * (12.0 - 1.8) / 5.0
                mb.cyl(0.09, 0.08, (xf - s * 0.04, yy, zz), (0, s * math.pi / 2, 0), BI, n=6, r2=0.04, bevel=0.0)
            mb.cyl(0.16, 1.2, (s * (GW / 2 + 0.05), y0_ - 0.05, zz), (0, 0, 0), BI, n=8, bevel=0.0)
        col_box2("SG_CasGateLeaf", (min(xa, xb), y0_, Z - 0.5), (max(xa, xb), y1_, lz1))
    # torres do portao (R 12, topo P3+44) com a janela acesa virada para a vila e o estandarte da ordem
    for (x, y, r0) in L.GATEHOUSE_TOWERS:
        wall_tower(mb, x, y, r0, GT_TOP, 26.0, lit=True, banners=banners)
    for x, y, r, top, sph in WALL_TOWERS:
        wall_tower(mb, x, y, r, top, sph)
    # lanternas da ordem SO nos nos (patio, ao lado do portao e da passagem leste)
    for sx in (-1, 1):
        EM.lantern_post(mb, mb, (sx * 17.5, -7.0, Z), 0.0, h=7.5, s=0.95)
    EM.lantern_post(mb, mb, (EG_X - 12.0, -7.0, Z), 0.0, h=7.0, s=0.9)
    col_box2("SG_CasWall", (-24.0, WFRONT, GVSPR), (24.0, wy1, GH_TOP))
    _fin(mb)



# ------------------------------------------------------------------ 2. NAVE 2x (casca do Mining Hall) em perfil de basilica
W_E = ((HX1, 0.0), (0.0, 1.0), (1.0, 0.0))            # u = y, t = x - 92 (0 = face interna, 5 = externa)
W_W = ((HX0, 0.0), (0.0, 1.0), (-1.0, 0.0))
W_S = ((0.0, HY0), (1.0, 0.0), (0.0, -1.0))            # u = x, t = 66 - y
W_N = ((0.0, HY1), (1.0, 0.0), (0.0, 1.0))             # u = x, t = y - 262
AISLE_WX = 70.5                                        # eixo das janelas das naves laterais na fachada / no fundo


def lean_z(ax):
    """cota da meia-agua da nave lateral na distancia |x| (nasce atras do parapeito, encosta no clerestorio)"""
    x0, z0, x1, z1 = OX1 + 1.0, EAVE + 0.5, CLR, LEAN_HI
    return z0 + (x0 - ax) / (x0 - x1) * (z1 - z0)


def nave_window(mb, W, uc):
    """janela alta da nave (10 x 34): vao de verdade na parede de 5, vidro de LUAR a 2 da face externa (o vitral do
    salao fica do lado de dentro), 2 lancetas + oculo no rendilhado, moldura de cantaria com capa-gota"""
    tf = TW
    poly = opening(uc, WIN_A, WIN_SILL, WIN_SPRING, WIN_RISE, n=4)
    tg = tf - 2.0
    panel(mb, W, poly, tg - 0.04, tg + 0.04, MOON)
    nz = int((WIN_SPRING - WIN_SILL) / 5.0)
    for k in range(1, nz + 1):
        zz = WIN_SILL + (WIN_SPRING - WIN_SILL) * k / (nz + 1)
        panel(mb, W, rect(uc - WIN_A, uc + WIN_A, zz - 0.07, zz + 0.07), tg + 0.14, tg + 0.24, BI)
    # rendilhado de cantaria (mainel + 2 subarcos + oculo) na frente do vidro
    panel(mb, W, rect(uc - 0.4, uc + 0.4, WIN_SILL, WIN_SPRING + 2.0), tg + 0.14, tg + 1.2, CAPL)
    sub = (WIN_A - 0.4) / 2.0
    for s in (-1, 1):
        c_ = uc + s * (0.4 + sub)
        i0 = ogive(c_, sub, WIN_SPRING - 0.4, sub * 1.6, n=3)
        i1 = ogive(c_, sub, WIN_SPRING - 0.4, sub * 1.6, d=0.36, n=3)
        panel(mb, W, i0 + list(reversed(i1)), tg + 0.14, tg + 1.0, CAPL)
    U, V, N = WUVN(W)
    zc = WIN_SPRING + WIN_RISE * 0.6
    ring(mb, _P(W, uc, 0.0, zc), U, V, N, 1.55, 1.95, tg + 0.14, tg + 1.0, CAPL, 10)
    # ordens da moldura: capialco em 2 degraus (a face interna do vao) + moldura saliente + capa-gota
    arch_band(mb, W, uc, WIN_A, WIN_SILL, WIN_SPRING, WIN_RISE, 1.6, tf - 0.05, tf + 0.55, CAPL, n=4)
    h0 = ogive(uc, WIN_A, WIN_SPRING, WIN_RISE, d=1.6, n=4)
    h1 = ogive(uc, WIN_A, WIN_SPRING, WIN_RISE, d=2.2, n=4)
    panel(mb, W, h0 + list(reversed(h1)), tf - 0.05, tf + 0.85, OB)
    for s in (-1, 1):
        u0_, u1_ = sorted((uc + s * (WIN_A + 1.55), uc + s * (WIN_A + 2.5)))
        panel(mb, W, rect(u0_, u1_, WIN_SPRING - 1.1, WIN_SPRING + 0.02), tf - 0.05, tf + 0.95, OB)
    panel(mb, W, rect(uc - WIN_A - 2.0, uc + WIN_A + 2.0, WIN_SILL - 0.7, WIN_SILL), tf - 0.05, tf + 0.9, CAPL)


def buttress(mb, s, y):
    """CONTRAFORTE da nave: soco em talude, 1o lance (7 de saliencia) com silhar, ressalto em talude a Z+40, 2o lance
    (4,6) ate acima da cornija, pinaculo do kit; ARCOBOTANTES DUPLOS por cima da meia-agua (pilar intermediario em
    |x| 70 com pinaculo) ate o clerestorio"""
    xo = s * OX1
    bp, bp2, hw = 7.0, 4.6, 2.3
    Wb = ((xo, 0.0), (0.0, 1.0), (float(s), 0.0))              # u = y, t = saliencia a partir da face da nave
    ledge(mb, Wb, y - hw - 0.6, y + hw + 0.6, plinth(ZB, SOC, bp + 0.75, bp + 0.25), OB)
    ledge(mb, Wb, y - hw - 0.3, y + hw + 0.3, [(-0.1, SOC), (bp + 0.2, SOC), (bp + 0.2, SOC + 0.3), (-0.1, SOC + 0.3)],
          SV)
    z1 = Z + 40.0
    ledge(mb, Wb, y - hw, y + hw, [(-0.1, SOC), (bp, SOC), (bp, z1), (bp2 - 0.05, z1 + bp - bp2 + 0.05),
                                   (-0.1, z1 + bp - bp2 + 0.05)], CM_)
    ledge(mb, Wb, y - hw - 0.12, y + hw + 0.12, [(bp - 0.2, z1 - 0.7), (bp + 0.26, z1 - 0.6), (bp + 0.26, z1 - 0.3),
                                                 (bp - 0.2, z1 - 0.05)], OB)
    # ladrilhado nas 3 faces do 1o lance (fino ate +8, medio ate +26, grande ate o ressalto)
    Wf = ((xo + s * bp, 0.0), (0.0, 1.0), (float(s), 0.0))
    for i, (z0_, z1_, tier) in enumerate(((SOC + 0.34, Z + 7.7, 0), (Z + 8.4, Z + 25.7, 1))):
        coursed(mb, Wf, y - hw, y + hw, z0_, z1_, (), tier, 0.55 if s > 0 else 0.0)
        if tier == 0:
            for sy in (-1, 1):
                Ws = ((0.0, y + sy * hw), (float(s), 0.0), (0.0, float(sy)))
                coursed(mb, Ws, OX1 + 0.05, OX1 + bp - 0.02, z0_, z1_, (), tier, 0.4)
    for zc_ in (Z + 8.0, Z + 26.0):
        ledge(mb, Wf, y - hw - 0.55, y + hw + 0.55, drip(zc_, 0.5), OB)
        for sy in (-1, 1):
            Ws = ((0.0, y + sy * hw), (float(s), 0.0), (0.0, float(sy)))
            ledge(mb, Ws, OX1 - 0.1, OX1 + bp + 0.5, drip(zc_, 0.5), OB)
    # 2o lance ate acima da cornija da nave lateral + pinaculo
    z2 = z1 + bp - bp2 + 0.05
    ztop = EAVE + 14.0
    ledge(mb, Wb, y - hw + 0.3, y + hw - 0.3, [(-0.1, z2 - 0.1), (bp2, z2 - 0.1), (bp2, ztop), (-0.1, ztop)], CM_)
    for zc_ in (Z + 72.0, EAVE - 1.2):
        ledge(mb, Wb, y - hw, y + hw, [(bp2 - 0.1, zc_ - 0.3), (bp2 + 0.4, zc_ - 0.2), (bp2 + 0.4, zc_ + 0.3),
                                       (bp2 - 0.1, zc_ + 0.5)], OB)
    # nicho cego com gablete na face do 2o lance (le "contraforte gotico" do beco)
    pinnacle(mb, xo + s * bp2 / 2.0, y, ztop, 1.25, hb=6.5, hn=12.0)
    # arcobotantes
    xm = 70.0
    zc, b = EAVE + 6.5, 9.0
    d_out, d_in = OX1 + 0.3, xm + 1.6
    Wfl = ((0.0, y), (float(s), 0.0), (0.0, 1.0))
    lo, hi = [], []
    for i in range(9):
        th = (math.pi / 2) * i / 8
        d = d_in + (d_out - d_in) * math.cos(th)
        lo.append((d, zc + b * math.sin(th)))
        hi.append((d, (ztop - 3.0) + (d_out - d) / (d_out - d_in) * 4.0))
    strip(mb, Wfl, lo, hi, -0.75, 0.75, CM_)
    mb.beam((s * d_out, y, hi[0][1] + 0.18), (s * d_in, y, hi[-1][1] + 0.18), 1.8, 0.36, OB, 0.0)
    # pilar intermediario sobre a meia-agua
    zpb = lean_z(xm) - 1.5
    zpt = LEAN_HI + 10.0
    mb.prism(sq_ch(s * xm, y, 1.6, 0.35), zpb, zpt, CM_)
    frustum(mb, s * xm, y, 2.2, 2.0, 8, zpt - 0.05, zpt + 0.5, OB, 22.5)
    pinnacle(mb, s * xm, y, zpt + 0.5, 0.9, hb=4.5, hn=9.0, crock=False)
    zc2, b2 = LEAN_HI - 1.0, 10.0
    d_out2, d_in2 = xm - 1.6, CLR
    lo, hi = [], []
    for i in range(9):
        th = (math.pi / 2) * i / 8
        d = d_in2 + (d_out2 - d_in2) * math.cos(th)
        lo.append((d, zc2 + b2 * math.sin(th)))
        hi.append((d, (zpt - 2.0) + (d_out2 - d) / (d_out2 - d_in2) * 4.0))
    strip(mb, Wfl, lo, hi, -0.7, 0.7, CM_)
    mb.beam((s * d_out2, y, hi[0][1] + 0.18), (s * d_in2, y, hi[-1][1] + 0.18), 1.7, 0.34, OB, 0.0)
    col_box2("SG_CasButtress", (min(xo, xo + s * bp), y - hw, Z - 0.5), (max(xo, xo + s * bp), y + hw, Z + 24.0))


def nave():
    rng = random.Random(5201)
    mb = MB("SG_Cas_Nave", "04_CASTLE", rng, detail="near")
    # --- paredes laterais: face interna exata no retangulo do salao, 7 janelas altas por lado (vao de verdade)
    opens = [(y, WIN_A, WIN_SILL, WIN_SPRING, WIN_RISE) for y in WIN_OUT]
    for W in (W_W, W_E):
        s = 1 if W[2][0] > 0 else -1
        wall_run(mb, W, OY0, OY1, ZB, EAVE, 0.0, TW, opens, CM_, IM)
        # a torre da fachada encosta aqui: a parede engrossa 0,6 por baixo dela (sem fresta de luz)
        panel(mb, W, rect(OY0 + 0.3, 79.8, ZB, EAVE), TW - 0.1, TW + 0.62, CM_)
        for y in WIN_OUT:
            nave_window(mb, W, y)
        excl = [(y - WIN_A - 2.6, y + WIN_A + 2.6, WIN_SILL - 1.2, Z + 80.0) for y in WIN_OUT]
        excl += [(y - 2.9, y + 2.9, ZB, EAVE) for y in BUTT_Y]
        wall_skin(mb, W, 80.6, OY1 - 0.4, t=TW, excl=excl, phase=0.3 if s > 0 else 0.0)
        # cordoes no peitoril e na nascenca das janelas + cornija + parapeito da nave lateral
        Wt = (_P(W, 0.0, TW, 0.0)[:2], W[1], W[2])
        for zc_ in (WIN_SILL - 1.5, Z + 80.0):
            ledge(mb, Wt, 80.6, OY1 + 0.6, drip(zc_, 0.45), OB)
        ledge(mb, Wt, OY0 - 0.6, OY1 + 1.1, cornice(EAVE, 1.3, 1.8), OB)
        panel(mb, W, rect(OY0, OY1, EAVE, EAVE + 2.6), TW - 1.3, TW + 0.35, CM_)
        ledge(mb, Wt, OY0 - 0.5, OY1 + 1.0, [(-1.5, EAVE + 2.5), (0.55, EAVE + 2.5), (0.55, EAVE + 2.72),
                                             (0.1, EAVE + 3.0), (-1.5, EAVE + 3.0)], OB)
        for y in BUTT_Y:
            buttress(mb, s, y)
        # contraforte de quina (fundo), em diagonal
        a = math.radians(45.0 if s > 0 else 135.0)
        bx, by = s * (OX1 + 2.2), OY1 + 2.2
        mb.box((5.0, 4.6, EAVE + 10.0 - ZB), (bx, by, (ZB + EAVE + 10.0) / 2), (0, 0, a), CM_, 0.0)
        mb.box((6.4, 6.0, SOC - ZB + 0.4), (bx, by, (ZB + SOC + 0.4) / 2), (0, 0, a), OB, 0.0)
        pinnacle(mb, bx, by, EAVE + 10.0, 1.2, hb=6.0, hn=12.0, rot=a)
        col_box("SG_CasButtress", (5.0, 4.6, 24.0), (bx, by, Z + 11.5), (0, 0, a))
    # --- fundo (norte): arco triunfal 40 x 60 (vao do presbiterio, retangular como o blockout; o sg_hall veste)
    wall_run(mb, W_N, HX0, HX1, ZB, EAVE, 0.0, TW, [(0.0, L.TRI_ARCH_W / 2, ZB, Z + L.TRI_ARCH_H, 0.0)], CM_, IM)
    for s in (-1, 1):
        u0_, u1_ = sorted((s * 38.4, s * (OX1 - 0.4)))
        wall_skin(mb, W_N, u0_, u1_, t=TW, excl=[(s * AISLE_WX - 7.0, s * AISLE_WX + 7.0, Z + 28.0, Z + 72.0)],
                  phase=0.8)
        Wt = ((0.0, OY1), (1.0, 0.0), (0.0, 1.0))
        lancet_win(mb, Wt, s * AISLE_WX, Z + 30.0, 34.0, 8.0, 0.0, glass="dark", frame_m=CAPL, dp=0.6, fw=0.8)
        ledge(mb, Wt, u0_, u1_ + s * 0.6, cornice(EAVE, 1.3, 1.8), OB)
        # empena da meia-agua (fundo)
        ui, uo = s * CLR, s * OX1
        panel(mb, W_N, [(uo, EAVE), (ui, EAVE), (ui, LEAN_HI + 2.4), (uo, EAVE + 2.6)], TW - 1.6, TW, CM_)
        L2 = math.hypot(ui - uo, LEAN_HI - EAVE)
        tilt = math.atan2(LEAN_HI - EAVE, ui - uo)
        mb.box((L2 + 0.8, 2.2, 0.6), _P(W_N, (ui + uo) / 2, TW - 0.7, (LEAN_HI + EAVE) / 2 + 2.9), (0, -tilt, 0), OB,
               0.0)
    # --- sul (fachada): parede do salao (5) com o vao da passagem 28 + rebaixos das folhas; a pele da fachada e do
    #     corpo central sao do facade()
    wall_run(mb, W_S, HX0, HX1, ZB, EAVE, 0.0, TW - 1.2, [(0.0, DW / 2 + POCK, ZB, Z + DH, 0.0)], CM_, IM)
    for s in (-1, 1):
        u0_, u1_ = sorted((s * CLR, s * HX1))
        wall_run(mb, W_S, u0_, u1_, ZB, EAVE, TW - 1.2, TW, [(s * AISLE_WX, WIN_A, WIN_SILL, WIN_SPRING, WIN_RISE)],
                 CM_)
        rwin(mb, W_S, s * AISLE_WX, WIN_A, WIN_SILL, WIN_SPRING, WIN_RISE, TW, 1.2, kind="dark", frame_m=CAPL, fw=0.9,
             dp=0.55, mull=True, tracery=True, hood=True)
        a_, b_ = sorted((s * (CLR + 4.4), s * (OX1 - 0.3)))
        wall_skin(mb, W_S, a_, b_, t=TW, excl=[(s * AISLE_WX - WIN_A - 2.4, s * AISLE_WX + WIN_A + 2.4,
                                                 WIN_SILL - 1.4, Z + 72.0)], phase=0.5)
        Wt = ((0.0, OY0), (1.0, 0.0), (0.0, -1.0))
        # oculo escuro acima da janela + cordoes + cornija + empena da meia-agua (tela inclinada com capa)
        lancet_win(mb, Wt, s * AISLE_WX, Z + 72.0, 12.0, 5.0, 0.0, glass="dark", frame_m=CAPL, dp=0.55, fw=0.6)
        ledge(mb, Wt, a_, b_, drip(WIN_SILL - 1.5, 0.45), OB)
        ledge(mb, Wt, min(a_, b_) - 0.5, max(a_, b_) + 0.5, cornice(EAVE, 1.3, 1.8), OB)
        ui, uo = s * (CLR + 4.0), s * OX1
        panel(mb, W_S, [(uo, EAVE), (ui, EAVE), (ui, LEAN_HI + 1.9), (uo, EAVE + 2.6)], TW - 1.6, TW, CM_)
        L2 = math.hypot(ui - uo, LEAN_HI + 1.9 - EAVE - 2.6)
        tilt = math.atan2(LEAN_HI + 1.9 - EAVE - 2.6, ui - uo)
        mb.box((L2 + 0.8, 2.2, 0.6), _P(W_S, (ui + uo) / 2, TW - 0.7, (LEAN_HI + 1.9 + EAVE + 2.6) / 2 + 0.3),
               (0, -tilt, 0), OB, 0.0)
    # --- clerestorio (x +-44, acima do teto do salao): janelas de luar na face (atras e sotao escuro), cornija
    for s in (-1, 1):
        W = ((s * (CLR - CLR_T), 0.0), (0.0, 1.0), (float(s), 0.0))
        panel(mb, W, rect(OY0, OY1, CEIL + 2.0, CLR_EAVE), 0.0, CLR_T, CM_)
        Wc = ((s * CLR, 0.0), (0.0, 1.0), (float(s), 0.0))
        for y in WIN_OUT:
            lancet_win(mb, Wc, y, LEAN_HI + 2.2, CLR_EAVE - LEAN_HI - 5.2, 4.6, 0.0, glass="dark", frame_m=CAPL,
                       dp=0.55, fw=0.55)
        ledge(mb, Wc, OY0 + 0.5, OY1 + 0.2, drip(LEAN_HI + 1.4, 0.45), OB)
        # mesa de cachorros + cornija do beiral
        ledge(mb, Wc, OY0, OY1 + 0.4, [(-0.2, CLR_EAVE - 1.35), (0.95, CLR_EAVE - 1.35), (0.95, CLR_EAVE - 0.3),
                                       (-0.2, CLR_EAVE - 0.3)], OB)
    # --- teto interno (opaco) na cota do plano + colisao
    mb.box2((HX0, HY0, CEIL), (HX1, HY1, CEIL + 2.0), IM, 0.0)
    mb.finish()
    box_walls_col("SG_CasHall", (HX0, HY0, HX1, HY1), Z - 0.5, EAVE, TW,
                  doors=[("S", 0.0, DW, DH), ("N", 0.0, L.TRI_ARCH_W, L.TRI_ARCH_H)])
    col_box2("SG_CasHallCeil", (OX0, OY0, CEIL), (OX1, OY1, CEIL + 2.0))


def slate_plane(mb, A, B, C, D, rows, m=NAVY, th=0.3):
    """agua de telhado em FIADAS de ardosia sobrepostas: quadrilatero A(beiral esq) B(beiral dir) C(cumeeira dir)
    D(cumeeira esq); cada fiada e uma placa inclinada que cobre 1,25 da seguinte (le escama de longe)"""
    from mathutils import Vector
    A, B, C, D = (Vector(p) for p in (A, B, C, D))
    nrm = (B - A).cross(D - A).normalized()
    if nrm.z < 0:
        nrm = -nrm
    for i in range(rows):
        f0, f1 = i / rows, min(1.0, (i + 1.3) / rows)
        a0, b0 = A + (D - A) * f0, B + (C - B) * f0
        a1, b1 = A + (D - A) * f1, B + (C - B) * f1
        lo_, hi_ = nrm * 0.42, nrm * 0.02               # beirada de cada fiada levantada: a fiada de cima pisa na de baixo
        pts = [a0 + lo_, b0 + lo_, b1 + hi_, a1 + hi_]
        bm = mb.bm
        va = [bm.verts.new(p) for p in pts]
        vb = [bm.verts.new(p + nrm * th) for p in pts]
        fs = [bm.faces.new(va), bm.faces.new(list(reversed(vb)))]
        for k in range(4):
            j = (k + 1) % 4
            fs.append(bm.faces.new((va[k], va[j], vb[j], vb[k])))
        _faces_ok(mb, fs)
        mb._post(va + vb, m, None, 0, 1)


def roofs():
    rng = random.Random(5301)
    mb = MB("SG_Cas_Telhados", "04_CASTLE", rng, detail="near")
    # telhado da nave central: 2 aguas de 49 graus do clerestorio ate a cumeeira 240; frente atras da tela da fachada
    e = 1.8
    x_e = CLR + e
    z_e = CLR_EAVE - 0.4 - e * (RIDGE - CLR_EAVE) / CLR
    yf, yb = FAC_Y + 2.0, OY1 + 1.6
    bm = mb.bm
    V = {k: bm.verts.new(p) for k, p in (("FL", (-x_e, yf, z_e)), ("FR", (x_e, yf, z_e)), ("BL", (-x_e, yb, z_e)),
                                         ("BR", (x_e, yb, z_e)), ("RF", (0.0, yf, RIDGE)), ("RB", (0.0, yb, RIDGE)))}
    for f in (("FL", "RF", "RB", "BL"), ("FR", "BR", "RB", "RF"), ("FL", "FR", "RF"), ("BL", "RB", "BR"),
              ("FL", "BL", "BR", "FR")):
        bm.faces.new([V[n] for n in f])
    mb._post(list(V.values()), NAVY, None, 0, 1)
    Ls = math.hypot(x_e, RIDGE - z_e)
    rows = int(Ls / 2.3)
    for s in (-1, 1):
        slate_plane(mb, (s * x_e, yf, z_e), (s * x_e, yb, z_e), (0.0, yb, RIDGE), (0.0, yf, RIDGE), rows)
        # testeira de obsidiana no beiral
        x0_, x1_ = sorted((s * (x_e - 0.5), s * (x_e + 0.14)))
        mb.box2((x0_, yf, z_e - 0.8), (x1_, yb, z_e + 0.36), OB, 0.0)
    mb.beam((0.0, yf, RIDGE + 0.5), (0.0, yb, RIDGE + 0.5), 1.4, 1.2, NAVY, 0.0)
    # crista de ferro (fita recortada A-B) com florao a cada 12
    Wr = ((0.0, 0.0), (0.0, 1.0), (1.0, 0.0))
    ya_, yb_ = yf + 4.0, yb - 2.0
    top = []
    nstep = int((yb_ - ya_) / 0.8)
    for i in range(nstep + 1):
        yy = ya_ + (yb_ - ya_) * i / nstep
        ph = (yy - ya_) % 3.2
        hz = 0.8 + 0.9 * (1.0 - abs(ph - 1.6) / 1.6) ** 2
        top.append((yy, RIDGE + 1.15 + hz))
    panel(mb, Wr, [(ya_, RIDGE + 1.1), (yb_, RIDGE + 1.1)] + list(reversed(top)), -0.08, 0.08, BI)
    yy = ya_ + 6.0
    while yy < yb_ - 2.0:
        EM._lathe(mb, (0.0, yy, RIDGE + 1.1), [(0.14, 0.0), (0.22, 0.45), (0.4, 1.3), (0.16, 1.9), (0.28, 2.3),
                                              (0.0, 3.4)], BI, 6, 0.0)
        yy += 12.0
    # FLECHA no meio da nave (agulha fina com lanterna de venezianas): a 3a altura da silhueta
    fy = 164.0
    zb_ = RIDGE - 3.0
    shaft(mb, 0.0, fy, 4.2, 8, zb_, RIDGE + 12.0, CM_, 22.5)
    ap = 4.2 * math.cos(math.pi / 8)
    for k in range(0, 8, 2):
        W = face_frame(0.0, fy, ap, 45.0 * k)
        lancet_win(mb, W, 0.0, RIDGE + 2.0, 8.0, 2.2, 0.0, glass="louver", frame_m=OB, dp=0.35, fw=0.25, sill=False)
    parapet_ring(mb, 0.0, fy, 4.2, 8, RIDGE + 12.0, 1.4, OB, 22.5, merlons=False)
    spire(mb, 0.0, fy, 4.0, 8, RIDGE + 13.44, 44.0, NAVY, 22.5, rings=(0.3, 0.6))
    finial(mb, 0.0, fy, RIDGE + 57.0, 1.8)
    # lucarnas escuras nas aguas da nave (venezianas): quebram a agua comprida
    k_ = (RIDGE - CLR_EAVE) / CLR
    for yy in (100.0, 128.0, 200.0, 228.0):
        for s in (-1, 1):
            xo = s * 30.0
            zr = CLR_EAVE + (CLR - 30.0) * k_
            mb.box2((min(xo, xo - s * 6.0), yy - 2.5, zr - 4.0), (max(xo, xo - s * 6.0), yy + 2.5, zr + 3.8), CM_, 0.0)
            mb.gable_roof(xo - s * 3.0, yy, 6.0, 5.0, zr + 3.8, 3.4, NAVY, thick=0.5, over=0.4, axis="X",
                          shingles=False, ridge_m=NAVY)
            Wl = ((xo, 0.0), (0.0, 1.0), (s * 1.0, 0.0))
            panel(mb, Wl, [(yy - 2.5, zr + 3.8), (yy + 2.5, zr + 3.8), (yy, zr + 7.2)], -0.3, 0.05, CM_)
            lancet_win(mb, Wl, yy, zr - 1.2, 4.2, 2.0, 0.0, glass="louver", frame_m=OB, dp=0.3, fw=0.3, sill=False)
    # meia-aguas das naves laterais (do parapeito ao clerestorio), em fiadas
    for s in (-1, 1):
        xo, xi = s * (OX1 + 0.4), s * (CLR + 0.05)
        zo, zi = EAVE + 0.4, LEAN_HI
        rows = int(math.hypot(xi - xo, zi - zo) / 2.3)
        slate_plane(mb, (xo, OY0 + 0.2, zo), (xo, OY1 - 0.2, zo), (xi, OY1 - 0.2, zi), (xi, OY0 + 0.2, zi), rows)
        mb.box2((min(xo, xi), OY0 + 0.3, zo - 1.2), (max(xo, xi), OY1 - 0.3, zo - 0.2), NAVY, 0.0)
    mb.finish()



# ------------------------------------------------------------------ 3. FACHADA: porche, porta, rosacea, tela, torrinhas
W_F = ((0.0, FAC_Y), (1.0, 0.0), (0.0, -1.0))          # face do corpo central (t = 0 em y 58,5)
W_P = ((0.0, YD), (1.0, 0.0), (0.0, -1.0))             # porche: t = 0 no plano da porta, 8 na frente
T_SK = TW - 1.2                                         # 3,8: fundo da pele do corpo central (W_S)
T_FC = TW + 2.5                                         # 7,5: face do corpo central (W_S)
ROSE_Z, ROSE_R = Z + 116.0, 17.0


def door_leaf(mb, s):
    """FOLHA da porta principal (14 x 34) aberta 90 graus e RECOLHIDA no rebaixo da parede da passagem: tabuas
    verticais com junta, 4 ferragens em T com cravos, dobradicas de pino na aresta do plano da porta, argola.
    A face a vista (lado da passagem) fica em |x| 14,1: o vao livre continua 28."""
    xf, xb = s * (DW / 2 + 0.1), s * (DW / 2 + 0.1 + LEAF_T)
    y0, y1 = YD + 0.15, YD + 13.95
    z0, z1 = Z + 0.2, Z + DH - 0.7
    mb.box2((min(xf + s * 0.14, xb), y0, z0), (max(xf + s * 0.14, xb), y1, z1), WD, 0.0)      # alma
    nb = 5
    for i in range(nb):
        ya = y0 + i * (y1 - y0) / nb + (0.04 if i else 0.0)
        yb = y0 + (i + 1) * (y1 - y0) / nb - (0.04 if i < nb - 1 else 0.0)
        mb.box2((min(xf, xf + s * 0.2), ya, z0 + 0.05), (max(xf, xf + s * 0.2), yb, z1 - 0.05), WD, 0.0)
    xi = xf - s * 0.15
    rs = (0, s * math.pi / 2, 0)
    for zz in (z0 + 3.2, z0 + 12.5, z1 - 12.5, z1 - 3.2):
        mb.box2((min(xi, xf), y0 + 0.3, zz - 0.3), (max(xi, xf), y1 - 1.2, zz + 0.3), BI, 0.0)
        mb.box2((min(xi, xf), y1 - 1.9, zz - 1.1), (max(xi, xf), y1 - 1.2, zz + 1.1), BI, 0.0)   # travessa do T
        for q in range(7):
            yy = y0 + 0.9 + q * (y1 - y0 - 3.4) / 6.0
            mb.cyl(0.1, 0.08, (xi - s * 0.04, yy, zz), rs, BI, n=6, r2=0.05, bevel=0.0)
        mb.cyl(0.22, 1.6, (s * (DW / 2 + 0.2), y0 - 0.12, zz), (0, 0, 0), BI, n=8, bevel=0.0)          # pino
    zr_ = Z + 6.5
    mb.cyl(0.42, 0.08, (xi - s * 0.04, y1 - 3.0, zr_), rs, BI, n=10, bevel=0.0)
    rp = [(xi - s * 0.16, y1 - 3.0 + 0.5 * math.sin(2 * math.pi * k / 12), zr_ - 0.5 + 0.5 * math.cos(2 * math.pi * k / 12))
          for k in range(13)]
    mb.tube(rp, 0.07, BI, 6)
    col_box2("SG_CasDoorLeaf", (min(xf, xb), YD, Z - 0.5), (max(xf, xb), HY0, Z + DH))


def paving(mb, x0, x1, y0, y1, z, cw, cd, mats, gap=0.08, zb=None):
    """lajes com junta rebaixada em 2 tons alternados (xadrez), topo em z"""
    nx, ny = max(1, int(round((x1 - x0) / cw))), max(1, int(round((y1 - y0) / cd)))
    zb = z - 0.45 if zb is None else zb
    for i in range(nx):
        for j in range(ny):
            a = x0 + (x1 - x0) * i / nx + (gap / 2 if i else 0.0)
            b = x0 + (x1 - x0) * (i + 1) / nx - (gap / 2 if i < nx - 1 else 0.0)
            c = y0 + (y1 - y0) * j / ny + (gap / 2 if j else 0.0)
            d = y0 + (y1 - y0) * (j + 1) / ny - (gap / 2 if j < ny - 1 else 0.0)
            mb.box2((a, c, zb), (b, d, z), mats[(i + j) % len(mats)], 0.0)


def porch(mb):
    """PORCHE da porta: 4 ordens de 2,5 x 2 escalonadas (jamba + timpano de cada camada), rolo continuo (colunelo ->
    capitel -> arquivolta) em cada ordem, timpano ogival ate 46 com o medalhao da ordem, verga reta a 34, capa-gota
    externa (moldura 48 x ~57), pilares com pinaculos, parapeito e WIMPERG com oculo trilobado e crochés.
    Atras do plano da porta: NARTEX de 14 (paredes com os rebaixos das folhas, teto em caixotoes)."""
    zd = Z + DH
    arise = TYMP - DH                                   # 12: flecha do timpano (arco abatido apontado)
    ztop = Z + 60.0
    # nartex (paredes, teto em caixotoes, massa acima)
    for s in (-1, 1):
        a_, b_ = sorted((s * (DW / 2 + POCK), s * PX))
        mb.box2((a_, YD, ZB), (b_, FAC_Y + 0.1, ztop), CM_, 0.0)
    mb.box2((-(DW / 2 + POCK), YD + 0.6, zd + 1.2), (DW / 2 + POCK, FAC_Y + 0.1, ztop), CM_, 0.0)
    mb.box2((-(DW / 2 + POCK), YD + 0.6, zd - 0.15), (DW / 2 + POCK, HY0 - 0.3, zd + 1.2), OB, 0.0)
    for yy in (YD + 4.2, YD + 8.4, YD + 12.6):
        mb.box2((-(DW / 2 + POCK), yy - 0.35, zd - 0.6), (DW / 2 + POCK, yy + 0.35, zd - 0.1), CAPL, 0.0)
    mb.box2((-0.35, YD + 0.6, zd - 0.6), (0.35, HY0 - 0.3, zd - 0.1), CAPL, 0.0)
    # timpano (pedra violeta, 0,2 atras do plano da porta) + verga + medalhao da ordem
    panel(mb, W_P, [(-DW / 2, zd + 0.6), (DW / 2, zd + 0.6)] + list(reversed(ogive(0.0, DW / 2, zd, arise, n=8)))[1:-1],
          -0.6, -0.2, VI)
    mb.box2((-DW / 2, YD - 0.7, zd), (DW / 2, YD + 0.45, zd + 2.0), CAPL, 0.06)
    for k in range(7):                                   # friso de pontas de diamante na verga
        xk = -DW / 2 + 2.0 + k * (DW - 4.0) / 6.0
        mb.cyl(0.45, 0.3, (xk, YD - 0.8, zd + 1.0), (math.pi / 2, 0, 0), OB, n=4, r2=0.0, bevel=0.0)
    EM.plaque(mb, mb, mb, mb, _P(W_P, 0.0, 0.1, zd + 7.4), -math.pi / 2, 3.2)
    # camadas das ordens: jambas e timpanos escalonados (cada camada 2 de fundo)
    rolls = []
    for k in range(1, NORD + 1):
        t0, t1 = (k - 1) * ORD_D, k * ORD_D
        d = (k - 1) * ORD_W
        xa = DW / 2 + d
        for s in (-1, 1):
            a_, b_ = sorted((s * xa, s * PX))
            panel(mb, W_P, rect(a_, b_, ZB, zd), t0, t1, CM_)
        arc = ogive(0.0, DW / 2, zd, arise, d=d, n=10)
        panel(mb, W_P, [(PX, zd), (PX, ztop), (-PX, ztop), (-PX, zd), (-xa, zd)] + arc[1:-1] + [(xa, zd)], t0, t1, CM_)
        # rolo (colunelo + arquivolta) na aresta saliente da camada
        tr = t1 - 0.36
        path = [_P(W_P, -(xa + 0.42), tr, Z + 1.7)] + [_P(W_P, u, tr, zz) for u, zz in
                                                      ogive(0.0, DW / 2, zd, arise, d=d + 0.42, n=14)] + \
               [_P(W_P, xa + 0.42, tr, Z + 1.7)]
        mb.tube(path, 0.5, VI if k % 2 else CAPL, 8)
        rolls.append((xa + 0.42, tr))
        # bases (plinto + toro) e capiteis (cesto + abaco) dos colunelos
        for s in (-1, 1):
            cp = _P(W_P, s * (xa + 0.42), tr, 0.0)
            mb.box((1.5, 1.5, 0.5), (cp[0], cp[1], Z + 0.25), (0, 0, 0), OB, 0.06)
            EM._lathe(mb, (cp[0], cp[1], Z + 0.5), [(0.72, 0.0), (0.72, 0.14), (0.6, 0.3), (0.66, 0.46), (0.5, 0.62),
                                                    (0.52, 1.2)], CAPL, 8, math.pi / 8)
            EM._lathe(mb, (cp[0], cp[1], zd - 1.66), [(0.5, 0.0), (0.58, 0.16), (0.52, 0.34), (0.66, 0.9), (0.86, 1.3),
                                                      (0.86, 1.6)], CAPL, 8, math.pi / 8)
    # friso de capiteis corrido nas frentes das camadas + soco de obsidiana nas jambas
    for k in range(1, NORD + 1):
        t1 = k * ORD_D
        xa = DW / 2 + (k - 1) * ORD_W
        xb = DW / 2 + k * ORD_W if k < NORD else PX
        for s in (-1, 1):
            a_, b_ = sorted((s * xa, s * xb))
            panel(mb, W_P, rect(a_, b_, zd - 0.9, zd + 0.3), t1 - 0.3, t1 + 0.28, OB)
            panel(mb, W_P, rect(a_, b_, ZB, Z + 1.4), t1 - 0.3, t1 + 0.18, OB)
    # capa-gota (label) em volta da ordem externa, com as mensulas
    tF = NORD * ORD_D
    dh = (NORD - 1) * ORD_W + 2.4
    h0 = ogive(0.0, DW / 2, zd, arise, d=dh, n=14)
    h1 = ogive(0.0, DW / 2, zd, arise, d=dh + 0.8, n=14)
    panel(mb, W_P, h0 + list(reversed(h1)), tF - 0.05, tF + 0.6, OB)
    for s in (-1, 1):
        u0_, u1_ = sorted((s * (DW / 2 + dh - 0.1), s * (DW / 2 + dh + 1.4)))
        panel(mb, W_P, rect(u0_, u1_, zd - 1.4, zd + 0.02), tF - 0.05, tF + 0.75, OB)
    # pilares da frente com pinaculo; parapeito do porche; lateral do porche com silhar
    for s in (-1, 1):
        px, py = s * (PX - 1.6), YP - 1.2
        mb.box((4.0, 3.6, SOC - ZB + 0.3), (px, py + 0.2, (ZB + SOC + 0.3) / 2), (0, 0, 0), OB, 0.0)
        mb.prism(sq_ch(px, py, 1.6, 0.4), SOC + 0.3, ztop + 3.0, CM_)
        for zz in (Z + 8.0, zd - 0.6, ztop - 0.6):
            frustum(mb, px, py, 2.25, 2.05, 8, zz, zz + 0.6, OB, 22.5)
        Wn = ((px, py - 1.6), (1.0, 0.0), (0.0, -1.0))
        lancet_win(mb, Wn, 0.0, Z + 12.0, 12.0, 1.6, 0.0, glass="slit", frame_m=CAPL, dp=0.4, fw=0.25)
        pinnacle(mb, px, py, ztop + 3.0, 1.4, hb=5.5, hn=13.0)
        Ws = ((s * PX, 0.0), (0.0, 1.0), (float(s), 0.0))
        coursed(mb, Ws, YP + 0.2, FAC_Y - 0.2, SOC + 0.3, Z + 7.7, (), 0, 0.3)
        coursed(mb, Ws, YP + 0.2, FAC_Y - 0.2, Z + 8.4, Z + 25.7, (), 1, 0.3)
        ledge(mb, Ws, YP - 0.1, FAC_Y, drip(Z + 8.0, 0.45), OB)
        ledge(mb, Ws, YP - 0.1, FAC_Y, plinth(ZB, SOC, 0.8, 0.4), OB)
        panel(mb, Ws, rect(YP, FAC_Y, ztop, ztop + 2.2), -0.7, 0.0, CM_)
        ledge(mb, Ws, YP - 0.4, FAC_Y, [(-0.9, ztop + 2.14), (0.2, ztop + 2.14), (0.2, ztop + 2.36), (-0.2, ztop + 2.6),
                                        (-0.9, ztop + 2.6)], OB)
    ledge(mb, W_P, -PX - 0.3, PX + 0.3, cornice(ztop, 0.9, 1.4), OB)
    panel(mb, W_P, rect(-PX + 3.2, PX - 3.2, ztop, ztop + 2.2), tF - 0.7, tF, CM_)
    for k in range(9):                                    # arcada cega no parapeito
        uc = -PX + 4.5 + k * (2 * PX - 9.0) / 8
        panel(mb, W_P, [(uc - 1.1, ztop + 0.3), (uc + 1.1, ztop + 0.3)] +
              list(reversed(ogive(uc, 1.1, ztop + 1.2, 0.8, n=3))), tF - 0.05, tF + 0.14, OB)
    ledge(mb, W_P, -PX + 3.0, PX - 3.0, [(-0.9, ztop + 2.14), (0.2, ztop + 2.14), (0.2, ztop + 2.36), (-0.2, ztop + 2.6),
                                         (-0.9, ztop + 2.6)], OB)
    # WIMPERG
    tw0, tw1 = tF + 0.02, tF + 1.1
    zf_, apex = Z + 48.0, Z + 86.0
    arc = [p for p in ogive(0.0, DW / 2, zd, arise, d=dh + 0.8, n=24) if p[1] > zf_]
    cc = (arise ** 2 - (DW / 2) ** 2) / DW
    xs = -cc + math.sqrt(max(0.0, (DW / 2 + cc + dh + 0.8) ** 2 - (zf_ - zd) ** 2))
    wx = 27.0
    poly = [(-wx, zf_), (-xs, zf_)] + arc + [(xs, zf_), (wx, zf_), (0.0, apex)]
    panel(mb, W_P, poly, tw0, tw1, CM_)
    oc = (0.0, Z + 70.0)
    U, V, N = WUVN(W_P)
    C = _P(W_P, oc[0], 0.0, oc[1])
    disc(mb, C, U, V, N, 4.6, tw1 - 0.05, tw1 + 0.14, OB, 20)
    ring(mb, C, U, V, N, 4.4, 5.3, tw1 - 0.05, tw1 + 0.55, CAPL, 20)
    for k in range(3):
        a = math.pi / 2 + k * 2 * math.pi / 3
        Ck = _P(W_P, oc[0] + 2.0 * math.cos(a), 0.0, oc[1] + 2.0 * math.sin(a))
        ring(mb, Ck, U, V, N, 1.55, 1.95, tw1 + 0.14, tw1 + 0.45, CAPL, 12)
    for s in (-1, 1):
        a = (s * (wx + 0.8), zf_ - 0.6)
        b = (0.0, apex + 0.6)
        L2 = math.hypot(b[0] - a[0], b[1] - a[1])
        tilt = math.atan2(b[1] - a[1], b[0] - a[0])
        mb.box((L2, 1.5, 1.0), _P(W_P, (a[0] + b[0]) / 2, tw1 - 0.4, (a[1] + b[1]) / 2 + 0.2), (0, -tilt, 0), OB, 0.0)
        nk = int(L2 / 3.2)
        for j in range(1, nk):
            f = j / nk
            u = a[0] + (b[0] - a[0]) * f
            zz = a[1] + (b[1] - a[1]) * f
            p = _P(W_P, u, tw1 - 0.4, zz + 0.95)
            mb.cyl(0.42, 1.1, p, (0, s * 0.45, 0), CAPL, n=4, r2=0.05, bevel=0.0)
    gp = _P(W_P, 0.0, tw1 - 0.4, 0.0)
    finial(mb, gp[0], gp[1], apex + 0.7, 2.6, CAPL)
    # pisos: 2 degraus largos, estrado do porche, soleira e o nartex (lajes com junta, 2 tons)
    paving(mb, -PX - 1.0, PX + 1.0, YP - 6.0, YP - 3.0, Z + 0.3, 4.0, 3.0, (CAPL, "Stone_SG_Floor"))
    paving(mb, -PX - 1.0, PX + 1.0, YP - 3.0, YP, Z + 0.6, 4.0, 3.0, ("Stone_SG_Floor", CAPL))
    paving(mb, -21.4, 21.4, YP, YD - 0.6, Z + 0.6, 3.6, 3.6, ("Stone_SG_MarbleBlack", "Stone_SG_Floor"))
    mb.box2((-DW / 2, YD - 0.6, Z - 0.3), (DW / 2, YD + 0.6, Z + 0.62), OB, 0.05)
    mb.box2((-DW / 2 + 0.3, YD - 0.72, Z + 0.3), (DW / 2 - 0.3, YD - 0.58, Z + 0.62), SV, 0.0)
    paving(mb, -(DW / 2 + POCK), DW / 2 + POCK, YD + 0.6, HY0 - 0.05, Z + 0.14, 3.7, 3.4,
           ("Stone_SG_MarbleBlack", "Stone_SG_Floor"))
    for s in (-1, 1):
        door_leaf(mb, s)
    # colisao do porche (fora do vao), degraus, estrado e nartex
    for s in (-1, 1):
        a_, b_ = sorted((s * DW / 2, s * PX))
        col_box2("SG_CasPorch", (a_, YP, Z - 0.5), (b_, YD, ztop))
        a_, b_ = sorted((s * (DW / 2 + POCK), s * PX))
        col_box2("SG_CasPorch", (a_, YD, Z - 0.5), (b_, FAC_Y, ztop))
    col_box2("SG_CasPorch", (-(DW / 2 + POCK), YD - 0.7, zd), (DW / 2 + POCK, FAC_Y, ztop))
    col_box2("SG_CasPorchStep", (-PX - 1.0, YP - 6.0, Z - 0.5), (PX + 1.0, YP - 3.0, Z + 0.3))
    col_box2("SG_CasPorchStep", (-PX - 1.0, YP - 3.0, Z - 0.5), (PX + 1.0, YD + 0.6, Z + 0.6))
    col_box2("SG_CasPorchStep", (-(DW / 2 + POCK), YD + 0.6, Z - 0.5), (DW / 2 + POCK, HY0, Z + 0.14))


def rose(mb):
    """ROSACEA R 17 do corpo central: recuo de 1,5 na pele, fundo de obsidiana, vitral violeta, rendilhado de
    cantaria (anel, 12 raios, 12 oculos) e o CRESCENTE DA ORDEM no medalhao central (o unico brilho do emblema)"""
    zc, R = ROSE_Z, ROSE_R
    tb = T_FC - 1.5
    U, V, N = WUVN(W_S)
    C = (0.0, HY0, zc)
    disc(mb, C, U, V, N, R, tb - 0.05, tb + 0.14, OB, 40)
    disc(mb, C, U, V, N, R, tb + 0.4, tb + 0.48, ROSE_G, 40)
    ring(mb, C, U, V, N, R - 1.1, R + 0.02, tb + 0.14, T_FC - 0.15, CAPL, 40)
    ring(mb, C, U, V, N, 4.6, 5.5, tb + 0.14, T_FC - 0.2, CAPL, 20)
    for k in range(12):
        a = 2 * math.pi * k / 12
        ca, sa = math.cos(a), math.sin(a)
        r0, r1, w = 5.4, R - 1.0, 0.32
        poly = [(ca * r0 - sa * w, zc + sa * r0 + ca * w), (ca * r1 - sa * w, zc + sa * r1 + ca * w),
                (ca * r1 + sa * w, zc + sa * r1 - ca * w), (ca * r0 + sa * w, zc + sa * r0 - ca * w)]
        panel(mb, W_S, poly, tb + 0.14, T_FC - 0.35, CAPL)
        a2 = a + math.pi / 12
        Ck = (11.2 * math.cos(a2), HY0, zc + 11.2 * math.sin(a2))
        ring(mb, Ck, U, V, N, 1.9, 2.3, tb + 0.14, T_FC - 0.4, CAPL, 10)
    disc(mb, C, U, V, N, 4.7, tb + 0.14, T_FC - 0.3, OB, 24)
    EM.emblem(mb, mb, mb, _P(W_S, 0.0, T_FC - 0.3, zc), -math.pi / 2, 3.7, depth=0.9, monumental=True, glow=VG_EMB)
    # molduras na face: anel de pedra violeta e anel de obsidiana
    ring(mb, C, U, V, N, R, R + 1.2, T_FC - 0.05, T_FC + 0.65, VI, 40)
    ring(mb, C, U, V, N, R + 1.2, R + 2.4, T_FC - 0.05, T_FC + 0.4, OB, 40)


def central_body(mb):
    """corpo central da fachada (88 de largura, face y 58,5): pele de 3,7 em faixas - faixa do porche, galeria de 9
    nichos, rosacea, galeria alta de 11 arcos e cornija com balaustrada; empena-tela ate 252 com oculo e crochés"""
    zd = Z + DH
    # faixa A (ate Z+62): vao da passagem; ladrilhado so ao lado do porche (x 30..40)
    wall_run(mb, W_S, -CLR, CLR, ZB, Z + 62.0, T_SK, T_FC, [(0.0, DW / 2 + POCK, ZB, zd, 0.0)], CM_)
    for s in (-1, 1):
        a_, b_ = sorted((s * (PX + 0.2), s * (CLR - 4.3)))
        wall_skin(mb, W_F, a_, b_, t=0.0, tiers=((Z + 8.0, 0), (Z + 26.0, 1), (Z + 60.0, 2)), phase=0.2,
                  excl=[(s * 35.2 - 2.9, s * 35.2 + 2.9, Z + 29.0, Z + 51.0)])
        lancet_win(mb, W_F, s * 35.2, Z + 30.0, 20.0, 3.2, 0.0, glass="dark", frame_m=CAPL, dp=0.55, fw=0.45)
    ledge(mb, W_F, -CLR + 4.0, CLR - 4.0, drip(Z + 62.0, 0.55), OB)
    # faixa B: galeria de nichos (fundo escuro, arcos com colunelos)
    zb_, zt_ = Z + 62.4, Z + 94.0
    panel(mb, W_S, rect(-CLR, CLR, zb_, zt_), T_SK, T_FC - 1.4, CM_)
    niches = [(-36.0 + 9.0 * k, 3.2, Z + 66.0, Z + 84.0, 5.5) for k in range(9)]
    wall_run(mb, W_S, -CLR, CLR, zb_, zt_, T_FC - 1.4, T_FC, niches, CM_)
    for uc, a, zs, zr, rise in niches:
        rwin(mb, W_S, uc, a, zs, zr, rise, T_FC, 1.4, kind="void", frame_m=CAPL, fw=0.45, dp=0.45, sill=True)
        for s in (-1, 1):
            cp = _P(W_S, uc + s * (a + 0.3), T_FC + 0.35, 0.0)
            mb.cyl(0.3, zr - zs - 0.6, (cp[0], cp[1], (zs + zr) / 2), (0, 0, 0), CAPL, 6, bevel=0.0)
    ledge(mb, W_F, -CLR + 4.0, CLR - 4.0, cornice(zt_, 0.9, 1.3), OB)
    # faixa C: rosacea (pele em 2 pecas em volta do circulo)
    zb_, zt_ = Z + 94.4, Z + 140.0
    panel(mb, W_S, rect(-CLR, CLR, zb_, zt_), T_SK, T_FC - 1.5, CM_)
    na = 40
    top = [(ROSE_R * math.cos(math.pi * i / na), ROSE_Z + ROSE_R * math.sin(math.pi * i / na)) for i in range(na + 1)]
    bot = [(ROSE_R * math.cos(-math.pi * i / na), ROSE_Z + ROSE_R * math.sin(-math.pi * i / na)) for i in range(na + 1)]
    panel(mb, W_S, [(CLR, ROSE_Z), (CLR, zt_), (-CLR, zt_), (-CLR, ROSE_Z)] + list(reversed(top)), T_FC - 1.5, T_FC,
          CM_)
    panel(mb, W_S, [(-CLR, ROSE_Z), (-CLR, zb_), (CLR, zb_), (CLR, ROSE_Z)] + bot, T_FC - 1.5, T_FC, CM_)
    rose(mb)
    # faixa D: galeria alta (11 arcos escuros) + cornija + balaustrada
    zb_, zt_ = Z + 140.4, FAC_TOP
    panel(mb, W_S, rect(-CLR, CLR, zb_, zt_), T_SK, T_FC - 1.2, CM_)
    arcs = [(-35.0 + 7.0 * k, 2.2, Z + 141.6, Z + 146.0, 3.2) for k in range(11)]
    wall_run(mb, W_S, -CLR, CLR, zb_, zt_, T_FC - 1.2, T_FC, arcs, CM_)
    for uc, a, zs, zr, rise in arcs:
        rwin(mb, W_S, uc, a, zs, zr, rise, T_FC, 1.2, kind="void", frame_m=CAPL, fw=0.35, dp=0.4, sill=False)
    ledge(mb, W_F, -CLR + 4.0, CLR - 4.0, drip(Z + 140.3, 0.55), OB)
    ledge(mb, W_F, -CLR + 4.0, CLR - 4.0, cornice(FAC_TOP, 1.2, 1.6), OB)
    # balaustrada: pilaretes quadrados + corrimao
    for k in range(29):
        u = -38.0 + k * 76.0 / 28
        mb.box((0.5, 0.5, 2.3), _P(W_F, u, 0.6, FAC_TOP + 1.15), (0, 0, 0), CM_, 0.0)
    mb.box2((-38.4, FAC_Y - 1.0, FAC_TOP + 2.3), (38.4, FAC_Y - 0.2, FAC_TOP + 2.8), OB, 0.0)
    # empena-tela (acima da cumeeira) com oculo e crochés
    gz0 = FAC_TOP + 0.4
    panel(mb, W_F, [(-CLR + 4.0, gz0), (CLR - 4.0, gz0), (0.0, GABLE_TOP)], -3.0, -0.4, CM_)
    U, V, N = WUVN(W_F)
    C = _P(W_F, 0.0, 0.0, gz0 + 17.0)
    disc(mb, C, U, V, N, 6.2, -0.45, -0.26, OB, 24)
    ring(mb, C, U, V, N, 6.0, 7.2, -0.45, 0.2, CAPL, 24)
    for k in range(4):
        a = math.pi / 4 + k * math.pi / 2
        Ck = _P(W_F, 2.6 * math.cos(a), 0.0, gz0 + 17.0 + 2.6 * math.sin(a))
        ring(mb, Ck, U, V, N, 2.0, 2.4, -0.26, 0.0, CAPL, 12)
    for s in (-1, 1):
        a = (s * (CLR - 3.0), gz0 - 0.4)
        b = (0.0, GABLE_TOP + 0.8)
        L2 = math.hypot(b[0] - a[0], b[1] - a[1])
        tilt = math.atan2(b[1] - a[1], b[0] - a[0])
        mb.box((L2, 3.4, 1.1), _P(W_F, (a[0] + b[0]) / 2, -1.6, (a[1] + b[1]) / 2 + 0.25), (0, -tilt, 0), OB, 0.0)
        nk = int(L2 / 3.6)
        for j in range(1, nk):
            f = j / nk
            p = _P(W_F, a[0] + (b[0] - a[0]) * f, -1.6, a[1] + (b[1] - a[1]) * f + 1.0)
            mb.cyl(0.5, 1.3, p, (0, s * 0.45, 0), CAPL, n=4, r2=0.05, bevel=0.0)
    gp = _P(W_F, 0.0, -1.6, 0.0)
    finial(mb, gp[0], gp[1], GABLE_TOP + 1.2, 3.2)


def fac_turret(mb, s):
    """torrinha-contraforte que marca o corpo central (8 x 8 de quinas chanfradas) ate acima da tela, lanterna
    octogonal de venezianas e agulha"""
    x, y = s * CLR, FAC_Y + 0.5
    hw = 4.0
    ztop = FAC_TOP + 10.0
    mb.box((hw * 2 + 1.8, hw * 2 + 1.8, SOC - ZB), (x, y, (ZB + SOC) / 2), (0, 0, 0), OB, 0.0)
    mb.prism(sq_ch(x, y, hw, 1.0), SOC, ztop, CM_)
    Wt = ((x, y - hw), (1.0, 0.0), (0.0, -1.0))
    coursed(mb, Wt, -hw + 1.05, hw - 1.05, SOC + 0.34, Z + 7.7, (), 0, 0.2)
    coursed(mb, Wt, -hw + 1.05, hw - 1.05, Z + 8.4, Z + 25.7, (), 1, 0.2)
    for zz in (Z + 8.0, Z + 26.0, Z + 62.0, Z + 94.0, Z + 140.3, FAC_TOP):
        mb.prism(sq_ch(x, y, hw + 0.45, 1.2), zz - 0.35, zz + 0.35, OB)
    for zz, h in ((Z + 34.0, 12.0), (Z + 104.0, 20.0), (Z + 150.0, 12.0)):
        lancet_win(mb, Wt, 0.0, zz, h, 1.8, 0.0, glass="slit", frame_m=CAPL, dp=0.45, fw=0.3)
    # lanterna octogonal + agulha
    frustum(mb, x, y, hw + 0.6, hw + 0.2, 8, ztop - 0.3, ztop + 0.5, OB, 22.5)
    rl = 3.6
    shaft(mb, x, y, rl, 8, ztop + 0.5, ztop + 9.0, CM_, 22.5)
    ap = rl * math.cos(math.pi / 8)
    for k in range(0, 8, 2):
        W = face_frame(x, y, ap, 45.0 * k)
        lancet_win(mb, W, 0.0, ztop + 1.8, 6.0, 1.6, 0.0, glass="louver", frame_m=OB, dp=0.3, fw=0.22, sill=False)
    parapet_ring(mb, x, y, rl, 8, ztop + 9.0, 1.2, OB, 22.5, merlons=False)
    spire(mb, x, y, rl - 0.2, 8, ztop + 10.24, 30.0, NAVY, 22.5, rings=(0.34,))
    finial(mb, x, y, ztop + 40.0, 1.6)
    col_box("SG_CasFacTurret", (2 * hw, 2 * hw, 24.0), (x, y, Z + 11.5))


def facade(banners):
    rng = random.Random(5401)
    mb = MB("SG_Cas_Fachada", "04_CASTLE", rng, detail="near")
    central_body(mb)
    for s in (-1, 1):
        fac_turret(mb, s)
    _fin(mb)
    mp = MB("SG_Cas_Porta", "04_CASTLE", random.Random(5402), detail="hero")
    porch(mp)
    _fin(mp)
    light("L_SGCas_Door", "POINT", (0.0, YP - 7.0, Z + 14.0), 900.0, WARM, 0.8)
    light("L_SGCas_Rose", "POINT", (0.0, FAC_Y - 16.0, ROSE_Z - 6.0), 900.0, VIOLET, 1.2)



# ------------------------------------------------------------------ 4. TORRES DA FACHADA (R 20)
def front_towers():
    """2 torres de 4 andares: base com ladrilhado e seteiras escuras; 2o andar com 4 janelas altas em VAO (2 ACESAS:
    a da praca e a de fora; 2 escuras de luar); campanario com vaos geminados de venezianas; coroamento com mata-caes,
    pinaculos e agulha com lucarnas ate 300"""
    mb = MB("SG_Cas_Torres", "04_CASTLE", random.Random(5501), detail="near")
    n, rot = 8, 22.5
    for x, y, r, top_ in L.FRONT_TOWERS:
        s = 1 if x > 0 else -1
        ap = r * math.cos(math.pi / n)
        out_phi = 0.0 if s > 0 else 180.0
        nave_phi = 180.0 if s > 0 else 0.0

        def hid(cx_, cy_):
            return OX0 - 0.3 < cx_ < OX1 + 0.9 and OY0 - 0.5 < cy_ < OY1

        socle(mb, x, y, r, n, ZB, SOC, rot, e=1.2)
        z1 = Z + 62.0
        shaft(mb, x, y, r, n, SOC, z1, CM_, rot)
        slits = [(270.0, Z + 14.0, 5.0, 1.3), (out_phi, Z + 14.0, 5.0, 1.3), ((270.0 + s * 45.0) % 360, Z + 36.0, 6.0, 1.3),
                 ((90.0 - s * 45.0) % 360, Z + 36.0, 6.0, 1.3), (90.0, Z + 20.0, 5.0, 1.3)]
        ex = {}
        for phi, zz, h, w in slits:
            ex.setdefault(int(round(phi)) % 360, []).append((-w / 2 - 0.9, w / 2 + 0.9, zz - 1.0, zz + h + 0.6))
        tower_skin(mb, x, y, r, n, rot, ZB, ((Z + 8.0, 0), (Z + 22.0, 1), (Z + 44.0, 2)), soc=False, hide=hid,
                   excl=ex)
        for phi, zz, h, w in slits:
            slit(mb, face_frame(x, y, ap, phi), zz, h, w)
        band(mb, x, y, r, n, z1 - 0.2, rot, h=1.2, e=0.55)
        # 2o andar: janelas altas em vao (acesas: praca e fora; escuras nas diagonais)
        op = (0.0, 2.4, z1 + 8.0, z1 + 24.0, 4.4)
        lit_k = [face_index(n, rot, 270.0), face_index(n, rot, out_phi)]
        dark_k = [face_index(n, rot, (270.0 + s * 45.0) % 360), face_index(n, rot, (90.0 - s * 45.0) % 360)]
        z2 = Z + 124.0
        faces = shaft_band(mb, x, y, r, n, rot, z1 + 0.5, z2, CM_, {k: [op] for k in lit_k + dark_k}, d=1.6)
        for k in lit_k + dark_k:
            W = faces[k][0]
            rwin(mb, W, *op, 0.0, 1.6, kind="lit" if k in lit_k else "dark", frame_m=CAPL, fw=0.7, dp=0.55,
                 mull=True, tracery=True, hood=True)
            panel(mb, W, rect(-2.5, 2.5, z1 + 15.2, z1 + 15.7), -1.46, -0.2, CAPL)           # travessa (pontas embutidas)
            ledge(mb, W, -r * 0.35, r * 0.35, drip(z1 + 7.2, 0.4), OB)
        band(mb, x, y, r, n, z2 - 0.2, rot, h=1.2, e=0.55)
        # campanario: vaos geminados com venezianas nas 4 faces retas, lancetas cegas nas diagonais
        z3 = FT_TOP - 3.2
        twin = [(-2.9, 1.8, z2 + 8.0, z2 + 32.0, 3.6), (2.9, 1.8, z2 + 8.0, z2 + 32.0, 3.6)]
        card = [face_index(n, rot, p) for p in (0.0, 90.0, 180.0, 270.0)]
        faces = shaft_band(mb, x, y, r, n, rot, z2 + 0.5, z3, CM_, {k: twin for k in card}, d=1.5)
        for k in range(n):
            W = faces[k][0]
            if k in card:
                for uc, a, zs, zr, rise in twin:
                    rwin(mb, W, uc, a, zs, zr, rise, 0.0, 1.5, kind="void", frame_m=CAPL, fw=0.4, dp=0.45,
                         lead=False)
                    louvers(mb, W, uc - a, uc + a, zs, zr, -1.1)
                arch_band(mb, W, 0.0, 5.2, z2 + 7.4, z2 + 32.0, 6.2, 0.7, -0.05, 0.5, OB, n=8)
        tower_crown(mb, x, y, r, n, rot, z3 + 3.2, FT_SPIRE_TIP - FT_TOP - 3.5, pin_s=1.0, sp_r=r - 2.2,
                    dorm=(270.0, out_phi), fin=3.0)
        ngon_col("SG_CasTower", x, y, n, r, Z - 0.5, FT_TOP, rot)
    mb.finish()


# ------------------------------------------------------------------ 5. TORRE-COROA: base (presbiterio, BOLSO, retabulo) + fuste + agulha
def crown():
    mb = MB("SG_Cas_Coroa", "04_CASTLE", random.Random(5601), detail="near")
    bx0, by0, bx1, by1 = L.CROWN_BASE                  # -38, 262, 38, 344
    wt = 5.0
    y0 = OY1                                           # 267: face norte da nave
    px0, py0, px1, py1, pz0, pz1 = L.THRONE_POCKET     # bolso do trono: x 20..35,5, y 288..300, z 54,6..76,6
    cx0, cy0, cx1, cy1 = L.CHANCEL
    ry0, ry1 = L.RETABLE_Y
    aw, ah = L.SECRET_ARCH
    zc = L.CHANCEL_Z
    MB_ = "Stone_SG_MarbleBlack"
    # --- estrutura (o blockout tinha a mesma divisao: casca aqui, acabamento do presbiterio no sg_hall)
    mb.box2((bx0, y0, ZB), (bx0 + wt, by1, BTOP), CM_, 0.0)                     # oeste
    mb.box2((bx1 - wt, y0, ZB), (bx1, py0, BTOP), CM_, 0.0)                     # leste (sul do bolso)
    mb.box2((bx1 - wt, py1, ZB), (bx1, by1, BTOP), CM_, 0.0)                    # leste (norte do bolso)
    mb.box2((px1, py0, ZB), (bx1, py1, BTOP), CM_, 0.0)                         # fundo do bolso (2,5 + baluarte)
    mb.box2((bx1 - wt, py0, ZB), (px1, py1, pz0 - 0.3), IM, 0.0)
    mb.box2((bx1 - wt, py0, pz1), (px1, py1, BTOP - 1.5), IM, 0.0)
    mb.box2((bx0 + wt, by1 - wt, ZB), (bx1 - wt, by1, BTOP), CM_, 0.0)          # norte
    mb.box2((bx0 + wt, y0, ZB), (cx0, ry1, BTOP - 1.5), IM, 0.0)                # parede oeste do presbiterio
    mb.box2((cx1, y0, ZB), (bx1 - wt, py0, BTOP - 1.5), IM, 0.0)                # parede leste com o BOLSO
    mb.box2((cx1, py1, ZB), (bx1 - wt, ry1, BTOP - 1.5), IM, 0.0)
    mb.box2((cx1, py0, ZB), (bx1 - wt, py1, pz0 - 0.3), IM, 0.0)
    mb.box2((cx1, py0, pz1), (bx1 - wt, py1, BTOP - 1.5), IM, 0.0)
    mb.box2((cx1 + 0.02, py0 + 0.02, pz0 - 0.3), (px1 - 0.02, py1 - 0.02, pz0 - 0.02), MB_, 0.0)   # piso do bolso (<= 54,6)
    # muro do retabulo (y 300..308) com o ARCO SECRETO 12 x 18 no eixo
    mb.box2((cx0, ry0, ZB), (-aw / 2, ry1, BTOP - 1.5), IM, 0.0)
    mb.box2((aw / 2, ry0, ZB), (cx1, ry1, BTOP - 1.5), IM, 0.0)
    mb.box2((-aw / 2, ry0, zc + ah), (aw / 2, ry1, BTOP - 1.5), IM, 0.0)
    mb.box2((-aw / 2, ry0, ZB), (aw / 2, ry1, zc - 0.3), IM, 0.0)
    # tetos: presbiterio (Z+60) e camara do poco (Z+36); laje do topo da base
    mb.box2((cx0, y0, Z + L.TRI_ARCH_H), (cx1, ry0, Z + L.TRI_ARCH_H + 1.5), IM, 0.0)
    mb.box2((bx0 + wt, ry1, Z + 36.0), (bx1 - wt, by1 - wt, Z + 37.5), IM, 0.0)
    mb.box2((bx0 + 0.05, y0 + 0.05, BTOP - 1.5), (bx1 - 0.05, by1 - 0.05, BTOP + 0.06), CM_, 0.0)
    # --- por fora: ladrilhado, cordoes, janelas escuras, contrafortes de quina, mata-caes no topo
    Wbw = ((bx0, 0.0), (0.0, 1.0), (-1.0, 0.0))
    Wbe = ((bx1, 0.0), (0.0, 1.0), (1.0, 0.0))
    Wbn = ((0.0, by1), (1.0, 0.0), (0.0, 1.0))
    bay = (283.0, 305.0, 2.4)                                                    # baluarte do bolso (face leste)
    for W, u0, u1, wins in ((Wbw, y0 + 0.3, by1 - 3.6, (318.0,)), (Wbe, y0 + 0.3, by1 - 3.6, (322.0,)),
                            (Wbn, bx0 + 3.6, bx1 - 3.6, (-17.0, 17.0))):
        ex = [(u - 5.2, u + 5.2, Z + 28.0, Z + 70.0) for u in wins]
        if W is Wbe:
            ex.append((bay[0] - 0.6, bay[1] + 0.6, ZB, Z + 44.0))
        wall_skin(mb, W, u0, u1, t=0.0, excl=ex, phase=0.6)
        for u in wins:
            lancet_win(mb, W, u, Z + 30.0, 38.0, 7.0, 0.0, glass="dark", frame_m=CAPL, dp=0.6, fw=0.9)
        for zz in (Z + 72.0, Z + 96.0):
            ledge(mb, W, u0 - 0.5, u1 + 0.5, drip(zz, 0.5), OB)
        machicolations(mb, W, u0 - 3.0, u1 + 3.0, BTOP + 1.2)
    # baluarte do bolso: le o bolso do trono por fora (parede engrossada com arco cego e talude de capa)
    Wbay = ((bx1 + bay[2], 0.0), (0.0, 1.0), (1.0, 0.0))
    panel(mb, Wbe, rect(bay[0], bay[1], ZB, Z + 42.0), -0.2, bay[2], CM_)
    ledge(mb, Wbe, bay[0] - 0.4, bay[1] + 0.4, [(-0.2, Z + 41.9), (bay[2] + 0.5, Z + 41.9), (bay[2] + 0.5, Z + 42.5),
                                                (-0.2, Z + 45.2)], OB)
    ledge(mb, Wbay, bay[0] - 0.2, bay[1] + 0.2, plinth(ZB, SOC, 0.8, 0.4), OB)
    coursed(mb, Wbay, bay[0] + 0.05, bay[1] - 0.05, SOC + 0.34, Z + 7.7, [(289.5, 298.5, Z + 9.0, Z + 38.0)], 0, 0.2)
    coursed(mb, Wbay, bay[0] + 0.05, bay[1] - 0.05, Z + 8.4, Z + 40.5, [(288.6, 299.4, Z + 9.0, Z + 38.0)], 1, 0.6)
    ledge(mb, Wbay, bay[0] - 0.2, bay[1] + 0.2, drip(Z + 8.0, 0.45), OB)
    arch_band(mb, Wbay, 294.0, 4.4, Z + 9.6, Z + 30.0, 6.0, 0.9, -0.05, 0.55, CAPL, n=8)
    panel(mb, Wbay, opening(294.0, 4.4, Z + 9.6, Z + 30.0, 6.0), -0.05, 0.14, OB)
    EM.plaque(mb, mb, mb, mb, _P(Wbay, 294.0, 0.6, Z + 23.0), 0.0, 1.9)
    for s in (-1, 1):
        a = math.radians(45.0 if s > 0 else 135.0)
        bx, by = s * (bx1 + 1.6), by1 + 1.6
        mb.box((5.0, 4.6, BTOP - 2.0 - ZB), (bx, by, (ZB + BTOP - 2.0) / 2), (0, 0, a), CM_, 0.0)
        mb.box((6.4, 6.0, SOC - ZB + 0.4), (bx, by, (ZB + SOC + 0.4) / 2), (0, 0, a), OB, 0.0)
        for zz in (Z + 8.0, Z + 40.0, Z + 72.0):
            mb.box((5.5, 5.1, 0.7), (bx, by, zz), (0, 0, a), OB, 0.0)
        pinnacle(mb, bx, by, BTOP - 2.0, 1.4, hb=6.0, hn=14.0, rot=a)
        col_box("SG_CasCrown", (5.0, 4.6, 24.0), (bx, by, Z + 11.5), (0, 0, a))
    # --- fuste octogonal R 30 (152 -> 311): 2 andares de lancetas escuras + campanario com 4 lancetas VIOLETA
    x, y, r, n, rot = CR_X, CR_Y, CR_R, 8, 22.5
    ap = r * math.cos(math.pi / n)
    socle(mb, x, y, r, n, BTOP - 0.6, BTOP + 3.0, rot, e=0.9)
    s1 = Z + 160.0
    shaft(mb, x, y, r, n, BTOP + 3.0, s1, CM_, rot)
    for k in range(n):
        phi = face_phi(n, rot, k)
        if abs(phi - 270.0) < 1.0:
            continue
        lancet_win(mb, face_frame(x, y, ap, phi), 0.0, Z + 112.0, 36.0, 6.4, 0.0, glass="dark", frame_m=CAPL, dp=0.6,
                   fw=0.9)
    for zz in (Z + 108.0, Z + 132.0):
        band(mb, x, y, r, n, zz, rot, h=1.0, e=0.5)
    band(mb, x, y, r, n, s1 - 0.3, rot, h=1.6, e=0.7)
    s2 = Z + 214.0
    shaft(mb, x, y, r, n, s1 + 0.5, s2, CM_, rot)
    for k in range(n):
        phi = face_phi(n, rot, k)
        W = face_frame(x, y, ap, phi)
        lancet_win(mb, W, 0.0, s1 + 10.0, 34.0, 5.4, 0.0, glass="dark", frame_m=CAPL, dp=0.55, fw=0.8)
    band(mb, x, y, r, n, s2 - 0.3, rot, h=1.6, e=0.7)
    op = (0.0, 3.4, s2 + 8.0, s2 + 32.0, 7.0)
    card = [face_index(n, rot, p) for p in (0.0, 90.0, 180.0, 270.0)]
    faces = shaft_band(mb, x, y, r, n, rot, s2 + 0.5, CR_TOP, CM_, {k: [op] for k in range(n)}, d=1.8)
    for k in range(n):
        W = faces[k][0]
        if k in card:
            rwin(mb, W, *op, 0.0, 1.8, kind="violet", frame_m=VI, fw=0.8, dp=0.6, mull=True, tracery=True, hood=True)
        else:
            rwin(mb, W, *op, 0.0, 1.8, kind="void", frame_m=CAPL, fw=0.7, dp=0.5, lead=False)
            louvers(mb, W, -3.4, 3.4, op[2], op[3], -1.4)
    # coroamento: mata-caes, 4 torrinhas nas diagonais, pinaculos nos vertices, agulha com lucarnas ate 376
    parapet_ring(mb, x, y, r, n, CR_TOP, 2.6, OB, rot)
    for k in range(n):
        phi = face_phi(n, rot, k)
        if k in card:
            continue
        a = math.radians(phi)
        tx, ty = x + (ap - 3.2) * math.cos(a), y + (ap - 3.2) * math.sin(a)
        shaft(mb, tx, ty, 3.6, 8, CR_TOP + 2.64, CR_TOP + 16.0, CM_, 22.5)
        for kk in range(2):
            Wt = face_frame(tx, ty, 3.6 * math.cos(math.pi / 8), phi + 180.0 * kk)
            lancet_win(mb, Wt, 0.0, CR_TOP + 6.0, 6.0, 1.4, 0.0, glass="slit", frame_m=OB, dp=0.3, fw=0.2, sill=False)
        parapet_ring(mb, tx, ty, 3.6, 8, CR_TOP + 16.0, 1.2, OB, 22.5, merlons=False)
        spire(mb, tx, ty, 3.4, 8, CR_TOP + 17.24, 22.0, NAVY, 22.5, rings=(0.36,))
        finial(mb, tx, ty, CR_TOP + 39.0, 1.8)
    for k in range(n):
        a = math.radians(rot + 360.0 * k / n)
        pinnacle(mb, x + (r + 0.6) * math.cos(a), y + (r + 0.6) * math.sin(a), CR_TOP + 2.64, 1.1, hb=3.2,
                 hn=11.0 if k % 2 else 8.0, body_m=OB, crock=False, rot=a)
    rs = 21.0
    h_sp = L.CROWN_SPIRE_TOP - 3.0 - (CR_TOP + 2.64)
    spire(mb, x, y, rs, n, CR_TOP + 2.64, h_sp, NAVY, rot, flare=0.1, rings=(0.26, 0.5, 0.74))
    dormers(mb, x, y, rs, n, CR_TOP + 2.64, h_sp, (0.0, 90.0, 180.0, 270.0), s=1.7)
    mb.rod((x, y, CR_TOP + 2.64 + h_sp - 0.4), (x, y, L.CROWN_SPIRE_TOP - 2.6), 0.35, SV, 6)
    finial(mb, x, y, L.CROWN_SPIRE_TOP - 2.9, 2.6)
    _fin(mb)
    # colisao (mesma divisao do blockout): casca, paredes do presbiterio em volta do BOLSO, retabulo, tetos
    col_box2("SG_CasCrown", (bx0, by1 - wt, Z - 0.5), (bx1, by1, BTOP))
    col_box2("SG_CasCrown", (bx0, y0, Z - 0.5), (bx0 + wt, by1 - wt, BTOP))
    # parede leste RECORTADA no bolso do trono (x 33..35,5, y 288..300, z 54,6..76,6): o trono recolhido entra ate 34,5
    col_box2("SG_CasCrown", (bx1 - wt, y0, Z - 0.5), (bx1, py0, BTOP))
    col_box2("SG_CasCrown", (bx1 - wt, py1, Z - 0.5), (bx1, by1 - wt, BTOP))
    col_box2("SG_CasCrown", (px1, py0, Z - 0.5), (bx1, py1, BTOP))
    col_box2("SG_CasCrown", (bx1 - wt, py0, Z - 0.5), (px1, py1, pz0))
    col_box2("SG_CasCrown", (bx1 - wt, py0, pz1), (px1, py1, BTOP))
    col_box2("SG_CasChancel", (bx0 + wt, y0, Z - 0.5), (cx0, ry1, BTOP))
    for p0, p1 in (((cx1, y0, Z - 0.5), (bx1 - wt, py0, BTOP)), ((cx1, py1, Z - 0.5), (bx1 - wt, ry1, BTOP)),
                   ((cx1, py0, Z - 0.5), (bx1 - wt, py1, pz0)), ((cx1, py0, pz1), (bx1 - wt, py1, BTOP))):
        col_box2("SG_CasChancel", p0, p1)
    for p0, p1 in (((cx0, ry0, Z - 0.5), (-aw / 2, ry1, BTOP)), ((aw / 2, ry0, Z - 0.5), (cx1, ry1, BTOP)),
                   ((-aw / 2, ry0, zc + ah), (aw / 2, ry1, BTOP))):
        col_box2("SG_CasRetable", p0, p1)
    col_box2("SG_CasHallCeil", (cx0, y0, Z + L.TRI_ARCH_H), (cx1, ry0, Z + L.TRI_ARCH_H + 1.5))
    col_box2("SG_CasHallCeil", (bx0 + wt, ry1, Z + 36.0), (bx1 - wt, by1 - wt, Z + 37.5))
    ngon_col("SG_CasCrown", x, y, n, r, BTOP - 1.0, CR_TOP, rot)
    light("L_SGCas_Crown", "POINT", (x, y - ap - 14.0, s2 + 22.0), 1600.0, VIOLET, 1.5)


# ------------------------------------------------------------------ 6. POCO da escada caracol ACIMA de z 44 (abaixo: sg_cave)
SPLIT_Z = 44.0
PR_IN, PR_OUT = 14.3, 18.3             # 16-gono da Torre do Poco do sg_cave (vertices em multiplos de 22,5): casa em z 44


def poco():
    """CASCA do poco da escada caracol de z 44 ate o teto da camara (Z+36), na MESMA planta da Torre do Poco do
    sg_cave (16 faces, vertices R 14,3 / 18,3): fiadas de ~4,9 com JUNTA EM V por dentro, vao do arco secreto ao sul
    (67,5 graus: passa os 12 do arco com folga), ombreiras de cantaria, nervuras do teto com fecho e uma coroa de
    ferro pendurada. Degraus, patamar de topo, nucleo e corrimao da escada INTEIRA sao do sg_cave; colisao do sg_col."""
    mb = MB("SG_Cas_Poco", "04_CASTLE", random.Random(5651), detail="near")
    cx, cy = L.SPIRAL_C
    zc = L.CHANCEL_Z
    aw, ah = L.SECRET_ARCH
    ztop = Z + 36.0
    oh = 34.0
    ap_in = PR_IN * math.cos(math.radians(11.25))
    T = PR_OUT * math.cos(math.radians(11.25)) - ap_in
    side = 2 * PR_IN * math.sin(math.radians(11.25))
    nc = 9
    hc = (ztop - SPLIT_Z) / nc
    for k in range(16):
        phi = 22.5 * k + 11.25
        W = face_frame(cx, cy, ap_in, phi)
        near = abs(((phi - 270.0 + 180.0) % 360.0) - 180.0) < oh + 12.0
        for hs in ((-1, 1) if near else (0,)):
            u0, u1 = sorted((0.0, hs * side / 2)) if hs else (-side / 2, side / 2)
            am = phi + hs * 5.6
            open_ = abs(((am - 270.0 + 180.0) % 360.0) - 180.0) < oh
            for c in range(nc):
                z0, z1 = SPLIT_Z + c * hc, SPLIT_Z + (c + 1) * hc
                spans = [(z0, z1)]
                if open_:
                    spans = []
                    if z0 < zc - 0.3:
                        spans.append((z0, min(z1, zc - 0.3)))
                    if z1 > zc + ah + 0.25:
                        spans.append((max(z0, zc + ah + 0.25), z1))
                for s0, s1 in spans:
                    if s1 - s0 < 0.3:
                        continue
                    j = min(0.2, (s1 - s0) * 0.2)
                    ledge(mb, W, u0, u1, [(j, s0), (0.0, s0 + j), (0.0, s1 - j), (j, s1), (T, s1), (T, s0)],
                          CM_ if c % 2 == 0 else ASH)
    # ombreiras e verga do vao (cantaria clara) no lado de dentro do poco
    for s in (-1, 1):
        a = math.radians(270.0 + s * oh)
        px, py = cx + (ap_in + 0.4) * math.cos(a), cy + (ap_in + 0.4) * math.sin(a)
        mb.box((1.2, 1.4, ah + 0.6), (px, py, zc + ah / 2 + 0.1), (0, 0, a), CAPL, 0.04)
    # teto: 16 nervuras do anel ate o fecho + coroa de ferro pendurada (sem brilho)
    for k in range(8):
        a = math.radians(45.0 * k)
        p0 = (cx + 2.6 * math.cos(a), cy + 2.6 * math.sin(a), ztop - 0.45)
        p1 = (cx + (ap_in - 0.1) * math.cos(a), cy + (ap_in - 0.1) * math.sin(a), ztop - 0.45)
        mb.beam(p0, p1, 0.7, 0.9, CAPL, 0.0)
    EM._lathe(mb, (cx, cy, ztop - 2.2), [(0.0, 0.0), (1.2, 0.3), (2.6, 1.2), (2.9, 2.2)], CAPL, 12, 0.0,
              caps=(False, False))
    mb.rod((cx, cy, ztop - 2.2), (cx, cy, ztop - 8.0), 0.12, BI, 6)
    EM._lathe(mb, (cx, cy, ztop - 8.3), [(2.9, 0.0), (3.2, 0.15), (3.2, 0.45), (2.9, 0.6)], BI, 16, 0.0,
              caps=(False, False))
    for k in range(8):
        a = 2 * math.pi * k / 8
        pc = (cx + 3.05 * math.cos(a), cy + 3.05 * math.sin(a))
        mb.rod((pc[0], pc[1], ztop - 7.7), (cx, cy, ztop - 3.2), 0.05, BI, 4)
        mb.cyl(0.22, 0.3, (pc[0], pc[1], ztop - 7.55), (0, 0, 0), BI, n=6, bevel=0.0)
    mb.finish()


# ------------------------------------------------------------------ 7. estandartes da ordem (torres do portao)
def standards(banners):
    mb = MB("SG_Cas_Estandartes", "04_CASTLE", random.Random(5801), detail="near")
    for top, yaw, w, h, off in banners:
        EM.banner(mb, mb, mb, mb, top, yaw, w, h, trim=EM.BRONZE)
        fx, fy_ = math.cos(yaw), math.sin(yaw)
        ux, uy = math.sin(yaw), -math.cos(yaw)
        for sd in (-1, 1):
            du = sd * (w / 2 + 0.25)
            wx, wy = top[0] + ux * du - fx * off, top[1] + uy * du - fy_ * off
            mb.beam((wx - fx * 0.1, wy - fy_ * 0.1, top[2]), (wx + fx * (off + 0.2), wy + fy_ * (off + 0.2), top[2]),
                    0.22, 0.26, BI, 0.0)
            mb.beam((wx - fx * 0.05, wy - fy_ * 0.05, top[2] - 1.3), (wx + fx * off * 0.85, wy + fy_ * off * 0.85,
                    top[2] - 0.1), 0.16, 0.16, BI, 0.0)
            mb.box((0.7, 0.12, 1.9), (wx + fx * 0.02, wy + fy_ * 0.02, top[2] - 0.6), (0, 0, yaw + math.pi / 2), BI, 0.0)
    _fin(mb)


# ------------------------------------------------------------------ build
def build():
    banners = []
    muralha(banners)
    stairs()
    nave()
    roofs()
    facade(banners)
    front_towers()
    crown()
    poco()
    standards(banners)
    SL.dummy("SCALE_Dummy_Porch", -5.0, YD - 4.0, Z + 0.6, math.pi / 2)
    light("L_SGCas_Gate", "POINT", (0.0, WFRONT - 7.0, Z + 6.0), 700.0, WARM, 0.6)
