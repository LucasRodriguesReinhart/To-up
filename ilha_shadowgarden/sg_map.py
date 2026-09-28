# sg_map.py - desenha a planta travada (sg_layout) num PNG de cima (sem Blender) + confere o encaixe no mundo Roblox.
# uso: python sg_map.py [saida.png]
import sys, os, math
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import sg_layout as L
from PIL import Image, ImageDraw, ImageFont

S = 3.0                      # px por stud
X0, X1, Y0, Y1 = -190.0, 300.0, -275.0, 225.0
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
    im = Image.new("RGB", (W, H), (24, 30, 58))
    d = ImageDraw.Draw(im)
    try:
        f = ImageFont.truetype("arial.ttf", 13)
    except Exception:
        f = None
    poly(d, L.ISLAND_RIM, fill=(70, 72, 90), outline=(20, 20, 30), width=2)
    col = {"P1": (120, 124, 140), "P2": (140, 144, 162), "P3": (170, 172, 190), "Summon": (130, 110, 170),
           "EntryHigh": (120, 124, 140), "EntryLow": (100, 104, 120)}
    for nm, pts, z, pr in sorted(L.floors(), key=lambda t: t[3]):
        poly(d, pts, fill=col[nm], outline=(30, 30, 40), width=2)
        if f:
            cx = sum(p[0] for p in pts) / len(pts)
            cy = sum(p[1] for p in pts) / len(pts)
            d.text(P(cx - 10, cy), "%s %.1f" % (nm, z), fill=(255, 255, 255), font=f)
    poly(d, L.plaza_poly(), fill=(150, 150, 164), outline=(40, 40, 50), width=2)
    c = L.PLAZA_C
    r = L.FOUNTAIN_R
    d.ellipse([P(c[0] - r, c[1] + r), P(c[0] + r, c[1] - r)], fill=(70, 120, 200))
    # ponte de chegada
    hw = L.DECK_W / 2
    d.rectangle([P(-hw, L.BRIDGE_Y1), P(hw, L.BRIDGE_Y0)], fill=(90, 90, 100), outline=(30, 30, 30))
    for y in (L.PORTICO_A_Y, L.PORTICO_B_Y):
        d.line([P(-14, y), P(14, y)], fill=(120, 80, 200), width=6)
    # ruas
    for pts, w, z in L.STREETS:
        poly(d, ribbon(pts, w / 2), fill=(186, 186, 200))
    # escadas
    for nm, foot, deg, w, n, tread, g in L.STAIRS:
        a = math.radians(deg)
        top = (foot[0] + math.cos(a) * tread * n, foot[1] + math.sin(a) * tread * n)
        poly(d, ribbon([foot[:2], top], w / 2), fill=(255, 255, 255), outline=(60, 60, 60))
    # ponte do summon + torre
    a0, a1, w = L.SUMMON_BRIDGE
    poly(d, ribbon([a0, a1], w / 2), fill=(200, 200, 210))
    tx, ty = L.SUMMON_TOWER
    d.rectangle([P(tx - 6, ty + 6), P(tx + 6, ty - 6)], fill=(140, 80, 220))
    # muralha
    d.rectangle([P(L.WALL_X[0], L.WALL_Y1), P(L.WALL_X[1], L.WALL_Y0)], fill=(50, 50, 64))
    d.rectangle([P(-L.GATEHOUSE_W / 2, L.WALL_Y1), P(L.GATEHOUSE_W / 2, L.WALL_Y0)], fill=(186, 186, 200))
    gx, gw = L.EAST_WALL_GAP
    d.rectangle([P(gx - gw / 2, L.WALL_Y1), P(gx + gw / 2, L.WALL_Y0)], fill=(186, 186, 200))
    for x, y, r in L.GATEHOUSE_TOWERS:
        d.ellipse([P(x - r, y + r), P(x + r, y - r)], fill=(50, 50, 64))
    # castelo + salao
    x0, x1 = L.HALL_X0 - L.HALL_WALL, L.HALL_X1 + L.HALL_WALL
    d.rectangle([P(x0, L.HALL_Y1 + L.HALL_WALL), P(x1, L.CASTLE_FACADE_Y)], fill=(40, 42, 60))
    d.rectangle([P(L.HALL_X0, L.HALL_Y1), P(L.HALL_X1, L.HALL_Y0)], fill=(96, 92, 120))
    mx0, my0, mx1, my1 = L.MINE_RECT
    d.rectangle([P(mx0, my1), P(mx1, my0)], outline=(255, 200, 0), width=2)
    d.rectangle([P(-L.HALL_DOOR_W / 2, L.HALL_Y0), P(L.HALL_DOOR_W / 2, L.CASTLE_FACADE_Y)], fill=(200, 200, 220))
    for x, y, r, top in L.FRONT_TOWERS:
        d.ellipse([P(x - r, y + r), P(x + r, y - r)], fill=(40, 42, 60), outline=(150, 120, 230), width=2)
    x, y, r, top = L.CROWN_TOWER
    d.ellipse([P(x - r, y + r), P(x + r, y - r)], fill=(40, 42, 60), outline=(180, 140, 255), width=3)
    # dungeon (portaria + salas sob a ilha, tracejado)
    cx, cy, w, dd = L.DUNGEON_HOUSE
    d.rectangle([P(cx - w / 2, cy + dd / 2), P(cx + w / 2, cy - dd / 2)], fill=(50, 40, 70), outline=(170, 90, 255), width=3)
    px, py = L.DUNGEON_PORTAL
    d.ellipse([P(px - 4, py + 4), P(px + 4, py - 4)], fill=(170, 90, 255))
    for nm, (a, b, c2, e) in L.DUN_ROOMS:
        d.rectangle([P(a, e), P(c2, b)], outline=(200, 120, 255), width=1)
        if f:
            d.text(P(a + 2, e - 2), "dun " + nm, fill=(220, 180, 255), font=f)
    # craft
    cx, cy = L.CRAFT_C
    r = L.CRAFT_R
    d.ellipse([P(cx - r, cy + r), P(cx + r, cy - r)], fill=(70, 60, 50), outline=(255, 180, 90), width=3)
    # casas
    for x, y, w, dd, deg, z in L.HOUSE_LOTS:
        a = math.radians(deg)
        ux, uy = math.cos(a), math.sin(a)
        vx, vy = -uy, ux
        pts = [(x + ux * s * dd / 2 + vx * t * w / 2, y + uy * s * dd / 2 + vy * t * w / 2)
               for s, t in ((-1, -1), (-1, 1), (1, 1), (1, -1))]
        poly(d, pts, fill=(60, 50, 44), outline=(230, 170, 80), width=2)
        d.line([P(x, y), P(x + ux * 7, y + uy * 7)], fill=(255, 200, 100), width=2)
    # saida
    b0 = L.EXIT_START
    b1 = L.exit_point(L.EXIT_BRIDGE_LEN)
    poly(d, ribbon([b0, b1], L.EXIT_W / 2), fill=(110, 110, 120), outline=(30, 30, 30))
    c = L.islet_center()
    r = L.GATE_ISLET_R
    d.ellipse([P(c[0] - r, c[1] + r), P(c[0] + r, c[1] - r)], fill=(90, 80, 90), outline=(30, 30, 30))
    g = L.gate_ds_pos()
    ux, uy = L.exit_dir()
    d.line([P(g[0] - uy * 12, g[1] + ux * 12), P(g[0] + uy * 12, g[1] - ux * 12)], fill=(220, 40, 40), width=6)
    a = L.anchor_pos()
    d.ellipse([P(a[0] - 3, a[1] + 3), P(a[0] + 3, a[1] - 3)], fill=(255, 0, 255))
    # borda
    for x, y, z, deg in L.WATERFALLS:
        d.ellipse([P(x - 4, y + 4), P(x + 4, y - 4)], fill=(80, 170, 255))
    for x, y, r, top, kind in L.CLIFF_SPIRES:
        d.ellipse([P(x - r, y + r), P(x + r, y - r)], fill=(30, 30, 40), outline=(90, 90, 110), width=2)
    for x, y, r, n in L.PINE_GROVES:
        d.ellipse([P(x - r, y + r), P(x + r, y - r)], outline=(40, 120, 90), width=2)
    # minerio
    cols = {"COMMON": (160, 160, 160), "UNCOMMON": (60, 200, 90), "EPIC": (170, 70, 230), "SUPERLEGENDARY": (255, 200, 0)}
    pts = L.ore_points()
    for kind, i, x, y, r in pts:
        d.ellipse([P(x - r, y + r), P(x + r, y - r)], fill=cols[kind])
    for room, kind, i, x, y, r in L.dun_ore_points():
        d.ellipse([P(x - r, y + r), P(x + r, y - r)], outline=cols[kind], width=2)
    for gx in range(-150, 301, 50):
        d.line([P(gx, Y0), P(gx, Y1)], fill=(80, 80, 110) if gx else (255, 80, 80), width=1)
    for gy in range(-250, 226, 50):
        d.line([P(X0, gy), P(X1, gy)], fill=(80, 80, 110) if gy else (255, 80, 80), width=1)
    if f:
        d.text((8, 8), "SG layout  (N para cima; 1 quadrado = 50 studs)  ores=%d" % len(pts), fill=(255, 255, 255), font=f)
    im.save(out)
    print("MAPA", out, im.size)
    return pts


def check():
    print("yaw mundo: %.3f" % L.WORLD_YAW_DEG)
    print("WORLD_FROM_PREV roblox:", tuple(round(v, 3) for v in L.to_roblox(0.0, L.PREV_Y, L.DECK)),
          "(esperado -579,227 28,2 650,727)")
    print("rumo +Y roblox:", tuple(round(v, 4) for v in L.dir_to_roblox(0, 1)), "(esperado -0,9205 0 -0,3907)")
    print("entrada roblox:", tuple(round(v, 2) for v in L.to_roblox(*L.ENTRY_SPAWN, L.P1)))
    print("castelo (centro do salao) roblox:", tuple(round(v, 2) for v in L.to_roblox(0.0, 88.0, L.P3)))
    a = L.anchor_pos()
    print("ancora DS (local):", tuple(round(v, 2) for v in a), "roblox:", tuple(round(v, 2) for v in L.to_roblox(a[0], a[1], L.EXIT_Z)))
    print("rumo saida roblox:", tuple(round(v, 4) for v in L.dir_to_roblox(*L.exit_dir())))
    xs, zs = [], []
    for x, y in L.ISLAND_RIM + L.summon_poly():
        rx, _, rz = L.to_roblox(x, y, 0)
        xs.append(rx)
        zs.append(rz)
    print("contorno roblox: x %.1f..%.1f  z %.1f..%.1f" % (min(xs), max(xs), min(zs), max(zs)))
    # Ilhas 1 e 2 (caixas das pecas no Studio, 2026-09-28): Naruto x -199..170 z 222..628; DB x -583..-142 z 582..946
    boxes = {"Naruto": (-199, 170, 222, 628), "DragonBall": (-583, -142, 582, 946)}
    for nm, (bx0, bx1, bz0, bz1) in boxes.items():
        best = 1e9
        for x, y in L.ISLAND_RIM + L.summon_poly():
            rx, _, rz = L.to_roblox(x, y, 0)
            dx = max(bx0 - rx, 0, rx - bx1)
            dz = max(bz0 - rz, 0, rz - bz1)
            best = min(best, math.hypot(dx, dz))
        print("distancia minima contorno SG <-> caixa %s: %.1f" % (nm, best))
    for nm, (x, y) in {"spawn": L.ENTRY_SPAWN, "praca": L.PLAZA_C, "summon": L.SUMMON_C, "craft": L.CRAFT_C,
                       "salao": (0, 88), "dungeon": L.DUNGEON_HOUSE[:2], "saida": (150, -38)}.items():
        print("zona %-8s -> %s (%s)" % (nm, L.zone_of(x, y), L.floor_name(x, y)))
    for nm, pts, z, pr in L.floors():
        if nm == "Summon":
            continue
        out = [p for p in pts if not L.point_in_poly(p[0], p[1], L.ISLAND_RIM)]
        print("fora do contorno %-9s: %d %s" % (nm, len(out), [tuple(round(c) for c in p) for p in out[:4]]))
    for x, y, w, dd, deg, z in L.HOUSE_LOTS:
        bad = [nm for pts, sw, sz in L.STREETS if sz == z and L.polyline_dist(x, y, pts) < sw / 2 + min(w, dd) / 2]
        zz = L.zone_of(x, y)
        if bad or zz != z:
            print("CASA (%.0f, %.0f) conflito: rua=%s zona=%s" % (x, y, bad, zz))


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "renders", "_mapa_planta.png")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    check()
    pts = main(out)
    from collections import Counter
    print("ores:", Counter(p[0] for p in pts), "dungeon:", len(L.dun_ore_points()))
