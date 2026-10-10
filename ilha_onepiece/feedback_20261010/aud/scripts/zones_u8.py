# zones_u8.py - agrupa as celulas U8 (alcancaveis, sem colisao) por ZONA semantica + categoria
import sys, json, math, collections
sys.dont_write_bytecode = True
import numpy as np
PROJ = r"C:/Users/lucas/OneDrive/Desktop/To up/ilha_onepiece"
sys.path.insert(0, PROJ)
import op_layout as L

g = np.load("grid.npz")
mk = np.load("u8_masks.npz")
meta = json.load(open("meta.json"))
xs, ys, zv, zcb, vo, vm = g["xs"], g["ys"], g["zv"], g["zcb"], g["vo"], g["vm"]
hit, cat = mk["hit"], mk["cat"]
CATN = {1: "chao", 2: "telhado", 3: "copa", 0: "outro"}
ST = 1.5


def near_poly(x, y, pts, r):
    return L.polyline_dist(x, y, [(p[0], p[1]) for p in pts]) <= r


def zone(x, y, z):
    if -179.5 <= x <= -168.5 and 50.0 <= y <= 302.0:
        return "canal_oeste"
    if near_poly(x, y, L.CANAL_E, 6.0) or L.point_in_poly(x, y, L.BASIN):
        return "canal_leste+bacia"
    for nm, poly, zz in L.ROCKS:
        if L.point_in_poly(x, y, poly):
            if nm in ("NERocksW", "NERocksE", "BackE", "CastleFootE"):
                return "montanha_NE(" + nm + ")"
            if nm in ("CastleFootW", "ButtressL", "ButtressR", "BackW", "BackN"):
                return "rochedo_castelo(" + nm + ")"
            return "rocha_" + nm
    if L.point_in_poly(x, y, L.SKULL_ROCK):
        return "caveira/promontorio"
    f = L.floor_name(x, y)
    if f:
        return "sobre_piso_" + f
    if L.point_in_poly(x, y, L.SHIP_DECK) or (236 <= x <= 262 and 100 <= y <= 200):
        return "navio"
    # faixas de borda sem piso por setor
    if y < 45:
        return "borda_sul(entrada/frente)"
    if x < -178:
        return "borda_oeste(lobo SO/W2b/W3)"
    if x > 200 and y < 280:
        return "borda_leste(porto/summon)"
    if x > 200:
        return "borda_NE(promontorio/caveira)"
    if y > 330:
        return "borda_castelo"
    return "outro_sem_piso"


if __name__ == '__main__':
    exec(open('zones_u8_main.py', encoding='utf-8').read())
