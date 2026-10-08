# vm_blockout - BLOCKOUT do hub inteiro (V0) na escala do avatar (5,2 studs): plato com canal, praca com medalhao
# rebaixado, terraco do spawn, ruas de paralelepipedo, casas enxaimel (vm_lib.house), ponte de pedra, FORJA (marco:
# chamine alta, salao aberto com a envoltoria do Ignis livre, roda d'agua), loja, ranking, patio dos portais com os 6
# portais APROVADOS (vm_portals), rua curva do sudeste + portao + ponte da Ilha 1, colinas, vegetacao e montanhas.
# Volumes simples, materiais lisos (a cor e a do Roblox). Cada zona e uma funcao; o V1+ troca zona por modulo de detalhe.
import math, random
import bpy
from mathutils import Vector
import vm_lib as VL
from vm_lib import B, slab, colr, colr_rot, ribbon_r, circle_r, sector_r
import vm_layout as L
import fm_lib
from fm_lib import MB, col_box
import fm_parts as FP


def _rng(k):
    return random.Random(k)


# ================================================================== TERRENO
def terrain():
    import vm_col
    S, N = vm_col.south_poly(), vm_col.north_poly()
    canal = VL.clip_box(L.PLATEAU, z0=L.CANAL_Z[0] - 1.0, z1=L.CANAL_Z[1] + 1.0)
    mb = MB("VM_Ter_Ground", "02_TERRAIN", _rng(1), detail="far", floor=-999)
    slab(mb, S, 0.2, L.Y_GRASS - 0.8, "Cliff_VM_Rock")
    slab(mb, S, L.Y_GRASS - 0.8, L.Y_GRASS, "Grass_VM")
    # norte: recorta a levada (x 32..40, z -85..-19) - so o leito fica ali
    rx0, rx1 = L.RACE_X[0] - 1.0, L.RACE_X[1] + 1.0
    for part in (VL.clip_box(N, x1=rx0), VL.clip_box(N, x0=rx1), VL.clip_box(N, x0=rx0, x1=rx1, z1=L.RACE_Z[1] - 1.0)):
        if len(part) >= 3:
            slab(mb, part, 0.2, L.Y_NORTH_GRASS - 0.8, "Cliff_VM_Rock")
            slab(mb, part, L.Y_NORTH_GRASS - 0.8, L.Y_NORTH_GRASS, "Grass_VM")
    race_bed = VL.clip_box(N, x0=rx0, x1=rx1, z0=L.RACE_Z[1] - 1.0)
    if len(race_bed) >= 3:
        slab(mb, race_bed, 0.2, L.Y_CANAL_BED, "Stone_VM_Dark")
    slab(mb, canal, 0.2, L.Y_CANAL_BED, "Stone_VM_Dark")                   # leito do canal
    mb.finish()
    # corpo do plato (rocha) afinando para baixo
    cb = MB("VM_Ter_Cliffs", "02_TERRAIN", _rng(2), detail="far", floor=-999)
    slab(cb, L.PLATEAU, -12.0, 0.2, "Cliff_VM_Rock")
    cx = sum(p[0] for p in L.PLATEAU) / len(L.PLATEAU)
    cz = sum(p[1] for p in L.PLATEAU) / len(L.PLATEAU)
    inner = [(cx + (x - cx) * 0.86, cz + (z - cz) * 0.86) for x, z in L.PLATEAU]
    slab(cb, inner, L.PLATEAU_BOTTOM, -12.0, "Cliff_VM_Rock")
    # blocos de rocha na borda (quebram a aresta reta do plato)
    rng = _rng(3)
    P = L.PLATEAU
    for i in range(len(P)):
        a, b = P[i], P[(i + 1) % len(P)]
        ln = math.hypot(b[0] - a[0], b[1] - a[1])
        k = max(1, int(ln / 22))
        for j in range(k):
            t = (j + 0.5) / k
            x, z = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
            s = rng.uniform(7, 12)
            cb.rock(tuple(B(x, z, rng.uniform(-6, -2))), (s * 1.4, s, s * 0.9), "Cliff_VM_Rock", 1, (0, 0, rng.uniform(0, 3)))
    cb.finish()
    # muros do canal (pedra; topo no piso de cada lado) e da levada
    w = MB("VM_Ter_CanalWalls", "02_TERRAIN", _rng(4), detail="far", floor=-999)
    z0, z1 = L.CANAL_Z
    x0, x1 = L.CANAL_X
    hw = L.STREET_HW + 2.0
    for a, b in ((x0, -hw), (hw, x1)):
        w.box2(B(a, z1 + 1.0, L.Y_CANAL_BED), B(b, z1, L.Y_PAVE - 0.02), "Stone_VM_Base", 0.0)
        w.box2(B(a, z1 + 1.05, L.Y_PAVE - 0.02), B(b, z1 - 0.05, L.Y_PAVE + 1.1), "Stone_VM_Trim", 0.0)   # mureta sul
    for a, b in ((x0, -hw), (hw, L.RACE_X[0] - 1.0), (L.RACE_X[1] + 1.0, x1)):
        w.box2(B(a, z0, L.Y_CANAL_BED), B(b, z0 - 1.0, L.Y_NORTH - 0.02), "Stone_VM_Base", 0.0)
        w.box2(B(a, z0 + 0.05, L.Y_NORTH - 0.02), B(b, z0 - 1.05, L.Y_NORTH + 1.1), "Stone_VM_Trim", 0.0)  # mureta norte
    rz0, rz1 = L.RACE_Z
    for xa, xb in ((L.RACE_X[0] - 1.0, L.RACE_X[0]), (L.RACE_X[1], L.RACE_X[1] + 1.0)):
        w.box2(B(xa, rz0, L.Y_CANAL_BED), B(xb, rz1 - 1.0, L.Y_NORTH + 1.1), "Stone_VM_Base", 0.0)
    w.box2(B(L.RACE_X[0], rz1, L.Y_CANAL_BED), B(L.RACE_X[1], rz1 - 1.0, L.Y_NORTH + 1.1), "Stone_VM_Base", 0.0)
    w.finish()
    hills()
    mountains()


def hills():
    """colinas verdes em volta do plato (fora do alcance; leem como a ref_01 no fundo)"""
    rng = _rng(11)
    mb = MB("VM_Ter_Hills", "02_TERRAIN", rng, detail="far", floor=-999)
    spots = [(-70, -190, 95, 34), (50, -200, 110, 40), (160, -160, 90, 30), (-180, -150, 80, 26), (235, -30, 80, 26),
             (250, 90, 90, 22), (-300, 20, 90, 30), (-290, 170, 80, 22), (-200, -60, 70, 24), (200, 170, 70, 18),
             (120, -260, 120, 60), (-130, -270, 120, 55)]
    for x, z, r, h in spots:
        top = L.Y_GRASS + h
        mb.ico(r, tuple(B(x, z, top - r * 0.55)), "Grass_VM_Hill", 2, (1.25, 1.0, 0.55), jitter=0.06)
        for k in range(3):                       # pinheiros na encosta (silhueta)
            a = rng.uniform(0, math.tau)
            f = rng.uniform(0.15, 0.5)
            y = top - 0.55 * r * f * f - 1.5
            VL.tree_pine(mb, x + math.cos(a) * f * r * 1.25, z + math.sin(a) * f * r, y, rng.uniform(16, 26), rng)
    mb.finish()


def mountains():
    """montanhas de fundo (SKYLINE, perspectiva aerea fria); sem nada no setor sul (+Z) onde seguem as ilhas"""
    rng = _rng(12)
    mb = MB("VM_Bg_Mountains", "02_TERRAIN", rng, detail="far", floor=-999)
    for k in range(17):
        a = 150.0 + k * (240.0 / 16) + rng.uniform(-5, 5)      # 150 -> 390 graus: oeste, norte, leste (sem o sul +Z)
        r = rng.uniform(560, 860)
        x, z = math.cos(math.radians(a)) * r, math.sin(math.radians(a)) * r
        h = rng.uniform(170, 300)
        base = rng.uniform(150, 230)
        mb.cyl(base, h, tuple(B(x, z, -60.0 + h / 2)), (0, 0, rng.uniform(0, 1)), "Cliff_VM_Far", 7, r2=base * 0.12,
               bevel=0.0)
        mb.cyl(base * 0.30, h * 0.26, tuple(B(x, z, -60.0 + h * 0.87)), (0, 0, rng.uniform(0, 1)), "Cliff_VM_FarSnow", 7,
               r2=base * 0.06, bevel=0.0)
    mb.finish()


# ================================================================== CIDADE: praca, terraco do spawn, ruas, props
PLAZA_TOP = L.Y_PAVE + 0.06          # praca 0,12 acima das ruas (nada coplanar onde se sobrepoem)
ROAD_TOP = L.Y_PAVE - 0.06


def town():
    rng = _rng(21)
    cx, cz = L.PLAZA_C
    mb = MB("VM_Town_Plaza", "03_TOWN", rng, detail="far", floor=-999)
    for a0, a1 in ((0, 180), (180, 360)):
        slab(mb, sector_r(cx, cz, L.MEDAL_R, L.PLAZA_R, a0, a1, 36), PLAZA_TOP - 0.4, PLAZA_TOP, "Stone_Paving_VM")
    # anel de meio-fio da praca (le o desenho do piso a distancia)
    for a0, a1 in ((0, 180), (180, 360)):
        slab(mb, sector_r(cx, cz, L.PLAZA_R - 1.2, L.PLAZA_R, a0, a1, 36), PLAZA_TOP, PLAZA_TOP + 0.12,
             "Stone_Paving_VM_Edge")
        slab(mb, sector_r(cx, cz, 20.0, 21.0, a0, a1, 30), PLAZA_TOP, PLAZA_TOP + 0.04, "Stone_Paving_VM_Edge")
    mb.finish()
    medallion()
    m2 = MB("VM_Town_Spawn", "03_TOWN", rng, detail="far", floor=-999)
    inner = [(x * 0.985, 100 + (z - 100) * 0.985) for x, z in L.SPAWN_TERRACE]
    slab(m2, L.SPAWN_TERRACE, L.Y_GRASS - 0.4, L.Y_SPAWN - 0.3, "Stone_VM_Base")
    slab(m2, inner, L.Y_SPAWN - 0.3, L.Y_SPAWN, "Stone_Paving_VM")
    # anel do ponto de nascimento (o SpawnLocation 10x10 fica por cima)
    sx, sz = L.SPAWN
    for a0, a1 in ((0, 180), (180, 360)):
        slab(m2, sector_r(sx, sz, 6.0, 7.0, a0, a1, 24), L.Y_SPAWN, L.Y_SPAWN + 0.12, "Metal_VM_Bronze")
    m2.finish()
    roads()
    props()


def medallion():
    """medalhao do piso: anel escuro + disco + PICARETA cruzando a BIGORNA em bronze, tudo abaixo do piso da praca
    (rebaixado 0,12; a colisao e o piso plano em 6,0)"""
    cx, cz = L.PLAZA_C
    mb = MB("VM_Town_Medallion", "03_TOWN", _rng(22), detail="far", floor=-999)
    top = PLAZA_TOP - 0.12
    for a0, a1 in ((0, 180), (180, 360)):
        slab(mb, sector_r(cx, cz, L.MEDAL_R - 1.4, L.MEDAL_R, a0, a1, 32), top - 0.4, top, "Stone_Paving_VM_Edge")
    slab(mb, circle_r(cx, cz, L.MEDAL_R - 1.4, 32), top - 0.45, top - 0.05, "Stone_Paving_VM")
    F = VL.face_frame(cx, cz, top - 0.05, 0, -1)          # +x local = norte (forja)
    # bigorna (vista de cima): corpo + chifre + base
    for (a, b, w, d) in ((-1.0, 0, 3.6, 5.2), (2.4, 0, 3.2, 2.0), (-3.4, 0, 1.6, 3.8)):
        mb.box((w, d, 0.1), F.p(a, b, 0.05), F.r(), "Metal_VM_Bronze", 0.0)
    # picareta cruzando (cabo diagonal + cabeca curva em 3 gomos)
    mb.box((11.0, 0.9, 0.1), F.p(0.2, 0.0, 0.07), F.r(rz=math.radians(40)), "Metal_VM_Bronze", 0.0)
    for k, (u, v, ang) in enumerate(((3.6, 4.0, 128), (4.6, 2.6, 150), (2.2, 5.0, 104))):
        mb.box((3.0, 0.9, 0.1), F.p(u, v, 0.07), F.r(rz=math.radians(ang)), "Metal_VM_Bronze", 0.0)
    mb.finish()


def _road(mb, name_pts, w, top, curb=True, rng=None):
    poly = ribbon_r(name_pts, w)
    slab(mb, poly, top - 0.4, top, "Stone_Paving_VM")
    if curb:
        for s in (-1, 1):
            edge = []
            for i, p in enumerate(name_pts):
                a = name_pts[max(0, i - 1)]
                b = name_pts[min(len(name_pts) - 1, i + 1)]
                dx, dz = b[0] - a[0], b[1] - a[1]
                ln = math.hypot(dx, dz) or 1.0
                edge.append((p[0] - dz / ln * s * (w / 2 - 0.4), p[1] + dx / ln * s * (w / 2 - 0.4)))
            slab(mb, ribbon_r(edge, 0.8), top, top + 0.14, "Stone_Paving_VM_Edge")


def roads():
    rng = _rng(23)
    mb = MB("VM_Town_Streets", "03_TOWN", rng, detail="far", floor=-999)
    hw = L.STREET_HW
    zs0, zs1 = L.STREET_S
    _road(mb, [(0, zs0 + 1.0), (0, zs1)], 2 * hw, ROAD_TOP)
    _road(mb, [(0, L.STREET_N[0]), (0, L.STREET_N[1])], 2 * hw, L.Y_NORTH)
    slab(mb, L.FORGE_SQ, L.Y_NORTH - 0.4, L.Y_NORTH - 0.001, "Stone_Paving_VM")
    _road(mb, L.WEST_ROAD, L.ROAD_W, ROAD_TOP)
    slab(mb, L.SHOP_STREET, ROAD_TOP - 0.4, ROAD_TOP, "Stone_Paving_VM")
    _road(mb, L.EXIT_ROAD, L.ROAD_W, ROAD_TOP)
    # trilha de terra no gramado sul (spawn -> rua curva), le como atalho
    slab(mb, ribbon_r([(14, 112), (26, 116), (40, 112)], 4.0), L.Y_GRASS - 0.2, L.Y_GRASS + 0.06, "Dirt_VM")
    mb.finish()
    bridge_canal()


def bridge_canal():
    """ponte de pedra em arco sobre o canal: tabuleiro em duas rampas (6,0 -> 7,4 -> 7,0), arco e guarda-corpos"""
    mb = MB("VM_Town_Bridge", "03_TOWN", _rng(24), detail="far", floor=-999)
    hw = L.STREET_HW
    zs, zn = L.BRIDGE_Z
    zc = (zs + zn) / 2
    for (za, ya), (zb, yb) in (((zs, L.Y_PAVE), (zc, L.BRIDGE_CROWN)), ((zc, L.BRIDGE_CROWN), (zn, L.Y_NORTH))):
        pa, pb = B(0, za, ya), B(0, zb, yb)
        d = pb - pa
        ln = d.length
        pitch = math.atan2(d.z, abs(d.y))
        c = (pa + pb) / 2 - Vector((0, 0, 0.6))
        sgn = 1 if d.y > 0 else -1
        mb.box((2 * hw, ln + 0.3, 1.2), c, (sgn * pitch, 0, 0), "Stone_Paving_VM", 0.0)
    # arco (aduelas) e pilares nas margens
    for s in (-1, 1):
        x = s * (hw + 0.6)
        for k in range(9):
            t = k / 8.0
            z = L.CANAL_Z[1] + 1.0 + (L.CANAL_Z[0] - 1.0 - L.CANAL_Z[1] - 1.0) * t
            yy = L.Y_CANAL_BED + 2.4 + math.sin(math.pi * t) * 3.2
            mb.box((1.4, 1.9, 1.5), B(x, z, yy), (0, 0, 0), "Stone_VM_Trim", 0.0)
        mb.box2(B(x - 0.7, zs, L.Y_PAVE), B(x + 0.7, zn, L.BRIDGE_CROWN + 1.3), "Stone_VM_Base", 0.0)     # guarda-corpo
        for z in (zs, zn):
            mb.box((1.8, 1.8, 2.6), B(x, z, L.BRIDGE_CROWN + 1.3), (0, 0, 0), "Stone_VM_Dark", 0.0)
    mb.box2(B(-hw, L.CANAL_Z[1] + 1.0, L.Y_CANAL_BED), B(hw, L.CANAL_Z[1] - 1.0, L.Y_PAVE - 0.7), "Stone_VM_Base", 0.0)
    mb.box2(B(-hw, L.CANAL_Z[0] + 1.0, L.Y_CANAL_BED), B(hw, L.CANAL_Z[0] - 1.0, L.Y_NORTH - 0.7), "Stone_VM_Base", 0.0)
    mb.finish()


def props():
    """postes de ferro com lanterna (NightOnly no V3), carroca com roda, barris e caixotes (SPEC 'Rua')"""
    rng = _rng(25)
    mb = MB("VM_Town_Props", "03_TOWN", rng, detail="far", floor=-999)

    def post(x, z, y):
        p = B(x, z, y)
        mb.box((1.2, 1.2, 0.8), (p.x, p.y, y + 0.4), (0, 0, 0), "Stone_VM_Dark", 0.0)
        mb.box((0.5, 0.5, 9.0), (p.x, p.y, y + 5.0), (0, 0, 0), "Metal_VM_Iron", 0.0)
        mb.box((1.1, 1.1, 1.5), (p.x, p.y, y + 9.9), (0, 0, 0), "Lantern_Glow", 0.0)
        mb.box((1.6, 1.6, 0.5), (p.x, p.y, y + 10.9), (0, 0, 0), "Metal_VM_Iron", 0.0)
    cx, cz = L.PLAZA_C
    for a in (35, 145, 215, 325):
        post(cx + math.cos(math.radians(a)) * (L.PLAZA_R - 3.0), cz + math.sin(math.radians(a)) * (L.PLAZA_R - 3.0), L.Y_PAVE)
    for z in (8.0, -30.0):
        for s in (-1, 1):
            post(s * (L.STREET_HW - 1.2), z, L.Y_PAVE if z > 0 else L.Y_NORTH)
    for (x, z) in ((30, 84), (54, 116), (44, 140), (-50, 50), (-92, 60), (58, 47)):
        post(x, z, L.Y_PAVE)
    # carroca (ref_01): caixa + 2 rodas grandes + varais, na rua curva
    F = VL.face_frame(57.0, 98.0, L.Y_PAVE, 0.3, 1.0)
    mb.box((6.0, 3.4, 1.6), F.p(0, 0, 2.6), F.r(), "Wood_VM_Plank", 0.0)
    for s in (-1, 1):
        mb.cyl(1.9, 0.5, F.p(-0.6, s * 2.0, 1.9), F.r(math.pi / 2, 0, 0), "Wood_VM_Timber", 10, bevel=0.0)
        mb.box((5.0, 0.3, 0.3), F.p(4.6, s * 1.0, 2.0), F.r(0, -0.25, 0), "Wood_VM_Timber", 0.0)
    for (x, z) in ((60.5, 103.0), (61.5, 105.0), (-20.0, 20.0), (12.0, 14.0), (-30.0, -46.0), (26.0, -46.0)):
        y = L.Y_NORTH if z < -20 else L.Y_PAVE
        p = B(x, z, y)
        mb.cyl(1.0, 2.4, (p.x, p.y, y + 1.2), (0, 0, 0), "Wood_VM_Plank", 8, r2=1.1, bevel=0.0)
    for (x, z) in ((63.0, 101.0), (-22.0, 18.0)):
        p = B(x, z, L.Y_PAVE)
        mb.box((2.2, 2.2, 2.2), (p.x, p.y, L.Y_PAVE + 1.1), (0, 0, rng.uniform(0, 1)), "Wood_VM_Plank", 0.0)
    mb.finish()


# ================================================================== CASAS
def houses():
    tops = []
    for h in L.HOUSES:
        ob, top = VL.house("VM_House_%s" % h["id"], h)
        tops.append((h["id"], round(top, 1)))
    print("CASAS: %d (cumeeiras %s)" % (len(tops), tops))


# ================================================================== FORJA (marco)
def forge():
    """FORJA DO IGNIS: base de pedra, andar enxaimel e telha laranja; salao central aberto pela frente (pe-direito ate
    os tirantes em Y 33: a envoltoria do golem fica LIVRE), alas oeste/leste fechadas, chamine de pedra alta no fundo,
    fornalha acesa atras do golem, roda d'agua na ala leste puxada pela levada, suportes de picaretas, placa da bigorna.
    Nada da forja entra na envoltoria do Ignis (QA_Env_Ignis) nem no chao livre diante dele (QA_Free_IgnisFront)."""
    rng = _rng(31)
    y0 = L.Y_NORTH
    hx0, hx1, hz0, hz1 = L.FORGE_HALL
    tie = L.FORGE_TIE_Y
    mb = MB("VM_Frg_Hall", "04_FORGE", rng, detail="far", floor=-999)
    # piso do salao (cota 7) - colisao: o piso do norte (vm_col) ja cobre em 7,0
    mb.box2(B(hx0, hz0, y0 - 0.4), B(hx1, hz1, y0 - 0.001), "Stone_VM_Trim", 0.0)
    # parede do fundo + fornalha (atras do golem: z <= -72, fora da envoltoria que vai ate -64,7)
    mb.box2(B(hx0, hz1, y0), B(hx1, hz1 - 1.2, tie), "Stone_VM_Base", 0.0)
    mb.box2(B(-7.5, hz1 + 4.5, y0), B(5.5, hz1, y0 + 6.5), "Stone_VM_Dark", 0.0)          # fornalha
    mb.box2(B(-4.0, hz1 + 4.6, y0 + 1.6), B(2.0, hz1 + 4.4, y0 + 4.6), "Forge_Glow_VM", 0.0)   # boca acesa
    FP.frustum(mb, tuple(B(-1.0, hz1 + 2.2, y0 + 6.5)), 13.0, 4.5, 6.0, 3.0, 9.0, "Stone_VM_Dark")  # coifa
    # pilares e verga da frente (vigas grossas), mao-francesa nos cantos de cima (fora da envoltoria: |x| >= 10)
    for x in (hx0 - 1.2, hx1 + 1.2):
        mb.box((2.6, 2.6, tie - y0 + 2.0), B(x, hz0 - 1.0, y0 + (tie - y0 + 2.0) / 2), (0, 0, 0), "Wood_VM_Timber", 0.0)
        mb.box((3.4, 3.4, 1.2), B(x, hz0 - 1.0, y0 + 0.6), (0, 0, 0), "Stone_VM_Dark", 0.0)
    mb.box2(B(hx0 - 2.6, hz0 - 2.4, tie), B(hx1 + 2.6, hz0 + 0.4, tie + 2.2), "Wood_VM_Timber", 0.0)   # verga
    for s, xp in ((1, hx0 - 0.2), (-1, hx1 + 0.2)):
        a = B(xp, hz0 - 1.0, tie - 7.0)
        b = B(xp + s * 5.0, hz0 - 1.0, tie)
        mb.beam(a, b, 1.2, 1.2, "Wood_VM_Timber", 0.0)
    # tirantes do salao (acima de Y 31)
    for z in (-58.0, -66.0, -74.0):
        mb.box2(B(hx0, z - 0.6, tie), B(hx1, z + 0.6, tie + 1.2), "Wood_VM_Timber", 0.0)
    # oitao da frente: reboco + enxaimel ate a cumeeira
    span = (hx1 - hx0) + 4.0
    rise = span / 2 * math.tan(math.radians(42))
    Ff = VL.face_frame((hx0 + hx1) / 2, hz0 - 1.0, tie + 2.2, 0, 1)
    Ff = VL.Frame(Ff.o.x, Ff.o.y, Ff.o.z, Ff.a - math.pi / 2)        # +y local = frente (+Z Roblox)
    VL.gable_tri(mb, Ff, span, 0.0, rise, -0.2, 0.8, "Plaster_VM_Cream", axis="x")
    mb.box((0.6, 0.5, rise * 0.95), Ff.p(0, 0.45, rise * 0.47), Ff.r(), "Wood_VM_Timber", 0.0)
    for s in (-1, 1):
        mb.beam(Ff.p(s * span * 0.42, 0.45, 0.4), Ff.p(0, 0.45, rise * 0.92), 0.6, 0.5, "Wood_VM_Timber", 0.0)
        mb.beam(Ff.p(s * span * 0.2, 0.45, 0.3), Ff.p(s * span * 0.2, 0.45, rise * 0.5), 0.6, 0.5, "Wood_VM_Timber", 0.0)
    # telhado do salao (cumeeira ao longo de Z)
    Fr = VL.face_frame((hx0 + hx1) / 2, (hz0 + hz1) / 2 - 1.0, tie + 2.2, 0, 1)
    Fr = VL.Frame(Fr.o.x, Fr.o.y, Fr.o.z, Fr.a - math.pi / 2)
    VL.roof_gable(mb, Fr, span, abs(hz1 - hz0) + 4.0, 0.0, 42.0, "Roof_VM_Terracotta", "Roof_VM_Ridge", over=1.6,
                  thick=0.9, ridge_axis="y")
    # placa da bigorna pendurada na verga (Y > 31, fora da envoltoria)
    mb.box((12.0, 0.6, 4.4), B(-0.9, hz0 + 0.9, tie + 4.6), (0, 0, 0), "Wood_VM_Plank", 0.0)
    mb.box((4.4, 0.3, 1.8), B(-0.9, hz0 + 1.3, tie + 4.9), (0, 0, 0), "Metal_VM_Bronze", 0.0)
    mb.box((2.0, 0.3, 1.0), B(-4.0, hz0 + 1.3, tie + 5.2), (0, 0, 0), "Metal_VM_Bronze", 0.0)
    mb.finish()
    for nm, (x0, x1, z0, z1) in (("VM_Frg_WingW", L.FORGE_WING_W), ("VM_Frg_WingE", L.FORGE_WING_E)):
        w = MB(nm, "04_FORGE", rng, detail="far", floor=-999)
        cxw, czw = (x0 + x1) / 2, (z0 + z1) / 2
        F = VL.face_frame(cxw, czw, y0, 0, 1)
        F = VL.Frame(F.o.x, F.o.y, F.o.z, F.a - math.pi / 2)         # +y local = +Z Roblox (frente)
        W, Dd = abs(x1 - x0), abs(z1 - z0)
        w.box((W, Dd, 10.0), F.p(0, 0, 5.0), F.r(), "Stone_VM_Base", 0.0)
        for sx in (-1, 1):
            for sy in (-1, 1):
                w.box((1.6, 1.6, 9.6), F.p(sx * (W / 2 - 0.5), sy * (Dd / 2 - 0.5), 5.0), F.r(), "Stone_VM_Trim", 0.0)
        w.box((W + 1.6, Dd + 1.6, 9.0), F.p(0, 0, 14.5), F.r(), "Plaster_VM_Ochre" if x0 < 0 else "Plaster_VM_Cream", 0.0)
        VL.timber_face(w, F, -(W + 1.6) / 2, (W + 1.6) / 2, (Dd + 1.6) / 2, 10.0, 19.0, "Wood_VM_Timber", sgn=1)
        Fs = VL.Frame(F.o.x, F.o.y, F.o.z, F.a + math.pi / 2)
        side = 1 if x0 < 0 else -1
        VL.timber_face(w, Fs, -(Dd + 1.6) / 2, (Dd + 1.6) / 2, side * (W + 1.6) / 2, 10.0, 19.0, "Wood_VM_Timber",
                       sgn=side)
        for k in range(3):
            w.box((2.0, 0.5, 2.8), F.p(-W / 2 + W * (k + 0.5) / 3, (Dd + 1.6) / 2 + 0.25, 14.5), F.r(),
                  "Window_VM_Dark", 0.0)
        w.box((5.0, 0.5, 7.0), F.p(0, Dd / 2 + 0.2, 3.5), F.r(), "Wood_VM_Plank", 0.0)       # portao da ala
        VL.roof_gable(w, F, W + 1.6, Dd + 1.6, 19.0, 50.0, "Roof_VM_Terracotta_B" if x0 < 0 else "Roof_VM_Terracotta",
                      "Roof_VM_Ridge", over=1.3, ridge_axis="y")
        rise_w = (W + 1.6) / 2 * math.tan(math.radians(50.0))
        for sy in (-1, 1):
            VL.gable_tri(w, F, W + 1.6, 19.0, rise_w, sy * (Dd + 1.6) / 2, 0.6, "Plaster_VM_Cream", axis="x")
        w.finish()
        col_box("Forge", (W, Dd, 19.0 + 1.0), (F.o.x, F.o.y, y0 + 9.5), F.r())
    # chamine de pedra alta (marco visivel do spawn por cima das casas) + brasa no topo
    cx, cz = L.CHIMNEY
    ch = MB("VM_Frg_Chimney", "04_FORGE", rng, detail="far", floor=-999)
    ch.box((13.0, 13.0, 27.0), B(cx, cz, y0 + 13.5), (0, 0, 0), "Stone_VM_Dark", 0.0)
    ch.box((14.0, 14.0, 1.2), B(cx, cz, y0 + 27.6), (0, 0, 0), "Stone_VM_Trim", 0.0)
    FP.frustum(ch, tuple(B(cx, cz, y0 + 28.2)), 11.0, 11.0, 8.6, 8.6, L.CHIMNEY_TOP - 3.0 - (y0 + 28.2), "Stone_VM_Dark")
    ch.box((11.6, 11.6, 1.4), B(cx, cz, L.CHIMNEY_TOP - 2.3), (0, 0, 0), "Stone_VM_Dark", 0.0)
    for s in (-1, 1):
        ch.box((11.6, 1.6, 1.6), B(cx, cz + s * 5.0, L.CHIMNEY_TOP - 0.8), (0, 0, 0), "Stone_VM_Dark", 0.0)
        ch.box((1.6, 8.4, 1.6), B(cx + s * 5.0, cz, L.CHIMNEY_TOP - 0.8), (0, 0, 0), "Stone_VM_Dark", 0.0)
    ch.box((8.0, 8.0, 0.4), B(cx, cz, L.CHIMNEY_TOP - 1.4), (0, 0, 0), "Forge_Glow_VM", 0.0)       # brasa
    # duto da coifa ate a chamine
    ch.box((5.0, 9.0, 5.0), B(-1.0, cz + 6.0, y0 + 17.0), (0, 0, 0), "Stone_VM_Dark", 0.0)
    ch.finish()
    col_box("Forge", (13.0, 13.0, L.CHIMNEY_TOP - y0), tuple(B(cx, cz, (L.CHIMNEY_TOP + y0) / 2)))
    colr("Forge", (hx0 - 2.0, y0, hz1 - 1.2), (hx1 + 2.0, tie + 2.0, hz1))                   # parede do fundo
    colr("Forge", (-7.5, y0, hz1), (5.5, y0 + 6.5, hz1 + 4.5))                                # fornalha
    for x in (hx0 - 1.2, hx1 + 1.2):
        colr("Forge", (x - 1.7, y0, hz0 - 2.7), (x + 1.7, tie + 2.0, hz0 + 0.7))              # pilares da frente
    wheel(rng)
    forge_props(rng)


def wheel(rng):
    """roda d'agua (blockout estatico; gira no V3) na ala leste, metade dentro da levada"""
    wx, wy, wz = L.WHEEL
    mb = MB("VM_Frg_Wheel", "04_FORGE", rng, detail="far", floor=-999)
    c = B(wx, wz, wy)
    r = L.WHEEL_R
    n = 16
    for k in range(n):
        a = math.tau * k / n
        p = Vector((c.x, c.y + math.cos(a) * r, c.z + math.sin(a) * r))
        mb.box((3.0, 1.0, 2.6), p, (a, 0, 0), "Wood_VM_Plank", 0.0)                 # pas
    for k in range(4):
        a = math.pi * k / 4
        mb.box((0.8, 2 * r * 0.95, 0.8), c, (a, 0, 0), "Wood_VM_Timber", 0.0)       # raios
    mb.cyl(0.9, 6.0, (c.x - 2.0, c.y, c.z), (0, math.pi / 2, 0), "Metal_VM_Iron", 8, bevel=0.0)   # eixo para a ala
    mb.finish()


def forge_props(rng):
    """suportes de picaretas a venda, sacos de carvao, lingotes (nada que pareca minerio de mineracao)"""
    mb = MB("VM_Frg_Props", "04_FORGE", rng, detail="far", floor=-999)
    y0 = L.Y_NORTH
    for x in (-22.0, 20.0):
        F = VL.face_frame(x, -47.0, y0, 0, 1)
        F = VL.Frame(F.o.x, F.o.y, F.o.z, F.a - math.pi / 2)
        mb.box((6.0, 1.0, 0.6), F.p(0, 0, 4.2), F.r(), "Wood_VM_Timber", 0.0)
        for s in (-1, 1):
            mb.box((0.6, 1.4, 4.6), F.p(s * 2.8, 0, 2.3), F.r(), "Wood_VM_Timber", 0.0)
        for k in range(4):
            xx = -2.1 + k * 1.4
            mb.box((0.35, 0.35, 4.4), F.p(xx, 0.6, 2.6), F.r(), "Wood_VM_Plank", 0.0)          # cabo
            mb.box((2.2, 0.5, 0.5), F.p(xx, 0.6, 4.7), F.r(rx=0.0, ry=0.25), "Metal_VM_Iron", 0.0)   # cabeca
    for (x, z) in ((-26.0, -50.0), (-27.5, -48.5), (24.5, -50.5)):
        p = B(x, z, y0)
        mb.ico(1.3, (p.x, p.y, y0 + 1.0), "Dirt_VM", 1, (1.0, 0.8, 1.0))      # saco de carvao (blockout)
    for k in range(3):
        p = B(14.0 + k * 1.2, -46.0, y0)
        mb.box((1.0, 2.2, 0.6), (p.x, p.y, y0 + 0.3 + k * 0.0), (0, 0, 0), "Metal_VM_Bronze", 0.0)   # lingotes
    mb.finish()


# ================================================================== SERVICOS: loja, ranking
def shop():
    """LOJA DE MOCHILAS (leste): terreo de pedra, andar enxaimel, oitao para a praca, porta 6x9 com toldo, vitrines em
    balanco dos dois lados da porta, balcao com o vendedor atras. Paredes de 16 (pedido do usuario em 09/24)."""
    rng = _rng(41)
    x0, x1, z0, z1 = L.SHOP
    y0 = L.Y_SHOP
    H = L.SHOP_WALL_H
    dz = L.SHOP_DOOR[1]
    mb = MB("VM_Shop_Building", "05_SERVICES", rng, detail="far", floor=-999)
    mb.box2(B(x0, z0, y0 - 0.4), B(x1, z1, y0), "Stone_Paving_VM", 0.0)                         # piso
    t = 1.0
    walls = [((x0, z0), (x0 + t, dz - 3.0)), ((x0, dz + 3.0), (x0 + t, z1)), ((x1 - t, z0), (x1, z1)),
             ((x0, z0), (x1, z0 + t)), ((x0, z1 - t), (x1, z1))]
    for (a, b) in walls:
        mb.box2(B(a[0], a[1], y0), B(b[0], b[1], y0 + 6.0), "Stone_VM_Base", 0.0)
        mb.box2(B(a[0], a[1], y0 + 6.0), B(b[0], b[1], y0 + H), "Plaster_VM_Cream", 0.0)
    mb.box2(B(x0, dz - 3.0, y0 + 9.0), B(x0 + t, dz + 3.0, y0 + H), "Plaster_VM_Cream", 0.0)        # sobre a porta
    Fw = VL.face_frame(x0, (z0 + z1) / 2, y0, -1, 0)
    Fw = VL.Frame(Fw.o.x, Fw.o.y, Fw.o.z, Fw.a - math.pi / 2)        # +y local = -X Roblox (fachada da praca)
    VL.timber_face(mb, Fw, -(z1 - z0) / 2, (z1 - z0) / 2, 0.0, 9.6, H, "Wood_VM_Timber", diag=True, sgn=1)
    # vitrines em balanco + toldo + placa
    for zc in (z0 + 6.5, z1 - 6.5):
        mb.box2(B(x0 - 1.6, zc - 3.5, y0 + 1.2), B(x0, zc + 3.5, y0 + 2.0), "Wood_VM_Timber", 0.0)
        mb.box2(B(x0 - 1.4, zc - 3.2, y0 + 2.0), B(x0 - 0.2, zc + 3.2, y0 + 6.8), "Window_VM_Dark", 0.0)
        mb.box2(B(x0 - 1.8, zc - 3.6, y0 + 6.8), B(x0, zc + 3.6, y0 + 7.4), "Wood_VM_Timber", 0.0)
    mb.box((3.0, 8.0, 0.4), B(x0 - 1.4, dz, y0 + 9.6), (0, math.radians(-20), 0), "Cloth_VM_Red", 0.0)
    mb.box((0.6, 8.0, 3.0), B(x0 - 0.7, dz, y0 + H + 1.0), (0, 0, 0), "Wood_VM_Plank", 0.0)
    mb.box((0.4, 3.0, 2.2), B(x0 - 1.1, dz, y0 + H + 1.0), (0, 0, 0), "Cloth_VM_Red", 0.0)   # mochila (placa)
    # telhado (cumeeira ao longo de X: oitao para a praca)
    Fr = VL.face_frame((x0 + x1) / 2, (z0 + z1) / 2, y0 + H, -1, 0)
    Fr = VL.Frame(Fr.o.x, Fr.o.y, Fr.o.z, Fr.a - math.pi / 2)
    VL.roof_gable(mb, Fr, (z1 - z0), (x1 - x0), 0.0, 45.0, "Roof_VM_Terracotta", "Roof_VM_Ridge", over=1.4,
                  ridge_axis="y")
    rise = (z1 - z0) / 2 * math.tan(math.radians(45))
    for x in (x0, x1):
        Fg = VL.face_frame(x, (z0 + z1) / 2, y0 + H, -1, 0)
        Fg = VL.Frame(Fg.o.x, Fg.o.y, Fg.o.z, Fg.a - math.pi / 2)
        VL.gable_tri(mb, Fg, (z1 - z0), 0.0, rise, -0.5 if x == x0 else 0.5, 1.0, "Plaster_VM_Cream", axis="x")
    # interior: balcao + estante
    mb.box2(B(74.0, 37.0, y0), B(76.0, 49.0, y0 + 3.6), "Wood_VM_Plank", 0.0)
    mb.box2(B(x1 - 2.5, z0 + 3.0, y0), B(x1 - 1.0, z1 - 3.0, y0 + 10.0), "Wood_VM_Timber", 0.0)
    mb.finish()
    # colisao: paredes (vao da porta), forro, balcao, estante
    for (a, b) in walls:
        colr("Shop", (a[0], y0, a[1]), (b[0], y0 + H, b[1]))
    colr("Shop", (x0, y0 + 9.0, dz - 3.0), (x0 + t, y0 + H, dz + 3.0))
    colr("Shop", (x0, y0 + H, z0), (x1, y0 + H + 2.0, z1))
    colr("Shop", (74.0, y0, 37.0), (76.0, y0 + 3.6, 49.0))
    colr("Shop", (x1 - 2.5, y0, z0 + 3.0), (x1 - 1.0, y0 + 10.0, z1 - 3.0))
    for zc in (z0 + 6.5, z1 - 6.5):
        colr("Shop", (x0 - 1.8, y0, zc - 3.6), (x0, y0 + 7.4, zc + 3.6))


def ranking():
    """RANKING TOP 100 (oeste): palco de pedra (6,4) voltado para a rua oeste e a praca, salao da guilda enxaimel atras
    (fundo dos quadros) e mastros com estandartes. Os quadros/podios sao do script (GlobalTop100): aqui so o lugar."""
    rng = _rng(42)
    ox, oz = L.RANK_O
    fx, fz = L.RANK_FACE
    n = math.hypot(fx, fz)
    fx, fz = fx / n, fz / n
    T = VL.face_frame(ox, oz, L.Y_RANK, -fz, fx)       # +x local = tangente, +y local = visitantes
    mb = MB("VM_Rank_Stage", "05_SERVICES", rng, detail="far", floor=-999)
    mb.box((58.0, 20.0, 1.2), T.p(0, 7.0, -1.0), T.r(), "Stone_VM_Base", 0.0)        # 5,8 .. 6,0
    mb.box((57.0, 19.0, 0.4), T.p(0, 7.0, -0.2), T.r(), "Stone_VM_Trim", 0.0)        # 6,0 .. 6,4
    for s in (-1, 1):
        mb.box((1.0, 1.0, 22.0), T.p(s * 30.0, 14.0, 11.0), T.r(), "Wood_VM_Timber", 0.0)
        mb.box((0.3, 6.0, 12.0), T.p(s * 30.0, 14.0 - 3.2, 14.0), T.r(rz=math.pi / 2), "Cloth_VM_Blue", 0.0)
    mb.finish()
    # salao da guilda atras dos quadros (casa enxaimel de 3 andares, fachada para o palco)
    back = (ox - fx * 13.0, oz - fz * 13.0)
    spec = dict(x=back[0], z=back[1], fx=fx, fz=fz, w=40, d=12, floors=3, ridge="x", plaster="Plaster_VM_Cream",
                roof="Roof_VM_Terracotta", chimney=1, dormer=True, y=L.Y_PAVE, ground_h=8.0)
    VL.house("VM_Rank_Hall", spec, coll="05_SERVICES", col_area="RankHall")


# ================================================================== PATIO DOS PORTAIS
def court():
    rng = _rng(51)
    cx, cz = L.COURT_C
    r0, r1, a0, a1 = L.COURT_RING
    mb = MB("VM_Court_Floor", "06_PORTALS", rng, detail="far", floor=-999)
    for b0, b1 in ((0, 180), (180, 360)):
        slab(mb, sector_r(cx, cz, 0.0001, r0, b0, b1, 36), PLAZA_TOP - 0.4, PLAZA_TOP, "Stone_Paving_VM")
    slab(mb, sector_r(cx, cz, r0, r0 + 1.0, a0, a1, 40), PLAZA_TOP - 0.4, L.Y_PORTAL - 0.6, "Stone_VM_Trim")
    slab(mb, sector_r(cx, cz, r0 + 1.0, r1, a0, a1, 48), L.Y_GRASS - 0.4, L.Y_PORTAL - 0.3, "Stone_VM_Base")
    slab(mb, sector_r(cx, cz, r0 + 1.2, r1 - 0.2, a0, a1, 48), L.Y_PORTAL - 0.3, L.Y_PORTAL, "Stone_Paving_VM")
    # pilares com estandarte entre os portais (6 + 1)
    for k in range(7):
        a = math.radians(180.0 + (k - 3.0) * L.PORTAL_STEP_DEG)
        x, z = cx + math.cos(a) * (r0 + 3.0), cz + math.sin(a) * (r0 + 3.0)
        p = B(x, z, L.Y_PORTAL)
        mb.box((2.0, 2.0, 12.0), (p.x, p.y, L.Y_PORTAL + 6.0), (0, 0, a), "Stone_VM_Trim", 0.0)
        mb.box((2.6, 2.6, 1.0), (p.x, p.y, L.Y_PORTAL + 12.5), (0, 0, a), "Stone_VM_Dark", 0.0)
        col_box("CourtPillar", (2.0, 2.0, 12.0), (p.x, p.y, L.Y_PORTAL + 6.0), (0, 0, a))
    mb.finish()
    import vm_portals
    return vm_portals.build()


# ================================================================== SAIDA: portao + ponte da Ilha 1
def exit_gate():
    rng = _rng(61)
    gx, gz = L.GATE
    hw = L.GATE_HW
    mb = MB("VM_Exit_Gate", "07_EXIT", rng, detail="far", floor=-999)
    for s in (-1, 1):
        x = gx + s * (hw + 3.2)
        mb.box((6.0, 6.0, 16.0), B(x, gz, L.Y_PAVE + 8.0), (0, 0, 0), "Stone_VM_Base", 0.0)
        mb.box((7.0, 7.0, 1.0), B(x, gz, L.Y_PAVE + 16.5), (0, 0, 0), "Stone_VM_Trim", 0.0)
        FP.frustum(mb, tuple(B(x, gz, L.Y_PAVE + 17.0)), 7.6, 7.6, 0.6, 0.6, 7.0, "Roof_VM_Terracotta")
        colr("Gate", (x - 3.0, L.Y_PAVE, gz - 3.0), (x + 3.0, L.Y_PAVE + 16.0, gz + 3.0))
    mb.box2(B(gx - hw - 1.0, gz - 1.2, L.Y_PAVE + 12.0), B(gx + hw + 1.0, gz + 1.2, L.Y_PAVE + 14.5), "Wood_VM_Timber", 0.0)
    Fg = VL.face_frame(gx, gz, L.Y_PAVE + 14.5, 0, 1)
    Fg = VL.Frame(Fg.o.x, Fg.o.y, Fg.o.z, Fg.a - math.pi / 2)
    VL.roof_gable(mb, Fg, 2 * hw + 2.0, 4.0, 0.0, 40.0, "Roof_VM_Terracotta", "Roof_VM_Ridge", over=0.8, ridge_axis="x")
    mb.box((7.0, 0.5, 2.4), B(gx, gz + 1.4, L.Y_PAVE + 10.6), (0, 0, 0), "Wood_VM_Plank", 0.0)   # placa ILHA 1
    mb.finish()
    bridge_isle(rng)


def bridge_isle(rng):
    """ponte de pedra ate a praca de chegada da Vila da Folha (Roblox z 222, piso 6): tabuleiro em 6,0 que faz a curva
    para o sudoeste e entra RETO (+Z) na largura da praca (x +-12) no patamar final; muretas, lanternas e pilares"""
    mb = MB("VM_Exit_Bridge", "07_EXIT", rng, detail="far", floor=-999)
    P = L.ISLE_BRIDGE[:-1]
    w = L.ISLE_BRIDGE_W
    slab(mb, ribbon_r(P, w), L.Y_ISLE - 1.6, L.Y_ISLE, "Stone_Paving_VM")
    slab(mb, ribbon_r(P, w + 2.4), L.Y_ISLE - 3.4, L.Y_ISLE - 1.6, "Stone_VM_Base")
    x0, x1, z0, z1 = L.ISLE_LANDING
    mb.box2(B(x0, z0, L.Y_ISLE - 1.6), B(x1, z1, L.Y_ISLE), "Stone_Paving_VM", 0.0)
    mb.box2(B(x0 - 1.2, z0, L.Y_ISLE - 3.4), B(x1 + 1.2, z1, L.Y_ISLE - 1.6), "Stone_VM_Base", 0.0)
    for s in (-1, 1):
        edge = []
        for i, p in enumerate(P):
            a = P[max(0, i - 1)]
            b = P[min(len(P) - 1, i + 1)]
            dx, dz = b[0] - a[0], b[1] - a[1]
            ln = math.hypot(dx, dz) or 1.0
            edge.append((p[0] - dz / ln * s * (w / 2 + 0.6), p[1] + dx / ln * s * (w / 2 + 0.6)))
        slab(mb, ribbon_r(edge, 1.2), L.Y_ISLE, L.Y_ISLE + 1.6, "Stone_VM_Base")
        mb.box2(B((x1 + 0.6) * s - 0.6, z0, L.Y_ISLE), B((x1 + 0.6) * s + 0.6, z1, L.Y_ISLE + 1.6), "Stone_VM_Base", 0.0)
    # pilares de apoio e postes com lanterna
    for i, (x, z) in enumerate(P[1:], 1):
        p = B(x, z, 0)
        mb.box((7.0, 7.0, 40.0), (p.x, p.y, L.Y_ISLE - 3.4 - 20.0), (0, 0, 0), "Stone_VM_Base", 0.0)
        mb.box((5.0, 5.0, 16.0), (p.x, p.y, L.Y_ISLE - 3.4 - 48.0), (0, 0, 0), "Stone_VM_Dark", 0.0)
    for (x, z) in ((44.0, 160.0), (56.0, 160.0), (39.0, 184.0), (24.5, 199.0), (-7.0, 219.0), (7.0, 219.0)):
        p = B(x, z, L.Y_ISLE)
        mb.box((0.5, 0.5, 8.0), (p.x, p.y, L.Y_ISLE + 4.0), (0, 0, 0), "Metal_VM_Iron", 0.0)
        mb.box((1.1, 1.1, 1.5), (p.x, p.y, L.Y_ISLE + 8.6), (0, 0, 0), "Lantern_Glow", 0.0)
    mb.finish()


# ================================================================== AGUA
def water():
    mb = MB("VM_Water_Canal", "08_WATER", _rng(71), detail="far", floor=-999)
    z0, z1 = L.CANAL_Z
    x0, x1 = L.CANAL_X
    mb.box2(B(x0 - 1.0, z1, L.Y_CANAL_BED), B(x1 + 1.0, z0, L.Y_WATER), "Water_VM", 0.0)
    mb.box2(B(L.RACE_X[0], z0, L.Y_CANAL_BED), B(L.RACE_X[1], L.RACE_Z[1], L.Y_WATER), "Water_VM", 0.0)
    # cachoeiras nas pontas do canal (saem do plato)
    for x in (x0 - 1.5, x1 + 1.5):
        mb.box2(B(x - 1.0, z1, L.PLATEAU_BOTTOM + 4.0), B(x + 1.0, z0, L.Y_WATER), "Water_VM", 0.0)
    mb.finish()


# ================================================================== VEGETACAO
def vegetation():
    """pinheiros estilizados e arvores de copa redonda: cinturao na borda do plato + grupos entre as construcoes
    (sorteio fixo; descarta pontos em ruas, praca, casas, forja, loja, ranking, patio e terraco)"""
    import vm_col
    rng = _rng(81)
    keep = []
    cx, cz = L.PLAZA_C
    keep.append(lambda x, z: math.hypot(x - cx, z - cz) < L.PLAZA_R + 4)
    keep.append(lambda x, z: math.hypot(x - L.COURT_C[0], z - L.COURT_C[1]) < L.COURT_RING[1] + 6)
    keep.append(lambda x, z: -24 < x < 24 and 84 < z < 116)                    # terraco do spawn
    keep.append(lambda x, z: -40 < x < 37 and -96 < z < -30)                   # forja + largo
    keep.append(lambda x, z: 55 < x < 96 and 24 < z < 62)                      # loja
    keep.append(lambda x, z: -14 < x < 14 and -40 < z < 20)                    # eixo
    keep.append(lambda x, z: -24 < z < 0)                                      # canal
    keep.append(lambda x, z: 28 < x < 44 and -90 < z < -18)                    # levada
    ox, oz = L.RANK_O
    keep.append(lambda x, z: math.hypot(x - ox, z - oz) < 34)                  # ranking
    for h in L.HOUSES:
        keep.append(lambda x, z, h=h: math.hypot(x - h["x"], z - h["z"]) < 13)
    roads = [L.WEST_ROAD, L.EXIT_ROAD, [(34, 43), (62, 43)], [(0, 15), (0, -36)]]

    def near_road(x, z):
        for pts in roads:
            for (ax, az), (bx, bz) in zip(pts, pts[1:]):
                dx, dz = bx - ax, bz - az
                t = max(0.0, min(1.0, ((x - ax) * dx + (z - az) * dz) / (dx * dx + dz * dz)))
                if math.hypot(x - ax - dx * t, z - az - dz * t) < L.ROAD_W / 2 + 5:
                    return True
        return False
    P = L.PLATEAU
    pts = []
    for i in range(len(P)):                       # cinturao: 7 studs para dentro da borda
        a, b = P[i], P[(i + 1) % len(P)]
        ln = math.hypot(b[0] - a[0], b[1] - a[1])
        k = max(1, int(ln / 15))
        nx, nz = -(b[1] - a[1]) / ln, (b[0] - a[0]) / ln
        for j in range(k):
            t = (j + rng.uniform(0.2, 0.8)) / k
            x, z = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
            for d in (8.0, 20.0):
                px, pz = x + nx * d, z + nz * d
                if not VL.in_poly(px, pz, P):
                    px, pz = x - nx * d, z - nz * d
                pts.append((px + rng.uniform(-3, 3), pz + rng.uniform(-3, 3)))
    for (x, z, r, n) in ((95, -40, 26, 6), (-80, -60, 30, 7), (-60, 120, 18, 4), (110, 40, 22, 5), (-160, -80, 20, 4),
                         (90, -100, 22, 5)):
        for k in range(n):
            a = rng.uniform(0, math.tau)
            d = rng.uniform(0, r)
            pts.append((x + math.cos(a) * d, z + math.sin(a) * d))
    S = vm_col.south_poly()
    groups = {}
    nt = 0
    for (x, z) in pts:
        if not VL.in_poly(x, z, P) or any(f(x, z) for f in keep) or near_road(x, z):
            continue
        if L.GATE[0] - 16 < x < L.GATE[0] + 16 and z > 135:
            continue
        y = L.Y_GRASS if VL.in_poly(x, z, S) else L.Y_NORTH_GRASS
        q = ("N" if z < -20 else "S") + ("W" if x < 0 else "E")
        mb = groups.get(q) or MB("VM_Veg_Trees_" + q, "09_VEGETATION", _rng(82 + len(groups)), detail="far",
                                 floor=-999)
        groups[q] = mb
        if rng.random() < 0.55:
            VL.tree_pine(mb, x, z, y, rng.uniform(18, 30), rng)
        else:
            VL.tree_round(mb, x, z, y, rng.uniform(14, 22), rng)
        nt += 1
    for mb in groups.values():
        mb.finish()
    print("VEGETACAO: %d arvores em %d grupos" % (nt, len(groups)))


def build():
    terrain()
    town()
    houses()
    forge()
    shop()
    ranking()
    rep = court()
    exit_gate()
    water()
    vegetation()
    return rep
