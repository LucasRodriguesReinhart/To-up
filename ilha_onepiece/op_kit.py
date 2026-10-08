# op_kit.py - KIT ARQUITETONICO da Ilha 5 (ONE PIECE / WANO), onda M2. Capital de Wano DIURNA: reboco claro entre
# pilares e vigas de madeira escura, telha azul-escura em canais com BEIRAL GROSSO (testeira dupla), cantos bem
# levantados, telhados ESCALONADOS (hisashi entre pisos, saia mokoshi, chidori-hafu na agua, karahafu sobre a entrada),
# varanda com guarda-corpo vermelho de laca e remates dourados SELETIVOS, comercio cenografico (frente de loja com
# balcao e mercadoria, noren indigo, chochin vermelho). Nao e a vila Taisho da Ilha 4: o metodo (pecas com encaixe,
# papel recuado, juntas, z-fight >= 0,12) vem do ds_kit (so leitura); a linguagem e Wano.
# Escopo: PLANO_OP secoes 8 e 14 (M2) + PROMPT_USUARIO secoes 10, 15, 16 e 17. So geometria VISUAL (a colisao andavel
# e do op_col; ha house_cols() para o corpo das casas). Nao e modulo de zona: o build_op nao o chama; o trecho
# (op_m2_trecho / op_m2_praca) e depois o op_capital (M4) importam e chamam as funcoes abaixo.
#
# ============================================================ CONVENCOES
#   F       fm_parts.Frame(ox, oy, oz, ang) - referencial LOCAL da peca. Casas e pecas soltas: origem no CENTRO DA
#           PLANTA, NO CHAO (z=0 = piso da rua), +y = FRENTE (rua), +x ao longo da frente, z para cima.
#           Faces de parede (Ff): origem no meio da fachada, z=0 no topo do soco (= piso), y=0 na FACE EXTERNA DOS
#           PILARES, +y para fora. As listas de vaos sao lidas da ESQUERDA para a DIREITA de quem olha de fora.
#   mb      fm_lib.MB do chamador: o kit desenha DENTRO do MB que voce passar. Junte varias casas no MESMO MB (1
#           MeshPart por material no export): o orcamento da capital e ~3,5 MeshParts por casa.
#   Escala: avatar 5. Porta 5,6 x 8,4; degrau <= 0,8; guarda-corpo 3,6-4; terreo 10,5 (topo da viga de beiral).
#   Z-fight: nenhuma face visivel coplanar com outra de material diferente a menos de 0,12; papel/luz >= 0,15 atras
#   da grade; pisos sobre pisos >= 0,3 ou so um deles (o piso do trecho e o UNICO tampo onde ele existe).
#   Materiais: so OPMATS do op_lib (nenhum material novo). Luz quente SO dentro de armacao (Window_OP_Warm no papel
#   recuado, Glass_OP_Lantern so na faixa do meio das lanternas). Vermelho (Wood_OP_Lacquer) so em varanda/guarda/
#   portao; dourado (Metal_OP_Gold) so em remates (giboshi, disco da onigawara do edificio-marco, ponteira).
#   Variacao: _h01 = crc32 + finalizador murmur3 (fmix32) - chaves vizinhas nao saem correlacionadas.
#
# ============================================================ API
# EDIFICIO INTEIRO (familias: "loja" fachada comercial | "casa" residencia | "esquina" edificio de esquina)
#   house(mb, F, spec, light_name=None, energy=70.0) -> info
#       spec = dict (ver DEFAULTS) ou um PRESETS[...] (copie e ajuste: dict(PRESETS["C1"], W=18.0)). Chaves:
#       W (frente) D (fundo) plinth=("soco"|"ishigaki"|"none", altura) plaster (terreo) plaster_up (pisos de cima)
#       floors = [dict(h, front, back, left, right, setback=(frente, fundos, lados), pent=True|False,
#                      skirt=True|False, balcony=None|dict(depth, faces="F"|"FR"...))]    (1o = terreo)
#       roof = dict(kind="irimoya"|"kirizuma"|"yosemune", ridge="x"|"y", pitch, over, gable, g_over, lift, tv,
#                   steep, gable_style="timber"|"board", chidori=None|dict(x, w, rise), gold=False)
#       roof_m (Roof_OP_Blue/Green/Red), kara=None|dict(x, w, depth, z) (karahafu na frente do terreo),
#       chochin=[(x, z), ...] (lanternas de parede na frente do terreo), lit, noren, lod (0 heroi / 1 fundo),
#       back_lod (fundos simplificados), side_lod (laterais sem rodape/kumiko, soco em laje; padrao 1 - use 0 na
#       esquina, que tem frente nas 2 ruas), seed.
#       info = dict(floor_z, top_z, ridge_z, eave_z, glow=[pontos mundo], doors=[(centro, yaw)], light_at, front_y)
#   house_cols(area, F, spec)            colisao simplificada (soco + corpo) via col_box (area = "OP_CapHouse"+nome)
#   pavilion(mb, F, W, D, h=8.0, kind="irimoya", red=True, roof_m=RB, open_side="F")   pavilhao aberto (familia)
#   PRESETS: C1 loja 2 pisos com varanda vermelha + chidori | C2 loja de empena para a rua (tsumairi) | C5 loja de
#            2 pisos com mushiko-mado e hisashi | C6 casa de cha larga com karahafu | ESQ esquina de 3 pisos
#            escalonada (saias + varanda + onigawara dourada) | CASA residencia | (pavilhao: pavilion())
# VAOS (front/back/left/right): string ou dict {"t": tipo, "w": largura, "lit": bool, "hood": bool, "noren": ...}
#   "plain" tabuas + reboco | "plaster" so reboco | "koshi" janela de trelica | "shoji" janela alta (capelo opcional)
#   | "lattice" trelica de rua | "mushiko" janela de barras de reboco (piso de cima) | "round" janela redonda
#   (maru-mado) | "door" porta de correr | "open_door" vao livre | "shop" frente de loja (balcao + mercadoria +
#   noren) | "open" vao aberto
# PECAS-BASE
#   foundation(mb, F, W, D, h, style, lod)      soco de cantaria / ishigaki com junta rebaixada
#   facade(mb, Ff, L, h, bays, ...)             fachada: soleira, viga de beiral que passa do canto, verga, pilares
#   wall_panel / panel(...)                      REBOCO ENTRE PILARES (recuado 0,22 da face dos pilares)
#   window(mb, Ff, s, z, w, h, kind, lit, hood) janela RECUADA com moldura, peitoril, painel de papel 0,24 atras
#   door(mb, Ff, s, w, h, kind, lit, noren)     porta (caixilho, soleira, folhas de correr recuadas) / vao com noren
#   shop_front(mb, Ff, a, b, zn, ...)           frente de loja cenografica com profundidade (balcao, prateleira)
#   roof_hip(mb, F, W, D, h, kind, ...)         irimoya / yosemune com beiral grosso, sori, espigoes, cumeeira
#   roof_gable(mb, F, W, D, h, ...)             kirizuma (empena com tabeira, gegyo, tercas)
#   roof_pent(mb, Ff, L, depth, z_top, ...)     hisashi (agua unica na parede, consolos)
#   roof_skirt(mb, F, W, D, depth, z_top, ...)  saia mokoshi em volta de um piso recuado (4 aguas com espigoes)
#   roof_kara(mb, Ff, L, depth, z_top, ...)     karahafu (capelo de beiral ondulado) sobre a entrada
#   chidori(mb, Fr, S, tv, x, w, yd, rise)      empena triangular sobre a agua (chamado pelo roof_hip)
#   ridge(...) / onigawara(...)                 cumeeira com fiadas de noshi + telha-ponteira (disco dourado opc.)
#   red_rail(mb, F, pts, h, base)               GUARDA-CORPO VERMELHO (pilaretes de laca com giboshi dourado)
#   balcony(mb, Ff, x0, x1, depth, z)           varanda em consolos com piso de tabuas e guarda-corpo vermelho
#   stair_stone(mb, F, w, n, rise, tread, ...)  escada de pedra em blocos (juntas desencontradas, focinho chanfrado,
#                                               espelho escuro recuado, banzos em 2 fiadas, z_off = piso do trecho,
#                                               newels = pilaretes de arranque/chegada, newel_lamp = andon no arranque)
#   slab_poly(mb, poly, z0, z1, c, m)           laje com chanfro no topo (JUNTA REBAIXADA entre lajes vizinhas)
#   pave(mb, region, x0, x1, y0, y1, rows, m, z_top, ...)   lajes em fiadas (running bond) recortadas no poligono
#   parapet(mb, F, L, h=2.4)                    mureta baixa de cantaria com capa de lajes e pilaretes
#   retaining_wall(mb, F, L, h, batter)        ARRIMO de pedra aparelhada (fiadas variadas, juntas rebaixadas, capa)
#   LANTERNAS (luz so dentro da armacao; light_name cria POINT NightOnly - use prefixo L_OPProp_ / L_OPCap_Win_):
#   chochin(mb, F, c, r, hgt, body)             lanterna de pano (8 lados, aros, tampas, faixa do meio acesa)
#   lantern_post(mb, F, h, light_name)          poste de rua de Wano: pedra, poste, travessa com 2 chochin
#   lantern_box_post(mb, F, h, light_name)      poste com andon de armacao (kumiko 2 x 3, papel recuado)
#   lantern_wall(mb, F, light_name)             chochin no braco de ferro (F na face da parede)
#   toro(mb, F, s, light_name)                  lanterna de pedra (pedestal, camara, chapeu, joia)
#   banner(mb, F, h, cloth, crest)              ESTANDARTE (nobori) com suporte real: base de pedra, colar,
#                                               mastro, braco de cima, aneis, peso de baixo, brasao recortado
#   jar / crate / barrel / bolts                mercadoria (boca, borda, aros, tampa) para bancas e lojas
#   bench(mb, F, x, y, L, ...)                  banco de tabuas com pes e travessas
# ESTUDIO (folhas de close-up; fora do jogo):
#   blender -b --factory-startup --python op_kit.py -- <pasta_saida> [peca ...]    (previa + roblox, 960 x 540)
import math, os, sys, zlib
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import op_lib as DL
import bpy, bmesh
from mathutils import Vector
from op_lib import MB, Frame, light, col_box, fm_lib

# ------------------------------------------------------------------ materiais (OPMATS) e constantes
WD, WM = "Wood_OP_Dark", "Wood_OP_Mid"
LAC, GOLD, IRON = "Wood_OP_Lacquer", "Metal_OP_Gold", "Metal_OP_Iron"
PL, PLW, PLS = "Plaster_OP", "Plaster_OP_Warm", "Plaster_OP_Shop"
RB, RG, RRED, RR = "Roof_OP_Blue", "Roof_OP_Green", "Roof_OP_Red", "Roof_OP_Ridge"
ST, STD, STP, STZ, STI = "Stone_OP", "Stone_OP_Dark", "Stone_OP_Path", "Stone_OP_Plaza", "Stone_OP_Inlay"
LIT, LGLOW = "Window_OP_Warm", "Glass_OP_Lantern"
INDIGO, CRED, CWHITE = "Cloth_OP_Indigo", "Cloth_OP_Red", "Cloth_OP_White"
WARM = (1.0, 0.64, 0.36)
B = 0.08            # chanfro unico das pecas estruturais
CP, IP = 1.0, 0.8   # pilar de canto / intermediario (secao)
KH = 2.4            # topo do rodape de tabuas (koshi-ita)
SILL = 0.9          # topo da soleira = piso interno
DOOR_W, DOOR_H = 5.6, 8.4


# ------------------------------------------------------------------ sorteio e geometria basica
def _h01(*a):
    """sorteio deterministico 0..1: crc32 da chave + finalizador murmur3 (fmix32) - sem correlacao entre vizinhas"""
    k = "|".join("%.2f" % v if isinstance(v, float) else str(v) for v in a)
    h = zlib.crc32(k.encode("utf-8")) & 0xffffffff
    h ^= h >> 16
    h = (h * 0x85ebca6b) & 0xffffffff
    h ^= h >> 13
    h = (h * 0xc2b2ae35) & 0xffffffff
    h ^= h >> 16
    return h / 4294967296.0


def sub(F, x=0.0, y=0.0, z=0.0, ang=0.0):
    p = F.p(x, y, z)
    return Frame(p.x, p.y, p.z, F.a + ang)


def bx(mb, F, x, y, z, sx, sy, sz, m, bev=0.0, rx=0.0, ry=0.0, rz=0.0):
    if sx <= 1e-3 or sy <= 1e-3 or sz <= 1e-3:
        return
    mb.box((sx, sy, sz), F.p(x, y, z), F.r(rx, ry, rz), m, bev)


def bb(mb, F, x0, x1, y0, y1, z0, z1, m, bev=0.0):
    x0, x1 = min(x0, x1), max(x0, x1)
    y0, y1 = min(y0, y1), max(y0, y1)
    z0, z1 = min(z0, z1), max(z0, z1)
    bx(mb, F, (x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2, x1 - x0, y1 - y0, z1 - z0, m, bev)


def loft(mb, F, rings, m, closed=True, caps=(True, True)):
    """aneis de pontos LOCAIS (mesma contagem) ligados em sequencia; tampas no primeiro e no ultimo"""
    bm = mb.bm
    V = [[bm.verts.new(F.p(*p)) for p in r] for r in rings]
    k = len(V[0])
    fs = []
    seg = k if closed else k - 1
    for a, b in zip(V, V[1:]):
        for j in range(seg):
            j2 = (j + 1) % k
            try:
                fs.append(bm.faces.new((a[j], a[j2], b[j2], b[j])))
            except ValueError:
                pass
    if closed and k >= 3:
        for vs, on in ((list(reversed(V[0])), caps[0]), (V[-1], caps[1])):
            if on:
                try:
                    fs.append(bm.faces.new(vs))
                except ValueError:
                    pass
    if fs:
        bmesh.ops.recalc_face_normals(bm, faces=fs)
    return mb._post([v for r in V for v in r], m, None, 0, 1)


def ext(mb, F, poly, axis, a0, a1, m):
    """prisma: poligono 2D no plano perpendicular a 'axis', extrudado de a0 a a1 ('x': (y,z); 'y': (x,z); 'z': (x,y))"""
    if axis == "x":
        R = lambda a: [(a, u, v) for u, v in poly]
    elif axis == "y":
        R = lambda a: [(u, a, v) for u, v in poly]
    else:
        R = lambda a: [(u, v, a) for u, v in poly]
    return loft(mb, F, [R(a0), R(a1)], m)


def lathe(mb, F, c, prof, n, m, rot=0.0, caps=(True, True)):
    """solido de revolucao (n lados) em volta do eixo vertical por c; prof = [(raio, z relativo)] de baixo para cima"""
    rings = []
    for r, h in prof:
        r = max(r, 0.01)
        rings.append([(c[0] + r * math.cos(rot + 2 * math.pi * j / n), c[1] + r * math.sin(rot + 2 * math.pi * j / n),
                       c[2] + h) for j in range(n)])
    return loft(mb, F, rings, m, caps=caps)


def lathe_y(mb, F, c, prof, n, m, rot=0.0, caps=(True, True)):
    """solido de revolucao em volta do eixo Y local (disco/aro de parede); prof = [(raio, y relativo)]"""
    rings = []
    for r, yy in prof:
        rings.append([(c[0] + r * math.cos(rot + 2 * math.pi * j / n), c[1] + yy,
                       c[2] + r * math.sin(rot + 2 * math.pi * j / n)) for j in range(n)])
    return loft(mb, F, rings, m, caps=caps)


def strip(mb, F, pts, side, w0, w1, h0, h1, m):
    """faixa de secao retangular ao longo de pts (locais): largura w0..w1 no vetor HORIZONTAL side, altura h0..h1 em z"""
    sx, sy = side[0], side[1]
    rings = []
    for x, y, z in pts:
        rings.append([(x + sx * w0, y + sy * w0, z + h0), (x + sx * w1, y + sy * w1, z + h0),
                      (x + sx * w1, y + sy * w1, z + h1), (x + sx * w0, y + sy * w0, z + h1)])
    return loft(mb, F, rings, m)


def sweep(mb, F, pts, prof, m):
    P = [F.p(*p) for p in pts]
    Q = [P[0]]
    for p in P[1:]:
        if (p - Q[-1]).length > 0.04:
            Q.append(p)
    if len(Q) >= 2:
        mb.sweep(Q, prof, m)


def beam(mb, F, a, b, w, h=None, m=WD, bev=0.0):
    mb.beam(F.p(*a), F.p(*b), w, h or w, m, bev)


def even(a, b, step):
    """posicoes igualmente espacadas DENTRO de [a, b] (passo <= step)"""
    n = max(1, int(math.ceil((b - a) / step - 1e-6)))
    return [a + (b - a) * (i + 0.5) / n for i in range(n)]


def stone(mb, F, x0, x1, z0, z1, yb, yf0, yf1, c=0.1, m=ST):
    """bloco de pedra com a FACE em y (yf0 em z0 .. yf1 em z1: talude) e chanfro c so na face; fundo em yb"""
    yz = lambda z: yf0 + (yf1 - yf0) * (z - z0) / max(1e-6, z1 - z0)
    r0 = [(x0, yb, z0), (x1, yb, z0), (x1, yb, z1), (x0, yb, z1)]
    r1 = [(x0, yz(z0) - c, z0), (x1, yz(z0) - c, z0), (x1, yz(z1) - c, z1), (x0, yz(z1) - c, z1)]
    r2 = [(x0 + c, yz(z0 + c), z0 + c), (x1 - c, yz(z0 + c), z0 + c), (x1 - c, yz(z1 - c), z1 - c),
          (x0 + c, yz(z1 - c), z1 - c)]
    loft(mb, F, [r0, r1, r2], m)


def rock_base(mb, F, x, y, z, r=0.8, hgt=0.45, m=ST):
    """pedra-base (soseki): oitavado levemente irregular, enterrado 0,15"""
    k = (1.0, 0.96, 1.03, 0.95, 1.0, 0.94, 1.02, 0.97)
    rot = (x * 0.37 + y * 0.21) % 0.8
    poly = [(x + r * k[i] * math.cos(rot + i * math.pi / 4), y + r * k[i] * math.sin(rot + i * math.pi / 4))
            for i in range(8)]
    ext(mb, F, poly, "z", z - 0.15, z + hgt, m)


def panel(mb, F, x0, x1, z0, z1, y0, y1, holes, m):
    """placa (x0..x1, z0..z1, espessura y0..y1) menos vaos retangulares [(a, b, za, zb)] - colunas pelas bordas"""
    hs = [(max(a, x0), min(b, x1), max(za, z0), min(zb, z1)) for a, b, za, zb in holes
          if b > x0 + 1e-3 and a < x1 - 1e-3 and zb > z0 + 1e-3 and za < z1 - 1e-3]
    xs = sorted(set([x0, x1] + [v for a, b, _, _ in hs for v in (a, b)]))
    for a, b in zip(xs, xs[1:]):
        if b - a < 1e-3:
            continue
        mid = (a + b) / 2
        cut = sorted((za, zb) for ha, hb, za, zb in hs if ha < mid < hb)
        zz = z0
        for za, zb in cut:
            if za > zz + 1e-3:
                bb(mb, F, a, b, y0, y1, zz, za, m)
            zz = max(zz, zb)
        if z1 > zz + 1e-3:
            bb(mb, F, a, b, y0, y1, zz, z1, m)


# ------------------------------------------------------------------ TELHADO: superficie com espessura e caimento
class Slope:
    """superficie do telhado z(x, y) no referencial do telhado (origem no centro da planta). Planos longos (frente/
    fundos): d = Yw - |y|; planos de topo: d = Xw - |x|. Acima da parede o caimento e p; no beiral (d < 0) cai p2 < p
    (beiral que chuta). lift levanta SO os cantos do beiral (sori): lift * (|x|/Xe)^3 * (|y|/Ye)^3."""

    def __init__(self, Xw, Yw, zw, p, p2, Xe, Ye, lift, pu=None, db=1e9):
        self.Xw, self.Yw, self.zw, self.p, self.p2, self.Xe, self.Ye, self.lift = Xw, Yw, zw, p, p2, Xe, Ye, lift
        self.pu, self.db = (pu or p), db

    def _z(self, d, x, y):
        if d > self.db:
            z = self.zw + self.p * self.db + self.pu * (d - self.db)
        else:
            z = self.zw + (self.p * d if d >= 0 else self.p2 * d)
        if self.lift:
            z += self.lift * min(1.0, abs(x) / self.Xe) ** 3 * min(1.0, abs(y) / self.Ye) ** 3
        return z

    def zy(self, x, y):
        return self._z(self.Yw - abs(y), x, y)

    def zx(self, x, y):
        return self._z(self.Xw - abs(x), x, y)


def sheet(mb, F, q, zf, tv, nu, tks, m=RB, m_bot=WD):
    """placa de telhado com espessura tv: quadrilatero de planta q = [beiral0, beiral1, topo1, topo0], malha nu x
    len(tks) seguindo zf(x, y). Topo e bordas em telha, face de baixo em madeira (forro do beiral)"""
    e0, e1, t1, t0 = q
    lerp = lambda a, b, t: (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
    G = []
    for t in tks:
        a, b = lerp(e0, t0, t), lerp(e1, t1, t)
        G.append([(lerp(a, b, i / nu)[0], lerp(a, b, i / nu)[1], zf(*lerp(a, b, i / nu))) for i in range(nu + 1)])
    bm = mb.bm
    T = [[bm.verts.new(F.p(*p)) for p in r] for r in G]
    Bt = [[bm.verts.new(F.p(p[0], p[1], p[2] - tv)) for p in r] for r in G]
    fs, fb = [], []

    def nf(vs, lst):
        try:
            lst.append(bm.faces.new(vs))
        except ValueError:
            pass
    nt = len(tks)
    for j in range(nt - 1):
        for i in range(nu):
            nf((T[j][i], T[j][i + 1], T[j + 1][i + 1], T[j + 1][i]), fs)
            nf((Bt[j][i], Bt[j + 1][i], Bt[j + 1][i + 1], Bt[j][i + 1]), fb)
    for i in range(nu):
        nf((T[0][i + 1], T[0][i], Bt[0][i], Bt[0][i + 1]), fs)
        nf((T[-1][i], T[-1][i + 1], Bt[-1][i + 1], Bt[-1][i]), fs)
    for j in range(nt - 1):
        nf((T[j + 1][0], T[j][0], Bt[j][0], Bt[j + 1][0]), fs)
        nf((T[j][nu], T[j + 1][nu], Bt[j + 1][nu], Bt[j][nu]), fs)
    bmesh.ops.recalc_face_normals(bm, faces=fs + fb)
    mb._post([v for r in T + Bt for v in r], m, None, 0, 1)
    mi = mb._mi_for(m_bot)
    for f in fb:
        if f.is_valid:
            f.material_index = mi


RIB = [(-0.34, -0.12), (-0.24, 0.17), (0.0, 0.29), (0.24, 0.17), (0.34, -0.12)]       # canal de telha (maru)
RIB_LO = [(-0.32, -0.12), (-0.2, 0.22), (0.2, 0.22), (0.32, -0.12)]
HIPP = [(-0.6, -0.2), (-0.5, 0.26), (-0.24, 0.52), (0.24, 0.52), (0.5, 0.26), (0.6, -0.2)]   # capa do espigao


def ribs(mb, F, lines, zf, lod=0, m=RB, prof=None):
    prof = prof or RIB_LO          # (M2) trapezio em todo lod: -20% de tris, mesma leitura de canal
    for line in lines:
        sweep(mb, F, [(x, y, zf(x, y)) for x, y in line], prof, m)


def onigawara(mb, F, x, zr, sx, s=1.0, horns=True, gold=False):
    """telha-ponteira da cumeeira: escudo alto com chifres (tsuno) e disco frontal (dourado no edificio-marco)"""
    poly = [(-1.3, -0.8), (1.3, -0.8), (1.38, 0.5), (1.1, 1.42), (0.66, 2.02), (0.0, 2.3), (-0.66, 2.02),
            (-1.1, 1.42), (-1.38, 0.5)]
    ext(mb, F, [(u * s, zr + v * s) for u, v in poly], "x", x - 0.12 * sx, x + 0.44 * sx * s, RR)
    # disco: atravessa o escudo e sai 0,16 a frente dele (nada coplanar)
    mb.rod(F.p(x + 0.3 * sx * s, 0, zr + 0.78 * s), F.p(x + 0.6 * sx * s, 0, zr + 0.78 * s), 0.52 * s,
           GOLD if gold else RR, 10)
    for k in ((-1, 1) if horns else ()):
        bx(mb, F, x + 0.1 * sx * s, k * 1.1 * s, zr + 2.12 * s, 0.42 * s, 0.34 * s, 1.0 * s, RR, 0.0, rx=-k * 0.5)


def ridge(mb, F, x0, x1, zr, pitch, w=2.2, oni=True, s=1.0, gold=False, courses=3, oni_ends=(True, True)):
    """cumeeira (o-mune) ao longo de x: base em tenda casada nos dois caimentos + fiadas de noshi escalonadas + capa
    redonda (kanmuri) + onigawara nas pontas. Wano: cumeeira ALTA (3 fiadas)."""
    hw = w / 2
    poly = [(-hw, zr - pitch * hw - 0.05), (0.0, zr - 0.05), (hw, zr - pitch * hw - 0.05), (hw, zr + 0.32 * s),
            (-hw, zr + 0.32 * s)]
    ext(mb, F, poly, "x", x0, x1, RR)
    z = zr + 0.28 * s
    for k in range(courses):
        f = 0.84 - 0.14 * k
        bb(mb, F, x0 + 0.12 + 0.1 * k, x1 - 0.12 - 0.1 * k, -f * hw, f * hw, z, z + 0.36 * s, RR)
        z += 0.32 * s
    mb.rod(F.p(x0 + 0.3, 0, z + 0.14 * s), F.p(x1 - 0.3, 0, z + 0.14 * s), 0.36 * hw, RR, 8)
    if oni:
        so = s * 0.74
        if oni_ends[0]:
            onigawara(mb, F, x0, zr, -1, so, True, gold)
        if oni_ends[1]:
            onigawara(mb, F, x1, zr, 1, so, True, gold)
    return z + 0.5 * s


def _hafu(mb, F, xh, ys, zf, tv, depth=0.9, m=WD, half=0.18):
    """tabeira de empena (hafu) sob a borda do telhado, em x = xh, ao longo de ys"""
    strip(mb, F, [(xh, y, zf(xh, y) - tv) for y in ys], (1, 0, 0), -half, half, -depth, 0.1, m)


def _gegyo(mb, F, xh, za, sx, m=WD, s=1.0, gold=False):
    """pendente do encontro das tabeiras (gegyo), 0,15 a frente da aba; remate dourado opcional"""
    poly = [(-1.0 * s, za + 0.5 * s), (1.0 * s, za + 0.5 * s), (0.62 * s, za - 0.48 * s), (0.0, za - 1.0 * s),
            (-0.62 * s, za - 0.48 * s)]
    ext(mb, F, poly, "x", xh - 0.12 * sx, xh + 0.45 * sx, m)
    if gold:
        mb.rod(F.p(xh + 0.3 * sx, 0, za - 0.1 * s), F.p(xh + 0.62 * sx, 0, za - 0.1 * s), 0.34 * s, GOLD, 8)


def _gable_timber(mb, F, x_in, x_out, zb, top, ymax, style="timber"):
    """madeiramento aparente da empena: 'timber' = frechal + 2 montantes + ventilacao de trelica; 'board' = tabuas
    verticais com mata-juntas (kitsure). Pecas 0,16 a frente do reboco da empena."""
    zt0 = zb + 0.25
    if style == "board":
        for y in even(-ymax + 0.2, ymax - 0.2, 0.8):
            t = top(y) - 0.04
            if t > zt0 + 0.4:
                bb(mb, F, x_in, x_out, y - 0.09, y + 0.09, zt0, t, WD)
        return
    zt1 = zt0 + 0.6
    yt = ymax
    while yt > 0.5 and top(yt) < zt1 + 0.3:
        yt -= 0.1
    if yt <= 0.6:
        return
    bb(mb, F, x_in, x_out, -yt, yt, zt0, zt1, WD)
    yp = yt * 0.55
    for k in (-1, 1):
        if top(k * yp) > zt1 + 0.6:
            bb(mb, F, x_in, x_out, k * yp - 0.24, k * yp + 0.24, zt1, top(k * yp) - 0.03, WD)
    za, zc = zt1 + 0.35, top(0.0) - 0.45
    hw = yp - 0.5
    if zc - za > 0.9 and hw > 0.6:
        zc = min(zc, za + 2.4)
        hw = min(hw, (zc - za) * 0.9)
        xm = x_in + 0.16
        bb(mb, F, x_in, xm, -hw, hw, za, zc, RR)
        for a, b, c_, e in ((-hw - 0.22, -hw, za - 0.22, zc + 0.22), (hw, hw + 0.22, za - 0.22, zc + 0.22),
                            (-hw, hw, za - 0.22, za), (-hw, hw, zc, zc + 0.22)):
            bb(mb, F, x_in, x_out, a, b, c_, e, WD)
        n = max(2, int(round(2 * hw / 0.5)))
        for i in range(1, n):
            y = -hw + 2 * hw * i / n
            bb(mb, F, xm - 0.02, xm + 0.14, y - 0.07, y + 0.07, za, zc, WD)


def _rafter(mb, F, pts, zf, tv, w=0.3, h=0.36):
    """caibro (taruki) sob o beiral, com a quebra na linha da parede"""
    for a, b in zip(pts, pts[1:]):
        beam(mb, F, (a[0], a[1], zf(*a) - tv - h / 2 + 0.02), (b[0], b[1], zf(*b) - tv - h / 2 + 0.02), w, h, WD)


def _fascia(mb, Fk, pts_fn, n, side, zf, tv, depth=0.6, d2=0.42, lod=0):
    """BEIRAL GROSSO de Wano: testeira (kayaoi) + 2a tabua mais baixa e recuada (hirokomai). pts_fn(t) -> (x, y).
    lod 1 (fundo): so a testeira, com menos pontos"""
    ts = (0.0, 0.06, 0.18, 0.35, 0.5, 0.65, 0.82, 0.94, 1.0) if lod == 0 else (0.0, 0.1, 0.5, 0.9, 1.0)
    P = [pts_fn(t) for t in ts]                           # n ignorado: mais pontos nas pontas (sori)
    # M6c: topo da testeira RENTE ao forro (era +0,06: a faixa de 0,06 da testeira ficava 0,12 atras da borda da
    # placa de telha = par telha x madeira a 0,12 em todo beiral do kit)
    strip(mb, Fk, [(x, y, zf(x, y) - tv) for x, y in P], side, -0.18, 0.18, -depth, 0.0, WD)
    if lod:
        return
    sx, sy = side[0], side[1]
    strip(mb, Fk, [(x - sx * 0.3, y - sy * 0.3, zf(x, y) - tv - depth + 0.04) for x, y in P], side, -0.14, 0.14,
          -d2, 0.02, WD)


def roof_hip(mb, F, W, D, h, kind="irimoya", pitch=0.55, over=3.2, gable=0.66, g_over=1.4, lift=1.2, tv=0.55,
             lod=0, gable_m=PL, gable_style="timber", rafters=True, m=RB, steep=1.5, back_lod=None, chidori=None,
             gold=False, courses=3, auto_rot=True):
    """telhado IRIMOYA (4 aguas + empena em cima, perfil concavo) ou YOSEMUNE (4 aguas). W x D = planta das faces
    externas dos pilares; h = topo da viga de beiral. A cumeeira corre no MAIOR lado (gira sozinho se D > W), a
    nao ser com auto_rot=False numa irimoya (cumeeira curta paralela a rua num lote fundo: hirairi).
    Beiral grosso (testeira dupla), sori forte nos cantos, capas de espigao com ponta levantada, cumeeira alta com
    onigawara, empena com tabeira + gegyo, tercas e caibros sob o beiral. chidori=dict(x, w, rise): empena
    triangular sobre a agua da FRENTE (+y; so quando a cumeeira corre em x)."""
    if W < D - 1e-6 and (auto_rot or kind != "irimoya" or (W - D) / 2 + gable * (D / 2 + 0.15) < 2.0):
        return roof_hip(mb, sub(F, ang=math.pi / 2), D, W, h, kind, pitch, over, gable, g_over, lift, tv, lod,
                        gable_m, gable_style, rafters, m, steep, back_lod, None, gold, courses)
    Xw, Yw = W / 2 + 0.15, D / 2 + 0.15
    Xe, Ye = Xw + over, Yw + over
    zw = h + tv + 0.06
    p, p2 = pitch, pitch * 0.5
    irim = kind == "irimoya"
    yb = gable * Yw if irim else 0.0
    S = Slope(Xw, Yw, zw, p, p2, Xe, Ye, lift, p * steep if irim else p, Yw - yb)
    pu = S.pu
    k = Xw - Yw
    xg = k + yb
    go = g_over if irim else 0.0
    zr = S.zy(0.0, 0.0)
    zb = S.zy(xg, yb)
    Fs = (F, sub(F, ang=math.pi))
    for ik, Fk in enumerate(Fs):
        lk = lod if (ik == 0 or back_lod is None) else max(lod, back_lod)
        sp = 2.1 if lk == 0 else 3.0
        tw = over / (Ye - yb)
        sheet(mb, Fk, [(-Xe, Ye), (Xe, Ye), (xg, yb), (-xg, yb)], S.zy, tv, max(6, int(2 * Xe / 4.2)),
              [0.0, tw * 0.5, tw, tw + (1 - tw) * 0.5, 1.0], m)
        if irim and yb > 0.05:
            sheet(mb, Fk, [(-xg - go, yb), (xg + go, yb), (xg + go, 0.0), (-xg - go, 0.0)], S.zy, tv,
                  max(4, int(2 * (xg + go) / 4.2)), [0.0, 0.5, 1.0], m)
        twe = over / max(0.1, Xe - xg)
        sheet(mb, Fk, [(Xe, -Ye), (Xe, Ye), (xg, yb), (xg, -yb)], S.zx, tv, max(4, int(2 * Ye / 4.2)),
              [0.0, twe * 0.5, min(0.99, twe), min(0.995, twe + (1 - twe) * 0.5), 1.0], m)
        lines = []
        cx_skip = None
        if chidori and ik == 0:
            cx_skip = (chidori.get("x", 0.0), chidori["w"] / 2 + 1.2)
        for x in even(-Xe + 0.35, Xe - 0.35, sp):
            ax = abs(x)
            tip = [(x, Ye + 0.16)]                      # (M2) sem o ponto do beiral: o trecho e reto
            if ax <= xg:
                line = tip + [(x, Yw)] + ([(x, yb)] if yb > 0.5 else [(x, Yw * 0.5)]) + [(x, 0.35)]
                if cx_skip and abs(x - cx_skip[0]) < cx_skip[1]:
                    line = tip + [(x, Yw - 0.2)]         # sob o chidori so o pe do canal (o resto fica coberto)
                lines.append(line)
            else:
                ye = ax - k + 0.5
                if ye < Ye - 0.35:
                    lines.append(tip + ([(x, Yw)] if ye < Yw - 0.2 else []) + [(x, ye)])
                if irim and ax <= xg + go - 0.25:
                    lines.append([(x, yb - 0.02), (x, 0.35)])
        ribs(mb, Fk, lines, S.zy, lk, m)
        lines = []
        for y in even(-Ye + 0.35, Ye - 0.35, sp):
            ay = abs(y)
            xe = (xg + 0.5) if (irim and ay <= yb - 0.6) else (ay + k + 0.5)
            if xe < Xe - 0.35:
                lines.append([(Xe + 0.16, y)] + ([(Xw, y)] if xe < Xw - 0.2 else []) + [(xe, y)])
        ribs(mb, Fk, lines, S.zx, lk, m)
        for sy in (1, -1):                                  # capas dos espigoes (ponta levantada no beiral)
            pts = [(Xe + 0.6, sy * (Ye + 0.6), S.zy(Xe, Ye) + 0.7)]
            for u in (0.0, 0.5, 1.0):
                pts.append((Xe + (Xw - Xe) * u, sy * (Ye + (Yw - Ye) * u), S.zy(Xe + (Xw - Xe) * u, Ye + (Yw - Ye) * u)))
            for u in (0.5, 1.0):
                x_, y_ = Xw + (xg - Xw) * u, Yw + (yb - Yw) * u
                pts.append((x_, sy * y_, S.zy(x_, y_)))
            sweep(mb, Fk, pts, HIPP, RR)
            tx, ty, tz = pts[0]
            if lk == 0:
                onigawara(mb, sub(Fk, tx, ty, 0.0, math.atan2(sy * (Ye - yb), Xe - xg)), -0.1, tz - 0.05, 1, 0.46, False)
        # beiral grosso: testeira dupla na agua longa e na de topo
        _fascia(mb, Fk, lambda t: ((-Xe + 0.42) + (2 * Xe - 0.84) * t, Ye - 0.34), 10, (0, 1, 0), S.zy, tv, lod=lk)
        _fascia(mb, Fk, lambda t: (Xe - 0.34, (-Ye + 0.42) + (2 * Ye - 0.84) * t), 8, (1, 0, 0), S.zx, tv, lod=lk)
        for sy in (1, -1):                                  # rincao (sumigi)
            beam(mb, Fk, (Xw - 0.8, sy * (Yw - 0.8), zw - tv - 0.75),
                 (Xe + 0.22, sy * (Ye + 0.22), S.zy(Xe, Ye) - tv - 0.32), 0.62, 0.66, WD)
        if rafters and lk == 0 and ik == 0:
            for x in even(-Xe + 0.8, Xe - 0.8, 2.3):
                y0 = max(Yw - 0.1, abs(x) - k + 0.3)
                y1 = Ye - 0.6
                if y1 - y0 > 0.5:
                    _rafter(mb, Fk, [(x, y0), (x, y1)], S.zy, tv)
            for y in []:                                   # (M2) caibros so na agua longa da frente
                x0 = max(Xw - 0.1, abs(y) + k + 0.3)
                x1 = Xe - 0.6
                if x1 - x0 > 0.5:
                    _rafter(mb, Fk, [(x0, y), (x1, y)], S.zx, tv)
        if irim and yb > 1.0:                               # empena da irimoya
            yf_ = yb - 0.55
            bb(mb, Fk, xg - 0.62, xg + 0.36, -yf_, yf_, zb - 0.22, zb + 0.22, RR)
            mb.rod(Fk.p(xg - 0.13, -yf_, zb + 0.3), Fk.p(xg - 0.13, yf_, zb + 0.3), 0.24, RR, 8)
            top = lambda y: S.zy(xg, y) - tv - 0.05
            y1 = yb - (tv + 0.12) / pu
            if y1 > 0.4:
                ys = [y1, y1 * 0.5, 0.0, -y1 * 0.5, -y1]
                poly = [(-y1, zb - 0.05), (y1, zb - 0.05)] + [(y, top(y)) for y in ys]
                ext(mb, Fk, poly, "x", xg - 0.45, xg - 0.25, gable_m)
                _gable_timber(mb, Fk, xg - 0.27, xg - 0.09, zb, top, y1, gable_style if lod == 0 else "board")
            xh = xg + go - 0.3
            ye = 0.0
            for i in range(1, 200):
                y = yb * i / 200
                if S.zy(xh, y) - tv - 0.7 < S.zx(xh - 0.2, y) + 0.4:
                    break
                ye = y
            if ye > 0.5:
                for sy in (1, -1):
                    _hafu(mb, Fk, xh, [sy * ye * i / 5 for i in range(6)], S.zy, tv, 0.7)
                _gegyo(mb, Fk, xh, S.zy(xh, 0.0) - tv - 0.7, 1, WD, 1.0, gold)
            for y in (0.0, yb * 0.5, -yb * 0.5):
                zt = S.zy(xg, y) - tv + 0.02
                bb(mb, Fk, xg - 0.62, xh - 0.2, y - 0.3, y + 0.3, zt - 0.7, zt, WD)
    if chidori:
        chidori_gable(mb, F, S, tv, chidori.get("x", 0.0), chidori["w"], Yw - 0.4, chidori.get("rise", None), m,
                      gable_m, gold)
    if irim:
        rtop = ridge(mb, F, -(xg + go + 0.2), xg + go + 0.2, zr, pu, 2.3, True, 1.0, gold, courses if lod == 0 else 1)
    elif xg > 0.4:
        rtop = ridge(mb, F, -(xg + 0.3), xg + 0.3, zr, p, 2.3, True, 1.0, gold, courses)
    else:
        lathe(mb, F, (0, 0, zr - 0.2), [(0.7, 0.0), (0.85, 0.35), (0.5, 0.6), (0.55, 0.9), (0.32, 1.3), (0.05, 1.8)],
              8, GOLD if gold else RR)
        rtop = zr + 1.6
    return dict(zr=zr, zb=zb, zw=zw, eave_z=S.zy(0.0, Ye) - tv - 0.62, Xe=Xe, Ye=Ye, top=rtop + 2.2, xg=xg, yb=yb,
                go=go, S=S)


def chidori_gable(mb, F, S, tv, xc, w, yd, rise=None, m=RB, gable_m=PL, gold=False):
    """CHIDORI-HAFU: empena triangular pousada na agua da frente (+y) do telhado F/S. Duas aguas proprias que morrem
    na agua de baixo (linha de encontro reta: os 2 planos sao planos), tabeiras, gegyo, triangulo de reboco recuado
    0,2 com madeiramento, cumeeira pequena com onigawara na frente."""
    X = w / 2
    ov = 0.9
    pd = 0.62
    ze = S.zy(xc, yd) + 0.35                               # beiral do chidori 0,35 acima da agua de baixo
    zt = ze + pd * (X + ov) if rise is None else ze + rise
    pd = (zt - ze) / (X + ov)
    p = S.p
    yfront = yd + ov

    def yback(dx):                                         # onde o plano do chidori encontra a agua de baixo
        zd = zt - pd * dx
        return S.Yw - (zd - S.zw) / p

    zf = lambda x, y: zt - pd * abs(x - xc)
    for s in (-1, 1):
        q = [(xc + s * (X + ov), yfront), (xc, yfront), (xc, yback(0.0) - 0.2), (xc + s * (X + ov), yback(X + ov) - 0.2)]
        if s > 0:
            q = [q[1], q[0], q[3], q[2]]
        sheet(mb, F, q, zf, tv * 0.8, 3, [0.0, 0.5, 1.0], m)
        lines = []
        for dx in even(0.5, X + ov - 0.3, 1.4):
            x = xc + s * dx
            lines.append([(x, yfront + 0.14), (x, yfront), (x, yback(dx) + 0.2)])
        ribs(mb, F, lines, zf, 1, m)
        # tabeira inclinada ao longo da borda da frente
        strip(mb, F, [(xc + s * (X + ov) * u, yfront - 0.3, zf(xc + s * (X + ov) * u, yfront) - tv * 0.8)
                      for u in (0.0, 0.5, 1.0)], (0, 1, 0), -0.18, 0.18, -0.7, 0.08, WD)
    # triangulo (reboco recuado) + madeiramento
    zbase = S.zy(xc, yd) - 0.15
    top = lambda x: zf(x, yd) - tv * 0.8 - 0.08
    Xi = X - 0.1
    while Xi > 0.5 and top(xc + Xi) < zbase + 0.3:
        Xi -= 0.1
    poly = [(xc - Xi, zbase), (xc + Xi, zbase), (xc + Xi, top(xc + Xi)), (xc, top(xc)), (xc - Xi, top(xc - Xi))]
    ext(mb, F, poly, "y", yd - 0.45, yd - 0.25, gable_m)
    Fg = sub(F, xc, 0.0, 0.0, math.pi / 2)                 # x de Fg = +y do telhado (para fora)
    _gable_timber(mb, Fg, yd - 0.27, yd - 0.09, zbase, lambda u: top(xc - u), Xi, "timber")
    _gegyo(mb, Fg, yfront - 0.3, zt - tv * 0.8 - 0.7, 1, WD, 0.8, gold)
    # cumeeira do chidori (ao longo de y), onigawara so na frente
    Fr = sub(F, xc, 0.0, 0.0, math.pi / 2)
    y0, y1 = yback(0.0) - 0.4, yfront + 0.15
    ridge(mb, Fr, y0, y1, zt, pd, 1.4, True, 0.7, gold, 1, (False, True))


def roof_gable(mb, F, W, D, h, pitch=0.62, over=3.0, g_over=1.8, lift=0.7, tv=0.55, lod=0, gable_m=PL,
               gable_style="timber", rafters=True, m=RB, wall_t=0.8, ridge_w=2.2, oni_s=1.0, back_lod=None,
               gold=False, courses=3):
    """telhado KIRIZUMA (duas aguas), cumeeira ao longo de x. Empenas em x = +-W/2 (no plano da parede de topo),
    aba de empena g_over com tabeira e gegyo, tercas aparentes, beiral grosso nas aguas"""
    Xw, Yw = W / 2, D / 2 + 0.15
    Xe, Ye = Xw + g_over, Yw + over
    zw = h + tv + 0.06
    p, p2 = pitch, pitch * 0.5
    S = Slope(Xw, Yw, zw, p, p2, Xe, Ye, lift)
    zr = S.zy(0.0, 0.0)
    tw = over / Ye
    for ik, Fk in enumerate((F, sub(F, ang=math.pi))):
        lk = lod if (ik == 0 or back_lod is None) else max(lod, back_lod)
        sp = 2.1 if lk == 0 else 3.0
        sheet(mb, Fk, [(-Xe, Ye), (Xe, Ye), (Xe, 0.0), (-Xe, 0.0)], S.zy, tv, max(4, int(2 * Xe / 4.2)),
              [0.0, tw * 0.5, tw, tw + (1 - tw) * 0.5, 1.0], m)
        ribs(mb, Fk, [[(x, Ye + 0.16), (x, Yw), (x, Yw * 0.5), (x, 0.35)]
                      for x in even(-Xe + 0.35, Xe - 0.35, sp)], S.zy, lk, m)
        _fascia(mb, Fk, lambda t: ((-Xe + 0.5) + (2 * Xe - 1.0) * t, Ye - 0.3), 8, (0, 1, 0), S.zy, tv, lod=lk)
        if rafters and lk == 0 and ik == 0:
            for x in even(-Xe + 0.8, Xe - 0.8, 2.3):
                y1 = Ye - 0.55
                _rafter(mb, Fk, [(x, Yw - 0.1), (x, y1)] if abs(x) < Xw - 0.5 else [(x, 0.6), (x, Yw), (x, y1)], S.zy, tv)
        top = lambda y: S.zy(Xw, y) - tv - 0.05
        ymax = D / 2
        ys = [ymax, ymax * 0.5, 0.0, -ymax * 0.5, -ymax]
        poly = [(-ymax, h - 0.1), (ymax, h - 0.1)] + [(y, top(y)) for y in ys]
        if gable_style != "none":
            ext(mb, Fk, poly, "x", Xw - wall_t, Xw - 0.24, gable_m)
            _gable_timber(mb, Fk, Xw - 0.26, Xw - 0.08, h - 0.25, top, ymax, gable_style if lk == 0 else "board")
        xh = Xe - 0.3
        for sy in (1, -1):
            _hafu(mb, Fk, xh, [sy * (Ye - 0.05) * u for u in (0.0, 0.25, Yw / Ye * 0.999, (Yw / Ye + 1) / 2, 1.0)],
                  S.zy, tv, 0.95, WD, 0.2)
        _gegyo(mb, Fk, xh, S.zy(xh, 0.0) - tv - 0.95, 1, WD, 1.0, gold)
        for y in (0.0, Yw * 0.5, -Yw * 0.5):
            zt = S.zy(Xw, y) - tv + 0.02 if y else zr - tv + 0.02
            bb(mb, Fk, Xw - 0.3, xh - 0.25, y - 0.3, y + 0.3, zt - 0.75, zt, WD)
    rtop = ridge(mb, F, -(Xe + 0.17), Xe + 0.17, zr, p, ridge_w, True, oni_s, gold, courses if lod == 0 else 1)
    return dict(zr=zr, zw=zw, eave_z=S.zy(0.0, Ye) - tv - 0.62, Xe=Xe, Ye=Ye, top=rtop + 2.2, S=S)


def roof_pent(mb, Ff, L, depth, z_top, pitch=0.42, tv=0.42, lift=0.45, lod=0, support="brackets", m=RB,
              rafters=True, embed=0.35, ends=True, xs=None):
    """agua unica encostada na parede (hisashi / capelo). Ff na face da parede (y=0, +y fora); z_top = topo da
    telha junto da parede; a placa entra 'embed' na parede. support: 'brackets' | 'braces' | 'none'"""
    X = L / 2
    zf = lambda x, y: z_top - pitch * y + lift * min(1.0, abs(x) / X) ** 3 * min(1.0, max(0.0, y) / depth) ** 3
    sheet(mb, Ff, [(-X, depth), (X, depth), (X, -embed), (-X, -embed)], zf, tv, max(3, int(L / 3.2)), [0.0, 0.5, 1.0], m)
    small = depth < 2.0
    if small:
        ribs(mb, Ff, [[(x, depth + 0.1), (x, depth), (x, 0.15)] for x in even(-X + 0.3, X - 0.3, 1.0)], zf, 1, m,
             [(-0.22, -0.08), (-0.14, 0.15), (0.14, 0.15), (0.22, -0.08)])
    else:
        ribs(mb, Ff, [[(x, depth + 0.15), (x, depth), (x, depth * 0.5), (x, 0.2)]
                      for x in even(-X + 0.35, X - 0.35, 1.5 if lod == 0 else 1.9)], zf, lod, m)
    bb(mb, Ff, -X + 0.2, X - 0.2, -0.12, 0.3 if not small else 0.22, z_top - 0.35, z_top + (0.3 if not small else 0.2),
       WD)
    hb = 0.5 if not small else 0.3
    yf = depth - 0.3
    strip(mb, Ff, [(x, yf, zf(x, yf) - tv) for x in [(-X + 0.4) + (2 * X - 0.8) * i / 6 for i in range(7)]],
          (0, 1, 0), -0.16, 0.16, -hb, 0.06, WD)
    if ends:
        for sx in (-1, 1):
            strip(mb, Ff, [(sx * (X - 0.32), y, zf(sx * (X - 0.32), y) - tv) for y in (0.0, depth * 0.5, depth - 0.05)],
                  (1, 0, 0), -0.13, 0.13, -hb, 0.08, WD)
    xs = xs if xs is not None else ([-X + 0.6, X - 0.6] + ([x for x in even(-X + 0.6, X - 0.6, 4.8)][1:-1] if L > 14 else []))
    if support == "brackets":
        zd = zf(0.0, depth - 0.57) - tv - 0.32
        bb(mb, Ff, -X + 0.25, X - 0.25, depth - 0.85, depth - 0.3, zd - 0.5, zd, WD)
        for x in xs:
            ext(mb, Ff, [(-0.35, zd - 0.5), (depth - 0.2, zd - 0.5), (depth - 0.2, zd - 0.95), (depth * 0.6, zd - 1.05),
                         (depth * 0.25, zd - 1.35), (-0.35, zd - 1.55)], "x", x - 0.22, x + 0.22, WD)
        if rafters and lod == 0:
            for x in even(-X + 0.7, X - 0.7, 1.6):
                beam(mb, Ff, (x, -0.2, zf(x, -0.2) - tv - 0.15), (x, depth - 0.45, zf(x, depth - 0.45) - tv - 0.15),
                     0.26, 0.32, WD)
    elif support == "braces":
        for x in xs:
            zb_ = zf(x, depth * 0.7) - tv
            beam(mb, Ff, (x, -0.1, zb_ - 0.25), (x, depth * 0.75, zb_ - 0.12), 0.22, 0.3, WD)
            beam(mb, Ff, (x, 0.05, zb_ - (1.4 if small else 2.4)), (x, depth * 0.55, zb_ - 0.25), 0.2, 0.22, WD)
    return dict(eave_z=zf(0.0, depth) - tv - hb)


def roof_kara(mb, Ff, L, depth, z_top, pitch=0.3, rise=1.5, tv=0.45, m=RB, gold=False):
    """KARAHAFU: capelo encostado na parede com a borda da frente em onda (sobe no meio, as pontas viram para cima).
    Tabeira curva grossa acompanhando a onda, gegyo no meio, canais, consolos nas pontas. Ff na face da parede."""
    X = L / 2

    def zf(x, y):
        u = min(1.0, abs(x) / X)
        t = max(0.0, y) / depth
        bell = 0.5 * (1.0 + math.cos(math.pi * min(1.0, u / 0.86)))
        flare = max(0.0, (u - 0.8) / 0.2) ** 2
        return z_top - pitch * y + (rise * bell + 0.55 * rise * flare) * t ** 1.4
    sheet(mb, Ff, [(-X, depth), (X, depth), (X, -0.35), (-X, -0.35)], zf, tv, 14, [0.0, 0.35, 0.7, 1.0], m)
    ribs(mb, Ff, [[(x, depth + 0.12), (x, depth), (x, depth * 0.55), (x, 0.2)] for x in even(-X + 0.35, X - 0.35, 1.25)],
         zf, 1, m)
    yf = depth - 0.28
    xs_ = [(-X + 0.25) + (2 * X - 0.5) * i / 16 for i in range(17)]
    strip(mb, Ff, [(x, yf, zf(x, yf) - tv) for x in xs_], (0, 1, 0), -0.2, 0.2, -0.95, 0.08, WD)
    strip(mb, Ff, [(x, yf - 0.32, zf(x, yf) - tv - 0.92) for x in xs_[2:-2]], (0, 1, 0), -0.12, 0.12, -0.36, 0.02, WD)
    zc = zf(0.0, yf) - tv - 0.95
    poly = [(-0.9, zc + 0.4), (0.9, zc + 0.4), (0.55, zc - 0.45), (0.0, zc - 0.9), (-0.55, zc - 0.45)]
    ext(mb, Ff, poly, "y", yf + 0.06, yf + 0.5, WD)
    if gold:
        mb.rod(Ff.p(0.0, yf + 0.36, zc - 0.05), Ff.p(0.0, yf + 0.66, zc - 0.05), 0.3, GOLD, 8)
    bb(mb, Ff, -X + 0.2, X - 0.2, -0.12, 0.3, z_top - 0.35, z_top + 0.3, WD)
    for sx in (-1, 1):
        x = sx * (X - 0.6)
        zd = zf(x, depth * 0.5) - tv - 0.3
        ext(mb, Ff, [(-0.35, zd), (depth - 0.4, zd), (depth - 0.4, zd - 0.5), (depth * 0.55, zd - 0.7),
                     (depth * 0.2, zd - 1.1), (-0.35, zd - 1.3)], "x", x - 0.24, x + 0.24, WD)
    return dict(eave_z=zf(0.0, depth) - tv - 0.95, top=zf(0.0, depth) + 0.3)


def roof_skirt(mb, F, W, D, depth, z_top, pitch=0.45, tv=0.45, lift=0.5, m=RB, lod=0):
    """SAIA (mokoshi) de 4 aguas em volta de um piso recuado: W x D = face do piso de cima (onde a saia encosta),
    mesma profundidade nos 4 lados (os planos se encontram no espigao diagonal), capas de espigao, testeira dupla"""
    Xi, Yi = W / 2, D / 2
    Xe, Ye = Xi + depth, Yi + depth

    def zfy(x, y):
        d = max(0.0, abs(y) - Yi + 0.35)
        return z_top - pitch * (abs(y) - Yi) + lift * (min(1.0, abs(x) / Xe) ** 3) * (min(1.0, d / depth) ** 3)

    def zfx(x, y):
        d = max(0.0, abs(x) - Xi + 0.35)
        return z_top - pitch * (abs(x) - Xi) + lift * (min(1.0, abs(y) / Ye) ** 3) * (min(1.0, d / depth) ** 3)
    for Fk in (F, sub(F, ang=math.pi)):
        sheet(mb, Fk, [(-Xe, Ye), (Xe, Ye), (Xi, Yi - 0.35), (-Xi, Yi - 0.35)], zfy, tv, max(4, int(2 * Xe / 4.2)),
              [0.0, 0.5, 1.0], m)
        sheet(mb, Fk, [(Xe, -Ye), (Xe, Ye), (Xi - 0.35, Yi), (Xi - 0.35, -Yi)], zfx, tv, max(3, int(2 * Ye / 4.2)),
              [0.0, 0.5, 1.0], m)
        sp = 1.5 if lod == 0 else 1.9
        ribs(mb, Fk, [[(x, Ye + 0.14), (x, Ye), (x, Yi + 0.2)] for x in even(-Xi + 0.4, Xi - 0.4, sp)], zfy, 1, m)
        ribs(mb, Fk, [[(Xe + 0.14, y), (Xe, y), (Xi + 0.2, y)] for y in even(-Yi + 0.4, Yi - 0.4, sp)], zfx, 1, m)
        for sy in (1, -1):
            pts = [(Xe + 0.45, sy * (Ye + 0.45), zfy(Xe, Ye) + 0.45)] + \
                  [(Xe + (Xi - Xe) * u, sy * (Ye + (Yi - Ye) * u), zfy(Xe + (Xi - Xe) * u, Ye + (Yi - Ye) * u))
                   for u in (0.0, 0.5, 1.0)]
            sweep(mb, Fk, pts, [(a * 0.75, b * 0.75) for a, b in HIPP], RR)
        _fascia(mb, Fk, lambda t: ((-Xe + 0.4) + (2 * Xe - 0.8) * t, Ye - 0.3), 8, (0, 1, 0), zfy, tv, 0.5, 0.34)
        _fascia(mb, Fk, lambda t: (Xe - 0.3, (-Ye + 0.4) + (2 * Ye - 0.8) * t), 6, (1, 0, 0), zfx, tv, 0.5, 0.34)
    # rufo contra o piso de cima
    for sx in (-1, 1):
        bb(mb, F, -Xi - 0.15, Xi + 0.15, sx * Yi - 0.12, sx * Yi + 0.3, z_top - 0.3, z_top + 0.3, WD)
        bb(mb, F, sx * Xi - 0.12, sx * Xi + 0.3, -Yi - 0.15, Yi + 0.15, z_top - 0.3, z_top + 0.3, WD)
    return dict(eave_z=z_top - pitch * depth - tv - 0.5)


def hip_cap(mb, F, c, hx, hy, z, over, rise, t, m, lift=0.0, nu=2):
    """chapeu de 4 aguas pequeno (lanterna) com espessura t, beiral 'over' e cantos levemente levantados"""
    S = Slope(hx, hy, z + t, rise / max(hx, hy), rise / max(hx, hy) * 0.55, hx + over, hy + over, lift)
    k = hx - hy
    Fc = sub(F, c[0], c[1], 0.0)
    tw = over / (hy + over)
    tks = [0.0, tw, 1.0]
    for Fk in (Fc, sub(Fc, ang=math.pi)):
        sheet(mb, Fk, [(-hx - over, hy + over), (hx + over, hy + over), (k, 0.0), (-k, 0.0)], S.zy, t, nu, tks, m, m)
        sheet(mb, Fk, [(hx + over, -hy - over), (hx + over, hy + over), (k, 0.0), (k, 0.0)], S.zx, t, nu, tks, m, m)
    return S.zy(0.0, 0.0)


# ------------------------------------------------------------------ PAREDES: estrutura + reboco + vaos
def boards(mb, Ff, a, b, z0=0.7, z1=KH):
    """rodape de tabuas (koshi-ita) recuado + mata-juntas (tabua 0,16 atras da mata-junta)"""
    bb(mb, Ff, a, b, -0.72, -0.18, z0, z1, WM)
    n = max(1, int(round((b - a) / 1.0)))
    for i in range(1, n):
        x = a + (b - a) * i / n
        bb(mb, Ff, x - 0.09, x + 0.09, -0.2, -0.02, z0, z1, WD)


def window(mb, Ff, s, z, w, h, kind="koshi", lit=True, hood=False, sill=True, head=0.3, lod=0, pl=PL):
    """janela RECUADA: caixilho (ombreiras, verga, peitoril com pingadeira), painel de papel 0,24 atras da frente do
    kumiko + grade. kind: 'koshi' (trelica baixa) | 'lattice' (trelica de rua) | 'shoji' | 'mushiko' (barras de
    reboco, piso de cima) | 'round' (maru-mado: reboco recortado em circulo, aro de madeira, cruz de kumiko).
    O vao na parede e de quem chama (s-w/2..s+w/2, z..z+h). Devolve o ponto (local Ff) para a luz."""
    x0, x1 = s - w / 2, s + w / 2
    pm = LIT if lit else PL
    if kind == "round":
        r = min(w, h) / 2
        cz = z + h / 2
        n = 16
        # cantos de reboco entre o quadrado do vao e o circulo (mesmo plano do reboco da parede)
        for qx, qz in ((1, 1), (-1, 1), (-1, -1), (1, -1)):
            pts = [(s + qx * r, cz + qz * r)]
            for i in range(5):
                a = (math.pi / 2) * i / 4
                pts.append((s + qx * r * math.cos(a), cz + qz * r * math.sin(a)))
            if qx * qz < 0:
                pts = list(reversed(pts))
            ext(mb, Ff, pts, "y", -0.8, -0.22, pl)
        lathe_y(mb, Ff, (s, 0.0, cz), [(r + 0.34, -0.12), (r + 0.34, 0.12), (r, 0.12), (r, -0.86), (r + 0.34, -0.86),
                                       (r + 0.34, -0.12)], n, WD, math.pi / n, (False, False))   # aro (anel aberto)
        lathe_y(mb, Ff, (s, 0.0, cz), [(r + 0.05, -0.78), (r + 0.05, -0.74)], 16, pm, math.pi / 16)   # papel redondo
        for d in (-r * 0.36, r * 0.36):
            hl = math.sqrt(max(0.0, r * r - d * d))
            bb(mb, Ff, s + d - 0.06, s + d + 0.06, -0.62, -0.48, cz - hl, cz + hl, WD)
            bb(mb, Ff, s - hl, s + hl, -0.62, -0.48, cz + d - 0.06, cz + d + 0.06, WD)
        return (s, 1.6, cz)
    j = 0.3
    zlo = z - (0.3 if sill else 0.0)
    bb(mb, Ff, x0 - j, x0, -0.86, -0.06, zlo, z + h + head, WD)
    bb(mb, Ff, x1, x1 + j, -0.86, -0.06, zlo, z + h + head, WD)
    bb(mb, Ff, x0, x1, -0.86, -0.06, z + h, z + h + head, WD)
    if sill:
        bb(mb, Ff, x0 - j - 0.1, x1 + j + 0.1, -0.86, 0.1, z - 0.3, z, WD)
    if kind == "mushiko":
        # barras de reboco (mushiko) 0,17 a frente da parede, papel/fundo escuro 0,5 atras delas
        # M6c: fundo de 0,20 encostado no tardoz das ombreiras (-0,86); era uma placa de 0,04 solta a -0,94
        bb(mb, Ff, x0 - 0.02, x1 + 0.02, -1.06, -0.86, z, z + h, LIT if lit else WD)
        nb = max(3, int(round(w / 0.62)))
        for i in range(1, nb):
            xx = x0 + w * i / nb
            bb(mb, Ff, xx - 0.17, xx + 0.17, -0.7, -0.05, z, z + h, pl)
        return (s, 1.6, z + h * 0.5)
    bb(mb, Ff, x0 - 0.02, x1 + 0.02, -0.78, -0.74, z, z + h, pm)
    kum = lod == 0 and kind not in ("koshi", "lattice")      # atras da trelica o kumiko nao aparece; lod 1 sem kumiko
    nv = (max(1, int(round(w / 1.0))) - 1) if kum else 0
    nh = (max(1, int(round(h / 1.2))) - 1) if kum else 0
    for i in range(1, nv + 1):
        xx = x0 + w * i / (nv + 1)
        bb(mb, Ff, xx - 0.05, xx + 0.05, -0.64, -0.5, z, z + h, WD)
    for i in range(1, nh + 1):
        zz = z + h * i / (nh + 1)
        bb(mb, Ff, x0, x1, -0.64, -0.5, zz - 0.05, zz + 0.05, WD)
    if kind in ("koshi", "lattice"):
        nb = max(2, int(round(w / (0.44 if kind == "koshi" else 0.52))))
        for i in range(1, nb):
            xx = x0 + w * i / nb
            bb(mb, Ff, xx - 0.08, xx + 0.08, -0.38, -0.16, z, z + h, WD)
        for zz in ((z + h * 0.62,) if kind == "koshi" else (z + h * 0.3, z + h * 0.7)):
            bb(mb, Ff, x0, x1, -0.4, -0.1, zz - 0.07, zz + 0.07, WD)
    if hood:
        roof_pent(mb, sub(Ff, s, 0.0, 0.0), w + 1.6, 1.5, z + h + head + 1.25, 0.5, 0.26, 0.15, 1, "braces",
                  xs=[-(w / 2 + 0.35), w / 2 + 0.35])
    return (s, 1.6, z + h * 0.5)


def _leaf(mb, Ff, xa, xb, ya, yb_, za, zb, lit):
    """folha de porta de correr: quadro, almofada baixa, trelica + papel (atras do quadro), puxador"""
    st = 0.3
    for x in (xa, xb - st):
        bb(mb, Ff, x, x + st, ya, yb_, za, zb, WM)
    zm = za + min(2.6, (zb - za) * 0.33)
    for z0_, z1_ in ((za, za + 0.55), (zm, zm + 0.25), (zb - 0.3, zb)):
        bb(mb, Ff, xa + st, xb - st, ya, yb_, z0_, z1_, WM)
    bb(mb, Ff, xa + st, xb - st, ya + 0.04, yb_ - 0.04, za + 0.55, zm, WD)
    bb(mb, Ff, xa + st, xb - st, ya - 0.04, ya - 0.01, zm + 0.25, zb - 0.3, LIT if lit else PL)
    n = max(2, int(round((xb - xa - 2 * st) / 0.36)))
    for i in range(1, n):
        x = xa + st + (xb - xa - 2 * st) * i / n
        bb(mb, Ff, x - 0.05, x + 0.05, yb_ - 0.06, yb_ - 0.01, zm + 0.25, zb - 0.3, WD)
    zk = (zm + zb) / 2
    bb(mb, Ff, xa + st, xb - st, yb_ - 0.06, yb_ - 0.01, zk - 0.05, zk + 0.05, WD)
    bb(mb, Ff, xb - st + 0.03, xb - st + 0.13, yb_ - 0.02, yb_ + 0.14, za + 3.7, za + 4.2, IRON)


def noren_cloth(mb, Ff, x0, x1, zt, ln, noren=True):
    """noren: 2-3 panos num varao na frente do vao x0..x1 (topo do varao em zt), bainha em volta do varao"""
    nm = noren if isinstance(noren, str) else INDIGO
    w = x1 - x0
    mb.rod(Ff.p(x0 - 0.45, 0.42, zt), Ff.p(x1 + 0.45, 0.42, zt), 0.08, WD, 6)
    n = 3 if w > 4.5 else 2
    g = 0.16
    sw = (w + 0.4 - g * (n - 1)) / n
    for i in range(n):
        xa = x0 - 0.2 + i * (sw + g)
        bb(mb, Ff, xa, xa + sw, 0.3, 0.36, zt - ln, zt - 0.2, nm)
        bb(mb, Ff, xa, xa + sw, 0.22, 0.62, zt - 0.3, zt + 0.12, nm)
        if nm == INDIGO:                          # barra branca na barra do pano (sem letras), 0,12 a frente
            bb(mb, Ff, xa + 0.15, xa + sw - 0.15, 0.36, 0.5, zt - ln + 0.25, zt - ln + 0.55, CWHITE)


def door(mb, Ff, s, w, h, kind="hikido", lit=False, noren=None, z0=SILL):
    """porta: caixilho (ombreiras, verga, soleira com trilhos) + folhas de correr RECUADAS em 2 trilhos ('hikido')
    ou vao livre ('open', com interior de quem chama) + noren opcional"""
    x0, x1 = s - w / 2, s + w / 2
    bb(mb, Ff, x0 - 0.3, x0, -0.9, -0.04, z0 - 0.25, z0 + h + 0.45, WD)
    bb(mb, Ff, x1, x1 + 0.3, -0.9, -0.04, z0 - 0.25, z0 + h + 0.45, WD)
    bb(mb, Ff, x0, x1, -0.9, -0.04, z0 + h, z0 + h + 0.45, WD)
    bb(mb, Ff, x0 - 0.3, x1 + 0.3, -0.95, 0.2, z0 - 0.25, z0, WD)
    if kind != "open":
        for yy in (-0.58, -0.36):
            bb(mb, Ff, x0, x1, yy - 0.03, yy + 0.03, z0, z0 + 0.06, WD)
        lw = w / 2 + 0.12
        _leaf(mb, Ff, x0, x0 + lw, -0.66, -0.5, z0 + 0.04, z0 + h - 0.04, lit)
        _leaf(mb, Ff, x1 - lw, x1, -0.44, -0.28, z0 + 0.04, z0 + h - 0.04, lit)
    else:                                         # vao livre: fundo de entrada (genkan) escuro com papel aceso
        bb(mb, Ff, x0, x1, -3.4, -0.9, z0 - 0.3, z0 - 0.05, WM)
        bb(mb, Ff, x0 - 0.3, x1 + 0.3, -3.7, -3.4, z0 - 0.3, z0 + h + 0.4, WD)
        bb(mb, Ff, s - 1.3, s + 1.3, -3.26, -3.22, z0 + 1.0, z0 + h - 1.2, LIT if lit else PL)     # 0,14 a frente
        for xx in (x0 - 0.15, x1 + 0.15):
            bb(mb, Ff, xx - 0.15, xx + 0.15, -3.4, -0.9, z0 - 0.3, z0 + h + 0.4, WD)
        bb(mb, Ff, x0, x1, -3.4, -0.9, z0 + h + 0.1, z0 + h + 0.4, WD)
    if noren:
        noren_cloth(mb, Ff, x0, x1, z0 + h - 0.12, min(3.4, h * 0.4), noren)
    return dict(center=(s, 0.0, z0), glow=(s, 1.8, z0 + h * 0.62))


# ------------------------------------------------------------------ mercadoria (bancas e lojas)
def jar(mb, F, x, y, z, r=0.55, h=1.3, m=STD, lid=False):
    """jarro de ceramica: pe, bojo, ombro, gargalo, BOCA com borda (lathe 8 lados)"""
    prof = [(r * 0.62, 0.0), (r * 0.95, h * 0.3), (r * 0.86, h * 0.68), (r * 0.46, h * 0.88), (r * 0.58, h * 0.97),
            (r * 0.56, h), (r * 0.38, h * 0.96)]
    lathe(mb, F, (x, y, z), prof, 8, m)
    if lid:
        lathe(mb, F, (x, y, z + h * 0.97), [(r * 0.6, 0.0), (r * 0.6, 0.1), (r * 0.2, 0.22), (r * 0.12, 0.34)], 8, WM)


def pot(mb, F, x, y, z, r=0.3, h=0.7, m=STD):
    """pote de prateleira (6 lados): pe, bojo, ombro e boca com borda - versao leve do jar para fundos de loja"""
    lathe(mb, F, (x, y, z), [(r * 0.65, 0.0), (r, h * 0.42), (r * 0.62, h * 0.84), (r * 0.7, h), (r * 0.45, h * 0.95)], 6, m)


def barrel(mb, F, x, y, z, r=0.75, h=1.6):
    """barril (taru): aduelas abauladas, 2 aros de corda escura, tampo recuado"""
    lathe(mb, F, (x, y, z), [(r * 0.86, 0.0), (r, h * 0.3), (r, h * 0.7), (r * 0.86, h), (r * 0.78, h),
                             (r * 0.78, h - 0.08)], 10, WM)
    for zz in (h * 0.2, h * 0.8):
        lathe(mb, F, (x, y, z + zz), [(r * 0.96 + 0.13, -0.1), (r * 0.96 + 0.13, 0.1)], 10, WD)   # aro 0,13 fora


def crate(mb, F, x, y, z, sx=1.4, sy=1.0, sz=0.9, ang=0.0):
    """caixa de tabuas com quadro (cantoneiras e travessas 0,12 a frente das tabuas)"""
    Fc = sub(F, x, y, z, ang)
    bb(mb, Fc, -sx / 2 + 0.1, sx / 2 - 0.1, -sy / 2 + 0.1, sy / 2 - 0.1, 0.0, sz - 0.2, WM)     # tampa recuada 0,15
    for qx in (-1, 1):
        for qy in (-1, 1):
            bb(mb, Fc, qx * (sx / 2 - 0.12), qx * (sx / 2 + 0.02), qy * (sy / 2 - 0.12), qy * (sy / 2 + 0.02), 0.0, sz, WD)
    for zz in (0.12, sz - 0.12):
        for qy in (-1, 1):
            bb(mb, Fc, -sx / 2 + 0.1, sx / 2 - 0.1, qy * (sy / 2 - 0.1), qy * (sy / 2 + 0.02), zz - 0.07, zz + 0.07, WD)


def bolts(mb, F, x, y, z, n=3, m=(CRED, INDIGO, CWHITE), r=0.3, L=1.6):
    """rolos de tecido deitados (pilha em piramide)"""
    k = 0
    for row in range(2):
        for i in range(n - row):
            xx = x + (i - (n - row - 1) / 2) * (2 * r + 0.04)
            mb.rod(F.p(xx, y - L / 2, z + r + row * (2 * r - 0.08)), F.p(xx, y + L / 2, z + r + row * (2 * r - 0.08)),
                   r, m[k % len(m)], 8)
            k += 1


def bench(mb, F, x, y, L=5.0, w=1.8, h=1.7, ang=0.0, z=0.0, m=WM):
    """banco de tabuas (shogi): tampo de 3 tabuas, quadro, 4 pes com travessas"""
    Fb_ = sub(F, x, y, z, ang)
    for i in range(3):
        bb(mb, Fb_, -L / 2, L / 2, -w / 2 + i * w / 3 + 0.03, -w / 2 + (i + 1) * w / 3 - 0.03, h - 0.2, h, m)
    bb(mb, Fb_, -L / 2 + 0.12, L / 2 - 0.12, -w / 2 + 0.08, w / 2 - 0.08, h - 0.44, h - 0.2, WD)
    for sx in (-1, 1):
        for sy in (-1, 1):
            bb(mb, Fb_, sx * (L / 2 - 0.35) - 0.13, sx * (L / 2 - 0.35) + 0.13, sy * (w / 2 - 0.3) - 0.13,
               sy * (w / 2 - 0.3) + 0.13, 0.0, h - 0.44, WD)
        bb(mb, Fb_, sx * (L / 2 - 0.35) - 0.08, sx * (L / 2 - 0.35) + 0.08, -w / 2 + 0.3, w / 2 - 0.3, 0.45, 0.6, WD)
    bb(mb, Fb_, -L / 2 + 0.35, L / 2 - 0.35, -0.07, 0.07, 0.45, 0.6, WD)


def shop_front(mb, Ff, a, b, zn, lit=True, seed=0, noren=True, lod=0):
    """FRENTE DE LOJA cenografica com profundidade: balcao (dai) na linha da fachada com tampo e frente de tabuas,
    mercadoria apoiada (jarros, rolos, caixas, barril sorteados), loja recuada 3,2 (piso, paredes, forro, prateleiras
    com potes, porta de papel acesa no fundo), noren indigo no topo do vao. O vao e a..b de 0 ate zn."""
    cw = b - a
    cx = (a + b) / 2
    dep = 3.6
    bb(mb, Ff, a, b, -dep, -0.9, 0.45, 0.7, WM)                                      # piso (tatami de tabuas)
    bb(mb, Ff, a - 0.2, b + 0.2, -dep - 0.3, -dep, 0.45, zn + 0.5, WD)               # fundo
    for xx in (a, b):
        bb(mb, Ff, xx - 0.12, xx + 0.12, -dep, -0.85, 0.45, zn + 0.5, WD)            # costados
    bb(mb, Ff, a, b, -dep, -0.85, zn + 0.1, zn + 0.5, WD)                            # forro
    # fundo: porta de correr de papel para os comodos (quadro, almofada, kumiko) - papel FOSCO de dia (a luz da loja
    # e a POINT NightOnly do chamador); nada de painel aceso chapado ocupando o fundo
    dw = min(2.8, cw - 1.2)
    bb(mb, Ff, cx - dw / 2 - 0.25, cx + dw / 2 + 0.25, -dep + 0.02, -dep + 0.7, 0.7, 0.95, WD)
    bb(mb, Ff, cx - dw / 2 - 0.25, cx + dw / 2 + 0.25, -dep + 0.02, -dep + 0.7, 6.9, 7.2, WD)
    # 2 trilhos: papel de cada folha 0,14+ a frente do que esta atras (parede / folha de tras)
    _leaf(mb, Ff, cx - 0.06, cx + dw / 2, -dep + 0.2, -dep + 0.34, 0.95, 6.9, False)
    _leaf(mb, Ff, cx - dw / 2, cx + 0.06, -dep + 0.52, -dep + 0.66, 0.95, 6.9, False)
    noren_cloth(mb, sub(Ff, 0.0, -dep + 0.55), cx - dw / 2 - 0.1, cx + dw / 2 + 0.1, 7.1, 1.8, CRED)
    for zz in ((3.9, 5.6) if lod == 0 else ()):                                      # prateleiras com potes
        for xa_, xb_ in ((a + 0.25, cx - 1.5), (cx + 1.5, b - 0.25)):
            if xb_ - xa_ < 0.8:
                continue
            bb(mb, Ff, xa_, xb_, -dep, -dep + 0.9, zz - 0.14, zz, WM)
            for i, xx in enumerate(even(xa_ + 0.2, xb_ - 0.2, 0.9)):
                if _h01(seed, zz, i) < 0.5:
                    pot(mb, Ff, xx, -dep + 0.45, zz, 0.28, 0.6 + 0.3 * _h01(seed, zz, i, "h"),
                        (STD, PL, WM, ST)[int(_h01(seed, zz, i, "m") * 4) % 4])
    # balcao (dai) com tampo saliente e mercadoria
    hz = 2.6
    bb(mb, Ff, a + 0.2, b - 0.2, -1.6, -0.3, 0.7, hz - 0.18, WD)
    for xx in even(a + 0.4, b - 0.4, 1.0):
        bb(mb, Ff, xx - 0.05, xx + 0.05, -0.3, -0.16, 0.8, hz - 0.3, WM)
    bb(mb, Ff, a + 0.05, b - 0.05, -1.75, -0.05, hz - 0.18, hz, WM)
    items = even(a + 0.9, b - 0.9, 1.7 if lod == 0 else 3.4)
    for i, xx in enumerate(items):
        r = _h01(seed, "it", i)
        if r < 0.3:
            jar(mb, Ff, xx, -0.95, hz, 0.42, 0.95, STD if r < 0.15 else PL, lid=r < 0.08)
        elif r < 0.55:
            bolts(mb, Ff, xx, -0.95, hz, 3, (CRED, INDIGO, CWHITE)[int(r * 10) % 3:] + (CRED, INDIGO), 0.26, 1.2)
        elif r < 0.8:
            crate(mb, Ff, xx, -0.95, hz, 1.2, 0.9, 0.7, 0.05)
            jar(mb, Ff, xx, -0.95, hz + 0.48, 0.22, 0.4, ST)       # M6b: pousado na tampa recuada (0,5), nao a 0,2 dela
        else:
            barrel(mb, Ff, xx, -0.95, hz, 0.5, 1.0)
    if noren:
        noren_cloth(mb, Ff, a + 0.2, b - 0.2, zn - 0.12, min(2.6, zn * 0.3), noren)
    return (cx, -2.0, zn * 0.55)


def facade(mb, Ff, L, h, bays, full=True, door_w=DOOR_W, door_h=DOOR_H, plaster=PL, lit=True, ext_=0.9, lod=0,
           noren=None, nageshi=True, seed=0, ground=True, win_z=5.2):
    """uma fachada: soleira (dodai), viga de beiral (keta) que PASSA dos cantos (kibana) nas fachadas 'full', verga
    continua (nageshi), pilares intermediarios e os vaos (reboco entre pilares recuado 0,22). Os pilares de CANTO
    sao de corner_posts(). L = entre as faces externas dos pilares de canto; h = topo da keta."""
    xi0, xi1 = -L / 2 + CP, L / 2 - CP
    zn = SILL + door_h + 0.45
    out = dict(glow=[], doors=[])
    bs = [dict(b) if isinstance(b, dict) else {"t": b} for b in bays]
    for b_ in bs:
        if "w" not in b_ and b_["t"] in ("door", "open_door"):
            b_["w"] = door_w + 0.6
    bs = list(reversed(bs))                              # lista lida da esquerda p/ a direita de quem olha de fora
    n = len(bs)
    fixed = sum(b_.get("w", 0.0) for b_ in bs)
    nfree = sum(1 for b_ in bs if "w" not in b_)
    free = (xi1 - xi0 - (n - 1) * IP - fixed) / max(1, nfree)
    if nfree and free < 1.4:
        print("KIT AVISO fachada L=%.1f: vaos livres de %.2f" % (L, free))
    xa, xb = (-L / 2, L / 2) if full else (xi0, xi1)
    bb(mb, Ff, xa, xb, -0.95, 0.06, 0.0, 0.7, WD)                                          # dodai
    ke = (-L / 2 - ext_, L / 2 + ext_) if full else (xi0, xi1)
    bb(mb, Ff, ke[0], ke[1], -0.95, 0.15, h - 1.0, h, WD, B if lod == 0 else 0.0)          # keta
    if nageshi and zn + 0.5 < h - 1.2:
        ne = (-L / 2 - 0.14, L / 2 + 0.14) if full else (-L / 2 + 0.25, L / 2 - 0.25)
        bb(mb, Ff, ne[0], ne[1], -0.25, 0.14, zn, zn + 0.5, WD)                            # nageshi
    x = xi0
    for i, sp in enumerate(bs):
        w = sp.get("w", free)
        a, b = x, x + w
        _bay(mb, Ff, a, b, sp, h, zn, plaster, lit, lod, out, noren, door_h, seed * 31 + i, ground, win_z)
        x = b
        if i < n - 1:
            bb(mb, Ff, x, x + IP, -0.9, 0.0, 0.7, h - 1.0, WD)
            x += IP
    out["glow"] = [Ff.p(*g) for g in out["glow"]]
    out["doors"] = [(Ff.p(*c), Ff.a) for c in out["doors"]]
    return out


def _bay(mb, Ff, a, b, sp, h, zn, plaster, lit, lod, out, noren, door_h, seed, ground=True, win_z=5.2):
    t = sp["t"]
    cw, cx = b - a, (a + b) / 2
    lt = sp.get("lit", lit)
    ztop = h - 0.95
    pl = sp.get("plaster", plaster)
    if t in ("plain", "koshi", "shoji", "round") and lod == 0 and ground:
        boards(mb, Ff, a, b, 0.7, KH)
        bb(mb, Ff, a, b, -0.76, 0.06, KH, KH + 0.25, WD)
    zb0 = KH + 0.25 if (lod == 0 and ground) else 0.7
    if t in ("plain", "plaster"):
        panel(mb, Ff, a, b, zb0 if t == "plain" else 0.7, ztop, -0.8, -0.22, [], pl)
        if sp.get("nuki", True) and zn - KH > 4.0 and lod == 0:
            zk = KH + 0.25 + (zn - KH - 0.25) * 0.5
            bb(mb, Ff, a, b, -0.34, -0.06, zk - 0.17, zk + 0.17, WD)
    elif t == "koshi":
        zs = zb0
        ww = min(cw - 1.2, sp.get("ww", 8.0))
        wh = min(sp.get("wh", 4.2), zn - 0.75 - zs)
        out["glow"].append(window(mb, Ff, cx, zs, ww, wh, "koshi", lt, sp.get("hood", False), sill=False, lod=lod, pl=pl))
        panel(mb, Ff, a, b, zs, ztop, -0.8, -0.22, [(cx - ww / 2 - 0.3, cx + ww / 2 + 0.3, zs - 0.01, zs + wh + 0.3)], pl)
    elif t in ("shoji", "mushiko", "round"):
        zs = sp.get("z", win_z if (t != "round" or not ground) else 3.6)
        if t == "round":
            ww = wh = min(cw - 1.6, sp.get("ww", 3.6), ztop - zs - 0.6)
        else:
            ww = min(cw - 1.6, sp.get("ww", 4.2))
            wh = min(sp.get("wh", 3.0), ztop - zs - 0.5)
        out["glow"].append(window(mb, Ff, cx, zs, ww, wh, t, lt, sp.get("hood", False), lod=lod, pl=pl))
        mg = 0.3 if t == "shoji" else (0.0 if t == "round" else 0.3)
        panel(mb, Ff, a, b, zb0 if t != "mushiko" else 0.7, ztop, -0.8, -0.22,
              [(cx - ww / 2 - mg, cx + ww / 2 + mg, zs - (0.3 if t != "round" else 0.0), zs + wh + mg)], pl)
    elif t == "lattice":
        lw = cw - 0.6
        out["glow"].append(window(mb, Ff, cx, 0.95, lw, zn - 0.45 - 0.95, "lattice", lt, False, head=0.45, lod=lod))
        panel(mb, Ff, a, b, zn, ztop, -0.8, -0.22, [], pl)
    elif t in ("door", "open_door"):
        dw = cw - 0.6
        kind = "hikido" if t == "door" else "open"
        nr = sp.get("noren", noren)
        d = door(mb, Ff, cx, dw, door_h, kind, lt, nr, SILL)
        out["glow"].append(d["glow"])
        out["doors"].append(d["center"])
        panel(mb, Ff, a, b, 0.7, ztop, -0.8, -0.22, [(cx - dw / 2 - 0.3, cx + dw / 2 + 0.3, 0.0, zn)], pl)
    elif t == "shop":
        g = shop_front(mb, Ff, a, b, zn, lt, seed, sp.get("noren", noren or True), lod)
        panel(mb, Ff, a, b, zn, ztop, -0.8, -0.22, [], pl)
        out["glow"].append(g)
    elif t == "open":
        if sp.get("rail"):
            bb(mb, Ff, a, b, -0.6, -0.2, 3.2, 3.5, WD)
        if sp.get("noren"):
            noren_cloth(mb, Ff, a + 0.25, b - 0.25, ztop - 0.25, min(3.4, ztop * 0.36), sp["noren"])


def corner_posts(mb, Fb, W, D, z0=0.7, z1=None, s=CP, lod=0):
    for sx in (-1, 1):
        for sy in (-1, 1):
            xa, xb = (W / 2 - s, W / 2) if sx > 0 else (-W / 2, -W / 2 + s)
            ya, yb_ = (D / 2 - s, D / 2) if sy > 0 else (-D / 2, -D / 2 + s)
            bb(mb, Fb, xa, xb, ya, yb_, z0, z1, WD, B if (lod == 0 and sy > 0) else 0.0)


def bracket(mb, F, x, y, z, L, w=0.5, h=0.9, m=WD):
    """misula (funa-hijiki) de topo plano em z, saindo L para +y, com o ventre curvo"""
    poly = [(y, z), (y + L, z), (y + L, z - h * 0.35), (y + L * 0.72, z - h * 0.45), (y + L * 0.42, z - h * 0.62),
            (y + L * 0.18, z - h * 0.86), (y, z - h)]
    ext(mb, F, poly, "x", x - w / 2, x + w / 2, m)


# ------------------------------------------------------------------ FUNDACAO
def foundation(mb, F, W, D, h, style="soco", lod=0, sides="FBLR", batter=8.0, lod_faces=""):
    """soco sob a casa. 'soco' = 1 fiada de cantaria (blocos longos com chanfro na face, juntas desencontradas pela
    largura sorteada, cantos travados: frente/fundos levam a pedra de canto); 'ishigaki' = fiadas com talude.
    W x D = topo (face de fora); z de 0 (chao) a h. Enterra 0,4. lod 1 = uma laje por lado."""
    if h <= 0.05 or style == "none":
        return
    t = math.tan(math.radians(batter)) if style == "ishigaki" else 0.0
    g = 0.06
    nc = 1 if style == "soco" else max(1, int(round((h + 0.4) / 1.15)))
    faces = {"F": (0.0, W, D), "B": (math.pi, W, D), "R": (-math.pi / 2, D, W), "L": (math.pi / 2, D, W)}
    for key, (ang, Lf, Df) in faces.items():
        if key not in sides:
            continue
        Ff = sub(F, 0.0, 0.0, 0.0, ang)
        own = key in "FB"
        xa = -Lf / 2 if own else -Lf / 2 + 0.95
        xb = Lf / 2 if own else Lf / 2 - 0.95
        if lod or key == "B" or key in lod_faces:
            bb(mb, Ff, xa, xb, Df / 2 - 0.9, Df / 2, -0.4, h, ST)
            continue
        for c in range(nc):
            z0 = -0.4 + (h + 0.4) * c / nc
            z1 = -0.4 + (h + 0.4) * (c + 1) / nc
            x = xa - ((h - z0) * t if own else 0.0)
            xe = xb + ((h - z0) * t if own else 0.0)
            k = 0
            while x < xe - 0.3:
                ln = 2.6 + 1.6 * _h01(F.o.x, F.o.y, key, c, k)
                k += 1
                x2 = min(xe, x + ln)
                if xe - x2 < 1.0:
                    x2 = xe
                y0f = Df / 2 + (h - z0) * t
                y1f = Df / 2 + (h - z1) * t
                df = 0.06 * (_h01(F.o.x, key, c, k, "d") - 0.5)
                stone(mb, Ff, x + g, x2 - g, z0 + g, z1 - (g if nc > 1 else 0.0), Df / 2 - 0.9, y0f + df, y1f + df,
                      0.1, ST if _h01(key, c, k, "m") > 0.2 else STD)
                x = x2


# ------------------------------------------------------------------ GUARDA-CORPO VERMELHO, VARANDA
def giboshi(mb, F, x, y, z, s=1.0):
    """remate dourado de pilarete (giboshi): colarinho, bulbo e ponta"""
    lathe(mb, F, (x, y, z), [(0.26 * s, 0.0), (0.27 * s, 0.1), (0.2 * s, 0.16), (0.3 * s, 0.32), (0.27 * s, 0.48),
                             (0.12 * s, 0.62), (0.04 * s, 0.78)], 8, GOLD)


def red_rail(mb, F, pts, h=3.6, base=0.0, step=3.4, m=LAC, gold=True):
    """GUARDA-CORPO VERMELHO de laca: pilaretes 0,44 com giboshi dourado nas pontas e nos cantos, corrimao (kasagi)
    que passa das pontas, travessa media e baixa, montantes curtos (tsuka). pts = [(x, y)] locais; z = base"""
    P = [Vector((p[0], p[1], 0.0)) for p in pts]
    nodes = []
    for i, (a, b) in enumerate(zip(P, P[1:])):
        d = b - a
        ln = d.length
        if ln < 0.3:
            continue
        nseg = max(1, int(math.ceil(ln / step)))
        for j in range(nseg + (1 if i == len(P) - 2 else 0)):
            nodes.append((a + d * (j / nseg), j == 0))
        ang = math.atan2(d.y, d.x)
        c = (a + b) / 2
        e0 = 0.3 if i == 0 else 0.0
        e1 = 0.3 if i == len(P) - 2 else 0.0
        cc = c + d.normalized() * (e1 - e0) / 2
        bx(mb, F, cc.x, cc.y, base + h - 0.14, ln + e0 + e1, 0.38, 0.28, m, 0.0, rz=ang)
        bx(mb, F, c.x, c.y, base + h * 0.55, ln, 0.18, 0.22, m, 0.0, rz=ang)
        bx(mb, F, c.x, c.y, base + 0.45, ln, 0.22, 0.24, m, 0.0, rz=ang)
        for j in range(nseg):
            for f in (0.33, 0.67):
                q = a + d * ((j + f) / nseg)
                bx(mb, F, q.x, q.y, base + (0.57 + h * 0.55 - 0.11) / 2, 0.14, 0.14, h * 0.55 - 0.11 - 0.57, m, 0.0,
                   rz=ang)
    for idx, (q, corner) in enumerate(nodes):
        bx(mb, F, q.x, q.y, base + (h + 0.2) / 2 - 0.1, 0.44, 0.44, h + 0.2, m, 0.0)
        if gold and (corner or idx == len(nodes) - 1):
            giboshi(mb, F, q.x, q.y, base + h + 0.1, 0.9)
        else:
            bx(mb, F, q.x, q.y, base + h + 0.18, 0.32, 0.32, 0.16, m, 0.0)


def balcony(mb, Ff, x0, x1, depth, z, rail_h=3.4, lod=0):
    """varanda em consolos (misulas) sob a viga de borda, piso de tabuas, guarda-corpo VERMELHO nos 3 lados"""
    for xx in [x0 + 0.4] + even(x0 + 0.4, x1 - 0.4, 3.4)[1:-1] + [x1 - 0.4]:
        bracket(mb, Ff, xx, -0.4, z - 0.22, depth + 0.3, 0.42, 1.4)
    nb = max(2, int(round(depth / 0.8)))
    for i in range(nb):
        ya = 0.05 + (depth - 0.05) * i / nb
        bb(mb, Ff, x0, x1, ya + 0.03, ya + (depth - 0.05) / nb - 0.03, z - 0.22, z, WM)
    bb(mb, Ff, x0, x1, depth - 0.45, depth, z - 0.72, z - 0.2, WD)
    red_rail(mb, Ff, [(x0 + 0.25, 0.1), (x0 + 0.25, depth - 0.22), (x1 - 0.25, depth - 0.22), (x1 - 0.25, 0.1)],
             rail_h, z)


# ------------------------------------------------------------------ ESCADA, LAJES, MURETA
def _tread_cuts(w, k, key, prev, tries=8):
    """larguras das pedras de um degrau (k pedras) com as juntas DESENCONTRADAS das do degrau de baixo"""
    best = None
    for t in range(tries):
        ws = [0.7 + 0.6 * _h01(key, t, j) for j in range(k)]
        sc = w / sum(ws)
        ws = [v * sc for v in ws]
        cuts = [-w / 2]
        for v in ws:
            cuts.append(cuts[-1] + v)
        cuts[-1] = w / 2
        inner = cuts[1:-1]
        gap = min([abs(c - p) for c in inner for p in prev] or [9.0])
        if best is None or gap > best[0]:
            best = (gap, cuts)
        if gap > 0.8:
            break
    return best[1]


def stair_stone(mb, F, w, n, rise=0.75, tread=1.8, cheeks=True, m=STP, riser_m=STD, cheek_m=ST, z_floor=None,
                seed=None, z_off=0.0, cheek_h=1.0, cap_m=STP, newels=False, newel_lamp=None):
    """escada de pedra: cada degrau em pedras de 2,6..5 (juntas desencontradas de degrau a degrau), focinho 0,1 com
    chanfro 0,05, espelho escuro recuado (bloco sob a pisada), 1 degrau em 5 com a pedra do meio gasta (0,04),
    banzos (sode-ishi) em pedras de 2 fiadas que vencem 2 degraus + capa de lajes inclinada. F no pe do 1o espelho
    (centro), sobe para +y. z_off levanta as pisadas (piso do trecho a +0,15 sobre a colisao). Devolve o topo."""
    TH, NOSE, G = 0.32, 0.1, 0.05
    zf = -0.3 if z_floor is None else z_floor
    key = seed if seed is not None else (round(F.o.x, 1), round(F.o.y, 1), round(F.a, 2), round(w, 1), n)
    kk = max(3, min(9, int(round(w / 3.6))))
    wear0 = int(_h01(key, "wear") * 5)
    prev = []
    for i in range(n):
        zt = rise * (i + 1) + z_off
        y0, y1 = tread * i, tread * (i + 1)
        bb(mb, F, -w / 2 + 0.04, w / 2 - 0.04, y0 + 0.08, y1 + 0.02, zf, zt - TH - 0.02, riser_m)
        k = kk - 1 if i in (0, n - 1) else kk
        cuts = _tread_cuts(w, max(2, k), (key, i), prev)
        prev = cuts[1:-1]
        mid = len(cuts) // 2 - 1
        for j, (x0, x1) in enumerate(zip(cuts, cuts[1:])):
            gx0 = x0 + (G if j > 0 else 0.0)
            gx1 = x1 - (G if j < len(cuts) - 2 else 0.0)
            ztop = zt - (0.04 if (i % 5 == wear0 and j == mid and 0 < i < n - 1) else 0.0)
            dn = 0.03 * (_h01(key, i, j, "n") - 0.5)
            stone(mb, F, gx0, gx1, zt - TH, ztop, y1 + 0.02, y0 - NOSE + dn, y0 - NOSE + dn, 0.05, m)
    if cheeks:
        # banzo (sode-ishigaki) INCLINADO acompanhando a linha dos focinhos: blocos de 2 degraus com o topo chanfrado,
        # junta de 0,06 entre eles, capa continua de lajes inclinadas (pingadeira 0,15 dos dois lados) e pilaretes
        # de arranque/chegada (as lanternas da escadaria pousam neles: topo em z_off + cheek_h + 0,75)
        ztl = lambda y: rise * (y / tread + 1.0) + z_off + cheek_h
        for s in (-1, 1):
            xa, xb = (w / 2, w / 2 + 1.2) if s > 0 else (-w / 2 - 1.2, -w / 2)
            for i in range(0, n, 2):
                i2 = min(n, i + 2)
                ya, yb_ = tread * i + 0.03, tread * i2 - 0.03
                # 2 fiadas: soco reto embaixo + bloco inclinado em cima com a face externa 0,08 recuada (linha de junta
                # sem fresta), pedra escura sorteada por bloco
                zlow = min(ztl(ya), ztl(yb_)) - 1.0
                xo = (lambda d: xb - d) if s > 0 else (lambda d: xa + d)
                xi = xa if s > 0 else xb
                if zlow > zf + 0.4:
                    loft(mb, F, [[(xi, ya, zf), (xo(0.0), ya, zf), (xo(0.0), ya, zlow - 0.08), (xo(0.08), ya, zlow),
                                  (xi, ya, zlow)],
                                 [(xi, yb_, zf), (xo(0.0), yb_, zf), (xo(0.0), yb_, zlow - 0.08), (xo(0.08), yb_, zlow),
                                  (xi, yb_, zlow)]], cheek_m if _h01(key, s, i, "l") > 0.3 else STD)
                else:
                    zlow = zf
                ring = lambda y: [(xa if s > 0 else xa + 0.08, y, zlow), (xb - 0.08 if s > 0 else xb, y, zlow),
                                  (xb - (0.08 if s > 0 else 0.0), y, ztl(y) - 0.12), (xb - 0.12 - (0.08 if s > 0 else 0.0), y, ztl(y)),
                                  (xa + 0.12 + (0.0 if s > 0 else 0.08), y, ztl(y)), (xa + (0.0 if s > 0 else 0.08), y, ztl(y) - 0.12)]
                loft(mb, F, [ring(ya), ring(yb_)], cheek_m if _h01(key, s, i, "c") > 0.25 else STD)
            ya, yb_ = 0.6, tread * (n - 1) + 0.2
            cap = lambda y: [(xa - 0.15, y, ztl(y) - 0.1), (xb + 0.15, y, ztl(y) - 0.1), (xb + 0.15, y, ztl(y) + 0.26),
                             (xa - 0.15, y, ztl(y) + 0.26)]
            loft(mb, F, [cap(ya), cap(yb_)], cap_m)
            for yc, zt in (((-0.55, z_off + cheek_h + 0.75), (tread * n - 0.45, rise * n + z_off + cheek_h + 0.75)) if newels else ()):
                bb(mb, F, xa - 0.2, xb + 0.2, yc - 0.65, yc + 0.65, zf, zt - 0.3, cheek_m)
                if newel_lamp and yc < 0:                  # pilarete de arranque com ANDON (tampa reta + suporte)
                    xm = (xa + xb) / 2
                    bb(mb, F, xm - 0.95, xm + 0.95, yc - 0.85, yc + 0.85, zt - 0.3, zt - 0.06, cap_m)
                    bb(mb, F, xm - 0.32, xm + 0.32, yc - 0.32, yc + 0.32, zt - 0.06, zt + 0.5, WD)
                    c = _box_lantern(mb, F, (xm, yc, zt + 0.64), 0.55, 0.55, 1.4)
                    light("%s_%d" % (newel_lamp, 0 if s < 0 else 1), "POINT", F.p(*c), 35.0, WARM, 0.2)
                else:
                    lathe(mb, F, ((xa + xb) / 2, yc, zt - 0.3), [(0.95, 0.0), (0.95, 0.16), (0.3, 0.42), (0.1, 0.5)], 4,
                          cap_m, math.pi / 4)
    return F.p(0.0, tread * n, rise * n + z_off)


def slab_poly(mb, poly, z0, z1, c=0.07, m=STZ, sides=True):
    """laje (poligono 2D ccw, mundo) de z0 a z1 com chanfro c no topo: lajes vizinhas lado a lado formam a JUNTA
    REBAIXADA (V) sem fresta e sem miolo de outra cor. Sem face de baixo. sides=False (laje cercada por outras: o pave
    decide) = so chanfro + topo (10 tris): as faces laterais ficariam escondidas pelas vizinhas."""
    if len(poly) < 3:
        return
    xs = [p[0] for p in poly]
    ys = [p[1] for p in poly]
    small = min(max(xs) - min(xs), max(ys) - min(ys)) < 4 * c + 0.1
    F0 = Frame(0.0, 0.0, 0.0, 0.0)
    if small or c <= 0:
        loft(mb, F0, [[(x, y, z0) for x, y in poly], [(x, y, z1) for x, y in poly]], m, caps=(False, True))
        return
    ins = DL.offset_poly(poly, -c)
    rings = ([[(x, y, z0) for x, y in poly]] if sides else []) + [[(x, y, z1 - c) for x, y in poly],
                                                                [(x, y, z1) for x, y in ins]]
    loft(mb, F0, rings, m, caps=(False, True))


def _area(P_):
    return abs(sum(P_[i][0] * P_[(i + 1) % len(P_)][1] - P_[(i + 1) % len(P_)][0] * P_[i][1] for i in range(len(P_)))) / 2


def _clip_rect(poly, rect):
    import op_layout as L
    return L.clip_rect(poly, rect)


def pave(mb, region, x0, x1, y0, y1, rows, m, z_top, z_bot=None, along="x", bond=0.5, key="pv", c=0.07, mats=None):
    """lajes em fiadas recortadas no poligono 'region' (ccw, mundo): fiadas perpendiculares a 'along' com
    profundidade rows (numero ou lista ciclica), comprimento das lajes sorteado em [L0, L1] (rows = (prof, L0, L1)),
    juntas desencontradas (bond). mats = [(material, peso)] sorteado por laje. Devolve o numero de lajes."""
    import op_layout as L_
    prof, L0, L1 = rows
    zb = z_top - 0.45 if z_bot is None else z_bot
    n = 0
    if along == "x":
        u0, u1, v0, v1 = x0, x1, y0, y1
    else:
        u0, u1, v0, v1 = y0, y1, x0, x1
    v = v0
    r = 0
    while v < v1 - 1e-3:
        dv = prof[r % len(prof)] if isinstance(prof, (list, tuple)) else prof
        vb = min(v1, v + dv)
        if v1 - vb < 0.6:
            vb = v1
        u = u0 - (L0 * bond * _h01(key, r, "o"))
        k = 0
        while u < u1 - 1e-3:
            ln = L0 + (L1 - L0) * _h01(key, r, k)
            ub = min(u1, u + ln)
            if u1 - ub < 0.6:
                ub = u1
            ua = max(u, u0)
            if ub - ua > 0.05:
                rect = (ua, v, ub, vb) if along == "x" else (v, ua, vb, ub)
                piece = _clip_rect(region, rect)
                if len(piece) >= 3 and _area(piece) > 0.25:
                    mm = m
                    if mats:
                        tot = sum(w for _, w in mats)
                        x = _h01(key, r, k, "m") * tot
                        for mat_, w in mats:
                            x -= w
                            if x <= 0:
                                mm = mat_
                                break
                    inner = len(piece) == 4 and abs(_area(piece) - (rect[2] - rect[0]) * (rect[3] - rect[1])) < 1e-3                         and min(L_.poly_edge_dist(px, py, region) for px, py in piece) > 0.05
                    slab_poly(mb, piece, zb, z_top, c, mm, not inner)
                    n += 1
            u = ub
            k += 1
        v = vb
        r += 1
    return n


def _xblock(mb, F, x0, x1, sec, m):
    """bloco extrudado ao longo de x com secao sec = [(y, z)] (ccw no plano y-z): pecas de cantaria com chanfro"""
    loft(mb, F, [[(x0, y, z) for y, z in sec], [(x1, y, z) for y, z in sec]], m)


def parapet(mb, F, L, h=2.4, th=1.3, m="Stone_OP_Wall", cap_m=STP, post_every=12.0, posts=True, key="pp"):
    """MURETA baixa de cantaria ao longo de x (F no meio da base, z=0 = piso): blocos de 2,2-4 (corpo, face
    chanfrada 0,1, junta de 0,06 desencontrada da capa, 1 em 5 mais escuro), capa de lajes com pingadeira 0,15 para
    fora dos dois lados e topo chanfrado, pilaretes mais altos a cada post_every com tampa piramidal. ~25 tris/stud."""
    m = m if m in fm_lib.MATS else ST
    zc = h - 0.38
    c = 0.1
    body = [(-th / 2, -0.3), (th / 2, -0.3), (th / 2, zc - c), (th / 2 - c, zc), (-th / 2 + c, zc), (-th / 2, zc - c)]
    x = -L / 2
    k = 0
    while x < L / 2 - 0.3:
        x2 = min(L / 2, x + 2.2 + 1.8 * _h01(key, F.o.x, F.o.y, k))
        if L / 2 - x2 < 1.0:
            x2 = L / 2
        _xblock(mb, F, x + 0.03, x2 - 0.03, body, m if _h01(key, "m", F.o.x, k) > 0.15 else ST)
        x = x2
        k += 1
    # junta escura (M6b: miolo 0,2 atras da face dos blocos e 0,3 para dentro das pontas: nada coplanar com o bloco
    # da ponta nem a 0,12 da face)
    bb(mb, F, -L / 2 + 0.3, L / 2 - 0.3, -th / 2 + 0.2, th / 2 - 0.2, -0.22, zc - 0.05, STD)
    o = 0.15
    cap = [(-th / 2 - o, zc - 0.04), (th / 2 + o, zc - 0.04), (th / 2 + o, zc + 0.22), (th / 2 + o - 0.12, zc + 0.36),
           (-th / 2 - o + 0.12, zc + 0.36), (-th / 2 - o, zc + 0.22)]
    ce = -0.2 if posts else 0.1                      # M6b: com pilaretes a capa morre DENTRO deles (pontas a 0,07 eram z-fight)
    x = -L / 2 - ce
    k = 0
    while x < L / 2 + ce - 0.3:
        x2 = min(L / 2 + ce, x + 2.6 + 1.4 * _h01(key, "cap", F.o.x, k))
        if L / 2 + ce - x2 < 1.0:
            x2 = L / 2 + ce
        _xblock(mb, F, x + 0.03, x2 - 0.03, cap, cap_m)
        x = x2
        k += 1
    if posts:
        n = max(1, int(round(L / post_every)))
        for i in range(n + 1):
            xp = max(-L / 2 + 0.75, min(L / 2 - 0.75, -L / 2 + L * i / n))
            bb(mb, F, xp - 0.75, xp + 0.75, -th / 2 - 0.25, th / 2 + 0.25, -0.3, h + 0.3, m)
            lathe(mb, F, (xp, 0.0, h + 0.3), [(1.08, 0.0), (1.08, 0.18), (0.25, 0.6), (0.08, 0.68)], 4, cap_m,
                  math.pi / 4)


def retaining_wall(mb, F, L, h, batter=6.0, m="Stone_OP_Wall", cap_m=STP, key="rw", cap=True, z0=-0.4, top=0.0,
                   face_off=0.0, core_lift=0.0):
    """ARRIMO de pedra aparelhada (kirikomi) ao longo de x, face para +y em y=0 no TOPO (talude 'batter' graus para
    fora embaixo): fiadas de altura variada (1,3..2,1), blocos de 2,6..4,6 com face chanfrada e juntas desencontradas
    sobre miolo escuro (junta rebaixada 0,06), 1 bloco em 6 em pedra escura, capa de lajes rente ao piso de cima.
    F no topo do muro (z=0 = piso de cima, o muro desce ate h abaixo + 0,4 enterrado). Sob um piso de lajes de outro
    construtor: cap=False, top=-0,16 (topo das pedras ESCONDIDO sob as lajes) e face_off=0,14 (face 0,14 a frente da
    borda das lajes: nada coplanar; a borda da laje vira o labio da capa)."""
    m = m if m in fm_lib.MATS else ST
    t = math.tan(math.radians(batter))
    capt = 0.4 if cap else 0.0
    zt = top - capt
    zb = -h + z0
    bb(mb, F, -L / 2 + 0.15, L / 2 - 0.15, -1.6, -0.25 + face_off, zb + 0.15 + core_lift, zt - 0.05, STD)                                          # miolo (juntas); core_lift (M6b): fundo do miolo longe do fundo das pedras
    z = zb
    c = 0
    while z < zt - 0.3:
        hc = 1.3 + 0.8 * _h01(key, F.o.x, F.o.y, "c", c)
        z2 = min(zt, z + hc)
        if zt - z2 < 0.8:
            z2 = zt
        x = -L / 2 - (0.0 if c % 2 else 0.9 * _h01(key, "o", c))
        k = 0
        while x < L / 2 - 0.2:
            x2 = min(L / 2, x + 2.6 + 2.0 * _h01(key, F.o.x, c, k))
            if L / 2 - x2 < 1.0:
                x2 = L / 2
            xa = max(x, -L / 2)
            df = 0.05 * (_h01(key, "d", c, k) - 0.5)
            stone(mb, F, xa + 0.03, x2 - 0.03, z + 0.03, z2 - 0.03, -1.2, -z * t + df + face_off, -z2 * t + df + face_off, 0.1,
                  m if _h01(key, "m", c, k) > 0.16 else STD)
            x = x2
            k += 1
        z = z2
        c += 1
    if cap:
        x = -L / 2
        k = 0
        while x < L / 2 - 0.2:
            x2 = min(L / 2, x + 2.8 + 1.4 * _h01(key, "cap", F.o.x, k))
            if L / 2 - x2 < 1.0:
                x2 = L / 2
            stone(mb, F, x + 0.03, x2 - 0.03, zt, 0.0, -1.5, 0.14, 0.14, 0.08, cap_m)
            x = x2
            k += 1


# ------------------------------------------------------------------ LANTERNAS (luz so dentro da armacao)
def chochin(mb, F, c, r=0.62, hgt=1.6, body=CRED, cap_m=WD, n=8):
    """CHOCHIN de 8 lados: corpo abaulado em 3 faixas (pontas no pano da cor 'body', SO a do meio acesa), aros
    0,12 para fora do pano nas emendas e no meio das faixas, tampas de laca escura. c = centro da BASE (x, y, z).
    Devolve o centro do corpo (ponto da luz)"""
    cx, cy, z0 = c
    zA, zB = z0 + 0.2, z0 + hgt - 0.2
    H = zB - zA
    rz = lambda u: r * (0.7 + 0.3 * math.sin(math.pi * u))
    cuts = (0.0, 0.3, 0.7, 1.0)
    for k in range(3):
        u0, u1 = cuts[k], cuts[k + 1]
        prof = [(rz(u0), H * u0), (rz((u0 + u1) / 2), H * (u0 + u1) / 2), (rz(u1), H * u1)]
        lathe(mb, F, (cx, cy, zA), prof, n, LGLOW if k == 1 else body, math.pi / n, (False, False))   # tubos abertos
    for u in (0.3, 0.7):
        rr = rz(u) + 0.12
        lathe(mb, F, (cx, cy, zA + H * u), [(rr, -0.04), (rr, 0.04)], n, cap_m, math.pi / n)
    rc = rz(0.0) + 0.07
    lathe(mb, F, (cx, cy, zA), [(rc * 0.8, -0.2), (rc, -0.1), (rc, 0.05)], n, cap_m, math.pi / n)
    lathe(mb, F, (cx, cy, zB), [(rc, -0.05), (rc, 0.1), (rc * 0.8, 0.2)], n, cap_m, math.pi / n)
    return (cx, cy, zA + H * 0.5)


def _box_lantern(mb, F, c, hx, hy, hz, frame=WD, cap_m=RR):
    """caixa de lanterna (andon): ARMACAO (montantes de canto 0,2, travessas 0,16, kumiko 2 x 3 por face), papel
    RECUADO 0,18 em 3 faixas (SO a do meio acesa = Neon; as de cima/baixo papel quente fosco), chapeu de 4 aguas com
    beiral 0,45 e ponteira de ferro. c = (x, y, z da base)"""
    cx, cy, z0 = c
    t, rb, ins = 0.2, 0.16, 0.18
    za, zb = z0 + rb, z0 + hz - rb
    z1, z2 = za + 0.25 * (zb - za), za + 0.75 * (zb - za)
    px, py = hx - ins, hy - ins
    bb(mb, F, cx - px, cx + px, cy - py, cy + py, za, z1, LIT)
    bb(mb, F, cx - px, cx + px, cy - py, cy + py, z1, z2, LGLOW)
    bb(mb, F, cx - px, cx + px, cy - py, cy + py, z2, zb, LIT)
    for sx in (-1, 1):
        for sy in (-1, 1):
            bb(mb, F, cx + sx * hx - (t if sx > 0 else 0), cx + sx * hx + (0 if sx > 0 else t),
               cy + sy * hy - (t if sy > 0 else 0), cy + sy * hy + (0 if sy > 0 else t), z0, z0 + hz, frame)
    q = 0.02
    bb(mb, F, cx - hx + q, cx + hx - q, cy - hy + q, cy + hy - q, z0, za, frame)
    bb(mb, F, cx - hx + q, cx + hx - q, cy - hy + q, cy + hy - q, zb, z0 + hz, frame)
    q = 0.04
    for zz in (z1, z2):
        bb(mb, F, cx - hx + q, cx + hx - q, cy - hy + q, cy + hy - q, zz - 0.07, zz + 0.07, frame)
    bb(mb, F, cx - 0.06, cx + 0.06, cy - hy + q, cy + hy - q, za, zb, frame)
    bb(mb, F, cx - hx + q, cx + hx - q, cy - 0.06, cy + 0.06, za, zb, frame)
    bb(mb, F, cx - hx - 0.08, cx + hx + 0.08, cy - hy - 0.08, cy + hy + 0.08, z0 - 0.14, z0 + 0.05, frame)
    zr = hip_cap(mb, F, (cx, cy), hx + 0.04, hy + 0.04, z0 + hz, 0.45, min(hx, hy) * 0.75, 0.1, cap_m, 0.12)
    lathe(mb, F, (cx, cy, zr - 0.05), [(0.16, 0.0), (0.2, 0.12), (0.1, 0.26), (0.13, 0.38), (0.02, 0.55)], 6, IRON)
    return (cx, cy, z0 + hz * 0.5)


def lantern_post(mb, F, h=9.0, arm=1.7, light_name=None, energy=40.0, body=CRED):
    """POSTE DE RUA de Wano: pedra-base com colar, poste chanfrado de 0,6 com 2 cintas de ferro, capitel e chapeu de
    telha, TRAVESSA (2 bracos com maos-francesas) e 2 CHOCHIN vermelhos pendurados em ganchos. F no pe; travessa ao
    longo de x"""
    rock_base(mb, F, 0.0, 0.0, 0.0, 1.0, 0.55)
    lathe(mb, F, (0, 0, 0.4), [(0.62, 0.0), (0.62, 0.3), (0.42, 0.42)], 4, ST, math.pi / 4)
    bb(mb, F, -0.3, 0.3, -0.3, 0.3, 0.5, h, WD, 0.06)
    for zz in (1.4, h - 2.4):
        bb(mb, F, -0.34, 0.34, -0.34, 0.34, zz - 0.12, zz + 0.12, IRON)
    bb(mb, F, -0.44, 0.44, -0.44, 0.44, h, h + 0.18, WD)
    hip_cap(mb, F, (0.0, 0.0), 0.44, 0.44, h + 0.18, 0.22, 0.34, 0.1, RR, 0.06)
    za = h - 0.9
    bb(mb, F, -arm - 0.4, arm + 0.4, -0.2, 0.2, za - 0.32, za, WD)
    pts = []
    for s in (-1, 1):
        beam(mb, F, (s * 0.2, 0.0, za - 1.9), (s * arm * 0.65, 0.0, za - 0.3), 0.16, 0.2, WD)
        x = s * arm
        mb.rod(F.p(x, 0.0, za - 0.3), F.p(x, 0.0, za - 0.75), 0.05, IRON, 6)
        pts.append(F.p(*chochin(mb, F, (x, 0.0, za - 0.75 - 1.6), 0.55, 1.6, body)))
    if light_name:
        light(light_name, "POINT", F.p(0.0, 0.0, za - 1.5), energy, WARM, 0.3)
    return pts


def lantern_box_post(mb, F, h=7.6, light_name=None, energy=35.0):
    """poste baixo com ANDON de armacao no topo (borda da praca / patamar): pedra, poste, mesa de apoio, caixa"""
    rock_base(mb, F, 0.0, 0.0, 0.0, 0.95, 0.5)
    bb(mb, F, -0.3, 0.3, -0.3, 0.3, 0.3, h - 1.9, WD, 0.06)
    bb(mb, F, -0.75, 0.75, -0.75, 0.75, h - 2.05, h - 1.85, WD)
    for s in (-1, 1):
        beam(mb, F, (0.0, s * 0.2, h - 3.0), (0.0, s * 0.62, h - 2.06), 0.14, 0.16, WD)
        beam(mb, F, (s * 0.2, 0.0, h - 3.0), (s * 0.62, 0.0, h - 2.06), 0.14, 0.16, WD)
    c = _box_lantern(mb, F, (0.0, 0.0, h - 1.85 + 0.14), 0.6, 0.6, 1.5)
    if light_name:
        light(light_name, "POINT", F.p(*c), energy, WARM, 0.2)
    return F.p(*c)


def lantern_wall(mb, F, light_name=None, energy=25.0, out=1.3, body=CRED):
    """chochin de parede: espelho de ferro com 2 parafusos, braco e mao-francesa, gancho. F na face da parede (+y
    fora), z = altura do braco"""
    bb(mb, F, -0.28, 0.28, -0.05, 0.12, -1.0, 0.85, IRON)
    for zz in (-0.7, 0.55):
        mb.rod(F.p(0.0, 0.1, zz), F.p(0.0, 0.26, zz), 0.07, IRON, 6)
    bb(mb, F, -0.08, 0.08, 0.05, out + 0.12, -0.12, 0.04, IRON)
    beam(mb, F, (0.0, 0.1, -0.85), (0.0, out * 0.7, -0.1), 0.1, 0.1, IRON)
    mb.rod(F.p(0.0, out, -0.04), F.p(0.0, out, -0.4), 0.04, IRON, 6)
    c = chochin(mb, F, (0.0, out, -0.4 - 1.35), 0.46, 1.35, body)
    if light_name:
        light(light_name, "POINT", F.p(*c), energy, WARM, 0.15)
    return F.p(*c)


def toro(mb, F, s=1.0, light_name=None, energy=35.0, m=ST):
    """lanterna de pedra (pedestal sextavado): base, fuste com aneis, plataforma, camara com 6 montantes e nucleo
    aceso recuado + 2 paineis cheios, chapeu com pontas enroladas (warabite), joia (hoju)"""
    S_ = lambda prof: [(r * s, z * s) for r, z in prof]
    lathe(mb, F, (0, 0, 0), S_([(1.4, -0.2), (1.4, 0.42), (1.12, 0.7), (0.66, 0.86)]), 6, m)
    lathe(mb, F, (0, 0, 0), S_([(0.46, 0.84), (0.46, 1.6), (0.56, 1.68), (0.56, 1.84), (0.44, 1.92), (0.42, 3.0),
                                (0.52, 3.08), (0.52, 3.16)]), 8, m)
    lathe(mb, F, (0, 0, 0), S_([(0.58, 3.14), (1.12, 3.58), (1.12, 3.88), (1.0, 3.96)]), 6, m)
    zc0, zc1, rc = 3.96 * s, 5.4 * s, 0.9 * s
    n = 6
    lathe(mb, F, (0, 0, 0), [(rc * 0.62, zc0 + 0.04), (rc * 0.62, zc1 - 0.1)], n, LGLOW)
    for i in range(n):
        a = 2 * math.pi * i / n
        bx(mb, F, rc * 0.9 * math.cos(a), rc * 0.9 * math.sin(a), (zc0 + zc1) / 2, 0.32 * s, 0.32 * s, zc1 - zc0, m, 0.0,
           rz=a)
    lathe(mb, F, (0, 0, 0), [(rc * 1.02, zc1 - 0.22 * s), (rc * 1.06, zc1 - 0.18 * s), (rc * 1.06, zc1 + 0.02),
                             (rc * 0.9, zc1 + 0.06)], n, m)
    ap = rc * math.cos(math.pi / n)
    for i in (1, 4):
        a = 2 * math.pi * (i + 0.5) / n
        bx(mb, F, ap * 0.86 * math.cos(a), ap * 0.86 * math.sin(a), (zc0 + zc1) / 2, rc * 0.95, 0.16 * s,
           zc1 - zc0 - 0.05, m, 0.0, rz=a + math.pi / 2)
    kz = zc1
    kasa = [(0.95, 0.0), (1.8, 0.14), (1.88, 0.34), (1.32, 0.62), (0.6, 1.02), (0.42, 1.12)]
    lathe(mb, F, (0, 0, kz), S_(kasa), n, m)
    rk = kasa[1][0] * s
    for i in range(n):
        a = 2 * math.pi * i / n
        bx(mb, F, rk * math.cos(a), rk * math.sin(a), kz + 0.32 * s, 0.36 * s, 0.28 * s, 0.36 * s, m, 0.0, ry=-0.6, rz=a)
    hz = kz + 1.12 * s
    lathe(mb, F, (0, 0, hz), S_([(0.36, 0.0), (0.48, 0.14), (0.32, 0.26), (0.32, 0.3), (0.42, 0.46), (0.36, 0.68),
                                 (0.15, 0.88), (0.02, 1.0)]), 8, m)
    c = (0.0, 0.0, (zc0 + zc1) / 2)
    if light_name:
        light(light_name, "POINT", F.p(*c), energy, WARM, 0.2)
    return F.p(*c)


# ------------------------------------------------------------------ ESTANDARTE (nobori) com suporte real
def banner(mb, F, h=16.0, cloth=CWHITE, crest=INDIGO, cw=2.6, side=1):
    """ESTANDARTE vertical (nobori) com SUPORTE REAL: base de pedra chanfrada com colar de ferro e 4 cunhas, mastro
    redondo afinando, ponteira dourada, braco de cima (chichi), pano preso por 5 aneis no mastro e
    no braco, barra de peso embaixo, BRASAO circular (anel + disco, contorno limpo) atravessando o pano e saindo 0,14
    dos dois lados (nada coplanar). F no pe; o pano fica para +x*side"""
    s = side
    bb(mb, F, -0.95, 0.95, -0.95, 0.95, -0.3, 0.55, ST, 0.08)
    lathe(mb, F, (0, 0, 0.55), [(0.62, 0.0), (0.62, 0.22), (0.44, 0.34)], 8, ST)
    lathe(mb, F, (0, 0, 0.86), [(0.34, -0.02), (0.34, 0.4)], 8, IRON)
    for i in range(4):
        a = math.pi / 4 + i * math.pi / 2
        beam(mb, F, (0.72 * math.cos(a), 0.72 * math.sin(a), 0.55), (0.3 * math.cos(a), 0.3 * math.sin(a), 1.2),
             0.14, 0.16, IRON)
    lathe(mb, F, (0, 0, 0.86), [(0.24, 0.0), (0.2, h - 0.86)], 8, WD)
    lathe(mb, F, (0, 0, h), [(0.22, 0.0), (0.3, 0.15), (0.18, 0.4), (0.03, 0.85)], 8, GOLD)
    zt = h - 0.55
    x0, x1 = s * 0.35, s * (cw + 0.55)
    bb(mb, F, min(-0.2 * s, x1), max(-0.2 * s, x1), -0.11, 0.11, zt - 0.11, zt + 0.11, WD)
    zc0, zc1 = zt - 0.35, zt - 0.35 - h * 0.58
    xa, xb = min(x0, s * (cw + 0.35)), max(x0, s * (cw + 0.35))
    bb(mb, F, xa, xb, -0.08, 0.08, zc1, zc0, cloth)
    bb(mb, F, xa - 0.1, xb + 0.1, -0.13, 0.13, zc1 - 0.18, zc1 + 0.05, WD)               # barra de peso
    for k in range(5):                                                                  # aneis de pano no mastro
        zz = zc0 - (zc0 - zc1) * (k + 0.5) / 5
        bb(mb, F, min(-0.3, x0 - 0.05), max(0.3, x0 + 0.05), -0.12, 0.12, zz - 0.12, zz + 0.12, cloth)
    for k in range(3):                                                                  # alcas no braco (0,13 fora)
        xx = xa + (xb - xa) * (k + 0.5) / 3
        bb(mb, F, xx - 0.14, xx + 0.14, -0.24, 0.24, zc0 - 0.05, zt + 0.26, cloth)
    if crest:
        cx = (xa + xb) / 2
        cz = zc0 - (zc0 - zc1) * 0.27
        R = min(1.0, (xb - xa) * 0.4)
        # anel (contorno limpo, 24 lados) + disco central: atravessam o pano e saem 0,14 de cada lado
        n = 16
        ro, ri = R, R * 0.74
        rings = []
        for rr, yy in ((ro, -0.22), (ro, 0.22), (ri, 0.22), (ri, -0.22)):
            rings.append([(cx + rr * math.cos(2 * math.pi * j / n), yy, cz + rr * math.sin(2 * math.pi * j / n))
                          for j in range(n)])
        rings.append(rings[0])
        loft(mb, F, rings, crest, caps=(False, False))
        lathe_y(mb, F, (cx, 0.0, cz), [(R * 0.4, -0.22), (R * 0.4, 0.22)], 10, crest)
    return F.p(0.0, 0.0, h)


# ------------------------------------------------------------------ PAVILHAO (familia)
def pavilion(mb, F, W, D, h=8.0, kind="irimoya", red=True, roof_m=RB, open_side="F", deck=1.2, lod=0, gold=False):
    """PAVILHAO aberto: pilares (laca vermelha ou madeira) sobre pedras, estrado de tabuas elevado com viga de borda,
    vigas de cabeca (nuki + keta) com consolos, guarda-corpo vermelho nos lados (aberto em open_side com degraus de
    pedra), telhado irimoya/yosemune com beiral grosso"""
    pm = LAC if red else WD
    xs = even(-W / 2 + 0.5, W / 2 - 0.5, 5.5)
    xs = [-W / 2 + 0.5] + xs[1:-1] + [W / 2 - 0.5] if len(xs) > 1 else [-W / 2 + 0.5, W / 2 - 0.5]
    ys = [-D / 2 + 0.5, D / 2 - 0.5]
    for x in xs:
        for y in ys:
            rock_base(mb, F, x, y, 0.0, 0.85, 0.45)
            # M6c: o pilar morre 0,15 dentro da keta (topos eram coplanares)
            bb(mb, F, x - 0.45, x + 0.45, y - 0.45, y + 0.45, 0.4, deck + h - 0.15, pm, B)
    nb = max(3, int(round(W / 0.9)))
    for i in range(nb):
        x0 = -W / 2 + 0.2 + (W - 0.4) * i / nb
        bb(mb, F, x0 + 0.03, x0 + (W - 0.4) / nb - 0.03, -D / 2 + 0.2, D / 2 - 0.2, deck - 0.22, deck, WM)
    for sy in (-1, 1):
        bb(mb, F, -W / 2, W / 2, sy * (D / 2 - 0.45) - 0.25, sy * (D / 2 - 0.45) + 0.25, deck - 0.75, deck - 0.2, WD)
    for sx in (-1, 1):
        bb(mb, F, sx * (W / 2 - 0.45) - 0.25, sx * (W / 2 - 0.45) + 0.25, -D / 2, D / 2, deck - 0.75, deck - 0.2, WD)
    for sy in (-1, 1):
        bb(mb, F, -W / 2 - 0.6, W / 2 + 0.6, sy * (D / 2 - 0.5) - 0.3, sy * (D / 2 - 0.5) + 0.3, deck + h - 2.4,
           deck + h - 1.8, pm)
        # M6c: keta 0,12 MAIS LARGA que o pilar (+-0,57 x +-0,45; era +-0,42: a face do pilar laqueado ficava 0,03
        # a frente da keta escura = z-fight laca x madeira)
        bb(mb, F, -W / 2 - 0.9, W / 2 + 0.9, sy * (D / 2 - 0.5) - 0.57, sy * (D / 2 - 0.5) + 0.57, deck + h - 0.9,
           deck + h, WD)
    for sx in (-1, 1):
        bb(mb, F, sx * (W / 2 - 0.5) - 0.57, sx * (W / 2 - 0.5) + 0.57, -D / 2 - 0.9, D / 2 + 0.9, deck + h - 0.9,
           deck + h - 0.02, WD)
    rh = 3.0
    if open_side != "R":
        red_rail(mb, F, [(W / 2 - 0.5, -D / 2 + 0.5), (W / 2 - 0.5, D / 2 - 0.5)], rh, deck)
    if open_side != "L":
        red_rail(mb, F, [(-W / 2 + 0.5, D / 2 - 0.5), (-W / 2 + 0.5, -D / 2 + 0.5)], rh, deck)
    red_rail(mb, F, [(-W / 2 + 0.5, -D / 2 + 0.5), (W / 2 - 0.5, -D / 2 + 0.5)], rh, deck)
    if open_side == "F":
        for s in (-1, 1):
            red_rail(mb, F, [(s * (W / 2 - 0.5), D / 2 - 0.5), (s * 2.6, D / 2 - 0.5)], rh, deck)
        ns = max(1, int(math.ceil(deck / 0.7)) - 1)
        rs = deck / (ns + 1)
        for j in range(ns):                                       # degraus de pedra ate o estrado
            y0 = D / 2 - 0.2 + j * 1.4
            stone(mb, sub(F, 0.0, 0.0, 0.0), -2.4, 2.4, -0.3, deck - rs * (j + 1), y0 - 1.0, y0 + 1.4, y0 + 1.4, 0.08, STP)
    if kind == "kirizuma":
        r = roof_gable(mb, sub(F, z=deck), W, D, h, 0.62, 2.8, 1.8, 0.7, 0.5, lod, PL, "board", True, roof_m)
    else:
        r = roof_hip(mb, sub(F, z=deck), W, D, h, kind, 0.55, 3.0, 0.66, 1.3, 1.1, 0.5, lod, PL, "timber", True,
                     roof_m, gold=gold)
    return dict(top_z=F.o.z + deck + r["zr"], deck_z=F.o.z + deck)


# ------------------------------------------------------------------ EDIFICIO (montagem + variacoes dirigidas)
DEFAULTS = dict(W=16.0, D=20.0, plinth=("soco", 0.9), plaster=PLS, plaster_up=PL, roof_m=RB,
                floors=[dict(h=10.5)], roof=dict(kind="irimoya", ridge="x"), kara=None, chochin=(), lit=True,
                noren=INDIGO, lod=0, back_lod=1, door_w=DOOR_W, door_h=DOOR_H, seed=0)
ROOF_DEF = dict(kind="irimoya", ridge="x", pitch=0.55, over=3.2, gable=0.66, g_over=1.5, lift=1.25, tv=0.55, steep=1.5,
                gable_style="timber", chidori=None, gold=False, courses=2)


def auto_bays(L, kind="side"):
    """laterais: reboco com 1 janela alta no meio; fundos: tabuas/reboco com koshi alternada"""
    n = max(1, int(round((L - 2 * CP) / 5.4)))
    if kind == "back":
        return ["plain" if i % 2 == 0 else "koshi" for i in range(n)] if n > 2 else ["plain"] * n
    out = ["plaster"] * n
    if n >= 2:
        out[n // 2] = "shoji"
    return out


PRESETS = {
    # C1 - LOJA de 2 pisos (hirairi): 2 vaos de loja + trelica no terreo, varanda VERMELHA no piso de cima com
    #      shoji, irimoya com CHIDORI na agua da frente. Gesto: varanda + chidori
    "C1": dict(W=16.0, D=22.0, plinth=("soco", 0.9),
               floors=[dict(h=10.5, front=["lattice", "shop", "shop"], left=["plaster", "round", "plaster"],
                            right=["plaster", "shoji", "plaster"]),
                       dict(h=8.6, front=["plaster", "shoji", "shoji", "plaster"], balcony=dict(depth=2.4),
                            left=["plaster", "plaster"], right=["plaster", "plaster"])],
               roof=dict(kind="irimoya", ridge="x", pitch=0.56, over=3.3, chidori=dict(x=0.0, w=7.0)),
               chochin=[(-5.0, 9.6), (5.0, 9.6)], gesture="varanda + chidori"),
    # C2 - LOJA de EMPENA para a rua (tsumairi): kirizuma com a cumeeira no fundo, empena de reboco com madeiramento,
    #      HISASHI corrido na frente, loja central entre 2 koshi. Gesto: empena para a rua
    "C2": dict(W=14.0, D=26.0, plinth=("soco", 0.9),
               floors=[dict(h=11.0, front=["koshi", {"t": "shop", "w": 6.2}, "koshi"], left=["plaster", "shoji", "plaster"],
                            right=["plaster", "plaster", "plaster"], front_pent=dict(z=9.2, depth=2.8))],
               roof=dict(kind="kirizuma", ridge="y", pitch=0.62, over=3.0, g_over=2.2), chochin=[(0.0, 10.2)],
               gesture="empena para a rua"),
    # C5 - LOJA de 2 pisos com MUSHIKO-MADO e hisashi entre os pisos, kirizuma paralelo a rua. Gesto: fachada
    #      machiya (barras de reboco + treliça)
    "C5": dict(W=14.0, D=20.0, plinth=("soco", 0.9),
               floors=[dict(h=10.0, front=["shop", "lattice"], left=["plaster", "plaster"], right=["plaster", "shoji"]),
                       dict(h=7.8, front=["plaster", "mushiko", "plaster"], pent=True, left=["plaster", "plaster"],
                            right=["plaster", "plaster"])],
               roof=dict(kind="kirizuma", ridge="x", pitch=0.6, over=3.0, g_over=2.0), chochin=[(-3.2, 8.9)],
               gesture="mushiko + hisashi"),
    # C6 - CASA DE CHA larga (1 piso alto): KARAHAFU sobre a entrada aberta com noren, koshi dos lados, irimoya
    #      grande. Gesto: karahafu
    "C6": dict(W=18.0, D=28.0, plinth=("soco", 1.0),
               floors=[dict(h=12.5, front=["koshi", {"t": "open_door", "w": 6.6, "noren": INDIGO}, "koshi"],
                            left=["plaster", "round", "shoji", "plaster"], right=["plaster", "shoji", "shoji", "plaster"])],
               roof=dict(kind="irimoya", ridge="y", pitch=0.55, over=3.4), kara=dict(x=0.0, w=9.6, depth=2.6, z=9.9),
               chochin=[(-6.4, 9.4), (6.4, 9.4)], gesture="karahafu"),
    # ESQ - ESQUINA de 3 pisos escalonados: lojas na frente e no lado da rua lateral (R), SAIAS (mokoshi) entre os
    #       pisos, varanda vermelha no 3o, irimoya com chidori e onigawara DOURADA (edificio-marco)
    "ESQ": dict(W=16.0, D=22.0, plinth=("soco", 1.0), roof_m=RRED, side_lod=0,
                floors=[dict(h=10.5, front=["shop", "shop"], right=["shop", "lattice", "plaster"],
                             left=["plaster", "shoji", "plaster"]),
                        dict(h=8.4, setback=(1.6, 1.6, 1.6), skirt=True, front=["plaster", "shoji", "plaster"],
                             right=["plaster", "round", "plaster"]),
                        dict(h=7.6, setback=(3.2, 3.2, 3.2), skirt=True, front=["shoji", "shoji"],
                             balcony=dict(depth=2.0), right=["plaster", "shoji"])],
                roof=dict(kind="irimoya", ridge="x", pitch=0.58, over=3.0, chidori=dict(x=0.0, w=5.4), gold=True, courses=3),
                chochin=[(-4.2, 9.6), (4.2, 9.6)], gesture="esquina-marco"),
    # CASA - residencia terrea: reboco quente, porta de correr com noren, 2 koshi, irimoya baixo, hisashi
    "CASA": dict(W=18.0, D=16.0, plinth=("soco", 0.9), plaster=PLW,
                 floors=[dict(h=10.0, front=["koshi", {"t": "door", "noren": INDIGO}, "koshi"], front_pent=dict(z=9.0,
                              depth=2.4))],
                 roof=dict(kind="irimoya", ridge="x", pitch=0.52, over=3.0), gesture="residencia"),
}


def _faces(Fz, W, D):
    return {"F": ("front", sub(Fz, 0.0, D / 2), W, True), "B": ("back", sub(Fz, 0.0, -D / 2, 0.0, math.pi), W, True),
            "R": ("right", sub(Fz, W / 2, 0.0, 0.0, -math.pi / 2), D, False),
            "L": ("left", sub(Fz, -W / 2, 0.0, 0.0, math.pi / 2), D, False)}


def house(mb, F, spec, light_name=None, energy=70.0):
    """monta um edificio so com o kit. F no centro da planta, no chao; +y = frente. Ver DEFAULTS/PRESETS."""
    sp = dict(DEFAULTS)
    sp.update(spec)
    W, D = sp["W"], sp["D"]
    pst, ph = sp["plinth"]
    lod = sp["lod"]
    seed = sp.get("seed", 0) or int(_h01(F.o.x, F.o.y) * 9999)
    info = dict(floor_z=F.o.z + ph, glow=[], doors=[], front_y=D / 2)
    foundation(mb, F, W + 0.6, D + 0.6, ph, pst, lod, lod_faces="LR" if sp.get("side_lod", 1) else "")
    floors = sp["floors"]
    z = ph
    prev = (W, D, 0.0)                                            # (W, D, cy) do piso de baixo
    lit = sp["lit"]
    for k, fl in enumerate(floors):
        sf, sbk, ss = fl.get("setback", (0.0, 0.0, 0.0))
        Wk, Dk = W - 2 * ss, D - sf - sbk
        cy = (sbk - sf) / 2
        Fk = sub(F, 0.0, cy, z)
        h = fl["h"]
        pl = sp["plaster"] if k == 0 else sp["plaster_up"]
        corner_posts(mb, Fk, Wk, Dk, 0.7 if k == 0 else 0.0, h - 1.0, CP, lod)
        if k > 0:                                                 # assoalho/viga do piso
            bb(mb, Fk, -Wk / 2 + 0.6, Wk / 2 - 0.6, -Dk / 2 + 0.6, Dk / 2 - 0.6, -0.5, 0.05, WD)
        for key, (nm, Ff, Lf, full) in _faces(Fk, Wk, Dk).items():
            bays = fl.get(nm, "auto")
            if bays == "auto" or bays is None:
                bays = auto_bays(Lf, "back" if key == "B" else "side")
            lf = max(lod, sp["back_lod"]) if key == "B" else (max(lod, sp.get("side_lod", 1)) if key in "LR" else lod)
            r = facade(mb, Ff, Lf, h, bays, full, sp["door_w"], sp["door_h"] if k == 0 else 3.6, pl, lit, 0.9, lf,
                       sp["noren"], k == 0, seed * 7 + k * 4 + "FBRL".index(key), k == 0, 5.2 if k == 0 else 2.2)
            info["glow"] += r["glow"]
            info["doors"] += r["doors"]
        if k > 0:
            Wp, Dp, cyp = prev
            front_lower = cyp + Dp / 2
            if fl.get("skirt"):
                dep = max(1.6, (Dp - Dk) / 2 + 1.8)
                roof_skirt(mb, Fk, Wk, Dk, dep, 1.2, 0.45, 0.42, 0.5, sp["roof_m"], lod)
            elif fl.get("balcony"):
                bd = fl["balcony"].get("depth", 2.4)
                Ffb = sub(Fk, 0.0, Dk / 2)
                balcony(mb, Ffb, -Wk / 2 + 0.6, Wk / 2 - 0.6, bd, 0.7, 3.4, lod)
            elif fl.get("pent", True):
                roof_pent(mb, sub(F, 0.0, front_lower, z), Wp + 1.2, 2.8, 1.45, 0.42, 0.42, 0.4, lod, "brackets")
                if lod == 0 and sp["back_lod"] == 0:
                    roof_pent(mb, sub(F, 0.0, cyp - Dp / 2, z, math.pi), Wp + 1.2, 2.8, 1.45, 0.42, 0.42, 0.4, 1, "brackets")
        fp = fl.get("front_pent")
        if fp:
            X_ = (Wk + 1.0) / 2
            roof_pent(mb, sub(Fk, 0.0, Dk / 2), Wk + 1.0, fp.get("depth", 2.8), fp.get("z", h - 1.8), 0.42, 0.42, 0.4,
                      lod, "brackets", xs=[-X_ + 0.6, X_ - 0.6])
        prev = (Wk, Dk, cy)
        z += h
        last = (Fk, Wk, Dk, h, cy)
    Fk, Wk, Dk, h, cy = last
    rf = dict(ROOF_DEF)
    rf.update(sp["roof"])
    along_x = rf["ridge"] == "x"
    Fb_top = sub(Fk)                                              # base do ultimo piso
    Fr, Wr, Dr = (Fb_top, Wk, Dk) if along_x else (sub(Fb_top, ang=math.pi / 2), Dk, Wk)
    gm = sp["plaster_up"] if len(floors) > 1 else sp["plaster"]
    if rf["kind"] == "kirizuma":
        r = roof_gable(mb, Fr, Wr, Dr, h, rf["pitch"], rf["over"], rf["g_over"], rf["lift"] * 0.6, rf["tv"], lod, gm,
                       rf["gable_style"], True, sp["roof_m"], back_lod=sp["back_lod"] if along_x else None,
                       gold=rf["gold"], courses=rf["courses"])
    else:
        r = roof_hip(mb, Fr, Wr, Dr, h, rf["kind"], rf["pitch"], rf["over"], rf["gable"], rf["g_over"], rf["lift"],
                     rf["tv"], lod, gm, rf["gable_style"], True, sp["roof_m"], rf["steep"],
                     sp["back_lod"] if along_x else None, rf["chidori"] if along_x else None, rf["gold"], rf["courses"],
                     auto_rot=False)
    info.update(top_z=Fr.o.z + r["top"], ridge_z=Fr.o.z + r["zr"], eave_z=Fr.o.z + r["eave_z"], roof=r)
    Fb = sub(F, z=ph)
    Ff0 = sub(Fb, 0.0, D / 2)
    if sp.get("kara"):
        kd = sp["kara"]
        rk = roof_kara(mb, sub(Ff0, kd.get("x", 0.0)), kd["w"], kd.get("depth", 2.6), kd.get("z", floors[0]["h"]), 0.3,
                       1.5, 0.45, sp["roof_m"], rf["gold"])
    for i, (x, zz) in enumerate(sp.get("chochin", ())):
        lantern_wall(mb, sub(Ff0, x, 0.15, zz), None, 0.0, 1.25)
    if light_name and info["glow"]:
        g = info["glow"][len(info["glow"]) // 2]
        light(light_name, "POINT", g, energy, WARM, 0.4)
    info["light_at"] = info["glow"][len(info["glow"]) // 2] if info["glow"] else None
    return info


def house_height(spec):
    sp = dict(DEFAULTS)
    sp.update(spec)
    return sp["plinth"][1] + sum(f["h"] for f in sp["floors"])


def house_cols(area, F, spec):
    """colisao simplificada de um edificio do kit: soco + corpo de cada piso (fachadas cenograficas fechadas: o balcao
    da loja fica na linha da fachada). Usa fm_lib.col_box (Parts invisiveis no Roblox)."""
    sp = dict(DEFAULTS)
    sp.update(spec)
    W, D = sp["W"], sp["D"]
    ph = sp["plinth"][1]
    z = ph
    col_box(area, (W + 0.6, D + 0.6, ph + 0.3), F.p(0, 0, (ph - 0.3) / 2), F.r())
    for k, fl in enumerate(sp["floors"]):
        sf, sbk, ss = fl.get("setback", (0.0, 0.0, 0.0))
        Wk, Dk = W - 2 * ss, D - sf - sbk
        cy = (sbk - sf) / 2
        col_box(area, (Wk, Dk, fl["h"]), F.p(0, cy, z + fl["h"] / 2), F.r())
        z += fl["h"]


# ================================================================== CORTE DE FACES ESCONDIDAS (M6b, orcamento)
def cull_hidden(mb, dmax=2.5, eps=0.004, frac=0.94):
    """apaga do bmesh do MB (ANTES do finish) as faces que NINGUEM ve: (a) face encostada (< 2 eps) numa face voltada
    para ela (fundo de pilar sobre a soleira, pontas de lajes/blocos colados) ou (b) face DENTRO de outro volume do
    mesmo objeto (o raio pela normal sai do volume por uma face de mesma orientacao a <= dmax: fundo do pilar dentro
    do reboco). Testa o centro e os vertices puxados 'frac' para o centro: so apaga se TODOS os raios confirmam (face
    parcialmente coberta fica). Frestas (face voltada para nos a mais de 2 eps) nunca sao apagadas. Devolve os tris
    cortados. Nao muda nada que apareca: so 'pagar com cortes onde nao se ve' (FINESSE_BRIEF)."""
    from mathutils.bvhtree import BVHTree
    bm = mb.bm
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    bm.normal_update()
    bm.faces.ensure_lookup_table()
    # M6c (determinismo): a ORDEM das faces no bmesh muda de um build para outro (mesma geometria, mesmas normais) e a
    # BVH desempata pela ordem -> 2 builds iguais cortavam 1..11 faces diferentes. A arvore agora e montada com as
    # faces em ordem GEOMETRICA (centro, normal) e cada poligono comecando no menor vertice (mesmo sentido)
    def _gkey(f):
        c = f.calc_center_median()
        return (round(c.x, 4), round(c.y, 4), round(c.z, 4), round(f.normal.x, 3), round(f.normal.y, 3),
                round(f.normal.z, 3), len(f.verts))
    order = sorted(bm.faces, key=_gkey)
    tv, tp, t2f = [], [], []
    for f in order:
        cs = [v.co.copy() for v in f.verts]
        k0 = min(range(len(cs)), key=lambda i: (round(cs[i].x, 4), round(cs[i].y, 4), round(cs[i].z, 4)))
        cs = cs[k0:] + cs[:k0]
        tp.append(list(range(len(tv), len(tv) + len(cs))))
        tv += cs
        t2f.append(f.index)
    tree = BVHTree.FromPolygons(tv, tp)
    kill = []
    for f in bm.faces:
        n = f.normal
        if n.length < 0.5:
            continue
        c = f.calc_center_median()
        pts = [c] + [c + (v.co - c) * frac for v in f.verts]
        # M6c: + meios das arestas e meio caminho centro-vertice: com so centro + vertices a empena atras das ripas
        # (kitsure/trelica) caia inteira 'dentro' das ripas e era cortada -> via-se o avesso do timpano entre as ripas
        vs_ = [v.co for v in f.verts]
        pts += [c + ((vs_[i] + vs_[(i + 1) % len(vs_)]) / 2 - c) * frac for i in range(len(vs_))]
        pts += [c + (v_ - c) * 0.5 for v_ in vs_]
        # M6c (determinismo): desvio fixo e minusculo no plano da face (da propria geometria, nao do indice): o raio
        # nunca passa exatamente numa aresta/vertice de outra face. Antes o empate entre 2 faces na mesma distancia era
        # decidido pela ordem das faces na BVH e 2 builds iguais cortavam 1..11 faces diferentes
        t1 = (vs_[1] - vs_[0])
        if t1.length > 1e-6:
            t1 = t1.normalized()
            t2 = n.cross(t1)
            dj = t1 * 0.00131 + t2 * 0.00217
            pts = [p + dj for p in pts]
        ok = True
        for p in pts:
            hit = tree.ray_cast(p + n * eps, n, dmax)
            if hit[0] is None or t2f[hit[2]] == f.index:
                ok = False
                break
            if hit[1].dot(n) < 0.0 and hit[3] > 2 * eps:
                ok = False
                break
        if ok:
            kill.append(f)
    tris = sum(len(f.verts) - 2 for f in kill)
    if kill:
        bmesh.ops.delete(bm, geom=kill, context="FACES")
    return tris


# ================================================================== ESTUDIO (folhas de close-up; fora do jogo)
def _tris(ob):
    return sum(len(p.vertices) - 2 for p in ob.data.polygons) if ob and ob.type == "MESH" else 0


def _studio_pieces():
    """(nome, construtor(mb, F) -> dict(focus=(x,y,z) local, size=(w,h), dummy=(x,y) local, view=(lado, alto)))
    F de cada peca: +y local aponta para a camera"""
    P = []

    def add(name, fn):
        P.append((name, fn))

    def wall_house(mb, F, bays, L, **kw):
        spec = dict(W=L, D=8.0, plinth=("soco", 0.9), floors=[dict(h=10.5, front=bays, back=["plaster"],
                                                                    left=["plaster"], right=["plaster"])],
                    roof=dict(kind="kirizuma", ridge="x", pitch=0.6, over=3.0, g_over=1.8))
        spec.update(kw)
        return house(mb, F, spec)

    for k in ("C1", "C2", "C5", "C6", "ESQ", "CASA"):
        def f(mb, F, k=k):
            sp = PRESETS[k]
            house(mb, F, sp, "L_OPKit_House_%s" % k)
            hh = house_height(sp) + 9.0
            Wd = max(sp["W"], sp["D"] * 0.6) + 8.0
            return dict(focus=(0, 0, hh * 0.45), size=(Wd * 1.4, hh * 1.3), dummy=(-sp["W"] * 0.3, sp["D"] / 2 + 4.5),
                        view=(1.1, 0.45))
        add("0%d_familia_%s" % ("C1 C2 C5 C6 ESQ CASA".split().index(k) + 1, k), f)

    def p_pav(mb, F):
        pavilion(mb, F, 14.0, 11.0, 8.5, "irimoya", True)
        return dict(focus=(0, 0, 7.0), size=(26.0, 19.0), dummy=(-5.0, 9.0), view=(1.1, 0.4))
    add("07_familia_pavilhao", p_pav)

    def p_front(k, foc, size, view=(0.7, 0.15), dummy=None):
        def f(mb, F):
            sp = PRESETS[k]
            house(mb, F, sp)
            return dict(focus=foc(sp), size=size, dummy=dummy or (-2.5, sp["D"] / 2 + 3.0), view=view)
        return f
    add("10_loja_balcao_noren_close", p_front("C1", lambda sp: (3.0, sp["D"] / 2 + 1.0, sp["plinth"][1] + 4.5),
                                              (12.0, 9.5), (0.5, 0.08)))
    add("11_varanda_vermelha_close", p_front("C1", lambda sp: (4.0, sp["D"] / 2 + 1.0, sp["plinth"][1] + 13.2),
                                             (10.0, 6.0), (1.0, 0.3)))
    add("12_chidori_hafu_close", p_front("C1", lambda sp: (0.0, sp["D"] / 2, sp["plinth"][1] + 22.6), (13.0, 7.5),
                                         (0.6, 0.6)))
    add("13_karahafu_close", p_front("C6", lambda sp: (0.0, sp["D"] / 2 + 1.5, sp["plinth"][1] + 10.6), (12.0, 7.0),
                                     (0.7, 0.2)))
    add("14_mushiko_hisashi_close", p_front("C5", lambda sp: (0.0, sp["D"] / 2 + 1.0, sp["plinth"][1] + 12.4),
                                            (12.0, 7.5), (0.8, 0.15)))
    add("15_empena_tsumairi", p_front("C2", lambda sp: (0.0, sp["D"] / 2, sp["plinth"][1] + 14.0), (20.0, 12.5),
                                      (0.6, 0.25)))

    def p_roofcorner(mb, F):
        info = house(mb, F, PRESETS["C1"])
        r = info["roof"]
        z0 = info["floor_z"] - F.o.z + 10.5
        return dict(focus=(r["Xe"] - 1.0, r["Ye"] - 1.0, z0 + r["zw"] - 1.0), size=(10.0, 6.0), dummy=(-2.5, 14.0),
                    view=(1.2, -0.25))
    add("16_beiral_grosso_quina", p_roofcorner)

    def p_ridge(mb, F):
        info = house(mb, F, PRESETS["ESQ"])
        return dict(focus=(4.5, 0.0, info["ridge_z"] - F.o.z + 1.0), size=(9.0, 5.0), dummy=(-2.5, 14.0), view=(1.6, 0.5))
    add("17_cumeeira_onigawara_dourada", p_ridge)

    def p_wall(mb, F):
        wall_house(mb, F, ["plain", "koshi", "plaster", "round", "plain"], 26.0)
        return dict(focus=(0, 4.0, 6.0), size=(24.0, 13.0), dummy=(-1.0, 6.0), view=(0.5, 0.1))
    add("18_parede_reboco_janelas", p_wall)

    def p_win(kind, zf=7.0):
        def f(mb, F):
            wall_house(mb, F, ["plain", kind, "plain"], 15.0)
            return dict(focus=(0, 4.0, zf), size=(8.0, 6.0), dummy=(-4.2, 6.0), view=(0.7, 0.05))
        return f
    add("19_janela_koshi_close", p_win("koshi", 4.6))
    add("20_janela_redonda_close", p_win("round", 6.4))
    add("21_porta_noren_close", p_win({"t": "door", "noren": INDIGO, "lit": True}, 5.6))
    add("22_saia_mokoshi_esquina", p_front("ESQ", lambda sp: (sp["W"] / 2 - 1.0, sp["D"] / 2 - 1.0,
                                                             sp["plinth"][1] + 12.0), (14.0, 10.0), (1.4, 0.35)))

    def p_stair(mb, F):
        stair_stone(mb, sub(F, 0, 5.0, 0.0, math.pi), 10.0, 6, 0.667, 1.8, z_off=0.15)
        bb(mb, F, -7.0, 7.0, -14.0, -5.8, -0.3, 4.15, STZ)
        return dict(focus=(0, -1.0, 2.3), size=(18.0, 9.0), dummy=(-3.5, 6.4), view=(1.0, 0.55))
    add("23_escada_pedra", p_stair)

    def p_pave(mb, F):
        o = F.o
        reg = [(o.x - 10, o.y - 8), (o.x + 10, o.y - 8), (o.x + 10, o.y + 8), (o.x - 10, o.y + 8)]
        pave(mb, reg, o.x - 10, o.x + 10, o.y - 8, o.y + 2, ((2.8,), 2.6, 4.2), STP, 0.15, key="k1",
             mats=[(STP, 6), (STZ, 2)])
        pave(mb, reg, o.x - 10, o.x + 10, o.y + 2, o.y + 3.2, ((1.2,), 3.2, 4.6), ST, 0.15, key="k2")
        pave(mb, reg, o.x - 10, o.x + 10, o.y + 3.2, o.y + 8, ((2.2,), 2.4, 3.2), STZ, 0.15, key="k3")
        return dict(focus=(0, 0, 0.0), size=(16.0, 8.0), dummy=(2.0, 1.0), view=(0.4, 1.1))
    add("24_piso_lajes_junta", p_pave)

    def p_parapet(mb, F):
        bb(mb, F, -9.0, 9.0, -3.0, 3.0, -0.3, 0.0, STZ)
        parapet(mb, F, 16.0, 2.4)
        return dict(focus=(0, 0.0, 1.4), size=(17.0, 6.0), dummy=(-2.0, 2.4), view=(0.6, 0.3))
    add("25_mureta_cantaria", p_parapet)

    def p_wall_rw(mb, F):
        bb(mb, F, -9.0, 9.0, -6.0, 0.0, 3.85, 4.15, STZ)
        retaining_wall(mb, sub(F, 0.0, 0.0, 4.15), 18.0, 4.15, 6.0, cap=True)
        parapet(mb, sub(F, 0.0, -1.0, 4.15), 18.0, 2.3)
        return dict(focus=(0, 0.0, 3.2), size=(17.0, 8.0), dummy=(-2.0, 2.4), view=(0.6, 0.15))
    add("25b_arrimo_com_mureta", p_wall_rw)

    def p_rail(mb, F):
        bb(mb, F, -8.0, 8.0, -3.0, 3.0, -0.3, 0.0, WM)
        red_rail(mb, F, [(7.5, -2.5), (7.5, 2.5), (-7.5, 2.5), (-7.5, -2.5)], 3.6, 0.0)
        return dict(focus=(0, 0.0, 2.0), size=(18.0, 8.0), dummy=(0.0, -1.0), view=(0.6, 0.6))
    add("26_guarda_corpo_vermelho", p_rail)

    def p_lpost(mb, F):
        lantern_post(mb, F, 9.0, 1.7, "L_OPKit_LampPost", 40.0)
        return dict(focus=(0, 0.0, 5.2), size=(7.0, 11.0), dummy=(-2.0, -1.6), view=(0.3, 0.1))
    add("27_lanterna_poste_chochin", p_lpost)

    def p_lpost_close(mb, F):
        lantern_post(mb, F, 9.0, 1.7, "L_OPKit_LampPost2", 40.0)
        return dict(focus=(1.7, 0.0, 6.4), size=(3.4, 3.4), dummy=(-2.0, -1.6), view=(0.5, 0.1))
    add("28_chochin_close", p_lpost_close)

    def p_box(mb, F):
        lantern_box_post(mb, F, 7.6, "L_OPKit_Box", 35.0)
        return dict(focus=(0, 0.0, 4.0), size=(5.5, 8.5), dummy=(-1.8, -1.4), view=(1.0, 0.1))
    add("29_lanterna_andon", p_box)

    def p_lwall(mb, F):
        wall_house(mb, F, ["plain", "plaster", "plain"], 14.0)
        lantern_wall(mb, sub(F, 0.0, 4.0, 0.9 + 7.2), "L_OPKit_LampWall", 25.0)
        return dict(focus=(0, 5.0, 7.4), size=(4.6, 3.8), dummy=(-2.6, 6.0), view=(1.4, 0.05))
    add("30_lanterna_parede", p_lwall)

    def p_toro(mb, F):
        toro(mb, F, 1.0, "L_OPKit_Toro", 35.0)
        return dict(focus=(-0.6, 0, 3.6), size=(8.0, 8.4), dummy=(-3.2, -1.2), view=(1.0, 0.3))
    add("31_toro_pedra", p_toro)

    def p_banner(mb, F):
        banner(mb, F, 16.0)
        return dict(focus=(1.4, 0.0, 8.0), size=(10.0, 17.5), dummy=(-1.8, -1.6), view=(0.3, 0.15))
    add("32_estandarte_suporte", p_banner)

    def p_banner_close(mb, F):
        banner(mb, F, 16.0)
        return dict(focus=(0.3, 0.0, 1.3), size=(4.0, 3.0), dummy=(-1.8, -1.6), view=(0.8, 0.5))
    add("33_estandarte_base_close", p_banner_close)

    def p_goods(mb, F):
        bb(mb, F, -4.0, 4.0, -2.0, 2.0, -0.3, 0.0, STZ)
        jar(mb, F, -2.6, 0.0, 0.0, 0.6, 1.4)
        jar(mb, F, -1.2, 0.6, 0.0, 0.45, 1.0, PL, True)
        barrel(mb, F, 0.4, 0.0, 0.0)
        crate(mb, F, 2.4, 0.2, 0.0, 1.4, 1.0, 0.9, 0.2)
        bolts(mb, F, 2.4, 0.2, 0.9, 3, (CRED, INDIGO, CWHITE), 0.26, 1.2)
        bench(mb, F, 0.0, -1.4, 4.4, 1.2, 1.6)
        return dict(focus=(0, 0.0, 0.9), size=(8.0, 3.6), dummy=(-3.8, -1.6), view=(0.5, 0.4))
    add("34_mercadoria_banco", p_goods)
    return P


def studio(out, only=()):
    import op_scene
    os.makedirs(out, exist_ok=True)
    DL.reset_scene()
    fm_lib.make_materials()
    op_scene.setup(res=(960, 540), samples=16)
    pieces = _studio_pieces()
    if only:
        pieces = [p for p in pieces if any(o in p[0] for o in only)]
    gm = MB("STUDIO_Ground", "00_REFERENCE", detail="far", floor=-999)
    gm.box((150.0 * (len(pieces) + 2), 260.0, 1.0), (75.0 * len(pieces), 0.0, -0.5), (0, 0, 0), "Grass_OP", 0.0)
    gm.finish()
    cams = []
    report = []
    for i, (name, fn) in enumerate(pieces):
        X = i * 150.0
        F = Frame(X, 0.0, 0.0, math.pi)
        mb = MB("OP_Kit_" + name, "05_CAPITAL")
        r = fn(mb, F)
        ob = mb.finish()
        report.append((name, _tris(ob), len(ob.data.materials) if ob else 0))
        dx, dy = r["dummy"]
        DL.dummy("SCALE_Dummy_" + name, *F.p(dx, dy, 0.0).to_tuple()[:2], 0.0, F.a + math.pi)
        fx, fy, fz = r["focus"]
        tgt = F.p(fx, fy, fz)
        vx, vz = r.get("view", (0.45, 0.3))
        d = Vector((-vx * 0.42, -1.0, vz * 0.42 + 0.12)).normalized()     # F.a = pi: local +y = mundo -y
        fov = 2 * math.atan(18.0 / 35.0)
        w, hgt = r["size"]
        dist = max(w, hgt * 16.0 / 9.0) * 0.5 / math.tan(fov / 2) * 1.12
        cn = "CAM_OPK_" + name
        fm_lib.camera(cn, tgt + d * dist, tgt, 35)
        cams.append(cn)
    fm_lib.make_materials()
    op_scene.tone_emissives()
    for o in bpy.data.objects:
        if o.type == "LIGHT" and o.name.startswith("L_OPKit"):
            o.data.use_shadow = False
    sc = bpy.context.scene
    sc.render.image_settings.file_format = "JPEG"
    sc.render.image_settings.quality = 88
    print("KIT tris por peca:")
    for name, t, nm in report:
        print("KIT %-34s tris=%6d materiais=%d" % (name, t, nm))
    if "--no-render" in sys.argv:
        return
    for mode, sub_ in (("rico", "previa"), ("roblox", "roblox")):
        if mode == "roblox":
            fm_lib.apply_preview("roblox")
            op_scene.tone_emissives()
        od = os.path.join(out, sub_)
        os.makedirs(od, exist_ok=True)
        for cn in cams:
            sc.camera = bpy.data.objects[cn]
            sc.render.filepath = os.path.join(od, cn + ".jpg")
            bpy.ops.render.render(write_still=True)
            print("KIT RENDER", mode, cn)


if __name__ == "__main__":
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    pos = [a for a in argv if not a.startswith("--")]
    out = pos[0] if pos else os.path.join(HERE, "renders", "m2", "kit")
    studio(out, pos[1:])
