# sg_props - VESTIR / PROPS da Ilha 3 (Shadow Garden). SO o que tem funcao de leitura (nada de encher vazio).
# ONDA 2 (2026-09-30, planta v4): lanterna da ordem (sg_emblem.lantern_post: soco de obsidiana, fuste de ferro negro,
# lanterna com vidro ambar, nucleo quente e chama) SO nos NOS da ilha nova que ninguem marcou ainda. Nos intervalos,
# nada (nada de cerca de luz). Quem ja marca os outros nos:
#   - entrada: porticos A/B, nos da ponte (sg_entry);       - topo da escada P1P2: arco de ferro da vila (sg_village);
#   - portas das casas: lanterna de parede (sg_village);      - topo da escada do portao e passagem leste: postes do
#   - alquimia / invocacao / saida: os modulos delas;           patamar do portao (sg_castle);
#   - pe da escada do portao: arco de ferro SG_Prop_GateArch (sg_court, agente do jardim).
# Este modulo poe:
#   1. PRACA (R 26): 4 postes nas diagonais (marcam a praca e as 4 bocas de rua) e 4 bancos de pedra voltados para a
#      fonte, nos vaos entre as ruas;
#   2. PE DA ESCADA P1P2: par de postes menores ao lado dos pilaretes do banzo (o topo ja tem o arco de ferro);
#   3. CRUZAMENTO do eixo com a rua do P2: 1 poste na quina sudeste (fora das 2 ruas);
#   4. PE DA ESCADA LESTE (EastP3, alquimia -> passagem leste): 1 poste ao lado do pe;
#   5. PORTA DO CASTELO: par de postes nas pontas dos degraus do porche (a luz quente e a L_SGCas_Door do castelo);
#   6. BOCA DO BECO OESTE (patio -> rota da saida): 1 poste ao sul da boca.
# Os postes e bancos assentam no chao REAL (raio para baixo na cena montada; o calcamento da vila fica 0,30 acima do
# patamar). Prefixo SG_Prop_, colecao 09_PROPS. Colisao propria: poste (caixa fina) e banco (bloco). As luzes reais sao
# do sg_lights (LAMPS: nome, x, y, z do chao, acesa?).
import math, random
import sg_lib as SL
from sg_lib import MB, col_box, Frame
import sg_layout as L
import sg_emblem as EM

P1, P2, P3 = L.P1, L.P2, L.P3
COLL = "09_PROPS"
PAVE = 0.30                          # topo do calcamento da vila acima do patamar (sg_village.PAVE)
LEG_M = "Stone_SG_Block_B"
SEAT_M = "Stone_SG_TrimLow"
SL.fm_lib.MATS.setdefault(SEAT_M, (SL.fm_lib.S(132, 128, 134), 0.8, 0.0, 0, None, 0.06))
import sg_court as CT

_C = L.PLAZA_C
CAMS = {
    "CAM_SGProp_Plaza": ((40.0, -262.0, P1 + 24.0), (0.0, -214.0, P1 + 2.0), 22),
    "CAM_SGProp_PH_Plaza": ((-30.0, -246.0, P1 + 5.5), (8.0, -205.0, P1 + 6.0), 22),
    "CAM_SGProp_PH_StairTop": ((-10.0, -128.0, P2 + 5.5), (0.0, -175.0, P1 + 6.0), 22),
    "CAM_SGProp_PH_P2Cross": ((-36.0, -80.0, P2 + 5.5), (10.0, -95.0, P2 + 5.0), 22),
    "CAM_SGProp_PH_CastleDoor": ((0.0, -6.0, P3 + 5.5), (0.0, 48.0, P3 + 12.0), 15),
    "CAM_SGProp_PH_EastFoot": ((132.0, -78.0, P2 + 5.5), (155.0, -30.0, P2 + 8.0), 22),
    "CAM_SGProp_PH_Beco": ((-60.0, 14.0, P3 + 5.5), (-120.0, 34.0, P3 + 5.0), 22),
}
# rotas extras: a volta pela borda da praca passa entre os bancos e os postes
EXTRA_ROUTES = {
    "PROP_PRACA_BORDA_N": ([(_C[0] + 20.5 * math.cos(math.radians(a)), _C[1] + 20.5 * math.sin(math.radians(a)))
                            for a in (20.0, 45.0, 62.0, 90.0, 118.0, 135.0, 150.0)], P1),
    "PROP_PRACA_BORDA_S": ([(_C[0] + 20.0 * math.cos(math.radians(a)), _C[1] + 20.0 * math.sin(math.radians(a)))
                            for a in (210.0, 225.0, 242.0, 270.0, 298.0, 315.0, 340.0)], P1),
}
EXTRA_PROBES = []

# postes: (nome, x, y, z_do_chao_esperado, acesa, altura, escala). A lanterna fica em z + h - 0,24 s + LH_GLASS s.
LAMP_H = 8.3                          # poste padrao (como os postes da vila)
PLAZA_LAMP_R = 23.6
_P1P2 = L.stair_frame("P1P2")
_EAST = L.stair_frame("EastP3")
POSTS = [("Plaza_%s" % n, _C[0] + PLAZA_LAMP_R * math.cos(math.radians(a)),
          _C[1] + PLAZA_LAMP_R * math.sin(math.radians(a)), P1 + PAVE, True, LAMP_H - 0.9, 1.0)
         for n, a in (("NE", 45.0), ("NW", 135.0), ("SW", 225.0), ("SE", 315.0))]
POSTS += [
    # pe da escada P1P2: ao lado dos pilaretes do banzo (x +-10, y -168,1), fora da largura da rua (14)
    ("P1P2Foot_W", -(_P1P2[2] / 2 + 4.0), _P1P2[0][1] - 1.6, P1 + PAVE, False, 6.6, 0.9),
    ("P1P2Foot_E", (_P1P2[2] / 2 + 4.0), _P1P2[0][1] - 1.6, P1 + PAVE, False, 6.6, 0.9),
    # cruzamento eixo (x +-7) x rua do P2 (y -91..-81): quina sudeste, no gramado
    ("P2Cross", 10.8, -95.0, P2, True, LAMP_H - 0.9, 1.0),
    # pe da escada leste (x 143..157, pe em y -40): lado leste, fora da rua que chega da alquimia
    ("EastP3Foot", _EAST[0][0] + _EAST[2] / 2 + 3.2, _EAST[0][1] - 3.0, P2, True, LAMP_H - 0.9, 1.0),
    # porta do castelo: pontas dos degraus do porche (x +-31, y 38..44); maiores (a porta e 28 x 34)
    ("CastleDoor_W", -35.5, 40.5, P3, False, 10.8, 1.4),
    ("CastleDoor_E", 35.5, 40.5, P3, False, 10.8, 1.4),
    # boca do beco oeste (o caminho sai do patio em (-90, 30) para (-150, 44)): ao sul da boca, no gramado
    ("BecoW", -103.0, 25.0, P3, True, LAMP_H - 0.9, 1.0),
]
# compat (sg_veg / sg_garden usam LAMPS como zona livre: nome, x, y, z, acesa)
LAMPS = [(n, x, y, z, lit) for n, x, y, z, lit, h, s in POSTS]
BENCH_R = 23.2
BENCH_A = (62.0, 118.0, 242.0, 298.0)
GLASS = {}                            # nome -> centro do vidro (o sg_lights poe a luz ali)
SINK = 0.05                           # soco e pes entram 0,05 no chao (nada coplanar com o calcamento: z-fight F5)


def _ground(x, y, z0, tol=1.2):
    """topo do chao REAL em (x, y) perto de z0: raio para baixo na cena montada, pulando colisao, vegetacao e
    marcadores. Sem acerto dentro da tolerancia, fica z0."""
    import bpy
    from mathutils import Vector
    dg = bpy.context.evaluated_depsgraph_get()
    sc = bpy.context.scene
    o = Vector((x, y, z0 + tol + 6.0))
    seen = []
    walk = None
    for _ in range(12):
        hit, loc, nrm, idx, ob, mw = sc.ray_cast(dg, o, Vector((0.0, 0.0, -1.0)), distance=2 * tol + 8.0)
        if not hit:
            break
        seen.append((ob.name, round(loc.z, 2)))
        if ob.name.startswith("COL_") and abs(loc.z - z0) <= tol and nrm.z > 0.7 and walk is None:
            walk = loc.z              # topo andavel: vale se o visual estiver coplanar com ele (o raio nao o ve)
        if ob.name.startswith(("COL_", "SG_Veg_", "SCALE_", "PREVIEW_", "BLK_")) or nrm.z < 0.7:
            o = loc - Vector((0.0, 0.0, 0.02))
            continue
        if abs(loc.z - z0) <= tol:
            return loc.z - SINK
        break
    if walk is not None:
        return walk - SINK
    print("PROPS AVISO: chao nao achado em (%.1f, %.1f) perto de %.2f; fica %.2f %s" % (x, y, z0, z0, seen))
    return z0


def lamp(mb, x, y, z, h=LAMP_H - 0.9, s=1.0):
    """poste-lanterna da ordem (sg_emblem.lantern_post). Devolve o centro do vidro."""
    c = EM.lantern_post(mb, mb, (x, y, z), 0.0, h=h, s=s)
    col_box("SG_PropLamp", (1.2 * s, 1.2 * s, h + 1.6 * s), (x, y, z + (h + 1.6 * s) / 2))
    return c


def bench(mb, x, y, z, yaw):
    """banco de pedra da praca (overhaul 01): 2 pes em console (perfil de balaustre achatado), assento em 2 pedras com
    pingadeira, encosto baixo em fronton suave. Frente (local +y) para 'yaw'. Colisao: um bloco."""
    F = Frame(x, y, z, yaw)
    prof = [(0.0, 0.62), (0.16, 0.62), (0.26, 0.46), (0.55, 0.34), (0.85, 0.40), (1.02, 0.56), (1.12, 0.64),
            (1.20, 0.64)]
    for sx in (-1.7, 1.7):
        rows = []
        for zz, hw in prof:
            rows.append([F.p(sx - 0.23, -hw, zz), F.p(sx + 0.23, -hw, zz), F.p(sx + 0.23, hw, zz),
                         F.p(sx - 0.23, hw, zz)])
        CT._loft(mb, rows, LEG_M)
    mb.box((4.7, 1.36, 0.10), F.p(0.0, 0.0, 1.25), F.r(), SEAT_M, 0.0)                     # pingadeira
    for sx in (-1, 1):
        mb.box((2.47, 1.6, 0.32), F.p(sx * 1.255, 0.0, 1.46), F.r(), SEAT_M, 0.1)          # assento (2 pedras)
    back = [(-2.3, 1.62), (2.3, 1.62), (2.3, 2.22), (1.2, 2.36), (0.0, 2.50), (-1.2, 2.36), (-2.3, 2.22)]
    CT._loft(mb, [[F.p(a, -0.80, b) for a, b in back], [F.p(a, -0.54, b) for a, b in back]], LEG_M)
    col_box("SG_PropBench", (5.0, 1.7, 2.5), F.p(0.0, 0.0, 1.25), F.r())


def build():
    rng = random.Random(3320)
    GLASS.clear()
    mb = MB("SG_Prop_Plaza", COLL, rng, detail="near")
    for n, x, y, z, lit, h, s in POSTS:
        if n.startswith(("Plaza", "P1P2Foot")):
            GLASS[n] = tuple(lamp(mb, x, y, _ground(x, y, z), h, s))
    for a in BENCH_A:
        r = math.radians(a)
        x, y = _C[0] + BENCH_R * math.cos(r), _C[1] + BENCH_R * math.sin(r)
        bench(mb, x, y, _ground(x, y, P1 + PAVE), r + math.pi / 2)      # frente para a fonte
    mb.finish()
    mr = MB("SG_Prop_NodeLamps", COLL, rng, detail="near")
    for n, x, y, z, lit, h, s in POSTS:
        if not n.startswith(("Plaza", "P1P2Foot")):
            GLASS[n] = tuple(lamp(mr, x, y, _ground(x, y, z), h, s))
    mr.finish()
    print("PROPS postes=%d bancos=%d acesos=%d" % (len(POSTS), len(BENCH_A), sum(1 for p in POSTS if p[4])))
