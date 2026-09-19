# lv10_section.py - ETAPA C (REVISAO 3): trecho representativo do acesso a Forja do Ignis.
# Preserva a revisao 2 (pedra clara, ouro ornamental, azul em detalhe, torre esbelta, escada de 18,
# patamar circular com inlays) e corrige acabamento/integracao:
#  - fachada com mais profundidade (recessos maiores, molduras duplas, pilastras com base/capitel,
#    cornijas com denticulos+modilhoes, cordoes, peitoris, plinto), FORJA em painel emoldurado menor
#  - braseiros de parede (sem bolsao na circulacao), sem urnas no topo da escada; postes menores (0,8)
#  - piso: medalhao em plataforma baixa, inlays embutidos com lábio de ouro, faixa com folhas
#  - agua: tambor/saia do patamar fecha o lado interno (sem bloco ciano exposto), prateleira/ledge,
#    margem externa curva, pontes em arco ligando patamar e passeio, pedras, capim junto da agua
#  - ambiente: rochedos estratificados com grama/arvores, arvores redondas verdes + alamos v3, saia rochosa da ilha
# Coordenadas na orientacao do Roblox: Blender(+X,+Y,+Z) -> Roblox(-X,+Z,+Y). FRENTE dos edificios = +Y.
import bpy, bmesh, math, os, random, importlib, sys
from mathutils import Vector
sys.path.insert(0, r"C:\Users\lucas\OneDrive\Desktop\To up\lobby_area\blender")
import lvlib, lv10_kit, lv10_kit3
importlib.reload(lvlib); importlib.reload(lv10_kit); importlib.reload(lv10_kit3)
from lvlib import box, cyl, ball, lathe, torus, ngon_prism, ring_prism, reg_poly, coll, clear_collection, B, _xform, puff_cloud
K = lv10_kit
K3 = lv10_kit3
TAU = math.tau
EXPORT = r"C:\Users\lucas\OneDrive\Desktop\To up\lobby_area\export"

PLAZA, LAND, TERR = 2.0, 5.0, 10.0
WATER, BASIN = 0.6, -2.2
SKIRT = -3.4            # base das saias/paredes (abaixo do fundo da agua)
YF = -112.0
YW = YF - 14.0
YT0 = -104.0
YT1 = -90.0
R_LAND = 30.0
R_DRUM = 34.4           # raio externo do tambor do patamar (= lado interno dos espelhos)
TW, TD = 30.0, 26.0
H1, H2, H3 = 20.0, 32.0, 14.0
SW = 18.0
MED = (0.0, -68.0)

def arc_pts(cx, cy, r, a0, a1, n=32):
    return [(cx + math.cos(a0 + (a1 - a0) * i / n) * r, cy + math.sin(a0 + (a1 - a0) * i / n) * r) for i in range(n + 1)]

def pointed_panel(out, x, y0, y1, w, z, mat_in='LPS', frame='GLD', fw=.32, tip=None):
    """painel embutido: lapis ligeiramente rebaixado + labio de ouro saliente (le como incrustado)"""
    tip = tip or w * .9
    poly = [(x - w/2, y0 + tip), (x, y0), (x + w/2, y0 + tip), (x + w/2, y1 - tip), (x, y1), (x - w/2, y1 - tip)]
    poly_o = [(x - w/2 - fw, y0 + tip - fw * .4), (x, y0 - fw * 1.3), (x + w/2 + fw, y0 + tip - fw * .4),
              (x + w/2 + fw, y1 - tip + fw * .4), (x, y1 + fw * 1.3), (x - w/2 - fw, y1 - tip + fw * .4)]
    out.add(frame, ngon_prism(poly_o, .14, (0, 0, z - .06)))
    out.add(mat_in, ngon_prism(poly, .1, (0, 0, z - .08)))

def lozenge(out, x, y, a, L, w, z, mat_in='LPS', frame='GLD', fw=.28):
    c, s = math.cos(a), math.sin(a)
    def P(u, v): return (x + u * c - v * s, y + u * s + v * c)
    out.add(frame, ngon_prism([P(-L/2 - fw, 0), P(0, w/2 + fw), P(L/2 + fw, 0), P(0, -w/2 - fw)], .14, (0, 0, z - .06)))
    out.add(mat_in, ngon_prism([P(-L/2, 0), P(0, w/2), P(L/2, 0), P(0, -w/2)], .1, (0, 0, z - .08)))

# ================================================================ TORRE
def tower(out):
    yb = YF - TD
    # torres de canto octogonais com cordoes e coroa
    for sx in (-1, 1):
        for sy, yy in ((0, YF - .6), (1, yb + .6)):
            hT = H1 + 2.2 + H2 + 2.4 + 5.0
            pts = reg_poly(2.1, 8, TAU / 16)
            out.add('SLT', ngon_prism([(sx * 15.0 + px, yy + py) for px, py in pts], hT, (0, 0, TERR)))
            out.add('SLT', ngon_prism([(sx * 15.0 + px, yy + py) for px, py in reg_poly(2.6, 8, TAU / 16)], 1.4, (0, 0, TERR)))   # plinto
            for zz in (TERR + 9.0, TERR + H1 + 1.2, TERR + H1 + 2.2 + 12.0, TERR + H1 + 2.2 + H2 + 1.4):
                out.add('SLT', ngon_prism([(sx * 15.0 + px, yy + py) for px, py in reg_poly(2.5, 8, TAU / 16)], .7, (0, 0, zz)))
                out.add('GLD', ngon_prism([(sx * 15.0 + px, yy + py) for px, py in reg_poly(2.55, 8, TAU / 16)], .12, (0, 0, zz + .7)))
            # seteiras estreitas
            for zz in (TERR + 14, TERR + 34):
                out.add('SLT', box((.9, .5, 3.0), (sx * 15.0, yy + 2.15, zz), bevel=.04)); out.add('DRK', box((.4, .3, 2.2), (sx * 15.0, yy + 2.3, zz)))
            out.add('SLT', lathe([(2.5, 0), (2.2, .5), (.05, 6.5)], (sx * 15.0, yy, TERR + hT), seg=8))
            out.add('GLD', lathe([(.5, 0), (.03, 1.8)], (sx * 15.0, yy, TERR + hT + 6.4), seg=6))
    # ---------- tier 1 ----------
    f1 = YF
    AD = 8.0
    K.arch_opening(out, (0, f1, TERR), 14, H1, 10, 9.5, 15.5, 2.2, mat='SMD')
    for s in (-1, 1):
        K.arch_opening(out, (s * 11, f1, TERR), 8, H1, 3.6, 6.0, 7.8, 3.0, mat='SMD', back='FRG', back_depth=3.2, pointed=False)
        K.arch_molding(out, (s * 11, f1 + .22, TERR), 3.6, 6.0, 7.8, r=.34, mat='SLT', pointed=False, double=True)
        out.add('GLD', box((.2, .24, 6.0), (s * 11, f1 - 2.0, TERR + 3.0)))
        out.add('GLD', box((3.0, .24, .2), (s * 11, f1 - 2.0, TERR + 4.2)))
        out.add('SLT', box((4.8, 1.0, .5), (s * 11, f1 + .3, TERR + 5.75), bevel=.06))        # peitoril
    K.arch_molding(out, (0, f1 + .38, TERR), 10, 9.5, 15.5, r=.62, mat='SLT', double=True)
    K.arch_molding(out, (0, f1 - 1.6, TERR), 8.6, 9.2, 14.8, r=.34, mat='SLT', gold=True)
    out.add('GLD', torus(1.0, .13, (0, f1 + .3, TERR + 17.0), (math.pi / 2, 0, 0), seg=14, sides=6))
    for s in (-1, 1):
        out.add('GLD', torus(.62, .11, (s * 1.4, f1 + .3, TERR + 16.1), (math.pi / 2, 0, 0), seg=12, sides=6))
    for x in (-7.0, 7.0):
        K.pilaster(out, (x, f1 + .7, TERR), 1.6, 1.4, H1)
    K3.string_course(out, -13.0, 13.0, f1, TERR + 1.0, h=1.2, d=.55)                          # plinto
    yb0 = f1 - 3.6
    for s in (-1, 1):
        out.add('SMD', box((9.6, yb0 - yb, H1), (s * 10.2, (yb0 + yb) / 2, TERR + H1 / 2)))
    yb1 = f1 - AD - .6
    out.add('SMD', box((TW, yb1 - yb, H1), (0, (yb1 + yb) / 2, TERR + H1 / 2)))
    # alcova
    out.add('FLL', box((10.6, AD + .4, .4), (0, f1 - AD / 2, TERR - .2)))
    out.add('SLT', box((.8, AD, 18), (-5.2, f1 - AD / 2, TERR + 9)))
    out.add('SLT', box((.8, AD, 18), (5.2, f1 - AD / 2, TERR + 9)))
    out.add('SLT', box((12, AD, 1.4), (0, f1 - AD / 2, TERR + 17.6)))
    out.add('DRK', box((12, .8, 19), (0, f1 - AD - .2, TERR + 9.2)))
    out.add('SLT', box((7.2, 1.6, .8), (0, f1 - AD + 1.0, TERR + 7.6), bevel=.1))
    out.add('SLT', ngon_prism([(-3.6, 0), (3.6, 0), (2.4, 2.0), (-2.4, 2.0)], 1.4, (0, f1 - AD + 1.7, TERR + 8.0), (math.pi / 2, 0, 0)))
    out.add('SMD', torus(3.1, .7, (0, f1 - AD + .6, TERR + 2.8), (math.pi / 2, 0, 0), seg=16, sides=8, arc=math.pi))
    out.add('EMB', torus(2.6, .4, (0, f1 - AD + .5, TERR + 2.8), (math.pi / 2, 0, 0), seg=16, sides=6, arc=math.pi))
    out.add('EMB', box((5.2, .5, 3.0), (0, f1 - AD + .55, TERR + 1.5)))
    out.add('DRK', box((6.4, .3, 4.2), (0, f1 - AD + .9, TERR + 2.1)))
    # braseiros de PAREDE (nao ocupam o piso)
    for s in (-1, 1):
        K3.sconce(out, (s * 9.4, f1 + .5, TERR + 6.4), s=.9)
    # cornija 1 + painel emoldurado do letreiro (menor, integrado)
    K.cornice(out, (0, f1, TERR + H1), TW + 1.6, 3.2, h=2.2)
    zp = TERR + H1 + 2.2
    out.add('SLT', box((14.0, 1.4, 3.4), (0, f1 - .1, zp + 1.7)))                                # painel
    out.add('SLT', box((14.6, .5, .5), (0, f1 + .6, zp + .25), bevel=.06))                       # moldura inferior
    out.add('SLT', box((14.6, .5, .5), (0, f1 + .6, zp + 3.4 - .25), bevel=.06))                 # moldura superior
    for s in (-1, 1):
        out.add('SLT', box((.5, .5, 3.4), (s * 7.05, f1 + .6, zp + 1.7), bevel=.06))
    out.add('GLD', box((13.4, .1, .08), (0, f1 + .86, zp + .55)))
    out.add('GLD', box((13.4, .1, .08), (0, f1 + .86, zp + 2.85)))
    K.gold_text(out, 'FORJA', (0, f1 + .95, zp + .95), size=3.4, depth=.6)
    for s in (-1, 1):
        out.add('SLT', box((2.2, 2.4, 3.4), (s * (TW / 2 - 3.0), f1 - .4, zp + 1.7), bevel=.12))
        out.add('GLD', ball(.42, (s * (TW / 2 - 3.0), f1 - .4, zp + 3.75), seg=8))
    # ---------- tier 2 ----------
    z2 = zp
    f2 = YF - 1.0
    W2 = TW - 2.0
    K.arch_opening(out, (0, f2, z2), 14, H2, 9, 13, 24, 3.4, mat='SMD', back='FRG', back_depth=3.6)
    for s in (-1, 1):
        K.arch_opening(out, (s * 10.5, f2, z2), 7, H2, 4.2, 12, 19, 3.4, mat='SMD', back='DRK', back_depth=3.6)
        K.arch_molding(out, (s * 10.5, f2 + .22, z2), 4.2, 12, 19, r=.34, mat='SLT', double=True)
        out.add('GLD', box((.2, .22, 11), (s * 10.5, f2 - 2.4, z2 + 5.5)))
        out.add('SLT', box((5.2, 1.0, .5), (s * 10.5, f2 + .3, z2 + 11.75), bevel=.06))       # peitoril
    K.arch_molding(out, (0, f2 + .3, z2), 9, 13, 24, r=.5, mat='SLT', double=True)
    out.add('SLT', box((10.4, 1.1, .6), (0, f2 + .35, z2 + 12.7), bevel=.06))                    # peitoril do vitral
    for x in (-3.0, -1.5, 0, 1.5, 3.0):
        out.add('GLD', box((.18, .22, 15), (x, f2 - 2.5, z2 + 7.5)))
    for zz in (z2 + 6.0, z2 + 11.0):
        out.add('GLD', box((8.0, .22, .18), (0, f2 - 2.5, zz)))
    out.add('GLD', torus(2.0, .16, (0, f2 - 2.5, z2 + 18.2), (math.pi / 2, 0, 0), seg=18, sides=6))
    out.add('GLD', torus(.9, .12, (0, f2 - 2.5, z2 + 21.3), (math.pi / 2, 0, 0), seg=12, sides=6))
    for x in (-7.0, 7.0):
        K.pilaster(out, (x, f2 + .65, z2), 1.5, 1.3, H2)
    K3.string_course(out, -13.5, 13.5, f2, z2 + 11.2, h=.55, d=.5, gold=True)                 # cordao ao nivel dos peitoris
    K3.string_course(out, -13.5, 13.5, f2, z2 + .2, h=.9, d=.45)
    yb2 = f2 - 4.3
    out.add('SMD', box((W2, yb2 - yb, H2), (0, (yb2 + yb) / 2, z2 + H2 / 2)))
    K.cornice(out, (0, f2, z2 + H2), W2 + 2.0, 3.2, h=2.4)
    K.balustrade(out, (-W2 / 2 + 2.6, f2 + .4), (W2 / 2 - 2.6, f2 + .4), z2 + H2 + 2.4, h=2.4)
    # ---------- tier 3 ----------
    z3 = z2 + H2 + 2.4
    f3 = YF - 3.0
    W3 = TW - 6.0
    for x in (-7.0, 0.0, 7.0):
        K.arch_opening(out, (x, f3, z3), 7.0, H3, 3.6, 8.0, 9.8, 2.4, mat='SMD', back='DRK', back_depth=2.6, pointed=False)
        K.arch_molding(out, (x, f3 + .2, z3), 3.6, 8.0, 9.8, r=.3, mat='SLT', pointed=False, gold=True, double=True)
        out.add('SLT', box((4.6, .9, .45), (x, f3 + .25, z3 + 7.8), bevel=.05))
    for x in (-10.5, -3.5, 3.5, 10.5):
        K.pilaster(out, (x, f3 + .6, z3), 1.3, 1.2, H3)
    K3.string_course(out, -12.0, 12.0, f3, z3 + .2, h=.8, d=.4)
    yb3 = f3 - 3.4
    out.add('SMD', box((W3, yb3 - (yb + 3.0), H3), (0, (yb3 + yb + 3.0) / 2, z3 + H3 / 2)))
    K.cornice(out, (0, f3, z3 + H3), W3 + 2.0, 3.0, h=2.4)
    # ---------- tambor + cupula + agulha ----------
    zd = z3 + H3 + 2.4
    yd = YF - TD / 2
    out.add('SLT', ngon_prism(reg_poly(11.5, 8, TAU / 16), 3.6, (0, yd, zd)))
    for i in range(8):
        a = i / 8 * TAU
        out.add('DRK', box((1.6, .4, 2.2), (math.cos(a) * 11.4, yd + math.sin(a) * 11.4, zd + 1.9), (0, 0, a + math.pi / 2)))
        out.add('SLT', box((1.4, 1.4, 3.6), (math.cos(a + TAU / 16) * 11.2, yd + math.sin(a + TAU / 16) * 11.2, zd + 1.8), (0, 0, a + TAU / 16), bevel=.08))
    out.add('GLD', ngon_prism(reg_poly(11.9, 8, TAU / 16), .4, (0, yd, zd + 3.6)))
    out.add('SLT', ngon_prism(reg_poly(12.2, 8, TAU / 16), .6, (0, yd, zd + 4.0)))
    prof = [(math.cos(t / 7 * math.pi / 2) * 11.0, math.sin(t / 7 * math.pi / 2) * 8.6) for t in range(8)]
    out.add('GLS', lathe(prof, (0, yd, zd + 4.6), seg=24))
    for i in range(8):
        a = i / 8 * TAU + TAU / 16
        bm = bmesh.new(); prev = None
        for k in range(8):
            t = k / 7
            rr = math.cos(t * math.pi / 2) * 11.2; zz = math.sin(t * math.pi / 2) * 8.6
            px, py = math.cos(a) * rr, math.sin(a) * rr
            v1 = bm.verts.new((px - math.sin(a) * .34, py + math.cos(a) * .34, zz))
            v2 = bm.verts.new((px + math.sin(a) * .34, py - math.cos(a) * .34, zz))
            v3 = bm.verts.new((px * 1.03, py * 1.03, zz + .28))
            if prev:
                bm.faces.new([prev[0], v1, v3, prev[2]]); bm.faces.new([prev[2], v3, v2, prev[1]])
            prev = (v1, v2, v3)
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        _xform(bm, (0, yd, zd + 4.6))
        out.add('GLD', bm)
    out.add('GLD', lathe([(1.4, 0), (1.6, .5), (.5, 1.0), (.55, 1.6), (.03, 8.0)], (0, yd, zd + 13.0), seg=12))
    out.add('GLD', ball(.55, (0, yd, zd + 17.5), seg=8))

# ================================================================ ALAS
def wings(out):
    fw = YW
    WH = 13.0
    for s in (-1, 1):
        x_in, x_out = s * 15.0, s * 40.0
        xc = (x_in + x_out) / 2
        WW = abs(x_out - x_in)
        yb = fw - 18.0
        for k in (-1, 1):
            xa = xc + k * 6.0
            K.arch_opening(out, (xa, fw, TERR), 12, WH, 5.0, 7.5, 10.0, 2.8, mat='SMD', back='FRG', back_depth=3.0, pointed=False)
            K.arch_molding(out, (xa, fw + .24, TERR), 5.0, 7.5, 10.0, r=.4, mat='SLT', pointed=False, double=True)
            out.add('GLD', box((.24, .24, 7.5), (xa, fw - 1.9, TERR + 3.75)))
            out.add('GLD', box((4.6, .24, .24), (xa, fw - 1.9, TERR + 5.2)))
            out.add('SLT', box((6.2, 1.0, .5), (xa, fw + .3, TERR + 7.25), bevel=.06))
        out.add('SMD', box((1.0, 2.8, WH), (xc, fw - 1.4, TERR + WH / 2)))
        for x in (xc - 12.0, xc, xc + 12.0):
            K.pilaster(out, (x, fw + .65, TERR), 1.6, 1.3, WH)
        K3.string_course(out, min(x_in, x_out) + .5, max(x_in, x_out) - .5, fw, TERR + 1.0, h=1.2, d=.55)
        wb = fw - 3.4
        out.add('SMD', box((WW, wb - yb, WH), (xc, (wb + yb) / 2, TERR + WH / 2)))
        K.cornice(out, (xc, fw, TERR + WH), WW + 1.4, 3.0, h=2.2)
        out.add('SLA', box((WW + .2, fw - yb - 2.0, .5), (xc, (fw + yb) / 2 - 1.0, TERR + WH + 2.2 + .1)))
        K.balustrade(out, (x_in + 1.0, fw + .3), (x_out - 1.0, fw + .3), TERR + WH + 2.2, h=2.4)
        cx, cy = s * 43.0, fw - 4.0
        HT = 22.0
        out.add('SMD', cyl(3.6, HT, (cx, cy, TERR), seg=18))
        out.add('SLT', cyl(4.0, 1.4, (cx, cy, TERR), seg=18))
        for zz in (TERR + 7.0, TERR + WH + 1.0, TERR + HT - 1.2):
            out.add('SLT', torus(3.7, .4, (cx, cy, zz), seg=18, sides=6))
        out.add('GLD', torus(3.75, .14, (cx, cy, TERR + HT - .6), seg=18, sides=5))
        out.add('SLT', cyl(4.1, .7, (cx, cy, TERR + HT), seg=18))
        out.add('GLS', lathe([(3.9, 0), (3.4, 1.6), (2.0, 3.2), (.6, 4.2), (.03, 4.7)], (cx, cy, TERR + HT + .7), seg=18))
        out.add('GLD', lathe([(.42, 0), (.03, 2.0)], (cx, cy, TERR + HT + 5.3), seg=6))
        for zz in (TERR + 5, TERR + 12, TERR + 18):
            out.add('SLT', box((1.1, .6, 2.8), (cx, cy + 3.6, zz), bevel=.05))
            out.add('DRK', box((.5, .4, 2.0), (cx, cy + 3.8, zz)))

# ================================================================ TERRACO, ESCADA, PATAMAR, INLAYS
def terrace_and_stairs(out):
    XT = 46.0
    out.add('FLL', box((2 * XT, YT0 - YW, .6), (0, (YT0 + YW) / 2, TERR - .3)))
    out.add('ASH', box((2 * XT, YT0 - YW, TERR - SKIRT - .6), (0, (YT0 + YW) / 2, SKIRT + (TERR - SKIRT - .6) / 2)))   # bloco do terraco ate abaixo da agua
    for s in (-1, 1):
        x0, x1 = SW / 2 + 1.8, XT
        xm = s * (x0 + x1) / 2
        out.add('SLT', box((x1 - x0, 1.6, .7), (xm, YT0 - .3, TERR + .1), bevel=.1))
        out.add('SLT', box((x1 - x0, .6, .8), (xm, YT0 + .3, TERR - 1.4), bevel=.06))          # cordao do muro de arrimo
        K.balustrade(out, (s * x0, YT0 - .7), (s * x1, YT0 - .7), TERR + .45, h=2.4)
    for s in (-1, 1):
        out.add('FLF', box((22, 16, .1), (s * 30, YW + 10, TERR + .02)))
    # escada 18 com beirais; bochechas inclinadas com coping e filete central fino
    n = 10
    rise = (TERR - LAND) / n
    run = (YT1 - YT0) / n
    for i in range(n):
        yy = YT1 - (i + .5) * run
        zz = LAND + i * rise
        out.add('FLL', box((SW, run + .1, rise), (0, yy, zz + rise / 2)))
        out.add('SLT', box((SW, .34, .18), (0, yy + run / 2 - .05, zz + rise - .09)))
    out.add('GLD', box((SW, .16, .05), (0, YT0 + .15, TERR + .03)))
    for s in (-1, 1):
        xc = s * (SW / 2 + .9)
        prof = [(YT1 + .6, LAND - .2), (YT0 - .8, LAND - .2), (YT0 - .8, TERR + 1.3), (YT1 + .6, LAND + 1.3)]
        bm = ngon_prism(prof, 1.8, (0, 0, 0))
        _xform(bm, (0, 0, 0), (math.pi / 2, 0, math.pi / 2)); _xform(bm, (xc - .9, 0, 0))
        out.add('SLT', bm)
        Lc = math.hypot(YT1 - YT0, TERR - LAND) + 1.6
        ang = math.atan2(TERR - LAND, YT0 - YT1)
        out.add('SLT', box((2.3, Lc, .5), (xc, (YT0 + YT1) / 2 - .1, (LAND + TERR) / 2 + 1.55), (ang, 0, 0), bevel=.1))
        out.add('GLD', box((.4, Lc - .6, .06), (xc, (YT0 + YT1) / 2 - .1, (LAND + TERR) / 2 + 1.84), (ang, 0, 0)))
        # pe da escada: pedestal baixo + poste MENOR (0.8); topo: sem urna (circulacao livre)
        K.pedestal(out, (s * (SW / 2 + 1.7), YT1 + 2.4, LAND), w=2.6, h=1.2)
        K.lamp_post(out, (s * (SW / 2 + 1.7), YT1 + 2.4, LAND + 1.2), scale=.8)
        K.pampas(out, (s * (SW / 2 + 3.4), YT1 + .4, LAND), h=2.0, seed=21 + s)
        K3.string_course(out, s * (SW / 2 + 1.8), s * 5.0, YT0 - .1, TERR - .05, h=.3, d=1.2)   # arremate do topo da escada
    # ---- patamar + tambor (saia ate abaixo da agua) + aneis ----
    half = arc_pts(0, YT1, R_LAND, 0, math.pi)
    out.add('FLL', ngon_prism(half + [(-R_LAND, YT1 - 14), (R_LAND, YT1 - 14)], LAND - PLAZA, (0, 0, PLAZA)))
    out.add('ASH', ngon_prism(arc_pts(0, YT1, R_DRUM, 0, math.pi) + [(-R_DRUM, YT1 - 14), (R_DRUM, YT1 - 14)], PLAZA - SKIRT, (0, 0, SKIRT)))   # TAMBOR: fecha o lado interno dos espelhos
    out.add('FLF', ring_prism(arc_pts(0, YT1, R_LAND - .3, 0, math.pi), arc_pts(0, YT1, R_LAND - 6.0, 0, math.pi), .08, (0, 0, LAND)))
    K.coping_arc(out, 0, YT1, R_LAND + .6, LAND - 1.0, 0, math.pi, w=1.4, h=1.0, gold=False)
    r2 = R_LAND + 3.2
    out.add('FLL', ring_prism(arc_pts(0, YT1, r2 + .6, 0, math.pi), arc_pts(0, YT1, R_LAND - .2, 0, math.pi), LAND - 1.5 - PLAZA, (0, 0, PLAZA)))
    K.coping_arc(out, 0, YT1, r2 + .6, LAND - 2.5, 0, math.pi, w=1.4, h=1.0, gold=True)
    # ledge baixo (nivel PLAZA) entre o anel e o tambor: margem de agua com capim
    out.add('FLR', ring_prism(arc_pts(0, YT1, R_DRUM, 0, math.pi), arc_pts(0, YT1, r2 + .5, 0, math.pi), .4, (0, 0, PLAZA - .4)))
    out.add('SLT', ring_prism(arc_pts(0, YT1, R_DRUM + .1, 0, math.pi), arc_pts(0, YT1, R_DRUM - .7, 0, math.pi), .35, (0, 0, PLAZA)))   # bordo com espessura
    for a in (math.radians(25), math.radians(62), math.radians(118), math.radians(155)):
        K.pampas(out, (math.cos(a) * (R_DRUM - 1.6), YT1 + math.sin(a) * (R_DRUM - 1.6), PLAZA), h=2.2, seed=int(a * 10))
    # ---- inlays (embutidos) + plataforma baixa do medalhao ----
    cx, cy = MED
    out.add('SLT', ring_prism(reg_poly(9.2, 32), reg_poly(8.6, 32), .18, (cx, cy, LAND)))          # bordo da plataforma
    out.add('FLL', cyl(8.65, .16, (cx, cy, LAND), seg=32))
    zt = LAND + .16
    out.add('GLD', ring_prism(reg_poly(6.0, 32), reg_poly(5.4, 32), .12, (cx, cy, zt - .04)))
    out.add('LPS', ring_prism(reg_poly(5.4, 32), reg_poly(4.3, 32), .1, (cx, cy, zt - .06)))
    out.add('GLD', ring_prism(reg_poly(4.3, 32), reg_poly(3.95, 32), .12, (cx, cy, zt - .04)))
    star = []
    for i in range(16):
        a = i / 16 * TAU + TAU / 32
        rr = 3.7 if i % 2 == 0 else 1.7
        star.append((cx + math.cos(a) * rr, cy + math.sin(a) * rr))
    out.add('LPS', ngon_prism(star, .1, (0, 0, zt - .06)))
    out.add('GLD', ngon_prism([(cx + (x - cx) * .8, cy + (y - cy) * .8) for x, y in star], .13, (0, 0, zt - .05)))
    out.add('GLD', cyl(.6, .14, (cx, cy, zt - .04), seg=12))
    for (ro, ri, m) in ((22.6, 22.1, 'GLD'), (22.1, 21.2, 'LPS'), (21.2, 20.9, 'GLD')):
        out.add(m, ring_prism(arc_pts(0, YT1, ro, 0, math.pi) + [(-ro, YT1 - .01)], arc_pts(0, YT1, ri, 0, math.pi) + [(-ri, YT1 - .01)], .12 if m == 'GLD' else .1, (0, 0, LAND - (.05 if m == 'GLD' else .07))))
    pointed_panel(out, 0, YT1 + 1.0, cy - 9.6, 2.4, LAND + .02)
    for a in (math.radians(35), math.radians(70), math.radians(110), math.radians(145)):
        lozenge(out, math.cos(a) * 14.5, YT1 + math.sin(a) * 14.5, a, 5.0, 1.8, LAND + .02)
    for a in (math.radians(20), math.radians(160)):
        lozenge(out, math.cos(a) * 26.5, YT1 + math.sin(a) * 26.5, a + math.pi / 2, 4.0, 1.4, LAND + .02)
    # postes do anel (0.8) + capim
    for s in (-1, 1):
        px, py = s * 21.0, YT1 + 19.0
        K.pedestal(out, (px, py, LAND), w=2.4, h=.9)
        K.lamp_post(out, (px, py, LAND + .9), scale=.8)
        K.pampas(out, (px + s * 2.4, py + 1.2, LAND), h=2.0, seed=31 + s)
    # canteiros baixos do anel (assimetricos): arvore redonda florida x arbusto + capim
    for (px, py, rr, seed, big) in ((-13.0, YT1 + 26.0, 3.2, 41, True), (13.5, YT1 + 25.5, 2.6, 43, False)):
        pts = reg_poly(rr, 8, TAU / 16)
        out.add('SLT', ring_prism([(px + x, py + y) for x, y in reg_poly(rr + .6, 8, TAU / 16)], [(px + x, py + y) for x, y in pts], .9, (0, 0, LAND)))
        out.add('GRS', ngon_prism([(px + x, py + y) for x, y in pts], .7, (0, 0, LAND)))
        if big:
            K3.round_tree(out, (px, py, LAND + .7), h=7.5, r=2.6, seed=seed, flowers='FLW')
            K.ground_cover(out, (px + 1.5, py - 1.5, LAND + .7), r=1.2, seed=seed + 2)
        else:
            K.bush(out, (px, py, LAND + .7), r=1.4, seed=seed, mat='LFV', flowers='FLW', n_fl=8)
            K.pampas(out, (px + 1.2, py - 1.0, LAND + .7), h=1.8, seed=seed + 1)
    n2 = 6
    for i in range(n2):
        r = (LAND - PLAZA) / n2
        out.add('FLL', box((12, 1.3, r), (0, YT1 + R_LAND + .6 + (i + .5) * 1.2, LAND - (i + 1) * r + r / 2)))
    # ---- canteiros do terraco: alamos v3 variados + arvore redonda + capim + cobertura ----
    for (s, seeds, hs, dens) in ((-1, (3, 4), (31, 23), (1.0, .8)), (1, (5, 6), (27, 20), (.9, 1.0))):
        cxp, cyp = s * 24.0, YW + 8.0
        pts = reg_poly(5.6, 8, TAU / 16)
        out.add('SLT', ring_prism([(cxp + x, cyp + y) for x, y in reg_poly(6.2, 8, TAU / 16)], [(cxp + x, cyp + y) for x, y in pts], 1.1, (0, 0, TERR)))
        out.add('SLT', ring_prism([(cxp + x, cyp + y) for x, y in reg_poly(6.8, 8, TAU / 16)], [(cxp + x, cyp + y) for x, y in reg_poly(6.2, 8, TAU / 16)], .5, (0, 0, TERR)))
        out.add('GRS', ngon_prism([(cxp + x, cyp + y) for x, y in pts], .9, (0, 0, TERR)))
        K3.poplar3(out, (cxp - s * 1.6, cyp + 1.2, TERR + .9), h=hs[0], r=3.1, seed=seeds[0], density=dens[0] * 1.15)
        K3.poplar3(out, (cxp + s * 2.2, cyp - 2.4, TERR + .9), h=hs[1], r=2.7, seed=seeds[1], density=dens[1] * 1.15)
        K.bush(out, (cxp + s * 2.4, cyp + 2.8, TERR + .9), r=1.4, seed=seeds[0] + 10, mat='LFG', flowers=None)
        K.pampas(out, (cxp - s * 3.0, cyp - 1.6, TERR + .9), h=2.6, seed=seeds[1] + 10)
        K.ground_cover(out, (cxp + s * 8.0, cyp + 4.0, TERR), r=2.4, seed=seeds[0] + 20)
        K.ground_cover(out, (cxp - s * 7.5, cyp + 5.5, TERR), r=1.6, seed=seeds[0] + 22)
        if s == -1:
            K3.poplar3(out, (cxp - 9.0, cyp - 3.0, TERR), h=25, r=2.2, seed=8, density=.7)
        else:
            K3.round_tree(out, (cxp + 8.5, cyp - 2.0, TERR), h=9.5, r=3.2, seed=9)
            K.bush(out, (cxp + 11.5, cyp + 3.0, TERR), r=1.3, seed=12, mat='LFV', flowers='FLW')

# ================================================================ AGUA, PONTES, ROCHAS, LIMITE
def water_and_rocks(out):
    for s in (-1, 1):
        x0, x1 = 34.0, 64.0
        y0, y1 = YT0, YT1 + R_LAND + 4.0       # -104 .. -56
        xc = s * (x0 + x1) / 2
        ccx, ccy = s * 20.0, -80.0
        a0 = math.atan2(y0 - ccy, s * 40.0); a1 = math.atan2(y1 - ccy, s * 40.0)
        if s < 0 and a0 < 0: a0 += TAU
        def A(r): return arc_pts(ccx, ccy, r, a0, a1, 24)
        # fundo com profundidade variavel + prateleiras rasas (fecha ate a saia)
        out.add('RCK', box((x1 - x0 + 2, y1 - y0 + 2, .6), (xc, (y0 + y1) / 2, BASIN - .3)))
        out.add('RCK', box((x1 - x0, 3.0, WATER - .5 - BASIN), (xc, y1 - 1.5, BASIN + (WATER - .5 - BASIN) / 2)))
        out.add('RCK', box((3.5, y1 - y0, WATER - .4 - BASIN), (s * (x1 - 3.0), (y0 + y1) / 2, BASIN + (WATER - .4 - BASIN) / 2)))
        # muro externo curvo (da saia ao passeio) + coping + balaustrada + passeio
        wall_in, wall_out = A(43.2), A(44.6)
        out.add('ASH', ring_prism(wall_out, wall_in, PLAZA - SKIRT + .1, (0, 0, SKIRT)))
        out.add('SLT', ring_prism(A(45.0), A(43.0), .5, (0, 0, PLAZA)))
        # PONTE em arco: do anel do patamar ate o PASSEIO externo (pousa sobre o muro), abrindo a balaustrada
        ang_b = math.radians(28)
        yb_ = YT1 + math.sin(ang_b) * (R_DRUM - .8)                 # z da ponte (-74.2)
        xw = ccx + math.sqrt(44.6 ** 2 - (yb_ - ccy) ** 2) * s       # x do muro externo nesse z
        pb0 = (s * math.cos(ang_b) * (R_DRUM - .8), yb_)
        pb1 = (xw + s * 1.6, yb_)
        K3.footbridge(out, pb0, pb1, PLAZA + 1.3, rise=2.0, W=4.4)
        for i in range(0, 24, 3):
            p1, p2 = wall_out[i], wall_out[min(i + 3, 24)]
            if abs((p1[1] + p2[1]) / 2 - yb_) < 4.2:
                continue                                              # vao da ponte
            K.balustrade(out, p1, p2, PLAZA + .5, h=2.4)
        # degrau de acesso do passeio a cabeceira da ponte
        out.add('SLT', box((3.0, 6.0, .65), (xw + s * 3.6, yb_, PLAZA + .32), bevel=.06))
        walk = wall_out + [(s * 78.0, y1), (s * 78.0, y0)]
        out.add('FLR', ngon_prism(walk, .5, (0, 0, PLAZA - .5)))
        out.add('ASH', ngon_prism(walk, PLAZA - .5 - SKIRT, (0, 0, SKIRT)))                      # saia sob o passeio
        # parede sul (reta) + coping
        out.add('ASH', box((x1 - x0 + 2, 1.2, PLAZA - SKIRT + .1), (xc, y1 + .6, SKIRT + (PLAZA - SKIRT + .1) / 2)))
        out.add('SLT', box((x1 - x0 + 2.6, 1.8, .5), (xc, y1 + .6, PLAZA + .25), bevel=.1))
        # pedras: submersas e emergindo perto das margens
        rnd = random.Random(int(31 + s))
        for k in range(6):
            rx = s * (x0 + 6 + rnd.random() * (x1 - x0 - 12)); ry = y0 + 6 + rnd.random() * (y1 - y0 - 12)
            K.rock(out, (rx, ry, BASIN + .3 + rnd.random() * 1.0), r=1.0 + rnd.random() * 1.2, seed=40 + k + int(s))
        K.rock(out, (s * (x0 + 4), y1 - 7, WATER - .35), r=1.6, seed=50 + int(s))
        K.rock(out, (s * (x1 - 7), y0 + 8, WATER - .55), r=1.3, seed=52 + int(s))
        K.rock(out, (s * (x0 + 9), y0 + 14, WATER - .2), r=1.1, seed=54 + int(s))
        # queda d'agua do muro do terraco
        out.add('SLT', box((3.6, 1.8, .9), (s * 30, y0 + .3, TERR - 2.2), bevel=.1))
        out.add('SLT', box((.5, 1.4, 1.2), (s * 31.9, y0 + .5, TERR - 1.6)))
        out.add('SLT', box((.5, 1.4, 1.2), (s * 28.1, y0 + .5, TERR - 1.6)))
        out.add('WTR', box((3.0, .35, TERR - 2.6 - WATER), (s * 30, y0 + 1.15, WATER + (TERR - 2.6 - WATER) / 2)))
        out.add('FOAM', puff_cloud([(s * 30 + dx, y0 + 1.6 + dy, WATER + .05, .9 + .3 * (k % 2)) for k, (dx, dy) in enumerate(((-1.2, 0), (0, .6), (1.2, 0), (0, -.2)))], 1, seed=7, seg=7))
        # vegetacao junto da agua (passeio externo)
        K.pampas(out, (s * 66, y0 + 8, PLAZA), h=2.6, seed=61 + s); K.pampas(out, (s * 67, y1 - 10, PLAZA), h=2.2, seed=63 + s)
        K.ground_cover(out, (s * 68, (y0 + y1) / 2, PLAZA), r=2.0, seed=65 + s)
        K3.round_tree(out, (s * 72, y0 + 18 + (6 if s > 0 else 0), PLAZA), h=9 + s, r=3.0, seed=80 + s, flowers='FLW' if s > 0 else None)
    # piso da praca no trecho + painel do eixo
    out.add('FLR', box((66, 26, .5), (0, YT1 + R_LAND + 4.0 + 13, PLAZA - .25)))
    out.add('ASH', box((66, 26, PLAZA - .5 - SKIRT), (0, YT1 + R_LAND + 4.0 + 13, SKIRT + (PLAZA - .5 - SKIRT) / 2)))
    pointed_panel(out, 0, YT1 + R_LAND + 6.0, YT1 + R_LAND + 26.0, 2.6, PLAZA + .02)
    # saia rochosa da ilha (fecha o vazio sob a plataforma)
    K3.island_skirt(out, 0, -92, 100.0, 48.0, SKIRT + .2, 40.0, seed=5)
    # rochedos estratificados (com grama e arvores) no limite + arvores redondas verdes
    for i, (rx, ry, rr, rh) in enumerate([(-74, -154, 17, 16), (72, -156, 16, 15), (-20, -164, 13, 12), (24, -162, 12, 14), (-94, -122, 12, 18), (96, -120, 11, 20)]):
        K3.cliff(out, (rx, ry, PLAZA - 4), r=rr, h=rh, seed=90 + i, tree=(i % 2 == 0))
    for i, (tx, ty, h, r) in enumerate([(-56, -142, 12, 4.2), (60, -144, 11, 3.8), (-34, -152, 10, 3.4), (34, -152, 12, 4.0), (-88, -104, 10, 3.6), (90, -102, 9, 3.2), (-46, -136, 8, 2.8)]):
        K3.round_tree(out, (tx, ty, PLAZA), h=h, r=r, seed=70 + i, flowers='FLW' if i % 3 == 0 else None)
    for i, (tx, ty, h) in enumerate([(-64, -148, 26), (66, -150, 24)]):
        K3.poplar3(out, (tx, ty, PLAZA), h=h, r=2.4, seed=100 + i, density=.8)

# ================================================================ BUILD / EXPORT
def split_big(root, LIMIT=15000):
    def tris(ob): return sum(len(p.vertices) - 2 for p in ob.data.polygons)
    def split(ob):
        me = ob.data
        xs = [v.co for v in me.vertices]
        ext = [max(c[i] for c in xs) - min(c[i] for c in xs) for i in range(3)]
        ax = ext.index(max(ext))
        cs = sorted(p.center[ax] for p in me.polygons); med = cs[len(cs) // 2]
        parts = []
        for side in (0, 1):
            bm = bmesh.new(); bm.from_mesh(me)
            kill = [f for f in bm.faces if (f.calc_center_median()[ax] >= med) != bool(side)]
            bmesh.ops.delete(bm, geom=kill, context='FACES')
            m2 = bpy.data.meshes.new(me.name + '_' + 'ab'[side]); bm.to_mesh(m2); bm.free()
            for mat in me.materials: m2.materials.append(mat)
            for p in m2.polygons: p.use_smooth = True
            o2 = bpy.data.objects.new(ob.name + '_' + 'ab'[side], m2); root.objects.link(o2); parts.append(o2)
        bpy.data.objects.remove(ob, do_unlink=True)
        return parts
    queue = [o for o in root.objects if o.type == 'MESH' and o.name != '_ORIGEM']
    while queue:
        o = queue.pop()
        if tris(o) > LIMIT: queue.extend(split(o))

def build():
    root = coll('LV10_SECAO')
    clear_collection(root)
    mats = K.mats()
    parts = {}
    for name, fn in (('torre', tower), ('alas', wings), ('piso', terrace_and_stairs), ('agua', water_and_rocks)):
        out = B(name, root, mats)
        fn(out)
        parts[name] = out.finish(uv_world=K.UV_WORLD, uv_scale=K.UV_SCALE)
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0); _xform(bm, (0, 0, 120))
    me = bpy.data.meshes.new('_ORIGEM'); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new('_ORIGEM', me); root.objects.link(ob)
    split_big(root)
    total = sum(sum(len(p.vertices) - 2 for p in o.data.polygons) for o in root.objects if o.type == 'MESH')
    print('SECAO objetos', len(root.objects), 'tris', total)
    return root

def export(root, name='LV10_SECAO'):
    bpy.ops.object.select_all(action='DESELECT')
    for o in root.all_objects:
        o.select_set(True)
    path = os.path.join(EXPORT, name + '.fbx')
    bpy.ops.export_scene.fbx(filepath=path, use_selection=True, axis_forward='-Z', axis_up='Y',
                             apply_scale_options='FBX_SCALE_ALL', mesh_smooth_type='FACE',
                             path_mode='COPY', embed_textures=True, use_mesh_modifiers=True,
                             add_leaf_bones=False, bake_anim=False, use_custom_props=False)
    print('exportado', path, os.path.getsize(path))
    return path
