# sg_props - VESTIR / PROPS da Ilha 3 (Shadow Garden). SO o que tem funcao de leitura (nada de encher vazio):
#   1. praca: 4 postes de ferro na borda (o pe da escada P1->P2 e a chegada da calcada ficam marcados; a vila deixou o
#      pe da escada para estas lanternas) e 4 bancos de pedra voltados para a fonte, nos vaos entre as ruas e a rota;
#   2. postes de rota (mesma familia dos postes da vila) SO nos trechos que ficaram escuros a noite: rua do P2 no oeste
#      (entre as casas, olhando para o mirante da cachoeira) e o fim da rua leste do P1 (mirante da cachoeira leste,
#      a rua termina ali). O caminho do patio ate a dungeon ja fica lido pelo
#      calcamento, pela luz do vao leste da muralha e pelo braseiro da portaria: sem poste ali.
# Prefixo SG_Prop_, colecao 09_PROPS. Colisao propria: poste (caixa fina) e banco (bloco). As luzes sao do sg_lights
# (LAMPS: nome, posicao da lanterna, acesa?).
import math, random
import sg_lib as SL
from sg_lib import MB, col_box, Frame
import sg_layout as L

P1, P2, P3 = L.P1, L.P2, L.P3
COLL = "09_PROPS"
IRON = "Metal_SG_BlackIron"          # ferro negro (paleta: grades, postes, correntes)
OBS = "Stone_SG_Obsidian"
STONE = "Stone_SG_Block"
TRIM = "Stone_SG_Trim"
GLOW = "Lantern_Glow"

CAMS = {
    "CAM_SGProp_Plaza": ((34.0, -168.0, P1 + 22.0), (0.0, -124.0, P1 + 2.0), 22),
    "CAM_SGProp_PH_PlazaN": ((6.0, -140.0, P1 + 5.2), (-4.0, -104.0, P1 + 5.0), 22),
    "CAM_SGProp_PH_P2West": ((-40.0, -44.0, P2 + 5.2), (-100.0, -50.0, P2 + 5.0), 22),
}
# rotas extras: a volta pela borda da praca passa entre os bancos e os postes
_C = L.PLAZA_C
EXTRA_ROUTES = {
    "PROP_PRACA_BORDA_N": ([(_C[0] + 20.5 * math.cos(math.radians(a)), _C[1] + 20.5 * math.sin(math.radians(a)))
                            for a in (20.0, 45.0, 62.0, 90.0, 118.0, 135.0, 150.0)], P1),
    "PROP_PRACA_BORDA_S": ([(_C[0] + 20.0 * math.cos(math.radians(a)), _C[1] + 20.0 * math.sin(math.radians(a)))
                            for a in (210.0, 225.0, 242.0, 270.0, 298.0, 315.0, 340.0)], P1),
}
EXTRA_PROBES = []

# (nome, x, y, z_piso, acesa) - postes; a lanterna fica em z_piso + 8,3 (como os postes da vila)
LAMP_H = 8.3
PLAZA_LAMP_R = 23.6
LAMPS = [("Plaza_NE", 45.0), ("Plaza_NW", 135.0), ("Plaza_SW", 225.0), ("Plaza_SE", 315.0)]
LAMPS = [(n, _C[0] + PLAZA_LAMP_R * math.cos(math.radians(a)), _C[1] + PLAZA_LAMP_R * math.sin(math.radians(a)), P1,
          n in ("Plaza_NE", "Plaza_NW")) for n, a in LAMPS]
LAMPS += [
    ("P2_West", -77.0, -51.3, P2, True),          # rua do P2 entre as casas do oeste (cipreste atras)
    ("P1_EastEnd", 113.0, -122.6, P1, True),      # fim da rua leste do P1: marca o mirante da cachoeira leste
]
BENCH_R = 23.2
BENCH_A = (62.0, 118.0, 242.0, 298.0)


def lamp(mb, x, y, z):
    """poste de ferro da vila (mesma familia do sg_village): soco de pedra, fuste, lanterna ambar com grade e agulha"""
    mb.cyl(0.75, 0.9, (x, y, z + 0.35), (0, 0, math.pi / 8), OBS, n=8, bevel=0.0)
    mb.cyl(0.5, 0.5, (x, y, z + 1.05), (0, 0, math.pi / 8), IRON, n=8, r2=0.3, bevel=0.0)
    mb.cyl(0.26, 6.2, (x, y, z + 4.3), (0, 0, 0), IRON, n=8, r2=0.2, bevel=0.0)
    mb.cyl(0.42, 0.3, (x, y, z + 4.0), (0, 0, 0), IRON, n=8, bevel=0.0)
    zc = z + LAMP_H
    mb.box((1.3, 1.3, 0.25), (x, y, zc - 0.95), (0, 0, 0), IRON, 0.0)
    mb.cyl(0.35, 0.6, (x, y, zc - 1.3), (0, 0, 0), IRON, n=8, r2=0.2, bevel=0.0)
    mb.box((0.85, 0.85, 1.5), (x, y, zc), (0, 0, 0), GLOW, 0.0)
    for sx in (-1, 1):
        for sy in (-1, 1):
            mb.box((0.22, 0.22, 1.7), (x + sx * 0.5, y + sy * 0.5, zc), (0, 0, 0), IRON, 0.0)
    SL.spire(mb, (x, y), 1.05, zc + 0.85, 1.6, IRON, n=4)
    mb.cyl(0.12, 0.8, (x, y, zc + 2.7), (0, 0, 0), IRON, n=4, r2=0.02, bevel=0.0)
    col_box("SG_PropLamp", (1.0, 1.0, 9.0), (x, y, z + 4.5))


def bench(mb, x, y, z, yaw):
    """banco de pedra (sem encosto): 2 pes de alvenaria + tampo de cantaria clara; frente para 'yaw'"""
    F = Frame(x, y, z, yaw)
    for s in (-1, 1):
        mb.box((0.9, 1.3, 1.25), F.p(s * 1.75, 0.0, 0.62), F.r(), STONE, 0.08)
    mb.box((5.0, 1.7, 0.42), F.p(0.0, 0.0, 1.46), F.r(), TRIM, 0.1)
    mb.box((4.4, 0.35, 0.3), F.p(0.0, -0.55, 0.15), F.r(), STONE, 0.0)      # travessa baixa (le como peca, nao caixa)
    col_box("SG_PropBench", (5.0, 1.7, 1.67), F.p(0.0, 0.0, 0.84), F.r())


def build():
    rng = random.Random(3320)
    mb = MB("SG_Prop_Plaza", COLL, rng, detail="near")
    for n, x, y, z, lit in LAMPS:
        if n.startswith("Plaza"):
            lamp(mb, x, y, z)
    for a in BENCH_A:
        r = math.radians(a)
        x, y = _C[0] + BENCH_R * math.cos(r), _C[1] + BENCH_R * math.sin(r)
        # Frame: local +y = frente do banco -> aponta para a fonte
        bench(mb, x, y, P1, r + math.pi / 2)
    mb.finish()
    mr = MB("SG_Prop_RouteLamps", COLL, rng, detail="near")
    for n, x, y, z, lit in LAMPS:
        if not n.startswith("Plaza"):
            lamp(mr, x, y, z)
    mr.finish()
