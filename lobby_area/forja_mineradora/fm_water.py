# fm_water - geografia da agua: NASCENTES (contrafortes NO/NE com entalhe em V e bacia de rocha, cachoeira central,
#            2 bicas do terraco) -> CANAL do ledge -> VERTEDOURO (parte vai pela CALHA da roda) -> TANQUE -> RIO
#            (2 corredeiras) -> roda d'agua de peito (aciona o eixo da forja) -> grade, bica e queda no penhasco sul
import math, random
from mathutils import Vector
from fm_lib import MB, D, col_box, col_box2, marker, light, resample, bezier
from fm_parts import (Frame, stone_parapet, fence, masonry_wall, timber_wall, window_glow, cliff_band, rock_scatter,
                      hanging_lantern, lantern, crate, barrel, stairs, P3, arch)
import fm_layout as L
import fm_water_kit as WK

C = "05_WATER_SYSTEM"
F0 = L.FLOOR
WZ_RIVER = 2.8
WZ_CANAL = 13.2
WZ_TERR = L.TERR - 0.7
# rio em 3 trechos (montante -> jusante): 2 corredeiras de ~0.55, longe das pontes (y 41 e -18) e da roda (y 8..32)
RAPIDS = (-3.0, -43.0)
RIVER_LEVELS = ((2.8, 47.2, RAPIDS[0]), (2.25, RAPIDS[0] - 1.6, RAPIDS[1]), (1.7, RAPIDS[1] - 1.6, -62.2))
# calha da roda de peito: sai do vertedouro e despeja no quadrante norte da roda (fundo externo >= 11.9 sobre a ponte)
FLUME = dict(x=L.WHEEL_C[0], y0=60.6, y1=30.0, z0=12.55, z1=12.25, w=3.0, t=0.35, side_h=1.05)
TRESTLES_Y = (55.0, 45.6, 36.0)
# o wheel_house (fora deste passe) recebia o Random(606) depois de pool_and_river + wheel consumirem 3464 palavras
# de 32 bits: reproduz o mesmo estado para a casa da roda e as pontes sairem identicas
_HOUSE_RNG_SKIP = 3464
# madeira e ferro molhados: variante fixa (1 MeshPart por material, sem sorteio de variantes)
WOOD_WET = "Wood_Dark_C"
WOOD_BOARD = "Wood_Plank_C"
IRON_WET = "Metal_Rust"
MOSS = "Grass_Dark"


def waterfall(mb, top, bottom_z, width, rng, out=(0, -1), lip=1.5, foam=True, tiers=1, name=None):
    """(compatibilidade) cachoeira em laminas do fm_water_kit"""
    return WK.cascade(mb, top, bottom_z, width, rng, out=out, lip=lip, ring=foam)


def level_at(y):
    """cota da agua do rio em y (nas corredeiras vale o trecho de cima)"""
    for z, ya, yb in RIVER_LEVELS:
        if y >= yb:
            return z
    return RIVER_LEVELS[-1][0]


def _minus(a, b, holes):
    """intervalo [a, b] (a < b) menos os buracos"""
    out = [(a, b)]
    for h0, h1 in holes:
        nxt = []
        for s0, s1 in out:
            if h1 <= s0 or h0 >= s1:
                nxt.append((s0, s1))
                continue
            if h0 > s0:
                nxt.append((s0, h0))
            if h1 < s1:
                nxt.append((h1, s1))
        out = nxt
    return out


def build():
    falls = MB("WATER_Waterfalls", C, random.Random(611))
    canal(falls)
    pool_and_river(random.Random(606))
    wheel(random.Random(607))
    rng = random.Random(606)
    for _ in range(_HOUSE_RNG_SKIP):
        rng.getrandbits(32)
    wheel_house(rng)
    bridges(rng)
    sources(random.Random(612), falls)
    falls.finish()


def canal(mb):
    """canal do ledge + vertedouro; a queda livre do vertedouro fica a oeste, a leste a agua entra na calha da roda"""
    rng = random.Random(611)
    y0, y1 = L.CANAL_Y
    # (face sul recuada 0.05 da parede interna do canal: sem z-fighting com o TER_MidLedge)
    mb.box2((L.WEST_X + 1, y0 + 1.65, 11.5), (L.EAST_X - 1, y1 - 0.6, WZ_CANAL), "Water", 0.0)
    sx = L.SPILL_X
    mb.box2((sx - 3.5, L.MID_FRONT_Y, 11.5), (sx + 3.5, y0 + 1.55, WZ_CANAL - 0.3), "Water", 0.0)
    # soleira de pedra do vertedouro
    mb.box2((sx - 4.6, L.MID_FRONT_Y - 1.2, 11.0), (sx + 4.6, L.MID_FRONT_Y + 0.4, 12.4), "Stone_Light", 0.2)
    # lamina sobre a soleira que alimenta a calha (leste)
    fx, fw = FLUME["x"], FLUME["w"]
    mb.box2((fx - fw / 2 + 0.1, FLUME["y0"], 12.4), (fx + fw / 2 - 0.1, L.MID_FRONT_Y + 0.2, 12.86), "Water", 0.0)
    # queda livre do vertedouro (oeste da calha), 2 fios
    WK.cascade(mb, (sx - 1.6, L.MID_FRONT_Y - 0.6, WZ_CANAL - 0.4), WZ_RIVER, 3.0, rng, out=(0, -1), lip=2.2,
               streams=((0.0, 1.0), (-1.75, 0.32)), stripes=2, ring_z=WZ_RIVER)
    # linhas de corrente (espuma) no canal apontando para o vertedouro
    for i in range(22):
        x = rng.uniform(L.WEST_X + 4, L.EAST_X - 4)
        y = rng.uniform(y0 + 2.5, y1 - 1.5)
        mb.box((rng.uniform(2, 5), 0.25, 0.08), (x, y, WZ_CANAL + 0.03), (0, 0, rng.uniform(-0.08, 0.08)), "Foam", 0.0)


# ------------------------------------------------------------------ tanque + rio
def _coping(mb, x, ya, yb, inward, rng, z0=2.55):
    """capeamento irregular do muro do rio: blocos de comprimentos/alturas diferentes, alguns saindo para a agua"""
    y = ya
    while y > yb + 0.3:
        ln = min(rng.uniform(2.0, 3.8), y - yb)
        top = F0 + rng.uniform(-0.05, 0.42)
        out = rng.uniform(0.0, 0.18) if rng.random() < 0.75 else rng.uniform(0.3, 0.55)
        th = 1.2 + out
        cx = x + inward * out / 2
        m = "Stone_Light" if rng.random() > 0.3 else "Stone_Dark"
        mb.box((th, ln - 0.1, top - z0), (cx, y - ln / 2, (top + z0) / 2), (0, 0, rng.uniform(-0.035, 0.035)), m, 0.14)
        y -= ln


def _mureta(mb, x, ya, yb, rng, side):
    """mureta de pedra seca na margem (no lugar da cerca), blocos irregulares, um ou outro faltando"""
    y = ya
    while y > yb + 0.4:
        ln = min(rng.uniform(1.5, 2.6), y - yb)
        if rng.random() < 0.1 and y - ln > yb + 1:
            y -= ln          # bloco caido: vira pedra solta ao pe
            mb.rock((x + side * rng.uniform(0.8, 1.6), y + ln / 2, F0 + 0.2), (1.1, 1.3, 0.8), "Cliff_Rock", 1,
                    (0, 0, rng.uniform(0, 3)))
            continue
        h = rng.uniform(1.1, 1.6)
        m = "Stone_Light" if rng.random() > 0.35 else "Stone_Dark"
        mb.box((1.15, ln - 0.08, h), (x + rng.uniform(-0.08, 0.08), y - ln / 2, F0 + h / 2 - 0.05),
               (0, rng.uniform(-0.03, 0.03), rng.uniform(-0.05, 0.05)), m, 0.16)
        y -= ln


def _broken_fence(fn, x, ya, yb, rng, side):
    """trecho de cerca quebrado: poste inclinado, travessa caida com a ponta no chao, travessa faltando"""
    n = max(2, int((ya - yb) / 3.8))
    step = (ya - yb) / n
    h = 3.0
    lean_i = rng.randrange(1, n + 1)
    tops = []
    for i in range(n + 1):
        y = ya - i * step
        rx = rng.uniform(-0.05, 0.05)
        ry = (side * rng.uniform(0.18, 0.3)) if i == lean_i else rng.uniform(-0.04, 0.04)
        fn.box((0.9, 0.9, h + 0.5), (x + math.sin(ry) * (h + 0.5) / 2, y, F0 + (h + 0.5) / 2 * math.cos(ry)),
               (rx, ry, rng.uniform(-0.1, 0.1)), WOOD_WET, 0.12)
        tops.append(Vector((x + math.sin(ry) * (h + 0.3), y, F0 + (h + 0.3) * math.cos(ry))))
    for i, (a, b) in enumerate(zip(tops, tops[1:])):
        mode = rng.choice(("ok", "fallen", "missing")) if i else "ok"
        if mode == "ok":
            fn.beam(a + Vector((0, 0, -0.25)), b + Vector((0, 0, -0.25)), 0.45, 0.35, "Wood_Light_C", 0.08)
            fn.beam(a + Vector((0, 0, -1.6)), b + Vector((0, 0, -1.6)), 0.45, 0.35, "Wood_Light_C", 0.08)
        elif mode == "fallen":
            g = Vector((b.x + side * rng.uniform(0.6, 1.4), b.y + rng.uniform(-0.4, 0.4), F0 + 0.25))
            fn.beam(a + Vector((0, 0, -1.6)), g, 0.45, 0.35, "Wood_Light_C", 0.08)
        # "missing": so os postes (travessa sumiu)


def pool_and_river(rng):
    mb = MB("WATER_Pool_River", C, rng)
    px0, py0, px1, py1 = L.POOL
    rx0, rx1 = L.RIVER_X
    # tanque: fundo, agua, borda de pedra (parapeito) exceto por onde o rio sai. A alvenaria so aparece acima da
    # agua (as fiadas submersas nao eram vistas e custavam ~1/2 dos triangulos do rio)
    mb.box2((px0, py0, 0.0), (px1, py1, 1.0), "Stone_Dark", 0.0)
    mb.box2((px0 + 1.2, py0 + 1.2, 1.0), (px1 - 1.2, py1 - 0.2, WZ_RIVER), "Water", 0.0)
    for (a, b) in (((px0 + 0.6, py0 + 0.6), (px0 + 0.6, py1)), ((px1 - 0.6, py0 + 0.6), (px1 - 0.6, py1)),
                   ((px0 + 0.6, py0 + 0.6), (rx0 - 0.6, py0 + 0.6)), ((rx1 + 0.6, py0 + 0.6), (px1 - 0.6, py0 + 0.6))):
        masonry_wall(mb, a, b, 2.4, F0, 1.2, rng, course=1.6, blk=(2.2, 3.6))
        stone_parapet(mb, "Water", [(a[0], a[1], F0), (b[0], b[1], F0)], h=1.6, w=1.4, rng=rng)
    # rio: 3 trechos em cotas diferentes ligados por 2 corredeiras
    ys, ye = py0 + 0.6, -62.0
    mb.box2((rx0, ye - 1, 0.0), (rx1, ys, 1.5), "Stone_Dark", 0.0)
    wx0, wx1 = rx0 + 0.6, rx1 - 0.6
    wheel_zone = (L.WHEEL_C[1] - L.WHEEL_R - 1.5, L.WHEEL_C[1] + L.WHEEL_R + 1.5)
    for lev, ya, yb in RIVER_LEVELS:
        mb.box2((wx0, yb, 1.5), (wx1, ya, lev), "Water", 0.0)
        # faixa central mais funda (le como correnteza, no lugar do tracejado de estrada)
        for s0, s1 in _minus(yb, ya, [wheel_zone]):
            if s1 - s0 > 3:
                mb.box2((wx0 + 1.9, s0 + 1.2, lev - 0.1), (wx1 - 1.9, s1 - 1.2, lev + 0.06), "Water_Deep", 0.0)
    # muro: fiadas baixas so onde a agua e mais baixa + capeamento irregular (cada corredeira fica no trecho de baixo)
    wall_ranges = ((ys, RAPIDS[0] + 0.2, RIVER_LEVELS[0][0]), (RAPIDS[0] + 0.2, RAPIDS[1] + 0.2, RIVER_LEVELS[1][0]),
                   (RAPIDS[1] + 0.2, ye, RIVER_LEVELS[2][0]))
    for ya, yb, lev in wall_ranges:
        for x, inward in ((rx0, 1), (rx1, -1)):
            if lev < 2.6:
                masonry_wall(mb, (x, ya), (x, yb), lev - 0.45, 2.6, 1.2, rng, course=3.05 - lev, blk=(2.4, 4.0))
            _coping(mb, x, ya, yb, inward, rng)
    # corredeiras: rampa de agua branca + faixa de espuma + pedras que furam a lamina
    for (lev_a, ya, yb), (lev_b, _, _) in zip(RIVER_LEVELS, RIVER_LEVELS[1:]):
        yr = yb
        mb.beam(((wx0 + wx1) / 2, yr + 0.2, lev_a - 0.08), ((wx0 + wx1) / 2, yr - 1.8, lev_b - 0.08), wx1 - wx0, 0.2,
                "Water_Fall", 0.0)
        mb.box((wx1 - wx0 - 0.3, 0.9, 0.12), ((wx0 + wx1) / 2, yr - 2.1, lev_b + 0.05), (0, 0, 0), "Foam", 0.0)
        for k in range(3):
            x = rng.uniform(wx0 + 0.8, wx1 - 0.8)
            y = yr - rng.uniform(-0.2, 1.4)
            mb.rock((x, y, lev_b - 0.1), (rng.uniform(1.0, 1.5), rng.uniform(0.9, 1.3), 1.3), "Cliff_Rock", 1,
                    (0, 0, rng.uniform(0, 3)))
        for k in range(2):
            WK.chevron(mb, (rng.uniform(wx0 + 1.5, wx1 - 1.5), yr - 2.8 - k * 1.6), lev_b + 0.07, rng, length=2.4)
        WK.foam_ring(mb, ((wx0 + wx1) / 2, yr - 2.2, lev_b), 2.2, rng, n=5, s=0.8, disc=False)
    # pedras no leito + chevrons de espuma a jusante (V aberto rio abaixo)
    placed = 0
    tries = 0
    while placed < 13 and tries < 200:
        tries += 1
        y = rng.uniform(ye + 3, ys - 3)
        if abs(y - L.WHEEL_C[1]) < 12 or any(abs(y - by) < 5 for by in (L.BRIDGE_MAIN_Y, L.BRIDGE_BACK_Y)):
            continue
        if any(abs(y - (yr - 1.0)) < 3.5 for yr in RAPIDS):
            continue
        lev = level_at(y)
        x = rng.uniform(wx0 + 1.2, wx1 - 1.2)
        sx, sy, sz = rng.uniform(1.0, 1.9), rng.uniform(1.0, 1.8), rng.uniform(1.1, 1.5)
        mb.rock((x, y, lev - 0.35), (sx, sy, sz), "Cliff_Rock" if rng.random() > 0.3 else "Cliff_Rock_Dark", 1,
                (0, 0, rng.uniform(0, 3)))
        WK.chevron(mb, (x, y - sy * 0.45), lev + 0.07, rng)
        placed += 1
    # espuma colada as paredes (quebrada) e pedras saindo da parede na linha d'agua
    for x, inward in ((wx0 + 0.25, 1), (wx1 - 0.25, -1)):
        y = ys - rng.uniform(0.5, 2.0)
        while y > ye - 0.5:
            ln = rng.uniform(1.4, 4.2)
            if abs(y - L.WHEEL_C[1]) > 12.5:
                lev = level_at(y)
                mb.box((0.42, ln, 0.08), (x + inward * rng.uniform(0.0, 0.15), y - ln / 2, lev + 0.05),
                       (0, 0, rng.uniform(-0.04, 0.04)), "Foam", 0.0)
            y -= ln + rng.uniform(1.5, 4.5)
    for k in range(9):
        y = rng.uniform(ye + 3, ys - 3)
        if abs(y - L.WHEEL_C[1]) < 12:
            continue
        side = rng.choice((0, 1))
        x = (wx0 + 0.2) if side == 0 else (wx1 - 0.2)
        mb.rock((x, y, level_at(y) + 0.15), (rng.uniform(0.9, 1.3), rng.uniform(1.0, 1.6), 0.9),
                "Cliff_Rock", 1, (0, 0, rng.uniform(0, 3)))
    # grade de ferro antes da bica (o leito leva ate a borda sul) + bica, fios, nevoa e bacia na face sul
    south_fall(mb, rng)
    # margens: cerca inteira / cerca quebrada / mureta de pedra / margem aberta com pedras (a COL continua a mesma)
    fn = MB("WATER_River_Fences", C, rng)
    wy = L.WHEEL_C[1]
    spans_all = []
    for x in (rx0 - 0.9, rx1 + 0.9):
        spans = [(ye + 1.5, L.BRIDGE_MAIN_Y - 6.0), (L.BRIDGE_MAIN_Y + 6.0, wy - 11.5),
                 (wy + 11.5, L.BRIDGE_BACK_Y - 3.5)]
        if x > rx1:
            spans = [(ye + 1.5, L.BRIDGE_MAIN_Y - 6.0), (L.BRIDGE_MAIN_Y + 6.0, wy - 3.0),
                     (wy + 3.0, L.BRIDGE_BACK_Y - 3.5)]
        side = -1 if x < rx0 else 1           # para fora do rio
        for a, b in spans:
            spans_all.append((x, a, b))
            _bank(mb, fn, x, b, a, side, rng)
    fn.finish()
    # colisao: leito do tanque e rio (o piso do tanque sobe para 3.3: quem cai sai pulando a borda, nao e poco)
    A = "Water"
    col_box2(A, (px0, py0, -2), (px1, py1, 3.3))
    col_box2(A, (rx0, ye - 1, -2), (rx1, ys, 1.5))
    for x in (rx0, rx1):
        col_box2(A, (x - 0.6, ye, 0), (x + 0.6, ys, F0))
    col_box2(A, (px0, py0, 0), (px0 + 1.2, py1, F0 + 1.6))
    col_box2(A, (px1 - 1.2, py0, 0), (px1, py1, F0 + 1.6))
    col_box2(A, (px0, py0, 0), (rx0, py0 + 1.2, F0 + 1.6))
    col_box2(A, (rx1, py0, 0), (px1, py0 + 1.2, F0 + 1.6))
    # guarda-corpo das margens (mesmas caixas do guarda-corpo antigo, agora independentes do visual)
    for x, a, b in spans_all:
        col_box(A, (b - a, 0.8, 5.0), (x, (a + b) / 2, F0 + 2.5), (0, 0, math.pi / 2))
    # guarda invisivel no bordo do vertedouro (passarela z14 -> tanque) e grade atravessando o rio antes da bica
    col_box2(A, (54.0, 61.5, 14.0), (66.0, 62.5, 18.0))
    col_box2(A, (rx0 - 0.5, -62.0, 1.5), (rx1 + 0.5, -61.0, 12.0))
    flume(mb, random.Random(6063))
    mb.finish()


def _bank(mb, fn, x, ya, yb, side, rng):
    """margem de ya (montante) ate yb (jusante): alterna cerca inteira, cerca quebrada, mureta e margem aberta"""
    y = ya
    prev = None
    kinds = ("fence", "broken", "wall", "open")
    wts = (0.36, 0.2, 0.26, 0.18)
    while y > yb + 0.5:
        k = prev
        while k == prev:
            r = rng.random()
            acc = 0.0
            for kk, w in zip(kinds, wts):
                acc += w
                if r <= acc:
                    k = kk
                    break
        ln = {"fence": rng.uniform(7.0, 12.0), "broken": rng.uniform(6.0, 8.5), "wall": rng.uniform(5.0, 9.0),
              "open": rng.uniform(3.5, 6.0)}[k]
        ln = min(ln, y - yb)
        if ln < 2.5:
            k = "wall" if prev != "wall" else "open"
        y1 = y - ln
        if k == "fence":
            fence(fn, "Water", [(x, y, F0), (x, y1, F0)], h=3.0, post_step=4.0, rng=rng, col=False, m=WOOD_WET,
                  rail_m="Wood_Light_C")
        elif k == "broken":
            _broken_fence(fn, x, y, y1, rng, side)
        elif k == "wall":
            _mureta(mb, x, y, y1, rng, side)
        else:
            for j in range(rng.randint(1, 2)):
                yy = y - ln * rng.uniform(0.2, 0.8)
                s = rng.uniform(1.5, 2.4)
                mb.rock((x + side * rng.uniform(-0.2, 0.8), yy, F0 + s * 0.12), (s * 1.3, s, s * 0.75),
                        "Cliff_Rock" if rng.random() > 0.35 else "Cliff_Rock_Dark", 1, (0, 0, rng.uniform(0, 3)))
        prev = k
        y = y1


def south_fall(mb, rng):
    """fim do rio: grade de ferro, bica de pedra projetando 3 studs, lamina que se divide em 2 fios que alargam,
    nuvens de nevoa a meia altura e bacia de rocha em z~-20 na face sul (respingo = VFX_Waterfall_South)"""
    rx0, rx1 = L.RIVER_X
    cx = (rx0 + rx1) / 2
    lev = RIVER_LEVELS[-1][0]
    # grade (barras verticais + 2 travessas chumbadas nos muros)
    for i in range(8):
        x = rx0 + 0.9 + i * (rx1 - rx0 - 1.8) / 7
        mb.box((0.26, 0.26, 3.6), (x, -61.5, 1.4 + 1.8), (0, 0, 0), IRON_WET, 0.0)
    for z in (2.3, 4.6):
        mb.box((rx1 - rx0 + 0.6, 0.34, 0.3), (cx, -61.5, z), (0, 0, 0), IRON_WET, 0.0)
    # bica: calha de pedra saindo da face do penhasco (y -62.35) 3 studs para o sul, sobre 2 misulas
    y0, y1 = -62.0, -65.4
    mb.box2((cx - 2.9, y1, 0.6), (cx + 2.9, y0, 1.45), "Stone_Dark", 0.15)
    for s in (-1, 1):
        mb.box2((cx + s * 2.9 - (0.8 if s > 0 else 0.0), y1, 1.45), (cx + s * 2.9 + (0.0 if s > 0 else 0.8), y0, 2.7),
                "Stone_Light", 0.18)
        mb.beam((cx + s * 2.0, -62.3, -2.2), (cx + s * 2.0, y1 + 0.5, 0.6), 0.9, 1.0, "Stone_Dark", 0.12)
    mb.box2((cx - 2.1, y1 + 0.1, 1.45), (cx + 2.1, y0, lev - 0.03), "Water", 0.0)
    # lamina unica no bocal + labio de espuma
    top = Vector((cx, y1 - 0.05, lev - 0.05))
    pts = WK.fall_path(top, -2.5, (0, -1), 1.3, 4)
    WK.ribbon(mb, pts, [4.0, 3.8, 3.4, 3.0, 2.6], "Water", (1, 0, 0), thick=0.3, bulge=0.25)
    WK.ribbon(mb, [p + Vector((0, -0.2, 0.1)) for p in pts[:3]], [4.1, 3.9, 3.0], "Foam", (1, 0, 0), thick=0.2,
              bulge=0.25)
    # 2 fios que alargam para baixo ate a bacia
    fy = pts[-1].y
    WK.cascade(mb, (cx, fy + 0.1, -1.6), -19.6, 4.0, rng, out=(0, -1), lip=0.6,
               streams=((-1.2, 0.5), (1.35, 0.34)), widen=1.75, stripes=1, lip_foam=False, ring=False, n=5)
    # nevoa a meia altura
    for i, xo in enumerate((-2.4, -0.6, 1.0, 2.6)):
        r = rng.uniform(1.0, 1.7)
        mb.ico(r, (cx + xo + rng.uniform(-0.4, 0.4), fy - rng.uniform(0.6, 1.6), rng.uniform(-14.0, -6.5)), "Foam", 1,
               (1.25, 0.85, 1.15), (0, 0, rng.uniform(0, 3)), jitter=0.25)
    # bacia de rocha apoiada na face sul
    by = fy - 1.2
    poly = [(-6.5, 3.2), (-4.0, -2.8), (0.0, -3.6), (4.2, -2.9), (6.8, 2.8), (0.0, 3.6)]
    from fm_parts import rock_column
    rock_column(mb, Vector((cx, by, 0)), poly, -27.0, -20.2, rng, "Cliff_Rock", taper=0.8, rings=2, jitter=0.1,
                tilt=0.03, chamfer=0.3)
    for s in (-1, 1):
        mb.rock((cx + s * 5.0, by - 1.0, -19.8), (3.2, 2.6, 2.0), "Cliff_Rock_Dark", 1, (0, 0, rng.uniform(0, 3)))
    mb.cyl(3.6, 0.3, (cx, by + 0.2, -20.1), (0, 0, 0.3), "Water", 8, bevel=0.0)
    WK.foam_ring(mb, (cx, by + 0.4, -19.95), 2.6, rng, n=6, s=1.0)
    # transborda da bacia e continua para o vale distante (fio fino)
    WK.cascade(mb, (cx + 1.2, by - 3.4, -20.0), -44.0, 2.0, rng, out=(0, -1), lip=0.8, stripes=0, ring=False,
               lip_foam=True, n=5)
    marker("VFX_Waterfall_South", (cx, by + 0.4, -19.6), (0, 0, 0), 3)


def flume(mb, rng):
    """calha de madeira da roda de PEITO: sai da soleira do vertedouro (comporta), corre para o sul sobre cavaletes
    (tanque, junto da ponte dos fundos) e despeja no quadrante norte da roda. Tabuas molhadas, musgo, cintas de ferro."""
    fx, y0, y1, z0, z1, w, t, sh = (FLUME[k] for k in ("x", "y0", "y1", "z0", "z1", "w", "t", "side_h"))

    def zf(y):                       # piso interno
        return z0 + (z1 - z0) * (y0 - y) / (y0 - y1)
    # tabuleiro em 3 lances (juntas nos cavaletes): fundo + 2 costados
    cuts = [y0] + [ty for ty in TRESTLES_Y] + [y1]
    for a, b in zip(cuts, cuts[1:]):
        za, zb = zf(a), zf(b)
        for s in (-1, 1):
            mb.beam((fx + s * (w / 2 + t / 2), a, za + (sh - t) / 2), (fx + s * (w / 2 + t / 2), b, zb + (sh - t) / 2),
                    t, sh + t, WOOD_BOARD, 0.05)
        mb.beam((fx, a, za - t / 2), (fx, b, zb - t / 2), w + 0.02, t, WOOD_WET, 0.05)
        # agua correndo na calha + estrias de espuma
        mb.beam((fx, a, za + 0.2), (fx, b, zb + 0.2), w - 0.05, 0.3, "Water", 0.0)
    for k in range(4):
        y = rng.uniform(y1 + 1.5, y0 - 3)
        mb.box((0.3, rng.uniform(2.0, 4.0), 0.06), (fx + rng.uniform(-0.9, 0.9), y, zf(y) + 0.37), (0, 0, 0), "Foam", 0.0)
    # cangas (moldura em U a cada ~6) com cinta de ferro
    ny = int((y0 - y1) / 7.5)
    bridge = (L.BRIDGE_BACK_Y - 4.2, L.BRIDGE_BACK_Y + 4.2)     # nada abaixo de 11.9 sobre o tabuleiro
    for i in range(ny + 1):
        y = y0 - 0.4 - i * (y0 - y1 - 0.8) / ny
        if bridge[0] < y < bridge[1]:
            continue
        z = zf(y)
        for s in (-1, 1):
            mb.box((0.42, 0.5, sh + t + 0.35), (fx + s * (w / 2 + t + 0.21), y, z - t + (sh + t + 0.35) / 2 - 0.35),
                   (0, 0, 0), WOOD_WET, 0.06)
        mb.box((w + 2 * t + 0.84, 0.5, 0.42), (fx, y, z - t - 0.21), (0, 0, 0), WOOD_WET, 0.06)
    # cavaletes: 2 pernas + chapeu + X de travamento (pernas no fundo do tanque / leito do rio)
    for ty in TRESTLES_Y:
        base = 1.0 if ty > L.POOL[1] else 1.5
        top = zf(ty) - t
        for s in (-1, 1):
            mb.beam((fx + s * 2.1, ty, base), (fx + s * 1.9, ty, top - 0.5), 0.6, 0.6, WOOD_WET, 0.06)
        mb.box((w + 2 * t + 2.2, 0.7, 0.5), (fx, ty, top - 0.25), (0, 0, 0), WOOD_WET, 0.06)
        mb.box((w + 2 * t + 2.3, 0.78, 0.16), (fx, ty, top - 0.3), (0, 0, 0), IRON_WET, 0.0)
        mb.beam((fx - 2.0, ty - 0.35, base + 1.8), (fx + 1.9, ty - 0.35, top - 1.0), 0.35, 0.3, WOOD_WET, 0.04)
        mb.beam((fx + 2.0, ty + 0.35, base + 1.8), (fx - 1.9, ty + 0.35, top - 1.0), 0.35, 0.3, WOOD_WET, 0.04)
        # musgo na linha d'agua das pernas e espuma a jusante
        lev = level_at(ty) if ty < L.POOL[1] else WZ_RIVER
        for s in (-1, 1):
            mb.ico(0.55, (fx + s * 2.05, ty, lev + 0.2), MOSS, 1, (1.2, 1.2, 0.8), jitter=0.2)
        if ty < L.POOL[1]:
            WK.chevron(mb, (fx - 2.1, ty - 0.4), lev + 0.07, rng, length=1.8)
            WK.chevron(mb, (fx + 2.1, ty - 0.4), lev + 0.07, rng, length=1.8)
    # mao-francesa segurando o balanco final (do cavalete de y36 ate a ponta sobre a roda)
    ty = TRESTLES_Y[-1]
    for s in (-1, 1):
        mb.beam((fx + s * 1.95, ty - 0.3, zf(ty) - t - 3.2), (fx + s * 1.95, y1 + 1.4, zf(y1 + 1.4) - t - 0.2), 0.4, 0.4,
                WOOD_WET, 0.04)
    # musgo nas juntas da calha (tufos achatados pendurados na quina de baixo dos costados, onde a agua vaza)
    for ty in (y0 - 0.2,) + TRESTLES_Y:
        for s in (-1, 1):
            if rng.random() < 0.7:
                mb.ico(rng.uniform(0.35, 0.55), (fx + s * (w / 2 + t + 0.05), ty + rng.uniform(-0.6, 0.6), zf(ty) - t - 0.1),
                       MOSS, 1, (0.8, 1.6, 0.9), (0, 0, rng.uniform(0, 3)), jitter=0.25)
    # comporta na soleira: 2 montantes, prancha levantada, travessa com volante
    gy = y0 + 0.35
    for s in (-1, 1):
        mb.box((0.5, 0.5, 3.2), (fx + s * (w / 2 + t + 0.25), gy, z0 + 1.2), (0, 0, 0), WOOD_WET, 0.06)
    mb.box((w + 2 * t + 1.1, 0.55, 0.45), (fx, gy, z0 + 2.9), (0, 0, 0), WOOD_WET, 0.06)
    mb.box((w + 0.1, 0.22, 1.0), (fx, gy, z0 + 2.0), (0, 0, 0), WOOD_BOARD, 0.04)
    mb.rod((fx, gy, z0 + 3.1), (fx, gy, z0 + 3.9), 0.1, IRON_WET, 5)
    mb.cyl(0.55, 0.14, (fx, gy, z0 + 3.95), (0, 0, 0), IRON_WET, 8, bevel=0.0)
    # ponta: a agua despeja nas pas do quadrante norte (roda de peito) e desce presa entre as pas e o peito
    wx, wyc = L.WHEEL_C
    R = L.WHEEL_R
    ye = y1
    zt = zf(ye) + 0.3
    pts = WK.fall_path((fx, ye - 0.05, zt), zt - 1.6, (0, -1), 0.6, 3)
    WK.ribbon(mb, pts, [w - 0.2, w - 0.25, w - 0.35, w - 0.45], "Water", (1, 0, 0), thick=0.28, bulge=0.2)
    WK.ribbon(mb, [p + Vector((0, 0.05, 0.12)) for p in pts[:3]], [w * 0.95, w * 0.85, w * 0.5], "Foam", (1, 0, 0),
              thick=0.18, bulge=0.2)
    rr = R + 0.3                                       # entre a ponta das pas (R) e o peito (R + 0.55)
    bucket = [Vector((fx, wyc + math.cos(a) * rr, 11.0 + math.sin(a) * rr))
              for a in (math.radians(d) for d in (4, -8, -20, -32, -44, -56))]
    WK.ribbon(mb, bucket, [w - 0.6] * len(bucket), "Water", (1, 0, 0), thick=0.2, bulge=0.12, flat=True)
    WK.ribbon(mb, [p + (p - Vector((fx, wyc, 11.0))).normalized() * -0.08 for p in bucket[:4]],
              [w * 0.35, w * 0.4, w * 0.3, w * 0.2], "Water_Fall", (1, 0, 0), thick=0.1, flat=True)
    # respingo na entrada: espuma achatada contra as pas
    for a, r in ((6, 0.7), (-2, 0.55)):
        aa = math.radians(a)
        mb.ico(r, (fx + rng.uniform(-0.8, 0.8), wyc + math.cos(aa) * (R + 0.1), 11.0 + math.sin(aa) * (R + 0.1) + 0.4),
               "Foam", 1, (1.5, 0.7, 0.8), (0, 0, rng.uniform(0, 3)), jitter=0.22)
    # peito: aba curva de tabuas acompanhando a roda por baixo da entrada d'agua (mantem a agua nas pas)
    arc_pts = [Vector((fx, wyc + math.cos(a) * (R + 0.75), 11.0 + math.sin(a) * (R + 0.75)))
               for a in (math.radians(d) for d in (6, -10, -26, -42, -58))]
    mb.sweep(arc_pts, [(-2.05, -0.2), (2.05, -0.2), (2.05, 0.2), (-2.05, 0.2)], WOOD_BOARD, True, up=(1, 0, 0))
    for p in arc_pts[1::2]:
        mb.box((4.5, 0.4, 0.4), (fx, p.y + 0.3, p.z), (0, 0, 0), WOOD_WET, 0.04)
    # mancais de alvenaria (no lugar das caixas lisas) com capitel de madeira, chapa de ferro e musgo
    for x, zb in ((L.RIVER_X[1] + 1.8, F0 - 0.2), (L.RIVER_X[0] - 1.8, F0 - 0.2)):
        masonry_wall(mb, (x, wyc - 1.55), (x, wyc + 1.55), zb, 9.0, 2.4, rng, course=1.3, mix=0.35, blk=(1.3, 1.7))
        mb.box((2.9, 3.7, 0.9), (x, wyc, 9.45), (0, 0, 0), WOOD_WET, 0.1)
        mb.box((3.0, 3.8, 0.18), (x, wyc, 9.35), (0, 0, 0), IRON_WET, 0.0)
        # musgo: tufos na base (umida) e escorrendo da face norte, que recebe os respingos
        for k in range(4):
            yface = wyc + (1.62 if k < 3 else -1.62)
            zz = 8.4 - k * 1.3 if k < 3 else F0 + 0.4
            mb.ico(rng.uniform(0.45, 0.7), (x + rng.uniform(-0.8, 0.8), yface, zz), MOSS, 1,
                   (1.2, 0.6, 1.3 if k < 3 else 0.8), (0, 0, rng.uniform(0, 3)), jitter=0.25)


# ------------------------------------------------------------------ roda d'agua (rotor intocado)
def wheel(rng):
    """roda d'agua de PEITO: a calha despeja no quadrante norte; eixo em X a z11 entra na casa da roda e segue ate a
    ala dos foles. Rotor (raio, pas, cubo) intocado: o export_vfx le. Mancais de alvenaria ficam no WATER_Pool_River."""
    wx, wy = L.WHEEL_C
    R = L.WHEEL_R
    az = 11.0
    mb = MB("WATER_Waterwheel", C, rng)
    Wd = 3.4
    for s in (-1, 1):
        x = wx + s * Wd / 2
        pts = [Vector((x, wy + math.cos(D(a)) * R, az + math.sin(D(a)) * R)) for a in range(0, 361, 15)]
        mb.sweep(pts, [(-0.35, -0.45), (0.35, -0.45), (0.35, 0.45), (-0.35, 0.45)], "Wood_Dark", True, up=(1, 0, 0))
        pts2 = [Vector((x, wy + math.cos(D(a)) * (R - 2.2), az + math.sin(D(a)) * (R - 2.2))) for a in range(0, 361, 20)]
        mb.sweep(pts2, [(-0.25, -0.3), (0.25, -0.3), (0.25, 0.3), (-0.25, 0.3)], "Wood_Dark", True, up=(1, 0, 0))
        for k in range(8):
            a = D(k * 45 + 10)
            mb.beam((x, wy, az), (x, wy + math.cos(a) * (R - 0.3), az + math.sin(a) * (R - 0.3)), 0.55, 0.55, "Wood_Light", 0.05)
        # aro de ferro
        pts3 = [Vector((x + s * 0.4, wy + math.cos(D(a)) * (R + 0.1), az + math.sin(D(a)) * (R + 0.1))) for a in range(0, 361, 15)]
        mb.sweep(pts3, [(-0.1, -0.2), (0.1, -0.2), (0.1, 0.2), (-0.1, 0.2)], "Metal_Iron", True, up=(1, 0, 0))
    # pas entre os aros
    for k in range(16):
        a = D(k * 22.5)
        p = Vector((wx, wy + math.cos(a) * (R - 1.1), az + math.sin(a) * (R - 1.1)))
        mb.box((Wd + 0.4, 0.35, 2.2), p, (a, 0, 0), "Wood_Plank", 0.05)
    # cubo e eixo (roda -> mancal leste; roda -> casa da roda -> ala dos foles)
    mb.cyl(1.4, Wd + 1.2, (wx, wy, az), (0, D(90), 0), "Metal_Dark", 12, bevel=0.1)
    mb.rod((wx + 6.5, wy, az), (L.MILL[0] + 1.6, wy, az), 0.6, "Wood_Dark", 10)
    # eixo alto (z 15.5): sai da casa da roda, cruza o vao por cima da passagem e entra na ala dos foles
    mb.rod((L.MILL[0] + 2.2, wy, 15.5), (L.FORGE_WING_R[2] - 0.8, wy, 15.5), 0.5, "Wood_Dark", 10)
    for x in (L.MILL[0] - 0.3, L.FORGE_WING_R[2] + 0.3):
        mb.box((0.8, 1.6, 1.6), (x, wy, 15.5), (0, 0, 0), "Metal_Iron", 0.08)
    for x in (wx - 3.0, wx + 3.0):
        mb.cyl(0.9, 0.6, (x, wy, az), (0, D(90), 0), "Metal_Iron", 10, bevel=0.0)
    # caixas de mancal (ferro) sobre os pilares de alvenaria (os pilares estao no WATER_Pool_River)
    mb.box((2.8, 3.4, 1.4), (L.RIVER_X[1] + 1.8, wy, az - 0.4), (0, 0, 0), "Metal_Iron", 0.1)
    mb.box((2.6, 3.4, 1.4), (L.RIVER_X[0] - 1.8, wy, az - 0.4), (0, 0, 0), "Metal_Iron", 0.1)
    # canal de fuga (rego) de tabuas em volta da roda
    for s in (-1, 1):
        mb.box2((wx + s * (Wd / 2 + 0.9) - 0.4, wy - R - 3, 1.2), (wx + s * (Wd / 2 + 0.9) + 0.4, wy + R + 3, 3.6),
                "Wood_Plank", 0.06)
    mb.finish()
    col_box2("Water", (wx - Wd / 2 - 1.3, wy - R - 1, 0), (wx + Wd / 2 + 1.3, wy + R + 1, az + R + 1))
    col_box2("Water", (L.RIVER_X[1] + 0.5, wy - 1.6, F0), (L.RIVER_X[1] + 3.1, wy + 1.6, az))
    marker("VFX_Waterwheel_Rotate", (wx, wy, az), (0, D(90), 0), 4, "SINGLE_ARROW",
           props={"axis": "X", "rpm": 6, "note": "girar Waterwheel em torno do eixo X"})
    # a agua da calha bate nas pas do quadrante norte (roda de peito); a saida das pas e no rego, embaixo
    hz = FLUME["z1"] + 0.3 - 1.6
    marker("VFX_Wheel_Splash", (wx, wy + math.sqrt(max(0.0, R * R - (az - hz) ** 2)) - 0.2, hz), (0, 0, 0), 2,
           props={"tipo": "roda de peito", "note": "agua da calha entra nas pas (quadrante norte)"})
    marker("VFX_Wheel_Tailrace", (wx, wy - R * 0.55, WZ_RIVER), (0, 0, 0), 2,
           props={"note": "pas saem da agua no rego (lado jusante, embaixo)"})


def wheel_house(rng):
    """casa da roda: eixo baixo (roda) -> roda de coroa -> pinhao no eixo alto (foles da forja); cames do eixo baixo
    acionam o martinete da oficina de refino. Porta para o patio sul.
    Passe fix2 - cara INDUSTRIAL (nao e casa de morar): terreo de pedra com FAIXA DE UMIDADE escura embaixo,
    tabuas verticais com mata-juntas em cima, CHAPAS DE MANCAL de ferro aparafusadas onde os eixos atravessam as
    paredes, ventilador de cumeeira (lanternim), guincho coberto no oitao sul, telheiro leste sobre a entrada do
    eixo da roda, ardosia com musgo; sem flores nem postigos pintados.
    O maquinario (eixo, coroa, pinhao, cames, martinete) e o MESMO de antes (o export_vfx separa por ilha).
    Rng: a casca usa um rng proprio e, no fim, o rng compartilhado avanca exatamente o que a versao anterior
    consumia (as pontes e as nascentes, construidas depois, nao mudam)."""
    from fm_arch_house import house
    import fm_arch_kit as K
    st0 = rng.getstate()
    wr = random.Random(st0[1][0] ^ 0x5A17)
    x0, y0, x1, y1 = L.MILL
    wy = L.WHEEL_C[1]
    az = 11.0
    uz = 15.5
    t = 1.4
    ze = F0 + 14.0
    ds0, ds1 = 6.5, 11.5
    FW = Frame((x0 + x1) / 2, (y0 + y1) / 2, 0.0, 0.0)
    V = dict(
        t=t, lower="stone", upper="board", zs=5.0, ze=14.0, pitch=40.0, door=(ds0, ds1, 8.0, 2.5), course=1.7,
        blk=(3.4, 5.6), damp=1.6, stone_bev=0.1,
        wins={0: [(1.5, 4.5, 8.5, 11.5, "grid")], 1: [(2.0, 5.0, 8.0, 11.0, "two")],
              2: [(4.0, 8.0, 7.0, 10.5, "grid+lit")], 3: [(3.2, 4.0, 1.9, 4.2, "slit"), (10.4, 11.2, 1.9, 4.2, "slit")]},
        holes_t={1: [(wy - y0 - 1.2, wy - y0 + 1.2, az - 1.2 - F0, az + 1.2 - F0)],
                 3: [(y1 - wy - 1.0, y1 - wy + 1.0, uz - 1.0 - F0, uz + 1.0 - F0)]},
        roof=dict(family="slate", over=(1.3, 1.3), ends=(1.3, 1.1), rafters=2.4, sag=0.4, alt=0.04),
        gables={0: dict(window=(2.0, 1.4, 1.45)), 1: dict(window=(1.8, 1.8, 2.2, "round"))},
        lean=[dict(edge=1, s0=3.0, s1=13.0, depth=3.4, z_hi=12.4, z_lo=10.6, content=None)],
        floor_top=0.35, back=(2,), ties=True,
    )
    mb = K.AMB("BLD_WheelHouse", "07_BUILDINGS", wr)
    A = "WheelHouse"
    info = house(mb, FW, x1 - x0, y1 - y0, F0, wr, V, area=A, name="WheelHouse")
    z_r = info["z_r"]
    # chapas de mancal: placa de ferro aparafusada + cinta, por fora das paredes onde os eixos atravessam
    for (xp, zp, sgn) in ((x1 + 0.05, az, 1), (x0 - 0.05, uz, -1)):
        mb.box((0.3, 3.4, 3.4), (xp, wy, zp), (0, 0, 0), "Metal_Iron", 0.06)
        mb.box((0.5, 4.2, 0.6), (xp + sgn * 0.1, wy, zp + 1.9), (0, 0, 0), "Metal_Dark", 0.0)
        mb.box((0.5, 4.2, 0.6), (xp + sgn * 0.1, wy, zp - 1.9), (0, 0, 0), "Metal_Dark", 0.0)
        for dy in (-1.3, 1.3):
            for dz in (-1.3, 1.3):
                mb.box((0.35, 0.4, 0.4), (xp + sgn * 0.2, wy + dy, zp + dz), (0, 0, 0), "Metal_Dark", 0.0)
    # ventilador de cumeeira (lanternim) com venezianas: a casa trabalha, esquenta e respira
    FV = Frame((x0 + x1) / 2, (y0 + y1) / 2 + 1.5, 0.0, 0.0)
    K.lbox(mb, FV, (2.6, 4.2, 1.8), 0, 0, z_r + 0.9, "Wood_Dark", 0.0)
    for k in range(3):
        for sx in (-1, 1):
            K.lbox(mb, FV, (0.2, 3.8, 0.35), sx * 1.35, 0, z_r + 0.5 + k * 0.5, "Wood_Plank", 0.0, ry=sx * 0.5)
    K.gable_roof(mb, FV, 0.0, -2.1, 2.1, z_r + 3.0, wr, sides=((1.3, z_r + 1.8, 0.5), (1.3, z_r + 1.8, 0.5)),
                 ends=((0.4, 0.0), (0.4, 0.0)), m="Roof", m2="Roof_Moss", sag=0.0, tile=(1.2, 1.8), course=1.0,
                 th=0.3, lip=0.2, horn_len=0.5, ridge_w=0.6, bevel=0.0, fascia=False)
    # guincho no oitao sul: viga saliente + roldana + corda + caixote, com telhadinho proprio (lucam)
    cxm = (x0 + x1) / 2
    ygab = y0 - 0.3
    hz = ze + 3.0
    mb.beam((cxm, ygab + 2.2, hz), (cxm, ygab - 3.5, hz), 0.8, 0.9, "Wood_Dark", 0.0)
    FH = Frame(cxm, ygab, 0.0, 0.0)
    K.gable_roof(mb, FH, 0.0, -3.4, 0.0, hz + 1.6, wr, sides=((1.2, hz + 0.55, 0.35), (1.2, hz + 0.55, 0.35)),
                 ends=((0.3, 0.0), (0.0, 0.0)), m="Roof", m2="Roof_Moss", sag=0.0, tile=(1.2, 1.8), course=1.1,
                 th=0.34, lip=0.24, horn_len=0.6, ridge_w=0.7, horns=(True, False), bevel=0.0)
    for sx in (-1, 1):
        K.lbox(mb, FH, (0.35, 0.35, 0.8), sx * 1.15, -3.1, hz + 0.3, "Wood_Dark", 0.0)
    mb.cyl(0.55, 0.35, (cxm, ygab - 3.0, hz - 0.8), (0, D(90), 0), "Metal_Dark", 10, bevel=0.0)
    mb.rod((cxm, ygab - 3.0, hz - 1.3), (cxm, ygab - 3.0, 17.4), 0.09, "Wood_Light", 4)
    mb.box((0.5, 0.5, 0.35), (cxm, ygab - 3.0, 17.3), (0, 0, 0), "Metal_Dark", 0.0)
    K.lbox(mb, FH, (1.6, 1.6, 1.5), 0.0, -3.0, 15.5 + 0.75, "Wood_Plank", 0.0, rz=0.35)
    K.lbox(mb, FH, (1.7, 1.7, 0.25), 0.0, -3.0, 15.5 + 1.2, "Wood_Dark", 0.0, rz=0.35)
    from fm_parts import pave_poly
    pave_poly(mb, [(x0 + t, y0 + t), (x1 - t, y0 + t), (x1 - t, y1 - t), (x0 + t, y1 - t)], F0 + 0.05, wr, tile=2.4,
              h=0.3, grout=False, bevel=0.0, m="Stone_Dark")
    # ---------------------------------------------------------------- maquinario (inalterado: export_vfx)
    # eixo baixo (roda) ate a roda de coroa
    mb.rod((x1, wy, az), (x0 + 1.6, wy, az), 0.6, "Wood_Dark", 10)
    gx = x0 + 2.4
    def gear(cx, r, z, teeth, m="Wood_Light"):
        mb.cyl(r, 0.8, (cx, wy, z), (0, D(90), 0), m, 20, bevel=0.1)
        mb.cyl(r * 0.35, 1.2, (cx, wy, z), (0, D(90), 0), "Metal_Dark", 10, bevel=0.05)
        for k in range(teeth):
            a = k / teeth * math.tau
            mb.box((1.0, 0.55, 0.7), (cx, wy + math.cos(a) * (r + 0.25), z + math.sin(a) * (r + 0.25)), (a, 0, 0),
                   "Wood_Dark", 0.03)
        for k in range(4):
            a = k / 4 * math.pi
            mb.beam((cx, wy - math.cos(a) * r * 0.9, z - math.sin(a) * r * 0.9),
                    (cx, wy + math.cos(a) * r * 0.9, z + math.sin(a) * r * 0.9), 0.9, 0.4, "Wood_Dark", 0.03)
    gear(gx, 2.9, az, 18)
    gear(gx, 1.3, uz, 9)
    mb.rod((gx - 0.4, wy, uz), (x0 - 0.5, wy, uz), 0.5, "Wood_Dark", 10)
    for s in (-1, 1):
        mb.box((0.8, 0.8, uz + 1.2 - F0), (gx + 1.4, wy + s * 1.6, (F0 + uz + 1.2) / 2), (0, 0, 0), "Wood_Dark", 0.08)
    mb.box((1.0, 4.0, 0.8), (gx + 1.4, wy, uz - 0.9), (0, 0, 0), "Wood_Dark", 0.08)
    # cames no eixo baixo + martinete (pivo ao norte, cabeca ao sul)
    hx = x0 + 5.5
    for k in range(3):
        a = k * math.tau / 3
        mb.beam((hx, wy, az), (hx, wy + math.cos(a) * 2.0, az + math.sin(a) * 2.0), 0.5, 0.8, "Metal_Iron", 0.05)
    piv = Vector((hx, wy + 5.0, 9.0))
    head = Vector((hx, wy - 4.0, 8.0))
    for s in (-1, 1):
        mb.box((0.8, 0.8, 9.0 - F0), (hx + s * 1.2, piv.y, (F0 + 9.0) / 2), (0, 0, 0), "Wood_Dark", 0.1)
    mb.beam(piv + Vector((0, 1.0, 0)), head, 0.9, 0.9, "Wood_Dark", 0.08)
    mb.box((1.8, 1.8, 2.0), head + Vector((0, 0, -0.8)), (0, 0, 0), "Metal_Dark", 0.12)
    mb.box((2.4, 2.4, 2.6), (hx, head.y, F0 + 1.3), (0, 0, 0), "Metal_Iron", 0.12)
    mb.box((1.2, 0.7, 0.3), (hx, head.y, F0 + 2.75), (0, 0, 0), "Metal_Heated", 0.05)
    # ---------------------------------------------------------------- oficina de refino
    mb.box2((x1 - 5.0, y1 - 7.0, F0), (x1 - 1.8, y1 - 2.0, F0 + 3.0), "Wood_Plank", 0.0)
    for k in range(6):
        mb.box((1.1, 0.6, 0.45), (x1 - 3.4 + (k % 2) * 1.2 - 0.6, y1 - 6.0 + (k // 2) * 1.2, F0 + 3.25), (0, 0, 0),
               "Metal_Iron", 0.0)
    hanging_lantern(mb, ((x0 + x1) / 2 + 1.5, (y0 + y1) / 2, ze - 0.3), name="L_WheelHouse", chain=4.0)
    lantern(mb, (x0 + ds1 + 2.6, y0 - 1.9, F0), D(180), name="L_WheelHouse_Door", h=6.0)
    mb.finish()
    # casca (paredes com vao da porta, telhado, piso) criada por house(); aqui so o maquinario
    col_box2(A, (x0 + ds1 + 1.9, y0 - 2.6, F0), (x0 + ds1 + 3.3, y0 - 1.2, F0 + 7.5))
    col_box2(A, (x0 - 0.5, y0 - 0.5, ze), (x1 + 0.5, y1 + 0.5, ze + 6))
    col_box2(A, (hx - 1.6, wy - 5.5, F0), (hx + 1.6, wy + 6.5, F0 + 3.0))
    col_box2(A, (gx - 1.0, wy - 3.5, F0), (gx + 2.0, wy + 3.5, uz + 1.5))
    col_box2(A, (x1 - 5.0, y1 - 7.0, F0), (x1 - 1.8, y1 - 2.0, F0 + 3.0))
    marker("DOOR_WheelHouse", (x0 + (ds0 + ds1) / 2, y0, F0), (0, 0, 0), 1.5)
    # cotas do maquinario gravadas no marcador (o export_vfx pode ler daqui em vez de copiar constantes)
    marker("VFX_TripHammer", tuple(head), (0, 0, 0), 1.5,
           props={"anim": "martinete sobe/desce 1x por volta de came", "pivot": tuple(piv), "axis": (1.0, 0.0, 0.0),
                  "cams": 3, "cam_len": 2.0, "cam_x": hx, "low_axle": (x1, wy, az), "high_axle_z": uz,
                  "gear_x": gx, "crown_r": 2.9, "crown_teeth": 18, "pinion_r": 1.3, "pinion_teeth": 9,
                  "ratio": 2.0})
    # o rng compartilhado segue exatamente como na versao anterior (3235 palavras de 32 bits)
    rng.setstate(st0)
    for _ in range(WHEELHOUSE_RNG_WORDS):
        rng.getrandbits(32)


WHEELHOUSE_RNG_WORDS = 3235


def bridges(rng):
    """ponte principal (y -18) em arco de madeira e ponte dos fundos (y 38) sobre o rio"""
    rx0, rx1 = L.RIVER_X
    mb = MB("BLD_Bridges", "07_BUILDINGS", rng)
    for by, w in ((L.BRIDGE_MAIN_Y, 10.0), (L.BRIDGE_BACK_Y, 6.0)):
        xa, xb = rx0 - 3.5, rx1 + 3.5
        L_ = xb - xa
        n = int(L_ / 0.9)
        rise = 1.4
        # tabuleiro em arco (tabuas) sobre vigas curvas
        for i in range(n):
            x = xa + (i + 0.5) * L_ / n
            f = (x - xa) / L_
            z = F0 + rise * math.sin(math.pi * f)
            slope = rise * math.pi / L_ * math.cos(math.pi * f)
            mb.box((L_ / n - 0.08, w, 0.4), (x, by + rng.uniform(-0.1, 0.1), z - 0.2), (0, -math.atan(slope), 0),
                   "Wood_Plank", 0.05)
        for s in (-1, 1):
            pts = [Vector((xa + L_ * k / 12, by + s * (w / 2 - 0.4), F0 - 0.9 + rise * math.sin(math.pi * k / 12)))
                   for k in range(13)]
            mb.sweep(pts, [(-0.4, -0.5), (0.4, -0.5), (0.4, 0.5), (-0.4, 0.5)], "Wood_Dark", True)
            # corrimao
            posts = [Vector((xa + L_ * k / 5, by + s * (w / 2 + 0.2), F0 + rise * math.sin(math.pi * k / 5))) for k in range(6)]
            for p in posts:
                mb.box((0.8, 0.8, 3.6), (p.x, p.y, p.z + 1.6), (0, 0, 0), "Wood_Dark", 0.1)
            top = [p + Vector((0, 0, 3.2)) for p in posts]
            mb.sweep(top, [(-0.3, -0.25), (0.3, -0.25), (0.3, 0.25), (-0.3, 0.25)], "Wood_Light", True)
            mid = [p + Vector((0, 0, 1.7)) for p in posts]
            mb.sweep(mid, [(-0.2, -0.2), (0.2, -0.2), (0.2, 0.2), (-0.2, 0.2)], "Wood_Light", True)
        # cabeceiras de pedra
        for x in (xa - 0.5, xb + 0.5):
            mb.box((2.2, w + 1.6, 1.4), (x, by, F0 - 0.5), (0, 0, 0), "Stone_Light", 0.2)
        # colisao: 3 rampas suaves (arco) + corrimao
        A = "Bridge"
        k = 6
        for i in range(k):
            f0, f1 = i / k, (i + 1) / k
            za = F0 + rise * math.sin(math.pi * f0)
            zb = F0 + rise * math.sin(math.pi * f1)
            from fm_lib import col_ramp
            col_ramp(A, (xa + L_ * f0, by, za), (xa + L_ * f1, by, zb), w, 1.0)
        for s in (-1, 1):
            col_box(A, (L_, 0.8, 5.0), ((xa + xb) / 2, by + s * (w / 2 + 0.2), F0 + 2.5))
        lantern(mb, (xa - 1.0, by - w / 2 - 1.2, F0), D(90), name="L_Bridge_%d_W" % int(by), h=6.5)
        lantern(mb, (xb + 1.0, by + w / 2 + 1.2, F0), D(-90), name="L_Bridge_%d_E" % int(by), h=6.5)
    mb.finish()


def _terrace_fall(mb, x, fall_x, notch_z, x0, x1, top_z, rng, name, streams_up, streams_lo, notch_w=5.0):
    """cachoeira de canto (NO/NE): contraforte de rocha com entalhe em V -> fio principal + fio fino -> bacia de rocha
    apoiada no muro de arrimo/terraco -> queda sobre o muro ate o canal, com espuma no encontro"""
    yf = L.UPPER_FRONT_Y + 0.6
    bocal = WK.buttress(mb, None, yf, rng, x0, x1, 11.5, L.TERR - 0.6, top_z, fall_x, notch_w, notch_z)
    # bacia de rocha: aro de pedras sobre o topo do muro (apoiada no contraforte), espelho d'agua, labio escuro na frente
    bx, by, bz = fall_x, L.UPPER_FRONT_Y - 0.6, L.TERR + 1.25
    for a in (140, 180, 222, 318, 0, 40):
        r = math.radians(a)
        s = rng.uniform(1.6, 2.2)
        mb.rock((bx + math.cos(r) * 3.1, by + math.sin(r) * 2.3, bz - 0.9), (s * 1.3, s, 2.4), "Cliff_Rock", 1,
                (0, 0, r + rng.uniform(-0.3, 0.3)))
    mb.cyl(2.7, 0.5, (bx, by, bz - 0.2), (0, 0, 0.2), "Water", 8, bevel=0.0)
    mb.rock((bx, by - 2.3, bz - 1.2), (5.0, 1.6, 1.6), "Cliff_Rock_Dark", 1, (0, 0, 0.05))     # labio da bacia
    # fio(s) de cima: do bocal ate a bacia, rente a rocha molhada do entalhe
    WK.cascade(mb, bocal, bz, 3.2, rng, out=(0, -1), lip=0.35, streams=streams_up, widen=1.25, stripes=2,
               ring_z=bz + 0.05, ring_s=0.8)
    # queda de baixo: transborda o labio, desce na frente do muro e cai no canal
    top2 = (bx, by - 2.9, bz - 0.4)
    WK.cascade(mb, top2, WZ_CANAL, 4.2, rng, out=(0, -1), lip=1.3, streams=streams_lo, widen=1.35, stripes=2,
               ring_z=WZ_CANAL + 0.02)
    # parede molhada atras da queda de baixo (manchas escuras no muro)
    for k in range(3):
        mb.rock((bx + rng.uniform(-2.5, 2.5), L.UPPER_FRONT_Y - 1.25, rng.uniform(15.0, 27.0)),
                (rng.uniform(2.0, 3.2), 0.7, rng.uniform(2.5, 4.5)), "Cliff_Rock_Dark", 1, (0, 0, 0))
    col_box2("UpperWall", (x0 - 0.5, L.UPPER_FRONT_Y + 0.2, L.TERR - 0.5), (x1 + 0.5, yf + 11.5, top_z + 4.0))
    marker("VFX_Waterfall_" + name, (bx, by - 3.2, (WZ_CANAL + bocal.z) / 2), (0, 0, 0), 3,
           props={"topo": round(bocal.z, 1), "bacia": round(bz, 1)})


def _terrace_spout(mb, x, rng, name):
    """bica do terraco (entre portais): nascente entre as pedras da berma -> bloco de pedra com canaleta sobre o muro
    de arrimo (encaixa no entalhe do muro) -> fio de agua caindo no canal"""
    yb, ye = L.UPPER_FRONT_Y + 3.4, L.UPPER_FRONT_Y - 3.6
    z_top = L.TERR + 2.2
    mb.box2((x - 1.35, ye, L.TERR - 1.4), (x + 1.35, yb, z_top), "Stone_Light", 0.2)
    mb.beam((x, L.UPPER_FRONT_Y - 1.3, L.TERR - 6.0), (x, ye + 0.6, L.TERR - 1.3), 1.6, 1.2, "Stone_Dark", 0.15)
    for s in (-1, 1):
        mb.box2((x + s * 1.35 - (0.5 if s > 0 else 0.0), ye, z_top), (x + s * 1.35 + (0.0 if s > 0 else 0.5), yb, z_top + 0.7),
                "Stone_Light", 0.12)
    mb.box2((x - 0.85, ye + 0.05, z_top), (x + 0.85, yb, z_top + 0.35), "Water", 0.0)
    mb.box((3.0, 0.8, 0.5), (x, ye + 0.2, z_top - 0.1), (0, 0, 0), "Stone_Dark", 0.12)      # pingadeira
    # nascente: pedra escura molhada entre 2 pedras claras
    # (baixas: nao passam da berma de rocha, nao criam obstaculo novo na visada do spawn para os discos)
    mb.rock((x, yb + 1.0, L.TERR + 2.0), (2.4, 1.8, 2.4), "Cliff_Rock_Dark", 1, (0, 0, 0.2))
    for s in (-1, 1):
        mb.rock((x + s * 2.2, yb + 0.6, L.TERR + 1.6), (2.2, 2.0, 2.6), "Cliff_Rock", 1, (0, 0, rng.uniform(0, 3)))
    WK.cascade(mb, (x, ye - 0.05, z_top + 0.3), WZ_CANAL, 1.8, rng, out=(0, -1), lip=1.2, streams=((0.0, 1.0),),
               widen=1.5, stripes=1, ring_z=WZ_CANAL + 0.02, ring_s=0.7)
    marker("VFX_Waterfall_" + name, (x, ye - 1.6, (WZ_CANAL + z_top) / 2), (0, 0, 0), 3)


def sources(rng, mb):
    """nascentes: NO e NE saem de ENTALHES em contrafortes de rocha (bacia no meio da altura), cachoeira central
    desce da montanha, cruza o terraco e cai no canal; 2 bicas do terraco entre DB/SG e OP/OPM"""
    y0, y1 = L.CANAL_Y
    # NO: contraforte encostado no penhasco oeste, entalhe abaixo da crista (z~51)
    _terrace_fall(mb, None, L.WEST_X + 3.5, 47.0, L.WEST_X - 1.0, L.PORTAL_X[0] - 8.6, 53.0, rng, "NW",
                  streams_up=((-0.4, 1.0), (1.9, 0.36)), streams_lo=((0.0, 1.0), (-2.3, 0.3)), notch_w=4.6)
    # NE: a grande (mais alta), encostada no penhasco leste
    _terrace_fall(mb, None, L.EAST_X - 5, 55.0, L.PORTAL_X[5] + 16.5, L.EAST_X + 3.6, 60.0, rng, "NE",
                  streams_up=((0.5, 1.0), (-2.2, 0.4)), streams_lo=((0.3, 1.0), (2.4, 0.32)), notch_w=5.6)
    # central: canal de pedra no terraco (atras da torre) + queda na parede superior
    sx = 0.0
    mb.box2((sx - 3.6, L.UPPER_FRONT_Y - 0.2, L.TERR - 2.2), (sx + 3.6, L.TERR_BACK_Y + 2, L.TERR - 1.0), "Stone_Dark", 0.0)
    for s in (-1, 1):
        mb.box2((sx + s * 3.6 - 0.7, L.UPPER_FRONT_Y + 1.0, L.TERR - 2.2), (sx + s * 3.6 + 0.7, L.TERR_BACK_Y + 2, L.TERR + 0.8),
                "Stone_Light", 0.2)
    mb.box2((sx - 2.9, L.UPPER_FRONT_Y - 0.2, L.TERR - 1.0), (sx + 2.9, L.TERR_BACK_Y + 2, WZ_TERR), "Water", 0.0)
    for k in range(5):
        yy = rng.uniform(L.UPPER_FRONT_Y + 4, L.TERR_BACK_Y - 2)
        mb.box((0.25, rng.uniform(2.0, 4.0), 0.06), (sx + rng.uniform(-1.8, 1.8), yy, WZ_TERR + 0.03), (0, 0, 0), "Foam", 0.0)
    # nascente central: sai entre rochas da crista de tras (bocal de pedra escura)
    for s in (-1, 1):
        mb.rock((sx + s * 3.6, L.TERR_BACK_Y + 5.5, 49.0), (3.4, 3.0, 4.4), "Cliff_Rock", 1, (0, 0, rng.uniform(0, 3)))
    mb.rock((sx, L.TERR_BACK_Y + 6.5, 48.6), (4.2, 2.6, 3.4), "Cliff_Rock_Dark", 1, (0, 0, 0.1))
    WK.cascade(mb, (sx, L.TERR_BACK_Y + 4, 50.0), WZ_TERR, 5.2, rng, out=(0, -1), lip=1.5,
               streams=((0.0, 1.0), (2.6, 0.3)), widen=1.3, stripes=2, ring_z=WZ_TERR + 0.03, ring_s=0.9)
    mb.box2((sx - 3.6, L.UPPER_FRONT_Y - 1.4, 11.5), (sx + 3.6, L.UPPER_FRONT_Y + 0.2, WZ_TERR - 0.6), "Stone_Dark", 0.2)
    WK.cascade(mb, (sx, L.UPPER_FRONT_Y - 0.4, WZ_TERR - 0.2), WZ_CANAL, 5.4, rng, out=(0, -1), lip=1.6,
               streams=((0.0, 1.0),), widen=1.3, stripes=3, ring_z=WZ_CANAL + 0.02)
    # passarela de pedra sobre o canal central (continuidade do terraco)
    for yy in (L.FLIGHT2_Y1 + 6.0,):
        mb.box2((sx - 5.0, yy - 3.0, L.TERR - 0.8), (sx + 5.0, yy + 3.0, L.TERR + 0.3), "Stone_Light", 0.25)
        col_box2("Terrace", (sx - 5.0, yy - 3.0, L.TERR - 1.0), (sx + 5.0, yy + 3.0, L.TERR + 0.3))
    for s in (-1, 1):
        col_box2("Terrace", (sx + s * 3.6 - 0.7, L.UPPER_FRONT_Y, L.TERR - 2.2), (sx + s * 3.6 + 0.7, L.FLIGHT2_Y1 + 3.0, L.TERR + 0.8))
        col_box2("Terrace", (sx + s * 3.6 - 0.7, L.FLIGHT2_Y1 + 9.0, L.TERR - 2.2), (sx + s * 3.6 + 0.7, L.TERR_BACK_Y + 2, L.TERR + 0.8))
    # bicas do terraco: entre Dragon Ball e Shadow Garden, entre One Piece e One Punch Man
    P = L.PORTAL_X
    _terrace_spout(mb, (P[1] + P[2]) / 2, rng, "TerraceW")
    _terrace_spout(mb, (P[4] + P[5]) / 2, rng, "TerraceE")
    marker("VFX_Waterfall_Center", (0, L.UPPER_FRONT_Y, 20), (0, 0, 0), 3)
    marker("VFX_Waterfall_Spill", (L.SPILL_X - 1.6, L.MID_FRONT_Y - 1.5, 8), (0, 0, 0), 3)
