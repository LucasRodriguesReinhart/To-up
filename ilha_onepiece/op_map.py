# op_map.py - desenha a planta travada (op_layout) num PNG de cima (sem Blender) + o mapa do MUNDO (Wano, Demon Slayer
# e Shadow Garden no Roblox) + confere encaixe, pisos dentro da borda, escadas (pe/topo no piso certo), forma, minerios,
# construcoes sobre piso/fora da praca e das escadas, e as rotas (comprimento/tempo).
# uso: python op_map.py [saida_planta.png] [saida_mundo.png]
import sys, os, math, importlib.util
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)
import op_layout as L
from PIL import Image, ImageDraw, ImageFont

S = 2.0                      # px por stud
X0, X1, Y0, Y1 = -270.0, 400.0, -150.0, 650.0
W, H = int((X1 - X0) * S), int((Y1 - Y0) * S)


def P(x, y):
    return ((x - X0) * S, (Y1 - y) * S)


def poly(d, pts, fill=None, outline=None, width=1):
    d.polygon([P(*p) for p in pts], fill=fill, outline=outline)
    if outline and width > 1:
        d.line([P(*p) for p in pts] + [P(*pts[0])], fill=outline, width=width)


def _font(sz):
    try:
        return ImageFont.truetype("arial.ttf", sz)
    except Exception:
        return None


def house_poly(b):
    nm, fam, x, y, w, dd, deg, z, fl, roof, rm = b
    a = math.radians(deg)
    fx, fy = math.cos(a), math.sin(a)           # frente
    ux, uy = -fy, fx                             # ao longo da fachada
    return [(x + ux * sx * w / 2 + fx * sy * dd / 2, y + uy * sx * w / 2 + fy * sy * dd / 2)
            for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))]


def main(out):
    im = Image.new("RGB", (W, H), (24, 120, 150))
    d = ImageDraw.Draw(im)
    f = _font(13)
    poly(d, L.ISLAND_RIM, fill=(96, 98, 104), outline=(230, 236, 220), width=2)
    poly(d, L.SWORD_SPUR, fill=(86, 88, 96))
    for nm, pts, z in L.ROCKS:
        poly(d, pts, fill=(110, 112, 118))
    poly(d, L.SKULL_ROCK, fill=(70, 70, 78), outline=(20, 20, 20))
    col = {"Court": (222, 210, 190), "CastleLanding": (200, 190, 170), "W3": (150, 180, 120), "Forecourt": (210, 196, 170),
           "Plaza": (198, 186, 160), "W2b": (170, 170, 140), "ExitLand": (170, 150, 120), "T1": (176, 160, 128),
           "Entry": (190, 180, 160), "HarborMid": (150, 120, 90), "Harbor": (140, 110, 80), "ShipDeck": (120, 80, 50)}
    for nm, pts, z, pr in sorted(L.floors(), key=lambda t: t[3]):
        poly(d, pts, fill=col[nm], outline=(40, 40, 50), width=1)
    poly(d, L.PLAZA, fill=(214, 204, 178), outline=(120, 100, 70), width=2)
    poly(d, L.BASIN, fill=(60, 180, 200))
    for pts in (L.CANAL_E, L.CANAL_W):
        d.line([P(p[0], p[1]) for p in pts], fill=(50, 170, 210), width=10)
    for nm, a, b, w in L.bridge_list():
        poly(d, L.ribbon([a[:2], b[:2]], w / 2), fill=(196, 50, 40), outline=(60, 10, 10))
    for nm, foot, deg, w, n, tread, g in L.STAIRS:
        t = L.stair_top(nm)
        poly(d, L.ribbon([foot[:2], t[:2]], w / 2), fill=(245, 245, 245), outline=(60, 60, 60))
        if f:
            d.text(P(t[0] + 3, t[1] + 3), nm, fill=(10, 10, 10), font=f)
    x0, y0, x1, y1 = L.MINE_RECT
    d.rectangle([P(x0, y1), P(x1, y0)], outline=(255, 210, 60), width=3)
    d.ellipse([P(L.EMBLEM_C[0] - L.EMBLEM_R, L.EMBLEM_C[1] + L.EMBLEM_R), P(L.EMBLEM_C[0] + L.EMBLEM_R,
               L.EMBLEM_C[1] - L.EMBLEM_R)], outline=(120, 90, 50), width=2)
    cols = {"COMMON": (240, 240, 240), "UNCOMMON": (90, 160, 255), "EPIC": (170, 90, 230), "SUPERLEGENDARY": (255, 120, 200)}
    for kind, i, x, y, r in L.ore_points():
        d.ellipse([P(x - r, y + r), P(x + r, y - r)], fill=cols[kind])
    for b in L.BUILDINGS:
        rc = {"Roof_OP_Blue": (52, 66, 104), "Roof_OP_Green": (70, 120, 96), "Roof_OP_Red": (160, 70, 54)}[b[10]]
        poly(d, house_poly(b), fill=rc, outline=(20, 20, 20), width=1)
        if f:
            d.text(P(b[2] - 6, b[3] + 5), b[0], fill=(255, 255, 255), font=f)
    kx, ky = L.KEEP_C
    hw, hd = L.KEEP_TIERS[0][:2]
    d.rectangle([P(kx - hw, ky + hd), P(kx + hw, ky - hd)], fill=(240, 240, 236), outline=(30, 30, 30), width=2)
    pts = [(p[0], p[1]) for p in L.TREE_TRUNK]
    d.line([P(*p) for p in pts], fill=(110, 70, 40), width=8)
    for (c, r, fl) in L.TREE_CANOPY:
        d.ellipse([P(c[0] - r, c[1] + r), P(c[0] + r, c[1] - r)], outline=(250, 140, 200), width=2)
    tx, ty = L.SUMMON_TOWER
    d.rectangle([P(tx - 12, ty + 20.6), P(tx + 8.6, ty - 20.6)], outline=(250, 210, 60), width=2)
    d.ellipse([P(tx - 5, ty + 5), P(tx + 5, ty - 5)], fill=(250, 210, 60))
    d.rectangle([P(L.TORII_IN[0] - 11, L.TORII_IN[1] + 1.5), P(L.TORII_IN[0] + 11, L.TORII_IN[1] - 1.5)], fill=(220, 30, 20))
    g = L.gate_opm_pos()
    d.ellipse([P(g[0] - 5, g[1] + 5), P(g[0] + 5, g[1] - 5)], fill=(255, 60, 60))
    a = L.anchor_opm_pos()
    d.ellipse([P(a[0] - 3, a[1] + 3), P(a[0] + 3, a[1] - 3)], fill=(255, 0, 255))
    sx, sy = L.SHIP_C
    d.rectangle([P(sx - 8, sy + 40), P(sx + 8, sy - 40)], outline=(60, 30, 10), width=3)
    d.ellipse([P(L.SKULL_C[0] - 8, L.SKULL_C[1] + 8), P(L.SKULL_C[0] + 8, L.SKULL_C[1] - 8)], fill=(30, 30, 30))
    d.ellipse([P(L.SWORD_POS[0] - 4, L.SWORD_POS[1] + 4), P(L.SWORD_POS[0] + 4, L.SWORD_POS[1] - 4)], fill=(200, 210, 230))
    pal = [(255, 200, 80), (255, 140, 60), (180, 230, 80), (255, 80, 80), (170, 140, 255), (100, 200, 255),
           (100, 220, 255), (200, 170, 255), (255, 160, 200), (120, 255, 200), (255, 255, 140), (255, 255, 255)]
    for i, (k, (pts, z)) in enumerate(L.routes().items()):
        d.line([P(*p) for p in pts], fill=pal[i % len(pal)], width=2)
    for gx in range(-250, 401, 50):
        d.line([P(gx, Y0), P(gx, Y1)], fill=(40, 100, 130) if gx else (255, 80, 80), width=1)
    for gy in range(-150, 651, 50):
        d.line([P(X0, gy), P(X1, gy)], fill=(40, 100, 130) if gy else (255, 80, 80), width=1)
    if f:
        d.text((8, 8), "Wano (local; +Y = eixo ponte->praca->castelo; +X = porto/saida; 1 quadrado = 50 studs)",
               fill=(255, 255, 255), font=_font(16))
    im.save(out)
    print("MAPA", out, im.size)


def _load_ro(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def world_map(out):
    """mundo no Roblox (X para a direita, Z para baixo) em volta da ancora: Wano, Demon Slayer, Shadow Garden, folga"""
    DS = _load_ro("ds_layout_ro", os.path.join(ROOT, "ilha_demonslayer", "ds_layout.py"))
    SG = _load_ro("sg_layout_ro", os.path.join(ROOT, "ilha_shadowgarden", "sg_layout.py"))
    ds = [(lambda r: (r[0], r[2]))(DS.to_roblox(x, y, 0)) for x, y in DS.ISLAND_RIM]
    sg = [(lambda w: (w[0], -w[1]))(SG.to_world_xy(x, y)) for x, y in SG.ISLAND_RIM]
    op = [(lambda r: (r[0], r[2]))(L.to_roblox(x, y, 0)) for x, y in L.ISLAND_RIM]
    spur = [(lambda r: (r[0], r[2]))(L.to_roblox(x, y, 0)) for x, y in L.SWORD_SPUR]
    xs = [p[0] for p in ds + sg + op]
    zs = [p[1] for p in ds + sg + op]
    ax0, ax1, az0, az1 = min(xs) - 700, max(xs) + 150, min(zs) - 150, max(zs) + 700
    s = 1600.0 / (ax1 - ax0)
    im = Image.new("RGB", (1600, int((az1 - az0) * s)), (16, 22, 40))
    d = ImageDraw.Draw(im)
    Q = lambda p: ((p[0] - ax0) * s, (p[1] - az0) * s)
    d.polygon([Q(p) for p in sg], fill=(70, 60, 110))
    d.polygon([Q(p) for p in ds], fill=(60, 80, 100))
    d.polygon([Q(p) for p in op], fill=(80, 170, 170))
    d.polygon([Q(p) for p in spur], fill=(70, 140, 140))
    for nm, a, b, w in L.bridge_list()[:2]:
        d.line([Q((lambda r: (r[0], r[2]))(L.to_roblox(*a[:2], 0))), Q((lambda r: (r[0], r[2]))(L.to_roblox(*b[:2], 0)))],
               fill=(220, 60, 50), width=4)
    ap = L.anchor_opm_pos()
    ux, uy = L.exit_dir()
    c = (ap[0] + ux * 350.0, ap[1] + uy * 350.0)
    cr = L.to_roblox(c[0], c[1], 0)
    r = 300.0 * s
    d.ellipse([((cr[0] - ax0) * s - r, (cr[2] - az0) * s - r), ((cr[0] - ax0) * s + r, (cr[2] - az0) * s + r)],
              outline=(255, 220, 120), width=2)
    a = L.to_roblox(L.PREV_X, L.PREV_Y, 0)
    d.ellipse([Q((a[0] - 6, a[2] - 6)), Q((a[0] + 6, a[2] + 6))], fill=(255, 0, 255))
    ar = L.to_roblox(ap[0], ap[1], 0)
    d.ellipse([Q((ar[0] - 6, ar[2] - 6)), Q((ar[0] + 6, ar[2] + 6))], fill=(255, 0, 255))
    f = _font(18)
    if f:
        d.text((10, 10), "Mundo Roblox (X ->, Z para baixo). Wano (ciano), Demon Slayer, Shadow Garden; circulo = espaco "
                         "livre da area 6 (r 300, 350 a frente da ancora OPM)", fill=(255, 255, 255), font=f)
    im.save(out)
    mind = lambda pt, pl: min(math.dist(pt, q) for q in pl)
    dsd = min(mind(p, ds) for p in op)
    sgd = min(mind(p, sg) for p in op)
    print("MUNDO folga borda Wano <-> borda DS %.0f | <-> SG %.0f | disco area 6 <-> DS %.0f, SG %.0f, Wano %.0f" % (
        dsd, sgd, mind((cr[0], cr[2]), ds) - 300, mind((cr[0], cr[2]), sg) - 300, mind((cr[0], cr[2]), op + spur) - 300))
    print("MUNDO disco area 6 centro roblox (%.0f, %.0f)" % (cr[0], cr[2]))
    print("MAPA", out, im.size)


def check():
    p = L.to_roblox(L.PREV_X, L.PREV_Y, L.DECK)
    dd = math.dist((p[0], p[1], p[2]), L.A_RBX)
    print("WORLD_FROM_PREV roblox (%.3f, %.3f, %.3f) ancora (%.3f, %.1f, %.3f) distancia %.4f %s" % (
        p + L.A_RBX + (dd, "OK" if dd < 1e-3 else "FAIL")))
    fw = L.dir_to_roblox(0, 1)
    print("rumo +Y local -> roblox (%.4f, %.4f, %.4f) (ancora %.4f, 0, %.4f)" % (fw + (L.A_FWD[0], L.A_FWD[2])))
    for nm, (x, y) in (("WORLD_ENTRY", L.SPAWN), ("MiningZone", L.MINE_C), ("SUMMON_Main", L.SUMMON_TOWER),
                       ("ISLAND_EXIT", L.EXIT_START), ("GATE_OnePunchMan", L.gate_opm_pos()),
                       ("ANCHOR_OnePunchMan", L.anchor_opm_pos()), ("KEEP", L.KEEP_C)):
        r = L.to_roblox(x, y, 0.0)
        print("  %-18s local (%8.2f, %8.2f) roblox (%9.2f, %9.2f)" % (nm, x, y, r[0], r[2]))
    fw = L.dir_to_roblox(*L.exit_dir())
    print("  ANCHOR_OnePunchMan fwd roblox (%.4f, 0, %.4f) heading_deg %.1f orientation_y %.1f" % (
        fw[0], fw[2], math.degrees(math.atan2(-fw[2], fw[0])), math.degrees(math.atan2(-fw[0], -fw[2])) % 360.0))
    rim = L.ISLAND_RIM
    for nm, pts, z, pr in L.floors():
        out = [q for q in pts if not L.point_in_poly(q[0], q[1], rim)]
        print("piso %-13s z %6.1f area %7.0f  vertices fora da borda: %d %s" % (nm, z, L.area(pts), len(out),
              [tuple(round(c) for c in q) for q in out[:5]]))
    bad = 0
    for nm, foot, deg, w, n, tread, g in L.STAIRS:
        a = math.radians(deg)
        fx, fy = foot[0] - math.cos(a) * (tread / 2 + 0.3), foot[1] - math.sin(a) * (tread / 2 + 0.3)
        t = L.stair_top(nm)
        tx, ty = t[0] + math.cos(a) * 0.6, t[1] + math.sin(a) * 0.6
        zf, zt = L.zone_of(fx, fy), L.zone_of(tx, ty)
        ok = zf is not None and abs(zf - foot[2]) < 0.3 and zt is not None and abs(zt - t[2]) < 0.3
        bad += not ok
        print("escada %-10s pe z %s (quer %.1f) topo z %s (quer %.1f) espelho %.3f n %d %s" % (
            nm, zf and round(zf, 2), foot[2], zt and round(zt, 2), t[2], L.stair_rise(nm), n, "OK" if ok else "FAIL"))
    lx = [q[0] for q in L.RIM_CTRL]
    ly = [q[1] for q in L.RIM_CTRL]
    print("forma: topo %.0f (x) x %.0f (y) area %.0f | praca %.0f x %.0f area %.0f | MiningZone %.0f x %.0f = %.0f" % (
        max(lx) - min(lx), max(ly) - min(ly), L.area(L.ISLAND_RIM),
        max(q[0] for q in L.PLAZA) - min(q[0] for q in L.PLAZA), max(q[1] for q in L.PLAZA) - min(q[1] for q in L.PLAZA),
        L.area(L.PLAZA), L.MINE_RECT[2] - L.MINE_RECT[0], L.MINE_RECT[3] - L.MINE_RECT[1],
        (L.MINE_RECT[2] - L.MINE_RECT[0]) * (L.MINE_RECT[3] - L.MINE_RECT[1])))
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
    print("forma: trecho reto mais longo da borda %.1f (meta <= 70; a borda da ancora OPM e reta de proposito)" % best)
    from collections import Counter
    pts = L.ore_points()
    print("ORE: %d pontos %s" % (len(pts), dict(Counter(q[0] for q in pts))))
    x0, y0, x1, y1 = L.MINE_RECT
    print("MiningZone em P (92,2): %s" % all(L.zone_of(x, y) == L.P for x in (x0, x1, 0.0) for y in (y0, y1, L.MINE_C[1])))
    # construcoes: sobre o piso da cota certa, fora da MiningZone + 8, fora das escadas e das pontes
    import itertools
    rects = []
    for nm, foot, deg, w, n_, tread, g in L.STAIRS:
        t = L.stair_top(nm)
        rects.append(("escada " + nm, L.ribbon([foot[:2], t[:2]], w / 2 + 1.25)))
    for nm, a, b, w in L.bridge_list():
        rects.append(("ponte " + nm, L.ribbon([a[:2], b[:2]], w / 2 + 1.0)))
    zone8 = L.rect_poly((x0 - 8, y0 - 8, x1 + 8, y1 + 8))
    for bdef in L.BUILDINGS:
        hp = house_poly(bdef)
        zs = {L.zone_of(x, y) for x, y in hp + [(bdef[2], bdef[3])]}
        probs = []
        if zs != {bdef[7]}:
            probs.append("pisos %s (quer %.1f)" % (sorted(z for z in zs if z) + ([None] if None in zs else []), bdef[7]))
        if any(L.point_in_poly(x, y, zone8) for x, y in hp):
            probs.append("dentro da MiningZone+8")
        for lab, rp in rects:
            if any(L.point_in_poly(x, y, rp) for x, y in hp) or any(L.point_in_poly(x, y, hp) for x, y in rp):
                probs.append("encosta em " + lab)
        print("predio %-3s %-9s %s" % (bdef[0], bdef[1], "OK" if not probs else "PROBLEMA " + "; ".join(probs)))
    for a_, b_ in itertools.combinations(L.BUILDINGS, 2):
        pa, pb = house_poly(a_), house_poly(b_)
        if any(L.point_in_poly(x, y, pb) for x, y in pa) or any(L.point_in_poly(x, y, pa) for x, y in pb):
            print("predio SOBREPOSTO %s x %s" % (a_[0], b_[0]))
    for k, (pts_, z) in L.routes().items():
        print("rota %-40s %5.0f studs  %4.1f s" % (k, L.plen(pts_), L.plen(pts_) / 16.0))
    return bad


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "plano", "planta_op.png")
    out2 = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "plano", "mundo_op.png")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    check()
    main(out)
    world_map(out2)
