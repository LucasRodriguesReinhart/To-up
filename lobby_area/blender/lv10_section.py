# lv10_section.py - ETAPA C: trecho representativo ACABADO do acesso a Forja do Ignis.
# Torre da Forja (3 tiers com arcos recuados e molduras), alas (1 vao de cada lado), terraco,
# escadaria monumental com bochechas/urnas/postes, patamar semicircular do spawn com aneis e
# medalhao, espelhos d'agua com pedras, canteiros com alamos dourados, rochedos de fundo.
# Coordenadas ja na orientacao do Roblox: Blender(+X,+Y,+Z) -> Roblox(-X,+Z,+Y). 1 un = 1 stud.
# CONVENCAO: a FRENTE dos edificios e +Y (praca); corpo cresce para -Y; saliencias = +Y.
import bpy, bmesh, math, os, random, importlib, sys
from mathutils import Vector
sys.path.insert(0, r"C:\Users\lucas\OneDrive\Desktop\To up\lobby_area\blender")
import lvlib, lv10_kit
importlib.reload(lvlib); importlib.reload(lv10_kit)
from lvlib import box, cyl, ball, lathe, torus, ngon_prism, ring_prism, reg_poly, coll, clear_collection, B, _xform
K = lv10_kit
TAU = math.tau
EXPORT = r"C:\Users\lucas\OneDrive\Desktop\To up\lobby_area\export"

# ---- niveis ----
PLAZA, LAND, TERR = 2.0, 5.0, 10.0
WATER, BASIN = 0.6, -1.0
# ---- eixo Y (== Z do Roblox) ----
YF = -112.0          # fachada da torre (frente, +Y)
YT0 = -104.0         # topo da escadaria (borda do terraco)
YT1 = -90.0          # pe da escadaria (patamar)
R_LAND = 30.0        # semicirculo do patamar, centro (0, YT1)
TW, TD = 40.0, 30.0  # torre
H1, H2, H3 = 22.0, 30.0, 16.0
SW = 26.0            # largura da escada

def arc_pts(cx, cy, r, a0, a1, n=32):
    return [(cx + math.cos(a0 + (a1 - a0) * i / n) * r, cy + math.sin(a0 + (a1 - a0) * i / n) * r) for i in range(n + 1)]

# ================================================================ TORRE
def tower(out):
    yc = YF - TD / 2
    # ---------- tier 1 (arcada terrea): frente em f1 ----------
    f1 = YF
    K.arch_opening(out, (0, f1, TERR), 20, H1, 14, 12, 19.4, 2.2, mat='SDK')                                # painel central com ogiva (alcova)
    for s in (-1, 1):
        K.arch_opening(out, (s * 15, f1, TERR), 10, H1, 5.5, 7.5, 10.25, 2.2, mat='SDK', back='FRG', back_depth=2.4, pointed=False)
    K.arch_molding(out, (0, f1 + .3, TERR), 14, 12, 19.4, r=.55, mat='SLT')
    # braseiros de forja flanqueando a alcova (identidade do Ignis no ponto de interacao)
    for s in (-1, 1):
        bx = s * 10.6
        out.add('SLT', box((2.4, 2.4, .5), (bx, f1 + 3.0, TERR + .25), bevel=.06))
        out.add('SDK', cyl(.42, 3.6, (bx, f1 + 3.0, TERR + .5), seg=8))
        out.add('GLD', lathe([(.5, 0), (1.5, .7), (1.7, 1.3), (1.15, 1.5)], (bx, f1 + 3.0, TERR + 4.1), seg=12))
        out.add('EMB', ball(1.0, (bx, f1 + 3.0, TERR + 5.5), seg=8, scl=(1, 1, .8)))
    for s in (-1, 1):
        K.arch_molding(out, (s * 15, f1 + .25, TERR), 5.5, 7.5, 10.25, r=.42, mat='SLT', pointed=False)
        out.add('GLD', box((.3, .3, 7.5), (s * 15, f1 - 1.4, TERR + 3.75)))          # tracaria dentro do nicho
        out.add('GLD', box((5.2, .3, .3), (s * 15, f1 - 1.4, TERR + 5.0)))
    for x in (-19.0, -9.6, 9.6, 19.0):
        K.pilaster(out, (x, f1 + .75, TERR), 1.9, 1.5, H1)
    # corpo do tier 1: dois blocos laterais + bloco de fundo, deixando a ALCOVA vazia (|x|<8, y de f1 a f1-12.4)
    # e comecando atras dos paineis de fundo dos nichos (recesso 2.2 + painel .3 + folga)
    AD = 12.0
    yb0 = f1 - 2.9                       # frente do corpo
    yback = YF - TD                      # fundo da torre
    for s in (-1, 1):
        out.add('SDK', box((12, yb0 - yback, H1), (s * 14, (yb0 + yback) / 2, TERR + H1 / 2)))
    yb1 = f1 - AD - .6
    out.add('SDK', box((TW, yb1 - yback, H1), (0, (yb1 + yback) / 2, TERR + H1 / 2)))
    # alcova da forja (12 de profundidade)
    out.add('FLL', box((14.4, AD + .4, .4), (0, f1 - AD / 2, TERR - .2)))
    out.add('SLT', box((.8, AD, 22), (-7.2, f1 - AD / 2, TERR + 11)))
    out.add('SLT', box((.8, AD, 22), (7.2, f1 - AD / 2, TERR + 11)))
    out.add('SLT', box((16, AD, 1.2), (0, f1 - AD / 2, TERR + 21.6)))
    out.add('DRK', box((16, .8, 23), (0, f1 - AD - .2, TERR + 11)))
    out.add('SLT', torus(4.6, .9, (0, f1 - AD + .6, TERR + 4.0), (math.pi / 2, 0, 0), seg=18, sides=8, arc=math.pi))
    out.add('EMB', torus(3.9, .5, (0, f1 - AD + .5, TERR + 4.0), (math.pi / 2, 0, 0), seg=18, sides=6, arc=math.pi))
    out.add('EMB', box((7.6, .5, 4.2), (0, f1 - AD + .55, TERR + 2.1)))
    out.add('DRK', box((9.0, .3, 6.0), (0, f1 - AD + .9, TERR + 3.0)))
    # cornija 1 + parapeitos de canto + texto FORJA sobre a cornija
    K.cornice(out, (0, f1, TERR + H1), TW + 2.4, 3.4, h=2.6)
    for s in (-1, 1):
        out.add('SLT', box((3.4, 3.4, 2.4), (s * 19.2, f1 - .4, TERR + H1 + 2.6 + 1.2), bevel=.1))
        out.add('GLD', lathe([(.9, 0), (.6, .6), (.05, 2.4)], (s * 19.2, f1 - .4, TERR + H1 + 5.0), seg=8))
    K.gold_text(out, 'FORJA', (0, f1 + 1.0, TERR + H1 + 2.8), size=6.4, depth=1.6)
    # ---------- tier 2 (ogivas altas; central com vitral dourado): frente recuada .8 ----------
    z2 = TERR + H1 + 2.6
    f2 = YF - .8
    K.arch_opening(out, (0, f2, z2), 18, H2, 12, 14, 25, 2.6, mat='SDK', back='FRG', back_depth=2.8)
    for s in (-1, 1):
        K.arch_opening(out, (s * 14, f2, z2), 10, H2, 6.5, 12, 20, 2.6, mat='SDK', back='DRK', back_depth=2.8)
    K.arch_molding(out, (0, f2 + .3, z2), 12, 14, 25, r=.55, mat='SLT')
    for s in (-1, 1):
        K.arch_molding(out, (s * 14, f2 + .25, z2), 6.5, 12, 20, r=.42, mat='SLT')
    for x in (-3.6, -1.2, 1.2, 3.6):
        out.add('GLD', box((.34, .3, 16), (x, f2 - 1.6, z2 + 8)))
    out.add('GLD', torus(2.6, .2, (0, f2 - 1.6, z2 + 17.5), (math.pi / 2, 0, 0), seg=18, sides=6))
    out.add('GLD', torus(1.3, .16, (0, f2 - 1.6, z2 + 21.0), (math.pi / 2, 0, 0), seg=14, sides=6))
    for s in (-1, 1):
        for x in (-1.6, 1.6):
            out.add('GLD', box((.3, .3, 12), (s * 14 + x, f2 - 1.6, z2 + 6)))
    for x in (-18.2, -8.6, 8.6, 18.2):
        K.pilaster(out, (x, f2 + .7, z2), 1.8, 1.4, H2)
    yb2 = f2 - 3.4                       # atras do painel do vitral (recesso 2.6 + painel .3 + folga)
    out.add('SDK', box((TW - 1.6, yb2 - (YF - TD), H2), (0, (yb2 + YF - TD) / 2, z2 + H2 / 2)))
    K.cornice(out, (0, f2, z2 + H2), TW + 1.2, 3.4, h=2.8)
    for s in (-1, 1):
        out.add('SLT', box((3.0, 3.0, 3.0), (s * 18.6, f2 - .4, z2 + H2 + 2.8 + 1.5), bevel=.1))
        out.add('SLT', lathe([(1.4, 0), (.9, 1.2), (.05, 5.0)], (s * 18.6, f2 - .4, z2 + H2 + 5.8), seg=8))
        out.add('GLD', lathe([(.4, 0), (.03, 1.6)], (s * 18.6, f2 - .4, z2 + H2 + 10.6), seg=6))
    # ---------- tier 3 (arcada de 5 arcos estreitos): frente recuada 2.5 ----------
    z3 = z2 + H2 + 2.8
    f3 = YF - 2.5
    W3, D3 = TW - 5.0, TD - 5.0
    for i in range(5):
        x = -12.8 + i * 6.4
        K.arch_opening(out, (x, f3, z3), 6.4, H3, 3.4, 8.5, 10.2, 1.6, mat='SDK', back='DRK', back_depth=1.8, pointed=False)
        K.arch_molding(out, (x, f3 + .2, z3), 3.4, 8.5, 10.2, r=.3, mat='SLT', pointed=False, gold=False)
    for x in (-16.4, 16.4):
        K.pilaster(out, (x, f3 + .7, z3), 1.6, 1.4, H3)
    out.add('SDK', box((W3, D3 - 1.6, H3), (0, yc - 2.5 - .8, z3 + H3 / 2)))
    K.cornice(out, (0, f3, z3 + H3), W3 + 1.2, 3.0, h=2.6)
    # ---------- tambor octogonal + cupula + agulha ----------
    zd = z3 + H3 + 2.6
    yd = yc - 2.5
    out.add('SLT', ngon_prism(reg_poly(13.5, 8, TAU / 16), 4.0, (0, yd, zd)))
    out.add('GLD', ngon_prism(reg_poly(13.8, 8, TAU / 16), .5, (0, yd, zd + 4.0)))
    for i in range(8):
        a = i / 8 * TAU
        out.add('SLT', box((1.6, 1.6, 4.4), (math.cos(a) * 12.6, yd + math.sin(a) * 12.6, zd + 2.2), (0, 0, a), bevel=.1))
    prof = [(math.cos(t / 7 * math.pi / 2) * 13.0, math.sin(t / 7 * math.pi / 2) * 10.0) for t in range(8)]
    out.add('GLS', lathe(prof, (0, yd, zd + 4.5), seg=24))
    for i in range(8):
        a = i / 8 * TAU + TAU / 16
        bm = bmesh.new(); prev = None
        for k in range(8):
            t = k / 7
            rr = math.cos(t * math.pi / 2) * 13.25; zz = math.sin(t * math.pi / 2) * 10.0
            px, py = math.cos(a) * rr, math.sin(a) * rr
            v1 = bm.verts.new((px - math.sin(a) * .4, py + math.cos(a) * .4, zz))
            v2 = bm.verts.new((px + math.sin(a) * .4, py - math.cos(a) * .4, zz))
            v3 = bm.verts.new((px * 1.03, py * 1.03, zz + .3))
            if prev:
                bm.faces.new([prev[0], v1, v3, prev[2]]); bm.faces.new([prev[2], v3, v2, prev[1]])
            prev = (v1, v2, v3)
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        _xform(bm, (0, yd, zd + 4.5))
        out.add('GLD', bm)
    out.add('GLD', lathe([(1.6, 0), (1.8, .5), (.6, 1.1), (.7, 1.6), (.03, 6.5)], (0, yd, zd + 14.3), seg=12))

# ================================================================ ALAS (1 vao de cada lado)
def wings(out):
    for s in (-1, 1):
        x0 = s * 33.0
        WW, WD = 26.0, 24.0
        yc = YF - WD / 2
        WH1, WH2 = 16.0, 10.0
        f1 = YF
        for k in (-1, 1):
            K.arch_opening(out, (x0 + k * 6.5, f1, TERR), 13, WH1, 5.8, 8.0, 10.9, 2.0, mat='SDK', back='FRG', back_depth=2.2, pointed=False)
            K.arch_molding(out, (x0 + k * 6.5, f1 + .25, TERR), 5.8, 8.0, 10.9, r=.42, mat='SLT', pointed=False)
            out.add('GLD', box((.3, .3, 8), (x0 + k * 6.5, f1 - 1.2, TERR + 4)))
            out.add('GLD', box((5.4, .3, .3), (x0 + k * 6.5, f1 - 1.2, TERR + 5.4)))
        for x in (x0 - 12.2, x0, x0 + 12.2):
            K.pilaster(out, (x, f1 + .7, TERR), 1.8, 1.4, WH1)
        wb = f1 - 2.8; wback = YF - WD
        out.add('SDK', box((WW, wb - wback, WH1), (x0, (wb + wback) / 2, TERR + WH1 / 2)))
        K.cornice(out, (x0, f1, TERR + WH1), WW + 1.6, 3.0, h=2.4)
        K.quoins(out, (s * 45.8, f1 - .2, TERR), WH1 - .5)
        z2 = TERR + WH1 + 2.4
        f2 = YF - 1.2
        for k in (-1, 1):
            K.arch_opening(out, (x0 + k * 6.5, f2, z2), 13, WH2, 4.4, 5.0, 7.2, 1.6, mat='SDK', back='DRK', back_depth=1.8, pointed=False)
            K.arch_molding(out, (x0 + k * 6.5, f2 + .2, z2), 4.4, 5.0, 7.2, r=.32, mat='SLT', pointed=False, gold=False)
        for x in (x0 - 12.2, x0, x0 + 12.2):
            K.pilaster(out, (x, f2 + .6, z2), 1.6, 1.2, WH2)
        wb2 = f2 - 2.4; wback2 = YF - WD + 2.0
        out.add('SDK', box((WW, wb2 - wback2, WH2), (x0, (wb2 + wback2) / 2, z2 + WH2 / 2)))
        K.cornice(out, (x0, f2, z2 + WH2), WW + 1.6, 3.0, h=2.4)
        out.add('SLA', box((WW + .4, WD - 3.0, .5), (x0, yc - 1.2, z2 + WH2 + 2.4)))
        K.balustrade(out, (x0 - WW / 2, f2 + .6), (x0 + WW / 2, f2 + .6), z2 + WH2 + 2.4, h=2.6)
        # torre de canto redonda com cupula pequena + seteiras
        cx = s * 50.0
        cy = YF - 4.0
        out.add('SDK', cyl(4.6, WH1 + WH2 + 6.0, (cx, cy, TERR), seg=16))
        for zz in (TERR + WH1 + 1.2, TERR + WH1 + WH2 + 5.2):
            out.add('SLT', torus(4.7, .45, (cx, cy, zz), seg=16, sides=6))
        out.add('GLD', torus(4.75, .16, (cx, cy, TERR + WH1 + WH2 + 6.3), seg=16, sides=5))
        out.add('SLT', cyl(5.2, .8, (cx, cy, TERR + WH1 + WH2 + 6.0), seg=16))
        out.add('GLS', lathe([(5.0, 0), (4.4, 1.8), (2.6, 3.6), (.8, 4.8), (.03, 5.4)], (cx, cy, TERR + WH1 + WH2 + 6.8), seg=16))
        out.add('GLD', lathe([(.5, 0), (.03, 2.2)], (cx, cy, TERR + WH1 + WH2 + 12.1), seg=6))
        for zz in (TERR + 6, TERR + 14, TERR + 22):
            out.add('SLT', box((1.2, .6, 3.2), (cx, cy + 4.55, zz), bevel=.05))
            out.add('DRK', box((.6, .4, 2.4), (cx, cy + 4.75, zz)))

# ================================================================ TERRACO, ESCADARIA, PATAMAR
def terrace_and_stairs(out):
    out.add('FLL', box((124, (YT0 - YF), .6), (0, (YF + YT0) / 2, TERR - .3)))
    out.add('ASH', box((124, YT0 - YF, TERR - PLAZA - .6), (0, (YF + YT0) / 2, PLAZA + (TERR - PLAZA - .6) / 2)))
    for s in (-1, 1):
        xm = s * (15.4 + (62 - 15.4) / 2)
        out.add('SLT', box((62 - 15.4, 1.4, .7), (xm, YT0 - .2, TERR + .1), bevel=.1))
        out.add('GLD', box((62 - 15.4, .4, .1), (xm, YT0 + .1, TERR + .48)))
        K.balustrade(out, (s * 15.4, YT0 - .6), (s * 62, YT0 - .6), TERR + .45, h=2.6)
    # escadaria LAND -> TERR (10 degraus) com faixa azul/ouro
    n = 10
    rise = (TERR - LAND) / n
    run = (YT0 - YT1) / n
    for i in range(n):
        yy = YT1 + (i + .5) * run
        zz = LAND + i * rise
        out.add('FLL', box((SW, abs(run) + .16, rise), (0, yy, zz + rise / 2)))
        out.add('LPS', box((3.2, abs(run) + .18, .06), (0, yy, zz + rise + .03)))
        for k in (-1, 1):
            out.add('GLD', box((.4, abs(run) + .18, .07), (k * 2.0, yy, zz + rise + .035)))
    for s in (-1, 1):
        xc = s * (SW / 2 + 1.2)
        out.add('SLT', box((2.4, 7.2, 3.6), (xc, YT1 - 3.6, LAND + 1.8)))
        out.add('SLT', box((2.4, 7.2, 6.4), (xc, YT1 - 10.6, LAND + 3.2)))
        out.add('SLT', box((2.8, 7.6, .5), (xc, YT1 - 3.6, LAND + 3.6 + .25), bevel=.12))
        out.add('SLT', box((2.8, 7.6, .5), (xc, YT1 - 10.6, LAND + 6.4 + .25), bevel=.12))
        out.add('GLD', box((2.9, 7.7, .1), (xc, YT1 - 3.6, LAND + 4.15)))
        out.add('GLD', box((2.9, 7.7, .1), (xc, YT1 - 10.6, LAND + 6.95)))
        K.urn(out, (xc, YT1 - 10.6, LAND + 6.4 + .5), r=1.35, seed=3 + s)
        K.pedestal(out, (xc, YT1 + 2.4, LAND), w=3.4, h=2.2)
        K.lamp_post(out, (xc, YT1 + 2.4, LAND + 2.2), scale=1.15)
        K.pedestal(out, (xc, YT0 - 2.0, TERR), w=3.0, h=1.6)
        K.urn(out, (xc, YT0 - 2.0, TERR + 1.6), r=1.2, seed=7 + s)
    # patamar semicircular + dois aneis descendo ate PLAZA
    half = arc_pts(0, YT1, R_LAND, 0, math.pi)
    out.add('FLL', ngon_prism(half + [(-R_LAND, YT1 - 14), (R_LAND, YT1 - 14)], LAND - PLAZA, (0, 0, PLAZA)))
    K.coping_arc(out, 0, YT1, R_LAND + .6, LAND - 1.0, 0, math.pi, w=1.4, h=1.0)
    r2 = R_LAND + 3.2
    out.add('FLL', ring_prism(arc_pts(0, YT1, r2 + .6, 0, math.pi), arc_pts(0, YT1, R_LAND - .2, 0, math.pi), LAND - 1.5 - PLAZA, (0, 0, PLAZA)))
    K.coping_arc(out, 0, YT1, r2 + .6, LAND - 2.5, 0, math.pi, w=1.4, h=1.0)
    out.add('ASH', ring_prism(arc_pts(0, YT1, r2 + 1.4, 0, math.pi), arc_pts(0, YT1, r2 - .2, 0, math.pi), 1.6, (0, 0, PLAZA - .1)))
    # medalhao do spawn (0,-66)
    cx, cy = 0, -66
    out.add('GLD', ring_prism(reg_poly(7.0, 32), reg_poly(6.3, 32), .1, (cx, cy, LAND)))
    out.add('LPS', ring_prism(reg_poly(6.3, 32), reg_poly(5.0, 32), .08, (cx, cy, LAND)))
    out.add('GLD', ring_prism(reg_poly(5.0, 32), reg_poly(4.6, 32), .1, (cx, cy, LAND)))
    star = []
    for i in range(16):
        a = i / 16 * TAU + TAU / 32
        rr = 4.3 if i % 2 == 0 else 1.9
        star.append((cx + math.cos(a) * rr, cy + math.sin(a) * rr))
    out.add('LPS', ngon_prism(star, .09, (0, 0, LAND)))
    out.add('GLD', ngon_prism([(cx + (x - cx) * .82, cy + (y - cy) * .82) for x, y in star], .11, (0, 0, LAND)))
    out.add('LPS', cyl(1.4, .13, (cx, cy, LAND), seg=16))
    out.add('GLD', cyl(.7, .15, (cx, cy, LAND), seg=12))
    # faixa azul do eixo (medalhao -> escada; medalhao -> borda do patamar)
    out.add('LPS', box((3.2, abs(cy + 7.0 - YT1), .06), (0, (YT1 + cy + 7.0) / 2, LAND + .03)))
    out.add('LPS', box((3.2, abs((YT1 + R_LAND) - (cy - 7.0)), .06), (0, ((YT1 + R_LAND) + (cy - 7.0)) / 2, LAND + .03)))
    for k in (-1, 1):
        out.add('GLD', box((.4, abs(cy + 7.0 - YT1), .07), (k * 2.0, (YT1 + cy + 7.0) / 2, LAND + .035)))
        out.add('GLD', box((.4, abs((YT1 + R_LAND) - (cy - 7.0)), .07), (k * 2.0, ((YT1 + R_LAND) + (cy - 7.0)) / 2, LAND + .035)))
    out.add('GLD', ring_prism(arc_pts(0, YT1, R_LAND - 2.0, 0, math.pi) + [(-(R_LAND - 2.0), YT1 - .01)], arc_pts(0, YT1, R_LAND - 2.5, 0, math.pi) + [(-(R_LAND - 2.5), YT1 - .01)], .07, (0, 0, LAND)))
    # postes no anel do patamar
    for s in (-1, 1):
        px, py = s * 23.0, YT1 + 18.0
        K.pedestal(out, (px, py, LAND), w=2.8, h=1.2)
        K.lamp_post(out, (px, py, LAND + 1.2))
    # escada frontal do patamar (LAND->PLAZA) no eixo
    n2 = 6
    for i in range(n2):
        r = (LAND - PLAZA) / n2
        out.add('FLL', box((14, 1.3, r), (0, YT1 + R_LAND + .6 + (i + .5) * 1.2, LAND - (i + 1) * r + r / 2)))
    # canteiros octogonais ao lado da escadaria com alamos dourados e arbustos
    for s in (-1, 1):
        cxp, cyp = s * 23.0, YT1 - 7.0
        pts = reg_poly(6.2, 8, TAU / 16)
        out.add('SLT', ring_prism([(cxp + x, cyp + y) for x, y in reg_poly(6.8, 8, TAU / 16)], [(cxp + x, cyp + y) for x, y in pts], 1.2, (0, 0, LAND)))
        out.add('SLT', ring_prism([(cxp + x, cyp + y) for x, y in reg_poly(7.4, 8, TAU / 16)], [(cxp + x, cyp + y) for x, y in reg_poly(6.8, 8, TAU / 16)], .6, (0, 0, LAND)))
        out.add('GRS', ngon_prism([(cxp + x, cyp + y) for x, y in pts], .9, (0, 0, LAND)))
        K.poplar(out, (cxp - s * 1.5, cyp + 1.5, LAND + .9), h=25, r=2.5, seed=11 + s)
        K.poplar(out, (cxp + s * 2.5, cyp - 2.5, LAND + .9), h=21, r=2.2, seed=13 + s)
        K.bush(out, (cxp + s * 2.0, cyp + 3.0, LAND + .9), r=1.6, seed=5 + s, mat='LFG', flowers=None)
        K.bush(out, (cxp - s * 3.0, cyp - 2.0, LAND + .9), r=1.3, seed=9 + s, mat='LFV')

# ================================================================ AGUA, ROCHAS, LIMITE
def water_and_rocks(out):
    for s in (-1, 1):
        x0, x1 = 33.0, 64.0
        y0, y1 = YT0, YT1 + R_LAND + 4.0   # -104 .. -56
        xc = s * (x0 + x1) / 2
        W = x1 - x0
        out.add('RCK', box((W, y1 - y0, .6), (xc, (y0 + y1) / 2, BASIN - .3)))
        out.add('ASH', box((1.2, y1 - y0, PLAZA - BASIN + .6), (s * x1, (y0 + y1) / 2, BASIN + (PLAZA - BASIN + .6) / 2 - .3)))
        out.add('ASH', box((W, 1.2, PLAZA - BASIN + .6), (xc, y1, BASIN + (PLAZA - BASIN + .6) / 2 - .3)))
        out.add('SLT', box((1.8, y1 - y0 + .6, .5), (s * x1, (y0 + y1) / 2, PLAZA + .25), bevel=.1))
        out.add('SLT', box((W + .6, 1.8, .5), (xc, y1, PLAZA + .25), bevel=.1))
        K.balustrade(out, (s * (x1 + .3), y0), (s * (x1 + .3), y1), PLAZA + .5, h=2.6)
        out.add('FLR', box((14, y1 - y0 + 2, .5), (s * (x1 + 7.5), (y0 + y1) / 2, PLAZA - .25)))
        rnd = random.Random(int(31 + s))
        for k in range(9):
            rx = s * (x0 + 3 + rnd.random() * (W - 6)); ry = y0 + 3 + rnd.random() * (y1 - y0 - 6)
            K.rock(out, (rx, ry, BASIN + rnd.random() * .8), r=1.1 + rnd.random() * 1.4, seed=40 + k + int(s))
        out.add('SLT', box((4.0, 1.6, 1.0), (s * 46, y0 + .2, TERR - 2.4), bevel=.1))
        out.add('WTR', box((3.2, .5, TERR - 2.9 - WATER), (s * 46, y0 + 1.1, WATER + (TERR - 2.9 - WATER) / 2)))
    out.add('FLR', box((66, 26, .5), (0, YT1 + R_LAND + 4.0 + 13, PLAZA - .25)))
    out.add('LPS', box((3.2, 26, .06), (0, YT1 + R_LAND + 4.0 + 13, PLAZA + .03)))
    for k in (-1, 1):
        out.add('GLD', box((.4, 26, .07), (k * 2.0, YT1 + R_LAND + 4.0 + 13, PLAZA + .035)))
    for i, (rx, ry, rr, rh) in enumerate([(-74, -150, 20, 26), (74, -150, 20, 26), (-20, -160, 16, 22), (20, -160, 16, 22), (-96, -120, 14, 30), (96, -120, 14, 30)]):
        out.add('RCK', lathe([(rr, 0), (rr * .95, rh * .35), (rr * .6, rh * .75), (rr * .25, rh)], (rx, ry, PLAZA - 6), seg=9))
        K.rock(out, (rx + rr * .7, ry + rr * .8, PLAZA), r=rr * .25, seed=60 + i)
    for i, (tx, ty, h) in enumerate([(-58, -138, 30), (58, -138, 30), (-30, -146, 26), (30, -146, 26), (-90, -100, 24), (90, -100, 24)]):
        K.poplar(out, (tx, ty, PLAZA), h=h, r=3.2, seed=70 + i, mat='LFV', mat2='LFV')

# ================================================================ BUILD / EXPORT
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
    total = sum(len(o.data.polygons) for objs in parts.values() for o in objs)
    print('SECAO objetos', {k: len(v) for k, v in parts.items()}, 'faces', total)
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
