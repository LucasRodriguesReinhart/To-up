# lv10_section.py - ETAPA C (revisao 2): trecho representativo do acesso a Forja do Ignis.
# Direcao visual corrigida: pedra CLARA (marfim / cinza claro quente) + dourado como ornamento integrado,
# azul so em detalhe; torre ESBELTA (30 de largura x ~93 de altura) com corpo central destacado,
# alas recuadas e baixas separadas por vegetacao; entrada arqueada dominante com escada de 18;
# inlays azul/ouro como paineis do piso; espelhos d'agua com margens curvas, prateleira rasa e pedras
# submersas; vegetacao alta delicada + baixa, assimetrica.
# Coordenadas na orientacao do Roblox: Blender(+X,+Y,+Z) -> Roblox(-X,+Z,+Y). FRENTE dos edificios = +Y.
import bpy, bmesh, math, os, random, importlib, sys
from mathutils import Vector
sys.path.insert(0, r"C:\Users\lucas\OneDrive\Desktop\To up\lobby_area\blender")
import lvlib, lv10_kit
importlib.reload(lvlib); importlib.reload(lv10_kit)
from lvlib import box, cyl, ball, lathe, torus, ngon_prism, ring_prism, reg_poly, coll, clear_collection, B, _xform
K = lv10_kit
TAU = math.tau
EXPORT = r"C:\Users\lucas\OneDrive\Desktop\To up\lobby_area\export"

PLAZA, LAND, TERR = 2.0, 5.0, 10.0
WATER, BASIN = 0.6, -2.2
YF = -112.0            # fachada da torre
YW = YF - 14.0         # fachada das alas (recuadas)
YT0 = -104.0           # topo da escada (borda do terraco)
YT1 = -90.0            # pe da escada (patamar)
R_LAND = 30.0
TW, TD = 30.0, 26.0
H1, H2, H3 = 20.0, 32.0, 14.0
SW = 18.0              # largura da escada
MED = (0.0, -68.0)     # medalhao do spawn (spawn real em (0,-66))

def arc_pts(cx, cy, r, a0, a1, n=32):
    return [(cx + math.cos(a0 + (a1 - a0) * i / n) * r, cy + math.sin(a0 + (a1 - a0) * i / n) * r) for i in range(n + 1)]

def pointed_panel(out, x, y0, y1, w, z, mat_in='LPS', frame='GLD', fw=.32, tip=None):
    """painel embutido no piso com pontas ogivais (ref: paineis azuis com moldura de ouro). y0<y1."""
    tip = tip or w * .9
    poly = [(x - w/2, y0 + tip), (x, y0), (x + w/2, y0 + tip), (x + w/2, y1 - tip), (x, y1), (x - w/2, y1 - tip)]
    poly_o = [(x - w/2 - fw, y0 + tip - fw * .4), (x, y0 - fw * 1.3), (x + w/2 + fw, y0 + tip - fw * .4),
              (x + w/2 + fw, y1 - tip + fw * .4), (x, y1 + fw * 1.3), (x - w/2 - fw, y1 - tip + fw * .4)]
    out.add(frame, ngon_prism(poly_o, .07, (0, 0, z)))
    out.add(mat_in, ngon_prism(poly, .09, (0, 0, z)))

def lozenge(out, x, y, a, L, w, z, mat_in='LPS', frame='GLD', fw=.28):
    """losango embutido alinhado ao angulo a"""
    c, s = math.cos(a), math.sin(a)
    def P(u, v): return (x + u * c - v * s, y + u * s + v * c)
    out.add(frame, ngon_prism([P(-L/2 - fw, 0), P(0, w/2 + fw), P(L/2 + fw, 0), P(0, -w/2 - fw)], .07, (0, 0, z)))
    out.add(mat_in, ngon_prism([P(-L/2, 0), P(0, w/2), P(L/2, 0), P(0, -w/2)], .09, (0, 0, z)))

# ================================================================ TORRE (esbelta, clara)
def tower(out):
    yb = YF - TD                       # fundo da torre
    # ---------- torres de canto octogonais (verticalidade) ----------
    for sx in (-1, 1):
        for sy, yy in ((0, YF - .6), (1, yb + .6)):
            hT = H1 + 2.2 + H2 + 2.4 + 5.0
            pts = reg_poly(2.1, 8, TAU / 16)
            out.add('SLT', ngon_prism([(sx * 15.0 + px, yy + py) for px, py in pts], hT, (0, 0, TERR)))
            for zz in (TERR + H1 + 1.2, TERR + H1 + 2.2 + H2 + 1.4):
                out.add('SLT', ngon_prism([(sx * 15.0 + px, yy + py) for px, py in reg_poly(2.5, 8, TAU / 16)], .8, (0, 0, zz)))
                out.add('GLD', ngon_prism([(sx * 15.0 + px, yy + py) for px, py in reg_poly(2.55, 8, TAU / 16)], .16, (0, 0, zz + .8)))
            out.add('SLT', lathe([(2.5, 0), (2.2, .5), (.05, 6.5)], (sx * 15.0, yy, TERR + hT), seg=8))
            out.add('GLD', lathe([(.5, 0), (.03, 1.8)], (sx * 15.0, yy, TERR + hT + 6.4), seg=6))
    # ---------- tier 1 ----------
    f1 = YF
    AD = 8.0
    K.arch_opening(out, (0, f1, TERR), 14, H1, 10, 9.5, 15.5, 2.2, mat='SMD')
    for s in (-1, 1):
        K.arch_opening(out, (s * 11, f1, TERR), 8, H1, 3.6, 6.0, 7.8, 2.2, mat='SMD', back='FRG', back_depth=2.4, pointed=False)
        K.arch_molding(out, (s * 11, f1 + .22, TERR), 3.6, 6.0, 7.8, r=.34, mat='SLT', pointed=False)
        out.add('GLD', box((.22, .24, 6.0), (s * 11, f1 - 1.3, TERR + 3.0)))
        out.add('GLD', box((3.2, .24, .22), (s * 11, f1 - 1.3, TERR + 4.2)))
    # portal: moldura externa grossa + moldura interna recuada (profundidade) + filete de ouro
    K.arch_molding(out, (0, f1 + .38, TERR), 10, 9.5, 15.5, r=.62, mat='SLT')
    K.arch_molding(out, (0, f1 - 1.1, TERR), 8.9, 9.3, 15.0, r=.4, mat='SLT', gold=True)
    # tímpano decorativo sobre o portal: trilobo dourado
    out.add('GLD', torus(1.1, .14, (0, f1 + .3, TERR + 17.2), (math.pi / 2, 0, 0), seg=14, sides=6))
    for s in (-1, 1):
        out.add('GLD', torus(.7, .12, (s * 1.5, f1 + .3, TERR + 16.2), (math.pi / 2, 0, 0), seg=12, sides=6))
    for x in (-7.0, 7.0):
        K.pilaster(out, (x, f1 + .7, TERR), 1.6, 1.4, H1)
    # corpo: blocos laterais + fundo, alcova vazia
    yb0 = f1 - 2.9
    for s in (-1, 1):
        out.add('SMD', box((9.6, yb0 - yb, H1), (s * 10.2, (yb0 + yb) / 2, TERR + H1 / 2)))
    yb1 = f1 - AD - .6
    out.add('SMD', box((TW, yb1 - yb, H1), (0, (yb1 + yb) / 2, TERR + H1 / 2)))
    # alcova da forja
    out.add('FLL', box((10.6, AD + .4, .4), (0, f1 - AD / 2, TERR - .2)))
    out.add('SLT', box((.8, AD, 18), (-5.2, f1 - AD / 2, TERR + 9)))
    out.add('SLT', box((.8, AD, 18), (5.2, f1 - AD / 2, TERR + 9)))
    out.add('SLT', box((12, AD, 1.4), (0, f1 - AD / 2, TERR + 17.6)))
    out.add('DRK', box((12, .8, 19), (0, f1 - AD - .2, TERR + 9.2)))
    # boca de forja: coifa de pedra clara + arco escuro + brasa + chamine
    out.add('SLT', box((7.2, 1.6, .8), (0, f1 - AD + 1.0, TERR + 7.6), bevel=.1))
    out.add('SLT', ngon_prism([(-3.6, 0), (3.6, 0), (2.4, 2.0), (-2.4, 2.0)], 1.4, (0, f1 - AD + 1.7, TERR + 8.0), (math.pi / 2, 0, 0)))
    out.add('SMD', torus(3.1, .7, (0, f1 - AD + .6, TERR + 2.8), (math.pi / 2, 0, 0), seg=16, sides=8, arc=math.pi))
    out.add('EMB', torus(2.6, .4, (0, f1 - AD + .5, TERR + 2.8), (math.pi / 2, 0, 0), seg=16, sides=6, arc=math.pi))
    out.add('EMB', box((5.2, .5, 3.0), (0, f1 - AD + .55, TERR + 1.5)))
    out.add('DRK', box((6.4, .3, 4.2), (0, f1 - AD + .9, TERR + 2.1)))
    # braseiros de forja flanqueando o portal (no terraco)
    for s in (-1, 1):
        bx = s * 8.4
        out.add('SLT', box((2.0, 2.0, .45), (bx, f1 + 3.2, TERR + .22), bevel=.06))
        out.add('SMD', cyl(.36, 3.0, (bx, f1 + 3.2, TERR + .45), seg=8))
        out.add('GLD', lathe([(.45, 0), (1.25, .6), (1.4, 1.1), (1.0, 1.3)], (bx, f1 + 3.2, TERR + 3.45), seg=12))
        out.add('EMB', ball(.8, (bx, f1 + 3.2, TERR + 4.6), seg=8, scl=(1, 1, .8)))
    # cornija 1 + painel do letreiro + FORJA
    K.cornice(out, (0, f1, TERR + H1), TW + 1.6, 3.2, h=2.2)
    out.add('SLT', box((TW - 4, 1.6, 2.4), (0, f1 - .3, TERR + H1 + 2.2 + 1.2)))
    out.add('GLD', box((TW - 4.2, .2, .14), (0, f1 + .55, TERR + H1 + 2.2 + .12)))
    for s in (-1, 1):
        out.add('SLT', box((2.2, 2.4, 3.0), (s * (TW / 2 - 3.2), f1 - .4, TERR + H1 + 2.2 + 1.5), bevel=.12))
        out.add('GLD', ball(.5, (s * (TW / 2 - 3.2), f1 - .4, TERR + H1 + 2.2 + 3.4), seg=8))
    K.gold_text(out, 'FORJA', (0, f1 + .75, TERR + H1 + 2.5), size=4.8, depth=1.2)
    # ---------- tier 2 ----------
    z2 = TERR + H1 + 2.2
    f2 = YF - 1.0
    W2 = TW - 2.0
    K.arch_opening(out, (0, f2, z2), 14, H2, 9, 13, 24, 2.4, mat='SMD', back='FRG', back_depth=2.6)
    for s in (-1, 1):
        K.arch_opening(out, (s * 10.5, f2, z2), 7, H2, 4.2, 12, 19, 2.4, mat='SMD', back='DRK', back_depth=2.6)
        K.arch_molding(out, (s * 10.5, f2 + .22, z2), 4.2, 12, 19, r=.34, mat='SLT')
        out.add('GLD', box((.2, .22, 11), (s * 10.5, f2 - 1.4, z2 + 5.5)))
    K.arch_molding(out, (0, f2 + .3, z2), 9, 13, 24, r=.5, mat='SLT')
    # tracaria do vitral: 5 maineis finos + 2 travessas + roseta
    for x in (-3.0, -1.5, 0, 1.5, 3.0):
        out.add('GLD', box((.18, .22, 15), (x, f2 - 1.5, z2 + 7.5)))
    for zz in (z2 + 6.0, z2 + 11.0):
        out.add('GLD', box((8.0, .22, .18), (0, f2 - 1.5, zz)))
    out.add('GLD', torus(2.0, .16, (0, f2 - 1.5, z2 + 18.2), (math.pi / 2, 0, 0), seg=18, sides=6))
    out.add('GLD', torus(.9, .12, (0, f2 - 1.5, z2 + 21.3), (math.pi / 2, 0, 0), seg=12, sides=6))
    for x in (-7.0, 7.0):
        K.pilaster(out, (x, f2 + .65, z2), 1.5, 1.3, H2)
    yb2 = f2 - 3.3
    out.add('SMD', box((W2, yb2 - yb, H2), (0, (yb2 + yb) / 2, z2 + H2 / 2)))
    K.cornice(out, (0, f2, z2 + H2), W2 + 2.0, 3.2, h=2.4)
    K.balustrade(out, (-W2 / 2 + 2.6, f2 + .4), (W2 / 2 - 2.6, f2 + .4), z2 + H2 + 2.4, h=2.4)
    # ---------- tier 3 (arcada de 3 arcos redondos) ----------
    z3 = z2 + H2 + 2.4
    f3 = YF - 3.0
    W3 = TW - 6.0
    for x in (-7.0, 0.0, 7.0):
        K.arch_opening(out, (x, f3, z3), 7.0, H3, 3.6, 8.0, 9.8, 1.6, mat='SMD', back='DRK', back_depth=1.8, pointed=False)
        K.arch_molding(out, (x, f3 + .2, z3), 3.6, 8.0, 9.8, r=.3, mat='SLT', pointed=False, gold=True)
    for x in (-10.5, -3.5, 3.5, 10.5):
        K.pilaster(out, (x, f3 + .6, z3), 1.3, 1.2, H3)
    yb3 = f3 - 3.6
    out.add('SMD', box((W3, yb3 - (yb + 3.0), H3), (0, (yb3 + yb + 3.0) / 2, z3 + H3 / 2)))
    K.cornice(out, (0, f3, z3 + H3), W3 + 2.0, 3.0, h=2.4)
    # ---------- tambor octogonal com janelinhas + cupula + agulha ----------
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

# ================================================================ ALAS (recuadas, baixas) + torres de canto
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
            K.arch_opening(out, (xa, fw, TERR), 12, WH, 5.0, 7.5, 10.0, 2.0, mat='SMD', back='FRG', back_depth=2.2, pointed=False)
            K.arch_molding(out, (xa, fw + .24, TERR), 5.0, 7.5, 10.0, r=.4, mat='SLT', pointed=False)
            out.add('GLD', box((.24, .24, 7.5), (xa, fw - 1.3, TERR + 3.75)))
            out.add('GLD', box((4.6, .24, .24), (xa, fw - 1.3, TERR + 5.2)))
        out.add('SMD', box((1.0, 2.2, WH), (xc, fw - 1.1, TERR + WH / 2)))     # trecho de parede entre os dois vaos
        for x in (xc - 12.0, xc, xc + 12.0):
            K.pilaster(out, (x, fw + .65, TERR), 1.6, 1.3, WH)
        wb = fw - 2.8
        out.add('SMD', box((WW, wb - yb, WH), (xc, (wb + yb) / 2, TERR + WH / 2)))
        K.cornice(out, (xc, fw, TERR + WH), WW + 1.4, 3.0, h=2.2)
        out.add('SLA', box((WW + .2, fw - yb - 2.0, .5), (xc, (fw + yb) / 2 - 1.0, TERR + WH + 2.2 + .1)))
        K.balustrade(out, (x_in + 1.0, fw + .3), (x_out - 1.0, fw + .3), TERR + WH + 2.2, h=2.4)
        # torre de canto redonda (mais alta que a ala) com cupula
        cx, cy = s * 43.0, fw - 4.0
        HT = 22.0
        out.add('SMD', cyl(3.6, HT, (cx, cy, TERR), seg=18))
        for zz in (TERR + WH + 1.0, TERR + HT - 1.2):
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
    # terraco: piso claro; tras da torre (y<YF) so nas alas
    out.add('FLL', box((2 * XT, YT0 - YW, .6), (0, (YT0 + YW) / 2, TERR - .3)))
    out.add('ASH', box((2 * XT, YT0 - YW, TERR - PLAZA - .6), (0, (YT0 + YW) / 2, PLAZA + (TERR - PLAZA - .6) / 2)))
    # muro de arrimo frontal (fora da escada) com coping e balaustrada
    for s in (-1, 1):
        x0, x1 = SW / 2 + 1.8, XT
        xm = s * (x0 + x1) / 2
        out.add('SLT', box((x1 - x0, 1.4, .6), (xm, YT0 - .2, TERR + .1), bevel=.1))
        K.balustrade(out, (s * x0, YT0 - .6), (s * x1, YT0 - .6), TERR + .4, h=2.4)
    # piso com folhas junto dos canteiros do terraco
    for s in (-1, 1):
        out.add('FLF', box((22, 16, .1), (s * 30, YW + 10, TERR + .02)))
    # ---- escada 18 de largura, 10 degraus, beiral saliente em pedra clara (sem faixa azul) ----
    n = 10
    rise = (TERR - LAND) / n
    run = (YT1 - YT0) / n          # 1.4
    for i in range(n):
        yy = YT1 - (i + .5) * run
        zz = LAND + i * rise
        out.add('FLL', box((SW, run + .1, rise), (0, yy, zz + rise / 2)))
        out.add('SLT', box((SW, .34, .18), (0, yy + run / 2 - .05, zz + rise - .09)))     # beiral/nosing
    out.add('GLD', box((SW, .16, .05), (0, YT0 + .15, TERR + .03)))                      # so o topo leva o fio de ouro
    # bochechas inclinadas (perfil YZ extrudado em X) + coping inclinado + pedestais
    for s in (-1, 1):
        xc = s * (SW / 2 + .9)
        prof = [(YT1 + .6, LAND - .2), (YT0 - .8, LAND - .2), (YT0 - .8, TERR + 1.3), (YT1 + .6, LAND + 1.3)]
        bm = ngon_prism(prof, 1.8, (0, 0, 0))                  # no plano (y,z) -> precisa girar
        # ngon_prism cria no plano XY e extruda em Z: usamos (y,z) como (x,y) e giramos para o plano YZ
        _xform(bm, (0, 0, 0), (math.pi / 2, 0, math.pi / 2))     # (u,v,w) -> plano YZ, extrusao em +X
        _xform(bm, (xc - .9, 0, 0))
        out.add('SLT', bm)
        Lc = math.hypot(YT1 - YT0, TERR - LAND) + 1.6
        ang = math.atan2(TERR - LAND, YT0 - YT1)
        out.add('SLT', box((2.3, Lc, .5), (xc, (YT0 + YT1) / 2 - .1, (LAND + TERR) / 2 + 1.55), (ang, 0, 0), bevel=.1))
        out.add('GLD', box((.5, Lc - .6, .06), (xc, (YT0 + YT1) / 2 - .1, (LAND + TERR) / 2 + 1.84), (ang, 0, 0)))   # so um filete central
        # pe: pedestal + poste ; topo: pedestal + urna
        K.pedestal(out, (s * (SW / 2 + 1.6), YT1 + 2.6, LAND), w=3.0, h=1.8)
        K.lamp_post(out, (s * (SW / 2 + 1.6), YT1 + 2.6, LAND + 1.8), scale=1.0)
        K.pedestal(out, (s * (SW / 2 + 1.6), YT0 - 2.2, TERR), w=2.8, h=1.4)
        K.urn(out, (s * (SW / 2 + 1.6), YT0 - 2.2, TERR + 1.4), r=1.1, seed=7 + s)
        K.pampas(out, (s * (SW / 2 + 3.6), YT1 + .6, LAND), h=2.4, seed=21 + s)
    # ---- patamar semicircular + aneis ----
    half = arc_pts(0, YT1, R_LAND, 0, math.pi)
    out.add('FLL', ngon_prism(half + [(-R_LAND, YT1 - 14), (R_LAND, YT1 - 14)], LAND - PLAZA, (0, 0, PLAZA)))
    out.add('FLF', ring_prism(arc_pts(0, YT1, R_LAND - .3, 0, math.pi), arc_pts(0, YT1, R_LAND - 6.0, 0, math.pi), .08, (0, 0, LAND)))   # faixa externa com folhas
    K.coping_arc(out, 0, YT1, R_LAND + .6, LAND - 1.0, 0, math.pi, w=1.4, h=1.0, gold=False)
    r2 = R_LAND + 3.2
    out.add('FLL', ring_prism(arc_pts(0, YT1, r2 + .6, 0, math.pi), arc_pts(0, YT1, R_LAND - .2, 0, math.pi), LAND - 1.5 - PLAZA, (0, 0, PLAZA)))
    K.coping_arc(out, 0, YT1, r2 + .6, LAND - 2.5, 0, math.pi, w=1.4, h=1.0, gold=True)
    out.add('ASH', ring_prism(arc_pts(0, YT1, r2 + 1.4, 0, math.pi), arc_pts(0, YT1, r2 - .2, 0, math.pi), 1.6, (0, 0, PLAZA - .1)))
    # ---- inlays azul/ouro integrados ao piso ----
    cx, cy = MED
    out.add('GLD', ring_prism(reg_poly(6.0, 32), reg_poly(5.4, 32), .1, (cx, cy, LAND)))
    out.add('LPS', ring_prism(reg_poly(5.4, 32), reg_poly(4.3, 32), .08, (cx, cy, LAND)))
    out.add('GLD', ring_prism(reg_poly(4.3, 32), reg_poly(3.95, 32), .1, (cx, cy, LAND)))
    star = []
    for i in range(16):
        a = i / 16 * TAU + TAU / 32
        rr = 3.7 if i % 2 == 0 else 1.7
        star.append((cx + math.cos(a) * rr, cy + math.sin(a) * rr))
    out.add('LPS', ngon_prism(star, .09, (0, 0, LAND)))
    out.add('GLD', ngon_prism([(cx + (x - cx) * .8, cy + (y - cy) * .8) for x, y in star], .11, (0, 0, LAND)))
    out.add('GLD', cyl(.6, .13, (cx, cy, LAND), seg=12))
    # anel concentrico (ouro-lapis-ouro) acompanhando o semicirculo, r=22
    for (ro, ri, m) in ((22.6, 22.1, 'GLD'), (22.1, 21.2, 'LPS'), (21.2, 20.9, 'GLD')):
        out.add(m, ring_prism(arc_pts(0, YT1, ro, 0, math.pi) + [(-ro, YT1 - .01)], arc_pts(0, YT1, ri, 0, math.pi) + [(-ri, YT1 - .01)], .08, (0, 0, LAND)))
    # painel do eixo: do medalhao ao pe da escada, com pontas ogivais
    pointed_panel(out, 0, YT1 + 1.0, cy - 6.6, 2.4, LAND + .02)
    # losangos radiais a 35 e 70 graus (r=14) e paineis menores nas diagonais externas (r=26)
    for a in (math.radians(35), math.radians(70), math.radians(110), math.radians(145)):
        lozenge(out, math.cos(a) * 14.5, YT1 + math.sin(a) * 14.5, a, 5.0, 1.8, LAND + .02)
    for a in (math.radians(20), math.radians(160)):
        lozenge(out, math.cos(a) * 26.5, YT1 + math.sin(a) * 26.5, a + math.pi / 2, 4.0, 1.4, LAND + .02)
    # postes no anel do patamar (pedestal baixo) + capim ao pe
    for s in (-1, 1):
        px, py = s * 21.0, YT1 + 19.0
        K.pedestal(out, (px, py, LAND), w=2.6, h=1.0)
        K.lamp_post(out, (px, py, LAND + 1.0), scale=.95)
        K.pampas(out, (px + s * 2.6, py + 1.4, LAND), h=2.2, seed=31 + s)
    # canteiros baixos junto do anel (assimetricos)
    for (px, py, rr, seed, big) in ((-13.0, YT1 + 26.0, 3.2, 41, True), (13.5, YT1 + 25.5, 2.6, 43, False)):
        pts = reg_poly(rr, 8, TAU / 16)
        out.add('SLT', ring_prism([(px + x, py + y) for x, y in reg_poly(rr + .6, 8, TAU / 16)], [(px + x, py + y) for x, y in pts], .9, (0, 0, LAND)))
        out.add('GRS', ngon_prism([(px + x, py + y) for x, y in pts], .7, (0, 0, LAND)))
        K.bush(out, (px, py, LAND + .7), r=1.8 if big else 1.3, seed=seed, mat='LFV', flowers='FLW', n_fl=8)
        K.pampas(out, (px + 1.4, py - 1.2, LAND + .7), h=1.8, seed=seed + 1)
    # escada frontal do patamar (LAND->PLAZA), 12 de largura
    n2 = 6
    for i in range(n2):
        r = (LAND - PLAZA) / n2
        out.add('FLL', box((12, 1.3, r), (0, YT1 + R_LAND + .6 + (i + .5) * 1.2, LAND - (i + 1) * r + r / 2)))
    # ---- canteiros do terraco (emolduram a torre) com alamos, capim e cobertura ----
    for (s, seeds, hs) in ((-1, (3, 4), (30, 24)), (1, (5, 6), (27, 22))):
        cxp, cyp = s * 24.0, YW + 8.0
        pts = reg_poly(5.6, 8, TAU / 16)
        out.add('SLT', ring_prism([(cxp + x, cyp + y) for x, y in reg_poly(6.2, 8, TAU / 16)], [(cxp + x, cyp + y) for x, y in pts], 1.1, (0, 0, TERR)))
        out.add('SLT', ring_prism([(cxp + x, cyp + y) for x, y in reg_poly(6.8, 8, TAU / 16)], [(cxp + x, cyp + y) for x, y in reg_poly(6.2, 8, TAU / 16)], .5, (0, 0, TERR)))
        out.add('GRS', ngon_prism([(cxp + x, cyp + y) for x, y in pts], .9, (0, 0, TERR)))
        K.poplar(out, (cxp - s * 1.6, cyp + 1.2, TERR + .9), h=hs[0], r=2.2, seed=seeds[0])
        K.poplar(out, (cxp + s * 2.2, cyp - 2.4, TERR + .9), h=hs[1], r=1.9, seed=seeds[1])
        K.bush(out, (cxp + s * 2.4, cyp + 2.8, TERR + .9), r=1.4, seed=seeds[0] + 10, mat='LFG', flowers=None)
        K.pampas(out, (cxp - s * 3.0, cyp - 1.6, TERR + .9), h=2.6, seed=seeds[1] + 10)
        K.ground_cover(out, (cxp + s * 8.0, cyp + 4.0, TERR), r=2.4, seed=seeds[0] + 20)
        # segundo alamo solto ao lado do canteiro (quebra a simetria)
        if s == -1:
            K.poplar(out, (cxp - 9.0, cyp - 3.0, TERR), h=26, r=2.0, seed=8)
        else:
            K.bush(out, (cxp + 8.5, cyp - 2.0, TERR), r=2.0, seed=9, mat='LFV', flowers='FLW')

# ================================================================ AGUA, ROCHAS, LIMITE
def water_and_rocks(out):
    for s in (-1, 1):
        x0, x1 = 34.0, 64.0
        y0, y1 = YT0, YT1 + R_LAND + 4.0       # -104 .. -56
        xc = s * (x0 + x1) / 2
        # margem externa CURVA: arco de raio ~44 centrado em (s*20, -80), do canto y0 ao canto y1.
        # para s=-1 os angulos ficam em torno de 180 graus: desembrulhar para nao varrer pelo lado errado
        ccx, ccy = s * 20.0, -80.0
        a0 = math.atan2(y0 - ccy, s * 40.0); a1 = math.atan2(y1 - ccy, s * 40.0)
        if s < 0 and a0 < 0: a0 += TAU
        def A(r): return arc_pts(ccx, ccy, r, a0, a1, 24)   # sempre de y0 (sul->norte? nao: de y0=-104 para y1=-56)
        # fundo com PROFUNDIDADE variavel: prateleira rasa junto ao patamar e ao muro, fundo escuro no meio
        out.add('RCK', box((x1 - x0, y1 - y0, .5), (xc, (y0 + y1) / 2, BASIN - .25)))
        out.add('RCK', box((3.0, y1 - y0, WATER - .35 - BASIN), (s * (x0 + 1.5), (y0 + y1) / 2, BASIN + (WATER - .35 - BASIN) / 2)))
        out.add('RCK', box((x1 - x0, 3.0, WATER - .5 - BASIN), (xc, y1 - 1.5, BASIN + (WATER - .5 - BASIN) / 2)))
        # muro externo curvo (ASH) + coping (SLT) + balaustrada; passeio externo em FLR ate x=78
        wall_in, wall_out = A(43.2), A(44.6)
        out.add('ASH', ring_prism(wall_out, wall_in, PLAZA - BASIN + .5, (0, 0, BASIN - .3)))
        out.add('SLT', ring_prism(A(45.0), A(43.0), .5, (0, 0, PLAZA)))
        for i in range(0, 24, 3):
            p1, p2 = wall_out[i], wall_out[min(i + 3, 24)]
            K.balustrade(out, p1, p2, PLAZA + .5, h=2.4)
        # passeio externo: regiao entre o arco (de y0 a y1) e a reta x=78 (poligono simples, sem cruzar)
        walk = wall_out + [(s * 78.0, y1), (s * 78.0, y0)]
        out.add('FLR', ngon_prism(walk, .5, (0, 0, PLAZA - .5)))
        # parede sul do espelho (reta) + coping
        out.add('ASH', box((x1 - x0 + 2, 1.2, PLAZA - BASIN + .5), (xc, y1 + .6, BASIN + (PLAZA - BASIN + .5) / 2 - .3)))
        out.add('SLT', box((x1 - x0 + 2.6, 1.8, .5), (xc, y1 + .6, PLAZA + .25), bevel=.1))
        # pedras: parte submersa, duas emergindo perto da margem
        rnd = random.Random(int(31 + s))
        for k in range(7):
            rx = s * (x0 + 4 + rnd.random() * (x1 - x0 - 10)); ry = y0 + 5 + rnd.random() * (y1 - y0 - 10)
            zr = BASIN + .4 + rnd.random() * 1.2
            K.rock(out, (rx, ry, zr), r=1.0 + rnd.random() * 1.3, seed=40 + k + int(s))
        K.rock(out, (s * (x0 + 5), y1 - 7, WATER - .3), r=1.7, seed=50 + int(s))
        K.rock(out, (s * (x1 - 8), y0 + 9, WATER - .5), r=1.4, seed=52 + int(s))
        # queda d'agua do muro do terraco: bica de pedra + lamina + espuma
        out.add('SLT', box((3.6, 1.8, .9), (s * 30, y0 + .3, TERR - 2.2), bevel=.1))
        out.add('SLT', box((.5, 1.4, 1.2), (s * 31.9, y0 + .5, TERR - 1.6)))
        out.add('SLT', box((.5, 1.4, 1.2), (s * 28.1, y0 + .5, TERR - 1.6)))
        out.add('WTR', box((3.0, .35, TERR - 2.6 - WATER), (s * 30, y0 + 1.15, WATER + (TERR - 2.6 - WATER) / 2)))
        out.add('FOAM', puff_cloud_xyzr([(s * 30 + dx, y0 + 1.6 + dy, WATER + .05, .9 + .3 * (k % 2)) for k, (dx, dy) in enumerate(((-1.2, 0), (0, .6), (1.2, 0), (0, -.2)))], 7))
        # capim e cobertura na margem externa
        K.pampas(out, (s * 66, y0 + 8, PLAZA), h=2.6, seed=61 + s); K.pampas(out, (s * 67, y1 - 10, PLAZA), h=2.2, seed=63 + s)
        K.ground_cover(out, (s * 68, (y0 + y1) / 2, PLAZA), r=2.0, seed=65 + s)
    # piso da praca no trecho + painel do eixo (nao uma faixa reta)
    out.add('FLR', box((66, 26, .5), (0, YT1 + R_LAND + 4.0 + 13, PLAZA - .25)))
    pointed_panel(out, 0, YT1 + R_LAND + 6.0, YT1 + R_LAND + 26.0, 2.6, PLAZA + .02)
    # limite do ambiente: rochedos claros + arvores verdes atras
    for i, (rx, ry, rr, rh) in enumerate([(-72, -156, 20, 24), (72, -156, 20, 24), (-18, -166, 16, 20), (22, -164, 15, 22), (-96, -124, 14, 28), (98, -122, 13, 30)]):
        out.add('RCK', lathe([(rr, 0), (rr * .95, rh * .35), (rr * .6, rh * .75), (rr * .25, rh)], (rx, ry, PLAZA - 6), seg=9))
        K.rock(out, (rx + rr * .7, ry + rr * .8, PLAZA), r=rr * .22, seed=60 + i)
    for i, (tx, ty, h) in enumerate([(-56, -140, 30), (60, -142, 27), (-32, -150, 25), (30, -152, 28), (-90, -104, 24), (92, -100, 22), (-46, -134, 20)]):
        K.poplar(out, (tx, ty, PLAZA), h=h, r=2.6, seed=70 + i, mat='LFV', mat2='LFV')

def puff_cloud_xyzr(centers, seed):
    from lvlib import puff_cloud
    return puff_cloud(centers, 1.0, seed=seed, seg=7)

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
