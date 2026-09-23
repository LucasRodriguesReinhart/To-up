# fm_terrain_ridges - silhueta distante: cordilheiras quebradas em volta do vale (substitui os cones de fundo)
# Leitura em 3 planos: macicos principais (agulhas, dentes partidos, paredoes, mesas) -> selas e contrafortes
# que ligam os macicos em cordilheiras -> cordilheira longinqua mais clara (profundidade tambem no Roblox,
# onde cada material vira cor solida). Tudo enraizado no vale distante (z -70): nada flutua.
import math, random
from mathutils import Vector
import fm_lib
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

# macicos principais: (x, y, topo, raio, tipo). Composicao pensada a partir do spawn (olhando +Y), alternando
# tipos vizinhos para o skyline nunca virar "^ ^ ^": dente alto + chifre + paredao serrilhado a NO, vao livre atras
# do Portao de Konoha (vista para o longe), mesa larga atras da chamine (a chamine continua sendo o heroi), o
# CHIFRE mais alto a NE entre um dente e um paredao, e a cordilheira descendo pelo leste, sul (mais baixa e mais
# longe, lado aberto do spawn) e oeste.
MAIN = [
    # norte / noroeste
    (-188, 250, 226, 30, "spire"),
    (-222, 200, 168, 26, "horn"),
    (-160, 300, 184, 23, "wall"),
    # (x -140..-45, y < 420 livre: o corredor de Konoha enxerga o longe)
    (14, 312, 162, 30, "mesa"),
    (62, 282, 188, 28, "spire"),
    (124, 258, 242, 34, "horn"),
    (178, 222, 196, 24, "wall"),
    (238, 165, 166, 30, "mesa"),
    # leste
    (282, 78, 186, 30, "spire"),
    (298, -22, 148, 32, "horn"),
    (286, -128, 122, 28, "wall"),
    (246, -236, 110, 26, "mesa"),
    # sul: mais baixo e mais longe (lado de chegada: o spawn olha para fora e ve o vale distante)
    (150, -336, 100, 30, "horn"),
    (36, -392, 82, 30, "mesa"),
    (-96, -350, 96, 30, "mesa"),
    (-212, -268, 122, 28, "spire"),
    # oeste
    (-268, -122, 138, 30, "horn"),
    (-288, -8, 160, 31, "mesa"),
    (-266, 102, 192, 30, "spire"),
]

# cordilheira longinqua (mais clara), aparece nas selas e atras do Portao de Konoha
FAR = [
    (-112, 600, 250, 60, "horn"), (40, 660, 292, 70, "spire"), (240, 560, 236, 58, "mesa"),
    (-330, 470, 226, 58, "spire"), (590, 170, 238, 62, "horn"), (560, -170, 204, 60, "wall"),
    (-580, 90, 244, 62, "mesa"), (-540, -230, 206, 58, "horn"), (-240, -540, 178, 56, "wall"),
    (170, -570, 190, 60, "spire"),
]

# zonas onde a silhueta NAO pode entrar (vale + terraco + planaltos proximos, corredor de Konoha)
KEEP_OUT = [(-212, -128, 244, 200), (-142, 120, -44, 420)]


def _free(x, y, r):
    for (x0, y0, x1, y1) in KEEP_OUT:
        if x0 - r < x < x1 + r and y0 - r < y < y1 + r:
            return False
    return True


def _blocked(x, y, a):
    """flancos dos macicos: nao entram no vale/terraco nem no corredor de Konoha"""
    return not _free(x, y, 0.7 * a)


def build(C="02_TERRAIN"):
    rng = random.Random(4242)
    mb = MB("TER_Mountains_Peaks", C, rng)
    ctr = Vector((0.0, 40.0, 0.0))
    # 1) macicos principais (cada um e um aglomerado de corpos: dente/chifre/paredao/mesa + flancos)
    for (x, y, top, r, kind) in MAIN:
        peak(mb, x, y, r, top - VIS0, rng, z0=VIS0, kind=kind, root=ROOT, m="Cliff_Rock_Mid",
             m2="Cliff_Rock_Mid_Dark", face=(ctr.x - x, ctr.y - y), avoid=_blocked)
    # 2) selas entre macicos vizinhos (ordem angular em volta do centro do vale): ligam tudo em cordilheira
    ring = sorted(MAIN, key=lambda p: math.atan2(p[1] - ctr.y, p[0] - ctr.x))
    for i, a in enumerate(ring):
        b = ring[(i + 1) % len(ring)]
        pa, pb = Vector((a[0], a[1], 0)), Vector((b[0], b[1], 0))
        gap = (pb - pa).length - 1.6 * (a[3] + b[3])
        if gap < 10:
            continue
        k = 1 if gap < 60 else 2
        for j in range(k):
            f = (j + 1) / (k + 1) + rng.uniform(-0.08, 0.08)
            p = pa.lerp(pb, f)
            out = (p - ctr).normalized()
            p += out * rng.uniform(10, 24)          # sela recuada
            rr = rng.uniform(18, 25)
            if not _free(p.x, p.y, rr * 0.8):
                continue
            tp = VIS0 + (min(a[2], b[2]) - VIS0) * rng.uniform(0.42, 0.6)
            peak(mb, p.x, p.y, rr, tp - VIS0, rng, z0=VIS0, kind="saddle", root=ROOT, m="Cliff_Rock_Mid",
                 m2="Cliff_Rock_Mid_Dark", face=(ctr.x - p.x, ctr.y - p.y), avoid=_blocked)
    # 3) cordilheira longinqua, cor mais clara e fria, sem patamares de grama (leitura atmosferica)
    for (x, y, top, r, kind) in FAR:
        peak(mb, x, y, r, top - VIS0, rng, z0=VIS0, kind=kind, root=ROOT, m="Cliff_Rock_Far",
             m2="Cliff_Rock_Far_Dark", lids=False, face=(ctr.x - x, ctr.y - y), avoid=_blocked)
    return mb.finish()


def build_far_valley(C="02_TERRAIN"):
    """chao do vale distante sob a nevoa (so para render; nao vai para o Roblox): cor fria e baixa,
    com colinas baixas facetadas no lugar dos cones de topo chato"""
    rng = random.Random(5151)
    f = MB("TER_Far_Valley", C, rng)
    f.box((2400, 2400, 2), (0, 0, ROOT), (0, 0, 0), "Far_Haze", 0.0)
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
