# op_props.py - M4 da Ilha 5 (ONE PIECE / WANO): VIDA DA CIDADE DIRIGIDA (PROMPT_USUARIO 10, 15, 16, 17; PLANO_OP
# secoes 4.3, 6, 9, 14). Zona "dressing" do build_op (ZONE_MODULES["dressing"] += ["op_props"]). Prefixo OP_Prop_,
# colecao 09_PROPS, dono "props" (teto 27k tris / 38 MeshParts: a borda da praca, OP_Prop_Plz_*, ja usa ~7,1k).
#
# NAO E ESPALHADO: cada conjunto conta uma coisa num lugar escolhido (e so ali):
#   MERCADO DO CANAL   a viela do canal (bairro SO, T1) vira a rua de feira do bairro: 5 BANCAS cenograficas (tampo de
#                      tabuas, pes em sapatas de pedra, travessas, prateleira de baixo, frente de tabuas com mata-juntas,
#                      TOLDO de tabuas em caibros com sanefa de pano; mercadoria APOIADA: ceramica, tecido, cestos de
#                      grao, lanternas de papel, cha), 1 par de nobori SO na entrada da feira, poste aceso no meio,
#                      poco no largo de SW4, carrinho de mao carregado, varais nos vaos entre as casas, barris/tinas.
#   CAIS DO CANAL      carga encostada nos fundos das casas do quarteirao oeste (caixas, fardos de arroz, barris) e
#                      um carrinho; poste aceso. Do outro lado (alem): poco, varal, tina.
#   TRAVESSA DO PORTO  bloco leste (T1): carrinho no mirante, carga nos fundos das lojas, varal, poste aceso.
#   SANTUARIO NE       sino (suzu) com corda na viga da frente do haiden, caixa de oferendas no estrado, quadro de
#                      ema (plaquinhas lisas, sem escrita), pavilhao de abluções (chozuya: bacia de pedra, bica, conchas).
#   TERRACO ALTO       poco no jardim entre as mansoes.
#   PLACAS             2 postes de direcao de madeira (setas lisas, sem texto; a seta do summon leva a ESTRELA aprovada)
#                      na saida da rua de chegada para a viela leste (summon) e para a viela do canal (feira).
# Nada dentro da MiningZone, nas rotas do QA nem na frente das portas: cada peca e conferida no build (folga das rotas
# >= 1,6 + raio, fora da zona + 8). APOIO: o chao de cada peca vem de RAIO contra as malhas construidas (pisos, lajes,
# terra dos quintais) - nada flutua nem afunda; o volume de cada peca e testado (BVH) contra paredes/beirais/postes das
# outras zonas (aviso no log se encostar). audit() (ver uso) confere TODAS as ilhas soltas dos OP_Prop_* (inclusive a
# borda da praca): ilha que nao toca nada = flutuando.
# LUZES: so NightOnly (L_OPProp_Lamp_*), 4 postes novos onde a rua lia apagada; o resto e papel aceso (Glass_OP_Lantern)
#   dentro de armacao (chochin das bancas). COLISAO: so o que bloqueia de verdade (bancas, poco, carrinhos, postes,
#   estandartes, chozuya, quadro de ema, pilhas de carga altas): COL_OP_Prop*.
# CAMERAS: CAM_OP_M4Prp_* (fora do export).
# uso extra: blender -b --factory-startup <blend> --python op_props.py -- audit     (flutuando / encostado)
import math, random, sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import bpy, bmesh
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree
import op_lib as DL
from op_lib import MB, col_box, Frame, light
import op_layout as L
import op_kit as K

T1, P, W3Z = L.T1, L.P, L.W3
COLL = "09_PROPS"
WD, WM, LAC, GOLD, IRON = K.WD, K.WM, K.LAC, K.GOLD, K.IRON
STD, STP = K.STD, K.STP
RR = K.RR
INDIGO, CRED, CWHITE = K.INDIGO, K.CRED, K.CWHITE
STRAW = "Cloth_OP_Straw"
SHG = "Roof_OP_Shingle"
LGLOW = K.LGLOW
WARM = K.WARM
EYE = 5.65
SENTINEL = "OP_Prop_Cidade"
_h = K._h01
bb = K.bb
sub = K.sub


# ================================================================== PECAS (F: origem no chao, +y = FRENTE)
def ring_y(mb, F, c, ro, ri, t, n, m, rot=0.0):
    """aro (roda, polia): coroa de raio ro..ri e espessura t em volta do eixo Y local por c"""
    cx, cy, cz = c
    rings = []
    for rr, yy in ((ro, -t / 2), (ro, t / 2), (ri, t / 2), (ri, -t / 2)):
        rings.append([(cx + rr * math.cos(rot + 2 * math.pi * j / n), cy + yy, cz + rr * math.sin(rot + 2 * math.pi * j / n))
                      for j in range(n)])
    rings.append(rings[0])
    K.loft(mb, F, rings, m, caps=(False, False))


def basket(mb, F, x, y, z, r=0.5, h=0.5, fill=STRAW):
    """cesto de bambu (corpo afunilado, BORDA de aro escuro 0,08 para fora) cheio de grao em monte"""
    K.lathe(mb, F, (x, y, z), [(r * 0.72, 0.0), (r * 0.95, h * 0.8), (r, h), (r - 0.07, h), (r - 0.07, h * 0.86)], 8, WM)
    K.lathe(mb, F, (x, y, z + h - 0.09), [(r + 0.07, 0.0), (r + 0.07, 0.12)], 8, WD)
    K.lathe(mb, F, (x, y, z + h * 0.84), [(r - 0.06, 0.0), (r * 0.62, 0.17), (r * 0.12, 0.26)], 8, fill)


def tub(mb, F, x, y, z, r=0.8, h=0.75, n=10):
    """tina (oke): parede de aduelas com espessura (boca aberta, fundo 0,18 acima do chao) e 2 aros escuros"""
    K.lathe(mb, F, (x, y, z), [(r * 0.88, 0.0), (r, h), (r - 0.12, h), (r - 0.12, 0.18), (0.02, 0.18)], n, WM,
            caps=(True, False))
    for zz in (0.16, h - 0.16):
        rr = r * 0.88 + r * 0.12 * zz / h + 0.06
        K.lathe(mb, F, (x, y, z + zz - 0.07), [(rr, 0.0), (rr, 0.14)], n, WD)


def bale(mb, F, x, y, z, ang=0.0, Ln=1.7, r=0.55):
    """fardo de arroz (tawara) deitado: palha abaulada, tampas de palha nas pontas, 3 amarras de corda"""
    Fb = sub(F, x, y, z + r, ang)
    rr = lambda u: r * (0.72 + 0.28 * math.sin(math.pi * min(1.0, max(0.0, u))))
    prof = [(rr(u), -Ln / 2 + Ln * u) for u in (0.0, 0.18, 0.5, 0.82, 1.0)]
    K.lathe_y(mb, Fb, (0, 0, 0), prof, 8, STRAW)
    for u in (0.24, 0.76):
        yy = -Ln / 2 + Ln * u
        K.lathe_y(mb, Fb, (0, 0, 0), [(rr(u) + 0.05, yy - 0.07), (rr(u) + 0.05, yy + 0.07)], 8, WD)


def stall(mb, F, W=5.0, D=2.4, goods="ceramica", cloth=INDIGO, seed=0, val=0.75):
    """BANCA de feira (cenografica): sapatas de pedra, 4 pes (os de tras mais altos), travessas laterais em 2
    alturas, prateleira de baixo com carga, TAMPO de 3 tabuas com quadro, FRENTE de tabuas com mata-juntas, TOLDO de
    tabuas em caibros (cai para a frente) com sanefa de pano; mercadoria APOIADA no tampo e na prateleira."""
    zc = 2.7
    yb, yf = -D / 2, D / 2
    hb, hf = 6.4, 5.5
    px = W / 2 - 0.25
    for x in (-px, px):
        for y, hh in ((yb + 0.25, hb), (yf - 0.25, hf)):
            bb(mb, F, x - 0.36, x + 0.36, y - 0.36, y + 0.36, -0.15, 0.24, STD)
            bb(mb, F, x - 0.15, x + 0.15, y - 0.15, y + 0.15, 0.24, hh, WD)
        for z in (0.72, zc - 0.55):                                          # travessas laterais
            bb(mb, F, x - 0.1, x + 0.1, yb + 0.4, yf - 0.4, z - 0.09, z + 0.09, WD)
    bb(mb, F, -px + 0.15, px - 0.15, yb + 0.16, yb + 0.34, 0.63, 0.81, WD)   # travessa de tras
    bb(mb, F, -px + 0.1, px - 0.1, yb + 0.4, yf - 0.4, 0.81, 0.93, WM)      # prateleira de baixo
    # tampo: quadro + 3 tabuas (frisos de 0,06 entre elas), beiral de 0,2 na frente e 0,12 dos lados
    bb(mb, F, -px - 0.05, px + 0.05, yb + 0.12, yf - 0.05, zc - 0.42, zc - 0.16, WD)
    y0, y1 = yb + 0.05, yf + 0.2
    for i in range(3):
        a = y0 + (y1 - y0) * i / 3 + (0.03 if i else 0.0)
        b = y0 + (y1 - y0) * (i + 1) / 3 - (0.03 if i < 2 else 0.0)
        bb(mb, F, -W / 2 - 0.12, W / 2 + 0.12, a, b, zc - 0.16, zc, WM)
    # frente de tabuas (recuada 0,12 da face dos pes) + mata-juntas 0,12 a frente
    bb(mb, F, -px + 0.15, px - 0.15, yf - 0.34, yf - 0.22, 0.3, zc - 0.42, WM)
    for xx in K.even(-px + 0.15, px - 0.15, 0.9)[:-1]:
        xs = xx + (px - 0.15 - (-px + 0.15)) / (2 * max(1, len(K.even(-px + 0.15, px - 0.15, 0.9))))
        bb(mb, F, xs - 0.07, xs + 0.07, yf - 0.22, yf - 0.1, 0.3, zc - 0.42, WD)
    bb(mb, F, -px + 0.15, px - 0.15, yf - 0.22, yf - 0.1, 0.3, 0.46, WD)   # rodape
    # TOLDO: vigas de cabeca, 3 caibros, tabuado inclinado (telha de madeira) com 3 ripas, sanefa
    bb(mb, F, -W / 2 - 0.25, W / 2 + 0.25, yb + 0.1, yb + 0.4, hb - 0.32, hb, WD)
    bb(mb, F, -W / 2 - 0.25, W / 2 + 0.25, yf - 0.4, yf - 0.1, hf - 0.32, hf, WD)
    s = (hf - hb) / (yf - yb - 0.5)
    zr = lambda y: hb + (y - (yb + 0.25)) * s
    ya, ye = yb - 0.55, yf + 1.0
    for x in (-px, 0.0, px):
        K.beam(mb, F, (x, ya, zr(ya) + 0.1), (x, ye, zr(ye) + 0.1), 0.16, 0.2, WD)
    t = 0.14
    zo = 0.2
    K.ext(mb, F, [(ya - 0.1, zr(ya - 0.1) + zo), (ye + 0.1, zr(ye + 0.1) + zo), (ye + 0.1, zr(ye + 0.1) + zo + t),
                  (ya - 0.1, zr(ya - 0.1) + zo + t)], "x", -W / 2 - 0.45, W / 2 + 0.45, SHG)
    for x in K.even(-W / 2 - 0.2, W / 2 + 0.2, 1.7):
        K.ext(mb, F, [(ya - 0.05, zr(ya - 0.05) + zo + t), (ye + 0.05, zr(ye + 0.05) + zo + t),
                      (ye + 0.05, zr(ye + 0.05) + zo + t + 0.12), (ya - 0.05, zr(ya - 0.05) + zo + t + 0.12)],
              "x", x - 0.09, x + 0.09, WD)
    yv = yf + 0.7
    zv = zr(yv) + 0.06
    mb.rod(F.p(-W / 2 - 0.35, yv, zv), F.p(W / 2 + 0.35, yv, zv), 0.07, WD, 6)
    nv = 3 if W > 4.5 else 2
    sw = (W + 0.4 - 0.12 * (nv - 1)) / nv
    for i in range(nv):
        xa = -W / 2 - 0.2 + i * (sw + 0.12)
        bb(mb, F, xa, xa + sw, yv - 0.04, yv + 0.04, zv - val, zv + 0.02, cloth)
        bb(mb, F, xa, xa + sw, yv - 0.13, yv + 0.13, zv - 0.14, zv + 0.12, cloth)          # bainha em volta do varao
        if cloth == INDIGO and val > 0.6:
            bb(mb, F, xa + 0.15, xa + sw - 0.15, yv + 0.04, yv + 0.16, zv - val + 0.12, zv - val + 0.32, CWHITE)
    # MERCADORIA
    g = goods
    if g == "ceramica":
        for i, xx in enumerate((-1.5, 0.0, 1.5)):
            K.jar(mb, F, xx, -0.25, zc, 0.42 + 0.06 * (i % 2), 0.95 + 0.15 * _h(seed, i), (STD, STP, STD)[i],
                  lid=(i == 1))
        for i, xx in enumerate((-2.0, -0.75, 0.75, 2.0)):
            K.pot(mb, F, xx, 0.75, zc, 0.26, 0.55, (STP, STD, WM, STP)[i])
        for xx in (-1.2, 1.2):
            K.jar(mb, F, xx, -0.1, 0.93, 0.36, 0.8, STD)
    elif g == "tecido":
        bolts(mb, F, -1.25, 0.2, zc, (CRED, INDIGO, CWHITE))
        bolts(mb, F, 1.25, 0.2, zc, (INDIGO, CWHITE, CRED))
        for i, (xx, m) in enumerate(((-1.5, CRED), (0.0, INDIGO), (1.5, CWHITE))):    # panos de amostra pendurados
            bb(mb, F, xx - 0.55, xx + 0.55, yb + 0.36, yb + 0.44, zc + 0.9, hb - 0.2, m)
        K.crate(mb, F, -1.1, -0.1, 0.93, 1.3, 0.9, 0.7)
        K.crate(mb, F, 1.1, -0.1, 0.93, 1.3, 0.9, 0.7)
    elif g == "cestos":
        for i, (xx, yy, m) in enumerate(((-1.6, -0.3, STRAW), (-0.3, 0.35, CWHITE), (1.0, -0.3, STRAW), (2.0, 0.45, WD))):
            basket(mb, F, xx, yy, zc, 0.5 if i % 2 == 0 else 0.42, 0.5, m)
        bale(mb, F, -0.9, -0.15, 0.93, 0.0, 1.5, 0.45)
        bale(mb, F, 1.0, -0.15, 0.93, 0.0, 1.5, 0.45)
    elif g == "lanternas":
        for i, xx in enumerate((-1.2, 1.2)):                                 # 2 chochin pendurados na viga da frente
            zh = hf - 0.32
            mb.rod(F.p(xx, yf - 0.25, zh), F.p(xx, yf - 0.25, zh - 0.35), 0.04, IRON, 6)
            K.chochin(mb, F, (xx, yf - 0.25, zh - 0.35 - 1.15), 0.42, 1.15, (CRED, CWHITE)[i])
        for xx in (-1.3, 1.3):                                               # 2 dobrados (lanterna fechada) no tampo
            K.lathe(mb, F, (xx, -0.2, zc), [(0.42, 0.0), (0.42, 0.12), (0.46, 0.18), (0.46, 0.34), (0.42, 0.4),
                                            (0.42, 0.52)], 8, CRED)
        K.crate(mb, F, 0.0, -0.1, 0.93, 1.6, 1.0, 0.8)
    elif g == "cha":
        K.crate(mb, F, -1.5, -0.1, zc, 1.1, 0.9, 0.7)
        K.crate(mb, F, -1.5, -0.1, zc + 0.7, 0.9, 0.8, 0.55, 0.12)
        for i, xx in enumerate((0.0, 1.4)):
            K.jar(mb, F, xx, -0.2, zc, 0.36, 0.8, (WD, STD)[i], lid=True)
        K.lathe(mb, F, (0.8, 0.75, zc), [(0.26, 0.0), (0.34, 0.12), (0.3, 0.34), (0.14, 0.42), (0.16, 0.48), (0.05, 0.56)],
                8, IRON)                                                     # chaleira de ferro
        K.pot(mb, F, 2.0, 0.7, zc, 0.24, 0.5, STP)
        tub(mb, F, -1.0, -0.1, 0.93, 0.6, 0.6, 8)
        K.crate(mb, F, 1.2, -0.1, 0.93, 1.3, 0.9, 0.7)


def bolts(mb, F, x, y, z, ms, r=0.22, Ln=1.3):
    """rolos de tecido deitados: 3 no tampo (octogono com a face de baixo NO tampo) + 2 ASSENTADOS no vao entre eles"""
    a = r * math.cos(math.pi / 8)
    k = 0
    for row, n in ((0, 3), (1, 2)):
        for i in range(n):
            xx = x + (i - (n - 1) / 2) * (2 * a + 0.02)
            zz = z + a + row * (2 * a - 0.14)
            mb.rod(F.p(xx, y - Ln / 2, zz), F.p(xx, y + Ln / 2, zz), r, ms[k % len(ms)], 8)
            k += 1


def cart(mb, F, load="fardos"):
    """CARRINHO DE MAO (daihachi): leito de tabuas em 2 longarinas que viram os varais, 3 travessas, eixo de ferro,
    2 RODAS (aro, cubo, 8 raios), varal com barra de puxar, 2 pes de descanso; carga apoiada no leito. Comprimento
    ao longo de x (varais para +x), rodas em x = -0,8"""
    R = 1.6
    zb = R + 0.1
    for s in (-1, 1):
        bb(mb, F, -2.6, 4.2, s * 1.15 - 0.13, s * 1.15 + 0.13, zb, zb + 0.3, WD)          # longarina/varal
        K.beam(mb, F, (3.3, s * 1.15, zb + 0.02), (3.55, s * 1.15, 0.0), 0.16, 0.16, WD)  # pe de descanso
        bb(mb, F, 3.4, 3.8, s * 1.15 - 0.16, s * 1.15 + 0.16, 0.0, 0.12, WD)
        y = s * 1.55
        ring_y(mb, F, (-0.8, y, R), R, R - 0.28, 0.26, 12, WD)                            # aro
        K.lathe_y(mb, F, (-0.8, y, R), [(0.32, -0.25), (0.32, 0.25)], 6, WD)                # cubo
        for k in range(6):
            a = 2 * math.pi * (k + 0.5) / 6
            K.beam(mb, F, (-0.8 + 0.3 * math.cos(a), y, R + 0.3 * math.sin(a)),
                   (-0.8 + (R - 0.24) * math.cos(a), y, R + (R - 0.24) * math.sin(a)), 0.12, 0.14, WM)
    mb.rod(F.p(-0.8, -1.82, R), F.p(-0.8, 1.82, R), 0.11, IRON, 8)                       # eixo
    mb.rod(F.p(4.0, -1.3, zb + 0.15), F.p(4.0, 1.3, zb + 0.15), 0.12, WD, 8)              # barra de puxar
    for x in (-2.35, -0.8, 1.4):
        bb(mb, F, x - 0.14, x + 0.14, -1.3, 1.3, zb - 0.22, zb, WD)                      # travessas
    n = 6
    for i in range(n):                                                                    # tabuado do leito
        a = -2.6 + 4.2 * i / n + (0.03 if i else 0.0)
        b = -2.6 + 4.2 * (i + 1) / n - (0.03 if i < n - 1 else 0.0)
        bb(mb, F, a, b, -1.02, 1.02, zb + 0.3, zb + 0.44, WM)
    zt = zb + 0.44
    if load == "fardos":
        bale(mb, F, -1.75, -0.52, zt, math.pi / 2 + 0.04, 1.6, 0.5)
        bale(mb, F, -1.75, 0.52, zt, math.pi / 2 - 0.05, 1.6, 0.5)
        bale(mb, F, -0.05, 0.0, zt, math.pi / 2, 1.6, 0.5)
        bale(mb, F, -1.75, 0.0, zt + 0.86, math.pi / 2, 1.6, 0.5)
    else:
        K.crate(mb, F, -1.5, -0.35, zt, 1.6, 1.2, 1.0, 0.05)
        K.crate(mb, F, 0.2, 0.3, zt, 1.4, 1.1, 0.9, -0.08)
        K.barrel(mb, F, -1.4, 0.0, zt + 1.0, 0.5, 1.0)


def wash_line(mb, F, Ln=8.0, h=5.6, seed=0, base=True):
    """VARAL: 2 postes em pedras-base com forquilha (2 tocos), vara de bambu apoiada nas forquilhas, roupas e panos
    pendurados (a vara atravessa a bainha), vaos de 0,25 entre as pecas"""
    for s in (-1, 1):
        x = s * Ln / 2
        if base:
            K.rock_base(mb, F, x, 0.0, 0.0, 0.6, 0.35, STD)
        else:                                                                # vao estreito: estaca com colar
            bb(mb, F, x - 0.24, x + 0.24, -0.24, 0.24, -0.15, 0.3, STD)
        bb(mb, F, x - 0.15, x + 0.15, -0.15, 0.15, 0.2, h - 0.05, WD)
        for sy in (-1, 1):
            K.beam(mb, F, (x, 0.0, h - 0.4), (x, sy * 0.32, h + 0.25), 0.11, 0.11, WD)
    mb.rod(F.p(-Ln / 2 - 0.3, 0.0, h + 0.02), F.p(Ln / 2 + 0.3, 0.0, h + 0.02), 0.09, WM, 6)
    cols = (CWHITE, INDIGO, CWHITE, CRED, STRAW, INDIGO, CWHITE)
    mg = 0.5 if Ln > 4.0 else 0.3
    n = max(2, int((Ln - 2 * mg) / 1.6))
    ws = [0.7 + 0.6 * _h("varal", seed, k) for k in range(n)]
    sc = (Ln - 2 * mg - 0.25 * (n - 1)) / sum(ws)
    x = -Ln / 2 + mg
    for k in range(n):
        w = ws[k] * sc
        ln = 1.3 + 1.3 * _h("varal", seed, k, "l")
        yo = 0.02 if k % 2 else -0.02
        m = cols[(k + seed) % len(cols)]
        bb(mb, F, x, x + w, yo - 0.04, yo + 0.04, h + 0.02 - ln, h + 0.1, m)
        if m == INDIGO and ln > 2.0:                                         # barra branca (sem letras) 0,12 a frente
            bb(mb, F, x + 0.12, x + w - 0.12, yo + 0.04, yo + 0.16, h - ln + 0.25, h - ln + 0.5, CWHITE)
        x += w + 0.25


def well(mb, F):
    """POCO (ido): boca de cantaria (coroa com espessura, capa escura, fundo escuro recuado), 2 esteios de madeira
    em sapatas, travessa baixa (nuki) e viga de cumeeira, POLIA de ferro, telhadinho de 2 aguas de tabuas com
    cumeeira, corda com balde pendurado e outro balde apoiado na capa"""
    ro, ri, hc = 1.6, 1.15, 2.0
    n = 8
    rings = []
    for rr, zz in ((ro, -0.2), (ro, hc), (ri, hc), (ri, 0.6)):
        rings.append([(rr * math.cos(2 * math.pi * j / n), rr * math.sin(2 * math.pi * j / n), zz) for j in range(n)])
    K.loft(mb, F, rings, STP, caps=(False, False))
    K.lathe(mb, F, (0, 0, 0.6), [(ri, -0.1), (ri, 0.02)], n, STD)                         # fundo escuro (agua)
    rings = []
    for rr, zz in ((ro + 0.12, hc - 0.05), (ro + 0.12, hc + 0.25), (ri - 0.1, hc + 0.25), (ri - 0.1, hc - 0.05)):
        rings.append([(rr * math.cos(2 * math.pi * j / n), rr * math.sin(2 * math.pi * j / n), zz) for j in range(n)])
    rings.append(rings[0])
    K.loft(mb, F, rings, STD, caps=(False, False))                                      # capa da boca
    hp = 5.6
    for s in (-1, 1):
        x = s * 2.1
        bb(mb, F, x - 0.4, x + 0.4, -0.4, 0.4, -0.15, 0.3, STD)
        bb(mb, F, x - 0.17, x + 0.17, -0.17, 0.17, 0.3, hp, WD)
    bb(mb, F, -2.55, 2.55, -0.12, 0.12, 2.9, 3.15, WD)                                  # nuki (passa os esteios)
    bb(mb, F, -2.75, 2.75, -0.2, 0.2, hp - 0.4, hp, WD)                                 # viga
    mb.rod(F.p(0, 0, hp - 0.4), F.p(0, 0, hp - 0.85), 0.05, IRON, 6)
    ring_y(mb, F, (0.0, 0.0, hp - 1.15), 0.34, 0.09, 0.16, 8, IRON)                      # polia
    mb.rod(F.p(0, -0.16, hp - 1.15), F.p(0, 0.16, hp - 1.15), 0.11, IRON, 6)
    # telhadinho de 2 aguas (tabuas sobre a viga), cumeeira escura
    zr, ze, ye = hp + 1.0, hp + 0.05, 1.75
    for s in (-1, 1):
        K.ext(mb, F, [(0.0, zr), (s * ye, ze), (s * ye, ze + 0.14), (0.0, zr + 0.14)], "x", -3.0, 3.0, SHG)
        K.beam(mb, F, (-2.75, 0.0, hp), (-2.75, s * (ye - 0.2), ze + 0.04), 0.14, 0.16, WD)
        K.beam(mb, F, (2.75, 0.0, hp), (2.75, s * (ye - 0.2), ze + 0.04), 0.14, 0.16, WD)
    K.ext(mb, F, [(-0.22, zr + 0.02), (0.22, zr + 0.02), (0.18, zr + 0.36), (-0.18, zr + 0.36)], "x", -3.15, 3.15, WD)
    bb(mb, F, -0.2, 0.2, -0.2, 0.2, hp, zr + 0.05, WD)                                   # pendural
    # corda + balde pendurado sobre a boca; 2o balde apoiado na capa
    mb.rod(F.p(0, 0.34, hp - 1.15), F.p(0, 0.34, 3.3), 0.04, STRAW, 5)
    tub(mb, F, 0.0, 0.34, 2.75, 0.32, 0.52, 8)
    mb.rod(F.p(-0.3, 0.34, 3.27), F.p(0.3, 0.34, 3.27), 0.04, IRON, 5)
    tub(mb, F, 0.0, -(ro + ri) / 2 - 0.04, hc + 0.25, 0.3, 0.5, 8)


def _star(mb, F, cx, cz, R, y0, y1, m=GOLD):
    """estrela de 5 pontas (iconografia aprovada do summon) em prismas convexos: pentagono + 5 pontas"""
    rI = R * 0.42
    inner = [(cx + rI * math.cos(math.pi / 2 + 2 * math.pi * (k + 0.5) / 5), cz + rI * math.sin(math.pi / 2 + 2 * math.pi * (k + 0.5) / 5))
             for k in range(5)]
    K.ext(mb, F, inner, "y", y0, y1, m)
    for k in range(5):
        a = math.pi / 2 + 2 * math.pi * k / 5
        tip = (cx + R * math.cos(a), cz + R * math.sin(a))
        K.ext(mb, F, [inner[(k - 1) % 5], inner[k], tip][::1], "y", y0, y1, m)


def signpost(mb, F, boards):
    """POSTE DE DIRECAO: sapata de pedra, poste com cinta de ferro e chapeuzinho de 4 aguas; tabuas em SETA (lisas,
    sem texto) presas no poste, cada uma apontando para o seu rumo (graus locais); star=True poe a estrela dourada
    do summon atravessando a tabua (sai 0,12 de cada lado)"""
    bb(mb, F, -0.5, 0.5, -0.5, 0.5, -0.2, 0.35, STD)
    bb(mb, F, -0.18, 0.18, -0.18, 0.18, 0.35, 6.3, WD)
    bb(mb, F, -0.22, 0.22, -0.22, 0.22, 1.2, 1.45, IRON)
    K.hip_cap(mb, F, (0.0, 0.0), 0.24, 0.24, 6.3, 0.3, 0.32, 0.08, SHG, 0.06)
    for deg, z, star in boards:
        Fb = sub(F, ang=math.radians(deg))
        poly = [(0.18, z - 0.34), (2.25, z - 0.34), (2.7, z), (2.25, z + 0.34), (0.18, z + 0.34)]
        K.ext(mb, Fb, poly, "y", -0.08, 0.08, WM)
        K.ext(mb, Fb, [(0.18, z - 0.4), (0.42, z - 0.4), (0.42, z + 0.4), (0.18, z + 0.4)], "y", -0.13, 0.13, WD)
        for xx in (0.3,):
            mb.rod(Fb.p(xx, -0.2, z), Fb.p(xx, 0.2, z), 0.05, IRON, 6)
        if star:
            _star(mb, Fb, 1.3, z, 0.27, -0.2, 0.2)


def suzu(mb, F, z_top, z_bot):
    """SINO do santuario: gancho de ferro, sino dourado (ombro, bojo, fenda escura), corda trancada vermelho/branco"""
    mb.rod(F.p(0, 0, z_top), F.p(0, 0, z_top - 0.35), 0.05, IRON, 6)
    zb = z_top - 1.25
    K.lathe(mb, F, (0, 0, zb), [(0.08, -0.02), (0.36, 0.06), (0.48, 0.3), (0.45, 0.6), (0.28, 0.82), (0.08, 0.9)],
            10, GOLD)
    bb(mb, F, -0.5, 0.5, -0.06, 0.06, zb + 0.24, zb + 0.32, IRON)
    for k, m in enumerate((CRED, CWHITE, CRED)):
        a = 2 * math.pi * k / 3
        ox, oy = 0.07 * math.cos(a), 0.07 * math.sin(a)
        mb.rod(F.p(ox, oy, zb + 0.02), F.p(-ox, -oy, z_bot), 0.06, m, 5)
    K.lathe(mb, F, (0, 0, z_bot - 0.5), [(0.04, 0.0), (0.16, 0.12), (0.12, 0.5)], 6, CRED)    # borla


def saisen(mb, F, W=2.4, D=1.1, h=1.2):
    """CAIXA DE OFERENDAS: caixa de tabuas escuras com cantoneiras, tampo de ripas em V (frestas), pes"""
    bb(mb, F, -W / 2, W / 2, -D / 2, D / 2, 0.15, h - 0.25, WM)
    for x in (-W / 2 + 0.12, W / 2 - 0.12):
        for y in (-D / 2 + 0.12, D / 2 - 0.12):
            bb(mb, F, x - 0.14, x + 0.14, y - 0.14, y + 0.14, 0.0, h - 0.2, WD)
    bb(mb, F, -W / 2 - 0.08, W / 2 + 0.08, -D / 2 - 0.08, D / 2 + 0.08, h - 0.3, h - 0.2, WD)
    for i in range(7):
        x = -W / 2 + 0.25 + (W - 0.5) * i / 6
        for s in (-1, 1):
            K.beam(mb, F, (x, s * (D / 2 - 0.05), h - 0.2), (x, s * 0.08, h - 0.48), 0.12, 0.08, WD)


def ema_rack(mb, F, W=3.4):
    """QUADRO DE EMA: 2 pes em sapatas, 2 trilhos, telhadinho de tabuas; plaquinhas de madeira em pentagono (LISAS,
    sem escrita) penduradas por cordao vermelho dos 2 lados (frente e verso)"""
    for s in (-1, 1):
        x = s * W / 2
        bb(mb, F, x - 0.3, x + 0.3, -0.3, 0.3, -0.15, 0.2, STD)
        bb(mb, F, x - 0.13, x + 0.13, -0.13, 0.13, 0.2, 3.9, WD)
    for z in (2.1, 3.1):
        bb(mb, F, -W / 2 - 0.2, W / 2 + 0.2, -0.08, 0.08, z - 0.08, z + 0.08, WD)
    for s in (-1, 1):
        K.ext(mb, F, [(0.0, 4.45), (s * 0.95, 3.85), (s * 0.95, 3.97), (0.0, 4.57)], "x", -W / 2 - 0.45, W / 2 + 0.45, SHG)
    bb(mb, F, -W / 2 - 0.1, W / 2 + 0.1, -0.12, 0.12, 3.85, 4.5, WD)
    k = 0
    for z in (2.1, 3.1):
        for side in (1,):
            for x in K.even(-W / 2 + 0.25, W / 2 - 0.25, 0.62):
                if _h("ema", z, side, x) < 0.22:
                    continue
                y = side * 0.14
                zt = z - 0.12
                K.ext(mb, F, [(x - 0.26, zt - 0.5), (x + 0.26, zt - 0.5), (x + 0.26, zt - 0.14), (x, zt), (x - 0.26, zt - 0.14)],
                      "y", y - 0.03, y + 0.03, WM)
                bb(mb, F, x - 0.03, x + 0.03, y - 0.04, y + 0.04, zt - 0.02, z - 0.06, CRED)
                k += 1
    return k


def chozuya(mb, F):
    """PAVILHAO DE ABLUCOES: 4 pilares em pedras-base, vigas, telhado de 4 aguas pequeno (chapeu do kit), BACIA de pedra
    com borda e agua escura recuada, BICA de bambu com suporte, 2 conchas (hishaku) na barra da bacia"""
    hx, hy, h = 1.9, 1.4, 5.2
    for sx in (-1, 1):
        for sy in (-1, 1):
            K.rock_base(mb, F, sx * hx, sy * hy, 0.0, 0.5, 0.3, STD)
            bb(mb, F, sx * hx - 0.18, sx * hx + 0.18, sy * hy - 0.18, sy * hy + 0.18, 0.25, h, WD)
    for sy in (-1, 1):
        bb(mb, F, -hx - 0.4, hx + 0.4, sy * hy - 0.2, sy * hy + 0.2, h - 0.45, h, WD)
    for sx in (-1, 1):
        bb(mb, F, sx * hx - 0.2, sx * hx + 0.2, -hy - 0.4, hy + 0.4, h - 0.45, h - 0.02, WD)
    K.hip_cap(mb, F, (0.0, 0.0), hx + 0.2, hy + 0.2, h, 0.9, 1.2, 0.2, SHG, 0.25)
    # bacia: bloco de pedra com borda e agua recuada (escura)
    bb(mb, F, -1.3, 1.3, -0.65, 0.65, 0.0, 1.0, STP)
    rings = []
    for (ax, ay, zz) in ((1.3, 0.65, 1.0), (1.3, 0.65, 1.3), (1.05, 0.4, 1.3), (1.05, 0.4, 1.05)):
        rings.append([(ax, ay, zz), (-ax, ay, zz), (-ax, -ay, zz), (ax, -ay, zz)])
    rings.append(rings[0])
    K.loft(mb, F, rings, STP, caps=(False, False))
    bb(mb, F, -1.05, 1.05, -0.4, 0.4, 1.0, 1.12, STD)                                   # agua escura
    # bica de bambu num suporte, caindo na bacia
    bb(mb, F, 1.45, 1.65, -0.1, 0.1, 0.0, 2.1, WD)
    mb.rod(F.p(1.7, 0.0, 1.95), F.p(0.5, 0.0, 1.62), 0.09, WM, 6)
    # barra das conchas + 2 conchas apoiadas
    mb.rod(F.p(-1.0, -0.6, 1.36), F.p(0.8, -0.6, 1.36), 0.05, WD, 5)
    for x in (-0.5, 0.3):
        mb.rod(F.p(x, -0.6, 1.4), F.p(x, 0.15, 1.42), 0.035, WM, 5)
        K.lathe(mb, F, (x, 0.3, 1.33), [(0.1, 0.0), (0.16, 0.06), (0.16, 0.22)], 6, WM, caps=(True, False))


def cluster(mb, F, items):
    """pilha de carga/uso: items = [(tipo, dx, dy, dz, args...)] no referencial F"""
    for it in items:
        t, x, y, z = it[0], it[1], it[2], it[3]
        a = it[4:] if len(it) > 4 else ()
        if t == "barril":
            K.barrel(mb, F, x, y, z, *a)
        elif t == "caixa":
            K.crate(mb, F, x, y, z, *a)
        elif t == "jarro":
            K.jar(mb, F, x, y, z, *a)
        elif t == "pote":
            K.pot(mb, F, x, y, z, *a)
        elif t == "tina":
            tub(mb, F, x, y, z, *a)
        elif t == "fardo":
            bale(mb, F, x, y, z, *a)
        elif t == "cesto":
            basket(mb, F, x, y, z, *a)


# ================================================================== APOIO (raio) e CONFLITO (BVH) contra a cena
SKIP = ("COL_", "PREVIEW_", "SCALE_", "OP_Prop_", "OP_Veg_", "OP_Plz_OreProxy", "BLK_", "CAM_", "VFX_")


class Probe:
    def __init__(self):
        self.objs = []
        for o in bpy.data.objects:
            if o.type != "MESH" or o.name.startswith(SKIP) or o.hide_render or not o.data.polygons:
                continue
            if o.users_collection and o.users_collection[0].name in ("00_REFERENCE", "_SCALE_REFERENCE"):
                continue
            ws = [o.matrix_world @ Vector(c) for c in o.bound_box]
            lo = Vector((min(v.x for v in ws), min(v.y for v in ws), min(v.z for v in ws)))
            hi = Vector((max(v.x for v in ws), max(v.y for v in ws), max(v.z for v in ws)))
            self.objs.append((o, lo, hi))
        self.cache = {}

    def tree(self, o):
        t = self.cache.get(o.name)
        if t is None:
            mw = o.matrix_world
            vs = [mw @ v.co for v in o.data.vertices]
            t = BVHTree.FromPolygons(vs, [p.vertices[:] for p in o.data.polygons])
            self.cache[o.name] = t
        return t

    def cands(self, lo, hi):
        return [o for o, a, b in self.objs if a.x <= hi.x and b.x >= lo.x and a.y <= hi.y and b.y >= lo.y
                and a.z <= hi.z and b.z >= lo.z]

    def ground(self, x, y, zref, up=2.6, down=3.0):
        org = Vector((x, y, zref + up))
        best = None
        for o in self.cands(Vector((x - 0.01, y - 0.01, zref - down)), Vector((x + 0.01, y + 0.01, zref + up))):
            hit = self.tree(o).ray_cast(org, Vector((0, 0, -1)), up + down)
            if hit[0] is not None and hit[1].z > 0.5 and (best is None or hit[0].z > best[0]):
                best = (hit[0].z, o.name)
        return best

    def clash(self, corners, z0, z1):
        """volume (prisma do contorno 'corners' de z0 a z1) x malhas da cena -> nomes que atravessam"""
        n = len(corners)
        vs = [Vector((x, y, z0)) for x, y in corners] + [Vector((x, y, z1)) for x, y in corners]
        fs = [list(range(n))[::-1], list(range(n, 2 * n))] + [[i, (i + 1) % n, n + (i + 1) % n, n + i] for i in range(n)]
        bt = BVHTree.FromPolygons(vs, fs)
        lo = Vector((min(v.x for v in vs), min(v.y for v in vs), z0))
        hi = Vector((max(v.x for v in vs), max(v.y for v in vs), z1))
        out = []
        for o in self.cands(lo, hi):
            t = self.tree(o)
            if t.overlap(bt):
                out.append(o.name)
                continue
            # volume que engole uma peca inteira (sem cruzar faces): vertice de dentro
            v0 = o.data.vertices
            if len(v0) < 400:
                mw = o.matrix_world
                for v in v0:
                    w = mw @ v.co
                    if lo.x < w.x < hi.x and lo.y < w.y < hi.y and z0 < w.z < z1 and _in_poly(w.x, w.y, corners):
                        out.append(o.name)
                        break
        return out


def _in_poly(x, y, poly):
    return L.point_in_poly(x, y, poly)


# ================================================================== CATALOGO DE PECAS (pegada, altura, colisao)
# tipo -> (meia largura x, meia profundidade y, altura, colisao (sx, sy, sz) ou None, folga extra das rotas)
FOOT = {
    "banca": (2.75, 1.65, 6.9, (5.0, 2.4, 2.8)),
    "carrinho": (3.0, 1.9, 3.4, (6.8, 3.6, 2.6)),
    "poco": (2.6, 1.9, 6.7, (4.6, 3.6, 2.4)),
    "varal": (4.5, 0.5, 6.0, None),
    "placa": (1.4, 1.4, 6.6, (0.6, 0.6, 6.3)),
    "poste": (2.0, 0.6, 9.5, (0.9, 0.9, 8.4)),
    "andon": (1.0, 1.0, 8.0, (1.1, 1.1, 7.6)),
    "estandarte": (2.4, 1.0, 11.0, (1.9, 1.9, 11.0)),
    "chozuya": (2.6, 2.2, 6.6, (4.4, 3.4, 3.0)),
    "ema": (2.2, 0.6, 4.6, (3.8, 0.7, 3.6)),
    "carga": (1.6, 1.4, 2.4, (3.0, 2.6, 2.2)),
    "carga_baixa": (1.4, 1.2, 1.6, None),
}
LOG = []          # (nome, tipo, x, y, z, avisos)
TRIS = {}


def _ntris(mb):
    return sum(len(f.verts) - 2 for f in mb.bm.faces)
LIGHTS = []


def _corners(x, y, a, hx, hy):
    c, s = math.cos(a), math.sin(a)
    return [(x + c * u - s * v, y + s * u + c * v) for u, v in ((-hx, -hy), (hx, -hy), (hx, hy), (-hx, hy))]


def _route_gap(x, y, r):
    best = 1e9
    for nm, (pts, _) in L.routes().items():
        best = min(best, L.polyline_dist(x, y, pts) - r)
    return best


def place(PR, mb, name, kind, x, y, face_deg, zref, fn, *args, foot=None, col=True, rr=None, **kw):
    """assenta a peca no chao REAL (maior raio sob o contorno), confere conflito, rota e MiningZone, desenha e poe a
    colisao. face_deg = rumo do mundo para onde a FRENTE (+y local) olha"""
    hx, hy, h, cs = foot or FOOT[kind]
    a = math.radians(face_deg) - math.pi / 2
    pts = _corners(x, y, a, hx * 0.8, hy * 0.8) + [(x, y)]
    zs = []
    for px, py in pts:
        g = PR.ground(px, py, zref)
        if g:
            zs.append(g[0])
    warn = []
    if not zs:
        z = zref
        warn.append("SEM CHAO")
    else:
        z = max(zs)
        if max(zs) - min(zs) > 0.35:
            warn.append("desnivel %.2f" % (max(zs) - min(zs)))
    hit = PR.clash(_corners(x, y, a, hx, hy), z + 0.4, z + h)
    if hit:
        warn.append("ENCOSTA " + ",".join(sorted(set(hit))[:4]))
    r = rr if rr is not None else math.hypot(hx, hy) * 0.85
    gap = _route_gap(x, y, r)
    if gap < 1.6:
        warn.append("ROTA %.1f" % gap)
    x0, y0, x1, y1 = L.MINE_RECT
    if x0 - 8 - r < x < x1 + 8 + r and y0 - 8 - r < y < y1 + 8 + r:
        warn.append("MININGZONE")
    F = Frame(x, y, z, a)
    t0 = _ntris(mb)
    res = fn(mb, F, *args, **kw)
    TRIS[name] = _ntris(mb) - t0
    if col and cs:
        col_box("OP_Prop" + kind.capitalize().replace("_", ""), cs, F.p(0.0, 0.0, cs[2] / 2), F.r())
    LOG.append((name, kind, x, y, z, warn))
    return F, res


# ================================================================== CONJUNTOS (posicoes dirigidas)
def _lamp(mb, F, name, chochin=False):
    if chochin:
        K.lantern_post(mb, F, 8.4, 1.6, name, 40.0)          # feira: travessa com 2 chochin vermelhos
    else:
        K.lantern_box_post(mb, F, 7.6, name, 35.0)          # cais / travessa / santuario: andon de armacao
    LIGHTS.append(name)


def _banner(mb, F, cloth, crest, side):
    K.banner(mb, F, 10.5, cloth, crest, 2.0, side)


def mercado(PR, mb):
    """FEIRA DA VIELA DO CANAL (T1): bancas dos 2 lados (frente para a viela), entrada marcada por 2 nobori"""
    z = T1
    st = [("BancaTecido", -82.4, 86.3, -90, "tecido", INDIGO), ("BancaCeramica", -76.8, 86.3, -90, "ceramica", CWHITE),
          ("BancaCestos", -125.8, 86.3, -90, "cestos", INDIGO), ("BancaLanternas", -120.0, 86.3, -90, "lanternas", INDIGO),
          ("BancaCha", -80.8, 67.9, 90, "cha", CRED)]
    for i, (nm, x, y, deg, g, cl) in enumerate(st):
        place(PR, mb, nm, "banca", x, y, deg, z, stall, 5.0, 2.4, g, cl, i, 0.42 if g == "lanternas" else 0.75)
    place(PR, mb, "Carrinho_Mercado", "carrinho", -57.5, 68.6, 90, z, cart, "fardos")
    place(PR, mb, "Poco_Mercado", "poco", -117.0, 67.0, 90, z, well)
    place(PR, mb, "Varal_SW", "varal", -90.25, 61.6, 90, z, wash_line, 2.3, 5.8, 1, False, foot=(1.4, 0.3, 6.0, None))
    place(PR, mb, "Poste_Mercado", "poste", -88.0, 84.8, 90, z, _lamp, "L_OPProp_Lamp_Mercado", True)
    for nm, x, y, side in (("Nobori_FeiraS", -46.0, 68.6, 1), ("Nobori_FeiraN", -52.5, 85.1, 1)):
        place(PR, mb, nm, "estandarte", x, y, 90, z, _banner, INDIGO, CWHITE, side, rr=1.2)   # rr: so a base no chao
    place(PR, mb, "Carga_SW1", "carga_baixa", -65.6, 67.0, 90, z, cluster,
          [("barril", -0.5, 0.0, 0.0, 0.7, 1.5), ("tina", 0.9, 0.3, 0.0, 0.7, 0.7)])
    place(PR, mb, "Carga_NW34", "carga", -111.0, 87.2, -90, z, cluster,
          [("barril", -0.6, 0.0, 0.0), ("barril", 0.85, 0.2, 0.0, 0.7, 1.5), ("caixa", 0.0, -0.1, 1.6, 1.3, 1.0, 0.8, 0.2)])
    place(PR, mb, "Carga_SW4", "carga", -128.6, 68.4, 90, z, cluster,
          [("fardo", 0.0, -0.55, 0.0, 0.0, 1.7, 0.55), ("fardo", 0.0, 0.55, 0.0, 0.0, 1.7, 0.55),
           ("fardo", 0.0, 0.0, 0.92, 0.0, 1.7, 0.55)])
    place(PR, mb, "Carga_SW3", "carga_baixa", -94.4, 67.4, 90, z, cluster,
          [("jarro", -0.5, 0.0, 0.0, 0.55, 1.3, STD), ("jarro", 0.6, 0.35, 0.0, 0.45, 1.0, STP),
           ("pote", 0.5, -0.6, 0.0, 0.32, 0.7)])


def cais(PR, mb):
    """CAIS DO CANAL (P): carga encostada nos fundos do quarteirao oeste; alem do canal: poco, varal, tina"""
    z = P
    place(PR, mb, "Carga_CaisW1", "carga", -156.2, 134.0, 0, z, cluster,
          [("caixa", 0.0, -0.7, 0.0, 1.6, 1.2, 1.0), ("caixa", 0.0, 0.7, 0.0, 1.6, 1.2, 1.0, 0.06),
           ("caixa", 0.0, 0.0, 1.0, 1.4, 1.1, 0.9, -0.1), ("barril", 0.0, 2.1, 0.0)])
    place(PR, mb, "Carga_CaisW2", "carga", -156.2, 168.0, 0, z, cluster,
          [("fardo", -0.55, 0.0, 0.0, math.pi / 2, 1.7, 0.55), ("fardo", 0.55, 0.0, 0.0, math.pi / 2, 1.7, 0.55),
           ("fardo", 0.0, 0.0, 0.92, math.pi / 2, 1.7, 0.55)])
    place(PR, mb, "Carrinho_Cais", "carrinho", -156.0, 225.5, 180, z, cart, "caixas")
    place(PR, mb, "Poste_Cais", "andon", -156.8, 196.6, 0, z, _lamp, "L_OPProp_Lamp_Cais")
    place(PR, mb, "Poco_Alem", "poco", -205.0, 164.5, 0, z, well)
    place(PR, mb, "Varal_Alem", "varal", -206.5, 239.0, 90, z, wash_line, 10.0, 5.6, 5)
    place(PR, mb, "Carga_Alem", "carga_baixa", -194.2, 157.4, 0, z, cluster,
          [("tina", 0.0, 0.0, 0.0, 0.8, 0.75), ("jarro", 0.2, 1.5, 0.0, 0.5, 1.2, STD)])
    place(PR, mb, "Poste_Alem", "andon", -191.0, 216.3, 0, z, _lamp, "L_OPProp_Lamp_Alem")


def leste(PR, mb):
    """TRAVESSA DO PORTO e saida da rua de chegada (T1): carrinho no mirante, carga, varal, placas"""
    z = T1
    place(PR, mb, "Carga_Mirante", "carga", 102.0, 69.8, 90, z, cluster,
          [("caixa", -0.9, 0.0, 0.0, 1.6, 1.2, 1.0), ("caixa", 0.8, 0.1, 0.0, 1.4, 1.1, 0.9, 0.1),
           ("caixa", -0.8, 0.0, 1.0, 1.3, 1.0, 0.8, -0.08), ("barril", 2.2, 0.2, 0.0, 0.7, 1.5)])
    place(PR, mb, "Carga_E5", "carga", 88.0, 78.8, 90, z, cluster,
          [("fardo", -0.9, 0.0, 0.0, 0.0, 1.7, 0.55), ("fardo", 0.9, 0.0, 0.0, 0.0, 1.7, 0.55),
           ("fardo", 0.0, 0.0, 0.92, 0.0, 1.7, 0.55)])
    place(PR, mb, "Varal_Leste", "varal", 96.9, 66.4, 90, z, wash_line, 2.8, 5.8, 2, False, foot=(1.65, 0.3, 6.0, None))
    place(PR, mb, "Poste_Travessa", "andon", 70.5, 79.6, 90, z, _lamp, "L_OPProp_Lamp_Travessa")
    # placas: saida da rua de chegada para a viela leste (summon, estrela) e para a viela do canal (feira)
    place(PR, mb, "Placa_Leste", "placa", 43.6, 102.6, 90, z, signpost, [(0.0, 5.0, True), (180.0, 4.2, False)], rr=0.6)
    place(PR, mb, "Placa_Canal", "placa", -15.6, 90.4, 90, z, signpost, [(180.0, 5.0, False), (90.0, 4.2, False)], rr=0.6)


def santuario(PR, mb):
    """SANTUARIO NE (P): sino e caixa de oferendas no haiden, quadro de ema, chozuya"""
    xh, yh = 146.5, 306.0                       # haiden (op_capital.shrine): frente para -x, estrado a P + 1,4
    deck = P + 1.4
    xf = xh - 4.7 + 0.5                         # viga da frente (nuki) em x = 142,3, base a deck + 7,6 - 2,4
    zn = deck + 7.6 - 2.4
    Fb = Frame(xf, yh, 0.0, 0.0)
    suzu(mb, Fb, zn, deck + 1.6)
    LOG.append(("Sino", "sino", xf, yh, zn, []))
    Fs = Frame(xh - 2.4, yh, deck, math.pi / 2)
    saisen(mb, Fs)
    col_box("OP_PropSaisen", (2.4, 1.1, 1.2), Fs.p(0, 0, 0.6), Fs.r())
    LOG.append(("Saisen", "saisen", Fs.o.x, Fs.o.y, deck, []))
    place(PR, mb, "Ema", "ema", 154.6, 299.0, 180, P, ema_rack)
    place(PR, mb, "Chozuya", "chozuya", 152.0, 319.4, -90, P, chozuya)


def terraco(PR, mb):
    pass


# ================================================================== CAMERAS
CAMS = {
    "CAM_OP_M4Prp_PH_Feira": ((-40.0, 80.6, T1 + EYE), (-130.0, 81.0, T1 + 3.5), 22),
    "CAM_OP_M4Prp_PH_FeiraEntrada": ((-10.0, 87.0, T1 + EYE), (-60.0, 81.0, T1 + 6.0), 22),
    "CAM_OP_M4Prp_PH_FeiraOeste": ((-134.0, 78.5, T1 + EYE), (-60.0, 80.0, T1 + 3.5), 22),
    "CAM_OP_M4Prp_PH_Cais": ((-163.0, 122.0, P + EYE), (-157.0, 240.0, P + 3.0), 22),
    "CAM_OP_M4Prp_PH_Alem": ((-187.0, 148.0, P + EYE), (-206.0, 240.0, P + 4.0), 22),
    "CAM_OP_M4Prp_PH_Travessa": ((53.0, 75.0, T1 + EYE), (112.0, 72.0, T1 + 3.0), 22),
    "CAM_OP_M4Prp_PH_Santuario": ((119.0, 306.0, P + EYE), (150.0, 306.0, P + 4.5), 22),
    "CAM_OP_M4Prp_PH_RuaChegada": ((0.0, 66.0, T1 + EYE), (8.0, 112.0, T1 + 4.0), 22),
    "CAM_OP_M4Prp_Aerea_Feira": ((-30.0, 50.0, T1 + 34.0), (-100.0, 80.0, T1), 24),
    "CAM_OP_M4Prp_Close_BancaCeramica": ((-75.0, 79.8, T1 + 4.6), (-77.0, 86.3, T1 + 2.8), 24),
    "CAM_OP_M4Prp_Close_BancaTecido": ((-85.0, 80.5, T1 + 4.6), (-82.4, 86.3, T1 + 3.0), 24),
    "CAM_OP_M4Prp_Close_BancaLanternas": ((-117.0, 80.0, T1 + 4.2), (-121.0, 86.3, T1 + 3.4), 24),
    "CAM_OP_M4Prp_Close_BancaCestos": ((-127.5, 80.2, T1 + 4.8), (-125.8, 86.3, T1 + 2.8), 24),
    "CAM_OP_M4Prp_Close_BancaCha": ((-77.8, 74.6, T1 + 4.6), (-80.8, 68.0, T1 + 2.8), 24),
    "CAM_OP_M4Prp_Close_Carrinho": ((-51.0, 74.5, T1 + 4.5), (-58.0, 68.6, T1 + 1.8), 24),
    "CAM_OP_M4Prp_Close_Poco": ((-112.0, 74.0, T1 + 5.0), (-117.0, 67.0, T1 + 3.0), 24),
    "CAM_OP_M4Prp_Close_Varal": ((-86.0, 74.0, T1 + 4.6), (-90.3, 61.6, T1 + 4.6), 24),
    "CAM_OP_M4Prp_Close_Placa": ((34.0, 110.0, T1 + 5.4), (43.6, 102.6, T1 + 4.6), 24),
    "CAM_OP_M4Prp_Close_Sino": ((136.5, 302.5, P + 5.2), (142.3, 306.0, P + 4.5), 24),
    "CAM_OP_M4Prp_Close_Chozuya": ((146.5, 311.5, P + 5.5), (152.0, 319.4, P + 3.0), 22),
    "CAM_OP_M4Prp_Close_Ema": ((149.0, 297.0, P + 4.2), (154.6, 299.0, P + 2.6), 24),
    "CAM_OP_M4Prp_Close_CargaCais": ((-162.0, 160.0, P + 4.5), (-156.0, 168.0, P + 1.2), 24),
}


def _cams():
    for n, (loc, tgt, lens) in CAMS.items():
        if bpy.data.objects.get(n) is None:
            DL.camera(n, loc, tgt, lens)


# ================================================================== BUILD
def build():
    if bpy.data.objects.get(SENTINEL):
        return
    LOG.clear()
    LIGHTS.clear()
    bpy.context.view_layer.update()
    PR = Probe()
    mb = MB(SENTINEL, COLL, random.Random(509), detail="hero")
    mercado(PR, mb)
    cais(PR, mb)
    leste(PR, mb)
    santuario(PR, mb)
    terraco(PR, mb)
    ob = mb.finish()
    _cams()
    tris = sum(len(p.vertices) - 2 for p in ob.data.polygons) if ob else 0
    nw = 0
    for nm, kind, x, y, z, warn in LOG:
        if warn:
            nw += 1
            print("op_props AVISO %-18s %-11s (%.1f, %.1f, %.2f): %s" % (nm, kind, x, y, z, "; ".join(warn)))
    print("op_props tris por peca: " + ", ".join("%s %d" % kv for kv in sorted(TRIS.items(), key=lambda t: -t[1])))
    print("op_props: %d pecas, %d tris, %d materiais, %d luzes NightOnly, %d avisos" % (
        len(LOG), tris, len(ob.data.materials) if ob else 0, len(LIGHTS), nw))


# ================================================================== AUDITORIA (flutuando / encostado)
def audit(prefixes=("OP_Prop_",), grow=0.04):
    """cada ILHA SOLTA (componente conexa) das malhas OP_Prop_* tem de tocar outra geometria (cena ou outra ilha):
    a ilha e inflada 'grow' e testada (BVH) contra todo o resto; ilha sem contato = FLUTUANDO"""
    allv, allf, owner = [], [], []
    islands = []
    for o in bpy.data.objects:
        if o.type != "MESH" or o.name.startswith(("COL_", "PREVIEW_", "SCALE_", "CAM_")) or o.hide_render:
            continue
        if o.users_collection and o.users_collection[0].name in ("00_REFERENCE", "_SCALE_REFERENCE"):
            continue
        mw = o.matrix_world
        bm = bmesh.new()
        bm.from_mesh(o.data)
        bm.verts.ensure_lookup_table()
        base = len(allv)
        allv += [mw @ v.co for v in bm.verts]
        mine = o.name.startswith(prefixes)
        comp = [-1] * len(bm.verts)
        if mine:
            cid = 0
            for v in bm.verts:
                if comp[v.index] >= 0:
                    continue
                stack = [v]
                comp[v.index] = cid
                while stack:
                    a = stack.pop()
                    for e in a.link_edges:
                        b = e.other_vert(a)
                        if comp[b.index] < 0:
                            comp[b.index] = cid
                            stack.append(b)
                cid += 1
        for f in bm.faces:
            allf.append([base + v.index for v in f.verts])
            owner.append((o.name, comp[f.verts[0].index]) if mine else (o.name, -1))
        if mine:
            groups = {}
            for f in bm.faces:
                groups.setdefault(comp[f.verts[0].index], []).append([base + v.index for v in f.verts])
            for cid, fs in groups.items():
                islands.append((o.name, cid, fs))
        bm.free()
    big = BVHTree.FromPolygons(allv, allf)
    floating = []
    for name, cid, fs in islands:
        idx = sorted({i for f in fs for i in f})
        pts = [allv[i] for i in idx]
        c = sum(pts, Vector()) / len(pts)
        ext = max((p - c).length for p in pts) or 1.0
        k = 1.0 + grow / ext
        loc = {i: j for j, i in enumerate(idx)}
        vs = [c + (p - c) * k for p in pts]
        t = BVHTree.FromPolygons(vs, [[loc[i] for i in f] for f in fs])
        ok = any(owner[j] != (name, cid) for _, j in t.overlap(big))
        if not ok:
            floating.append((name, cid, tuple(round(v, 1) for v in c), round(ext, 2)))
    print("AUDIT ilhas soltas %s: %d, flutuando: %d" % (",".join(prefixes), len(islands), len(floating)))
    for f in floating[:60]:
        print("AUDIT FLUTUANDO", f)
    return floating


if __name__ == "__main__":
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    if "audit" in argv:
        pre = tuple(a for a in argv if a.startswith("OP_")) or ("OP_Prop_",)
        audit(pre)
