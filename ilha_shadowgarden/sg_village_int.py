# sg_village_int - INTERIORES das 7 casas da vila (onda 1, agente 1e, 2026-09-30; FINESSE 3 agente I, 2026-10-05).
# Pedido do usuario: "modele as casas por dentro para deixar elas funcionais e acessiveis".
# Chamado pelo sg_village.build() depois do exterior de cada casa (o exterior devolve as janelas, a lareira/chamine e
# o telhado). Tudo em coordenadas REAIS do lote (sg_village.lot_frame: +Y = frente, porta no meio da frente), menos o
# forro do telhado e as tesouras, que usam o referencial do kit (sg_village.KitXF) para casar com a ardosia.
#
# FINESSE 3 (AUDITORIA3 03.13, 04.01-04.11):
#   - UM INTERIOR POR OFICIO (04.01): taverna (H1), ferreiro com forja (H2), boticario (H3), oficina do minerador
#     (H4), cartografo (H5), casa da guarda (H6), mestre de armas (H7); quartos do andar com layout proprio (04.07).
#   - PAREDES COM ESTRUTURA (04.02): lambril de tabuas ate 3,0 com batentes, prumos de canto, frechal sob as vigas;
#     no andar, enxaimel por dentro (soleira, montantes, maos-francesas); 2-3 objetos de leitura por parede.
#   - 3 VALORES DE MADEIRA + 2 TECIDOS (04.05): estrutura escura (Wood_SG_Dark), moveis medios (Wood_SGVilMid), piso
#     um valor abaixo dos moveis (Wood_SGVilFloor); navy e vinho (Cloth_SGVilWine); linho/cera claro (TrimLow).
#   - ORCAMENTO DE MESHPARTS: o objeto SG_Vil_Int_<casa> (escondido por distancia no cliente) so usa 5 materiais
#     (2 madeiras, navy, vinho, linho); pedra, ferro, brilho, reboco e o PISO ficam no objeto do exterior da casa
#     (SG_Vil_Houses_P*), que ja tem esses materiais: nenhuma MeshPart nova por casa (so 1 por grupo, o piso).
#   - FRESTA DE LUZ (03.13): o forro de reboco desce ate -0,30 (dentro do soco) e o leito do piso entra 0,3 no forro;
#     a luz real da casa passa a ter sombra (fm_lib desliga sombra em POINT < 500 W: era ela que vazava pela parede
#     e acendia a face de cima do filete do soco).
#   - FORRO DAS TERREAS FECHADO (04.09) com vigas mestras e tirantes; o peito da chamine sobe reto e atravessa o forro
#     numa caixa de madeira (04.06). Lareiras com toras, brasa recuada e chama em laminas (04.04); velas em gota
#     (04.11); postigos abertos na frente/direita com vidraca e folhas (04.08); tapetes e cobertas com borda (04.10).
#   - COLISAO so de moveis grandes no meio do comodo (mesa, balcao, cama, forja, estante alta, manequim); props de
#     canto, de parede e sob a escada ficam sem colisao (orcamento de colisoes da zona village).
import math, random
from mathutils import Vector
import sg_lib as SL
from sg_lib import MB, col_box, Frame, light, fm_lib
import sg_layout as L
import sg_col
import sg_village as V

# ------------------------------------------------------------------ paleta do interior (04.05)
W_STR = V.WOOD                   # estrutura: vigas, escada, lambril, caixilhos (escura, a mesma do enxaimel de fora)
W_MID = "Wood_SGVilMid"          # moveis (media, quente)
W_FLR = "Wood_SGVilFloor"        # piso de tabuas (um valor abaixo dos moveis) - vai no objeto do exterior
M_WINE = "Cloth_SGVilWine"       # estofado, coberta, cortina, tapete (vinho)
fm_lib.MATS.setdefault(W_MID, (fm_lib.S(138, 98, 62), 0.8, 0.0, 0, None, 0.08))
fm_lib.MATS.setdefault(W_FLR, (fm_lib.S(114, 80, 52), 0.85, 0.0, 0, None, 0.10))
fm_lib.MATS.setdefault(M_WINE, (fm_lib.S(104, 34, 48), 0.8, 0.0, 0, None, 0.04))
M_NAVY = V.M_CURT                # navy (tapete, postigos fechados, livros, agua)
M_LIN = V.M_CAP                  # linho / cera / papel / palha (Stone_SG_TrimLow, claro)
# so no objeto do EXTERIOR (mx()): pedra, ferro, brilho, reboco, piso
M_STONE, M_DARK, IRON, M_GLOW, M_PLAS = V.M_DRESS, V.M_JNT, "Metal_SG_Iron", V.M_ROOM, V.M_PL
WOOD = W_STR
M_CLOTH = M_NAVY
FLOOR = 0.30                 # topo do piso interno (= topo da rua e do caminho)
WALL = 1.0                   # casca 0,5 + forro 0,5 (colisao da onda 0)
B = 0.05                     # chanfro dos moveis
REAL_LIGHT = ("H1", "H2", "H5", "H7")
_X = [None]                  # objeto do exterior da casa em construcao (pedra / ferro / brilho / piso)


def mx():
    return _X[0]


# ------------------------------------------------------------------ cameras (as da AUDITORIA3 por casa + fechamentos)
def _cams():
    out = {}
    EYE = 5.5
    for nm, tp, x, y, w, d, deg, z in L.HOUSES:
        a = math.radians(deg) - math.pi / 2

        def P(u, v, h, x=x, y=y, z=z, a=a):
            return (x + u * math.cos(a) - v * math.sin(a), y + u * math.sin(a) + v * math.cos(a), z + h)
        iw, idp = w - 2.0, d - 2.0
        T = L.HOUSE_TYPES[tp]
        zf = T["h0"] + 1.0
        e = 0.3 + EYE
        k = "CAM_A3_04_%s_" % nm
        if nm in ("H1", "H7"):                       # 03.13: lateral com o soco (as da auditoria) + fechamento do pe
            out["CAM_A3_03_%s_Lado" % nm] = (P(-w / 2 - 16.0, d / 2 + 8.0, EYE), P(0.0, -2.0, 8.0), 20)
            out["CAM_SGVilInt_%s_Pe" % nm] = (P(-w / 2 - 7.0, 3.0, 3.2), P(-w / 2, 1.0, 1.4), 24)
        if tp == "B":
            out[k + "Taverna"] = (P(iw / 2 - 4.0, idp / 2 - 3.0, e), P(-iw / 2 + 2.0, 0.0, 6.0), 16)
            out[k + "Escada"] = (P(iw / 2 - 6.0, -1.0, e), P(-iw / 2 + 6.0, -idp / 2 + 3.0, 10.0), 16)
            # (a da auditoria ficava em u = iw/2 - 5, hoje DENTRO da galeria de quartos: recua 3,5 para o corredor)
            out[k + "Mezanino"] = (P(iw / 2 - 8.5, idp / 2 - 6.0, zf + e), P(-iw / 2 + 6.0, 2.0, zf - 3.0), 16)
            out[k + "Quarto"] = (P(-iw / 2 + 4.0, -idp / 2 + 9.0, zf + e), P(iw / 2 - 3.0, idp / 2 - 4.0, zf + 2.0), 16)
            out["CAM_SGVilInt_%s_Balcao" % nm] = (P(-6.0, 0.0, e), P(10.0, 9.0, 3.5), 18)
        elif tp == "A":
            out[k + "Sala"] = (P(iw / 2 - 7.0, idp / 2 - 3.0, e), P(-iw / 2, 1.0, 4.5), 16)
            out[k + "Escada"] = (P(iw / 2 - 5.0, -1.0, e), P(-iw / 2 + 5.0, -idp / 2 + 3.0, 9.0), 16)
            out[k + "Quarto"] = (P(-iw / 2 + 5.0, 2.0, zf + e), P(iw / 2 - 2.7, idp / 2 - 4.6, zf + 1.5), 16)
            out["CAM_SGVilInt_%s_Oficio" % nm] = (P(-6.0, 7.5, e), P(10.0, -2.0, 3.0), 18)
        else:
            out[k + "Sala"] = (P(iw / 2 - 3.0, idp / 2 - 2.5, e), P(-iw / 2, 1.0, 4.5), 16)
            out[k + "Oficina"] = (P(-iw / 2 + 4.0, idp / 2 - 2.5, e), P(iw / 2 - 3.0, -idp / 2 + 2.0, 3.0), 16)
            out[k + "Forro"] = (P(0.0, idp / 2 - 2.0, e), P(0.0, -3.0, T["h0"] + 6.0), 15)
    return out


CAMS = _cams()
_CAMS_MADE = [False]


def make_cams():
    """o studio so le o CAMS dos modulos de build_sg.ZONE_MODULES (sg_village): com SG_INT_CAMS=1 no ambiente, este
    modulo cria as suas cameras na cena (so no studio; o build normal nao as cria)"""
    import os
    if _CAMS_MADE[0] or not os.environ.get("SG_INT_CAMS"):
        return
    _CAMS_MADE[0] = True
    import bpy
    for n, (loc, tgt, lens) in CAMS.items():
        if n not in bpy.data.objects:
            fm_lib.camera(n, loc, tgt, lens)


# ------------------------------------------------------------------ primitivas no referencial do lote (reais)
def tb(mb, F, cx, cy, z0, sx, sy, sz, m, bevel=B, yaw=0.0):
    """caixa pela BASE (z0) no lote. Chanfro so em peca que o jogador le de perto (maior lado >= 2,5: tampos,
    balcao, bau, cabeceira); peca pequena comum sai reta (AGENT_BRIEF 7: nada de chanfro em peca pequena)"""
    if max(sx, sy, sz) < 3.2:
        bevel = 0.0
    mb.box((sx, sy, sz), F.p(cx, cy, z0 + sz / 2), F.r(0, 0, yaw), m, bevel)


def bm_(mb, F, a, b, w, h, m=WOOD):
    mb.beam(F.p(*a), F.p(*b), w, h, m, 0.0)


def rod(mb, F, a, b, r, m=IRON, n=6):
    mb.rod(F.p(*a), F.p(*b), r, m, n)


def lcol(area, F, cx, cy, z0, sx, sy, sz, yaw=0.0):
    col_box(area, (sx, sy, sz), F.p(cx, cy, z0 + sz / 2), F.r(0, 0, yaw))


def rot2(u, v, a):
    return (u * math.cos(a) - v * math.sin(a), u * math.sin(a) + v * math.cos(a))


class Sub:
    """sub-referencial dentro do lote (moveis girados): p(u, v) -> (x, y) do lote"""

    def __init__(self, cx, cy, yaw):
        self.cx, self.cy, self.a = cx, cy, yaw

    def xy(self, u, v):
        du, dv = rot2(u, v, self.a)
        return (self.cx + du, self.cy + dv)


def sbox(mb, F, S, u, v, z0, sx, sy, sz, m, bevel=B):
    x, y = S.xy(u, v)
    tb(mb, F, x, y, z0, sx, sy, sz, m, bevel, S.a)


def lathe(mb, F, x, y, z, prof, m, n=6, closed=False, caps=(True, True)):
    if max(r for r, h in prof) < 0.5:
        n = min(n, 5)                                   # louca/frasco pequeno: 5 lados bastam a 5 studs
    p = F.p(x, y, z)
    V._lathe(mb, (p.x, p.y, p.z), prof, m, n, 0.0, closed, caps)


# ------------------------------------------------------------------ chama do kit (04.04 / 04.11 / 15.06): gota <= 0,4
def flame(mb, p, h=0.36):
    k = h / 0.36
    V._lathe(mb, (p[0], p[1], p[2]), [(0.0, 0.0), (0.11 * k, 0.12 * k), (0.06 * k, 0.26 * k), (0.0, h)], M_GLOW, 5)


def flame_blades(mb, F, cx, cy, z0, h=1.3, yaw=0.0, n=2):
    """chama grande (lareira/forja): 2 linguas finas, cada uma em 3 pecas que se SOBREPOEM (sem degrau), afinam e
    torcem em torno do eixo (sem cone)"""
    for k in range(n):
        S = Sub(cx + ((k - 0.5) * 0.7 if n > 1 else 0.0), cy, yaw + k * 0.6)
        hh = h * (1.0 if k == 0 else 0.72)
        for (w, d, z, zh, tw) in ((0.84, 0.16, 0.0, 0.52, 0.0), (0.56, 0.13, 0.3, 0.5, 0.55), (0.28, 0.1, 0.6, 0.42, 1.1)):
            x, y = S.xy(0.0, 0.0)
            p = F.p(x, y, z0 + (z + zh / 2) * hh)
            mb.box((w * hh, d, zh * hh), (p.x, p.y, p.z), (0.0, 0.0, F.a + S.a + tw), M_GLOW, 0.0)


def candle(mi, F, x, y, z, s=1.0):
    """vela de cera (linho) com a chama do kit (brilho no objeto do exterior)"""
    p = F.p(x, y, z)
    mi.cyl(0.2 * s, 0.6 * s, (p.x, p.y, p.z + 0.3 * s), m=M_LIN, n=5, bevel=0.0)
    flame(mx(), (p.x, p.y, p.z + 0.6 * s), 0.36)


# ------------------------------------------------------------------ moveis (Tier B: base, corpo, remate)
def table(mb, F, cx, cy, lx, ly, h=3.4, yaw=0.0, m=W_MID):
    S = Sub(cx, cy, yaw)
    sbox(mb, F, S, 0, 0, FLOOR + h - 0.32, lx, ly, 0.32, m, 0.08)                   # tampo
    for k in ((-1, 1) if lx >= 4.0 else ()):                                       # saia (so mesa grande)
        sbox(mb, F, S, 0, k * (ly / 2 - 0.45), FLOOR + h - 0.8, lx - 1.0, 0.2, 0.48, m, 0.0)
    for ku in (-1, 1):
        for kv in (-1, 1):
            u, v = ku * (lx / 2 - 0.55), kv * (ly / 2 - 0.55)
            sbox(mb, F, S, u, v, FLOOR, 0.5, 0.5, h - 0.32, m, 0.0)                  # perna


def chair(mb, F, cx, cy, yaw, back=True, m=W_MID, pad=None):
    """cadeira: assento 1,95 do chao, 4 pernas, encosto com 2 montantes e travessa (yaw = para onde olha);
    pad = material do estofado"""
    S = Sub(cx, cy, yaw)
    zs = FLOOR + 1.95
    sbox(mb, F, S, 0, 0, zs, 1.8, 1.8, 0.22, m, 0.06)
    if pad:
        sbox(mb, F, S, 0, 0, zs + 0.22, 1.6, 1.6, 0.22, pad, 0.1)
    for ku in (-1, 1):
        for kv in (-1, 1):
            sbox(mb, F, S, ku * 0.7, kv * 0.7, FLOOR, 0.26, 0.26, 1.95, m, 0.0)
    if back:
        for ku in (-1, 1):
            sbox(mb, F, S, ku * 0.7, -0.78, zs, 0.26, 0.26, 2.3, m, 0.0)
        sbox(mb, F, S, 0, -0.8, zs + 1.5, 1.6, 0.18, 0.7, m, 0.03)


def stool(mb, F, cx, cy, m=W_MID):
    p = F.p(cx, cy, FLOOR)
    mb.cyl(0.85, 0.24, (p.x, p.y, p.z + 2.0), m=m, n=6, bevel=0.05)
    for k in range(3):
        a = 2 * math.pi * k / 3 + 0.3
        mb.beam((p.x + 0.55 * math.cos(a), p.y + 0.55 * math.sin(a), p.z + 1.9),
                (p.x + 0.8 * math.cos(a), p.y + 0.8 * math.sin(a), p.z), 0.22, 0.22, m, 0.0)


def bench(mb, F, cx, cy, ln, yaw=0.0, m=W_MID):
    S = Sub(cx, cy, yaw)
    sbox(mb, F, S, 0, 0, FLOOR + 1.8, ln, 1.3, 0.24, m, 0.06)
    for k in (-1, 1):
        sbox(mb, F, S, k * (ln / 2 - 0.7), 0, FLOOR, 0.3, 1.1, 1.8, m, 0.03)


def rug(mb, F, cx, cy, lx, ly, yaw=0.0, m=M_NAVY, border=M_WINE):
    """tapete (04.10): corpo 0,14, barra de 0,4 um pouco mais alta, faixa de desenho no meio e franja clara nas pontas
    (as pontas sao os lados v = +-ly/2)"""
    S = Sub(cx, cy, yaw)
    sbox(mb, F, S, 0, 0, FLOOR, lx - 0.8, ly - 0.8, 0.14, m, 0.0)
    for k in (-1, 1):
        sbox(mb, F, S, k * (lx / 2 - 0.2), 0, FLOOR, 0.4, ly, 0.17, border, 0.03)
        sbox(mb, F, S, 0, k * (ly / 2 - 0.2), FLOOR, lx - 0.8, 0.4, 0.17, border, 0.03)
        sbox(mb, F, S, 0, k * (ly / 2 + 0.25), FLOOR, lx - 1.2, 0.5, 0.08, M_LIN, 0.0)          # franja
    sbox(mb, F, S, 0, 0, FLOOR + 0.14, lx * 0.5, ly * 0.55, 0.03, border, 0.0)                 # faixa de desenho


def shelf(mb, F, cx, cy, yaw, wd, h, dp=1.5, items="books", z0=None, m=W_MID):
    """estante: 2 laterais, fundo, prateleiras, cornija e o que guarda (livros, potes, garrafas, frascos) arrumado
    por prateleira (sem sorteio). A frente aponta para +v do sub-referencial"""
    S = Sub(cx, cy, yaw)
    z0 = FLOOR if z0 is None else z0
    for k in (-1, 1):
        sbox(mb, F, S, k * (wd / 2 - 0.15), 0, z0, 0.3, dp, h, m, 0.0)
    sbox(mb, F, S, 0, -dp / 2 + 0.08, z0, wd - 0.3, 0.16, h, m, 0.0)
    sbox(mb, F, S, 0, 0.05, z0 + h, wd + 0.4, dp + 0.3, 0.3, m, 0.06)
    n = 3 if h < 7.5 else 4
    for i in range(n):
        zz = z0 + 0.25 + (h - 0.8) * i / (n - 1)
        sbox(mb, F, S, 0, 0.05, zz, wd - 0.3, dp - 0.1, 0.18, m, 0.0)
        if i == n - 1:
            continue
        zi = zz + 0.18
        if items == "books":
            lots = ((-0.3, 0.3, 1.5), (0.22, 0.24, 1.3)) if i % 2 == 0 else ((-0.24, 0.34, 1.35), (0.3, 0.16, 1.55))
            for j, (fu, fw, bh) in enumerate(lots):
                sbox(mb, F, S, fu * wd, -0.05, zi, fw * wd, 1.0, bh, (M_NAVY, M_WINE, M_LIN)[(j + i) % 3], 0.0)
        elif items == "none":
            continue
        else:
            k = 0
            u = -wd / 2 + 0.9
            while u < wd / 2 - 0.6:
                x, y = S.xy(u, 0.0)
                if items == "pots":
                    lathe(mb, F, x, y, zi, [(0.3, 0.0), (0.46, 0.35), (0.42, 0.8), (0.24, 1.0), (0.3, 1.12), (0.0, 1.12)],
                          M_LIN if k % 2 else M_NAVY, 6)
                elif items == "jars":                                      # frascos do boticario (2 formas, 3 tons)
                    if k % 2:
                        lathe(mb, F, x, y, zi, [(0.3, 0.0), (0.34, 0.9), (0.14, 1.1), (0.14, 1.45), (0.0, 1.45)],
                              (M_NAVY, M_WINE)[(k // 2) % 2], 5)
                    else:
                        lathe(mb, F, x, y, zi, [(0.36, 0.0), (0.4, 0.7), (0.3, 0.95), (0.34, 1.1), (0.0, 1.1)],
                              M_LIN, 6)
                else:                                                      # garrafas
                    lathe(mb, F, x, y, zi, [(0.26, 0.0), (0.28, 0.7), (0.12, 0.95), (0.1, 1.3), (0.0, 1.3)],
                          M_NAVY if k % 2 else M_WINE, 5)
                u += 1.6
                k += 1


def bed(mb, F, cx, cy, yaw, lx=5.2, ly=9.0, cover=M_NAVY, canopy=False, m=W_MID):
    """cama: cabeceira alta com remates, pe mais baixo, estrado, colchao, coberta com barra, dobra de linho e
    travesseiro. yaw = para onde o PE aponta (a cabeceira fica em v = -ly/2). canopy: 4 colunas, cimalha e cortina"""
    S = Sub(cx, cy, yaw)
    hb = 6.0
    ph = 8.2 if canopy else hb
    pf = 8.2 if canopy else 2.8
    for k in (-1, 1):
        sbox(mb, F, S, k * (lx / 2 - 0.2), -ly / 2 + 0.2, FLOOR, 0.4, 0.4, ph, m, 0.05)
        sbox(mb, F, S, k * (lx / 2 - 0.2), ly / 2 - 0.2, FLOOR, 0.4, 0.4, pf, m, 0.05)
        sbox(mb, F, S, k * (lx / 2 - 0.12), 0, FLOOR + 0.8, 0.24, ly - 0.6, 0.8, m, 0.03)
        if not canopy:
            sbox(mb, F, S, k * (lx / 2 - 0.2), -ly / 2 + 0.2, FLOOR + hb, 0.56, 0.56, 0.22, m, 0.0)   # remate
    sbox(mb, F, S, 0, -ly / 2 + 0.2, FLOOR + 2.2, lx - 0.8, 0.26, 2.6, m, 0.04)       # cabeceira
    sbox(mb, F, S, 0, ly / 2 - 0.2, FLOOR + 1.3, lx - 0.8, 0.22, 1.2, m, 0.04)        # pe
    sbox(mb, F, S, 0, 0, FLOOR + 1.3, lx - 0.5, ly - 0.7, 0.9, M_LIN, 0.12)           # colchao
    sbox(mb, F, S, 0, 0.9, FLOOR + 2.0, lx - 0.3, ly * 0.62, 0.36, cover, 0.12)       # coberta
    sbox(mb, F, S, 0, ly * 0.3 + 0.5, FLOOR + 2.0, lx - 0.2, 1.0, 0.42, M_WINE if cover == M_NAVY else M_NAVY, 0.1)  # barra
    sbox(mb, F, S, 0, -ly / 2 + 1.1, FLOOR + 2.1, lx - 1.2, 1.1, 0.5, M_LIN, 0.2)      # travesseiro
    if canopy:
        zt = FLOOR + ph
        for k in (-1, 1):
            sbox(mb, F, S, k * (lx / 2 - 0.2), 0, zt - 0.3, 0.3, ly, 0.3, m, 0.03)
            sbox(mb, F, S, 0, k * (ly / 2 - 0.2), zt - 0.3, lx, 0.3, 0.3, m, 0.03)
        sbox(mb, F, S, 0, 0, zt - 0.02, lx + 0.2, ly + 0.2, 0.14, cover, 0.0)             # pano de cima
        sbox(mb, F, S, 0, 0, zt - 0.9, lx + 0.3, ly + 0.3, 0.6, M_WINE, 0.06)              # sanefa
        sbox(mb, F, S, 0, -ly / 2 + 0.05, FLOOR + 2.3, lx - 0.2, 0.14, zt - FLOOR - 3.2, cover, 0.04)   # cortina da cabeceira
        sbox(mb, F, S, lx / 2 - 0.5, -ly / 2 + 2.0, FLOOR + 0.3, 0.6, 0.6, zt - FLOOR - 1.2, M_WINE, 0.1)   # cortina recolhida


def chest(mb, F, cx, cy, yaw, lx=3.2, ly=1.8, h=2.0, m=W_MID):
    S = Sub(cx, cy, yaw)
    sbox(mb, F, S, 0, 0, FLOOR, lx, ly, h, m, 0.06)
    sbox(mb, F, S, 0, 0, FLOOR + h, lx + 0.1, ly + 0.1, 0.35, m, 0.1)
    for u in (-lx / 2 + 0.4, lx / 2 - 0.4):
        sbox(mx(), F, S, u, 0, FLOOR + 0.1, 0.18, ly + 0.08, h + 0.3, IRON, 0.02)         # cintas de ferro
    sbox(mx(), F, S, 0, ly / 2 + 0.04, FLOOR + h - 0.6, 0.4, 0.1, 0.5, IRON, 0.02)         # fecho


def wardrobe(mb, F, cx, cy, yaw, lx=4.4, ly=2.0, h=8.0, m=W_MID):
    S = Sub(cx, cy, yaw)
    sbox(mb, F, S, 0, 0, FLOOR, lx, ly, 0.5, W_STR, 0.06)
    sbox(mb, F, S, 0, 0, FLOOR + 0.5, lx - 0.2, ly - 0.2, h - 1.0, W_STR, 0.0)
    sbox(mb, F, S, 0, 0.05, FLOOR + h - 0.5, lx + 0.4, ly + 0.3, 0.5, W_STR, 0.08)
    for k in (-1, 1):
        sbox(mb, F, S, k * lx / 4, ly / 2 - 0.02, FLOOR + 0.9, lx / 2 - 0.35, 0.14, h - 1.8, m, 0.04)  # portas
        sbox(mx(), F, S, k * 0.3, ly / 2 + 0.08, FLOOR + h * 0.45, 0.14, 0.1, 0.7, IRON, 0.02)


def barrel(mb, F, cx, cy, z0=None, r=1.1, h=2.8, lying=False, yaw=0.0, m=W_MID):
    """barril: aduelas em torno de 8 lados com bojo, 2 aros de ferro"""
    z0 = FLOOR if z0 is None else z0
    prof = [(r * 0.86, 0.0), (r, h * 0.5), (r * 0.86, h)]
    if not lying:
        p = F.p(cx, cy, z0)
        V._lathe(mb, (p.x, p.y, p.z), prof, m, 8)
        for zz in (0.1, 0.8):
            V._lathe(mx(), (p.x, p.y, p.z + h * zz), [(r * 0.9 + 0.06, 0.0), (r * 0.95 + 0.06, h * 0.08)], IRON, 8,
                     caps=(False, False))
    else:
        S = Sub(cx, cy, yaw)
        a = F.p(*S.xy(-h / 2, 0.0), z=z0 + r)
        b = F.p(*S.xy(h / 2, 0.0), z=z0 + r)
        mb.rod(a, b, r * 0.94, m, 8)
        for t in (0.18, 0.82):
            c = a + (b - a) * t
            d = (b - a).normalized() * 0.12
            mx().rod(c - d, c + d, r * 0.94 + 0.14, IRON, 8)


def crate(mb, F, cx, cy, z0=None, s=2.2, yaw=0.0, m=W_MID):
    z0 = FLOOR if z0 is None else z0
    S = Sub(cx, cy, yaw)
    sbox(mb, F, S, 0, 0, z0, s, s, s, m, 0.08)
    for zz in (z0 + 0.15, z0 + s - 0.45):                                      # 2 travessas na frente
        sbox(mb, F, S, 0, -(s / 2 + 0.03), zz, s - 0.2, 0.08, 0.3, W_STR, 0.02)


def book(mb, F, x, y, z, yaw=0.0, open_=False, m=M_WINE, s=1.0):
    """livro fechado (capa + folhas) ou aberto (2 paginas)"""
    S = Sub(x, y, yaw)
    if open_:
        sbox(mb, F, S, 0, 0, z, 1.4 * s, 2.0 * s, 0.26, m, 0.04)
        for k in (-1, 1):
            sbox(mb, F, S, k * 0.33 * s, 0, z + 0.26, 0.6 * s, 1.8 * s, 0.1, M_LIN, 0.0)
    else:
        sbox(mb, F, S, 0, 0, z, 1.0 * s, 1.4 * s, 0.34 * s, m, 0.03)
        sbox(mb, F, S, 0.06 * s, 0, z + 0.05, 0.88 * s, 1.3 * s, 0.24 * s, M_LIN, 0.0)


def tapestry(mb, F, S, u, v, z, wd, h, m=M_WINE, band=M_NAVY):
    """tapecaria pendurada numa vara: pano com barra e franja (frente para +v do sub-referencial)"""
    x0, y0 = S.xy(u - wd / 2 - 0.4, v)
    x1, y1 = S.xy(u + wd / 2 + 0.4, v)
    rod(mb, F, (x0, y0, z + h), (x1, y1, z + h), 0.1, W_STR, 5)
    sbox(mb, F, S, u, v, z, wd, 0.12, h, m, 0.0)
    sbox(mb, F, S, u, v + 0.08, z + h * 0.2, wd - 0.6, 0.06, h * 0.55, band, 0.0)
    sbox(mb, F, S, u, v + 0.09, z + h * 0.42, wd * 0.5, 0.05, h * 0.12, M_LIN, 0.0)
    sbox(mb, F, S, u, v, z - 0.45, wd, 0.1, 0.45, M_LIN, 0.0)


def framed_map(mb, F, S, u, z, wd, hh):
    """mapa emoldurado na parede (S na face da parede, +v para dentro do comodo): moldura, folha de linho, 2 manchas
    de terra navy"""
    sbox(mb, F, S, u, 0.1, z, wd, 0.2, hh, W_STR, 0.04)
    sbox(mb, F, S, u, 0.24, z + 0.25, wd - 0.5, 0.08, hh - 0.5, M_LIN, 0.0)
    sbox(mb, F, S, u - wd * 0.15, 0.3, z + hh * 0.3, wd * 0.35, 0.05, hh * 0.4, M_NAVY, 0.0)
    sbox(mb, F, S, u + wd * 0.22, 0.3, z + hh * 0.5, wd * 0.2, 0.05, hh * 0.25, M_NAVY, 0.0)


def peg_rail(mb, F, S, u, v, z, wd, capes=(M_NAVY, M_WINE)):
    """cabideiro: rua de madeira com 4 cavilhas e capas penduradas (frente para +v)"""
    sbox(mb, F, S, u, v, z, wd, 0.26, 0.5, W_STR, 0.03)
    n = 4
    for k in range(n):
        uu = u - wd / 2 + wd * (k + 0.5) / n
        x, y = S.xy(uu, v + 0.3)
        x2, y2 = S.xy(uu, v + 0.75)
        rod(mb, F, (x, y, z + 0.3), (x2, y2, z + 0.45), 0.09, W_MID, 4)
        if k < len(capes):
            sbox(mb, F, S, uu, v + 0.55, z - 5.2, 1.7, 0.5, 5.4, capes[k], 0.18)


def wall_shelf(mb, F, S, u, v, z, wd, items="pots"):
    """prateleira de parede com misulas e louca (frente para +v)"""
    sbox(mb, F, S, u, v + 0.55, z, wd, 1.1, 0.2, W_MID, 0.03)
    for k in (-1, 1):
        sbox(mb, F, S, u + k * (wd / 2 - 0.5), v + 0.3, z - 0.7, 0.3, 0.6, 0.7, W_STR, 0.0)
    nn = max(2, int(wd / 1.5))
    for k in range(nn):
        uu = u - wd / 2 + wd * (k + 0.5) / nn
        x, y = S.xy(uu, v + 0.55)
        if items == "pots":
            if k % 2:
                lathe(mb, F, x, y, z + 0.2, [(0.3, 0.0), (0.42, 0.4), (0.3, 0.8), (0.0, 0.8)], (M_NAVY, M_LIN)[k % 4 == 1], 6)
            else:
                lathe(mb, F, x, y, z + 0.2, [(0.42, 0.0), (0.46, 0.14), (0.14, 0.2), (0.0, 0.2)], M_LIN, 6)   # prato
        else:
            lathe(mb, F, x, y, z + 0.2, [(0.26, 0.0), (0.28, 0.7), (0.12, 0.95), (0.1, 1.3), (0.0, 1.3)],
                  (M_NAVY, M_WINE, M_LIN)[k % 3], 5)


def mug(mb, F, x, y, z, m=W_MID):
    lathe(mb, F, x, y, z, [(0.34, 0.0), (0.36, 0.7), (0.0, 0.7)], m, 6)


def lantern_table(mi, F, x, y, z, s=1.0):
    """lanterna de mesa: base, 4 montantes, tampa e nucleo quente (brilho no exterior)"""
    p = F.p(x, y, z)
    mi.box((0.9 * s, 0.9 * s, 0.14), (p.x, p.y, p.z + 0.07), (0, 0, F.a), W_STR, 0.02)
    for k in range(4):
        a = F.a + math.pi / 4 + k * math.pi / 2
        mi.box((0.1, 0.1, 1.1 * s), (p.x + 0.42 * s * math.cos(a), p.y + 0.42 * s * math.sin(a), p.z + 0.14 + 0.55 * s),
               (0, 0, a), W_STR, 0.0)
    V._lathe(mi, (p.x, p.y, p.z + 0.14 + 1.1 * s), [(0.62 * s, 0.0), (0.2 * s, 0.3 * s), (0.0, 0.34 * s)], W_STR, 6)
    V._lathe(mx(), (p.x, p.y, p.z + 0.2), [(0.22 * s, 0.0), (0.26 * s, 0.5 * s), (0.0, 0.8 * s)], M_GLOW, 6)


# ------------------------------------------------------------------ lareira de pedra (acesa, brilho contido)
def fireplace(mi, F, x0, y0, y1, dep, zt, nm, big=False, upper=None, pot=False):
    """peito de chamine de cantaria (no objeto do EXTERIOR: ja tem a pedra) encostado na parede 'left' (x0 = face do
    forro): fiadas de 2 alturas, BOCA em arco abatido com fundo de fuligem, lareira (brasa recuada Neon medio + chama em
    2 laminas + 3 toras + cavaletes de ferro), consolo de madeira, lajeado da lareira na frente.
    upper = (z0, z1, dx, y0, y1) peito do andar de cima ate a chamine. pot = caldeirao pendurado (taverna)."""
    ms = mx()
    xf = x0 + dep
    yc = (y0 + y1) / 2
    wd = y1 - y0
    bw = 4.2 if big else 3.2
    bh = 3.9 if big else 3.3
    hs = (2.6, 1.9)
    zz, k = 0.0, 0
    while zz < zt - 0.05:
        h = min(hs[k % 2], zt - zz)
        ins = 0.0 if k % 2 == 0 else 0.1
        za, zb = zz + 0.04, zz + h - 0.04
        if za >= bh + FLOOR - 0.05:
            tb(ms, F, x0 + (dep - ins) / 2, yc, za, dep - ins, wd - ins, zb - za, M_STONE, 0.0)
        else:
            for s0, s1 in ((y0, yc - bw / 2), (yc + bw / 2, y1)):
                tb(ms, F, x0 + (dep - ins) / 2, (s0 + s1) / 2, za, dep - ins, s1 - s0, zb - za, M_STONE, 0.0)
            if zb > bh + FLOOR:
                tb(ms, F, x0 + (dep - ins) / 2, yc, bh + FLOOR, dep - ins, bw, zb - bh - FLOOR, M_STONE, 0.0)
        zz += h
        k += 1
    # boca: fundo de fuligem, teto e arco abatido de aduelas
    tb(ms, F, x0 + 0.3, yc, FLOOR, 0.6, bw, bh, M_DARK, 0.0)
    tb(ms, F, x0 + dep / 2, yc, FLOOR + bh - 0.3, dep - 0.2, bw, 0.3, M_DARK, 0.0)
    n = 3
    for i in range(n):
        a0 = math.pi * (0.15 + 0.7 * i / n)
        a1 = math.pi * (0.15 + 0.7 * (i + 1) / n)
        am = (a0 + a1) / 2
        r = bw / 2 / math.cos(math.pi * 0.35)
        ym = yc - r * math.cos(am)
        zm = FLOOR + bh - 0.6 - r * math.sin(math.pi * 0.15) + r * math.sin(am)
        tb(ms, F, xf + 0.1, ym, zm - 0.35, 0.3, 2 * r * math.sin((a1 - a0) / 2) - 0.08, 0.7, M_STONE, 0.0)
    # consolo de madeira (prateleira) sobre misulas
    zmn = FLOOR + bh + 1.0
    tb(mi, F, xf + 0.35, yc, zmn, 1.0, wd + 0.8, 0.35, W_STR, 0.06)
    for s in (-1, 1):
        tb(mi, F, xf + 0.2, yc + s * (wd / 2 - 0.4), zmn - 0.9, 0.6, 0.4, 0.9, W_STR, 0.03)
    candle(mi, F, xf + 0.35, yc - (wd / 2 - 0.4), zmn + 0.35, 1.0)
    lathe(mi, F, xf + 0.35, yc + 0.8, zmn + 0.35, [(0.3, 0.0), (0.42, 0.4), (0.25, 0.8), (0.3, 0.9), (0.0, 0.9)], M_NAVY, 6)
    # lajeado da lareira e fogo
    tb(ms, F, xf + 1.1, yc, FLOOR, 2.2, bw + 2.4, 0.12, M_STONE, 0.04)
    tb(ms, F, x0 + dep * 0.55, yc, FLOOR, dep * 0.9, bw - 0.2, 0.2, M_DARK, 0.0)
    xfire = x0 + dep * 0.55
    for i, (dy, ang) in enumerate(((-0.5, 0.25), (0.5, -0.25), (0.0, 0.0))):
        zc = FLOOR + 0.55 + 0.3 * (i == 2)
        a = F.p(xfire - 0.8, yc + dy - math.sin(ang) * 1.2, zc)
        b = F.p(xfire + 0.6, yc + dy + math.sin(ang) * 1.2, zc)
        mi.rod(a, b, 0.28, W_STR, 5)
    # brasa: cama escura com a faixa Neon RECUADA (so a base brilha) + chama em 2 laminas
    tb(ms, F, xfire - 0.1, yc, FLOOR + 0.2, 1.3, bw * 0.6, 0.22, M_DARK, 0.03)
    tb(ms, F, xfire - 0.1, yc, FLOOR + 0.42, 1.0, bw * 0.5, 0.12, M_GLOW, 0.0)
    flame_blades(ms, F, xfire - 0.1, yc + 0.1, FLOOR + 0.86, 1.25 if big else 1.05, yaw=0.3)
    if pot:
        rod(ms, F, (xf - 0.3, yc - bw / 2 + 0.3, FLOOR + bh - 0.5), (xf - 0.3, yc + bw / 2 - 0.3, FLOOR + bh - 0.5), 0.1, IRON, 5)
        rod(ms, F, (xf - 0.3, yc, FLOOR + bh - 0.5), (xf - 0.3, yc, FLOOR + 2.3), 0.06, IRON, 4)
        lathe(ms, F, xf - 0.3, yc, FLOOR + 1.0, [(0.5, 0.0), (0.95, 0.5), (0.9, 1.15), (0.75, 1.3), (0.0, 1.3)], IRON, 8)
    if upper:
        z0u, z1u, dxu, uy0, uy1 = upper
        zz, k = z0u, 0
        while zz < z1u - 0.05:
            h = min((4.6, 3.6)[k % 2], z1u - zz)
            ins = 0.0 if k % 2 == 0 else 0.1
            tb(ms, F, x0 + (dxu - ins) / 2, (uy0 + uy1) / 2, zz + 0.04, dxu - ins, (uy1 - uy0) - ins, h - 0.08,
               M_STONE, 0.0)
            zz += h
            k += 1


def forge(mi, F, x0, y0, y1, dep, zt, upper=None):
    """FORJA do ferreiro (H2) no lugar da lareira: peito de cantaria cego, lareira ALTA de alvenaria na frente (bancada
    de 3,0 com cama de carvao e brasa recuada), coifa de ferro em 3 degraus presa ao peito com 2 montantes, fole de
    couro ao lado e cocho de tempera"""
    ms = mx()
    xf = x0 + dep
    yc = (y0 + y1) / 2
    wd = y1 - y0
    hs = (2.6, 1.9)
    zz, k = 0.0, 0
    while zz < zt - 0.05:
        h = min(hs[k % 2], zt - zz)
        ins = 0.0 if k % 2 == 0 else 0.1
        tb(ms, F, x0 + (dep - ins) / 2, yc, zz + 0.04, dep - ins, wd - ins, h - 0.08, M_STONE, 0.0)
        zz += h
        k += 1
    # lareira alta (bancada de alvenaria 3,4 x 8,4 x 3,0) com tampo escuro
    hx, hy = xf + 1.7, yc + 1.0                                     # lareira: y -1,0..5,0 (rota do QA passa a -3,5)
    tb(ms, F, hx, hy, FLOOR, 3.4, wd, 1.6, M_STONE, 0.0)
    tb(ms, F, hx, hy, FLOOR + 1.6, 3.2, wd - 0.2, 1.3, M_STONE, 0.0)
    tb(ms, F, hx, hy, FLOOR + 2.9, 3.5, wd + 0.1, 0.22, M_DARK, 0.04)
    tb(ms, F, hx - 0.1, hy, FLOOR + 3.12, 1.9, 3.2, 0.24, M_DARK, 0.08)                 # cama de carvao
    tb(ms, F, hx - 0.1, hy, FLOOR + 3.36, 1.3, 2.3, 0.12, M_GLOW, 0.0)                  # brasa recuada
    flame_blades(ms, F, hx - 0.15, hy, FLOOR + 3.44, 0.8, yaw=0.5)
    # coifa de ferro em 3 degraus (do peito para fora) + 2 montantes
    for (dx, wy, z, hh) in ((3.4, wd - 0.4, 7.2, 0.5), (2.6, wd - 1.6, 7.7, 1.3), (1.6, wd - 3.2, 9.0, 1.6)):
        tb(ms, F, xf + dx / 2, hy, FLOOR + z, dx, wy, hh, M_DARK, 0.06)
    for s in (-1, 1):
        rod(ms, F, (xf + 3.1, hy + s * (wd / 2 - 0.6), FLOOR + 2.9), (xf + 3.1, hy + s * (wd / 2 - 0.6), FLOOR + 7.3), 0.14, IRON, 6)
    # fole: 2 tabuas (a de cima inclinada), bico de ferro para a lareira, cabo
    S = Sub(xf + 1.6, y1 + 3.2, 0.0)
    sbox(mi, F, S, 0, 0, FLOOR + 1.9, 3.4, 1.9, 0.3, W_MID, 0.04)
    sbox(mi, F, S, 0, 0, FLOOR + 2.2, 3.0, 1.6, 0.9, M_WINE, 0.3)                       # couro
    p = F.p(*S.xy(0.3, 0.0), z=FLOOR + 3.1)
    mi.box((3.4, 1.9, 0.26), (p.x, p.y, p.z + 0.2), (0.0, -0.18, F.a), W_MID, 0.04)
    rod(ms, F, S.xy(-1.0, -0.9) + (FLOOR + 2.3,), S.xy(-1.0, -2.4) + (FLOOR + 2.9,), 0.1, IRON, 5)
    rod(mi, F, S.xy(1.8, 0.0) + (FLOOR + 3.2,), S.xy(4.2, 0.0) + (FLOOR + 4.3,), 0.12, W_MID, 5)
    for k in (-1, 1):
        sbox(mi, F, S, k * 1.3, 0, FLOOR, 0.4, 1.3, 1.9, W_STR, 0.0)
    # cocho de tempera (agua navy) na frente da lareira, lado da sala
    S2 = Sub(xf + 5.2, y1 + 4.6, 0.0)
    sbox(mi, F, S2, 0, 0, FLOOR, 4.0, 1.7, 1.8, W_MID, 0.04)
    sbox(mi, F, S2, 0, 0, FLOOR + 1.8, 4.2, 1.9, 0.18, W_STR, 0.03)
    sbox(mi, F, S2, 0, 0, FLOOR + 1.55, 3.4, 1.2, 0.25, M_NAVY, 0.0)
    if upper:
        z0u, z1u, dxu, uy0, uy1 = upper
        zz, k = z0u, 0
        while zz < z1u - 0.05:
            h = min((4.6, 3.6)[k % 2], z1u - zz)
            ins = 0.0 if k % 2 == 0 else 0.1
            tb(ms, F, x0 + (dxu - ins) / 2, (uy0 + uy1) / 2, zz + 0.04, dxu - ins, (uy1 - uy0) - ins, h - 0.08,
               M_STONE, 0.0)
            zz += h
            k += 1


# ------------------------------------------------------------------ escada de madeira + guarda-corpo
def stair_wood(mb, F, xs, yb, sw, n, rise, tread, open_side=1):
    """escada reta de madeira que sobe em +X a partir de (xs, yb): degraus (pisada com focinho + espelho), banzo
    fechado do lado aberto (com o fechamento de tabuas embaixo), banzo de parede, CORRIMAO sobre balaustres (1 por
    2 degraus) e pilares de arranque/chegada torneados"""
    ys = yb + open_side * sw / 2                      # lado aberto
    yw = yb - open_side * sw / 2                      # lado da parede
    for i in range(n):
        zt = rise * (i + 1)
        x0 = xs + tread * i
        tb(mb, F, x0 + tread / 2 + 0.05, yb, zt - 0.18, tread + 0.12, sw - 0.1, 0.18, W_STR, 0.0)    # pisada
    zt_ = rise * n
    xe = xs + tread * n
    k = rise / tread
    for yy, th in ((ys - open_side * 0.2, 0.4), (yw + open_side * 0.12, 0.24)):
        a = (xs - 0.3, yy, rise * 0.5 - 0.9)
        b = (xe, yy, zt_ - 0.9)
        bm_(mb, F, a, b, th, 1.5)
    npan = int(min(xe - xs - 2.0, 5.0) / 1.6)
    for j in range(npan):
        xa = xs + 1.2 + 1.6 * j
        xb = xa + 1.5
        zt_a = rise * 0.5 + (xa - xs) * k - 1.7
        if zt_a < 0.8:
            continue
        tb(mb, F, (xa + xb) / 2, ys - open_side * 0.2, FLOOR, 1.5, 0.14, zt_a - FLOOR, W_MID, 0.02)
    rh = 3.0
    for i in range(1, n, 3):
        x = xs + tread * i + 0.4
        if x > xe - 0.4:
            break
        zb = rise * (i + 1)
        tb(mb, F, x, ys - open_side * 0.3, zb, 0.24, 0.24, rh - 0.1, W_STR, 0.0)
    a = (xs - 0.2, ys - open_side * 0.3, rise + rh)
    b = (xe, ys - open_side * 0.3, zt_ + rh)
    bm_(mb, F, a, b, 0.36, 0.3)
    for (x, zb, hh) in ((xs - 0.3, 0.0, rise + rh + 0.4), (xe + 0.3, zt_, rh + 0.4)):
        tb(mb, F, x, ys - open_side * 0.3, FLOOR if zb == 0 else zb, 0.62, 0.62, hh, W_STR, 0.06)
        V._lathe(mb, tuple(F.p(x, ys - open_side * 0.3, (FLOOR if zb == 0 else zb) + hh)),
                 [(0.36, 0.0), (0.2, 0.2), (0.28, 0.42), (0.0, 0.72)], W_STR, 4, math.pi / 4)


def rail(mb, F, a, b, z, h=3.2, step=4.0, posts=True):
    """guarda-corpo de madeira: rodape, corrimao e balaustres; pilares nas pontas"""
    ax, ay = a
    bx, by = b
    ln = math.hypot(bx - ax, by - ay)
    if ln < 0.5:
        return
    ux, uy = (bx - ax) / ln, (by - ay) / ln
    bm_(mb, F, (ax, ay, z + h), (bx, by, z + h), 0.4, 0.3)
    nn = max(1, int(ln / step))
    for j in range(1, nn):
        x, y = ax + ux * ln * j / nn, ay + uy * ln * j / nn
        tb(mb, F, x, y, z + 0.36, 0.22, 0.22, h - 0.5, W_STR, 0.0)
    if posts:
        for (x, y) in (a, b):
            tb(mb, F, x, y, z, 0.56, 0.56, h + 0.35, W_STR, 0.05)


# ------------------------------------------------------------------ forro de parede, janelas por dentro, porta
def wall_faces(F, w, d):
    return {"front": V.Face(F, (0.0, d / 2), (1.0, 0.0), w), "back": V.Face(F, (0.0, -d / 2), (-1.0, 0.0), w),
            "right": V.Face(F, (w / 2, 0.0), (0.0, -1.0), d), "left": V.Face(F, (-w / 2, 0.0), (0.0, 1.0), d)}


def s_on(wall, c):
    return {"front": c, "back": -c, "right": -c, "left": c}[wall]


def _cut(spans, gaps):
    out = list(spans)
    for g0, g1 in gaps:
        nc = []
        for a, b in out:
            if g1 <= a or g0 >= b:
                nc.append((a, b))
                continue
            if g0 > a + 0.05:
                nc.append((a, g0))
            if b > g1 + 0.05:
                nc.append((g1, b))
        out = nc
    return out


def band(mb, f, off0, off1, z0, z1, m, lim, gaps=(), bevel=0.0):
    """faixa na face f entre -lim..lim (dentro do forro) menos as lacunas"""
    for a, b in _cut([(-lim, lim)], gaps):
        if b - a > 0.2:
            f.box(mb, (a + b) / 2, (off0 + off1) / 2, (z0 + z1) / 2, b - a, off1 - off0, z1 - z0, m, bevel=bevel)


def linings(mbx, mi, F, hrec, info, levels, two, stair_xe=None):
    """forro de reboco (0,5) dos 4 lados em cada andar, com os vaos da porta e das janelas, desce ate -0,30 (03.13);
    ESTRUTURA por dentro (04.02): terreo = lambril de tabuas ate 3,0 com batentes e cimalha, prumos de canto e
    frechal sob as vigas; andar = soleira, montantes nos vaos e no meio dos panos, maos-francesas nos cantos;
    janelas (04.08): frente e direita com os postigos ABERTOS (folhas encostadas na parede, vidraca navy e caixilho
    com cruzeta), fundo e esquerda fechados; a bandeira da loja fechada"""
    nm, tp, x, y, w, d, deg, z = hrec
    fs = wall_faces(F, w, d)
    dw2 = (V.DW / 2 + 0.1) * V.K
    dh = (V.DH + 0.1) * V.K
    hy0, hy1 = info["hearth"]
    up = info.get("upper")
    for li, (z0, z1) in enumerate(levels):
        for wall, f in fs.items():
            side = wall in ("right", "left")
            lim = (d / 2 - WALL) if side else (w / 2 - WALL)
            s0, s1 = (-lim, lim) if side else (-(w / 2 - 0.5), w / 2 - 0.5)
            holes = []
            if li == 0 and wall == "front":
                holes.append((-dw2, dw2, -1.0, dh))
            wins = [wd for wd in info["windows"] if wd["wall"] == wall and wd["story"] == li]
            zlo = z0 - 0.6 if li == 0 else z0 - 0.1
            V.slab_holes(mbx, f, s0, s1, zlo, z1, -WALL, -0.5, holes, M_PLAS)
            # lacunas da estrutura baixa: porta, lareira (esquerda), escada (fundo do terreo)
            gaps = [(-dw2 - 0.6, dw2 + 0.6)] if (li == 0 and wall == "front") else []
            if wall == "left":
                if li == 0:
                    gaps.append((hy0 - 0.4, hy1 + 0.4))
                elif up:
                    gaps.append((up[3] - 0.3, up[4] + 0.3))
            if li == 0 and wall == "back" and two and stair_xe is not None:
                gaps.append((-1e9, 1e9))
            wgaps = [(s_on(wall, wd["c"]) - wd["w"] / 2 - 0.5, s_on(wall, wd["c"]) + wd["w"] / 2 + 0.5) for wd in wins]
            if li == 0:
                # lambril ate 3,0 (chega acima do piso: nada rente), cimalha e batentes a cada ~4,4
                band(mi, f, -WALL - 0.18, -WALL + 0.02, z0 - 0.1, z0 + 3.0, W_STR, lim, gaps)
                band(mi, f, -WALL - 0.34, -WALL, z0 + 3.0, z0 + 3.3, W_STR, lim, gaps)
                nb = 1 if side else min(3, max(1, int((2 * lim - 1.0) / 7.0)))     # batentes so nas paredes longas
                for k in range(1, nb):
                    s = -lim + 0.5 + (2 * lim - 1.0) * k / nb
                    if any(g0 < s < g1 for g0, g1 in gaps) or abs(s) > lim - 0.4:
                        continue
                    f.box(mi, s, -WALL - 0.26, z0 + 1.45, 0.32, 0.16, 3.0, W_STR)
                # frechal sob as vigas do teto (segura o vigamento) / sob o forro das terreas
                if not two:
                    band(mi, f, -WALL - 0.34, -WALL, z1 - 2.2, z1 - 1.9, W_STR, lim, [])
            else:
                # enxaimel por dentro: soleira, frechal, montantes (nos vaos e no meio dos panos), maos-francesas
                band(mi, f, -WALL - 0.26, -WALL, z0 - 0.05, z0 + 0.5, W_STR, lim, gaps)
                band(mi, f, -WALL - 0.26, -WALL, z1 - 0.5, z1, W_STR, lim, [])
                posts = []
                for wd in wins:
                    s = s_on(wall, wd["c"])
                    if wall == "front":
                        posts += [s - wd["w"] / 2 - 0.5, s + wd["w"] / 2 + 0.5]
                edges = sorted([-lim + 0.5, lim - 0.5] + posts +
                               [s_on(wall, wd["c"]) + k * (wd["w"] / 2 + 0.5) for wd in wins for k in (-1, 1)])
                for a, b in zip(edges, edges[1:]):
                    mid = (a + b) / 2
                    if b - a > 9.0 and not any(g0 < mid < g1 for g0, g1 in wgaps + gaps):
                        posts.append(mid)
                for s in posts:
                    if abs(s) > lim - 0.7 or any(g0 < s < g1 for g0, g1 in gaps):
                        continue
                    f.box(mi, s, -WALL - 0.14, (z0 + z1) / 2 + 0.05, 0.4, 0.28, z1 - z0 - 0.9, W_STR)
                for k in ((-1,) if side else (1,)):
                    sa, sb = k * (lim - 0.6), k * (lim - 3.6)
                    if any(g0 < min(sa, sb) + 0.3 and g1 > max(sa, sb) - 0.3 for g0, g1 in wgaps + gaps):
                        continue
                    f.beam(mi, sa, z1 - 4.0, sb, z1 - 0.7, -WALL - 0.14, 0.3, 0.26, W_STR)
            for wi, wd in enumerate(wins):
                s = s_on(wall, wd["c"])
                ww, za, zb = wd["w"], wd["z0"], wd["z1"]
                zc = (za + zb) / 2
                h = zb - za
                f.box(mi, s, -WALL - 0.3, za - 0.1, ww + 0.9, 0.6, 0.2, W_STR)                  # peitoril
                shop = wd.get("kind") == "shop"
                open_ = wall in ("front", "right") and not shop
                if not open_:
                    f.box(mi, s, -WALL - 0.06, zc, ww, 0.12, h, M_NAVY)                          # postigos fechados
                    continue
                f.box(mi, s, -WALL - 0.05, zc, ww, 0.1, h, M_NAVY)                               # vidraca (noite)
                for k in (-1, 1):                                                                 # folhas abertas
                    f.box(mi, s + k * (ww * 0.75 + 0.14), -WALL - 0.08, zc, ww / 2, 0.14, h - 0.1, W_STR)
        # prumos de canto (so no andar de enxaimel: no terreo o lambril e a cimalha fecham o canto)
        for kx in ((-1, 1) if li > 0 else ()):
            for ky in (-1, 1):
                tb(mi, F, kx * (w / 2 - WALL - 0.25), ky * (d / 2 - WALL - 0.25), z0 - 0.05, 0.5, 0.5, z1 - z0 + 0.05,
                   W_STR, 0.0)
    # porta por dentro: guarnicao e as 2 FOLHAS abertas, encostadas na parede (165 graus)
    f = fs["front"]
    gw = 0.5
    for k in (-1, 1):
        f.box(mi, k * (dw2 + gw / 2), -WALL - 0.1, (FLOOR + dh) / 2, gw, 0.2, dh - FLOOR + gw, W_STR)
    f.box(mi, 0.0, -WALL - 0.1, dh + gw / 2, 2 * dw2 + 2 * gw, 0.2, gw, W_STR)
    th = math.radians(165.0)
    lw = V.DW / 2 * V.K - 0.1
    lh = V.DH * V.K - 0.2
    for k in (-1, 1):
        hx, hy = k * (dw2 - 0.12), d / 2 - WALL - 0.2
        ux, uy = (-k * math.cos(th), -math.sin(th))
        yaw = math.atan2(uy, ux)
        S = Sub(hx, hy, yaw)
        sbox(mi, F, S, lw / 2, 0.0, FLOOR + 0.06, lw, 0.34, lh, W_STR, 0.0)
        for zz in (1.1, lh - 1.4):
            sbox(mi, F, S, lw / 2, -0.24, FLOOR + zz, lw - 0.4, 0.14, 0.5, W_STR, 0.02)
            sbox(mx(), F, S, lw * 0.35, 0.22, FLOOR + zz + 0.1, lw * 0.7, 0.08, 0.26, IRON, 0.0)
        x_, y_ = S.xy(lw - 0.6, 0.3)
        p = F.p(x_, y_, FLOOR + lh * 0.46)
        mx().box((0.14, 0.14, 0.7), (p.x, p.y, p.z), (0, 0, S.a + F.a), IRON, 0.0)


def floor_boards(ms, F, x0, x1, y0, y1, zt, m=W_FLR, pw=4.4, holes=(), lap=0.3):
    """piso de tabuas (junta de 0,08 sobre o leito escuro 0,18 abaixo do topo) entre x0..x1, y0..y1; holes = retangulos
    (x0, y0, x1, y1) sem piso (vao da escada, vazio do mezanino). lap = quanto o leito entra no forro (03.13).
    Vai no objeto do EXTERIOR (material do piso: 1 MeshPart por grupo de casas, nao por casa)."""
    for (a0, a1, b0, b1) in _free_rects(x0, x1, y0, y1, holes):
        ex0 = lap if abs(a0 - x0) < 1e-3 else 0.0
        ex1 = lap if abs(a1 - x1) < 1e-3 else 0.0
        ey0 = lap if abs(b0 - y0) < 1e-3 else 0.0
        ey1 = lap if abs(b1 - y1) < 1e-3 else 0.0
        tb(ms, F, (a0 - ex0 + a1 + ex1) / 2, (b0 - ey0 + b1 + ey1) / 2, zt - 0.3, a1 - a0 + ex0 + ex1,
           b1 - b0 + ey0 + ey1, 0.12, M_DARK, 0.0)
        n = max(1, int(round((b1 - b0) / pw)))
        for j in range(n):
            c0 = b0 + (b1 - b0) * j / n + 0.04
            c1 = b0 + (b1 - b0) * (j + 1) / n - 0.04
            sp = a0 + (a1 - a0) * (0.38 if j % 3 == 1 else 0.64)
            for (e0, e1) in (((a0, sp - 0.04), (sp + 0.04, a1)) if j % 3 else ((a0, a1),)):
                if e1 - e0 > 0.3:
                    tb(ms, F, (e0 + e1) / 2, (c0 + c1) / 2, zt - 0.18, e1 - e0, c1 - c0, 0.18, m, 0.0)


def flag_floor(ms, F, x0, x1, y0, y1, zt, sz=4.4, lap=0.3):
    """lajeado da taverna: lajes de ~3 em fiadas desencontradas, 2 tons de pedra (junta de 0,1 sobre o leito)"""
    tb(ms, F, (x0 + x1) / 2, (y0 + y1) / 2, zt - 0.4, x1 - x0 + 2 * lap, y1 - y0 + 2 * lap, 0.12, M_DARK, 0.0)
    ny = max(1, int(round((y1 - y0) / sz)))
    for j in range(ny):
        c0 = y0 + (y1 - y0) * j / ny + 0.05
        c1 = y0 + (y1 - y0) * (j + 1) / ny - 0.05
        off = (sz / 2) * (j % 2)
        xs = [x0] + [x0 + off + sz * i for i in range(1, 40) if x0 + off + sz * i < x1 - 0.8] + [x1]
        for i, (e0, e1) in enumerate(zip(xs, xs[1:])):
            tb(ms, F, (e0 + e1) / 2, (c0 + c1) / 2, zt - 0.28, e1 - e0 - 0.1, c1 - c0, 0.28,
               M_STONE if (i + j) % 3 else M_LIN, 0.0)


def ceiling(ms, mi, F, iw, idp, zc, holes, joist_step=5.0):
    """teto do terreo = laje do andar: forro de tabuas (face de baixo em zc), leito e piso de tabuas (topo zc + 1);
    vigas aparentes de 0,7 x 1,0 (param no vao da escada/vazio) e vigas de borda no vao"""
    x0, x1, y0, y1 = -iw / 2, iw / 2, -idp / 2, idp / 2
    floor_boards(ms, F, x0, x1, y0, y1, zc + 1.0, holes=holes)
    for (a0, a1, b0, b1) in _free_rects(x0, x1, y0, y1, holes):
        tb(mi, F, (a0 + a1) / 2, (b0 + b1) / 2, zc, a1 - a0, b1 - b0, 0.12, W_STR, 0.0)
    xs = [x0 + joist_step * (k + 0.5) for k in range(int(iw / joist_step))]
    for xj in xs:
        segs = [(y0, y1)]
        for hx0, hy0, hx1, hy1 in holes:
            if hx0 - 0.4 < xj < hx1 + 0.4:
                nsg = []
                for a, b in segs:
                    if hy1 <= a or hy0 >= b:
                        nsg.append((a, b))
                        continue
                    if hy0 > a:
                        nsg.append((a, hy0))
                    if hy1 < b:
                        nsg.append((hy1, b))
                segs = nsg
        for a, b in segs:
            if b - a > 1.0:
                tb(mi, F, xj, (a + b) / 2, zc - 1.0, 0.7, b - a, 1.0, W_STR, 0.0)
    for hx0, hy0, hx1, hy1 in holes:
        for yy in (hy0, hy1):
            if y0 + 0.5 < yy < y1 - 0.5:
                tb(mi, F, (hx0 + hx1) / 2, yy + (0.35 if yy == hy1 else -0.35), zc - 1.0, hx1 - hx0, 0.7, 1.12, W_STR,
                   0.0)


def ceiling_flat(mi, F, iw, idp, zc, breast):
    """forro FECHADO das casas terreas (04.09): tabuado em zc, viga mestra ao longo de x (apoiada no peito da chamine
    e numa misula na parede oposta), 3 tirantes de 0,8 x 1,0 ao longo de y; o peito atravessa o forro numa caixa de
    madeira com rufo (04.06). breast = (x0, x1, y0, y1) do peito"""
    bx0, bx1, by0, by1 = breast
    tb(mi, F, 0.0, 0.0, zc, iw + 0.6, idp + 0.6, 0.14, W_STR, 0.0)
    tb(mi, F, (bx1 + iw / 2) / 2, (by0 + by1) / 2, zc - 1.9, iw / 2 - bx1, 0.7, 1.9, W_STR, 0.04)       # viga mestra
    tb(mi, F, iw / 2 - 0.5, (by0 + by1) / 2, zc - 2.9, 1.0, 0.9, 1.0, W_STR, 0.03)                       # misula
    for xt in (-iw / 4 - 0.5, 0.0, iw / 4 + 0.5):
        tb(mi, F, xt, 0.0, zc - 1.0, 0.8, idp + 0.4, 1.0, W_STR, 0.04)                                   # tirantes
    # caixa de madeira (rufo) do peito no forro: 3 lados (o 4o e a parede)
    tb(mi, F, bx1 + 0.15, (by0 + by1) / 2, zc - 0.5, 0.3, by1 - by0 + 0.6, 0.6, W_STR, 0.03)
    for yy in (by0 - 0.15, by1 + 0.15):
        tb(mi, F, (bx0 + bx1) / 2, yy, zc - 0.5, bx1 - bx0, 0.3, 0.6, W_STR, 0.03)


def _free_rects(x0, x1, y0, y1, holes):
    rects = [(x0, x1, y0, y1)]
    for hx0, hy0, hx1, hy1 in holes:
        out = []
        for (p0, p1, q0, q1) in rects:
            if hx1 <= p0 or hx0 >= p1 or hy1 <= q0 or hy0 >= q1:
                out.append((p0, p1, q0, q1))
                continue
            if hx0 > p0:
                out.append((p0, hx0, q0, q1))
            if hx1 < p1:
                out.append((hx1, p1, q0, q1))
            m0, m1 = max(p0, hx0), min(p1, hx1)
            if hy0 > q0:
                out.append((m0, m1, q0, hy0))
            if hy1 < q1:
                out.append((m0, m1, hy1, q1))
        rects = out
    return rects


# ------------------------------------------------------------------ telhado por dentro (referencial do kit)
def roof_inside(mbx, mi, F, info):
    """forro inclinado de tabuas (0,6 abaixo da ardosia), meia-parede de reboco (joelho) do frechal ate o forro nas
    paredes do beiral, frechal de madeira e TESOURAS (linha, pendural, pernas e escoras). Tudo no referencial do kit."""
    G = info["G"]
    ze, R, hd, cy = info["ze"], info["R"], info["hd"], info["cy"]
    bx0, bx1, by0, by1 = info["body0"]
    t = math.atan2(R, hd)
    tn = math.tan(t)
    lx0, lx1 = bx0 + 0.5, bx1 - 0.5
    ly0, ly1 = by0 + 0.5, by1 - 0.5

    def zu(yy):
        return ze + R - abs(yy - cy) * tn
    gap = 0.3
    info["zboard"] = lambda gy: (zu(gy) - gap - 0.12) * V.K
    with V.KitXF([mbx, mi], F):
        for s, yw in ((1, ly1), (-1, ly0)):
            zk = zu(yw) - gap - 0.12
            if zk > ze + 0.05:
                mbx.box((lx1 - lx0, 0.25, zk - ze + 0.1), G.p((lx0 + lx1) / 2, yw + s * 0.125, (ze + zk) / 2 + 0.05),
                        G.r(), M_PLAS, 0.0)
            mi.box((lx1 - lx0, 0.3, 0.32), G.p((lx0 + lx1) / 2, yw - s * 0.15, zk - 0.16), G.r(), W_STR, 0.02)
            ya, yb_ = yw, cy
            za, zb_ = zu(ya) - gap, zu(yb_) - gap
            ln = math.hypot(yb_ - ya, zb_ - za)
            ang = math.atan2(zb_ - za, abs(yb_ - ya))
            mid = G.p((lx0 + lx1) / 2, (ya + yb_) / 2, (za + zb_) / 2 - 0.06 / math.cos(ang))
            mi.box((lx1 - lx0, ln, 0.12), mid, G.r(-s * ang, 0, 0), W_STR, 0.0)
        mi.box((lx1 - lx0, 0.5, 0.6), G.p((lx0 + lx1) / 2, cy, zu(cy) - gap - 0.4), G.r(), W_STR, 0.03)
        nt = max(2, int((lx1 - lx0) / 5.0))
        dxs = [xd for sd_, xd in info.get("dormers", [])]
        for j in range(nt):
            xt = lx0 + (lx1 - lx0) * (j + 0.5) / nt
            for xd in dxs:
                if abs(xt - xd) < 2.2:
                    xt = xd + (2.3 if xt >= xd else -2.3)
            zt_ = max(ze + 0.5, min(zu(ly0), zu(ly1)) - gap - 0.5)
            info.setdefault("trusses", []).append((xt, zt_ - 0.225))
            mi.box((0.4, ly1 - ly0, 0.45), G.p(xt, (ly0 + ly1) / 2, zt_), G.r(), W_STR, 0.03)
            ztop = zu(cy) - gap - 0.35
            mi.box((0.4, 0.4, ztop - zt_), G.p(xt, cy, (zt_ + ztop) / 2), G.r(), W_STR, 0.03)
            for s, yw in ((1, ly1), (-1, ly0)):
                a = G.p(xt, yw - s * 0.2, zt_ + 0.1)
                b = G.p(xt, cy + s * 0.25, ztop - 0.1)
                mi.beam(a, b, 0.36, 0.42, W_STR, 0.0)


# ------------------------------------------------------------------ luzes e colisao
def house_light(nm, F, fx, fy, z, prev_name=None, energy=260.0):
    p = F.p(fx, fy, z)
    if prev_name is None:
        ob = light("L_SGVil_House_%s" % nm, "POINT", (p.x, p.y, p.z), energy, (1.0, 0.66, 0.36), 0.5)
        try:
            ob.data.use_shadow = True        # 03.13: sem sombra a luz atravessava a parede e acendia o soco por fora
        except Exception:
            pass
    else:
        ob = light(prev_name, "AREA", (p.x, p.y, p.z), energy, (1.0, 0.7, 0.42), 1.0)
        try:
            ob.data.size = 6.0
        except Exception:
            pass
    return (p.x, p.y, p.z)


def collisions(area, F, hrec, T, eave):
    """a colisao da onda 0 (sg_blockout.house) com o piso interno a 0,30 e o soco: paredes de 1 com o vao da porta
    8 x 11, forro (segura a camera)"""
    nm, tp, x, y, w, d, deg, z = hrec
    t = WALL
    dw, dh = L.HOUSE_DOOR
    for sx, sy, lx, ly in ((0, -d / 2 + t / 2, w, t), (-w / 2 + t / 2, 0, t, d), (w / 2 - t / 2, 0, t, d)):
        col_box(area, (lx, ly, eave + 0.5), F.p(sx, sy, eave / 2 - 0.25), F.r())
    for s in (-1, 1):
        seg = (w - dw) / 2
        col_box(area, (seg, t, eave + 0.5), F.p(s * (dw / 2 + seg / 2), d / 2 - t / 2, eave / 2 - 0.25), F.r())
    col_box(area, (dw, t, eave - dh), F.p(0, d / 2 - t / 2, dh + (eave - dh) / 2), F.r())
    col_box(area + "Roof", (w, d, 1.0), F.p(0, 0, eave + 0.5), F.r())
    col_box(area, (w - 2 * t, d - 2 * t, 1.0), F.p(0, 0, FLOOR - 0.5), F.r())            # piso interno
    so = 0.84
    for sx, sy, lx, ly in ((0, -d / 2 - so / 2, w + 2 * so, so), (-w / 2 - so / 2, 0, so, d), (w / 2 + so / 2, 0, so, d)):
        col_box(area + "Socle", (lx, ly, 2.0), F.p(sx, sy, 1.0), F.r())
    for s in (-1, 1):
        seg = (w + 2 * so - dw - 1.2) / 2
        col_box(area + "Socle", (seg, so, 2.0), F.p(s * (dw / 2 + 0.6 + seg / 2), d / 2 + so / 2, 1.0), F.r())


# ------------------------------------------------------------------ interior por tipo
def interior(mbx, hrec, spec, info):
    nm, tp, x, y, w, d, deg, z = hrec
    T = L.HOUSE_TYPES[tp]
    F = V.lot_frame(hrec)
    rng = random.Random(4300 + int(nm[1:]))
    mi = MB("SG_Vil_Int_%s" % nm, V.COLL, rng, detail="near")
    _X[0] = mbx
    make_cams()
    area = "SG_VilHouse%s" % nm
    iw, idp = w - 2 * WALL, d - 2 * WALL
    two = T["floors"] == 2
    h0 = T["h0"]
    zf = h0 + 1.0
    eave = info["ze"] * V.K
    big = tp == "B"
    dep = 3.3
    hy0, hy1 = (-2.0, 8.0) if big else (-2.0, 4.0)
    xl = -iw / 2
    info["hearth"] = (hy0, hy1)
    ch = info["chimneys"][0] if info.get("chimneys") else None
    upper = None
    zch = ch[4] if ch else eave
    if two and ch:
        cu, cv, cwx, cdp, _ = ch
        upper = (zf, zch + 0.4, max(1.2, (cu + cwx / 2) - xl + 0.1), cv - cdp / 2 - 0.1, cv + cdp / 2 + 0.1)
    info["upper"] = upper
    zc_flat = eave - 2.0                                   # forro fechado das terreas (face de baixo)
    levels = [(FLOOR, h0 if two else eave)] + ([(zf, eave)] if two else [])
    # escada: cotas (a colisao e a rota do QA dependem delas)
    rise = h0 + 1.0
    n = int(math.ceil(rise / 0.83))
    tread, sw = 1.6, 6.0
    xs = -iw / 2 + 2.0
    yb = -idp / 2 + sw / 2
    xe = xs + n * tread
    linings(mbx, mi, F, hrec, info, levels, two, stair_xe=(xe if two else None))
    # piso do terreo (no objeto do exterior: material do piso compartilhado pelo grupo)
    if tp == "B":
        flag_floor(mbx, F, -iw / 2, iw / 2, -idp / 2, idp / 2, FLOOR)
    else:
        floor_boards(mbx, F, -iw / 2, iw / 2, -idp / 2, idp / 2, FLOOR)
    # lareira / forja (+ peito do andar de cima ate a base da chamine)
    zt_breast = (h0 + 0.46) if two else (zc_flat + 0.9)
    if nm == "H2":
        forge(mi, F, xl, hy0, hy1, dep, zt_breast, upper=upper)
        lcol(area, F, xl + dep / 2 + 1.7, (hy0 + hy1) / 2 + 1.0, 0.0, dep + 3.4, hy1 - hy0, 3.2)
        lcol(area, F, xl + dep / 2, (hy0 + hy1) / 2, 0.0, dep, hy1 - hy0, h0)
    else:
        fireplace(mi, F, xl, hy0, hy1, dep, zt_breast, nm, big=big, upper=upper, pot=(tp == "B"))
        lcol(area, F, xl + dep / 2, (hy0 + hy1) / 2, 0.0, dep, hy1 - hy0, (h0 if two else zch))
    if upper:
        lcol(area, F, xl + upper[2] / 2, (upper[3] + upper[4]) / 2, zf, upper[2], upper[4] - upper[3], zch - zf)
    fx_light = (xl + dep + 4.5, (hy0 + hy1) / 2, FLOOR + 5.0)
    if nm in REAL_LIGHT:
        house_light(nm, F, *fx_light)
    else:
        house_light(nm, F, 0.0, 0.0, (h0 if two else zc_flat) - 1.5, prev_name="PREVIEW_L_SGVil_%s_T" % nm, energy=900.0)
    if two:
        house_light(nm, F, 2.0, 3.0, eave - 1.0, prev_name="PREVIEW_L_SGVil_%s_A" % nm, energy=900.0)
    holes = []
    if two:
        stair_wood(mi, F, xs, yb, sw, n, rise / n, tread, open_side=1)
        sg_col.stair_col(area + "Stair", F.p(xs, yb, 0.0), F.a, sw, n, rise / n, tread, guards=False)
        holes = [(-iw / 2, -idp / 2, xe, -idp / 2 + sw)]
        void = spec.get("void")
        if void:
            holes.append(void)
        for (a0, a1, b0, b1) in _free_rects(-iw / 2, iw / 2, -idp / 2, idp / 2, holes):
            if a1 - a0 > 0.3 and b1 - b0 > 0.3:
                lcol(area + "Floor", F, (a0 + a1) / 2, (b0 + b1) / 2, zf - 1.0, a1 - a0, b1 - b0, 1.0)
        ceiling(mbx, mi, F, iw, idp, h0, holes)
        gy = -idp / 2 + sw + 0.3
        gx0, gx1 = -iw / 2, xe - 1.0
        lcol(area + "Guard", F, (gx0 + gx1) / 2, gy, zf, gx1 - gx0, 0.6, 3.6)
        rail(mi, F, (gx0 + 0.3, gy), (gx1, gy), zf, 3.2)
        if void:
            vx0, vy0, vx1, vy1 = void
            for a, b in (((vx0, vy0), (vx1, vy0)), ((vx1, vy0), (vx1, vy1)), ((vx1, vy1), (vx0, vy1)),
                         ((vx0, vy1), (vx0, vy0))):
                ax, ay = a[0] + (0.3 if a[0] == vx0 else -0.3), a[1] + (0.3 if a[1] == vy0 else -0.3)
                bx, by = b[0] + (0.3 if b[0] == vx0 else -0.3), b[1] + (0.3 if b[1] == vy0 else -0.3)
                rail(mi, F, (ax, ay), (bx, by), zf, 3.2)
                ln = math.hypot(bx - ax, by - ay)
                lcol(area + "Guard", F, (ax + bx) / 2, (ay + by) / 2, zf, ln + 0.6, 0.6, 3.6,
                     yaw=math.atan2(by - ay, bx - ax))
    else:
        ceiling_flat(mi, F, iw, idp, zc_flat, (xl, xl + dep, hy0, hy1))
    collisions(area, F, hrec, T, eave)
    if spec.get("shop") is not None:
        lcol(area + "Socle", F, spec["shop"], d / 2 + 1.0, 0.0, V.SHOP_W * V.K + 1.6, 2.0, 4.2)
    if two:
        roof_inside(mbx, mi, F, info)
    if info.get("turret"):
        tx, ty, r, ztop = info["turret"]
        p = F.p(tx * V.K, ty * V.K, 0.0)
        SL.octo_col(area + "Turret", p.x, p.y, (r + 0.3) * V.K, z - 0.8, z + ztop * V.K)
    ctx = dict(area=area, iw=iw, idp=idp, h0=h0, zf=zf, xe=xe, zc=zc_flat, eave=eave)
    {"H1": furnish_tavern, "H2": furnish_smith, "H3": furnish_apothecary, "H4": furnish_miner,
     "H5": furnish_cartographer, "H6": furnish_guard, "H7": furnish_arms}[nm](mi, F, ctx, spec, info)
    mi.finish()
    _X[0] = None


def _lift(fn):
    """chama um movel 'de piso' com o piso do andar de cima (troca FLOOR temporariamente)"""
    def wrap(*a, z=0.0, **k):
        global FLOOR
        old = FLOOR
        FLOOR = z + 0.0
        try:
            return fn(*a, **k)
        finally:
            FLOOR = old
    return wrap


def desk(mi, F, cx, cy, yaw, zf=None, lx=5.0, ly=2.2, candle_=True, books=2):
    """escrivaninha com cadeira (frente da cadeira para -v), vela e livros"""
    z = FLOOR if zf is None else zf
    S = Sub(cx, cy, yaw)
    _lift(table)(mi, F, cx, cy, lx, ly, 2.9, yaw, z=z)
    cxy = S.xy(0.0, 2.0)
    _lift(chair)(mi, F, cxy[0], cxy[1], yaw + math.pi, z=z)
    if candle_:
        candle(mi, F, *S.xy(-lx / 2 + 0.7, 0.3), z + 2.9, 1.0)
    if books >= 1:
        book(mi, F, *S.xy(0.4, 0.1), z + 2.9, yaw, open_=True)
    if books >= 2:
        book(mi, F, *S.xy(lx / 2 - 1.0, -0.4), z + 2.9, yaw + 0.3, m=M_NAVY)


def wash_stand(mi, F, cx, cy, yaw, zf):
    S = Sub(cx, cy, yaw)
    _lift(table)(mi, F, cx, cy, 2.4, 2.4, 3.0, yaw, z=zf)
    lathe(mi, F, cx, cy, zf + 3.0, [(0.5, 0.0), (1.0, 0.3), (1.1, 0.5), (0.0, 0.5)], M_LIN, 8)        # bacia


def partition(mi, F, ctx, x_, y0, y1, zf, z1, door=None):
    """tabique de enxaimel (04.07): soleira, frechal, montantes e reboco entre eles, ao longo de y em x_"""
    ms = mx()
    hh = z1 - zf
    tb(mi, F, x_, (y0 + y1) / 2, zf, 0.4, y1 - y0, 0.5, W_STR, 0.03)
    tb(mi, F, x_, (y0 + y1) / 2, z1 - 0.5, 0.4, y1 - y0, 0.5, W_STR, 0.03)
    npost = max(2, int(round((y1 - y0) / 3.2)))
    for k in range(npost + 1):
        yy = y0 + (y1 - y0) * k / npost
        tb(mi, F, x_, yy, zf + 0.5, 0.4, 0.4, hh - 1.0, W_STR, 0.0)
    tb(ms, F, x_, (y0 + y1) / 2, zf + 0.5, 0.22, y1 - y0, hh - 1.0, M_PLAS, 0.0)
    bm_(mi, F, (x_, y0 + 0.3, zf + hh * 0.55), (x_, y0 + 3.0, z1 - 0.6), 0.24, 0.3)
    lcol(ctx["area"], F, x_, (y0 + y1) / 2, zf, 0.5, y1 - y0, hh)
    if door:
        d0, d1 = door
        tb(mi, F, x_, (d0 + d1) / 2, z1 - 3.0, 0.5, d1 - d0 + 0.8, 0.5, W_STR, 0.03)
        for yy in (d0, d1):
            tb(mi, F, x_, yy, zf, 0.5, 0.5, z1 - 3.0 - zf, W_STR, 0.0)


# ------------------------------------------------------------------ H2 FERREIRO
def furnish_smith(mi, F, ctx, spec, info):
    area, iw, idp, zf = ctx["area"], ctx["iw"], ctx["idp"], ctx["zf"]
    ms = mx()
    xl = -iw / 2
    # bigorna sobre cepo na frente da forja
    ax, ay = xl + 7.8, 6.2                                    # fora do corredor porta -> escada (>= 3,4 livre)
    p = F.p(ax, ay, FLOOR)
    mi.cyl(0.85, 2.1, (p.x, p.y, p.z + 1.05), m=W_MID, n=8, bevel=0.0)
    tb(ms, F, ax, ay, FLOOR + 2.1, 1.3, 0.9, 0.35, IRON, 0.03)
    tb(ms, F, ax, ay, FLOOR + 2.45, 0.8, 0.5, 0.45, IRON, 0.0)
    tb(ms, F, ax + 0.2, ay, FLOOR + 2.9, 2.2, 0.7, 0.5, IRON, 0.08)
    q = F.p(ax + 1.3, ay, FLOOR + 3.15)
    ms.cyl(0.3, 1.2, (q.x, q.y, q.z), (0, math.pi / 2, F.a), IRON, n=6, r2=0.1, bevel=0.0)
    lcol(area, F, ax, ay, 0.0, 2.2, 1.2, 3.4)
    rod(mi, F, (ax - 0.5, ay + 0.1, FLOOR + 3.4), (ax - 0.5, ay + 0.1, FLOOR + 5.2), 0.08, W_MID, 4)   # martelo pousado
    tb(ms, F, ax - 0.5, ay + 0.1, FLOOR + 5.0, 0.5, 0.26, 0.26, IRON, 0.0)
    # esmeril: roda de pedra vertical numa armacao com manivela e banco
    gx, gy = 7.0, -2.0
    S = Sub(gx, gy, 0.0)
    for k in (-1, 1):
        sbox(mi, F, S, k * 1.1, 0, FLOOR, 0.4, 1.8, 2.6, W_STR, 0.0)
        sbox(mi, F, S, k * 1.1, 0, FLOOR, 0.5, 2.2, 0.3, W_STR, 0.0)
    sbox(mi, F, S, 0, 0, FLOOR + 1.0, 2.4, 1.6, 0.6, W_MID, 0.03)
    p = F.p(gx, gy, FLOOR + 2.6)
    ms.cyl(1.4, 0.5, (p.x, p.y, p.z), (0, math.pi / 2, F.a), M_STONE, n=10, bevel=0.0)
    rod(ms, F, (gx - 1.5, gy, FLOOR + 2.6), (gx + 1.6, gy, FLOOR + 2.6), 0.1, IRON, 5)
    rod(ms, F, (gx + 1.6, gy, FLOOR + 2.6), (gx + 1.6, gy, FLOOR + 3.4), 0.08, IRON, 4)
    rod(mi, F, (gx + 1.6, gy, FLOOR + 3.4), (gx + 2.3, gy, FLOOR + 3.4), 0.09, W_MID, 4)
    lcol(area, F, gx, gy, 0.0, 3.0, 2.4, 3.4)
    # bancada de trabalho sob a janela da frente direita (x 8,6..13,8): torno, ferramentas, pecas
    bx, by = 11.2, idp / 2 - 1.0
    S = Sub(bx, by, 0.0)
    sbox(mi, F, S, 0, 0, FLOOR + 3.3, 6.4, 2.0, 0.3, W_MID, 0.06)
    for ku in (-1, 1):
        for kv in (-1, 1):
            sbox(mi, F, S, ku * 2.8, kv * 0.7, FLOOR, 0.45, 0.45, 3.3, W_MID, 0.0)
    sbox(mi, F, S, 0, 0, FLOOR + 0.9, 5.8, 1.6, 0.16, W_MID, 0.02)
    lcol(area, F, bx, by, 0.0, 6.4, 2.0, 3.6)
    tb(ms, F, bx + 2.2, by + 0.5, FLOOR + 3.6, 1.1, 0.8, 0.8, IRON, 0.05)                   # torno
    rod(ms, F, (bx + 2.2, by + 1.3, FLOOR + 4.0), (bx + 2.2, by - 0.4, FLOOR + 4.0), 0.07, IRON, 4)
    for j, u in enumerate((-2.4, -1.3, -0.1)):
        a = F.p(*S.xy(u, 0.3 - 0.4 * (j % 2)), z=FLOOR + 3.7)
        mi.beam(a, F.p(*S.xy(u + 0.9, -0.5 + 0.3 * (j % 2)), z=FLOOR + 3.7), 0.16, 0.12, W_MID, 0.0)
        ms.box((0.32, 0.5, 0.3), a, (0, 0, F.a + 0.3 * j), IRON, 0.02)                     # martelos / tenaz
    for u in (-2.5, -1.6):
        sbox(ms, F, S, u, -0.3, FLOOR + 0.9 + 0.16, 0.5, 1.2, 0.6, IRON, 0.0)                # ferro em barra
    # quadro de ferramentas na parede da direita (y 2..8), ganchos com martelos, tenazes e ferraduras
    xr = iw / 2 - 0.2
    S = Sub(xr, 2.5, math.pi / 2)
    tb(mi, F, xr - 0.1, 2.5, FLOOR + 4.4, 0.24, 6.4, 3.6, W_STR, 0.03)
    for j, v in enumerate((-2.4, -1.2, 0.0, 1.2, 2.4)):
        yy = 2.5 + v
        zt = FLOOR + 7.4
        rod(mi, F, (xr - 0.45, yy, zt), (xr - 0.45, yy, zt - 1.9 - 0.5 * (j % 2)), 0.1, W_MID, 4)
        if j % 2:
            tb(ms, F, xr - 0.45, yy, zt - 2.4, 0.3, 1.0, 0.4, IRON, 0.02)                       # martelo
        else:
            rod(ms, F, (xr - 0.45, yy - 0.25, zt - 1.9), (xr - 0.45, yy - 0.5, zt - 3.4), 0.08, IRON, 4)   # tenaz
            rod(ms, F, (xr - 0.45, yy + 0.25, zt - 1.9), (xr - 0.45, yy + 0.5, zt - 3.4), 0.08, IRON, 4)
    # caixa de carvao e caixotes, barril de agua sob a escada (ponta alta)
    crate(mi, F, 6.0, -idp / 2 + 1.5, s=2.4)
    tb(ms, F, 6.0, -idp / 2 + 1.5, FLOOR + 2.4, 2.0, 2.0, 0.5, M_DARK, 0.3)
    crate(mi, F, 9.0, -idp / 2 + 1.4, s=2.0)
    barrel(mi, F, 11.8, -idp / 2 + 1.5)
    # barras e pecas prontas encostadas na parede da direita (y -4..-1): ferraduras e laminas
    for j, yy in enumerate((-4.5, -3.6, -2.7)):
        rod(ms, F, (xr - 0.3, yy, FLOOR + 0.1), (xr - 0.9, yy, FLOOR + 5.2 + 0.5 * j), 0.1, IRON, 4)
    # tapete de couro (vinho) pequeno na porta? nao: oficina. Tapecaria da guilda na parede da frente esquerda
    S = Sub(-10.5, idp / 2 - 0.06, math.pi)
    tapestry(mi, F, S, 0.0, 0.0, FLOOR + 4.0, 3.6, 4.5, m=M_NAVY, band=M_WINE)
    # ANDAR: cama encostada na direita, bau, mesa com 2 bancos, lavatorio, cabideiro na esquerda, tapete vinho
    _lift(bed)(mi, F, iw / 2 - 4.7, 6.3, math.pi / 2, cover=M_WINE, z=zf)
    lcol(area, F, iw / 2 - 4.7, 6.3, zf, 9.0, 5.2, 2.2)
    _lift(chest)(mi, F, iw / 2 - 10.3, 6.3, math.pi / 2, z=zf)
    _lift(table)(mi, F, 3.0, 8.0, 5.0, 2.8, 3.2, z=zf)
    lcol(area, F, 3.0, 8.0, zf, 5.0, 2.8, 3.2)
    _lift(stool)(mi, F, 1.0, 5.8, z=zf)
    _lift(stool)(mi, F, 5.2, 5.8, z=zf)
    candle(mi, F, 3.6, 8.3, zf + 3.2, 1.1)
    mug(mi, F, 2.0, 7.6, zf + 3.2)
    wash_stand(mi, F, iw / 2 - 1.6, 0.5, math.pi / 2, zf)
    S = Sub(-iw / 2 + 0.13, 9.0, -math.pi / 2)
    peg_rail(mi, F, S, 0.0, 0.0, zf + 7.0, 3.0, capes=(M_NAVY, M_WINE))
    _lift(wardrobe)(mi, F, -12.4, idp / 2 - 1.1, math.pi, z=zf, lx=4.0)
    _lift(rug)(mi, F, 2.0, 2.5, 9.0, 6.0, z=zf, m=M_WINE, border=M_NAVY)


# ------------------------------------------------------------------ H3 BOTICARIO
def furnish_apothecary(mi, F, ctx, spec, info):
    area, iw, idp, zf, h0 = ctx["area"], ctx["iw"], ctx["idp"], ctx["zf"], ctx["h0"]
    ms = mx()
    # balcao de venda (frente para a porta) no quadrante da frente direita, atras dele a estante alta de frascos
    bx, by = 8.5, 3.5
    tb(mi, F, bx, by, FLOOR, 10.0, 2.0, 3.3, W_STR, 0.04)
    tb(mi, F, bx, by, FLOOR + 3.3, 10.6, 2.8, 0.32, W_MID, 0.1)
    for j in range(5):
        tb(mi, F, bx - 4.0 + 2.0 * j, by + 1.06, FLOOR + 0.5, 1.5, 0.14, 2.3, W_MID, 0.04)      # almofadas
    lcol(area, F, bx, by, 0.0, 10.6, 2.8, 3.6)
    for j, u in enumerate((-4.0, -2.6, -1.4)):
        prof = [(0.3, 0.0), (0.34, 0.9), (0.14, 1.1), (0.14, 1.5), (0.0, 1.5)] if j % 2 else \
               [(0.4, 0.0), (0.44, 0.7), (0.3, 0.95), (0.34, 1.1), (0.0, 1.1)]
        lathe(mi, F, bx + u, by - 0.3, FLOOR + 3.62, prof, (M_WINE, M_LIN, M_NAVY)[j], 6)
    book(mi, F, bx + 0.6, by + 0.2, FLOOR + 3.62, 0.2, open_=True, m=M_NAVY)
    # balanca: coluna, travessao e 2 pratos
    sx, sy = bx + 3.4, by - 0.2
    rod(ms, F, (sx, sy, FLOOR + 3.62), (sx, sy, FLOOR + 5.4), 0.1, IRON, 5)
    tb(ms, F, sx, sy, FLOOR + 3.62, 0.9, 0.9, 0.14, IRON, 0.02)
    rod(ms, F, (sx - 1.1, sy, FLOOR + 5.3), (sx + 1.1, sy, FLOOR + 5.3), 0.06, IRON, 4)
    for k in (-1, 1):
        rod(ms, F, (sx + k * 1.1, sy, FLOOR + 5.3), (sx + k * 1.1, sy, FLOOR + 4.3), 0.03, IRON, 3)
        p = F.p(sx + k * 1.1, sy, FLOOR + 4.3)
        ms.cyl(0.42, 0.08, (p.x, p.y, p.z), m=IRON, n=6, bevel=0.0)
    # estantes altas de frascos na parede da direita (atras do balcao e ao lado da porta)
    shelf(mi, F, iw / 2 - 0.8, -3.0, math.pi / 2, 7.0, 7.4, 1.6, items="jars")
    lcol(area, F, iw / 2 - 0.8, -3.0, 0.0, 1.6, 7.0, 7.4)
    shelf(mi, F, iw / 2 - 0.8, 3.0, math.pi / 2, 4.6, 7.0, 1.6, items="jars")
    # mesa de trabalho a esquerda: pilao, alambique, frascos, caderno; cadeira
    tx, ty = -11.5, 7.8
    table(mi, F, tx, ty, 3.0, 6.0, 3.4)
    chair(mi, F, tx + 2.6, ty - 0.5, math.pi / 2)
    lathe(ms, F, tx + 0.2, ty - 1.8, FLOOR + 3.4, [(0.45, 0.0), (0.5, 0.5), (0.4, 0.75), (0.0, 0.75)], M_STONE, 8)   # pilao
    rod(mi, F, (tx + 0.2, ty - 1.8, FLOOR + 3.7), (tx + 0.5, ty - 1.3, FLOOR + 4.8), 0.1, W_MID, 5)                # mao
    lathe(ms, F, tx - 0.4, ty + 0.4, FLOOR + 3.4, [(0.6, 0.0), (0.8, 0.5), (0.5, 1.2), (0.18, 1.4), (0.18, 2.2), (0.0, 2.2)], IRON, 8)  # alambique
    rod(ms, F, (tx - 0.4, ty + 0.4, FLOOR + 5.5), (tx + 0.2, ty + 1.8, FLOOR + 4.6), 0.08, IRON, 4)
    lathe(mi, F, tx + 0.2, ty + 1.9, FLOOR + 3.4, [(0.28, 0.0), (0.3, 0.7), (0.1, 0.9), (0.1, 1.3), (0.0, 1.3)], M_WINE, 5)
    book(mi, F, tx + 0.8, ty - 0.4, FLOOR + 3.4, 0.4, m=M_NAVY)
    candle(mi, F, tx - 0.9, ty + 2.4, FLOOR + 3.4, 1.0)
    # ervas secando: vara pendurada nas vigas (2 cordas) com 6 molhos; outra vara menor junto a lareira
    for (hx0, hx1, hy, nb) in ((-1.0, 7.0, -1.5, 6), (-11.0, -6.0, 7.5, 3)):
        zb = h0 - 1.0
        zr = zb - 2.2
        for xx in (hx0 + 0.6, hx1 - 0.6):
            rod(mi, F, (xx, hy, zb), (xx, hy, zr), 0.05, M_LIN, 3)
        rod(mi, F, (hx0, hy, zr), (hx1, hy, zr), 0.1, W_STR, 5)
        for k in range(nb):
            xx = hx0 + 0.9 + (hx1 - hx0 - 1.8) * k / max(1, nb - 1)
            # molho de ervas secas pendurado de cabeca para baixo: 4 hastes finas abertas em leque a partir do cordel
            # (palito, nunca volume facetado: nada que leia como cristal)
            rod(mi, F, (xx, hy, zr), (xx, hy, zr - 0.4), 0.04, M_LIN, 3)
            for j, (du, dv) in enumerate(((-0.35, 0.1), (0.3, -0.15), (0.0, 0.35))):
                bm_(mi, F, (xx, hy, zr - 0.35), (xx + du, hy + dv, zr - 1.9 + 0.2 * (j % 2)), 0.14, 0.14,
                    (W_MID, W_STR)[(j + k) % 2])
    # caixotes e barril de raizes sob a escada, tapete vinho pequeno diante do balcao
    crate(mi, F, 6.5, -idp / 2 + 1.4, s=2.2)
    barrel(mi, F, 9.6, -idp / 2 + 1.4, r=1.0, h=2.5)
    rug(mi, F, 4.0, 7.5, 5.0, 3.4, m=M_WINE, border=M_NAVY)
    S = Sub(-iw / 2, 8.0, -math.pi / 2)
    wall_shelf(mi, F, S, 0.0, 0.0, FLOOR + 6.4, 4.0, items="jars")
    # ANDAR: cama de dossel a direita, escrivaninha com frascos, guarda-roupa, bau sob a janela, tapete navy
    _lift(bed)(mi, F, iw / 2 - 4.7, 5.0, math.pi / 2, cover=M_NAVY, canopy=True, z=zf)
    lcol(area, F, iw / 2 - 4.7, 5.0, zf, 9.0, 5.2, 2.2)
    desk(mi, F, -10.0, 5.5, math.pi / 2, zf=zf, books=1)
    lathe(mi, F, -10.3, 7.1, zf + 2.9, [(0.3, 0.0), (0.34, 0.9), (0.14, 1.1), (0.14, 1.5), (0.0, 1.5)], M_NAVY, 5)
    _lift(wardrobe)(mi, F, -12.4, idp / 2 - 1.1, math.pi, z=zf, lx=4.0)
    _lift(chest)(mi, F, 4.0, idp / 2 - 1.1, 0.0, z=zf)
    _lift(rug)(mi, F, 1.0, 3.0, 8.0, 10.0, z=zf, yaw=math.pi / 2)
    S = Sub(0.0, -idp / 2 + 0.13, 0.0)
    peg_rail(mi, F, S, 0.0, 0.0, zf + 7.0, 2.6, capes=(M_WINE,))
    candle(mi, F, 8.0, 1.8, zf + 2.5, 1.1)
    _lift(table)(mi, F, 8.0, 1.8, 1.7, 1.7, 2.5, z=zf)


# ------------------------------------------------------------------ H5 CARTOGRAFO
def furnish_cartographer(mi, F, ctx, spec, info):
    area, iw, idp, zf, h0 = ctx["area"], ctx["iw"], ctx["idp"], ctx["zf"], ctx["h0"]
    ms = mx()
    # mesa grande de mapas no meio (mapa de linho com 2 continentes navy), compasso gigante, lanterna, rolos
    tx, ty = 5.0, 2.0
    table(mi, F, tx, ty, 10.0, 6.0, 3.4)
    lcol(area, F, tx, ty, 0.0, 10.0, 6.0, 3.4)
    # carta nautica: folha de linho com moldura navy, 2 continentes pequenos (navy com miolo vinho), rosa dos ventos
    tb(mi, F, tx - 0.6, ty, FLOOR + 3.4, 6.6, 4.0, 0.08, M_LIN, 0.0)
    for k in (-1, 1):
        tb(mi, F, tx - 0.6, ty + k * 1.9, FLOOR + 3.48, 6.6, 0.14, 0.03, M_NAVY, 0.0)
        tb(mi, F, tx - 0.6 + k * 3.23, ty, FLOOR + 3.48, 0.14, 4.0, 0.03, M_NAVY, 0.0)
    zm = FLOOR + 3.48
    for pts, sc in ((((-3.2, -1.2), (-1.4, -1.8), (0.2, -0.6), (-0.4, 0.9), (-2.4, 1.6), (-3.4, 0.4)), 0.62),
                    (((0.9, 0.2), (2.6, -0.9), (3.4, 0.6), (2.4, 1.7), (1.2, 1.3)), 0.62)):
        mi.prism([tuple(F.p(tx - 0.6 + u * sc, ty + v * sc, 0.0))[:2] for u, v in pts], zm, zm + 0.05, M_NAVY, 0.0)
        mi.prism([tuple(F.p(tx - 0.6 + u * sc * 0.5, ty + v * sc * 0.5 + 0.05, 0.0))[:2] for u, v in pts], zm + 0.05,
                 zm + 0.08, M_WINE, 0.0)
    lathe(mi, F, tx + 1.6, ty + 1.2, zm, [(0.45, 0.0), (0.45, 0.04), (0.0, 0.04)], M_WINE, 8)             # rosa dos ventos
    for k in (-1, 1):                                                                       # compasso de pontas
        rod(ms, F, (tx + 2.0 + k * 0.7, ty - 1.2, FLOOR + 3.48), (tx + 2.0, ty - 1.2, FLOOR + 5.4), 0.08, IRON, 4)
    lathe(ms, F, tx + 2.0, ty - 1.2, FLOOR + 5.3, [(0.14, 0.0), (0.18, 0.25), (0.0, 0.5)], IRON, 5)
    lantern_table(mi, F, tx + 3.8, ty - 1.9, FLOOR + 3.4, 1.0)
    rod(mi, F, (tx - 3.6, ty - 2.2, FLOOR + 3.65), (tx + 0.8, ty - 2.2, FLOOR + 3.65), 0.25, M_LIN, 6)      # rolo
    book(mi, F, tx - 3.4, ty + 1.9, FLOOR + 3.4, 0.2, m=M_WINE)
    for cx, cy in ((tx - 3.0, ty - 4.2), (tx + 1.0, ty - 4.2)):
        stool(mi, F, cx, cy)
    chair(mi, F, tx + 6.3, ty, math.pi / 2)
    # escaninhos de rolos na parede da direita (atras do balcao: y -5..1)
    rx, ry = iw / 2 - 0.9, -2.5
    S = Sub(rx, ry, math.pi / 2)
    sbox(mi, F, S, 0, 0, FLOOR, 7.0, 1.8, 0.4, W_STR, 0.03)
    for k in (-1, 1):
        sbox(mi, F, S, k * 3.35, 0, FLOOR + 0.4, 0.3, 1.8, 7.0, W_STR, 0.0)
    sbox(mi, F, S, 0, -0.8, FLOOR + 0.4, 6.8, 0.16, 7.0, W_STR, 0.0)
    for i in range(4):
        sbox(mi, F, S, 0, 0, FLOOR + 0.4 + 7.0 * i / 3 - (0.2 if i == 3 else 0.0), 6.8, 1.8, 0.2, W_MID, 0.0)
    for u in (-1.7, 0.0, 1.7):
        sbox(mi, F, S, u, 0, FLOOR + 0.4, 0.16, 1.7, 7.0, W_MID, 0.0)
    for i in range(3):
        for j, u in enumerate((-2.55, -0.85, 0.85, 2.55)):
            if (i + j) % 3 == 2:
                continue
            x0, y0 = S.xy(u, -0.6)
            x1, y1 = S.xy(u, 0.95)
            zz = FLOOR + 0.6 + 7.0 * i / 3 + 0.3
            rod(mi, F, (x0, y0, zz), (x1, y1, zz), 0.26, (M_LIN, M_LIN, M_WINE)[(i + j) % 3], 6)
    lcol(area, F, rx, ry, 0.0, 1.8, 7.0, 7.6)
    # globo com meridiano de ferro e pe de 3 pernas, junto a vitrine da loja
    gx, gy = 11.5, 7.5
    p = F.p(gx, gy, FLOOR)
    for k in range(3):
        a = F.a + 2 * math.pi * k / 3
        mi.beam((p.x + 1.0 * math.cos(a), p.y + 1.0 * math.sin(a), p.z), (p.x, p.y, p.z + 2.6), 0.26, 0.26, W_MID, 0.0)
    mi.cyl(0.4, 0.5, (p.x, p.y, p.z + 2.6), m=W_MID, n=6, bevel=0.03)
    mi.ico(1.35, (p.x, p.y, p.z + 4.4), M_NAVY, sub=1)
    V._lathe(ms, (p.x, p.y, p.z + 4.4), [(1.5, -0.15), (1.5, 0.15)], IRON, 12, closed=False, caps=(False, False))
    ms.cyl(1.55, 0.14, (p.x, p.y, p.z + 4.4), (0, math.pi / 2, F.a + 0.5), IRON, n=12, r2=1.55, bevel=0.0, caps=False)
    rod(ms, F, (gx, gy, FLOOR + 3.1), (gx, gy, FLOOR + 5.9), 0.07, IRON, 4)
    lcol(area, F, gx, gy, 0.0, 2.4, 2.4, 6.0)
    # mesa de desenho inclinada sob a janela da frente esquerda (x -9,8), com folha e tinteiro
    dx, dy = -9.8, idp / 2 - 1.6
    S = Sub(dx, dy, 0.0)
    for ku in (-1, 1):
        sbox(mi, F, S, ku * 1.9, 0.5, FLOOR, 0.4, 0.4, 3.6, W_MID, 0.0)
        sbox(mi, F, S, ku * 1.9, -0.6, FLOOR, 0.4, 0.4, 2.9, W_MID, 0.0)
    p = F.p(dx, dy, FLOOR + 3.3)
    mi.box((4.6, 1.9, 0.26), (p.x, p.y, p.z), (0.32, 0.0, F.a), W_MID, 0.06)
    mi.box((3.0, 1.3, 0.06), (p.x, p.y + 0.0, p.z + 0.16), (0.32, 0.0, F.a), M_LIN, 0.0)
    sbox(mi, F, S, 0, -0.9, FLOOR + 2.85, 4.4, 0.2, 0.3, W_MID, 0.0)
    stool(mi, F, dx, dy - 2.4)
    # estante de livros e atlas sob a escada (ponta alta) + barril de rolos
    shelf(mi, F, 8.5, -idp / 2 + 0.9, 0.0, 5.0, 6.0, 1.5, items="books")
    barrel(mi, F, 12.6, -idp / 2 + 1.5, r=1.0, h=2.5)
    for k in range(4):
        a = 2 * math.pi * k / 4
        rod(mi, F, (12.6 + 0.4 * math.cos(a), -idp / 2 + 1.5 + 0.4 * math.sin(a), FLOOR + 1.0),
            (12.6 + 0.7 * math.cos(a), -idp / 2 + 1.5 + 0.7 * math.sin(a), FLOOR + 4.6), 0.22, M_LIN, 5)
    # mapa emoldurado na parede da frente (direita da porta, sob a bandeira da loja) e na esquerda sobre o consolo
    for (S, u, z, wd, hh) in ((Sub(10.0, idp / 2, math.pi), 0.0, FLOOR + 5.2, 4.4, 3.0),
                              (Sub(-iw / 2, 8.0, -math.pi / 2), 0.0, FLOOR + 5.0, 3.6, 2.8)):
        framed_map(mi, F, S, u, z, wd, hh)
    # ANDAR: tabique em x = 4 (quarto a esquerda, escritorio a direita com vao de porta no lado da escada)
    partition(mi, F, ctx, 4.0, 4.5, idp / 2 - 0.1, zf, ctx["eave"] - 1.0)
    tb(mi, F, 4.0, 0.0, zf + 8.6, 0.5, 9.6, 0.5, W_STR, 0.03)
    # quarto: cama de armario (caixa de madeira com cortina) encostada na frente entre as janelas, bau, lavatorio
    _lift(bed)(mi, F, -4.25, 6.2, math.pi, cover=M_NAVY, lx=5.2, ly=8.8, z=zf)
    lcol(area, F, -4.25, 6.2, zf, 5.2, 8.8, 2.2)
    S = Sub(-4.25, idp / 2, math.pi)
    tapestry(mi, F, S, 0.0, 0.0, zf + 6.6, 3.6, 3.2, m=M_WINE, band=M_NAVY)             # sobre a cabeceira
    _lift(chest)(mi, F, -11.5, 9.6, 0.0, z=zf)
    wash_stand(mi, F, -12.8, 2.0, math.pi / 2, zf)
    _lift(rug)(mi, F, -6.0, 0.0, 9.0, 6.0, z=zf, m=M_WINE, border=M_NAVY)
    S = Sub(-iw / 2, -2.0, -math.pi / 2)
    wall_shelf(mi, F, S, 0.0, 0.0, zf + 6.0, 3.0, items="pots")
    # escritorio: escrivaninha sob a janela da frente direita, estante na direita, globo pequeno, tapete navy
    desk(mi, F, 10.0, idp / 2 - 3.2, 0.0, zf=zf, lx=5.6, ly=2.4, books=2)
    lcol(area, F, 10.0, idp / 2 - 3.2, zf, 5.6, 2.4, 2.9)
    shelf(mi, F, iw / 2 - 0.8, 1.5, math.pi / 2, 5.0, 7.0, 1.5, items="books", z0=zf)
    _lift(rug)(mi, F, 9.0, 1.5, 7.0, 5.0, z=zf)
    S = Sub(4.28, 7.0, -math.pi / 2)
    tapestry(mi, F, S, 0.0, 0.0, zf + 3.5, 4.0, 4.5, m=M_NAVY, band=M_WINE)


# ------------------------------------------------------------------ H7 MESTRE DE ARMAS
def furnish_arms(mi, F, ctx, spec, info):
    area, iw, idp, zf, h0 = ctx["area"], ctx["iw"], ctx["idp"], ctx["zf"], ctx["h0"]
    ms = mx()
    xr = iw / 2
    # armeiro de lancas e alabardas na parede da direita (y -4..3): 2 ruas, 5 hastes, pontas de ferro
    S = Sub(xr - 0.25, -0.5, math.pi / 2)
    for zz in (1.2, 6.2):
        sbox(mi, F, S, 0, 0.0, FLOOR + zz, 7.0, 0.5, 0.5, W_STR, 0.03)
    for j, v in enumerate((-2.8, -1.4, 0.0, 1.4, 2.8)):
        x_, y_ = S.xy(v, 0.55)
        hh = 9.6 if j % 2 == 0 else 8.4
        rod(mi, F, (x_, y_, FLOOR + 0.4), (x_, y_, FLOOR + hh), 0.11, W_MID, 4)
        if j == 2:
            tb(ms, F, x_, y_, FLOOR + hh - 1.2, 0.2, 1.1, 1.6, IRON, 0.0)                   # alabarda
        else:
            p = F.p(x_, y_, FLOOR + hh)
            V._lathe(ms, (p.x, p.y, p.z), [(0.18, 0.0), (0.2, 0.25), (0.0, 1.1)], IRON, 4)
    # escudos redondos na parede da direita (y 9,5) e na esquerda; espadas cruzadas sobre o consolo da lareira
    for (x_, y_, rot, mcol) in ((13.0, idp / 2 - 0.35, (math.pi / 2, 0.0, F.a), M_WINE),
                                (-xr + 0.35, -7.5, (0.0, math.pi / 2, F.a), M_NAVY)):
        p = F.p(x_, y_, FLOOR + 6.6)
        mi.cyl(1.3, 0.3, (p.x, p.y, p.z), rot, mcol, n=10, bevel=0.05)
        ms.cyl(0.38, 0.4, (p.x, p.y, p.z), rot, IRON, n=8, bevel=0.03)
        ms.cyl(1.32, 0.12, (p.x, p.y, p.z), rot, IRON, n=10, r2=1.1, bevel=0.0)
    xb = -xr + 3.3 + 0.35                                 # face do peito da chamine
    for k in (-1, 1):
        a = (xb, 1.0 + k * 1.6, FLOOR + 7.4)
        b = (xb, 1.0 - k * 1.6, FLOOR + 11.0)
        rod(ms, F, a, b, 0.14, IRON, 4)
        tb(mi, F, xb, 1.0 + k * 1.2, FLOOR + 8.2, 0.3, 1.0, 0.3, W_MID, 0.02, yaw=k * 0.42)
    # boneco de treino: poste, travessa, torso acolchoado e cabeca
    px, py = 5.0, 0.5
    tb(mi, F, px, py, FLOOR, 1.6, 1.6, 0.4, W_STR, 0.04)
    tb(mi, F, px, py, FLOOR + 0.4, 0.5, 0.5, 8.2, W_STR, 0.0)
    tb(mi, F, px, py, FLOOR + 5.4, 3.6, 0.4, 0.4, W_STR, 0.0)
    lathe(mi, F, px, py, FLOOR + 3.4, [(0.75, 0.0), (1.05, 0.9), (1.0, 2.4), (0.55, 3.3), (0.0, 3.4)], M_WINE, 6)   # saco acolchoado
    lathe(ms, F, px, py, FLOOR + 4.15, [(1.07, 0.0), (1.07, 0.22)], IRON, 6, caps=(False, False))                 # cinta
    lathe(mi, F, px, py, FLOOR + 7.0, [(0.3, 0.0), (0.62, 0.4), (0.6, 1.1), (0.0, 1.4)], M_LIN, 6)
    lcol(area, F, px, py, 0.0, 2.2, 1.8, 8.6)
    # alvo de palha na parede da direita (ponta da escada) e estante de armas junto a porta
    p = F.p(xr - 0.5, -8.0, FLOOR + 5.5)
    mi.cyl(1.7, 0.5, (p.x, p.y, p.z), (0, math.pi / 2, F.a), M_LIN, n=12, bevel=0.0)
    mi.cyl(1.2, 0.6, (p.x, p.y, p.z), (0, math.pi / 2, F.a), M_WINE, n=12, bevel=0.0)
    mi.cyl(0.5, 0.7, (p.x, p.y, p.z), (0, math.pi / 2, F.a), M_NAVY, n=8, bevel=0.0)
    for k in range(3):
        a = 0.3 + k * 0.9
        q = (xr - 0.9, -8.0 + 0.9 * math.cos(a), FLOOR + 5.5 + 0.9 * math.sin(a))
        rod(mi, F, (q[0] - 3.4, q[1], q[2] - 0.5), q, 0.06, W_MID, 4)                      # dardos cravados
    # manequim de armadura (peitoral, ombreiras, elmo) na frente esquerda, sob a janela
    mxx, myy = -12.4, 9.8
    tb(mi, F, mxx, myy, FLOOR, 1.8, 1.8, 0.4, W_STR, 0.04)
    tb(mi, F, mxx, myy, FLOOR + 0.4, 0.4, 0.4, 7.0, W_STR, 0.0)
    tb(ms, F, mxx, myy, FLOOR + 3.4, 2.2, 1.3, 3.0, IRON, 0.35)
    for k in (-1, 1):
        tb(ms, F, mxx + k * 1.3, myy, FLOOR + 5.9, 0.9, 1.2, 0.5, IRON, 0.15)
    lathe(ms, F, mxx, myy, FLOOR + 7.1, [(0.5, 0.0), (0.66, 0.5), (0.6, 1.1), (0.0, 1.5)], IRON, 8)
    tb(mi, F, mxx, myy - 0.1, FLOOR + 6.4, 1.6, 1.0, 0.5, M_WINE, 0.1)
    lcol(area, F, mxx, myy, 0.0, 2.4, 1.8, 8.6)
    # bancada de amolar e mesa com pedra de amolar, bau de armas, barril de lancas
    bx, by = 10.0, 4.5
    table(mi, F, bx, by, 5.0, 2.6, 3.2)
    lcol(area, F, bx, by, 0.0, 5.0, 2.6, 3.2)
    bench(mi, F, bx, by - 2.3, 4.0)
    tb(ms, F, bx - 1.0, by + 0.2, FLOOR + 3.2, 1.4, 0.7, 0.4, M_STONE, 0.04)                 # pedra de amolar
    tb(ms, F, bx + 1.2, by - 0.2, FLOOR + 3.2, 0.3, 2.6, 0.08, IRON, 0.0)                    # lamina
    tb(mi, F, bx + 1.2, by + 1.6, FLOOR + 3.2, 0.3, 0.9, 0.3, W_STR, 0.0)
    chest(mi, F, -12.5, 7.4, 0.0, 3.6, 1.9, 2.0)
    barrel(mi, F, 12.6, idp / 2 - 1.8, r=1.0, h=2.5)
    for k in range(3):
        a = 2 * math.pi * k / 3 + 0.4
        rod(mi, F, (12.6 + 0.3 * math.cos(a), idp / 2 - 1.8 + 0.3 * math.sin(a), FLOOR + 1.0),
            (12.6 + 0.6 * math.cos(a), idp / 2 - 1.8 + 0.6 * math.sin(a), FLOOR + 7.4), 0.11, W_MID, 4)
    crate(mi, F, 8.5, -idp / 2 + 1.4, s=2.2)
    # ANDAR: cama de casal entre as janelas da frente, catre do aprendiz, cabideiro, bau, estante de armas, tapete
    _lift(bed)(mi, F, -4.25, 6.2, math.pi, cover=M_WINE, z=zf)
    lcol(area, F, -4.25, 6.2, zf, 5.2, 9.0, 2.2)
    _lift(bed)(mi, F, iw / 2 - 3.9, 5.5, math.pi / 2, lx=3.6, ly=7.4, cover=M_NAVY, z=zf)
    lcol(area, F, iw / 2 - 3.9, 5.5, zf, 7.4, 3.6, 2.2)
    _lift(chest)(mi, F, -4.25, 0.6, 0.0, z=zf, lx=3.6)
    _lift(wardrobe)(mi, F, -14.0, -2.5, -math.pi / 2, z=zf, lx=4.0)
    S = Sub(-iw / 2 + 0.13, 9.2, -math.pi / 2)
    peg_rail(mi, F, S, 0.0, 0.0, zf + 7.0, 3.0, capes=(M_WINE, M_NAVY))
    _lift(rug)(mi, F, 3.0, 4.0, 10.0, 6.0, z=zf, m=M_NAVY, border=M_WINE, yaw=math.pi / 2)
    _lift(table)(mi, F, 9.5, 2.5, 2.0, 2.0, 2.5, z=zf)
    candle(mi, F, 9.5, 2.5, zf + 2.5, 1.1)
    S = Sub(iw / 2, 9.5, math.pi / 2)
    wall_shelf(mi, F, S, 0.0, 0.0, zf + 6.2, 3.0, items="pots")


# ------------------------------------------------------------------ H1 TAVERNA
def furnish_tavern(mi, F, ctx, spec, info):
    """taverna (04.03): balcao com tampo saliente, frente almofadada em 2 tons e rodape de pedra; prateleiras de
    garrafas e barris deitados atras; 5 mesas com bancos e canecas; caldeirao na lareira e quadro de cardapio; lustre
    de ferro com velas em gota; mezanino com 2 mesas e galeria de 3 quartos com cortina"""
    area, iw, idp, zf, h0 = ctx["area"], ctx["iw"], ctx["idp"], ctx["zf"], ctx["h0"]
    ms = mx()
    bx, by = 8.0, 6.5
    tb(mi, F, bx, by, FLOOR, 12.0, 2.0, 3.3, W_STR, 0.04)
    tb(mi, F, bx, by, FLOOR + 3.3, 12.8, 3.0, 0.34, W_MID, 0.1)
    for j in range(6):
        tb(mi, F, bx - 5.0 + 2.0 * j, by - 1.08, FLOOR + 0.7, 1.5, 0.16, 2.2, W_MID, 0.05)       # almofadas
    tb(ms, F, bx, by - 1.1, FLOOR, 12.2, 0.3, 0.45, M_STONE, 0.03)                               # rodape de pedra
    lcol(area, F, bx, by, 0.0, 12.8, 3.0, 3.7)
    for u in (-4.6, 1.0):
        mug(mi, F, bx + u, by - 0.2, FLOOR + 3.64)
    lathe(mi, F, bx + 3.2, by + 0.3, FLOOR + 3.64, [(0.4, 0.0), (0.46, 1.1), (0.2, 1.4), (0.18, 1.9), (0.0, 1.9)], M_NAVY, 6)   # jarra
    # atras do balcao: estante de garrafas na parede da frente e barris deitados em berco
    shelf(mi, F, bx - 1.0, idp / 2 - 0.8, math.pi, 8.0, 7.0, 1.4, items="bottles")
    for j, xx in enumerate((12.4, 15.2)):
        tb(mi, F, xx, idp / 2 - 1.6, FLOOR, 2.6, 2.4, 0.6, W_STR, 0.04)
        barrel(mi, F, xx, idp / 2 - 1.6, z0=FLOOR + 0.6, r=1.15, h=2.4, lying=True, yaw=math.pi / 2)
    # mesas compridas com bancos e canecas (5), em volta da sala
    tables = ((-10.4, 10.9, 8.0, 0.0), (-11.0, 2.2, 6.0, 0.0), (4.0, -2.0, 6.0, 0.0), (11.0, -1.5, 6.0, 0.0),
              (11.0, -8.2, 6.0, 0.0))
    for i, (cx, cy, ln, yw) in enumerate(tables):
        table(mi, F, cx, cy, ln, 2.8, 3.4, yw)
        lcol(area, F, cx, cy, 0.0, ln, 2.8, 3.6, yw)
        sides = (-1,) if i == 0 else (-1, 1)
        for k in sides:
            bench(mi, F, cx, cy + k * 2.3, ln - 1.0, yw)
        mug(mi, F, cx - ln / 4, cy + 0.4, FLOOR + 3.4)
        if i in (1, 3):
            candle(mi, F, cx + 0.3, cy - 0.2, FLOOR + 3.4, 1.0)
        if i == 2:
            lantern_table(mi, F, cx - 0.4, cy + 0.2, FLOOR + 3.4, 0.9)
    # cadeira de bracos junto ao fogo, lenha empilhada ao lado do lajeado
    chair(mi, F, -11.5, 6.5, math.pi / 2, pad=M_WINE)
    for k, (dy, dz) in enumerate(((0.0, 0.0), (0.6, 0.0), (0.3, 0.55))):
        rod(mi, F, (-iw / 2 + 3.6, 9.2 + dy, FLOOR + 0.3 + dz), (-iw / 2 + 6.2, 9.2 + dy, FLOOR + 0.3 + dz), 0.3, W_STR, 5)
    # cardapio em cavalete junto a ponta do balcao, virado para a porta (lousa escura com 3 linhas)
    S = Sub(3.5, 9.8, 0.0)
    for k in (-1, 1):
        sbox(mi, F, S, k * 1.3, -0.5, FLOOR, 0.3, 0.3, 4.6, W_STR, 0.0)
    sbox(mi, F, S, 0, -0.4, FLOOR + 1.6, 3.0, 0.2, 2.6, W_STR, 0.04)
    sbox(ms, F, S, 0, -0.28, FLOOR + 1.8, 2.6, 0.06, 2.2, M_DARK, 0.0)
    for j in range(3):
        sbox(mi, F, S, -0.2 + 0.15 * j, -0.23, FLOOR + 2.2 + 0.55 * j, 1.8 - 0.4 * j, 0.04, 0.16, M_LIN, 0.0)
    # lustre de ferro com velas (no vazio do mezanino)
    vx0, vy0, vx1, vy1 = spec["void"]
    lx, ly = (vx0 + vx1) / 2, (vy0 + vy1) / 2
    zl = zf + 4.0
    p = F.p(lx, ly, zl)
    V._lathe(ms, (p.x, p.y, p.z), [(3.2, 0.0), (3.4, 0.2), (3.2, 0.4), (2.9, 0.2)], IRON, 10, closed=True)
    for k in range(6):
        a = 2 * math.pi * k / 6
        cx, cy = lx + 3.2 * math.cos(a), ly + 3.2 * math.sin(a)
        candle(mi, F, cx, cy, zl + 0.4, 1.2)
    for k in range(3):
        a = 2 * math.pi * k / 3
        ms.rod((p.x + 3.1 * math.cos(a), p.y + 3.1 * math.sin(a), p.z + 0.3), (p.x, p.y, p.z + 4.2), 0.06, IRON, 4)
    gy = (ly / V.K) if not info["gf"] else (-lx / V.K)
    ztop = F.o.z + info["zboard"](gy) if "zboard" in info else p.z + 8.0
    ms.rod((p.x, p.y, p.z + 4.2), (p.x, p.y, ztop), 0.12, IRON, 4)
    # MEZANINO: galeria de 3 quartos com cortina na parede da direita (y -5..13), 2 mesas com bancos
    xg = iw / 2 - 6.6                                  # frente dos quartos (vara da cortina)
    cells = ((1.0, 4.8), (4.8, 8.6), (8.6, idp / 2 - WALL))
    for i, (y0, y1) in enumerate(cells):
        yc = (y0 + y1) / 2
        lxb = min(4.2, y1 - y0 - 0.5)
        _lift(bed)(mi, F, iw / 2 - 3.2, yc, math.pi / 2, lx=lxb, ly=6.0, cover=(M_WINE, M_NAVY, M_WINE)[i], z=zf)
        lcol(area, F, iw / 2 - 3.2, yc, zf, 6.0, lxb, 2.2)
        candle(mi, F, iw / 2 - 0.6, y0 + 0.5, zf + 5.0, 1.0)
        if i > 0:                                      # tabique entre quartos
            tb(mi, F, iw / 2 - 3.3, y0, zf, 6.6, 0.4, 0.5, W_STR, 0.03)
            tb(mi, F, iw / 2 - 3.3, y0, zf + 8.0, 6.6, 0.4, 0.5, W_STR, 0.03)
            tb(mi, F, xg + 0.2, y0, zf + 0.5, 0.4, 0.4, 7.5, W_STR, 0.0)
            tb(ms, F, iw / 2 - 3.3, y0, zf + 0.5, 6.4, 0.22, 7.5, M_PLAS, 0.0)
            lcol(area, F, iw / 2 - 3.3, y0, zf, 6.6, 0.5, 8.5)
        rod(ms, F, (xg, y0 + 0.2, zf + 8.0), (xg, y1 - 0.2, zf + 8.0), 0.1, IRON, 5)
        # cortina: 1 fechada, 2 recolhidas em um lado
        if i == 0:
            tb(mi, F, xg, yc, zf + 0.3, 0.16, y1 - y0 - 0.6, 7.6, M_WINE, 0.06)
        else:
            tb(mi, F, xg, y0 + 0.9, zf + 0.3, 0.7, 1.3, 7.6, (M_NAVY, M_WINE)[i == 1], 0.2)
    tb(mi, F, xg, (cells[0][0] + cells[-1][1]) / 2, zf + 8.0, 0.5, cells[-1][1] - cells[0][0] + 0.4, 0.5, W_STR, 0.03)
    tb(mi, F, xg, cells[0][0], zf, 0.5, 0.5, 8.0, W_STR, 0.0)
    _lift(table)(mi, F, -7.0, 11.0, 6.0, 2.4, 3.3, z=zf)
    lcol(area, F, -7.0, 11.0, zf, 6.0, 2.4, 3.4)
    _lift(bench)(mi, F, -7.0, 9.2, 5.0, z=zf)
    _lift(table)(mi, F, -14.6, 8.5, 2.6, 6.0, 3.3, z=zf)
    lcol(area, F, -14.6, 8.5, zf, 2.6, 6.0, 3.4)
    _lift(bench)(mi, F, -16.9, 8.5, 5.0, yaw=math.pi / 2, z=zf)
    mug(mi, F, -6.0, 11.2, zf + 3.3)
    candle(mi, F, -14.6, 8.8, zf + 3.3, 1.0)
    # lado direito do vazio (o que a camera do mezanino ve): mesa com bancos, barril e caixote no canto, tapecaria
    _lift(table)(mi, F, 3.5, 9.6, 6.0, 2.6, 3.3, z=zf)
    lcol(area, F, 3.5, 9.6, zf, 6.0, 2.6, 3.4)
    _lift(bench)(mi, F, 3.5, 7.6, 5.0, z=zf)
    _lift(bench)(mi, F, 3.5, 11.6, 5.0, z=zf)
    mug(mi, F, 2.4, 9.3, zf + 3.3)
    candle(mi, F, 4.6, 9.9, zf + 3.3, 1.0)
    _lift(barrel)(mi, F, 9.6, idp / 2 - 2.2, r=1.0, h=2.5, z=zf)
    _lift(crate)(mi, F, 9.4, idp / 2 - 4.8, s=2.0, yaw=0.3, z=zf)
    S = Sub(0.0, idp / 2 - WALL, math.pi)
    tapestry(mi, F, S, 0.0, 0.0, zf + 4.5, 2.4, 4.6, m=M_NAVY, band=M_WINE)
    S = Sub(-iw / 2, -2.5, -math.pi / 2)
    tapestry(mi, F, S, 0.0, 0.0, zf + 4.0, 4.0, 5.0, m=M_WINE, band=M_NAVY)


# ------------------------------------------------------------------ H4 OFICINA DO MINERADOR (terrea)
def furnish_miner(mi, F, ctx, spec, info):
    area, iw, idp, zc = ctx["area"], ctx["iw"], ctx["idp"], ctx["zc"]
    ms = mx()
    S = Sub(1.0, -idp / 2 + 1.0, 0.0)
    sbox(mi, F, S, 0, 0, FLOOR + 3.3, 11.0, 1.9, 0.32, W_MID, 0.06)
    for u in (-5.1, -1.7, 1.7, 5.1):
        sbox(mi, F, S, u, 0, FLOOR, 0.45, 1.6, 3.3, W_MID, 0.04)
    sbox(mi, F, S, 0, 0.1, FLOOR + 0.9, 10.2, 1.5, 0.16, W_MID, 0.02)
    lcol(area, F, 1.0, -idp / 2 + 1.0, 0.0, 11.0, 1.9, 3.6)
    x, y = S.xy(-3.8, 0.3)
    tb(ms, F, x, y, FLOOR + 3.62, 1.2, 0.8, 0.8, IRON, 0.05)
    rod(ms, F, (x, y + 0.6, FLOOR + 4.1), (x, y - 0.6, FLOOR + 4.1), 0.07, IRON, 4)
    for u in (-1.2, 0.2):
        a = F.p(*S.xy(u, 0.2), z=FLOOR + 3.66)
        mi.beam(a, F.p(*S.xy(u + 1.2, 0.0), z=FLOOR + 3.66), 0.18, 0.14, W_MID, 0.0)
        ms.box((0.3, 0.6, 0.3), a, (0, 0, F.a), IRON, 0.03)
    lantern_table(mi, F, 4.5, -idp / 2 + 1.0, FLOOR + 3.62, 1.0)
    tb(mi, F, 1.0, -idp / 2 + 0.12, FLOOR + 4.6, 6.4, 0.24, 3.4, W_STR, 0.03)
    for j, u in enumerate((-2.4, -1.2, 0.0, 1.2, 2.4)):
        x = 1.0 + u
        rod(mi, F, (x, -idp / 2 + 0.3, FLOOR + 7.4), (x, -idp / 2 + 0.3, FLOOR + 5.2 + 0.4 * (j % 2)), 0.1, W_MID, 4)
        tb(ms, F, x, -idp / 2 + 0.3, FLOOR + 5.0 + 0.4 * (j % 2), 0.9 if j % 2 else 0.5, 0.2, 0.4, IRON, 0.02)
    lantern(mi, F, -iw / 4 - 0.5, -3.0, zc - 1.0, 5.0)
    xr = iw / 2 - 0.2
    tb(mi, F, xr, -4.6, FLOOR + 6.2, 0.3, 5.0, 0.5, W_STR, 0.04)
    for j, yy in enumerate((-6.2, -3.2)):
        pickaxe(mi, F, xr - 0.45, yy, FLOOR + 6.4, big=(j % 2 == 0))
    ore_cart(mi, F, 6.0, 1.0)
    lcol(area, F, 6.0, 1.0, 0.0, 3.2, 5.0, 3.4)
    for (cx, cy) in ((-5.5, 5.0), (-3.2, 5.6)):
        barrel(mi, F, cx, cy)
    crate(mi, F, 8.8, -3.4, s=2.2)
    crate(mi, F, 8.8, -3.4, z0=FLOOR + 2.2, s=1.8, yaw=0.3)
    S = Sub(iw / 2, 3.5, math.pi / 2)
    wall_shelf(mi, F, S, 0.0, 0.0, FLOOR + 6.0, 3.6, items="pots")
    S = Sub(-iw / 2 + 0.13, 8.5, -math.pi / 2)
    peg_rail(mi, F, S, 0.0, 0.0, FLOOR + 7.2, 3.0, capes=(M_NAVY,))
    rug(mi, F, 0.0, 5.0, 5.0, 3.4, m=M_WINE, border=M_NAVY)


# ------------------------------------------------------------------ H6 CASA DA GUARDA (terrea)
def furnish_guard(mi, F, ctx, spec, info):
    area, iw, idp, zc = ctx["area"], ctx["iw"], ctx["idp"], ctx["zc"]
    ms = mx()
    # cama em ALCOVA (tabique de madeira + cortina), mesa com 2 bancos, armeiro de lancas, escudos, bau, prateleira
    bed(mi, F, 8.0, -3.4, 0.0, cover=M_WINE)
    lcol(area, F, 8.0, -3.4, 0.0, 5.2, 9.0, 2.2)
    tb(mi, F, 5.0, -3.8, FLOOR, 0.4, 8.4, 8.0, W_STR, 0.04)
    tb(mi, F, 7.9, 0.5, FLOOR + 7.6, 6.2, 0.4, 0.4, W_STR, 0.03)
    tb(mi, F, 5.8, 0.55, FLOOR + 0.4, 1.1, 0.2, 7.2, M_NAVY, 0.05)
    lcol(area, F, 5.0, -3.8, 0.0, 0.4, 8.4, 8.0)
    table(mi, F, 1.4, 0.4, 6.0, 3.0, 3.4)
    lcol(area, F, 1.4, 0.4, 0.0, 6.0, 3.0, 3.4)
    bench(mi, F, 1.4, -1.9, 5.0)
    bench(mi, F, 1.4, 2.7, 5.0)
    candle(mi, F, 1.4, 0.4, FLOOR + 3.4, 1.2)
    mug(mi, F, 2.6, -0.4, FLOOR + 3.4)
    book(mi, F, 0.2, 0.9, FLOOR + 3.4, 0.3, open_=True, m=M_NAVY)
    # armeiro de lancas na parede da frente (lado esquerdo da porta): 2 ruas, 4 hastes com ponta de ferro
    yr = idp / 2 - 0.35
    tb(mi, F, -7.2, yr, FLOOR + 1.0, 4.4, 0.4, 0.4, W_STR, 0.03)
    tb(mi, F, -7.2, yr, FLOOR + 6.4, 4.4, 0.4, 0.4, W_STR, 0.03)
    for j, xx in enumerate((-8.8, -7.7, -6.6, -5.5)):
        rod(mi, F, (xx, yr - 0.2, FLOOR + 0.6), (xx, yr - 0.2, FLOOR + 9.4), 0.1, W_MID, 4)
        p = F.p(xx, yr - 0.2, FLOOR + 9.4)
        V._lathe(ms, (p.x, p.y, p.z), [(0.18, 0.0), (0.2, 0.2), (0.0, 1.0)], IRON, 4)
    for j, yy in enumerate((-5.2, 6.0)):
        p = F.p(-iw / 2 + 0.4, yy, FLOOR + 6.4)
        mi.cyl(1.2, 0.3, (p.x, p.y, p.z), (0, math.pi / 2, F.a), (M_NAVY, M_WINE)[j], n=10, bevel=0.05)
        ms.cyl(0.35, 0.36, (p.x, p.y, p.z), (0, math.pi / 2, F.a), IRON, n=8, bevel=0.03)
        ms.cyl(1.22, 0.12, (p.x, p.y, p.z), (0, math.pi / 2, F.a), IRON, n=10, r2=1.0, bevel=0.0)
    chest(mi, F, -2.5, -idp / 2 + 1.2, 0.0, 3.2, 1.8, 2.0)
    shelf(mi, F, iw / 2 - 0.8, 4.2, math.pi / 2, 4.2, 6.5, 1.4, items="pots")
    # ganchos com capas da guarda junto a porta (direita), quadro de avisos e chaves na esquerda
    S = Sub(1.5, -idp / 2 + 0.13, 0.0)
    peg_rail(mi, F, S, 0.0, 0.0, FLOOR + 7.0, 2.6, capes=(M_NAVY, M_NAVY))
    S = Sub(-iw / 2, -6.5, -math.pi / 2)
    sbox(mi, F, S, 0, 0.08, FLOOR + 5.2, 3.0, 0.16, 2.4, W_MID, 0.03)
    for j in range(3):
        sbox(mi, F, S, -0.8 + 0.8 * j, 0.2, FLOOR + 5.6 + 0.4 * (j % 2), 0.6, 0.06, 0.9, M_LIN, 0.0)
    rod(mi, F, (-iw / 2, -9.3, FLOOR + 6.4), (-iw / 2 + 0.6, -9.3, FLOOR + 6.4), 0.08, W_MID, 4)
    rod(ms, F, (-iw / 2 + 0.5, -9.3, FLOOR + 6.3), (-iw / 2 + 0.5, -9.3, FLOOR + 5.4), 0.12, IRON, 4)
    barrel(mi, F, -8.5, 7.5, r=1.0, h=2.5)


def pickaxe(mi, F, x, y, z, big=True):
    """picareta pendurada pela cabeca: cabo de madeira para baixo, cabeca de ferro curva em 2 pontas"""
    ms = mx()
    ln = 4.2 if big else 3.4
    rod(mi, F, (x, y, z), (x, y, z - ln), 0.14, W_MID, 6)
    a = F.p(x, y - 1.3, z - 0.25)
    b = F.p(x, y + 1.3, z - 0.25)
    c = F.p(x, y, z + 0.1)
    ms.beam(a, c, 0.24, 0.3, IRON, 0.0)
    ms.beam(c, b, 0.24, 0.3, IRON, 0.0)
    tb(ms, F, x, y, z - 0.25, 0.42, 0.5, 0.5, IRON, 0.04)


def ore_cart(mi, F, cx, cy):
    """carrinho de mina de madeira com cintas de ferro, 4 rodas com aro, puxador, carga coberta por LONA (sem
    minerio a vista) sobre 2 trilhos e dormentes"""
    ms = mx()
    for yy in (-2.8, -1.4, 0.0, 1.4, 2.8):
        tb(mi, F, cx, cy + yy, FLOOR, 3.6, 0.6, 0.2, W_STR, 0.03)
    for s in (-1, 1):
        tb(ms, F, cx + s * 1.0, cy, FLOOR + 0.2, 0.24, 7.0, 0.22, IRON, 0.02)
    zb = FLOOR + 1.3
    tb(mi, F, cx, cy, zb, 2.8, 4.4, 0.25, W_MID, 0.04)
    for s in (-1, 1):
        tb(mi, F, cx + s * 1.3, cy, zb + 0.25, 0.25, 4.4, 1.8, W_MID, 0.04)
        tb(mi, F, cx, cy + s * 2.1, zb + 0.25, 2.8, 0.25, 1.8, W_MID, 0.04)
        for yy in (-1.3, 1.3):
            tb(ms, F, cx + s * 1.44, cy + yy, zb + 0.1, 0.06, 0.3, 2.0, IRON, 0.0)
    tb(mi, F, cx, cy, zb + 1.9, 2.7, 4.3, 0.5, M_NAVY, 0.25)                       # lona
    for sx in (-1, 1):
        for sy in (-1, 1):
            p = F.p(cx + sx * 1.0, cy + sy * 1.4, FLOOR + 0.42 + 0.72)
            ms.cyl(0.72, 0.26, (p.x, p.y, p.z), (0, math.pi / 2, F.a), IRON, n=10, bevel=0.03)
            mi.cyl(0.3, 0.34, (p.x, p.y, p.z), (0, math.pi / 2, F.a), W_MID, n=6, bevel=0.0)
    bm_(ms, F, (cx, cy + 2.2, zb + 0.9), (cx, cy + 3.4, zb + 1.2), 0.2, 0.2, IRON)


def lantern(mi, F, x, y, ztop, drop):
    """lanterna de oficina pendurada: corrente, tampa, gaiola de ferro de 4 montantes e o nucleo quente"""
    ms = mx()
    p = F.p(x, y, ztop)
    zb = ztop - drop
    ms.rod((p.x, p.y, ztop), (p.x, p.y, zb + 1.3), 0.05, IRON, 4)
    V._lathe(ms, (p.x, p.y, zb + 1.0), [(0.62, 0.0), (0.2, 0.3), (0.0, 0.34)], IRON, 6)
    for k in range(4):
        a = math.pi / 4 + k * math.pi / 2
        ms.box((0.1, 0.1, 1.0), (p.x + 0.45 * math.cos(a), p.y + 0.45 * math.sin(a), zb + 0.5), (0, 0, a), IRON, 0.0)
    ms.box((0.9, 0.9, 0.14), (p.x, p.y, zb + 0.07), (0, 0, F.a), IRON, 0.02)
    V._lathe(ms, (p.x, p.y, zb + 0.14), [(0.22, 0.0), (0.26, 0.4), (0.0, 0.72)], M_GLOW, 6)
