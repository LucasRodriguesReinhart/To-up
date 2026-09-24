# fm_terrain_ridges - silhueta distante: cordilheiras quebradas em volta do vale (substitui os cones de fundo)
# Skyline com HIERARQUIA (nada de "| | | |"): duas dominantes (NO e NE, esta com o busto do guardiao-ferreiro
# esculpido), cada uma ladeada por ombros largos e baixos (paredao / mesa); mesa larga e baixa atras da torre (a
# coroa da forja recorta contra o ceu); no maximo 2 agulhas no anel; sul como cordilheira baixa e comprida (topos
# 60-80) com base em talude e um entalhe que mostra o vale distante. Vizinhos contrastam em largura (1:2:4) e
# altura (1:1.4:2), em grupos de 2-3 com vaos desiguais (a cordilheira longinqua aparece nos vaos).
# Planos de profundidade por material (cor solida no Roblox): medio Cliff_Rock_Mid, longe Cliff_Rock_Far.
# Tudo enraizado no vale distante (z -70): nada flutua.
import math, random
from mathutils import Vector
import fm_lib
import fm_parts
from fm_lib import MB
from fm_parts import peak

# cor solida por plano (o Roblox nao recebe o ruido do shader): longe = mais claro e mais frio
fm_lib.MATS.setdefault("Cliff_Rock_Mid", ((0.25, 0.26, 0.33), 0.92, 0.0, 0, None, 0.10))
fm_lib.MATS.setdefault("Cliff_Rock_Mid_Dark", ((0.16, 0.165, 0.225), 0.92, 0.0, 0, None, 0.08))
fm_lib.MATS.setdefault("Cliff_Rock_Far", ((0.27, 0.30, 0.42), 0.95, 0.0, 0, None, 0.05))
fm_lib.MATS.setdefault("Cliff_Rock_Far_Dark", ((0.19, 0.21, 0.32), 0.95, 0.0, 0, None, 0.05))
fm_lib.MATS.setdefault("Far_Haze", ((0.20, 0.27, 0.27), 1.0, 0.0, 0, None, 0.04))

ROOT = -70.0      # chao do vale distante
VIS0 = 30.0       # base visual (nivel do terraco): proporcoes das massas contam daqui

# macicos principais: (x, y, topo, raio, tipo)
MAIN = [
    # NO: grupo de 3 - ombro-paredao, DOMINANTE NO, ombro-mesa (o corpo encolhe fora do corredor de Konoha)
    (-230, 194, 156, 34, "wall"),
    (-190, 252, 240, 46, "dominant"),
    (-176, 312, 166, 40, "mesa"),
    # (x -140..-45, y < 420 livre: o corredor de Konoha enxerga o longe)
    # N: mesa larga e baixa atras da torre (sozinha), depois o grupo da DOMINANTE NE (com o rosto)
    (14, 318, 124, 46, "mesa"),
    (70, 296, 150, 30, "wall"),
    (124, 258, 242, 46, "dominant"),
    (184, 216, 160, 42, "mesa"),
    # leste: mesa baixa + agulha (1 de 2) + chifre; vao; paredao baixo + mesa
    (246, 150, 122, 44, "mesa"),
    (288, 70, 176, 22, "spire"),
    (300, -24, 138, 32, "horn"),
    (292, -132, 94, 36, "wall"),
    (250, -240, 86, 40, "mesa"),
    # sul: cordilheira baixa e comprida (topos 60-80, base em talude); entalhe entre o 2o e o 3o (vale distante)
    (176, -320, 72, 50, "range"),
    (58, -376, 64, 54, "range"),
    (-96, -372, 78, 52, "range"),
    (-190, -306, 66, 55, "range"),
    # oeste: chifre + mesa larga + agulha (2 de 2)
    (-272, -124, 112, 30, "horn"),
    (-294, -8, 126, 46, "mesa"),
    (-270, 98, 178, 22, "spire"),
]
NE_DOMINANT = (124, 258)
GUARD_SHELF = 124.0          # patamar do busto (acima das faixas de tras vistas do spawn)
GUARD_LOOK = (0.0, -60.0)    # o busto olha para o spawn/praca
GUARD_H = 74.0

# cordilheira longinqua (mais clara), aparece nos vaos entre os grupos e atras do Portao de Konoha
FAR = [
    (-112, 600, 236, 80, "wall"), (40, 668, 296, 52, "horn"), (236, 566, 214, 88, "mesa"),
    (-334, 468, 250, 50, "horn"), (590, 176, 226, 78, "wall"), (560, -170, 196, 60, "mesa"),
    (-584, 92, 262, 54, "horn"), (-540, -232, 186, 90, "wall"), (-244, -540, 150, 70, "mesa"),
    (170, -574, 162, 96, "wall"),
]

# cadeia de ilhas do jogo (lobby ativo, 2026-09-24): da borda sul do spawn a Vila da Folha (Area 1) e as outras areas
# seguem para o SUL do Blender (Roblox +z), com ~392 de largura. Nenhuma silhueta nessa faixa: o sul do anel abre e,
# da praca, o jogador ve a primeira ilha.
ISLES = (-205, -900, 205, -118)
# zonas onde a silhueta NAO pode entrar (vale + terraco + planaltos proximos, corredor de Konoha, cadeia de ilhas)
KEEP_OUT = [(-212, -128, 244, 200), (-142, 120, -44, 420), ISLES]


def _in_isles(x, y, r):
    x0, y0, x1, y1 = ISLES
    return x0 - r < x < x1 + r and y0 - r < y < y1 + r


def _free(x, y, r):
    for (x0, y0, x1, y1) in KEEP_OUT:
        if x0 - r < x < x1 + r and y0 - r < y < y1 + r:
            return False
    return True


def _blocked(x, y, a):
    """flancos dos macicos: nao entram no vale/terraco nem no corredor de Konoha"""
    return not _free(x, y, 0.7 * a)


def _corridor(x, y):
    """corpo principal: nunca dentro da janela do corredor de Konoha (o Passo da Folha enxerga o longe)"""
    x0, y0, x1, y1 = KEEP_OUT[1]
    return x0 < x < x1 and y0 < y < y1


def build(C="02_TERRAIN"):
    rng = random.Random(4242)
    mb = MB("TER_Mountains_Peaks", C, rng)
    ctr = Vector((0.0, 40.0, 0.0))
    guard = None
    main = [m for m in MAIN if not _in_isles(m[0], m[1], 0.9 * m[3])]
    far = [m for m in FAR if not _in_isles(m[0], m[1], 0.9 * m[3])]
    print("SKYLINE: %d/%d macicos e %d/%d longinquos fora da cadeia de ilhas" % (len(main), len(MAIN), len(far), len(FAR)))
    # 1) macicos principais
    for (x, y, top, r, kind) in main:
        face = (ctr.x - x, ctr.y - y)
        shelf = None
        if (x, y) == NE_DOMINANT:
            face = (GUARD_LOOK[0] - x, GUARD_LOOK[1] - y)
            shelf = GUARD_SHELF
        peak(mb, x, y, r, top - VIS0, rng, z0=VIS0, kind=kind, root=ROOT, m="Cliff_Rock_Mid",
             m2="Cliff_Rock_Mid_Dark", face=face, avoid=_blocked, fit=_corridor,
             base_taper=(1.0 / 1.6 if kind == "range" else None), shelf_z=shelf)
        if (x, y) == NE_DOMINANT:
            guard = dict(fm_parts._LAST_PEAK, c=(x, y))
    # 2) selas so dentro dos grupos (vaos curtos) e baixas: entre os grupos o vao fica aberto para o longe
    ring = sorted(main, key=lambda p: math.atan2(p[1] - ctr.y, p[0] - ctr.x))
    for i, a in enumerate(ring):
        b = ring[(i + 1) % len(ring)]
        pa, pb = Vector((a[0], a[1], 0)), Vector((b[0], b[1], 0))
        gap = (pb - pa).length - 1.6 * (a[3] + b[3])
        if gap < 10 or gap > 70 or rng.random() > 0.6:
            continue
        f = 0.5 + rng.uniform(-0.12, 0.12)
        p = pa.lerp(pb, f)
        out = (p - ctr).normalized()
        p += out * rng.uniform(12, 26)          # sela recuada
        rr = rng.uniform(16, 22)
        if not _free(p.x, p.y, rr * 0.8):
            continue
        tp = VIS0 + (min(a[2], b[2]) - VIS0) * rng.uniform(0.35, 0.5)
        peak(mb, p.x, p.y, rr, tp - VIS0, rng, z0=VIS0, kind="saddle", root=ROOT, m="Cliff_Rock_Mid",
             m2="Cliff_Rock_Mid_Dark", face=(ctr.x - p.x, ctr.y - p.y), avoid=_blocked)
    # 3) cordilheira longinqua, cor mais clara e fria, sem patamares de grama (leitura atmosferica)
    for (x, y, top, r, kind) in far:
        peak(mb, x, y, r, top - VIS0, rng, z0=VIS0, kind=kind, root=ROOT, m="Cliff_Rock_Far",
             m2="Cliff_Rock_Far_Dark", lids=False, face=(ctr.x - x, ctr.y - y), avoid=_blocked)
    ob = mb.finish()
    # 4) busto do guardiao-ferreiro no patamar da dominante NE, de frente para o vale
    if guard and "face" in guard:
        import fm_terrain_guardian
        f = Vector((guard["face"][0], guard["face"][1], 0.0)).normalized()
        o = Vector((guard["c"][0], guard["c"][1], 0.0)) + f * 18.0
        fm_terrain_guardian.build(C, (o.x, o.y, guard["shelf_z"] - 1.5), (f.x, f.y), height=GUARD_H)
    return ob


def build_far_valley(C="02_TERRAIN"):
    """chao do vale distante sob a nevoa: o plano de 2400 e objeto proprio (TER_Far_Valley_Plane, o export tira)
    e as colinas baixas facetadas ficam em TER_Far_Valley"""
    rng = random.Random(5151)
    pl = MB("TER_Far_Valley_Plane", C, rng)
    pl.box((2400, 2400, 2), (0, 0, ROOT), (0, 0, 0), "Far_Haze", 0.0)
    pl.finish()
    f = MB("TER_Far_Valley", C, rng)
    n = 0
    for i in range(200):
        a = rng.uniform(0, math.tau)
        r = rng.uniform(330, 760)
        x, y = math.cos(a) * r, math.sin(a) * r + 40
        if not _free(x, y, 40):
            continue
        s = rng.uniform(40, 90)
        f.rock((x, y, ROOT + s * 0.12), (s * rng.uniform(1.4, 2.4), s * rng.uniform(1.0, 1.6), s * rng.uniform(0.35, 0.6)),
               "Far_Haze", 1, (0, 0, rng.uniform(0, 6)), jitter=0.2)
        n += 1
        if n >= 26:
            break
    return f.finish()
