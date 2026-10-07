import math, json
from geo import *
YAW, R, S, EXD = 100.0, 160.0, 140.0, 120.0
F = Fit(YAW, R, S, EXD)
i1 = i1_polys(); i2 = i2_polys()
P = F.polys()
out = {}
p0 = F.local_of_bl(A_RBX[0], -A_RBX[1])
print("WORLD_FROM_PREV local", [round(v,2) for v in p0], "len %.1f turn %.1f arc %.1f"%(F.length, F.turn, F.arc_len))
print("bridge local", [tuple(round(v,1) for v in F.local_of_bl(*q)) for q in F.bridge_bl])
# check round trip
print("check A", [round(v,2) for v in F.rbx(*p0)])
def R3(name, x, y, z):
    r = F.rbx(x, y); print("%-34s local (%7.1f,%7.1f,%6.1f)  roblox (%8.1f, %6.1f, %7.1f)"%(name, x, y, z, r[0], z, r[1]))
R3("WORLD_ENTRY_ShadowGarden", 0, -268, P1+0.2)
R3("praca/fonte", *PLAZA_C, P1)
R3("SUMMON_Main", -216, -222, SUM)
R3("CRAFT_Station", *CRAFT_C, P2)
R3("porta do castelo", 0, FACADE_Y, P3)
R3("MiningZone centro", 0, 148, P3)
R3("THRONE_Interact", 0, 286, P3+2.4)
R3("THRONE rest", 0, 294, P3+2.4)
R3("THRONE_Park", 27.5, 294, P3+2.4)
R3("THRONE_Stair_Top", 0, 306, P3+2.4)
R3("escada fundo (galeria)", 0, 306, CAVE_GALLERY)
R3("DUNGEON_Hall (portal)", *CAVE_PORTAL, CAVE_FLOOR+1.6)
R3("DUN_ROOM_R1", 0, 48, DUN_Z); R3("DUN_ROOM_R2", 0, 144, DUN_Z); R3("DUN_ROOM_R3", 0, 250, DUN_Z)
R3("ISLAND_EXIT_ShadowGarden", *EXIT_START, P3)
a4, d4 = F.anchor4(); print("ISLAND_NEXT_ANCHOR_DemonSlayer roblox (%.1f, %.1f, %.1f) fwd (%.4f, 0, %.4f) heading_deg %.1f"%(a4[0], P3, a4[1], d4[0], d4[1], math.degrees(math.atan2(-d4[1], d4[0]))))
ux, uy = exit_dir_local(EXD)
g = (EXIT_START[0]+ux*(64+12), EXIT_START[1]+uy*(64+12)); R3("GATE_DemonSlayer", g[0], g[1], P3)
print("i2 fwd heading at A (deg, Roblox atan2(-z,x))", round(math.degrees(math.atan2(0.3907, -0.9205)),1))
rim = P['rim']
print("distancias: rim-i2rim %.0f rim-i2islet %.0f rim-i2bridge %.0f rim-i1 %.0f rim-picos %.0f rim-montanhas %.0f"%(poly_dist(rim,i2['rim']),poly_dist(rim,i2['islet']),poly_dist(rim,i2['bridge']),poly_dist(rim,i1['rim']),poly_dist(rim,LOBBY['picos']),poly_dist(rim,LOBBY['montanhas'])))
print("praca->i2rim %.0f ; ponte chegada -> picos %.0f ; saida/ilhota -> i2 %.0f"%(min(segd(F.rbx(*PLAZA_C), i2['rim'][k], i2['rim'][(k+1)%len(i2['rim'])]) for k in range(len(i2['rim']))), poly_dist(P['arrival'], LOBBY['picos']), multi_dist([P['islet'],P['exit_bridge']],[i2['rim'],i2['islet']])))
xs=[p[0] for p in rim]; zs=[p[1] for p in rim]
print("bbox novo rim x %.0f..%.0f z %.0f..%.0f centro (%.0f, %.0f)"%(min(xs),max(xs),min(zs),max(zs),(min(xs)+max(xs))/2,(min(zs)+max(zs))/2))
o3=i3_old_polys(); print("old rim-i2 %.0f old rim-picos %.0f"%(poly_dist(o3['rim'],i2['rim']),poly_dist(o3['rim'],LOBBY['picos'])))
# area em planta
def area(P): return abs(sum(P[i][0]*P[(i+1)%len(P)][1]-P[(i+1)%len(P)][0]*P[i][1] for i in range(len(P))))/2
print("area planta nova %.0f  antiga %.0f"%(area(RIM), area(SG.ISLAND_RIM)))
