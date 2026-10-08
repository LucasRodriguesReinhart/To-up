# wb_court.py - CAMINHO DOS MUNDOS: o patio dos 6 portais APROVADOS + so o que faz sentido num portal medieval.
# - Portais: codigo compartilhado SO LEITURA (lobby_area/vila_medieval/vm_portals.py, que chama os fm_pv3_* e o
#   fm_portals.onepiece do lobby antigo): importado aqui e com a planta trocada em memoria (vm_portals.L = wb_layout);
#   cada portal nasce com o pad na cota Y_PORTAL olhando o centro do patio (Naruto ao sul ... One Punch Man ao norte).
# - Decoracao (prefixo WB_Court_, colecao 06_PORTALS): portico de entrada a leste do disco (2 pilares de pedra com
#   capitel e lanterna, viga com o letreiro "CAMINHO DOS MUNDOS" lido por quem chega, estandarte dourado sob a viga),
#   poste de setas em COURT_SIGN (6 setas na ordem de dificuldade apontando para o portal certo), postes de lanterna
#   no terraco entre os portais + 2 na entrada, 6 estandartes em mastro com a cor de cada mundo, 3 degraus de pedra
#   escura (tapete) do disco ao terraco na frente de cada portal, canteiros de arbustos/flores e rochedos no fundo.
#   NENHUM banco, nada no raio de 12 studs do centro de um portal.
# O chao do patio (disco r 40 na cota 7, terraco r 40..74 na cota 8,2 com 2 degraus em anel) e do wb_terrain.
import math
import os
import random
import sys

import bpy
import fm_lib
import wb_lib as W
import wb_layout as L
from wb_kit import Fr, bb, beam, cyl, lantern_post, lantern, banner, signpost, bush, text, STD, ST, TB, PK, TXT
from wb_lib import RB, V

PREFIX = "WB_Court_"
COLL = "06_PORTALS"
AREA = "Court"
SEED = 1306
CAMS = [("CAM_WB_Court_Entrada", (-80.0, 13.0, 58.0), (-140.0, 16.0, 62.0), 20),
        ("CAM_WB_Court_Aerea", (-134.0, 150.0, 170.0), (-134.0, 8.0, 62.0), 24),
        ("CAM_WB_Court_Portal", (-120.0, 12.0, 62.0), (-190.0, 16.0, 62.0), 24),
        ("CAM_WB_Court_Portico", (-58.0, 11.0, 56.0), (-96.0, 15.0, 62.0), 30),       # letreiro de quem chega
        ("CAM_WB_Court_Mastros", (-112.0, 11.0, 30.0), (-140.0, 15.0, 2.0), 24)]      # OPM + mastro da ponta norte

# ------------------------------------------------------------------ medidas (Roblox)
GATE = (-93.0, 62.0)          # portico: plano x = -93 (borda leste do disco), olha +X; quem chega olha -X
GATE_HALF = 8.5               # pilares em z = 62 +- 8,5 -> vao livre 14,8 (>= 12), altura livre 12 (>= 10)
PILLAR_H = 12.0
LAMP_R = 60.0                 # postes de lanterna no meio de dois portais vizinhos
LAMP_ENTRY = ((37.5, 24.0), (37.5, -34.0))      # (raio, angulo) dos 2 postes da entrada, no disco
BANNER_R = 71.0               # mastros dos estandartes, atras/ao lado de cada portal (fora do lote +-13,9 x 9,6)
BANNER_OFF = 12.0             # graus a partir do portal: tang 14,8 / radial 13,4 = 1 stud fora da largura do lote e
#                               4 atras dele (o poste fica a 15,5). Portais do sul: mastro ao sul; do norte: ao norte
#                               -> simetrico em torno do eixo oeste, os 2 mastros das pontas emolduram o semicirculo
KERB_R = (81.0, 47.5)         # meio-fio dos canteiros: atras do terraco / em volta da metade leste do disco
STEP_R = (36.5, 38.2, 40.3, 42.6)                 # 3 degraus de 0,4 (o anel do wb_terrain fica por baixo)
WORLD_CLOTH = {"Naruto": "WB_Cloth_Gold", "DragonBall": "WB_Cloth_Red", "ShadowGarden": "WB_Cloth_Purple",
               "DemonSlayer": "WB_Cloth_Green", "OnePiece": "WB_Cloth_Blue", "OnePunchMan": "WB_Cloth_Gold"}
WORLD_LABEL = {"Naruto": "NARUTO", "DragonBall": "DRAGON BALL", "ShadowGarden": "SHADOW GARDEN",
               "DemonSlayer": "DEMON SLAYER", "OnePiece": "ONE PIECE", "OnePunchMan": "ONE PUNCH MAN"}


def polar(r, deg):
    """(x, z) Roblox a r studs do centro do patio no angulo deg (atan2(dz, dx): 90 = sul, 180 = oeste)"""
    a = math.radians(deg)
    return L.COURT_C[0] + r * math.cos(a), L.COURT_C[1] + r * math.sin(a)


def court_frame(y, deg):
    """frame na cota y com origem no centro do patio e +y local apontando para fora no angulo deg"""
    a = math.radians(deg)
    return Fr.rbx(L.COURT_C[0], L.COURT_C[1], y, math.cos(a), math.sin(a))


def facing_center(x, z, y):
    return Fr.rbx(x, z, y, L.COURT_C[0] - x, L.COURT_C[1] - z)


def on_plateau(x, z, margin=4.0):
    """ponto (e o ponto 'margin' mais para fora do patio) dentro do plato de grama"""
    a = math.atan2(z - L.COURT_C[1], x - L.COURT_C[0])
    return (fm_lib.point_in_poly(x, z, L.PLATEAU)
            and fm_lib.point_in_poly(x + margin * math.cos(a), z + margin * math.sin(a), L.PLATEAU))


# ------------------------------------------------------------------ portico de entrada
def gate(b):
    gx, gz = GATE
    F = Fr.rbx(gx, gz, L.Y_PAVE, 1.0, 0.0)          # f = +X; +x local = sul
    H = PILLAR_H
    for s in (-1, 1):
        x = s * GATE_HALF
        bb(b, F, x - 1.5, x + 1.5, -1.5, 1.5, -0.8, 1.0, STD, bevel=0.12)       # plinto (desce ate a grama 6,8)
        bb(b, F, x - 1.1, x + 1.1, -1.1, 1.1, 0.9, H - 1.0, ST)                 # fuste 2,2 x 2,2
        bb(b, F, x - 1.3, x + 1.3, -1.3, 1.3, H * 0.5 - 0.3, H * 0.5 + 0.3, STD)  # cinta
        bb(b, F, x - 1.5, x + 1.5, -1.5, 1.5, H - 1.0, H, STD, bevel=0.15)      # capitel
        beam(b, F, (x - s * 1.1, 0.0, H - 3.4), (x - s * 4.2, 0.0, H + 0.2), 0.55, 0.55, TB)   # mao-francesa
        # lanterna em pe sobre a capa da viga, no eixo do pilar (base da lanterna = topo da capa)
        lantern(b, F, x, 0.0, H + 3.0 + 1.3 * 1.62, "L_WB_Lamp_Court_Gate_%d" % (0 if s < 0 else 1), s=1.3)
        fm_lib.col_box(AREA, (3.0, 3.0, H + 0.8), F.p(x, 0.0, (H + 0.8) / 2 - 0.8), (0, 0, F.yaw()))
    # viga de madeira sobre os capiteis + capa de tabuas
    bb(b, F, -GATE_HALF - 1.9, GATE_HALF + 1.9, -0.9, 0.9, H, H + 2.4, TB, bevel=0.1)
    bb(b, F, -GATE_HALF - 2.1, GATE_HALF + 2.1, -1.2, 1.2, H + 2.4, H + 3.0, PK, bevel=0.06)
    # letreiro na face LESTE da viga (+y local): tabua com molduras e letras lidas por quem chega (olhando -X)
    bb(b, F, -8.4, 8.4, 0.9, 1.25, H + 0.35, H + 2.05, PK, bevel=0.05)
    for z0, z1 in ((H + 0.2, H + 0.42), (H + 1.98, H + 2.2)):
        bb(b, F, -8.6, 8.6, 0.9, 1.32, z0, z1, TB)
    for x in (-8.6, 8.6):
        bb(b, F, x - 0.12, x + 0.12, 0.9, 1.32, H + 0.2, H + 2.2, TB)
    text(b, F, "CAMINHO DOS MUNDOS", 1.05, TXT, 0.0, 1.28, H + 1.2, 0.14, bold=True)
    # estandarte dourado pendurado sob a viga, no plano do portico (emblema vermelho para ler sobre o ouro);
    # curto (3,8) para nao tapar os portais de quem chega: fica acima de 15,1 no meio do vao
    banner(b, F, 0.0, 0.0, H - 0.1, "WB_Cloth_Gold", 2.6, 3.8, pole=False, emblem=False)
    emblem(b, F, 0.0, 0.0, H - 0.1 - 3.8 * 0.45, 2.6 * 0.26, "WB_Cloth_Red")
    fm_lib.col_box(AREA, (2 * GATE_HALF + 3.8, 1.8, 3.0), F.p(0.0, 0.0, H + 1.5), (0, 0, F.yaw()))


# ------------------------------------------------------------------ poste de setas
def sign(b):
    sx, sz = L.COURT_SIGN
    F = Fr.rbx(sx, sz, L.Y_PAVE, -1.0, 0.0)
    arms = []
    for i, (key, aid) in enumerate(L.PORTALS):
        (px, pz), _ = L.portal_pos(i)
        d = V((px - sx, -(pz - sz), 0.0))                       # direcao Blender do poste ao portal
        ang = math.degrees(math.atan2(F.f.x * d.y - F.f.y * d.x, F.f.x * d.x + F.f.y * d.y))
        arms.append((WORLD_LABEL[key], ang))
        fa = F.sub(0, 0, 0, ang).f                                # conferencia: a seta aponta mesmo para o portal
        err = math.degrees(math.acos(max(-1.0, min(1.0, fa.dot(d.normalized())))))
        print("  seta %-14s %7.1f graus -> portal (%.1f, %.1f), erro %.2f graus" % (WORLD_LABEL[key], ang, px, pz, err))
    signpost(b, F, arms, h=12.0)
    fm_lib.col_box(AREA, (1.6, 1.6, 12.0), RB(sx, sz, L.Y_PAVE + 6.0))


# ------------------------------------------------------------------ degraus (tapete de pedra escura) de cada portal
def steps(b, i):
    F = court_frame(L.Y_PAVE, L.portal_bearing(i))
    for k in range(3):
        r0, r1 = STEP_R[k], STEP_R[k + 1]
        top = 0.4 * (k + 1) + 0.05                               # 7,45 / 7,85 / 8,25: nada coplanar com o anel
        bb(b, F, -5.0, 5.0, r0, r1, -0.4, top, STD, bevel=0.08)
        fm_lib.col_box(AREA, (10.0, r1 - r0, top + 0.4), F.p(0.0, (r0 + r1) / 2, (top - 0.4) / 2), (0, 0, F.yaw()))


# ------------------------------------------------------------------ postes de lanterna
def lamp_points():
    pts = []
    for i in range(len(L.PORTALS) - 1):
        pts.append((LAMP_R, (L.portal_bearing(i) + L.portal_bearing(i + 1)) / 2, L.Y_PORTAL))
    for rr, a in LAMP_ENTRY:
        pts.append((rr, a, L.Y_PAVE))
    return pts


def lamps(b):
    for k, (rr, a, y) in enumerate(lamp_points()):
        x, z = polar(rr, a)
        lantern_post(b, facing_center(x, z, y), 0.0, 0.0, "L_WB_Lamp_Court_%d" % k, h=9.0)
        fm_lib.col_box(AREA, (1.4, 1.4, 9.0), RB(x, z, y + 4.5))


# ------------------------------------------------------------------ estandartes em mastro
def banner_points():
    return [(BANNER_R, L.portal_bearing(i) + banner_off(i)) for i in range(len(L.PORTALS))]


def emblem(b, F, x, y, z, r, m):
    """disco chato no PLANO do pano (o emblema do kit e uma esfera achatada em eixos de mundo: fica de lado em
    frames girados), dos dois lados do tecido"""
    cyl(b, F, (x, y - 0.24, z), (x, y + 0.24, z), r, m, seg=12)


def banner_off(i):
    return -BANNER_OFF if i < len(L.PORTALS) / 2 else BANNER_OFF


def mast(b, F, cloth, side):
    """mastro de madeira com base de pedra e ponteira de latao; o pano cai de um lado so (side = +-1 em x local)"""
    H, w, h = 12.0, 2.8, 7.0
    bb(b, F, -0.9, 0.9, -0.9, 0.9, -0.3, 0.6, STD, bevel=0.1)
    cyl(b, F, (0.0, 0.0, 0.5), (0.0, 0.0, H), 0.28, TB, seg=8, r1=0.2)
    b.sphere(F.p(0.0, 0.0, H + 0.3), 0.42, "WB_Brass", seg=8)
    xb = side * (w / 2 + 0.45)
    banner(b, F, xb, 0.0, H - 0.7, cloth, w, h, pole=False, emblem=False)
    emblem(b, F, xb, 0.0, H - 0.7 - h * 0.45, w * 0.26, "WB_Cloth_Red" if cloth == "WB_Cloth_Gold" else "WB_Cloth_Gold")


def banners(b):
    for i, (key, aid) in enumerate(L.PORTALS):
        rr, a = banner_points()[i]
        x, z = polar(rr, a)
        side = -1 if banner_off(i) < 0 else 1          # o pano cai para o lado do portal dele
        mast(b, facing_center(x, z, L.Y_PORTAL), WORLD_CLOTH[key], side)
        fm_lib.col_box(AREA, (1.2, 1.2, 12.0), RB(x, z, L.Y_PORTAL + 6.0))


# ------------------------------------------------------------------ canteiros e rochedos
def kerb(b, rr, a0, a1, step=7.5):
    """meio-fio de pedra escura em arco (segmentos retos) na grama, so onde o plato existe"""
    n = max(1, int(round((a1 - a0) / step)))
    for k in range(n):
        aa, ab = a0 + (a1 - a0) * k / n, a0 + (a1 - a0) * (k + 1) / n
        (xa, za), (xb, zb) = polar(rr, aa), polar(rr, ab)
        if not (on_plateau(xa, za, 1.5) and on_plateau(xb, zb, 1.5)):
            continue
        b.beam(RB(xa, za, L.Y_GRASS + 0.1), RB(xb, zb, L.Y_GRASS + 0.1), 0.7, 0.5, STD)


def garden(b, r):
    skipped = 0
    # meio-fio dos canteiros: atras do terraco e em volta da metade leste do disco (entrada livre)
    kerb(b, KERB_R[0], 86.0, 274.0)
    kerb(b, KERB_R[1], -84.0, -26.0)
    kerb(b, KERB_R[1], 18.0, 86.0)
    # arbustos na borda externa do terraco (r 76..80, grama)
    a, k = 88.0, 0
    while a <= 272.0:
        x, z = polar(r.uniform(76.0, 80.0), a)
        if on_plateau(x, z):
            bush(b, Fr(RB(x, z, L.Y_GRASS), (0, 1)), 0.0, 0.0, r.uniform(2.0, 3.0), seed=k,
                 flowers=r.choice([None, "WB_FlowerRed", "WB_FlowerPink", "WB_FlowerYellow", None]))
            fm_lib.col_box(AREA, (3.0, 3.0, 2.4), RB(x, z, L.Y_GRASS + 1.2))
        else:
            skipped += 1
        a += r.uniform(7.0, 10.0)
        k += 1
    # rochedos fechando o fundo (r 84..88, atras do meio-fio), semi-enterrados
    for k in range(12):
        a = 92.0 + k * 15.0 + r.uniform(-4.0, 4.0)
        x, z = polar(r.uniform(84.0, 88.0), a)
        if not on_plateau(x, z, 3.0):
            skipped += 1
            continue
        rad = r.uniform(2.6, 4.6)
        sy, sz = r.uniform(0.7, 1.0), r.uniform(0.5, 0.7)
        b.sphere(RB(x, z, L.Y_GRASS - rad * sz * 0.4), rad, "WB_Stone", seg=8, scale=(1.0, sy, sz))
        fm_lib.col_box(AREA, (rad * 1.6, rad * sy * 1.6, rad * sz * 1.1), RB(x, z, L.Y_GRASS + rad * sz * 0.2))
    # canteiros do lado leste do disco (fora do meio-fio, r 43,5..46), deixando a entrada livre (-28..20 graus)
    for a in list(range(-80, -28, 9)) + list(range(22, 82, 9)):
        x, z = polar(r.uniform(43.5, 46.0), a + r.uniform(-2.0, 2.0))
        if not on_plateau(x, z, 2.0):
            skipped += 1
            continue
        bush(b, Fr(RB(x, z, L.Y_GRASS), (0, 1)), 0.0, 0.0, r.uniform(1.8, 2.6), seed=100 + a,
             flowers=r.choice([None, "WB_FlowerRed", "WB_FlowerYellow", "WB_FlowerWhite"]))
        fm_lib.col_box(AREA, (2.8, 2.8, 2.2), RB(x, z, L.Y_GRASS + 1.1))
    if skipped:
        print("WB_Court: %d canteiros/rochedos fora do plato (PLATEAU curto a sudoeste do patio) - pulados" % skipped)


# ------------------------------------------------------------------ portais aprovados (vm_portals, so leitura)
def portals():
    vila = os.path.join(W.ROOT, "lobby_area", "vila_medieval")
    if vila not in sys.path:
        sys.path.insert(0, vila)
    import fm_pv3
    import vm_portals
    import wb_layout
    fm_pv3.load()                       # os modulos dos portais registram materiais/texturas das espirais
    fm_lib.make_materials()             # ... e o make tem de rodar depois do load (regra do fm_pv3)
    vm_portals.L = wb_layout            # planta NOSSA (mesmos nomes: PORTALS, portal_pos, Y_PORTAL)
    before = set(bpy.data.objects)
    report = vm_portals.build()
    new = [o for o in bpy.data.objects if o not in before]        # malhas em 06_PORTALS, COL_, marcadores, luzes
    return new, report


def footprint(new):
    """extensao de cada portal no referencial dele (radial: + = atras, - = para o centro; tang; altura) e a folga
    dos postes/mastros desta decoracao em relacao ao lote de cada portal"""
    out = {}
    for i, (key, aid) in enumerate(L.PORTALS):
        (nx, nz), (fx, fz) = L.portal_pos(i)
        p = RB(nx, nz, L.Y_PORTAL)
        o_dir = V((-fx, fz, 0.0))                 # Blender: do centro para o portal
        t_dir = V((o_dir.y, -o_dir.x, 0.0))
        lo, hi = [1e9, 1e9, 1e9], [-1e9, -1e9, -1e9]
        glo, ghi = [1e9, 1e9], [-1e9, -1e9]
        for o in new:
            if o.type != "MESH" or o.get("vm_portal") != key or o.name.startswith("COL_"):
                continue
            mw = o.matrix_world
            for v in o.data.vertices:
                d = mw @ v.co - p
                c = (d.dot(o_dir), d.dot(t_dir), d.z)
                for j in range(3):
                    lo[j] = min(lo[j], c[j])
                    hi[j] = max(hi[j], c[j])
                if c[2] < 4.0:
                    glo[0], glo[1] = min(glo[0], c[0]), min(glo[1], c[1])
                    ghi[0], ghi[1] = max(ghi[0], c[0]), max(ghi[1], c[1])
        out[key] = (lo, hi, glo, ghi)
        print("PORTAL %-12s radial %6.1f..%5.1f  tang %6.1f..%5.1f  alt %5.1f..%5.1f | chao(alt<4) radial %6.1f..%5.1f tang %6.1f..%5.1f"
              % (key, lo[0], hi[0], lo[1], hi[1], lo[2], hi[2], glo[0], ghi[0], glo[1], ghi[1]))
    # folgas da decoracao
    items = [("poste %d" % k, rr, a) for k, (rr, a, y) in enumerate(lamp_points())]
    items += [("mastro %s" % L.PORTALS[i][0], rr, a) for i, (rr, a) in enumerate(banner_points())]
    for name, rr, a in items:
        x, z = polar(rr, a)
        best = None
        for i, (key, aid) in enumerate(L.PORTALS):
            (nx, nz), (fx, fz) = L.portal_pos(i)
            d = V((x - nx, -(z - nz), 0.0))
            o_dir = V((-fx, fz, 0.0))
            t_dir = V((o_dir.y, -o_dir.x, 0.0))
            rad, tan = d.dot(o_dir), d.dot(t_dir)
            dist = math.hypot(x - nx, z - nz)
            lo, hi, glo, ghi = out[key]
            inside_rad = glo[0] - 1.0 <= rad <= ghi[0] + 1.0
            gap_t = min(abs(tan - glo[1]), abs(tan - ghi[1])) if not (glo[1] <= tan <= ghi[1]) else -1.0
            if best is None or dist < best[0]:
                best = (dist, key, rad, tan, inside_rad, gap_t)
        dist, key, rad, tan, inside_rad, gap_t = best
        flag = "" if dist >= 12.0 and (not inside_rad or gap_t >= 1.0) else "  <<< CONFERIR"
        print("  %-20s r %.1f a %6.1f -> portal %-12s dist %5.1f  radial %6.1f tang %6.1f  folga_t %5.1f%s"
              % (name, rr, a, key, dist, rad, tan, gap_t, flag))
    return out


# ------------------------------------------------------------------ entrada
def build():
    objs, report = portals()
    footprint(objs)
    tris_p = sum(t for (_k, _a, _n, t, _f, _c) in report)
    n_mesh = sum(1 for o in objs if o.type == "MESH" and not o.name.startswith("COL_"))
    n_col = sum(1 for o in objs if o.name.startswith("COL_"))
    n_mark = sum(1 for o in objs if o.type == "EMPTY")
    n_light = sum(1 for o in objs if o.type == "LIGHT")
    print("PORTAIS: %d tris em %d malhas (+ %d COL, %d marcadores, %d luzes)" % (tris_p, n_mesh, n_col, n_mark, n_light))
    r = random.Random(SEED)
    b = W.Build(PREFIX + "Decor", COLL, seed=SEED)
    gate(b)
    sign(b)
    for i in range(len(L.PORTALS)):
        steps(b, i)
    lamps(b)
    banners(b)
    decor = b.finish()
    b = W.Build(PREFIX + "Garden", COLL, seed=SEED + 1)
    garden(b, r)
    decor += b.finish()
    tris_d = sum(len(p.vertices) - 2 for o in decor for p in o.data.polygons)
    n_col = sum(1 for o in bpy.data.objects if o.name.startswith("COL_" + AREA + "_"))
    print("DECORACAO WB_Court_: %d objetos, %d tris, %d COL_%s (%s)" % (len(decor), tris_d, n_col, AREA, ", ".join(
        "%s=%d" % (o.name.split("__")[-1], sum(len(p.vertices) - 2 for p in o.data.polygons)) for o in decor)))
    return decor + objs
