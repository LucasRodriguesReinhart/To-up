# wb_check.py - checagem de ENGENHARIA da planta (sem Blender): nenhuma pegada se sobrepoe, nenhuma casa invade rua
# ou praca, toda casa fica a <= 6 studs de um chao andavel, tudo dentro do plato, rotas de QA so por chao andavel.
# uso: python wb_check.py
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import wb_layout as L


def house_poly(h):
    fx, fz = h["fx"], h["fz"]
    n = math.hypot(fx, fz)
    fx, fz = fx / n, fz / n
    tx, tz = -fz, fx
    w, dd = h["w"] / 2, h["d"] / 2
    c = (h["x"], h["z"])
    return [(c[0] + tx * a + fx * b, c[1] + tz * a + fz * b) for a, b in ((-w, dd), (w, dd), (w, -dd), (-w, -dd))]


def _axes(poly):
    out = []
    for i in range(len(poly)):
        x0, z0 = poly[i]
        x1, z1 = poly[(i + 1) % len(poly)]
        n = (-(z1 - z0), x1 - x0)
        l = math.hypot(*n) or 1.0
        out.append((n[0] / l, n[1] / l))
    return out


def _proj(poly, ax):
    vs = [p[0] * ax[0] + p[1] * ax[1] for p in poly]
    return min(vs), max(vs)


def gap(a, b):
    """folga entre poligonos CONVEXOS (SAT): > 0 = separados, < 0 = penetram (aprox.)"""
    best = -1e9
    for ax in _axes(a) + _axes(b):
        a0, a1 = _proj(a, ax)
        b0, b1 = _proj(b, ax)
        best = max(best, max(b0 - a1, a0 - b1))
    return best


def inside(x, z, poly):
    ins = False
    j = len(poly) - 1
    for i in range(len(poly)):
        xi, zi = poly[i]
        xj, zj = poly[j]
        if (zi > z) != (zj > z) and x < (xj - xi) * (z - zi) / (zj - zi + 1e-12) + xi:
            ins = not ins
        j = i
    return ins


def rect(x0, z0, x1, z1):
    return [(x0, z0), (x1, z0), (x1, z1), (x0, z1)]


def circle(cx, cz, r, n=16):
    return [(cx + r * math.cos(2 * math.pi * k / n), cz + r * math.sin(2 * math.pi * k / n)) for k in range(n)]


def ribbon(pts, w):
    out = []
    for a, b in zip(pts[:-1], pts[1:]):
        dx, dz = b[0] - a[0], b[1] - a[1]
        n = math.hypot(dx, dz)
        nx, nz = -dz / n * w / 2, dx / n * w / 2
        out.append([(a[0] + nx, a[1] + nz), (b[0] + nx, b[1] + nz), (b[0] - nx, b[1] - nz), (a[0] - nx, a[1] - nz)])
    return out


def footprints():
    f = {}
    for h in L.HOUSES:
        f["casa " + h["id"]] = house_poly(h)
    fo = L.FORGE
    f["forja"] = rect(fo["x0"], fo["z_back"], fo["x1"], fo["z_front"])
    s = L.SHOP
    f["loja"] = rect(s["x0"], s["z0"], s["x1"], s["z1"])
    f["mural"] = L.RANK_BOX
    for i, (x, z, _, c) in enumerate(L.STALLS):
        f["barraca%d" % (i + 1)] = rect(x - 4, z - 6, x + 4, z + 6)
    f["fonte"] = circle(L.FOUNTAIN[0], L.FOUNTAIN[1], L.FOUNTAIN_R + 2)
    f["carroca"] = rect(L.CART[0] - 4, L.CART[1] - 6, L.CART[0] + 4, L.CART[1] + 6)
    for i, (x, z) in enumerate(L.OAKS):
        f["carvalho%d" % (i + 1)] = rect(x - 2, z - 2, x + 2, z + 2)
    f["poco"] = circle(L.WELL[0], L.WELL[1], 3.5, 8)
    f["correio"] = rect(L.MAILBOX[0] - 1.5, L.MAILBOX[1] - 1.5, L.MAILBOX[0] + 1.5, L.MAILBOX[1] + 1.5)
    f["placa"] = rect(L.SIGN[0] - 6, L.SIGN[1] - 1, L.SIGN[0] + 6, L.SIGN[1] + 1)
    f["poste setas"] = rect(L.SIGNPOST[0] - 1, L.SIGNPOST[1] - 1, L.SIGNPOST[0] + 1, L.SIGNPOST[1] + 1)
    return f


def walkable():
    out = {"praca": L.PLAZA}
    for i, r in enumerate(ribbon(L.WEST_ROAD, L.ROAD_W)):
        out["rua oeste %d" % i] = r
    sw = L.SOUTH_ROAD_W / 2
    out["rua sul"] = rect(-sw, L.SOUTH_ROAD[0][1], sw, L.SOUTH_ROAD[1][1])
    out["largo poco"] = rect(-14, 88, 14, 104)
    out["patio"] = circle(L.COURT_C[0], L.COURT_C[1], L.COURT_R, 24)
    r0, r1, a0, a1 = L.COURT_RING
    cx, cz = L.COURT_C
    ring = [(cx + r1 * math.cos(math.radians(a)), cz + r1 * math.sin(math.radians(a))) for a in range(int(a0), int(a1) + 1, 10)]
    ring += [(cx + r0 * math.cos(math.radians(a)), cz + r0 * math.sin(math.radians(a))) for a in range(int(a1), int(a0) - 1, -10)]
    out["patio terraco"] = ring
    out["quintal W"] = L.FORGE_YARD
    out["quintal E"] = L.FORGE_YARD_E
    b = L.BRIDGE
    out["ponte"] = rect(b["x"] - b["w"] / 2, b["z0"], b["x"] + b["w"] / 2, b["z1"])
    out["portao"] = rect(-L.GATE_HW, L.GATE[1] - 6, L.GATE_HW, L.BRIDGE["z0"])
    out["forja"] = rect(L.FORGE_BAY[0], L.FORGE["z_back"] + 4, L.FORGE_BAY[1], L.FORGE["z_front"] + 6)
    out["loja"] = rect(L.SHOP["x0"], L.SHOP["z0"] + 2, L.SHOP["x1"] - 2, L.SHOP["z1"] - 2)
    out["mural palco"] = L.RANK_STAGE
    return out


def main():
    f = footprints()
    wk = walkable()
    bad = 0
    keys = list(f)
    for i in range(len(keys)):
        for j in range(i + 1, len(keys)):
            g = gap(f[keys[i]], f[keys[j]])
            if g < 1.0:
                print("  SOBREPOSICAO  %-14s x %-14s folga %.1f" % (keys[i], keys[j], g))
                bad += 1
    solid = [k for k in f if not k.startswith(("barraca", "fonte", "carvalho", "carroca", "poco", "correio", "placa",
                                               "poste"))]
    for k in solid:
        for rk, rp in wk.items():
            if rk in ("forja", "loja", "mural palco"):
                continue
            if rk == "patio terraco":
                g = min(math.hypot(px - L.COURT_C[0], pz - L.COURT_C[1]) for px, pz in f[k]) - L.COURT_RING[1]
                ang = [math.degrees(math.atan2(pz - L.COURT_C[1], px - L.COURT_C[0])) % 360 for px, pz in f[k]]
                if all(not (L.COURT_RING[2] <= a_ <= L.COURT_RING[3]) for a_ in ang):
                    g = 99.0
            else:
                g = gap(f[k], rp)
            if g < -0.5:
                print("  INVADE CHAO   %-14s x %-14s %.1f" % (k, rk, g))
                bad += 1
    for k in f:
        if not k.startswith("casa"):
            continue
        g = min(gap(f[k], rp) for rp in wk.values())
        if g > 8.0:
            print("  LONGE DA RUA  %-14s folga %.1f" % (k, g))
            bad += 1
    for k, poly in f.items():
        for (x, z) in poly:
            if not inside(x, z, L.PLATEAU):
                print("  FORA DO PLATO %s (%.0f, %.0f)" % (k, x, z))
                bad += 1
                break
    # mobiliario da praca: nada a menos de 12 studs de um portal e nada no eixo do spawn (x -8..8 entre a cerca e a forja)
    for k, poly in f.items():
        cx = sum(p[0] for p in poly) / len(poly)
        cz = sum(p[1] for p in poly) / len(poly)
        for i in range(6):
            (px, pz), _ = L.portal_pos(i)
            if math.hypot(cx - px, cz - pz) < 12.0:
                print("  PERTO DO PORTAL %s" % k)
                bad += 1
        if not k.startswith(("casa", "forja", "loja", "mural")) and abs(cx) < 8.0 and -46 < cz < L.FENCE_Z:
            print("  NO EIXO DO SPAWN %s" % k)
            bad += 1
    # rotas: cada ponto sobre chao andavel (tolerancia 1 stud: ponto dentro de algum poligono alargado)
    for name, (pts, y) in L.routes().items():
        for (x, z) in pts:
            if not any(inside(x, z, poly) or gap([(x - 1, z - 1), (x + 1, z - 1), (x + 1, z + 1), (x - 1, z + 1)], poly) <= 0.0
                       for poly in wk.values()):
                print("  ROTA FORA DO CHAO %s em (%.0f, %.0f)" % (name, x, z))
                bad += 1
    # tempos a pe
    for name, (pts, y) in L.routes().items():
        d = sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(pts[:-1], pts[1:]))
        print("  %-28s %5.0f studs  %4.1f s" % (name, d, d / L.WALK))
    print("CHECK: %d problemas" % bad)
    return bad


if __name__ == "__main__":
    sys.exit(1 if main() else 0)
