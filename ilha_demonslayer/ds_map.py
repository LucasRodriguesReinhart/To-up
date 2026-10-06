# ds_map.py - desenha a planta travada (ds_layout) num PNG de cima (sem Blender) + confere o encaixe no mundo Roblox,
# os pisos dentro da borda, as escadas (pe e topo no piso certo) e a forma (razoes, trechos retos da borda).
# uso: python ds_map.py [saida.png]
import sys, os, math
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ds_layout as L
from PIL import Image, ImageDraw, ImageFont

S = 2.0                      # px por stud
X0, X1, Y0, Y1 = -200.0, 240.0, -140.0, 720.0
W, H = int((X1 - X0) * S), int((Y1 - Y0) * S)


def P(x, y):
    return ((x - X0) * S, (Y1 - y) * S)


def poly(d, pts, fill=None, outline=None, width=1):
    d.polygon([P(*p) for p in pts], fill=fill, outline=outline)
    if outline and width > 1:
        d.line([P(*p) for p in pts] + [P(*pts[0])], fill=outline, width=width)


def main(out):
    im = Image.new("RGB", (W, H), (20, 24, 44))
    d = ImageDraw.Draw(im)
    try:
        f = ImageFont.truetype("arial.ttf", 13)
    except Exception:
        f = None
    poly(d, L.ISLAND_RIM, fill=(54, 58, 70), outline=(200, 220, 200), width=2)
    poly(d, L.WEST_RIDGE, fill=(80, 84, 96))
    poly(d, L.NE_BANK, fill=(80, 84, 96))
    poly(d, L.BACK_ROCKS, fill=(70, 74, 86))
    col = {"Summon": (128, 112, 176), "Forge": (160, 146, 128), "ExitLand": (150, 138, 120), "Berm": (120, 116, 150),
           "VillageHigh": (110, 150, 100), "T1": (150, 122, 86), "Bamboo": (96, 130, 70), "Entry": (120, 120, 112)}
    for nm, pts, z, pr in sorted(L.floors(), key=lambda t: t[3]):
        poly(d, pts, fill=col[nm], outline=(30, 30, 40), width=1)
    poly(d, L.CLEARING, outline=(220, 190, 120), width=2)
    poly(d, L.POND, fill=(50, 90, 170))
    for pts, w in ((L.BAMBOO_RAMP, 8.0), (L.EXIT_PATH, 10.0), (L.VILLAGE_STREET, 7.0), (L.VILLAGE_STREET_HIGH, 7.0)):
        poly(d, L.ribbon(pts, w / 2), fill=(196, 182, 150))
    d.line([P(*p) for p in L.CHANNEL], fill=(80, 140, 230), width=5)
    for nm, a, b, w in L.bridge_list():
        poly(d, L.ribbon([a[:2], b[:2]], w / 2), fill=(120, 84, 56), outline=(30, 20, 10))
    poly(d, L.pier_poly(), fill=(140, 136, 128), outline=(30, 30, 30))
    a0, a1, w = L.FOOTBRIDGE
    poly(d, L.ribbon([a0, a1], w / 2), fill=(120, 84, 56))
    for nm, foot, deg, w, n, tread, g in L.STAIRS:
        t = L.stair_top(nm)
        poly(d, L.ribbon([foot[:2], t[:2]], w / 2), fill=(240, 240, 240), outline=(60, 60, 60))
    x0, y0, x1, y1 = L.MINE_RECT
    d.rectangle([P(x0, y1), P(x1, y0)], outline=(255, 210, 60), width=2)
    cols = {"COMMON": (220, 220, 220), "UNCOMMON": (90, 160, 255), "EPIC": (170, 90, 230), "SUPERLEGENDARY": (255, 120, 200)}
    for kind, i, x, y, r in L.ore_points():
        d.ellipse([P(x - r, y + r), P(x + r, y - r)], fill=cols[kind])
    for k, (x0, y0, x1, y1, e, r) in L.FORGE.items():
        d.rectangle([P(x0, y1), P(x1, y0)], fill=(90, 60, 44), outline=(250, 200, 120), width=2)
    for nm, tp, x, y, w, dd, deg, z, fl in L.HOUSES:
        d.rectangle([P(x - w / 2, y + dd / 2), P(x + w / 2, y - dd / 2)], fill=(226, 214, 190), outline=(40, 30, 20), width=2)
        if f:
            d.text(P(x - 6, y + 4), nm, fill=(20, 20, 20), font=f)
    tx, ty = L.SUMMON_TOWER
    d.ellipse([P(tx - 6, ty + 6), P(tx + 6, ty - 6)], fill=(250, 210, 60))
    for x, y in (L.TORII_IN, L.TORII_OUT):
        d.rectangle([P(x - 7, y + 1.5), P(x + 7, y - 1.5)], fill=(200, 40, 30))
    g = L.gate_op_pos()
    d.ellipse([P(g[0] - 4, g[1] + 4), P(g[0] + 4, g[1] - 4)], fill=(60, 200, 255))
    a = L.anchor_op_pos()
    d.ellipse([P(a[0] - 3, a[1] + 3), P(a[0] + 3, a[1] - 3)], fill=(255, 0, 255))
    for x, y in L.WISTERIA:
        d.ellipse([P(x - 4, y + 4), P(x + 4, y - 4)], fill=(190, 140, 240))
    rc = {"SHADOW_GATE->ENTRY": (255, 255, 255)}
    pal = [(255, 200, 80), (255, 140, 60), (180, 230, 80), (255, 80, 80), (170, 140, 255), (100, 200, 255),
           (100, 220, 255), (200, 170, 255), (255, 160, 200), (120, 255, 200), (255, 255, 140)]
    for i, (k, (pts, z)) in enumerate(L.routes().items()):
        d.line([P(*p) for p in pts], fill=rc.get(k, pal[i % len(pal)]), width=2)
    for gx in range(-200, 241, 50):
        d.line([P(gx, Y0), P(gx, Y1)], fill=(60, 60, 90) if gx else (255, 80, 80), width=1)
    for gy in range(-100, 721, 50):
        d.line([P(X0, gy), P(X1, gy)], fill=(60, 60, 90) if gy else (255, 80, 80), width=1)
    if f:
        d.text((8, 8), "DS layout (local; +Y = percurso; 1 quadrado = 50 studs)", fill=(255, 255, 255), font=f)
    im.save(out)
    print("MAPA", out, im.size)


def check():
    p = L.to_roblox(L.PREV_X, L.PREV_Y, L.DECK)
    d = math.dist((p[0], p[2]), (L.A_RBX[0], L.A_RBX[2]))
    print("WORLD_FROM_PREV roblox (%.3f, %.3f, %.3f) ancora (%.4f, %.1f, %.4f) distancia %.4f %s" % (
        p[0], p[1], p[2], L.A_RBX[0], L.A_RBX[1], L.A_RBX[2], d, "OK" if d < 1e-3 else "FAIL"))
    f = L.dir_to_roblox(0, 1)
    print("rumo +Y local -> roblox (%.4f, %.4f, %.4f) (ancora %.4f, 0, %.4f)" % (f + (L.A_FWD[0], L.A_FWD[2])))
    for nm, (x, y) in (("WORLD_ENTRY", L.SPAWN), ("MiningZone", L.MINE_C), ("SUMMON_Main", L.SUMMON_TOWER),
                       ("ISLAND_EXIT", L.EXIT_START), ("GATE_OnePiece", L.gate_op_pos()),
                       ("ANCHOR_OnePiece", L.anchor_op_pos())):
        r = L.to_roblox(x, y, 0.0)
        print("  %-16s local (%8.2f, %8.2f) roblox (%9.2f, %9.2f)" % (nm, x, y, r[0], r[2]))
    fw = L.dir_to_roblox(*L.exit_dir())
    print("  ANCHOR_OnePiece fwd roblox (%.4f, 0, %.4f) heading_deg %.1f" % (fw[0], fw[2], math.degrees(math.atan2(-fw[2], fw[0]))))
    rim = L.ISLAND_RIM
    for nm, pts, z, pr in L.floors():
        out = [q for q in pts if not L.point_in_poly(q[0], q[1], rim)]
        near = [q for q in pts if L.point_in_poly(q[0], q[1], rim) and L.poly_edge_dist(q[0], q[1], rim) < 1.0]
        print("piso %-12s area %7.0f  fora da borda: %d %s  rente (<1): %d" % (nm, L.area(pts), len(out),
              [tuple(round(c) for c in q) for q in out[:4]], len(near)))
    for nm, foot, deg, w, n, tread, g in L.STAIRS:
        a = math.radians(deg)
        fx, fy = foot[0] - math.cos(a) * (tread / 2 + 0.3), foot[1] - math.sin(a) * (tread / 2 + 0.3)
        t = L.stair_top(nm)
        tx, ty = t[0] + math.cos(a) * 0.6, t[1] + math.sin(a) * 0.6
        zf, zt = L.zone_of(fx, fy), L.zone_of(tx, ty)
        ok = zf is not None and abs(zf - foot[2]) < 0.3 and zt is not None and abs(zt - t[2]) < 0.3
        print("escada %-12s pe z %s (quer %.1f) topo z %s (quer %.1f) espelho %.3f piso %.2f %s" % (
            nm, zf and round(zf, 2), foot[2], zt and round(zt, 2), t[2], L.stair_rise(nm), tread, "OK" if ok else "FAIL"))
    lx = [q[0] for q in L.RIM_CTRL]
    ly = [q[1] for q in L.RIM_CTRL]
    print("forma: topo %.0f x %.0f razao %.2f area %.0f ; clareira %.0f x %.0f (razao %.2f) area %.0f" % (
        max(ly) - min(ly), max(lx) - min(lx), (max(ly) - min(ly)) / (max(lx) - min(lx)), L.area(L.ISLAND_RIM),
        max(q[1] for q in L.CLEARING) - min(q[1] for q in L.CLEARING), max(q[0] for q in L.CLEARING) - min(q[0] for q in L.CLEARING),
        (max(q[1] for q in L.CLEARING) - min(q[1] for q in L.CLEARING)) / (max(q[0] for q in L.CLEARING) - min(q[0] for q in L.CLEARING)),
        L.area(L.CLEARING)))
    # trecho reto mais longo da borda: soma de segmentos consecutivos com desvio < 6 graus
    best = 0.0
    n = len(rim)
    for i in range(n):
        a0 = math.atan2(rim[(i + 1) % n][1] - rim[i][1], rim[(i + 1) % n][0] - rim[i][0])
        run = 0.0
        for k in range(n):
            a_, b_ = rim[(i + k) % n], rim[(i + k + 1) % n]
            ang = math.atan2(b_[1] - a_[1], b_[0] - a_[0])
            if abs((ang - a0 + math.pi) % (2 * math.pi) - math.pi) > math.radians(8.0):
                break
            run += math.hypot(b_[0] - a_[0], b_[1] - a_[1])
        best = max(best, run)
    print("forma: trecho reto mais longo da borda %.1f (meta <= 60) %s" % (best, "OK" if best <= 60 else "FAIL"))
    pts = L.ore_points()
    from collections import Counter
    print("ORE: %d pontos %s" % (len(pts), dict(Counter(q[0] for q in pts))))
    x0, y0, x1, y1 = L.MINE_RECT
    print("MiningZone %.0f x %.0f, em T1: %s" % (x1 - x0, y1 - y0, all(L.zone_of(x, y) == L.T1 for x in (x0, x1) for y in (y0, y1))))
    for k, (pts_, z) in L.routes().items():
        print("rota %-40s %5.0f studs  %4.1f s" % (k, L.plen(pts_), L.plen(pts_) / 16.0))


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "renders", "onda0", "_mapa_planta.png")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    check()
    main(out)
