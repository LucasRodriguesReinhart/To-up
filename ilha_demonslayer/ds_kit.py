# ds_kit.py - KIT ARQUITETONICO da Ilha 4 (DEMON SLAYER), onda 1b. Vila japonesa da era Taisho: madeira escura
# aparente, reboco claro RECUADO entre pilares e vigas, telha escura azul-ardosia em canais, soco de pedra.
# Escopo: PLANO_DS secao 8 + PROMPT_USUARIO secoes 10, 20, 21 e 22. So geometria VISUAL (a colisao andavel e do
# ds_col / de quem monta; ha um ajudante house_cols() opcional). Nao e modulo de zona: build_ds nao o chama; a vila
# (ds_village, onda 2a) e a forja (ds_forge, onda 2b) importam e chamam as funcoes abaixo.
#
# ============================================================ CONVENCOES
#   F       fm_parts.Frame(ox, oy, oz, ang) - referencial LOCAL da peca. Casas e pecas soltas: origem no CENTRO DA
#           PLANTA, NO CHAO (z=0 = terreno), +y = FRENTE (rua), +x ao longo da frente, z para cima.
#           Faces de parede (Ff): origem no meio da fachada, z=0 no topo do soco (= piso), y=0 na FACE EXTERNA DOS
#           PILARES, +y para fora. (Ff local +x corre para a ESQUERDA de quem olha de fora; as listas de vaos sao
#           lidas da esquerda para a direita de quem olha de fora - o kit inverte por dentro.)
#   mb      fm_lib.MB do chamador: o kit desenha DENTRO do MB que voce passar (1 MB por casa = poucas MeshParts:
#           1 por material). Nomeie o MB com o prefixo do dono (DS_Vil_*, DS_Frg_*, DS_Prop_*...).
#   sub(F, x, y, z, ang)  referencial filho (para posicionar pecas dentro de outra).
#   Escala: avatar 5. Porta 5,6 x 8,4 (entravel 8 x 11), degrau <= 0,8, guarda-corpo 4, pe-direito da casa 12,5.
#   Z-fight: nenhuma face visivel coplanar; papel/luz >= 0,12 atras da grade/moldura; pecas sobrepostas entram
#   >= 0,04 umas nas outras. Bevel unico 0,08-0,12 nas pecas estruturais (B).
#   Materiais: so DSMATS (ds_lib) + 3 novos (Plaster_DS_Ochre / Plaster_DS_Ash = tom da casa, Plaster_DS_Shoji =
#   papel apagado). Luz quente SO dentro de moldura (Window_DS_Warm no shoji recuado; Glass_DS_Lantern na camara).
#
# ============================================================ API (o que a onda 2 chama)
# CASA INTEIRA
#   house(mb, F, spec, light_name=None, energy=80.0) -> info
#       spec = dict (ver DEFAULTS) ou um PRESETS["V1".."V6"] (copie e ajuste: dict(PRESETS["V2"], W=20.0)).
#       Chaves: W (frente, x) D (fundo, y) h (pe-direito ate o topo da viga de beiral) plinth=("ishigaki"|"soco"|
#       "none", altura) roof="irimoya"|"kirizuma"|"yosemune" ridge="long"|"x"|"y" pitch over gable g_over lift
#       front/back/left/right = lista de vaos (ver VAOS) ou "auto"; door_w door_h; plaster="base"|"ochre"|"ash"|
#       "kura"; engawa=lista de lados ("F","R","B","L"); engawa_d; stories=1|2; upper=dict(h, front, back, left,
#       right, balcony=True|False); kura=True (armazem); lit=True|False|lista de lados acesos; noren=True|material;
#       lod=0 (heroi) | 1 (fundo: sem caibros, menos canais); back_lod=1 (fundos simplificados); steps=True.
#       Tambem: steep (irimoya: caimento de cima = pitch * steep, padrao 1,5), hisashi_front + hisashi_z (beiral
#       intermediario na frente), benches=((x, y, comprimento, rumo), ...) (bancos internos), gable_style.
#       info = dict(floor_z, top_z, ridge_z, eave_z, glow=[pontos mundo p/ luz], doors=[(centro mundo, yaw)],
#                   footprint=(w, d) com o soco, roof=dict(zr, zb, zw, Xe, Ye, xg, yb...) no referencial do telhado,
#                   light_at=ponto mundo da luz da casa)
#       Orcamento medido (tris / materiais = MeshParts): V1 8,9k/10  V2 15,3k/12  V3 10,1k/12  V4 13,4k/11
#       V5 20,9k/12  V6 18,7k/11 -> 87k das 110k da vila. lod=1 (casa de fundo) corta ~30% (canais e caibros).
#   house_cols(area, F, spec, info=None)  colisao simplificada (soco + corpo; porta aberta vira vao) via col_box
#   PRESETS = V1 chaya aberta | V2 minka terrea | V3 oficina (frente de loja) | V4 kura (torre branca) |
#             V5 sobrado com sacada | V6 casa principal (porta 8 x 11, engawa em L) - variacoes dirigidas
# VAOS (itens das listas front/back/...: string ou dict {"t": tipo, "w": largura, "lit": bool, "hood": bool})
#   "plain" tabuas + reboco | "plaster" so reboco | "koshi" janela baixa de trelica | "shoji" janela alta com capelo
#   opcional | "lattice" trelica de rua (demaregoshi) | "door" porta de correr (hikido) | "itado" porta de tabuas |
#   "open_door" vao de porta livre (casa entravel) | "open" vao aberto (pavilhao) | "shop" frente de loja (shitomi
#   erguido + agebutai)
# PECAS-BASE (todas: mb, F, ... ; F na base da peca)
#   foundation(mb, F, W, D, h, style="ishigaki"|"soco", batter=8.0, lod=0, sides="FBLR")
#   facade(mb, Ff, L, h, bays, full=True, door_w, door_h, plaster, lit, ext, lod, ground, noren) -> dict
#   corner_posts(mb, Fb, W, D, z0, z1)
#   post(mb, F, x, y, z0, z1, s=0.9, base=True)        pilar chanfrado sobre pedra (soseki)
#   beam(mb, F, a, b, w, h, m=WD)                       viga entre 2 pontos locais
#   bracket(mb, F, x, y, z, L, w=0.5, h=0.9)            misula/consolo (funa-hijiki) saindo para +y
#   bench(mb, F, x, y, L=5.0, w=2.0, h=1.7, ang=0.0, z=0.0)   banco de casa de cha (shogi)
#   rock_base(mb, F, x, y, z, r=0.8, hgt=0.45)           pedra-base natural (soseki / tsuka-ishi)
#   boards(mb, Ff, a, b, z0, z1)                         rodape de tabuas (koshi-ita) com mata-juntas
#   panel(mb, Ff, x0, x1, z0, z1, y0, y1, holes, m)      placa com vaos retangulares
#   window(mb, Ff, s, z, w, h, kind="koshi"|"shoji"|"lattice", lit=True, hood=False, sill=True) -> ponto de luz
#   door(mb, Ff, s, w, h, kind="hikido"|"itado"|"open", lit=False, noren=None) -> dict
#   kura_body(mb, F, W, D, h, ...), kura_window(mb, Ff, s, z, w, h, ...), kura_door(mb, Ff, s, w, h, ...)
#   roof_hip(mb, F, W, D, h, kind="irimoya"|"yosemune", pitch, over, gable, g_over, lift, tv, lod, gable_m,
#            gable_style="timber"|"board", rafters, m, steep=1.5, back_lod=None)
#            -> dict(zr, zb, zw, eave_z, Xe, Ye, xg, yb, go, top)                 (cumeeira ao longo do MAIOR lado)
#            irimoya em 2 caimentos (empena mais inclinada: perfil concavo japones), beiral que chuta (p2 = p/2),
#            cantos levantados (lift); back_lod: a agua de -y com menos canais e sem caibros
#   roof_gable(mb, F, W, D, h, pitch, over, g_over, lift, tv, lod, gable_m, gable_style="timber"|"kura"|"none",
#              ridge_w=2.0, oni_s=1.0) -> dict                                    (kirizuma; cumeeira ao longo de x)
#   roof_pent(mb, Ff, L, depth, z_top, pitch, tv, lift, lod, support="brackets"|"braces"|"none") (hisashi/capelo)
#   ridge(mb, F, x0, x1, zr, pitch, w=2.0, oni=True, s=1.0) / onigawara(mb, F, x, zr, sx, s=1.0)
#   engawa(mb, Ff, x0, x1, depth, ground, z=0.35, step_x=None, posts=True)
#   steps_to(mb, Ff, x, y0, z_top, z_ground, w=3.6)     pedras de degrau naturais (kutsunugi-ishi)
#   stair_stone(mb, F, w, n, rise=0.75, tread=1.9, cheeks=True)   escada de pedra (focinho chanfrado, espelho escuro)
#   stair_wood(mb, F, w, n, rise=0.75, tread=1.4, rail=True)      escada de madeira com banzos e corrimao
#   railing(mb, F, pts, h=4.0, base=0.0)                guarda-corpo de madeira ao longo de pontos (x, y) locais
#   fence(mb, F, pts, h=3.2, style="ripa"|"bamboo")     cerca baixa (ripas com mouroes / bambu yotsume-gaki)
#   balcony(mb, Ff, x0, x1, depth, z)                   sacada em consolos com guarda-corpo
#   garden_wall(mb, F, L, h=6.0, th=1.2)                muro de jardim (tsuiji) com cobertura de telha; ao longo de x
#   gate_mon(mb, F, w=8.5, h=9.5, depth=3.2, open_=True)  portao de cumeeira (munamon), +y = rua. Pilares de 1,3:
#            o muro encosta na face externa do pilar (centro do muro em x = +-(w/2 + 0.55 + 0.65 + L/2))
# LANTERNAS (luz SO dentro da camara; light_name cria um POINT no centro da camara)
#   lantern_post(mb, F, h=8.6, arm=1.9, light_name=None, energy=40.0)   poste de madeira + braco + caixa de papel
#   lantern_wall(mb, F, light_name=None, energy=30.0, out=1.3)           F na face da parede (+y fora), z = suporte
#   toro(mb, F, style="kasuga"|"yukimi"|"oki", s=1.0, light_name=None, energy=35.0)   lanterna de pedra (pedestal)
# MUDANCAS DA ONDA 2a (dono do kit = 2a; API intacta):
#   - roof_hip: a tabeira (hafu) da empena irimoya termina acima da agua de topo medida na face INTERNA dela e acima dos
#     canais (antes a ponta furava a telha perto do pe da empena: o "bloquinho" do close da cumeeira);
#   - noren_cloth(mb, Ff, x0, x1, zt, ln, noren) extraido de door(); o vao "open" agora honra {"noren": True} (o preset
#     V1 ja pedia e nao saia);
#   - MIN_BEVEL / MIN_BEVEL_SIZE (padrao 0 = sem mudanca): opt-in de quem chama para zerar chanfros < MIN_BEVEL e de
#     pecas com menor dimensao < MIN_BEVEL_SIZE (a vila usa 0,07 / 0,5 durante o build: ~-20% de tris na madeira).
# ESTUDIO (folhas de close-up, fora do jogo):
#   blender -b --factory-startup --python ds_kit.py -- <pasta_saida> [peca ...]   (previa + roblox, 960 x 540)
import math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import ds_lib as DL
import bpy, bmesh
from mathutils import Vector
from ds_lib import MB, Frame, light, col_box, fm_lib

# ------------------------------------------------------------------ materiais (DSMATS) e constantes
WD, WM = "Wood_DS_Dark", "Wood_DS_Mid"
PL, PLK = "Plaster_DS", "Plaster_DS_Kura"
RT, RR = "Roof_DS_Tile", "Roof_DS_Ridge"
ST, STD, STP = "Stone_DS", "Stone_DS_Dark", "Stone_DS_Path"
IRON = "Metal_DS_Iron"
LIT, PAPER = "Window_DS_Warm", "Plaster_DS_Shoji"
LGLOW = "Glass_DS_Lantern"
CLOTH = "Cloth_DS_Indigo"
BAMBOO, BAMBOO_G = "Bamboo_DS_Dry", "Bamboo_DS"
PLASTER_TONES = {"base": PL, "ochre": "Plaster_DS_Ochre", "ash": "Plaster_DS_Ash", "kura": PLK}
WARM = (1.0, 0.64, 0.34)
B = 0.1             # bevel unico das pecas estruturais
CP, IP = 1.0, 0.8   # pilar de canto / intermediario (secao)
KH = 2.6            # topo do rodape de tabuas
SILL = 0.9          # topo da soleira (shikii) = piso interno
DOOR_W, DOOR_H = 5.6, 8.4


# ------------------------------------------------------------------ geometria basica
def sub(F, x=0.0, y=0.0, z=0.0, ang=0.0):
    p = F.p(x, y, z)
    return Frame(p.x, p.y, p.z, F.a + ang)


MIN_BEVEL = 0.0     # (2a) chanfro minimo: bev abaixo disto vira 0 (opt-in por quem chama; 0 = comportamento original)
MIN_BEVEL_SIZE = 0.0  # (2a) e pecas cuja MENOR dimensao fica abaixo disto tambem saem sem chanfro


def bx(mb, F, x, y, z, sx, sy, sz, m, bev=0.0, rx=0.0, ry=0.0, rz=0.0):
    if sx <= 1e-3 or sy <= 1e-3 or sz <= 1e-3:
        return
    if bev and (bev < MIN_BEVEL or min(sx, sy, sz) < MIN_BEVEL_SIZE):
        bev = 0.0
    mb.box((sx, sy, sz), F.p(x, y, z), F.r(rx, ry, rz), m, bev)


def bb(mb, F, x0, x1, y0, y1, z0, z1, m, bev=0.0):
    x0, x1 = min(x0, x1), max(x0, x1)
    y0, y1 = min(y0, y1), max(y0, y1)
    z0, z1 = min(z0, z1), max(z0, z1)
    bx(mb, F, (x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2, x1 - x0, y1 - y0, z1 - z0, m, bev)


def loft(mb, F, rings, m, closed=True, caps=(True, True), bev=0.0, tint=None):
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
    return mb._post([v for r in V for v in r], m, tint, bev, 1)


def ext(mb, F, poly, axis, a0, a1, m, bev=0.0):
    """prisma: poligono 2D no plano perpendicular a 'axis', extrudado de a0 a a1 ('x': (y,z); 'y': (x,z); 'z': (x,y))"""
    if axis == "x":
        R = lambda a: [(a, u, v) for u, v in poly]
    elif axis == "y":
        R = lambda a: [(u, a, v) for u, v in poly]
    else:
        R = lambda a: [(u, v, a) for u, v in poly]
    return loft(mb, F, [R(a0), R(a1)], m, bev=bev)


def lathe(mb, F, c, prof, n, m, rot=0.0, caps=(True, True)):
    """solido de revolucao (n lados) em volta do eixo vertical por c; prof = [(raio, z relativo)] de baixo para cima"""
    rings = []
    for r, h in prof:
        r = max(r, 0.01)
        rings.append([(c[0] + r * math.cos(rot + 2 * math.pi * j / n), c[1] + r * math.sin(rot + 2 * math.pi * j / n),
                       c[2] + h) for j in range(n)])
    return loft(mb, F, rings, m, caps=caps)


def strip(mb, F, pts, side, w0, w1, h0, h1, m, bev=0.0):
    """faixa de secao retangular ao longo de pts (locais): largura w0..w1 no vetor HORIZONTAL side, altura h0..h1 em z"""
    sx, sy = side[0], side[1]
    rings = []
    for x, y, z in pts:
        rings.append([(x + sx * w0, y + sy * w0, z + h0), (x + sx * w1, y + sy * w1, z + h0),
                      (x + sx * w1, y + sy * w1, z + h1), (x + sx * w0, y + sy * w0, z + h1)])
    return loft(mb, F, rings, m, bev=bev)


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


def stone(mb, F, x0, x1, z0, z1, yb, yf0, yf1, c=0.12, m=ST):
    """bloco de pedra com a FACE em y (yf0 em z0 .. yf1 em z1: talude) e chanfro c so na face (20 tris); fundo em yb"""
    yz = lambda z: yf0 + (yf1 - yf0) * (z - z0) / max(1e-6, z1 - z0)
    r0 = [(x0, yb, z0), (x1, yb, z0), (x1, yb, z1), (x0, yb, z1)]
    r1 = [(x0, yz(z0) - c, z0), (x1, yz(z0) - c, z0), (x1, yz(z1) - c, z1), (x0, yz(z1) - c, z1)]
    r2 = [(x0 + c, yz(z0 + c), z0 + c), (x1 - c, yz(z0 + c), z0 + c), (x1 - c, yz(z1 - c), z1 - c),
          (x0 + c, yz(z1 - c), z1 - c)]
    loft(mb, F, [r0, r1, r2], m)


def rock_base(mb, F, x, y, z, r=0.8, hgt=0.45, m=ST):
    """pedra-base natural (soseki / tsuka-ishi): oitavado levemente irregular, enterrado 0,15"""
    k = (1.0, 0.97, 1.03, 0.96, 1.0, 0.95, 1.02, 0.98)
    rot = (x * 0.37 + y * 0.21) % 0.8
    poly = [(x + r * k[i] * math.cos(rot + i * math.pi / 4), y + r * k[i] * math.sin(rot + i * math.pi / 4))
            for i in range(8)]
    ext(mb, F, poly, "z", z - 0.15, z + hgt, m, 0.08)


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


def rrect(W, D, r, seg=3):
    """retangulo de cantos arredondados (anti-horario)"""
    pts = []
    for cx, cy, a0 in ((W / 2 - r, -D / 2 + r, -math.pi / 2), (W / 2 - r, D / 2 - r, 0.0),
                       (-W / 2 + r, D / 2 - r, math.pi / 2), (-W / 2 + r, -D / 2 + r, math.pi)):
        for i in range(seg + 1):
            a = a0 + (math.pi / 2) * i / seg
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


# ------------------------------------------------------------------ TELHADO: superficie com espessura e caimento
class Slope:
    """superficie do telhado em z(x, y) no referencial do telhado (origem no centro da planta). Planos longos (F/B):
    distancia d = Yw - |y| da linha da parede para dentro; planos de topo (R/L): d = Xw - |x|. Acima da parede o
    caimento e p; no beiral (d < 0) cai p2 < p (beiral que 'chuta' para fora). lift levanta SO os cantos do beiral
    (sori): lift * (|x|/Xe)^3 * (|y|/Ye)^3 - igual nos dois planos sobre o espigao (sem fresta)."""

    def __init__(self, Xw, Yw, zw, p, p2, Xe, Ye, lift, pu=None, db=1e9):
        self.Xw, self.Yw, self.zw, self.p, self.p2, self.Xe, self.Ye, self.lift = Xw, Yw, zw, p, p2, Xe, Ye, lift
        self.pu, self.db = (pu or p), db           # acima de d = db (pe da empena) o caimento sobe para pu

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


def sheet(mb, F, q, zf, tv, nu, tks, m=RT, m_bot=WD):
    """placa de telhado com espessura tv (offset vertical): quadrilatero de planta q = [beiral0, beiral1, topo1, topo0],
    malha nu x len(tks) seguindo zf(x, y). Topo e bordas em telha, face de baixo em madeira (forro do beiral)"""
    e0, e1, t1, t0 = q
    lerp = lambda a, b, t: (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
    G = []
    for t in tks:
        a, b = lerp(e0, t0, t), lerp(e1, t1, t)
        row = []
        for i in range(nu + 1):
            P = lerp(a, b, i / nu)
            row.append((P[0], P[1], zf(P[0], P[1])))
        G.append(row)
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


RIB = [(-0.32, -0.12), (-0.26, 0.13), (0.0, 0.27), (0.26, 0.13), (0.32, -0.12)]       # canal de telha (maru)
RIB_LO = [(-0.3, -0.12), (-0.2, 0.2), (0.2, 0.2), (0.3, -0.12)]
HIPP = [(-0.55, -0.2), (-0.47, 0.22), (-0.22, 0.47), (0.22, 0.47), (0.47, 0.22), (0.55, -0.2)]   # capa do espigao


def ribs(mb, F, lines, zf, lod=0, m=RT, prof=None):
    prof = prof or (RIB if lod == 0 else RIB_LO)
    for line in lines:
        sweep(mb, F, [(x, y, zf(x, y)) for x, y in line], prof, m)


def onigawara(mb, F, x, zr, sx, s=1.0, horns=True):
    """telha-ponteira da cumeeira: placa em escudo com disco e chifres (tsuno), virada para fora em x"""
    poly = [(-1.25, -0.75), (1.25, -0.75), (1.32, 0.45), (1.05, 1.3), (0.62, 1.88), (0.0, 2.1), (-0.62, 1.88),
            (-1.05, 1.3), (-1.32, 0.45)]
    ext(mb, F, [(u * s, zr + v * s) for u, v in poly], "x", x - 0.12 * sx, x + 0.42 * sx * s, RR, 0.05 if horns else 0.0)
    mb.rod(F.p(x + 0.38 * sx * s, 0, zr + 0.72 * s), F.p(x + 0.56 * sx * s, 0, zr + 0.72 * s), 0.5 * s, RR,
           10 if horns else 6)
    for k in ((-1, 1) if horns else ()):
        bx(mb, F, x + 0.1 * sx * s, k * 1.02 * s, zr + 1.95 * s, 0.4 * s, 0.32 * s, 0.95 * s, RR, 0.04, rx=-k * 0.5)


def ridge(mb, F, x0, x1, zr, pitch, w=2.0, oni=True, s=1.0):
    """cumeeira (o-mune) ao longo de x: base em tenda casada nos dois caimentos + 2 fiadas de noshi + capa redonda
    (kanmuri) + onigawara nas pontas"""
    hw = w / 2
    poly = [(-hw, zr - pitch * hw - 0.2), (0.0, zr - 0.2), (hw, zr - pitch * hw - 0.2), (hw, zr + 0.32 * s),
            (-hw, zr + 0.32 * s)]
    ext(mb, F, poly, "x", x0, x1, RR)
    bb(mb, F, x0 + 0.1, x1 - 0.1, -0.78 * w / 2, 0.78 * w / 2, zr + 0.28 * s, zr + 0.64 * s, RR, 0.05)
    bb(mb, F, x0 + 0.2, x1 - 0.2, -0.6 * w / 2, 0.6 * w / 2, zr + 0.6 * s, zr + 0.96 * s, RR, 0.05)
    mb.rod(F.p(x0 + 0.25, 0, zr + 1.1 * s), F.p(x1 - 0.25, 0, zr + 1.1 * s), 0.42 * w / 2, RR, 8)
    if oni:
        onigawara(mb, F, x0, zr, -1, s)
        onigawara(mb, F, x1, zr, 1, s)


def _hafu(mb, F, xh, ys, zf, tv, depth=0.85, m=WD, half=0.17):
    """tabeira de empena (hafu) sob a borda do telhado, em x = xh, ao longo de ys"""
    strip(mb, F, [(xh, y, zf(xh, y) - tv) for y in ys], (1, 0, 0), -half, half, -depth, 0.1, m, 0.04)


def _gegyo(mb, F, xh, za, sx, m=WD, s=1.0):
    """pendente do encontro das tabeiras (gegyo)"""
    poly = [(-0.95 * s, za + 0.5 * s), (0.95 * s, za + 0.5 * s), (0.6 * s, za - 0.45 * s), (0.0, za - 0.95 * s),
            (-0.6 * s, za - 0.45 * s)]
    ext(mb, F, poly, "x", xh - 0.12 * sx, xh + 0.24 * sx, m, 0.04)


def _gable_timber(mb, F, x_in, x_out, zb, top, ymax, style="timber"):
    """madeiramento aparente da empena (frechal + 2 montantes + ventilacao de trelica entre eles)"""
    if style not in ("timber", "board"):
        return
    zt0 = zb + 0.25
    if style == "board":                                   # empena de tabuas com mata-juntas (kitsure)
        for y in even(-ymax + 0.2, ymax - 0.2, 0.75):
            t = top(y) - 0.04
            if t > zt0 + 0.4:
                bb(mb, F, x_in, x_out, y - 0.08, y + 0.08, zt0, t, WD)
        return
    zt1 = zt0 + 0.6
    yt = ymax
    while yt > 0.5 and top(yt) < zt1 + 0.3:
        yt -= 0.1
    if yt <= 0.6:
        return
    bb(mb, F, x_in, x_out, -yt, yt, zt0, zt1, WD, 0.04)                    # frechal (nuki da empena)
    yp = yt * 0.55
    for k in (-1, 1):
        if top(k * yp) > zt1 + 0.6:
            bb(mb, F, x_in, x_out, k * yp - 0.24, k * yp + 0.24, zt1, top(k * yp) - 0.03, WD, 0.04)
    za, zc = zt1 + 0.35, top(0.0) - 0.45                  # ventilacao: fundo escuro + moldura + 3 balaustres
    hw = yp - 0.5
    if zc - za > 0.9 and hw > 0.6:
        zc = min(zc, za + 2.4)
        hw = min(hw, (zc - za) * 0.9)
        d = x_out - x_in
        xm = x_in + 0.14
        bb(mb, F, x_in - 0.1, xm, -hw, hw, za, zc, RR)
        for a, b, c_, e in ((-hw - 0.22, -hw, za - 0.22, zc + 0.22), (hw, hw + 0.22, za - 0.22, zc + 0.22),
                            (-hw, hw, za - 0.22, za), (-hw, hw, zc, zc + 0.22)):
            bb(mb, F, x_in, x_out, a, b, c_, e, WD)
        n = max(2, int(round(2 * hw / 0.5)))
        for i in range(1, n):
            y = -hw + 2 * hw * i / n
            bb(mb, F, xm - 0.02, x_out - 0.04, y - 0.07, y + 0.07, za, zc, WD)


def _rafter(mb, F, pts, zf, tv, w=0.28, h=0.34):
    """caibro (taruki) colado na face de baixo do telhado; pts em planta com a QUEBRA na linha da parede (o beiral
    chuta para fora: um caibro reto atravessaria a telha)"""
    for a, b in zip(pts, pts[1:]):
        beam(mb, F, (a[0], a[1], zf(*a) - tv - h / 2 + 0.02), (b[0], b[1], zf(*b) - tv - h / 2 + 0.02), w, h, WD)


def roof_hip(mb, F, W, D, h, kind="irimoya", pitch=0.55, over=3.4, gable=0.68, g_over=1.3, lift=0.9, tv=0.5,
             lod=0, gable_m=PL, gable_style="timber", rafters=True, m=RT, steep=1.5, back_lod=None):
    """telhado IRIMOYA (4 aguas embaixo + empena em cima) ou YOSEMUNE (4 aguas). W x D = planta das FACES EXTERNAS
    dos pilares; h = topo da viga de beiral (keta). A cumeeira corre no MAIOR lado (gira sozinho se D > W).
    Pecas de encontro: capas de espigao (com ponta levantada), cumeeira com onigawara, cumeeira do pe da empena,
    tabeiras (hafu) + gegyo, terca/caibros/rincao (sumigi) sob o beiral, testeira (kayaoi)."""
    if W < D - 1e-6:
        return roof_hip(mb, sub(F, ang=math.pi / 2), D, W, h, kind, pitch, over, gable, g_over, lift, tv, lod,
                        gable_m, gable_style, rafters, m, steep, back_lod)
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
        lk = lod if (ik == 0 or back_lod is None) else max(lod, back_lod)     # agua dos fundos mais simples
        sp = 1.4 if lk == 0 else 1.75
        # -------- agua longa (frente) + aba da empena (kerauba)
        tw = over / (Ye - yb)
        sheet(mb, Fk, [(-Xe, Ye), (Xe, Ye), (xg, yb), (-xg, yb)], S.zy, tv, max(6, int(2 * Xe / 3.0)),
              [0.0, tw * 0.5, tw, tw + (1 - tw) * 0.5, 1.0], m)
        if irim and yb > 0.05:
            sheet(mb, Fk, [(-xg - go, yb), (xg + go, yb), (xg + go, 0.0), (-xg - go, 0.0)], S.zy, tv,
                  max(4, int(2 * (xg + go) / 3.0)), [0.0, 0.5, 1.0], m)
        # -------- agua de topo (direita)
        twe = over / max(0.1, Xe - xg)
        sheet(mb, Fk, [(Xe, -Ye), (Xe, Ye), (xg, yb), (xg, -yb)], S.zx, tv, max(4, int(2 * Ye / 3.0)),
              [0.0, twe * 0.5, min(0.99, twe), min(0.995, twe + (1 - twe) * 0.5), 1.0], m)
        # -------- canais de telha
        lines = []
        for x in even(-Xe + 0.35, Xe - 0.35, sp):
            ax = abs(x)
            tip = [(x, Ye + 0.16), (x, Ye)]
            if ax <= xg:
                lines.append(tip + [(x, Yw)] + ([(x, yb)] if yb > 0.5 else [(x, Yw * 0.5)]) + [(x, 0.35)])
            else:
                ye = ax - k + 0.5
                if ye < Ye - 0.35:
                    lines.append(tip + ([(x, Yw)] if ye < Yw - 0.2 else []) + [(x, ye)])
                if irim and ax <= xg + go - 0.25:
                    lines.append([(x, yb - 0.02), (x, 0.35)])
        ribs(mb, Fk, lines, S.zy, lk, m)
        sp = 1.4 if lod == 0 else 1.75
        lines = []
        for y in even(-Ye + 0.35, Ye - 0.35, sp):
            ay = abs(y)
            xe = (xg + 0.5) if (irim and ay <= yb - 0.6) else (ay + k + 0.5)
            if xe < Xe - 0.35:
                lines.append([(Xe + 0.16, y), (Xe, y)] + ([(Xw, y)] if xe < Xw - 0.2 else []) + [(xe, y)])
        ribs(mb, Fk, lines, S.zx, lod, m)
        # -------- capas dos 2 espigoes deste lado (ponta levantada no beiral)
        for sy in (1, -1):
            pts = [(Xe + 0.55, sy * (Ye + 0.55), S.zy(Xe, Ye) + 0.55)]
            for u in (0.0, 0.5, 1.0):
                pts.append((Xe + (Xw - Xe) * u, sy * (Ye + (Yw - Ye) * u), S.zy(Xe + (Xw - Xe) * u, Ye + (Yw - Ye) * u)))
            for u in (0.5, 1.0):
                x_, y_ = Xw + (xg - Xw) * u, Yw + (yb - Yw) * u
                pts.append((x_, sy * y_, S.zy(x_, y_)))
            sweep(mb, Fk, pts, HIPP, RR)
            tx, ty, tz = pts[0]
            onigawara(mb, sub(Fk, tx, ty, 0.0, math.atan2(sy * (Ye - yb), Xe - xg)), -0.1, tz - 0.05, 1, 0.42, False)
        # -------- testeiras do beiral (kayaoi), caibros (taruki) e rincao (sumigi)
        yf = Ye - 0.34
        strip(mb, Fk, [(x, yf, S.zy(x, yf) - tv) for x in [(-Xe + 0.42) + (2 * Xe - 0.84) * i / 10 for i in range(11)]],
              (0, 1, 0), -0.17, 0.17, -0.55, 0.06, WD)
        xf = Xe - 0.34
        strip(mb, Fk, [(xf, y, S.zx(xf, y) - tv) for y in [(-Ye + 0.42) + (2 * Ye - 0.84) * i / 8 for i in range(9)]],
              (1, 0, 0), -0.17, 0.17, -0.55, 0.06, WD)
        for sy in (1, -1):
            beam(mb, Fk, (Xw - 0.8, sy * (Yw - 0.8), zw - tv - 0.75),
                 (Xe + 0.22, sy * (Ye + 0.22), S.zy(Xe, Ye) - tv - 0.32), 0.6, 0.62, WD, B)
        if rafters and lod == 0:
            for x in (even(-Xe + 0.75, Xe - 0.75, 1.45) if lk == 0 else []):
                y0 = max(Yw - 0.1, abs(x) - k + 0.3)
                y1 = Ye - 0.52
                if y1 - y0 > 0.5:
                    _rafter(mb, Fk, [(x, y0), (x, y1)], S.zy, tv)
            for y in even(-Ye + 0.75, Ye - 0.75, 1.45):
                x0 = max(Xw - 0.1, abs(y) + k + 0.3)
                x1 = Xe - 0.52
                if x1 - x0 > 0.5:
                    _rafter(mb, Fk, [(x0, y), (x1, y)], S.zx, tv)
        # -------- empena (irimoya): cumeeira do pe, triangulo, madeiramento, tabeiras, gegyo, tercas
        if irim and yb > 1.0:
            yf_ = yb - 0.55
            bb(mb, Fk, xg - 0.62, xg + 0.36, -yf_, yf_, zb - 0.22, zb + 0.22, RR, 0.05)
            mb.rod(Fk.p(xg - 0.13, -yf_, zb + 0.3), Fk.p(xg - 0.13, yf_, zb + 0.3), 0.24, RR, 8)
            top = lambda y: S.zy(xg, y) - tv - 0.05
            y1 = yb - (tv + 0.12) / pu
            if y1 > 0.4:
                ys = [y1, y1 * 0.5, 0.0, -y1 * 0.5, -y1]
                poly = [(-y1, zb - 0.18), (y1, zb - 0.18)] + [(y, top(y)) for y in ys]
                ext(mb, Fk, poly, "x", xg - 0.45, xg - 0.25, gable_m)
                _gable_timber(mb, Fk, xg - 0.27, xg - 0.05, zb, top, y1, gable_style)
            xh = xg + go - 0.3
            ye = 0.0
            for i in range(1, 200):
                y = yb * i / 200
                # (2a) a tabeira termina ACIMA da agua de topo medida na face de DENTRO dela (xh - 0,2) e acima dos
                # canais (0,27): antes a ponta furava a telha perto do pe da empena ("bloquinho")
                if S.zy(xh, y) - tv - 0.65 < S.zx(xh - 0.2, y) + 0.4:
                    break
                ye = y
            if ye > 0.5:
                for sy in (1, -1):
                    _hafu(mb, Fk, xh, [sy * ye * i / 5 for i in range(6)], S.zy, tv, 0.65)
                _gegyo(mb, Fk, xh, S.zy(xh, 0.0) - tv - 0.65, 1)
            for y in (0.0, yb * 0.5, -yb * 0.5):                       # tercas (moya) aparecendo sob a aba
                zt = S.zy(xg, y) - tv + 0.02
                bb(mb, Fk, xg - 0.5, xh - 0.2, y - 0.3, y + 0.3, zt - 0.7, zt, WD, 0.05)
    # -------- cumeeira
    if irim:
        ridge(mb, F, -(xg + go + 0.2), xg + go + 0.2, zr, pu)
    elif xg > 0.4:
        ridge(mb, F, -(xg + 0.3), xg + 0.3, zr, p)
    else:
        lathe(mb, F, (0, 0, zr - 0.2), [(0.6, 0.0), (0.75, 0.35), (0.45, 0.6), (0.5, 0.85), (0.3, 1.25), (0.05, 1.7)],
              8, RR)
    return dict(zr=zr, zb=zb, zw=zw, eave_z=S.zy(0.0, Ye) - tv - 0.55, Xe=Xe, Ye=Ye, top=zr + 2.1, xg=xg, yb=yb, go=go)


def roof_gable(mb, F, W, D, h, pitch=0.62, over=3.2, g_over=2.0, lift=0.6, tv=0.5, lod=0, gable_m=PL,
               gable_style="timber", rafters=True, m=RT, wall_t=0.8, ridge_w=2.0, oni_s=1.0, fascia=True,
               back_lod=None):
    """telhado KIRIZUMA (duas aguas), cumeeira ao longo de x. Empenas em x = +-W/2 (no plano da parede de topo),
    aba de empena g_over com tabeira e gegyo, tercas aparentes sob a aba"""
    Xw, Yw = W / 2, D / 2 + 0.15
    Xe, Ye = Xw + g_over, Yw + over
    zw = h + tv + 0.06
    p, p2 = pitch, pitch * 0.5
    S = Slope(Xw, Yw, zw, p, p2, Xe, Ye, lift)
    zr = S.zy(0.0, 0.0)
    tw = over / Ye
    small = ridge_w < 1.5
    for ik, Fk in enumerate((F, sub(F, ang=math.pi))):
        lk = lod if (ik == 0 or back_lod is None) else max(lod, back_lod)
        sp = 1.4 if lk == 0 else 1.75
        sheet(mb, Fk, [(-Xe, Ye), (Xe, Ye), (Xe, 0.0), (-Xe, 0.0)], S.zy, tv, max(4, int(2 * Xe / 3.0)),
              [0.0, tw * 0.5, tw, tw + (1 - tw) * 0.5, 1.0], m)
        if not small:
            ribs(mb, Fk, [[(x, Ye + 0.16), (x, Ye), (x, Yw), (x, Yw * 0.5), (x, 0.35)]
                          for x in even(-Xe + 0.35, Xe - 0.35, sp)], S.zy, lk, m)
        else:
            ribs(mb, Fk, [[(x, Ye + 0.1), (x, Ye), (x, 0.25)] for x in even(-Xe + 0.3, Xe - 0.3, 1.1)], S.zy, 1, m,
                 [(-0.2, -0.08), (-0.13, 0.13), (0.13, 0.13), (0.2, -0.08)])
        if fascia:
            yf = Ye - 0.3
            strip(mb, Fk, [(x, yf, S.zy(x, yf) - tv) for x in [(-Xe + 0.5) + (2 * Xe - 1.0) * i / 8 for i in range(9)]],
                  (0, 1, 0), -0.15, 0.15, -0.5 if not small else -0.3, 0.06, WD)
        if rafters and lk == 0 and not small:
            for x in even(-Xe + 0.75, Xe - 0.75, 1.45):
                y1 = Ye - 0.5
                _rafter(mb, Fk, [(x, Yw - 0.1), (x, y1)] if abs(x) < Xw - 0.5 else [(x, 0.6), (x, Yw), (x, y1)], S.zy, tv)
        # empena (em +x deste lado)
        top = lambda y: S.zy(Xw, y) - tv - 0.05
        ymax = D / 2
        ys = [ymax, ymax * 0.5, 0.0, -ymax * 0.5, -ymax]
        poly = [(-ymax, h - 0.1), (ymax, h - 0.1)] + [(y, top(y)) for y in ys]
        if gable_style == "kura":
            ext(mb, Fk, poly, "x", Xw - wall_t, Xw, gable_m)
        elif gable_style != "none":
            ext(mb, Fk, poly, "x", Xw - wall_t, Xw - 0.22, gable_m)
            _gable_timber(mb, Fk, Xw - 0.24, Xw - 0.02, h - 0.25, top, ymax, gable_style)
        xh = Xe - 0.3
        hd, hh = (1.3, 0.34) if gable_style == "kura" else ((0.9, 0.18) if not small else (0.4, 0.12))
        hm = PLK if gable_style == "kura" else WD
        for sy in (1, -1):
            _hafu(mb, Fk, xh, [sy * (Ye - 0.05) * u for u in (0.0, 0.25, Yw / Ye * 0.999, (Yw / Ye + 1) / 2, 1.0)],
                  S.zy, tv, hd, hm, hh)
        if not small:
            _gegyo(mb, Fk, xh, S.zy(xh, 0.0) - tv - hd, 1, hm)
            for y in (0.0, Yw * 0.5, -Yw * 0.5):                        # tercas aparentes sob a aba
                zt = S.zy(Xw, y) - tv + 0.02 if y else zr - tv + 0.02
                bb(mb, Fk, Xw - 0.3, xh - 0.25, y - 0.3, y + 0.3, zt - 0.75, zt, WD if gable_style != "kura" else PLK, 0.05)
    ridge(mb, F, -(Xe + 0.17), Xe + 0.17, zr, p, ridge_w, oni=True, s=oni_s)
    return dict(zr=zr, zw=zw, eave_z=S.zy(0.0, Ye) - tv - 0.5, Xe=Xe, Ye=Ye, top=zr + 2.1 * oni_s)


def roof_pent(mb, Ff, L, depth, z_top, pitch=0.42, tv=0.4, lift=0.35, lod=0, support="brackets", m=RT,
              rafters=True, embed=0.35, ends=True, xs=None):
    """agua unica encostada na parede (hisashi / capelo de porta e janela). Ff na face da parede (y=0, +y fora);
    z_top = topo da telha junto da parede; a placa entra 'embed' na parede. support: 'brackets' (consolos +
    mao-francesa + terca de ponta), 'braces' (so maos-francesas), 'none'"""
    X = L / 2
    zf = lambda x, y: z_top - pitch * y + lift * min(1.0, abs(x) / X) ** 3 * min(1.0, max(0.0, y) / depth) ** 3
    sheet(mb, Ff, [(-X, depth), (X, depth), (X, -embed), (-X, -embed)], zf, tv, max(3, int(L / 3.0)),
          [0.0, 0.5, 1.0], m)
    small = depth < 2.0
    if small:
        ribs(mb, Ff, [[(x, depth + 0.1), (x, depth), (x, 0.15)] for x in even(-X + 0.3, X - 0.3, 1.0)], zf, 1, m,
             [(-0.22, -0.08), (-0.14, 0.15), (0.14, 0.15), (0.22, -0.08)])
    else:
        ribs(mb, Ff, [[(x, depth + 0.15), (x, depth), (x, depth * 0.5), (x, 0.2)]
                      for x in even(-X + 0.35, X - 0.35, 1.3 if lod == 0 else 1.75)], zf, lod, m)
    # rufo de madeira contra a parede (mizukiri)
    bb(mb, Ff, -X + 0.06, X - 0.06, -0.12, 0.3 if not small else 0.22, z_top - 0.35, z_top + (0.3 if not small else 0.2), WD,
       0.03)
    yf = depth - 0.3
    hb = 0.5 if not small else 0.3
    strip(mb, Ff, [(x, yf, zf(x, yf) - tv) for x in [(-X + 0.4) + (2 * X - 0.8) * i / 6 for i in range(7)]],
          (0, 1, 0), -0.15, 0.15, -hb, 0.06, WD)
    if ends:
        for sx in (-1, 1):
            strip(mb, Ff, [(sx * (X - 0.18), y, zf(sx * (X - 0.18), y) - tv) for y in (0.0, depth * 0.5, depth - 0.05)],
                  (1, 0, 0), -0.13, 0.13, -hb, 0.08, WD)
    xs = xs if xs is not None else ([-X + 0.6, X - 0.6] + ([] if L < 9 else
                                                          [x for x in even(-X + 0.6, X - 0.6, 4.5)][1:-1] if L > 14 else []))
    if support == "brackets":
        zd = zf(0.0, depth - 0.57) - tv - 0.32
        bb(mb, Ff, -X + 0.25, X - 0.25, depth - 0.85, depth - 0.3, zd - 0.5, zd, WD, 0.05)       # terca de ponta
        for x in xs:
            ext(mb, Ff, [(-0.35, zd - 0.5), (depth - 0.2, zd - 0.5), (depth - 0.2, zd - 0.95), (depth * 0.6, zd - 1.05),
                         (depth * 0.25, zd - 1.35), (-0.35, zd - 1.55)], "x", x - 0.22, x + 0.22, WD, 0.04)
            beam(mb, Ff, (x, 0.05, zd - 3.4), (x, depth * 0.55, zd - 1.1), 0.26, 0.3, WD)
        if rafters and lod == 0:
            for x in even(-X + 0.7, X - 0.7, 1.45):
                beam(mb, Ff, (x, -0.2, zf(x, -0.2) - tv - 0.15), (x, depth - 0.45, zf(x, depth - 0.45) - tv - 0.15),
                     0.26, 0.32, WD)
    elif support == "braces":
        for x in xs:
            zb_ = zf(x, depth * 0.7) - tv
            beam(mb, Ff, (x, -0.1, zb_ - 0.25), (x, depth * 0.75, zb_ - 0.12), 0.22, 0.3, WD)
            beam(mb, Ff, (x, 0.05, zb_ - (1.4 if small else 2.4)), (x, depth * 0.55, zb_ - 0.25), 0.2, 0.22, WD)
    return dict(eave_z=zf(0.0, depth) - tv - hb)


def hip_cap(mb, F, c, hx, hy, z, over, rise, t, m, lift=0.0, nu=2):
    """chapeu de 4 aguas pequeno (lanterna) com espessura t, beiral 'over' e cantos levemente levantados"""
    Xw, Yw = hx, hy
    S = Slope(Xw, Yw, z + t, rise / max(hx, hy), rise / max(hx, hy) * 0.55, hx + over, hy + over, lift)
    k = Xw - Yw
    Fc = sub(F, c[0], c[1], 0.0)
    tw = over / (hy + over)
    tks = [0.0, tw, 1.0]
    for Fk in (Fc, sub(Fc, ang=math.pi)):
        sheet(mb, Fk, [(-hx - over, hy + over), (hx + over, hy + over), (k, 0.0), (-k, 0.0)], S.zy, t, nu, tks, m, m)
        sheet(mb, Fk, [(hx + over, -hy - over), (hx + over, hy + over), (k, 0.0), (k, 0.0)], S.zx, t, nu, tks, m, m)
    return S.zy(0.0, 0.0)


# ------------------------------------------------------------------ PAREDES: estrutura + vedacao + vaos
def boards(mb, Ff, a, b, z0=0.7, z1=KH):
    """rodape de tabuas (koshi-ita) recuado + mata-juntas verticais"""
    bb(mb, Ff, a, b, -0.72, -0.14, z0, z1, WM)
    n = max(1, int(round((b - a) / 0.95)))
    for i in range(1, n):
        x = a + (b - a) * i / n
        bb(mb, Ff, x - 0.09, x + 0.09, -0.16, -0.02, z0, z1, WD)


def window(mb, Ff, s, z, w, h, kind="koshi", lit=True, hood=False, sill=True, head=0.3, lod=0):
    """janela com caixilho (ombreiras, verga, peitoril com pingadeira), shoji (papel aceso ou apagado) RECUADO 0,6 da
    face dos pilares + grade de kumiko, e trelica koshi na frente (kind 'koshi'/'lattice'). O vao na parede e de quem
    chama (s-w/2..s+w/2, z..z+h). Devolve o ponto (local Ff) para a luz da casa."""
    x0, x1 = s - w / 2, s + w / 2
    j = 0.3
    zlo = z - (0.3 if sill else 0.0)
    bb(mb, Ff, x0 - j, x0, -0.86, -0.06, zlo, z + h + head, WD, 0.04)
    bb(mb, Ff, x1, x1 + j, -0.86, -0.06, zlo, z + h + head, WD, 0.04)
    bb(mb, Ff, x0, x1, -0.86, -0.06, z + h, z + h + head, WD, 0.04)
    if sill:
        bb(mb, Ff, x0 - j - 0.1, x1 + j + 0.1, -0.86, 0.1, z - 0.3, z, WD, 0.04)
    bb(mb, Ff, x0 - 0.02, x1 + 0.02, -0.7, -0.62, z, z + h, LIT if lit else PAPER)
    nv = max(1, int(round(w / 0.95))) - 1
    nh = max(1, int(round(h / 1.15))) - 1
    for i in range(1, nv + 1):
        xx = x0 + w * i / (nv + 1)
        bb(mb, Ff, xx - 0.05, xx + 0.05, -0.64, -0.5, z, z + h, WD)
    for i in range(1, nh + 1):
        zz = z + h * i / (nh + 1)
        bb(mb, Ff, x0, x1, -0.64, -0.5, zz - 0.05, zz + 0.05, WD)
    if kind in ("koshi", "lattice"):
        nb = max(2, int(round(w / (0.42 if kind == "koshi" else 0.5))))
        for i in range(1, nb):
            xx = x0 + w * i / nb
            bb(mb, Ff, xx - 0.08, xx + 0.08, -0.38, -0.16, z, z + h, WD)
        for zz in ((z + h * 0.62,) if kind == "koshi" else (z + h * 0.3, z + h * 0.7)):
            bb(mb, Ff, x0, x1, -0.4, -0.1, zz - 0.07, zz + 0.07, WD)
    if hood:
        roof_pent(mb, sub(Ff, s, 0.0, 0.0), w + 1.6, 1.5, z + h + head + 1.25, 0.5, 0.26, 0.15, 1, "braces",
                  xs=[-(w / 2 + 0.35), w / 2 + 0.35])
    return (s, 1.6, z + h * 0.5)


def _leaf(mb, Ff, xa, xb, ya, yb_, za, zb, kind, lit, lod=0):
    """folha de porta de correr: quadro (montantes/travessas), almofada baixa, trelica + papel em cima, puxador"""
    st = 0.3
    if kind == "itado":
        bb(mb, Ff, xa + 0.05, xb - 0.05, ya + 0.03, yb_ - 0.05, za, zb, WM)
        for x in (xa, xb - st):
            bb(mb, Ff, x, x + st, ya, yb_, za, zb, WD, 0.03)
        for zz in (za + 0.6, (za + zb) / 2, zb - 0.6):
            bb(mb, Ff, xa + st, xb - st, yb_ - 0.06, yb_ + 0.04, zz - 0.2, zz + 0.2, WD, 0.03)
        if lod == 0:
            n = max(2, int(round((xb - xa - 2 * st) / 0.6)))
            for i in range(1, n):
                x = xa + st + (xb - xa - 2 * st) * i / n
                bb(mb, Ff, x - 0.03, x + 0.03, yb_ - 0.08, yb_ - 0.04, za + 0.1, zb - 0.1, WD)
        bb(mb, Ff, xb - st - 0.4, xb - st - 0.15, yb_ + 0.02, yb_ + 0.1, za + 3.6, za + 4.3, IRON)
        return
    for x in (xa, xb - st):
        bb(mb, Ff, x, x + st, ya, yb_, za, zb, WM, 0.03)
    zm = za + min(2.6, (zb - za) * 0.33)
    for z0_, z1_ in ((za, za + 0.55), (zm, zm + 0.25), (zb - 0.3, zb)):
        bb(mb, Ff, xa + st, xb - st, ya, yb_, z0_, z1_, WM, 0.03)
    bb(mb, Ff, xa + st, xb - st, ya + 0.04, yb_ - 0.04, za + 0.55, zm, WD)                       # almofada
    bb(mb, Ff, xa + st, xb - st, ya, ya + 0.03, zm + 0.25, zb - 0.3, LIT if lit else PAPER)       # papel (atras)
    n = max(2, int(round((xb - xa - 2 * st) / 0.34)))
    for i in range(1, n):
        x = xa + st + (xb - xa - 2 * st) * i / n
        bb(mb, Ff, x - 0.05, x + 0.05, yb_ - 0.1, yb_ - 0.01, zm + 0.25, zb - 0.3, WD)
    zk = (zm + zb) / 2
    bb(mb, Ff, xa + st, xb - st, yb_ - 0.1, yb_ - 0.01, zk - 0.05, zk + 0.05, WD)
    bb(mb, Ff, xb - st + 0.08, xb - 0.08, yb_ - 0.02, yb_ + 0.04, za + 3.7, za + 4.2, IRON)


def door(mb, Ff, s, w, h, kind="hikido", lit=False, noren=None, z0=SILL, lod=0):
    """porta: caixilho (ombreiras, verga kamoi, soleira shikii com trilhos) + folhas de correr RECUADAS em 2 trilhos
    (hikido: quadro + almofada + trelica/papel; itado: tabuas com travessas e puxador de ferro; open: vao livre) +
    noren opcional (cortina em 2-3 panos num varao). O vao na parede e de quem chama (s-w/2..s+w/2, 0..z0+h)."""
    x0, x1 = s - w / 2, s + w / 2
    bb(mb, Ff, x0 - 0.3, x0, -0.9, -0.04, z0 - 0.25, z0 + h + 0.45, WD, 0.04)
    bb(mb, Ff, x1, x1 + 0.3, -0.9, -0.04, z0 - 0.25, z0 + h + 0.45, WD, 0.04)
    bb(mb, Ff, x0, x1, -0.9, -0.04, z0 + h, z0 + h + 0.45, WD, 0.04)
    bb(mb, Ff, x0 - 0.3, x1 + 0.3, -0.95, 0.2, z0 - 0.25, z0, WD, 0.04)
    if kind != "open":
        for yy in (-0.58, -0.36):
            bb(mb, Ff, x0, x1, yy - 0.03, yy + 0.03, z0, z0 + 0.06, WD)
        lw = w / 2 + 0.12
        _leaf(mb, Ff, x0, x0 + lw, -0.66, -0.5, z0 + 0.04, z0 + h - 0.04, kind, lit, lod)
        _leaf(mb, Ff, x1 - lw, x1, -0.44, -0.28, z0 + 0.04, z0 + h - 0.04, kind, lit, lod)
    if noren:
        noren_cloth(mb, Ff, x0, x1, z0 + h - 0.12, min(3.6, h * 0.42), noren)
    return dict(center=(s, 0.0, z0), glow=(s, 1.8, z0 + h * 0.62))


def noren_cloth(mb, Ff, x0, x1, zt, ln, noren=True):
    """noren (cortina em 2-3 panos num varao) na frente do vao x0..x1, topo do varao em zt, panos de comprimento ln
    (2a: extraido de door() para o vao 'open' tambem poder levar noren)"""
    nm = noren if isinstance(noren, str) else CLOTH
    w = x1 - x0
    mb.rod(Ff.p(x0 - 0.45, 0.42, zt), Ff.p(x1 + 0.45, 0.42, zt), 0.08, WD, 6)
    n = 3 if w > 4.5 else 2
    g = 0.14
    sw = (w + 0.4 - g * (n - 1)) / n
    for i in range(n):
        xa = x0 - 0.2 + i * (sw + g)
        bb(mb, Ff, xa, xa + sw, 0.3, 0.36, zt - ln, zt - 0.2, nm)
        bb(mb, Ff, xa, xa + sw, 0.3, 0.54, zt - 0.3, zt + 0.12, nm)


def _shop(mb, Ff, a, b, zn, lit=True, ground=0.0):
    """frente de oficina: shitomi (painel de trelica erguido em tirantes de ferro) + agebutai (banca dobrada) +
    fundo da oficina (piso de tabuas, parede, prateleiras de tabuas, porta de papel acesa)"""
    cw = b - a
    ln = min(3.4, zn * 0.4)
    th = math.radians(14.0)
    hz = zn - 0.15
    cy, cz = 0.25 + ln / 2 * math.cos(th), hz + ln / 2 * math.sin(th)
    bx(mb, Ff, (a + b) / 2, cy, cz, cw - 0.2, ln, 0.22, WM, 0.03, rx=th)
    for k in range(4):
        u = -ln / 2 + ln * (k + 0.5) / 4
        bx(mb, Ff, (a + b) / 2, cy + u * math.cos(th), cz + u * math.sin(th) + 0.13, cw - 0.2, 0.14, 0.08, WD, 0.0, rx=th)
    for x in (a + 0.35, b - 0.35):
        bx(mb, Ff, x, cy, cz + 0.13, 0.16, ln, 0.1, WD, 0.0, rx=th)
        ye, ze = 0.25 + ln * math.cos(th) - 0.15, hz + ln * math.sin(th)
        mb.rod(Ff.p(x, ye, ze), Ff.p(x, 0.15, hz + 1.6), 0.05, IRON, 6)
    zb = 2.2
    bb(mb, Ff, a + 0.15, b - 0.15, 0.2, 2.1, zb - 0.22, zb, WM, 0.03)
    bb(mb, Ff, a + 0.15, b - 0.15, 1.95, 2.15, zb - 0.6, zb - 0.22, WD)
    for x in (a + 0.5, b - 0.5):
        bb(mb, Ff, x - 0.12, x + 0.12, 1.7, 1.94, ground + 0.02, zb - 0.6, WD)
    # fundo da oficina
    bb(mb, Ff, a, b, -4.4, -0.9, 0.45, 0.7, WM)
    bb(mb, Ff, a, b, -4.7, -4.4, 0.7, zn + 0.5, PL)
    for zz in (2.8, 4.6, 6.4):
        bb(mb, Ff, a + 0.4, b - 0.4, -4.4, -3.4, zz - 0.18, zz, WD, 0.03)
        for x in (a + 0.5, b - 0.5):
            bb(mb, Ff, x - 0.1, x + 0.1, -4.4, -3.5, zz - 0.95, zz - 0.18, WD)
    bb(mb, Ff, (a + b) / 2 - 1.3, (a + b) / 2 + 1.3, -4.3, -4.24, 0.7, 6.2, LIT if lit else PAPER)
    bb(mb, Ff, a, b, -4.7, -0.9, zn + 0.5, zn + 0.75, WD)


def facade(mb, Ff, L, h, bays, full=True, door_w=DOOR_W, door_h=DOOR_H, plaster=PL, lit=True, ext=0.9, lod=0,
           ground=0.0, noren=None, nageshi=True):
    """uma fachada: soleira (dodai), viga de beiral (keta) que PASSA dos cantos (kibana) nas fachadas 'full',
    verga continua (nageshi) sobre os pilares, pilares intermediarios e os vaos. Os pilares de CANTO sao de
    corner_posts(). L = entre as faces externas dos pilares de canto; h = topo da keta."""
    xi0, xi1 = -L / 2 + CP, L / 2 - CP
    zn = SILL + door_h + 0.45
    out = dict(glow=[], doors=[])
    bs = [dict(b) if isinstance(b, dict) else {"t": b} for b in bays]
    for b_ in bs:
        if "w" not in b_ and b_["t"] in ("door", "itado", "open_door"):
            b_["w"] = door_w + 0.6
    bs = list(reversed(bs))                              # lista lida da esquerda p/ a direita de quem olha de fora
    n = len(bs)
    fixed = sum(b_.get("w", 0.0) for b_ in bs)
    nfree = sum(1 for b_ in bs if "w" not in b_)
    free = (xi1 - xi0 - (n - 1) * IP - fixed) / max(1, nfree)
    if nfree and free < 1.4:
        print("KIT AVISO fachada L=%.1f: vaos livres de %.2f" % (L, free))
    xa, xb = (-L / 2, L / 2) if full else (xi0, xi1)
    bb(mb, Ff, xa, xb, -0.95, 0.06, 0.0, 0.7, WD, B)                                         # dodai
    ke = (-L / 2 - ext, L / 2 + ext) if full else (xi0, xi1)
    bb(mb, Ff, ke[0], ke[1], -0.95, 0.15, h - 1.0, h, WD, B)                                 # keta
    if nageshi and zn + 0.5 < h - 1.2:
        ne = (-L / 2 - 0.14, L / 2 + 0.14) if full else (-L / 2 + 0.25, L / 2 - 0.25)
        bb(mb, Ff, ne[0], ne[1], -0.25, 0.14, zn, zn + 0.5, WD, 0.05)                        # nageshi
    x = xi0
    for i, sp in enumerate(bs):
        w = sp.get("w", free)
        a, b = x, x + w
        _bay(mb, Ff, a, b, sp, h, zn, plaster, lit, lod, out, ground, noren, door_h)
        x = b
        if i < n - 1:
            bb(mb, Ff, x, x + IP, -0.9, 0.0, 0.7, h - 1.0, WD, B)
            x += IP
    out["glow"] = [Ff.p(*g) for g in out["glow"]]
    out["doors"] = [(Ff.p(*c), Ff.a) for c in out["doors"]]
    return out


def _bay(mb, Ff, a, b, sp, h, zn, plaster, lit, lod, out, ground, noren, door_h):
    t = sp["t"]
    cw, cx = b - a, (a + b) / 2
    lt = sp.get("lit", lit)
    ztop = h - 0.95
    pl = sp.get("plaster", plaster)
    if t in ("plain", "koshi", "shoji"):
        boards(mb, Ff, a, b, 0.7, KH)
        bb(mb, Ff, a, b, -0.76, 0.06, KH, KH + 0.25, WD, 0.04)
    if t in ("plain", "plaster"):
        panel(mb, Ff, a, b, KH + 0.25 if t == "plain" else 0.7, ztop, -0.8, -0.22, [], pl)
        if sp.get("nuki", True) and zn - KH > 4.0:              # travessa aparente (nuki) a meia altura
            zk = KH + 0.25 + (zn - KH - 0.25) * 0.5
            bb(mb, Ff, a, b, -0.34, -0.06, zk - 0.17, zk + 0.17, WD)
    elif t == "koshi":
        zs = KH + 0.25
        ww = min(cw - 1.2, sp.get("ww", 9.0))
        wh = min(sp.get("wh", 4.4), zn - 0.75 - zs)
        out["glow"].append(window(mb, Ff, cx, zs, ww, wh, "koshi", lt, sp.get("hood", False), sill=False, lod=lod))
        panel(mb, Ff, a, b, zs, ztop, -0.8, -0.22, [(cx - ww / 2 - 0.3, cx + ww / 2 + 0.3, zs - 0.01, zs + wh + 0.3)], pl)
    elif t == "shoji":
        zs = sp.get("z", 5.4)
        ww = min(cw - 1.6, sp.get("ww", 4.2))
        wh = min(sp.get("wh", 3.0), zn - 0.75 - zs) if zs < zn else min(sp.get("wh", 2.4), ztop - zs - 0.5)
        out["glow"].append(window(mb, Ff, cx, zs, ww, wh, "shoji", lt, sp.get("hood", False), lod=lod))
        panel(mb, Ff, a, b, KH + 0.25, ztop, -0.8, -0.22, [(cx - ww / 2 - 0.3, cx + ww / 2 + 0.3, zs - 0.3, zs + wh + 0.3)],
              pl)
    elif t == "lattice":
        lw = cw - 0.6
        out["glow"].append(window(mb, Ff, cx, 0.95, lw, zn - 0.45 - 0.95, "lattice", lt, False, head=0.45, lod=lod))
        panel(mb, Ff, a, b, zn, ztop, -0.8, -0.22, [], pl)
    elif t in ("door", "itado", "open_door"):
        dw = cw - 0.6
        kind = {"door": "hikido", "itado": "itado", "open_door": "open"}[t]
        nr = sp.get("noren", noren)
        d = door(mb, Ff, cx, dw, door_h, kind, lt and kind == "hikido", nr, SILL, lod)
        out["glow"].append(d["glow"])
        out["doors"].append(d["center"])
        panel(mb, Ff, a, b, 0.7, ztop, -0.8, -0.22, [(cx - dw / 2 - 0.3, cx + dw / 2 + 0.3, 0.0, zn)], pl)
    elif t == "shop":
        _shop(mb, Ff, a, b, zn, lt, ground)
        panel(mb, Ff, a, b, zn, ztop, -0.8, -0.22, [], pl)
        out["glow"].append((cx, 1.0, zn * 0.5))
    elif t == "open":
        if sp.get("rail"):
            bb(mb, Ff, a, b, -0.6, -0.2, 3.2, 3.5, WD, 0.03)
        if sp.get("noren"):                                    # (2a) o preset V1 pedia noren no vao aberto
            noren_cloth(mb, Ff, a + 0.25, b - 0.25, ztop - 0.25, min(3.4, ztop * 0.36), sp["noren"])
    # (open: so a estrutura - pavilhao)


def corner_posts(mb, Fb, W, D, z0=0.7, z1=None, s=CP):
    for sx in (-1, 1):
        for sy in (-1, 1):
            xa, xb = (W / 2 - s, W / 2) if sx > 0 else (-W / 2, -W / 2 + s)
            ya, yb_ = (D / 2 - s, D / 2) if sy > 0 else (-D / 2, -D / 2 + s)
            bb(mb, Fb, xa, xb, ya, yb_, z0, z1, WD, B)


def post(mb, F, x, y, z0, z1, s=0.9, base=True, m=WD):
    """pilar quadrado chanfrado sobre pedra natural (soseki)"""
    if base:
        rock_base(mb, F, x, y, z0, s * 0.95, 0.4)
        z0 += 0.4
    bb(mb, F, x - s / 2, x + s / 2, y - s / 2, y + s / 2, z0, z1, m, min(0.12, s * 0.15))


def bracket(mb, F, x, y, z, L, w=0.5, h=0.9, m=WD):
    """misula (funa-hijiki) de topo plano em z, saindo L para +y, com o ventre curvo"""
    poly = [(y, z), (y + L, z), (y + L, z - h * 0.35), (y + L * 0.72, z - h * 0.45), (y + L * 0.42, z - h * 0.62),
            (y + L * 0.18, z - h * 0.86), (y, z - h)]
    ext(mb, F, poly, "x", x - w / 2, x + w / 2, m, 0.04)


# ------------------------------------------------------------------ FUNDACOES
def foundation(mb, F, W, D, h, style="ishigaki", batter=8.0, lod=0, sides="FBLR", cap=True):
    """soco sob a casa: 'ishigaki' = pedras em fiadas com TALUDE (batter graus), cantos travados alternados
    (sangi-zumi), juntas rebaixadas sobre miolo escuro e capa de lajes; 'soco' = cantaria reta em blocos longos.
    W x D = topo (face de fora); z de 0 (chao) a h. Enterra 0,4."""
    if h <= 0.05 or style == "none":
        return
    t = math.tan(math.radians(batter)) if style == "ishigaki" else 0.0
    g = 0.06
    bb(mb, F, -W / 2 + 0.16, W / 2 - 0.16, -D / 2 + 0.16, D / 2 - 0.16, -0.4, h - 0.3, STD)      # miolo (juntas)
    capt = 0.38 if cap else 0.0
    zc = h - capt
    nc = max(1, int(round((zc + 0.4) / (1.15 if style == "ishigaki" else 1.6))))
    pat = (2.7, 1.9, 3.3, 2.3, 1.7, 3.0, 2.5) if style == "ishigaki" else (3.4, 2.8, 3.8, 3.1)
    if lod:
        pat = tuple(v * 1.35 for v in pat)
    faces = {"F": (0.0, W, D), "B": (math.pi, W, D), "R": (-math.pi / 2, D, W), "L": (math.pi / 2, D, W)}
    for key, (ang, Lf, Df) in faces.items():
        if key not in sides:
            continue
        Ff = sub(F, 0.0, 0.0, 0.0, ang)
        long_axis = key in "FB"
        for c in range(nc):
            z0 = -0.4 + (zc + 0.4) * c / nc
            z1 = -0.4 + (zc + 0.4) * (c + 1) / nc
            own = (c % 2 == 0) == long_axis                 # este lado leva a pedra de canto nesta fiada?
            ext_c = (h - z0) * t
            xa = -Lf / 2 - (ext_c if own else -0.9)
            xb = Lf / 2 + (ext_c if own else -0.9)
            x = xa
            k = (c * 3 + (0 if long_axis else 2)) % len(pat)
            while x < xb - 0.3:
                ln = pat[k % len(pat)] * (1.25 if (x == xa and own and style == "ishigaki") else 1.0)
                k += 1
                x2 = min(xb, x + ln)
                if xb - x2 < 0.9:
                    x2 = xb
                y0f = Df / 2 + (h - z0) * t
                y1f = Df / 2 + (h - z1) * t
                df = (0.0, 0.08, -0.05, 0.05, 0.02, -0.03, 0.07)[k % 7] if style == "ishigaki" else 0.0
                stone(mb, Ff, x + g, x2 - g, z0 + g, z1 - g, Df / 2 - 0.9, y0f - g * t + df, y1f + df,
                      (0.14, 0.2, 0.12, 0.18)[k % 4] if style == "ishigaki" else 0.08)
                x = x2
        if cap:
            x = -Lf / 2 - 0.15
            k = 1 if long_axis else 3
            while x < Lf / 2 + 0.15 - 0.3:
                ln = (3.6, 2.9, 4.2, 3.2)[k % 4] * (1.2 if lod else 1.0)
                k += 1
                x2 = min(Lf / 2 + 0.15, x + ln)
                if Lf / 2 + 0.15 - x2 < 1.0:
                    x2 = Lf / 2 + 0.15
                xa_ = x + (0.04 if x > -Lf / 2 else 0.0)
                xb_ = x2 - (0.04 if x2 < Lf / 2 else 0.0)
                if not long_axis:                     # capa de topo nao invade a capa das fachadas longas
                    xa_, xb_ = max(xa_, -Lf / 2 + 1.25), min(xb_, Lf / 2 - 1.25)
                if xb_ - xa_ > 0.3:
                    stone(mb, Ff, xa_, xb_, zc, h, Df / 2 - 1.25, Df / 2 + 0.15, Df / 2 + 0.15, 0.1, ST)
                x = x2


# ------------------------------------------------------------------ KURA (armazem de reboco grosso)
def kura_body(mb, F, W, D, h, m=PLK, r=0.7, namako=3.4, belts=(), lod=0):
    """corpo do kura: reboco grosso de cantos arredondados, faixa namako (telhas escuras em losango com juntas de
    reboco em relevo) na base, cintas de reboco nos andares e cornija em 2 degraus sob o beiral. z=0 = piso"""
    ext(mb, F, rrect(W, D, r), "z", 0.0, h, m)
    if namako:
        ext(mb, F, rrect(W + 0.24, D + 0.24, r + 0.12), "z", 0.02, namako, m)
        ext(mb, F, rrect(W + 0.6, D + 0.6, r + 0.3), "z", 0.04, 0.45, m)
        ext(mb, F, rrect(W + 0.6, D + 0.6, r + 0.3), "z", namako - 0.4, namako + 0.02, m)
        for ang, Lf, Df in ((0.0, W, D), (math.pi, W, D), (-math.pi / 2, D, W), (math.pi / 2, D, W)):
            Ff = sub(F, 0.0, 0.0, 0.0, ang)
            yy = Df / 2 + 0.12
            pitch_ = 1.42 if lod == 0 else 1.9
            row = 0
            z = 0.45 + pitch_ / 2
            while z < namako - 0.4:
                off = (row % 2) * pitch_ / 2
                xm = Lf / 2 - r - 0.35
                xx = -xm + off
                while xx <= xm + 1e-6:
                    bx(mb, Ff, xx, yy + 0.05, z, pitch_ * 0.64, 0.16, pitch_ * 0.64, RR, 0.0, ry=math.pi / 4)
                    xx += pitch_
                z += pitch_ / 2
                row += 1
    for zb in belts:
        ext(mb, F, rrect(W + 0.5, D + 0.5, r + 0.25), "z", zb, zb + 0.55, m)
    ext(mb, F, rrect(W + 0.5, D + 0.5, r + 0.25), "z", h - 0.95, h - 0.45, m)
    ext(mb, F, rrect(W + 1.0, D + 1.0, r + 0.5), "z", h - 0.45, h + 0.02, m)


def kura_window(mb, Ff, s, z, w, h, lit=True, shutters=True, hood=True, m=PLK):
    """janela de kura aplicada na face (y=0 = face do reboco): moldura em 2 degraus salientes, painel aceso/papel
    RECUADO (0,12 da parede), grade de ferro, 2 portas grossas de reboco abertas contra a parede, capelo de telha"""
    x0, x1 = s - w / 2, s + w / 2
    for o, d in ((0.8, 0.62), (0.4, 0.36)):
        oi = o - 0.4 if o > 0.5 else 0.0
        for a, b, c, e in ((x0 - o, x0 - oi, z - o, z + h + o), (x1 + oi, x1 + o, z - o, z + h + o),
                           (x0 - oi, x1 + oi, z - o, z - oi), (x0 - oi, x1 + oi, z + h + oi, z + h + o)):
            bb(mb, Ff, a, b, -0.3, d, c, e, m, 0.05)
    bb(mb, Ff, x0, x1, 0.12, 0.2, z, z + h, LIT if lit else PAPER)
    n = max(2, int(round(w / 0.5)))
    for i in range(1, n):
        xx = x0 + w * i / n
        mb.rod(Ff.p(xx, 0.32, z - 0.02), Ff.p(xx, 0.32, z + h + 0.02), 0.06, IRON, 6)
    if shutters:
        lw = w / 2 + 0.5
        for k in (-1, 1):
            xa = s + k * (w / 2 + 0.9)
            xb = xa + k * lw
            bb(mb, Ff, xa, xb, 0.14, 0.6, z - 0.35, z + h + 0.35, m, 0.05)
            bb(mb, Ff, xa + k * 0.22, xb - k * 0.22, 0.6, 0.86, z - 0.12, z + h + 0.12, m, 0.04)
            for zz in (z + 0.4, z + h - 0.4):
                bb(mb, Ff, min(xa + k * 0.2, xa - k * 0.45), max(xa + k * 0.2, xa - k * 0.45), 0.08, 0.66, zz - 0.09, zz + 0.09,
                   IRON)
    if hood:
        roof_pent(mb, sub(Ff, s, 0.0, 0.0), w + 3.4, 1.6, z + h + 1.75, 0.5, 0.3, 0.2, 1, "braces",
                  xs=[-(w / 2 + 0.9), w / 2 + 0.9], embed=0.6)
    return (s, 1.6, z + h / 2)


def kura_door(mb, Ff, s, w, h, z0=0.0, m=PLK, lit=False):
    """porta de kura: moldura em 3 degraus de reboco, folhas de ferro com cintas e argolas, soleira de pedra,
    capelo de telha em consolos"""
    x0, x1 = s - w / 2, s + w / 2
    for o, d in ((1.2, 1.1), (0.8, 0.86), (0.4, 0.64)):
        oi = o - 0.4
        for a, b, c, e in ((x0 - o, x0 - oi, z0, z0 + h + o), (x1 + oi, x1 + o, z0, z0 + h + o),
                           (x0 - oi, x1 + oi, z0 + h + oi, z0 + h + o)):
            bb(mb, Ff, a, b, -0.3, d, c, e, m, 0.05)
    for k in (-1, 1):
        xa, xb = (x0, s - 0.03) if k < 0 else (s + 0.03, x1)
        bb(mb, Ff, xa, xb, 0.32, 0.48, z0 + 0.05, z0 + h, IRON)          # folha a frente da faixa namako (>= 0,12)
        for zz in (z0 + 0.9, z0 + h * 0.5, z0 + h - 0.9):
            bb(mb, Ff, xa + 0.1, xb - 0.1, 0.48, 0.56, zz - 0.18, zz + 0.18, IRON)
        mb.rod(Ff.p(s + k * 0.55, 0.56, z0 + h * 0.5 - 0.45), Ff.p(s + k * 0.55, 0.78, z0 + h * 0.5 - 0.45), 0.2,
               IRON, 8)
    bb(mb, Ff, x0 - 1.4, x1 + 1.4, -0.3, 1.5, z0 - 0.45, z0 + 0.04, ST, 0.08)
    roof_pent(mb, sub(Ff, s, 0.0, 0.0), w + 4.2, 2.4, z0 + h + 2.4, 0.45, 0.34, 0.25, 0, "brackets",
              xs=[-(w / 2 + 1.5), w / 2 + 1.5], embed=0.6)
    return dict(center=(s, 0.0, z0), glow=(s, 1.8, z0 + h * 0.6))


# ------------------------------------------------------------------ VARANDA, ESCADAS, GUARDAS, CERCAS
def steps_to(mb, Ff, x, y0, z_top, z_ground, w=3.6):
    """pedras de degrau naturais (kutsunugi-ishi) do chao ate z_top, saindo de y0 para +y"""
    dz = z_top - z_ground
    if dz < 0.25:
        return
    n = max(1, int(math.ceil(dz / 0.78 - 0.05)))
    rise = dz / n
    for i in range(n):
        zt = z_top - rise * i
        if zt <= z_ground + 0.12:
            break
        ya = y0 + 0.05 + i * 1.35
        wi = w - i * 0.35
        cy_ = ya + 0.8
        kk = (1.0, 0.93, 1.04, 0.97, 1.02, 0.95, 1.05, 0.96, 1.0, 0.94)
        poly = [(x + wi / 2 * kk[(j + i * 3) % 10] * math.cos(2 * math.pi * j / 10 + 0.2 * i),
                 cy_ + 0.8 * kk[(j + i * 3 + 5) % 10] * math.sin(2 * math.pi * j / 10 + 0.2 * i)) for j in range(10)]
        ext(mb, Ff, poly, "z", z_ground - 0.25, zt - 0.02, STP, 0.16)


def engawa(mb, Ff, x0, x1, depth, ground, z=0.35, step_x=None, posts=True, lod=0):
    """varanda de tabuas (engawa) na face Ff (y=0 face dos pilares, z=0 piso do soco): tabuas ao comprido com
    fresta, viga de borda (engamachi) e de topo, barrotes, pilaretes (tsuka) sobre pedras e degrau de pedra"""
    nb = max(2, int(round((depth - 0.1) / 0.85)))
    bw = (depth - 0.1) / nb
    for i in range(nb):
        ya = 0.1 + i * bw
        bb(mb, Ff, x0, x1, ya + 0.05, ya + bw - 0.04, z - 0.22, z, WM, 0.03)
    bb(mb, Ff, x0, x1, depth - 0.55, depth, z - 0.88, z - 0.22, WD, B)
    for xe in (x0, x1 - 0.45):
        bb(mb, Ff, xe, xe + 0.45, 0.1, depth - 0.55, z - 0.88, z - 0.22, WD, B)
    for xx in even(x0 + 0.45, x1 - 0.45, 2.6)[1:-1] if x1 - x0 > 6 else []:
        bb(mb, Ff, xx - 0.2, xx + 0.2, 0.1, depth - 0.55, z - 0.62, z - 0.22, WD)
    if posts and z - 0.88 > ground + 0.5:
        n = max(2, int(round((x1 - x0) / 3.6)) + 1)
        for i in range(n):
            xp = x0 + 0.5 + (x1 - x0 - 1.0) * i / (n - 1)
            rock_base(mb, Ff, xp, depth - 0.28, ground, 0.5, 0.32)
            bb(mb, Ff, xp - 0.24, xp + 0.24, depth - 0.52, depth - 0.04, ground + 0.3, z - 0.86, WD, 0.04)
    if step_x is not None:
        steps_to(mb, Ff, step_x, depth, z - 0.75, ground, 3.4)


def stair_stone(mb, F, w, n, rise=0.75, tread=1.9, cheeks=True, m=STP, riser_m=STD, cheek_m=ST, z_floor=None):
    """escada de pedra: pisada com focinho chanfrado saliente 0,12, espelho escuro recuado, banzos de pedra em
    degraus com capa. F no pe do 1o espelho (centro), sobe para +y"""
    TH, NOSE = 0.3, 0.12
    zf = -0.3 if z_floor is None else z_floor
    for i in range(n):
        zt = rise * (i + 1)
        bb(mb, F, -w / 2 + 0.04, w / 2 - 0.04, tread * i, tread * (i + 1) + 0.02, zf, zt - TH - 0.02, riser_m)
        stone(mb, F, -w / 2, w / 2, zt - TH, zt, tread * (i + 1) + 0.02, tread * i - NOSE, tread * i - NOSE, 0.07, m)
    if cheeks:
        for s in (-1, 1):
            for i in range(n):
                zt = rise * (i + 1) + 0.55
                xa, xb = (w / 2, w / 2 + 1.0) if s > 0 else (-w / 2 - 1.0, -w / 2)
                Fc = sub(F, (xa + xb) / 2, 0.0, 0.0, -s * math.pi / 2)      # +y do banzo = para FORA da escada
                ya_, yb2 = tread * i - 0.12, (tread * (i + 1) + 0.12 if i == n - 1 else tread * (i + 1) - 0.02)
                u0, u1 = (-yb2, -ya_) if s > 0 else (ya_, yb2)                 # x do banzo = -+y da escada
                stone(mb, Fc, u0, u1, zf, zt, -0.5, 0.5, 0.5, 0.1, cheek_m)
    return F.p(0.0, tread * n, rise * n)


def stair_wood(mb, F, w, n, rise=0.75, tread=1.4, rail=True, rail_h=3.6):
    """escada de madeira: 2 banzos inclinados, degraus encaixados (sem espelho), pilaretes e corrimao"""
    L, H = tread * n, rise * n
    xs = w / 2 + 0.16
    for s in (-1, 1):
        beam(mb, F, (s * xs, -0.25, 0.1), (s * xs, L + 0.1, H + 0.25), 0.3, 1.0, WD, 0.06)
    for i in range(n):
        zt = rise * (i + 1)
        bb(mb, F, -w / 2 - 0.02, w / 2 + 0.02, tread * i + 0.05, tread * (i + 1) - 0.02, zt - 0.22, zt, WM, 0.03)
    if rail:
        for s in (-1, 1):
            x = s * (xs + 0.05)
            for y, z in ((0.1, 0.0), (L - 0.2, H)):
                bb(mb, F, x - 0.2, x + 0.2, y - 0.2, y + 0.2, z, z + rail_h + 0.3, WD, 0.06)
            beam(mb, F, (x, -0.1, rail_h + 0.1), (x, L + 0.05, H + rail_h + 0.1), 0.34, 0.26, WD, 0.04)
            beam(mb, F, (x, 0.0, rail_h * 0.5), (x, L - 0.3, H + rail_h * 0.5), 0.16, 0.2, WD)
    return F.p(0.0, L, H)


def railing(mb, F, pts, h=4.0, base=0.0, step=3.2, m=WD):
    """guarda-corpo de madeira: pilaretes chanfrados com capitel, corrimao (kasagi) que passa das pontas, travessa
    media e baixa, montante curto no meio de cada vao. pts = [(x, y)] locais; z = base"""
    P = [Vector((p[0], p[1], 0.0)) for p in pts]
    nodes = []
    for i, (a, b) in enumerate(zip(P, P[1:])):
        d = b - a
        ln = d.length
        if ln < 0.3:
            continue
        nseg = max(1, int(math.ceil(ln / step)))
        for j in range(nseg + (1 if i == len(P) - 2 else 0)):
            nodes.append(a + d * (j / nseg))
        ang = math.atan2(d.y, d.x)
        c = (a + b) / 2
        e0 = 0.35 if i == 0 else 0.0
        e1 = 0.35 if i == len(P) - 2 else 0.0
        cc = c + d.normalized() * (e1 - e0) / 2
        bx(mb, F, cc.x, cc.y, base + h - 0.15 + (0.02 if i % 2 else 0.0), ln + e0 + e1, 0.36, 0.3, m, 0.05, rz=ang)
        bx(mb, F, c.x, c.y, base + h * 0.55, ln, 0.18, 0.22, m, 0.03, rz=ang)
        bx(mb, F, c.x, c.y, base + 0.5, ln, 0.2, 0.24, m, 0.03, rz=ang)
        for j in range(nseg):
            q = a + d * ((j + 0.5) / nseg)
            bx(mb, F, q.x, q.y, base + (0.62 + h * 0.55 - 0.11) / 2, 0.16, 0.16, h * 0.55 - 0.11 - 0.62, m, 0.0, rz=ang)
    for q in nodes:
        bx(mb, F, q.x, q.y, base + (h - 0.3) / 2, 0.42, 0.42, h - 0.3, m, 0.06)
        bx(mb, F, q.x, q.y, base + h + 0.08, 0.3, 0.3, 0.16, m, 0.04)


def fence(mb, F, pts, h=3.2, style="ripa", step=4.0):
    """cerca baixa: 'ripa' = mouroes de capitel piramidal + 2 travessas + ripas verticais; 'bamboo' = yotsume-gaki
    (mouroes de bambu grosso com nos, travessas e montantes alternados de bambu, amarras escuras)"""
    P = [Vector((p[0], p[1], 0.0)) for p in pts]
    for i, (a, b) in enumerate(zip(P, P[1:])):
        d = b - a
        ln = d.length
        if ln < 0.3:
            continue
        u = d.normalized()
        nv = Vector((-u.y, u.x, 0.0))
        ang = math.atan2(d.y, d.x)
        nseg = max(1, int(math.ceil(ln / step)))
        posts_ = [a + d * (j / nseg) for j in range(nseg + (1 if i == len(P) - 2 else 0))]
        if style == "bamboo":
            for q in posts_:
                mb.cyl(0.22, h + 0.4, F.p(q.x, q.y, (h + 0.4) / 2 - 0.1), (0, 0, 0), BAMBOO, 7, bevel=0.0)
                for zz in (0.9, 2.2, h + 0.1):
                    mb.cyl(0.25, 0.08, F.p(q.x, q.y, zz), (0, 0, 0), BAMBOO, 7, bevel=0.0)
            for zz in (0.7, h * 0.5, h - 0.25):
                o = nv * 0.26
                mb.rod(F.p(a.x + o.x, a.y + o.y, zz), F.p(b.x + o.x, b.y + o.y, zz), 0.09, BAMBOO_G if zz > 1 else BAMBOO, 6)
            nvb = max(2, int(round(ln / 0.95)))
            for j in range(1, nvb):
                q = a + d * (j / nvb)
                o = nv * (0.12 if j % 2 else 0.4)
                mb.rod(F.p(q.x + o.x, q.y + o.y, -0.1), F.p(q.x + o.x, q.y + o.y, h + 0.05), 0.08, BAMBOO, 6)
                for zz in (0.7, h * 0.5, h - 0.25):
                    bx(mb, F, q.x + nv.x * 0.26, q.y + nv.y * 0.26, zz, 0.18, 0.5, 0.16, WD, 0.0, rz=ang)
        else:                                     # tategoshi: mouroes, 2 travessas, ripas e capa (kasagi) continua
            for q in posts_:
                bx(mb, F, q.x, q.y, (h + 0.15) / 2 - 0.15, 0.5, 0.5, h + 0.15, WD, 0.06, rz=ang)
            c = (a + b) / 2
            bx(mb, F, c.x + nv.x * 0.15, c.y + nv.y * 0.15, h + 0.12, ln + (0.5 if i in (0, len(P) - 2) else 0.0), 0.82, 0.22,
               WD, 0.05, rz=ang)
            for zz in (h * 0.22, h * 0.74):
                bx(mb, F, c.x + nv.x * 0.32, c.y + nv.y * 0.32, zz, ln, 0.16, 0.28, WM, 0.03, rz=ang)
            nr = max(2, int(round(ln / 0.52)))
            for j in range(nr):
                q = a + d * ((j + 0.5) / nr)
                o = nv * 0.45
                bx(mb, F, q.x + o.x, q.y + o.y, (h + 0.12) / 2, 0.34, 0.1, h - 0.12, WM, 0.0, rz=ang)


def balcony(mb, Ff, x0, x1, depth, z, rail_h=3.6, lod=0):
    """sacada em consolos (misulas) sob a viga de borda, piso de tabuas e guarda-corpo nos 3 lados"""
    for xx in [x0 + 0.4] + even(x0 + 0.4, x1 - 0.4, 3.4)[1:-1] + [x1 - 0.4]:
        bracket(mb, Ff, xx, -0.4, z - 0.22, depth + 0.3, 0.42, 1.3)
    nb = max(2, int(round(depth / 0.8)))
    for i in range(nb):
        ya = 0.05 + (depth - 0.05) * i / nb
        bb(mb, Ff, x0, x1, ya + 0.03, ya + (depth - 0.05) / nb - 0.03, z - 0.22, z, WM, 0.03)
    bb(mb, Ff, x0, x1, depth - 0.45, depth, z - 0.7, z - 0.2, WD, 0.05)
    railing(mb, Ff, [(x0 + 0.25, 0.1), (x0 + 0.25, depth - 0.22), (x1 - 0.25, depth - 0.22), (x1 - 0.25, 0.1)],
            rail_h, z)


# ------------------------------------------------------------------ MURO E PORTAO
def garden_wall(mb, F, L, h=6.0, th=1.2, lod=1):
    """muro de jardim (tsuiji): soco de pedra em blocos, reboco, viga de madeira e cobertura de telha em 2 aguas
    com cumeeira propria. F no centro da base, muro ao longo de x"""
    for sy in (1, -1):
        Ff = sub(F, 0.0, 0.0, 0.0, 0.0 if sy > 0 else math.pi)
        x = -L / 2
        k = 0
        while x < L / 2 - 0.3:
            x2 = min(L / 2, x + (2.6, 3.4, 2.2, 3.0)[k % 4])
            if L / 2 - x2 < 0.9:
                x2 = L / 2
            stone(mb, Ff, x + 0.05, x2 - 0.05, -0.3, 1.05, -0.2, th / 2 + 0.28, th / 2 + 0.22, 0.1)
            x = x2
            k += 1
    bb(mb, F, -L / 2 + 0.05, L / 2 - 0.05, -th / 2, th / 2, 1.0, h - 0.5, PL)
    bb(mb, F, -L / 2, L / 2, -th / 2 - 0.12, th / 2 + 0.12, h - 0.62, h - 0.1, WD, 0.04)
    roof_gable(mb, F, L, th + 0.24, h - 0.08, 0.6, 0.55, 0.25, 0.0, 0.26, 1, PL, "none", False, RT, 0.6, 0.9, 0.4)


def gate_mon(mb, F, w=8.5, h=9.5, depth=3.2, open_=True, lod=0):
    """portao de cumeeira (munamon): 2 pilares sobre pedra, travessa (kabuki) que passa dos pilares, linha baixa,
    vigas de apoio do telhado, montante de cumeeira, telhado kirizuma com onigawara, 2 folhas de tabuas abertas para
    DENTRO (-y) e soleira de pedra. F no centro da soleira, +y = rua"""
    hw = w / 2 + 0.55
    for s in (-1, 1):
        rock_base(mb, F, s * hw, 0.0, 0.0, 1.05, 0.4)
        bb(mb, F, s * hw - 0.65, s * hw + 0.65, -0.65, 0.65, 0.3, h, WD, B)
        bb(mb, F, s * hw - 0.42, s * hw + 0.42, -depth / 2 - 0.4, depth / 2 + 0.4, h - 0.05, h + 0.65, WD, B)
        beam(mb, F, (s * hw, -0.4, h - 2.6), (s * hw, -depth / 2 - 0.1, h + 0.1), 0.3, 0.34, WD)
        beam(mb, F, (s * hw, 0.4, h - 2.6), (s * hw, depth / 2 + 0.1, h + 0.1), 0.3, 0.34, WD)
    bb(mb, F, -hw - 1.4, hw + 1.4, -0.5, 0.5, h - 1.25, h - 0.45, WD, B)
    bb(mb, F, -hw, hw, -0.35, 0.35, h - 3.1, h - 2.6, WD, 0.05)
    bb(mb, F, -hw, hw, -0.75, 0.75, -0.3, 0.22, ST, 0.08)
    info = roof_gable(mb, F, 2 * hw + 1.1, depth, h + 0.65, 0.62, 1.2, 1.4, 0.4, 0.42, 1, PL, "none", False)
    for s in (-1, 1):
        bb(mb, F, s * hw - 0.25, s * hw + 0.25, -0.25, 0.25, h + 0.65, info["zr"] - 0.4, WD, 0.04)
    beam(mb, F, (-hw - 1.3, 0.0, info["zr"] - 0.75), (hw + 1.3, 0.0, info["zr"] - 0.75), 0.55, 0.65, WD, 0.05)
    lw = w / 2 - 0.02
    zt = h - 3.15
    for s in (-1, 1):
        hx = s * (w / 2)
        if open_:
            Fl = sub(F, hx, -0.3, 0.0, -s * math.radians(84.0))
            xa, xb = (-lw, 0.0) if s > 0 else (0.0, lw)
        else:
            Fl = sub(F, 0.0, -0.3, 0.0)
            xa, xb = (0.02, w / 2) if s > 0 else (-w / 2, -0.02)
        bb(mb, Fl, xa, xb, -0.12, 0.12, 0.3, zt, WM)
        for zz in (1.2, zt * 0.5 + 0.3, zt - 0.8):
            bb(mb, Fl, xa + 0.15, xb - 0.15, -0.24, -0.12, zz - 0.22, zz + 0.22, WD, 0.03)
        for zz in (1.2, zt - 0.8):
            e = xb if s > 0 else xa
            bb(mb, Fl, e - 1.4 if s > 0 else e, e if s > 0 else e + 1.4, 0.12, 0.18, zz - 0.12, zz + 0.12, IRON)
    return info


# ------------------------------------------------------------------ LANTERNAS
def _box_lantern(mb, F, c, hx, hy, hz, frame=WD, paper=LGLOW, cap_m=RT, iron_top=IRON, tray=True):
    """caixa de lanterna: 4 montantes, travessa de cima, bandeja, papel/vidro RECUADO 0,15 da armacao, cruzetas na
    frente do papel, chapeu de 4 aguas com beiral e argola/ponteira. c = (x, y, z da base)"""
    cx, cy, z0 = c
    t = 0.16
    bb(mb, F, cx - hx + 0.15, cx + hx - 0.15, cy - hy + 0.15, cy + hy - 0.15, z0 + 0.05, z0 + hz - 0.12, paper)
    for sx in (-1, 1):
        for sy in (-1, 1):
            bb(mb, F, cx + sx * hx - (t if sx > 0 else 0), cx + sx * hx + (0 if sx > 0 else t),
               cy + sy * hy - (t if sy > 0 else 0), cy + sy * hy + (0 if sy > 0 else t), z0, z0 + hz, frame)
    bb(mb, F, cx - hx, cx + hx, cy - hy, cy + hy, z0 + hz - 0.16, z0 + hz, frame)
    if tray:
        bb(mb, F, cx - hx - 0.08, cx + hx + 0.08, cy - hy - 0.08, cy + hy + 0.08, z0 - 0.14, z0 + 0.05, frame, 0.03)
    zm = z0 + hz * 0.52
    for sx in (-1, 1):
        x = cx + sx * (hx - 0.06)
        bb(mb, F, x - 0.04, x + 0.04, cy - hy + t, cy + hy - t, zm - 0.04, zm + 0.04, frame)
        bb(mb, F, x - 0.04, x + 0.04, cy - 0.04, cy + 0.04, z0 + 0.05, z0 + hz - 0.16, frame)
    for sy in (-1, 1):
        y = cy + sy * (hy - 0.06)
        bb(mb, F, cx - hx + t, cx + hx - t, y - 0.04, y + 0.04, zm - 0.04, zm + 0.04, frame)
        bb(mb, F, cx - 0.04, cx + 0.04, y - 0.04, y + 0.04, z0 + 0.05, z0 + hz - 0.16, frame)
    zr = hip_cap(mb, F, (cx, cy), hx + 0.04, hy + 0.04, z0 + hz, 0.32, min(hx, hy) * 0.75, 0.1, cap_m, 0.1)
    lathe(mb, F, (cx, cy, zr - 0.05), [(0.16, 0.0), (0.2, 0.12), (0.1, 0.26), (0.13, 0.38), (0.02, 0.55)], 6, iron_top)
    return (cx, cy, z0 + hz * 0.5), zr + 0.5


def lantern_post(mb, F, h=8.6, arm=1.9, light_name=None, energy=40.0):
    """lanterna de poste: pedra-base, poste chanfrado com capitel e chapeu, braco com mao-francesa, gancho de ferro
    e caixa de papel pendurada (armacao, papel recuado, cruzetas, chapeu de telha, ponteira). F no pe; braco p/ +y"""
    rock_base(mb, F, 0.0, 0.0, 0.0, 0.95, 0.5)
    bb(mb, F, -0.3, 0.3, -0.3, 0.3, 0.3, h, WD, 0.08)
    bb(mb, F, -0.42, 0.42, -0.42, 0.42, h, h + 0.16, WD, 0.04)
    hip_cap(mb, F, (0.0, 0.0), 0.42, 0.42, h + 0.16, 0.18, 0.32, 0.1, RT, 0.05)
    bb(mb, F, -0.2, 0.2, -0.25, arm + 0.3, h - 0.95, h - 0.58, WD, 0.04)
    beam(mb, F, (0.0, 0.2, h - 2.5), (0.0, arm * 0.6, h - 0.9), 0.18, 0.2, WD)
    ztop = h - 0.95
    mb.rod(F.p(0.0, arm, ztop + 0.05), F.p(0.0, arm, ztop - 0.6), 0.05, IRON, 6)
    hz = 1.35
    capz = 0.55
    z0 = ztop - 0.6 - capz - hz
    c, _ = _box_lantern(mb, F, (0.0, arm, z0), 0.55, 0.55, hz)
    if light_name:
        light(light_name, "POINT", F.p(*c), energy, WARM, 0.2)
    return F.p(*c)


def lantern_wall(mb, F, light_name=None, energy=30.0, out=1.3):
    """lanterna de parede: espelho de ferro com 2 parafusos, braco e mao-francesa de ferro, base e caixa pequena
    (armacao de ferro, vidro/papel recuado, chapeu de ferro). F na face da parede (+y fora), z = altura do braco"""
    bb(mb, F, -0.28, 0.28, -0.05, 0.12, -1.0, 0.85, IRON, 0.03)
    for zz in (-0.7, 0.55):
        mb.rod(F.p(0.0, 0.1, zz), F.p(0.0, 0.2, zz), 0.07, IRON, 6)
    bb(mb, F, -0.08, 0.08, 0.05, out + 0.3, -0.12, 0.04, IRON)
    beam(mb, F, (0.0, 0.1, -0.85), (0.0, out * 0.7, -0.1), 0.1, 0.1, IRON)
    bb(mb, F, -0.48, 0.48, out - 0.48, out + 0.48, 0.04, 0.12, IRON, 0.02)
    c, _ = _box_lantern(mb, F, (0.0, out, 0.14), 0.4, 0.4, 0.95, IRON, LGLOW, IRON, IRON, tray=False)
    if light_name:
        light(light_name, "POINT", F.p(*c), energy, WARM, 0.15)
    return F.p(*c)


def toro(mb, F, style="kasuga", s=1.0, light_name=None, energy=35.0, m=ST):
    """lanterna de pedra (pedestal): 'kasuga' (sextavada alta: base, fuste com aneis, plataforma, camara com 4
    aberturas recuadas e 2 paineis, chapeu com pontas enroladas, joia hoju), 'yukimi' (3 pes, chapeu largo,
    baixa: beira d'agua), 'oki' (pequena quadrada de caminho). Luz SO dentro da camara."""
    S_ = lambda prof: [(r * s, z * s) for r, z in prof]
    if style == "yukimi":
        for i in range(3):
            a = 2 * math.pi * i / 3 + math.pi / 6
            ca, sa = math.cos(a), math.sin(a)
            beam(mb, F, (1.25 * s * ca, 1.25 * s * sa, 0.0), (0.7 * s * ca, 0.7 * s * sa, 1.3 * s), 0.34 * s, 0.34 * s, m, 0.05)
            beam(mb, F, (0.7 * s * ca, 0.7 * s * sa, 1.3 * s), (0.62 * s * ca, 0.62 * s * sa, 1.75 * s), 0.34 * s, 0.34 * s, m, 0.05)
        lathe(mb, F, (0, 0, 0), S_([(0.95, 1.6), (1.0, 1.85), (0.85, 1.95)]), 6, m)
        zc0, zc1, rc = 1.95, 3.0, 0.72
        zk = 3.0
        kasa = [(0.8, 0.0), (2.2, 0.18), (2.25, 0.36), (1.4, 0.62), (0.5, 0.95), (0.35, 1.02)]
        hoju_z = zk + 1.02
    elif style == "oki":
        lathe(mb, F, (0, 0, 0), S_([(1.0, -0.2), (1.0, 0.3), (0.85, 0.42)]), 4, m, math.pi / 4)
        zc0, zc1, rc = 0.42, 1.55, 0.7
        zk = 1.55
        kasa = [(0.8, 0.0), (1.35, 0.15), (1.35, 0.3), (0.7, 0.62), (0.3, 0.78)]
        hoju_z = zk + 0.78
    else:
        lathe(mb, F, (0, 0, 0), S_([(1.3, -0.2), (1.3, 0.38), (1.08, 0.64), (0.62, 0.8)]), 6, m)
        lathe(mb, F, (0, 0, 0), S_([(0.44, 0.78), (0.44, 1.55), (0.53, 1.62), (0.53, 1.78), (0.42, 1.86),
                                    (0.4, 2.95), (0.5, 3.02), (0.5, 3.1)]), 8, m)
        lathe(mb, F, (0, 0, 0), S_([(0.55, 3.08), (1.08, 3.52), (1.08, 3.82), (0.98, 3.9)]), 6, m)
        zc0, zc1, rc = 3.9, 5.32, 0.86
        zk = 5.32
        kasa = [(0.95, 0.0), (1.72, 0.14), (1.8, 0.32), (1.28, 0.6), (0.58, 1.0), (0.4, 1.1)]
        hoju_z = zk + 1.1
    n = 4 if style == "oki" else 6
    rot = math.pi / 4 if n == 4 else 0.0
    zc0, zc1, rc = zc0 * s, zc1 * s, rc * s
    # camara: nucleo aceso recuado + montantes de pedra nos cantos + verga anel + 2 paineis cheios (kasuga)
    lathe(mb, F, (0, 0, 0), [(rc * 0.66, zc0 + 0.04), (rc * 0.66, zc1 - 0.1)], n, LGLOW, rot)
    for i in range(n):
        a = rot + 2 * math.pi * i / n
        bx(mb, F, rc * 0.9 * math.cos(a), rc * 0.9 * math.sin(a), (zc0 + zc1) / 2, 0.3 * s, 0.3 * s, zc1 - zc0, m, 0.03,
           rz=a)
    lathe(mb, F, (0, 0, 0), [(rc * 1.02, zc1 - 0.22 * s), (rc * 1.06, zc1 - 0.18 * s), (rc * 1.06, zc1 + 0.02),
                             (rc * 0.9, zc1 + 0.06)], n, m, rot)
    if style == "oki":
        lathe(mb, F, (0, 0, 0), [(rc * 1.02, zc0 - 0.02), (rc * 1.06, zc0 + 0.14 * s), (rc * 0.95, zc0 + 0.18 * s)],
              n, m, rot)
    ap = rc * math.cos(math.pi / n)
    if style == "kasuga":
        for i in (1, 4):
            a = rot + 2 * math.pi * (i + 0.5) / n
            bx(mb, F, ap * 0.86 * math.cos(a), ap * 0.86 * math.sin(a), (zc0 + zc1) / 2, rc * 0.95, 0.16 * s,
               zc1 - zc0 - 0.05, m, 0.02, rz=a + math.pi / 2)
            bx(mb, F, ap * 0.95 * math.cos(a), ap * 0.95 * math.sin(a), (zc0 + zc1) / 2 + 0.1 * s, 0.34 * s, 0.06 * s,
               0.34 * s, STD, 0.0, rz=a + math.pi / 2)
    else:
        for i in range(n):
            a = rot + 2 * math.pi * (i + 0.5) / n
            bx(mb, F, ap * 0.9 * math.cos(a), ap * 0.9 * math.sin(a), zc0 + 0.18 * s, rc * 0.95, 0.12 * s, 0.3 * s, m,
               0.0, rz=a + math.pi / 2)
    # chapeu + pontas enroladas (warabite) + joia (hoju) com colarinho de petalas
    kz = zk * s
    lathe(mb, F, (0, 0, kz), S_(kasa), n, m, rot)
    if style != "oki":
        rk = kasa[1][0] * s
        for i in range(n):
            a = rot + 2 * math.pi * i / n
            bx(mb, F, rk * math.cos(a), rk * math.sin(a), kz + 0.3 * s, 0.34 * s, 0.26 * s, 0.34 * s, m, 0.04,
               ry=-0.6, rz=a)
    hz = hoju_z * s
    lathe(mb, F, (0, 0, hz), S_([(0.34, 0.0), (0.46, 0.14), (0.3, 0.26), (0.3, 0.3), (0.4, 0.46), (0.34, 0.66),
                                 (0.14, 0.86), (0.02, 0.98)]), 8, m)
    c = (0.0, 0.0, (zc0 + zc1) / 2)
    if light_name:
        light(light_name, "POINT", F.p(*c), energy, WARM, 0.2)
    return F.p(*c)


def bench(mb, F, x, y, L=5.0, w=2.0, h=1.7, ang=0.0, z=0.0):
    """banco de casa de cha (shogi): tampo de 3 tabuas, quadro, 4 pes com travessas"""
    Fb_ = sub(F, x, y, z, ang)
    for i in range(3):
        bb(mb, Fb_, -L / 2, L / 2, -w / 2 + i * w / 3 + 0.03, -w / 2 + (i + 1) * w / 3 - 0.03, h - 0.2, h, WM, 0.03)
    bb(mb, Fb_, -L / 2 + 0.12, L / 2 - 0.12, -w / 2 + 0.08, w / 2 - 0.08, h - 0.44, h - 0.2, WD)
    for sx in (-1, 1):
        for sy in (-1, 1):
            bb(mb, Fb_, sx * (L / 2 - 0.35) - 0.13, sx * (L / 2 - 0.35) + 0.13, sy * (w / 2 - 0.3) - 0.13,
               sy * (w / 2 - 0.3) + 0.13, 0.0, h - 0.44, WD)
        bb(mb, Fb_, sx * (L / 2 - 0.35) - 0.08, sx * (L / 2 - 0.35) + 0.08, -w / 2 + 0.3, w / 2 - 0.3, 0.45, 0.6, WD)
    bb(mb, Fb_, -L / 2 + 0.35, L / 2 - 0.35, -0.07, 0.07, 0.45, 0.6, WD)


# ------------------------------------------------------------------ CASA (montagem + variacoes dirigidas)
DEFAULTS = dict(W=18.0, D=14.0, h=12.5, plinth=("ishigaki", 1.6), roof="irimoya", ridge="long", pitch=0.55,
                over=3.4, gable=0.68, g_over=1.3, lift=0.9, tv=0.5, front="auto", back="auto", left="auto",
                right="auto", door_w=DOOR_W, door_h=DOOR_H, plaster="base", engawa=(), engawa_d=3.0, stories=1,
                upper=None, kura=False, lit=True, noren=None, lod=0, back_lod=1, steps=True, gable_style="timber")


def auto_bays(L, kind="side", door=False):
    """vaos automaticos (variacao dirigida pelo comprimento): laterais = reboco com 1 janela alta no meio; fundos =
    tabuas/reboco com janelas baixas alternadas"""
    n = max(1, int(round((L - 2 * CP) / 5.2)))
    if kind == "back":
        return ["plain" if i % 2 == 0 else "koshi" for i in range(n)] if n > 2 else ["plain"] * n
    out = ["plaster"] * n
    if n >= 2:
        out[n // 2] = "shoji"
    return out


PRESETS = {
    # V1 - casa de cha (chaya) ABERTA: o 1o edificio depois do torii (gesto: aberta). Pavilhao de 3 vaos livres na
    #      frente, fundo fechado de tabuas com janela baixa, noren no vao do meio, telhado irimoya baixo e largo
    "V1": dict(W=14.0, D=10.0, h=10.8, plinth=("soco", 1.0), roof="irimoya", pitch=0.52, over=3.2, gable=0.7,
               front=["open", {"t": "open", "noren": True}, "open"], back=["plain", "koshi", "plain"],
               left=["open", "plaster"], right=["shoji", "plaster"], plaster="base", engawa=("F",), engawa_d=2.6,
               steps=True, benches=((-2.6, 0.6, 4.6, 0.0), (3.2, -1.2, 3.6, math.pi / 2)), gesture="aberta"),
    # V2 - minka terrea: porta de correr com noren, 2 janelas koshi, engawa do lado do jardim (R), irimoya baixo
    "V2": dict(W=22.0, D=16.0, h=12.5, plinth=("ishigaki", 1.6), roof="irimoya", pitch=0.54, over=3.4, gable=0.66,
               front=["plain", "koshi", "door", "koshi", "plain"], back="auto", left="auto",
               right=["plain", "door", "plain"], plaster="base", engawa=("R",), noren=True, gesture="engawa"),
    # V3 - oficina (afiador/carpinteiro): FRENTE DE LOJA (gesto) - 2 vaos de shitomi erguido + banca, porta de
    #      tabuas no lado, kirizuma de empena para os lados, reboco ocre, capelo (hisashi) sobre a loja
    "V3": dict(W=18.0, D=14.0, h=13.5, plinth=("soco", 1.2), roof="kirizuma", ridge="x", pitch=0.6, over=3.0,
               g_over=2.0, door_h=7.4, front=["plain", "shop", "shop", "plaster"], back="auto", left="auto",
               right=["plaster", "itado", "plaster"], plaster="ochre", hisashi_front=True, hisashi_z=11.8,
               gesture="loja"),
    # V4 - kura de 2 pisos: TORRE BRANCA (gesto) - reboco grosso, namako, cintas, janelas de kura com portas
    #      abertas, porta de ferro com capelo, ishigaki alto, kirizuma de empena de reboco
    "V4": dict(W=14.0, D=12.0, h=19.0, plinth=("ishigaki", 2.4), roof="kirizuma", ridge="x", pitch=0.62,
               over=2.6, g_over=1.6, kura=True, plaster="kura", gesture="torre branca"),
    # V5 - sobrado: SACADA (gesto) no 2o piso, trelica de rua (demaregoshi) no terreo, hisashi nos fundos, reboco
    #      frio, irimoya alto
    "V5": dict(W=22.0, D=16.0, h=11.8, plinth=("ishigaki", 1.8), roof="irimoya", pitch=0.56, over=3.4, gable=0.7,
               front=["plain", "lattice", {"t": "door", "noren": True}, "lattice", "plain"], back="auto",
               left="auto", right="auto", plaster="ash", stories=2,
               upper=dict(h=9.6, front=["plaster", "shoji", "shoji", "shoji", "plaster"], balcony=True),
               gesture="sacada"),
    # V6 - casa principal do mestre-ferreiro: porta ENTRAVEL 8 x 11 (open_door), engawa em L (frente + direita),
    #      irimoya grande de empena de tabuas, pe-direito 13,5. Portao e jardim: gate_mon + garden_wall (gesto)
    "V6": dict(W=30.0, D=20.0, h=14.0, plinth=("ishigaki", 2.0), roof="irimoya", pitch=0.54, over=3.8, gable=0.64,
               g_over=1.6, door_w=8.0, door_h=11.0,
               front=["plain", "koshi", "lattice", {"t": "open_door", "w": 8.6}, "lattice", "koshi", "plain"],
               back="auto", left="auto", right=["plain", "koshi", "door", "koshi", "plain"], plaster="base",
               engawa=("R",), engawa_d=3.2, gable_style="board", gesture="portao e jardim"),
}


def house(mb, F, spec, light_name=None, energy=80.0):
    """monta uma casa so com o kit. F no centro da planta, no chao; +y = frente. Ver DEFAULTS/PRESETS."""
    sp = dict(DEFAULTS)
    sp.update(spec)
    W, D, h = sp["W"], sp["D"], sp["h"]
    pst, ph = sp["plinth"]
    pl = PLASTER_TONES.get(sp["plaster"], sp["plaster"])
    lod = sp["lod"]
    info = dict(floor_z=F.o.z + ph, glow=[], doors=[], footprint=(W + 1.2, D + 1.2))
    foundation(mb, F, W + 1.2, D + 1.2, ph, pst, lod=lod)
    Fb = sub(F, z=ph)
    if sp["kura"]:
        return _kura_house(mb, F, Fb, sp, info, light_name, energy)
    bb(mb, Fb, -W / 2 + 0.9, W / 2 - 0.9, -D / 2 + 0.9, D / 2 - 0.9, 0.4, 0.66, WM)     # assoalho (vaos abertos)
    for bx_, by_, bl, ba in sp.get("benches", ()):
        bench(mb, Fb, bx_, by_, bl, ang=ba, z=0.66)
    lit = sp["lit"]
    lit_of = (lambda k: k in lit) if isinstance(lit, (list, tuple, str)) else (lambda k: bool(lit))

    def faces_of(Fz):
        return {"F": ("front", sub(Fz, 0.0, D / 2), W, True), "B": ("back", sub(Fz, 0.0, -D / 2, 0.0, math.pi), W, True),
                "R": ("right", sub(Fz, W / 2, 0.0, 0.0, -math.pi / 2), D, False),
                "L": ("left", sub(Fz, -W / 2, 0.0, 0.0, math.pi / 2), D, False)}
    faces = faces_of(Fb)

    def floor_walls(Fz, hh, bays_of, door_h, nageshi=True, lodf=lambda k: lod):
        corner_posts(mb, Fz, W, D, 0.7, hh - 1.0)
        for k, (key, Ff, Lf, full) in faces_of(Fz).items():
            bays = bays_of.get(key, "auto")
            if bays == "auto" or bays is None:
                bays = auto_bays(Lf, "back" if k == "B" else "side")
            r = facade(mb, Ff, Lf, hh, bays, full, sp["door_w"], door_h, pl, lit_of(k), 0.9, lodf(k), -ph if Fz is Fb else 0.0,
                       sp["noren"], nageshi)
            info["glow"] += r["glow"]
            info["doors"] += r["doors"]
    floor_walls(Fb, h, sp, sp["door_h"], lodf=lambda k: max(lod, sp["back_lod"] if k == "B" else lod))
    htop = h
    if sp["stories"] == 2:
        up = dict(h=9.6, front="auto", back="auto", left="auto", right="auto", balcony=False)
        up.update(sp["upper"] or {})
        Fu = sub(Fb, z=h)
        floor_walls(Fu, up["h"], up, 3.6, nageshi=False, lodf=lambda k: max(lod, sp["back_lod"] if k == "B" else lod))
        htop = h + up["h"]
        if up["balcony"]:
            balcony(mb, sub(Fu, 0.0, D / 2), -W / 2 + 1.2, W / 2 - 1.2, 2.6, 0.7)
        else:
            roof_pent(mb, sub(Fb, 0.0, D / 2), W + 1.4, 2.8, h + 1.45, 0.42, 0.42, 0.35, lod, "brackets")
        roof_pent(mb, sub(Fb, 0.0, -D / 2, 0.0, math.pi), W + 1.4, 2.8, h + 1.45, 0.42, 0.42, 0.35, 1, "brackets")
    if sp.get("hisashi_front"):
        X_ = (W + 1.0) / 2
        roof_pent(mb, sub(Fb, 0.0, D / 2), W + 1.0, 3.2, sp.get("hisashi_z", h - 1.8), 0.4, 0.42, 0.35, lod, "brackets",
                  xs=[-X_ + 0.6, X_ - 0.6])
    along_x = (W >= D) if sp["ridge"] == "long" else (sp["ridge"] == "x")
    Fr, Wr, Dr = (Fb, W, D) if along_x else (sub(Fb, ang=math.pi / 2), D, W)
    if sp["roof"] == "kirizuma":
        r = roof_gable(mb, Fr, Wr, Dr, htop, sp["pitch"], sp["over"], sp["g_over"], sp["lift"] * 0.6, sp["tv"], lod,
                       pl, sp["gable_style"], back_lod=sp["back_lod"] if along_x else None)
    else:
        r = roof_hip(mb, Fr, Wr, Dr, htop, sp["roof"], sp["pitch"], sp["over"], sp["gable"], sp["g_over"], sp["lift"],
                     sp["tv"], lod, pl if sp["gable_style"] != "board" else WD, sp["gable_style"], True, RT,
                     sp.get("steep", 1.5), sp["back_lod"] if along_x else None)
    info.update(top_z=F.o.z + ph + htop, ridge_z=Fr.o.z + r["zr"], eave_z=Fr.o.z + r["eave_z"], roof=r,
                roof_along_x=along_x)
    # varandas e degraus
    ed = sp["engawa_d"]
    door_xs = {}
    for c, yaw in info["doors"]:
        for k, (key, Ffb, Lf, full) in faces.items():
            if abs(((yaw - Ffb.a + math.pi) % (2 * math.pi)) - math.pi) < 1e-3:
                lx = (c - Ffb.o)
                ca, sa = math.cos(-Ffb.a), math.sin(-Ffb.a)
                door_xs.setdefault(k, []).append(lx.x * ca - lx.y * sa)
    eng = sp["engawa"]
    for k in eng:
        key, Ff, Lf, full = faces[k]
        x0, x1 = -Lf / 2, Lf / 2
        if k == "F":                     # as varandas de frente/fundos cobrem o quadrado do canto (L)
            x1 += ed if "R" in eng else 0.0
            x0 -= ed if "L" in eng else 0.0
        if k == "B":
            x1 += ed if "L" in eng else 0.0
            x0 -= ed if "R" in eng else 0.0
        sx = door_xs.get(k, [0.0])[0]
        engawa(mb, Ff, x0, x1, ed, -ph, 0.35, sx if sp["steps"] else None)
    if sp["steps"]:
        for k, xs_ in door_xs.items():
            if k in sp["engawa"]:
                continue
            key, Ff, Lf, full = faces[k]
            for x in xs_:
                steps_to(mb, Ff, x, 0.6, SILL - 0.25, -ph, sp["door_w"] + 1.6)
    if light_name and info["glow"]:
        g = info["glow"][len(info["glow"]) // 2]
        light(light_name, "POINT", g, energy, WARM, 0.4)
    info["light_at"] = info["glow"][len(info["glow"]) // 2] if info["glow"] else None
    return info


def _kura_house(mb, F, Fb, sp, info, light_name, energy):
    W, D, h = sp["W"], sp["D"], sp["h"]
    lit = sp["lit"]
    h1 = h * 0.5
    kura_body(mb, Fb, W, D, h, PLK, 0.7, 3.4, (h1,), sp["lod"])
    Ff = sub(Fb, 0.0, D / 2 + 0.0)
    d = kura_door(mb, Ff, 0.0, 4.6, 8.0, 0.0, PLK)
    info["doors"].append((Ff.p(0.0, 0.0, 0.0), Ff.a))
    info["glow"].append(kura_window(mb, Ff, 0.0, h1 + 2.4, 2.8, 2.8, lit))
    for ang, Lf, Df in ((-math.pi / 2, D, W), (math.pi / 2, D, W), (math.pi, W, D)):
        Fs = sub(sub(Fb, 0.0, 0.0, 0.0, ang), 0.0, Df / 2)
        if ang == math.pi:
            kura_window(mb, Fs, 0.0, h1 + 2.4, 2.4, 2.4, False, True, True)
        else:
            kura_window(mb, Fs, 0.0, 4.6, 2.2, 2.2, False, True, True)
            kura_window(mb, Fs, 0.0, h1 + 2.4, 2.2, 2.2, lit and ang < 0, True, True)
    r = roof_gable(mb, Fb, W, D, h + 0.02, sp["pitch"], sp["over"], sp["g_over"], 0.4, sp["tv"], sp["lod"], PLK,
                   "kura", True, RT, 1.2)
    if sp["steps"]:
        steps_to(mb, Ff, 0.0, 1.5, -0.45, -sp["plinth"][1], 6.0)
    info.update(top_z=Fb.o.z + h, ridge_z=Fb.o.z + r["zr"], eave_z=Fb.o.z + r["eave_z"])
    if light_name:
        light(light_name, "POINT", info["glow"][0], energy, WARM, 0.4)
    info["light_at"] = info["glow"][0]
    return info


def house_cols(area, F, spec, info=None):
    """colisao simplificada de uma casa do kit: soco + corpo fechado (ou com o vao da porta aberta 'open_door' na
    frente, para casas entraveis o interior e de quem monta). Usa fm_lib.col_box (Parts invisiveis no Roblox)."""
    sp = dict(DEFAULTS)
    sp.update(spec)
    W, D, h = sp["W"], sp["D"], sp["h"]
    ph = sp["plinth"][1]
    htop = h + ((sp["upper"] or {}).get("h", 9.6) if sp["stories"] == 2 else 0.0)
    col_box(area, (W + 1.2, D + 1.2, ph), F.p(0, 0, ph / 2), F.r())
    fr = sp["front"] if isinstance(sp["front"], list) else []
    if any((b if isinstance(b, str) else b.get("t")) == "open_door" for b in fr):
        dw = sp["door_w"] + 0.2
        for sx in (-1, 1):
            ww = (W - dw) / 2
            col_box(area, (ww, 1.0, htop), F.p(sx * (dw / 2 + ww / 2), D / 2 - 0.5, ph + htop / 2), F.r())
        col_box(area, (dw, 1.0, htop - SILL - sp["door_h"]), F.p(0, D / 2 - 0.5, ph + (htop + SILL + sp["door_h"]) / 2), F.r())
        for sy in (-1,):
            col_box(area, (W, 1.0, htop), F.p(0, sy * (D / 2 - 0.5), ph + htop / 2), F.r())
        for sx in (-1, 1):
            col_box(area, (1.0, D, htop), F.p(sx * (W / 2 - 0.5), 0, ph + htop / 2), F.r())
    else:
        col_box(area, (W, D, htop), F.p(0, 0, ph + htop / 2), F.r())


# ================================================================== ESTUDIO (folhas de close-up; fora do jogo)
def _tris(ob):
    return sum(len(p.vertices) - 2 for p in ob.data.polygons) if ob and ob.type == "MESH" else 0


def _studio_pieces():
    """(nome, construtor(mb, F) -> dict(focus=(x,y,z) local, size=(w,h), dummy=(x,y) local, view=(lado, alto)))
    F de cada peca: +y local aponta para a camera; +x local fica a ESQUERDA da imagem"""
    P = []

    def add(name, fn):
        P.append((name, fn))

    def wall_house(mb, F, bays, L, plinth=("soco", 1.2), **kw):
        spec = dict(W=L, D=8.0, h=12.5, plinth=plinth, roof="kirizuma", ridge="x", pitch=0.6, over=3.0, g_over=1.8,
                    front=bays, back=["plaster"], left=["plaster"], right=["plaster"], steps=True)
        spec.update(kw)
        return house(mb, F, spec)

    add("01_fundacao_ishigaki", lambda mb, F: (foundation(mb, F, 12.0, 7.0, 2.4, "ishigaki"),
                                               dict(focus=(0, 3.5, 1.0), size=(16.0, 5.0), dummy=(8.0, 3.0)))[1])
    add("02_fundacao_soco", lambda mb, F: (foundation(mb, F, 12.0, 7.0, 1.4, "soco"),
                                           dict(focus=(0, 3.5, 0.6), size=(16.0, 4.5), dummy=(8.0, 3.0)))[1])

    def p_wall(mb, F):
        wall_house(mb, F, ["plain", "plaster", "plain"], 18.0)
        return dict(focus=(0, 4.0, 7.5), size=(21.0, 16.5), dummy=(-3.0, 6.0))
    add("03_parede_shinkabe", p_wall)

    def p_corner(mb, F):
        wall_house(mb, F, ["plain", "koshi"], 13.0)
        return dict(focus=(6.0, 4.4, 12.4), size=(8.0, 5.0), dummy=(9.0, 6.0), view=(1.3, -0.35))
    add("04_canto_pilar_viga_beiral", p_corner)

    def p_win(kind, extra=None, zf=6.4, hgt=8.5):
        def f(mb, F):
            wall_house(mb, F, ["plain", dict(t=kind, **(extra or {})), "plain"], 17.0)
            return dict(focus=(0, 4.0, zf), size=(10.0, hgt), dummy=(-4.4, 6.0))
        return f
    add("05_janela_koshi", p_win("koshi"))
    add("06_janela_shoji_capelo", p_win("shoji", {"hood": True}, 8.4, 8.0))
    add("07_janela_trelica_rua", p_win("lattice", None, 6.4, 10.5))

    def p_door(kind, extra=None, zf=5.8, hgt=10.5, **kw):
        def f(mb, F):
            wall_house(mb, F, ["plain", dict(t=kind, **(extra or {})), "plain"], 18.0, **kw)
            return dict(focus=(0, 4.0, zf), size=(11.0, hgt), dummy=(-4.6, 6.4))
        return f
    add("08_porta_hikido_noren", p_door("door", {"noren": True, "lit": True}))
    add("09_porta_itado", p_door("itado"))
    add("10_porta_aberta_8x11", p_door("open_door", {"w": 8.6}, 7.4, 13.5, door_w=8.0, door_h=11.0, h=14.0))

    def p_shop(mb, F):
        wall_house(mb, F, ["plain", "shop", "plaster"], 16.0)
        return dict(focus=(0, 5.0, 6.6), size=(13.0, 11.5), dummy=(3.6, 7.4), view=(0.6, 0.45))
    add("11_frente_de_loja", p_shop)

    def p_kura(mb, F):
        house(mb, F, PRESETS["V4"])
        return dict(focus=(0, 5.0, 13.0), size=(24.0, 33.0), dummy=(-4.8, 9.6), view=(0.9, 0.35))
    add("12_kura_namako_janela_porta", p_kura)

    def p_kura_close(mb, F):
        house(mb, F, PRESETS["V4"])
        return dict(focus=(0, 7.0, 6.6), size=(13.0, 10.5), dummy=(-4.8, 9.6), view=(0.7, 0.2))
    add("13_kura_porta_ferro_close", p_kura_close)

    IRI = dict(W=20.0, D=14.0, h=11.0, plinth=("soco", 1.0), front=["plain", "koshi", "door", "plain"], roof="irimoya")

    def p_roof_irimoya(mb, F):
        house(mb, F, IRI)
        return dict(focus=(0, 0, 11.0), size=(36.0, 26.0), dummy=(-6.0, 9.0), view=(1.0, 0.9))
    add("14_telhado_irimoya", p_roof_irimoya)

    def p_roof_corner(mb, F):
        r = house(mb, F, IRI)["roof"]
        return dict(focus=(r["Xe"] - 1.0, r["Ye"] - 1.0, 1.0 + r["zw"] - 1.4), size=(9.0, 5.5), dummy=(-6.0, 9.0),
                    view=(1.1, -0.3))
    add("15_telhado_quina_beiral_close", p_roof_corner)

    def p_roof_gableend(mb, F):
        r = house(mb, F, IRI)["roof"]
        return dict(focus=(r["xg"] + 0.6, 0.0, 1.0 + (r["zb"] + r["zr"]) / 2 + 0.2), size=(13.0, 7.5),
                    dummy=(-6.0, 9.0), view=(4.0, 0.3))
    add("16_empena_irimoya_close", p_roof_gableend)

    def p_ridge(mb, F):
        r = house(mb, F, IRI)["roof"]
        return dict(focus=(r["xg"] + r["go"] + 0.2, 0.0, 1.0 + r["zr"] + 0.7), size=(7.0, 4.0), dummy=(-6.0, 9.0),
                    view=(2.2, 0.45))
    add("17_cumeeira_onigawara_close", p_ridge)

    def p_kirizuma(mb, F):
        house(mb, F, dict(W=18.0, D=14.0, h=11.5, plinth=("soco", 1.2), roof="kirizuma", ridge="x",
                          front=["plain", "koshi", "door", "plain"], g_over=2.0))
        return dict(focus=(0, 0, 11.0), size=(34.0, 26.0), dummy=(-6.0, 8.5), view=(1.4, 0.8))
    add("18_telhado_kirizuma", p_kirizuma)

    def p_yose(mb, F):
        house(mb, F, dict(W=12.0, D=12.0, h=10.0, plinth=("soco", 1.0), roof="yosemune", over=3.0,
                          front=["open", "open"], back=["plain", "plain"], left=["open", "plaster"],
                          right=["plaster", "open"], benches=((0.0, -1.5, 5.0, 0.0),)))
        return dict(focus=(0, 0, 9.0), size=(24.0, 20.0), dummy=(-3.0, 7.5), view=(1.2, 0.7))
    add("19_telhado_hogyo_pavilhao", p_yose)

    def p_pent(mb, F):
        wall_house(mb, F, ["plain", "door", "plain"], 16.0, hisashi_front=True)
        return dict(focus=(0, 5.5, 9.6), size=(17.0, 10.0), dummy=(-4.0, 7.6), view=(0.6, 0.3))
    add("20_hisashi_consolos", p_pent)

    def p_engawa(mb, F):
        house(mb, F, dict(W=16.0, D=12.0, h=12.5, plinth=("ishigaki", 1.8), roof="kirizuma", ridge="x",
                          front=["plain", "door", "plain"], engawa=("F",), engawa_d=3.0))
        return dict(focus=(0, 8.0, 2.4), size=(18.0, 9.5), dummy=(-4.6, 10.8), view=(0.6, 0.25))
    add("21_engawa_degrau", p_engawa)

    def p_stair_stone(mb, F):
        stair_stone(mb, sub(F, 0, 4.0, 0.0, math.pi), 6.0, 6, 0.75, 1.9)
        bb(mb, F, -5.0, 5.0, -12.0, -7.3, -0.3, 4.5, STD)
        return dict(focus=(0, -1.6, 2.3), size=(15.0, 8.5), dummy=(-4.4, 5.6), view=(1.0, 0.6))
    add("22_escada_pedra", p_stair_stone)

    def p_stair_wood(mb, F):
        stair_wood(mb, sub(F, 0, 3.0, 0.0, math.pi), 4.0, 6, 0.75, 1.4)
        bb(mb, F, -4.0, 4.0, -9.5, -5.3, -0.3, 4.5, WM)
        return dict(focus=(0, -1.2, 3.2), size=(13.0, 9.0), dummy=(-3.4, 2.4), view=(1.0, 0.45))
    add("23_escada_madeira", p_stair_wood)

    def p_rail(mb, F):
        bb(mb, F, -8.0, 8.0, -3.0, 3.0, -0.3, 0.0, WM)
        railing(mb, F, [(7.5, -2.5), (7.5, 2.5), (-7.5, 2.5), (-7.5, -2.5)], 4.0, 0.0)
        return dict(focus=(0, 0.0, 2.0), size=(19.0, 8.0), dummy=(0.0, -1.0), view=(0.6, 0.6))
    add("24_guarda_corpo", p_rail)

    def p_fence(style):
        def f(mb, F):
            fence(mb, F, [(-8.0, 0.0), (0.0, 0.0), (6.0, -4.0)], 3.2, style)
            return dict(focus=(-1.0, -1.0, 1.6), size=(18.0, 7.0), dummy=(-3.0, -2.8), view=(0.5, 0.4))
        return f
    add("25_cerca_ripas", p_fence("ripa"))
    add("26_cerca_bambu", p_fence("bamboo"))

    def p_lpost(mb, F):
        lantern_post(mb, F, 8.6, 1.9, "L_DSKit_LampPost", 40.0)
        return dict(focus=(0, 0.8, 5.0), size=(7.0, 10.5), dummy=(-1.8, -1.4), view=(1.6, 0.1))
    add("27_lanterna_poste", p_lpost)

    def p_lpost_close(mb, F):
        lantern_post(mb, F, 8.6, 1.9, "L_DSKit_LampPost2", 40.0)
        return dict(focus=(0, 1.6, 6.5), size=(3.6, 3.6), dummy=(-1.8, -1.4), view=(1.3, 0.1))
    add("28_lanterna_poste_close", p_lpost_close)

    def p_lwall(mb, F):
        wall_house(mb, F, ["plain", "plaster", "plain"], 14.0)
        lantern_wall(mb, sub(F, 0.0, 4.0, 1.2 + 7.2), "L_DSKit_LampWall", 30.0)
        return dict(focus=(0, 5.0, 8.6), size=(4.8, 3.9), dummy=(-2.6, 6.0), view=(1.5, 0.05))
    add("29_lanterna_parede", p_lwall)

    def p_toro(style, s=1.0):
        def f(mb, F):
            toro(mb, F, style, s, "L_DSKit_Toro_%s" % style, 35.0)
            hgt = {"kasuga": 7.6, "yukimi": 4.4, "oki": 2.6}[style] * s
            return dict(focus=(-0.8, 0, max(hgt * 0.5, 2.7)), size=(max(hgt * 1.3, 7.5), max(hgt * 1.15, 6.4)),
                        dummy=(-3.4, -1.2), view=(1.0, 0.3))
        return f
    add("30_toro_kasuga", p_toro("kasuga"))
    add("31_toro_yukimi", p_toro("yukimi"))
    add("32_toro_oki", p_toro("oki"))

    def p_gate(mb, F):
        gate_mon(mb, F)
        for s in (-1, 1):
            garden_wall(mb, sub(F, s * 11.95, 0.0), 13.0)
        return dict(focus=(0, 0, 6.0), size=(30.0, 15.0), dummy=(-2.0, 3.4), view=(0.9, 0.45))
    add("33_portao_munamon_muro", p_gate)

    for k in ("V1", "V2", "V3", "V4", "V5", "V6"):
        def f(mb, F, k=k):
            sp = PRESETS[k]
            house(mb, F, sp, "L_DSKit_House_%s" % k)
            Wd = sp["W"] + 2 * sp.get("over", 3.4)
            hh = (sp["h"] + (sp["upper"]["h"] if sp.get("stories") == 2 else 0) + sp["plinth"][1]
                  + sp.get("pitch", 0.6) * min(sp["W"], sp["D"]) / 2 + 3.0)
            return dict(focus=(0, 0, hh * 0.47), size=(Wd * 1.12, hh * 1.18), dummy=(-sp["W"] * 0.3, sp["D"] / 2 + 4.5),
                        view=(1.2, 0.55))
        add("4%d_casa_%s" % (int(k[1]), k), f)

    def p_example(mb, F):
        house(mb, F, PRESETS["V2"], "L_DSKit_House_Ex")
        return dict(focus=(2.0, 8.0, 7.6), size=(22.0, 13.0), dummy=(1.6, 12.4), view=(0.75, -0.08))
    add("50_casa_exemplo_altura_jogador", p_example)
    return P


def studio(out, only=()):
    import ds_scene
    os.makedirs(out, exist_ok=True)
    DL.reset_scene()
    fm_lib.make_materials()
    ds_scene.setup(res=(960, 540), samples=16)
    pieces = _studio_pieces()
    if only:
        pieces = [p for p in pieces if any(o in p[0] for o in only)]
    # chao do estudio (terra escura) - fora do kit
    gm = MB("STUDIO_Ground", "00_REFERENCE", detail="far", floor=-999)
    gm.box((150.0 * (len(pieces) + 2), 260.0, 1.0), (75.0 * len(pieces), 0.0, -0.5), (0, 0, 0), "Dirt_DS_Dark", 0.0)
    gm.finish()
    cams = []
    report = []
    for i, (name, fn) in enumerate(pieces):
        X = i * 150.0
        F = Frame(X, 0.0, 0.0, math.pi)
        mb = MB("DS_Kit_" + name, "05_VILLAGE")
        r = fn(mb, F)
        ob = mb.finish()
        report.append((name, _tris(ob), len(ob.data.materials) if ob else 0))
        dx, dy = r["dummy"]
        DL.dummy("SCALE_Dummy_" + name, *F.p(dx, dy, 0.0).to_tuple()[:2], 0.0 + r.get("dummy_z", 0.0), F.a + math.pi)
        fx, fy, fz = r["focus"]
        tgt = F.p(fx, fy, fz)
        vx, vz = r.get("view", (0.45, 0.3))
        d = Vector((-vx * 0.42, -1.0, vz * 0.42 + 0.12)).normalized()
        fov = 2 * math.atan(18.0 / 35.0)
        w, hgt = r["size"]
        dist = max(w, hgt * 16.0 / 9.0) * 0.5 / math.tan(fov / 2) * 1.12
        cn = "CAM_DSK_" + name
        fm_lib.camera(cn, tgt + d * dist, tgt, 35)
        cams.append(cn)
    fm_lib.make_materials()
    ds_scene.tone_emissives()
    for o in bpy.data.objects:
        if o.type == "LIGHT" and o.name.startswith("L_DSKit"):
            o.data.use_shadow = False
    sc = bpy.context.scene
    sc.render.image_settings.file_format = "JPEG"
    sc.render.image_settings.quality = 88
    print("KIT tris por peca:")
    for name, t, nm in report:
        print("KIT %-34s tris=%6d materiais=%d" % (name, t, nm))
    for mode, sub_ in (("rico", "previa"), ("roblox", "roblox")):
        if mode == "roblox":
            fm_lib.apply_preview("roblox")
            ds_scene.tone_emissives()
        od = os.path.join(out, sub_)
        os.makedirs(od, exist_ok=True)
        for cn in cams:
            sc.camera = bpy.data.objects[cn]
            sc.render.filepath = os.path.join(od, cn + ".jpg")
            bpy.ops.render.render(write_still=True)
            print("KIT RENDER", mode, cn)
    if "--save" in sys.argv:
        bpy.ops.wm.save_as_mainfile(filepath=os.path.join(out, "kit_studio.blend"), compress=True)


if __name__ == "__main__":
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    pos = [a for a in argv if not a.startswith("--")]
    out = pos[0] if pos else os.path.join(HERE, "renders", "onda1", "1b_kit")
    studio(out, pos[1:])
