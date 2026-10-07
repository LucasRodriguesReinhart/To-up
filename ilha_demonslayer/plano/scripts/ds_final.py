# ds_final.py - numeros do plano (imprime): encaixe, folgas, marcadores em Roblox, rotas, minerios
import sys, math
sys.dont_write_bytecode = True
from ds_geo import *
W = world_polys()
i1, i2, s3 = G.i1_polys(), G.i2_polys(), sg_polys()
p0 = rbx(*PREV)
print("WORLD_FROM_PREV local", PREV, "-> roblox (%.2f, %.2f) ancora (%.2f, %.2f)" % (p0[0], p0[1], A_RBX[0], A_RBX[2]))
f = dir_rbx(0, 1); r = dir_rbx(1, 0)
print("local +Y -> roblox fwd (%.4f, %.4f) ; +X (direita) -> (%.4f, %.4f)" % (f + r))
def R(name, x, y, z, extra=""):
    q = rbx(x, y); print("%-34s local (%7.1f,%7.1f,%6.1f)  roblox (%9.2f, %6.2f, %8.2f) %s" % (name, x, y, z, q[0], z, q[1], extra))
R("WORLD_FROM_PREV", *PREV, DECK)
R("TORII_IN", *TORII_IN, T0)
R("WORLD_ENTRY_DemonSlayer", 0.0, 22.0, T0 + 0.2)
R("MiningZone centro", *MINE_C, T1)
R("SUMMON_Main (torre)", *SUMMON_TOWER, T3)
R("Forja boca da fornalha", FURNACE_MOUTH[0], FURNACE_MOUTH[1], T4)
R("Torre-chamine", 37.0, 493.0, T4)
R("TORII_OUT", *TORII_OUT, T4)
R("ISLAND_EXIT_DemonSlayer", *EXIT_START, T4)
g = gate_op(); R("GATE_OnePiece", g[0], g[1], T4)
a, d = anchor_op()
print("ISLAND_NEXT_ANCHOR_OnePiece roblox (%.2f, %.2f, %.2f) fwd (%.4f, 0, %.4f)" % (a[0], T4, a[1], d[0], d[1]))
print("  heading_deg roblox atan2(-z, x) = %.1f ; rumo atan2(z,x)=%.1f" % (math.degrees(math.atan2(-d[1], d[0])), math.degrees(math.atan2(d[1], d[0]))))
L0 = (0.0, -177.0); rad = (a[0] - L0[0], a[1] - L0[1]); n = math.hypot(*rad)
dev = math.degrees(math.acos((rad[0] * d[0] + rad[1] * d[1]) / n))
print("  desvio do radial lobby->ancora: %.1f graus; distancia ao centro do lobby %.0f" % (dev, n))
# espaco da area 5: disco r 300 a 350 a frente
c5 = (a[0] + d[0] * 350, a[1] + d[1] * 350)
disk = G.circle(c5, 300, 48)
print("  disco area 5 centro (%.0f, %.0f): folga ate Ilha 3 %.0f, Ilha 2 %.0f, Ilha 1 %.0f, picos %.0f, Ilha 4 %.0f" % (
    c5[0], c5[1], G.poly_dist(disk, s3['rim']), G.poly_dist(disk, i2['rim']), G.poly_dist(disk, i1['rim']),
    G.poly_dist(disk, G.LOBBY['picos']), G.poly_dist(disk, W['rim'])))
rim = W["rim"]
xs = [p[0] for p in rim]; zs = [p[1] for p in rim]
print("bbox rim Ilha4 roblox x %.0f..%.0f z %.0f..%.0f centro (%.0f, %.0f)" % (min(xs), max(xs), min(zs), max(zs), (min(xs)+max(xs))/2, (min(zs)+max(zs))/2))
lx = [p[0] for p in RIM]; ly = [p[1] for p in RIM]
print("planta local x %.0f..%.0f (%.0f) y %.0f..%.0f (%.0f) area %.0f studs2 ; razao %.2f" % (min(lx), max(lx), max(lx)-min(lx), min(ly), max(ly), max(ly)-min(ly), area(RIM), (max(ly)-min(ly))/(max(lx)-min(lx))))
print("clareira area %.0f ; MiningZone %.0f x %.0f = %.0f" % (area(CLEARING), MINE_RECT[2]-MINE_RECT[0], MINE_RECT[3]-MINE_RECT[1], (MINE_RECT[2]-MINE_RECT[0])*(MINE_RECT[3]-MINE_RECT[1])))
print("FOLGAS (sem ilhotas):")
for nm, A_ in (("rim", rim), ("ponte saida", W["bridge_out"]), ("cabeceira", W["pier"])):
    print("  %-12s -> SG rim %.0f | SG ilhota %.0f | SG ponte saida %.0f | Ilha 2 %.0f | Ilha 1 %.0f | picos lobby %.0f | montanhas %.0f" % (
        nm, G.poly_dist(A_, s3['rim']), G.poly_dist(A_, s3['islet']), G.poly_dist(A_, s3['bridge']), G.poly_dist(A_, i2['rim']),
        G.poly_dist(A_, i1['rim']), G.poly_dist(A_, G.LOBBY['picos']), G.poly_dist(A_, G.LOBBY['montanhas'])))
print("  ponte chegada -> SG rim %.0f, -> SG ilhota %.0f (encosta na ancora: esperado 0)" % (G.poly_dist(W['bridge_in'], s3['rim']), G.poly_dist(W['bridge_in'], s3['islet'])))
# distancia do mar FAR_GROUND da Ilha 1 (x -1024..1024)
print("  borda leste da Ilha 4 (x max) %.0f vs fim do mar da Ilha 1 x -1024" % max(xs))
print("ESCADAS:")
for n, (fx, fy), deg, w, k, rise, tread, z in STAIRS:
    t = stair_top(n); print("  %-12s pe (%6.1f,%6.1f,%5.1f) topo (%6.1f,%6.1f,%5.1f) larg %4.1f %2d x %.3f piso %.2f" % (n, fx, fy, z, t[0], t[1], t[2], w, k, rise, tread))
print("ROTAS (comprimento em planta, tempo a 16 studs/s):")
for k, v in ROUTES.items():
    L_ = plen(v); print("  %-30s %5.0f  %4.1f s" % (k, L_, L_ / 16.0))
pts, step = ore_points()
from collections import Counter
print("ORE: %d pontos, passo %.1f, %s" % (len(pts), step, dict(Counter(p[0] for p in pts))))
for nm, t, x, y, w, dd, deg, z in HOUSES:
    R("casa %s %s" % (nm, t), x, y, z)
