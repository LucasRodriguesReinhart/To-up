# il_veg - vegetacao COMPOSITIVA da Ilha 1 (dono: integracao). Nada de espalhar: cada grupo tem funcao.
#   emoldurar : portao de entrada, escadas da vila, salao principal, praca do summon
#   separar   : gramado SO x terraco do summon, anel x vale leste, vila x plato
#   transicao : bordas do penhasco, prateleira de lobulos, plato do paredao (quebra a silhueta)
# 4 especies (folhosa redonda, pinheiro, pinheiro-guarda-chuva, sakura) x 3 escalas; arbustos; flores so em pontos.
# Espaco negativo: anel, fosso, pracas, ruas, escadas, pontes e o eixo de visao da entrada ficam LIVRES.
# Cada candidata e testada contra a geometria real dos outros modulos (BVH): se encosta em algo, sai.
import math, random, zlib
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
import il_lib as IL
from il_lib import MB, col_box
import il_layout as L
import fm_veg_kit as VK

C = "10_VEGETATION"
SEED = 3301
# (grupo, centro x, y, raio, n, especies, escala) - escala: S 7-9, M 10-13, L 14-18
GROUPS = [
    # emoldurar a entrada (fora das alas do portao)
    ("Entrada", -38.0, -107.0, 5.0, 2, ("young", "broad"), "M"),
    ("Entrada", 38.0, -106.0, 5.0, 2, ("young", "broad"), "M"),
    # gramado sudoeste: separa o anel do terraco do summon e da o primeiro plano das vistas do sul
    ("SO", -98.0, -52.0, 12.0, 4, ("broad", "broad", "fir"), "L"),
    ("SO", -70.0, -88.0, 9.0, 3, ("broad", "young"), "M"),
    ("SO", -118.0, -22.0, 8.0, 2, ("broad",), "M"),
    # gramado sudeste
    ("SE", 60.0, -95.0, 8.0, 3, ("broad", "young"), "M"),
    ("SE", 88.0, -66.0, 8.0, 3, ("broad", "fir"), "L"),
    # vale leste (casas e riacho)
    ("Leste", 142.0, -2.0, 6.0, 2, ("broad",), "M"),
    ("Leste", 136.0, 62.0, 7.0, 3, ("fir", "broad"), "L"),
    ("Leste", 96.0, -34.0, 5.0, 1, ("broad",), "M"),
    # terraco do summon: sakuras emoldurando a praca
    ("Summon", -98.0, 50.0, 4.0, 1, ("sakura",), "M"),
    ("Summon", -150.0, 0.0, 5.0, 2, ("sakura", "broad"), "M"),
    ("Summon", -150.0, 50.0, 5.0, 1, ("sakura",), "L"),
    # NO do T1: separa o summon da vila
    ("T1_NO", -118.0, 104.0, 10.0, 3, ("broad", "fir"), "L"),
    ("T1_NO", -86.0, 88.0, 5.0, 1, ("broad",), "S"),
    # T1 norte: moldura do topo da escadaria central (baixas: nao tapam o salao)
    ("T1_N", -22.0, 104.0, 2.0, 1, ("broad",), "S"),
    ("T1_N", 22.0, 102.0, 2.0, 1, ("broad",), "S"),
    ("T1_N", -64.0, 97.0, 4.0, 1, ("broad",), "M"),
    ("T1_N", 64.0, 95.0, 4.0, 1, ("broad",), "M"),
    # T2: sakuras ao lado do salao, folhosas atras dos predios
    ("T2", -33.0, 173.0, 3.0, 1, ("sakura",), "M"),
    ("T2", 33.0, 173.0, 3.0, 1, ("sakura",), "M"),
    ("T2", -82.0, 180.0, 6.0, 2, ("broad", "fir"), "L"),
    ("T2", 82.0, 178.0, 6.0, 2, ("broad", "fir"), "L"),
    ("T2", -128.0, 158.0, 7.0, 2, ("fir", "broad"), "L"),
    ("T2", 108.0, 166.0, 5.0, 1, ("fir",), "M"),
    # plato do paredao: pinheiros-guarda-chuva quebrando a linha do topo
    ("Plato", -100.0, 196.0, 8.0, 2, ("umbrella", "fir"), "L"),
    ("Plato", -58.0, 204.0, 6.0, 2, ("fir", "umbrella"), "M"),
    ("Plato", 20.0, 205.0, 6.0, 2, ("umbrella",), "M"),
    ("Plato", 60.0, 202.0, 6.0, 2, ("fir", "umbrella"), "L"),
    ("Plato", 98.0, 190.0, 6.0, 2, ("umbrella", "fir"), "M"),
    # bordas (transicao para o penhasco)
    ("SO", -134.0, -34.0, 6.0, 2, ("broad", "fir"), "M"),
    ("SE", 124.0, -50.0, 5.0, 2, ("broad",), "M"),
    ("Leste", 146.0, 22.0, 4.0, 1, ("fir",), "L"),
    ("T2", 80.0, 138.0, 4.0, 1, ("broad",), "M"),
    ("T1_NO", -146.0, 100.0, 5.0, 2, ("broad", "fir"), "L"),
    ("Entrada", -58.0, -104.0, 5.0, 1, ("broad",), "L"),
    ("Entrada", 60.0, -100.0, 5.0, 1, ("broad",), "L"),
]
SIZES = {"S": (9.0, 11.0), "M": (12.0, 15.0), "L": (16.0, 21.0)}
BUSHES = [  # (x, y, n, raio) - pes de escada, cantos de casa, borda do muro do anel ao sul
    (-12.0, -95.0, 2, 3.0), (12.0, -95.0, 2, 3.0), (-50.0, -70.0, 3, 5.0), (50.0, -70.0, 3, 5.0),
    (-26.0, -90.0, 2, 3.0), (26.0, -90.0, 2, 3.0), (-94.0, 26.0, 2, 3.0), (-10.0, 99.0, 2, 2.0), (10.0, 99.0, 2, 2.0),
    (-14.0, 128.0, 2, 2.0), (14.0, 128.0, 2, 2.0), (126.0, -26.0, 2, 3.0), (100.0, 34.0, 2, 3.0),
    (-138.0, 88.0, 3, 5.0), (72.0, 124.0, 2, 3.0), (-72.0, 124.0, 2, 3.0)]
FLOWERS = [(-22.0, -100.0), (22.0, -100.0), (-106.0, 6.0), (-134.0, 40.0), (-24.0, 136.0), (24.0, 136.0)]


def _free_axes(x, y):
    """eixos de visao e circulacao que ficam livres (espaco negativo)"""
    r = math.hypot(x, y)
    if r < L.T1_WALL_R + 1.0:                      # fosso, anel e faixa do anel
        return False
    if abs(x) < 16.0 and -200.0 < y < 140.0:        # eixo entrada -> fosso -> salao
        return False
    ex, ey = L.EXIT_START
    ux, uy = L.exit_dir()
    t = (x - ex) * ux + (y - ey) * uy
    d = abs(-(x - ex) * uy + (y - ey) * ux)
    if -6.0 < t < L.EXIT_BRIDGE_LEN + 50.0 and d < L.EXIT_W / 2 + 6.0:   # ponte de saida
        return False
    cx, cy = L.SUMMON_C
    if math.hypot(x - cx, y - cy) < L.SUMMON_R + 2.0:          # praca do summon
        return False
    for sx, sy in [(p[0], p[1]) for p in L.STREAM]:               # riacho
        if math.hypot(x - sx, y - sy) < L.STREAM_W:
            return False
    return True


_ROUTES = None


def _near_route(x, y, clear=4.0):
    """a arvore/arbusto nao pode ficar a menos de 'clear' de nenhuma das 14 rotas de navegacao"""
    global _ROUTES
    if _ROUTES is None:
        import il_qa
        _ROUTES = [pts for pts, z0 in il_qa.routes().values()]
    for pts in _ROUTES:
        for (ax, ay), (bx, by) in zip(pts, pts[1:]):
            dx, dy = bx - ax, by - ay
            dd = dx * dx + dy * dy
            t = 0.0 if dd < 1e-9 else max(0.0, min(1.0, ((x - ax) * dx + (y - ay) * dy) / dd))
            if math.hypot(x - ax - dx * t, y - ay - dy * t) < clear:
                return True
    return False


def _obstacles():
    """BVH das malhas de OUTROS modulos (predios, pontes, props, torre...): arvore nao encosta em nada"""
    verts, polys = [], []
    for o in bpy.data.objects:
        if o.type != "MESH" or o.name.startswith(("TER_", "VEG_", "SKY_", "COL_", "SCALE_", "WATER_")):
            continue
        if o.hide_render:
            continue
        mw = o.matrix_world
        base = len(verts)
        me = o.data
        verts += [mw @ v.co for v in me.vertices]
        polys += [[base + i for i in p.vertices] for p in me.polygons]
    return BVHTree.FromPolygons(verts, polys) if polys else None


def _ground():
    verts, polys = [], []
    for o in bpy.data.objects:
        if o.type == "MESH" and o.name.startswith(("TER_",)) and not o.hide_render:
            mw = o.matrix_world
            base = len(verts)
            verts += [mw @ v.co for v in o.data.vertices]
            polys += [[base + i for i in p.vertices] for p in o.data.polygons]
    return BVHTree.FromPolygons(verts, polys) if polys else None


def _ground_z(gb, x, y):
    z0 = L.zone_of(x, y)
    if gb is None:
        return z0
    hit = gb.ray_cast(Vector((x, y, 140.0)), Vector((0, 0, -1)), 400.0)
    if hit[0] is None:
        return None
    return hit[0].z


def build():
    rng = random.Random(SEED)
    ob = _obstacles()
    gb = _ground()
    placed = []          # (x, y, raio_copa)
    stats = {"ok": 0, "fora": 0}
    mbs = {}

    def mbfor(group):
        if group not in mbs:
            mbs[group] = MB("VEG_%s" % group, C, random.Random(zlib.crc32(group.encode()) & 0xffff), detail="near")
        return mbs[group]

    for group, gx, gy, gr, n, kinds, size in GROUPS:
        for k in range(n):
            ok = False
            for t in range(30):
                a = rng.uniform(0, math.tau)
                d = gr * math.sqrt(rng.random()) if n > 1 else rng.uniform(0, gr * 0.4)
                x, y = gx + math.cos(a) * d, gy + math.sin(a) * d
                h = rng.uniform(*SIZES[size])
                kind = kinds[k % len(kinds)]
                crown = h * (0.42 if kind in ("broad", "sakura") else 0.34)
                if not IL_point_in_rim(x, y, 3.0) or not _free_axes(x, y) or _near_route(x, y, 4.0):
                    continue
                if any(math.hypot(x - px, y - py) < (crown + pr) * 0.72 for px, py, pr in placed):
                    continue
                z = _ground_z(gb, x, y)
                if z is None or z < L.G - 1.0 and group not in ("Plato",):
                    continue
                if ob is not None:
                    hit = ob.find_nearest(Vector((x, y, z + h * 0.55)), crown * 0.95)
                    hit2 = ob.find_nearest(Vector((x, y, z + 2.0)), 2.5)
                    if hit[0] is not None or hit2[0] is not None:
                        continue
                mb = mbfor(group)
                lod = 0 if group in ("Entrada", "T1_N", "T2", "Summon") else 1
                walkable = group not in ("Plato",)
                clear = 6.0 if walkable else None
                if kind == "broad":
                    VK.broadleaf(mb, (x, y, z), h, rng, lod=lod, clear=clear if clear else 4.0)
                elif kind == "sakura":
                    VK.sakura_tree(mb, (x, y, z), h, rng, lod=lod, clear=clear if clear else 4.0)
                elif kind == "umbrella":
                    VK.umbrella_pine(mb, (x, y, z), h, rng, lod=lod)
                else:
                    VK.pine(mb, (x, y, z), h, rng, lod=lod, form=kind if kind in ("fir", "young", "spruce") else "fir",
                            clear=clear)
                if walkable:
                    col_box("VegTrunk", (1.6, 1.6, 7.0), (x, y, z + 3.5))
                placed.append((x, y, crown))
                stats["ok"] += 1
                ok = True
                break
            if not ok:
                stats["fora"] += 1
    # arbustos
    bm = MB("VEG_Bushes", C, random.Random(SEED + 1), detail="near")
    nb = 0
    for bx, by, n, br in BUSHES:
        for k in range(n):
            for t in range(12):
                a = rng.uniform(0, math.tau)
                d = br * math.sqrt(rng.random())
                x, y = bx + math.cos(a) * d, by + math.sin(a) * d
                if not IL_point_in_rim(x, y, 1.5) or math.hypot(x, y) < L.RING_R1 + 1.0 or _near_route(x, y, 3.0):
                    continue
                z = _ground_z(gb, x, y)
                if z is None:
                    continue
                if ob is not None and ob.find_nearest(Vector((x, y, z + 1.0)), 1.8)[0] is not None:
                    continue
                VK.bush(bm, (x, y, z), rng.uniform(1.6, 2.4), rng, lod=1)
                nb += 1
                break
    bm.finish()
    fl = MB("VEG_Flowers", C, random.Random(SEED + 2), detail="near")
    for fx, fy in FLOWERS:
        z = _ground_z(gb, fx, fy)
        if z is None:
            continue
        VK.flower_bush(fl, (fx, fy, z), 1.6, rng)
    fl.finish()
    # prateleira de lobulos: pinheirinhos baixos em alguns lobulos (transicao para o penhasco)
    sh = MB("VEG_Shelf", C, random.Random(SEED + 3), detail="far")
    ns = 0
    pts = L.SHELF_RIM
    for i in range(0, len(pts), 3):
        x, y = pts[i]
        cx, cy = x * 0.94, y * 0.94
        if abs(cx) < 30 and cy < -100:             # sob a ponte de chegada
            continue
        if not _free_axes(cx, cy) and math.hypot(cx, cy) > L.T1_WALL_R + 1:
            continue
        z = _ground_z(gb, cx, cy)
        if z is None or z > L.G - 3.0:
            continue
        VK.pine(sh, (cx, cy, z), rng.uniform(9.0, 13.0), rng, lod=2, form="young")
        ns += 1
    sh.finish()
    for mb in mbs.values():
        mb.finish()
    print("VEG arvores=%d (recusadas %d) arbustos=%d prateleira=%d grupos=%d" % (
        stats["ok"], stats["fora"], nb, ns, len(mbs)))


def IL_point_in_rim(x, y, inset):
    """dentro do contorno da ilha com folga 'inset' da borda"""
    from fm_lib import point_in_poly
    rim = L.ISLAND_RIM
    if not point_in_poly(x, y, rim):
        return False
    for i in range(len(rim)):
        ax, ay = rim[i]
        bx, by = rim[(i + 1) % len(rim)]
        dx, dy = bx - ax, by - ay
        t = max(0.0, min(1.0, ((x - ax) * dx + (y - ay) * dy) / (dx * dx + dy * dy)))
        if math.hypot(x - ax - dx * t, y - ay - dy * t) < inset:
            return False
    return True
