# op_kit2.py - KIT V2 de arquitetura da Ilha 5 (ONE PIECE / WANO - Flower Capital). Substitui o op_kit (reprovado
# pelo usuario em 10/10: "casas feias, mal projetadas", "pequenas estruturas mal modeladas", "postes feios",
# "sem vida por dentro"). Referencia: ref/ref_03_atmosfera_wano_anime.jpg (telhados escalonados coloridos em camadas,
# beirais profundos, madeira escura + reboco, varandas, densidade).
#
# O QUE MUDOU EM RELACAO AO op_kit (diagnostico: "caixa de reboco branco + telhado de chapa azul")
#   * TELHA DE VERDADE NA GEOMETRIA: a placa do telhado e ONDULADA (canal + capa: perfil de 3 pontos por modulo) -
#     no Roblox (SmoothPlastic, sem textura) a luz desenha as fiadas de kawara sozinha; perfil CONCAVO (caimento
#     0,4 no beiral -> ~1,05 na cumeeira) + cantos levantados; beiral GROSSO (telha 0,5 + testeira 0,6) com caibros
#     e misulas aparentes; cumeeira alta com onigawara.
#   * SILHUETA por tipo (6 tipos), varios niveis de telhado por casa (hisashi, saia mokoshi, chidori, torre),
#     empenas para a rua (tsumairi) misturadas com cumeeiras paralelas (hirairi): de cima le como a ref_03.
#   * PAREDE = ESTRUTURA DE MADEIRA ESCURA (soleira, pilares, nuki, nageshi, frechal) com PREENCHIMENTOS pequenos
#     (rodape de tabuas, reboco quente emoldurado, trelica koshi densa, mushiko, shoji, tabuado) - nunca um pano
#     branco grande.
#   * COR POR CONJUNTO (ROOF_SETS): azul vivo, verde-agua, vermelho, roxo, marinho, verde.
#   * INTERIOR REAL na loja (a) e na casa de cha (e): piso, balcao/mesas, prateleiras com mercadoria, lanternas de
#     papel acesas, parede de fundo, forro.
#
# ============================================================ CONVENCOES (as mesmas do op_kit)
#   F   fm_parts.Frame(ox, oy, oz, ang). Edificios e pecas: origem no CENTRO DA PLANTA, NO CHAO (z=0 = rua),
#       +y = FRENTE (rua), +x ao longo da frente. Fachadas (Ff): origem no meio da fachada, y=0 na face EXTERNA dos
#       pilares, +y para fora, z=0 no piso daquele andar.
#   mb  fm_lib.MB do chamador (varias casas no MESMO MB = 1 MeshPart por material). As placas de telha sao cascas
#       FECHADAS (o finish() recalcula normais): nada de face solta virada para baixo.
#   Escala: avatar 5. Porta >= 4,4 x 6,6; degrau <= 0,8; guarda-corpo ~3.
#   Z-fight: faces paralelas de materiais diferentes >= 0,12 (papel 0,2 atras da trelica; reboco 0,3 atras dos pilares).
#   Lotes encostados: W = largura do lote. sides=(esq, dir) diz se a lateral e EMPENA CEGA (encostada no vizinho:
#   parede simples) ou FACHADA (ponta de quadra). g_over (beiral lateral) passa do lote: os telhados vizinhos se
#   SOBREPOEM (alturas diferentes por tipo/seed) - e assim que a ref_03 le.
#
# ============================================================ API
# MATERIAIS: ROOF_SETS = cor por conjunto (PLANO_V2 3.2): RCOB Roof_OP_Cobalt | RTEAL Roof_OP_Teal | RVIO
#   Roof_OP_Violet | RREDV Roof_OP_RedV2 (+ RB marinho, RG verde). CURB/GUTTER = Stone_OP_Curb/Gutter. Os valores
#   do plano sao registrados aqui com setdefault se a V2-0 ainda nao os pos no op_lib (o op_lib sempre ganha).
#   Material novo no op_lib (1 linha, deste kit): Cloth_OP_Tatami. Roof_OP_Teal = valor do PLANO_V2.
# TIPOS (todos devolvem info = dict(kind, W, D, top_z, ridge_z, eave_z, glow=[pts mundo], doors=[pts], light_at)):
#   loja(mb, F, W=14, D=16, roof_m=RAZ, shop_side=1, tsuma=False, roof="kirizuma"|"irimoya", awning=False,
#        udatsu=True, sides=(False, False), lod=0, seed=0, light_name=None, noren="auto", h0=9, h1=7,
#        upper="mushiko"|"shoji"|"double", pent_m=None)        (a) machiya-loja 2 pisos: LOJA ABERTA COM INTERIOR,
#        porta com noren, koshi, hisashi em misulas, udatsu, sode-kanban, chochin de beiral; tsuma=True = empena p/ rua
#   sobrado(mb, F, W=16, D=16, roof_m=RTEAL, skirt_m=None, rail_m=WD|LAC, shop=False, sides=(True, True), lod, seed)
#        (b) 3 pisos: hisashi + VARANDA CORRIDA + SAIA MOKOSHI + 3o piso recuado com irimoya e chidori (4 camadas)
#   esquina(mb, F, W=16, D=16, roof_m=RREDV, tower_m=None, corner=1, lod, seed, light_name)
#        (c) esquina: lojas nas 2 ruas, hisashi que dobra a esquina (espigao), yosemune, TORRE-MIRANTE no canto
#        (varanda vermelha em misulas + hogyo com remate dourado). corner=+1/-1 = lado +x/-x e a rua lateral
#   kura(mb, F, W=10, D=14, roof_m=RB, tsuma=True, lod=0, h=12.5)  (d) armazem: soco alto, namako-kabe diagonal,
#        molduras, porta-cofre com molduras em degrau, janela alta, kirizuma pesado (telha 0,7, cumeeira de 3 fiadas)
#   chaya(mb, F, W=22, D=16, roof_m=RPUR, garden_side=1, lod=0, light_name=None, garden_w=7, sides=(False, False))
#        (e) casa de cha/estalagem: ENGAWA sob hisashi em pilares, KARAHAFU dourado na entrada, frente aberta com
#        INTERIOR DE TATAMI (mesas, zabuton, tokonoma, andon), 2o piso com varanda vermelha, irimoya, JARDIM
#        (cerca de bambu, muro tsuiji, pisantes, toro, pinheirinho)
#   fundo(mb, F, W=10, D=10, roof_m=RB, tsuma=False, lod=1, seed=0, sides=(False, False))
#        (f) casa pequena de fundo de quadra (barata: telha lod 1, sem caibros)
#   BUILD = {"loja": loja, ...}; build(mb, F, kind, **kw); footprint(kind, **kw) -> (W, D) das paredes
#   (os beirais passam ~2,6 na frente/fundos e g_over ~1,2 nas laterais: lotes geminados SOBREPOEM os telhados)
# TELHADOS (reusaveis)
#   roof2(mb, F, W, D, zw, kind="irimoya"|"kirizuma"|"yosemune"|"hogyo", m, ov=2.8, g_over=1.4, s0=0.4, s1=1.05,
#         lift=1.0, tv=0.5, dg=0.5, lod=0, back_lod=1, chidori=dict(x, w, y), gable_style="timber", gold=False,
#         courses=2, rafters=True, brackets=[x...], ends=(estilo -x, estilo +x), end_lod=None)
#         W x D = planta nas faces dos pilares; zw = topo do frechal (z local de F); cumeeira ao longo de x
#         (irimoya/yosemune giram sozinhos se D > W). ends (kirizuma): False | "plain" | "board" | "timber".
#         -> dict(zr, z_e, Xe, Ye, Hf(x, y), top, eave_z, Xg)
#   pent2(mb, Ff, L, depth, z_top, m, s=0.42, tv=0.38, lift=0.45, lod, xs=[x misulas/pilares], support="brackets"|
#         "posts"|"none", post_z, ends=(bool, bool), ylo=fn)    hisashi ondulado (Ff na face da parede, +y fora)
#   skirt2(mb, F, Wi, Di, dep, z_top, m, ...)    saia mokoshi de 4 aguas em volta de um piso recuado
#   tiles(mb, F, cols, ylo, Ye, H, m, tv, soffit, rows, coarse)   placa de telha ondulada (casca FECHADA) - nucleo
#   _wave(x0, x1, P=2.0, amp=0.3, lod)          perfil canal+capa (lod 0: 3 pts/modulo; 1: dente; 2: liso)
# PAREDES
#   wall2(mb, Ff, L, h, bays, plaster, lod, lit, head, noren, corners, upper) - bays = [tipo | (tipo, largura) |
#       dict(t=, w=, lit=, noren=, head=, rail=, upper_board=)]:
#       "plaster" rodape de tabuas + reboco emoldurado | "plain" so reboco (fundos) | "board" tabuado | "koshi"
#       trelica sobre rodape | "lattice" trelica alta (sengoshi) | "door" porta de correr com kumiko + noren |
#       "shop" vao de loja aberto com noren | "mushiko" barras de reboco | "shoji" janela de shoji (+ corrimao) |
#       "amado" tapume | "open" vao livre (engawa)
#   blind_wall(mb, Ff, L, h, m)  empena cega | plinth(mb, F, W, D, ph, steps) soco | _body(...) 1 andar, 4 faces
# PECAS PEQUENAS (tris medidos no relatorio; alvo <= 600)
#   lamp_andon(mb, F, light_name)   andon de poste baixo (4,6): pedestal de pedra, fuste, caixa de papel em kumiko
#   lamp_post(mb, F, light_name)    poste de madeira com chochin sob telhadinho (braco com mao-francesa para +x)
#   eave_lantern(mb, Ff, x, z, light_name)   chochin de beiral (braco de parede); chochin2 / hanging_lantern
#   toro2(mb, F, light_name, s)     toro de pedra kasuga (camara com janelas recortadas, kasa com cantos levantados)
#   well2(mb, F, roof_m)            poco: anel de pedra, tampa, esteios, sarilho, corda, balde, telhadinho ondulado
#   bridge2(mb, F, span=10, width=6, rise=1.4, bank_z=0, water_z, bed_z)   ponte em ARCO que vence o vao: encontros
#                                   de pedra fora do vao, F no meio do canal no nivel das margens, vao ao longo de x
#   stall2(mb, F, light_name)       banca de rua (+y = freguesia) | goods_pile(mb, F, "barrels"|"crates")
#   bamboo_fence(mb, F, L, h) | tsuiji(mb, F, L, h, roof_m) | nobori2(mb, F, h, cloth, band)
#   street2(mb, F, L, road_w=18, walk_w=4)   rua ao longo de x: leito assentado (laje 3 x 1,5, junta 0,08), sarjeta
#                                   0,8 a -0,15, meio-fio 0,3 x 0,5 (topo +0,35), calcadas -> devolve z da calcada
# ORCAMENTO: os tipos foram medidos com e sem op_kit.cull_hidden (o chamador deve rodar cull_hidden no MB da quadra).
# ESTUDIO (folhas de gate; fora do jogo):
#   blender -b --factory-startup --python op_kit2.py -- <pasta_saida> [filtro ...] [--roblox] [--no-render]
import math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import op_lib as DL
import op_kit as K
import bpy, bmesh
from mathutils import Vector
from op_lib import MB, Frame, light, col_box, fm_lib
from op_kit import (sub, bx, bb, loft, ext, lathe, lathe_y, strip, sweep, beam, even, _h01, chochin, hip_cap,
                    onigawara, ridge, giboshi, red_rail, rock_base, HIPP, cull_hidden, _gegyo, _gable_timber, _hafu)

# ------------------------------------------------------------------ materiais (OPMATS do op_lib)
WD, WM, LAC, GOLD, IRON = "Wood_OP_Dark", "Wood_OP_Mid", "Wood_OP_Lacquer", "Metal_OP_Gold", "Metal_OP_Iron"
PL, PLW, PLS = "Plaster_OP", "Plaster_OP_Warm", "Plaster_OP_Shop"
RB, RG, RRED, RR = "Roof_OP_Blue", "Roof_OP_Green", "Roof_OP_Red", "Roof_OP_Ridge"
RCOB, RTEAL, RVIO, RREDV = "Roof_OP_Cobalt", "Roof_OP_Teal", "Roof_OP_Violet", "Roof_OP_RedV2"   # PLANO_V2 3.2
RAZ, RPUR = RCOB, RVIO                    # nomes antigos do kit2 (compat)
CURB, GUTTER, STC = "Stone_OP_Curb", "Stone_OP_Gutter", "Stone_OP_Court"
# os materiais do PLANO_V2 sao acrescentados no op_lib pela V2-0; se este kit rodar antes, registra o MESMO valor
# aqui (setdefault: o op_lib sempre ganha). Valores de meio-fio/sarjeta sao provisorios ate a V2-0.
for _k, _v in {"Roof_OP_Cobalt": (fm_lib.S(60, 90, 168), 0.7, 0.0, 0, None, 0.05),
               "Roof_OP_Teal": (fm_lib.S(62, 148, 138), 0.7, 0.0, 0, None, 0.05),
               "Roof_OP_Violet": (fm_lib.S(104, 84, 152), 0.7, 0.0, 0, None, 0.05),
               "Roof_OP_RedV2": (fm_lib.S(172, 62, 52), 0.7, 0.0, 0, None, 0.05),
               "Stone_OP_Curb": (fm_lib.S(150, 144, 134), 0.85, 0.0, 0, None, 0.05),
               "Stone_OP_Gutter": (fm_lib.S(112, 108, 102), 0.85, 0.0, 0, None, 0.04)}.items():
    fm_lib.MATS.setdefault(_k, _v)
ST, STD, STP = "Stone_OP", "Stone_OP_Dark", "Stone_OP_Path"
LIT, LGLOW = "Window_OP_Warm", "Glass_OP_Lantern"
INDIGO, CRED, CWHITE, CBLACK, STRAW = "Cloth_OP_Indigo", "Cloth_OP_Red", "Cloth_OP_White", "Cloth_OP_Black", \
    "Cloth_OP_Straw"
TATAMI = "Cloth_OP_Tatami"                                                 # KIT2 (op_lib)
LEAF, BARK = "Leaf_OP_Pine", "Bark_OP"
WARM = (1.0, 0.64, 0.36)
ROOF_SETS = {"cobalto": RCOB, "verde-agua": RTEAL, "vermelho": RREDV, "roxo": RVIO, "marinho": RB, "verde": RG}
HB = ("B",)                     # V2-3: fachada de tras escondida (fundos encostados)
POST, CPOST = 0.7, 0.9          # pilar intermediario / de canto
SILL_H, PLATE_H = 0.45, 0.65    # soleira (dodai) e frechal (keta)


# ================================================================== TELHA ONDULADA (nucleo do kit)
def _wave(x0, x1, P=2.0, amp=0.3, lod=0):
    """amostras (x, altura) do perfil de telha ao longo de x: lod 0 = canal largo + capa (3 pontos por modulo),
    lod 1 = dente (2 pontos, modulo 1,4x), lod 2 = liso. Pontas sempre em 0."""
    if x1 - x0 < 0.05:
        return [(x0, 0.0), (x1, 0.0)]
    if lod >= 2 or amp <= 0.0:
        n = max(1, int(math.ceil((x1 - x0) / 4.0)))
        return [(x0 + (x1 - x0) * i / n, 0.0) for i in range(n + 1)]
    if lod == 1:
        P, fr = P * 1.4, ((0.0, 0.0), (0.6, amp))
    else:
        fr = ((0.0, 0.0), (0.55, 0.0), (0.78, amp))
    n = max(1, int(round((x1 - x0) / P)))
    Pp = (x1 - x0) / n
    out = [(x0 + Pp * (j + f), h) for j in range(n) for f, h in fr]
    out.append((x1, 0.0))
    return out


ROWS = (0.0, 0.2, 0.5, 1.0)


def tiles(mb, F, cols, ylo, Ye, H, m, tv=0.5, soffit=WD, rows=ROWS, coarse=3.6):
    """PLACA DE TELHA ondulada (casca FECHADA: o finish() recalcula normais sem virar nada): colunas
    cols=[(x, onda)] ao longo do beiral, do beiral (y=Ye) ate y=ylo(x) (cumeeira/espigao/parede). Topo = H(x, y) +
    onda (material m); fundo LISO = H - tv (forro 'soffit') so nas colunas de controle (a cada ~coarse e nas quebras de
    ylo); borda do beiral e borda de cima = n-gonos verticais planos (pontas das telhas). As fileiras sao fracoes do
    comprimento de cada coluna: a borda de cima segue exatamente a linha do espigao."""
    bm = mb.bm
    n, r = len(cols), len(rows)
    yl = [min(ylo(x), Ye - 0.05) for x, h in cols]
    # colunas de controle do fundo: pontas, quebras de ylo e a cada 'coarse'
    idx = [0]
    for i in range(1, n - 1):
        x0, x1, x2 = cols[i - 1][0], cols[i][0], cols[i + 1][0]
        s0 = (yl[i] - yl[i - 1]) / max(1e-6, x1 - x0)
        s1 = (yl[i + 1] - yl[i]) / max(1e-6, x2 - x1)
        if abs(s1 - s0) > 1e-3 or x1 - cols[idx[-1]][0] >= coarse - 1e-6:
            if x2 - x1 > 1e-6 and x1 - cols[idx[-1]][0] > 0.4:
                idx.append(i)
    if n - 1 not in idx:
        if len(idx) > 1 and cols[n - 1][0] - cols[idx[-1]][0] < 0.4:
            idx[-1] = n - 1
        else:
            idx.append(n - 1)
    T, Bt = [], {}
    for i, (x, h) in enumerate(cols):
        ys = [Ye - (Ye - yl[i]) * f for f in rows]
        T.append([bm.verts.new(F.p(x, y, H(x, y) + h)) for y in ys])
    for i in idx:
        x = cols[i][0]
        ys = [Ye - (Ye - yl[i]) * f for f in rows]
        Bt[i] = [bm.verts.new(F.p(x, y, H(x, y) - tv)) for y in ys]
    top, bot = [], []

    def nf(vs, lst):
        try:
            lst.append(bm.faces.new(vs))
        except ValueError:
            pass
    for i in range(n - 1):
        for k in range(r - 1):
            nf((T[i][k], T[i + 1][k], T[i + 1][k + 1], T[i][k + 1]), top)
    for a, b in zip(idx, idx[1:]):
        for k in range(r - 1):
            nf((Bt[a][k], Bt[a][k + 1], Bt[b][k + 1], Bt[b][k]), bot)
        nf([T[i][0] for i in range(a, b + 1)] + [Bt[b][0], Bt[a][0]], top)              # pontas das telhas
        nf([T[i][-1] for i in range(b, a - 1, -1)] + [Bt[a][-1], Bt[b][-1]], top)        # borda de cima
    for j in (0, n - 1):
        for k in range(r - 1):
            nf((T[j][k], T[j][k + 1], Bt[j][k + 1], Bt[j][k]), top)
    bmesh.ops.recalc_face_normals(bm, faces=top + bot)
    mb._post([v for c in T for v in c] + [v for c in Bt.values() for v in c], m, None, 0, 1)
    mi = mb._mi_for(soffit)
    for f in bot:
        if f.is_valid:
            f.material_index = mi


def bracket2(mb, F, x, y0, L, ztop, w=0.44, h=1.3, m=WD, block=True):
    """MISULA em balanco (de y0 para +y, comprimento L), topo em ztop; perfil recortado (degrau + curva) e bloco
    (masu) na ponta. Extrudada em x (largura w)"""
    poly = [(y0, ztop), (y0 + L, ztop), (y0 + L, ztop - 0.32), (y0 + L * 0.72, ztop - 0.42),
            (y0 + L * 0.42, ztop - h * 0.72), (y0, ztop - h)]
    ext(mb, F, poly, "x", x - w / 2, x + w / 2, m)
    if block:
        bb(mb, F, x - w / 2 - 0.08, x + w / 2 + 0.08, y0 + L - 0.62, y0 + L + 0.06, ztop, ztop + 0.3, m)


HIPP4 = [(-0.62, -0.2), (-0.4, 0.46), (0.4, 0.46), (0.62, -0.2)]


def _hipcap(mb, F, pts, s=1.0, tip_oni=False):
    sweep(mb, F, pts, [(a * 0.9 * s, b * 0.9 * s) for a, b in HIPP4], RR)
    if tip_oni:
        tx, ty, tz = pts[0]
        ang = math.atan2(pts[1][1] - ty, pts[1][0] - tx) + math.pi
        onigawara(mb, sub(F, tx, ty, 0.0, ang), -0.1, tz - 0.1, 1, 0.42 * s, False)


BIG = 1.0e6                       # V2-3: "sem corte" nos limites de lote (clip)


def party_clip(W, sides, D=None, back=None, lim=None):
    """V2-3 (zero interpenetracao): limites do lote para os cortes do kit - lado ENCOSTADO (sides[i] False) corta tudo
    na divisa (+-W/2); lado exposto so corta em lim[i] (meia distancia ate um predio vizinho proximo; padrao: nao
    corta). back = limite do fundo (distancia do centro) se houver vizinho atras.
    -> (x-, x+, y-, y+) no referencial do edificio (+y = frente)"""
    lim = lim or (BIG, BIG)
    return (lim[0] if sides[0] else W / 2.0, lim[1] if sides[1] else W / 2.0, BIG if back is None else back, BIG)


def rot_clip(c):
    """clip (x-, x+, y-, y+) de F -> clip do referencial sub(F, ang=pi/2) (x' = F.y, y' = -F.x)"""
    if c is None:
        return None
    return (c[2], c[3], c[1], c[0])


# V3-cut (orcamento 625k): pontos das TESTEIRAS (faixas sob a borda do beiral) - lod 0 como era; lod >= 1 com menos
# trechos (o sori so levanta perto dos cantos: erro < 0,06 na curva, sempre dentro da placa de telha de 0,5)
STRIP_T0 = (0.0, 0.06, 0.2, 0.4, 0.6, 0.8, 0.94, 1.0)
STRIP_T1 = (0.0, 0.15, 0.35, 0.65, 0.85, 1.0)
STRIP_T2 = (0.0, 0.15, 0.5, 0.85, 1.0)
GABLE_BOARD_STEP = {0: 0.8, 1: 0.8, 2: 1.1, 3: 1.5}   # V3-cut: tabuas da empena (kitsure) nas casas lod 2/3
# V3-cut LOD 3 = casa LONGE das rotas (frente a > 25 de qualquer rota do jogo; op_capital decide): a mesma casa do lod 2
# com a telha ondulada no modulo 1,3x (mesma onda, menos colunas), hisashi numa faixa so, tabeiras com 5 pontos,
# kumiko/trelica/mushiko mais abertos e tabuas da empena a 1,5 - silhueta, cores e camadas iguais
LOD3_P = 1.3
BACK_P = 1.0      # V3-cut: o op_capital poe LOD3_P aqui enquanto monta uma casa cuja agua de TRAS da para o fundo de
#                   outra fileira (patio entre fileiras: so se ve de cima/de longe) e volta a 1.0 depois


def _gable_wood(mb, F, x_in, x_out, zb, top, ymax, style, lod):
    """madeiramento da empena: 'timber' = op_kit._gable_timber; 'board' = tabuas verticais com o passo do lod
    (V3-cut: lod 2 = passo 1,1 em vez de 0,8 - mesma leitura de tabuado, 30% menos pecas)"""
    if style != "board":
        return _gable_timber(mb, F, x_in, x_out, zb, top, ymax, style)
    zt0 = zb + 0.25
    for y in even(-ymax + 0.2, ymax - 0.2, GABLE_BOARD_STEP.get(min(3, lod), 0.8)):
        t = top(y) - 0.04
        if t > zt0 + 0.4:
            bb(mb, F, x_in, x_out, y - 0.09, y + 0.09, zt0, t, WD)


def _ridge2(mb, F, x0, x1, zr, pitch, w=2.2, oni=True, s=1.0, gold=False, courses=3, oni_ends=(True, True), lod=0):
    """cumeeira: lod 0 = op_kit.ridge; V3-cut lod >= 1 = a mesma cumeeira (tenda + fiadas + capa) com a capa redonda
    de 6 lados e onigawara com o disco de 6 lados (de 4 a 30 studs de altura a diferenca nao aparece)"""
    if lod == 0:
        return ridge(mb, F, x0, x1, zr, pitch, w, oni, s, gold, courses, oni_ends)
    hw = w / 2
    poly = [(-hw, zr - pitch * hw - 0.05), (0.0, zr - 0.05), (hw, zr - pitch * hw - 0.05), (hw, zr + 0.32 * s),
            (-hw, zr + 0.32 * s)]
    ext(mb, F, poly, "x", x0, x1, RR)
    z = zr + 0.28 * s
    for k in range(courses):
        f = 0.84 - 0.14 * k
        bb(mb, F, x0 + 0.12 + 0.1 * k, x1 - 0.12 - 0.1 * k, -f * hw, f * hw, z, z + 0.36 * s, RR)
        z += 0.32 * s
    mb.rod(F.p(x0 + 0.3, 0, z + 0.14 * s), F.p(x1 - 0.3, 0, z + 0.14 * s), 0.36 * hw, RR, 6)
    if oni:
        so = s * 0.74
        for x, sx, on in ((x0, -1, oni_ends[0]), (x1, 1, oni_ends[1])):
            if not on:
                continue
            opoly = [(-1.3, -0.8), (1.3, -0.8), (1.38, 0.5), (1.1, 1.42), (0.66, 2.02), (0.0, 2.3), (-0.66, 2.02),
                     (-1.1, 1.42), (-1.38, 0.5)]
            ext(mb, F, [(u * so, zr + v * so) for u, v in opoly], "x", x - 0.12 * sx, x + 0.44 * sx * so, RR)
            mb.rod(F.p(x + 0.3 * sx * so, 0, zr + 0.78 * so), F.p(x + 0.6 * sx * so, 0, zr + 0.78 * so), 0.52 * so,
                   GOLD if gold else RR, 6)
            for k in (-1, 1):
                bx(mb, F, x + 0.1 * sx * so, k * 1.1 * so, zr + 2.12 * so, 0.42 * so, 0.34 * so, 1.0 * so, RR, 0.0,
                   rx=-k * 0.5)
    return z + 0.5 * s


def roof2(mb, F, W, D, zw, kind="irimoya", m=RAZ, ov=2.8, g_over=1.4, s0=0.4, s1=1.05, lift=1.0, tv=0.5,
          dg=0.5, lod=0, back_lod=1, chidori=None, gable_m=PLW, gable_style="timber", gold=False, courses=2,
          rafters=True, brackets=None, amp=0.3, P=2.0, ends=(True, True), oni=True, hafu_m=WD, ridge_w=2.2,
          end_lod=None, clip=None, back_p=None):
    """TELHADO V2 (cumeeira ao longo de x). W x D = planta nas faces dos pilares, zw = topo do frechal.
    kind: 'kirizuma' 2 aguas (empenas em x=+-W/2, aba lateral g_over) | 'irimoya' 4 aguas embaixo + empena em cima
    (dg = fracao do caimento ate a base da empena) | 'yosemune' 4 aguas | 'hogyo' piramide (W=D) com remate.
    Perfil concavo: caimento s0 no beiral -> s1 na cumeeira; lift levanta os cantos (sori). ends = (empena -x, +x)
    desenhadas (kirizuma encostado no vizinho: False no lado cego).
    V2-3 clip = (x-, x+, y-, y+): NADA do telhado passa destas distancias do centro (divisa do lote encostado no
    vizinho): as aguas sao CORTADAS na divisa (a superficie continua a mesma, so termina ali), testeiras/caibros/
    espigoes/onigawara do lado cortado somem e a empena cortada vira empena de divisa (reboco ate a telha, sem
    tabeira) - assim o telhado nunca entra na casa vizinha (op_capital mede: zero interseccao)."""
    if kind in ("irimoya", "yosemune") and W < D - 1e-6:
        return roof2(mb, sub(F, ang=math.pi / 2), D, W, zw, kind, m, ov, g_over, s0, s1, lift, tv, dg, lod, back_lod,
                     None, gable_m, gable_style, gold, courses, rafters, None, amp, P, ends, oni, hafu_m, ridge_w,
                     end_lod, rot_clip(clip), back_p=1.0)
    end_lod = lod if end_lod is None else end_lod
    bp = BACK_P if back_p is None else back_p   # V3-cut: modulo da onda na agua de TRAS (ik 1)
    if lod >= 3:
        P = P * LOD3_P                    # V3-cut lod 3: mesma onda, modulo 1,3x
    cxn, cxp, cyn, cyp = clip or (BIG, BIG, BIG, BIG)
    Xw, Yw = W / 2 + 0.12, D / 2 + 0.12
    Ye = Yw + ov
    hipish = kind in ("irimoya", "yosemune", "hogyo")
    Xe = Xw + (ov if hipish else g_over)
    if kind == "hogyo":
        Xe = Ye = max(Xe, Ye)
    dr = Ye

    def zp(d):
        return s0 * d + 0.5 * (s1 - s0) * d * d / dr
    z_e = zw + tv + 0.3 - zp(ov)

    def lf(x, y):
        return lift * min(1.0, abs(x) / Xe) ** 3 * min(1.0, abs(y) / Ye) ** 3

    def Hf(x, y):
        return z_e + zp(Ye - abs(y)) + lf(x, y)

    def He(u, v):                    # plano de topo no referencial Fe (v = distancia do centro ao longo de x)
        return z_e + zp(Xe - abs(v)) + lf(v, u)
    zr = z_e + zp(Ye)
    dgv = dg * Ye
    Xg = Xe - dgv
    go = g_over
    Fs = (F, sub(F, ang=math.pi))
    Fe = (sub(F, ang=-math.pi / 2), sub(F, ang=math.pi / 2))     # +v = +x / +v = -x
    hip_y = lambda x: Ye - (Xe - abs(x))
    # limites por agua (referencial local de cada agua): (x esquerda, x direita, beiral)
    lim_s = ((-cxn, cxp, cyp), (-cxp, cxn, cyn))
    lim_e = ((-cyp, cyn, cxp), (-cyn, cyp, cxn))

    def rng(a, b, xa, xb):
        a, b = max(a, xa), min(b, xb)
        return (a, b) if b - a > 0.3 else None

    def hip_ok(a, b, ye, hipf):
        """recorta [a, b] onde a linha do espigao (hipf) fica ABAIXO do beiral cortado ye (sobra telha)"""
        if ye >= Ye - 1e-6:
            return (a, b)
        lim = Xe - (Ye - ye) - 0.05            # |x| < lim
        return rng(a, b, -lim, lim)
    P0 = P
    for ik, Fk in enumerate(Fs):
        lk = min(1, lod if ik == 0 else max(lod, back_lod))      # V2-3: telha SEMPRE ondulada (lod 2 so nas paredes)
        P = P0 * (bp if ik == 1 else 1.0)
        xa, xb, cye = lim_s[ik]
        ye = min(Ye, cye)
        cut_e = ye < Ye - 1e-6
        RW = ROWS if lk == 0 else (0.0, 0.35, 1.0)               # V2-3: lod >= 1 = 2 faixas de telha por agua
        if kind == "kirizuma":
            r_ = rng(-Xe, Xe, xa, xb)
            if r_:
                tiles(mb, Fk, _wave(r_[0], r_[1], P, amp, lk), lambda x: 0.0, ye, Hf, m, tv, rows=RW)
        elif kind == "irimoya":
            r_ = rng(-Xg, Xg, xa, xb)
            if r_:
                tiles(mb, Fk, _wave(r_[0], r_[1], P, amp, lk), lambda x: 0.0, ye, Hf, m, tv, rows=RW)
            for s in (-1, 1):
                a, b = sorted((s * Xg, s * Xe))
                r_ = rng(a, b, xa, xb)
                r_ = r_ and hip_ok(r_[0], r_[1], ye, hip_y)
                if r_:
                    tiles(mb, Fk, _wave(r_[0], r_[1], P, amp, lk), lambda x: hip_y(x), ye, Hf, m, tv,
                          rows=(0.0, 0.3, 1.0))
                a, b = sorted((s * Xg, s * (Xg + go)))
                r_ = rng(a, b, xa, xb)
                if r_ and ye > 0.6:
                    tiles(mb, Fk, _wave(r_[0], r_[1], P, amp, max(lk, 1)), lambda x: 0.0, min(Ye - dgv, ye), Hf, m,
                          tv, rows=(0.0, 0.5, 1.0))
        else:
            r_ = rng(-Xe, Xe, xa, xb)
            r_ = r_ and hip_ok(r_[0], r_[1], ye, hip_y)
            if r_:
                tiles(mb, Fk, _wave(r_[0], r_[1], P, amp, lk), lambda x: max(0.0, hip_y(x)), ye, Hf, m, tv, rows=RW)
        if cut_e:
            continue                  # beiral cortado na divisa: sem testeira, caibros nem rincoes
        # testeira (kayaoi) grossa sob a borda do beiral
        xm = Xe - (0.35 if hipish else 0.2)
        r_ = rng(-xm, xm, xa + 0.05, xb - 0.05)
        if r_:
            P_ = [(r_[0] + (r_[1] - r_[0]) * t, Ye - 0.32) for t in (STRIP_T0 if lk == 0 else STRIP_T1)]
            strip(mb, Fk, [(x, y, Hf(x, y) - tv) for x, y in P_], (0, 1, 0), -0.17, 0.17, -0.62, 0.04, WD)
        if rafters and lk == 0:
            for x in even(-Xw + 0.5, Xw - 0.5, 1.25):
                y0 = Yw - 0.3
                if hipish and abs(x) > Xw - 0.9:
                    continue
                if x - 0.15 < xa or x + 0.15 > xb:
                    continue
                beam(mb, Fk, (x, y0, Hf(x, y0) - tv - 0.16), (x, Ye - 0.5, Hf(x, Ye - 0.5) - tv - 0.16), 0.24, 0.28, WD)
            if brackets:
                yp = Yw + 1.05
                zp_ = min(Hf(x, yp) for x in (-Xw, 0.0, Xw)) - tv - 0.32
                bb(mb, Fk, max(-Xw - 0.4, xa), min(Xw + 0.4, xb), yp - 0.26, yp + 0.26, zp_ - 0.5, zp_, WD)
                for x in brackets:
                    xx = x
                    if xa + 0.3 < xx < xb - 0.3:
                        bracket2(mb, Fk, xx, Yw - 0.6, 1.95, zp_ - 0.5, 0.44, 1.4, WD, False)
        if hipish:
            for sy in (1, -1):        # rincao (sumigi) sob o canto
                if sy > 0 and (Xe + 0.4 > xb):
                    continue
                if sy < 0 and (-Xe - 0.4 < xa):
                    continue
                beam(mb, Fk, (sy * (Xw - 0.7), Yw - 0.7, zw - 0.25),
                     (sy * (Xe + 0.12), Ye + 0.12, Hf(Xe, Ye) - tv - 0.3), 0.55, 0.6, WD)
    P = P0
    # planos de topo (4 aguas)
    if hipish:
        for ie, Fk in enumerate(Fe):
            ua, ub, cxe = lim_e[ie]
            xe_ = min(Xe, cxe)
            cut = xe_ < Xe - 1e-6
            if kind == "irimoya":
                ylo_e = lambda u: max(Xg, Xe - (Ye - abs(u)))
                if Xg > xe_ - 0.4:
                    continue
            else:
                ylo_e = lambda u: max(0.0, Xe - (Ye - abs(u)))
            r_ = rng(-Ye, Ye, ua, ub)
            if r_ and cut:
                lim = Ye - (Xe - xe_) - 0.05
                r_ = rng(r_[0], r_[1], -lim, lim)
            if r_:
                tiles(mb, Fk, _wave(r_[0], r_[1], P, amp, 1), ylo_e, xe_, He, m, tv, rows=(0.0, 0.3, 1.0))
            if cut:
                continue
            um = Ye - 0.35
            r_ = rng(-um, um, ua + 0.05, ub - 0.05)
            if r_:
                P_ = [(r_[0] + (r_[1] - r_[0]) * t, Xe - 0.32) for t in ((0.0, 0.1, 0.35, 0.65, 0.9, 1.0) if lod == 0 else STRIP_T2)]
                strip(mb, Fk, [(u, v, He(u, v) - tv) for u, v in P_], (0, 1, 0), -0.17, 0.17, -0.62, 0.04, WD)
        # capas de espigao (da ponta levantada ate a cumeeira / base da empena), recortadas pela divisa
        tend = dgv if kind == "irimoya" else Ye
        for sx in (1, -1):
            for sy in (1, -1):
                cx_ = cxp if sx > 0 else cxn
                cy_ = cyp if sy > 0 else cyn
                t0 = max(0.0, Xe - cx_ + 0.75, Ye - cy_ + 0.75) if (cx_ < BIG or cy_ < BIG) else 0.0
                if t0 >= tend - 0.3:
                    continue
                pts = [] if t0 > 0 else [(sx * (Xe + 0.55), sy * (Ye + 0.55), Hf(Xe, Ye) + 0.78)]
                for f in ((0.0, 0.12, 0.35, 0.65, 1.0) if lod == 0 else (0.0, 0.2, 0.5, 1.0)):   # V3-cut: lod >= 1 = 3 trechos
                    t = t0 + (tend - t0) * f
                    x, y = sx * (Xe - t), sy * (Ye - t)
                    pts.append((x, y, Hf(x, y) + 0.3))
                _hipcap(mb, F, pts, 1.0, oni and lod == 0 and sy > 0 and t0 == 0)
    # empenas
    cut_x = (cxn < Xe - 1e-6, cxp < Xe - 1e-6)
    if kind == "kirizuma":
        for ie, (Fx, st) in enumerate(((sub(F, ang=math.pi), ends[0]), (F, ends[1]))):
            c_ = (cxn, cxp)[ie]
            if cut_x[ie]:                 # EMPENA DE DIVISA: reboco ate a telha, rente a divisa (sem tabeira)
                xc = min(c_, Xw) - 0.02
                top = lambda y: Hf(xc, y) - tv - 0.05
                ymax = D / 2
                poly = [(-ymax, zw - 0.1), (ymax, zw - 0.1)] + [(y, top(y)) for y in (ymax, ymax * 0.5, 0.0, -ymax * 0.5,
                                                                                        -ymax)]
                ext(mb, Fx, poly, "x", xc - 0.45, xc, gable_m)
                continue
            if not st:
                continue
            st = gable_style if st is True else st
            top = lambda y: Hf(Xw, y) - tv - 0.05
            ymax = D / 2
            poly = [(-ymax, zw - 0.1), (ymax, zw - 0.1)] + [(y, top(y)) for y in (ymax, ymax * 0.5, 0.0, -ymax * 0.5, -ymax)]
            ext(mb, Fx, poly, "x", Xw - 0.75, Xw - 0.3, gable_m)
            if st in ("timber", "board"):
                _gable_wood(mb, Fx, Xw - 0.32, Xw - 0.14, zw - 0.25, top, ymax, st if end_lod == 0 else "board", end_lod)
            xh = Xe + 0.04
            ylo_, yhi_ = (-min(Ye, cyp), min(Ye, cyn)) if ie == 0 else (-min(Ye, cyn), min(Ye, cyp))
            hys = sorted(set(round(min(max(y, ylo_ + 0.05), yhi_ - 0.05), 4) for y in
                             ((Ye - 0.05, Ye * 0.6, Yw * 0.5, 0.0, -Yw * 0.5, -Ye * 0.6, -Ye + 0.05) if end_lod < 3
                              else (Ye - 0.05, Ye * 0.5, 0.0, -Ye * 0.5, -Ye + 0.05))), reverse=True)
            _hafu(mb, Fx, xh, hys, Hf, tv, 0.95, hafu_m, 0.22)
            if end_lod == 0:
                _gegyo(mb, Fx, xh, Hf(xh, 0.0) - tv - 0.95, 1, hafu_m, 1.0, gold)
            for y in (0.0, Yw * 0.55, -Yw * 0.55):          # tercas (moya) aparentes
                zt = Hf(Xw, y) - tv + 0.02
                bb(mb, Fx, Xw - 0.3, xh - 0.25, y - 0.28, y + 0.28, zt - 0.7, zt, WD)
    elif kind == "irimoya":
        for ie, Fx in enumerate((F, sub(F, ang=math.pi))):
            c_ = (cxp, cxn)[ie]
            zb = z_e + zp(dgv)
            yb = Ye - dgv
            if Xg + 0.32 > c_:
                continue
            bb(mb, Fx, Xg - 0.75, Xg + 0.32, -yb + 0.3, yb - 0.3, zb - 0.15, zb + 0.32, RR)       # kirioto (base)
            top = lambda y: Hf(Xg, y) - tv - 0.06
            y1 = yb - 0.3
            ys = [y1, y1 * 0.5, 0.0, -y1 * 0.5, -y1]
            poly = [(-y1, zb + 0.2), (y1, zb + 0.2)] + [(y, top(y)) for y in ys]
            ext(mb, Fx, poly, "x", Xg - 0.75, Xg - 0.5, gable_m)
            _gable_wood(mb, Fx, Xg - 0.52, Xg - 0.34, zb + 0.1, top, y1, gable_style if end_lod == 0 else "board", end_lod)
            xh = Xg + go + 0.04
            if xh + 0.5 > c_:
                continue
            _hafu(mb, Fx, xh, [yb, yb * 0.5, 0.0, -yb * 0.5, -yb], Hf, tv, 0.85, hafu_m, 0.22)
            if end_lod == 0:
                _gegyo(mb, Fx, xh, Hf(xh, 0.0) - tv - 0.85, 1, hafu_m, 1.0, gold)
            for y in (0.0, yb * 0.5, -yb * 0.5):
                zt = Hf(Xg, y) - tv + 0.02
                bb(mb, Fx, Xg - 0.5, xh - 0.25, y - 0.28, y + 0.28, zt - 0.7, zt, WD)
    if chidori and kind in ("irimoya", "yosemune", "kirizuma") and cyp >= Ye:
        xc_, wc_ = chidori.get("x", 0.0), chidori.get("w", W * 0.42)
        if -cxn + 0.5 < xc_ - wc_ / 2 - 1.0 and xc_ + wc_ / 2 + 1.0 < cxp - 0.5:
            _chidori(mb, F, Hf, tv, xc_, wc_, Yw + chidori.get("y", 0.4), m, zr, gable_m, gold, lod, P, amp)
    # cumeeira (recortada na divisa: sem onigawara do lado cortado)

    def rlim(x0, x1, pad=0.0):
        a = max(x0, -cxn + 0.05)
        b = min(x1, cxp - 0.05)
        return a, b, (x0 >= -cxn + 0.05 + pad, x1 <= cxp - 0.05 - pad)
    if kind == "kirizuma":
        a, b, oe = rlim(-(Xe + 0.2), Xe + 0.2, 0.9)
        rtop = _ridge2(mb, F, a, b, zr + 0.14, s1, ridge_w, oni, 1.0, gold, courses if lod == 0 else 1, oe, lod)
    elif kind == "irimoya":
        a, b, oe = rlim(-(Xg + go + 0.2), Xg + go + 0.2, 0.9)
        rtop = _ridge2(mb, F, a, b, zr + 0.14, s1, ridge_w, oni, 1.0, gold, courses if lod == 0 else 1, oe, lod)
    elif Xe - Ye > 0.6:
        a, b, oe = rlim(-(Xe - Ye + 0.3), Xe - Ye + 0.3, 0.9)
        rtop = _ridge2(mb, F, a, b, zr + 0.14, s1, ridge_w, oni, 1.0, gold, courses, oe, lod)
    else:
        lathe(mb, F, (0, 0, zr - 0.3), [(1.0, 0.0), (1.05, 0.45), (0.55, 0.8), (0.7, 1.2), (0.5, 1.45), (0.62, 1.85),
                                        (0.3, 2.5), (0.05, 3.2)], 8, GOLD if gold else RR)
        rtop = zr + 2.9
    return dict(zr=zr, z_e=z_e, Xe=Xe, Ye=Ye, Hf=Hf, top=rtop + 2.0, eave_z=Hf(0.0, Ye) - tv - 0.62, Xg=Xg, F=F,
                clip=(cxn, cxp, cyn, cyp), kind=kind, tv=tv)


def _chidori(mb, F, Hf, tv, xc, w, yd, m, zr, gable_m, gold, lod, P, amp):
    """CHIDORI-HAFU: empena triangular pousada na agua da frente. Duas aguas onduladas proprias (cumeeira ao longo
    de y) que entram no telhado de baixo, triangulo de reboco recuado com madeiramento, tabeiras, gegyo, cumeeira
    pequena com onigawara na frente."""
    X, ovc = w / 2, 0.9
    yfront = yd + ovc
    pc = 1.0
    zt = Hf(xc + X + ovc, yfront) + 0.5 + pc * (X + ovc)
    if zt > zr - 0.6:
        zt = zr - 0.6
        pc = (zt - Hf(xc + X + ovc, yfront) - 0.5) / (X + ovc)
    yb = yd
    while yb > 0.3 and Hf(xc, yb) < zt + 0.4:
        yb -= 0.25
    tvc = tv * 0.8
    Hs = lambda u, v: zt - pc * abs(v)
    Fa = sub(F, xc, 0.0, 0.0, -math.pi / 2)          # (u, v) -> (xc + v, -u)
    Fb = sub(F, xc, 0.0, 0.0, math.pi / 2)           # (u, v) -> (xc - v, u)
    tiles(mb, Fa, _wave(-yfront, -yb, P * 0.8, amp * 0.85, lod), lambda u: 0.0, X + ovc, Hs, m, tvc,
          rows=(0.0, 0.5, 1.0))
    tiles(mb, Fb, _wave(yb, yfront, P * 0.8, amp * 0.85, lod), lambda u: 0.0, X + ovc, Hs, m, tvc, rows=(0.0, 0.5, 1.0))
    zbase = Hf(xc, yd) - 0.3
    top = lambda x: zt - pc * abs(x - xc) - tvc - 0.06
    Xi = X
    while Xi > 0.5 and top(xc + Xi) < zbase + 0.3:
        Xi -= 0.1
    poly = [(xc - Xi, zbase), (xc + Xi, zbase), (xc + Xi, top(xc + Xi)), (xc, top(xc)), (xc - Xi, top(xc - Xi))]
    ext(mb, F, poly, "y", yd - 0.5, yd - 0.28, gable_m)
    Fg = sub(F, xc, 0.0, 0.0, math.pi / 2)           # x de Fg = +y de F
    _gable_timber(mb, Fg, yd - 0.3, yd - 0.12, zbase, lambda u: top(xc - u), Xi, "timber")
    for s in (-1, 1):
        strip(mb, F, [(xc + s * (X + ovc) * u, yfront - 0.12, Hs(0, (X + ovc) * u) - tvc) for u in (0.0, 0.5, 1.0)],
              (0, 1, 0), -0.17, 0.17, -0.72, 0.06, WD)
    _gegyo(mb, Fg, yfront - 0.12, zt - tvc - 0.72, 1, WD, 0.8, gold)
    ridge(mb, Fg, yb, yfront + 0.15, zt + 0.12, pc, 1.4, True, 0.7, gold, 1, (False, True))


def pent2(mb, Ff, L, depth, z_top, m=RAZ, s=0.42, tv=0.38, lift=0.45, lod=0, xs=None, embed=0.4, ends=True,
          rafters=True, amp=0.22, P=1.6, support="brackets", post_z=None, ylo=None, clip=None):
    """HISASHI ondulado (agua unica) encostado na parede: Ff na face da parede (y=0, +y fora), z_top = topo da telha
    junto da parede. support: 'brackets' (misulas nos xs) | 'posts' (pilares ate post_z = z do piso, viga de borda)
    | 'none'. V2-3 clip = (x-, x+): o hisashi TERMINA na divisa do lote (lado encostado: sem tabeira lateral).
    Devolve dict(eave_z, H)"""
    X = L / 2
    xa, xb = -X, X
    if clip:
        xa, xb = max(-X, -clip[0]), min(X, clip[1])
    ends = (ends, ends) if isinstance(ends, bool) else ends
    ends = (ends[0] and xa <= -X + 1e-6, ends[1] and xb >= X - 1e-6)

    def H(x, y):
        return z_top - s * y + lift * min(1.0, abs(x) / X) ** 3 * min(1.0, max(0.0, y) / depth) ** 3
    tiles(mb, Ff, _wave(xa, xb, P * (LOD3_P if lod >= 3 else 1.0), amp, min(1, lod)), ylo or (lambda x: -embed), depth,
          H, m, tv, rows=(0.0, 0.4, 1.0) if lod == 0 else (0.0, 1.0))   # V3-cut: lod >= 1 = 1 faixa (agua reta;
    #                                                                 o sori dos cantos fica linear: < 0,17 de diferenca)
    ia, ib = xa + (0.15 if xa <= -X + 1e-6 else 0.02), xb - (0.15 if xb >= X - 1e-6 else 0.02)
    nst = 6 if lod == 0 else 4                   # V3-cut: lod >= 1 = testeira em 4 trechos (a curva so sobe nas pontas)
    bb(mb, Ff, ia, ib, -0.2, 0.32, z_top - 0.12, z_top + 0.36, WD)              # rufo (mizukiri)
    fa, fb = xa + (0.25 if ends[0] or xa <= -X + 1e-6 else 0.05), xb - (0.25 if xb >= X - 1e-6 else 0.05)
    strip(mb, Ff, [(x, depth - 0.25, H(x, depth - 0.25) - tv) for x in [fa + (fb - fa) * i / nst for i in range(nst + 1)]],
          (0, 1, 0), -0.15, 0.15, -0.52, 0.04, WD)
    for sx, on in ((-1, ends[0]), (1, ends[1])):
        if on:
            strip(mb, Ff, [(sx * (X - 0.1), y, H(sx * (X - 0.1), y) - tv) for y in (0.05, depth * 0.5, depth - 0.05)],
                  (1, 0, 0), -0.13, 0.13, -0.5, 0.08, WD)
    xs = xs if xs is not None else ([-X + 0.7, X - 0.7] + (even(-X + 0.7, X - 0.7, 4.6)[1:-1] if L > 11 else []))
    xs = [x for x in xs if xa + 0.3 <= x <= xb - 0.3]
    if lod >= 1 and len(xs) > 2:
        xs = [xs[0], xs[-1]]                     # V2-3: lod >= 1 = misulas so nas pontas
    zb_ = lambda y: H(0.0, y) - tv
    ba, bb_ = xa + (0.3 if xa <= -X + 1e-6 else 0.05), xb - (0.3 if xb >= X - 1e-6 else 0.05)
    if support == "brackets":
        for x in xs:
            bracket2(mb, Ff, x, -0.3, depth - 0.45, zb_(depth - 0.6) - 0.2, 0.4, 1.3)
        yb = depth - 0.75
        bb(mb, Ff, ba, bb_, yb - 0.24, yb + 0.24, zb_(yb) - 0.6, zb_(yb) - 0.12, WD)
    elif support == "posts":
        yb = depth - 0.75
        bb(mb, Ff, ba, bb_, yb - 0.28, yb + 0.28, zb_(yb) - 0.7, zb_(yb) - 0.1, WD)
        for x in xs:
            bb(mb, Ff, x - 0.3, x + 0.3, yb - 0.3, yb + 0.3, post_z or 0.0, zb_(yb) - 0.7, WD)
            beam(mb, Ff, (x, 0.0, zb_(yb) - 2.1), (x, yb - 0.25, zb_(yb) - 0.85), 0.22, 0.3, WD)
    if rafters and lod == 0:
        for x in even(xa + 0.6, xb - 0.6, 1.35):
            beam(mb, Ff, (x, -0.2, H(x, -0.2) - tv - 0.15), (x, depth - 0.5, H(x, depth - 0.5) - tv - 0.15), 0.22, 0.26, WD)
    return dict(eave_z=H(0.0, depth) - tv - 0.52, H=H)


def skirt2(mb, F, Wi, Di, dep, z_top, m=RAZ, s=0.45, tv=0.4, lift=0.55, lod=0, P=1.6, amp=0.24, clip=None):
    """SAIA MOKOSHI de 4 aguas em volta de um piso recuado (Wi x Di = face do piso de cima; mesma aba 'dep' nos 4
    lados): placas onduladas que se encontram nos espigoes, capas de espigao com ponta levantada, testeiras, rufo.
    V2-3 clip = (x-, x+[, y-, y+]): a saia e CORTADA na divisa do lote (lados e fundo encostados no vizinho)."""
    Xi, Yi = Wi / 2, Di / 2
    Xe, Ye = Xi + dep, Yi + dep
    if lod >= 3:
        P = P * LOD3_P                    # V3-cut lod 3
    c4 = tuple(clip or ()) + (BIG,) * (4 - len(clip or ()))
    cn, cp, cyn, cyp = c4

    def lf(x, y):
        return lift * min(1.0, abs(x) / Xe) ** 3 * min(1.0, abs(y) / Ye) ** 3
    Hy = lambda x, y: z_top - s * (abs(y) - Yi) + lf(x, y)
    Hx = lambda u, v: z_top - s * (abs(v) - Xi) + lf(v, u)
    for k, Fk in enumerate((F, sub(F, ang=math.pi))):
        xa, xb = (max(-Xe, -cn), min(Xe, cp)) if k == 0 else (max(-Xe, -cp), min(Xe, cn))
        ye = min(Ye, cyp if k == 0 else cyn)
        if ye < Yi + 0.3:
            continue
        lim = Xi + ye - Yi - 0.05
        xa, xb = max(xa, -lim), min(xb, lim)
        tiles(mb, Fk, _wave(xa, xb, P, amp, 1 if (k or lod) else 0),
              lambda x: (Yi - 0.35) if abs(x) <= Xi else min(Ye - 0.05, Yi + abs(x) - Xi), ye, Hy, m, tv,
              rows=(0.0, 0.45, 1.0) if lod == 0 else (0.0, 1.0))
        if k == 0 and ye >= Ye - 1e-6:
            fa, fb = max(-Xe + 0.4, xa + 0.05), min(Xe - 0.4, xb - 0.05)
            strip(mb, Fk, [(x, Ye - 0.3, Hy(x, Ye - 0.3) - tv) for x in [fa + (fb - fa) * t for t in
                                                                          ((0, .1, .3, .5, .7, .9, 1) if lod == 0
                                                                           else STRIP_T2)]],
                  (0, 1, 0), -0.15, 0.15, -0.5, 0.04, WD)
        bb(mb, Fk, -Xi - 0.1, Xi + 0.1, Yi - 0.15, Yi + 0.3, z_top - 0.12, z_top + 0.36, WD)
    for Fk, c, (ua0, ub0) in ((sub(F, ang=-math.pi / 2), cp, (-cyp, cyn)), (sub(F, ang=math.pi / 2), cn, (-cyn, cyp))):
        xe_ = min(Xe, c)
        if xe_ < Xi + 0.3:
            continue
        lim = Yi + xe_ - Xi - 0.05
        ua, ub = max(-Ye, -lim, ua0), min(Ye, lim, ub0)
        if ub - ua < 0.3:
            continue
        tiles(mb, Fk, _wave(ua, ub, P, amp, max(lod, 1)),
              lambda u: (Xi - 0.35) if abs(u) <= Yi else min(Xe - 0.05, Xi + abs(u) - Yi), xe_, Hx, m, tv,
              rows=(0.0, 0.45, 1.0) if lod == 0 else (0.0, 1.0))
        if xe_ >= Xe - 1e-6:
            fa, fb = max(-Ye + 0.4, ua + 0.05), min(Ye - 0.4, ub - 0.05)
            strip(mb, Fk, [(u, Xe - 0.3, Hx(u, Xe - 0.3) - tv) for u in [fa + (fb - fa) * t for t in
                                                                          (0, .2, .5, .8, 1)]],
                  (0, 1, 0), -0.15, 0.15, -0.5, 0.04, WD)
        bb(mb, Fk, -Yi - 0.1, Yi + 0.1, Xi - 0.15, Xi + 0.3, z_top - 0.12, z_top + 0.36, WD)
    for sx in (1, -1):
        c = cp if sx > 0 else cn
        for sy in (1, -1):
            cy = cyp if sy > 0 else cyn
            f0 = max(0.0, (Xe - c + 0.7) / dep if c < BIG else 0.0, (Ye - cy + 0.7) / dep if cy < BIG else 0.0)
            if f0 >= 0.9:
                continue
            pts = [] if f0 > 0 else [(sx * (Xe + 0.4), sy * (Ye + 0.4), Hy(Xe, Ye) + 0.6)]
            for f in (0.0, 0.3, 0.7, 1.0):
                f = f0 + (1.0 - f0) * f
                x, y = sx * (Xe - dep * f), sy * (Ye - dep * f)
                pts.append((x, y, Hy(x, y) + 0.26))
            _hipcap(mb, F, pts, 0.8, False)
    return dict(eave_z=z_top - s * dep - tv - 0.5)


# ================================================================== PAREDES: estrutura de madeira + preenchimentos
def _span(L, bays, cp):
    """bays -> [(tipo, opcoes, a, b)] com a..b = vao livre entre pilares; cp = (pilar esq, pilar dir)"""
    norm = []
    for bay in bays:
        if isinstance(bay, str):
            norm.append((bay, {}, None))
        elif isinstance(bay, dict):
            o = dict(bay)
            t = o.pop("t")
            w = o.pop("w", None)
            norm.append((t, o, w))
        else:
            norm.append((bay[0], dict(bay[2]) if len(bay) > 2 else {}, bay[1]))
    n = len(norm)
    free = L - cp[0] - cp[1] - POST * (n - 1)
    fixed = sum(w for _, _, w in norm if w)
    nfree = sum(1 for _, _, w in norm if not w)
    wf = (free - fixed) / nfree if nfree else 0.0
    out = []
    x = -L / 2 + cp[0]
    for t, o, w in norm:
        w = w or wf
        out.append((t, o, x, x + w))
        x += w + POST
    return out


def _noren(mb, Ff, a, b, zt, ln=2.0, m=INDIGO, y=0.22, n=None):
    """noren: pano dividido em tiras (fendas de 0,1) pendurado de uma vara, 0,22 a frente dos pilares (n = tiras;
    V2-3: 2 nas fileiras de lod >= 1)"""
    bb(mb, Ff, a - 0.1, b + 0.1, y - 0.1, y + 0.1, zt - 0.22, zt, WD)
    n = n or max(2, int(round((b - a) / 1.15)))
    w = (b - a) / n
    for i in range(n):
        bb(mb, Ff, a + i * w + 0.05, a + (i + 1) * w - 0.05, y + 0.12, y + 0.24, zt - 0.22 - ln, zt - 0.18, m)


def _boards(mb, Ff, a, b, z0, z1, lod, step=1.05):
    """tabuado recuado 0,34 + mata-juntas 0,14 a frente"""
    bb(mb, Ff, a, b, -0.78, -0.34, z0, z1, WM)
    if lod == 0:
        xs = even(a, b, step)
        for x in xs[:-1]:
            xx = x + (b - a) / len(xs) / 2
            bb(mb, Ff, xx - 0.08, xx + 0.08, -0.34, -0.2, z0, z1, WD)


def _rail(mb, Ff, a, b, z0, z1, y0=-0.5, y1=-0.14):
    bb(mb, Ff, a, b, y0, y1, z0, z1, WD)


def _plaster(mb, Ff, a, b, z0, z1, pl, mid=4.4):
    """reboco recuado 0,3 + nuki aparente no meio se o pano passa de 'mid' de altura"""
    if z1 - z0 < 0.05:
        return
    bb(mb, Ff, a, b, -0.78, -0.3, z0, z1, pl)
    if z1 - z0 > mid:
        zm = (z0 + z1) / 2
        _rail(mb, Ff, a, b, zm - 0.14, zm + 0.14)


def _paper(lit):
    return LIT if lit else PL


def _lattice(mb, Ff, a, b, z0, z1, lit, step=0.46, w=0.17, rails=True, lod=0):
    """trelica koshi densa: ripas verticais 0,16 a cada 0,42 na frente, papel 0,24 atras (aceso ou nao). V2-3 lod 2:
    ripas a cada ~0,9 (fileiras de tras)"""
    bb(mb, Ff, a, b, -0.86, -0.64, z0, z1, _paper(lit))
    step = step * (1.0, 1.25, 1.9, 2.5)[min(3, lod)]
    for x in even(a, b, step):
        bb(mb, Ff, x - w / 2, x + w / 2, -0.4, -0.16, z0, z1, WD)
    if rails:
        _rail(mb, Ff, a, b, z1, z1 + 0.26, -0.55, -0.12)


def _kumiko(mb, Ff, a, b, z0, z1, lit, dx=0.8, dz=1.0, lod=0):
    """janela/porta de shoji: papel recuado + grade fina de kumiko 0,2 a frente (lod 1: grade 1,7x mais aberta)"""
    if lod:
        dx, dz = dx * (1.7 if lod < 3 else 2.4), dz * (1.7 if lod < 3 else 2.4)
    bb(mb, Ff, a, b, -0.9, -0.7, z0, z1, _paper(lit))
    xs = even(a, b, dx)
    for x in xs[:-1]:
        xx = x + (b - a) / len(xs) / 2
        bb(mb, Ff, xx - 0.06, xx + 0.06, -0.62, -0.5, z0, z1, WD)
    zs = even(z0, z1, dz)
    for z in zs[:-1]:
        zz = z + (z1 - z0) / len(zs) / 2
        bb(mb, Ff, a, b, -0.62, -0.5, zz - 0.06, zz + 0.06, WD)
    for xa, xb in ((a, a + 0.16), (b - 0.16, b)):
        bb(mb, Ff, xa, xb, -0.62, -0.42, z0, z1, WD)


def wall2(mb, Ff, L, h, bays, plaster=PLW, lod=0, lit=True, head=None, noren=INDIGO, corners=(True, True),
          upper=False, plate=True, sill=True, ext=(0.3, 0.3)):
    """FACHADA de estrutura aparente: soleira (dodai), pilares, frechal (keta) e, por vao, um PREENCHIMENTO
    (tipos no topo do arquivo). Ff no meio da fachada (y=0 na face dos pilares, +y fora), z=0 no piso do andar.
    head = altura do nageshi (verga de portas/lojas) no terreo. corners=(False, ...) reserva o pilar de canto mas
    nao o desenha (a fachada da frente/fundos ja o desenhou). ext = quanto o frechal passa do canto (V2-3: 0 no lado
    encostado no vizinho). Devolve dict(glow=[pontos], doors=[pontos])"""
    cp = (CPOST, CPOST)
    zt = h - PLATE_H
    z0 = SILL_H if sill else 0.0
    xl = -L / 2 + (0.0 if corners[0] else CPOST)
    xr = L / 2 - (0.0 if corners[1] else CPOST)
    if sill:
        bb(mb, Ff, xl, xr, -0.86, 0.06, 0.0, SILL_H, WD)
    if plate:
        bb(mb, Ff, xl - (ext[0] if corners[0] else 0.0), xr + (ext[1] if corners[1] else 0.0), -0.86, 0.12, zt, h, WD)
    sp = _span(L, bays, cp)
    for on, x0, x1 in ((corners[0], -L / 2, -L / 2 + CPOST), (corners[1], L / 2 - CPOST, L / 2)):
        if on:
            bb(mb, Ff, x0, x1, -0.86, 0.0, z0, zt, WD)
    for t, o, a, b in sp[:-1]:
        bb(mb, Ff, b, b + POST, -0.86, 0.0, z0, zt, WD)
    out = dict(glow=[], doors=[])
    for t, o, a, b in sp:
        bl = o.get("lit", lit)
        hb = o.get("head", head)
        if t == "plaster":
            if upper:
                _plaster(mb, Ff, a, b, z0, zt, plaster)
            else:
                _boards(mb, Ff, a, b, z0, 2.2, lod)
                _rail(mb, Ff, a, b, 2.2, 2.48)
                _plaster(mb, Ff, a, b, 2.48, zt, plaster)
        elif t == "plain":
            bb(mb, Ff, a, b, -0.78, -0.3, z0, zt, plaster)
        elif t == "board":
            _boards(mb, Ff, a, b, z0, zt, lod)
            _rail(mb, Ff, a, b, (z0 + zt) / 2 - 0.14, (z0 + zt) / 2 + 0.14)
        elif t == "amado":
            bb(mb, Ff, a, b, -0.78, -0.34, z0, zt, WM)
            if lod == 0:
                zs = even(z0, zt, 0.9)
                for z in zs[:-1]:
                    zz = z + (zt - z0) / len(zs) / 2
                    bb(mb, Ff, a, b, -0.34, -0.22, zz - 0.06, zz + 0.06, WD)
        elif t in ("koshi", "lattice"):
            zb = (1.5 if not upper else 1.1) if t == "koshi" else z0 + 0.6
            _boards(mb, Ff, a, b, z0, zb, 1)
            _rail(mb, Ff, a, b, zb, zb + 0.26)
            zk = hb if (hb and not upper) else (zt - 1.1 if not upper else zt - 0.9)
            _lattice(mb, Ff, a, b, zb + 0.26, zk, bl, lod=lod)
            _plaster(mb, Ff, a, b, zk + 0.26, zt, plaster)
            out["glow"].append(Ff.p((a + b) / 2, -0.5, (zb + zk) / 2))
        elif t == "door":
            hd_ = hb or min(zt - 0.8, 6.9)
            _rail(mb, Ff, a, b, hd_, hd_ + 0.36, -0.6, -0.12)
            w2 = (b - a) / 2
            leaves = ((a, a + w2 + 0.1, 0.0), (b - w2 - 0.1, b, 0.22)) if lod == 0 else ((a, b, 0.0),)
            for xa, xb, yo in leaves:                  # V2-3: lod >= 1 = 1 folha (porta fechada), kumiko aberto
                bb(mb, Ff, xa, xb, -1.0 + yo, -0.84 + yo, z0, z0 + 2.0, WM)
                Fl = sub(Ff, 0.0, -0.3 + yo)
                _kumiko(mb, Fl, xa + 0.2, xb - 0.2, z0 + 2.0, hd_ - 0.2, bl, 0.7 * (1.0 + 0.8 * (lod >= 2)),
                        1.1 * (1.0 + 0.8 * (lod >= 2)), lod)
                for zz0, zz1 in ((z0 + 1.9, z0 + 2.12), (hd_ - 0.22, hd_)):
                    bb(mb, Ff, xa, xb, -0.96 + yo, -0.72 + yo, zz0, zz1, WD)
            _plaster(mb, Ff, a, b, hd_ + 0.36, zt, plaster)
            nm = o.get("noren", noren)
            if nm:
                _noren(mb, Ff, a - 0.1, b + 0.1, hd_ + 0.1, 2.0, nm, n=2 if lod >= 1 else None)
            out["doors"].append(Ff.p((a + b) / 2, 0.8, 0.0))
            out["glow"].append(Ff.p((a + b) / 2, -0.6, z0 + 4.0))
        elif t == "shop":
            hd_ = hb or min(zt - 0.8, 7.0)
            bb(mb, Ff, a - 0.1, b + 0.1, -0.9, 0.02, hd_, hd_ + 0.5, WD)            # verga larga
            if zt - hd_ - 0.5 > 0.3:
                if o.get("upper_board"):
                    _boards(mb, Ff, a, b, hd_ + 0.5, zt, 1)
                else:
                    _plaster(mb, Ff, a, b, hd_ + 0.5, zt, plaster)
            nm = o.get("noren", noren)
            if nm:
                _noren(mb, Ff, a, b, hd_ + 0.12, 1.9, nm, n=2 if lod >= 1 else None)
            out["doors"].append(Ff.p((a + b) / 2, 0.8, 0.0))
        elif t == "mushiko":
            zw0, zw1 = 1.3, min(zt - 0.8, 4.3)
            _plaster(mb, Ff, a, b, z0, zw0 - 0.3, plaster)
            _plaster(mb, Ff, a, b, zw1 + 0.3, zt, plaster)
            bb(mb, Ff, a, b, -1.1, -0.9, zw0, zw1, LIT if bl else CBLACK)
            for x in even(a + 0.15, b - 0.15, 0.78 * (1.0, 1.25, 1.7, 2.2)[min(3, lod)]):
                bb(mb, Ff, x - 0.19, x + 0.19, -0.78, -0.3, zw0, zw1, plaster)
            for zz0, zz1 in ((zw0 - 0.3, zw0), (zw1, zw1 + 0.3)):
                bb(mb, Ff, a, b, -0.78, -0.12, zz0, zz1, plaster)
        elif t == "shoji":
            zs0 = 1.55 if upper else 2.6
            zs1 = min(zt - 0.6, zs0 + 3.6)
            if upper:
                _plaster(mb, Ff, a, b, z0, zs0 - 0.26, plaster)
            else:
                _boards(mb, Ff, a, b, z0, zs0 - 0.26, lod)
            _rail(mb, Ff, a, b, zs0 - 0.26, zs0, -0.6, -0.1)
            _kumiko(mb, Ff, a, b, zs0, zs1, bl, 0.95 if upper else 0.8, 1.15 if upper else 1.0, lod)
            _rail(mb, Ff, a, b, zs1, zs1 + 0.26, -0.6, -0.12)
            _plaster(mb, Ff, a, b, zs1 + 0.26, zt, plaster)
            out["glow"].append(Ff.p((a + b) / 2, -0.8, (zs0 + zs1) / 2))
            if o.get("rail", upper) and lod == 0:                                   # tesuri (corrimao de janela)
                zr = zs0 + 1.3
                bb(mb, Ff, a + 0.1, b - 0.1, 0.45, 0.8, zr - 0.2, zr, WD)
                for x in even(a + 0.4, b - 0.4, 0.55):
                    bb(mb, Ff, x - 0.07, x + 0.07, 0.52, 0.72, zs0 - 0.27, zr - 0.2, WD)
                bb(mb, Ff, a + 0.1, b - 0.1, -0.1, 0.8, zs0 - 0.45, zs0 - 0.27, WD)
        elif t == "open":
            if hb:
                bb(mb, Ff, a - 0.1, b + 0.1, -0.9, 0.02, hb, hb + 0.45, WD)
                _plaster(mb, Ff, a, b, hb + 0.45, zt, plaster)
            if o.get("noren"):
                _noren(mb, Ff, a, b, (hb or zt) + 0.1, 1.6, o["noren"])
    return out


def blind_wall(mb, Ff, L, h, m=PL, z0=0.0):
    """empena CEGA = PAREDE-MEIA (lateral encostada no vizinho): reboco RENTE a divisa (V2-3: nada passa da face, o
    vizinho encosta do outro lado) + frechal, sem pilares de canto (a frente ja os tem)"""
    bb(mb, Ff, -L / 2 + CPOST, L / 2 - CPOST, -0.6, 0.0, z0, h - PLATE_H, m)
    bb(mb, Ff, -L / 2 + CPOST, L / 2 - CPOST, -0.86, 0.0, h - PLATE_H, h, WD)


def plinth(mb, F, W, D, ph=0.8, steps=(), party=(False, False)):
    """soco de cantaria: corpo + capa de lajes recuada 0,08 (linha de sombra) + degraus de pedra nas portas
    (steps = [(x, largura)] na frente). party = lados encostados no vizinho (V2-3: o soco para na divisa)"""
    xa = -W / 2 - (0.0 if party[0] else 0.35)
    xb = W / 2 + (0.0 if party[1] else 0.35)
    bb(mb, F, xa, xb, -D / 2 - 0.35, D / 2 + 0.35, -0.3, ph - 0.22, ST)
    bb(mb, F, xa + (0.0 if party[0] else 0.08), xb - (0.0 if party[1] else 0.08), -D / 2 - 0.27, D / 2 + 0.27, ph - 0.22,
       ph, STP)
    for x, w in steps:
        bb(mb, F, x - w / 2, x + w / 2, D / 2 + 0.35, D / 2 + 1.5, -0.2, ph * 0.5, STP)


def _faces(F, W, D, z=0.0):
    return {"F": (sub(F, 0.0, D / 2, z), W), "B": (sub(F, 0.0, -D / 2, z, math.pi), W),
            "R": (sub(F, W / 2, 0.0, z, -math.pi / 2), D), "L": (sub(F, -W / 2, 0.0, z, math.pi / 2), D)}


def _body(mb, F, W, D, z, h, faces, plaster=PLW, lod=0, lit=True, head=None, upper=False, noren=INDIGO,
          back_lod=1, party=(False, False), hide=()):
    """um andar inteiro: faces = {"F": bays | "blind" | None, "B": ..., "L": ..., "R": ...}. Frente e fundos
    desenham os pilares de canto; as laterais nao. Devolve glow/doors somados."""
    out = dict(glow=[], doors=[])
    fr = _faces(F, W, D, z)
    for key in ("F", "B", "R", "L"):
        bays = faces.get(key)
        if bays is None or key in hide:          # V2-3: fundos encostados no vizinho de tras nao se veem
            continue
        Ff, L = fr[key]
        side = key in "RL"
        if bays == "blind":
            blind_wall(mb, Ff, L, h, plaster)
            continue
        if (key == "B" and max(lod, back_lod) >= 1) or (side and lod >= 2):
            bays = ["plain"]                       # V2-3: fundos (e laterais no lod 2) so em reboco emoldurado
        lk = lod if key != "B" else max(lod, back_lod)
        pl_ = (party[0], party[1]) if key == "F" else (party[1], party[0])
        r = wall2(mb, Ff, L, h, bays, plaster, lk, lit, head if key != "B" else None, noren,
                  (not side, not side), upper, ext=(0.0 if pl_[0] else 0.3, 0.0 if pl_[1] else 0.3))
        out["glow"] += r["glow"]
        out["doors"] += r["doors"]
    return out


# ------------------------------------------------------------------ mobiliario / mercadoria (baratos)
def pot6(mb, F, x, y, z, r=0.32, h=0.75, m=STD):
    lathe(mb, F, (x, y, z), [(r * 0.62, 0.0), (r, h * 0.45), (r * 0.6, h * 0.86), (r * 0.66, h)], 6, m)


def box_goods(mb, F, x, y, z, sx, sy, sz, m=WM, band=WD):
    bb(mb, F, x - sx / 2, x + sx / 2, y - sy / 2, y + sy / 2, z, z + sz, m)
    bb(mb, F, x - sx / 2 - 0.04, x + sx / 2 + 0.04, y - sy / 2 - 0.04, y + sy / 2 + 0.04, z + sz * 0.42, z + sz * 0.58,
       band)


def bolt_row(mb, F, x0, x1, y, z, d=0.55, cols=(CRED, INDIGO, CWHITE, STRAW)):
    """rolos de tecido em pe na prateleira (caixas coloridas lado a lado)"""
    n = max(1, int((x1 - x0) / (d + 0.08)))
    for i in range(n):
        xx = x0 + (i + 0.5) * (x1 - x0) / n
        bb(mb, F, xx - d / 2, xx + d / 2, y - 0.45, y + 0.45, z, z + 1.0 + 0.25 * (i % 2), cols[i % len(cols)])


def chochin2(mb, F, c, r=0.55, hgt=1.4, body=CRED, n=6):
    """CHOCHIN leve (6 lados, ~100 tris): tampas de laca escura, corpo abaulado no pano 'body' e SO a faixa do meio
    acesa (Glass_OP_Lantern). c = centro da BASE. Devolve o centro (local)"""
    cx, cy, z0 = c
    H = hgt
    za, zb, zc_, zd = z0 + 0.14, z0 + H * 0.4, z0 + H * 0.62, z0 + H - 0.14
    lathe(mb, F, (cx, cy, z0), [(r * 0.62, 0.0), (r * 0.7, 0.16)], n, WD, math.pi / n)
    lathe(mb, F, (cx, cy, za), [(r * 0.78, 0.0), (r, zb - za)], n, body, math.pi / n)
    lathe(mb, F, (cx, cy, zb), [(r * 1.0, 0.0), (r * 1.0, zc_ - zb)], n, LGLOW, math.pi / n)
    lathe(mb, F, (cx, cy, zc_), [(r, 0.0), (r * 0.78, zd - zc_)], n, body, math.pi / n)
    lathe(mb, F, (cx, cy, zd - 0.02), [(r * 0.7, 0.0), (r * 0.62, 0.16)], n, WD, math.pi / n)
    return (cx, cy, (zb + zc_) / 2)


def rail2(mb, F, pts, h=2.9, base=0.0, step=2.9, m=LAC, gold=True):
    """GUARDA-CORPO leve: pilaretes 0,34 nos nos, corrimao (kasagi) que passa das pontas, travessa media e rodape;
    giboshi dourado (6 lados) nas pontas e nos cantos, tampinha nos outros pilaretes. pts = [(x, y)] locais"""
    P = [Vector((p[0], p[1], 0.0)) for p in pts]
    nodes = []
    for i, (a, b) in enumerate(zip(P, P[1:])):
        d = b - a
        ln = d.length
        if ln < 0.3:
            continue
        nseg = max(1, int(math.ceil(ln / step)))
        for j in range(nseg + (1 if i == len(P) - 2 else 0)):
            nodes.append((a + d * (j / nseg), j == 0 or (i == len(P) - 2 and j == nseg)))
        ang = math.atan2(d.y, d.x)
        c = (a + b) / 2
        e0 = 0.25 if i == 0 else 0.17
        e1 = 0.25 if i == len(P) - 2 else 0.17
        cc = c + d.normalized() * (e1 - e0) / 2
        bx(mb, F, cc.x, cc.y, base + h - 0.13, ln + e0 + e1, 0.36, 0.26, m, 0.0, rz=ang)
        bx(mb, F, c.x, c.y, base + h * 0.55, ln, 0.16, 0.18, m, 0.0, rz=ang)
        bx(mb, F, c.x, c.y, base + 0.32, ln, 0.2, 0.2, m, 0.0, rz=ang)
    for q, corner in nodes:
        bx(mb, F, q.x, q.y, base + (h - 0.26) / 2, 0.34, 0.34, h - 0.26, m, 0.0)
        if gold and corner:
            _gibo(mb, F, q.x, q.y, base + h, 0.9)


def hanging_lantern(mb, F, x, y, zc, r=0.5, hgt=1.3, body=CRED, cord=0.9):
    """chochin pendurado (cordao de ferro + corpo); devolve o centro (local)"""
    mb.rod(F.p(x, y, zc + hgt * 0.5 + cord), F.p(x, y, zc + hgt * 0.5 - 0.02), 0.04, IRON, 4)
    return chochin2(mb, F, (x, y, zc - hgt * 0.5), r, hgt, body)


def andon_floor(mb, F, x, y, z, s=1.0):
    """andon de piso (lanterna de papel em armacao): pes, caixa de papel acesa, tampa"""
    hx, hz = 0.45 * s, 1.4 * s
    for sx in (-1, 1):
        for sy in (-1, 1):
            bb(mb, F, x + sx * hx - 0.07, x + sx * hx + 0.07, y + sy * hx - 0.07, y + sy * hx + 0.07, z, z + hz + 0.3, WD)
    bb(mb, F, x - hx + 0.08, x + hx - 0.08, y - hx + 0.08, y + hx - 0.08, z + 0.35, z + hz, LGLOW)
    bb(mb, F, x - hx - 0.08, x + hx + 0.08, y - hx - 0.08, y + hx + 0.08, z + hz, z + hz + 0.14, WD)
    return F.p(x, y, z + hz * 0.6)


def _interior_shop(mb, F, x0, x1, yf, depth, z0, h, seed=0, light_name=None, energy=60.0, lim=None):
    """INTERIOR da loja atras do vao aberto (x0..x1; yf = face interna da frente; piso de terra = topo do soco z0):
    doma na frente com banca baixa de mercadoria, estrado de madeira (agari) ao fundo com balcao (choba) e biombo,
    prateleiras na parede do fundo (rolos de tecido / potes / caixas), 2 chochin acesos sob o forro, divisorias
    laterais, porta com noren para os fundos. Devolve [pontos de luz]."""
    yb = yf - depth
    zc = z0 + h - PLATE_H
    xa, xb = x0 - 0.6, x1 + 0.6
    if lim is not None:                     # V2-3: as paredes do interior ficam DENTRO do lote (parede-meia)
        xa, xb = max(xa, -lim + 0.4), min(xb, lim - 0.4)
    bb(mb, F, xa - 0.4, xa, yb, yf, z0, zc, PLW)
    bb(mb, F, xb, xb + 0.4, yb, yf, z0, zc, PLW)
    bb(mb, F, xa - 0.4, xb + 0.4, yb - 0.4, yb, z0, zc, PLW)
    bb(mb, F, xa - 0.4, xb + 0.4, yb - 0.4, yf, zc, zc + 0.3, WD)
    for yy in (yb + depth * 0.35, yb + depth * 0.75):
        bb(mb, F, xa, xb, yy - 0.3, yy + 0.3, zc - 0.55, zc, WD)
    ya = yb + depth * 0.52
    bb(mb, F, xa, xb, yb, ya, z0, z0 + 1.15, WM)
    bb(mb, F, xa, xb, ya - 0.3, ya + 0.05, z0 + 0.3, z0 + 1.2, WD)
    for k, zz in enumerate((z0 + 2.6, z0 + 4.1, z0 + 5.6)):
        bb(mb, F, xa + 0.4, xb - 0.4, yb, yb + 1.1, zz - 0.18, zz, WD)
        if k == 0:
            bolt_row(mb, F, xa + 0.6, xb - 0.6, yb + 0.55, zz)
        elif k == 1:
            for j, xx in enumerate(even(xa + 0.6, xb - 0.6, 1.0)):
                pot6(mb, F, xx, yb + 0.55, zz, 0.3, 0.7 + 0.15 * (j % 2), (STD, WM, PL)[j % 3])
        else:
            for j, xx in enumerate(even(xa + 0.6, xb - 0.6, 1.4)):
                box_goods(mb, F, xx, yb + 0.55, zz, 1.1, 0.8, 0.7, (WM, STRAW)[j % 2])
    for xx in (xa + 0.55, xb - 0.55):
        bb(mb, F, xx - 0.12, xx + 0.12, yb, yb + 1.1, z0 + 1.15, z0 + 6.2, WD)
    left = _h01(seed, "bal") < 0.5
    xc = xa + (xb - xa) * (0.3 if left else 0.7)
    bb(mb, F, xc - 1.4, xc + 1.4, ya - 1.6, ya - 0.4, z0 + 1.15, z0 + 2.1, WD)
    bb(mb, F, xc - 1.5, xc + 1.5, ya - 1.7, ya - 0.3, z0 + 2.1, z0 + 2.28, WM)
    for xx in even(xc - 1.4, xc + 1.4, 0.45):
        bb(mb, F, xx - 0.05, xx + 0.05, ya - 0.3, ya - 0.2, z0 + 2.28, z0 + 3.0, WD)
    box_goods(mb, F, xc - 0.7, ya - 1.0, z0 + 2.28, 0.7, 0.5, 0.35, CRED, WD)
    yd = yf - 1.6
    bb(mb, F, x0 + 0.4, x1 - 0.4, yd - 0.9, yd + 0.9, z0 + 1.2, z0 + 1.42, WM)
    for xx in (x0 + 0.6, x1 - 0.6):
        for yy in (yd - 0.7, yd + 0.7):
            bb(mb, F, xx - 0.12, xx + 0.12, yy - 0.12, yy + 0.12, z0, z0 + 1.2, WD)
    for j, xx in enumerate(even(x0 + 0.8, x1 - 0.8, 1.3)):
        if j % 3 == 0:
            pot6(mb, F, xx, yd, z0 + 1.42, 0.42, 0.9, (STD, WM)[j % 2])
        elif j % 3 == 1:
            box_goods(mb, F, xx, yd, z0 + 1.42, 1.0, 1.0, 0.55, STRAW, WD)
        else:
            bolt_row(mb, F, xx - 0.6, xx + 0.6, yd, z0 + 1.42, 0.5)
    xd = xb - 2.4 if left else xa + 2.4
    bb(mb, F, xd - 1.2, xd + 1.2, yb + 0.02, yb + 0.16, z0 + 1.15, z0 + 6.4, CBLACK)
    _noren(mb, sub(F, 0.0, yb), xd - 1.2, xd + 1.2, z0 + 6.4, 2.1, INDIGO, 0.1)
    pts = []
    for xx in ((xa + xb) / 2 - (xb - xa) * 0.22, (xa + xb) / 2 + (xb - xa) * 0.22):
        pts.append(F.p(*hanging_lantern(mb, F, xx, yf - depth * 0.42, zc - 2.0, 0.5, 1.3)))
    if light_name:
        light(light_name, "POINT", F.p((xa + xb) / 2, yf - depth * 0.45, zc - 2.2), energy, WARM, 0.5)
    return pts


def _vitrine(mb, F, x0, x1, yf, z0, h, depth=2.6, seed=0, lod=0):
    """VITRINE RASA (PLANO_V2 3.5: lojas sem interior): fundo de reboco a 'depth' da face interna, forro escuro,
    estrado baixo com mercadoria apoiada e 2 prateleiras na parede do fundo, chochin aceso. Devolve [ponto de luz]"""
    yb = yf - depth
    zc = z0 + h - PLATE_H
    bb(mb, F, x0 - 0.3, x1 + 0.3, yb - 0.4, yb, z0, zc, PLW)
    for xx in (x0 - 0.3, x1):
        bb(mb, F, xx, xx + 0.3, yb, yf, z0, zc, PLW)
    bb(mb, F, x0 - 0.3, x1 + 0.3, yb - 0.4, yf, zc, zc + 0.3, WD)
    bb(mb, F, x0, x1, yb, yf - 0.6, z0, z0 + 1.2, WM)
    for zz in ((z0 + 3.0, z0 + 4.6) if lod == 0 else (z0 + 3.0,)):
        bb(mb, F, x0 + 0.2, x1 - 0.2, yb, yb + 0.9, zz - 0.16, zz, WD)
    if lod < 2:
        bolt_row(mb, F, x0 + 0.4, x1 - 0.4, yb + 0.45, z0 + 3.0, 0.6 if not lod else 1.0)
    for j, xx in enumerate(even(x0 + 0.5, x1 - 0.5, 1.3 if not lod else 2.2) if lod < 2 else []):
        if j % 2:
            box_goods(mb, F, xx, yb + 0.45, z0 + 4.6, 1.0, 0.7, 0.6, (WM, STRAW)[j % 4 // 2])
        pot6(mb, F, xx, yb + 1.4, z0 + 1.2, 0.36, 0.8 + 0.15 * (j % 2), (STD, WM, PL)[j % 3])
    if lod:
        return [F.p((x0 + x1) / 2, yb + depth * 0.55, zc - 2.2)]
    return [F.p(*hanging_lantern(mb, F, (x0 + x1) / 2, yb + depth * 0.55, zc - 1.6, 0.45, 1.2, CRED, 0.4))]


def _sign(mb, F, x, z, s=1.0, m=WD, panel=PLW, crest=RR):
    """SODE-KANBAN: placa pendurada PERPENDICULAR a fachada (le ao longo da rua): braco com mao-francesa, quadro
    escuro, painel claro recuado 0,14 nas 2 faces, disco do brasao, chapeuzinho de telha. F na face do pilar
    (+y fora), x = pilar, z = altura do braco"""
    L, Hh = 1.4 * s, 3.0 * s
    bb(mb, F, x - 0.14, x + 0.14, -0.1, L + 0.9, z - 0.3, z, m)
    beam(mb, F, (x, 0.05, z - 1.5), (x, L * 0.6, z - 0.3), 0.14, 0.2, m)
    y0, y1 = 0.5, 0.5 + L
    for k in (y0, y1):
        mb.rod(F.p(x, k + 0.1, z - 0.3), F.p(x, k + 0.1, z - 0.62), 0.04, IRON, 4)
    zt, zb = z - 0.6, z - 0.6 - Hh
    bb(mb, F, x - 0.16, x + 0.16, y0, y1, zb, zt, m)
    bb(mb, F, x - 0.3, x + 0.3, y0 + 0.16, y1 - 0.16, zb + 0.16, zt - 0.16, panel)
    bb(mb, F, x - 0.24, x + 0.24, y0 - 0.12, y1 + 0.12, zt - 0.02, zt + 0.2, RR)
    lathe_y(mb, sub(F, x, (y0 + y1) / 2, 0.0, math.pi / 2), (0.0, 0.0, zt - Hh * 0.32),
            [(0.42 * s, -0.36), (0.42 * s, 0.36)], 10, crest)


def _udatsu(mb, F, x, y_front, y_back, z0, z1, roof_m, pl=PL, narrow=False):
    """UDATSU: asa corta-fogo de reboco no 2o piso (passa da fachada), soco escuro, chapeuzinho de 2 aguas com
    cumeeira e onigawara na frente. narrow (V2-3, lado encostado): chapeu estreito que nao passa de x +- 0,62"""
    t = 0.9
    xa, xb = x - t / 2, x + t / 2
    bb(mb, F, xa, xb, y_back, y_front, z0, z1, pl)
    bb(mb, F, xa - 0.08, xb + 0.08, y_back, y_front + 0.08, z0 - 0.3, z0 + 0.12, WD)
    L = y_front - y_back + 0.6
    yc = (y_front + y_back) / 2 + 0.3
    bo, bw = (0.3, 0.68) if narrow else (0.48, 1.1)
    for s in (-1, 1):
        bx(mb, F, x + s * bo, yc, z1 + 0.3, bw, L, 0.26, roof_m, 0.0, ry=s * 0.55)
    bb(mb, F, x - 0.22, x + 0.22, yc - L / 2, yc + L / 2, z1 + 0.52, z1 + 0.92, RR)
    bb(mb, F, x - 0.36, x + 0.36, yc + L / 2 - 0.3, yc + L / 2 + 0.05, z1 + 0.4, z1 + 1.4, RR)


def _awning(mb, Ff, a, b, z, depth=2.4, cols=(CRED, CWHITE), drop=0.9):
    """toldo de pano listrado sobre bracos de madeira; Ff na face da parede, z = altura na parede"""
    n = max(3, int(round((b - a) / 0.9)))
    w = (b - a) / n
    ang = math.atan2(drop, depth)
    Ld = math.hypot(depth, drop)
    for i in range(n):
        xx = a + (i + 0.5) * w
        bx(mb, Ff, xx, depth / 2, z - drop / 2, w + 0.01, Ld, 0.1, cols[i % 2], 0.0, rx=-ang)
        bb(mb, Ff, xx - w / 2 + 0.03, xx + w / 2 - 0.03, depth - 0.06, depth + 0.06, z - drop - 0.7, z - drop + 0.05,
           cols[i % 2])
    for xx in (a + 0.1, b - 0.1):
        beam(mb, Ff, (xx, 0.0, z - 1.8), (xx, depth - 0.1, z - drop - 0.05), 0.16, 0.2, WD)
    bb(mb, Ff, a, b, depth - 0.15, depth + 0.1, z - drop - 0.12, z - drop + 0.1, WD)


# ================================================================== TIPOS DE EDIFICIO
def _posts_x(L, bays):
    """centros dos pilares de uma fachada (cantos inclusive) - para apoiar misulas de hisashi"""
    sp = _span(L, bays, (CPOST, CPOST))
    xs = [-L / 2 + CPOST / 2] + [b + POST / 2 for t, o, a, b in sp[:-1]] + [L / 2 - CPOST / 2]
    return xs, sp


def _info(kind, W, D, F, r, glow, doors, extra=None):
    d = dict(kind=kind, W=W, D=D, top_z=F.o.z + r["top"], ridge_z=F.o.z + r["zr"], eave_z=F.o.z + r["eave_z"],
             glow=glow, doors=doors, light_at=glow[len(glow) // 2] if glow else None, roof=r)
    d.update(extra or {})
    return d


def _karahafu2(mb, Ff, L, depth, z_top, m, rise=1.6, gold=True, lod=0, post_z=None):
    """KARAHAFU ondulado: capelo encostado na parede com a borda da frente em onda (sobe no meio, pontas viram
    para cima), tabeira grossa curva, gegyo com remate dourado, misulas nas pontas. Ff na face da parede"""
    X = L / 2

    def zf(x, y):
        u = min(1.0, abs(x) / X)
        t = max(0.0, y) / depth
        bell = 0.5 * (1.0 + math.cos(math.pi * min(1.0, u / 0.86)))
        flare = max(0.0, (u - 0.8) / 0.2) ** 2
        return z_top - 0.3 * y + (rise * bell + 0.55 * rise * flare) * t ** 1.4
    tiles(mb, Ff, _wave(-X, X, 1.5, 0.24, lod), lambda x: -0.35, depth, zf, m, 0.42, rows=(0.0, 0.3, 0.65, 1.0),
          coarse=1.2)
    yf = depth - 0.3
    xs_ = [(-X + 0.25) + (2 * X - 0.5) * i / 16 for i in range(17)]
    strip(mb, Ff, [(x, yf, zf(x, yf) - 0.42) for x in xs_], (0, 1, 0), -0.22, 0.22, -1.0, 0.06, WD)
    zc = zf(0.0, yf) - 0.42 - 1.0
    ext(mb, Ff, [(-0.9, zc + 0.4), (0.9, zc + 0.4), (0.55, zc - 0.45), (0.0, zc - 0.9), (-0.55, zc - 0.45)], "y",
        yf + 0.1, yf + 0.5, WD)
    if gold:
        mb.rod(Ff.p(0.0, yf + 0.38, zc - 0.05), Ff.p(0.0, yf + 0.68, zc - 0.05), 0.32, GOLD, 8)
    bb(mb, Ff, -X + 0.2, X - 0.2, -0.15, 0.32, z_top - 0.12, z_top + 0.36, WD)
    for sx in (-1, 1):
        bracket2(mb, Ff, sx * (X - 0.6), -0.3, depth - 0.7, zf(sx * (X - 0.6), depth * 0.5) - 0.42 - 0.3, 0.46, 1.3)
    if post_z is not None:                       # porticos: 2 pilares + viga (kashira-nuki) sob a tabeira
        yp = depth - 0.55
        for sx in (-1, 1):
            x = sx * (X - 0.55)
            bb(mb, Ff, x - 0.32, x + 0.32, yp - 0.32, yp + 0.32, post_z, zf(x, yp) - 0.42, WD)
            rock_base(mb, Ff, x, yp, post_z, 0.6, 0.35)
        zk = zf(X - 0.55, yp) - 0.42 - 1.5
        bb(mb, Ff, -X + 0.2, X - 0.2, yp - 0.22, yp + 0.22, zk - 0.45, zk, WD)
    return dict(top=zf(0.0, depth) + 0.3)


def loja(mb, F, W=14.0, D=16.0, roof_m=RAZ, shop_side=1, tsuma=False, roof="kirizuma", awning=False, udatsu=True,
         sides=(False, False), lod=0, seed=0, light_name=None, plaster=PLW, noren="auto", h0=9.0, h1=7.0,
         g_over=1.2, upper="mushiko", sign=True, pent_m=None, interior=True, back=None, lim=None, hide_back=False):
    """(a) MACHIYA-LOJA de 2 pisos: terreo com LOJA ABERTA (interior real) + porta com noren + trelica koshi,
    HISASHI ondulado com misulas, 2o piso baixo com mushiko-mado (ou shoji com corrimao), UDATSU nas divisas,
    placa sode-kanban, telhado kirizuma paralelo a rua (ou tsuma=True: empena para a rua). sides = (lateral -x,
    lateral +x) expostas (ponta de quadra) - False = encostada no vizinho (V2-3: PAREDE-MEIA, nada passa da divisa:
    soco, frechal, hisashi e telhado cortados em x = +-W/2). interior=False (V2-3, PLANO_V2 3.5) = VITRINE rasa no
    lugar do interior. back = limite do fundo (distancia do centro) quando ha vizinho atras."""
    ph = 0.8
    z0, z1 = ph, ph + h0
    party = (not sides[0], not sides[1])
    clip = party_clip(W, sides, D, back, lim)
    kw = 3.0 if W >= 13.0 else 0.0
    bays = ([("koshi", kw)] if kw else []) + [("door", 4.4), {"t": "shop", "upper_board": True}]
    if shop_side < 0:
        bays = list(reversed(bays))
    xs, sp = _posts_x(W, bays)
    shop = [(a, b) for t, o, a, b in sp if t == "shop"][0]
    door = [(a, b) for t, o, a, b in sp if t == "door"][0]
    dx = (door[0] + door[1]) / 2
    plinth(mb, F, W, D, ph, [(dx, 5.0)], party)
    side_bays = ["board", "koshi", "plaster", "board"] if lod == 0 else ["board", "plaster"]
    fg = {"F": bays, "B": ["amado", "plaster", "koshi"],
          "L": side_bays if sides[0] else "blind", "R": side_bays if sides[1] else "blind"}
    if noren == "auto":
        noren = (INDIGO, INDIGO, CRED, CWHITE, "Cloth_OP_Black")[int(_h01(seed, "nor") * 5)]
    g = _body(mb, F, W, D, z0, h0, fg, plaster, lod, True, 7.0, noren=noren, party=party,
              hide=HB if hide_back else ())
    up = {"mushiko": [("plaster", 1.8), "mushiko", ("plaster", 1.8)],
          "shoji": [("plaster", 1.6), {"t": "shoji", "rail": True}, ("plaster", 1.6)],
          "double": ["mushiko", ("plaster", 1.2), {"t": "shoji", "rail": True}]}[upper]
    su = ["board", "plaster", "shoji", "board"] if lod == 0 else ["plaster", "shoji"]
    fu = {"F": up, "B": ["plaster", "shoji", "plaster"], "L": su if sides[0] else "blind", "R": su if sides[1] else "blind"}
    g2 = _body(mb, F, W, D, z1, h1, fu, PL, lod, _h01(seed, "lit2") < 0.6, upper=True, party=party,
              hide=HB if hide_back else ())
    Ff = sub(F, 0.0, D / 2)
    pm = pent_m or roof_m
    pent2(mb, Ff, W + 0.3, 3.0, z1 + 0.9, pm, lod=lod, xs=xs, clip=clip[:2])
    if awning:
        _awning(mb, Ff, shop[0], shop[1], z0 + 7.35, 2.0, (CRED, CWHITE) if _h01(seed, "aw") < 0.5 else (INDIGO, CWHITE),
                0.8)
    if udatsu and lod < 2:
        for k, sx in enumerate((-1, 1)):
            if lod >= 1 and sx < 0:
                continue                             # V2-3: lod >= 1 = 1 udatsu por divisa (o do vizinho faz o outro)
            nar = party[k]
            _udatsu(mb, F, sx * (W / 2 - (0.72 if nar else 0.45)), D / 2 + 1.1, D / 2 - 2.6, z1 + 0.45, z1 + h1 + 0.25,
                    pm, narrow=nar)
    if sign and lod == 0:
        _sign(mb, Ff, shop_side * (W / 2 - 0.45), z0 + 6.6, 1.0)
    if interior:
        pts = _interior_shop(mb, F, shop[0], shop[1], D / 2 - 0.86, min(7.5, D * 0.5), z0, h0, seed, light_name,
                             lim=W / 2 - 0.05)
    else:
        pts = _vitrine(mb, F, shop[0], shop[1], D / 2 - 0.86, z0, h0, 2.6, seed, lod)
    if lod == 0:
        hanging_lantern(mb, Ff, dx, 2.15, z0 + 6.0, 0.55, 1.5)
    zw = z1 + h1
    if tsuma:
        r = roof2(mb, sub(F, ang=math.pi / 2), D, W, zw, "kirizuma", roof_m, ov=g_over + 0.4, g_over=2.2, lod=lod,
                  back_lod=0 if lod == 0 else 1, ends=("board" if lod == 0 else "plain", "timber"), brackets=None,
                  s0=0.4, s1=0.9, clip=rot_clip(clip))
    elif roof == "irimoya":
        r = roof2(mb, F, W, D, zw, "irimoya", roof_m, ov=2.6, g_over=1.4, lod=lod, brackets=xs[1:-1], clip=clip)
    else:
        r = roof2(mb, F, W, D, zw, "kirizuma", roof_m, ov=2.6, g_over=g_over, lod=lod, s0=0.38, s1=0.86,
                  ends=("timber" if sides[0] else "plain", "timber" if sides[1] else "plain"), brackets=xs[1:-1],
                  clip=clip)
    return _info("loja", W, D, F, r, pts + g["glow"] + g2["glow"], g["doors"])


def sobrado(mb, F, W=16.0, D=16.0, roof_m=RTEAL, skirt_m=None, rail_m=WD, shop=False, sides=(True, True), lod=0,
            seed=0, light_name=None, plaster=PLW, h0=8.6, h1=7.0, h2=6.4, chidori=True, noren=INDIGO, back=None, lim=None, hide_back=False, top="irimoya"):
    """(b) SOBRADO de 3 pisos: terreo de trelicas + porta (ou loja), HISASHI, VARANDA CORRIDA no 2o piso (sobre
    misulas, guarda-corpo de madeira ou laca vermelha) com shoji aceso, SAIA MOKOSHI de 4 aguas, 3o piso recuado
    1,6 com irimoya + chidori: 4 niveis de telhado/varanda empilhados. V2-3: lados encostados (sides False) cortam
    soco, hisashi, saia e telhado na divisa."""
    ph = 0.8
    z0, z1 = ph, ph + h0
    z2 = z1 + h1
    party = (not sides[0], not sides[1])
    clip = party_clip(W, sides, D, back, lim)
    if shop:
        bays = [("lattice", 3.2), ("door", 4.4), {"t": "shop", "upper_board": True}]
    else:
        bays = [("koshi", None), ("door", 4.4), ("lattice", None), ("koshi", None)]
    bays = [b if b[1] else b[0] for b in bays] if not shop else bays
    xs, sp = _posts_x(W, bays)
    door = [(a, b) for t, o, a, b in sp if t == "door"][0]
    dx = (door[0] + door[1]) / 2
    plinth(mb, F, W, D, ph, [(dx, 5.0)], party)
    sb = ["board", "koshi", "plain"]
    g = _body(mb, F, W, D, z0, h0, {"F": bays, "B": ["amado", "plain"], "L": sb if sides[0] else "blind",
                                    "R": sb if sides[1] else "blind"}, plaster, lod, True, 7.0, noren=noren,
              party=party, hide=HB if hide_back else ())
    if shop:
        sh = [(a, b) for t, o, a, b in sp if t == "shop"][0]
        g["glow"] += _vitrine(mb, F, sh[0], sh[1], D / 2 - 0.86, z0, h0, 2.6, seed, lod)
    nb = max(3, int(round((W - 2) / 4.6)))
    u2 = [("plaster", 1.0)] + [{"t": "shoji", "rail": False}] * nb + [("plaster", 1.0)]
    s2 = ["plain", "shoji", "plain"]
    g2 = _body(mb, F, W, D, z1, h1, {"F": u2, "B": ["plain"], "L": s2 if sides[0] else "blind",
                                     "R": s2 if sides[1] else "blind"}, PL, lod, True, upper=True, party=party,
               hide=HB if hide_back else ())
    Ff = sub(F, 0.0, D / 2)
    sm = skirt_m or roof_m
    pent2(mb, Ff, W + 0.3, 2.8, z1 + 0.85, sm, lod=lod, xs=xs, clip=clip[:2])
    # varanda corrida (deck sobre misulas curtas, acima do hisashi)
    F2 = sub(Ff, 0.0, 0.0, z1)
    zd = 1.3
    for x in xs:
        if lod < 2:
            bracket2(mb, F2, x, -0.3, 2.2, zd - 0.25, 0.4, 0.55, WD, False)
    nbd = 3
    for i in range(nbd):
        y0 = 0.05 + 2.0 * i / nbd
        bb(mb, F2, -W / 2 + 0.2, W / 2 - 0.2, y0 + 0.03, y0 + 2.0 / nbd - 0.03, zd - 0.25, zd, WM)
    bb(mb, F2, -W / 2 + 0.1, W / 2 - 0.1, 1.75, 2.15, zd - 0.6, zd - 0.05, WD)
    rail2(mb, F2, [(-W / 2 + 0.45, 0.2), (-W / 2 + 0.45, 1.85), (W / 2 - 0.45, 1.85), (W / 2 - 0.45, 0.2)], 2.9, zd,
             2.9, rail_m, rail_m == LAC)
    for x in (-W / 4, W / 4):
        if lod == 0:
            hanging_lantern(mb, F2, x, 1.2, zd - 2.2, 0.45, 1.2, CRED, 0.3)
    # 3o piso recuado + saia
    sbk = 1.6
    W3, D3 = W - 2 * sbk, D - 2 * sbk
    nb3 = max(2, int(round((W3 - 2) / 4.4)))
    u3 = ["plaster"] + ["shoji"] * nb3 + ["plaster"]
    g3 = _body(mb, F, W3, D3, z2, h2, {"F": u3, "B": ["plain"], "L": ["plain", "shoji", "plain"],
                                       "R": ["plain", "shoji", "plain"]}, PL, lod, True, upper=True)
    skirt2(mb, sub(F, z=0.0), W3, D3, sbk + 1.7, z2 + 1.0, sm, lod=lod, clip=clip)
    xs3, _ = _posts_x(W3, u3)
    r = roof2(mb, F, W3, D3, z2 + h2, top, roof_m, ov=2.6, g_over=1.5, lod=lod, dg=0.42, rafters=False,
              chidori=dict(w=W3 * 0.5) if chidori and lod == 0 else None, brackets=xs3[1:-1] if lod == 0 else None,
              clip=clip)
    return _info("sobrado", W, D, F, r, g["glow"] + g2["glow"] + g3["glow"], g["doors"])


def esquina(mb, F, W=16.0, D=16.0, roof_m=RREDV, tower_m=None, corner=1, lod=0, seed=0, light_name=None, plaster=PLW,
            h0=9.0, h1=7.0, tw=7.0, noren=INDIGO, back=None, lim=None, hide_back=False, solo=False):
    """(c) CASA DE ESQUINA com TORRE-MIRANTE: 2 pisos com lojas nas 2 ruas (frente e lateral 'corner'), hisashi que
    DOBRA a esquina (espigao na diagonal), irimoya no corpo, e no canto da esquina uma torre de 2 andares acima do
    telhado: piso fechado de shoji + MIRANTE aberto com varanda vermelha em misulas e telhado piramidal (hogyo)
    com remate dourado. V2-3: o lado oposto a esquina e PAREDE-MEIA (corta soco, hisashi e telhado na divisa);
    solo=True = os 2 lados expostos (lote sozinho entre 2 ruas)."""
    c = 1 if corner >= 0 else -1
    ph = 0.8
    z0, z1 = ph, ph + h0
    z2 = z1 + h1
    sides = (True, True) if solo else ((False, True) if c > 0 else (True, False))
    party = (not sides[0], not sides[1])
    clip = party_clip(W, sides, D, back, lim)
    fb = [("koshi", 2.8), ("door", 4.4), {"t": "shop", "upper_board": True}]
    sb_ = [{"t": "shop", "upper_board": True}, ("koshi", 2.8), "plaster"]
    if c < 0:
        fb = list(reversed(fb))
    xs, sp = _posts_x(W, fb)
    door = [(a, b) for t, o, a, b in sp if t == "door"][0]
    shop = [(a, b) for t, o, a, b in sp if t == "shop"][0]
    dx = (door[0] + door[1]) / 2
    plinth(mb, F, W, D, ph, [(dx, 5.0)], party)
    fg = {"F": fb, "B": ["amado", "plain"]}
    fg["R" if c > 0 else "L"] = sb_
    fg["L" if c > 0 else "R"] = ["plaster", "koshi", "plain"] if solo else "blind"
    g = _body(mb, F, W, D, z0, h0, fg, plaster, lod, True, 7.0, noren=noren, party=party,
              hide=HB if hide_back else ())
    pts = _vitrine(mb, F, shop[0], shop[1], D / 2 - 0.86, z0, h0, 2.6, seed, lod)
    fu = {"F": [("plaster", 1.6), "mushiko", ("plaster", 1.6)], "B": ["plain"]}
    fu["R" if c > 0 else "L"] = ["plaster", "shoji", "plaster", "shoji", "plaster"]
    fu["L" if c > 0 else "R"] = ["plain", "shoji", "plain"] if solo else "blind"
    g2 = _body(mb, F, W, D, z1, h1, fu, PL, lod, True, upper=True, party=party,
              hide=HB if hide_back else ())
    # hisashi que dobra a esquina: frente + lateral, cortados na diagonal do canto, capa de espigao
    dep = 3.0
    Ff = sub(F, c * dep / 2, D / 2)
    xcw = c * W / 2 - c * dep / 2
    pc_ = None if solo else ((W / 2 + dep / 2, BIG) if c > 0 else (BIG, W / 2 + dep / 2))
    pent2(mb, Ff, W + 0.3 + dep, dep, z1 + 0.9, roof_m, lod=lod, lift=0.0, xs=[x - c * dep / 2 for x in xs],
          ylo=lambda x: max(-0.4, c * (x - xcw)), ends=(c > 0, c < 0), clip=pc_)
    Fs = sub(F, c * W / 2, dep / 2, 0.0, -c * math.pi / 2)
    Ls = D + 0.3 + dep
    ucs = c * (dep / 2 - D / 2)
    pent2(mb, Fs, Ls, dep, z1 + 0.9, roof_m, lod=max(lod, 1), lift=0.0, rafters=False,
          xs=[c * (dep / 2 - y) for y in (D / 2 - 0.45, D / 6, -D / 6, -D / 2 + 0.45)],
          ylo=lambda u: max(-0.4, c * (ucs - u)), ends=(c < 0, c > 0))
    zt = z1 + 0.9
    pts_h = [(c * (W / 2 + dep + 0.4), D / 2 + dep + 0.4, zt - 0.42 * dep + 0.55)]
    for f in (0.0, 0.4, 1.0):
        pts_h.append((c * (W / 2 + dep * (1 - f)), D / 2 + dep * (1 - f), zt - 0.42 * dep * (1 - f) + 0.25))
    _hipcap(mb, F, pts_h, 0.75)
    if lod == 0:
        _sign(mb, sub(F, 0.0, D / 2), c * (W / 2 - 0.45), z0 + 6.6, 1.0)
    if lod == 0:
        hanging_lantern(mb, sub(F, 0.0, D / 2), dx, 2.15, z0 + 6.0, 0.55, 1.5)
    r = roof2(mb, F, W, D, z2, "yosemune", roof_m, ov=2.6, s0=0.4, s1=0.95, lod=lod, rafters=False, clip=clip)
    # torre
    tm = tower_m or roof_m
    Ft = sub(F, c * (W / 2 - tw / 2), D / 2 - tw / 2)
    ht = 6.4
    tb, tp = ["plaster", "shoji", "plaster"], ["plaster"]
    ft = {"F": tb, "B": tp}
    ft["R" if c > 0 else "L"] = tb
    ft["L" if c > 0 else "R"] = tp
    gt = _body(mb, Ft, tw, tw, z2, ht, ft, PL, max(lod, 1), True, upper=True)
    zl = z2 + ht
    dk = 1.3
    Wl = tw + 2 * dk
    for k, Fk in enumerate((sub(Ft, 0, tw / 2, zl), sub(Ft, 0, -tw / 2, zl, math.pi), sub(Ft, tw / 2, 0, zl, -math.pi / 2),
                            sub(Ft, -tw / 2, 0, zl, math.pi / 2))):
        bracket2(mb, Fk, 0.0, -0.3, dk + 0.1, -0.05, 0.5, 1.2, WD, False)
    bb(mb, Ft, -Wl / 2, Wl / 2, -Wl / 2, Wl / 2, zl - 0.05, zl + 0.35, WM)
    bb(mb, Ft, -Wl / 2 - 0.05, Wl / 2 + 0.05, -Wl / 2 - 0.05, Wl / 2 + 0.05, zl - 0.45, zl - 0.05, WD)
    q = Wl / 2 - 0.35
    rail2(mb, Ft, [(-q, -q), (q, -q), (q, q), (-q, q), (-q, -q + 0.01)], 2.8, zl + 0.35, 2.4 if lod == 0 else 4.2, LAC,
          True)
    hl = 5.2
    for sx in (-1, 1):
        for sy in (-1, 1):
            bb(mb, Ft, sx * (tw / 2 - 0.4) - 0.4, sx * (tw / 2 - 0.4) + 0.4, sy * (tw / 2 - 0.4) - 0.4,
               sy * (tw / 2 - 0.4) + 0.4, zl + 0.35, zl + hl, WD)
    for Fk, L in ((sub(Ft, 0, tw / 2), tw), (sub(Ft, 0, -tw / 2, 0, math.pi), tw), (sub(Ft, tw / 2, 0, 0, -math.pi / 2), tw),
                  (sub(Ft, -tw / 2, 0, 0, math.pi / 2), tw)):
        bb(mb, Fk, -L / 2 - 0.2, L / 2 + 0.2, -0.8, 0.12, zl + hl - 0.6, zl + hl, WD)
        bb(mb, Fk, -L / 2 + 0.8, L / 2 - 0.8, -0.6, -0.2, zl + hl - 1.5, zl + hl - 0.6, LAC)          # ranma vermelho
        bb(mb, Fk, -L / 2 + 0.8, L / 2 - 0.8, -0.7, -0.5, zl + 0.35, zl + 1.6, PL)                    # peitoril baixo
    hanging_lantern(mb, Ft, 0.0, 0.0, zl + 2.8, 0.6, 1.5)
    rt = roof2(mb, Ft, tw, tw, zl + hl, "hogyo", tm, ov=2.6, s0=0.45, s1=1.1, lift=1.4, lod=max(lod, 1), gold=True,
               rafters=False, end_lod=lod)
    info = _info("esquina", W, D, F, r, pts + g["glow"] + g2["glow"] + gt["glow"], g["doors"])
    info["top_z"] = Ft.o.z + rt["top"]
    return info


def _namako(mb, Ff, a, b, z0, z1, step=1.5, lod=0):
    """NAMAKO-KABE: placa de telha escura com grade DIAGONAL de juntas de reboco salientes + moldura de reboco"""
    bb(mb, Ff, a, b, -0.1, 0.12, z0, z1, RR)
    if lod <= 1:
        w = 0.24
        L = (b - a) + (z1 - z0)
        k = int(L / step) + 1
        for s in (1, -1):
            for i in range(-k, k + 1):
                c = i * step
                # reta x - s*(z - z0) = a + c, recortada no retangulo
                pts = []
                for zz in (z0, z1):
                    xx = a + c + s * (zz - z0)
                    if a - 1e-6 <= xx <= b + 1e-6:
                        pts.append((xx, zz))
                for xx in (a, b):
                    zz = z0 + (xx - a - c) * s
                    if z0 - 1e-6 <= zz <= z1 + 1e-6:
                        pts.append((xx, zz))
                pts = sorted(set((round(p[0], 4), round(p[1], 4)) for p in pts))
                if len(pts) >= 2 and math.hypot(pts[-1][0] - pts[0][0], pts[-1][1] - pts[0][1]) > 0.4:
                    (xa, za), (xb, zb) = pts[0], pts[-1]
                    beam(mb, Ff, (xa, 0.2, za), (xb, 0.2, zb), w, 0.16, PL)
    for z_, h_ in ((z0 - 0.3, 0.32), (z1, 0.32)):
        bb(mb, Ff, a - 0.15, b + 0.15, -0.12, 0.36, z_, z_ + h_, PL)
    for x_ in (a - 0.32, b):
        bb(mb, Ff, x_, x_ + 0.32, -0.12, 0.36, z0, z1, PL)


def kura(mb, F, W=10.0, D=14.0, roof_m=RB, tsuma=True, lod=0, seed=0, h=12.5, crest=True, sides=(True, True),
         back=None, lim=None):
    """(d) KURA (armazem): soco de pedra alto, corpo macico de reboco claro, faixa NAMAKO (grade diagonal) na base,
    cinta de molduras escalonadas sob o beiral, PORTA-COFRE com molduras em degrau, folhas grossas abertas e
    hisashi em misulas, janela alta com portinholas de reboco, brasao (kamon) na empena, telhado kirizuma PESADO
    (telha grossa, cumeeira de 3 fiadas, onigawara grande). V2-3: lado encostado (sides False) = parede-meia lisa:
    soco, molduras, namako e telhado param na divisa."""
    zb = 1.4
    party = (not sides[0], not sides[1])
    clip = party_clip(W, sides, D, back, lim)
    xa_, xb_ = -W / 2 - (0.0 if party[0] else 0.5), W / 2 + (0.0 if party[1] else 0.5)
    bb(mb, F, xa_, xb_, -D / 2 - 0.5, D / 2 + 0.5, -0.3, zb - 0.3, ST)
    bb(mb, F, xa_ + (0.0 if party[0] else 0.1), xb_ - (0.0 if party[1] else 0.1), -D / 2 - 0.4, D / 2 + 0.4, zb - 0.3,
       zb, STP)
    zt = zb + h
    bb(mb, F, -W / 2, W / 2, -D / 2, D / 2, zb, zt, PL)
    # faces: frente = empena (tsuma) na rua
    fr = _faces(F, W, D)
    zn = zb + 3.2
    for key in ("F", "R", "L", "B"):
        Ff, L = fr[key]
        if key == "B" and lod > 0:
            continue
        if (key == "R" and party[1]) or (key == "L" and party[0]):
            continue
        # molduras que dobram o canto: param na divisa do lado encostado (F: -x = esq; B: girado, -x = dir)
        pa, pb = (party[0], party[1]) if key == "F" else ((party[1], party[0]) if key == "B" else (False, False))
        e1a, e1b = (0.0 if pa else 0.2), (0.0 if pb else 0.2)
        e2a, e2b = (0.0 if pa else 0.4), (0.0 if pb else 0.4)
        if key == "F":                                    # a frente tem a porta-cofre: namako so dos lados
            for a_, b_ in ((-L / 2 + 0.5, -2.3 - 1.25), (2.3 + 1.25, L / 2 - 0.5)):
                if b_ - a_ > 0.6:
                    _namako(mb, Ff, a_, b_, zb + 0.3, zn, 1.5, lod)
        else:
            _namako(mb, Ff, -L / 2 + 0.5, L / 2 - 0.5, zb + 0.3, zn, 1.5, lod if key in "RL" else 1)
        # cinta de molduras (hachimaki) sob o beiral
        bb(mb, Ff, -L / 2 - e1a, L / 2 + e1b, -0.2, 0.3, zt - 1.6, zt - 1.2, PL)
        bb(mb, Ff, -L / 2 - e2a, L / 2 + e2b, -0.2, 0.55, zt - 0.8, zt - 0.3, PL)
    # porta-cofre na frente
    Ff, L = fr["F"]
    dw, dh = 4.6, 6.8
    for k, (e, dy) in enumerate(((0.9, 0.3), (0.55, 0.6), (0.25, 0.9))):
        bb(mb, Ff, -dw / 2 - e, -dw / 2, -0.1, dy, zb, zb + dh + e, PL)
        bb(mb, Ff, dw / 2, dw / 2 + e, -0.1, dy, zb, zb + dh + e, PL)
        bb(mb, Ff, -dw / 2 - e, dw / 2 + e, -0.1, dy, zb + dh, zb + dh + e, PL)
    bb(mb, Ff, -dw / 2, dw / 2, -0.1, 0.06, zb, zb + dh, WD)                         # porta interna escura
    for x in even(-dw / 2 + 0.3, dw / 2 - 0.3, 1.15):
        bb(mb, Ff, x - 0.06, x + 0.06, 0.06, 0.18, zb + 0.4, zb + dh - 0.3, WM)
    for zz in (zb + 1.4, zb + dh - 1.4):                                             # faixas de ferro
        bb(mb, Ff, -dw / 2, dw / 2, 0.06, 0.2, zz - 0.15, zz + 0.15, IRON)
    bb(mb, Ff, -dw / 2 - 1.2, dw / 2 + 1.2, 0.0, 1.6, zb - 0.6, zb + 0.15, STP)       # soleira de pedra
    pent2(mb, sub(Ff, 0.0, 0.9), dw + 3.6, 1.9, zb + dh + 2.4, roof_m, s=0.5, tv=0.45, lod=lod,
          xs=[-(dw + 3.6) / 2 + 0.6, (dw + 3.6) / 2 - 0.6])
    # janela alta com portinholas
    zw0 = zt - 0.6
    ww = 2.4
    for e, dy in ((0.5, 0.3), (0.25, 0.55)):
        bb(mb, Ff, -ww / 2 - e, ww / 2 + e, -0.1, dy, zw0 + 0.6, zw0 + 0.6 + 2.2 + e, PL)
    bb(mb, Ff, -ww / 2, ww / 2, -0.17, 0.05, zw0 + 0.6, zw0 + 2.8, CBLACK)
    for x in even(-ww / 2 + 0.2, ww / 2 - 0.2, 0.5):
        bb(mb, Ff, x - 0.07, x + 0.07, 0.05, 0.2, zw0 + 0.6, zw0 + 2.8, IRON)
    for s in (-1, 1):
        bb(mb, Ff, s * (ww / 2 + 0.55) - 0.15, s * (ww / 2 + 0.55) + 0.15, 0.3, 1.5, zw0 + 0.6, zw0 + 2.8, PL)
    pent2(mb, sub(Ff, 0.0, 0.55), ww + 2.0, 1.0, zw0 + 3.6, roof_m, s=0.5, tv=0.3, lod=1, rafters=False,
          xs=[-(ww + 2.0) / 2 + 0.4, (ww + 2.0) / 2 - 0.4])
    if tsuma:
        r = roof2(mb, sub(F, ang=math.pi / 2), D, W, zt, "kirizuma", roof_m, ov=1.9, g_over=1.7, s0=0.5, s1=0.95,
                  lift=0.6, tv=0.7, lod=lod, back_lod=lod, ends=("plain", "plain"), courses=3, ridge_w=2.6,
                  rafters=False, gable_m=PL, clip=rot_clip(clip))
    else:
        r = roof2(mb, F, W, D, zt, "kirizuma", roof_m, ov=1.9, g_over=1.7, s0=0.5, s1=0.95, lift=0.6, tv=0.7, lod=lod,
                  ends=("plain", "plain"), courses=3, ridge_w=2.6, rafters=False, gable_m=PL, clip=clip)
    if crest and not tsuma and not party[1]:
        zc_ = zt + 2.0
        Fk = sub(F, 0.0, D / 2 - 0.3) if tsuma else sub(F, W / 2 - 0.3, 0.0, 0.0, -math.pi / 2)
        n = 16
        rings = []
        for rr, yy in ((1.3, 0.0), (1.3, 0.42), (0.95, 0.42), (0.95, 0.0)):
            rings.append([(rr * math.cos(2 * math.pi * j / n), yy, zc_ + rr * math.sin(2 * math.pi * j / n)) for j in range(n)])
        rings.append(rings[0])
        loft(mb, Fk, rings, RR, caps=(False, False))
        lathe_y(mb, Fk, (0.0, 0.0, zc_), [(0.45, 0.0), (0.45, 0.42)], 8, RR)
    return _info("kura", W, D, F, r, [], [Ff.p(0.0, 1.0, 0.0)])


def _interior_tea(mb, F, x0, x1, yf, depth, z0, h, seed=0, light_name=None, energy=55.0, lim=None):
    """INTERIOR da casa de cha: piso de TATAMI com bordas escuras, 2 mesas baixas com almofadas (zabuton) e jogo de
    cha, tokonoma no fundo (estrado + rolo pendurado + vaso), fusuma emoldurados, 2 andon de piso acesos + chochin,
    forro com vigas. Devolve [pontos de luz]"""
    yb = yf - depth
    zc = z0 + h - PLATE_H
    xa, xb = x0 - 0.6, x1 + 0.6
    if lim is not None:                     # V2-3: paredes do interior DENTRO do predio (parede-meia)
        xa, xb = max(xa, -lim + 0.4), min(xb, lim - 0.4)
    zf = z0 + 0.55
    bb(mb, F, xa - 0.4, xa, yb, yf, z0, zc, PLW)
    bb(mb, F, xb, xb + 0.4, yb, yf, z0, zc, PLW)
    bb(mb, F, xa - 0.4, xb + 0.4, yb - 0.4, yb, z0, zc, PLW)
    bb(mb, F, xa - 0.4, xb + 0.4, yb - 0.4, yf, zc, zc + 0.3, WD)
    for yy in (yb + depth * 0.3, yb + depth * 0.7):
        bb(mb, F, xa, xb, yy - 0.25, yy + 0.25, zc - 0.5, zc, WD)
    bb(mb, F, xa, xb, yb, yf, z0, zf, TATAMI)
    for x in even(xa, xb, 3.0)[:-1]:
        xx = x + (xb - xa) / len(even(xa, xb, 3.0)) / 2
        bb(mb, F, xx - 0.07, xx + 0.07, yb, yf, zf - 0.05, zf + 0.12, WD)
    bb(mb, F, xa, xb, (yb + yf) / 2 - 0.07, (yb + yf) / 2 + 0.07, zf - 0.05, zf + 0.12, WD)
    # tokonoma
    xt = xa + (xb - xa) * (0.28 if _h01(seed, "toko") < 0.5 else 0.72)
    bb(mb, F, xt - 2.0, xt + 2.0, yb, yb + 1.4, zf, zf + 0.5, WM)
    bb(mb, F, xt - 2.2, xt + 2.2, yb, yb + 0.2, zf, zc, WD)
    bb(mb, F, xt - 0.7, xt + 0.7, yb + 0.2, yb + 0.3, zf + 1.6, zf + 5.4, CWHITE)
    bb(mb, F, xt - 0.5, xt + 0.5, yb + 0.29, yb + 0.33, zf + 2.4, zf + 4.4, INDIGO)
    for zz in (zf + 1.6, zf + 5.4):
        mb.rod(F.p(xt - 0.85, yb + 0.3, zz), F.p(xt + 0.85, yb + 0.3, zz), 0.08, WD, 6)
    pot6(mb, F, xt + 1.2, yb + 0.7, zf + 0.5, 0.35, 0.9, STD)
    for zz in (zf + 1.0, zc - 1.0):
        bb(mb, F, xt - 2.2, xt + 2.2, yb + 0.2, yb + 0.5, zz - 0.15, zz + 0.15, WD)
    # fusuma no resto do fundo
    for x in even(xa + 0.2, xb - 0.2, 3.0):
        if abs(x - xt) < 2.6:
            continue
        bb(mb, F, x - 1.35, x + 1.35, yb + 0.02, yb + 0.14, zf, zf + 6.0, PLS)
        for xx in (x - 1.35, x + 1.2):
            bb(mb, F, xx, xx + 0.15, yb + 0.14, yb + 0.26, zf, zf + 6.0, WD)
    # mesas baixas + zabuton + cha
    for j, xm in enumerate(even(xa + 1.5, xb - 1.5, 5.5)):
        ym = yb + depth * 0.58
        bb(mb, F, xm - 1.1, xm + 1.1, ym - 0.75, ym + 0.75, zf + 0.75, zf + 0.95, WM)
        for sx in (-1, 1):
            for sy in (-1, 1):
                bb(mb, F, xm + sx * 0.9 - 0.1, xm + sx * 0.9 + 0.1, ym + sy * 0.55 - 0.1, ym + sy * 0.55 + 0.1, zf,
                   zf + 0.75, WD)
        for sy in (-1, 1):
            bb(mb, F, xm - 0.55, xm + 0.55, ym + sy * 1.5 - 0.5, ym + sy * 1.5 + 0.5, zf, zf + 0.2,
               (CRED, INDIGO)[(j + (sy > 0)) % 2])
        pot6(mb, F, xm - 0.3, ym, zf + 0.95, 0.22, 0.4, PL)
        pot6(mb, F, xm + 0.35, ym + 0.2, zf + 0.95, 0.14, 0.25, STD)
    pts = [andon_floor(mb, F, xa + 1.0, yf - 1.6, zf, 1.0), andon_floor(mb, F, xb - 1.0, yf - 1.6, zf, 1.0)]
    pts.append(F.p(*hanging_lantern(mb, F, (xa + xb) / 2, yb + depth * 0.5, zc - 1.9, 0.5, 1.3, CWHITE)))
    if light_name:
        light(light_name, "POINT", F.p((xa + xb) / 2, yb + depth * 0.55, zc - 2.0), energy, WARM, 0.5)
    return pts


def _pine(mb, F, x, y, z, s=1.0):
    """pinheirinho de jardim podado (niwaki): tronco inclinado + 3 almofadas"""
    beam(mb, F, (x, y, z), (x + 0.6 * s, y, z + 2.4 * s), 0.45 * s, 0.45 * s, BARK)
    beam(mb, F, (x + 0.6 * s, y, z + 2.4 * s), (x - 0.4 * s, y + 0.3 * s, z + 4.0 * s), 0.36 * s, 0.36 * s, BARK)
    for px, py, pz, r in ((0.9, 0.0, 2.6, 1.3), (-0.6, 0.4, 4.1, 1.1), (0.3, -0.2, 5.0, 0.8)):
        mb.ico(r * s, F.p(x + px * s, y + py * s, z + pz * s), LEAF, 1, (1.25, 1.25, 0.55))


def chaya_bays(Wb, gs):
    """vaos da frente da casa de cha: trelica + FRENTE ABERTA + porta; predio estreito (< 16) perde a trelica para o
    vao aberto (interior de tatami) continuar largo (>= 5)"""
    bays = ([("koshi", 3.0)] if Wb >= 16.0 else []) + [{"t": "open", "head": 7.0}, ("door", 4.4)]
    return list(reversed(bays)) if gs < 0 else bays


def chaya(mb, F, W=22.0, D=16.0, roof_m=RPUR, garden_side=1, lod=0, seed=0, light_name=None, plaster=PLW,
          h0=9.0, h1=6.8, garden_w=7.0, sides=(False, False), noren=CRED, back=None, lim=None, hide_back=False):
    """(e) CASA DE CHA / ESTALAGEM: ENGAWA (varanda de tabuas) na frente sob hisashi em pilares, frente ABERTA com
    shoji corridos -> INTERIOR de tatami (mesas baixas, almofadas, tokonoma, andon acesos), KARAHAFU ondulado com
    remate dourado sobre a entrada, 2o piso com varanda VERMELHA e shoji acesos, irimoya + chidori, JARDIM lateral
    com cerca de bambu, pisantes, toro e pinheirinho. V2-3: sides = (lado -x, lado +x) expostos; o lado do predio
    encostado no vizinho e parede-meia (soco, hisashi e telhado cortados na divisa); o muro do jardim fica dentro."""
    gs = 1 if garden_side >= 0 else -1
    ph = 1.0
    z0, z1 = ph, ph + h0
    Wb = W - garden_w
    xb_ = -gs * garden_w / 2
    Fb = sub(F, xb_)
    cF = party_clip(W, sides, D, back, lim)
    cB = (cF[0] + xb_, cF[1] - xb_, cF[2], cF[3])              # limites no referencial do predio (Fb)
    pside = not sides[0 if gs > 0 else 1]                          # o lado do predio oposto ao jardim e divisa?
    eng = 3.0
    Din = D - eng
    Fg = sub(Fb, 0.0, -eng / 2)
    bays = chaya_bays(Wb, gs)
    xs, sp = _posts_x(Wb, bays)
    op = [(a, b) for t, o, a, b in sp if t == "open"][0]
    door = [(a, b) for t, o, a, b in sp if t == "door"][0]
    dx = (door[0] + door[1]) / 2
    # soco + engawa
    pa_ = 0.0 if (pside and gs > 0) else 0.35
    pb_ = 0.0 if (pside and gs < 0) else 0.35
    bb(mb, Fb, -Wb / 2 - pa_, Wb / 2 + pb_, -D / 2 - 0.35, D / 2 - eng + 0.35, -0.3, ph - 0.22, ST)
    bb(mb, Fb, -Wb / 2 - max(0.0, pa_ - 0.08), Wb / 2 + max(0.0, pb_ - 0.08), -D / 2 - 0.27, D / 2 - eng + 0.27,
       ph - 0.22, ph, STP)
    ze = ph + 0.45
    nbd = 5
    for i in range(nbd):
        y0 = D / 2 - eng + 0.3 + (eng - 0.3) * i / nbd
        bb(mb, Fb, -Wb / 2, Wb / 2, y0 + 0.03, y0 + (eng - 0.3) / nbd - 0.03, ze - 0.25, ze, WM)
    bb(mb, Fb, -Wb / 2, Wb / 2, D / 2 - 0.45, D / 2 + 0.05, ze - 0.75, ze - 0.24, WD)
    for x in even(-Wb / 2 + 0.6, Wb / 2 - 0.6, 3.6) + [-Wb / 2 + 0.6, Wb / 2 - 0.6]:
        bb(mb, Fb, x - 0.25, x + 0.25, D / 2 - 0.45, D / 2 - 0.0, -0.1, ze - 0.75, WD)
    for k, (yy, zz) in enumerate(((D / 2 + 1.0, ze * 0.66), (D / 2 + 2.2, ze * 0.33))):
        bb(mb, Fb, dx - 2.2 + 0.3 * k, dx + 2.2 - 0.3 * k, yy - 0.6, yy + 0.6, -0.2, zz, STP)
    sd = ["plaster", "shoji", "plaster"]
    fg = {"F": bays, "B": ["amado", "plain"]}
    fg["R" if gs > 0 else "L"] = sd
    fg["L" if gs > 0 else "R"] = sd if sides[0 if gs > 0 else 1] else "blind"
    party = ((pside and gs > 0), (pside and gs < 0))
    g = _body(mb, Fg, Wb, Din, z0, h0, fg, plaster, lod, True, 7.0, noren=noren, party=party,
              hide=HB if hide_back else ())
    # shoji corridos nas pontas do vao aberto
    Ffg = sub(Fg, 0.0, Din / 2)
    for xa_ in (op[0], op[1] - 2.0):
        _kumiko(mb, sub(Ffg, 0.0, -0.4), xa_, xa_ + 2.0, z0 + SILL_H, z0 + 7.0, True, 0.66, 1.0)
    pts = _interior_tea(mb, Fg, op[0], op[1], Din / 2 - 0.86, 6.6, z0, h0, seed, light_name, lim=Wb / 2 - 0.05)
    # hisashi em pilares sobre a engawa, aberto no meio para o karahafu da entrada
    zt = z1 + 0.8
    dep = eng + 0.6
    kx0, kx1 = dx - 3.6, dx + 3.6
    xl, xr = -Wb / 2 - (0.0 if party[0] else 0.15), Wb / 2 + (0.0 if party[1] else 0.15)
    for a, b in ((xl, kx0), (kx1, xr)):
        if b - a > 1.5:
            Fp = sub(Ffg, (a + b) / 2)
            pts_x = [p - (a + b) / 2 for p in (a + 0.6, b - 0.6)]
            en = (not (party[0] and a == xl), not (party[1] and b == xr))
            pent2(mb, Fp, b - a, dep, zt, roof_m, lod=lod, xs=pts_x, support="posts", post_z=ze, ends=en)
    _karahafu2(mb, sub(Ffg, dx), kx1 - kx0, dep, zt + 0.6, roof_m, 1.7, True, lod, post_z=0.0)
    for x in (kx0 + 1.4, kx1 - 1.4):
        hanging_lantern(mb, Ffg, x, dep - 1.1, zt - 2.7, 0.6, 1.5, CRED, 0.5)
    pts.append(andon_floor(mb, Fb, dx + (3.2 if gs > 0 else -3.2), D / 2 - 0.9, ze, 1.5))
    # 2o piso
    nb = max(3, int(round((Wb - 2) / 4.4)))
    u2 = [("plaster", 1.0)] + ["shoji"] * nb + [("plaster", 1.0)]
    f2 = {"F": u2, "B": ["plain"]}
    f2["R" if gs > 0 else "L"] = ["plain", "shoji", "plain"]
    f2["L" if gs > 0 else "R"] = ["plaster", "shoji", "plaster"] if sides[0 if gs > 0 else 1] else "blind"
    g2 = _body(mb, Fg, Wb, Din, z1, h1, f2, PL, max(lod, 1), True, upper=True, party=party,
              hide=HB if hide_back else ())
    F2 = sub(Ffg, 0.0, 0.0, z1)
    zd = 1.3
    xs2, _ = _posts_x(Wb, u2)
    for x in xs2:
        bracket2(mb, F2, x, -0.3, 1.9, zd - 0.25, 0.4, 0.55, WD, False)
    bb(mb, F2, -Wb / 2 + 0.2, Wb / 2 - 0.2, 0.05, 1.8, zd - 0.25, zd, WM)
    bb(mb, F2, -Wb / 2 + 0.1, Wb / 2 - 0.1, 1.5, 1.9, zd - 0.6, zd - 0.05, WD)
    rail2(mb, F2, [(-Wb / 2 + 0.45, 0.2), (-Wb / 2 + 0.45, 1.6), (Wb / 2 - 0.45, 1.6), (Wb / 2 - 0.45, 0.2)], 2.8, zd,
             3.0, LAC, True)
    r = roof2(mb, Fg, Wb, Din, z1 + h1, "irimoya", roof_m, ov=2.8, g_over=1.6, lod=lod, dg=0.42, rafters=False,
              chidori=None, brackets=xs2[1:-1], clip=(cB[0], cB[1], cB[2] - eng / 2, cB[3] + eng / 2))
    # jardim
    xg0 = gs * (W / 2 - garden_w) if gs > 0 else -W / 2
    xg1 = xg0 + garden_w
    Fz = F
    bb(mb, Fz, xg0 + 0.2, xg1 - 0.2, -D / 2 + 0.4, D / 2 - 0.2, -0.2, 0.15, "Stone_OP_Court")
    gate = (xg0 + 1.0, xg0 + 3.4) if gs > 0 else (xg1 - 3.4, xg1 - 1.0)
    bamboo_fence(mb, sub(Fz, (xg0 + gate[0]) / 2 if gs > 0 else (gate[1] + xg1) / 2, D / 2 - 0.1),
                 (gate[0] - xg0) if gs > 0 else (xg1 - gate[1]), 3.2)
    bamboo_fence(mb, sub(Fz, (gate[1] + xg1) / 2 if gs > 0 else (xg0 + gate[0]) / 2, D / 2 - 0.1),
                 (xg1 - gate[1]) if gs > 0 else (gate[0] - xg0), 3.2)
    xo = xg1 - 0.95 if gs > 0 else xg0 + 0.95                     # V2-3: muro + chapeu dentro do lote
    tsuiji(mb, sub(Fz, xo, 0.0, 0.0, math.pi / 2), D - 0.4, 4.2, roof_m)
    xm = (gate[0] + gate[1]) / 2
    for k, (yy, xx) in enumerate(((D / 2 - 1.6, xm), (D / 2 - 3.6, xm - gs * 0.6), (D / 2 - 5.6, xm + gs * 0.2),
                                  (D / 2 - 7.6, xm + gs * 1.2))):
        lathe(mb, Fz, (xx, yy, 0.12), [(0.85, 0.0), (0.8, 0.2)], 6, STP, 0.3 * k)
    toro2(mb, sub(Fz, (xg0 + xg1) / 2 + gs * 1.6, -1.0), None, 0.8)
    _pine(mb, Fz, (xg0 + xg1) / 2 - gs * 0.8, -D / 2 + 3.2, 0.15, 1.0)
    mb.rock(Fz.p((xg0 + xg1) / 2 + gs * 1.2, -D / 2 + 2.0, 0.4), (2.0, 1.4, 1.1), "Stone_OP", 1, jitter=0.2)
    info = _info("chaya", W, D, Fg, r, pts + g["glow"] + g2["glow"], [Ffg.p(dx, eng + 1.0, 0.0)])
    return info


def fundo(mb, F, W=10.0, D=10.0, roof_m=RB, tsuma=False, lod=1, seed=0, plaster=PLW, h0=8.0, sides=(False, False),
          back=None, lim=None, hide_back=False, hisashi=False):
    """(f) CASA PEQUENA DE FUNDO de quadra (barata): soco baixo, terreo com tabuado + porta + koshi, hisashi pequeno
    sobre a porta, telhado kirizuma em lod 1 (onda de 2 pontos), empenas de tabuado."""
    ph = 0.6
    z0 = ph
    bays = ["board", ("door", 4.4), "koshi"] if _h01(seed, "fd") < 0.5 else ["koshi", ("door", 4.4), "board"]
    xs, sp = _posts_x(W, bays)
    door = [(a, b) for t, o, a, b in sp if t == "door"][0]
    dx = (door[0] + door[1]) / 2
    party = (not sides[0], not sides[1])
    clip = party_clip(W, sides, D, back, lim)
    plinth(mb, F, W, D, ph, [(dx, 4.6)], party)
    sb = ["plaster", "board"]
    g = _body(mb, F, W, D, z0, h0, {"F": bays, "B": ["plaster", "amado"], "L": sb if sides[0] else "blind",
                                    "R": sb if sides[1] else "blind"}, plaster, lod, _h01(seed, "fl") < 0.5, 6.6,
              noren=INDIGO if _h01(seed, "nr") < 0.5 else None, party=party, hide=HB if hide_back else ())
    if hisashi:                                  # V2-3: hisashi continuo na frente toda (flag 'h' da planta)
        pent2(mb, sub(F, 0.0, D / 2), W + 0.3, 2.2, z0 + h0 - 0.2, roof_m, lod=lod, rafters=False, xs=xs,
              clip=clip[:2])
    else:
        pent2(mb, sub(F, dx, D / 2), 6.0, 1.8, z0 + h0 - 0.4, roof_m, lod=lod, rafters=False, xs=[-2.4, 2.4],
              clip=(clip[0] + dx, clip[1] - dx))
    if tsuma:
        r = roof2(mb, sub(F, ang=math.pi / 2), D, W, z0 + h0, "kirizuma", roof_m, ov=1.5, g_over=1.5, lod=max(lod, 1),
                  back_lod=1, ends=("plain", "board"), rafters=False, courses=1, ridge_w=1.8, clip=rot_clip(clip))
    else:
        r = roof2(mb, F, W, D, z0 + h0, "kirizuma", roof_m, ov=2.0, g_over=1.0, lod=max(lod, 1), back_lod=1,
                  ends=("board" if sides[0] else "plain", "board" if sides[1] else "plain"), rafters=False, courses=1,
                  ridge_w=1.8, clip=clip)
    return _info("fundo", W, D, F, r, g["glow"], g["doors"])


def portal2(mb, F, W=6.0, D=20.0, roof_m=RAZ, h=9.6, clear=7.4, lod=0, seed=0, sides=(False, False), back=None, lim=None,
            light_name=None):
    """(g) PASSAGEM COBERTA (V2-3, PLANO_V2 3.2: a viela atravessa a quadra sem abrir buraco na fachada): 2 porticos
    (frente e fundo) de pilares escuros em pedras-base, verga com placa (gaku) e noren curto, sala de cima de reboco
    com janela de trelica, forro de tabuas com vigas sobre o vao livre (>= clear), 2 chochin pendurados e telhado de
    empena para a rua (cortado na divisa dos 2 vizinhos). Origem no meio do lote, no chao da viela."""
    clip = party_clip(W, sides, D, back, lim)
    zt = h - PLATE_H
    for k, Fk in enumerate((sub(F, 0.0, D / 2), sub(F, 0.0, -D / 2, 0.0, math.pi))):
        for sx in (-1, 1):
            x = sx * (W / 2 - 0.52)
            bb(mb, Fk, x - 0.38, x + 0.38, -0.82, -0.06, 0.0, zt, WD)
            bb(mb, Fk, x - 0.5, x + 0.5, -0.94, 0.06, -0.2, 0.35, ST)
        bb(mb, Fk, -W / 2 + 0.04, W / 2 - 0.04, -0.9, 0.02, clear, clear + 0.55, WD)              # verga
        bb(mb, Fk, -W / 2 + 0.04, W / 2 - 0.04, -0.9, 0.12, zt, h, WD)                           # frechal
        bb(mb, Fk, -W / 2 + 0.8, W / 2 - 0.8, -0.72, -0.3, clear + 0.55, zt, PLW)                 # sala de cima
        ww = min(2.6, W - 2.4)
        bb(mb, Fk, -ww / 2 - 0.2, ww / 2 + 0.2, -0.5, -0.1, clear + 0.95, zt - 0.3, WD)
        _lattice(mb, Fk, -ww / 2, ww / 2, clear + 1.15, zt - 0.5, True, 0.42, 0.15, False)
        if k == 0:                                     # placa (gaku) e noren curto na boca da passagem
            bb(mb, Fk, -1.0, 1.0, -0.1, 0.12, clear - 1.3, clear - 0.1, WD)
            bb(mb, Fk, -0.8, 0.8, 0.12, 0.2, clear - 1.15, clear - 0.25, PLW)
            _noren(mb, Fk, -W / 2 + 0.9, W / 2 - 0.9, clear - 0.05, 1.1, INDIGO, 0.3)
    bb(mb, F, -W / 2 + 0.05, W / 2 - 0.05, -D / 2 + 0.8, D / 2 - 0.8, clear + 0.05, clear + 0.35, WM)      # forro
    for y in even(-D / 2 + 1.6, D / 2 - 1.6, 2.6):
        bb(mb, F, -W / 2 + 0.05, W / 2 - 0.05, y - 0.2, y + 0.2, clear - 0.35, clear + 0.06, WD)
    for sx in (-1, 1):                                 # laterais da sala de cima (rentes a divisa, dentro do lote)
        bb(mb, F, sx * (W / 2 - 0.45), sx * W / 2, -D / 2 + 0.82, D / 2 - 0.82, clear + 0.35, zt, PL)
    pts = [F.p(*hanging_lantern(mb, F, 0.0, y, clear - 1.6, 0.45, 1.2, CRED, 0.4)) for y in (-D / 4, D / 4)]
    if light_name:
        light(light_name, "POINT", F.p(0.0, 0.0, clear - 1.8), 25.0, WARM, 0.2)
    r = roof2(mb, sub(F, ang=math.pi / 2), D, W, h, "kirizuma", roof_m, ov=1.4, g_over=1.6, lod=max(lod, 1),
              back_lod=1, ends=("board", "board"), rafters=False, courses=1, ridge_w=1.8, s0=0.42, s1=0.9,
              clip=rot_clip(clip))
    return _info("portal", W, D, F, r, pts, [])


def haiden2(mb, F, W=18.0, D=20.0, roof_m=RREDV, lod=0, seed=0, light_name=None, sides=(True, True), back=None, lim=None,
            energy=55.0):
    """(h) HAIDEN do santuario NE (V2-3, PLANO_V2 3.4/3.5 - interior vivo): soco de pedra alto com escada de 4
    degraus, piso de tabuas elevado; frente ABERTA (gaihai) entre pilares de laca vermelha: caixa de oferendas
    (saisen-bako), corda do sino (suzu) com sino dourado, SHIMENAWA grossa com shide brancos, 2 chochin, barris de
    sake (komodaru) empilhados, quadro de ema; ao fundo, a parede de trelica vermelha do santuario interno com o
    altar (espelho dourado, sakaki, oferendas) e o forro de vigas. Irimoya grande + KARAHAFU dourado sobre a escada.
    Origem no meio do lote no chao; +y = frente."""
    clip = party_clip(W, sides, D, back, lim)
    ph = 1.6
    Do = D * 0.45                                     # frente aberta (onde se entra)
    yi = D / 2 - Do                                   # face do santuario interno
    bb(mb, F, -W / 2, W / 2, -D / 2, D / 2, -0.3, ph - 0.3, ST)
    bb(mb, F, -W / 2 + 0.08, W / 2 - 0.08, -D / 2 + 0.08, D / 2 - 0.08, ph - 0.3, ph - 0.12, STP)
    bb(mb, F, -W / 2 + 0.3, W / 2 - 0.3, -D / 2 + 0.3, D / 2 - 0.2, ph - 0.12, ph, WM)                  # assoalho
    for i in range(1, 5):                                                                                # escada
        zz = ph - 0.32 * i
        bb(mb, F, -3.6, 3.6, D / 2 + 0.4 * (i - 1) - 0.05, D / 2 + 0.4 * i, -0.3, zz, STP)
    for sx in (-1, 1):
        x0 = sx * 3.6
        bb(mb, F, x0 - 0.3, x0 + 0.3, D / 2, D / 2 + 1.7, -0.3, ph + 0.25, ST)
    zt = ph + 9.0
    xs = [-W / 2 + 0.6, -W / 4, 0.0, W / 4, W / 2 - 0.6]
    for y in (D / 2 - 0.6, yi):                       # pilares de laca: frente e linha do santuario interno
        for x in xs:
            if y == yi and abs(x) < 0.1:
                continue
            if y == D / 2 - 0.6 and abs(x) < 0.1:
                continue
            bb(mb, F, x - 0.42, x + 0.42, y - 0.42, y + 0.42, ph, zt, LAC)
            bb(mb, F, x - 0.55, x + 0.55, y - 0.55, y + 0.55, ph, ph + 0.35, WD)
    for y in (D / 2 - 0.6, yi):                                                     # nuki e verga
        bb(mb, F, -W / 2 + 0.2, W / 2 - 0.2, y - 0.3, y + 0.3, zt - 0.7, zt, LAC)
        bb(mb, F, -W / 2 + 0.2, W / 2 - 0.2, y - 0.22, y + 0.22, zt - 2.4, zt - 1.9, LAC)
    for sx in (-1, 1):                                                               # laterais da frente: guarda baixa
        x = sx * (W / 2 - 0.6)
        bb(mb, F, x - 0.18, x + 0.18, yi + 0.4, D / 2 - 1.0, ph + 2.6, ph + 2.9, LAC)
        bb(mb, F, x - 0.12, x + 0.12, yi + 0.4, D / 2 - 1.0, ph + 1.1, ph + 1.3, LAC)
        for y in even(yi + 0.6, D / 2 - 1.2, 1.4):
            bb(mb, F, x - 0.1, x + 0.1, y - 0.1, y + 0.1, ph, ph + 2.6, LAC)
    # santuario interno: paredes, trelica vermelha na frente com vao do altar
    bb(mb, F, -W / 2 + 0.2, W / 2 - 0.2, -D / 2 + 0.2, -D / 2 + 0.7, ph, zt, PLW)
    for sx in (-1, 1):
        x0, x1 = sorted((sx * (W / 2 - 0.7), sx * (W / 2 - 0.2)))
        bb(mb, F, x0, x1, -D / 2 + 0.2, yi, ph, zt, PLW)
        for y in even(-D / 2 + 1.0, yi - 0.4, 3.0):                                       # pilares aparentes
            p0, p1 = sorted((sx * (W / 2 - 0.45), sx * (W / 2 - 0.05)))
            bb(mb, F, p0, p1, y - 0.3, y + 0.3, ph, zt, WD)
    Fi = sub(F, 0.0, yi)
    for a, b in ((-W / 2 + 1.0, -2.6), (2.6, W / 2 - 1.0)):
        _lattice(mb, Fi, a, b, ph + 0.6, zt - 2.5, False, 0.5, 0.18, True)
        bb(mb, Fi, a, b, -0.5, -0.2, ph, ph + 0.6, LAC)
        bb(mb, Fi, a, b, -0.5, -0.2, zt - 2.5, zt - 0.7, PLW)
    bb(mb, F, -2.6, 2.6, -D / 2 + 0.7, yi - 0.4, zt - 0.5, zt - 0.2, WD)                        # forro do altar
    ya = yi - 3.2                                                                     # altar
    bb(mb, F, -2.2, 2.2, ya - 0.8, ya + 0.8, ph, ph + 1.6, LAC)
    bb(mb, F, -2.4, 2.4, ya - 0.95, ya + 0.95, ph + 1.6, ph + 1.8, WD)
    lathe_y(mb, sub(F, 0.0, ya - 0.4, 0.0, 0.0), (0.0, 0.0, ph + 3.2), [(1.0, -0.12), (1.0, 0.12)], 16, GOLD)
    bb(mb, F, -0.5, 0.5, ya - 0.55, ya - 0.25, ph + 1.8, ph + 2.2, WD)
    for sx in (-1, 1):                                                               # sakaki + oferendas
        pot6(mb, F, sx * 1.6, ya, ph + 1.8, 0.28, 0.7, PL)
        mb.ico(0.6, F.p(sx * 1.6, ya, ph + 3.0), "Leaf_OP_Pine", 1, (1.0, 1.0, 1.4))
        bb(mb, F, sx * 0.9 - 0.35, sx * 0.9 + 0.35, ya + 0.3, ya + 0.8, ph + 1.8, ph + 2.2, CWHITE)
    # frente aberta: caixa de oferendas, sino, shimenawa, chochin, barris de sake, ema
    ys = yi + 1.6
    bb(mb, F, -1.8, 1.8, ys - 0.7, ys + 0.7, ph, ph + 1.5, WD)
    for x in even(-1.6, 1.6, 0.36):
        bb(mb, F, x - 0.08, x + 0.08, ys - 0.72, ys + 0.72, ph + 1.5, ph + 1.62, WM)
    bb(mb, F, -1.9, 1.9, ys - 0.8, ys + 0.8, ph + 1.35, ph + 1.45, GOLD)
    zs = zt - 2.4
    lathe(mb, F, (0.0, D / 2 - 0.6, zs - 1.3), [(0.1, 0.0), (0.55, 0.15), (0.62, 0.55), (0.4, 0.95), (0.08, 1.1)], 8, GOLD)
    mb.rod(F.p(0.0, D / 2 - 0.6, zs - 1.3), F.p(0.0, D / 2 - 0.6, ph + 1.8), 0.13, CRED, 6)
    mb.rod(F.p(0.12, D / 2 - 0.6, zs - 1.3), F.p(0.2, D / 2 - 0.6, ph + 2.2), 0.1, CWHITE, 6)
    rope = [(x, D / 2 - 0.15, zs - 0.35 - 0.9 * (1.0 - (2.0 * x / (W - 2.0)) ** 2)) for x in
            [-(W / 2 - 1.0) + (W - 2.0) * i / 8 for i in range(9)]]
    sweep(mb, F, rope, [(-0.42, -0.42), (0.42, -0.42), (0.42, 0.42), (-0.42, 0.42)], STRAW)
    for x, y, z in rope[1:-1]:
        for j in range(3):                                                           # shide (papel em zigue-zague)
            bb(mb, F, x - 0.12 + 0.14 * (j % 2), x + 0.12 + 0.14 * (j % 2), y - 0.03, y + 0.03,
               z - 0.45 - 0.36 * (j + 1), z - 0.45 - 0.36 * j, CWHITE)
    pts = []
    for x in (-W / 4 - 1.2, W / 4 + 1.2):
        pts.append(F.p(*hanging_lantern(mb, F, x, D / 2 - 1.4, zt - 3.4, 0.55, 1.5, CWHITE, 0.6)))
    for sx in (-1, 1):                                                              # komodaru (barris de sake)
        xb_ = sx * (W / 2 - 2.4)
        for j, (dx_, dz_) in enumerate(((-0.8, 0.0), (0.8, 0.0), (0.0, 1.5))):
            lathe(mb, F, (xb_ + dx_, yi + 1.3, ph + dz_), [(0.72, 0.0), (0.75, 0.75), (0.72, 1.5)], 8,
                  (CWHITE, STRAW, CWHITE)[j])
            bb(mb, F, xb_ + dx_ - 0.5, xb_ + dx_ + 0.5, yi + 0.5, yi + 0.56, ph + dz_ + 0.3, ph + dz_ + 1.1, CRED)
    bb(mb, F, W / 2 - 1.2, W / 2 - 1.0, yi + 3.2, yi + 6.4, ph + 2.0, ph + 4.6, WD)                    # ema
    for k, y in enumerate(even(yi + 3.4, yi + 6.2, 0.6)):
        bb(mb, F, W / 2 - 1.36, W / 2 - 1.2, y - 0.24, y + 0.24, ph + 2.4 + 1.1 * (k % 2), ph + 3.0 + 1.1 * (k % 2),
           WM)
    bb(mb, F, -W / 2 + 0.3, W / 2 - 0.3, yi, D / 2 - 0.3, zt - 0.4, zt - 0.1, WD)                      # forro frente
    for x in even(-W / 2 + 0.6, W / 2 - 0.6, 2.4):
        bb(mb, F, x - 0.16, x + 0.16, yi, D / 2 - 0.3, zt - 0.85, zt - 0.4, WD)
    if light_name:
        light(light_name, "POINT", F.p(0.0, yi + Do * 0.5, zt - 3.0), energy, WARM, 0.5)
    r = roof2(mb, F, W, D, zt, "irimoya", roof_m, ov=2.8, g_over=1.6, lod=lod, dg=0.45, rafters=lod == 0,
              brackets=xs[1:-1], gold=True, gable_style="timber", clip=clip)
    _karahafu2(mb, sub(F, 0.0, D / 2 + 0.15), 8.4, 2.6, zt - 0.2, roof_m, 1.6, True, lod, post_z=None)
    return _info("santuario", W, D, F, r, pts, [F.p(0.0, D / 2 + 1.6, 0.0)])


def honden2(mb, F, W=10.0, D=10.0, roof_m=RREDV, lod=0, seed=0, sides=(True, True), back=None, lim=None):
    """(i) HONDEN (santuario principal, fechado): soco de pedra, corpo elevado de tabuas sobre pilares de laca,
    portas de trelica, varandinha e escada com corrimao vermelho, telhado de 2 aguas + hisashi em pilares sobre a
    escada (nagare), CHIGI e KATSUOGI na cumeeira, cerca TAMAGAKI vermelha em volta. Origem no meio do lote, no
    chao, +y = frente."""
    clip = party_clip(W, sides, D, back, lim)
    bb(mb, F, -W / 2, W / 2, -D / 2, D / 2, -0.3, 0.6, ST)
    bb(mb, F, -W / 2 + 0.08, W / 2 - 0.08, -D / 2 + 0.08, D / 2 - 0.08, 0.6, 0.75, STP)
    Wi, Di = W - 4.4, D - 5.0
    yc = -1.0
    Fc = sub(F, 0.0, yc)
    zf = 2.4
    for sx in (-1, 1):
        for sy in (-1, 1):
            bb(mb, Fc, sx * Wi / 2 - 0.25, sx * Wi / 2 + 0.25, sy * Di / 2 - 0.25, sy * Di / 2 + 0.25, 0.75, zf + 4.6, LAC)
    bb(mb, Fc, -Wi / 2 - 0.5, Wi / 2 + 0.5, -Di / 2 - 0.5, Di / 2 + 0.5, zf - 0.3, zf, WM)
    bb(mb, Fc, -Wi / 2 + 0.25, Wi / 2 - 0.25, -Di / 2 + 0.25, Di / 2 - 0.25, zf, zf + 4.3, WM)
    Fb_ = sub(Fc, 0.0, -Di / 2 + 0.25, 0.0, math.pi)
    for x in even(-Wi / 2 + 0.3, Wi / 2 - 0.3, 0.9):
        bb(mb, Fb_, x - 0.06, x + 0.06, -0.1, 0.02, zf, zf + 4.3, WD)
    Ff = sub(Fc, 0.0, Di / 2 - 0.25)
    _lattice(mb, Ff, -Wi / 2 + 0.4, Wi / 2 - 0.4, zf + 0.4, zf + 3.6, False, 0.45, 0.16, True)
    bb(mb, Ff, -Wi / 2 + 0.3, Wi / 2 - 0.3, -0.4, 0.12, zf + 3.6, zf + 4.3, LAC)
    q = Wi / 2 + 0.35                                                               # varandinha
    rail2(mb, Fc, [(-q, Di / 2 + 0.3), (-q, -Di / 2 - 0.3), (q, -Di / 2 - 0.3), (q, Di / 2 + 0.3)], 1.6, zf, 2.2, LAC,
          True)
    for i in range(1, 6):                                                           # escada de madeira
        zz = zf - 0.33 * i
        y0 = yc + Di / 2 + 0.5 + 0.42 * (i - 1)
        bb(mb, F, -1.5, 1.5, y0, y0 + 0.42, 0.75, max(0.95, zz), WM)
    for sx in (-1, 1):
        beam(mb, F, (sx * 1.6, yc + Di / 2 + 0.4, zf + 1.4), (sx * 1.6, yc + Di / 2 + 2.6, 2.1), 0.2, 0.2, LAC)
    zt = zf + 4.6
    ry = roof2(mb, Fc, Wi, Di, zt, "kirizuma", roof_m, ov=1.4, g_over=1.2, lod=max(lod, 1), back_lod=1,
               ends=("board", "board"), rafters=False, courses=1, ridge_w=1.6, s0=0.55, s1=1.0, gold=True,
               clip=(clip[0], clip[1], clip[2] + yc, clip[3] - yc))
    ye = Di / 2 + 0.12 + 1.4
    pent2(mb, sub(Fc, 0.0, ye - 0.3), Wi + 2.0, 2.0, ry["Hf"](0.0, ye - 0.3) - 0.55, roof_m, s=0.5, lod=1,
          rafters=False, xs=[-Wi / 2 - 0.4, Wi / 2 + 0.4], support="posts", post_z=0.75)
    zr = ry["zr"]
    for k, x in enumerate(even(-Wi / 2 + 0.6, Wi / 2 - 0.6, 1.4)):                   # katsuogi
        mb.rod(Fc.p(x, -0.7, zr + 1.3), Fc.p(x, 0.7, zr + 1.3), 0.28, GOLD if k % 2 else WD, 6)
    for sx in (-1, 1):                                                              # chigi (forquilha)
        for s2 in (-1, 1):
            beam(mb, Fc, (sx * (Wi / 2 + 0.9), 0.0, zr - 0.2), (sx * (Wi / 2 + 1.5), s2 * 0.7, zr + 2.2), 0.24, 0.24, WD)
    pts = [(-W / 2 + 0.4, D / 2 - 0.4), (-W / 2 + 0.4, -D / 2 + 0.4), (W / 2 - 0.4, -D / 2 + 0.4),
           (W / 2 - 0.4, D / 2 - 0.4), (2.2, D / 2 - 0.4)]
    rail2(mb, F, pts, 2.2, 0.75, 2.4, LAC, True)
    rail2(mb, F, [(-2.2, D / 2 - 0.4), (-W / 2 + 0.4, D / 2 - 0.4)], 2.2, 0.75, 2.4, LAC, True)
    return _info("honden", W, D, F, ry, [], [F.p(0.0, D / 2, 0.0)])


def mansao2(mb, F, W=30.0, D=24.0, roof_m=RG, lod=1, seed=0, sides=(True, True), back=None, lim=None,
            hide_back=False, gd=7.0, light_name=None):
    """(j) MANSAO do terraco alto (V2-3, PLANO_V2 3.2 "mansoes com muro de jardim"): sobrado largo de 3 pisos no
    fundo do lote (varanda vermelha, saia mokoshi, irimoya), JARDIM na frente fechado por muro TSUIJI com PORTAO de
    telhadinho, pisantes do portao a porta e 2 pinheirinhos podados. Origem no meio do lote, +y = frente."""
    Fh = sub(F, 0.0, -gd / 2)
    info = sobrado(mb, Fh, min(W - 2.0, 16.0), D - gd, roof_m, shop=False, rail_m=LAC, sides=(True, True), lod=lod,
                   seed=seed,
                   back=None if back is None else back - gd / 2, chidori=lod == 0, hide_back=hide_back)
    gw = 5.0
    yw = D / 2 - 1.5                                  # V2-3: muro, chapeu e portao DENTRO do lote (colisao cobre)
    Lw = W / 2 - gw / 2 - 1.4
    for s in (-1, 1):
        tsuiji(mb, sub(F, s * (gw / 2 + 0.2 + Lw / 2), yw), Lw, 4.2, roof_m)
        tsuiji(mb, sub(F, s * (W / 2 - 1.3), yw - gd / 2 + 1.1, 0.0, math.pi / 2), gd - 2.2, 4.2, roof_m)
    for s in (-1, 1):                                          # portao (2 pilares + verga + telhadinho)
        x = s * (gw / 2 - 0.1)
        bb(mb, F, x - 0.35, x + 0.35, yw - 0.35, yw + 0.35, 0.0, 5.6, WD)
        rock_base(mb, F, x, yw, 0.0, 0.6, 0.35)
    bb(mb, F, -gw / 2 - 0.3, gw / 2 + 0.3, yw - 0.3, yw + 0.3, 4.9, 5.4, WD)
    for s in (-1, 1):
        bx(mb, F, 0.0, yw + s * 0.62, 6.0, gw + 1.6, 1.45, 0.2, roof_m, 0.0, rx=-s * 0.55)
    bb(mb, F, -gw / 2 - 0.9, gw / 2 + 0.9, yw - 0.18, yw + 0.18, 6.25, 6.6, RR)
    for k in range(4):                                         # pisantes
        lathe(mb, F, (0.4 * (k % 2) - 0.2, yw - 1.4 - k * 1.5, 0.12), [(0.8, 0.0), (0.75, 0.18)], 6, STP, 0.4 * k)
    for s in (-1, 1):
        _pine(mb, F, s * W / 3.2, yw - gd / 2 - 0.2, 0.1, 1.2)
    info["kind"] = "mansao"
    return info


BUILD = {"loja": loja, "sobrado": sobrado, "esquina": esquina, "kura": kura, "chaya": chaya, "fundo": fundo,
         "portal": portal2, "santuario": haiden2, "honden": honden2, "mansao": mansao2}
FOOTPRINT = {"loja": (14.0, 16.0), "sobrado": (16.0, 16.0), "esquina": (16.0, 16.0), "kura": (10.0, 14.0),
             "chaya": (22.0, 16.0), "fundo": (10.0, 10.0)}


def build(mb, F, kind, **kw):
    """monta o tipo 'kind' (BUILD) com os parametros kw"""
    return BUILD[kind](mb, F, **kw)


def footprint(kind, **kw):
    """(W, D) do lote ocupado pelas paredes (os beirais passam ~2,6 na frente e g_over nas laterais)"""
    W, D = FOOTPRINT[kind]
    return kw.get("W", W), kw.get("D", D)


# ================================================================== PECAS PEQUENAS (<= 600 tris)
def tsuiji(mb, F, L, h=4.2, roof_m=RB):
    """MURO TSUIJI de jardim: soco de pedra, pano de reboco com faixas, chapeu de telha de 2 aguas (tabuas) com
    cumeeira. F no meio, ao longo de x"""
    bb(mb, F, -L / 2, L / 2, -0.5, 0.5, -0.2, 0.6, ST)
    bb(mb, F, -L / 2 + 0.05, L / 2 - 0.05, -0.4, 0.4, 0.6, h, PLW)
    for zz in (h - 1.2, h - 0.75):
        bb(mb, F, -L / 2 + 0.05, L / 2 - 0.05, -0.46, 0.46, zz - 0.08, zz + 0.08, PL)
    for s in (-1, 1):
        bx(mb, F, 0.0, s * 0.42, h + 0.22, L + 0.4, 1.0, 0.18, roof_m, 0.0, rx=-s * 0.5)
    bb(mb, F, -L / 2 - 0.2, L / 2 + 0.2, -0.16, 0.16, h + 0.38, h + 0.62, RR)


def bamboo_fence(mb, F, L, h=3.2, step=2.0):
    """CERCA BAIXA DE BAMBU (yotsume-gaki): mouroes de madeira, 3 travessas e montantes de bambu (6 lados) amarrados
    (amarras escuras). F no meio, ao longo de x"""
    for x in [-L / 2 + 0.2] + even(-L / 2 + 0.2, L / 2 - 0.2, 3.2)[1:-1] + [L / 2 - 0.2]:
        bb(mb, F, x - 0.2, x + 0.2, -0.2, 0.2, -0.2, h + 0.15, WD)
    for zz in (h * 0.3, h * 0.62, h * 0.92):
        mb.rod(F.p(-L / 2 + 0.05, 0.25, zz), F.p(L / 2 - 0.05, 0.25, zz), 0.11, STRAW, 6)
    for x in even(-L / 2 + 0.6, L / 2 - 0.6, step):
        mb.rod(F.p(x, 0.0, -0.1), F.p(x, 0.0, h + 0.25), 0.12, STRAW, 6)
def _gibo(mb, F, x, y, z, s=1.0, m=GOLD):
    """giboshi leve (6 lados): colar, bulbo, ponta"""
    lathe(mb, F, (x, y, z), [(0.24 * s, 0.0), (0.18 * s, 0.14), (0.28 * s, 0.32), (0.12 * s, 0.6), (0.02 * s, 0.78)], 6, m)


def lamp_andon(mb, F, light_name=None, energy=30.0, h=4.6):
    """ANDON DE POSTE BAIXO (~4,6): pedestal de pedra em 2 degraus, fuste de madeira com colar, mesa com 4 maos-
    francesas, CAIXA DE PAPEL em armacao (montantes, travessas, kumiko em cruz em cada face, papel aceso RECUADO
    0,14), chapeu de 4 aguas com beiral e ponteira. F no pe."""
    bb(mb, F, -0.75, 0.75, -0.75, 0.75, -0.2, 0.42, STP)
    bb(mb, F, -0.52, 0.52, -0.52, 0.52, 0.42, 0.78, ST)
    zt = h - 2.05
    bb(mb, F, -0.24, 0.24, -0.24, 0.24, 0.78, zt, WD)
    bb(mb, F, -0.3, 0.3, -0.3, 0.3, 1.0, 1.22, IRON)
    bb(mb, F, -0.66, 0.66, -0.66, 0.66, zt, zt + 0.16, WD)
    for a in range(4):
        dx, dy = ((1, 0), (0, 1), (-1, 0), (0, -1))[a]
        beam(mb, F, (dx * 0.2, dy * 0.2, zt - 0.85), (dx * 0.55, dy * 0.55, zt - 0.02), 0.12, 0.12, WD)
    z0, hz, hx = zt + 0.16, 1.55, 0.52
    bb(mb, F, -hx + 0.14, hx - 0.14, -hx + 0.14, hx - 0.14, z0 + 0.12, z0 + hz - 0.12, LGLOW)
    for sx in (-1, 1):
        for sy in (-1, 1):
            bb(mb, F, sx * hx - 0.09, sx * hx + 0.09, sy * hx - 0.09, sy * hx + 0.09, z0, z0 + hz, WD)
    for zz in (z0, z0 + hz - 0.12):
        bb(mb, F, -hx, hx, -hx, hx, zz, zz + 0.12, WD)
    bb(mb, F, -0.05, 0.05, -hx - 0.02, hx + 0.02, z0 + 0.12, z0 + hz - 0.12, WD)      # kumiko: montante do meio
    bb(mb, F, -hx - 0.02, hx + 0.02, -0.05, 0.05, z0 + 0.12, z0 + hz - 0.12, WD)
    bb(mb, F, -hx - 0.02, hx + 0.02, -hx - 0.02, hx + 0.02, z0 + hz * 0.5 - 0.05, z0 + hz * 0.5 + 0.05, WD)
    zr = hip_cap(mb, F, (0.0, 0.0), hx + 0.05, hx + 0.05, z0 + hz, 0.42, 0.5, 0.12, RR, 0.14, 1)
    lathe(mb, F, (0, 0, zr - 0.06), [(0.16, 0.0), (0.2, 0.12), (0.08, 0.3), (0.02, 0.5)], 6, IRON)
    c = F.p(0.0, 0.0, z0 + hz * 0.5)
    if light_name:
        light(light_name, "POINT", c, energy, WARM, 0.3)
    return c


def lamp_post(mb, F, light_name=None, energy=35.0, h=7.6, arm=1.6):
    """POSTE DE MADEIRA com CHOCHIN SOB TELHADINHO: pedra-base (soseki) oitavada, poste com chanfro e 1 cinta,
    chapeuzinho de 2 aguas no topo, braco (com mao-francesa) que leva um telhadinho proprio de 2 aguas sobre o
    chochin vermelho pendurado. F no pe; o braco aponta para +x."""
    rock_base(mb, F, 0.0, 0.0, 0.0, 0.85, 0.5)
    bb(mb, F, -0.27, 0.27, -0.27, 0.27, 0.35, h, WD)
    bb(mb, F, -0.32, 0.32, -0.32, 0.32, 1.3, 1.5, IRON)
    for s in (-1, 1):                                                   # chapeu do poste
        bx(mb, F, 0.0, s * 0.36, h + 0.22, 0.95, 0.8, 0.14, RR, 0.0, rx=-s * 0.6)
    bb(mb, F, -0.5, 0.5, -0.07, 0.07, h + 0.4, h + 0.52, RR)
    za = h - 0.9
    bb(mb, F, 0.0, arm + 0.55, -0.13, 0.13, za - 0.28, za, WD)
    beam(mb, F, (0.2, 0.0, za - 1.5), (arm * 0.6, 0.0, za - 0.26), 0.13, 0.15, WD)
    for s in (-1, 1):                                                   # telhadinho sobre o chochin
        bx(mb, F, arm, s * 0.42, za + 0.3, 1.25, 0.95, 0.13, RR, 0.0, rx=-s * 0.62)
    bb(mb, F, arm - 0.62, arm + 0.62, -0.07, 0.07, za + 0.48, za + 0.6, RR)
    bb(mb, F, arm - 0.08, arm + 0.08, -0.08, 0.08, za, za + 0.4, WD)
    mb.rod(F.p(arm, 0.0, za - 0.26), F.p(arm, 0.0, za - 0.6), 0.04, IRON, 4)
    c = chochin2(mb, F, (arm, 0.0, za - 0.6 - 1.5), 0.55, 1.5, CRED, 8)
    if light_name:
        light(light_name, "POINT", F.p(*c), energy, WARM, 0.25)
    return F.p(*c)


def eave_lantern(mb, Ff, x, z, light_name=None, energy=20.0, out=1.1, body=CRED):
    """CHOCHIN DE BEIRAL: espelho e braco de madeira com mao-francesa saindo da parede, gancho e chochin. Ff na face
    do pilar (+y fora), z = altura do braco"""
    bb(mb, Ff, x - 0.2, x + 0.2, -0.1, 0.1, z - 1.0, z + 0.3, WD)
    bb(mb, Ff, x - 0.1, x + 0.1, -0.05, out + 0.15, z - 0.2, z, WD)
    beam(mb, Ff, (x, 0.05, z - 0.95), (x, out * 0.65, z - 0.18), 0.1, 0.12, WD)
    mb.rod(Ff.p(x, out, z - 0.2), Ff.p(x, out, z - 0.45), 0.035, IRON, 4)
    c = chochin2(mb, Ff, (x, out, z - 0.45 - 1.25), 0.45, 1.25, body)
    if light_name:
        light(light_name, "POINT", Ff.p(*c), energy, WARM, 0.15)
    return Ff.p(*c)


def toro2(mb, F, light_name=None, s=1.0, energy=30.0, m=ST):
    """TORO DE PEDRA (kasuga): base sextavada, fuste com anel do meio, chudai, CAIXA DE FOGO com 6 montantes e
    janelas recortadas (nucleo aceso recuado + 2 paineis cheios com janela redonda), kasa com 6 cantos levantados
    (warabite) e hoju. F no pe; s = escala (1 ~ 6,6 de altura)"""
    S_ = lambda prof: [(r * s, z * s) for r, z in prof]
    lathe(mb, F, (0, 0, 0), S_([(1.25, -0.15), (1.25, 0.35), (0.95, 0.6), (0.6, 0.72)]), 6, m)
    lathe(mb, F, (0, 0, 0), S_([(0.42, 0.7), (0.38, 1.7), (0.5, 1.8), (0.5, 1.95), (0.36, 2.05), (0.36, 2.8)]), 6, m, 0.52)
    lathe(mb, F, (0, 0, 0), S_([(0.5, 2.78), (1.0, 3.15), (1.0, 3.42)]), 6, m)
    z0, z1, rc = 3.42 * s, 4.75 * s, 0.82 * s
    lathe(mb, F, (0, 0, 0), [(rc * 0.55, z0), (rc * 0.55, z1)], 6, LGLOW)
    for i in range(6):
        a = 2 * math.pi * i / 6
        bx(mb, F, rc * 0.88 * math.cos(a), rc * 0.88 * math.sin(a), (z0 + z1) / 2, 0.3 * s, 0.3 * s, z1 - z0, m, 0.0, rz=a)
    ap = rc * math.cos(math.pi / 6) * 0.86
    for i in (1, 4):
        a = 2 * math.pi * (i + 0.5) / 6
        Fp = sub(F, ap * math.cos(a), ap * math.sin(a), 0.0, a - math.pi / 2)
        for xa, xb, za, zb in ((-0.4, 0.4, 0.0, 0.35), (-0.4, 0.4, 0.95, 1.33), (-0.4, -0.22, 0.35, 0.95),
                               (0.22, 0.4, 0.35, 0.95)):
            bb(mb, Fp, xa * s, xb * s, -0.08 * s, 0.08 * s, z0 + za * s, z0 + zb * s, m)
    kz = z1
    lathe(mb, F, (0, 0, kz), S_([(0.9, 0.0), (1.75, 0.16), (1.75, 0.34), (1.2, 0.62), (0.55, 0.98), (0.4, 1.08)]), 6, m)
    for i in range(6):
        a = 2 * math.pi * i / 6
        bx(mb, F, 1.72 * s * math.cos(a), 1.72 * s * math.sin(a), kz + 0.42 * s, 0.34 * s, 0.26 * s, 0.4 * s, m, 0.0,
           ry=-0.7, rz=a)
    hz = kz + 1.06 * s
    lathe(mb, F, (0, 0, hz), S_([(0.3, 0.0), (0.42, 0.14), (0.28, 0.26), (0.38, 0.42), (0.32, 0.62), (0.12, 0.82),
                                 (0.02, 0.95)]), 6, m)
    c = F.p(0.0, 0.0, (z0 + z1) / 2)
    if light_name:
        light(light_name, "POINT", c, energy, WARM, 0.2)
    return c


def well2(mb, F, roof_m=RTEAL):
    """POCO: bocal de pedra em ANEL (10 lados) com boca escura, capa de lajes, tampa de tabuas sobre metade, 2
    esteios em pedras-base, viga de cumeeira, SARILHO (eixo + tambor + manivela), corda ate o balde apoiado na borda,
    telhadinho de 2 aguas ONDULADO apoiado nos esteios (tabeiras e cumeeira). F no centro do bocal"""
    n = 10
    ro, ri, hb = 1.7, 1.25, 1.45
    rings = []
    for rr, zz in ((ro, -0.1), (ro, hb - 0.2), (ri, hb - 0.2), (ri, hb - 0.75)):
        rings.append([(rr * math.cos(2 * math.pi * j / n), rr * math.sin(2 * math.pi * j / n), zz) for j in range(n)])
    rings.append(rings[0])
    loft(mb, F, rings, ST, caps=(False, False))
    lathe(mb, F, (0, 0, hb - 0.76), [(ri + 0.02, 0.0), (ri + 0.02, 0.01)], n, CBLACK)
    lathe(mb, F, (0, 0, hb - 0.2), [(ro + 0.12, -0.02), (ro + 0.12, 0.2), (ri - 0.08, 0.2), (ri - 0.08, 0.0)], n, STP)
    for k in range(3):                                                  # tampa: 3 tabuas sobre a metade -x
        y0 = -1.35 + k * 0.9
        bb(mb, F, -ro - 0.05, -0.05, y0 + 0.04, y0 + 0.86, hb, hb + 0.2, WM)
    bb(mb, F, -1.0, -0.82, -1.4, 1.4, hb + 0.2, hb + 0.34, WD)
    ph = 4.5
    for s in (-1, 1):
        y = s * (ro + 0.4)
        bb(mb, F, -0.5, 0.5, y - 0.5, y + 0.5, -0.1, 0.3, ST)
        bb(mb, F, -0.2, 0.2, y - 0.2, y + 0.2, 0.3, ph, WD)
        beam(mb, F, (0.0, y, ph - 1.3), (0.0, y - s * 0.9, ph - 0.05), 0.14, 0.16, WD)
    bb(mb, F, -0.24, 0.24, -ro - 0.8, ro + 0.8, ph, ph + 0.3, WD)
    za = 3.0
    mb.rod(F.p(0.0, -ro - 0.62, za), F.p(0.0, ro + 0.62, za), 0.09, WD, 6)
    lathe_y(mb, F, (0.0, 0.0, za), [(0.36, -0.5), (0.36, 0.5)], 6, WM)
    beam(mb, F, (0.0, ro + 0.62, za), (0.0, ro + 0.62, za - 0.65), 0.1, 0.1, WD)
    beam(mb, F, (0.0, ro + 0.62, za - 0.65), (0.0, ro + 1.15, za - 0.65), 0.1, 0.1, WD)
    mb.rod(F.p(0.36, 0.1, za), F.p(0.6, 0.35, hb + 1.0), 0.04, STRAW, 4)
    lathe(mb, F, (0.6, 0.35, hb), [(0.3, 0.0), (0.38, 0.85)], 6, WM)
    lathe(mb, F, (0.6, 0.35, hb + 0.5), [(0.4, -0.06), (0.4, 0.06)], 6, IRON)
    # telhadinho: 2 placas onduladas lod 1 (cumeeira ao longo de y), tabeiras, cumeeira
    zt = ph + 0.3 + 1.0
    X, Y = 1.7, ro + 1.3
    Hs = lambda u, v: zt - 0.62 * abs(v)
    for Fk in (sub(F, 0.0, 0.0, 0.0, -math.pi / 2), sub(F, 0.0, 0.0, 0.0, math.pi / 2)):
        tiles(mb, Fk, _wave(-Y, Y, 1.6, 0.18, 1), lambda u: 0.0, X, Hs, roof_m, 0.26, rows=(0.0, 1.0), coarse=9.0)
    for s in (-1, 1):
        strip(mb, F, [(0.0, s * (Y - 0.1), zt - 0.26), (X, s * (Y - 0.1), Hs(0, X) - 0.26)], (0, 1, 0), -0.12, 0.12,
              -0.45, 0.04, WD)
        strip(mb, F, [(0.0, s * (Y - 0.1), zt - 0.26), (-X, s * (Y - 0.1), Hs(0, X) - 0.26)], (0, 1, 0), -0.12, 0.12,
              -0.45, 0.04, WD)
    bb(mb, F, -0.3, 0.3, -Y - 0.1, Y + 0.1, zt - 0.1, zt + 0.3, RR)
    return F.p(0.0, 0.0, 0.0)


def bridge2(mb, F, span=10.0, width=6.0, rise=1.4, bank_z=0.0, water_z=-1.6, bed_z=-2.6, m=LAC):
    """PONTE EM ARCO laqueada que VENCE O VAO: encontros de pedra FORA do vao (nas duas margens, do leito ate a
    margem, com capa), tabuleiro curvo (laca vermelha nas faces, tabuado por cima) que nasce no nivel das margens e
    sobe 'rise' no meio, arcos laterais por baixo, guarda-corpo vermelho curvo com giboshi dourado nas pontas.
    F no meio do canal, z=0 = nivel das margens, vao ao longo de x (margens em x = +-span/2)."""
    hs = span / 2
    ab = 2.2
    for s in (-1, 1):                                                  # encontros (abutments)
        x0, x1 = sorted((s * hs, s * (hs + ab)))
        bb(mb, F, x0, x1, -width / 2 - 0.6, width / 2 + 0.6, bed_z, bank_z - 0.25, ST)
        bb(mb, F, x0 - 0.1, x1 + 0.1, -width / 2 - 0.7, width / 2 + 0.7, bank_z - 0.25, bank_z + 0.05, STP)
    L = hs + ab
    zd = lambda x: bank_z + rise * (1.0 - (x / L) ** 2) ** 0.85 + 0.05
    N = 8
    xs = [-L + 2 * L * i / N for i in range(N + 1)]
    for (w2, z0, z1, mm) in ((width / 2 + 0.2, -0.75, -0.08, m), (width / 2 - 0.15, -0.1, 0.06, WM)):
        rings = []
        for x in xs:
            z = zd(x)
            rings.append([(x, -w2, z + z0), (x, w2, z + z0), (x, w2, z + z1), (x, -w2, z + z1)])
        loft(mb, F, rings, mm)
    for x in xs[1:-1]:                                                  # frisos escuros entre as tabuas
        sl = -2 * 0.85 * rise * x / (L * L) / max(0.05, (1.0 - (x / L) ** 2) ** 0.15)
        bx(mb, F, x, 0.0, zd(x) + 0.04, 0.14, width - 0.4, 0.1, WD, 0.0, ry=-math.atan(sl))
    for s in (-1, 1):                                                  # arcos laterais por baixo
        y = s * (width / 2 + 0.05)
        arc = [(x, y, bank_z - 0.45 + (zd(x) - 1.0 - bank_z + 0.45) * (1 - (x / hs) ** 2)) for x in
               [-hs + 2 * hs * i / 6 for i in range(7)]]
        sweep(mb, F, arc, [(-0.16, -0.3), (0.16, -0.3), (0.16, 0.3), (-0.16, 0.3)], m)
    rh = 2.6
    for s in (-1, 1):
        y = s * (width / 2 - 0.05)
        posts = [-L + 0.3, 0.0, L - 0.3]
        for x in posts:
            bb(mb, F, x - 0.22, x + 0.22, y - 0.22, y + 0.22, zd(x) - 0.1, zd(x) + rh, m)
        rail = [(x, y, zd(x) + rh - 0.1) for x in xs]
        sweep(mb, F, rail, [(-0.2, -0.14), (0.2, -0.14), (0.2, 0.14), (-0.2, 0.14)], m)
        for x in (posts[0], posts[-1]):
            lathe(mb, F, (x, y, zd(x) + rh), [(0.24, 0.0), (0.3, 0.25), (0.1, 0.55), (0.02, 0.72)], 6, GOLD)
    return dict(apex_z=F.o.z + zd(0.0), ends=(F.p(-L, 0, bank_z), F.p(L, 0, bank_z)))


def stall2(mb, F, light_name=None, roof=CRED):
    """BANCA DE RUA: tampo de tabuas com quadro, 4 pernas com travessas, prateleira baixa com caixas, mercadoria
    APOIADA (potes, rolos, caixas), 2 esteios atras + toldo de pano listrado inclinado, chochin pendurado. F no
    meio da frente do tampo (+y = freguesia)"""
    W, Dp, ht = 4.4, 1.8, 2.6
    bb(mb, F, -W / 2, W / 2, -Dp, 0.0, ht - 0.18, ht, WM)
    bb(mb, F, -W / 2 + 0.1, W / 2 - 0.1, -Dp + 0.1, -0.1, ht - 0.45, ht - 0.18, WD)
    for sx in (-1, 1):
        for y in (-Dp + 0.2, -0.2):
            bb(mb, F, sx * (W / 2 - 0.25) - 0.12, sx * (W / 2 - 0.25) + 0.12, y - 0.12, y + 0.12, 0.0, ht - 0.45, WD)
    bb(mb, F, -W / 2 + 0.2, W / 2 - 0.2, -Dp + 0.15, -0.15, 0.6, 0.78, WM)
    box_goods(mb, F, -1.0, -Dp / 2, 0.78, 1.2, 1.0, 0.7, STRAW, WD)
    box_goods(mb, F, 0.6, -Dp / 2, 0.78, 1.0, 1.0, 0.55, WM, WD)
    pot6(mb, F, -1.4, -0.7, ht, 0.36, 0.8, STD)
    pot6(mb, F, -0.6, -0.9, ht, 0.28, 0.6, PL)
    bolt_row(mb, F, 0.1, 1.9, -0.9, ht, 0.5)
    hb = 5.6
    for sx in (-1, 1):
        bb(mb, F, sx * (W / 2 - 0.15) - 0.13, sx * (W / 2 - 0.15) + 0.13, -Dp - 0.3, -Dp + 0.0, 0.0, hb, WD)
    bb(mb, F, -W / 2 - 0.1, W / 2 + 0.1, -Dp - 0.3, -Dp, hb - 0.25, hb, WD)
    n = 5
    w = (W + 0.6) / n
    dep, drop = 3.0, 1.2
    ang = math.atan2(drop, dep)
    for i in range(n):
        xx = -(W + 0.6) / 2 + (i + 0.5) * w
        bx(mb, F, xx, -Dp - 0.15 + dep / 2, hb - drop / 2 + 0.05, w + 0.01, math.hypot(dep, drop), 0.1,
           (roof, CWHITE)[i % 2], 0.0, rx=-ang)
        bb(mb, F, xx - w / 2 + 0.02, xx + w / 2 - 0.02, -Dp - 0.2 + dep - 0.05, -Dp - 0.2 + dep + 0.05, hb - drop - 0.6,
           hb - drop + 0.05, (roof, CWHITE)[i % 2])
    for sx in (-1, 1):
        beam(mb, F, (sx * (W / 2 - 0.15), -Dp - 0.15, hb - 1.6), (sx * (W / 2 - 0.15), -Dp + dep - 0.4, hb - drop - 0.05),
             0.12, 0.14, WD)
    c = hanging_lantern(mb, F, 1.6, -0.4, hb - drop - 1.2, 0.36, 0.9, CRED, 0.3)
    if light_name:
        light(light_name, "POINT", F.p(*c), 20.0, WARM, 0.15)
    return F.p(*c)


def barrel2(mb, F, x, y, z, r=0.72, h=1.55, lying=False):
    if lying:
        Fb = sub(F, x, y, z + r, 0.0)
        mb.rod(Fb.p(-h / 2, 0, 0), Fb.p(h / 2, 0, 0), r, WM, 8)
        for xx in (-h * 0.3, h * 0.3):
            mb.rod(Fb.p(xx - 0.06, 0, 0), Fb.p(xx + 0.06, 0, 0), r + 0.1, WD, 8)
        return
    lathe(mb, F, (x, y, z), [(r * 0.88, 0.0), (r, h * 0.5), (r * 0.88, h), (r * 0.78, h - 0.08)], 8, WM)
    for zz in (h * 0.2, h * 0.8):
        lathe(mb, F, (x, y, z + zz), [(r * 0.95 + 0.12, -0.08), (r * 0.95 + 0.12, 0.08)], 8, WD)


def tawara(mb, F, x, y, z, ang=0.0, r=0.55, L=1.6):
    """fardo de arroz (tawara): cilindro de palha deitado, tampas mais escuras, 2 amarras"""
    Fb = sub(F, x, y, z + r, ang)
    mb.rod(Fb.p(-L / 2, 0, 0), Fb.p(L / 2, 0, 0), r, STRAW, 8)
    for xx in (-L * 0.25, L * 0.25):
        mb.rod(Fb.p(xx - 0.06, 0, 0), Fb.p(xx + 0.06, 0, 0), r + 0.07, WM, 8)


def goods_pile(mb, F, kind="barrels"):
    """carga em pilha (cais, fundos de loja): 'barrels' = 3 barris em pe + 1 deitado + 2 tawara; 'crates' = caixas
    empilhadas desencontradas + tawara em piramide"""
    if kind == "barrels":
        barrel2(mb, F, -0.9, 0.0, 0.0)
        barrel2(mb, F, 0.75, -0.2, 0.0)
        barrel2(mb, F, -0.1, 1.25, 0.0, 0.62, 1.3)
        barrel2(mb, F, 0.2, -1.6, 0.0, 0.6, 1.4, True)
        tawara(mb, F, 2.3, 0.6, 0.0, 1.5)
        tawara(mb, F, 2.3, -0.6, 0.0, 1.5)
    else:
        box_goods(mb, F, -0.8, 0.0, 0.0, 1.5, 1.2, 1.0, WM, WD)
        box_goods(mb, F, 0.8, 0.1, 0.0, 1.4, 1.2, 0.9, WM, WD)
        box_goods(mb, F, -0.1, 0.0, 1.0, 1.3, 1.1, 0.9, STRAW, WD)
        for i, (x, zz) in enumerate(((2.4, 0.0), (3.5, 0.0), (2.95, 0.95))):
            tawara(mb, F, x, 0.0, zz, math.pi / 2, 0.5, 1.5)


def nobori2(mb, F, h=9.0, cloth=CWHITE, band=INDIGO, cw=1.5):
    """ESTANDARTE (nobori) com SUPORTE REAL: base de pedra com colar, mastro sextavado, braco de cima (chichi),
    pano preso por 4 aneis no mastro e alcas no braco, faixa de cor no topo e barra de peso. F no pe; pano para +x"""
    bb(mb, F, -0.7, 0.7, -0.7, 0.7, -0.2, 0.5, ST)
    lathe(mb, F, (0, 0, 0.5), [(0.36, 0.0), (0.36, 0.35), (0.22, 0.45)], 6, IRON)
    lathe(mb, F, (0, 0, 0.5), [(0.17, 0.0), (0.14, h - 0.5)], 6, WD)
    _gibo(mb, F, 0.0, 0.0, h, 0.8)
    zt = h - 0.5
    bb(mb, F, -0.1, cw + 0.45, -0.08, 0.08, zt - 0.08, zt + 0.08, WD)
    zc0, zc1 = zt - 0.25, zt - 0.25 - h * 0.62
    bb(mb, F, 0.3, cw + 0.3, -0.06, 0.06, zc1, zc0 - 1.0, cloth)
    bb(mb, F, 0.3, cw + 0.3, -0.06, 0.06, zc0 - 1.0, zc0, band)
    bb(mb, F, 0.2, cw + 0.4, -0.11, 0.11, zc1 - 0.16, zc1 + 0.04, WD)
    for k in range(4):
        zz = zc0 - (zc0 - zc1) * (k + 0.5) / 4
        bb(mb, F, -0.24, 0.36, -0.1, 0.1, zz - 0.1, zz + 0.1, band)
    for xx in (0.6, cw):
        bb(mb, F, xx - 0.1, xx + 0.1, -0.12, 0.12, zc0 - 0.05, zt + 0.12, band)
    return F.p(0.0, 0.0, h)


# ================================================================== RUA: leito assentado, sarjeta, meio-fio, calcada
def street2(mb, F, L, road_w=18.0, walk_w=4.0, slab=(3.0, 1.5), walk_slab=(2.0, 1.2), key=0, walks=(True, True),
            curbs=True, berco=True, thin=False):
    """TRECHO DE RUA ao longo de x (F no eixo, z=0 = topo do leito): leito de PEDRA ASSENTADA em fiadas (laje 3 x 1,5,
    juntas rebaixadas 0,08 sobre berco escuro), SARJETA de 0,8 a -0,15 (pedras escuras), MEIO-FIO 0,3 x 0,5 (topo
    +0,35) e CALCADA de 'walk_w' em lajes menores no topo +0,35. Devolve a cota da calcada.
    V2-3: curbs=False = viela/praca (sem meio-fio, borda de pedra); thin=True = cada laje e SO a face de cima (2 tris,
    0,08 acima do berco escuro: as juntas leem iguais de cima e da altura do jogador) - a cidade inteira cabe no
    orcamento. Com thin, o MB da rua deve ser fechado com finish(recalc=False) (as lajes ja saem viradas para cima)."""
    zw = 0.35
    hw = road_w / 2

    def course(y0, y1, sx, sy, z, m, key2, gap=0.08, berco=True):
        if berco:
            bb(mb, F, -L / 2, L / 2, y0, y1, z - 0.3, z - gap, STD)               # berco escuro (aparece nas juntas)
        nr = max(1, int(round((y1 - y0) / sy)))
        h_ = (y1 - y0) / nr
        for r in range(nr):
            ya, yb = y0 + r * h_, y0 + (r + 1) * h_
            off = (0.5 * sx if r % 2 else 0.0) + sx * 0.23 * _h01(key, key2, r)
            x = -L / 2 - off
            k = 0
            while x < L / 2 - 0.05:
                w_ = sx * (0.8 + 0.4 * _h01(key, key2, r, k))
                xa, xb = max(-L / 2, x), min(L / 2, x + w_)
                if xb - xa > 0.25:
                    if thin:
                        a0, a1, b0, b1 = xa + gap / 2, xb - gap / 2, ya + gap / 2, yb - gap / 2
                        mb.quad(F.p(a0, b0, z), F.p(a1, b0, z), F.p(a1, b1, z), F.p(a0, b1, z), m)
                    else:
                        bb(mb, F, xa + gap / 2, xb - gap / 2, ya + gap / 2, yb - gap / 2, z - 0.3, z, m)
                x += w_
                k += 1
    if not curbs:                 # V2-3: VIELA / praca (PLANO_V2 3.3: sem meio-fio, com BORDA de pedra)
        course(-hw + 0.55, hw - 0.55, slab[0], slab[1], 0.0, STP, "rd", berco=berco)
        nseg = max(1, int(round(L / 1.8)))
        for s in (-1, 1):
            y0, y1 = sorted((s * (hw - 0.55), s * hw))
            if berco:
                bb(mb, F, -L / 2, L / 2, y0, y1, -0.3, -0.1, STD)
            for i in range(nseg):
                xa = -L / 2 + L * i / nseg
                bb(mb, F, xa + 0.04, xa + L / nseg - 0.04, y0 + 0.04, y1 - 0.04, -0.3, 0.0, ST)
        return 0.0
    course(-hw + 0.8, hw - 0.8, slab[0], slab[1], 0.0, STP, "rd")
    for s, on in ((-1, walks[0]), (1, walks[1])):
        y0, y1 = sorted((s * (hw - 0.8), s * hw))
        bb(mb, F, -L / 2, L / 2, y0, y1, -0.6, -0.15, GUTTER)                      # sarjeta
        c0, c1 = sorted((s * hw, s * (hw + 0.3)))
        nseg = max(1, int(round(L / 2.4)))
        for i in range(nseg):                                                     # meio-fio em pecas de 2,4
            xa = -L / 2 + L * i / nseg
            bb(mb, F, xa + 0.03, xa + L / nseg - 0.03, c0, c1, -0.6, zw, CURB)
        if on:
            w0, w1 = sorted((s * (hw + 0.3), s * (hw + 0.3 + walk_w)))
            course(w0, w1, walk_slab[0], walk_slab[1], zw, ST, "wk%d" % s)
    return zw


# ================================================================== V3-cut: faces que NINGUEM ve (orcamento 625k)
OCC_SKIP = ("COL_", "PREVIEW_", "SCALE_", "VFX_", "CAM_", "OP_Plz_OreProxy", "OP_Ter_Piers", "OP_Water_", "OP_Veg_Blockout")
OCC_SKIP_MATS = ("P_OPM_Glass",)          # transparentes nao tampam nada


def _pocket_dirs(n, tilts=(45.0, 75.0), naz=8):
    t1 = n.orthogonal().normalized()
    t2 = n.cross(t1)
    out = [(n, 1.0)]
    for a in tilts:
        ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))
        for k in range(naz):
            b = 2.0 * math.pi * k / naz + 0.3
            out.append(((n * ca + (t1 * math.cos(b) + t2 * math.sin(b)) * sa).normalized(), ca))
    return out


POCKET_G, POCKET_TILT = 3.0, 62.0         # bolso: tampa a <= G em todo o hemisferio ate POCKET_TILT graus da normal
POCKET_G_DOWN = 0.5                        # faces viradas para baixo (fundo de banco/beiral baixo): so bolso estreito


def cull_pockets(objs, occ_prefixes=(), G=None, inside_d=6.0, verbose=True, tag="kit2", g_at=None, under=False):
    """V3-cut (orcamento 625k, nada que apareca muda): apaga, nos objetos 'objs' JA FINALIZADOS, as faces que nenhuma
    camera alcanca, testando contra a cena estatica (objs + objetos com prefixo em occ_prefixes, sem colisao/previa/
    VFX/transparentes):
      (a) DENTRO: a normal e 8 direcoes a 45 graus batem no AVESSO de alguma malha a <= inside_d (face enterrada num
          volume fechado: pe de pilar dentro da soleira, ponta de viga dentro da parede, fundo enterrado no terreno);
      (b) BOLSO: de TODOS os pontos de amostra (centro, cantos e meios das arestas puxados 6% para dentro), a normal e
          16 direcoes inclinadas 45 e 75 graus batem em ALGUMA malha a <= G/cos (face tampada por outra a <= G em todo
          o hemisferio: costas de ripa/kumiko contra o papel, topo de caibro sob o forro, parede-meia contra a do
          vizinho, fundo de peca pousada no piso, lados de pecas encostadas com fresta).
    g_at(ponto) -> G local (opcional): interiores vivos usam um bolso menor (o jogador entra e olha de perto).
      (c) under=True: face virada para BAIXO com todos os vertices 0,05..1,0 abaixo do piso andavel da planta
          (op_layout.zone_of): so se veria de dentro da terra (fundo do soco, base enterrada). Nao use onde a camera passa por baixo
          do piso (cais sobre a agua, ponte).
    Uma face que TAMPA outra apagada nunca e apagada (pares mutuos: so um sai), ordem geometrica (deterministico). Os
    raios saem com um desvio fixo e minusculo no plano da face (nunca exatamente numa aresta). Devolve tris cortados."""
    from mathutils.bvhtree import BVHTree
    from op_layout import zone_of
    G = POCKET_G if G is None else G
    if isinstance(objs, str):                     # prefixo do dono
        objs = [o for o in bpy.data.objects if o.name.startswith(objs)]
    objs = [o for o in objs if o is not None and o.type == "MESH" and len(o.data.polygons)]
    if not objs:
        return 0
    occ = list(objs)
    names = set(o.name for o in objs)
    for o in bpy.data.objects:
        if o.type != "MESH" or o.name in names or not o.name.startswith(tuple(occ_prefixes)) or \
                o.name.startswith(OCC_SKIP):
            continue
        if o.users_collection and o.users_collection[0].name in ("00_REFERENCE", "_SCALE_REFERENCE"):
            continue
        occ.append(o)
    V, P, own = [], [], []
    PK = []
    for oi, o in enumerate(occ):
        me, mw = o.data, o.matrix_world
        skip = set(i for i, m in enumerate(me.materials) if m and m.name.startswith(OCC_SKIP_MATS))
        b = len(V)
        V.extend(mw @ v.co for v in me.vertices)
        for p in me.polygons:
            if p.material_index in skip:
                continue
            c_, n_ = mw @ p.center, p.normal
            # determinismo (licao do cull_hidden M6c): a ORDEM das faces muda entre builds e a BVH desempata faces
            # coincidentes pela ordem -> arvore montada em ordem GEOMETRICA
            PK.append(((round(c_.x, 4), round(c_.y, 4), round(c_.z, 4), round(n_.x, 3), round(n_.y, 3),
                        round(n_.z, 3), len(p.vertices), o.name), [b + i for i in p.vertices], (oi, p.index)))
    PK.sort(key=lambda t: t[0])
    for k_, vs_, ow_ in PK:
        P.append(vs_)
        own.append(ow_)
    tree = BVHTree.FromPolygons(V, P)
    isl = {}                                      # ilha (peca conexa) de cada poligono (objs + ocluidores)
    for oi, o in enumerate(occ):
        me = o.data
        par = list(range(len(me.vertices)))

        def root(a):
            while par[a] != a:
                par[a] = par[par[a]]
                a = par[a]
            return a
        for p in me.polygons:
            vs_ = p.vertices
            r0 = root(vs_[0])
            for v in vs_[1:]:
                r1 = root(v)
                if r1 != r0:
                    par[r1] = r0
        for p in me.polygons:
            isl[(oi, p.index)] = (oi, root(p.vertices[0]))
    cand = []                                     # (chave geometrica, obj, poligono, tris, bloqueadores)
    for oi, o in enumerate(objs):
        me, mw = o.data, o.matrix_world
        m3 = mw.to_3x3()
        for p in me.polygons:
            n = m3 @ p.normal
            if n.length < 0.5:
                continue
            n = n.normalized()
            vs = [mw @ me.vertices[i].co for i in p.vertices]
            k0 = min(range(len(vs)), key=lambda i: (round(vs[i].x, 4), round(vs[i].y, 4), round(vs[i].z, 4)))
            vs = vs[k0:] + vs[:k0]                       # determinismo: amostras a partir do menor vertice
            c = sum(vs, Vector()) / len(vs)
            if max(abs((v - c).dot(n)) for v in vs) > 0.004:
                continue                  # face TORCIDA (telha ondulada): fica - o raio cruzaria a propria malha
            pts = [c] + [c + (v - c) * 0.94 for v in vs] + \
                [c + ((vs[i] + vs[(i + 1) % len(vs)]) / 2 - c) * 0.94 for i in range(len(vs))]
            for i in range(1, len(vs) - 1):              # + grade de ~0,45 na face (a ponta que fura uma onda de
                a_, b_, c_ = vs[0], vs[i], vs[i + 1]      # telha entre 2 amostras nao escapa)
                k = min(10, max(1, int(math.ceil(max((b_ - a_).length, (c_ - a_).length, (c_ - b_).length) / 0.45))))
                if k > 1:
                    pts += [a_ + (b_ - a_) * ((u + 1.0 / 3.0) / k) + (c_ - a_) * ((w + 1.0 / 3.0) / k)
                            for u in range(k) for w in range(k - u)]
            t1 = vs[1] - vs[0]
            if t1.length > 1e-6:
                t1 = t1.normalized()
                dj = t1 * 0.00131 + n.cross(t1) * 0.00217
                pts = [q + dj for q in pts]
            if under and n.z < -0.7:
                below = True
                for v in vs:
                    zf_ = zone_of(v.x, v.y)
                    if zf_ is None or v.z > zf_ - 0.05 or v.z < zf_ - 1.0:     # so logo abaixo do piso (soco)
                        below = False
                        break
                if below:
                    key = (round(c.x, 3), round(c.y, 3), round(c.z, 3), round(n.x, 3), round(n.y, 3), round(n.z, 3),
                           len(vs), o.name)
                    cand.append((key, oi, p.index, len(vs) - 2, set()))
                    continue
            ds = _pocket_dirs(n, (45.0, POCKET_TILT))
            blk = set()
            hid = True                                   # (a) dentro de um volume fechado
            me_ = (oi, p.index)

            def cast(q, d, dist):
                """raio que ignora a PROPRIA face (quads torcidos da telha se cruzam com o raio da normal)"""
                o_ = q + n * 0.004
                for _ in range(4):
                    h = tree.ray_cast(o_, d, dist)
                    if h[0] is None or own[h[2]] != me_:
                        return h
                    dist -= h[3] + 1e-3
                    if dist <= 0.0:
                        return (None, None, None, None)
                    o_ = h[0] + d * 1e-3
                return (None, None, None, None)

            def joint(pts_, nis, dist):
                """entre 2 pontos vizinhos (<= 0,7) tampados por pecas DIFERENTES, raios na normal a cada 0,02: se
                algum escapa (ou passa de 'dist') ha uma junta/fresta entre as pecas (passo 0,02: junta >= 0,04)"""
                ks = list(nis)
                prs = set()
                for ia_ in ks:                           # so o vizinho MAIS PROXIMO de outra peca (a fronteira)
                    best_ = None
                    for ib_ in ks:
                        if nis[ib_] == nis[ia_]:
                            continue
                        ln_ = (pts_[ib_] - pts_[ia_]).length
                        if ln_ <= 0.7 and (best_ is None or ln_ < best_[0]):
                            best_ = (ln_, ib_)
                    if best_:
                        prs.add((min(ia_, best_[1]), max(ia_, best_[1])))
                for ia_, ib_ in sorted(prs):
                    pa, pb = pts_[ia_], pts_[ib_]
                    m_ = max(2, int((pb - pa).length / 0.02))
                    for t_ in range(1, m_):
                        if cast(pa + (pb - pa) * (t_ / m_), n, dist + 0.02)[0] is None:
                            return True
                return False
            nisl = {}                                    # ponto -> peca que tampa na direcao da NORMAL
            for qi, q in enumerate(pts):
                for d, ca in ds[:9]:
                    h = cast(q, d, inside_d)
                    if h[0] is None or h[1].dot(d) <= 0.0:
                        hid = False
                        break
                    blk.add(h[2])
                    if ca == 1.0:
                        nisl[qi] = isl.get(own[h[2]])
                if not hid:
                    break
            if hid and len(set(nisl.values())) > 1 and joint(pts, nisl, inside_d):
                hid = False                              # tampada por 2+ pecas com JUNTA entre elas
            if not hid:
                blk = set()
                hid = True                               # (b) bolso
                Gf = G if g_at is None else min(G, g_at(c))
                if n.z < -0.3:
                    Gf = min(Gf, POCKET_G_DOWN)          # face virada para baixo: a camera baixa (olhando para cima) a ve
                nisl = {}
                for qi, q in enumerate(pts):
                    for d, ca in ds:
                        h = cast(q, d, Gf / ca + 0.02)
                        if h[0] is None:
                            hid = False
                            break
                        blk.add(h[2])
                        if ca == 1.0:
                            nisl[qi] = isl.get(own[h[2]])
                    if not hid:
                        break
                if hid and len(set(nisl.values())) > 1 and joint(pts, nisl, Gf):
                    hid = False                          # tampada por 2+ pecas (lajes, pedras, tabuas) com JUNTA entre
                    #                                      elas (0,04..0,08): pelo vao se veria o buraco - fica
            if hid:
                # so face de SOLIDO bem orientado: o raio para TRAS (para dentro da propria peca) tem de sair dela por
                # uma face voltada para fora (normal no sentido do raio). Face invertida (normal para dentro: o Roblox
                # nao a desenha e mostra o que esta atras) ou chapa aberta ficam - apaga-las abriria um buraco
                mi = isl[me_]
                for q in (pts[0], pts[1], pts[2]):       # (so conta a PROPRIA peca: pecas que se cruzam nao contam)
                    o_, dist, ok = q - n * 0.004, 40.0, False
                    for _ in range(24):
                        h = tree.ray_cast(o_, -n, dist)
                        if h[0] is None:
                            break
                        k_ = own[h[2]]
                        if k_ != me_ and isl.get(k_) == mi:
                            ok = h[1].dot(-n) > 0.0
                            break
                        dist -= h[3] + 1e-3
                        if dist <= 0.0:
                            break
                        o_ = h[0] - n * 1e-3
                    if not ok:
                        hid = False
                        break
            if hid:
                key = (round(c.x, 3), round(c.y, 3), round(c.z, 3), round(n.x, 3), round(n.y, 3), round(n.z, 3),
                       len(vs), o.name)
                cand.append((key, oi, p.index, len(vs) - 2, set(own[k] for k in blk)))
    cand.sort(key=lambda t: t[0])
    removed, protected = set(), set()
    kill = {}
    for key, oi, pi, nt, blk in cand:
        me_ = (oi, pi)
        if me_ in protected or (blk & removed):
            continue
        removed.add(me_)
        protected |= blk
        kill.setdefault(oi, []).append(pi)
    cut = 0
    for oi, pis in kill.items():
        o = objs[oi]
        bm = bmesh.new()
        bm.from_mesh(o.data)
        bm.faces.ensure_lookup_table()
        fs = [bm.faces[i] for i in pis]
        cut += sum(len(f.verts) - 2 for f in fs)
        bmesh.ops.delete(bm, geom=fs, context="FACES_ONLY")
        loose = [e for e in bm.edges if not e.link_faces]
        bmesh.ops.delete(bm, geom=loose, context="EDGES")
        lv = [v for v in bm.verts if not v.link_edges]
        bmesh.ops.delete(bm, geom=lv, context="VERTS")
        bm.to_mesh(o.data)
        bm.free()
        o.data.update()
    if verbose:
        print("%s cull_pockets: -%d tris em %d objetos (candidatas %d, ocluidores %d objs)" % (
            tag, cut, len(kill), len(cand), len(occ)))
    return cut
# ================================================================== ESTUDIO (folhas de gate; fora do jogo)
def _tris(ob):
    return sum(len(p.vertices) - 2 for p in ob.data.polygons) if ob and ob.type == "MESH" else 0


STUDIO = []          # (nome, construtor(mb, F) -> dict(cams=[(sufixo, foco local, dist, yaw, elev)], dummy=(x, y)))


def item(name):
    def deco(fn):
        STUDIO.append((name, fn))
        return fn
    return deco


def _cam(name, F, focus, dist, yaw, elev, lens=35):
    tgt = F.p(*focus)
    a = math.radians(yaw)
    e = math.radians(elev)
    dl = Vector((math.sin(a) * math.cos(e), math.cos(a) * math.cos(e)))
    ca, sa = math.cos(F.a), math.sin(F.a)
    dw = Vector((dl.x * ca - dl.y * sa, dl.x * sa + dl.y * ca, math.sin(e)))
    fm_lib.camera(name, tgt + dw * dist, tgt, lens)
    return name


EYE = 5.5          # olho do jogador acima do piso


def _type_cams(W, D, H, front_y=None, close=None):
    """frente, 3/4, de cima (camera alta do jogo, ~35 graus) e close na altura do jogador"""
    fy = D / 2 if front_y is None else front_y
    R = max(W, H) * 1.05 + 14.0
    cams = [("frente", (0.0, fy, H * 0.42), R, 0, 6), ("34", (0.0, 0.0, H * 0.45), R * 1.05, 38, 20),
            ("cima", (0.0, 0.0, H * 0.35), R * 1.35, 25, 36)]
    if close:
        cams.append(("close", "at") + close)
    return cams


@item("A_loja")
def _ia(mb, F):
    loja(mb, F, 14.0, 16.0, RCOB, 1, sides=(True, False), light_name="L_OPK2_LojaA", upper="mushiko", awning=False)
    return dict(cams=_type_cams(14.0, 16.0, 26.0, close=((-1.0, 8.0 + 6.0, 0.8 + EYE), (4.5, 6.0, 4.6), 20)),
                dummy=(9.5, 10.0))


@item("A2_loja_tsuma")
def _ia2(mb, F):
    loja(mb, F, 12.0, 16.0, RVIO, -1, tsuma=True, awning=True, upper="shoji", sides=(True, True), seed=3)
    return dict(cams=_type_cams(12.0, 16.0, 26.0, close=((3.0, 8.0 + 6.5, 0.8 + EYE), (-2.5, 6.0, 5.6), 20)),
                dummy=(-8.5, 10.0))


@item("B_sobrado")
def _ib(mb, F):
    sobrado(mb, F, 16.0, 16.0, RTEAL, sides=(True, True))
    return dict(cams=_type_cams(16.0, 16.0, 34.0, close=((-3.0, 8.0 + 6.0, 0.8 + EYE), (1.0, 7.0, 7.5), 20)),
                dummy=(10.5, 10.0))


@item("C_esquina")
def _ic(mb, F):
    esquina(mb, F, 16.0, 16.0, RREDV, RCOB, 1, light_name="L_OPK2_Esq")
    return dict(cams=_type_cams(16.0, 16.0, 40.0, close=((12.0, 15.0, 0.8 + EYE), (5.0, 6.0, 8.0), 20)),
                dummy=(-10.0, 10.5))


@item("D_kura")
def _id(mb, F):
    kura(mb, F, 10.0, 14.0, RCOB)
    goods_pile(mb, sub(F, 7.5, 6.0), "barrels")
    return dict(cams=_type_cams(10.0, 14.0, 24.0, close=((7.0, 7.0 + 8.0, EYE + 0.3), (0.5, 7.0, 6.0), 22)),
                dummy=(-7.5, 9.0))


@item("E_chaya")
def _ie(mb, F):
    chaya(mb, F, 22.0, 16.0, RVIO, 1, light_name="L_OPK2_Chaya")
    return dict(cams=_type_cams(22.0, 16.0, 26.0, close=((-6.0, 8.0 + 5.5, 1.0 + EYE), (-3.0, 4.0, 4.5), 20)),
                dummy=(-13.0, 9.5))


@item("F_fundo")
def _if(mb, F):
    fundo(mb, sub(F, -5.6), 10.0, 10.0, RB, sides=(True, False))
    fundo(mb, sub(F, 5.6), 10.0, 10.0, RTEAL, tsuma=True, seed=7, sides=(False, True))
    return dict(cams=_type_cams(21.0, 10.0, 16.0, close=((-3.0, 5.0 + 6.0, 0.6 + EYE), (-4.0, 5.0, 4.0), 22)),
                dummy=(12.5, 6.0))


@item("G_pecas")
def _ig(mb, F):
    xs = {}
    lamp_andon(mb, sub(F, -24.0, 0.0), "L_OPK2_Andon")
    lamp_post(mb, sub(F, -16.0, 0.0), "L_OPK2_Post")
    toro2(mb, sub(F, -7.0, 0.0), "L_OPK2_Toro")
    well2(mb, sub(F, 3.0, 0.0))
    stall2(mb, sub(F, 13.5, 1.0), "L_OPK2_Stall")
    goods_pile(mb, sub(F, 22.0, 0.0), "barrels")
    goods_pile(mb, sub(F, 22.0, -5.0), "crates")
    bamboo_fence(mb, sub(F, -10.0, -6.0), 14.0, 3.2)
    nobori2(mb, sub(F, 30.0, -1.0))
    bb(mb, F, 36.0, 44.0, -4.5, -3.0, 0.0, 9.0, PLW)                        # parede para o chochin de beiral
    eave_lantern(mb, sub(F, 40.0, -3.0), 0.0, 7.6, "L_OPK2_Eave")
    return dict(cams=[("geral", (0.0, -1.0, 3.5), 62.0, 0, 14),
                      ("cima", (0.0, -1.0, 2.0), 60.0, 15, 38),
                      ("andon", (-24.0, 0.0, 2.6), 8.5, 28, 14),
                      ("poste_chochin", (-15.2, 0.0, 4.8), 10.0, -35, 8),
                      ("toro", (-7.0, 0.0, 3.4), 9.5, 25, 12),
                      ("poco", (3.0, 0.0, 3.0), 12.5, 50, 18),
                      ("banca", (13.5, 0.0, 2.6), 10.0, 28, 16),
                      ("carga", (22.0, -2.5, 1.2), 10.0, 25, 26),
                      ("nobori", (30.3, -1.0, 4.8), 13.0, 25, 8),
                      ("chochin_beiral", (40.0, -2.4, 6.2), 6.0, 30, 6),
                      ("cerca", (-12.0, -6.0, 1.6), 13.0, -20, 22)], dummy=(-11.5, 4.0))


@item("H_ponte")
def _ih(mb, F):
    zb = 2.6
    span, wd = 10.0, 6.0
    for s in (-1, 1):                                                    # margens do canal (cais de pedra + piso)
        x0, x1 = sorted((s * span / 2, s * (span / 2 + 16.0)))
        bb(mb, F, x0, x1, -14.0, 14.0, -0.3, zb - 0.3, "Stone_OP_Wall")
        bb(mb, F, x0 + (0.0 if s > 0 else 0.0), x1, -14.0, 14.0, zb - 0.3, zb, STP)
    bb(mb, F, -span / 2, span / 2, -14.0, 14.0, -0.3, 0.2, "Dirt_OP_Dark")
    bb(mb, F, -span / 2, span / 2, -14.0, 14.0, 0.2, 1.1, "Water_OP_Basin")
    r = bridge2(mb, sub(F, z=zb), span, wd, 1.4, 0.0, 1.0 - zb, 0.2 - zb)
    for s in (-1, 1):
        lamp_andon(mb, sub(F, s * (span / 2 + 3.0), wd / 2 + 1.6, zb), None)
    E = EYE + zb
    return dict(cams=[("lado", (0.0, 0.0, zb), 34.0, 0, 8), ("34", (0.0, 0.0, zb + 1.0), 32.0, 40, 22),
                      ("cima", (0.0, 0.0, zb), 42.0, 20, 38),
                      ("jogador", "at", (-span / 2 - 7.0, 1.0, E), (0.0, 0.0, zb + 2.0), 22)],
                dummy=(-span / 2 - 3.5, 3.5), dummy_z=zb)


def _street_scene(mb, F, parts):
    """RUA-MODELO (~64 de frente): lado A = QUADRA-MODELO de 5 lotes geminados (cobalto / verde-agua / roxo /
    vermelho + kura), lado B = esquina com torre + loja + casa de cha; casas de fundo atras do lado A; leito
    assentado, sarjeta, meio-fio, calcadas; andon, poste de chochin, banca, carga. y=0 = eixo da rua."""
    road, walk = 18.0, 4.0
    zs = street2(mb, F, 72.0, road, walk, key=1)
    fa = -(road / 2 + 0.3 + walk)
    # lado A (frente para +y)
    lots = [("loja", 12.0, dict(roof_m=RCOB, shop_side=-1, sides=(True, False), upper="mushiko", seed=11,
                                light_name="L_OPK2_Rua_L1")),
            ("sobrado", 16.0, dict(roof_m=RTEAL, sides=(False, False), rail_m=WD, seed=12)),
            ("loja", 12.0, dict(roof_m=RVIO, shop_side=1, tsuma=True, awning=True, upper="shoji", seed=13)),
            ("loja", 14.0, dict(roof_m=RREDV, shop_side=-1, roof="irimoya", upper="double", seed=14, h0=9.4)),
            ("kura", 10.0, dict(roof_m=RCOB))]
    x = -32.0
    xa = []
    for kind, W, kw in lots:
        D = 16.0 if kind != "kura" else 14.0
        Fh = sub(F, x + W / 2, fa - D / 2 - 0.35, zs)
        info = BUILD[kind](mb, Fh, W=W, D=D, **kw)
        parts.append("%s %.0f" % (kind, W))
        xa.append(x + W / 2)
        x += W
    # fundos (atras do lado A)
    for i, xx in enumerate((-20.0, -9.0, 8.0)):
        fundo(mb, sub(F, xx, fa - 16.0 - 0.7 - 6.0 - 5.0, zs, math.pi), 10.0, 10.0, (RB, RTEAL, RVIO)[i],
              tsuma=i == 1, seed=20 + i, sides=(True, True))
    # lado B (frente para -y)
    fb = road / 2 + 0.3 + walk
    rowb = [("chaya", 22.0, dict(roof_m=RVIO, garden_side=1, light_name="L_OPK2_Rua_Ch")),
            ("loja", 14.0, dict(roof_m=RTEAL, shop_side=1, upper="shoji", awning=True, seed=31)),
            ("esquina", 16.0, dict(roof_m=RREDV, tower_m=RCOB, corner=-1, seed=32))]
    x = -30.0
    for kind, W, kw in rowb:
        D = 16.0
        Fh = sub(F, x + W / 2, fb + D / 2 + 0.35, zs, math.pi)
        BUILD[kind](mb, Fh, W=W, D=D, **kw)
        parts.append("%s %.0f" % (kind, W))
        x += W
    # pecas na calcada
    ya, yb = fa + 0.9, fb - 0.9
    for xx in (-20.0, 8.0, 21.6):                                           # andon nas divisas dos lotes
        lamp_andon(mb, sub(F, xx, ya, zs))
    for xx in (-8.0, 6.0):
        lamp_post(mb, sub(F, xx, yb, zs, math.pi))
    stall2(mb, sub(F, -33.0, fb - 1.4, zs))
    goods_pile(mb, sub(F, 30.0, fa + 1.6, zs), "crates")
    toro2(mb, sub(F, 30.0, yb - 0.6, zs), None, 0.8)
    return zs, fa, fb


@item("Q_rua_modelo")
def _iq(mb, F):
    parts = []
    LIFT = 0.4
    zs, fa, fb = _street_scene(mb, sub(F, z=LIFT), parts)
    zs += LIFT
    E = zs + EYE
    cams = [
        ("cima_1", "at", (-56.0, 30.0, 52.0), (-2.0, -6.0, 6.0), 24),
        ("cima_2", "at", (40.0, -60.0, 54.0), (0.0, -6.0, 6.0), 24),
        ("eixo", "at", (-44.0, 2.0, E), (20.0, -2.0, 7.0), 22),
        ("close_1_loja", "at", (-23.0, fa + 7.0, E), (-26.0, fa - 1.0, 6.4), 16),
        ("close_2_sobrado", "at", (-9.0, fa + 7.0, E), (-12.0, fa - 1.0, 6.8), 16),
        ("close_3_tsuma", "at", (5.0, fa + 7.0, E), (2.0, fa - 1.0, 6.4), 16),
        ("close_4_irimoya", "at", (18.0, fa + 7.0, E), (15.0, fa - 1.0, 6.6), 16),
        ("close_5_kura", "at", (30.0, fa + 7.5, E), (27.0, fa - 1.0, 6.4), 16),
        ("close_6_chaya", "at", (-12.5, fb - 7.0, E), (-15.5, fb + 1.0, 6.2), 16),
        ("close_7_esquina", "at", (25.0, fb - 7.0, E), (16.0, fb + 1.0, 8.5), 16),
    ]
    return dict(cams=cams, dummies=[(-30.0, fa + 1.2), (-9.5, fb - 1.4), (11.0, fa + 1.3)], dummy_z=zs,
                parts=" | ".join(parts))


def studio(out, only=()):
    import op_scene
    out = os.path.abspath(out)
    os.makedirs(out, exist_ok=True)
    DL.reset_scene()
    fm_lib.make_materials()
    op_scene.setup(res=(960, 540), samples=16)
    items = [p for p in STUDIO if not only or any(o in p[0] for o in only)]
    gm = MB("STUDIO_Ground", "00_REFERENCE", detail="far", floor=-999)
    gm.box((220.0 * (len(items) + 2), 400.0, 1.0), (110.0 * len(items), 0.0, -0.5), (0, 0, 0), "Grass_OP", 0.0)
    gm.finish()
    cams, report = [], []
    for i, (name, fn) in enumerate(items):
        F = Frame(i * 220.0, 0.0, 0.0, math.pi)
        mb = MB("OP_Kit2_" + name, "05_CAPITAL")
        r = fn(mb, F)
        t_raw = len(mb.bm.faces) and sum(len(f.verts) - 2 for f in mb.bm.faces)
        ob = mb.finish()
        report.append((name, t_raw, _tris(ob), len(ob.data.materials) if ob else 0, r.get("parts", "")))
        for k, (dx, dy) in enumerate(r.get("dummies", [r.get("dummy", (0.0, 0.0))])):
            p = F.p(dx, dy, 0.0)
            DL.dummy("SCALE_Dummy_%s_%d" % (name, k), p.x, p.y, r.get("dummy_z", 0.0), F.a + math.pi)
        for spec in r["cams"]:
            cn = "CAM_K2_%s_%s" % (name, spec[0])
            if spec[1] == "at":
                fm_lib.camera(cn, F.p(*spec[2]), F.p(*spec[3]), spec[4])
                cams.append(cn)
            else:
                suf, foc, dist, yaw, el = spec
                cams.append(_cam(cn, F, foc, dist, yaw, el, r.get("lens", 35)))
    fm_lib.make_materials()
    op_scene.tone_emissives()
    for o in bpy.data.objects:
        if o.type == "LIGHT" and o.name.startswith("L_OPK2"):
            o.data.use_shadow = False
    sc = bpy.context.scene
    sc.render.image_settings.file_format = "JPEG"
    sc.render.image_settings.quality = 90
    with open(os.path.join(out, "tris_kit2.txt"), "a") as fh:
        for name, tr, t, nm, parts in report:
            line = "KIT2 %-26s tris=%6d materiais=%2d %s" % (name, t, nm, parts)
            print(line)
            fh.write(line + "\n")
    if "--no-render" in sys.argv:
        return
    modes = (("rico", "previa"), ("roblox", "roblox"))
    if "--roblox" in sys.argv:
        modes = (("roblox", "roblox"),)
    for mode, sub_ in modes:
        if mode == "roblox":
            fm_lib.apply_preview("roblox")
            op_scene.tone_emissives()
        od = os.path.join(out, sub_)
        os.makedirs(od, exist_ok=True)
        for cn in cams:
            sc.camera = bpy.data.objects[cn]
            sc.render.filepath = os.path.join(od, cn + ".jpg")
            bpy.ops.render.render(write_still=True)
            print("KIT2 RENDER", mode, cn)


if __name__ == "__main__":
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    pos = [a for a in argv if not a.startswith("--")]
    out = pos[0] if pos else os.path.join(HERE, "renders", "v2", "kit2")
    studio(out, pos[1:])
