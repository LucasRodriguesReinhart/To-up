# lv10_block.py - ETAPA B: blockout (versao de trabalho) da composicao revisada do lobby.
# Volumes simples em clay, sem materiais luminosos. Serve para validar proporcoes/ocupacao,
# NAO e acabamento. Coordenadas ja na orientacao do Roblox: Blender +Y == Roblox +Z (saida),
# -Y == Forja. Blender +X == Roblox -X.  Z para cima. 1 unidade = 1 stud.
import bpy, bmesh, math, importlib, sys
sys.path.insert(0, r"C:\Users\lucas\OneDrive\Desktop\To up\lobby_area\blender")
import lvlib
importlib.reload(lvlib)
from lvlib import box, cyl, ball, lathe, ngon_prism, ring_prism, reg_poly, stairs, coll, clear_collection, B, _xform

TAU = math.tau
# ---- niveis (studs) ----
CORR = 0.0      # corredor / estrada para as ilhas
PLAZA = 2.0     # praca, boulevard, eixos
LAND = 5.0      # patamar do spawn (semicirculo, ref. imagem Tower)
TERR = 10.0     # terraco da Forja
WATER = 0.6
# ---- posicoes no eixo (Y blender == Z roblox) ----
Y_FACADE = -112.0   # plano da fachada da Forja
Y_STAIR0 = -100.0   # topo da escadaria (terraco)
Y_STAIR1 = -88.0    # pe da escadaria (patamar)
R_LAND = 30.0       # raio do semicirculo do patamar (centro em Y_STAIR1)
R_PLAZA = 42.0
R_CAN_IN, R_CAN_OUT, R_OUTER = 46.0, 72.0, 86.0
Y_GATE = 150.0

CLAY = {'CLAY': (200, 196, 188), 'CLAY2': (160, 158, 154), 'CLAYW': (90, 150, 190), 'CLAYG': (120, 160, 90), 'CLAYD': (110, 100, 92)}
for k, v in CLAY.items():
    lvlib.MATS[k] = v

def mats():
    return {k: lvlib._mat(k) for k in CLAY}

def build():
    root = coll('LV10_BLOCK')
    clear_collection(root)
    out = B('block', root, mats())
    A = out.add
    # ------------- plataforma geral (ilha) -------------
    A('CLAY2', box((300, 330, 6), (0, -5, -3.0)))                            # laje do sitio (topo 0 = fundo do canal)
    # nivel 2 (praca): octogono central, anel externo e o resto do sitio fora do anel (tiras + cantos)
    A('CLAY2', ring_prism(reg_poly(R_OUTER, 8, TAU/16), reg_poly(R_CAN_OUT, 8, TAU/16), PLAZA, (0, 0, 0)))
    F = R_OUTER * math.cos(TAU / 16)   # distancia das faces do octogono externo (79.5)
    A('CLAY2', box((300, 170 - F, PLAZA), (0, -5 - (170 - F) / 2 - F + 0, PLAZA / 2)))     # tira norte (Forja)
    A('CLAY2', box((300, 160 - F, PLAZA), (0, F + (160 - F) / 2, PLAZA / 2)))              # tira sul (portao)
    for s in (-1, 1):
        A('CLAY2', box((150 - F, 2 * F, PLAZA), (s * (F + (150 - F) / 2), 0, PLAZA / 2)))  # tiras leste/oeste
        for t in (-1, 1):
            A('CLAY2', box((60, 60, PLAZA - .02), (s * 80, t * 80, PLAZA / 2 - .01)))       # cantos
    # canal (agua) entre praca e anel externo
    A('CLAYW', ring_prism(reg_poly(R_CAN_OUT, 8, TAU/16), reg_poly(R_CAN_IN, 8, TAU/16), .3, (0, 0, WATER)))
    # rebaixo do canal (escava visualmente): paredes
    A('CLAY2', ring_prism(reg_poly(R_CAN_OUT + .6, 8, TAU/16), reg_poly(R_CAN_OUT - .4, 8, TAU/16), PLAZA - WATER + .2, (0, 0, WATER - .2)))
    A('CLAY2', ring_prism(reg_poly(R_CAN_IN + .4, 8, TAU/16), reg_poly(R_CAN_IN - .6, 8, TAU/16), PLAZA - WATER + .2, (0, 0, WATER - .2)))
    # praca central + medalhao (estrela) + 4 eixos cruzando o canal
    A('CLAY', ngon_prism(reg_poly(R_PLAZA, 8, TAU/16), .4, (0, 0, PLAZA)))
    A('CLAY', ngon_prism(reg_poly(14, 8, TAU/16), .8, (0, 0, PLAZA + .4)))
    A('CLAY', ngon_prism(reg_poly(6, 8, 0), 1.2, (0, 0, PLAZA + 1.2)))
    A('CLAYW', lathe([(2.2, 0), (1.4, 4), (.1, 8)], (0, 0, PLAZA + 2.4), seg=6))   # monumento de cristal (volume)
    A('CLAY', box((30, 2 * R_OUTER + 4, .6), (0, 0, PLAZA)))            # eixo N-S
    A('CLAY', box((2 * R_OUTER + 4, 18, .6), (0, 0, PLAZA)))            # eixo L-O
    # gazebos nas diagonais (ilhas no canal)
    for a in (TAU/8, 3*TAU/8, 5*TAU/8, 7*TAU/8):
        gx, gy = math.cos(a) * 59, math.sin(a) * 59
        A('CLAY', cyl(11, PLAZA - WATER + .6, (gx, gy, WATER - .2), seg=16))
        A('CLAY', cyl(9, .8, (gx, gy, PLAZA + .4), seg=16))
        for i in range(8):
            b = i / 8 * TAU
            A('CLAY', cyl(.5, 8, (gx + math.cos(b) * 6.5, gy + math.sin(b) * 6.5, PLAZA + 1.2), seg=8))
        A('CLAY', cyl(7.6, 1.2, (gx, gy, PLAZA + 9.2), seg=16))
        A('CLAYW', lathe([(7.0, 0), (6.2, 2.4), (4.2, 4.4), (1.2, 5.6), (0.05, 6.2)], (gx, gy, PLAZA + 10.4), seg=16))
    # ------------- patamar do spawn (semicirculo) + aneis + agua lateral -------------
    pts = [(math.cos(t / 24 * math.pi) * R_LAND, Y_STAIR1 + math.sin(t / 24 * math.pi) * R_LAND) for t in range(25)]
    pts = [(x, y) for (x, y) in pts]
    A('CLAY', ngon_prism(pts + [(-R_LAND, Y_STAIR1 - 14), (R_LAND, Y_STAIR1 - 14)], LAND - PLAZA, (0, 0, PLAZA)))
    for i, (rr, hh) in enumerate([(R_LAND + 2.2, 2.0), (R_LAND + 4.4, 1.0)]):
        pr = [(math.cos(t / 24 * math.pi) * rr, Y_STAIR1 + math.sin(t / 24 * math.pi) * rr) for t in range(25)]
        A('CLAY2', ngon_prism(pr + [(-rr, Y_STAIR1 - 14), (rr, Y_STAIR1 - 14)], hh, (0, 0, PLAZA)))
    A('CLAY', cyl(6.5, .3, (0, -66, LAND), seg=24))    # medalhao do spawn (0,5,-66)
    # espelhos d'agua flanqueando o patamar (entre semicirculo e alas)
    for s in (-1, 1):
        A('CLAY2', box((44, 40, 1.6), (s * 62, -92, PLAZA - 1.8)))          # borda
        A('CLAYW', box((40, 36, .3), (s * 62, -92, WATER)))
        for k in range(5):
            A('CLAY2', ball(1.6 + (k % 3) * .5, (s * (50 + k * 5.5), -80 - (k * 7) % 30, WATER - .4), seg=8))
    # ------------- escadaria monumental (LAND -> TERR) -------------
    n = 10
    rise = (TERR - LAND) / n
    run = (Y_STAIR1 - Y_STAIR0) / n
    for i in range(n):
        A('CLAY', box((26, run + .1, rise), (0, Y_STAIR1 - (i + .5) * run, LAND + i * rise + rise / 2)))
    for s in (-1, 1):
        A('CLAY', box((3.2, 14, TERR - LAND + 1.2), (s * 14.6, -94, LAND + (TERR - LAND) / 2)))   # bochechas
        A('CLAY', box((3.8, 3.8, 3.2), (s * 14.6, -87.5, LAND + 1.6)))   # pedestais no pe
        A('CLAYG', ball(2.6, (s * 14.6, -87.5, LAND + 5.2), seg=8))      # urna com arbusto dourado
        A('CLAY', cyl(.5, 11, (s * 20, -84, LAND), seg=8))               # postes no pe da escada
        A('CLAY', ball(1.1, (s * 20, -84, LAND + 11.5), seg=8))
        A('CLAY', cyl(.5, 11, (s * 26, -64, LAND), seg=8))               # postes no anel do patamar
        A('CLAY', ball(1.1, (s * 26, -64, LAND + 11.5), seg=8))
    # ------------- terraco da Forja -------------
    A('CLAY', box((120, 14, TERR - PLAZA), (0, Y_FACADE + 6, PLAZA + (TERR - PLAZA) / 2)))
    A('CLAY', box((120, 12, TERR - PLAZA), (0, Y_STAIR0 + 6 - 12, PLAZA + (TERR - PLAZA) / 2)))
    # ------------- Forja: torre alta + alas (ref. Tower) -------------
    TW, TD = 40, 30
    H1, H2, H3 = 24, 30, 20            # arcada terrea, tier ogival, tier alto + coroa
    yc = Y_FACADE - TD / 2
    A('CLAYD', box((TW, TD, H1), (0, yc, TERR + H1 / 2)))
    A('CLAY', box((TW + 2.4, TD + 2.4, 1.6), (0, yc, TERR + H1 + .8)))                   # cornija 1
    A('CLAYD', box((TW - 1.5, TD - 1.5, H2), (0, yc, TERR + H1 + 1.6 + H2 / 2)))
    A('CLAY', box((TW + 1.2, TD + 1.2, 1.8), (0, yc, TERR + H1 + H2 + 2.5)))             # cornija 2
    A('CLAYD', box((TW - 4, TD - 4, H3), (0, yc, TERR + H1 + H2 + 3.4 + H3 / 2)))
    A('CLAY', ngon_prism(reg_poly(14, 8, TAU/16), 3, (0, yc, TERR + H1 + H2 + H3 + 3.4)))
    A('CLAYW', lathe([(12, 0), (10.5, 4), (6.5, 8), (1.5, 10.5), (0.05, 11)], (0, yc, TERR + H1 + H2 + H3 + 6.4), seg=16))
    A('CLAY', lathe([(1.2, 0), (0.05, 9)], (0, yc, TERR + H1 + H2 + H3 + 17), seg=8))
    # vao central (recesso da forja, onde fica o Ignis ~16 studs) e vaos laterais
    A('CLAYD', box((16, 12, 20), (0, Y_FACADE - 6, TERR + 10)))
    # pilastras da fachada (relevo real)
    for x in (-19, -9, 9, 19):
        A('CLAY', box((2.6, 2.4, H1 + H2 + 1.6), (x, Y_FACADE - 1.1, TERR + (H1 + H2 + 1.6) / 2)))
    # alas: dois pavimentos com arcadas, mais baixas
    for s in (-1, 1):
        xw = s * 41
        A('CLAYD', box((42, 24, 16), (xw, Y_FACADE - 12, TERR + 8)))
        A('CLAY', box((43, 25, 1.4), (xw, Y_FACADE - 12, TERR + 16.7)))
        A('CLAYD', box((38, 20, 10), (xw, Y_FACADE - 13, TERR + 17.4 + 5)))
        A('CLAY', box((39, 21, 1.2), (xw, Y_FACADE - 13, TERR + 33)))
        for k in range(4):
            A('CLAY', box((2.2, 2.0, 16), (xw - 15 + k * 10, Y_FACADE - .9, TERR + 8)))
        # torre de canto com cupula pequena
        A('CLAYD', cyl(5, 30, (s * 64, Y_FACADE - 4, TERR), seg=12))
        A('CLAYW', lathe([(5.4, 0), (4.4, 2.4), (2, 4.4), (.05, 5.4)], (s * 64, Y_FACADE - 4, TERR + 30), seg=12))
    # ------------- limite do ambiente: rochedos + arvores altas atras/ao lado -------------
    for i, (rx, ry, rr, rh) in enumerate([(-75, -150, 22, 26), (75, -150, 22, 26), (-118, -118, 18, 34), (118, -118, 18, 34), (-135, -60, 16, 22), (135, -60, 16, 22), (-140, 20, 16, 20), (140, 20, 16, 20), (-120, 110, 18, 18), (120, 110, 18, 18)]):
        A('CLAY2', lathe([(rr, -6), (rr * .92, rh * .45), (rr * .55, rh * .85), (rr * .2, rh)], (rx, ry, PLAZA - 2), seg=10))
    for i, (tx, ty) in enumerate([(-30, -132), (30, -132), (-70, -100), (70, -100), (-96, -70), (96, -70), (-100, 60), (100, 60), (-40, 118), (40, 118)]):
        h = 22 + (i % 3) * 4
        A('CLAY2', cyl(.8, h * .45, (tx, ty, PLAZA), seg=6))
        for k in range(6):
            zz = PLAZA + h * .35 + k * (h * .11)
            rr = 3.6 * (1 - k / 7.5)
            A('CLAYG', ball(rr, (tx, ty, zz), seg=8, scl=(1, 1, 1.4)))
    # ------------- boulevard sul + portao + escada para o corredor -------------
    A('CLAY', box((30, 100, .6), (0, 100, PLAZA)))
    for s in (-1, 1):
        A('CLAYW', box((22, 90, .3), (s * 30, 96, WATER)))
        A('CLAY2', box((24, 92, 1.4), (s * 30, 96, PLAZA - 1.9)))
        for yy in range(60, 141, 20):
            A('CLAY', cyl(.5, 10, (s * 17, yy, PLAZA), seg=8))
            A('CLAY', ball(1.0, (s * 17, yy, PLAZA + 10.5), seg=8))
        A('CLAYD', box((10, 10, 26), (s * 22, Y_GATE, PLAZA + 13)))
        A('CLAY', lathe([(6, 0), (3, 3), (.05, 7)], (s * 22, Y_GATE, PLAZA + 26), seg=8))
    A('CLAYD', box((34, 6, 6), (0, Y_GATE, PLAZA + 25)))
    n = 4
    for i in range(n):
        A('CLAY', box((34, 4.1, .5), (0, Y_GATE + 8 + (i + .5) * 4, PLAZA - (i + .5) * .5)))
    A('CLAY2', box((92, 60, 3), (0, Y_GATE + 56, CORR - 1.5)))   # inicio da estrada do corredor
    # ------------- edificios laterais (Santuario -X blender / Loja +X blender) -------------
    for s, w in ((-1, 60), (1, 40)):
        A('CLAYD', box((22, w, 16), (s * 126, 0, PLAZA + 8)))
        A('CLAY', box((23, w + 1, 1.4), (s * 126, 0, PLAZA + 16.7)))
        for k in range(int(w // 10)):
            A('CLAY', box((2.0, 2.2, 16), (s * 115.5, -w / 2 + 5 + k * 10, PLAZA + 8)))
    objs = out.finish(uv_world=())
    return objs

if __name__ == '__main__' or True:
    objs = build()
    print('blockout', len(objs), 'objetos')
