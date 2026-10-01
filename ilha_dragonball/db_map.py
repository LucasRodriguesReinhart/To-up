# db_map.py - desenha a planta travada (db_layout) num PNG de cima (sem Blender) + confere encaixe no mundo Roblox.
# uso: python db_map.py [saida.png]
import sys, os, math
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import db_layout as L
from PIL import Image, ImageDraw, ImageFont

S = 3.0                      # px por stud
X0, X1, Y0, Y1 = -260.0, 300.0, -230.0, 260.0
W, H = int((X1 - X0) * S), int((Y1 - Y0) * S)


def P(x, y):
    return ((x - X0) * S, (Y1 - y) * S)


def poly(d, pts, fill=None, outline=None, width=1):
    d.polygon([P(*p) for p in pts], fill=fill, outline=outline)
    if outline and width > 1:
        d.line([P(*p) for p in pts] + [P(*pts[0])], fill=outline, width=width)


def ribbon(pts, hw):
    left, right = [], []
    n = len(pts)
    for i in range(n):
        x, y = pts[i]
        if i == 0:
            dx, dy = pts[1][0] - x, pts[1][1] - y
        elif i == n - 1:
            dx, dy = x - pts[i - 1][0], y - pts[i - 1][1]
        else:
            dx, dy = pts[i + 1][0] - pts[i - 1][0], pts[i + 1][1] - pts[i - 1][1]
        ln = math.hypot(dx, dy) or 1.0
        nx, ny = -dy / ln, dx / ln
        left.append((x + nx * hw, y + ny * hw))
        right.append((x - nx * hw, y - ny * hw))
    return left + list(reversed(right))


def main(out):
    im = Image.new("RGB", (W, H), (40, 90, 150))
    d = ImageDraw.Draw(im)
    try:
        f = ImageFont.truetype("arial.ttf", 13)
    except Exception:
        f = None
    poly(d, L.ISLAND_RIM, fill=(206, 176, 128), outline=(90, 60, 40), width=2)
    poly(d, L.HUB_POLY, fill=(190, 200, 150), outline=(80, 90, 60), width=2)
    poly(d, L.CAP_POLY, fill=(230, 232, 240), outline=(40, 60, 120), width=2)
    poly(d, L.prom_poly(), fill=(226, 214, 190), outline=(120, 110, 90))
    poly(d, L.arena_poly(), fill=(222, 170, 110), outline=(150, 90, 50), width=2)
    poly(d, L.summon_poly(), fill=(150, 150, 210), outline=(60, 60, 140), width=2)
    poly(d, ribbon(L.EXIT_PATH, L.EXIT_PATH_HW), fill=(200, 190, 170), outline=(100, 90, 80))
    poly(d, ribbon(L.HUB_EXIT_LINK, L.HUB_EXIT_LINK_HW), fill=(200, 190, 170), outline=(100, 90, 80))
    x0, y0, x1, y1 = L.ENTRY_PLAZA
    d.rectangle([P(x0, y1), P(x1, y0)], fill=(236, 226, 206), outline=(120, 110, 90))
    # ponte de chegada + escadaria
    hw = L.DECK_W / 2
    d.rectangle([P(-hw, L.BRIDGE_Y1), P(hw, L.BRIDGE_Y0)], fill=(180, 180, 180), outline=(60, 60, 60))
    d.rectangle([P(-L.ENTRY_STAIR_W / 2, L.ENTRY_STAIR_Y1), P(L.ENTRY_STAIR_W / 2, L.BRIDGE_Y1)], fill=(160, 160, 160),
                outline=(60, 60, 60))
    d.line([P(-L.GATE_OPEN_W / 2 - 6, L.GATE_Y), P(L.GATE_OPEN_W / 2 + 6, L.GATE_Y)], fill=(20, 40, 110), width=6)
    # ponte de saida + ilhota + portao SG + ancora
    ux, uy = L.exit_dir()
    b0 = L.EXIT_START
    b1 = L.exit_point(L.EXIT_BRIDGE_LEN)
    poly(d, ribbon([b0, b1], L.EXIT_W / 2), fill=(170, 160, 150), outline=(60, 60, 60))
    c = L.islet_center()
    r = L.GATE_ISLET_R
    d.ellipse([P(c[0] - r, c[1] + r), P(c[0] + r, c[1] - r)], fill=(120, 100, 130), outline=(60, 40, 80))
    g = L.gate_sg_pos()
    d.line([P(g[0] - uy * 12, g[1] + ux * 12), P(g[0] + uy * 12, g[1] - ux * 12)], fill=(150, 60, 220), width=6)
    a = L.anchor_pos()
    d.ellipse([P(a[0] - 3, a[1] + 3), P(a[0] + 3, a[1] - 3)], fill=(255, 0, 255))
    # escadas: acessos da arena
    for ang, w, kind in L.ARENA_ACCESS:
        foot, top, _ = L.access_frame(ang)
        d.line([P(*foot), P(*top)], fill=(255, 255, 255) if kind == "stair" else (255, 220, 120), width=int(w * S))
    # outras escadas
    x, y, w = L.HUB_STAIR
    d.rectangle([P(x - w / 2, y), P(x + w / 2, y - 5 * L.TREAD)], fill=(255, 255, 255))
    for x, y, w in L.HUB_SIDE_STAIRS:
        d.rectangle([P(x - w / 2, y), P(x + w / 2, y - 5 * L.TREAD)], fill=(255, 255, 255))
    x, y, w = L.CAP_STAIR
    d.rectangle([P(x - w / 2, y), P(x + w / 2, y - L.CAP_STAIR_N * L.TREAD)], fill=(255, 255, 255))
    x, y, w = L.SUMMON_STAIR
    d.rectangle([P(x - L.SUMMON_STAIR_N * L.TREAD, y + w / 2), P(x, y - w / 2)], fill=(255, 255, 255))
    fx, fy, fdeg, fw = L.EXIT_STAIR
    a2 = math.radians(fdeg)
    d.line([P(fx, fy), P(fx + math.cos(a2) * 8.5, fy + math.sin(a2) * 8.5)], fill=(255, 255, 255), width=int(fw * S))
    # capsule
    cx, cy = L.CAPSULE_C
    R = L.CAPSULE_R
    d.ellipse([P(cx - R, cy + R), P(cx + R, cy - R)], fill=(245, 245, 250), outline=(30, 60, 160), width=4)
    R2 = L.CAPSULE_HALL_R
    d.ellipse([P(cx - R2, cy + R2), P(cx + R2, cy - R2)], outline=(120, 140, 200), width=2)
    for ax_, ay_, ar in L.CAPSULE_ANNEX:
        d.ellipse([P(ax_ - ar, ay_ + ar), P(ax_ + ar, ay_ - ar)], fill=(240, 240, 246), outline=(30, 60, 160), width=2)
    x0, y0, x1, y1 = L.CAPSULE_FOYER
    d.rectangle([P(x0, y1), P(x1, y0)], outline=(200, 80, 40), width=2)
    # summon torre
    tx, ty = L.SUMMON_TOWER
    d.rectangle([P(tx - 8, ty + 8), P(tx + 8, ty - 8)], fill=(90, 90, 170))
    # mesas
    for x, y, r, h, kind in L.MESAS:
        d.ellipse([P(x - r, y + r), P(x + r, y - r)], fill=(170, 100, 60), outline=(90, 50, 30), width=2)
        if f:
            d.text(P(x - 6, y + 2), "%d" % h, fill=(255, 255, 255), font=f)
    for x, y, r in L.GARDENS:
        d.ellipse([P(x - r, y + r), P(x + r, y - r)], outline=(40, 140, 40), width=2)
    for pts, w in L.GROUND_PATHS:
        d.line([P(*p) for p in pts], fill=(240, 236, 226), width=int(w * S))
    for x, y, r, h in L.PLATEAU_ROCKS:
        d.ellipse([P(x - r, y + r), P(x + r, y - r)], fill=(160, 90, 50), outline=(90, 50, 30))
    for x, y, r, h in L.ARENA_ROCKS:
        d.ellipse([P(x - r, y + r), P(x + r, y - r)], fill=(180, 100, 60), outline=(90, 50, 30))
    # torres/satelites
    for x, y, r, kind, walk in L.TOWER_SITES:
        d.ellipse([P(x - r, y + r), P(x + r, y - r)], fill=(250, 250, 255), outline=(20, 50, 150), width=3)
        if f:
            d.text(P(x - 10, y - r - 1), kind, fill=(0, 0, 60), font=f)
    for x, y, r, kind in L.HUB_LOTS:
        d.rectangle([P(x - r, y + r), P(x + r, y - r)], outline=(30, 30, 30), width=2)
        if f:
            d.text(P(x - r, y + r + 12), kind, fill=(0, 0, 0), font=f)
    for x, y, r, kind in L.GROUND_LOTS:
        d.rectangle([P(x - r, y + r), P(x + r, y - r)], outline=(90, 20, 20), width=2)
        if f:
            d.text(P(x - r, y + r + 12), kind, fill=(90, 0, 0), font=f)
    for k, (a0, a1) in L.SAT_BRIDGES.items():
        d.line([P(*a0), P(*a1)], fill=(200, 200, 210), width=int(L.SAT_BRIDGE_W * S))
    for x, y, r in L.PODS:
        d.ellipse([P(x - r, y + r), P(x + r, y - r)], fill=(250, 250, 255), outline=(40, 80, 170), width=2)
    # agua
    for x, y, r in (L.POOL_SW, L.POOL_SE, L.POOL_NW):
        d.ellipse([P(x - r, y + r), P(x + r, y - r)], fill=(60, 150, 220))
    d.line([P(*L.POOL_SW[:2]), P(*L.FALL_SW)], fill=(60, 150, 220), width=int(5 * S))
    d.line([P(*L.POOL_SE[:2]), P(*L.FALL_SE)], fill=(60, 150, 220), width=int(4 * S))
    d.line([P(*L.POOL_NW[:2]), P(*L.CASCADE_NW_TOP[:2])], fill=(60, 150, 220), width=int(4 * S))
    # pod central
    x, y, r = L.CORE_POD
    d.ellipse([P(x - r, y + r), P(x + r, y - r)], fill=(250, 250, 255), outline=(40, 80, 170), width=2)
    # minerio
    cols = {"COMMON": (120, 120, 120), "UNCOMMON": (60, 200, 90), "EPIC": (170, 70, 230), "SUPERLEGENDARY": (255, 200, 0)}
    pts = L.ore_points()
    for kind, i, x, y, r in pts:
        d.ellipse([P(x - r, y + r), P(x + r, y - r)], fill=cols[kind])
    # arco de rocha da saida
    ax_, ay_, adeg = L.EXIT_ARCH
    d.ellipse([P(ax_ - 3, ay_ + 3), P(ax_ + 3, ay_ - 3)], fill=(90, 40, 20))
    # grade 50
    for gx in range(-250, 301, 50):
        d.line([P(gx, Y0), P(gx, Y1)], fill=(255, 255, 255, 40) if gx else (255, 80, 80), width=1)
    for gy in range(-200, 251, 50):
        d.line([P(X0, gy), P(X1, gy)], fill=(255, 255, 255, 40) if gy else (255, 80, 80), width=1)
    if f:
        d.text((8, 8), "DB layout  (N para cima; 1 quadrado = 50 studs)  ores=%d" % len(pts), fill=(255, 255, 255), font=f)
    im.save(out)
    print("MAPA", out, im.size)
    return pts


def check():
    # encaixe no mundo e distancias
    print("WORLD_FROM_PREV roblox:", tuple(round(v, 2) for v in L.to_roblox(0.0, L.PREV_Y, L.DECK)))
    print("centro arena roblox:", tuple(round(v, 2) for v in L.to_roblox(0.0, 0.0, L.ARENA)))
    print("entrada spawn roblox:", tuple(round(v, 2) for v in L.to_roblox(*L.ENTRY_SPAWN, L.GROUND)))
    a = L.anchor_pos()
    print("ancora SG (local):", tuple(round(v, 2) for v in a), "roblox:", tuple(round(v, 2) for v in L.to_roblox(a[0], a[1], L.EXIT_Z)))
    ux, uy = L.exit_dir()
    w0 = L.to_world_xy(0, 0)
    w1 = L.to_world_xy(ux, uy)
    print("rumo saida roblox (fwd_x, fwd_z):", round(w1[0] - w0[0], 4), round(-(w1[1] - w0[1]), 4))
    xs, zs = [], []
    for x, y in L.ISLAND_RIM:
        rx, _, rz = L.to_roblox(x, y, 0)
        xs.append(rx)
        zs.append(rz)
    print("contorno roblox: x %.1f..%.1f  z %.1f..%.1f" % (min(xs), max(xs), min(zs), max(zs)))
    # distancia minima do contorno DB ate a Ilha 1 (caixa aproximada do contorno Naruto em Roblox)
    sys.path.insert(0, os.path.join(HERE, "..", "ilha_naruto"))
    import il_layout as NL
    nar = [(-x, 420.0 + y) for x, y in NL.ISLAND_RIM]
    isl = NL.islet_center()
    nar += [(-isl[0] + 23 * math.cos(t), 420.0 + isl[1] + 23 * math.sin(t)) for t in [i * 0.3 for i in range(21)]]
    best = (1e9, None)
    for x, y in L.ISLAND_RIM:
        rx, _, rz = L.to_roblox(x, y, 0)
        for nx, nz in nar:
            dd = math.hypot(rx - nx, rz - nz)
            if dd < best[0]:
                best = (dd, (x, y))
    print("distancia minima contorno DB <-> Ilha 1: %.1f (no ponto local %s)" % best)
    # conferencias de zona
    for nm, (x, y) in {"spawn": L.ENTRY_SPAWN, "summon": L.SUMMON_C, "capsule": L.CAPSULE_C, "hub_front": (0, 90),
                       "exit_path": L.EXIT_PATH[1], "arena_c": (0, 0)}.items():
        print("zona %-10s -> %.1f" % (nm, L.zone_of(x, y)))
    # tudo dentro do contorno?
    for nm, pts in {"hub": L.HUB_POLY, "cap": L.CAP_POLY, "summon": L.summon_poly(), "prom": L.prom_poly()}.items():
        out = [p for p in pts if not L.point_in_poly(p[0] * 0.995, p[1] * 0.995, L.ISLAND_RIM)]
        print("fora do contorno %-7s: %d pontos %s" % (nm, len(out), [tuple(round(c) for c in p) for p in out[:4]]))


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "renders", "_mapa_planta.png")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    check()
    pts = main(out)
    from collections import Counter
    print("ores:", Counter(p[0] for p in pts))
