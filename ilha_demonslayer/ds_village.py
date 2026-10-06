# ds_village - VILA da Ilha 4 (DEMON SLAYER), onda 2a (PLANO_DS secoes 4.2, 5, 8 e 12; PROMPT_USUARIO secoes 9, 10,
# 18-26). Substitui ds_blockout.village. Prefixo DS_Vil_, colecao 05_VILLAGE. Tudo com o kit (ds_kit, onda 1b).
#
# LEITURA: a vila e uma RUA que sobe da trilha ate a escada OesteForja, com as casas do lado de dentro (oeste) VIRADAS
# PARA A RUA e para a clareira (as fachadas acesas sao o que o jogador ve do espaco de jogo). A densidade cresce do
# portao para dentro: cha (V1) na chegada -> minka com horta (V2) -> oficina (V3) que conversa com a forja -> escada
# VilaAlta -> kura branco (V4) marcando a vila de longe -> sobrado com sacada para a clareira (V5) -> casa principal
# (V6) com muro, portao e jardim ao pe da escada da forja ("a vila pertence a forja").
# GESTO de cada casa (nada de 6 copias): V1 aberta em 3 lados (pavilhao), V2 empena para a rua + engawa para o sul,
# V3 frente de loja com capelo e cumeeira ao longo da rua, V4 torre branca com a empena para a rua, V5 sacada no 2o
# piso para a clareira, V6 portao munamon + muro tsuiji + jardim com trelica (fujidana) + interior visitavel.
# Rumo de cada fachada segue a curva da rua (15..23 graus na rua baixa, -6..0 na alta) e o V4 olha para o sul (para
# quem sobe a VilaAlta); cumeeiras alternam (N-S: V1, V3, V5, V6; L-O: V2, V4); reboco por casa (ocre, base, cinza).
# INTERIORES (so V1 e V6, PLANO 4.2): forro de tabuas com ripas (saobuchi), luz quente dentro de moldura (chochin,
# andon, braseiro do irori), moveis em escala de jogo, colisao propria (piso, paredes com vao, rampas de entrada).
# RUA: terra batida (cobre o leito que o ds_terrain deixa 0,5 abaixo numa faixa de 3,7) + faixa central de LAJES com
# juntas e bordas que se desfazem na terra; alarga nos nos (portao, pe/topo das escadas, portao do V6). Lanternas de
# poste so nos NOS (NightOnly: L_DSProp_Lamp_Vil_*). Cercas baixas em setores (borda do T2 sobre a clareira, quintal
# do V2). Escadas da planta (VilaAlta, VilaClareira, OesteForja) com ds_kit.stair_stone no envelope do ds_col.
# Props soltos (vasos, varais, barris, horta) sao do ds_props (onda 3b): ver PROP_ANCHORS (so dados, sem geometria).
# MUDANCAS DE PLANTA (justificadas no relatorio): casas aproximadas da rua (a planta deixava 35-56 de gramado vazio
# entre a rua e as fachadas), V2 18 x 22 (fundo maior que a frente: a irimoya vira a empena para a rua), poco e
# oratorio 8-9 para oeste (o ponto da planta cai em cima da trilha de terra da margem oeste do ds_terrain).
import math, zlib
from mathutils import Vector
import ds_lib as DL
from ds_lib import MB, col_box, col_ramp, light, Frame, ccw
import ds_layout as L
import ds_kit as K
from ds_kit import sub, bb, bx, lathe, ext, beam

T1, T2, T4 = L.T1, L.T2, L.T4
C = "05_VILLAGE"
WD, WM, PL, RT, RR = K.WD, K.WM, K.PL, K.RT, K.RR
ST, STD, STP = K.ST, K.STD, K.STP
LAJE = "Stone_DS_Laje"
DIRT, DIRTD = "Dirt_DS", "Dirt_DS_Dark"
IRON, LIT, PAPER, LGLOW, CLOTH = K.IRON, K.LIT, K.PAPER, K.LGLOW, K.CLOTH
TATAMI = "Bamboo_DS_Dry"          # palha do tatami (sem material novo)
EMBER = "Ember_DS_Glow"
WARM = K.WARM
SLAB_TOP = 0.3                    # lajes acima do piso: >= 0,12 acima da grama do ds_terrain (0,18) onde encostam
DIRT_TOP = 0.04                   # terra batida da rua (cobre o leito; mesmo material da pele: sem z-fight de cor)
DIRT_HW = 4.4                     # meia-largura da terra batida: o leito do ds_terrain e 3,7 do eixo MAS a pele dele
                                  # sai de marching squares em grade de 2,0 (a borda real varia ate ~1,2): 5,0 cobre


def hh(*a):
    s = "|".join("%.2f" % v if isinstance(v, float) else str(v) for v in a)
    return (zlib.crc32(s.encode("utf-8")) & 0xffffffff) / 4294967296.0


def cyc(seq, i):
    return seq[i % len(seq)]


def edges(a, b, step):
    """bordas de n celulas iguais em [a, b] (largura <= step); ds_kit.even devolve os CENTROS"""
    n = max(1, int(math.ceil((b - a) / step - 1e-6)))
    return [a + (b - a) * i / n for i in range(n + 1)]


# ================================================================== CASAS (posicao, rumo da frente, spec do kit)
# rumo = direcao da FRENTE no plano local (graus; 0 = +X = para a rua/clareira). F = Frame(x, y, z, rumo - 90).
def _spec(base, **kw):
    s = dict(K.PRESETS[base])
    s.update(kw)
    return s


HOUSES = [
    # V1 chaya: aberta na frente (3 vaos, noren no do meio) e nos 2 vaos da frente das laterais; olha a rua girada 15
    #   graus para o portao (quem entra ve o interior aceso de 3/4). Telhado irimoya baixo e largo.
    ("V1", (-64.9, 128.5), T1, 15.0, _spec("V1", plaster="ochre", right=["plaster", {"t": "open", "w": 5.2}],
                                            front=["open", {"t": "open", "noren": True, "w": 5.6}, "open"],
                                            left=["open", "plaster"], benches=(), lit=["B", "L"])),   # vaos de entrada >= 5
    # V2 minka: 18 de frente x 22 de fundo -> a cumeeira corre para tras e a EMPENA da irimoya olha a rua; engawa no
    #   sul (para a chegada), porta com noren no meio, koshi dos lados. Horta/varal: ds_props (PROP_ANCHORS).
    ("V2", (-86.0, 158.0), T1, 20.0, _spec("V2", W=18.0, D=22.0, front=["koshi", "door", "koshi"],
                                            right=["plain", "shoji", "plain", "plain"], left="auto", plaster="base",
                                            engawa=("R",), engawa_d=3.0)),
    # V3 oficina do afiador: frente de loja (shitomi + banca) e capelo, kirizuma com a cumeeira AO LONGO da rua.
    ("V3", (-95.0, 197.0), T1, 23.0, _spec("V3", plaster="ash")),
    # V4 kura: olha para o SUL (porta de ferro para quem chega pela VilaAlta); a empena branca encara a rua.
    ("V4", (-105.0, 252.0), T2, -90.0, _spec("V4", lod=1)),
    # V5 sobrado: porta no eixo da escada VilaClareira (y 284), sacada do 2o piso para a clareira, reboco ocre.
    ("V5", (-102.0, 286.0), T2, -6.0, _spec("V5", plaster="ochre")),
    # V6 casa principal: frente 30 para o jardim e o portao (leste), engawa em L (frente + sul), porta aberta 8 x 11
    #   ENTRAVEL; lateral sul com janelas koshi (o interior usa a parede); luzes proprias (irori + andon).
    ("V6", (-124.0, 338.0), T2, 0.0, _spec("V6", engawa=("F", "R"), right=["koshi", "plaster", "plain"],
                                            back=["koshi", "plaster", "plaster", "plaster", "koshi"],
                                            front=["plain", "koshi", "lattice", {"t": "open_door", "w": 8.6},
                                                   "lattice", "koshi", "plain"])),
]
HOUSE_BY = {h[0]: h for h in HOUSES}
ENTERABLE = ("V1", "V6")
LIGHT_E = {"V1": 0.0, "V2": 90.0, "V3": 90.0, "V4": 70.0, "V5": 90.0, "V6": 0.0}   # 0 = luz propria do interior


def house_frame(nm):
    _, (x, y), z, face, sp = HOUSE_BY[nm]
    return Frame(x, y, z, math.radians(face - 90.0))


def full_spec(nm):
    sp = dict(K.DEFAULTS)
    sp.update(HOUSE_BY[nm][4])
    return sp


def faces_of(Fb, W, D):
    return {"F": (sub(Fb, 0.0, D / 2), W), "B": (sub(Fb, 0.0, -D / 2, 0.0, math.pi), W),
            "R": (sub(Fb, W / 2, 0.0, 0.0, -math.pi / 2), D), "L": (sub(Fb, -W / 2, 0.0, 0.0, math.pi / 2), D)}


def bay_spans(Lf, bays, door_w):
    """replica a divisao de vaos do ds_kit.facade: [(tipo, x0, x1)] no referencial da face (x da face)"""
    xi0, xi1 = -Lf / 2 + K.CP, Lf / 2 - K.CP
    bs = [dict(b) if isinstance(b, dict) else {"t": b} for b in bays]
    for b_ in bs:
        if "w" not in b_ and b_["t"] in ("door", "itado", "open_door"):
            b_["w"] = door_w + 0.6
    bs = list(reversed(bs))
    n = len(bs)
    fixed = sum(b_.get("w", 0.0) for b_ in bs)
    nfree = sum(1 for b_ in bs if "w" not in b_)
    free = (xi1 - xi0 - (n - 1) * K.IP - fixed) / max(1, nfree)
    out, x = [], xi0
    for i, b_ in enumerate(bs):
        w = b_.get("w", free)
        out.append((b_["t"], x, x + w))
        x += w + K.IP
    return out


# ------------------------------------------------------------------ colisao das casas
def cbox(area, F, x0, x1, y0, y1, z0, z1):
    x0, x1 = min(x0, x1), max(x0, x1)
    y0, y1 = min(y0, y1), max(y0, y1)
    return col_box(area, (x1 - x0, y1 - y0, z1 - z0), F.p((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2), F.r())


def cramp(area, F, a, b, w):
    return col_ramp(area, F.p(*a), F.p(*b), w)


def house_collision(nm, F, sp):
    """V2..V5: corpo fechado (ds_kit.house_cols) + engawa + rampa nos degraus da porta. V1/V6 (entraveis): base ate o
    piso interno, paredes com os vaos ABERTOS de verdade, engawa e rampas de entrada (ver interiores)"""
    area = "DS_VilHouse" + nm
    W, D, h = sp["W"], sp["D"], sp["h"]
    ph = sp["plinth"][1]
    htop = h + ((sp["upper"] or {}).get("h", 9.6) if sp["stories"] == 2 else 0.0)
    Fb = sub(F, z=ph)
    ed = sp["engawa_d"]
    if nm not in ENTERABLE:
        K.house_cols(area, F, sp)
    else:
        cbox(area, F, -W / 2 - 0.6, W / 2 + 0.6, -D / 2 - 0.6, D / 2 + 0.6, -0.6, ph + 0.66)     # base = piso interno
        for k, (Ff, Lf) in faces_of(Fb, W, D).items():
            key = {"F": "front", "B": "back", "R": "right", "L": "left"}[k]
            bays = sp[key]
            if bays == "auto" or bays is None:
                bays = K.auto_bays(Lf, "back" if k == "B" else "side")
            spans = bay_spans(Lf, bays, sp["door_w"])
            runs, cur = [], [-Lf / 2, None]
            for t, a, b in spans:
                if t in ("open", "open_door"):
                    runs.append((cur[0], a))
                    cur = [b, None]
                    if t == "open_door":                 # verga acima da porta
                        cbox(area, Ff, a, b, -1.0, 0.0, K.SILL + sp["door_h"], htop)
            runs.append((cur[0], Lf / 2))
            for a, b in runs:
                if b - a > 0.05:
                    cbox(area, Ff, a, b, -1.0, 0.0, 0.66, htop)
    # engawa (piso de tabuas) + rampa da pedra de degrau ate ele
    eng = sp["engawa"]
    door_x = {}
    if nm in ENTERABLE or eng:
        for k in eng:
            Ff, Lf = faces_of(Fb, W, D)[k]
            x0, x1 = -Lf / 2, Lf / 2
            if k == "F":
                x1 += ed if "R" in eng else 0.0
                x0 -= ed if "L" in eng else 0.0
            cbox(area, Ff, x0, x1, 0.0, ed, -ph - 0.4, 0.35)
    # rampas de entrada (sobre as pedras de degrau do kit): portas da frente
    Ff, Lf = faces_of(Fb, W, D)["F"]
    fb = sp["front"] if isinstance(sp["front"], list) else []
    cands = [(t, a, b) for t, a, b in bay_spans(Lf, fb, sp["door_w"])
             if t in ("door", "open_door", "itado") or (t == "open" and nm in ENTERABLE)]
    if cands and not sp.get("kura"):
        t, a, b = min(cands, key=lambda c: abs(c[1] + c[2]))          # o vao mais perto do eixo (pedra do kit)
        cx = (a + b) / 2
        y0 = ed if "F" in eng else 0.6
        ztop = 0.35 if "F" in eng else K.SILL - 0.25
        cramp(area, Ff, (cx, y0 + 4.4, -ph), (cx, y0 - 0.3, ztop), min(b - a, 6.0))
    return area


def side_entry(mb, area, F, sp, side):
    """entrada pela lateral aberta (pavilhao): pedras de degrau do kit no vao da FRENTE da face + rampa de colisao
    do chao ate o piso"""
    W, D = sp["W"], sp["D"]
    ph = sp["plinth"][1]
    Fb = sub(F, z=ph)
    Ff, Lf = faces_of(Fb, W, D)[side]
    key = {"R": "right", "L": "left"}[side]
    for t, a, b in bay_spans(Lf, sp[key], sp["door_w"]):
        if t == "open":
            cx = (a + b) / 2
            K.steps_to(mb, Ff, cx, 0.6, 0.66 - 0.75, -ph, min(3.4, b - a))
            cramp(area, Ff, (cx, 4.8, -ph), (cx, -0.2, 0.66), b - a)
            return


# ================================================================== INTERIORES
def ceiling(mb, Fb, W, D, z, lod=0):
    """forro saobuchi: tabuas (Wood_DS_Mid) sobre ripas escuras a cada 1,8 e moldura de parede (mawaribuchi)"""
    x0, x1, y0, y1 = -W / 2 + 0.9, W / 2 - 0.9, -D / 2 + 0.9, D / 2 - 0.9
    bb(mb, Fb, x0, x1, y0, y1, z, z + 0.22, WM)
    for x in K.even(x0 + 0.3, x1 - 0.3, 1.8)[1:-1]:
        bb(mb, Fb, x - 0.12, x + 0.12, y0, y1, z - 0.2, z + 0.02, WD)
    for sy in (-1, 1):
        bb(mb, Fb, x0, x1, sy * (y1 - 0.2) - 0.2, sy * (y1 - 0.2) + 0.2, z - 0.32, z + 0.02, WD)
    for sx in (-1, 1):
        bb(mb, Fb, sx * (x1 - 0.2) - 0.2, sx * (x1 - 0.2) + 0.2, y0, y1, z - 0.32, z + 0.02, WD)


def chochin(mb, F, x, y, z, r=0.9, hgt=1.9, light_name=None, energy=60.0):
    """lanterna de papel pendurada: aros escuros em cima/embaixo, gomos do papel (8 lados) e cordao; luz DENTRO"""
    prof = [(r * 0.62, 0.0), (r * 0.9, hgt * 0.2), (r, hgt * 0.5), (r * 0.9, hgt * 0.8), (r * 0.62, hgt)]
    lathe(mb, F, (x, y, z), prof, 8, LGLOW)
    for zz, rr in ((0.0, r * 0.66), (hgt, r * 0.66)):
        lathe(mb, F, (x, y, z + zz - 0.14), [(rr + 0.06, 0.0), (rr + 0.06, 0.28)], 8, WD)
    for k in range(4):                                   # costelas (bambu) por fora do papel
        a = math.pi / 4 + k * math.pi / 2
        pts = [(x + (pr + 0.04) * math.cos(a), y + (pr + 0.04) * math.sin(a), z + pz) for pr, pz in prof]
        K.sweep(mb, F, pts, [(-0.05, -0.05), (0.05, -0.05), (0.05, 0.05), (-0.05, 0.05)], WD)
    mb.rod(F.p(x, y, z + hgt + 0.14), F.p(x, y, z + hgt + 1.2), 0.05, IRON, 6)
    if light_name:
        light(light_name, "POINT", F.p(x, y, z + hgt * 0.5), energy, WARM, 0.3)


def andon(mb, F, x, y, z, light_name=None, energy=70.0):
    """lampada de pe (andon): 4 pes, armacao quadrada de madeira com papel RECUADO, bandeja e alca"""
    hx, hz = 0.75, 2.6
    for sx in (-1, 1):
        for sy in (-1, 1):
            bb(mb, F, x + sx * hx - 0.12, x + sx * hx + 0.12, y + sy * hx - 0.12, y + sy * hx + 0.12, z, z + hz + 0.6, WD)
    bb(mb, F, x - hx + 0.1, x + hx - 0.1, y - hx + 0.1, y + hx - 0.1, z + 0.75, z + hz, LGLOW)
    for zz in (0.75, hz, hz * 0.55):
        for sy in (-1, 1):
            bb(mb, F, x - hx, x + hx, y + sy * hx - 0.08, y + sy * hx + 0.08, z + zz - 0.06, z + zz + 0.06, WD)
        for sx in (-1, 1):
            bb(mb, F, x + sx * hx - 0.08, x + sx * hx + 0.08, y - hx, y + hx, z + zz - 0.06, z + zz + 0.06, WD)
    bb(mb, F, x - 0.06, x + 0.06, y - hx, y + hx, z + hz + 0.5, z + hz + 0.62, WD)
    if light_name:
        light(light_name, "POINT", F.p(x, y, z + 1.7), energy, WARM, 0.3)


def kettle(mb, F, x, y, z, s=1.0):
    """chaleira de ferro (tetsubin): corpo achatado, tampa, bico e alca"""
    lathe(mb, F, (x, y, z), [(0.35 * s, 0.0), (0.62 * s, 0.18 * s), (0.66 * s, 0.42 * s), (0.5 * s, 0.68 * s),
                             (0.3 * s, 0.74 * s), (0.22 * s, 0.86 * s), (0.04 * s, 0.9 * s)], 10, IRON)
    beam(mb, F, (x + 0.55 * s, y, z + 0.35 * s), (x + 0.95 * s, y, z + 0.62 * s), 0.14 * s, 0.14 * s, IRON)
    K.sweep(mb, F, [(x - 0.5 * s, y, z + 0.66 * s), (x - 0.38 * s, y, z + 1.15 * s), (x + 0.38 * s, y, z + 1.15 * s),
                    (x + 0.5 * s, y, z + 0.66 * s)], [(-0.05, -0.05), (0.05, -0.05), (0.05, 0.05), (-0.05, 0.05)], IRON)


def pot(mb, F, x, y, z, r=0.4, hgt=0.8, m=STD, n=8):
    lathe(mb, F, (x, y, z), [(r * 0.6, 0.0), (r, hgt * 0.38), (r * 0.82, hgt * 0.84), (r * 0.58, hgt),
                             (r * 0.01, hgt * 0.98)], n, m)


def shelf_unit(mb, F, x0, x1, y0, y1, z0, levels, m=WD, board=WM):
    """estante de tabuas com montantes e travessas (contra a parede, profundidade y0..y1)"""
    for x in (x0, x1 - 0.3):
        for y in (y0, y1 - 0.3):
            bb(mb, F, x, x + 0.3, y, y + 0.3, z0, z0 + levels[-1] + 0.3, m, 0.04)
    for zz in levels:
        bb(mb, F, x0 - 0.1, x1 + 0.1, y0, y1, z0 + zz, z0 + zz + 0.22, board, 0.03)


def tansu(mb, F, x, y, z, w=4.0, d=1.6, steps=(3.2, 2.2, 1.2), along=1):
    """kaidan-dansu (bau em escada): blocos de gavetas com frentes almofadadas e puxadores de ferro"""
    n = len(steps)
    seg = w / n
    for i, hgt in enumerate(steps):
        xa = x - w / 2 + i * seg
        bb(mb, F, xa + 0.04, xa + seg - 0.04, y, y + d, z, z + hgt, WD, 0.05)
        rows = max(1, int(round(hgt / 1.05)))
        for r in range(rows):
            za, zb_ = z + 0.12 + r * (hgt - 0.2) / rows, z + 0.12 + (r + 1) * (hgt - 0.2) / rows - 0.12
            bb(mb, F, xa + 0.2, xa + seg - 0.2, y + d, y + d + 0.08, za, zb_, WM, 0.02)
            bb(mb, F, xa + seg / 2 - 0.3, xa + seg / 2 + 0.3, y + d + 0.06, y + d + 0.16, (za + zb_) / 2 - 0.07,
               (za + zb_) / 2 + 0.07, IRON)


def interior_V1(mb, F, sp, Fb):
    """casa de cha: forro, balcao com fogareiro (kamado) e chaleira, estante de xicaras no fundo, 2 bancos (shogi)
    com manta indigo, chochin pendurado (a luz da casa), tabuleiro com bule e xicaras"""
    W, D, h = sp["W"], sp["D"], sp["h"]
    ceiling(mb, Fb, W, D, h - 1.0)
    yb = -D / 2 + 0.9                                   # face interna da parede do fundo
    # balcao (fundo, lado direito de quem entra = +x local)
    x0, x1 = -2.2, 3.9
    bb(mb, Fb, x0, x1, yb, yb + 1.9, 0.66, 3.3, WD, 0.06)
    bb(mb, Fb, x0 - 0.1, x1 + 0.05, yb - 0.02, yb + 2.1, 3.3, 3.55, WM, 0.04)
    for x in K.even(x0 + 0.4, x1 - 0.4, 1.1)[1:-1]:
        bb(mb, Fb, x - 0.07, x + 0.07, yb + 1.9, yb + 1.98, 0.9, 3.1, WM)
    # fogareiro de barro sobre o balcao + chaleira; estante de xicaras acima
    kx = x1 - 1.4
    lathe(mb, Fb, (kx, yb + 0.95, 3.55), [(0.82, 0.0), (0.9, 0.5), (0.82, 1.1), (0.55, 1.2)], 8, STD)
    bb(mb, Fb, kx - 0.3, kx + 0.3, yb + 1.86, yb + 1.98, 3.78, 4.22, EMBER)          # boca do fogareiro (brasa)
    for x0_, x1_, z0_, z1_ in ((kx - 0.44, kx - 0.3, 3.66, 4.36), (kx + 0.3, kx + 0.44, 3.66, 4.36),
                               (kx - 0.44, kx + 0.44, 3.66, 3.78), (kx - 0.44, kx + 0.44, 4.22, 4.36)):
        bb(mb, Fb, x0_, x1_, yb + 1.84, yb + 2.04, z0_, z1_, IRON)                  # aro de ferro da boca
    kettle(mb, Fb, kx, yb + 0.95, 4.75, 0.9)
    shelf_unit(mb, Fb, x0 + 0.2, x1 - 0.4, yb, yb + 1.0, 4.9, (0.0, 1.6))
    for i, x in enumerate(K.even(x0 + 0.6, kx - 1.5, 0.85)):
        pot(mb, Fb, x, yb + 0.5, 5.12, 0.26 + 0.06 * (i % 2), 0.55 + 0.25 * (i % 3 == 0), (STD, PL, ST)[i % 3], 6)
    for i, x in enumerate(K.even(x0 + 0.7, x1 - 0.8, 0.95)):
        pot(mb, Fb, x, yb + 0.5, 6.72, 0.3, 0.5, (PL, STD)[i % 2], 6)
    # bancos (shogi) com manta: lateral esquerda e frente-direita (de frente para a rua)
    K.bench(mb, Fb, -W / 2 + 2.3, -1.2, 5.0, ang=math.pi / 2, z=0.66)
    bb(mb, Fb, -W / 2 + 1.38, -W / 2 + 3.22, -3.6, 1.2, 2.36, 2.5, CLOTH)
    K.bench(mb, Fb, W / 2 - 1.9, -1.9, 3.8, ang=math.pi / 2, z=0.66)               # contra a parede R (fundo)
    bb(mb, Fb, W / 2 - 2.82, W / 2 - 0.98, -3.72, -0.08, 2.36, 2.5, CLOTH)
    # tabuleiro com bule e xicaras sobre o banco da esquerda
    bb(mb, Fb, -W / 2 + 1.7, -W / 2 + 2.9, -0.6, 0.6, 2.5, 2.64, WM)
    pot(mb, Fb, -W / 2 + 2.3, 0.0, 2.64, 0.3, 0.5, STD, 8)
    for dy in (-0.25, 0.25):
        pot(mb, Fb, -W / 2 + 1.95, 0.0 + dy, 2.64, 0.12, 0.22, PL, 6)
    # chochin no meio do vao (a luz da casa)
    chochin(mb, Fb, 0.0, 0.2, h - 4.6, 0.9, 1.9, "L_DSVil_V1_Chochin", 90.0)


def interior_V1_col(area, Fb, sp):
    W, D = sp["W"], sp["D"]
    yb = -D / 2 + 0.9
    cbox(area, Fb, -2.2, 3.9, yb, yb + 2.1, 0.66, 3.6)
    cbox(area, Fb, -W / 2 + 1.3, -W / 2 + 3.3, -3.7, 1.3, 0.66, 2.4)
    cbox(area, Fb, W / 2 - 2.9, W / 2 - 0.9, -3.8, 0.0, 0.66, 2.4)


def interior_V6(mb, F, sp, Fb):
    """casa principal: genkan/itanoma de tabuas na frente com o IRORI (braseiro afundado num caixilho, cinza, brasas,
    trempe, chaleira no jizai-kagi pendurado da viga-mestra), viga-mestra (hari) de lado a lado, divisoria de fusuma
    com o vao do meio aberto (6,4) mostrando o zashiki de tatami elevado com tokonoma (pergaminho) e chigaidana, mesa
    baixa com almofadas, andon aceso, kaidan-dansu e estante de potes nas laterais, forro saobuchi"""
    W, D, h = sp["W"], sp["D"], sp["h"]
    xi, yi = W / 2 - 0.9, D / 2 - 0.9                  # faces internas (14,1 / 9,1)
    ceiling(mb, Fb, W, D, h - 1.0)
    fl = 0.66
    # viga-mestra (hari) atravessando de parede a parede sobre o irori + 2 vigas de apoio
    yh = 5.0
    bb(mb, Fb, -xi, xi, yh - 0.55, yh + 0.55, h - 3.4, h - 2.2, WD, 0.12)
    for x in (-xi + 0.3, xi - 0.3):
        bb(mb, Fb, x - 0.45, x + 0.45, yh - 0.45, yh + 0.45, fl, h - 3.3, WD, 0.1)
    # IRORI: caixilho (robuchi) elevado 0,34, cinza, brasas, trempe (gotoku) e chaleira no jizai-kagi
    ix, iy, ir = -5.5, yh, 2.0
    bb(mb, Fb, ix - ir, ix + ir, iy - ir, iy + ir, fl - 0.05, fl + 0.12, STD)
    for s in (-1, 1):
        bb(mb, Fb, ix - ir, ix + ir, iy + s * (ir - 0.25) - 0.25, iy + s * (ir - 0.25) + 0.25, fl, fl + 0.34, WD, 0.06)
        bb(mb, Fb, ix + s * (ir - 0.25) - 0.25, ix + s * (ir - 0.25) + 0.25, iy - ir + 0.5, iy + ir - 0.5, fl, fl + 0.34,
           WD, 0.06)
    bb(mb, Fb, ix - ir + 0.5, ix + ir - 0.5, iy - ir + 0.5, iy + ir - 0.5, fl + 0.12, fl + 0.18, STD)    # cinza
    for k, (dx, dy, s_) in enumerate(((-0.35, 0.2, 0.42), (0.3, -0.25, 0.36), (0.1, 0.45, 0.3), (-0.2, -0.4, 0.32),
                                      (0.45, 0.3, 0.28))):
        bx(mb, Fb, ix + dx, iy + dy, fl + 0.24, s_ * 1.4, s_, s_ * 0.6, EMBER if k < 2 else RR, 0.04, rz=0.4 * k)
    for k in range(3):
        a = 2 * math.pi * k / 3
        beam(mb, Fb, (ix + 0.75 * math.cos(a), iy + 0.75 * math.sin(a), fl + 0.18),
             (ix + 0.55 * math.cos(a), iy + 0.55 * math.sin(a), fl + 0.95), 0.1, 0.1, IRON)
    lathe(mb, Fb, (ix, iy, fl + 0.92), [(0.62, 0.0), (0.62, 0.08), (0.52, 0.1)], 10, IRON)
    kettle(mb, Fb, ix, iy, fl + 1.02, 1.05)
    mb.rod(Fb.p(ix, iy, fl + 2.25), Fb.p(ix, iy, h - 3.4), 0.13, K.BAMBOO, 8)          # jizai-kagi (bambu)
    ext(mb, Fb, [(ix - 0.55, fl + 3.42), (ix + 0.45, fl + 3.32), (ix + 0.62, fl + 3.52), (ix + 0.45, fl + 3.72),
                 (ix - 0.55, fl + 3.64), (ix - 0.72, fl + 3.53)], "y", iy - 0.1, iy + 0.1, WD)   # peixe (yokozuchi)
    mb.rod(Fb.p(ix, iy, fl + 1.95), Fb.p(ix, iy, fl + 3.35), 0.06, IRON, 6)
    K.sweep(mb, Fb, [(ix - 0.35, iy, fl + 1.72), (ix - 0.3, iy, fl + 2.1), (ix, iy, fl + 2.25), (ix + 0.3, iy, fl + 2.1),
                     (ix + 0.35, iy, fl + 1.72)], [(-0.05, -0.05), (0.05, -0.05), (0.05, 0.05), (-0.05, 0.05)], IRON)
    for dx, dy, a in ((ir + 1.3, 0.0, math.pi / 2), (-ir - 1.3, 0.0, 0.2)):                # almofadas (zabuton)
        bx(mb, Fb, ix + dx, iy + dy, fl + 0.12, 1.9, 1.9, 0.24, CLOTH, 0.08, rz=a)
    # divisoria de fusuma (y = 0,5): trilho (shikii), verga (kamoi), bandeira de trelica (ranma) e paineis;
    # vao do meio ABERTO (x -3,2..3,2) e 2 paineis empurrados para os lados
    yd = 0.5
    zk = 9.4
    bb(mb, Fb, -xi, xi, yd - 0.3, yd + 0.3, fl, fl + 0.22, WD)
    bb(mb, Fb, -xi, xi, yd - 0.3, yd + 0.3, zk, zk + 0.6, WD, 0.05)
    bb(mb, Fb, -xi, xi, yd - 0.08, yd + 0.08, zk + 0.6, h - 1.2, PAPER)
    for x in K.even(-xi, xi, 1.2)[1:-1]:
        bb(mb, Fb, x - 0.07, x + 0.07, yd - 0.18, yd + 0.18, zk + 0.6, h - 1.2, WD)
    bb(mb, Fb, -xi, xi, yd - 0.3, yd + 0.3, h - 1.45, h - 1.15, WD)
    pe = edges(-xi, xi, 3.6)                           # 8 paineis em 2 trilhos alternados (sem interpenetrar)
    panels = list(zip(pe, pe[1:]))
    mid = len(panels) // 2
    for k, (a, b) in enumerate(panels):
        yy = yd + (0.15 if k % 2 else -0.15)
        if k == mid - 1:                                  # os 2 do meio correm para os lados: vao de ~6,8
            a, b = a - 3.4, b - 3.4
        elif k == mid:
            a, b = a + 3.4, b + 3.4
        zp = fl + 2.1                                     # koshi-fusuma: almofada de tabua embaixo, papel em cima
        bb(mb, Fb, a + 0.04, b - 0.04, yy - 0.09, yy + 0.09, fl + 0.22, zp, WM)
        bb(mb, Fb, a + 0.04, b - 0.04, yy - 0.09, yy + 0.09, zp, zk, PAPER)
        for x in (a + 0.04, b - 0.34):
            bb(mb, Fb, x, x + 0.3, yy - 0.12, yy + 0.12, fl + 0.22, zk, WD)
        for zz in (fl + 0.22, zp - 0.12, zp + (zk - zp) * 0.62, zk - 0.3):
            bb(mb, Fb, a + 0.04, b - 0.04, yy - 0.12, yy + 0.12, zz, zz + (0.3 if zz in (fl + 0.22, zk - 0.3) else 0.2), WD)
        bb(mb, Fb, b - 0.8, b - 0.5, yy - 0.13, yy + 0.13, fl + 4.2, fl + 4.6, IRON)      # puxador (hikite)
    # ZASHIKI: estrado de tatami elevado 0,36 (piso sobre piso >= 0,3), rodeado de kamachi escuro
    zt = fl + 0.36
    y0, y1 = -yi, yd - 0.3
    bb(mb, Fb, -xi, xi, y0, y1, fl, zt - 0.14, WD)
    bb(mb, Fb, -xi, xi, y1 - 0.4, y1, fl, zt + 0.02, WD, 0.04)                       # kamachi (borda)
    tw, tl = 2.9, 5.8                                       # tatami 1:2
    xs = edges(-xi + 0.1, xi - 0.1, tw)
    for i, (a, b) in enumerate(zip(xs, xs[1:])):
        ys = [y0 + 0.1, y0 + 0.1 + tl, y1 - 0.45] if i % 2 == 0 else [y0 + 0.1, y1 - 0.45 - tl, y1 - 0.45]
        for c, d in zip(ys, ys[1:]):
            bb(mb, Fb, a + 0.17, b - 0.17, c + 0.05, d - 0.05, zt - 0.3, zt, TATAMI)
            for x in (a + 0.05, b - 0.17):                  # heri (borda de pano) nas laterais longas, lado a lado
                bb(mb, Fb, x, x + 0.12, c + 0.05, d - 0.05, zt - 0.3, zt + 0.02, CLOTH)
    # tokonoma no fundo, no eixo da porta: piso de tabua 0,5 acima, pilar (tokobashira), verga (otoshigake),
    # pergaminho (kakejiku) e vaso
    tx0, tx1 = -3.4, 3.4
    yb = -yi
    bb(mb, Fb, tx0, tx1, yb, yb + 3.0, zt - 0.3, zt + 0.5, WM, 0.05)
    bb(mb, Fb, tx0, tx1, yb + 2.7, yb + 3.05, zt - 0.3, zt + 0.52, WD, 0.04)
    for x in (tx0 - 0.3, tx1):
        bb(mb, Fb, x, x + 0.3 + 0.0, yb, yb + 3.05, zt, h - 1.2, WD, 0.05)
    bb(mb, Fb, tx0, tx1, yb, yb + 3.05, zt + 7.4, zt + 8.1, WD, 0.04)
    bb(mb, Fb, tx0 + 0.3, tx1 - 0.3, yb + 0.02, yb + 0.12, zt + 0.5, zt + 7.4, PL)
    bb(mb, Fb, -1.0, 1.0, yb + 0.12, yb + 0.26, zt + 1.6, zt + 6.6, PAPER)            # kakejiku
    bb(mb, Fb, -1.2, 1.2, yb + 0.12, yb + 0.3, zt + 6.6, zt + 7.0, CLOTH)
    bb(mb, Fb, -1.2, 1.2, yb + 0.12, yb + 0.3, zt + 1.3, zt + 1.6, CLOTH)
    ext(mb, Fb, [(-0.7, zt + 2.6), (-0.2, zt + 4.9), (0.15, zt + 4.2), (0.45, zt + 5.3), (0.75, zt + 2.6)], "y",
        yb + 0.26, yb + 0.4, CLOTH)                                                  # pintura: montanhas em tinta
    pot(mb, Fb, 1.9, yb + 1.3, zt + 0.5, 0.45, 1.2, STD, 8)
    for k in range(3):
        mb.rod(Fb.p(1.9, yb + 1.3, zt + 1.6), Fb.p(1.9 + (k - 1) * 0.5, yb + 1.3 + 0.2 * k, zt + 3.2 + 0.3 * k),
               0.06, WD, 5)
    # chigaidana (prateleiras desencontradas) a direita do tokonoma
    cx0, cx1 = tx1 + 0.3, tx1 + 4.6
    bb(mb, Fb, cx0, cx1, yb, yb + 2.4, zt - 0.3, zt + 1.6, WD, 0.04)
    bb(mb, Fb, cx0, cx1, yb, yb + 2.4, zt + 6.6, zt + 7.0, WD, 0.04)
    bb(mb, Fb, cx0, cx0 + 2.6, yb, yb + 1.8, zt + 3.4, zt + 3.62, WM, 0.03)
    bb(mb, Fb, cx0 + 1.7, cx1, yb, yb + 1.8, zt + 4.3, zt + 4.52, WM, 0.03)
    bb(mb, Fb, cx0 + 2.45, cx0 + 2.65, yb, yb + 0.3, zt + 3.62, zt + 4.3, WD)
    pot(mb, Fb, cx0 + 0.9, yb + 0.9, zt + 3.62, 0.35, 0.8, PL, 8)
    # mesa baixa (chabudai) com almofadas e o andon aceso
    mx, my = -5.0, -4.6
    lathe(mb, Fb, (mx, my, zt + 1.0), [(1.7, 0.0), (1.75, 0.08), (1.75, 0.22), (1.6, 0.3), (0.01, 0.3)], 12, WD)
    for k in range(4):
        a = math.pi / 4 + k * math.pi / 2
        bb(mb, Fb, mx + 1.05 * math.cos(a) - 0.14, mx + 1.05 * math.cos(a) + 0.14, my + 1.05 * math.sin(a) - 0.14,
           my + 1.05 * math.sin(a) + 0.14, zt, zt + 1.0, WD)
    for dx, dy in ((0.0, 2.7), (2.7, 0.0), (0.0, -2.7)):
        bx(mb, Fb, mx + dx, my + dy, zt + 0.12, 1.9, 1.9, 0.24, CLOTH, 0.08)
    andon(mb, Fb, -xi + 1.6, -yi + 1.8, zt, "L_DSVil_V6_Andon", 110.0)
    # laterais do itanoma: bau em escada (direita, encostado na parede sul) e estante de potes (esquerda)
    tansu(mb, sub(Fb, xi, 7.4, 0.0, math.pi / 2), 0.0, 0.0, fl, 3.3, 1.7, (3.6, 2.5, 1.4))
    shelf_unit(mb, Fb, -xi, -xi + 1.4, 5.7, 8.9, fl, (0.4, 2.6, 4.8, 7.0), WD, WM)
    for i, y in enumerate(K.even(6.0, 8.5, 1.25)):
        pot(mb, Fb, -xi + 0.7, y, fl + 0.62, 0.42, 1.1 + 0.3 * (i % 2), (STD, ST)[i % 2], 8)
        pot(mb, Fb, -xi + 0.7, y + 0.3, fl + 3.04, 0.32, 0.75, (PL, STD)[i % 2], 6)
    # luz do irori (baixa e quente, perto das brasas)
    light("L_DSVil_V6_Irori", "POINT", Fb.p(ix, iy, fl + 3.0), 160.0, (1.0, 0.56, 0.28), 0.4)


def interior_V6_col(area, Fb, sp):
    W, D, h = sp["W"], sp["D"], sp["h"]
    xi, yi = W / 2 - 0.9, D / 2 - 0.9
    fl = 0.66
    cbox(area, Fb, -5.5 - 2.0, -5.5 + 2.0, 5.0 - 2.0, 5.0 + 2.0, fl, fl + 2.4)          # irori (+ chaleira)
    for x in (-xi + 0.3, xi - 0.3):
        cbox(area, Fb, x - 0.45, x + 0.45, 4.55, 5.45, fl, h - 2.2)                       # esteios da viga
    # divisoria: so as pontas de paineis (vao do meio de 6,4 livre)
    cbox(area, Fb, -xi, -3.5, 0.2, 0.8, fl, h - 1.0)
    cbox(area, Fb, 3.5, xi, 0.2, 0.8, fl, h - 1.0)
    cbox(area, Fb, -xi, xi, -yi, 0.2, fl, fl + 0.36)                                     # estrado de tatami
    cbox(area, Fb, -3.7, 3.7 + 4.6, -yi, -yi + 3.05, fl + 0.36, fl + 0.36 + 0.5)         # tokonoma + chigaidana
    cbox(area, Fb, xi - 1.8, xi, 5.75, 9.05, fl, fl + 3.6)                               # tansu
    cbox(area, Fb, -xi, -xi + 1.4, 5.7, 8.9, fl, fl + 7.3)                               # estante


# ================================================================== CASA INTEIRA
def build_house(nm):
    F = house_frame(nm)
    sp = full_spec(nm)
    mb = MB("DS_Vil_House" + nm, C, detail="hero")
    e = LIGHT_E[nm]
    info = K.house(mb, F, sp, ("L_DSVil_Win_" + nm) if e > 0 else None, e)
    Fb = sub(F, z=sp["plinth"][1])
    area = house_collision(nm, F, sp)
    if nm == "V1":
        interior_V1(mb, F, sp, Fb)
        interior_V1_col(area, Fb, sp)
        side_entry(mb, area, F, sp, "R")
    elif nm == "V6":
        interior_V6(mb, F, sp, Fb)
        interior_V6_col(area, Fb, sp)
        garden_V6(mb, F, sp)
    mb.finish()
    return info


# ------------------------------------------------------------------ V6: muro, portao, jardim, trelica
GARDEN_E = -84.0                  # muro de frente (leste) do jardim do V6, com o portao no eixo da casa
GARDEN_Y = (316.0, 360.0)


def garden_V6(mb, F, sp):
    """jardim fechado do V6: muro tsuiji baixo (4,4: o olho do jogador passa por cima) na frente com o portao munamon
    no eixo da porta, cercas de bambu nas laterais, caminho de pedras (tobi-ishi) do portao ate os degraus da engawa,
    lanterna yukimi e a TRELICA (fujidana) da glicinia do plano (L.WISTERIA[2]; a planta e do ds_veg)"""
    _, (cx, cy), z, face, _ = HOUSE_BY["V6"]
    area = "DS_VilGarden"
    gy0, gy1 = GARDEN_Y
    gw = 9.0                                         # vao do portao (munamon: w 8,5 + pilares)
    Fg = Frame(GARDEN_E, cy, z, -math.pi / 2)        # +y = rua (leste)
    K.gate_mon(mb, Fg, 8.5, 9.6, 3.2, True)
    hw = 8.5 / 2 + 0.55 + 0.65
    WL = 7.6                                         # muro tsuiji so ladeando o portao; o resto em yotsume
    for s in (-1, 1):
        y0, y1 = (cy + hw, cy + hw + WL) if s < 0 else (cy - hw - WL, cy - hw)
        yc = (y0 + y1) / 2
        Fw = Frame(GARDEN_E, yc, z, -math.pi / 2)    # o muro corre ao longo do x local (= -y do mundo)
        K.garden_wall(mb, Fw, WL, 4.4, 1.0)
        col_box(area, (1.2, WL, 4.4), (GARDEN_E, yc, z + 2.2))
        ye = gy1 if s < 0 else gy0
        yw = y1 + 0.35 if s < 0 else y0 - 0.35
        fence_run(mb, [(GARDEN_E, yw), (GARDEN_E, ye)], z, area, 3.2, "yotsume")
    for s in (-1, 1):                                # pilares do portao (centro em w/2 + 0,55)
        col_box(area, (1.4, 1.4, 9.6), (GARDEN_E, cy + s * (8.5 / 2 + 0.55), z + 4.8))
    # cercas de bambu (yotsume-gaki) nas laterais do jardim, da casa ate o muro
    x_house = cx + 10.0 + 3.2                        # face da engawa da frente
    xf = cx                                          # cercas laterais: do muro ate o meio da casa (fundos abertos)
    for yy in (gy0, gy1):
        fence_run(mb, [(GARDEN_E - 0.6, yy), (xf, yy)], z, area, 3.2, "yotsume")
    # caminho de pedras do portao ate os degraus da engawa (no eixo da porta)
    Fp = Frame(GARDEN_E, cy, z, math.pi / 2)        # +y = para dentro (oeste)
    yv = 0.6
    k = 0
    while yv < abs(GARDEN_E - x_house) - 4.2:
        w_ = 2.4 + 0.5 * hh("gv", k)
        off = (0.7 if k % 2 else -0.7) * (0.6 + 0.4 * hh("go", k))
        pts = [(off + w_ / 2 * math.cos(2 * math.pi * j / 9) * (0.9 + 0.2 * hh("gp", k, j)),
                yv + 1.0 + 0.85 * math.sin(2 * math.pi * j / 9) * (0.9 + 0.2 * hh("gq", k, j))) for j in range(9)]
        ext(mb, Fp, pts, "z", -0.25, 0.34, STP)
        yv += 2.2 + 0.4 * hh("gs", k)
        k += 1
    # lanterna de pedra yukimi perto da glicinia (sem luz: a luz do jardim e a janela da casa)
    wx, wy = L.WISTERIA[2]
    K.toro(mb, Frame(wx + 4.6, wy - 6.0, z, 0.3), "yukimi", 1.0)
    col_box(area, (3.0, 3.0, 4.0), (wx + 4.6, wy - 6.0, z + 2.0))
    # fujidana: 4 esteios sobre pedras, 2 vigas, 7 ripas; topo a 8,6 (a glicinia do ds_veg pende dela)
    Ft = Frame(wx, wy, z, 0.0)
    a, b_ = 3.6, 3.2
    for sx in (-1, 1):
        for sy in (-1, 1):
            K.post(mb, Ft, sx * a, sy * b_, 0.0, 8.0, 0.6, True)
            col_box(area, (0.8, 0.8, 8.0), (wx + sx * a, wy + sy * b_, z + 4.0))
    for sx in (-1, 1):
        bb(mb, Ft, sx * a - 0.3, sx * a + 0.3, -b_ - 1.2, b_ + 1.2, 7.8, 8.4, WD, 0.06)
    for y in K.even(-b_ - 0.8, b_ + 0.8, 1.1):
        bb(mb, Ft, -a - 1.0, a + 1.0, y - 0.13, y + 0.13, 8.4, 8.66, K.BAMBOO, 0.0)


# ================================================================== RUA
def polyline_stations(pts, ext0=0.0, ext1=0.0, step=0.5):
    """estacoes ao longo da polilinha (com extensoes retas nas pontas): (s, x, y, tx, ty) com tangente SUAVIZADA
    (media numa janela de +-2,5) - as fiadas de lajes viram nas curvas sem sobrepor"""
    P = [Vector((x, y, 0.0)) for x, y in pts]
    if ext0:
        d = (P[0] - P[1]).normalized()
        P.insert(0, P[0] + d * ext0)
    if ext1:
        d = (P[-1] - P[-2]).normalized()
        P.append(P[-1] + d * ext1)
    segs = list(zip(P, P[1:]))
    total = sum((b - a).length for a, b in segs)
    out = []
    s = 0.0
    while s <= total + 1e-6:
        acc = 0.0
        for a, b in segs:
            ln = (b - a).length
            if acc + ln >= s - 1e-9 or (a, b) == segs[-1]:
                t = min(1.0, max(0.0, (s - acc) / ln))
                p = a + (b - a) * t
                out.append([s, p.x, p.y, (b - a).x / ln, (b - a).y / ln])
                break
            acc += ln
        s += step
    sm = []
    for i, st in enumerate(out):
        k = 5
        tx = sum(o[3] for o in out[max(0, i - k):i + k + 1])
        ty = sum(o[4] for o in out[max(0, i - k):i + k + 1])
        ln = math.hypot(tx, ty) or 1.0
        sm.append((st[0], st[1], st[2], tx / ln, ty / ln))
    return sm, total


def station_at(st, s):
    i = min(len(st) - 1, max(0, int(round(s / (st[1][0] - st[0][0])))))
    return st[i]


def slab(mb, quad, z, top=SLAB_TOP, th=0.45, ch=0.08, m=None):
    """laje com chanfro no topo (quad anti-horario em planta); m=None mistura 2 pedras pela posicao (laje media
    ~70% / caminho claro ~30%, DIRIGIDO por hash: nada de faixa de uma cor so)"""
    if m is None:
        cx_, cy_ = sum(p[0] for p in quad) / 4, sum(p[1] for p in quad) / 4
        m = STP if hh(round(cx_, 1), round(cy_, 1), "mat") < 0.3 else LAJE
    _slab(mb, quad, z, top, th, ch, m)


def _slab(mb, quad, z, top, th, ch, m):
    """laje com chanfro no topo (quad anti-horario em planta)"""
    bm = mb.bm
    c = (sum(p[0] for p in quad) / 4, sum(p[1] for p in quad) / 4)
    inner = [(p[0] + (c[0] - p[0]) * ch / max(0.4, math.dist(p, c)) * 1.4,
              p[1] + (c[1] - p[1]) * ch / max(0.4, math.dist(p, c)) * 1.4) for p in quad]
    vt = [bm.verts.new((x, y, z + top)) for x, y in inner]
    vm = [bm.verts.new((x, y, z + top - ch)) for x, y in quad]
    vb = [bm.verts.new((x, y, z + top - th)) for x, y in quad]
    bm.faces.new(vt)
    for k in range(4):
        j = (k + 1) % 4
        bm.faces.new((vm[k], vm[j], vt[j], vt[k]))
        bm.faces.new((vb[k], vb[j], vm[j], vm[k]))
    mb._post(vt + vm + vb, m, None, 0, 1)


def lay_street(mb, pts, z, key, ext0, ext1, half=2.4, wide=(), s_from=0.0, s_to=None):
    """terra batida (faixa de 4,0 de meia-largura) + lajes na faixa central (meia-largura 'half', alargando nos nos
    'wide' = [(s, meia-largura extra, alcance)]). As lajes da borda saem em sorteio DIRIGIDO (hh) -> a faixa se desfaz
    na terra; juntas de 0,22 mostram a terra"""
    st, total = polyline_stations(pts, ext0, ext1)
    s_to = total if s_to is None else s_to
    # terra batida: poligono unico (esquerda + direita invertida), so entre s_from e s_to
    left, right = [], []
    for s, x, y, tx, ty in st:
        if s_from - 1e-6 <= s <= s_to + 1e-6:
            nx, ny = -ty, tx
            left.append((x + nx * DIRT_HW, y + ny * DIRT_HW))
            right.append((x - nx * DIRT_HW, y - ny * DIRT_HW))
    poly = left[::2] + [left[-1]] + list(reversed(right[::2] + [right[-1]]))
    mb.prism(ccw(poly), z - 0.6, z + DIRT_TOP, DIRT)

    def hw_at(s):
        e = 0.0
        for s0, extra, reach in wide:
            e = max(e, extra * max(0.0, 1.0 - abs(s - s0) / reach))
        return half + e
    n = 0
    s, r = s_from + 0.3, 0
    depth = (2.3, 2.8, 2.0, 2.6, 3.0, 2.2)
    widths = (2.6, 2.0, 3.0, 2.3, 2.8, 1.8, 2.4)
    while s < s_to - 0.6:
        d = min(cyc(depth, r), s_to - 0.3 - s)
        if d < 0.8:
            break
        a0, a1 = station_at(st, s), station_at(st, s + d)
        hw = hw_at(s + d / 2)
        t = -hw - (0.6 if r % 2 else 0.0)
        c = 0
        while t < hw - 0.4:
            w = cyc(widths, r * 5 + c + int(hh(key, "w") * 7))
            t0, t1 = max(t, -hw), min(t + w, hw)
            edge = t0 <= -hw + 0.01 or t1 >= hw - 0.01
            keep = (not edge) or hh(key, r, c, "e") > 0.3
            if t1 - t0 > 0.7 and keep:
                g = 0.11
                jit = [(hh(key, r, c, k) - 0.5) * 0.24 for k in range(8)]
                q = []
                for k, (aa, tt) in enumerate(((a0, t0 + g), (a1, t0 + g), (a1, t1 - g), (a0, t1 - g))):
                    sgn = 1.0 if aa is a0 else -1.0
                    _, x, y, tx, ty = aa
                    nx, ny = -ty, tx
                    ss = g * sgn + jit[2 * k] * 0.5
                    tt += jit[2 * k + 1]
                    q.append((x + tx * ss + nx * tt, y + ty * ss + ny * tt))
                slab(mb, ccw(q), z)
                n += 1
            t += w
            c += 1
        s += d
        r += 1
    return n, st


def street_lamp(mb, x, y, z, toward, name, h=8.6):
    """lanterna de poste do kit com o braco virado para 'toward' (x, y) + colisao do poste"""
    a = math.atan2(toward[1] - y, toward[0] - x) - math.pi / 2
    K.lantern_post(mb, Frame(x, y, z, a), h, 1.9, name, 45.0)
    col_box("DS_VilLamp", (0.9, 0.9, h), (x, y, z + h / 2))


def street_low():
    mb = MB("DS_Vil_StreetLow", C, detail="near")
    pts = L.VILLAGE_STREET
    st, total = polyline_stations(pts, 4.0, 4.0)
    p2, _ = door_world("V2")
    nodes = ((s_of(st, *L.VILLAGE_GATE), 1.3, 6.0), (s_of(st, p2.x, p2.y), 0.9, 5.0), (total - 4.0, 1.3, 7.0))
    n, st = lay_street(mb, pts, T1, "rb", 4.0, 4.0, 2.3, wide=nodes)
    # portao da vila: 2 postes-lanterna altos + marco de pedra (nao e torii)
    gx, gy = L.VILLAGE_GATE
    (ax, ay), (bx_, by_) = L.VILLAGE_STREET[0], L.VILLAGE_STREET[2]
    sl = math.hypot(bx_ - ax, by_ - ay)
    ux, uy = (bx_ - ax) / sl, (by_ - ay) / sl
    px, py = uy, -ux                                  # perpendicular (para a direita de quem sobe)
    for s in (-1, 1):
        x, y = gx + s * 5.4 * px, gy + s * 5.4 * py
        street_lamp(mb, x, y, T1, (gx, gy), "L_DSProp_Lamp_Vil_Gate%s" % ("L" if s < 0 else "R"), 10.4)
    marker_stone(mb, gx - 9.6 * px - 1.0 * ux, gy - 9.6 * py - 1.0 * uy, T1, math.atan2(uy, ux) - math.pi)
    # lanterna no ramal do V2 (lado da rua oposto as casas) e no pe da VilaAlta
    street_lamp(mb, -50.2, 160.0, T1, (-58.0, 162.0), "L_DSProp_Lamp_Vil_Low")
    street_lamp(mb, -91.5, 214.5, T1, (-84.0, 213.0), "L_DSProp_Lamp_Vil_AltaFoot")
    # escada VilaAlta (envelope do ds_col) e VilaClareira (do T1 da margem oeste ao T2)
    plan_stair_kit(mb, "VilaAlta")
    plan_stair_kit(mb, "VilaClareira")
    branch_paths(mb, ("V1", "V2", "V3"))
    yard_fences(mb, st)
    well(mb)                                          # poco e oratorio no mesmo objeto (MeshParts por material)
    hokora(mb)
    mb.finish()
    return n


def street_high():
    mb = MB("DS_Vil_StreetHigh", C, detail="near")
    pts = L.VILLAGE_STREET_HIGH
    st, total = polyline_stations(pts, 1.55, 4.0)
    p6 = (GARDEN_E, HOUSE_BY["V6"][1][1])
    nodes = ((0.0, 1.3, 6.0), (s_of(st, -78.0, 284.0), 1.3, 8.0), (s_of(st, p6[0], p6[1]), 1.3, 8.0))
    n, st = lay_street(mb, pts, T2, "ra", 1.55, 4.0, 2.3, wide=nodes)
    # largo da VilaClareira: lajes do topo da escada ate a rua (y 284)
    sx0, sx1 = L.stair_top("VilaClareira")[0], -76.5
    k = 0
    x = sx0 - 0.3
    while x > sx1 + 0.8:
        d = cyc((1.9, 2.2, 1.7, 2.4), k)
        t = -3.3 - (0.5 if k % 2 else 0.0)
        c = 0
        while t < 3.3:
            w = cyc((2.3, 1.8, 2.6, 2.0), k * 3 + c)
            t0, t1 = max(t, -3.3), min(t + w, 3.3)
            if t1 - t0 > 0.7 and (abs(t0) < 3.2 or hh("vc", k, c) > 0.35):
                q = [(x - 0.11, 284.0 + t0 + 0.11), (x - 0.11, 284.0 + t1 - 0.11), (x - d + 0.11, 284.0 + t1 - 0.11),
                     (x - d + 0.11, 284.0 + t0 + 0.11)]
                slab(mb, ccw(q), T2)
            t += w
            c += 1
        x -= d
        k += 1
    street_lamp(mb, -63.5, 276.5, T2, (-60.0, 284.0), "L_DSProp_Lamp_Vil_Clareira")
    street_lamp(mb, -91.0, 234.0, T2, (-84.0, 236.0), "L_DSProp_Lamp_Vil_AltaTop")
    street_lamp(mb, -78.5, 345.0, T2, (-72.0, 344.0), "L_DSProp_Lamp_Vil_OesteForja")
    street_lamp(mb, -79.5, 326.0, T2, (-80.0, 338.0), "L_DSProp_Lamp_Vil_V6Gate")
    plan_stair_kit(mb, "OesteForja")
    branch_paths(mb, ("V4", "V5"))
    gate_path_V6(mb)
    edge_fence(mb)
    mb.finish()
    return n


def gate_path_V6(mb):
    """lajes do portao do V6 ate a terra batida da rua (o portao fica 13 para dentro da rua)"""
    cy = HOUSE_BY["V6"][1][1]
    x = GARDEN_E + 1.0
    k = 0
    xe = -67.3 - 3.2                                   # borda da terra batida em y 338
    while x < xe - 0.6:
        d = min(cyc((2.0, 2.4, 1.8, 2.2), k), xe - x)
        t = -3.0 - (0.45 if k % 2 else 0.0)
        c = 0
        while t < 3.0:
            w = cyc((2.2, 1.9, 2.5), k * 2 + c)
            t0, t1 = max(t, -3.0), min(t + w, 3.0)
            if t1 - t0 > 0.7:
                q = [(x + 0.11, cy + t0 + 0.11), (x + d - 0.11, cy + t0 + 0.11), (x + d - 0.11, cy + t1 - 0.11),
                     (x + 0.11, cy + t1 - 0.11)]
                slab(mb, ccw(q), T2)
            t += w
            c += 1
        x += d
        k += 1


def marker_stone(mb, x, y, z, ang):
    """marco de pedra do portao da vila (dohyo): base em 2 degraus, fuste com topo em pirâmide baixa e painel
    rebaixado na face da rua (sem letreiro)"""
    F = Frame(x, y, z, ang)
    bb(mb, F, -1.7, 1.7, -1.4, 1.4, -0.3, 0.5, ST, 0.1)
    bb(mb, F, -1.25, 1.25, -1.0, 1.0, 0.5, 1.0, ST, 0.08)
    ext(mb, F, [(-0.7, -0.55), (0.7, -0.55), (0.7, 0.55), (-0.7, 0.55)], "z", 1.0, 5.6, ST, 0.08)
    lathe(mb, F, (0.0, 0.0, 5.6), [(0.99, 0.0), (0.7, 0.42), (0.05, 0.7)], 4, ST, math.pi / 4)
    bb(mb, F, -0.45, 0.45, 0.5, 0.69, 1.8, 4.9, STD)
    col_box("DS_VilMarker", (1.6, 1.4, 6.3), F.p(0, 0, 3.15), F.r())


def plan_stair_kit(mb, name):
    """escada da planta com a pedra do kit (focinho chanfrado, espelho escuro recuado, banzos em degraus) no MESMO
    envelope do ds_col (largura, degraus, espelho, pisada): pe do 1o espelho em L.stair_frame"""
    foot, deg, w, n, tread, g = L.stair_frame(name)
    rise = L.stair_rise(name)
    F = Frame(foot[0], foot[1], foot[2], math.radians(deg) - math.pi / 2)
    K.stair_stone(mb, F, w, n, rise, tread, True)


# ------------------------------------------------------------------ ramais (rua -> porta) e cercas
def door_world(nm):
    """centro da soleira da porta da frente (mundo) e rumo da frente"""
    F = house_frame(nm)
    sp = full_spec(nm)
    fb = sp["front"] if isinstance(sp["front"], list) else []
    ph = sp["plinth"][1]
    if sp.get("kura"):
        return F.p(0.0, sp["D"] / 2 + 1.5, 0.0), F
    for t, a, b in bay_spans(sp["W"], fb, sp["door_w"]):
        if t in ("door", "open_door", "itado"):
            return F.p((a + b) / 2, sp["D"] / 2, 0.0), F
    return F.p(0.0, sp["D"] / 2, 0.0), F


def branch_paths(mb, names):
    """pisantes (tobi-ishi) da rua ate os degraus de cada casa: pedras irregulares 0,3 acima do chao (acima da grama
    de 0,18), em zigue-zague leve; V6 tem o proprio caminho dentro do jardim (garden_V6)"""
    for nm in names:
        if nm == "V6":
            continue
        F = house_frame(nm)
        sp = full_spec(nm)
        z = HOUSE_BY[nm][2]
        p0, _ = door_world(nm)
        dx, dy = math.cos(math.radians(HOUSE_BY[nm][3])), math.sin(math.radians(HOUSE_BY[nm][3]))
        start = 4.6 if not sp.get("kura") else 5.2
        if "F" in sp["engawa"]:
            start = sp["engawa_d"] + 4.6
        pts = L.VILLAGE_STREET + [(-84.0, 216.0)] if z == T1 else L.VILLAGE_STREET_HIGH
        k = 0
        u = start
        while k < 14:
            x, y = p0.x + dx * u, p0.y + dy * u
            if L.polyline_dist(x, y, pts) < 3.6:
                break
            off = (0.55 if k % 2 else -0.55) * (0.6 + 0.5 * hh(nm, "o", k))
            cx, cy = x - dy * off, y + dx * off
            w_ = 2.0 + 0.6 * hh(nm, "w", k)
            d_ = 1.5 + 0.4 * hh(nm, "d", k)
            rot = math.atan2(dy, dx) + (hh(nm, "r", k) - 0.5) * 0.5
            poly = [(cx + math.cos(rot) * d_ / 2 * math.cos(2 * math.pi * j / 9) * (0.92 + 0.16 * hh(nm, k, j))
                     - math.sin(rot) * w_ / 2 * math.sin(2 * math.pi * j / 9) * (0.92 + 0.16 * hh(nm, j, k)),
                     cy + math.sin(rot) * d_ / 2 * math.cos(2 * math.pi * j / 9) * (0.92 + 0.16 * hh(nm, k, j))
                     + math.cos(rot) * w_ / 2 * math.sin(2 * math.pi * j / 9) * (0.92 + 0.16 * hh(nm, j, k)))
                    for j in range(9)]
            mb.prism(ccw(poly), z - 0.25, z + 0.34, STP, 0.0)
            u += 2.3 + 0.3 * hh(nm, "s", k)
            k += 1


def s_of(st, x, y):
    """arco (s) da estacao mais proxima de (x, y)"""
    return min(st, key=lambda o: (o[1] - x) ** 2 + (o[2] - y) ** 2)[0]


def offset_line(st, off, s0, s1, step=2.0):
    """pontos da paralela a rua (off > 0 = lado esquerdo de quem sobe = casas) entre s0 e s1"""
    out = []
    for s, x, y, tx, ty in st:
        if s0 - 1e-6 <= s <= s1 + 1e-6 and (not out or s - out[-1][0] >= step - 1e-6 or s >= s1 - 0.25):
            out.append((s, x - ty * off, y + tx * off))
    return [(x, y) for s, x, y in out]


def rail_fence(mb, pts, z, h=2.8, step=3.6):
    """cerca baixa ABERTA de mouroes e 2 travessas passantes (nuki), mourao chanfrado com capitel em piramide: le de
    longe como cerca (nao como muro) e deixa ver as casas por cima/por entre"""
    P = [Vector((x, y, 0.0)) for x, y in pts]
    F0 = Frame(0.0, 0.0, z, 0.0)
    for i, (a, b_) in enumerate(zip(P, P[1:])):
        d = b_ - a
        ln = d.length
        if ln < 0.3:
            continue
        ang = math.atan2(d.y, d.x)
        nseg = max(1, int(math.ceil(ln / step)))
        last = i == len(P) - 2
        for j in range(nseg + (1 if last else 0)):
            q = a + d * (j / nseg)
            bx(mb, F0, q.x, q.y, (h - 0.1) / 2 - 0.15, 0.44, 0.44, h + 0.05, WD, 0.05, rz=ang)
            lathe(mb, F0, (q.x, q.y, h - 0.12), [(0.36, 0.0), (0.02, 0.32)], 4, WD, ang + math.pi / 4)
        e0 = 0.3 if i == 0 else 0.0
        e1 = 0.3 if last else 0.0
        c = (a + b_) / 2 + d.normalized() * (e1 - e0) / 2
        for zz, th in ((h * 0.4, 0.26), (h * 0.8, 0.3)):
            bx(mb, F0, c.x, c.y, zz, ln + e0 + e1, 0.18, th, WM, 0.03, rz=ang)


def yotsume(mb, pts, z, h=3.2, step=3.6):
    """cerca de bambu aberta (yotsume-gaki) LEVE: mouroes de madeira, 3 varas horizontais e montantes de bambu
    alternados na frente/atras (sem amarras: tris)"""
    P = [Vector((x, y, 0.0)) for x, y in pts]
    F0 = Frame(0.0, 0.0, z, 0.0)
    for i, (a, b_) in enumerate(zip(P, P[1:])):
        d = b_ - a
        ln = d.length
        if ln < 0.3:
            continue
        u = d.normalized()
        nv = Vector((-u.y, u.x, 0.0))
        ang = math.atan2(d.y, d.x)
        nseg = max(1, int(math.ceil(ln / step)))
        for j in range(nseg + (1 if i == len(P) - 2 else 0)):
            q = a + d * (j / nseg)
            bx(mb, F0, q.x, q.y, (h + 0.3) / 2 - 0.2, 0.36, 0.36, h + 0.3, WD, 0.04, rz=ang)
        for zz in (0.75, h * 0.52, h - 0.2):
            o = nv * 0.24
            mb.rod(F0.p(a.x + o.x, a.y + o.y, zz), F0.p(b_.x + o.x, b_.y + o.y, zz), 0.09, K.BAMBOO, 5)
        nvb = max(2, int(round(ln / 0.9)))
        for j in range(1, nvb):
            q = a + d * (j / nvb)
            o = nv * (0.06 if j % 2 else 0.42)
            mb.rod(F0.p(q.x + o.x, q.y + o.y, -0.1), F0.p(q.x + o.x, q.y + o.y, h - 0.05 - 0.25 * (j % 3 == 0)),
                   0.075, K.BAMBOO, 5)


def fence_col(area, pts, z, h):
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        col_box(area, (math.hypot(x1 - x0, y1 - y0) + 0.3, 0.7, h + 0.2), ((x0 + x1) / 2, (y0 + y1) / 2, z + h / 2),
                (0, 0, math.atan2(y1 - y0, x1 - x0)))


def fence_run(mb, pts, z, area, h=2.8, style="rail", col=True):
    (rail_fence if style == "rail" else yotsume)(mb, pts, z, h)
    if col:
        fence_col(area, pts, z, h)


def yard_fences(mb, st):
    """cerca baixa de ripas na frente do quintal do V2 (paralela a rua, 5,4 do eixo = 1,4 da terra batida), aberta no
    ramal da porta; colisao fina por trecho"""
    F = house_frame("V2")
    sp = full_spec("V2")
    W, D = sp["W"], sp["D"]
    ss = sorted(s_of(st, *tuple(F.p(sx * (W / 2 + 0.6), D / 2 + 0.6, 0.0))[:2]) for sx in (-1, 1))
    p, _ = door_world("V2")
    sm = s_of(st, p.x, p.y)
    for a, b in ((ss[0] - 2.0, sm - 2.4), (sm + 2.4, ss[1] + 3.0)):
        if b - a > 2.0:
            fence_run(mb, offset_line(st, 5.4, a, b), T1, "DS_VilFence", 2.6, "rail")


def edge_fence(mb):
    """cerca baixa na borda do T2 sobre a clareira, 0,7 para dentro da borda (a guarda invisivel do ds_col fica logo
    atras e e ela que segura o jogador: a cerca so a torna legivel); aberta no topo da VilaClareira"""
    P = ccw(DL.offset_poly(L.VILLAGE_HIGH, -0.7))
    pts = []
    for (x0, y0), (x1, y1) in zip(P, P[1:] + P[:1]):
        n = max(1, int(math.hypot(x1 - x0, y1 - y0) / 1.0))
        for k in range(n):
            pts.append((x0 + (x1 - x0) * k / n, y0 + (y1 - y0) * k / n))
    ok = lambda x, y: x > -77.0 and (229.0 <= y <= 278.2 or 289.8 <= y <= 340.0)
    runs, cur = [], []
    for q in pts:
        if ok(*q):
            cur.append(q)
        elif cur:
            runs.append(cur)
            cur = []
    if cur:
        runs.append(cur)
    for r in runs:
        r = sorted(r, key=lambda q: q[1])
        if len(r) < 3:
            continue
        simp = [r[0]]
        for q in r[1:]:
            if math.dist(q, simp[-1]) >= 3.8:
                simp.append(q)
        if math.dist(r[-1], simp[-1]) > 0.8:
            simp.append(r[-1])
        fence_run(mb, simp, T2, "DS_VilFence", 2.8, "rail", col=False)


# ================================================================== POCO E ORATORIO (borda oeste da clareira)
WELL = (-39.0, 196.0)             # planta: (-30, 196) caia em cima da trilha de terra do ds_terrain (x -29,4)
HOKORA = (-47.5, 206.5)           # planta: (-34, 214) caia na trilha de terra e no inicio da cerca da borda (-42, 214)


def well(mb):
    """poco coberto: bocal de pedra octogonal em 2 fiadas com capa, tampa de tabuas pela metade, 2 esteios com
    travessa, roldana de ferro, corda e balde (oke) de aduelas com aros, telhadinho kirizuma; lajes em volta"""
    x, y = WELL
    F = Frame(x, y, T1, math.radians(15.0))
    for i in range(8):
        a = 2 * math.pi * i / 8 + math.pi / 8
        Fs = sub(F, 2.05 * math.cos(a), 2.05 * math.sin(a), 0.0, a - math.pi / 2)
        for k, (z0, z1) in enumerate(((-0.3, 0.95), (0.95, 2.1))):
            K.stone(mb, Fs, -0.82 + 0.04, 0.82 - 0.04, z0 + 0.04, z1 - 0.04, -0.45, 0.35, 0.33, 0.12, ST)
        K.stone(mb, Fs, -0.86, 0.86, 2.1, 2.42, -0.5, 0.45, 0.45, 0.08, STP)
    lathe(mb, F, (0, 0, 0), [(1.5, -0.3), (1.5, 1.6)], 8, STD, math.pi / 8)                 # miolo escuro (agua)
    for k in range(5):                                                                      # tampa pela metade
        bb(mb, F, -1.7, 0.0, -1.6 + k * 0.66 + 0.03, -1.6 + (k + 1) * 0.66 - 0.03, 2.42, 2.6, WM)
    bb(mb, F, -1.0, -0.8, -1.65, 1.65, 2.6, 2.75, WD)
    for s in (-1, 1):
        K.rock_base(mb, F, s * 2.9, 0.0, 0.0, 0.6, 0.35)
        bb(mb, F, s * 2.9 - 0.28, s * 2.9 + 0.28, -0.28, 0.28, 0.3, 7.6, WD, 0.06)
    bb(mb, F, -3.6, 3.6, -0.24, 0.24, 6.2, 6.7, WD, 0.05)
    mb.cyl(0.42, 0.28, F.p(0.0, 0.0, 5.75), (math.pi / 2, 0, F.a), IRON, 10, bevel=0.0)       # roldana
    bb(mb, F, -0.06, 0.06, -0.06, 0.06, 5.75, 6.2, IRON)
    mb.rod(F.p(0.0, 0.36, 5.75), F.p(0.0, 0.36, 3.6), 0.04, BAMBOO_ROPE, 5)
    mb.rod(F.p(0.0, -0.36, 5.75), F.p(0.6, -1.2, 2.6), 0.04, BAMBOO_ROPE, 5)
    lathe(mb, F, (0.0, 0.36, 2.75), [(0.45, 0.0), (0.52, 0.85), (0.0, 0.85)], 8, WM)        # balde (pendurado)
    for zz in (0.18, 0.62):
        lathe(mb, F, (0.0, 0.36, 2.75 + zz), [(0.5 + zz * 0.08, 0.0), (0.5 + zz * 0.08, 0.1)], 8, IRON)
    K.roof_gable(mb, sub(F, 0.0, 0.0, 0.0, 0.0), 7.2, 4.4, 7.6, 0.62, 1.0, 0.7, 0.2, 0.32, 1, PL, "none", False, RT,
                 0.5, 1.2, 0.55)
    # lajes em volta (pateo de servico) e a pedra de pisar
    for i in range(10):
        a = 2 * math.pi * (i + 0.5) / 10
        r0, r1 = 3.0, 4.6 + 0.4 * hh("wl", i)
        q = [(r0 * math.cos(a - 0.29), r0 * math.sin(a - 0.29)), (r1 * math.cos(a - 0.27), r1 * math.sin(a - 0.27)),
             (r1 * math.cos(a + 0.27), r1 * math.sin(a + 0.27)), (r0 * math.cos(a + 0.29), r0 * math.sin(a + 0.29))]
        slab(mb, ccw([tuple(F.p(px, py, 0.0))[:2] for px, py in q]), T1, 0.32)
    col_box("DS_VilWell", (5.4, 5.4, 2.6), (x, y, T1 + 1.3))
    for s in (-1, 1):
        p = F.p(s * 2.9, 0.0, 0.0)
        col_box("DS_VilWell", (0.7, 0.7, 7.6), (p.x, p.y, T1 + 3.8))


BAMBOO_ROPE = "Bamboo_DS_Dry"


def hokora(mb):
    """oratorio de vila (hokora): soco de pedra em 2 degraus, caixa de madeira com portinhas de trelica e telhado
    nagare (agua da frente mais longa), corda (shimenawa) com shide de papel, caixa de oferendas e 2 toro oki; sem torii"""
    x, y = HOKORA
    F = Frame(x, y, T1, math.radians(-100.0))         # frente para o poco e a trilha da margem (leste)
    bb(mb, F, -2.4, 2.4, -2.2, 2.2, -0.3, 0.7, ST, 0.1)
    bb(mb, F, -1.8, 1.8, -1.7, 1.6, 0.7, 1.5, ST, 0.08)
    bb(mb, F, -1.5, 1.5, -1.4, 1.3, 1.5, 1.75, WD, 0.04)
    bb(mb, F, -1.25, 1.25, -1.2, 1.0, 1.75, 4.1, WM, 0.04)
    for s in (-1, 1):
        bb(mb, F, s * 1.25 - 0.18, s * 1.25 + 0.18, 0.82, 1.18, 1.75, 4.3, WD, 0.03)
    for s in (-1, 1):                                   # portinhas de trelica com papel atras
        bb(mb, F, s * 0.55 - 0.48, s * 0.55 + 0.48, 0.98, 1.02, 2.0, 3.8, PAPER)
        for xx in K.even(s * 0.55 - 0.48, s * 0.55 + 0.48, 0.24):
            bb(mb, F, xx - 0.03, xx + 0.03, 1.02, 1.08, 2.0, 3.8, WD)
        for zz in (2.0, 2.9, 3.8):
            bb(mb, F, s * 0.55 - 0.5, s * 0.55 + 0.5, 1.02, 1.1, zz - 0.04, zz + 0.04, WD)
    K.roof_gable(mb, sub(F, 0.0, 0.25, 0.0, 0.0), 3.4, 3.2, 4.25, 0.7, 0.9, 0.5, 0.25, 0.22, 1, WD, "none", False, RT,
                 0.4, 0.9, 0.38)
    mb.rod(F.p(-1.4, 1.35, 3.95), F.p(1.4, 1.35, 3.95), 0.12, BAMBOO_ROPE, 8)          # shimenawa
    for xx in (-0.7, 0.7):
        ext(mb, F, [(xx - 0.15, 3.85), (xx + 0.12, 3.85), (xx + 0.0, 3.35), (xx + 0.2, 3.3), (xx - 0.05, 2.9),
                    (xx - 0.2, 2.95)], "y", 1.4, 1.44, PAPER)
    bb(mb, F, -0.9, 0.9, 1.8, 2.6, 0.7, 1.4, WD, 0.04)                                  # caixa de oferendas
    for xx in K.even(-0.8, 0.8, 0.22)[1:-1]:
        bb(mb, F, xx - 0.05, xx + 0.05, 1.85, 2.55, 1.38, 1.54, WM)
    for s in (-1, 1):
        K.toro(mb, sub(F, s * 3.4, 1.4, 0.0), "oki", 0.85)
    col_box("DS_VilHokora", (4.8, 4.4, 4.6), (x, y, T1 + 2.3), (0, 0, F.a))


# ================================================================== ancoras para o ds_props (onda 3b) - SO DADOS
# (nome, x, y, z, raio livre, o que cabe ali) - a vila deixa o espaco; ninguem cria geometria aqui
PROP_ANCHORS = [
    ("V2_horta", -101.0, 138.0, T1, 7.0, "horta em canteiros + espantalho/cerca de bambu (fundo-sul do V2)"),
    ("V2_varal", -104.0, 176.0, T1, 4.0, "varal de bambu com roupas (lado norte do V2)"),
    ("V2_engawa", -79.0, 144.0, T1, 3.0, "cesto/peneira de arroz na engawa sul"),
    ("V3_patio", -82.0, 186.0, T1, 4.0, "rebolo de afiar, tabuas encostadas, barril de agua (frente da oficina)"),
    ("V1_rua", -55.0, 121.0, T1, 2.5, "banco externo + guarda-sol de papel (wagasa) na frente da chaya"),
    ("V4_patio", -113.0, 236.5, T2, 3.5, "barris e sacos de arroz na frente do kura (ele olha para o sul)"),
    ("V5_frente", -88.0, 296.0, T2, 3.0, "vasos de planta e tina de agua ao lado da porta"),
    ("V5_varal", -116.0, 306.0, T2, 4.0, "varal (fundo do sobrado)"),
    ("V6_jardim", -96.0, 326.0, T2, 4.0, "pedras de jardim, bacia de agua (tsukubai) - sem lagoa"),
    ("Mirante_T2", -60.0, 300.0, T2, 3.0, "banco na borda do T2 olhando a clareira"),
]


# ================================================================== QA: rotas para DENTRO das casas visitaveis
def qa_routes():
    """rotas do andador (fm_qa.walk) da rua para dentro do V1 e do V6 (porta >= 5 de vao livre, sem prender):
    {nome: ([(x, y)...], z_inicial)}"""
    out = {}
    F = house_frame("V1")
    sp = full_spec("V1")
    D = sp["D"]
    p = lambda x, y: tuple(F.p(x, y, 0.0))[:2]
    out["RUA->V1 (chaya, vao do meio)"] = ([p(0.0, D / 2 + 9.0), p(0.0, D / 2 + 2.0), p(0.0, 0.0), p(-1.0, -1.0),
                                            p(-2.0, 1.2), p(2.6, 1.2)], T1)
    out["RUA->V1 (lateral aberta do portao)"] = ([p(13.0, 2.4), p(7.5, 2.4), p(2.0, 2.4), p(0.0, 2.0)], T1)
    F = house_frame("V6")
    sp = full_spec("V6")
    D = sp["D"]
    p = lambda x, y: tuple(F.p(x, y, 0.0))[:2]
    cy = HOUSE_BY["V6"][1][1]
    out["RUA->V6 (portao, jardim, porta, irori, zashiki)"] = (
        [(-72.0, cy), (GARDEN_E + 4.0, cy), (GARDEN_E - 3.0, cy), p(0.0, D / 2 + 8.0), p(0.0, D / 2 + 1.0),
         p(0.0, 5.0), p(0.0, 1.5), p(0.0, -2.0), p(-5.0, -2.0), p(4.0, -2.5)], T2)
    out["V6 genkan -> volta do irori -> bau"] = ([p(0.0, 8.0), p(-10.0, 8.0), p(-10.0, 1.9), p(9.0, 1.9),
                                                    p(10.0, 6.0)],
                                                  T2 + sp["plinth"][1] + 0.66)
    return out


def qa_run():
    """roda as rotas internas sobre as colisoes COL_ (como o ds_qa.nav); devolve a lista de falhas"""
    import fm_qa
    import ds_qa
    bvh, n = ds_qa.col_bvh()
    bad = []
    for nm, (pts, z0) in qa_routes().items():
        f, z = fm_qa.walk(bvh, pts, z0)
        print(("OK   " if not f else "FAIL ") + "ROTA_VILA " + nm + ("" if not f else "  " + str(f)))
        if f:
            bad.append(nm)
    return bad


# ================================================================== cameras de estudio (closes da zona)
def _hc(nm, side, dist, eye_z, tz, lens=24, fwd=0.0):
    """camera de 3/4 da casa: alvo no meio da fachada da frente (tz acima do chao), olho a 'dist' na diagonal"""
    F = house_frame(nm)
    sp = full_spec(nm)
    D = sp["D"]
    t = F.p(0.0, D / 2 + fwd, tz)
    e = F.p(side * dist * 0.62, D / 2 + dist * 0.78, eye_z)
    return (tuple(round(c, 2) for c in e), tuple(round(c, 2) for c in t), lens)


def _cams():
    c = {
        "CAM_DSVil_Aerial": ((-14.0, 168.0, 132.0), (-96.0, 258.0, 64.0), 24),
        "CAM_DSVil_AerialN": ((-34.0, 410.0, 140.0), (-96.0, 250.0, 64.0), 24),
        "CAM_DSVil_FromClearing": ((-6.0, 240.0, T1 + 5.5), (-104.0, 286.0, T2 + 9.0), 22),
        "CAM_DSVil_PH_Gate": ((-24.0, 98.0, T1 + 5.5), (-66.0, 150.0, T1 + 6.0), 22),
        "CAM_DSVil_PH_StreetLow": ((-50.0, 136.0, T1 + 5.5), (-88.0, 214.0, T1 + 7.0), 22),
        "CAM_DSVil_PH_StreetHigh": ((-83.0, 238.0, T2 + 5.5), (-72.0, 336.0, T2 + 7.0), 22),
        "CAM_DSVil_PH_V6Gate": ((-70.0, 330.0, T2 + 5.5), (-114.0, 340.0, T2 + 7.0), 22),
        "CAM_DSVil_Well": ((-26.0, 186.0, T1 + 6.0), (-40.0, 200.0, T1 + 3.0), 26),
        "CAM_DSVil_Hokora": ((-37.5, 203.0, T1 + 4.5), (-47.5, 206.5, T1 + 2.4), 28),
        "CAM_DSVil_LampGate": ((-27.0, 112.0, T1 + 8.0), (-33.4, 118.8, T1 + 7.5), 30),
        "CAM_DSVil_GateMarker": ((-34.0, 106.0, T1 + 4.5), (-46.0, 109.5, T1 + 3.2), 26),
        "CAM_DSVil_PH_VilaClareira": ((-30.0, 290.0, T1 + 5.5), (-62.0, 284.0, T2 + 4.0), 22),
        "CAM_DSVil_PH_OesteForja": ((-74.0, 318.0, T2 + 5.5), (-66.0, 360.0, T2 + 9.0), 22),
    }
    for nm, side, dist, ez, tz in (("V1", -1, 26.0, 9.0, 6.0), ("V2", 1, 34.0, 10.0, 7.0), ("V3", 1, 30.0, 8.0, 7.0),
                                   ("V4", 1, 32.0, 9.0, 11.0), ("V5", -1, 36.0, 12.0, 11.0), ("V6", 1, 44.0, 14.0, 9.0)):
        c["CAM_DSVil_%s" % nm] = _hc(nm, side, dist, ez, tz)                 # alturas relativas ao chao da casa
        c["CAM_DSVil_%s_PH" % nm] = _hc(nm, -side * 0.4, 14.0, 5.5, 5.8, 22)
    # interiores: V1 visto da rua e de dentro; V6 visto da porta (altura do jogador no degrau) e de dentro
    F = house_frame("V1")
    sp = full_spec("V1")
    z = T1 + sp["plinth"][1] + 0.66
    c["CAM_DSVil_V1_In"] = (tuple(F.p(-4.6, 2.6, 5.4)), tuple(F.p(3.0, -4.6, 3.6)), 18)
    c["CAM_DSVil_V1_Door"] = (tuple(F.p(1.0, 12.0, 5.5 - 0.2)), tuple(F.p(0.6, -3.0, 4.2)), 22)
    F = house_frame("V6")
    sp = full_spec("V6")
    z = sp["plinth"][1] + 0.66
    c["CAM_DSVil_V6_Door"] = (tuple(F.p(0.0, 15.2, z + 4.6)), tuple(F.p(-1.5, -6.0, z + 4.2)), 20)
    c["CAM_DSVil_V6_In"] = (tuple(F.p(5.0, 8.6, z + 5.5)), tuple(F.p(-3.0, -7.6, z + 3.4)), 16)
    c["CAM_DSVil_V6_InBack"] = (tuple(F.p(-8.0, -6.8, z + 0.36 + 5.5)), tuple(F.p(2.0, 9.0, z + 3.8)), 16)
    F2 = house_frame("V2")
    c["CAM_DSVil_RoofClose_V2"] = (tuple(F2.p(5.0, 22.0 / 2 + 7.0, 1.6 + 12.5 + 7.5)), tuple(F2.p(1.0, 22.0 / 2 - 4.0, 1.6 + 12.5 + 4.0)), 26)
    c["CAM_DSVil_RoofClose_V6"] = (tuple(F.p(15.0 + 9.0, 10.0, 2.0 + 14.0 + 6.0)), tuple(F.p(13.0, 1.0, 2.0 + 14.0 + 5.0)), 26)
    c["CAM_DSVil_V6_Garden"] = (tuple(F.p(-9.0, 34.0, z + 7.0)), tuple(F.p(2.0, 6.0, z + 6.0)), 22)
    return {k: (tuple(round(v, 2) for v in a), tuple(round(v, 2) for v in b), l) for k, (a, b, l) in c.items()}


CAMS = _cams()


# ================================================================== build
LOW_BEVEL = (0.07, 0.5)            # ds_kit.MIN_BEVEL / MIN_BEVEL_SIZE durante a vila: chanfros < 0,07 e pecas finas
                                   # (< 0,5) sem chanfro (invisivel a 3+ studs; ~-25% de tris na madeira)


def build():
    old = (K.MIN_BEVEL, K.MIN_BEVEL_SIZE)
    K.MIN_BEVEL, K.MIN_BEVEL_SIZE = LOW_BEVEL
    try:
        for nm, *_ in HOUSES:
            build_house(nm)
        street_low()
        street_high()
    finally:
        K.MIN_BEVEL, K.MIN_BEVEL_SIZE = old
