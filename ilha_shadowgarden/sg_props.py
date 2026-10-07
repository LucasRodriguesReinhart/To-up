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
# FINESSE 3C (2026-10-06, agente R: 02.05, 03.01, 03.14, 03.15, 16.02): a vila passa a ser HABITADA sem virar feira.
# Uma CENA de oficio por casa (3 a 6 pecas, num canto logico do lote, nunca espalhadas), o resto do gramado continua
# espaco negativo:
#   H1 taverna ........ patio de servico no flanco da cozinha (leste, de frente para a praca): berco com 2 barris
#                       deitados, barris de pe, caixotes e o carrinho de mao; lenha ao lado da chamine (oeste, 03.09);
#   H2 ferreiro ....... sob o alpendre: forja de mao (lareira de pedra, brasa dentro do aro, coifa e cano ate o telhado),
#                       fole, bigorna no cepo, cocho de tempera com balde; pilha de lenha no pano oeste (03.09);
#   H3 boticario ...... secador de ervas (cavaletes em A, varas, macos pendurados e um pano) e cestos no flanco leste;
#                       banco de pedra sob a janela cega do pano oeste, que olha a praca (03.09);
#   H4 minerador ...... trilho curto (dormentes + 2 trilhos, para-choque) com o carrinho de mina VAZIO e o cavalete de
#                       ferramentas na parede leste (nada de minerio);
#   H5 cartografo ..... mesa de mapas encostada no flanco leste (folha aberta com pesos, rolos, tinteiro), cesto de
#                       rolos e banqueta;
#   H6 casa da guarda . posto de vigia no canto de tras (braseiro aceso com luz, banco na parede, cavalete de lancas);
#                       BECO de tras (03.14): telheiro de lenha entre as janelas, escada de servico encostada e a
#                       carroca de lenha parada;
#   H7 mestre de armas  BECO de tras (03.14) vira o terreiro de treino: chao batido, manequim, alvo e cavalete de armas.
#   02.05 bancos da praca refeitos: pes em voluta (plinto, pe, console e 2 rolos), assento em 2 pedras com nariz
#         torneado e pingadeira, espaldar com 2 arcos cegos e capa em 3 pecas; mesmo ritmo (pares no eixo N-S);
#   03.15 fim de rua: leste do P1 = banco de pedra virado para a vista + lanterna; oeste do P2 = banco virado para a
#         cachoeira + poste de direcao; terraco norte (pedido do G) = banco e lapide da ordem;
#   beco oeste (pedido do J): lanternas nos 3 nos (sobre o muro dos 2 nichos, par de bracos na fonte de parede) e a
#         lanterna pendurada no portico (com luz: sg_lights).
# Os postes e bancos assentam no chao REAL (raio para baixo na cena montada; o calcamento da vila fica 0,30 acima do
# patamar). Prefixo SG_Prop_, colecao 09_PROPS. As cenas da vila vao no MESMO objeto da praca (mesma paleta: 1 malha
# por material) e as lanternas do beco no objeto das lanternas de no. Colisao so nas caixas grandes em que o jogador
# esbarra. As luzes reais sao do sg_lights (LAMPS: nome, x, y, z do chao, acesa?; EXTRA_LIGHTS).
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

# paleta do vestir (so materiais que a ilha ja exporta)
WOOD = "Wood_SG_Dark"                # estrutura: postes, cavaletes, aros de madeira, carroca
WMID = "Wood_SGVilMid"               # madeira media dos moveis (sg_village_int): aduelas, tampos, caixotes, cabos
SL.fm_lib.MATS.setdefault(WMID, (SL.fm_lib.S(138, 98, 62), 0.8, 0.0, 0, None, 0.08))
IRON = "Metal_SG_Iron"
LINEN = "Plaster_SG"                 # linho / palha / papel (claro quente)
NAVY = "Cloth_SG_Navy"               # pano, couro do fole, aneis do alvo
LEAF = "Leaf_SGBox"                  # ervas
DIRT = "Dirt_SG"                     # chao batido do terreiro
OBS = "Stone_SG_Obsidian"            # carvao, agua escura do cocho
EMBER = "SG_LampCore_Glow"           # brasa (Neon ambar ESCURO, so dentro do aro da forja e da bacia do braseiro)

_C = L.PLAZA_C
CAMS = {
    "CAM_SGProp_Plaza": ((40.0, -262.0, P1 + 24.0), (0.0, -214.0, P1 + 2.0), 22),
    "CAM_SGProp_PH_Plaza": ((-30.0, -246.0, P1 + 5.5), (8.0, -205.0, P1 + 6.0), 22),
    "CAM_SGProp_PH_StairTop": ((-10.0, -128.0, P2 + 5.5), (0.0, -175.0, P1 + 6.0), 22),
    "CAM_SGProp_PH_P2Cross": ((-36.0, -80.0, P2 + 5.5), (10.0, -95.0, P2 + 5.0), 22),
    "CAM_SGProp_PH_CastleDoor": ((0.0, -6.0, P3 + 5.5), (0.0, 48.0, P3 + 12.0), 15),
    "CAM_SGProp_PH_EastFoot": ((132.0, -78.0, P2 + 5.5), (155.0, -30.0, P2 + 8.0), 22),
    "CAM_SGProp_PH_Beco": ((-60.0, 14.0, P3 + 5.5), (-120.0, 34.0, P3 + 5.0), 22),
    # FINESSE 3C (agente R): um canto de oficio por casa, fins de rua, beco oeste e terraco norte (olho a 5,5)
    "CAM_SGR_H1_Servico": ((-56.0, -251.0, P1 + 5.5), (-73.0, -265.0, P1 + 2.5), 22),
    "CAM_SGR_H2_Forja": ((-102.0, -214.0, P1 + 5.5), (-112.0, -193.0, P1 + 3.5), 22),
    "CAM_SGR_H3_Ervas": ((138.0, -244.0, P1 + 5.5), (116.0, -259.0, P1 + 2.5), 22),
    "CAM_SGR_H4_Trilho": ((128.0, -210.0, P1 + 5.5), (120.0, -179.0, P1 + 2.0), 22),
    "CAM_SGR_H5_Mapas": ((-30.0, -98.0, P2 + 5.5), (-50.0, -113.0, P2 + 2.5), 22),
    "CAM_SGR_H6_Guarda": ((-88.0, -76.0, P2 + 5.5), (-106.0, -50.0, P2 + 3.0), 22),
    "CAM_SGR_H6_Beco": ((-103.0, -26.5, P2 + 5.5), (-124.0, -46.0, P2 + 3.5), 22),
    "CAM_SGR_H7_Treino": ((-26.0, -34.0, P2 + 5.5), (-62.0, -36.0, P2 + 2.5), 22),
    "CAM_SGR_P1E_Fim": ((126.0, -219.0, P1 + 5.5), (158.0, -222.0, P1 + 2.0), 22),
    "CAM_SGR_P2W_Fim": ((-148.0, -84.0, P2 + 5.5), (-178.0, -86.0, P2 + 2.0), 22),
    "CAM_SGR_Beco_Fonte": ((-147.0, 122.0, P3 + 5.5), (-135.0, 139.0, P3 + 3.0), 22),
    "CAM_SGR_Beco_Portico": ((-140.0, 166.0, P3 + 5.5), (-136.5, 195.0, P3 + 7.5), 22),
    "CAM_SGR_Terraco": ((-22.0, 350.0, P3 + 5.5), (-42.0, 372.0, P3 + 2.0), 22),
    "CAM_SGR_Plaza_Bench": ((1.0, -213.0, P1 + 4.6), (10.9, -201.5, P1 + 1.6), 22),
    "CAM_SGR_P2_Media": ((-40.0, -130.0, P2 + 34.0), (-92.0, -52.0, P2), 22),
    "CAM_SGR_P1_Media": ((0.0, -300.0, P1 + 40.0), (-60.0, -230.0, P1), 22),
    # copias das CAM_A3_* da auditoria que o studio da zona dressing nao cria (sg_scene.a3_cams; olho a 5,5)
    "CAM_A3_02_Praca_Chegada": ((0.0, -262.0, P1 + 5.5), (0.0, -222.0, P1 + 6.0), 20),
    "CAM_A3_03_RuaP1_W": ((-30.0, -222.0, P1 + 5.5), (-150.0, -222.0, P1 + 8.0), 20),
    "CAM_A3_03_RuaP1_E": ((30.0, -222.0, P1 + 5.5), (150.0, -222.0, P1 + 8.0), 20),
    "CAM_A3_03_RuaP2_W": ((-10.0, -86.0, P2 + 5.5), (-160.0, -86.0, P2 + 8.0), 20),
    "CAM_A3_03_EixoP2": ((0.0, -140.0, P2 + 5.5), (0.0, -40.0, P3 + 20.0), 20),
    "CAM_A3_03_Vila_Media": ((70.0, -310.0, P1 + 55.0), (-30.0, -170.0, P1), 20),
    "CAM_A3_03_VilaAlta_Media": ((60.0, -150.0, P2 + 45.0), (-70.0, -80.0, P2), 20),
    "CAM_A3_13_Terraco_Norte": ((10.0, 358.0, P3 + 5.5), (-116.0, 342.0, P3 + 6.0), 20),
}


def _a3_house_cams():
    """CAM_A3_03_<casa>_Frente / _Lado (mesma formula do sg_scene._house_cams)"""
    out = {}
    for nm, tp, x, y, w, d, deg, z in L.HOUSES:
        a = math.radians(deg) - math.pi / 2

        def P(u, v, h, x=x, y=y, z=z, a=a):
            return (x + u * math.cos(a) - v * math.sin(a), y + u * math.sin(a) + v * math.cos(a), z + h)
        out["CAM_A3_03_%s_Frente" % nm] = (P(w * 0.45, d / 2 + 20.0, 5.5), P(-2.0, 0.0, 9.0), 20)
        out["CAM_A3_03_%s_Lado" % nm] = (P(-w / 2 - 16.0, d / 2 + 8.0, 5.5), P(0.0, -2.0, 8.0), 20)
    return out


CAMS.update(_a3_house_cams())

# rotas extras: a volta pela borda da praca passa entre os bancos e os postes; o beco de tras de H6/H7 e o terreiro
# continuam abertos (03.14); o flanco de servico da taverna e o fim das 2 ruas ficam livres
EXTRA_ROUTES = {
    "PROP_PRACA_BORDA_N": ([(_C[0] + 20.5 * math.cos(math.radians(a)), _C[1] + 20.5 * math.sin(math.radians(a)))
                            for a in (20.0, 45.0, 62.0, 90.0, 118.0, 135.0, 150.0)], P1),
    "PROP_PRACA_BORDA_S": ([(_C[0] + 20.0 * math.cos(math.radians(a)), _C[1] + 20.0 * math.sin(math.radians(a)))
                            for a in (210.0, 225.0, 242.0, 270.0, 298.0, 315.0, 340.0)], P1),
    "PROP_BECO_H6_H7": ([(-94.0, -78.0), (-94.0, -47.0), (-84.0, -30.0), (-40.0, -28.5), (-22.0, -50.0)], P2),
    "PROP_TAVERNA_SERVICO": ([(-56.0, -244.0), (-60.0, -258.0), (-59.5, -272.0)], P1),
    "PROP_TAVERNA_PORTAO": ([(-59.0, -265.0), (-67.4, -265.0)], P1),
    "PROP_BOTICARIO_PORTAO": ([(126.0, -260.6), (118.0, -260.6)], P1),
    "PROP_RUA_P1_FIM_LESTE": ([(140.0, -218.0), (150.0, -218.0), (150.0, -228.0)], P1),
    "PROP_RUA_P2_FIM_OESTE": ([(-160.0, -82.0), (-168.0, -82.0), (-168.0, -92.0)], P2),
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
    # 03.15: fim da rua leste do P1 (no parapeito): lanterna ao lado do banco da vista (so Neon: o teto de luzes)
    ("RuaP1_Fim", 155.0, -229.4, P1, False, 6.6, 0.9),
]
# compat (sg_veg / sg_garden usam LAMPS como zona livre: nome, x, y, z, acesa)
LAMPS = [(n, x, y, z, lit) for n, x, y, z, lit, h, s in POSTS]
BENCH_R = 23.2
BENCH_A = (62.0, 118.0, 242.0, 298.0)
GLASS = {}                            # nome -> centro do vidro (o sg_lights poe a luz ali)
EXTRA_LIGHTS = []                     # (nome, loc, energia, cor, raio): braseiro da guarda (sg_lights, NightOnly)
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
        if ob.name.startswith(("COL_", "SG_Veg_", "SCALE_", "PREVIEW_", "BLK_", "SG_Prop_")) or nrm.z < 0.7:
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


# ------------------------------------------------------------------ primitivas baratas (sem chanfro: props pequenos)
def _frustum(mb, c0, w0, d0, w1, d1, h, m, ang=0.0, top=True, bottom=True):
    """tronco de piramide retangular sem chanfro (c0 = centro da base, ang = giro)"""
    ca, sa = math.cos(ang), math.sin(ang)

    def P(x, y, z):
        return (c0[0] + x * ca - y * sa, c0[1] + x * sa + y * ca, c0[2] + z)
    rows = [[P(-w0 / 2, -d0 / 2, 0), P(w0 / 2, -d0 / 2, 0), P(w0 / 2, d0 / 2, 0), P(-w0 / 2, d0 / 2, 0)],
            [P(-w1 / 2, -d1 / 2, h), P(w1 / 2, -d1 / 2, h), P(w1 / 2, d1 / 2, h), P(-w1 / 2, d1 / 2, h)]]
    CT._loft(mb, rows, m, cap0="ngon" if bottom else None, cap1="ngon" if top else None)


def _axl(mb, o, ax, prof, m, n=8, ph=0.0, caps=(True, True)):
    """torno em torno de um eixo qualquer (prof = [(raio, distancia)]), tampas opcionais"""
    from mathutils import Vector
    ax = Vector(ax).normalized()
    o = Vector(o)
    ref = Vector((0.0, 0.0, 1.0)) if abs(ax.z) < 0.9 else Vector((1.0, 0.0, 0.0))
    e1 = ax.cross(ref).normalized()
    e2 = ax.cross(e1).normalized()
    rows = []
    for r, d in prof:
        rows.append([o + ax * d + (e1 * math.cos(ph + 2 * math.pi * i / n) + e2 * math.sin(ph + 2 * math.pi * i / n)) * r
                     for i in range(n)] if r > 1e-5 else [o + ax * d])
    CT._loft(mb, rows, m, cap0="ngon" if caps[0] else None, cap1="ngon" if caps[1] else None)


def _lathe(mb, c, prof, m, n=8, rot=0.0, caps=(True, True)):
    EM._lathe(mb, c, prof, m, n, rot, caps=caps)


def keg(mb, x, y, z, r=1.0, h=2.6, rot=0.0):
    """barril de pe: bojo em 2 troncos (aduelas de madeira media) e 2 arcos de ferro"""
    _lathe(mb, (x, y, z), [(r * 0.84, 0.0), (r, h * 0.5), (r * 0.84, h)], WMID, 8, rot)
    for t in (0.17, 0.83):
        hr = r * (0.84 + 0.16 * (1.0 - abs(t - 0.5) * 2.0)) + 0.05
        _lathe(mb, (x, y, z), [(hr, h * t - 0.12), (hr, h * t + 0.12)], IRON, 8, rot, caps=(False, False))


def keg_lying(mb, c, ax, r=1.0, ln=2.8):
    """barril deitado (eixo ax), c = centro"""
    from mathutils import Vector
    ax = Vector(ax).normalized()
    o = Vector(c) - ax * ln / 2
    _axl(mb, o, ax, [(r * 0.84, 0.0), (r, ln / 2), (r * 0.84, ln)], WMID, 8, math.pi / 8)
    for t in (0.17, 0.83):
        hr = r * (0.84 + 0.16 * (1.0 - abs(t - 0.5) * 2.0)) + 0.05
        _axl(mb, o, ax, [(hr, ln * t - 0.12), (hr, ln * t + 0.12)], IRON, 8, math.pi / 8, caps=(False, False))


def crate(mb, x, y, z, s, yaw):
    """caixote de tabua media com 2 cintas de madeira escura"""
    mb.box((s, s, s), (x, y, z + s / 2), (0, 0, yaw), WMID, 0.0)
    for dz in (0.24, s - 0.24):
        mb.box((s + 0.1, s + 0.1, 0.22), (x, y, z + dz), (0, 0, yaw), WOOD, 0.0)


def basket(mb, x, y, z, r=0.62, h=0.95, fill=LEAF):
    """cesto de vime (tronco de cone aberto) com o conteudo em monte saindo pela boca"""
    _lathe(mb, (x, y, z), [(r * 0.78, 0.0), (r, h - 0.08), (r + 0.06, h)], WMID, 8, caps=(True, False))
    _lathe(mb, (x, y, z), [(r - 0.02, h - 0.22), (r * 0.6, h + 0.18), (0.0, h + 0.3)], fill, 8, 0.4, caps=(False, False))


def woodpile(mb, x, y, z, out_yaw, ln, rows=3, depth=1.4, r=0.42, posts=True):
    """pilha de lenha encostada (frente da pilha para out_yaw): corpo escuro e as TOPOS das achas em madeira media,
    em fiadas desencontradas; 2 esteios nas pontas"""
    G = Frame(x, y, z, out_yaw - math.pi / 2)            # local +y = para fora da parede, x ao longo dela
    H = rows * 2 * r * 0.92 + 0.08
    mb.box((ln, depth, H), G.p(0.0, 0.0, H / 2 - 0.02), G.r(), WOOD, 0.0)
    step = 2 * r * 1.04
    for i in range(rows):
        k = int((ln - 0.3) / step) - (i % 2)
        x0 = -(k - 1) * step / 2
        zc = r * 0.95 + i * 2 * r * 0.92
        for j in range(k):
            xx = x0 + j * step + (0.08 if (i + j) % 3 == 0 else -0.05)
            rr = r * (0.92 if (i * 5 + j) % 4 else 0.8)
            _axl(mb, G.p(xx, depth / 2 - 0.04, zc), G.p(xx, depth / 2 + 1.0, zc) - G.p(xx, depth / 2, zc),
                 [(rr, 0.0), (rr, 0.16)], WMID, 6, 0.3 * j, caps=(False, True))
    if posts:
        for e in (-1, 1):
            mb.box((0.3, 0.3, H + 0.5), G.p(e * (ln / 2 + 0.16), depth / 2 - 0.2, (H + 0.5) / 2), G.r(), WOOD, 0.0)
    return H


def plank_bench(mb, x, y, z, yaw, ln=3.0):
    """banco de tabua (assento espesso sobre 2 cavaletes de pernas abertas): o banco encostado das casas"""
    F = Frame(x, y, z, yaw)
    mb.box((ln, 1.05, 0.26), F.p(0.0, 0.0, 1.62), F.r(), WMID, 0.0)
    for e in (-1, 1):
        for s in (-1, 1):
            mb.beam(F.p(e * (ln / 2 - 0.45), s * 0.62, 0.0), F.p(e * (ln / 2 - 0.45), s * 0.26, 1.5), 0.2, 0.22, WOOD, 0.0)
        mb.box((0.24, 1.0, 0.2), F.p(e * (ln / 2 - 0.45), 0.0, 1.4), F.r(), WOOD, 0.0)


def pick(mb, a, b, hd):
    from mathutils import Vector
    a, b = Vector(a), Vector(b)
    ax = (b - a).normalized()
    hd = Vector(hd)
    hd = (hd - ax * hd.dot(ax)).normalized()
    mb.beam(a, b + ax * 0.12, 0.15, 0.15, WMID, 0.0)
    mb.beam(b - hd * 0.95 - ax * 0.28, b + hd * 0.95 - ax * 0.28, 0.2, 0.22, IRON, 0.0)


def shovel(mb, a, b):
    from mathutils import Vector
    a, b = Vector(a), Vector(b)
    ax = (b - a).normalized()
    side = ax.cross(Vector((0.0, 0.0, 1.0)))
    side = side.normalized() if side.length > 0.1 else Vector((1.0, 0.0, 0.0))
    mb.beam(a + ax * 1.0, b, 0.14, 0.14, WMID, 0.0)
    mb.beam(a, a + ax * 1.05, 0.8, 0.08, IRON, 0.0)
    mb.beam(b - side * 0.3, b + side * 0.3, 0.13, 0.13, WMID, 0.0)


def bucket(mb, x, y, z, r=0.5):
    _lathe(mb, (x, y, z), [(r * 0.8, 0.0), (r, 0.95)], WMID, 8, caps=(True, False))
    _lathe(mb, (x, y, z), [(r * 0.78, 0.82), (r * 0.78, 0.84)], OBS, 8, caps=(False, True))      # agua escura
    _lathe(mb, (x, y, z), [(r * 0.85 + 0.04, 0.12), (r * 0.85 + 0.04, 0.26)], IRON, 8, caps=(False, False))


# ------------------------------------------------------------------ 02.05 banco de pedra da praca
def bench(mb, x, y, z, yaw, col=True):
    """banco de pedra (02.05): PES EM VOLUTA (plinto chanfrado, pe recuado, console e 2 rolos: o de baixo puxa o pe
    para a frente, o de cima recebe o assento), ASSENTO de 2 pedras com nariz torneado e pingadeira recuada, ESPALDAR
    baixo com 2 arcos cegos em relevo e capa em 3 pecas (a do meio mais alta). Assento a 1,74; frente (local +y) para
    'yaw'. Colisao: um bloco."""
    F = Frame(x, y, z, yaw)
    for sx in (-1.75, 1.75):
        _frustum(mb, F.p(sx, 0.0, 0.0), 0.72, 1.5, 0.6, 1.36, 0.3, LEG_M, F.a, bottom=False)       # plinto
        mb.box((0.46, 0.92, 0.98), F.p(sx, -0.12, 0.78), F.r(), LEG_M, 0.0)                        # pe
        mb.box((0.5, 1.36, 0.26), F.p(sx, 0.02, 1.4), F.r(), LEG_M, 0.0)                            # console
        mb.rod(F.p(sx - 0.25, 0.42, 0.52), F.p(sx + 0.25, 0.42, 0.52), 0.24, LEG_M, 8)             # voluta de baixo
        mb.rod(F.p(sx - 0.25, 0.6, 1.2), F.p(sx + 0.25, 0.6, 1.2), 0.19, LEG_M, 8)                 # voluta de cima
    mb.box((4.5, 1.24, 0.12), F.p(0.0, -0.06, 1.47), F.r(), LEG_M, 0.0)                            # pingadeira
    for e in (-1, 1):
        mb.box((2.36, 1.56, 0.26), F.p(e * 1.2, -0.04, 1.62), F.r(), SEAT_M, 0.05)                 # assento
    mb.rod(F.p(-2.38, 0.74, 1.6), F.p(2.38, 0.74, 1.6), 0.15, SEAT_M, 8)                           # nariz torneado
    # espaldar: pano de silhar + 2 arcos cegos em relevo + capa em 3 pecas
    mb.box((4.6, 0.32, 1.06), F.p(0.0, -0.66, 2.27), F.r(), LEG_M, 0.0)
    for e in (-1, 1):
        cx = e * 1.16
        arc = [(cx - 0.78, 1.86), (cx + 0.78, 1.86), (cx + 0.78, 2.3)]
        arc += [(cx + 0.78 * math.cos(math.radians(a)), 2.3 + 0.42 * math.sin(math.radians(a)))
                for a in (30.0, 60.0, 90.0, 120.0, 150.0)]
        arc += [(cx - 0.78, 2.3)]
        CT._loft(mb, [[F.p(u, -0.52, v) for u, v in arc], [F.p(u, -0.42, v) for u, v in arc]], SEAT_M, cap0=None,
                 cap1="fan")
    mb.box((1.6, 0.5, 0.2), F.p(0.0, -0.66, 2.9), F.r(), SEAT_M, 0.0)
    for e in (-1, 1):
        mb.box((1.55, 0.46, 0.16), F.p(e * 1.58, -0.66, 2.86), F.r(), SEAT_M, 0.0)
    if col:
        col_box("SG_PropBench", (5.0, 1.7, 2.5), F.p(0.0, 0.0, 1.25), F.r())


# ------------------------------------------------------------------ cenas das casas (03.01 / 16.02)
def hframe(nm):
    for rec in L.HOUSES:
        if rec[0] == nm:
            n, tp, x, y, w, d, deg, z = rec
            return Frame(x, y, z, math.radians(deg) - math.pi / 2), w, d, z
    raise KeyError(nm)


def wheelbarrow(mb, x, y, z, yaw):
    """carrinho de mao parado (roda para local +x), pes no chao"""
    F = Frame(x, y, z, yaw)
    mb.rod(F.p(1.45, -0.13, 0.56), F.p(1.45, 0.13, 0.56), 0.56, WOOD, 10)
    mb.rod(F.p(1.45, -0.16, 0.56), F.p(1.45, 0.16, 0.56), 0.14, IRON, 6)
    _lathe(mb, F.p(0.15, 0.0, 0.8), [(0.9, 0.0), (1.38, 0.72), (1.24, 0.72), (0.8, 0.12)], WMID, 4, F.a + math.pi / 4)
    for s in (-1, 1):
        mb.beam(F.p(1.5, s * 0.3, 0.56), F.p(-2.0, s * 0.68, 1.28), 0.16, 0.18, WOOD, 0.0)
        mb.beam(F.p(-0.85, s * 0.6, 1.0), F.p(-0.9, s * 0.64, 0.0), 0.16, 0.16, WOOD, 0.0)


def mureta(mb, F, a, b, z, h=1.25, piers=(True, True), urn=False):
    """mureta de lote (03.01): pano de silhar com capa clara de remate e pilares de ponta com capa; a e b em
    coordenadas do LOTE (u, v). urn: vaso de pedra com ervas sobre o pilar de b (o portao do quintal)"""
    pa, pb = F.p(a[0], a[1], z - F.o.z), F.p(b[0], b[1], z - F.o.z)
    ln = (pb - pa).length
    yaw = math.atan2(pb.y - pa.y, pb.x - pa.x)
    c = (pa + pb) / 2
    mb.box((ln, 0.62, h - 0.18), (c.x, c.y, z + (h - 0.18) / 2 - 0.04), (0, 0, yaw), LEG_M, 0.0)
    mb.box((ln + 0.1, 0.86, 0.2), (c.x, c.y, z + h - 0.12), (0, 0, yaw), SEAT_M, 0.0)
    for p, on in ((pa, piers[0]), (pb, piers[1])):
        if not on:
            continue
        mb.box((1.05, 1.05, h + 0.3), (p.x, p.y, z + (h + 0.3) / 2 - 0.04), (0, 0, yaw), LEG_M, 0.0)
        mb.box((1.3, 1.3, 0.22), (p.x, p.y, z + h + 0.33), (0, 0, yaw), SEAT_M, 0.0)
    if urn:
        zu = z + h + 0.44
        _lathe(mb, (pb.x, pb.y, zu), [(0.22, 0.0), (0.34, 0.12), (0.2, 0.3), (0.42, 0.78), (0.48, 0.86)], SEAT_M, 8,
               caps=(False, False))
        _lathe(mb, (pb.x, pb.y, zu), [(0.44, 0.74), (0.5, 1.05), (0.28, 1.35), (0.0, 1.42)], LEAF, 8, 0.3,
               caps=(False, False))
    col_box("SG_PropMureta", (ln + 0.6, 0.9, h + 0.4), (c.x, c.y, z + (h + 0.4) / 2), (0, 0, yaw))


def taverna(mb, rng):
    """H1: patio de servico no flanco leste (a cozinha: chamine 2 no canto de tras), visto da praca"""
    F, w, d, z = hframe("H1")
    u0 = w / 2                                                        # face leste (u = +19)
    zg = _ground(*F.p(u0 + 2.0, -4.0)[:2], z)
    # berco de 2 vigas com 2 barris deitados (eixo para fora da parede) na frente da janela cega
    for du in (1.3, 2.9):
        mb.box((0.36, 5.0, 0.42), F.p(u0 + du, -6.7, zg - z + 0.21), F.r(), WOOD, 0.0)
        for dv in (-8.9, -4.5):
            mb.box((0.5, 0.32, 0.3), F.p(u0 + du, dv, zg - z + 0.57), F.r(), WOOD, 0.0)
    for dv in (-7.8, -5.6):
        keg_lying(mb, F.p(u0 + 2.1, dv, zg - z + 0.4 + 1.02), F.p(1, 0) - F.p(0, 0), 1.02, 2.8)
    # barris de pe e um menor na frente, caixotes empilhados
    keg(mb, *F.p(u0 + 1.85, -2.6, zg - z), r=1.0, h=2.6, rot=0.2)
    keg(mb, *F.p(u0 + 1.95, -0.25, zg - z), r=1.0, h=2.6, rot=0.5)
    keg(mb, *F.p(u0 + 3.65, -1.6, zg - z), r=0.78, h=2.0, rot=0.1)
    crate(mb, *F.p(u0 + 1.75, 2.3, zg - z), 1.9, F.a + 0.06)
    crate(mb, *F.p(u0 + 1.7, 2.25, zg - z + 1.9), 1.5, F.a - 0.32)
    wheelbarrow(mb, *F.p(u0 + 5.6, -10.4, zg - z), F.a + math.radians(200.0))
    col_box("SG_PropTavern", (3.8, 14.2, 2.8), F.p(u0 + 2.2, -3.8, zg - z + 1.4), F.r())
    # o quintal de servico fechado por mureta (03.01): norte, leste com a abertura do portao (vaso no pilar)
    mureta(mb, F, (u0 + 0.75, 3.9), (u0 + 8.0, 3.9), zg, piers=(False, True))
    mureta(mb, F, (u0 + 8.0, 3.9), (u0 + 8.0, -0.6), zg, piers=(False, True), urn=True)
    mureta(mb, F, (u0 + 8.0, -5.4), (u0 + 8.0, -13.0), zg, piers=(True, True))
    # lenha ao lado da chamine monumental (pano oeste, 03.09): entre o peito da chamine e a janela cega
    xw, yw, _ = F.p(-u0 - 1.35, -2.25)
    woodpile(mb, xw, yw, _ground(xw, yw, z), F.a + math.pi, 3.6, rows=3)
    col_box("SG_PropWood", (1.5, 3.9, 2.6), (xw, yw, z + 1.3), F.r())
    # vassoura encostada ao lado da porta (entre a porta e o canteiro)
    mb.beam(F.p(-5.05, d / 2 + 1.25, 0.05), F.p(-5.45, d / 2 + 0.75, 4.3), 0.12, 0.12, WMID, 0.0)
    _frustum(mb, F.p(-5.02, d / 2 + 1.28, 0.0), 0.75, 0.28, 0.3, 0.16, 0.95, LINEN, F.a + 0.1)


def forge(mb, rng):
    """H2: forja de mao sob o alpendre (u 6..16 da frente, fundo 5,2): lareira de pedra com aro, brasa dentro do aro,
    coifa e cano ate o telhado do alpendre; fole; bigorna no cepo; cocho de tempera e balde; lenha no pano oeste"""
    F, w, d, z = hframe("H2")
    v0 = d / 2                                                        # face da frente
    zg = _ground(*F.p(11.0, v0 + 2.0)[:2], z)
    h = zg - z
    # lareira
    hu, hv = 13.6, v0 + 1.95                                          # entre a janela (u 9,8) e o poste (15,4)
    mb.box((2.8, 1.9, 1.95), F.p(hu, hv, h + 0.975), F.r(), LEG_M, 0.0)
    for (du, dv, su, sv) in ((0.0, 0.85, 3.0, 0.3), (0.0, -0.85, 3.0, 0.3), (1.35, 0.0, 0.3, 1.4), (-1.35, 0.0, 0.3, 1.4)):
        mb.box((su, sv, 0.32), F.p(hu + du, hv + dv, h + 2.11), F.r(), SEAT_M, 0.0)
    mb.box((2.4, 1.4, 0.16), F.p(hu, hv, h + 2.02), F.r(), OBS, 0.0)
    mb.box((1.2, 0.7, 0.16), F.p(hu + 0.1, hv - 0.05, h + 2.1), F.r(0, 0, 0.2), EMBER, 0.0)
    _frustum(mb, F.p(hu, hv - 0.1, h + 4.5), 2.7, 1.9, 0.72, 0.72, 1.5, IRON, F.a, bottom=False)
    mb.rod(F.p(hu, hv - 0.1, h + 5.95), F.p(hu, hv - 0.1, h + 11.3), 0.3, IRON, 8, caps=False)
    for e in (-1, 1):
        mb.beam(F.p(hu + e * 1.2, hv - 0.9, h + 4.52), F.p(hu + e * 0.6, hv - 0.9, h + 2.3), 0.1, 0.1, IRON, 0.0)
    # fole (tabuas em cunha + couro) no lado oeste, bico apontando para o aro
    bu = hu - 2.25
    mb.box((0.5, 1.2, 1.45), F.p(bu, hv, h + 0.72), F.r(), WOOD, 0.0)
    mb.box((1.5, 1.0, 0.1), F.p(bu, hv, h + 1.5), F.r(), WOOD, 0.0)
    mb.box((1.5, 0.9, 0.1), F.p(bu, hv, h + 2.0), F.r(0.0, -0.18, 0.0), WOOD, 0.0)
    _frustum(mb, F.p(bu - 0.05, hv, h + 1.55), 1.35, 0.86, 1.2, 0.8, 0.36, NAVY, F.a)
    mb.beam(F.p(bu + 0.7, hv, h + 1.72), F.p(hu - 1.3, hv, h + 1.98), 0.14, 0.14, IRON, 0.0)
    # bigorna no cepo, na frente da lareira (dentro da linha dos postes do alpendre)
    au, av = hu - 0.6, v0 + 4.0
    _lathe(mb, F.p(au, av, h), [(0.78, 0.0), (0.7, 1.5)], WOOD, 8)
    _lathe(mb, F.p(au, av, h + 1.5), [(0.55, 0.0), (0.0, 0.02)], WMID, 8, caps=(False, False))
    _frustum(mb, F.p(au, av, h + 1.5), 0.9, 0.62, 0.5, 0.36, 0.34, IRON, F.a)
    mb.box((0.44, 0.32, 0.3), F.p(au, av, h + 1.98), F.r(), IRON, 0.0)
    mb.box((1.2, 0.56, 0.3), F.p(au - 0.1, av, h + 2.28), F.r(), IRON, 0.0)
    _axl(mb, F.p(au + 0.5, av, h + 2.3), F.p(1, 0) - F.p(0, 0), [(0.25, 0.0), (0.0, 0.8)], IRON, 6)
    mb.beam(F.p(au - 0.3, av - 0.15, h + 2.5), F.p(au - 0.3, av + 0.75, h + 2.5), 0.12, 0.12, WMID, 0.0)   # martelo
    mb.box((0.4, 0.22, 0.22), F.p(au - 0.3, av - 0.2, h + 2.52), F.r(), IRON, 0.0)
    # cocho de tempera (agua escura) entre a porta e a lareira, e o balde
    tu, tv = 8.25, v0 + 1.4
    mb.box((2.3, 1.2, 0.18), F.p(tu, tv, h + 0.25), F.r(), WOOD, 0.0)
    for s in (-1, 1):
        mb.box((2.3, 0.16, 1.15), F.p(tu, tv + s * 0.52, h + 0.73), F.r(), WOOD, 0.0)
        mb.box((0.16, 0.9, 1.15), F.p(tu + s * 1.07, tv, h + 0.73), F.r(), WOOD, 0.0)
    mb.box((2.0, 0.9, 0.1), F.p(tu, tv, h + 1.1), F.r(), OBS, 0.0)
    bucket(mb, *F.p(tu - 0.1, tv + 1.55, h), r=0.45)
    col_box("SG_PropForge", (8.4, 2.6, 2.4), F.p(11.05, v0 + 1.85, h + 1.2), F.r())
    col_box("SG_PropAnvil", (1.6, 1.6, 2.5), F.p(au, av, h + 1.25), F.r())
    # lenha no pano oeste (+u): entre a janela da frente e a janela cega (03.09)
    xw, yw, _ = F.p(w / 2 + 1.35, 0.9)
    woodpile(mb, xw, yw, _ground(xw, yw, z), F.a, 6.8, rows=3)
    col_box("SG_PropWood", (1.5, 7.1, 2.6), (xw, yw, z + 1.3), F.r())


def drying_rack(mb, F, u, v, ln, zb):
    """secador de ervas: 2 cavaletes em A (no plano u-z), vara de cima e 2 de baixo ao longo de v, macos pendurados"""
    top = 4.2
    for dv in (-ln / 2, ln / 2):
        for s in (-1, 1):
            mb.beam(F.p(u + s * 0.95, v + dv, zb), F.p(u + s * 0.08, v + dv, zb + top + 0.2), 0.18, 0.2, WOOD, 0.0)
        mb.beam(F.p(u - 0.62, v + dv, zb + 1.5), F.p(u + 0.62, v + dv, zb + 1.5), 0.14, 0.14, WOOD, 0.0)
    mb.beam(F.p(u, v - ln / 2 - 0.3, zb + top), F.p(u, v + ln / 2 + 0.3, zb + top), 0.16, 0.16, WOOD, 0.0)
    for s in (-1, 1):
        mb.beam(F.p(u + s * 0.66, v - ln / 2, zb + 1.5), F.p(u + s * 0.66, v + ln / 2, zb + 1.5), 0.12, 0.12, WOOD, 0.0)
    n = 6
    for i in range(n):
        dv = -ln / 2 + 0.75 + (ln - 1.5) * i / (n - 1)
        m = LEAF if i % 3 != 1 else LINEN
        ln_b = (0.95, 1.2, 0.8)[i % 3]
        _frustum(mb, F.p(u, v + dv, zb + top - 0.1 - ln_b), 0.18, 0.18, 0.5, 0.4, ln_b, m, F.a + 0.3 * i)
    # um pano de linho dobrado sobre a vara de baixo do lado de fora
    mb.box((0.08, 1.9, 0.9), F.p(u + 0.74, v + ln / 2 - 1.5, zb + 1.08), F.r(), NAVY, 0.0)


def apothecary(mb, rng):
    """H3: secador de ervas e cestos no flanco leste; banco sob a janela cega do pano oeste (03.09)"""
    F, w, d, z = hframe("H3")
    u0 = w / 2
    zg = _ground(*F.p(u0 + 3.0, -3.0)[:2], z)
    h = zg - z
    drying_rack(mb, F, u0 + 3.4, -2.9, 6.4, h)
    col_box("SG_PropRack", (2.2, 6.8, 4.4), F.p(u0 + 3.4, -2.9, h + 2.2), F.r())
    basket(mb, *F.p(u0 + 1.6, 1.7, h), r=0.66, fill=LEAF)
    basket(mb, *F.p(u0 + 2.2, 3.15, h), r=0.55, h=0.8, fill=LINEN)
    basket(mb, *F.p(u0 + 5.6, -7.0, h), r=0.6, fill=LEAF)
    # quintal das ervas fechado por mureta (03.01): norte e leste, abertura no meio do lado leste (vaso no pilar)
    mureta(mb, F, (u0 + 0.75, 4.6), (u0 + 8.2, 4.6), zg, piers=(False, True))
    mureta(mb, F, (u0 + 8.2, 4.6), (u0 + 8.2, -0.4), zg, piers=(False, True), urn=True)
    mureta(mb, F, (u0 + 8.2, -4.8), (u0 + 8.2, -10.2), zg, piers=(True, True))
    # banco encostado no pano oeste, sob a janela cega (v -5,4)
    xb, yb, _ = F.p(-u0 - 1.25, -5.4)
    plank_bench(mb, xb, yb, _ground(xb, yb, z), F.a + math.pi / 2, ln=3.4)


def rail_stub(mb, a, b, zb, gauge=2.6):
    """trilho curto: dormentes de madeira e 2 trilhos de ferro, de a a b"""
    from mathutils import Vector
    a, b = Vector((a[0], a[1], zb)), Vector((b[0], b[1], zb))
    t = (b - a)
    ln = t.length
    t.normalize()
    yaw = math.atan2(t.y, t.x)
    nrm = Vector((-t.y, t.x, 0.0))
    n = int(ln / 1.7)
    for i in range(n + 1):
        p = a + t * (ln * i / n)
        mb.box((0.62, gauge + 1.3, 0.24), (p.x, p.y, zb + 0.12), (0, 0, yaw + (0.04 if i % 3 == 1 else 0.0)), WOOD, 0.0)
    for s in (-1, 1):
        c = (a + b) / 2 + nrm * s * gauge / 2
        mb.box((ln + 0.6, 0.2, 0.32), (c.x, c.y, zb + 0.4), (0, 0, yaw), IRON, 0.0)
    return yaw, nrm


def mine_cart(mb, x, y, zr, yaw):
    """carrinho de mina VAZIO sobre o trilho (zr = topo do trilho): caçamba aberta de ferro, chassi e 4 rodas"""
    F = Frame(x, y, zr, yaw)
    for su in (-0.95, 0.95):
        for s in (-1, 1):
            mb.rod(F.p(su, s * 1.2, 0.46), F.p(su, s * 1.42, 0.46), 0.46, IRON, 8)
    mb.box((2.7, 2.2, 0.26), F.p(0.0, 0.0, 0.92), F.r(), WOOD, 0.0)
    _lathe(mb, F.p(0.0, 0.0, 1.05), [(1.5, 0.0), (1.85, 1.45), (1.66, 1.45), (1.32, 0.2)], IRON, 4, F.a + math.pi / 4)
    for s in (-1, 1):
        mb.box((0.18, 2.4, 0.2), F.p(s * 1.36, 0.0, 2.45), F.r(), WOOD, 0.0)


def miner(mb, rng):
    """H4: trilho curto paralelo a parede leste, carrinho vazio, para-choque no fim; ferramentas na parede"""
    F, w, d, z = hframe("H4")
    xr = 122.0
    zg = _ground(xr, -180.0, z)
    yaw, nrm = rail_stub(mb, (xr, -187.8), (xr, -172.6), zg)
    mine_cart(mb, xr, -176.6, zg + 0.56, yaw)
    # para-choque: trave e 2 escoras (fim norte)
    mb.box((3.6, 0.9, 1.1), (xr, -171.4, zg + 0.95), (0, 0, 0), WOOD, 0.0)
    for s in (-1, 1):
        mb.beam((xr + s * 1.3, -174.0, zg + 0.5), (xr + s * 1.3, -171.7, zg + 1.3), 0.26, 0.26, IRON, 0.0)
        mb.box((0.45, 0.45, 1.8), (xr + s * 1.75, -170.9, zg + 0.9), (0, 0, 0), WOOD, 0.0)
    col_box("SG_PropCart", (3.2, 4.0, 3.0), (xr, -176.6, zg + 1.6))
    col_box("SG_PropBumper", (4.0, 1.2, 1.8), (xr, -171.2, zg + 0.9))
    # cavalete de ferramentas encostado na parede leste (entre a quina da frente e o peito da chamine)
    xw = 116.0 + 0.6 + 0.35
    for yy in (-188.0, -184.4):
        mb.box((0.34, 0.34, 3.7), (xw, yy, zg + 1.85), (0, 0, 0), WOOD, 0.0)
    for zz in (1.0, 3.2):
        mb.box((0.3, 4.0, 0.28), (xw + 0.05, -186.2, zg + zz), (0, 0, 0), WOOD, 0.0)
    pick(mb, (xw + 1.0, -187.4, zg + 0.05), (xw + 0.3, -187.3, zg + 3.5), (0.0, 1.0, 0.0))
    pick(mb, (xw + 1.05, -185.7, zg + 0.05), (xw + 0.32, -185.9, zg + 3.45), (0.0, 1.0, 0.0))
    shovel(mb, (xw + 1.1, -184.9, zg + 0.05), (xw + 0.3, -185.0, zg + 3.5))
    crate(mb, 125.6, -188.6, zg, 1.7, 0.18)
    col_box("SG_PropTools", (1.8, 4.6, 3.8), (xw + 0.55, -186.2, zg + 1.9))


def cartographer(mb, rng):
    """H5: mesa de mapas encostada no flanco leste (entre a janela e a janela cega), cesto de rolos e banqueta"""
    F, w, d, z = hframe("H5")
    u0 = w / 2
    zg = _ground(*F.p(u0 + 2.0, 1.0)[:2], z)
    h = zg - z
    tu, tv = u0 + 1.5, 1.0
    mb.box((1.7, 3.6, 0.18), F.p(tu, tv, h + 2.06), F.r(), WMID, 0.0)
    for su in (-0.66, 0.66):
        for sv in (-1.55, 1.55):
            mb.box((0.2, 0.2, 1.98), F.p(tu + su, tv + sv, h + 0.99), F.r(), WOOD, 0.0)
        mb.box((0.14, 3.1, 0.18), F.p(tu + su, tv, h + 0.5), F.r(), WOOD, 0.0)
    mb.box((1.25, 1.65, 0.04), F.p(tu + 0.05, tv - 0.55, h + 2.17), F.r(0, 0, 0.1), LINEN, 0.0)        # mapa aberto
    for dv in (-1.32, 0.22):
        mb.box((0.22, 0.22, 0.14), F.p(tu + 0.42, tv + dv, h + 2.23), F.r(), IRON, 0.0)                 # pesos
    mb.rod(F.p(tu - 0.2, tv + 0.75, h + 2.28), F.p(tu - 0.25, tv + 1.6, h + 2.28), 0.13, LINEN, 6)    # rolos
    mb.rod(F.p(tu + 0.25, tv + 0.9, h + 2.27), F.p(tu + 0.55, tv + 1.62, h + 2.27), 0.12, LINEN, 6)
    _lathe(mb, F.p(tu - 0.3, tv - 1.45, h + 2.15), [(0.13, 0.0), (0.1, 0.24), (0.04, 0.28)], OBS, 6)  # tinteiro
    # cesto alto de rolos
    cu, cv = u0 + 1.2, -2.0
    _lathe(mb, F.p(cu, cv, h), [(0.48, 0.0), (0.58, 1.3), (0.62, 1.36)], WMID, 8, caps=(True, False))
    for i, (du, dv, tl) in enumerate(((0.15, 0.1, 0.18), (-0.18, 0.12, -0.12), (0.05, -0.2, 0.08), (-0.1, -0.05, 0.0))):
        mb.rod(F.p(cu + du, cv + dv, h + 0.4), F.p(cu + du + tl, cv + dv + tl * 0.5, h + 2.0 + 0.15 * i), 0.12, LINEN, 5)
    # banqueta
    su_, sv_ = u0 + 3.3, 1.6
    _lathe(mb, F.p(su_, sv_, h + 1.42), [(0.55, 0.0), (0.55, 0.16)], WMID, 8)
    for k in range(3):
        a = 2 * math.pi * k / 3 + 0.3
        mb.beam(F.p(su_ + 0.55 * math.cos(a), sv_ + 0.55 * math.sin(a), h), F.p(su_ + 0.3 * math.cos(a),
                sv_ + 0.3 * math.sin(a), h + 1.44), 0.14, 0.14, WOOD, 0.0)
    col_box("SG_PropMapTable", (2.0, 3.9, 2.3), F.p(tu, tv, h + 1.15), F.r())
    # toldo de lona navy preso na parede (abrigo da mesa): 2 varas na frente, lona caida e sanefa
    ua, ub, za, zb_ = u0 + 0.02, u0 + 3.0, h + 5.75, h + 4.75
    tl = math.atan2(za - zb_, ub - ua)
    ln_c = math.hypot(ub - ua, za - zb_)
    mb.box((ln_c, 4.6, 0.08), F.p((ua + ub) / 2, tv, (za + zb_) / 2), F.r(0.0, tl, 0.0), NAVY, 0.0)
    mb.box((0.06, 4.6, 0.55), F.p(ub + 0.02, tv, zb_ - 0.27), F.r(), NAVY, 0.0)
    for sv in (-2.1, 2.1):
        mb.box((0.16, 0.16, zb_ - h + 0.1), F.p(ub - 0.12, tv + sv, (zb_ + h) / 2), F.r(), WOOD, 0.0)
        mb.beam(F.p(u0 + 0.03, tv + sv, za + 0.9), F.p(ub - 0.12, tv + sv, zb_ + 0.04), 0.06, 0.06, IRON, 0.0)


def brazier(mb, x, y, z):
    """braseiro de ferro em tripe: bacia com borda, carvao e a brasa no coracao (dentro da borda). Devolve a luz."""
    for k in range(3):
        a = 2 * math.pi * k / 3 + 0.5
        mb.beam((x + 0.95 * math.cos(a), y + 0.95 * math.sin(a), z), (x + 0.3 * math.cos(a), y + 0.3 * math.sin(a),
                z + 2.75), 0.13, 0.13, IRON, 0.0)
    mb.box((0.9, 0.9, 0.08), (x, y, z + 1.0), (0, 0, 0.5), IRON, 0.0)
    _lathe(mb, (x, y, z), [(0.28, 2.62), (0.9, 3.08), (1.02, 3.3), (0.88, 3.3), (0.8, 3.14)], IRON, 8, 0.2)
    _lathe(mb, (x, y, z), [(0.8, 3.15), (0.5, 3.36), (0.0, 3.42)], OBS, 8, 0.2, caps=(False, False))
    _lathe(mb, (x + 0.08, y, z), [(0.46, 3.3), (0.22, 3.55), (0.0, 3.6)], EMBER, 6, 0.0, caps=(False, False))
    return (x, y, z + 4.3)


def spear_rack(mb, x, y, z, yaw):
    """cavalete de lancas: base, 2 montantes, travessa com 4 lancas encostadas"""
    F = Frame(x, y, z, yaw)
    mb.box((2.6, 0.7, 0.3), F.p(0, 0, 0.15), F.r(), WOOD, 0.0)
    for s in (-1, 1):
        mb.box((0.26, 0.26, 3.2), F.p(s * 1.15, -0.1, 1.75), F.r(), WOOD, 0.0)
    mb.box((2.7, 0.26, 0.26), F.p(0, -0.1, 3.3), F.r(), WOOD, 0.0)
    for i in range(4):
        su = -0.84 + 0.56 * i
        b = F.p(su, 0.18, 0.32)
        t = F.p(su + 0.04, -0.2, 5.9)
        mb.rod(b, t, 0.07, WMID, 4)
        _lathe(mb, tuple(t), [(0.13, 0.0), (0.0, 0.7)], IRON, 4, F.a)


def guard(mb, rng):
    """H6: posto de vigia no canto leste de tras (braseiro aceso, banco encostado, cavalete de lancas) e o BECO de tras
    (03.14): telheiro de lenha entre as 2 janelas, escada de servico encostada e a carroca de lenha parada"""
    F, w, d, z = hframe("H6")
    # posto de vigia (x -110 = face leste; peito da chamine em y -55,3..-61,7; contraforte em y -49,7..-52,3)
    bx, by = -104.6, -51.0
    zb = _ground(bx, by, z)
    EXTRA_LIGHTS.append(("H6Brazier", brazier(mb, bx, by, zb), 260.0, (1.0, 0.56, 0.26), 0.5))
    col_box("SG_PropBrazier", (2.0, 2.0, 3.4), (bx, by, zb + 1.7))
    plank_bench(mb, -108.75, -53.8, _ground(-108.75, -53.8, z), math.pi / 2, ln=2.7)
    spear_rack(mb, -102.2, -47.2, _ground(-102.2, -47.2, z), math.radians(232.0))
    col_box("SG_PropSpears", (2.8, 1.0, 3.6), (-102.2, -47.2, zb + 1.8), (0, 0, math.radians(232.0)))
    # BECO DE TRAS: telheiro de lenha entre as janelas de tras (x -117,7 .. -126,3), y > -49
    yb = -49.0 + 0.6
    zt = _ground(-122.0, yb + 1.5, z)
    woodpile(mb, -122.0, yb + 0.72, zt, math.pi / 2, 6.6, rows=3, posts=False)
    for xx in (-125.6, -118.4):
        mb.box((0.34, 0.34, 3.6), (xx, yb + 2.3, zt + 1.8), (0, 0, 0), WOOD, 0.0)
        mb.beam((xx, yb + 2.3, zt + 3.5), (xx, -48.98, zt + 4.3), 0.26, 0.26, WOOD, 0.0)
    for k in range(5):                                                # telhado de tabuas (5 tabuas em agua)
        mb.box((1.42, 3.9, 0.16), (-124.9 + 1.45 * k, -47.0, zt + 3.98 + (0.03 if k % 2 else 0.0)),
               (math.radians(-14.0), 0, 0), WOOD if k % 2 else WMID, 0.0)
    col_box("SG_PropShed", (7.6, 2.6, 3.4), (-122.0, yb + 1.3, zt + 1.7))
    # escada de servico encostada (entre a janela de tras oeste e a quina)
    xl = -131.4
    foot, top = (xl, yb + 3.3, zt), (xl, -48.86, zt + 11.6)
    from mathutils import Vector
    fa, ta = Vector(foot), Vector(top)
    for s in (-1, 1):
        mb.beam(fa + Vector((s * 0.62, 0, 0)), ta + Vector((s * 0.62, 0, 0)), 0.18, 0.22, WOOD, 0.0)
    for k in range(1, 11):
        p = fa.lerp(ta, k / 11.0)
        mb.box((1.3, 0.12, 0.14), (p.x, p.y, p.z), (0, 0, 0), WMID, 0.0)
    # carroca de lenha parada no beco (varais apoiados no chao, para leste)
    handcart(mb, -108.2, -40.6, _ground(-108.2, -40.6, z), math.radians(8.0))
    col_box("SG_PropHandcart", (4.4, 3.2, 2.6), (-108.6, -40.7, z + 1.3), (0, 0, math.radians(8.0)))


def handcart(mb, x, y, z, yaw):
    """carroca de 2 rodas (varais para local +x, apoiados no chao) com achas no leito"""
    F = Frame(x, y, z, yaw)
    for s in (-1, 1):
        mb.rod(F.p(-0.4, s * 1.18, 1.12), F.p(-0.4, s * 1.42, 1.12), 1.12, WOOD, 10)
        mb.rod(F.p(-0.4, s * 1.1, 1.12), F.p(-0.4, s * 1.52, 1.12), 0.2, IRON, 6)
    pitch = math.atan2(1.55 - 0.3, 4.4)
    Fm = (F.r(0.0, pitch, 0.0))
    mb.box((3.8, 2.1, 0.22), F.p(-0.4, 0.0, 1.62), Fm, WMID, 0.0)
    for s in (-1, 1):
        mb.box((3.8, 0.14, 0.62), F.p(-0.4, s * 1.0, 1.98), Fm, WOOD, 0.0)
        mb.beam(F.p(1.4, s * 0.72, 1.3), F.p(4.0, s * 0.62, 0.22), 0.2, 0.22, WOOD, 0.0)
    mb.box((0.14, 2.1, 0.7), F.p(-2.28, 0.0, 2.2), Fm, WOOD, 0.0)
    for i, (dy, dz) in enumerate(((-0.55, 0.0), (0.0, 0.0), (0.55, 0.0), (-0.28, 0.48), (0.28, 0.48))):
        mb.rod(F.p(-1.85, dy, 2.05 + dz + 0.25), F.p(1.0, dy + 0.05, 1.82 + dz + 0.25), 0.27, WOOD if i % 2 else WMID, 6)


def target(mb, x, y, z, yaw):
    """alvo de palha em cavalete (frente para local +y): disco de palha, aneis navy e linho"""
    F = Frame(x, y, z, yaw)
    tilt = math.radians(10.0)
    for s in (-1, 1):
        mb.beam(F.p(s * 1.2, 0.3, 0.0), F.p(s * 0.5, -0.05, 4.2), 0.18, 0.2, WOOD, 0.0)
    mb.beam(F.p(0.0, -1.5, 0.0), F.p(0.0, -0.2, 4.0), 0.18, 0.2, WOOD, 0.0)
    mb.beam(F.p(-1.2, 0.35, 1.6), F.p(1.2, 0.35, 1.6), 0.16, 0.16, WOOD, 0.0)
    from mathutils import Vector
    c = F.p(0.0, 0.32, 2.9)
    ax = (F.p(0.0, math.cos(tilt), math.sin(tilt)) - F.p(0.0, 0.0, 0.0))
    _axl(mb, c - ax * 0.25, ax, [(1.55, 0.0), (1.55, 0.45)], WMID, 12)
    for r, d, m in ((1.12, 0.47, NAVY), (0.72, 0.49, LINEN), (0.3, 0.51, NAVY)):
        _axl(mb, c - ax * 0.25 + ax * (d - 0.04), ax, [(r, 0.0), (r, 0.04)], m, 12, caps=(False, True))


def dummy(mb, x, y, z, yaw):
    """manequim de treino: poste com pes em cruz, bracos em travessa, tronco de saco e cabeca"""
    F = Frame(x, y, z, yaw)
    for a in (0.0, math.pi / 2):
        mb.box((2.4, 0.4, 0.36), F.p(0, 0, 0.18), F.r(0, 0, a), WOOD, 0.0)
    mb.box((0.42, 0.42, 4.5), F.p(0, 0, 2.25), F.r(), WOOD, 0.0)
    _lathe(mb, F.p(0, 0, 0), [(0.62, 2.0), (0.82, 2.7), (0.74, 3.75), (0.42, 4.15)], LINEN, 6, F.a, caps=(True, False))
    _lathe(mb, F.p(0, 0, 0), [(0.0, 4.15), (0.4, 4.4), (0.42, 4.85), (0.0, 5.15)], LINEN, 6, F.a)
    mb.box((3.0, 0.3, 0.3), F.p(0, 0, 3.55), F.r(), WOOD, 0.0)
    mb.box((1.66, 0.12, 0.2), F.p(0, 0.0, 2.6), F.r(), NAVY, 0.0)       # cinta de couro


def arms_rack(mb, x, y, z, yaw):
    """cavalete de armas encostado (frente local +y): 2 cavaletes, travessas, 3 espadas, 2 lancas e o escudo"""
    F = Frame(x, y, z, yaw)
    ln = 5.6
    for s in (-1, 1):
        mb.box((0.32, 0.9, 3.7), F.p(s * ln / 2, 0.0, 1.85), F.r(), WOOD, 0.0)
    for zz, dy in ((0.9, 0.25), (3.0, -0.2)):
        mb.box((ln + 0.3, 0.28, 0.28), F.p(0.0, dy, zz), F.r(), WOOD, 0.0)
    for i in range(3):
        su = -1.9 + 0.75 * i
        a, b = F.p(su, 0.4, 0.95), F.p(su + 0.06, -0.08, 3.6)
        mb.beam(a, a.lerp(b, 0.7), 0.26, 0.07, IRON, 0.0)                              # lamina
        g = a.lerp(b, 0.72)
        mb.beam(F.p(su - 0.42, 0.05, g.z - z), F.p(su + 0.42, 0.05, g.z - z), 0.12, 0.12, IRON, 0.0)
        mb.beam(g, b, 0.13, 0.13, NAVY, 0.0)                                           # punho
    for i in range(2):
        su = 0.6 + 0.6 * i
        mb.rod(F.p(su, 0.4, 0.1), F.p(su + 0.05, -0.18, 5.6), 0.07, WMID, 4)
        _lathe(mb, tuple(F.p(su + 0.05, -0.18, 5.6)), [(0.13, 0.0), (0.0, 0.65)], IRON, 4, F.a)
    so = F.p(ln / 2 + 0.25, 0.1, 2.3)
    ax = F.p(1.0, 0.0, 0.0) - F.p(0.0, 0.0, 0.0)
    _axl(mb, so, ax, [(1.0, 0.0), (1.0, 0.14)], WMID, 10)
    _axl(mb, so + ax * 0.14, ax, [(0.3, 0.0), (0.0, 0.22)], IRON, 6, caps=(True, False))


def arms_master(mb, rng):
    """H7: o beco entre a casa e a muralha (03.14) vira o TERREIRO de treino: chao batido, manequim, alvo e cavalete"""
    F, w, d, z = hframe("H7")
    zg = _ground(-62.0, -35.0, z)
    pts = [(-73.5, -39.6), (-60.0, -40.2), (-50.0, -39.4), (-47.6, -35.2), (-49.4, -29.8), (-62.0, -28.6),
           (-71.8, -29.6), (-74.6, -34.6)]
    mb.prism(SL.ccw(pts), zg - 0.06, z + 0.07, DIRT, bevel=0.0)
    # (a rota VEG_P2_ciprestes do sg_veg atravessa o terreiro em diagonal de (-76, -30) a (-40, -34): tudo ao sul dela)
    dummy(mb, -66.0, -36.2, z + 0.07, math.radians(-80.0))
    col_box("SG_PropDummy", (1.6, 1.6, 5.2), (-66.0, -36.2, z + 2.6))
    target(mb, -52.4, -37.0, z + 0.07, math.radians(-110.0))                 # face para leste (quem vem do eixo)
    col_box("SG_PropTarget", (3.2, 2.2, 4.4), (-52.4, -37.0, z + 2.2), (0, 0, math.radians(-110.0)))
    yr = -44.0 + 0.6 + 0.55
    arms_rack(mb, -62.0, yr, _ground(-62.0, yr, z), 0.0)
    col_box("SG_PropArms", (6.6, 1.3, 3.8), (-62.0, yr, z + 1.9))


# ------------------------------------------------------------------ 03.15 fins de rua + terraco norte
def signpost(mb, x, y, z, yaw):
    """poste de direcao: soco de pedra, poste de madeira, 2 tabuas em seta (uma para a vila, outra para a praca)"""
    F = Frame(x, y, z, yaw)
    _frustum(mb, F.p(0, 0, 0), 1.3, 1.3, 1.0, 1.0, 0.7, LEG_M, F.a, bottom=False)
    mb.box((0.36, 0.36, 5.4), F.p(0, 0, 3.3), F.r(), WOOD, 0.0)
    _frustum(mb, F.p(0, 0, 6.0), 0.5, 0.5, 0.05, 0.05, 0.4, WOOD, F.a, bottom=False)
    for zz, ang, ln in ((5.1, 0.0, 2.6), (4.25, math.radians(-62.0), 2.1)):
        Fb = Frame(x, y, z, yaw + ang)
        x0 = 0.2
        pts = [(x0, -0.32), (x0 + ln, -0.32), (x0 + ln + 0.45, 0.0), (x0 + ln, 0.32), (x0, 0.32)]
        CT._loft(mb, [[Fb.p(u, -0.07, zz + v) for u, v in pts], [Fb.p(u, 0.07, zz + v) for u, v in pts]], WMID)
    col_box("SG_PropSign", (1.0, 1.0, 6.0), F.p(0, 0, 3.0), F.r())


def stele(mb, x, y, z, yaw):
    """lapide da ordem (memoria discreta): plinto, estela de topo em arco, placa de ferro com o crescente"""
    F = Frame(x, y, z, yaw)
    _frustum(mb, F.p(0, 0, 0), 2.1, 1.0, 1.9, 0.86, 0.4, LEG_M, F.a, bottom=False)
    prof = [(-0.75, 0.38), (0.75, 0.38), (0.75, 2.2)] + [(0.75 * math.cos(math.radians(a)), 2.2 + 0.55 *
                                                          math.sin(math.radians(a))) for a in (30, 60, 90, 120, 150)] + [(-0.75, 2.2)]
    CT._loft(mb, [[F.p(u, -0.24, v) for u, v in prof], [F.p(u, 0.24, v) for u, v in prof]], SEAT_M, cap0="fan",
             cap1="fan")
    mb.box((0.9, 0.08, 0.62), F.p(0.0, 0.26, 1.75), F.r(), IRON, 0.0)                    # placa de ferro
    mb.box((1.62, 0.56, 0.12), F.p(0.0, 0.0, 1.16), F.r(), LEG_M, 0.0)                    # cinta


def waymark(mb, x, y, z, yaw):
    """marco de pedra no eixo do fim da rua (fecha a perspectiva): plinto, dado com cornija e placa de ferro voltada
    para a rua, fuste em tronco de piramide e piramidion (topo ~8)"""
    F = Frame(x, y, z, yaw)
    _frustum(mb, F.p(0, 0, 0), 2.5, 2.5, 2.2, 2.2, 0.55, LEG_M, F.a, bottom=False)
    mb.box((1.7, 1.7, 1.85), F.p(0, 0, 1.45), F.r(), LEG_M, 0.0)
    mb.box((2.05, 2.05, 0.26), F.p(0, 0, 2.5), F.r(), SEAT_M, 0.0)
    _frustum(mb, F.p(0, 0, 2.63), 1.2, 1.2, 0.74, 0.74, 4.6, LEG_M, F.a, bottom=False)
    _frustum(mb, F.p(0, 0, 7.23), 0.96, 0.96, 0.06, 0.06, 0.95, SEAT_M, F.a, bottom=False)
    mb.box((0.62, 0.95, 0.06), F.p(0.0, 0.88, 1.55), F.r(0, 0, math.pi / 2), IRON, 0.0)
    col_box("SG_PropWaymark", (2.5, 2.5, 7.6), F.p(0, 0, 3.8), F.r())


def street_ends(mb, rng):
    """03.15: cada rua acaba num lugar. Leste do P1: banco virado para a vista (costas para a rua) com a lanterna ao
    lado. Oeste do P2: MARCO de pedra no eixo (fecha a perspectiva da rua), banco virado para a cachoeira oeste ao
    norte dele e o poste de direcao de volta para a vila ao sul."""
    xb, yb = 155.2, -221.0
    bench(mb, xb, yb, _ground(xb, yb, P1), -math.pi / 2)
    waymark(mb, -176.2, -86.0, _ground(-176.2, -86.0, P2), -math.pi / 2)
    xb, yb = -173.4, -79.6
    bench(mb, xb, yb, _ground(xb, yb, P2), math.radians(25.0))
    signpost(mb, -172.4, -92.4, _ground(-172.4, -92.4, P2), 0.0)


def terrace(mb, rng):
    """terraco norte (pedido do G): banco de frente para a cachoeira do norte e a lapide da ordem ao lado"""
    xb, yb = -42.0, 371.0
    bench(mb, xb, yb, _ground(xb, yb, P3), math.radians(56.0))
    xs, ys = -35.2, 372.6
    stele(mb, xs, ys, _ground(xs, ys, P3), math.radians(-160.0))
    col_box("SG_PropStele", (2.2, 1.1, 2.8), (xs, ys, P3 + 1.4), (0, 0, math.radians(-160.0)))


# ------------------------------------------------------------------ beco oeste (pedido do J): lanternas nos nos
def alley_lamps(mm, mg):
    """lanternas do beco oeste (sg_court.west_alley): sobre o muro no fundo dos 2 nichos (s 36 e 227), par de bracos na
    estela da fonte de parede (s 96) e a lanterna pendurada no portico (s 150, a unica com luz). Devolve o vidro dela."""
    P = CT._Path(L.EXIT_ROUTE[1:])
    O = CT.ALLEY_W
    for sn in (36.0, 227.0):
        x0, y0, tx, ty = P.at(sn)
        cx, cy = P.pt(sn, O + 0.35)
        nx, ny = ty, -tx
        x, y = cx + nx * 4.95, cy + ny * 4.95
        zc = P3 + 2.88
        _lathe(mm, (x, y, zc), [(0.42, 0.0), (0.3, 0.16), (0.2, 0.62), (0.32, 0.72)], EM.L_IRON, 6, 0.0)
        EM.lantern_head(mm, mg, (x, y, zc + 0.72 + EM.LH_BASE * 0.9), math.atan2(-ny, -nx), 0.9)
    yaw = P.yaw(96.0)
    for e in (-1, 1):
        sw = 96.0 + e * 2.05
        a = P.pt(sw, O - 0.2)
        b = P.pt(sw, O - 1.25)
        z = P3 + 3.05
        mm.beam((a[0], a[1], z), (b[0], b[1], z), 0.14, 0.18, EM.L_IRON, 0.0)
        mm.beam((a[0], a[1], z - 0.95), (b[0] * 0.55 + a[0] * 0.45, b[1] * 0.55 + a[1] * 0.45, z - 0.05), 0.1, 0.1,
                EM.L_IRON, 0.0)
        _lathe(mm, (b[0], b[1], z + 0.02), [(0.32, 0.0), (0.32, 0.08)], EM.L_IRON, 6, 0.0)
        EM.lantern_head(mm, mg, (b[0], b[1], z + 0.1 + EM.LH_BASE * 0.78), yaw + math.pi / 2, 0.78)
    # portico: corrente do caibro do meio e lanterna pendurada (topo dela abaixo de P3 + 9,3)
    x, y = P.pt(150.0, 0.0)
    zt = P3 + 10.25
    zl = P3 + 7.0
    for k in range(4):
        za, zb_ = zt - k * 0.32, zt - (k + 1) * 0.32
        mm.box((0.1, 0.24 if k % 2 else 0.08, 0.36), (x, y, (za + zb_) / 2), (0, 0, P.yaw(150.0)), EM.L_IRON, 0.0)
    return EM.lantern_head(mm, mg, (x, y, zl + EM.LH_BASE), P.yaw(150.0), 1.0)


def build():
    rng = random.Random(3320)
    GLASS.clear()
    EXTRA_LIGHTS.clear()
    mb = MB("SG_Prop_Plaza", COLL, rng, detail="near")
    for n, x, y, z, lit, h, s in POSTS:
        if n.startswith(("Plaza", "P1P2Foot", "RuaP1")):
            GLASS[n] = tuple(lamp(mb, x, y, _ground(x, y, z), h, s))
    for a in BENCH_A:
        r = math.radians(a)
        x, y = _C[0] + BENCH_R * math.cos(r), _C[1] + BENCH_R * math.sin(r)
        bench(mb, x, y, _ground(x, y, P1 + PAVE), r + math.pi / 2)      # frente para a fonte
    # FINESSE 3C: as cenas das casas, os fins de rua e o terraco no MESMO objeto (mesma paleta)
    def _tris(m):
        return sum(len(f.verts) - 2 for f in m.bm.faces)
    t0 = _tris(mb)
    per = {"postes+bancos_praca": t0}
    for fn in (taverna, forge, apothecary, miner, cartographer, guard, arms_master, street_ends, terrace):
        fn(mb, rng)
        t1 = _tris(mb)
        per[fn.__name__] = t1 - t0
        t0 = t1
    print("PROPS tris por cena:", per)
    mb.finish()
    mr = MB("SG_Prop_NodeLamps", COLL, rng, detail="near")
    for n, x, y, z, lit, h, s in POSTS:
        if not n.startswith(("Plaza", "P1P2Foot", "RuaP1")):
            GLASS[n] = tuple(lamp(mr, x, y, _ground(x, y, z), h, s))
    tb = sum(len(f.verts) - 2 for f in mr.bm.faces)
    GLASS["BecoPortico"] = tuple(alley_lamps(mr, mr))
    print("PROPS tris lanternas do beco:", sum(len(f.verts) - 2 for f in mr.bm.faces) - tb)
    mr.finish()
    print("PROPS postes=%d bancos=%d acesos=%d cenas=7 casas + 2 fins de rua + terraco + beco (5 lanternas)" % (
        len(POSTS), len(BENCH_A) + 3, sum(1 for p in POSTS if p[4])))
