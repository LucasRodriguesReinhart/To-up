# sg_castle - CASTELO da Ilha 3 (Shadow Garden): o heroi da ilha, a SEDE da ordem. Substitui sg_blockout.castle.
#   muralha sobre a borda sul do P3 (ameias, mata-caes) + portao central (vao 16 x 18) entre 2 torres com VERGA BAIXA
#   (da praca o olho passa por cima dela e acha o emblema) + passagem leste aberta ate o ceu com 2 torrinhas + cortina
#   oeste ate a ala oeste + escadas Gate/EastP3; nave = CASCA do Mining Hall (face interna = retangulo do salao,
#   parede 4, teto opaco e colidivel em HALL_CEIL), porta com arquivoltas ogivais alternando pedra violeta/obsidiana e
#   medalhao da ordem no timpano; janelas altas (vidro frio de luar, o mesmo do hall); EMBLEMA MONUMENTAL da ordem
#   (sg_emblem) no lugar da antiga rosacea: medalhao de obsidiana com contorno de energia, campo de pedra violeta e
#   grande arco ogival de prata que abraca o porche; clerestorio com lancetas de energia violeta, telhado preto-violeta
#   com cumeeira/rincoes de prata, naves laterais, contrafortes com pinaculos e arcobotantes; 2 torres da fachada com
#   varanda de mata-caes; TORRE-COROA heroi com linhas de energia nas arestas, lancetas violeta e pontas de energia;
#   alas NAO entraveis (oeste sobre o terreno bravo, leste no beco junto a nave), janelas quentes (vida humana);
#   4 estandartes da ordem (sg_emblem.banner) em ritmo simetrico: torres do portao e torres da fachada.
#   Camadas de material: BASE (soco de obsidiana + cordao de prata) / CORPO (pedra do castelo, faixas de obsidiana nos
#   andares, molduras violeta) / COROAMENTO (mata-caes de obsidiana, remate violeta, agulhas preto-violeta com aneis e
#   remates de prata). Nenhum simbolo alem do emblema da ordem.
#   Dentro do salao: SO a casca (pele de pedra de interior, teto, nervuras do teto). O acabamento e do agente HALL.
# Colisao propria: paredes da nave com o vao da porta, teto, contrafortes, porche, torres, muralha (vaos do portao e
# da passagem leste), cortina, alas. Nada colidivel dentro de MINE_RECT entre piso+0,3 e piso+12.
import math, random
import sg_lib as SL
import fm_lib
from sg_lib import MB, col_box, col_box2, light, ngon_col, box_walls_col
import sg_layout as L

# ------------------------------------------------------------------ materiais novos (2 de 9)
fm_lib.MATS.setdefault("Stone_SGCasInterior", (fm_lib.S(104, 104, 120), 0.8, 0.0, 0, None, 0.08))  # pele interna
# vidro frio de luar: MESMOS valores do sg_hall (dentro e fora casam)
fm_lib.MATS.setdefault("Glass_SGHallMoon", (fm_lib.S(96, 124, 186), 0.4, 0.0, 0.4, fm_lib.S(110, 145, 220), 0.0))
import sg_emblem as EM

# REFINAMENTO 2026-09-28: paleta com FUNCAO (sg_lib.SMATS) - base/soco/faixas = obsidiana, corpo = Stone_SG_Castle,
# molduras nobres = pedra violeta, remates = prata, ferragens = ferro negro, energia (so linhas e focos) = neon violeta
OB = "Stone_SG_Obsidian"
VI = "Stone_SG_Violet"
SV = "Metal_SG_Silver"
BI = "Metal_SG_BlackIron"
VG = "SG_VioletDeep_Glow"
RG = "SG_Rune_Glow"
WW_M = "Window_Warm"

Z = L.P3
Z2 = L.P2
ZB = Z - 0.4                        # base das paredes (afunda no piso)
ZT = 33.0                           # base do que nasce no terreno bravo (acima da caixa da dungeon, z 32)
CEIL = L.HALL_CEIL                  # 80,2
HX0, HY0, HX1, HY1 = L.HALL_X0, L.HALL_Y0, L.HALL_X1, L.HALL_Y1
TW = L.HALL_WALL
OX0, OY0, OX1, OY1 = HX0 - TW, HY0 - TW, HX1 + TW, HY1 + TW     # -46, 40, 46, 136 (face externa)
EAVE = CEIL + 8.0                   # 88,2 cornija das naves laterais
CLR = 22.0                          # meia largura do corpo central (clerestorio / fachada central)
CLR_TOP = CEIL + 32.0               # 112,2 beiral do telhado da nave
NAVE_RISE = 30.0                    # cumeeira ~142, de quatro aguas na frente (a coroa aparece da praca)
AISLE_HI = 101.0                    # topo do telhado de meia-agua das naves laterais (encosta no clerestorio)
# ritmo da nave casado com o interior (sg_hall): 4 janelas por lado no eixo dos vitrais, contrafortes nas pilastras
WIN_Y = [HY0 + 16.0 + k * (HY1 - HY0 - 32.0) / 3.0 for k in range(4)]                 # 60, 78,67, 97,33, 116
_DY = WIN_Y[1] - WIN_Y[0]
BUTT_Y = [WIN_Y[0] - _DY / 2] + [(a + b) / 2 for a, b in zip(WIN_Y, WIN_Y[1:])] + [WIN_Y[-1] + _DY / 2]  # 50,67..125,33
WIN_A, WIN_RISE = 3.0, 3.9          # meia largura / flecha do arco (vao 6 x 12,0, igual ao vitral interno)
WIN_SILL = Z + 17.6                 # 69,8 (acima de piso+14; o peitoril interno e a galeria alta do salao)
WIN_SPRING = Z + 21.8               # 74,0 -> apice 77,9 (abaixo do teto em 80,2)
DW, DH = L.HALL_DOOR_W, L.HALL_DOOR_H
ARCH_RISE = 9.5                     # flecha das arquivoltas do portal (nascem na verga, 70,2)
SOC = Z + 2.6                       # topo do soco de obsidiana (cordao de prata logo acima)
# emblema monumental da fachada (centro piso+47, acima da porta de 18, abaixo da empena) e o arco de prata que o emoldura
EMB_Z, EMB_R = Z + 47.0, 9.5
ARC_A, ARC_ZR, ARC_RISE = 15.0, Z + 32.0, 34.0
GAB_W, GAB_TOP = 13.0, CLR_TOP + 18.0
FT_SPIRE = 32.0                     # agulha das torres da fachada (abaixo da flecha da coroa)
WALL_TOP = Z + 12.0                 # 64,2 passeio da muralha
GATE_R = min(7.0, (L.GATEHOUSE_TOWERS[1][0] - L.GATEHOUSE_W / 2 - 0.06) / math.cos(math.pi / 8))   # face plana 0,06 atras do vao
EG_X, EG_W = L.EAST_WALL_GAP
EG_R = 3.6
EG_AP = EG_R * math.cos(math.pi / 8)
EG_TURRETS = [(EG_X - EG_W / 2 - EG_AP - 0.06, -6.2), (EG_X + EG_W / 2 + EG_AP + 0.06, -6.2)]
SW_TOWER = (L.WALL_X[0] - 0.5, -6.2, 6.5)
CR_X, CR_Y, CR_R, CR_TOP = L.CROWN_TOWER
BACK_TURRETS = [(-48.0, 138.0, 5.0), (48.0, 138.0, 5.0)]
FAC_TURRETS = [(-CLR, 38.4, 3.2), (CLR, 38.4, 3.2)]
# alas (nao entraveis): oeste sobre o terreno bravo, leste no beco entre a nave e o patio da dungeon
WW = (-94.0, 65.0, -62.0, 133.0)    # x0, y0, x1, y1 corpo da ala oeste
WW_EAVE = 86.2
EW = (OX1 + 3.4, 50.0, 60.0, 134.0)  # ala leste (encosta nos contrafortes)
EW_EAVE = Z + 12.0
WING_TOWERS = [(-95.0, 65.0, 6.5, 112.0, 26.0), (-95.0, 133.0, 6.0, 102.0, 20.0), (-66.0, 138.0, 6.5, 114.0, 24.0),
               (55.0, 140.0, 6.5, 106.0, 22.0)]
WALL_TOWERS = [(-46.0, -6.0, 4.6), (62.0, -6.0, 4.6)]      # torres intermediarias da muralha (sul da face: y -10,3)
CURTAIN_TOWER = (-82.0, 16.0, 5.5)                          # torre da cortina oeste

WARM = (1.0, 0.72, 0.45)
VIOLET = (0.62, 0.45, 1.0)

P1, P2, P3 = L.P1, L.P2, L.P3
CAMS = {
    "CAM_SGCas_FrontHigh": ((0.0, -230.0, 150.0), (0.0, 70.0, 112.0), 24),
    "CAM_SGCas_West": ((-300.0, 60.0, 150.0), (0.0, 80.0, 105.0), 24),
    "CAM_SGCas_East": ((300.0, 30.0, 150.0), (0.0, 80.0, 105.0), 24),
    "CAM_SGCas_BackNE": ((210.0, 360.0, 190.0), (0.0, 95.0, 110.0), 24),
    "CAM_SGCas_PlayerHeight_Plaza": ((6.0, -150.0, P1 + 5.2), (0.0, 60.0, P3 + 62.0), 22),
    "CAM_SGCas_PlayerHeight_Gate": ((-8.0, -52.0, P2 + 5.2), (0.0, -6.0, P3 + 16.0), 22),
    "CAM_SGCas_PlayerHeight_Forecourt": ((-30.0, 6.0, P3 + 5.2), (6.0, 60.0, P3 + 36.0), 20),
    "CAM_SGCas_PlayerHeight_WestAlley": ((-56.0, 60.0, P3 + 5.2), (-50.0, 130.0, P3 + 18.0), 20),
    "CAM_SGCas_PlayerHeight_DungeonYard": ((96.0, 36.0, P3 + 5.2), (40.0, 110.0, P3 + 40.0), 20),
    "CAM_SGCas_PlayerHeight_Terrace": ((-40.0, 172.0, P3 + 5.2), (0.0, 140.0, P3 + 66.0), 20),
    "CAM_SGCas_PlayerHeight_EastGap": ((112.0, -46.0, P2 + 5.2), (112.0, -4.0, P3 + 10.0), 22),
}

# rota extra: patio -> contorno da torre oeste da fachada -> beco oeste -> terraco norte (atras da coroa)
EXTRA_ROUTES = {
    "PATIO->BECO_OESTE->TERRACO": ([(0.0, 20.0), (-40.0, 24.0), (-60.0, 28.0), (-70.0, 36.0), (-66.0, 50.0),
                                    (-56.0, 62.0), (-54.0, 100.0), (-52.0, 128.0), (-55.3, 136.0), (-55.0, 142.0),
                                    (-40.0, 162.0), (-24.0, 170.0)], P3),
}
EXTRA_PROBES = []


# ------------------------------------------------------------------ geometria base
def _fin(mb):
    """finish + limpeza das lascas de area nula que o tubo fechado do sg_emblem (congelado) deixa na emenda do anel"""
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
    """arco ogival (2 arcos) de (uc-a-d, zr) pelo apice ate (uc+a+d, zr); d = afastamento (moldura)"""
    rise = max(rise, a)
    c = (rise * rise - a * a) / (2.0 * a)
    R = a + c + d
    th1 = math.acos(max(-1.0, min(1.0, -c / R)))
    left = [(uc + c + R * math.cos(th), zr + R * math.sin(th)) for th in
            [math.pi + (th1 - math.pi) * k / n for k in range(n + 1)]]
    left[-1] = (uc, left[-1][1])
    right = [(2 * uc - u, z) for (u, z) in reversed(left[:-1])]
    return left + right


def wall_run(mb, W, u0, u1, zb, zt, t0, t1, opens, m, inner_m=None):
    """parede de u0 a u1 com vaos ogivais: opens = [(uc, a, peitoril, nascenca, flecha)]"""
    cur = u0
    for uc, a, zs, zr, rise in sorted(opens):
        l, r = uc - a, uc + a
        if l - cur > 0.01:
            panel(mb, W, rect(cur, l, zb, zt), t0, t1, m, inner_m)
        if zs - zb > 0.01:
            panel(mb, W, rect(l, r, zb, zs), t0, t1, m, inner_m)
        panel(mb, W, [(r, zt), (l, zt)] + ogive(uc, a, zr, rise), t0, t1, m, inner_m)
        cur = r
    if u1 - cur > 0.01:
        panel(mb, W, rect(cur, u1, zb, zt), t0, t1, m, inner_m)


def window(mb, W, uc, a, zs, zr, rise, t_glass, t_out, glass_m="Glass_SGHallMoon", frame_m=VI, fw=0.8,
           dp=0.45, mullion=True, sill=True, sill_m=OB):
    """vidro ogival no meio da parede + moldura (ombreiras + arquivolta numa peca so) + mainel + peitoril"""
    arc = ogive(uc, a, zr, rise)
    panel(mb, W, [(uc - a, zs), (uc + a, zs)] + list(reversed(arc)), t_glass - 0.08, t_glass + 0.08, glass_m)
    if mullion:
        panel(mb, W, rect(uc - 0.22, uc + 0.22, zs, zr + rise * 0.45), t_glass - 0.3, t_glass + 0.3, frame_m)
        panel(mb, W, rect(uc - a, uc + a, zr - 0.2, zr + 0.2), t_glass - 0.3, t_glass + 0.3, frame_m)
    if frame_m:
        outer = ogive(uc, a, zr, rise, d=fw)
        band = [(uc - a, zs), (uc - a, zr)] + arc[1:-1] + [(uc + a, zr), (uc + a, zs), (uc + a + fw, zs),
                                                         (uc + a + fw, zr)] + list(reversed(outer))[1:-1] + \
               [(uc - a - fw, zr), (uc - a - fw, zs)]
        panel(mb, W, band, t_out - 0.05, t_out + dp, frame_m)
    if sill:
        panel(mb, W, rect(uc - a - fw - 0.3, uc + a + fw + 0.3, zs - 0.55, zs), t_out - 0.05, t_out + dp + 0.35, sill_m)


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


def rect_frustum(mb, x0, y0, x1, y1, z0, z1, e0, e1, m):
    """bloco retangular com talude (base alargada e0, topo e1)"""
    bm = mb.bm
    a = [bm.verts.new(p) for p in ((x0 - e0, y0 - e0, z0), (x1 + e0, y0 - e0, z0), (x1 + e0, y1 + e0, z0),
                                   (x0 - e0, y1 + e0, z0))]
    b = [bm.verts.new(p) for p in ((x0 - e1, y0 - e1, z1), (x1 + e1, y0 - e1, z1), (x1 + e1, y1 + e1, z1),
                                   (x0 - e1, y1 + e1, z1))]
    bm.faces.new(list(reversed(a)))
    bm.faces.new(b)
    for i in range(4):
        j = (i + 1) % 4
        bm.faces.new((a[i], a[j], b[j], b[i]))
    mb._post(a + b, m, None, 0, 1)


def shaft(mb, cx, cy, r, n, z0, z1, m, rot0=None):
    mb.prism(ngon_pts(cx, cy, r, n, rot0), z0, z1, m)


def spire(mb, cx, cy, r, n, z0, h, m, rot0=None, flare=0.1, rings=(0.36,), ring_m=SV):
    """agulha gotica: beiral levemente alargado + cone ingreme; aneis de prata no beiral e ao longo do cone"""
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
        frustum(mb, cx, cy, rr + 0.12, rr + 0.12, n, z0 - 0.35, z0 + 0.05, ring_m, rot0)
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


def hip_roof(mb, x0, y0, x1, y1, z0, h, m, ridge_frac=0.5):
    """telhado de quatro aguas (cumeeira ao longo do lado maior)"""
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


def face_frame(cx, cy, ap, phi_deg):
    """referencial de parede na face de um poligono (centro da face, u tangente, t para fora)"""
    ph = math.radians(phi_deg)
    return ((cx + ap * math.cos(ph), cy + ap * math.sin(ph)), (-math.sin(ph), math.cos(ph)), (math.cos(ph), math.sin(ph)))


def slit(mb, W, z0, h, w=0.9, m="Window_Warm", pointed=True):
    a = w / 2
    if pointed:
        panel(mb, W, [(-a, z0), (a, z0)] + list(reversed(ogive(0.0, a, z0 + h - a * 1.4, a * 1.4, n=3))), -0.1, 0.14, m)
    else:
        panel(mb, W, rect(-a, a, z0, z0 + h), -0.1, 0.14, m)


def socle(mb, x, y, r, n, z0, z1, rot, e=0.9):
    """soco de obsidiana (base alargada) + cordao de prata no topo: a BASE de tudo o que e castelo"""
    frustum(mb, x, y, r + e, r + 0.25, n, z0, z1, OB, rot)
    frustum(mb, x, y, r + 0.42, r + 0.42, n, z1 - 0.05, z1 + 0.4, SV, rot)


def band(mb, x, y, r, n, z, rot, m=OB, h=1.2, e=0.5):
    """faixa horizontal (marca de andar) em volta de um fuste"""
    frustum(mb, x, y, r + e, r + e, n, z, z + h, m, rot)


def glow_edges(mb, cx, cy, r, n, z0, z1, rot0, which, w=0.32, out=0.12):
    """linhas de energia finas e continuas nas arestas (vertices) de um fuste poligonal"""
    for k in which:
        a = math.radians(rot0 + 360.0 * k / n)
        px, py = cx + (r + out) * math.cos(a), cy + (r + out) * math.sin(a)
        mb.box((w, w, z1 - z0), (px, py, (z0 + z1) / 2), (0, 0, a + math.pi / 4), VG, 0.0)


def small_tower(mb, x, y, r, z0, ztop, sph, rot=22.5, slits=(270.0,)):
    """torre octogonal simples: soco, fuste, cordao, parapeito com mata-caes, agulha navy, remate de prata"""
    zs = max(z0 + 3.0, Z + 2.6)
    socle(mb, x, y, r, 8, z0, zs, rot, e=0.8)
    shaft(mb, x, y, r, 8, zs, ztop, "Stone_SG_Castle", rot)
    parapet_ring(mb, x, y, r, 8, ztop, 1.8, OB, rot, merlons=False)
    spire(mb, x, y, r - 0.2, 8, ztop + 1.8, sph, "Roof_SG_Navy", rot)
    mb.rod((x, y, ztop + 1.6 + sph), (x, y, ztop + 3.4 + sph), 0.18, SV, 6)
    ap = r * math.cos(math.pi / 8)
    for phi in slits:
        slit(mb, face_frame(x, y, ap, phi), ztop - 9.0, 3.0, 0.8)


def parapet_ring(mb, cx, cy, r, n, z0, h, m, rot0=None, corbel_m=OB, merlons=True, cap_m=VI):
    """parapeito com mata-caes: fiada de misulas + anel saliente + ameias"""
    ap = r * math.cos(math.pi / n)
    side = 2 * r * math.sin(math.pi / n)
    rot0 = 180.0 / n if rot0 is None else rot0
    for k in range(n):
        phi = rot0 + 360.0 * k / n + 180.0 / n
        W = face_frame(cx, cy, ap, phi)
        for f in ((-0.28, 0.28) if side > 5 else (0.0,)):
            panel(mb, W, rect(f * side - 0.35, f * side + 0.35, z0 - 1.6, z0), -0.2, 0.8, corbel_m)
    frustum(mb, cx, cy, r + 0.9, r + 0.9, n, z0, z0 + h, m, rot0)
    if cap_m:
        frustum(mb, cx, cy, r + 1.1, r + 1.1, n, z0 + h - 0.45, z0 + h, cap_m, rot0)
    if merlons:
        for k in range(n):
            phi = rot0 + 360.0 * k / n + 180.0 / n
            W = face_frame(cx, cy, ap + 0.9 * math.cos(math.pi / n), phi)
            for f in ((-0.25, 0.25) if side > 5 else (0.0,)):
                panel(mb, W, rect(f * side - 0.6, f * side + 0.6, z0 + h, z0 + h + 1.4), -1.0, 0.0, m)


# ------------------------------------------------------------------ 1. muralha, portao, passagem leste, cortina oeste
def muralha(banners):
    rng = random.Random(5101)
    mb = MB("SG_Cas_Muralha", "04_CASTLE", rng, detail="near")
    wy0, wy1 = L.WALL_Y0, L.WALL_Y1
    gw = L.GATEHOUSE_W
    cuts = [(-gw / 2, gw / 2), (EG_X - EG_W / 2, EG_X + EG_W / 2)]
    xs = [L.WALL_X[0]] + [c for ab in cuts for c in ab] + [L.WALL_X[1]]
    front = wy0 - 0.3                           # 0,3 a frente da face do arrimo (sem z-fight com o terreno)
    for a, b in zip(xs[0::2], xs[1::2]):
        mb.box2((a, front, Z2 - 0.6), (b, wy1, WALL_TOP), "Stone_SG_Block", 0.0)
        # talude de obsidiana (soco inclinado) na base, sobre o P2, com cordao de prata no topo
        panel(mb, ((a, 0.0), (0.0, 1.0), (1.0, 0.0)), [(front - 0.9, Z2 - 0.6), (front + 0.05, Z2 - 0.6),
                                                        (front + 0.05, Z2 + 5.6)], 0.0, b - a, OB)
        mb.box2((a, front - 0.3, Z2 + 5.5), (b, front + 0.1, Z2 + 5.9), SV, 0.0)
        # faixa de obsidiana + fiada de misulas (mata-caes) + ameias na face externa; parapeito baixo na face do patio
        mb.box2((a, front - 0.7, WALL_TOP - 1.6), (b, front + 0.2, WALL_TOP), OB, 0.0)
        n = max(1, int((b - a) / 3.2))
        step = (b - a) / n
        for k in range(n):
            x = a + (k + 0.5) * step
            mb.box((0.7, 0.8, 1.4), (x, front - 0.35, WALL_TOP - 2.3), (0, 0, 0), OB, 0.0)
            if k % 2 == 0:
                mb.box((min(1.9, step * 0.9), 1.3, 2.2), (x, front - 0.1, WALL_TOP + 1.1), (0, 0, 0), "Stone_SG_Block", 0.08)
        mb.box2((a, wy1 - 0.8, WALL_TOP), (b, wy1, WALL_TOP + 1.1), "Stone_SG_Block", 0.0)
        mb.box2((a, front - 0.45, Z - 0.6), (b, front + 0.1, Z + 0.4), OB, 0.0)      # faixa no nivel do P3
        mb.box2((a, wy1 - 0.25, Z + 0.0), (b, wy1 + 0.25, Z + 1.2), OB, 0.0)         # rodape do lado do patio
        col_box2("SG_CasWall", (a, wy0, Z - 0.5), (b, wy1, WALL_TOP))
    # --- torre-portaria: VERGA baixa de obsidiana entre as 2 torres (vao 16 x 18 livre). Baixa de proposito: da praca,
    # o olho passa por cima dela e encontra o emblema monumental da fachada.
    gz = Z + L.GATEHOUSE_H
    gh = 3.6
    gy0, gy1 = wy0 - 1.6, wy1 + 1.4
    mb.box2((-gw / 2 - 0.5, gy0, gz), (gw / 2 + 0.5, gy1, gz + gh), "Stone_SG_Castle", 0.0)
    col_box2("SG_CasWall", (-gw / 2, gy0, gz), (gw / 2, gy1, gz + gh))
    for yy, sgn in ((gy0, -1), (gy1, 1)):
        W = ((0.0, yy), (1.0, 0.0), (0.0, sgn))
        # verga de obsidiana entre filetes de pedra violeta, remate violeta saliente; nada acima (vista livre)
        panel(mb, W, rect(-gw / 2 - 0.3, gw / 2 + 0.3, gz - 0.3, gz + 2.9), -0.05, 0.35, OB)
        panel(mb, W, rect(-gw / 2 - 0.3, gw / 2 + 0.3, gz - 0.5, gz - 0.1), -0.05, 0.55, VI)
        panel(mb, W, rect(-gw / 2 - 0.5, gw / 2 + 0.5, gz + 2.9, gz + 3.9), -0.05, 0.8, VI)
        # fecho (chave) de pedra violeta no meio da verga; o simbolo da ordem no portao vem dos estandartes das torres
        # (um medalhao aqui empilhava 4 luas no mesmo eixo, vistas da escada)
        panel(mb, W, [(-1.3, gz + 2.9), (1.3, gz + 2.9), (0.8, gz - 0.5), (-0.8, gz - 0.5)], -0.05, 0.6, VI)
    mb.box2((-gw / 2 - 0.5, gy0 - 0.3, gz + gh), (gw / 2 + 0.5, gy1 + 0.3, gz + 3.9), VI, 0.0)
    # grade levadica recolhida (dentes de ferro negro)
    for k in range(9):
        x = -gw / 2 + 0.9 + k * (gw - 1.8) / 8
        mb.box((0.36, 0.36, 1.6), (x, -6.0, gz - 0.2), (0, 0, 0), BI, 0.0)
    mb.box2((-gw / 2, -6.25, gz - 0.9), (gw / 2, -5.75, gz - 0.5), BI, 0.0)
    # --- torres do portao (planta), face plana alinhada ao vao; estandarte da ordem na face sul
    for (x, y, r0) in L.GATEHOUSE_TOWERS:
        r = GATE_R
        rot = 22.5
        socle(mb, x, y, r, 8, Z2 - 0.6, Z2 + 4.0, rot)
        shaft(mb, x, y, r, 8, Z2 + 4.0, Z + 36.0, "Stone_SG_Castle", rot)
        band(mb, x, y, r, 8, WALL_TOP - 1.6, rot, h=1.6, e=0.35)
        parapet_ring(mb, x, y, r, 8, Z + 36.0, 2.4, OB, rot)
        spire(mb, x, y, r - 0.4, 8, Z + 38.4, 19.0, "Roof_SG_Navy", rot)
        mb.rod((x, y, Z + 57.0), (x, y, Z + 60.0), 0.22, SV, 6)
        ap = r * math.cos(math.pi / 8)
        s = 1 if x > 0 else -1
        out_phi = 0.0 if s > 0 else 180.0
        for phi, zz, h, w in ((270.0 + s * 45.0, Z + 14.0, 3.4, 0.9), (out_phi, Z + 27.0, 3.4, 0.9)):
            slit(mb, face_frame(x, y, ap, phi % 360.0), zz, h, w)
        W = face_frame(x, y, ap, 270.0)
        banners.append((_P(W, 0.0, 0.45, Z + 33.0), -math.pi / 2, 3.8, 17.0))
        ngon_col("SG_CasTower", x, y, 8, r, Z2 - 0.5, Z + 36.0, rot)
    # --- passagem leste (aberta ate o ceu) com 2 torrinhas
    for x, y in EG_TURRETS:
        socle(mb, x, y, EG_R, 8, Z2 - 0.6, Z2 + 3.0, 22.5, e=0.6)
        shaft(mb, x, y, EG_R, 8, Z2 + 3.0, Z + 18.0, "Stone_SG_Castle", 22.5)
        frustum(mb, x, y, EG_R + 0.7, EG_R + 0.7, 8, Z + 18.0, Z + 19.6, OB, 22.5)
        frustum(mb, x, y, EG_R + 0.85, EG_R + 0.85, 8, Z + 19.2, Z + 19.6, VI, 22.5)
        spire(mb, x, y, EG_R + 0.2, 8, Z + 19.6, 11.0, "Roof_SG_Navy", 22.5)
        slit(mb, face_frame(x, y, EG_AP, 270.0), Z + 9.0, 2.8, 0.8)
        ngon_col("SG_CasTower", x, y, 8, EG_R, Z2 - 0.5, Z + 18.0, 22.5)
    # --- torre de canto sudoeste + cortina oeste pela borda do P3 ate a ala oeste
    x, y, r = SW_TOWER
    socle(mb, x, y, r, 8, ZT, Z2 + 4.0, 22.5, e=1.0)
    shaft(mb, x, y, r, 8, Z2 + 4.0, Z + 20.0, "Stone_SG_Castle", 22.5)
    band(mb, x, y, r, 8, Z - 0.6, 22.5)
    parapet_ring(mb, x, y, r, 8, Z + 20.0, 2.2, OB, 22.5)
    spire(mb, x, y, r - 0.3, 8, Z + 22.2, 15.0, "Roof_SG_Navy", 22.5)
    slit(mb, face_frame(x, y, r * math.cos(math.pi / 8), 270.0), Z + 8.0, 3.2, 0.9)
    ngon_col("SG_CasTower", x, y, 8, r, Z2 - 0.5, Z + 20.0, 22.5)
    for (x, y, r) in WALL_TOWERS:
        small_tower(mb, x, y, r, Z2 - 0.6, Z + 21.0, 13.0, slits=(270.0, 90.0))
        ngon_col("SG_CasTower", x, y, 8, r, Z2 - 0.5, Z + 21.0, 22.5)
    x, y, r = CURTAIN_TOWER
    small_tower(mb, x, y, r, ZT, Z + 24.0, 15.0, slits=(180.0, 0.0))
    ngon_col("SG_CasTower", x, y, 8, r, Z - 0.5, Z + 24.0, 22.5)
    edge = [(L.WALL_X[0], wy0), (-78.0, 40.0), (-60.0, 60.0)]
    th = 3.4
    for (ax, ay), (bx, by) in zip(edge, edge[1:]):
        dx, dy = bx - ax, by - ay
        ln = math.hypot(dx, dy)
        ux, uy = dx / ln, dy / ln
        nx, ny = -uy, ux                        # para fora (oeste) no contorno anti-horario
        ang = math.atan2(dy, dx)
        cx, cy = (ax + bx) / 2 + nx * th / 2, (ay + by) / 2 + ny * th / 2
        top = Z + 10.0
        mb.box((ln + th, th, top - ZT), (cx, cy, (ZT + top) / 2), (0, 0, ang), "Stone_SG_Block", 0.0)
        mb.box((ln + th, th + 0.8, 1.2), (cx + nx * 0.4, cy + ny * 0.4, top - 0.6), (0, 0, ang), OB, 0.0)
        n = max(1, int(ln / 3.4))
        for k in range(n):
            if k % 2 == 0:
                t = (k + 0.5) / n
                px, py = ax + dx * t + nx * (th - 0.6), ay + dy * t + ny * (th - 0.6)
                mb.box((1.8, 1.2, 2.0), (px, py, top + 1.0), (0, 0, ang), "Stone_SG_Block", 0.08)
        col_box("SG_CasCurtain", (ln + th, th, top - Z + 0.5), (cx, cy, (Z - 0.5 + top) / 2), (0, 0, ang))
    _fin(mb)


def stairs():
    mb = MB("SG_Cas_Escadas", "04_CASTLE", random.Random(5103), detail="near")
    SL.plan_stair(mb, "Gate")
    SL.plan_stair(mb, "EastP3")
    mb.finish()


# ------------------------------------------------------------------ 2. nave: casca do Mining Hall
def nave():
    rng = random.Random(5201)
    mb = MB("SG_Cas_Nave", "04_CASTLE", rng, detail="near")
    IM = "Stone_SGCasInterior"
    CM = "Stone_SG_Castle"
    tg = TW * 0.5                                        # vidro no meio da parede
    opens_side = [(y, WIN_A, WIN_SILL, WIN_SPRING, WIN_RISE) for y in WIN_Y]
    # paredes laterais (u = y), face interna exata no retangulo do salao
    for W in (((HX0, 0.0), (0.0, 1.0), (-1.0, 0.0)), ((HX1, 0.0), (0.0, 1.0), (1.0, 0.0))):
        wall_run(mb, W, HY0, HY1, ZB, EAVE, 0.0, TW, opens_side, CM, IM)
        for y in WIN_Y:
            window(mb, W, y, WIN_A, WIN_SILL, WIN_SPRING, WIN_RISE, tg, TW)
        # cornija de obsidiana (coroamento) + parapeito baixo com remate violeta
        panel(mb, W, rect(HY0 - TW, HY1 + TW, EAVE - 1.0, EAVE + 0.4), TW - 0.2, TW + 0.8, OB)
        panel(mb, W, rect(HY0 - TW, HY1 + TW, EAVE + 0.4, EAVE + 2.0), TW - 0.9, TW, CM)
        panel(mb, W, rect(HY0 - TW, HY1 + TW, EAVE + 1.7, EAVE + 2.1), TW - 1.0, TW + 0.15, VI)
        # soco de obsidiana + cordao de prata; faixa de obsidiana marcando o andar das janelas
        panel(mb, W, rect(HY0 - TW, HY1 + TW, ZB, SOC), TW - 0.1, TW + 0.7, OB)
        panel(mb, W, rect(HY0 - TW, HY1 + TW, SOC - 0.05, SOC + 0.35), TW - 0.1, TW + 0.8, SV)
        panel(mb, W, rect(HY0 - TW, HY1 + TW, WIN_SILL - 1.6, WIN_SILL - 0.55), TW - 0.1, TW + 0.5, OB)
    # fachada sul (u = x, t para fora = -y): naves laterais com janela + corpo central com a porta
    WS = ((0.0, HY0), (1.0, 0.0), (0.0, -1.0))
    WN = ((0.0, HY1), (1.0, 0.0), (0.0, 1.0))
    for W, front in ((WS, True), (WN, False)):
        for s in (-1, 1):
            u0, u1 = (OX0, -CLR) if s < 0 else (CLR, OX1)
            uw = s * 33.0
            opens = [(uw, WIN_A, WIN_SILL, WIN_SPRING, WIN_RISE)] if front else []   # fundo fechado: altar do hall
            wall_run(mb, W, u0, u1, ZB, EAVE, 0.0, TW, opens, CM, IM)
            if front:
                window(mb, W, uw, WIN_A, WIN_SILL, WIN_SPRING, WIN_RISE, tg, TW)
            # empena de meia-agua da nave lateral (esconde o perfil do telhado)
            uo, ui = (OX0, -CLR) if s < 0 else (OX1, CLR)
            panel(mb, W, [(uo, EAVE), (ui, EAVE), (ui, AISLE_HI + 1.6), (uo, EAVE + 3.2)], 0.4, TW, CM)
            panel(mb, W, [(uo, EAVE + 2.6), (ui, AISLE_HI + 1.0), (ui, AISLE_HI + 2.2), (uo, EAVE + 3.8)], TW - 0.2,
                  TW + 0.6, OB)
            panel(mb, W, rect(min(uo, ui), max(uo, ui), ZB, SOC), TW - 0.1, TW + 0.7, OB)
            panel(mb, W, rect(min(uo, ui), max(uo, ui), SOC - 0.05, SOC + 0.35), TW - 0.1, TW + 0.8, SV)
            panel(mb, W, rect(min(uo, ui), max(uo, ui), EAVE - 1.0, EAVE + 0.4), TW - 0.2, TW + 0.8, OB)
            panel(mb, W, rect(min(uo, ui), max(uo, ui), WIN_SILL - 1.6, WIN_SILL - 0.55), TW - 0.1, TW + 0.5, OB)
        if front:
            panel(mb, W, rect(-CLR, -DW / 2, ZB, CLR_TOP), 0.0, TW, CM, IM)
            panel(mb, W, rect(DW / 2, CLR, ZB, CLR_TOP), 0.0, TW, CM, IM)
            panel(mb, W, rect(-DW / 2, DW / 2, Z + DH, CLR_TOP), 0.0, TW, CM, IM)
        else:
            panel(mb, W, rect(-CLR, CLR, ZB, CLR_TOP), 0.0, TW, CM, IM)
        if front:
            # soco + cordao de prata do corpo central (fora do vao da porta)
            for s_ in (-1, 1):
                u0_, u1_ = sorted((s_ * CLR, s_ * (DW / 2 + 5.6)))
                panel(mb, W, rect(u0_, u1_, ZB, SOC), TW - 0.1, TW + 0.7, OB)
                panel(mb, W, rect(u0_, u1_, SOC - 0.05, SOC + 0.35), TW - 0.1, TW + 0.8, SV)
            # faixas de obsidiana marcando os andares (fora do arco do emblema)
            for s_ in (-1, 1):
                u0_, u1_ = sorted((s_ * CLR, s_ * (ARC_A + 2.6)))
                panel(mb, W, rect(u0_, u1_, EAVE - 1.0, EAVE + 0.4), TW - 0.2, TW + 0.8, OB)
                panel(mb, W, rect(u0_, u1_, WIN_SILL - 1.6, WIN_SILL - 0.55), TW - 0.1, TW + 0.5, OB)
            # coroamento da fachada: misulas de obsidiana + parapeito; no meio, a EMPENA que recebe o arco de prata do
            # emblema (o parapeito se interrompe onde o arco sobe)
            for k in range(14):
                u = -CLR + (k + 0.5) * 2 * CLR / 14
                if abs(u) < GAB_W - 0.8:
                    continue
                panel(mb, W, rect(u - 0.4, u + 0.4, CLR_TOP - 1.8, CLR_TOP), TW - 0.2, TW + 0.8, OB)
            for s_ in (-1, 1):
                a_, b_ = sorted((s_ * (CLR + 0.6), s_ * GAB_W))
                a2, b2 = sorted((s_ * (CLR + 0.8), s_ * GAB_W))
                panel(mb, W, rect(a_, b_, CLR_TOP, CLR_TOP + 2.4), TW - 1.4, TW + 0.8, CM)
                panel(mb, W, rect(a2, b2, CLR_TOP + 2.0, CLR_TOP + 2.6), TW - 1.6, TW + 1.0, VI)
            for k in range(8):
                u = -CLR + 1.2 + k * (2 * CLR - 2.4) / 7
                if abs(u) < GAB_W + 0.6:
                    continue
                panel(mb, W, rect(u - 0.9, u + 0.9, CLR_TOP + 2.6, CLR_TOP + 4.4), TW - 1.2, TW + 0.6, OB)
            # empena central (pedra do corpo), rampantes de obsidiana, remate de prata
            gz1 = GAB_TOP
            panel(mb, W, [(-GAB_W, CLR_TOP - 2.0), (GAB_W, CLR_TOP - 2.0), (GAB_W, CLR_TOP + 2.4), (0.0, gz1),
                          (-GAB_W, CLR_TOP + 2.4)], TW - 1.4, TW, CM)
            for sd in (-1, 1):
                a, b = (sd * (GAB_W + 0.4), CLR_TOP + 2.2), (0.0, gz1)
                L2 = math.hypot(b[0] - a[0], b[1] - a[1])
                tilt = math.atan2(b[1] - a[1], b[0] - a[0])
                mb.box((L2 + 1.2, 2.4, 1.0), _P(W, (a[0] + b[0]) / 2, TW - 0.4, (a[1] + b[1]) / 2 + 0.35),
                       (0, -tilt, 0), OB, 0.0)
                mb.box((L2 + 1.0, 0.5, 0.3), _P(W, (a[0] + b[0]) / 2, TW + 0.55, (a[1] + b[1]) / 2 + 0.95),
                       (0, -tilt, 0), SV, 0.0)
                # pinaculos nos pes da empena
                px = sd * (GAB_W + 0.4)
                mb.box((1.8, 1.8, 3.4), _P(W, px, TW - 0.3, CLR_TOP + 4.0), (0, 0, 0), OB, 0.0)
                SL.spire(mb, _P(W, px, TW - 0.3, 0)[:2], 1.25, CLR_TOP + 5.7, 6.5, "Roof_SG_Navy", n=4)
                mb.rod(_P(W, px, TW - 0.3, CLR_TOP + 12.0), _P(W, px, TW - 0.3, CLR_TOP + 13.4), 0.14, SV, 4)
            mb.box((1.6, 1.6, 2.2), _P(W, 0.0, TW - 0.5, gz1 + 0.6), (0, 0, 0), OB, 0.0)
            mb.rod(_P(W, 0.0, TW - 0.5, gz1 + 1.6), _P(W, 0.0, TW - 0.5, gz1 + 5.2), 0.26, SV, 6)
            mb.ico(0.55, _P(W, 0.0, TW - 0.5, gz1 + 5.4), SV, 1)
            continue
        # empena de tras (encosta na torre-coroa)
        g_lo = CLR_TOP + 1.9
        apex = CLR_TOP + NAVE_RISE + 1.9
        panel(mb, W, [(-CLR, CLR_TOP), (CLR, CLR_TOP), (CLR, g_lo), (0.0, apex), (-CLR, g_lo)], 0.8, TW, CM)
        for s in (-1, 1):
            a = (s * CLR, g_lo)
            b = (0.0, apex)
            L2 = math.hypot(b[0] - a[0], b[1] - a[1])
            tilt = math.atan2(b[1] - a[1], b[0] - a[0])
            mid = _P(W, (a[0] + b[0]) / 2, 2.4, (a[1] + b[1]) / 2 + 0.2)
            mb.box((L2 + 0.8, 3.6, 0.9), mid, (0, -tilt, 0), OB, 0.0)
        mb.rod(_P(W, 0.0, TW - 1.0, apex), _P(W, 0.0, TW - 1.0, apex + 4.5), 0.3, "Metal_SG_Silver", 6)
        mb.ico(0.7, _P(W, 0.0, TW - 1.0, apex + 4.8), "Metal_SG_Silver", 1)
    # clerestorio (acima do teto interno): paredes x +-CLR com janelas cegas (vidro rente, sem vazar o sotao)
    for s in (-1, 1):
        W = ((s * (CLR - 2.0), 0.0), (0.0, 1.0), (s * 1.0, 0.0))
        panel(mb, W, rect(HY0, HY1, CEIL + 2.0, CLR_TOP), 0.0, 2.0, CM)
        for y in WIN_Y:
            # lancetas altas do clerestorio: energia violeta (o castelo "respira" violeta no alto)
            window(mb, W, y, 1.9, AISLE_HI + 1.6, CLR_TOP - 5.0, 2.8, 2.05, 2.0, glass_m=VG, mullion=True, fw=0.6,
                   dp=0.35)
        panel(mb, W, rect(HY0 - TW, HY1 + TW, CLR_TOP - 0.9, CLR_TOP + 0.3), 1.6, 2.7, OB)
    # contrafortes (em degraus) + pinaculos + arcobotantes ate o clerestorio
    for y in BUTT_Y:
        for s in (-1, 1):
            xo = s * OX1
            mb.box2((min(xo, xo + s * 3.4), y - 1.6, ZB), (max(xo, xo + s * 3.4), y + 1.6, Z + 20.0), CM, 0.0)
            mb.box2((min(xo, xo + s * 4.1), y - 2.1, ZB), (max(xo, xo + s * 4.1), y + 2.1, SOC), OB, 0.0)
            mb.box2((min(xo, xo + s * 4.2), y - 2.2, SOC - 0.05), (max(xo, xo + s * 4.2), y + 2.2, SOC + 0.35), SV, 0.0)
            # degrau superior
            mb.box2((min(xo, xo + s * 2.4), y - 1.3, Z + 20.0), (max(xo, xo + s * 2.4), y + 1.3, EAVE + 3.0), CM, 0.0)
            mb.box((1.3, 2.9, 0.7), (xo + s * 2.9, y, Z + 20.2), (0, s * 0.6, 0), OB, 0.0)
            px = xo + s * 1.2
            mb.box((2.2, 2.2, 4.0), (px, y, EAVE + 5.0), (0, 0, 0), CM, 0.0)
            mb.box((2.6, 2.6, 0.6), (px, y, EAVE + 7.2), (0, 0, 0), OB, 0.0)
            SL.spire(mb, (px, y), 1.55, EAVE + 7.5, 12.0, "Roof_SG_Navy", n=4)
            mb.rod((px, y, EAVE + 19.2), (px, y, EAVE + 20.8), 0.13, SV, 4)
            # pinaculo no topo do clerestorio onde o arcobotante encosta
            qx = s * (CLR + 0.6)
            mb.box((1.8, 1.8, 3.0), (qx, y, CLR_TOP + 1.5), (0, 0, 0), CM, 0.0)
            mb.box((2.2, 2.2, 0.5), (qx, y, CLR_TOP + 3.2), (0, 0, 0), OB, 0.0)
            SL.spire(mb, (qx, y), 1.3, CLR_TOP + 3.45, 9.0, "Roof_SG_Navy", n=4)
            mb.rod((qx, y, CLR_TOP + 12.2), (qx, y, CLR_TOP + 13.6), 0.12, SV, 4)
            # arcobotante: viga inclinada do pinaculo ao clerestorio + escora curva por baixo
            a = (xo + s * 0.4, y, EAVE + 2.4)
            b = (s * CLR, y, AISLE_HI + 3.4)
            mb.beam(a, b, 1.1, 1.3, CM, 0.0)
            c = (s * (CLR + (OX1 - CLR) * 0.45), y, AISLE_HI - 1.6)
            mb.beam((xo + s * 0.2, y, EAVE + 0.4), c, 0.9, 0.9, CM, 0.0)
            mb.beam(c, (s * CLR, y, AISLE_HI + 1.4), 0.9, 0.9, CM, 0.0)
            col_box2("SG_CasButtress", (min(xo, xo + s * 3.4), y - 1.6, Z - 0.5), (max(xo, xo + s * 3.4), y + 1.6, Z + 20.0))
    # teto interno (opaco) + nervuras transversais alinhadas aos contrafortes
    mb.box2((OX0 + 0.3, OY0 + 0.3, CEIL), (OX1 - 0.3, OY1 - 0.3, CEIL + 2.0), IM, 0.0)
    for y in BUTT_Y:
        mb.box2((HX0, y - 0.7, CEIL - 1.0), (HX1, y + 0.7, CEIL), "Stone_SG_Trim", 0.0)
    mb.box2((-0.7, HY0, CEIL - 1.0), (0.7, HY1, CEIL), "Stone_SG_Trim", 0.0)
    for x in (HX0 + 0.5, HX1 - 0.5):
        mb.box2((x - 0.5, HY0, CEIL - 0.9), (x + 0.5, HY1, CEIL), "Stone_SG_Trim", 0.0)
    mb.finish()
    # colisao: paredes com o vao da porta + teto que segura a camera
    box_walls_col("SG_CasHall", (HX0, HY0, HX1, HY1), Z - 0.5, EAVE, TW, doors=[("S", 0.0, DW, DH)])
    col_box2("SG_CasHallCeil", (OX0, OY0, CEIL), (OX1, OY1, CEIL + 2.0))


def nave_roof(mb, e=1.6, yf=HY0 - 2.0, yb=OY1 + 1.4):
    """telhado da nave: quatro aguas na frente (atras do parapeito da fachada), empena atras (na torre-coroa);
    solido fechado + fiadas de ardosia recortadas nas aguas + cumeeira e rincoes"""
    bm = mb.bm
    k = NAVE_RISE / CLR
    zE = CLR_TOP - k * e
    zR = CLR_TOP + NAVE_RISE
    H = CLR + e
    yr = yf + H
    FL, FR = (-H, yf, zE), (H, yf, zE)
    BL, BR = (-H, yb, zE), (H, yb, zE)
    RF, RB = (0.0, yr, zR), (0.0, yb, zR)
    vs = {n: bm.verts.new(p) for n, p in (("FL", FL), ("FR", FR), ("BL", BL), ("BR", BR), ("RF", RF), ("RB", RB))}
    for f in (("FL", "RF", "RB", "BL"), ("FR", "BR", "RB", "RF"), ("FL", "FR", "RF"), ("BL", "RB", "BR"),
              ("FL", "BL", "BR", "FR")):
        bm.faces.new([vs[n] for n in f])
    mb._post(list(vs.values()), "Roof_SG_Navy", None, 0, 1)
    th = math.atan2(zR - zE, H)
    Ls = math.hypot(H, zR - zE)
    rows = int(Ls / 1.9)
    for i in range(rows):
        f0, f1 = i / rows, min(1.0, (i + 1.25) / rows)
        fm = (f0 + f1) / 2
        z = zE + fm * (zR - zE)
        rl = (f1 - f0) * Ls
        for sd in (-1, 1):
            x = sd * H * (1.0 - fm)
            ya = yf + f1 * H
            nx, nz = sd * math.sin(th), math.cos(th)
            mb.box((rl, yb - ya, 0.45), (x + nx * 0.22, (ya + yb) / 2, z + nz * 0.22), (0, sd * th, 0), "Roof_SG_Navy", 0.0)
        xl = 2 * H * (1.0 - f1)
        if xl > 0.6:
            y = yf + fm * H
            mb.box((xl, rl, 0.45), (0.0, y - math.sin(th) * 0.22, z + math.cos(th) * 0.22), (th, 0, 0), "Roof_SG_Navy", 0.0)
    mb.beam((0.0, yr, zR + 0.4), (0.0, yb, zR + 0.4), 1.1, 1.1, "Roof_SG_Navy", 0.0)
    mb.beam((0.0, yr, zR + 1.05), (0.0, yb, zR + 1.05), 0.5, 0.3, SV, 0.0)          # cumeeira de prata
    for sd in (-1, 1):
        mb.beam((0.0, yr, zR + 0.4), (sd * H, yf, zE + 0.4), 0.9, 0.9, "Roof_SG_Navy", 0.0)
        mb.beam((0.0, yr, zR + 0.95), (sd * H, yf, zE + 0.95), 0.4, 0.28, SV, 0.0)   # rincoes de prata
    return zR + 0.9


def roofs():
    rng = random.Random(5301)
    mb = MB("SG_Cas_Telhados", "04_CASTLE", rng, detail="near")
    # telhado da nave: navy ingreme, fiadas de ardosia, cumeeira escura + crista de prata
    ridge = nave_roof(mb)
    y = OY0 + CLR + 6.0
    while y < OY1 - 6.0:
        mb.rod((0.0, y, ridge), (0.0, y, ridge + 2.2), 0.16, "Metal_SG_Silver", 4)
        mb.box((0.18, 0.9, 0.9), (0.0, y, ridge + 2.0), (math.pi / 4, 0, 0), "Metal_SG_Silver", 0.0)
        y += 4.0
    # fleche (agulha fina) no cruzeiro da nave
    fy = (OY0 + OY1) / 2 + 6.0
    shaft(mb, 0.0, fy, 2.2, 8, ridge - 2.0, ridge + 4.0, OB, 22.5)
    spire(mb, 0.0, fy, 2.4, 8, ridge + 4.0, 12.0, "Roof_SG_Navy", 22.5)
    mb.rod((0.0, fy, ridge + 15.6), (0.0, fy, ridge + 17.6), 0.18, "Metal_SG_Silver", 6)
    # lucarnas escuras no telhado da nave (quebram a agua comprida; sem luz: sotao)
    for yy in (61.0, 88.0, 115.0):
        for s in (-1, 1):
            xo = s * 13.0
            zr = CLR_TOP + NAVE_RISE * (1.0 - 13.0 / CLR) + 0.9
            mb.box2((min(xo, xo - s * 5.0), yy - 2.0, zr - 3.0), (max(xo, xo - s * 5.0), yy + 2.0, zr + 3.4),
                    "Stone_SG_Castle", 0.0)
            mb.gable_roof(xo - s * 2.5, yy, 5.0, 4.0, zr + 3.4, 2.8, "Roof_SG_Navy", thick=0.45, over=0.35, axis="X",
                          shingles=False, ridge_m="Roof_SG_Navy")
            Wl = ((xo, 0.0), (0.0, 1.0), (s * 1.0, 0.0))
            window(mb, Wl, yy, 0.8, zr - 1.0, zr + 1.6, 1.0, 0.02, 0.0, glass_m=OB, mullion=False,
                   fw=0.35, dp=0.25, sill=False)
    # meia-aguas das naves laterais (da cornija ao clerestorio)
    for s in (-1, 1):
        xo, xi = s * (OX1 + 1.2), s * CLR
        zo, zi = EAVE - 0.3, AISLE_HI
        L2 = math.hypot(xi - xo, zi - zo)
        tilt = math.atan2(zi - zo, xi - xo)
        rows = int(L2 / 1.9)
        for k in range(rows):
            f0, f1 = k / rows, min(1.0, (k + 1.3) / rows)
            ax, az = xo + (xi - xo) * f0, zo + (zi - zo) * f0
            bx, bz = xo + (xi - xo) * f1, zo + (zi - zo) * f1
            mb.box((math.hypot(bx - ax, bz - az), OY1 - OY0 - 2.0, 0.6), ((ax + bx) / 2, (OY0 + OY1) / 2, (az + bz) / 2 + 0.3),
                   (0, -tilt, 0), "Roof_SG_Navy", 0.0)
    mb.finish()


# ------------------------------------------------------------------ 3. fachada: porta, arquivoltas, emblema monumental
def facade(banners):
    rng = random.Random(5401)
    mb = MB("SG_Cas_Fachada", "04_CASTLE", rng, detail="hero")
    CM = "Stone_SG_Castle"
    fy = OY0                                              # face externa da fachada (y 40)
    W = ((0.0, fy), (1.0, 0.0), (0.0, -1.0))              # u = x, t = para fora (-y)
    zd = Z + DH                                           # verga 70,2
    # porche em degraus (3 ordens) - nada invade o vao de 16. Arquivoltas alternando pedra violeta / obsidiana
    orders = 3
    ow = 1.2
    arch_m = (VI, OB, VI)
    for k in range(orders):
        t0, t1 = k * ow, (k + 1) * ow
        for s in (-1, 1):
            u0 = s * (DW / 2 + k * ow)
            u1 = s * (DW / 2 + orders * ow + 2.0)
            panel(mb, W, rect(min(u0, u1), max(u0, u1), ZB, zd), t0, t1, CM)
            panel(mb, W, rect(min(u0, u1), max(u0, u1), ZB, SOC), t1 - 0.05, t1 + 0.12, OB)
            mb.cyl(0.42, DH - 1.6, _P(W, s * (DW / 2 + k * ow + 0.1), t0 + 0.1, Z + 0.8 + (DH - 1.6) / 2),
                   (0, 0, 0), arch_m[k], 8, bevel=0.0)
            mb.box((1.3, 1.3, 0.8), _P(W, s * (DW / 2 + k * ow + 0.1), t0 + 0.1, Z + 0.4), (0, 0, 0), OB, 0.1)
        inner = ogive(0.0, DW / 2, zd, ARCH_RISE, d=k * ow)
        outer = ogive(0.0, DW / 2, zd, ARCH_RISE, d=(k + 1) * ow)
        panel(mb, W, inner + list(reversed(outer)), t0, t1 + 0.1, arch_m[k])
    # capiteis (friso de obsidiana na verga, filete de prata)
    pw = DW / 2 + orders * ow + 2.0
    panel(mb, W, rect(-pw, pw, zd, zd + 0.9), -0.1, orders * ow + 0.4, OB)
    panel(mb, W, rect(-pw, pw, zd + 0.9, zd + 1.15), -0.1, orders * ow + 0.5, SV)
    # massa do porche ate a empena (wimperg) baixa, que APONTA para o emblema; timpano de obsidiana com o medalhao
    outer_all = ogive(0.0, DW / 2, zd, ARCH_RISE, d=orders * ow)
    gab_top = zd + ARCH_RISE + orders * ow + 3.0
    panel(mb, W, [(pw, zd), (pw, zd + 6.0), (0.0, gab_top), (-pw, zd + 6.0), (-pw, zd)] + outer_all,
          orders * ow - 0.6, orders * ow + 0.2, CM)
    panel(mb, W, [(-DW / 2, zd), (DW / 2, zd)] + list(reversed(ogive(0.0, DW / 2, zd, ARCH_RISE))), -0.05, 0.25, OB)
    EM.plaque(mb, mb, mb, mb, _P(W, 0.0, 0.3, zd + 4.3), -math.pi / 2, 2.9)
    for s in (-1, 1):
        a = (s * pw, zd + 6.0)
        b = (0.0, gab_top)
        L2 = math.hypot(b[0] - a[0], b[1] - a[1])
        tilt = math.atan2(b[1] - a[1], b[0] - a[0])
        mb.box((L2 + 0.6, 1.4, 0.8), _P(W, (a[0] + b[0]) / 2, orders * ow + 0.1, (a[1] + b[1]) / 2 + 0.35),
               (0, -tilt, 0), OB, 0.0)
        mb.box((L2 + 0.4, 0.3, 0.25), _P(W, (a[0] + b[0]) / 2, orders * ow + 0.85, (a[1] + b[1]) / 2 + 0.78),
               (0, -tilt, 0), SV, 0.0)
        # pinaculos do porche (pedra violeta, agulha preto-violeta, remate de prata)
        px = s * (pw - 0.4)
        mb.box((1.6, 1.6, zd + 6.0 - Z + 2.0), _P(W, px, orders * ow + 0.4, (Z + zd + 8.0) / 2), (0, 0, 0), VI, 0.08)
        mb.box((2.0, 2.0, SOC - Z + 0.4), _P(W, px, orders * ow + 0.4, (Z - 0.4 + SOC) / 2), (0, 0, 0), OB, 0.0)
        SL.spire(mb, _P(W, px, orders * ow + 0.4, 0)[:2], 1.2, zd + 8.0, 7.5, "Roof_SG_Navy", n=4)
        mb.rod(_P(W, px, orders * ow + 0.4, zd + 15.2), _P(W, px, orders * ow + 0.4, zd + 16.6), 0.14, SV, 4)
    mb.ico(0.5, _P(W, 0.0, orders * ow - 0.2, gab_top + 0.5), SV, 1)
    # torrinhas-contraforte da fachada (marcam o corpo central) com agulhas
    for x, y, r in FAC_TURRETS:
        socle(mb, x, y, r, 8, ZB, SOC, 22.5, e=0.6)
        shaft(mb, x, y, r, 8, SOC, CLR_TOP + 10.0, CM, 22.5)
        for zz in (EAVE - 1.0, CLR_TOP - 0.9):
            band(mb, x, y, r, 8, zz, 22.5, e=0.45)
        frustum(mb, x, y, r + 0.6, r + 0.6, 8, CLR_TOP + 10.0, CLR_TOP + 11.4, OB, 22.5)
        frustum(mb, x, y, r + 0.75, r + 0.75, 8, CLR_TOP + 11.0, CLR_TOP + 11.4, VI, 22.5)
        spire(mb, x, y, r, 8, CLR_TOP + 11.4, 17.0, "Roof_SG_Navy", 22.5)
        mb.rod((x, y, CLR_TOP + 28.0), (x, y, CLR_TOP + 30.0), 0.18, SV, 6)
        col_box("SG_CasFacTurret", (2 * r, 2 * r, 20.0), (x, y, Z + 9.5))
    _fin(mb)
    emblem_monument()
    # colisao do porche (fora do vao)
    for s in (-1, 1):
        u0, u1 = s * (DW / 2 + ow), s * pw          # a 1a ordem (rente ao vao) fica sem colisao: vao livre de 16
        col_box2("SG_CasPorch", (min(u0, u1), fy - orders * ow, Z - 0.5), (max(u0, u1), fy, zd + 7.0))
    light("L_SGCas_Door", "POINT", (0.0, fy - 5.0, Z + 11.0), 700.0, WARM, 0.6)


def emblem_monument():
    """O SIMBOLO DA ORDEM na fachada: emblema monumental (sg_emblem) num medalhao de obsidiana com contorno de
    energia violeta, sobre um campo de pedra violeta emoldurado por um grande arco ogival de prata que abraca o porche.
    E o primeiro ponto que o olho encontra vindo da praca (a verga do portao da muralha e baixa para nao tapa-lo)."""
    mb = MB("SG_Cas_Emblema", "04_CASTLE", random.Random(5451), detail="hero")
    fy = OY0
    W = ((0.0, fy), (1.0, 0.0), (0.0, -1.0))
    zd = Z + DH
    arc = ogive(0.0, ARC_A, ARC_ZR, ARC_RISE, n=10)
    # campo violeta dentro do arco (acima da verga do porche)
    panel(mb, W, [(-ARC_A, zd), (ARC_A, zd)] + list(reversed(arc)), 0.0, 0.3, VI)
    # arco de prata (banda interna) + banda externa de obsidiana; ombreiras descem ate o soco
    a_sv = ogive(0.0, ARC_A, ARC_ZR, ARC_RISE, d=0.9, n=10)
    a_ob = ogive(0.0, ARC_A, ARC_ZR, ARC_RISE, d=2.6, n=10)
    panel(mb, W, arc + list(reversed(a_sv)), -0.05, 1.0, SV)
    panel(mb, W, a_sv + list(reversed(a_ob)), -0.05, 0.7, OB)
    for s in (-1, 1):
        u0, u1 = sorted((s * ARC_A, s * (ARC_A + 0.9)))
        u2, u3 = sorted((s * (ARC_A + 0.9), s * (ARC_A + 2.6)))
        panel(mb, W, rect(u0, u1, SOC + 0.35, ARC_ZR), -0.05, 1.0, SV)
        panel(mb, W, rect(u2, u3, SOC + 0.35, ARC_ZR), -0.05, 0.7, OB)
        # capitel da ombreira (onde o arco nasce)
        panel(mb, W, rect(min(u0, u2) - 0.3, max(u1, u3) + 0.3, ARC_ZR - 1.0, ARC_ZR), -0.05, 1.3, OB)
        # uplight de energia no pe da ombreira (luminaria de obsidiana com o topo em neon violeta)
        ux = s * (ARC_A + 1.3)
        mb.box((3.0, 1.6, 0.5), _P(W, ux, 1.9, Z + 0.25), (0, 0, 0), OB, 0.0)
        mb.box((2.4, 1.0, 0.14), _P(W, ux, 1.9, Z + 0.55), (0, 0, 0), VG, 0.0)
    # medalhao: disco de obsidiana, contorno de energia (neon violeta) e aro de obsidiana
    C = (0.0, fy, EMB_Z)
    U, V, N = (1.0, 0.0, 0.0), (0.0, 0.0, 1.0), (0.0, -1.0, 0.0)
    R0 = EMB_R * 1.2
    disc(mb, C, U, V, N, R0, 0.3, 1.0, OB, 32)
    ring(mb, C, U, V, N, R0, R0 + 0.55, 0.3, 0.9, VG, 32)
    ring(mb, C, U, V, N, R0 + 0.55, R0 + 1.25, 0.3, 1.1, OB, 32)
    EM.emblem(mb, mb, mb, _P(W, 0.0, 1.0, EMB_Z), -math.pi / 2, EMB_R, depth=1.2, monumental=True)
    _fin(mb)
    light("L_SGCas_Emblem", "POINT", (0.0, fy - 9.0, Z + 30.0), 900.0, VIOLET, 1.0)


# ------------------------------------------------------------------ 4. torres da fachada + torrinhas de tras
def towers(banners):
    rng = random.Random(5501)
    mb = MB("SG_Cas_Torres", "04_CASTLE", rng, detail="near")
    CM = "Stone_SG_Castle"
    for x, y, r, top in L.FRONT_TOWERS:
        rot = 22.5
        ap = r * math.cos(math.pi / 8)
        s = 1 if x > 0 else -1
        # BASE: soco de obsidiana + cordao de prata / CORPO: pedra do castelo com faixas de obsidiana nos andares /
        # COROAMENTO: varanda com mata-caes de obsidiana, parapeito com remate violeta, agulha preto-violeta com aneis
        socle(mb, x, y, r, 8, ZB, Z + 3.4, rot, e=1.1)
        shaft(mb, x, y, r, 8, Z + 3.4, top, CM, rot)
        band(mb, x, y, r, 8, Z + 15.0, rot, h=1.0, e=0.4)
        band(mb, x, y, r, 8, top - 14.0, rot, h=1.2, e=0.5)
        parapet_ring(mb, x, y, r, 8, EAVE + 0.4, 1.9, OB, rot, merlons=False)      # varanda / mata-caes
        out_phi = 0.0 if s > 0 else 180.0
        # janelas: baixas e medias QUENTES (vida); ultimo andar em lancetas de energia violeta
        for phi in (out_phi, 270.0 + 45.0 * s, 90.0 - 45.0 * s):
            slit(mb, face_frame(x, y, ap, phi % 360.0), Z + 18.0, 3.4, 0.9)
        for phi in (270.0, out_phi, 270.0 + 45.0 * s, 90.0 - 45.0 * s):
            slit(mb, face_frame(x, y, ap, phi % 360.0), EAVE + 5.0, 3.6, 0.9)
        for phi in (270.0, out_phi, 90.0):
            Wf = face_frame(x, y, ap, phi)
            window(mb, Wf, 0.0, 1.3, top - 11.5, top - 5.6, 2.2, -0.02, 0.0, glass_m=VG, mullion=True,
                   fw=0.55, dp=0.35)
        parapet_ring(mb, x, y, r, 8, top, 2.6, OB, rot)
        spire(mb, x, y, r - 1.3, 8, top + 2.6, FT_SPIRE, "Roof_SG_Navy", rot, rings=(0.3, 0.62))
        mb.rod((x, y, top + FT_SPIRE + 2.4), (x, y, top + FT_SPIRE + 6.0), 0.26, SV, 6)
        mb.ico(0.6, (x, y, top + FT_SPIRE + 6.2), SV, 1)
        # lucarnas na agulha (4 faces, luz violeta) e pinaculos nos cantos do parapeito
        for k in range(4):
            phi = math.radians(90.0 * k)
            d = (r - 1.3) * 0.62
            lx, ly = x + d * math.cos(phi), y + d * math.sin(phi)
            lz = top + 2.6 + FT_SPIRE * 0.24
            mb.box((1.6, 2.2, 3.2), (lx, ly, lz + 1.6), (0, 0, phi), OB, 0.0)
            mb.box((0.25, 1.2, 1.8), (lx + 0.8 * math.cos(phi), ly + 0.8 * math.sin(phi), lz + 1.5), (0, 0, phi),
                   VG, 0.0)
            SL.spire(mb, (lx, ly), 1.25, lz + 3.2, 2.6, "Roof_SG_Navy", n=4)
        for k in range(4):
            a = math.radians(rot + 45.0 + 90.0 * k)
            px, py = x + (r + 0.4) * math.cos(a), y + (r + 0.4) * math.sin(a)
            mb.box((1.2, 1.2, 2.6), (px, py, top + 3.9), (0, 0, a), OB, 0.0)
            SL.spire(mb, (px, py), 0.9, top + 5.2, 7.0, "Roof_SG_Navy", n=4)
            mb.rod((px, py, top + 12.0), (px, py, top + 13.2), 0.1, SV, 4)
        # estandarte da ordem pendurado sob a varanda, na face que olha a praca; uplight de energia no pe
        W = face_frame(x, y, ap, 270.0)
        banners.append((_P(W, 0.0, 0.5, EAVE - 1.9), -math.pi / 2, 5.0, 19.0))
        mb.box((3.2, 1.6, 0.5), _P(W, 0.0, 2.2, Z + 0.25), (0, 0, 0), OB, 0.0)
        mb.box((2.6, 1.0, 0.14), _P(W, 0.0, 2.2, Z + 0.55), (0, 0, 0), VG, 0.0)
        ngon_col("SG_CasTower", x, y, 8, r, Z - 0.5, top, rot)
    for x, y, r in BACK_TURRETS:
        socle(mb, x, y, r, 8, ZB, Z + 3.0, 22.5, e=0.7)
        shaft(mb, x, y, r, 8, Z + 3.0, CLR_TOP + 4.0, CM, 22.5)
        band(mb, x, y, r, 8, EAVE - 1.0, 22.5, e=0.4)
        parapet_ring(mb, x, y, r, 8, CLR_TOP + 4.0, 1.8, OB, 22.5, merlons=False)
        spire(mb, x, y, r, 8, CLR_TOP + 5.8, 20.0, "Roof_SG_Navy", 22.5)
        mb.rod((x, y, CLR_TOP + 25.4), (x, y, CLR_TOP + 27.4), 0.16, SV, 6)
        for phi in (90.0, 0.0 if x > 0 else 180.0):
            slit(mb, face_frame(x, y, r * math.cos(math.pi / 8), phi), Z + 22.0, 3.2, 0.8)
            slit(mb, face_frame(x, y, r * math.cos(math.pi / 8), phi), EAVE + 6.0, 3.2, 0.8, m=VG)
        ngon_col("SG_CasTower", x, y, 8, r, Z - 0.5, EAVE, 22.5)
    mb.finish()


def standards(banners):
    """estandartes da ordem (sg_emblem.banner): roxo profundo, barra negra, bordas de prata, emblema; ritmo simetrico
    (2 nas torres do portao da muralha, 2 nas torres da fachada)"""
    mb = MB("SG_Cas_Estandartes", "04_CASTLE", random.Random(5801), detail="near")
    for top, yaw, w, h in banners:
        EM.banner(mb, mb, mb, mb, top, yaw, w, h)
    _fin(mb)


# ------------------------------------------------------------------ 5. torre-coroa (heroi)
def crown():
    rng = random.Random(5601)
    mb = MB("SG_Cas_Coroa", "04_CASTLE", rng, detail="near")
    CM = "Stone_SG_Castle"
    x, y, r, top = CR_X, CR_Y, CR_R, CR_TOP
    n = 12
    rot = 15.0
    ap = r * math.cos(math.pi / n)
    z1 = Z + 72.0                                          # 1o corpo ate ~124
    r2 = r - 1.6
    ap2 = r2 * math.cos(math.pi / n)
    socle(mb, x, y, r, n, ZB, Z + 4.0, rot, e=1.3)
    shaft(mb, x, y, r, n, Z + 4.0, z1, CM, rot)
    band(mb, x, y, r, n, EAVE - 1.0, rot, e=0.7)
    # contrafortes diagonais (4) com pinaculos no recuo; LINHA DE ENERGIA continua na face externa de cada um, que
    # segue pela aresta do 2o corpo ate as torrinhas da coroa
    for k in range(4):
        a = math.radians(45.0 + 90.0 * k)
        bx, by = x + (ap + 1.2) * math.cos(a), y + (ap + 1.2) * math.sin(a)
        mb.box((3.2, 3.0, z1 - ZB), (bx, by, (ZB + z1) / 2), (0, 0, a), CM, 0.0)
        mb.box((4.0, 3.8, Z + 4.0 - ZB), (bx, by, (ZB + Z + 4.0) / 2), (0, 0, a), OB, 0.0)
        mb.box((4.1, 3.9, 0.4), (bx, by, Z + 4.2), (0, 0, a), SV, 0.0)
        mb.box((2.2, 2.4, 8.0), (bx - 0.6 * math.cos(a), by - 0.6 * math.sin(a), z1 + 4.0), (0, 0, a), CM, 0.0)
        SL.spire(mb, (bx - 0.6 * math.cos(a), by - 0.6 * math.sin(a)), 1.6, z1 + 8.0, 10.0, "Roof_SG_Navy", n=4)
        ro = ap + 1.2 + 1.6 + 0.08
        mb.box((0.3, 0.36, z1 - Z - 6.0), (x + ro * math.cos(a), y + ro * math.sin(a), (Z + 5.0 + z1 - 1.0) / 2),
               (0, 0, a), VG, 0.0)
        col_box("SG_CasCrown", (3.2, 3.0, 20.0), (bx, by, Z + 9.5), (0, 0, a))
    # janelas altas do 1o corpo: energia violeta (faces visiveis: leste, oeste, norte e diagonais)
    for phi in (0.0, 30.0, 60.0, 90.0, 120.0, 150.0, 180.0):
        Wf = face_frame(x, y, ap, phi)
        window(mb, Wf, 0.0, 1.1, Z + 44.0, Z + 51.5, 1.9, -0.02, 0.0, glass_m=VG, mullion=False, fw=0.5, dp=0.3)
    frustum(mb, x, y, r + 0.9, r + 0.9, n, z1, z1 + 1.4, OB, rot)
    frustum(mb, x, y, r + 1.05, r + 1.05, n, z1 + 1.0, z1 + 1.4, VI, rot)
    # 2o corpo recuado: campanario com lancetas altas; faces alternadas em energia violeta (ritmo), o resto veneziana
    zc = top - 6.0
    shaft(mb, x, y, r2, n, z1 + 1.4, zc, CM, rot)
    for k in range(n):
        phi = (rot + 360.0 * k / n + 180.0 / n) % 360.0
        Wf = face_frame(x, y, ap2, phi)
        lit = int(round(phi)) % 60 == 30
        window(mb, Wf, 0.0, 1.5, z1 + 16.0, zc - 12.0, 2.6, -0.02, 0.0,
               glass_m=VG if lit else OB, mullion=True, fw=0.6, dp=0.4)
    band(mb, x, y, r2, n, z1 + 10.0, rot, h=1.0, e=0.5)
    glow_edges(mb, x, y, r2, n, z1 + 1.4, zc, rot, (1, 4, 7, 10))
    glow_edges(mb, x, y, r2 + 0.9, n, zc, top - 0.45, rot, (1, 4, 7, 10))
    # coroamento: mata-caes de obsidiana + parapeito ate o topo da alvenaria (178) com remate violeta
    parapet_ring(mb, x, y, r2, n, zc, top - zc, OB, rot, merlons=False)
    # coroa de agulhas: 4 torrinhas-pinaculo grandes nas diagonais (ponta de energia violeta) + 8 agulhas
    for k in range(n):
        a = math.radians(rot + 360.0 * k / n)
        if k % 3 == 1:                                        # vertices a 45, 135, 225, 315 graus
            rr = r2 - 0.6
            px, py = x + rr * math.cos(a), y + rr * math.sin(a)
            shaft(mb, px, py, 2.4, 8, top - 1.0, top + 11.0, CM, 22.5)
            frustum(mb, px, py, 2.9, 2.9, 8, top + 11.0, top + 12.2, OB, 22.5)
            frustum(mb, px, py, 3.05, 3.05, 8, top + 11.8, top + 12.2, VI, 22.5)
            spire(mb, px, py, 2.5, 8, top + 12.2, 17.0, "Roof_SG_Navy", 22.5, rings=(0.3, 0.62))
            mb.rod((px, py, top + 28.8), (px, py, top + 30.6), 0.16, SV, 6)
            SL.spire(mb, (px, py), 0.42, top + 30.4, 2.6, VG, n=4)
            slit(mb, face_frame(px, py, 2.4 * math.cos(math.pi / 8), math.degrees(a)), top + 3.0, 3.6, 0.8, m=VG)
            ro = 2.4 * math.cos(math.pi / 8) + 0.1
            mb.box((0.3, 0.3, 11.2), (px + ro * math.cos(a), py + ro * math.sin(a), top + 5.4), (0, 0, a), VG, 0.0)
        else:
            rr = r2 + 0.3
            px, py = x + rr * math.cos(a), y + rr * math.sin(a)
            shaft(mb, px, py, 1.3, 6, top, top + 5.0, OB, 0.0)
            SL.spire(mb, (px, py), 1.45, top + 5.0, 11.0, "Roof_SG_Navy", n=6)
            mb.rod((px, py, top + 15.6), (px, py, top + 17.0), 0.1, SV, 4)
    # flecha principal (sai direto do coroamento) com 4 lucarnas violeta e aneis de prata, ate CROWN_SPIRE_TOP;
    # no topo, o ponto mais alto da ilha: orbe de energia violeta sobre a haste de prata
    rs = 10.2
    sh = L.CROWN_SPIRE_TOP - 3.2 - top
    spire(mb, x, y, rs, n, top, sh, "Roof_SG_Navy", rot, flare=0.12, rings=(0.3, 0.55, 0.78))
    for phi in (0.0, 90.0, 180.0, 270.0):
        a = math.radians(phi)
        d = rs * 0.66
        lz = top + sh * 0.2
        lx, ly = x + d * math.cos(a), y + d * math.sin(a)
        mb.box((2.4, 2.8, 4.0), (lx, ly, lz + 2.0), (0, 0, a), OB, 0.0)
        mb.box((0.25, 1.4, 2.2), (lx + 1.2 * math.cos(a), ly + 1.2 * math.sin(a), lz + 1.9), (0, 0, a), VG, 0.0)
        SL.spire(mb, (lx, ly), 1.6, lz + 4.0, 3.2, "Roof_SG_Navy", n=4)
    mb.rod((x, y, top + sh - 0.4), (x, y, L.CROWN_SPIRE_TOP - 1.4), 0.3, SV, 6)
    mb.ico(0.9, (x, y, L.CROWN_SPIRE_TOP - 0.9), VG, 1)
    mb.box((0.3, 2.6, 0.3), (x, y, top + sh + 1.3), (0, 0, 0), SV, 0.0)
    mb.finish()
    ngon_col("SG_CasCrown", x, y, n, r, Z - 0.5, top, rot)


# ------------------------------------------------------------------ 6. alas (NAO entraveis: sem porta nenhuma)
def wings():
    rng = random.Random(5701)
    mb = MB("SG_Cas_Alas", "04_CASTLE", rng, detail="near")
    CM = "Stone_SG_Castle"
    # --- ala oeste sobre o terreno bravo: soco de pedra escura, corpo, telhado de ardosia ingreme, lucarnas
    x0, y0, x1, y1 = WW
    rect_frustum(mb, x0, y0, x1, y1, ZT, Z - 1.0, 3.2, 1.2, OB)
    mb.box2((x0, y0, Z - 1.0), (x1, y1, WW_EAVE), CM, 0.0)
    mb.box2((x0 - 0.6, y0 - 0.6, Z - 1.0), (x1 + 0.6, y1 + 0.6, SOC), OB, 0.0)
    mb.box2((x0 - 0.75, y0 - 0.75, SOC - 0.05), (x1 + 0.75, y1 + 0.75, SOC + 0.35), SV, 0.0)
    mb.box2((x0 - 0.4, y0 - 0.4, Z + 16.0), (x1 + 0.4, y1 + 0.4, Z + 17.0), OB, 0.0)
    mb.box2((x0 - 0.7, y0 - 0.7, WW_EAVE - 1.1), (x1 + 0.7, y1 + 0.7, WW_EAVE), OB, 0.0)
    cx = (x0 + x1) / 2
    w = x1 - x0
    rise = 20.0
    mb.gable_roof(cx, (y0 + y1) / 2, w, y1 - y0, WW_EAVE, rise, "Roof_SG_Navy", thick=0.8, over=1.4, axis="Y",
                  ridge_m=SV)
    for yy, sg in ((y0, -1), (y1, 1)):
        mb.gable_wall(cx, yy + sg * 0.4, w, WW_EAVE, rise, 0.8, "Y", CM)
    # janelas quentes (2 andares) nas 4 faces; nenhuma porta
    faces = [(((x1, 0.0), (0.0, 1.0), (1.0, 0.0)), y0 + 5.0, y1 - 5.0),
             (((x0, 0.0), (0.0, 1.0), (-1.0, 0.0)), y0 + 5.0, y1 - 5.0),
             (((0.0, y0), (1.0, 0.0), (0.0, -1.0)), x0 + 5.0, x1 - 5.0),
             (((0.0, y1), (1.0, 0.0), (0.0, 1.0)), x0 + 5.0, x1 - 5.0)]
    for fi, (W, u0, u1) in enumerate(faces):
        nwin = max(2, int((u1 - u0) / 9.0) + 1)
        for k in range(nwin):
            u = u0 + (u1 - u0) * k / (nwin - 1)
            for j, zz in enumerate((Z + 6.0, Z + 20.0)):
                lit = (k + j + fi) % 3 == 0                    # janelas quentes pontuais; o resto de venezianas
                window(mb, W, u, 1.0, zz, zz + 3.0, 1.4, 0.02, 0.0,
                       glass_m="Window_Warm" if lit else OB, mullion=False, fw=0.45, dp=0.3, sill=True)
    for yy in (y0 + 14.0, (y0 + y1) / 2, y1 - 14.0):
        dx0 = x1 - 1.0
        mb.box2((dx0 - 5.0, yy - 2.2, WW_EAVE + 0.5), (dx0, yy + 2.2, WW_EAVE + 6.0), CM, 0.0)
        mb.gable_roof(dx0 - 2.5, yy, 5.0, 4.4, WW_EAVE + 6.0, 3.0, "Roof_SG_Navy", thick=0.5, over=0.4, axis="X",
                      shingles=False, ridge_m="Roof_SG_Navy")
        mb.box((0.3, 1.5, 2.6), (dx0 + 0.05, yy, WW_EAVE + 3.4), (0, 0, 0), "Window_Warm", 0.0)
    col_box2("SG_CasWingW", (x0, y0, Z - 0.5), (x1, y1, WW_EAVE))
    # --- ala leste: corpo baixo no beco (deixa as janelas da nave livres acima), telhado de ardosia
    ex0, ey0, ex1, ey1 = EW
    mb.box2((ex0, ey0, ZB), (ex1, ey1, EW_EAVE), CM, 0.0)
    mb.box2((ex0, ey0 - 0.4, ZB), (ex1 + 0.6, ey1 + 0.4, SOC), OB, 0.0)
    mb.box2((ex0, ey0 - 0.55, SOC - 0.05), (ex1 + 0.75, ey1 + 0.55, SOC + 0.35), SV, 0.0)
    mb.box2((ex0, ey0 - 0.6, EW_EAVE - 1.0), (ex1 + 0.6, ey1 + 0.6, EW_EAVE), OB, 0.0)
    mb.gable_roof((ex0 + ex1) / 2, (ey0 + ey1) / 2, ex1 - ex0, ey1 - ey0, EW_EAVE, 5.0, "Roof_SG_Navy", thick=0.6,
                  over=0.8, axis="Y", ridge_m=SV)
    for yy in (ey0 + 0.3, ey1 - 0.3):
        mb.gable_wall((ex0 + ex1) / 2, yy, ex1 - ex0, EW_EAVE, 5.0, 0.6, "Y", CM)
    W = ((ex1, 0.0), (0.0, 1.0), (1.0, 0.0))
    for k in range(6):
        u = ey0 + 9.0 + k * (ey1 - ey0 - 18.0) / 5
        window(mb, W, u, 1.1, Z + 4.0, Z + 7.6, 1.5, 0.02, 0.0, glass_m="Window_Warm" if k % 2 == 0 else OB,
               mullion=False, fw=0.45, dp=0.3)
        mb.box((0.5, 1.4, 1.2), (ex1 + 0.3, u, EW_EAVE - 1.8), (0, 0, 0), OB, 0.0)
    col_box2("SG_CasWingE", (ex0 - 3.4, ey0, Z - 0.5), (ex1, ey1, EW_EAVE + 2.0))
    # --- torres das alas (agulhas escalonadas ate a coroa)
    for (tx, ty, tr, ttop, sph) in WING_TOWERS:
        socle(mb, tx, ty, tr, 8, ZT, SOC, 22.5, e=1.0)
        shaft(mb, tx, ty, tr, 8, SOC, ttop, CM, 22.5)
        band(mb, tx, ty, tr, 8, (Z + ttop) / 2, 22.5, h=1.0, e=0.45)
        parapet_ring(mb, tx, ty, tr, 8, ttop, 2.0, OB, 22.5, merlons=False)
        spire(mb, tx, ty, tr - 0.4, 8, ttop + 2.0, sph, "Roof_SG_Navy", 22.5)
        mb.rod((tx, ty, ttop + 2.0 + sph - 0.3), (tx, ty, ttop + 4.6 + sph), 0.2, SV, 6)
        apx = tr * math.cos(math.pi / 8)
        for phi in (0.0, 90.0, 180.0, 270.0):
            slit(mb, face_frame(tx, ty, apx, phi), ttop - 12.0, 3.4, 1.0)
        ngon_col("SG_CasWingTower", tx, ty, 8, tr, Z - 0.5, ttop, 22.5)
    mb.finish()


# ------------------------------------------------------------------ build
def build():
    banners = []
    muralha(banners)
    stairs()
    nave()
    roofs()
    facade(banners)
    towers(banners)
    crown()
    wings()
    standards(banners)
    light("L_SGCas_Gate", "POINT", (0.0, L.WALL_Y0 - 5.0, Z + 9.0), 600.0, WARM, 0.6)
    light("L_SGCas_EastGap", "POINT", (EG_X, L.WALL_Y0 - 4.0, Z + 7.0), 380.0, WARM, 0.5)
