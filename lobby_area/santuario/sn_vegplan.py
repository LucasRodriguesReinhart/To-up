# sn_vegplan.py - ONDE vai cada arvore/arbusto (sem bpy): bosques emoldurando as estacoes, nunca na frente delas.
# Regras: fora das zonas de exclusao (praca, estrados, loja, tabuas, spawn, avenida, forja, bigorna, martelo, trilhas);
# pinheiros no fundo (borda do plato e atras dos portais), carvalhos no meio, alguns dourados para cor, arbustos
# floridos na beira das trilhas; ARVORE ANCIA a sudoeste da forja abracando ruinas (marco secundario).
import math
import random

import sn_layout as L


def _in_poly(x, z, poly):
    ins = False
    n = len(poly)
    for i in range(n):
        x1, z1 = poly[i]
        x2, z2 = poly[(i + 1) % n]
        if (z1 > z) != (z2 > z) and x < (x2 - x1) * (z - z1) / (z2 - z1 + 1e-12) + x1:
            ins = not ins
    return ins


def _edge_dist(x, z, poly):
    best = 1e9
    n = len(poly)
    for i in range(n):
        x1, z1 = poly[i]
        x2, z2 = poly[(i + 1) % n]
        dx, dz = x2 - x1, z2 - z1
        t = max(0.0, min(1.0, ((x - x1) * dx + (z - z1) * dz) / (dx * dx + dz * dz + 1e-12)))
        best = min(best, math.hypot(x - (x1 + t * dx), z - (z1 + t * dz)))
    return best


def keepout():
    """zonas proibidas: circulos (x, z, r) e retangulos (x0, x1, z0, z1)"""
    circ = [(L.C[0], L.C[1], L.PLAZA_R + 6.0)]
    for i in range(len(L.PORTALS)):
        (x, z), (fx, fz) = L.portal_pos(i)
        circ.append((x, z, 21.0))
        # corredor de chegada ao estrado (da praca ate o portal)
        for t in (0.25, 0.5, 0.75):
            circ.append((x + fx * 18 * t + fx * 4, z + fz * 18 * t + fz * 4, 7.0))
    sx, sz = L.SHOP_C
    circ.append((sx, sz, 26.0))
    rx, rz = L.RANK_O
    fx, fz = L.RANK_FACE
    for t in (-24, -12, 0, 12, 24):
        circ.append((rx - fz * t + fx * 2, rz + fx * t + fz * 2, 13.0))
    circ.append((rx + fx * 12, rz + fz * 12, 12.0))
    circ.append((L.HAMMER["head"][0], L.HAMMER["head"][1], 30.0))
    circ.append((L.FORGE_C[0], L.FORGE_C[1], 26.0))
    # ilha dos portais: patio + anel interno livres; corredor da ponte nas duas cabeceiras; trilha oeste do plato
    ix, iz = L.PORTAL_ISLE_C
    circ.append((ix, iz, L.PORTAL_R - 12.0))
    bz = L.ISLE_BRIDGE["z"]
    for t in (0.2, 0.4, 0.6, 0.8):
        circ.append((L.ISLE_BRIDGE["x_main"] * t + (-L.PLAZA_R) * (1 - t), bz * t, 7.0))
    circ.append((L.RUIN_HEAD[0], L.RUIN_HEAD[1], 14.0))
    for (x, z, yaw) in L.RUIN_ARCHES:
        circ.append((x, z, 10.0))
    for (x, z, m, sc) in L.RUIN_CRYSTALS:
        circ.append((x, z, 5.0 * sc))
    for (xa, za, xc, zc) in L.RUIN_WALLS:
        for t in (0.0, 0.25, 0.5, 0.75, 1.0):
            circ.append((xa + (xc - xa) * t, za + (zc - za) * t, 5.0))
    for i in range(18):
        a = math.radians(i * 20.0 + 5.0)
        circ.append((47.0 * math.cos(a), 47.0 * math.sin(a), 3.5))
    rect = [(-28.0, 28.0, 40.0, 84.0),                      # terraco do spawn + escada
            (-14.0, 14.0, 80.0, 152.0),                     # avenida + portao
            (L.ANVIL_PLINTH[0] - 6, L.ANVIL_PLINTH[1] + 6, L.ANVIL_PLINTH[2] - 6, L.ANVIL_PLINTH[3] + 8),
            (-20.0, 20.0, -92.0, -36.0)]                    # canal de lava / forja
    rect.append((L.ISLE_BRIDGE["x_isle"] - 30.0, L.ISLE_BRIDGE["x_main"] + 22.0, bz - 10.0, bz + 10.0))
    # trilhas da praca ate a loja e as tabuas
    for (tx, tz) in (L.SHOP_C, L.RANK_O):
        for t in (0.55, 0.7, 0.85):
            circ.append((tx * t, tz * t, 7.0))
    return circ, rect


def land_of(x, z):
    for (nm, poly, c) in L.LANDS:
        if _in_poly(x, z, poly):
            return poly
    return None


def edge_dist(x, z):
    p = land_of(x, z)
    return _edge_dist(x, z, p) if p else -1.0


def free(x, z, margin=0.0):
    p = land_of(x, z)
    if p is None or _edge_dist(x, z, p) < 5.0:
        return False
    circ, rect = keepout()
    for (cx, cz, r) in circ:
        if math.hypot(x - cx, z - cz) < r + margin:
            return False
    for (x0, x1, z0, z1) in rect:
        if x0 - margin < x < x1 + margin and z0 - margin < z < z1 + margin:
            return False
    return True


ANCIENT = (-96.0, -112.0)          # arvore ancia: a oeste do plinto da bigorna, atras do martelo


def open_lawn(x, z):
    """gramados que ficam LIVRES de arvores (linhas de visada da praca/spawn para portais, loja e tabuas)"""
    r = math.hypot(x - L.C[0], z - L.C[1])
    a = math.degrees(math.atan2(z - L.C[1], x - L.C[0])) % 360
    if 40.0 < r < 70.0 and 160.0 < a < 190.0:        # vista da praca para a ponte da ilha dos portais
        return True
    if 40.0 < r < 66.0 and (a > 312.0 or a < 72.0):
        return True
    if 40.0 < r < 84.0 and 14.0 < a < 66.0:          # frente das Tabuas dos Campeoes
        return True
    if 40.0 < r < 70.0 and 318.0 < a < 352.0:        # frente da loja
        return True
    return False


def spots(seed=11):
    r = random.Random(seed)
    out = {}
    pts = []
    # amostragem com distancia minima (bosques: 9..13 studs entre troncos)
    tries = 0
    while tries < 14000 and len(pts) < 124:
        tries += 1
        x, z = r.uniform(-310, 150), r.uniform(-164, 150)
        if not free(x, z, 1.5):
            continue
        dmin = 10.5 if edge_dist(x, z) < 30 else 13.0
        if any(math.hypot(x - a, z - b) < dmin for (a, b) in pts):
            continue
        if math.hypot(x - ANCIENT[0], z - ANCIENT[1]) < 30 or open_lawn(x, z):
            continue
        pts.append((x, z))
    for (x, z) in pts:
        e = edge_dist(x, z)
        north = z < -70
        if e < 22 or north:
            nm = r.choice(["pine1", "pine1", "pine2", "oak1"])
        else:
            nm = r.choice(["oak1", "oak2", "oak3", "oak1", "oak2", "oakG", "pine2"])
        out.setdefault(nm, []).append((x, z, L.Y_GRASS, r.uniform(0, 360), r.uniform(0.85, 1.18)))
    # arbustos: beira das trilhas e dos estrados, em grupinhos
    bushes = []
    tries = 0
    while tries < 6000 and len(bushes) < 90:
        tries += 1
        x, z = r.uniform(-305, 140), r.uniform(-150, 140)
        if not free(x, z, -3.5) or free(x, z, 0.5):
            continue                                    # so na faixa de 0..3,5 studs em volta das zonas
        if any(math.hypot(x - a, z - b) < 4.5 for (a, b) in bushes):
            continue
        if any(math.hypot(x - L.portal_pos(i)[0][0], z - L.portal_pos(i)[0][1]) < 27 for i in range(len(L.PORTALS))):
            continue
        bushes.append((x, z))
    for (x, z) in bushes:
        out.setdefault(r.choice(["bush1", "bushF", "bushF"]), []).append(
            (x, z, L.Y_GRASS, r.uniform(0, 360), r.uniform(0.8, 1.35)))
    out["ancient"] = [(ANCIENT[0], ANCIENT[1], L.Y_GRASS, 30.0, 1.0)]
    return out


if __name__ == "__main__":
    s = spots()
    print({k: len(v) for k, v in s.items()})
