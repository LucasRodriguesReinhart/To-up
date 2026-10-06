# sg_village - VILA da Ilha 3 (Shadow Garden), PLANTA v4 (onda 1, agente 1e, 2026-09-30).
# Pedido do usuario: "aumente a proporcao das casas para elas terem mais impacto no ambiente" e "modele as casas por
# dentro para deixar elas funcionais e acessiveis".
#   - 7 CASAS VISITAVEIS (sg_layout.HOUSES): A 32 x 24 com 2 andares, B taverna 38 x 28, C terrea 24 x 18. O EXTERIOR e o
#     KIT APROVADO do overhaul 02 (soco em fiadas, terreo de cantaria com cunhais, enxaimel, janela com recuo e pinazios,
#     ardosia em fiadas com escama, cumeeira em pecas, aguas-furtadas, chamines, torreao numa casa, loja) construido no
#     referencial do kit e levado a ESCALA 2 (K) por uma transformacao por primitiva (MB._post com _xf): a casa inteira
#     dobra de tamanho sem redesenhar o kit (o avatar de 5 fica na proporcao da porta de 8 x 11).
#   - PAREDE OCA: casca externa de 0,5 (nucleo/reboco) + forro interno de 0,5 (reboco, sg_village_int) = a parede de 1
#     da colisao da onda 0. Vaos de VERDADE na casca (porta, janelas, bandeira da loja, sotao): a luz do comodo fica
#     RECUADA 0,30-0,36 atras da face (REGRA do brief: nada aceso a menos de 0,12 da face ou do vidro), e de dentro o vao
#     mostra os postigos fechados.
#   - PORTA ABERTA: vao livre de 8 x 11 no meio da frente, soleira baixa (0,12 acima do piso e da rua), cantaria com
#     verga e fecho (terreo de pedra) ou portal de madeira com misulas em ogiva (terreo de enxaimel); as 2 folhas ficam
#     abertas, encostadas na parede de dentro (sg_village_int).
#   - O INTERIOR (piso, forro de parede, escada, moveis, lareira) e do sg_village_int (um objeto SG_Vil_Int_<casa> por
#     casa, para o cliente esconder de longe).
# Ruas e praca: lajes com JUNTA VISIVEL (leito escuro 0,6 abaixo do topo), 2 tons por fiada, meio-fio chanfrado; o
# topo do calcamento fica 0,30 ACIMA do patamar (familia F5 do z-fight: piso sobre o terreno >= 0,3, com colisao
# propria no topo) e a fonte e a da v3 (pedra estanque; a agua e do Roblox pelos WATER_Fountain_* do sg_core, cotas
# iguais). Floreiras de janela e canteiros de pedra vazios na frente das casas (a grama/flor e da onda 2).
# (Historico da v3 - praca, fonte, overhaul 01/02, acabamento - em git: sg_village.py ate o commit 1b334fb.)
import math, random
import bmesh
from mathutils import Vector, Matrix
import sg_lib as SL
from sg_lib import MB, col_box, Frame, light, octo_col, fm_lib
import sg_layout as L
import sg_emblem as EM
import sg_core as CORE

P1, P2, P3 = L.P1, L.P2, L.P3
COLL = "05_VILLAGE"
# FINESSE 3 (03.12): a vila NAO usa mais o Window_Warm (painel inteiro laranja): vidro escuro proprio + faixa acesa.
M_PANE = "Glass_SGVilPane"      # vidraca escura neutra (Glass no Roblox): transom e janelas apagadas
fm_lib.MATS.setdefault(M_PANE, (fm_lib.S(34, 38, 52), 0.12, 0.0, 0, None, 0.0))
WIN = M_PANE
WOOD = "Wood_SG_Dark"
STONE = "Stone_SG_Block"
TRIM = "Stone_SG_Trim"
ROOF = "Roof_SG_Slate"
# FINESSE 3 (03.16): 2a ardosia (um valor acima, mais fria) dirigida por casa; cumeeira em obsidiana (telha escura)
ROOF_B = "Roof_SGVilSlateB"
fm_lib.MATS.setdefault(ROOF_B, (fm_lib.S(52, 58, 76), 0.75, 0.0, 0, None, 0.08))
IRON = "Metal_SG_Iron"
M_PL = "Plaster_SGVil"          # reboco apagado (frio-quente, escuro)
M_COB = "Stone_SGVilCobble"     # calcamento escuro (tom B das lajes)
M_SHUT = "Wood_SGVilNavy"       # persianas / postigos pintados de navy
fm_lib.MATS.setdefault(M_PL, (fm_lib.S(96, 88, 88), 0.8, 0.0, 0, None, 0.06))
fm_lib.MATS.setdefault(M_COB, (fm_lib.S(72, 76, 92), 0.9, 0.0, 0, None, 0.10))
fm_lib.MATS.setdefault(M_SHUT, (fm_lib.S(36, 42, 72), 0.75, 0.0, 0, None, 0.05))
M_BLOOM = "Leaf_SGPropBloom"
fm_lib.MATS.setdefault(M_BLOOM, (fm_lib.S(98, 66, 132), 0.85, 0.0, 0, None, 0.08))
OBS = "Stone_SG_Obsidian"
BIRON = "Metal_SG_BlackIron"
M_ROOM = "SG_VilRoom_Glow"      # luz do comodo: Neon MEDIO-ESCURO quente (03.12: um valor abaixo, menos saturado)
fm_lib.MATS.setdefault(M_ROOM, (fm_lib.S(150, 92, 48), 0.5, 0.0, 1.05, fm_lib.S(150, 92, 48), 0.0))
M_CURT = "Cloth_SG_Navy"        # cortina / bando / persiana de pano
M_DIRT = "Dirt_SG"              # terra (canteiros)
M_JNT = "Stone_SG_Floor"        # nucleo escuro que so aparece nas juntas
M_ASH = "Stone_SG_Castle_B"     # silhar do terreo de pedra
M_DRESS = "Stone_SG_Block_B"    # cunhais, soco, ombreiras, chamines
M_CAP = "Stone_SG_TrimLow"      # remates perto do jogador
fm_lib.MATS.setdefault(M_CAP, (fm_lib.S(132, 128, 134), 0.8, 0.0, 0, None, 0.06))
M_POT = "Roof_Red"              # pote ceramico da chamine
B_PROP = 0.05
B_CAST = 0.03

# ------------------------------------------------------------------ escala do kit e parede oca (unidades do KIT)
K = 2.0                          # o kit aprovado x2: porta 8 x 11 = 4 x 5,5 do kit, pe-direito 12 = 6
T_EXT = 0.25                     # casca externa (0,5)
T_LIN = 0.25                     # forro interno (0,5) - desenhado pelo sg_village_int
ZC0 = 1.0                        # o corpo nasce sobre o soco (2,0 acima da rua)
FLOOR_K = 0.15                   # piso interno a 0,30 acima do patamar (= topo das lajes da rua)
DW, DH = 4.0, 5.5                # vao da porta (kit) = 8 x 11
GLOW_OFF, GLOW_T = -0.2, 0.03    # luz do comodo: -0,43..-0,37 atras da face (03.12: Neon recuado 0,4)
PANE_OFF, PANE_T = -0.03, 0.02   # vidraca escura logo atras da grade de pinazios
CURT_OFF, CURT_T = -0.09, 0.03   # cortina/persiana: -0,21..-0,15 (entre o vidro e a luz)
PAVE = 0.30                      # topo das lajes/soleiras acima do patamar (F5)

# ------------------------------------------------------------------ transformacao por primitiva (kit -> mundo)
if not hasattr(MB, "_post_orig"):
    MB._post_orig = MB._post

    def _post_xf(self, verts, m, tint, bevel, seg, angle=0.5):
        xf = self.__dict__.get("_xf")
        if xf is not None:
            M, k = xf
            for v in verts:
                if v.is_valid:
                    v.co = M @ v.co
            if bevel:
                bevel = bevel * k
        return MB._post_orig(self, verts, m, tint, bevel, seg, angle)
    MB._post = _post_xf


class KitXF:
    """contexto: as primitivas desenhadas no referencial do kit (origem 0, unidades do kit) nos MB dados saem no mundo:
    T(lote) . Rz(rumo do lote) . S(K)"""

    def __init__(self, mbs, F):
        self.mbs = [m for m in mbs if m is not None]
        self.M = Matrix.Translation(Vector(F.o)) @ Matrix.Rotation(F.a, 4, "Z") @ Matrix.Scale(K, 4)

    def __enter__(self):
        for m in self.mbs:
            m._xf = (self.M, K)
        return self

    def __exit__(self, *a):
        for m in self.mbs:
            m._xf = None


def lot_frame(hrec):
    nm, tp, x, y, w, d, deg, z = hrec
    return Frame(x, y, z, math.radians(deg) - math.pi / 2)     # local +Y = frente (a mesma da onda 0)


# ------------------------------------------------------------------ cameras (v4)
CAMS = {
    # rua da vila na altura do jogador (IMPACTO das casas) e visao geral
    "CAM_SGVil_Street_P1W": ((-22.0, -218.0, P1 + 5.5), (-112.0, -226.0, P1 + 13.0), 20),
    "CAM_SGVil_Street_P1E": ((24.0, -226.0, P1 + 5.5), (112.0, -220.0, P1 + 13.0), 20),
    "CAM_SGVil_Street_P2": ((-8.0, -88.0, P2 + 5.5), (-110.0, -84.0, P2 + 14.0), 20),
    "CAM_SGVil_Overview": ((70.0, -318.0, P1 + 62.0), (-10.0, -190.0, P1 + 6.0), 20),
    # cada tipo por fora
    "CAM_SGVil_Ext_B": ((-56.0, -212.0, P1 + 6.0), (-92.0, -262.0, P1 + 16.0), 20),
    "CAM_SGVil_Ext_A": ((66.0, -210.0, P1 + 6.0), (96.0, -258.0, P1 + 16.0), 20),
    "CAM_SGVil_Ext_C": ((76.0, -226.0, P1 + 6.0), (104.0, -180.0, P1 + 11.0), 20),
    "CAM_SGVil_Ext_A2": ((-20.0, -76.0, P2 + 6.0), (-66.0, -114.0, P2 + 14.0), 20),
    # entrando pela porta (H2, ferreiro) e interiores
    "CAM_SGVil_Door": ((-100.0, -210.0, P1 + 5.5), (-100.0, -184.0, P1 + 5.0), 22),
    "CAM_SGVil_Int_Sala": ((-108.0, -189.5, P1 + 6.2), (-86.5, -181.0, P1 + 4.0), 16),
    "CAM_SGVil_Int_Escada": ((-91.0, -186.0, P1 + 6.5), (-108.0, -172.0, P1 + 9.0), 16),
    "CAM_SGVil_Int_Quarto": ((-89.0, -176.0, P1 + 18.6), (-111.0, -186.5, P1 + 15.0), 16),
    "CAM_SGVil_Int_Taverna": ((-78.0, -251.0, P1 + 6.2), (-100.0, -262.0, P1 + 8.0), 15),
    "CAM_SGVil_Int_Mezanino": ((-79.0, -255.0, P1 + 20.5), (-101.0, -260.0, P1 + 12.0), 15),
    "CAM_SGVil_Int_Oficina": ((110.5, -187.0, P1 + 6.8), (97.0, -176.0, P1 + 3.0), 15),
    # praca com a fonte
    "CAM_SGVil_Praca": ((16.0, -246.0, P1 + 5.5), (0.0, -222.0, P1 + 5.0), 22),
    # FINESSE 3: as cameras da AUDITORIA 3 que o studio nao cria (sg_scene.a3_cams nao entra no build), olho a 5,5
    "CAM_A3_02_Fonte_CU": ((10.0, -237.0, P1 + 5.5), (0.0, -222.0, P1 + 5.0), 20),
    "CAM_A3_02_Praca_Piso": ((-17.0, -210.0, P1 + 5.5), (-2.0, -232.0, P1), 22),
    "CAM_A3_02_Praca_Chegada": ((0.0, -262.0, P1 + 5.5), (0.0, -222.0, P1 + 6.0), 20),
    "CAM_A3_02_Praca_Alta": ((44.0, -284.0, P1 + 42.0), (0.0, -222.0, P1), 22),
    "CAM_A3_03_RuaP1_W": ((-30.0, -222.0, P1 + 5.5), (-150.0, -222.0, P1 + 8.0), 20),
    "CAM_A3_03_RuaP1_E": ((30.0, -222.0, P1 + 5.5), (150.0, -222.0, P1 + 8.0), 20),
    "CAM_A3_03_RuaP2_W": ((-10.0, -86.0, P2 + 5.5), (-160.0, -86.0, P2 + 8.0), 20),
    "CAM_A3_03_EixoP2": ((0.0, -140.0, P2 + 5.5), (0.0, -40.0, P3 + 20.0), 20),
    "CAM_A3_03_Vila_Media": ((70.0, -310.0, P1 + 55.0), (-30.0, -170.0, P1), 20),
    "CAM_A3_14_Oeste": ((-820.0, 20.0, 220.0), (0.0, 20.0, 80.0), 24),
}


def _a3_house_cams():
    """as cameras CAM_A3_03_<casa>_Frente / _Lado da auditoria (mesma formula do sg_scene._house_cams)"""
    out = {}
    for nm, tp, x, y, w, d, deg, z in L.HOUSES:
        a = math.radians(deg) - math.pi / 2

        def P(u, v, h, x=x, y=y, z=z, a=a):
            return (x + u * math.cos(a) - v * math.sin(a), y + u * math.sin(a) + v * math.cos(a), z + h)
        out["CAM_A3_03_%s_Frente" % nm] = (P(w * 0.45, d / 2 + 20.0, 5.5), P(-2.0, 0.0, 9.0), 20)
        out["CAM_A3_03_%s_Lado" % nm] = (P(-w / 2 - 16.0, d / 2 + 8.0, 5.5), P(0.0, -2.0, 8.0), 20)
    return out


CAMS.update(_a3_house_cams())

# rotas extras: as ruas e a praca livres (as rotas das 7 casas - porta e escada - sao do sg_qa.house_routes)
EXTRA_ROUTES = {
    "VIL_RUA_P1_OESTE": ([(-30.0, -222.0), (-100.0, -222.0), (-160.0, -222.0)], P1),
    "VIL_RUA_P1_LESTE": ([(30.0, -222.0), (96.0, -222.0), (150.0, -222.0)], P1),
    "VIL_RUA_P2": ([(-165.0, -86.0), (-100.0, -86.0), (-40.0, -86.0), (0.0, -86.0), (60.0, -86.0), (93.0, -86.0)], P2),
    "VIL_PRACA_ANEL": ([(L.PLAZA_C[0] + 13.0 * math.cos(math.radians(a)), L.PLAZA_C[1] + 13.0 * math.sin(math.radians(a)))
                        for a in range(-90, 271, 45)], P1),
}
EXTRA_PROBES = []


# ------------------------------------------------------------------ utilidades
def ring_prism(mb, c, r0, r1, n, z0, z1, m, rot0=0.0):
    """anel poligonal (n lados, vertices em rot0 + k*360/n) de r0 a r1, de z0 a z1"""
    bm = mb.bm
    cx, cy = c
    ang = [math.radians(rot0) + 2 * math.pi * k / n for k in range(n)]
    ob = [bm.verts.new((cx + r1 * math.cos(a), cy + r1 * math.sin(a), z0)) for a in ang]
    ot = [bm.verts.new((cx + r1 * math.cos(a), cy + r1 * math.sin(a), z1)) for a in ang]
    ib = [bm.verts.new((cx + r0 * math.cos(a), cy + r0 * math.sin(a), z0)) for a in ang]
    it = [bm.verts.new((cx + r0 * math.cos(a), cy + r0 * math.sin(a), z1)) for a in ang]
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((ob[i], ob[j], ot[j], ot[i]))
        bm.faces.new((it[i], it[j], ib[j], ib[i]))
        bm.faces.new((ot[i], ot[j], it[j], it[i]))
        bm.faces.new((ib[i], ib[j], ob[j], ob[i]))
    mb._post(ob + ot + ib + it, m, None, 0, 1)


def ngon(c, r, n, rot0=0.0):
    return [(c[0] + r * math.cos(math.radians(rot0) + 2 * math.pi * k / n),
             c[1] + r * math.sin(math.radians(rot0) + 2 * math.pi * k / n)) for k in range(n)]


def tri_slab(mb, pts, nvec, th, m):
    """triangulo (3 pontos no plano de fora) extrudado para dentro (-nvec) com espessura th"""
    bm = mb.bm
    a = [bm.verts.new(Vector(p)) for p in pts]
    b = [bm.verts.new(Vector(p) - nvec * th) for p in pts]
    bm.faces.new(a)
    bm.faces.new(list(reversed(b)))
    for i in range(3):
        j = (i + 1) % 3
        bm.faces.new((a[j], a[i], b[i], b[j]))
    mb._post(a + b, m, None, 0, 1)


def poly_slab(mb, pts2, plane, th, m):
    """poligono 2D (u, v) num plano vertical: plane = (origem, eixo_u, eixo_v, normal); extruda -normal"""
    o, eu, ev, nv = plane
    bm = mb.bm
    a = [bm.verts.new(o + eu * u + ev * v) for u, v in pts2]
    b = [bm.verts.new(o + eu * u + ev * v - nv * th) for u, v in pts2]
    bm.faces.new(a)
    bm.faces.new(list(reversed(b)))
    n = len(pts2)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((a[j], a[i], b[i], b[j]))
    mb._post(a + b, m, None, 0, 1)


class Face:
    """face de parede no referencial G: centro c (2D local), tangente u, normal n = rot90(u) para fora"""

    def __init__(self, G, c, u, length):
        self.G, self.c, self.u, self.L = G, c, u, length
        self.n = (-u[1], u[0])
        self.yaw = G.a + math.atan2(u[1], u[0])

    def P(self, s, off, z):
        c, u, n = self.c, self.u, self.n
        return self.G.p(c[0] + u[0] * s + n[0] * off, c[1] + u[1] * s + n[1] * off, z)

    def box(self, mb, s, off, z, sx, sy, sz, m, rx=0.0, ry=0.0, bevel=0.0):
        mb.box((sx, sy, sz), self.P(s, off, z), (rx, ry, self.yaw), m, bevel)

    def beam(self, mb, s0, z0, s1, z1, off, w, h, m=WOOD):
        mb.beam(self.P(s0, off, z0), self.P(s1, off, z1), w, h, m, 0.0)

    def nvec(self):
        a = self.G.a
        nx, ny = self.n
        return Vector((nx * math.cos(a) - ny * math.sin(a), nx * math.sin(a) + ny * math.cos(a), 0.0))

    def uvec(self):
        return Vector((math.cos(self.yaw), math.sin(self.yaw), 0.0))

    def s_of(self, gx, gy):
        """coordenada s (ao longo da face) do ponto (gx, gy) do referencial G (sem o giro de G)"""
        return (gx - self.c[0]) * self.u[0] + (gy - self.c[1]) * self.u[1]


def _merge_cols(cols):
    out = []
    for a, b, segs in cols:
        if out and out[-1][2] == segs and abs(out[-1][1] - a) < 1e-6:
            out[-1] = (out[-1][0], b, segs)
        else:
            out.append((a, b, segs))
    return out


def slab_holes(mb, f, s0, s1, z0, z1, off0, off1, holes, m):
    """placa de parede na face f (s0..s1, z0..z1, espessura off0..off1) com VAOS retangulares [(a, b, za, zb)]:
    colunas pelas bordas dos vaos; em cada coluna, as faixas livres em z (colunas iguais vizinhas se fundem)"""
    hs = [(max(a, s0), min(b, s1), max(za, z0), min(zb, z1)) for a, b, za, zb in holes
          if b > s0 + 1e-4 and a < s1 - 1e-4 and zb > z0 + 1e-4 and za < z1 - 1e-4]
    xs = sorted(set([s0, s1] + [v for a, b, _, _ in hs for v in (a, b)]))
    cols = []
    for a, b in zip(xs, xs[1:]):
        if b - a < 1e-4:
            continue
        mid = (a + b) / 2
        cut = sorted((za, zb) for ha, hb, za, zb in hs if ha < mid < hb)
        zz, segs = z0, []
        for za, zb in cut:
            if za > zz + 1e-4:
                segs.append((zz, za))
            zz = max(zz, zb)
        if z1 > zz + 1e-4:
            segs.append((zz, z1))
        cols.append((a, b, tuple(segs)))
    oc, th = (off0 + off1) / 2, off1 - off0
    for a, b, segs in _merge_cols(cols):
        for za, zb in segs:
            f.box(mb, (a + b) / 2, oc, (za + zb) / 2, b - a, th, zb - za, m)


def poly_holes(mb, f, poly, off0, off1, holes, m):
    """poligono (s, z) no plano da face (empena), espessura off0..off1, menos vaos retangulares [(a, b, za, zb)]"""
    s_min, s_max = min(p[0] for p in poly), max(p[0] for p in poly)
    xs = sorted(set([s_min, s_max] + [v for a, b, _, _ in holes for v in (a, b) if s_min < v < s_max]))
    nv = f.nvec()
    plane = (f.P(0.0, off1, 0.0), f.uvec(), Vector((0.0, 0.0, 1.0)), nv)
    for a, b in zip(xs, xs[1:]):
        if b - a < 1e-4:
            continue
        col = SL.clip(SL.clip(poly, 1.0, 0.0, b), -1.0, 0.0, -a)
        if len(col) < 3:
            continue
        mid = (a + b) / 2
        cut = sorted((za, zb) for ha, hb, za, zb in holes if ha < mid < hb)
        bands, zz = [], -1e9
        for za, zb in cut:
            bands.append((zz, za))
            zz = zb
        bands.append((zz, 1e9))
        for za, zb in bands:
            pc = SL.clip(SL.clip(col, 0.0, 1.0, zb), 0.0, -1.0, -za)
            if len(pc) >= 3 and abs(SL.area(pc)) > 1e-3:
                poly_slab(mb, pc, plane, off1 - off0, m)


def ring_rect(mb, G, outer, inner, z0, z1, m, bevel=0.0):
    """moldura retangular (4 caixas) entre o retangulo externo e o interno (x0, x1, y0, y1), de z0 a z1"""
    ox0, ox1, oy0, oy1 = outer
    ix0, ix1, iy0, iy1 = inner
    zc, h = (z0 + z1) / 2, z1 - z0
    for (a0, a1, b0, b1) in ((ox0, ox1, iy1, oy1), (ox0, ox1, oy0, iy0), (ox0, ix0, iy0, iy1), (ix1, ox1, iy0, iy1)):
        if a1 - a0 > 1e-3 and b1 - b0 > 1e-3:
            mb.box((a1 - a0, b1 - b0, h), G.p((a0 + a1) / 2, (b0 + b1) / 2, zc), G.r(), m, bevel)


def band_face(mb, f, off0, off1, z0, z1, m, ext=0.0, gaps=(), bevel=0.0):
    """faixa ao longo da face (s de -L/2-ext a L/2+ext) menos as lacunas [(s0, s1)] (porta)"""
    cuts = [(-f.L / 2 - ext, f.L / 2 + ext)]
    for g0, g1 in gaps:
        nc = []
        for a, b in cuts:
            if g1 <= a or g0 >= b:
                nc.append((a, b))
                continue
            if g0 > a + 0.05:
                nc.append((a, g0))
            if b > g1 + 0.05:
                nc.append((g1, b))
        cuts = nc
    for a, b in cuts:
        f.box(mb, (a + b) / 2, (off0 + off1) / 2, (z0 + z1) / 2, b - a, off1 - off0, z1 - z0, m, bevel=bevel)


# ------------------------------------------------------------------ kit: remates, janela, loja, lanterna
def _lathe(mb, c, prof, m, n=8, rot=0.0, closed=False, caps=(True, True)):
    EM._lathe(mb, c, prof, m, n, rot, closed, caps)


def finial_iron(mb, p, s=1.0, m=IRON):
    prof = [(0.26, 0.0), (0.1, 0.22), (0.1, 0.8), (0.22, 1.0), (0.08, 1.25), (0.0, 2.1)]
    _lathe(mb, tuple(p), [(r * s, h * s) for r, h in prof], m, 6, 0.0, caps=(False, True))


def finial_wood(mb, p, s=1.0):
    prof = [(0.0, -1.3), (0.2, -0.9), (0.15, -0.45), (0.27, -0.2), (0.27, 0.4), (0.2, 0.62), (0.22, 0.95),
            (0.0, 1.45)]
    _lathe(mb, tuple(p), [(r * s, h * s) for r, h in prof], WOOD, 6, math.pi / 6)


def _hood(mb, f, s, z, w):
    """capelo de ardosia sobre a janela (telhadinho de 1 agua em 2 maos-francesas)"""
    t = math.radians(24.0)
    f.box(mb, s, 0.62, z + 0.32, w + 1.1, 1.05, 0.18, ROOF, rx=-t)
    f.box(mb, s, 0.1, z + 0.52, w + 1.0, 0.2, 0.3, WOOD)
    for k in (-1, 1):
        sb = s + k * (w / 2 + 0.44)
        mb.beam(f.P(sb, 0.06, z - 0.42), f.P(sb, 0.86, z + 0.2), 0.14, 0.14, WOOD, 0.0)


LIFE = [None]                  # MB de vestir das casas (lanternas de suporte, caixas de janela)
GARDEN_HOUSE = [0]             # tema das floreiras (sg_garden.BOX_THEME) da casa que esta sendo montada


def window_box(mb, f, s, zlo, w):
    """caixa de janela de madeira com rebordo em 2 maos-francesas de ferro + o plantio do kit do sg_garden"""
    mb = LIFE[0] or mb
    zb = zlo - 0.72
    f.box(mb, s, 0.72, zb, w + 0.4, 0.56, 0.42, WOOD)
    f.box(mb, s, 0.74, zb + 0.24, w + 0.56, 0.66, 0.09, WOOD)
    for k in (-1, 1):
        mb.beam(f.P(s + k * (w / 2 - 0.1), 0.05, zb - 0.9), f.P(s + k * (w / 2 - 0.1), 0.86, zb - 0.28), 0.1, 0.1,
                IRON, 0.0)
    # (vazia: o plantio e da onda 2 / sg_garden.window_box_planting)


def window(mb, f, s, zlo, w, h, head="hood", shutters=False, planter=False, style="cross", dress="open",
           stone=False, lod=0, back=False):
    """janela do kit com o vao VAZADO na casca (quem chama abre o vao s-w/2..s+w/2, zlo..zlo+h):
      - comodo aceso (2/3 de baixo, Neon medio) e vidro ambar (1/3 de cima) RECUADOS 0,30-0,36 atras da face;
      - cortina/persiana entre a face e a luz (0,12 de cada lado); grade de pinazios no plano da face;
      - moldura de madeira (caixilho de 0,42) ou ombreiras de pedra (stone=True) + peitoril com pingadeira + cabeca;
      - back=True: fundo de tabuas navy atras da luz (vao de sotao, sem forro interno)."""
    zc = zlo + h / 2
    D = 0.42
    zs = zlo + h * 0.64
    # FINESSE 3 (03.12): o painel inteiro NAO acende mais. A bandeira de cima (1/3) e vidro escuro; embaixo, a luz do
    # comodo (Neon medio-escuro) fica RECUADA 0,4 numa FAIXA entre as cortinas ('curtain'), no vao todo menos as
    # ombreiras ('open') ou NAO acende ('blind': vidraca escura + persiana = janela apagada, ritmo dirigido por casa).
    lit = dress in ("open", "curtain")
    if lit:
        ws = w * 0.5 if dress == "curtain" else w - 0.5
        f.box(mb, s, GLOW_OFF, (zlo + zs) / 2 + 0.02, ws, GLOW_T, zs - zlo - 0.08, M_ROOM)
        f.box(mb, s, PANE_OFF, (zs + zlo + h) / 2, w, PANE_T, zlo + h - zs, M_PANE)
        if dress == "curtain":
            for k in (-1, 1):
                f.box(mb, s + k * (w / 2 - w * 0.14), CURT_OFF, (zlo + zs) / 2, w * 0.28, CURT_T, zs - zlo, M_CURT)
        elif lod == 0:
            f.box(mb, s, CURT_OFF, zs - 0.16, w, CURT_T, 0.32, M_CURT)                 # bando
    else:
        f.box(mb, s, PANE_OFF, zc, w, PANE_T, h, M_PANE)
        f.box(mb, s, CURT_OFF, zlo + h - h * 0.3, w - 0.1, CURT_T, h * 0.6, M_CURT)    # persiana meio descida
    if back:
        f.box(mb, s, -0.36, zc, w, 0.05, h, M_SHUT)
    if stone:
        for k in (-1, 1):
            f.box(mb, s + k * (w / 2 + 0.18), 0.22, zc + 0.05, 0.36, 0.44, h + 0.3, M_DRESS)
        if lod == 0:
            f.box(mb, s, 0.12, zlo + h + 0.1, w + 0.02, 0.24, 0.2, WOOD)
    else:
        f.box(mb, s, D / 2, zlo + h + 0.16, w + 0.64, D, 0.32, WOOD)
        for k in (-1, 1):
            f.box(mb, s + k * (w / 2 + 0.16), D / 2, zc - 0.05, 0.32, D, h + 0.3, WOOD)
    f.box(mb, s, 0.26, zlo - 0.17, w + 1.0, 0.52, 0.26, M_CAP)
    if style == "trio":
        for k in (-1, 1):
            f.box(mb, s + k * w / 6, 0.0, zc, 0.12, 0.1, h, WOOD)
        f.box(mb, s, 0.0, zs, w, 0.1, 0.12, WOOD)
        if lod == 0:
            f.box(mb, s, 0.0, zlo + h * 0.32, w, 0.08, 0.07, WOOD)
        if head and lod == 0:
            _hood(mb, f, s, zlo + h + 0.32, w)
    else:
        if lod < 2:
            f.box(mb, s, 0.0, zc, 0.1, 0.1, h, WOOD)                         # montante
        f.box(mb, s, 0.0, zs, w, 0.1, 0.12, WOOD)                            # travessa
        if head in ("arch", "hood") and lod == 0:
            _hood(mb, f, s, zlo + h + 0.32, w)
        elif head == "lintel":
            f.box(mb, s, 0.25, zlo + h + (0.5 if lod == 0 else 0.3), w + 1.1, 0.5, 0.5 if lod == 0 else 0.6, M_CAP)
            if lod == 0:
                f.box(mb, s, 0.32, zlo + h + 0.55, 0.5, 0.62, 0.66, M_DRESS)
        elif head == "label":
            f.box(mb, s, 0.25, zlo + h + (0.5 if lod == 0 else 0.3), w + 1.3, 0.5, 0.26 if lod == 0 else 0.6, M_CAP)
            if lod == 0:
                for k in (-1, 1):
                    f.box(mb, s + k * (w / 2 + 0.62), 0.25, zlo + h + 0.1, 0.3, 0.5, 0.6, M_CAP)
    if shutters:
        lw = w * 0.52
        for k in (-1, 1):
            if k > 0 and dress == "blind":
                # 03.12: na janela apagada, uma folha esta MEIO FECHADA (girada 70 graus na dobradica)
                th = math.radians(70.0)
                sh = s + k * (w / 2 + 0.4)
                cs, oc = sh + k * (lw / 2) * math.cos(th), 0.17 + (lw / 2) * math.sin(th)
                mb.box((lw, 0.2, h + 0.1), f.P(cs, oc, zc), (0, 0, f.yaw + k * th), M_SHUT, 0.0)
                mb.box((lw - 0.12, 0.08, 0.26), f.P(cs + 0.14 * math.sin(th) * k, oc - 0.14 * math.cos(th),
                                                     zlo + h * 0.5), (0, 0, f.yaw + k * th), WOOD, 0.0)
                continue
            cs = s + k * (w / 2 + 0.4 + w * 0.26 + 0.08)
            f.box(mb, cs, 0.17, zc, lw, 0.2, h + 0.1, M_SHUT)
            f.box(mb, cs, 0.3, zlo + h * 0.5, lw - 0.12, 0.08, 0.26, WOOD)
    if planter:
        window_box(mb, f, s, zlo, w)


SHOP_Z0, SHOP_Z1 = 2.1, 4.3


def shop_holes(s, w):
    """vao da BANDEIRA acesa da loja (a persiana e fechada: o resto do vao e o fundo escuro da propria casca)"""
    return [(s - w / 2, s + w / 2, SHOP_Z1 + 0.55, SHOP_Z1 + 1.35)]


SHOP_W = 2.0


def shopfront(mb, f, s, w=SHOP_W, awning="slate"):
    """vitrine de loja com persiana FECHADA de ripas (fundo escuro = a casca), balcao de pedra em 3 consolas, bandeira
    acesa RECUADA (vao na casca) com pinazios, toldo de ardosia com testeira recortada e maos-francesas de ferro.
    awning='cloth' (03.08, boticario): toldo de LONA navy esticada em 2 varas de ferro, com a barra da frente em
    madeira e a sanefa recortada"""
    z0, z1 = SHOP_Z0, SHOP_Z1
    n = 6
    ph = (z1 - z0 - 0.08) / n
    for i in range(n):
        f.box(mb, s, 0.18, z0 + 0.04 + ph * (i + 0.5), w - 0.04, 0.12, ph - 0.07, M_SHUT, rx=-0.12)
    f.box(mb, s, 0.26, z0 + 0.06, w, 0.12, 0.12, WOOD)
    f.box(mb, s, 0.3, z0 + 0.3, 0.3, 0.1, 0.16, BIRON)
    f.box(mb, s, 0.5, z0 - 0.12, w + 0.8, 1.0, 0.26, M_CAP)
    for u in (-w / 2 + 0.2, 0.0, w / 2 - 0.2):
        f.box(mb, s + u, 0.34, z0 - 0.42, 0.4, 0.66, 0.34, M_DRESS)
        f.box(mb, s + u, 0.22, z0 - 0.78, 0.32, 0.42, 0.38, M_DRESS)
    f.box(mb, s, 0.1, (z0 - 0.25 + ZC0) / 2, w + 0.3, 0.2, z0 - 0.25 - ZC0, M_DRESS)
    for k in (-1, 1):
        f.box(mb, s + k * (w / 2 + 0.25), 0.22, (z0 - 0.3 + z1 + 0.5) / 2, 0.5, 0.4, z1 - z0 + 0.8, WOOD)
    f.box(mb, s, 0.22, z1 + 0.25, w + 1.0, 0.44, 0.5, WOOD)                    # verga
    f.box(mb, s, GLOW_OFF, z1 + 0.95, w, GLOW_T, 0.8, M_ROOM)                  # bandeira acesa (recuada)
    for k in (-1, 0, 1):
        f.box(mb, s + k * w / 3, 0.0, z1 + 0.95, 0.12, 0.1, 0.8, WOOD)
    f.box(mb, s, 0.2, z1 + 1.45, w + 1.0, 0.36, 0.3, WOOD)
    t = math.radians(28.0)
    W2, dep = w + 1.0, 2.0
    zt0 = z1 + 1.95
    nv = f.nvec()
    ev = Vector((0.0, 0.0, 1.0))
    eu = f.uvec()
    if awning == "cloth":
        t = math.radians(20.0)
        dep = 2.3
        f.box(mb, s, dep / 2 * math.cos(t) + 0.05, zt0 - dep / 2 * math.sin(t), W2 + 0.2, dep, 0.08, M_CURT, rx=-t)
        oe_ = dep * math.cos(t) + 0.05
        ze_ = zt0 - dep * math.sin(t)
        for k in (-1, 1):                                        # varas de ferro (da parede ate a barra)
            sb = s + k * (W2 / 2 - 0.1)
            mb.rod(f.P(sb, 0.08, zt0 + 0.02), f.P(sb, oe_, ze_ + 0.02), 0.05, IRON, 5)
            mb.rod(f.P(sb, oe_ - 0.02, ze_ - 0.02), f.P(sb, 0.1, z1 + 0.6), 0.045, IRON, 5)   # escora caida
        f.box(mb, s, oe_, ze_ - 0.02, W2 + 0.3, 0.14, 0.14, WOOD)                               # barra da frente
        for i in range(5):                                       # sanefa recortada (5 abas)
            f.box(mb, s - W2 / 2 + W2 * (i + 0.5) / 5, oe_ + 0.02, ze_ - 0.3, W2 / 5 - 0.08, 0.05, 0.42, M_CURT)
        return
    f.box(mb, s, dep / 2 * math.cos(t) + 0.05, zt0 - dep / 2 * math.sin(t), W2, dep, 0.2, ROOF, rx=-t)
    ze_ = zt0 - dep * math.sin(t) - 0.08
    oe_ = dep * math.cos(t) + 0.02
    pts = [(-W2 / 2, 0.12), (W2 / 2, 0.12), (W2 / 2, -0.26), (-W2 / 2, -0.26)]
    poly_slab(mb, [(p[0], p[1]) for p in pts], (f.P(s, oe_ + 0.1, ze_), eu, ev, nv), 0.1, WOOD)
    prof = [(-0.055, -0.055), (0.055, -0.055), (0.055, 0.055), (-0.055, 0.055)]
    for k in (-1, 1):
        sb = s + k * (w / 2 + 0.3)
        pts3 = []
        for i in range(6):
            a = (math.pi / 2) * i / 5
            pts3.append(tuple(f.P(sb, 0.1 + 1.2 * (1 - math.cos(a)), z1 + 0.25 + 0.85 * math.sin(a))))
        mb.sweep(pts3, prof, IRON, True, None, up=(eu.x, eu.y, 0.0))


WL_S = 0.68


def wall_lantern(mb, f, s, za, base=0.0):
    """lanterna de suporte: espelho de ferro, braco com mao-francesa curva, remate torneado e a lanterna da ordem"""
    mb = LIFE[0] or mb
    f.box(mb, s, base + 0.07, za - 0.4, 0.44, 0.14, 1.0, IRON, bevel=B_CAST)
    mb.beam(f.P(s, base + 0.1, za), f.P(s, base + 1.42, za), 0.12, 0.15, IRON, 0.0)
    prof = [(-0.05, -0.05), (0.05, -0.05), (0.05, 0.05), (-0.05, 0.05)]
    eu = f.uvec()
    pts = []
    for i in range(5):
        a = (math.pi / 2) * i / 4
        pts.append(tuple(f.P(s, base + 0.12 + 0.95 * (1 - math.cos(a)), za - 0.85 + 0.8 * math.sin(a))))
    mb.sweep(pts, prof, IRON, True, None, up=(eu.x, eu.y, 0.0))
    _lathe(mb, tuple(f.P(s, base + 1.46, za - 0.07)), [(0.12, 0.0), (0.12, 0.1), (0.0, 0.26)], IRON, 6)
    top = za - 0.08
    c = f.P(s, base + 1.18, top - 0.2 - 2.05 * WL_S)
    mb.rod(f.P(s, base + 1.18, top), f.P(s, base + 1.18, top - 0.25), 0.04, IRON, 4)
    EM.lantern_head(mb, mb, (c.x, c.y, c.z), f.yaw, WL_S)


def timber_face(mb, f, z0, z1, wins, pattern="chevron", zsill=None, keep=(), door=None):
    """estrutura aparente: soleira, frechal, montantes e o PREENCHIMENTO dos vaos cheios ('chevron' / 'cross' /
    'studs'). keep = lanternas (ali nao nasce montante); door = (s0, s1, zt): a soleira e o preenchimento param no vao
    da porta (portal proprio: door_timber)"""
    Lf = f.L
    if door:
        d0, d1, dzt = door
        for a, b in ((-Lf / 2 - 0.15, d0 - 0.62), (d1 + 0.62, Lf / 2 + 0.15)):
            f.box(mb, (a + b) / 2, 0.15, z0 + 0.22, b - a, 0.3, 0.44, WOOD)
    else:
        f.box(mb, 0.0, 0.15, z0 + 0.22, Lf + 0.3, 0.3, 0.44, WOOD)
    f.box(mb, 0.0, 0.15, z1 - 0.22, Lf + 0.3, 0.3, 0.44, WOOD)
    xs = [-Lf / 2 + 0.22, Lf / 2 - 0.22]
    blocked = []
    for s, w in wins:
        xs += [s - w / 2 - 0.55, s + w / 2 + 0.55]
        blocked.append((s - w / 2 - 0.6, s + w / 2 + 0.6))
    if door:
        blocked.append((door[0] - 0.7, door[1] + 0.7))
    xs = sorted(xs)
    full = list(xs)
    for a, b in zip(xs, xs[1:]):
        mid = (a + b) / 2
        if b - a > 3.4 and not any(b0 < mid < b1 for b0, b1 in blocked):
            near = [k for k in keep if a < k < b]
            if near:
                for k in near:
                    for dd in (-0.95, 0.95):
                        if a + 0.5 < k + dd < b - 0.5:
                            full.append(k + dd)
            else:
                full.append(mid)
    full = sorted(full)
    for x in full:
        if door and door[0] - 0.65 < x < door[1] + 0.65:
            continue
        f.box(mb, x, 0.15, (z0 + z1) / 2, 0.42, 0.3, z1 - z0 - 0.3, WOOD)
    za, zb = z0 + 0.45, z1 - 0.45
    for a, b in zip(full, full[1:]):
        mid = (a + b) / 2
        if door and door[0] - 0.7 < mid < door[1] + 0.7:
            continue
        win = [(b0, b1) for b0, b1 in blocked if b0 < mid < b1]
        lan = any(a < k < b for k in keep)
        if win:
            if zsill is None or zsill - za < 0.9 or b - a < 1.0:
                continue
            if pattern == "cross":
                f.beam(mb, a + 0.25, za, b - 0.25, zsill - 0.05, 0.12, 0.2, 0.28)
                f.beam(mb, a + 0.25, zsill - 0.05, b - 0.25, za, 0.12, 0.2, 0.28)
            elif pattern == "studs":
                n = max(1, int((b - a) / 1.2))
                for k in range(1, n):
                    f.box(mb, a + (b - a) * k / n, 0.12, (za + zsill) / 2, 0.26, 0.24, zsill - za, WOOD)
            continue
        if b - a < 1.0 or pattern == "posts":
            continue
        if lan:
            f.box(mb, mid, 0.13, z0 + (z1 - z0) * 0.2, b - a, 0.26, 0.3, WOOD)
            continue
        if pattern == "cross":
            f.beam(mb, a + 0.2, za, b - 0.2, zb, 0.15, 0.3, 0.34)
            f.beam(mb, a + 0.2, zb, b - 0.2, za, 0.12, 0.24, 0.34)
        elif pattern == "studs":
            n = max(1, int(round((b - a) / 1.2)))
            for k in range(1, n):
                f.box(mb, a + (b - a) * k / n, 0.12, (z0 + z1) / 2, 0.3, 0.24, z1 - z0 - 0.5, WOOD)
            f.box(mb, mid, 0.13, (z0 + z1) / 2 - 0.2, b - a, 0.26, 0.3, WOOD)
        elif mid < 0:
            f.beam(mb, a + 0.2, za, b - 0.2, zb, 0.15, 0.3, 0.38)
        else:
            f.beam(mb, a + 0.2, zb, b - 0.2, za, 0.15, 0.3, 0.38)


def win_slots(Lf, w, n=None, margin=1.6):
    n = n if n is not None else max(1, int((Lf - 2 * margin + 1.2) / (w + 2.4)))
    step = (Lf - 2 * margin) / n
    return [-Lf / 2 + margin + step * (k + 0.5) for k in range(n)]


# ------------------------------------------------------------------ pedra: soco, silhar, cunhais, porta
COURSES = (1.1, 0.8)


def socle(mb, G, body, fs, front, door=True):
    """soco em 2 fiadas + filete de obsidiana, em ANEL (a casa e oca) e aberto no vao da porta:
    nucleo escuro (-0,4..0,5, sai 0,38), blocos com junta na frente (0,34..0,5), fiada de cima recuada (0,5..0,88,
    sai 0,28) e o filete (0,88..0,98, sai 0,33). A parte de dentro do anel morre dentro da casca."""
    gap = [(-DW / 2 - 0.3, DW / 2 + 0.3)] if door else []
    for key, f in fs.items():
        g = gap if key == front else ()
        ext = 0.4 if key in ("+y", "-y") else 0.0
        band_face(mb, f, -T_EXT + 0.03, 0.38, -0.4, 0.5, M_JNT, ext=ext, gaps=g)
        band_face(mb, f, -T_EXT + 0.05, 0.28, 0.5, 0.88, M_DRESS, ext=(0.3 if ext else 0.0), gaps=g)
        band_face(mb, f, -T_EXT + 0.07, 0.33, 0.88, 0.98, OBS, ext=(0.35 if ext else 0.0), gaps=g)
        # blocos com junta so na fachada (o resto: faixa corrida)
        if key == front:
            L_ = f.L + 0.84
            nb = max(1, int(round(L_ / 3.0)))
            cuts = [-L_ / 2 + L_ * k / nb for k in range(nb + 1)]
            for a, b in zip(cuts, cuts[1:]):
                for g0, g1 in g or [(1e9, 1e9)]:
                    parts = [(a, b)]
                    if not (g1 <= a or g0 >= b):
                        parts = [(a, g0), (g1, b)]
                    for pa, pb in parts:
                        pa2 = pa + (0.04 if pa > -L_ / 2 + 1e-3 else 0.0)
                        pb2 = pb - (0.04 if pb < L_ / 2 - 1e-3 else 0.0)
                        if pb2 - pa2 > 0.2:
                            f.box(mb, (pa2 + pb2) / 2, 0.42, 0.05, pb2 - pa2, 0.16, 0.9, M_DRESS)


def ashlar(mb, f, z0, z1, legs, excl, phase=0, joints=True, joint_rows=0):
    """silhar em relevo raso (0,07) na face f: fiadas de 2 alturas, blocos de ~4,2 com juntas desencontradas sobre o
    nucleo escuro (a casca). legs(k) = pernas dos cunhais; excl = [(s0, s1, za, zb)] vaos.
    joint_rows (03.09): nas laterais (joints=False) as 'joint_rows' fiadas de BAIXO ganham juntas verticais (blocos
    menores onde o jogador passa); as de cima ficam corridas"""
    hs = COURSES
    n2 = max(1, int(round((z1 - z0) / sum(hs))))
    sc = (z1 - z0) / (n2 * sum(hs))
    zz = z0
    k = 0
    while zz < z1 - 0.05:
        h = hs[k % 2] * sc
        za, zb = zz + 0.04, zz + h - 0.04
        la, lb = legs(k)
        rects = [(-f.L / 2 + la + 0.06, f.L / 2 - lb - 0.06, za, zb, True)]
        for e0, e1, ez0, ez1 in excl:
            out = []
            for a, b, ra, rb, full in rects:
                if e1 <= a or e0 >= b or ez1 <= ra or ez0 >= rb:
                    out.append((a, b, ra, rb, full))
                    continue
                if e0 - a > 0.3:
                    out.append((a, e0 - 0.05, ra, rb, full))
                if b - e1 > 0.3:
                    out.append((e1 + 0.05, b, ra, rb, full))
                m0, m1 = max(a, e0 - 0.05), min(b, e1 + 0.05)
                if ez0 - ra > 0.14:
                    out.append((m0, m1, ra, ez0 - 0.04, False))
                if rb - ez1 > 0.14:
                    out.append((m0, m1, ez1 + 0.04, rb, False))
            rects = out
        PL = 4.2
        off = (phase + k) % 2 * PL / 2
        for a, b, ra, rb, full in rects:
            cuts = [a, b]
            if (joints or k < joint_rows) and full:
                cuts = [a] + [(-f.L / 2 + off + PL * j) for j in range(-1, int(f.L / PL) + 3)
                              if a + 0.8 < -f.L / 2 + off + PL * j < b - 0.8] + [b]
            for c0, c1 in zip(cuts, cuts[1:]):
                p0 = c0 + (0.04 if c0 > a else 0.0)
                p1 = c1 - (0.04 if c1 < b else 0.0)
                if p1 - p0 > 0.12:
                    f.box(mb, (p0 + p1) / 2, 0.035, (ra + rb) / 2, p1 - p0, 0.07, rb - ra, M_ASH)
        zz += h
        k += 1


def quoins(mb, G, x0, x1, y0, y1, z0, z1, front="+y"):
    """cunhais que SEGUEM as fiadas do silhar: perna longa 1,5 / curta 0,9 alternadas, saliencia 0,22 / 0,15"""
    hs = COURSES
    n2 = max(1, int(round((z1 - z0) / sum(hs))))
    sc = (z1 - z0) / (n2 * sum(hs))
    la, lb = 1.5, 0.9
    zz = z0
    k = 0
    while zz < z1 - 0.05:
        h = hs[k % 2] * sc
        pq = 0.22 if k % 2 == 0 else 0.15
        ax, ay = (la, lb) if k % 2 == 0 else (lb, la)
        for cx_, cy_ in ((x0, y0), (x1, y0), (x0, y1), (x1, y1)):
            sgx = 1.0 if cx_ > (x0 + x1) / 2 else -1.0
            sgy = 1.0 if cy_ > (y0 + y1) / 2 else -1.0
            fr = (front == "+y" and sgy > 0) or (front == "+x" and sgx > 0)
            # perna ao longo de x (face +-y) com o canto, e perna ao longo de y (face +-x) sem o canto; as duas so
            # ate a face interna da casca (T_EXT): o forro interno fica limpo
            ti = T_EXT - 0.03
            mb.box((ax + pq, pq + ti, h - 0.08), G.p(cx_ - sgx * (ax - pq) / 2, cy_ + sgy * (pq - ti) / 2,
                                                          zz + h / 2), G.r(), M_DRESS, 0.0)
            mb.box((pq + ti, ay - T_EXT, h - 0.08), G.p(cx_ + sgx * (pq - ti) / 2, cy_ - sgy * (ay + T_EXT) / 2,
                                                             zz + h / 2), G.r(), M_DRESS, 0.0)
        zz += h
        k += 1

    def legs_x(k):
        return ((la if k % 2 == 0 else lb),) * 2

    def legs_y(k):
        return ((lb if k % 2 == 0 else la),) * 2
    return legs_x, legs_y


def door_stone(mb, f, style="default"):
    """portal de cantaria: ombreiras em 3 pedras alternadas (saem 0,6: cobrem o corte do soco), verga lisa de remate,
    FECHO saliente, pingadeira por cima, soleira baixa; RESVESTIMENTO de madeira no vao (a espessura da parede).
    FINESSE 3 (03.08, variacao DIRIGIDA pelo oficio; o vao livre 8 x 11 nao muda):
      'segmental' (boticario H3): verga em ARCO ABATIDO de 5 aduelas em leque com fecho maior;
      'label'     (cartografo H5): pingadeira gotica com LABEL STOPS pesados e DEGRAU de pedra largo na soleira;
      'rustic'    (mestre de armas H7): ombreiras em cantaria RUSTICA (saem 0,85, chanfro largo, 2 larguras);
      'plain'     (ferreiro H2): ombreiras em 2 pedras grandes, so a verga (o ALPENDRE de madeira cobre a porta)."""
    zs = [0.0, 2.75, DH] if style == "plain" else [0.0, 1.85, 3.7, DH]
    dep, bev = (0.85, 0.1) if style == "rustic" else (0.6, B_PROP)
    for k in (-1, 1):
        for i, (za, zb) in enumerate(zip(zs, zs[1:])):
            wj = (0.8 if i % 2 == 0 else 0.58) if style == "rustic" else (0.66 if i % 2 == 0 else 0.5)
            f.box(mb, k * (DW / 2 + 0.1 + wj / 2), dep / 2 - 0.05, (za + zb) / 2 + 0.02, wj, dep, zb - za - 0.06,
                  M_DRESS, bevel=bev)
    if style == "segmental":
        for i in range(5):
            u = (i - 2) / 2.0                                    # -1..1
            if i == 2:
                continue
            f.box(mb, u * 2.3, 0.25, DH + 0.46 + 0.16 * (1 - u * u), 0.96, 0.6, 0.76, M_CAP, ry=u * math.radians(17.0),
                  bevel=0.06)
        f.box(mb, 0.0, 0.12, DH + 0.5, DW + 1.7, 0.3, 0.8, M_JNT)                      # junta escura entre as aduelas
        f.box(mb, 0.0, 0.36, DH + 0.7, 0.86, 0.82, 1.0, M_DRESS, bevel=B_PROP)         # fecho
        f.box(mb, 0.0, 0.3, DH + 1.24, DW + 2.2, 0.7, 0.14, M_CAP, bevel=0.03)
        return
    if style == "plain":
        f.box(mb, 0.0, 0.25, DH + 0.46, DW + 1.7, 0.6, 0.72, M_CAP, bevel=B_PROP)
        return
    f.box(mb, 0.0, 0.25, DH + 0.46, DW + 1.7, 0.6, 0.72, M_CAP, bevel=B_PROP)
    kw = 0.86 if style == "rustic" else 0.72
    f.box(mb, 0.0, 0.33, DH + 0.66, kw, 0.76, 0.92, M_DRESS, bevel=(0.08 if style == "rustic" else B_PROP))
    f.box(mb, 0.0, 0.34, DH + 1.21, DW + 2.2, 0.78, 0.18, M_CAP, bevel=0.03)
    if style == "label":
        for k in (-1, 1):
            f.box(mb, k * (DW / 2 + 1.05), 0.36, DH + 0.72, 0.42, 0.76, 0.9, M_CAP)                # label stops
            f.box(mb, k * (DW / 2 + 1.05), 0.44, DH + 0.3, 0.3, 0.6, 0.2, M_DRESS)
            # degrau de pedra largo na soleira (2 blocos, topo = soleira, 0,12 acima da rua)
            f.box(mb, k * (DW + 1.6) / 4, 0.95, -0.09, (DW + 1.6) / 2 - 0.04, 0.8, 0.6, M_DRESS, bevel=B_PROP)
        return
    for k in (-1, 1):
        f.box(mb, k * (DW / 2 + 1.0), 0.34, DH + 0.9, 0.24, 0.72, 0.6, M_CAP, bevel=0.03)


def door_timber(mb, f, zt):
    """portal de madeira do terreo de enxaimel: 2 montantes largos, verga com as MISULAS em ogiva nos cantos (o vao
    le 'gotico' sem fechar o retangulo livre de 8 x 11), capelo de ardosia em maos-francesas"""
    for k in (-1, 1):
        f.box(mb, k * (DW / 2 + 0.32), 0.16, (ZC0 + DH + 0.5) / 2 - 0.25, 0.64, 0.4, DH + 0.5 - ZC0 + 0.5, WOOD)
        f.box(mb, k * (DW / 2 + 0.42), 0.18, 0.5, 0.74, 0.44, 1.0, M_DRESS, bevel=B_PROP)   # base de pedra
    f.box(mb, 0.0, 0.18, DH + 0.3, DW + 1.9, 0.44, 0.6, WOOD)
    nv = f.nvec()
    for k in (-1, 1):
        x0 = k * DW / 2
        tri_slab(mb, [f.P(x0, 0.12, DH - 1.0), f.P(x0, 0.12, DH), f.P(x0 - k * 0.9, 0.12, DH)], nv, 0.3, WOOD)
    if zt - DH > 2.6:
        _hood(mb, f, 0.0, DH + 0.95, DW + 0.6)


def door_reveal(mb, f):
    """o vao atravessa a parede oca (casca + forro): revestimento de madeira nas 2 ombreiras e no teto do vao; a
    soleira de pedra baixa (0,12 acima do piso e da rua) avanca 0,55 para fora"""
    tw = T_EXT + T_LIN
    for k in (-1, 1):
        f.box(mb, k * (DW / 2 + 0.05), -tw / 2, (FLOOR_K + DH) / 2, 0.1, tw + 0.02, DH - FLOOR_K, WOOD)
    f.box(mb, 0.0, -tw / 2, DH + 0.05, DW + 0.2, tw + 0.02, 0.1, WOOD)
    f.box(mb, 0.0, (-tw + 0.55) / 2, 0.21 - 0.3, DW + 0.2, tw + 0.55, 0.6, M_DRESS, bevel=B_PROP)


# ------------------------------------------------------------------ telhado: fiadas, cumeeira, chamine
def slate_course(mb, G, xa, xb, ay, az, s, tr, lr, thr, teeth=0, depth=0.3, m=ROOF):
    dy, dz = s * math.cos(tr), -math.sin(tr)
    ny, nz = s * math.sin(tr), math.cos(tr)
    out = [(xa, 0.0), (xb, 0.0)]
    if teeth:
        for j in range(2 * teeth + 1):
            out.append((xb - j * (xb - xa) / (2 * teeth), lr if j % 2 == 0 else lr - depth))
    else:
        out += [(xb, lr), (xa, lr)]
    bm = mb.bm
    lo = [bm.verts.new(G.p(u, ay + dy * v, az + dz * v)) for u, v in out]
    hi = [bm.verts.new(G.p(u, ay + dy * v + ny * thr, az + dz * v + nz * thr)) for u, v in out]
    n = len(out)
    faces = [bm.faces.new(lo), bm.faces.new(list(reversed(hi)))]
    for i in range(n):
        j = (i + 1) % n
        faces.append(bm.faces.new((lo[j], lo[i], hi[i], hi[j])))
    bmesh.ops.recalc_face_normals(bm, faces=faces)
    mb._post(lo + hi, m, None, 0, 1)


def roof_z(ze, R, hd, cy, y, thr=0.34):
    t = math.atan2(R, hd)
    return ze + R - abs(y - cy) * math.tan(t) + thr / math.cos(t)


def chimney(mb, G, cx_, cy_, wx_, dp, z0, z1, kind, ze, R, hd, cy, m_roof=ROOF):
    """chamine do kit: fuste em fiadas de 2 alturas, RUFO inclinado no telhado, capa com ressalto duplo e pote"""
    t = math.atan2(R, hd)
    zr = roof_z(ze, R, hd, cy, cy_)
    zlow = min(roof_z(ze, R, hd, cy, cy_ - dp / 2), roof_z(ze, R, hd, cy, cy_ + dp / 2)) - 0.4
    if z0 is None:
        z0 = zlow - 0.2                    # 2a chamine: nasce logo abaixo da ardosia (sem peito por dentro)
    mb.box((wx_ - 0.1, dp - 0.1, zlow - z0), G.p(cx_, cy_, (z0 + zlow) / 2), G.r(), M_DRESS, 0.0)
    zz = zlow
    k = 0
    top = z1 - 0.62
    while zz < top - 0.05:
        h = min((1.5, 0.6)[k % 2], top - zz)
        ins = 0.0 if k % 2 == 0 else 0.1
        mb.box((wx_ - ins, dp - ins, h), G.p(cx_, cy_, zz + h / 2), G.r(), M_DRESS, 0.0)
        zz += h
        k += 1
    mb.box((wx_ + 0.24, dp + 0.24, 0.2), G.p(cx_, cy_, top + 0.1), G.r(), M_DRESS, 0.0)
    mb.box((wx_ + 0.46, dp + 0.46, 0.24), G.p(cx_, cy_, top + 0.32), G.r(), M_CAP, 0.04)
    mb.box((wx_ + 0.16, dp + 0.16, 0.16), G.p(cx_, cy_, top + 0.52), G.r(), M_DRESS, 0.0)
    zt = top + 0.6
    sg = 1 if cy_ >= cy else -1
    if abs(cy_ - cy) < dp / 2 + 0.2:
        for s2 in (-1, 1):
            mb.box((wx_ + 0.5, 1.0, 0.14), G.p(cx_, cy + s2 * 0.45, ze + R + 0.35), G.r(-s2 * t, 0, 0), m_roof, 0.0)
    else:
        mb.box((wx_ + 0.5, dp / math.cos(t) + 0.5, 0.14), G.p(cx_, cy_, zr + 0.02), G.r(-sg * t, 0, 0), m_roof, 0.0)
    pot = [(0.3, 0.0), (0.33, 0.1), (0.25, 0.5), (0.35, 0.8), (0.29, 0.88)]
    if kind == "twin":
        for kk in (-1, 1):
            q = G.p(cx_ + kk * 0.55, cy_, zt) if wx_ >= dp else G.p(cx_, cy_ + kk * 0.55, zt)
            _lathe(mb, tuple(q), pot, M_POT, 6)
    elif kind == "hood":
        for kx in (-1, 1):
            for ky in (-1, 1):
                mb.box((0.14, 0.14, 0.8), G.p(cx_ + kx * 0.55, cy_ + ky * 0.55, zt + 0.4), G.r(), IRON, 0.0)
        th2 = math.radians(32.0)
        for s2 in (-1, 1):
            mb.box((wx_ + 0.5, 1.05, 0.12), G.p(cx_, cy_ + s2 * 0.44, zt + 1.06), G.r(-s2 * th2, 0, 0), m_roof, 0.0)
    else:
        _lathe(mb, tuple(G.p(cx_, cy_, zt)), pot, M_POT, 6)


# ------------------------------------------------------------------ casa (referencial do kit)
WALLKEY = {False: {"front": "+y", "back": "-y", "right": "+x", "left": "-x"},
           True: {"front": "+x", "back": "-x", "right": "-y", "left": "+y"}}


def ze_top(stories):
    return ZC0 + sum(h for _, h in stories)


def win_defaults(tp):
    """janelas por andar em coordenadas do LOTE (reais): (parede, coordenada ao longo dela - u na frente/fundo, v nas
    laterais). A lareira fica na parede 'left' (onda 0) e a escada ao longo do fundo: dali so saem janelas altas"""
    if tp == "A":
        return {0: {"front": [-9.8, 9.8], "right": [7.2], "left": [7.4]},
                1: {"front": [-8.54, 0.0, 8.54], "back": [-8.0, 8.0], "right": [-2.0], "left": [6.0]}}
    if tp == "B":
        return {0: {"front": [-11.6, 11.6], "right": [6.0]},
                1: {"front": [-12.8, -4.27, 4.27, 12.8], "back": [-10.0, 0.0, 10.0], "right": [-7.0, 7.0],
                    "left": [-7.0, 11.0]}}
    return {0: {"front": [-8.4, 8.4], "back": [-6.0, 6.0], "right": [0.0]}}


def blind_window(mb, f, s, zlo, w, h):
    """03.09: janela CEGA com peitoril de verdade no pano lateral: nicho VAZADO na casca (recuo 0,12), postigos navy
    FECHADOS dentro do nicho, ombreiras de pedra, verga e peitoril com pingadeira. Le 'janela fechada', nao parede.
    Devolve o vao a abrir na casca."""
    zc = zlo + h / 2
    f.box(mb, s, -0.2, zc, w + 0.12, 0.06, h + 0.12, M_JNT)            # fundo escuro (esconde o forro interno)
    for k in (-1, 1):
        f.box(mb, s + k * w / 4, -0.1, zc, w / 2 - 0.05, 0.08, h - 0.08, M_SHUT, bevel=0.03)
        f.box(mb, s + k * w / 4, -0.04, zlo + h * 0.5, w / 2 - 0.18, 0.05, 0.24, WOOD)
        f.box(mb, s + k * (w / 2 + 0.18), 0.22, zc + 0.05, 0.36, 0.44, h + 0.3, M_DRESS)
    f.box(mb, s, 0.25, zlo + h + 0.32, w + 1.1, 0.5, 0.5, M_CAP)
    f.box(mb, s, 0.26, zlo - 0.17, w + 1.0, 0.52, 0.26, M_CAP)
    return (s - w / 2, s + w / 2, zlo, zlo + h)


def chimney_breast(mb, f, s, wb, z0, z1):
    """03.09: PEITO DE CHAMINE externo (sai 0,4) no pano lateral da lareira: base em talude, fuste em fiadas de 2
    alturas sobre nucleo escuro, ombro com pingadeira no topo (a chamine do telhado continua por cima)"""
    f.box(mb, s, 0.2, (z0 + z1) / 2, wb, 0.4, z1 - z0, M_JNT)
    f.box(mb, s, 0.3, z0 + 0.55, wb + 0.6, 0.6, 1.1, M_DRESS)
    mb.beam(f.P(s, 0.6, z0 + 1.1), f.P(s, 0.42, z0 + 1.7), wb + 0.6, 0.2, M_CAP, 0.0)      # talude
    zz, k = z0 + 1.7, 0
    while zz < z1 - 0.2:
        hh = min((1.6, 0.9)[k % 2], z1 - zz)
        ins = 0.0 if k % 2 == 0 else 0.1
        f.box(mb, s, 0.22, zz + hh / 2, wb - ins, 0.44, hh - 0.06, M_DRESS)
        zz += hh
        k += 1
    mb.beam(f.P(s, 0.5, z1), f.P(s, 0.1, z1 + 0.5), wb + 0.36, 0.2, M_CAP, 0.0)            # ombro (pingadeira)


def buttress(mb, f, s, z0, z1):
    """03.09: CONTRAFORTE de canto em 2 lances com capas inclinadas (pingadeiras) de pedra clara"""
    zm = z0 + (z1 - z0) * 0.42
    f.box(mb, s, 0.36, (z0 + zm) / 2, 1.3, 0.72, zm - z0, M_DRESS)
    f.box(mb, s, 0.28, (zm + z1) / 2, 1.1, 0.56, z1 - zm, M_DRESS)
    mb.beam(f.P(s, 0.76, zm - 0.02), f.P(s, 0.52, zm + 0.5), 1.4, 0.2, M_CAP, 0.0)
    mb.beam(f.P(s, 0.6, z1 - 0.02), f.P(s, 0.06, z1 + 0.95), 1.22, 0.22, M_CAP, 0.0)


def porch(mb, f, F, s0, s1, dep, zw, m_roof):
    """03.08 (ferreiro H2): ALPENDRE de madeira aberto ao lado da porta: 2 postes com base de pedra, frechais, maos-
    francesas, 4 caibros e agua de ardosia (a forja de mao e do vestir, agente R). Sem colisao (postes finos)."""
    t = math.radians(18.0)
    zf = zw - dep * math.tan(t)
    sc = (s0 + s1) / 2
    for sp in (s0 + 0.3, s1 - 0.3):
        f.box(mb, sp, dep - 0.25, 0.35, 0.62, 0.62, 0.7, M_DRESS)
        f.box(mb, sp, dep - 0.25, (0.7 + zf - 0.4) / 2, 0.36, 0.36, zf - 0.4 - 0.7, WOOD)
        mb.beam(f.P(sp, dep - 0.25, zf - 1.7), f.P(sp, dep - 1.1, zf - 0.55), 0.16, 0.22, WOOD, 0.0)
    f.box(mb, sc, dep - 0.25, zf - 0.22, s1 - s0 + 0.4, 0.3, 0.36, WOOD)                  # frechal da frente
    for k in (-1, 1):
        f.box(mb, sc + k * (s1 - s0) / 2, 0.3, zw - 0.75, 0.3, 0.5, 0.5, WOOD)             # misulas
    for i in range(4):
        sr = s0 + (s1 - s0) * (i + 0.5) / 4
        mb.beam(f.P(sr, 0.4, zw - 0.1), f.P(sr, dep + 0.1, zf - 0.1), 0.2, 0.24, WOOD, 0.0)
    Ls = (dep + 0.3) / math.cos(t)
    f.box(mb, sc, (dep + 0.3) / 2 + 0.02, (zw + zf) / 2 - 0.04 * dep + 0.14, s1 - s0 + 0.9, Ls, 0.16, m_roof, rx=-t)
    f.box(mb, sc, dep + 0.34, zf + 0.08, s1 - s0 + 0.9, 0.08, 0.3, WOOD)                   # testeira


def balconette(mb, f, s, zlo, w):
    """03.08 (mestre de armas H7): SACADA de ferro (balconete) na janela central do andar: 2 misulas, estrado de
    madeira, montantes, balaustres e corrimao"""
    zp = zlo - 0.34
    for k in (-1, 1):
        mb.beam(f.P(s + k * (w / 2 + 0.25), 0.04, zp - 0.85), f.P(s + k * (w / 2 + 0.25), 1.0, zp - 0.08), 0.12, 0.14,
                IRON, 0.0)
        f.box(mb, s + k * (w / 2 + 0.6), 1.06, zp + 0.58, 0.08, 0.08, 1.16, IRON)
    f.box(mb, s, 0.86, zp, w + 1.3, 0.62, 0.12, WOOD)
    f.box(mb, s, 1.06, zp + 1.14, w + 1.3, 0.1, 0.08, IRON)
    n = 5
    for i in range(n):
        sb = s - w / 2 - 0.55 + (w + 1.1) * (i + 0.5) / n
        mb.rod(f.P(sb, 1.06, zp + 0.06), f.P(sb, 1.06, zp + 1.1), 0.03, IRON, 4)


def kit_house(mb, hrec, spec):
    """monta o EXTERIOR de uma casa no referencial do kit (a transformacao do lote ja esta ativa em mb e LIFE).
    Devolve as informacoes para o interior: janelas (reais, no lote), telhado (kit), chamines, torreao."""
    nm, tp, x, y, w, d, deg, z = hrec
    T = L.HOUSE_TYPES[tp]
    gf = spec.get("gable_front", False)
    G = Frame(0.0, 0.0, 0.0, math.pi / 2 if gf else 0.0)
    W, D = ((d, w) if gf else (w, d))
    W, D = W / K, D / K
    WK = WALLKEY[gf]
    front, back = WK["front"], WK["back"]
    two = T["floors"] == 2
    h0 = (T["h0"] + (1.0 if two else 2.0)) / K - ZC0
    stories = [(spec.get("ground", "stone"), h0)] + ([(spec.get("upper", "timber"), T["h1"] / K)] if two else [])
    jet = spec.get("jetty", 0.0) if two else 0.0
    R = spec["rise"]
    rm = ROOF_B if spec.get("roof") == "B" else ROOF                 # 03.16: 2 ardosias dirigidas por casa
    Fw = lot_frame(hrec)
    gvar = spec.get("ground_kind", "default")
    wx0, wx1, wy0, wy1 = -W / 2, W / 2, -D / 2, D / 2
    body0 = (wx0, wx1, wy0, wy1)
    wins_spec = spec.get("wins") or win_defaults(tp)
    info = {"windows": [], "G_a": G.a, "stories": stories, "jet": jet}

    def faces(b):
        x0, x1, y0, y1 = b
        return {"+y": Face(G, (0.0, y1), (1.0, 0.0), x1 - x0), "-y": Face(G, (0.0, y0), (-1.0, 0.0), x1 - x0),
                "+x": Face(G, (x1, (y0 + y1) / 2), (0.0, -1.0), y1 - y0),
                "-x": Face(G, (x0, (y0 + y1) / 2), (0.0, 1.0), y1 - y0)}

    def lot_to_g(u, v):
        return (v / K, -u / K) if gf else (u / K, v / K)

    fs0 = faces(body0)
    socle(mb, G, body0, fs0, front)
    zc = ZC0
    body = body0
    top_b = body0
    for si, (kind, h) in enumerate(stories):
        b = body0
        if si > 0 and jet > 0:
            x0, x1, y0, y1 = body0
            b = (x0, x1 + jet, y0, y1) if gf else (x0, x1, y0 - jet * 0.6, y1 + jet)
            bx0, bx1, by0, by1 = b
            # placa do balanco em ANEL (o miolo e o piso do andar de cima, sg_village_int)
            ring_rect(mb, G, (bx0 - 0.15, bx1 + 0.15, by0 - 0.15, by1 + 0.15),
                      (x0 + T_EXT - 0.06, x1 - T_EXT + 0.06, y0 + T_EXT - 0.06, y1 - T_EXT + 0.06), zc - 0.2, zc + 0.3,
                      WOOD)
            ff = fs0[front]
            for s in win_slots(ff.L, 0.4, n=int(ff.L / 2.4), margin=0.8):
                if abs(s) < DW / 2 + 1.3 or any(abs(s - q) < 0.75 for q in info.get("lan", [])):
                    continue
                ff.box(mb, s, jet / 2, zc - 0.45, 0.4, jet, 0.8, WOOD)
        x0, x1, y0, y1 = b
        stone = kind == "stone"
        fs = faces(b)
        if stone:
            lx, ly = quoins(mb, G, x0, x1, y0, y1, zc, zc + h, front)
        zlo_skin = -0.3 if si == 0 else zc
        for key, f in fs.items():
            wall = [k_ for k_, v_ in WK.items() if v_ == key][0]
            is_front = key == front
            coords = list(wins_spec.get(si, {}).get(wall, []))
            shop = spec.get("shop") if (si == 0 and is_front) else None
            if shop is not None:
                coords = [c for c in coords if (c > 0) != (shop > 0)]
            wmode = spec.get("win", "cross") if (is_front and kind == "timber") else "cross"
            if si == 0 and is_front and tp == "B":
                wmode = "trio"
            ww = 3.0 if wmode == "trio" else 1.7
            if si == 0:
                zl, wh = ZC0 + 0.7, 3.4
            else:
                zl, wh = zc + 1.5, 3.0
            holes, wins = [], []
            shut = bool(is_front and stone and shop is None and spec.get("shutters"))
            boxes = spec.get("planter") and kind == "timber" and is_front and si == len(stories) - 1
            dress_seq = spec.get("dress", "coc")
            for wi, c in enumerate(coords):
                s = f.s_of(*lot_to_g(*((c, 0.0) if wall in ("front", "back") else (0.0, c))))
                dr = {"c": "curtain", "o": "open", "b": "blind"}[dress_seq[(wi + si + (0 if is_front else 1))
                                                                           % len(dress_seq)]]
                window(mb, f, s, zl, ww, wh, head=(spec.get("stone_head", "lintel") if stone else "hood"),
                       shutters=shut, planter=bool(boxes) and (len(coords) <= 2 or wi in (0, len(coords) - 1)),
                       style=wmode, dress=dr, stone=stone, lod=(0 if is_front else (2 if (wall == "back" or si > 0) else 1)))
                holes.append((s - ww / 2, s + ww / 2, zl, zl + wh))
                wins.append((s, ww))
                info["windows"].append(dict(wall=wall, c=c, story=si, w=ww * K, z0=zl * K, z1=(zl + wh) * K))
            if shop is not None:
                sshop = f.s_of(*lot_to_g(shop, 0.0))
                shopfront(mb, f, sshop, awning=spec.get("awning", "slate"))
                holes += shop_holes(sshop, SHOP_W)
                info["windows"].append(dict(wall=wall, c=shop, story=si, w=SHOP_W * K, z0=(SHOP_Z1 + 0.55) * K,
                                            z1=(SHOP_Z1 + 1.35) * K, kind="shop"))
            side = wall in ("left", "right")
            # 03.09: panos laterais com estrutura: janela cega (postigos fechados) no terco de tras, peito de chamine
            # na parede da lareira, contraforte no canto de tras; 03.10: montantes cerrados nas laterais de enxaimel
            excl_side = []
            if side and si == 0 and stone and tp != "C":
                vb = -d / 2 + (6.6 if tp == "A" else 7.4)                     # v do nicho (lote, terco de tras)
                sb = f.s_of(*lot_to_g(0.0, vb))
                if all(abs(sb - q) > 2.4 for q, _ in wins):
                    hb = blind_window(mb, f, sb, zl, ww, wh)
                    holes.append(hb)
                    excl_side.append((hb[0] - 0.42, hb[1] + 0.42, hb[2] - 0.45, hb[3] + 0.2))
            door = si == 0 and is_front
            if door:
                holes.append((-DW / 2 - 0.1, DW / 2 + 0.1, -1.0, DH + 0.1))
            sh = T_EXT if key in ("+x", "-x") else 0.0
            slab_holes(mb, f, -f.L / 2 + sh, f.L / 2 - sh, zlo_skin, zc + h, -T_EXT, 0.0, holes,
                       M_JNT if stone else M_PL)
            # lanternas de suporte (so na fachada do terreo): ao lado da porta, do lado do eixo da vila (par na loja/taverna)
            lan = []
            if door:
                side = spec.get("lan_side", 1) if shop is None else (-1 if shop > 0 else 1)
                lan = [side * (DW / 2 + 1.35)] if not spec.get("lan_pair") else [-(DW / 2 + 1.35), DW / 2 + 1.35]
                info["lan"] = lan
            if kind == "timber":
                pat = spec.get("frame", "chevron") if is_front else spec.get("side_frame", "posts")
                timber_face(mb, f, zc, zc + h, wins, pattern=pat, zsill=zl - 0.45, keep=lan,
                            door=((-DW / 2, DW / 2, DH) if door else None))
            else:
                excl = [(s - ww / 2 - 0.42, s + ww / 2 + 0.42, zl - 0.45, zl + wh + 0.2) for s, ww_ in wins]
                excl += excl_side
                if shop is not None:
                    excl.append((sshop - SHOP_W / 2 - 0.75, sshop + SHOP_W / 2 + 0.75, 0.0, 6.35))
                if door:
                    excl.append((-DW / 2 - 0.7, DW / 2 + 0.7, 0.0, DH + 1.3))
                if side and si == 0 and spec.get("chimney") and wall == "left":
                    cu, cv = spec["chimney"]
                    wb = (2.4 if spec.get("chim_kind") == "twin" else 1.5) + 0.3
                    excl.append((f.s_of(*lot_to_g(0.0, cv)) - wb / 2 - 0.1, f.s_of(*lot_to_g(0.0, cv)) + wb / 2 + 0.1,
                                 zc - 1.0, zc + h + 1.0))
                if side and si == 0:
                    sgn = 1.0 if key == "+x" else -1.0
                    excl.append((sgn * f.L / 2 - (1.75 if sgn > 0 else -0.1), sgn * f.L / 2 + (0.1 if sgn > 0 else 1.75),
                                 zc - 1.0, zc + h * 0.72 + 1.0))
                legs = lx if key in ("+y", "-y") else ly
                ashlar(mb, f, zc, zc + h, legs, excl, phase=(0 if key in ("+y", "-y") else 1), joints=is_front,
                       joint_rows=(2 if side else 0))
            if side and si == 0 and spec.get("chimney") and wall == "left":
                cu, cv = spec["chimney"]
                wb = (2.4 if spec.get("chim_kind") == "twin" else 1.5) + 0.3
                chimney_breast(mb, f, f.s_of(*lot_to_g(0.0, cv)), wb, -0.3, ze_top(stories) - 0.1)
            if side and si == 0 and stone:
                sgn = 1.0 if key == "+x" else -1.0
                buttress(mb, f, sgn * (f.L / 2 - 1.0), -0.3, zc + h * 0.72)
            if door:
                if stone:
                    door_stone(mb, f, style=spec.get("door_style", "default"))
                else:
                    door_timber(mb, f, zc + h)
                door_reveal(mb, f)
                za = min(zc + h, 6.6) - 1.0
                for q in lan:
                    wall_lantern(mb, f, q, za, base=(0.07 if stone else 0.0))
                if gvar == "porch":
                    porch(mb, f, Fw, 3.0, 8.0, 2.6, zc + h - 0.45, rm)
            if is_front and si == 1 and spec.get("balcony"):
                for s, ww_ in wins:
                    if abs(s) < 0.5:
                        balconette(mb, f, s, zl, ww_)
        if stone and si < len(stories) - 1:
            ring_rect(mb, G, (x0 - 0.25, x1 + 0.25, y0 - 0.25, y1 + 0.25),
                      (x0 + T_EXT - 0.03, x1 - T_EXT + 0.03, y0 + T_EXT - 0.03, y1 - T_EXT + 0.03),
                      zc + h - 0.4, zc + h, M_CAP, 0.04)                       # cordao de pedra
        zc += h
        top_b = b
    ze = zc
    # ---- telhado ingreme (cumeeira ao longo de x de G)
    x0, x1, y0, y1 = top_b
    cy = (y0 + y1) / 2
    hd = (y1 - y0) / 2
    oe, og, th = 1.0, 0.8, 0.6
    t = math.atan2(R, hd)
    Ls = (hd + oe) / math.cos(t)
    dl = math.radians(3.0)
    tr = t - dl
    nrow = max(4, int(round(Ls / 1.4)))
    wts = [1.3 if (nrow - 1 - k) % 2 == 0 else 0.8 for k in range(nrow)]
    tot = sum(wts)
    xa, xb = x0 - og, x1 + og
    nt = max(4, int(round((xb - xa) / 1.9)))
    for s in (-1, 1):
        acc = 0.0
        fr_slope = (front == "+y" and s > 0)
        for k in range(nrow):
            f0 = acc / tot
            acc += wts[k]
            f1 = min(1.0, (acc + 0.42) / tot)
            ay = cy + s * f0 * (hd + oe)
            az = ze + R - f0 * (R + oe * math.tan(t))
            lr = (f1 - f0) * Ls
            eave = k == nrow - 1
            scal = (nrow - 1 - k) in ((1, 3) if fr_slope else (1,))
            if eave:
                trk, thk = tr, 0.3
            else:
                v0 = wts[k] / tot * Ls
                below = 0.3 if k + 1 == nrow - 1 else 0.2
                trk, thk = t - math.atan2(below + 0.04, v0), 0.2
            slate_course(mb, G, xa, xb, ay, az, s, trk, lr, thk, teeth=(nt if scal else 0), depth=0.26, m=rm)
        for xe in (x0 - og - 0.1, x1 + og + 0.1):
            mb.beam(G.p(xe, cy, ze + R + th), G.p(xe, cy + s * (hd + oe), ze - oe * math.tan(t) + th * 0.6), 0.28,
                    0.7, WOOD, 0.0)
    ez = ze - oe * math.tan(t)
    for s in (-1, 1):
        mb.box((x1 - x0 + 2 * og, 0.3, 0.55), G.p((x0 + x1) / 2, cy + s * (hd + oe - 0.12), ez - 0.05), G.r(), WOOD,
               0.0)
        nr = max(3, int((x1 - x0) / 2.8))
        if (front == "+y" and s < 0) or front == "+x":
            continue
        for k in range(nr + 1):
            xr = x0 + 0.35 + (x1 - x0 - 0.7) * k / nr
            mb.beam(G.p(xr, cy + s * (hd - 0.1), ze - 0.32), G.p(xr, cy + s * (hd + oe - 0.3), ez - 0.2), 0.26, 0.32,
                    WOOD, 0.0)
    rt = ze + R + th / math.cos(t)
    Lr = xb - xa + 0.3
    npc = max(3, int(round(Lr / 1.8)))
    for k in range(npc):
        u0 = xa - 0.15 + Lr * k / npc + 0.05
        u1 = xa - 0.15 + Lr * (k + 1) / npc - 0.05
        mb.box((u1 - u0, 0.62, 0.62), G.p((u0 + u1) / 2, cy, rt - 0.28), G.r(math.pi / 4, 0, 0), OBS, 0.0)
    for xe in (x0 - og - 0.1, x1 + og + 0.1):
        if spec.get("ridge", "crest") == "crest":
            mb.box((0.56, 0.56, 0.5), G.p(xe, cy, rt + 0.05), G.r(), WOOD, 0.0)
            finial_iron(mb, G.p(xe, cy, rt + 0.3), 1.0)
        else:
            finial_wood(mb, G.p(xe, cy, rt + 0.1), 1.0)
    # empenas: parede oca (0,5 = casca + forro) com o vao da janela de sotao; estrutura aparente por fora
    for sx, key in ((1, "+x"), (-1, "-x")):
        f = Face(G, (x1 if sx > 0 else x0, cy), (0.0, -1.0) if sx > 0 else (0.0, 1.0), y1 - y0)
        attic = (key == front) or (spec.get("attic_all", False) and key == "+x" and not gf)
        zc_win = ze + 1.0
        aw, ah = 1.3, 2.0
        poly = [(-hd, ze), (hd, ze), (0.0, ze + R)]
        holes = [(-aw / 2, aw / 2, zc_win, zc_win + ah)] if attic else []
        poly_holes(mb, f, poly, -(T_EXT + T_LIN), 0.0, holes, M_PL)
        f.box(mb, 0.0, 0.15, ze + 0.22, y1 - y0 + 0.3, 0.3, 0.44, WOOD)
        zcol = (ze + 4.6) if attic else (ze + R * 0.42)
        if attic:
            window(mb, f, 0.0, zc_win, aw, ah, head="hood" if key == front else None, style="cross",
                   dress=("curtain" if key == front else "blind"), back=True)
            f.box(mb, 0.0, 0.15, (zcol + 0.2 + ze + R - 0.6) / 2, 0.42, 0.3, ze + R - 0.6 - zcol - 0.2, WOOD)
        else:
            f.box(mb, 0.0, 0.15, ze + R * 0.46, 0.42, 0.3, R * 0.9, WOOD)
        half = hd * (1 - (zcol - ze) / R) - 0.3
        f.box(mb, 0.0, 0.15, zcol, 2 * half, 0.3, 0.42, WOOD)
        for k in (-1, 1):
            f.beam(mb, k * (hd - 0.5), ze + 0.4, k * max(0.5 * half, 1.7), zcol - 0.1, 0.15, 0.3, 0.36)
    # aguas-furtadas: frente em placa VAZADA (a luz recua no vao), corpo de reboco atras, empena de madeira com
    # guarda-pos, rufos de ardosia no encontro com a agua principal
    for di, (side, xd) in enumerate(spec.get("dormers", [])):
        s = 1 if side == "+y" else -1
        wd = 2.8
        yf = cy + s * (hd - 0.6)
        zr = ze + R * (1 - (hd - 0.6) / hd)
        zb = zr + th / math.cos(t) + 0.1
        zt = zb + 2.9
        yb = cy + s * hd * (1 - (zt - ze) / R)
        fd = Face(G, (xd, yf), (s * 1.0, 0.0), wd)
        slab_holes(mb, fd, -wd / 2, wd / 2, zr - 0.6, zt, -0.4, 0.0, [(-0.65, 0.65, zb + 0.5, zb + 2.3)], M_PL)
        ya0, ya1 = sorted((yb - s * 0.4, yf - s * 0.4))
        mb.box((wd, ya1 - ya0, zt - zr + 0.2), G.p(xd, (ya0 + ya1) / 2, (zr - 0.2 + zt) / 2), G.r(), M_PL, 0.0)
        rr = 1.7
        hw = wd / 2 + 0.35
        t2 = math.atan2(rr, hw)
        L2 = hw / math.cos(t2)
        ln = abs(yf - yb) + 1.0
        for s2 in (-1, 1):
            mb.box((L2, ln, 0.32), G.p(xd + s2 * hw / 2, (yf + yb) / 2 + s * 0.3, zt + rr / 2 + 0.16),
                   G.r(0, s2 * t2, 0), rm, 0.0)
        mb.box((0.42, ln + 0.1, 0.42), G.p(xd, (yf + yb) / 2 + s * 0.3, zt + rr + 0.2), G.r(0, math.pi / 4, 0), OBS,
               0.0)
        tri_slab(mb, [fd.P(-wd / 2, 0.0, zt), fd.P(wd / 2, 0.0, zt), fd.P(0.0, 0.0, zt + rr)], fd.nvec(), 0.4, WOOD)
        for k in (-1, 1):
            # ONDA 3 (z-fight): guarda-po 0,08 mais para fora (a frente dele ficava a 0,04 da ponta da agua da agua-furtada)
            mb.beam(fd.P(k * (hw + 0.05), 0.80, zt + 0.02), fd.P(0.0, 0.80, zt + rr + 0.34), 0.2, 0.42, WOOD, 0.0)
            xk = xd + k * (wd / 2 + 0.16)
            mb.beam(G.p(xk, yf, roof_z(ze, R, hd, cy, yf) - 0.06), G.p(xk, yb, roof_z(ze, R, hd, cy, yb) - 0.06),
                    0.34, 0.14, rm, 0.0)
        # 03.12: a 2a agua-furtada fica APAGADA (ritmo acesa / apagada dirigido)
        window(mb, fd, 0.0, zb + 0.5, 1.3, 1.8, head=None, dress=("open" if di == 0 else "blind"), lod=2)
        finial_iron(mb, G.p(xd, (yf + yb) / 2 + s * 0.85, zt + rr + 0.38), 0.55)
    # chamines (a 1a sobe da LAREIRA do interior: parede 'left', v ~ lareira)
    chims = []
    if spec.get("chimney"):
        chims.append((spec["chimney"], spec.get("chim_kind", "stack"), spec.get("chim_h", 2.6)))
    if spec.get("chimney2"):
        chims.append((spec["chimney2"], spec.get("chim2_kind", "stack"), spec.get("chim2_h", 1.6)))
    info["chimneys"] = []
    for ci, ((cu, cv), kind, hx) in enumerate(chims):
        gx, gy = lot_to_g(cu, cv)
        if ci == 0:
            # a da lareira: comprida AO LONGO da parede da empena (sobe do peito de pedra do interior)
            ext_u, ext_v = 1.5, (2.4 if kind == "twin" else 1.5)
            wxc, dpc = (ext_v, ext_u) if gf else (ext_u, ext_v)
            chimney(mb, G, gx, gy, wxc, dpc, ze - 0.5, ze + R + hx, kind, ze, R, hd, cy, m_roof=rm)
            info["chimneys"].append((cu, cv, ext_u * K, ext_v * K, (ze - 0.5) * K))
        else:
            wxc = 2.4 if kind == "twin" else 1.5
            chimney(mb, G, gx, gy, wxc, 1.5, None, ze + R + hx, kind, ze, R, hd, cy, m_roof=rm)
    # torreao (canto da frente): escarpa, fuste OCO em 8 placas com as frestas vazadas, cordoes, misulas, agulha
    tur = spec.get("turret")
    if tur:
        info["turret"] = turret(mb, G, tur, x0, x1, y0, y1, ze, stories, rm)
    info.update(ze=ze, R=R, hd=hd, cy=cy, top_b=top_b, body0=body0, W=W, D=D, gf=gf, G=G, front=front,
                dormers=spec.get("dormers", []))
    return info


def turret(mb, G, tur, x0, x1, y0, y1, ze, stories, rm=ROOF):
    """torreao do canto da frente (H3). FINESSE 3 (03.11 + 14.04): embasamento em TALUDE com cordao, fuste em FIADAS de
    2 alturas (relevo 0,12, blocos desencontrados, juntas escuras) com 2 frestas por andar nas faces de fora, misulas
    sob o balanco, LANTERNA octogonal com 8 lancetas cegas e AGULHA mais alta (marco vertical da vila contra o castelo)."""
    sx, sy = tur
    r = 2.5
    ap0 = r * math.cos(math.pi / 8)
    tx = (x0 - ap0 + T_EXT) if sx < 0 else (x1 + ap0 - T_EXT)
    ty = (y1 + 0.4) if sy > 0 else (y0 - 0.4)
    wp = G.p(tx, ty, 0.0)
    zt1 = ze + 3.2
    rot8 = math.radians(22.5)
    # embasamento em talude (2 lances) + cordao
    _lathe(mb, (wp.x, wp.y, -0.4), [(r + 0.5, 0.0), (r + 0.5, 0.8), (r + 0.34, 0.92), (r + 0.34, 1.3), (r + 0.08, 2.2),
                                     (r + 0.22, 2.3), (r + 0.22, 2.56), (r + 0.02, 2.64)], M_DRESS, 8, rot8,
           caps=(False, False))
    out = math.degrees(math.atan2(wp.y - G.o.y, wp.x - G.o.x))
    out = 45.0 * round(out / 45.0)
    ap = r * math.cos(math.pi / 8)
    fw = 2 * r * math.sin(math.pi / 8)
    G0 = Frame(0.0, 0.0, 0.0, 0.0)
    fr_z = (ze - 5.2, ze + 0.4)
    zb0 = 2.2
    for k in range(8):
        a = math.radians(45.0 * k)
        nx_, ny_ = math.cos(a), math.sin(a)
        f = Face(G0, (wp.x + ap * nx_, wp.y + ap * ny_), (ny_, -nx_), fw)
        da = ((45.0 * k - out + 180.0) % 360.0) - 180.0
        slits = abs(da) < 46.0
        holes = [(-0.3, 0.3, zz - 0.9, zz + 0.9) for zz in fr_z] if slits else []
        slab_holes(mb, f, -fw / 2, fw / 2, zb0, zt1, -0.4, 0.0, holes, M_JNT)
        if abs(da) > 100.0:
            continue                                            # face dentro da casa: so o nucleo
        # fiadas de 2 alturas em relevo 0,12: 2 blocos nas fiadas pares, 1 nas impares (juntas desencontradas);
        # as 2 faces de lado (+-90) so ate o 1o cordao (faixa do jogador)
        ztop = zt1 if abs(da) < 50.0 else ZC0 + stories[0][1]
        zz, kk = zb0 + 0.06, 0
        while zz < ztop - 0.5:
            hh = min((1.0, 0.72)[kk % 2], ztop - 0.45 - zz)
            if hh < 0.3:
                break
            segs = [(-fw / 2 + 0.03, fw / 2 - 0.03)] if kk % 2 else [(-fw / 2 + 0.03, -0.03), (0.03, fw / 2 - 0.03)]
            if slits:
                for zs_ in fr_z:
                    if zz < zs_ + 1.75 and zz + hh > zs_ - 1.2:
                        cut = []
                        for pa, pb in segs:
                            if pb <= -0.64 or pa >= 0.64:
                                cut.append((pa, pb))
                            else:
                                if -0.64 - pa > 0.15:
                                    cut.append((pa, -0.64))
                                if pb - 0.64 > 0.15:
                                    cut.append((0.64, pb))
                        segs = cut
            for pa, pb in segs:
                if pb - pa > 0.15:
                    f.box(mb, (pa + pb) / 2, 0.06, zz + hh / 2, pb - pa, 0.12, hh - 0.06, M_ASH)
            zz += hh
            kk += 1
        for zz in (fr_z if slits else ()):
            f.box(mb, 0.0, GLOW_OFF, zz - 0.3, 0.5, GLOW_T, 1.1, M_ROOM)
            f.box(mb, 0.0, PANE_OFF, zz + 0.55, 0.6, PANE_T, 0.7, M_PANE)
            f.box(mb, 0.0, -0.36, zz, 0.6, 0.05, 1.8, M_SHUT)
            for kk in (-1, 1):
                f.box(mb, kk * 0.47, 0.17, zz - 0.05, 0.3, 0.34, 1.9, M_DRESS)
                mb.beam(f.P(kk * 0.47, 0.17, zz + 0.84), f.P(0.0, 0.17, zz + 1.52), 0.46, 0.34, M_DRESS, 0.0)
            f.box(mb, 0.0, 0.2, zz + 1.56, 0.5, 0.4, 0.36, M_DRESS)
            f.box(mb, 0.0, 0.2, zz - 1.02, 1.1, 0.4, 0.2, M_CAP)
    for zz in (ZC0 + stories[0][1], ze - 1.2):
        _lathe(mb, (wp.x, wp.y, zz), [(r - 0.02, 0.0), (r + 0.24, 0.08), (r + 0.24, 0.3), (r - 0.02, 0.38)], M_CAP,
               8, rot8, caps=(False, False))
    for k in range(8):
        a = math.radians(45.0 * k)
        px_, py_ = wp.x + (ap + 0.16) * math.cos(a), wp.y + (ap + 0.16) * math.sin(a)
        mb.box((0.34, 0.5, 0.34), (px_, py_, zt1 - 0.62), (0, 0, a), M_DRESS, 0.0)
        px_, py_ = wp.x + (ap + 0.28) * math.cos(a), wp.y + (ap + 0.28) * math.sin(a)
        mb.box((0.52, 0.52, 0.3), (px_, py_, zt1 - 0.3), (0, 0, a), M_DRESS, 0.03)
    _lathe(mb, (wp.x, wp.y, zt1), [(r - 0.1, -0.02), (r + 0.5, 0.0), (r + 0.62, 0.14), (r + 0.62, 0.34),
                                    (r + 0.45, 0.46), (r - 0.1, 0.46)], M_CAP, 8, rot8, caps=(False, True))
    # LANTERNA: tambor octogonal recuado com 8 lancetas cegas (obsidiana) e cordao; depois a agulha
    zs0 = zt1 + 0.46
    hl = 2.4
    rl = r - 0.2
    _lathe(mb, (wp.x, wp.y, zs0), [(r + 0.2, 0.0), (r + 0.2, 0.12), (rl, 0.26), (rl, hl - 0.26), (r + 0.1, hl - 0.14),
                                    (r + 0.1, hl)], M_ASH, 8, rot8, caps=(False, True))
    apl = rl * math.cos(math.pi / 8)
    for k in range(8):
        a = math.radians(45.0 * k)
        cx_, cy_ = wp.x + (apl + 0.02) * math.cos(a), wp.y + (apl + 0.02) * math.sin(a)
        mb.box((0.16, 0.5, 1.2), (cx_, cy_, zs0 + 0.26 + 0.75), (0, 0, a), OBS, 0.0)
        mb.box((0.16, 0.36, 0.36), (cx_, cy_, zs0 + 0.26 + 1.35 + 0.08), (math.pi / 4, 0, a), OBS, 0.0)
    zs1 = zs0 + hl
    H = 14.0
    prof = [(r + 0.95, 0.0), (r + 0.95, 0.12), (r + 0.55, 0.42)]
    for j, fz in enumerate((0.16, 0.34, 0.56)):
        rr0 = (r + 0.55) * (1 - fz) + 0.24 * fz
        prof += [(rr0 + 0.18, H * fz - 0.02), (rr0 - 0.02, H * fz + 0.05)]
    prof += [(0.3, H - 0.4), (0.0, H)]
    _lathe(mb, (wp.x, wp.y, zs1), prof, rm, 8, rot8, caps=(True, False))
    finial_iron(mb, (wp.x, wp.y, zs1 + H - 0.35), 1.0)
    a_ = math.radians(out)
    nx_, ny_ = math.cos(a_), math.sin(a_)
    zl_ = zs1 + H * 0.2
    rl_ = (r + 0.55) * (1 - 0.2) + 0.24 * 0.2
    cp = Vector((wp.x + nx_ * (rl_ - 0.35), wp.y + ny_ * (rl_ - 0.35), zl_ + 0.55))
    mb.box((1.0, 1.0, 1.1), cp, (0, 0, a_), M_PL, 0.0)
    mb.box((0.1, 0.62, 0.62), cp + Vector((nx_ * 0.57, ny_ * 0.57, 0.0)), (0, 0, a_), M_SHUT, 0.0)   # postigo
    for kk in (-1, 1):
        mb.box((0.7, 1.4, 0.12), cp + Vector((nx_ * 0.1, ny_ * 0.1, 0.75)) + Vector((-ny_ * kk * 0.28,
                                                                                     nx_ * kk * 0.28, 0.0)),
               (0, -kk * math.radians(40.0), a_ + math.pi / 2), rm, 0.0)
    return (wp.x, wp.y, r, zt1)


# ------------------------------------------------------------------ as 7 casas (variacao DIRIGIDA pelo papel)
# coordenadas das chamines e lojas no LOTE (reais, +v = frente). A 1a chamine sobe da lareira (parede 'left').
SPECS = {
    # taverna "Estalagem da Lua Negra": terreo de cantaria com janelas triplas, andar em balanco com cruzes de Santo
    # Andre, 2 aguas-furtadas, chamine monumental dupla + a da cozinha, remates de ferro, par de lanternas
    "H1": dict(ground="stone", upper="timber", jetty=0.8, rise=9.0, dormers=[("+y", -4.8), ("+y", 4.8)],
               chimney=(-16.3, 3.0), chim_kind="twin", chim_h=3.0, chimney2=(12.0, -9.0), chim2_kind="stack",
               attic_all=True, win="cross", frame="cross", ridge="crest", dress="cob", lan_pair=True,
               stone_head="lintel", void=(-12.0, -3.0, -2.0, 9.0), roof="A"),
    # ferreiro: loja do lado do eixo, balanco com escoras em chevron, agua-furtada, chamine dupla
    "H2": dict(ground="stone", upper="timber", jetty=0.8, rise=8.4, shop=-9.4, dormers=[("+y", 3.6)],
               chimney=(-13.3, 1.0), chim_kind="twin", chimney2=(10.0, -8.0), chim2_kind="hood", attic_all=True,
               win="cross", frame="chevron", ridge="crest", dress="obc", lan_side=-1, roof="B",
               ground_kind="porch", door_style="plain"),
    # boticario: o TORREAO no canto do eixo (marco de quem chega), loja do outro lado, montantes cerrados, postigos
    "H3": dict(ground="stone", upper="timber", jetty=0.8, rise=8.6, turret=(-1, 1), shop=9.4,
               wins={0: {"front": [-9.8], "right": [7.2]},
                     1: {"front": [-8.54, 0.0, 8.54], "back": [-8.0, 8.0], "right": [-2.0], "left": [3.0]}},
               dormers=[("+y", 3.4)], chimney=(-13.3, 1.0), chim_kind="stack", chim_h=3.2, attic_all=True,
               win="cross", frame="studs", ridge="crest", dress="cbo", lan_side=-1, planter=True, roof="A",
               door_style="segmental", awning="cloth"),
    # oficina do minerador: empena gotica de frente, enxaimel inteiro com montantes cerrados, floreiras, chamine de
    # chapeu (forja pequena)
    "H4": dict(ground="timber", gable_front=True, rise=7.4, chimney=(-9.3, 1.0), chim_kind="hood", attic_all=True,
               win="cross", frame="studs", side_frame="studs", ridge="roll", dress="ocb", planter=True, lan_side=-1,
               roof="B"),
    # cartografo: pingadeira gotica nas janelas de pedra, postigos, loja do lado do eixo, 2 aguas-furtadas, montantes
    "H5": dict(ground="stone", upper="timber", jetty=0.8, rise=8.8, shop=9.4, dormers=[("+y", -3.6), ("+y", 3.6)],
               chimney=(-13.3, 1.0), chim_kind="stack", chimney2=(10.0, -8.0), chim2_kind="hood", attic_all=True,
               win="cross", frame="studs", ridge="roll", stone_head="label", shutters=True, dress="cob",
               lan_side=1, roof="B", door_style="label"),
    # casa da guarda: TODA de pedra, vergas com fecho, postigos, remates de ferro, chamine dupla (terrea)
    "H6": dict(ground="stone", rise=7.0, chimney=(-9.3, 1.0), chim_kind="twin", attic_all=True, win="cross",
               dormers=[("+y", 0.0)], wins={0: {"back": [-6.0, 6.0], "right": [0.0]}},
               ridge="crest", stone_head="lintel", shutters=True, dress="obc", lan_side=1, roof="A"),
    # mestre de armas: balanco com chevron, 2 aguas-furtadas, 2 chamines, postigos, janela a janela
    "H7": dict(ground="stone", upper="timber", jetty=0.8, rise=8.2, dormers=[("+y", -3.8), ("+y", 3.8)],
               chimney=(-13.3, 1.0), chim_kind="twin", chimney2=(10.0, -8.0), chim2_kind="stack", attic_all=True,
               win="cross", frame="chevron", ridge="crest", shutters=True, dress="boc", lan_side=-1, planter=True,
               roof="B", door_style="rustic", balcony=True),
}
GARDEN_THEME = {"H1": 1, "H2": 6, "H3": 3, "H4": 4, "H5": 9, "H6": 6, "H7": 1}
GROUPS = [("P1", ("H1", "H2", "H3", "H4")), ("P2", ("H5", "H6", "H7"))]


# ------------------------------------------------------------------ praca + fonte (cotas da agua do sg_core)
M_SLAB_A = "Stone_Paving_SG_B"   # lajes, tom A
M_SLAB_B = M_COB                 # lajes, tom B
M_ASHLAR = "Stone_SG_Block_B"    # cantaria dos aneis
M_JOINT = "Stone_SG_Floor"       # leito escuro das juntas
M_BASIN = "Stone_SG_Castle_B"    # parede e fundo da bacia
JOINT_D = 0.10                   # FINESSE 3 (03.02): junta rasa (0,10) num tom medio, nao um poco preto


def slab_ring(mb, c, r0, r1, n, z0, z1, m, a_off=0.0, gap=0.12, sub=1, skip=None):
    """lajes em setores de anel (tampo + lados, sem fundo nem bevel: o que le no Roblox e a junta em relevo)"""
    for k in range(n):
        if skip and skip(k):
            continue
        a0 = a_off + 2 * math.pi * k / n
        a1 = a_off + 2 * math.pi * (k + 1) / n
        ri, ro = r0 + gap / 2, r1 - gap / 2
        di, do = (gap / 2) / ri, (gap / 2) / ro
        outer = [(c[0] + ro * math.cos(a0 + do + (a1 - a0 - 2 * do) * j / sub),
                  c[1] + ro * math.sin(a0 + do + (a1 - a0 - 2 * do) * j / sub)) for j in range(sub + 1)]
        inner = [(c[0] + ri * math.cos(a1 - di - (a1 - a0 - 2 * di) * j / sub),
                  c[1] + ri * math.sin(a1 - di - (a1 - a0 - 2 * di) * j / sub)) for j in range(sub + 1)]
        mm = m(k) if callable(m) else m
        sett(mb, SL.ccw(outer + inner), z0, z1, mm)


def fountain_figure(mb, F, s, z0):
    """PONTO DE ENCAIXE do agente J (02.03, proxima onda): a figura PROPRIA da fonte (ninfa encapuzada com cantaro,
    ou a lua sobre pedestal com 4 bicas), no referencial F (local +Y = frente, virada para a chegada), escala s
    (altura ~7,3 s), pe da figura em z0 (local, acima do plinto). Base disponivel: disco de raio 1,02 no topo do
    plinto; a lamina d'agua da taca de cima fica 0,46 abaixo de z0 (hole_r 1,17).
    Enquanto isso (variante minima desta onda): o hooded_figure 'hood' em pedra CLARA (TrimLow) com o vazio do
    capuz em obsidiana, contra os guardioes ESCUROS da porta (nao repete o mesmo hero no eixo da chegada)."""
    import sg_court as CT
    CT.hooded_figure(mb, F, s, z0, "Stone_SG_TrimLow", OBS, kind="hood")


def fountain_statue(mb, x, y, zb, yaw, s=0.88):
    """coroamento da fonte: PLINTO octogonal de obsidiana nas cotas da agua (raio 1,15 <= hole_r 1,17 da taca de
    cima; zb = fundo da taca, a lamina fica 0,20 acima) com toro e filete, e a figura (fountain_figure)."""
    F = Frame(x, y, zb, yaw - math.pi / 2)
    EM._lathe(mb, (x, y, zb), [(1.15, 0.0), (1.15, 0.3), (1.3, 0.36), (1.32, 0.54), (1.2, 0.62), (1.02, 0.66)], OBS,
              8, math.pi / 8, caps=(False, True))
    fountain_figure(mb, F, s, 0.66)


def plaza():
    """praca R 26 (PLAZA_C). FINESSE 3 (02.04, 03.02): lajes em aneis de 2 tons SEM bevel, junta rasa (0,10) sobre o
    leito medio-escuro, anel de cantaria junto do degrau da fonte, rosacea de aneis, faixa de lajes RADIAIS e MEIO-FIO
    de cantaria de 0,8 em segmentos de 3 (0,16 acima das lajes, capa recuada) fechando o disco. O topo das lajes fica
    PAVE (0,30) acima do patamar (F5). A fonte e separada (fountain())."""
    rng = random.Random(4101)
    mb = MB("SG_Vil_Plaza", COLL, rng, detail="near")
    c = L.PLAZA_C
    R = L.PLAZA_R
    z = P1
    zt = z + PAVE
    zb = zt - JOINT_D
    mb.prism(SL.ccw(ngon(c, R - 0.05, 48)), z - 0.1, zb, M_JOINT)
    slab_ring(mb, c, 9.7, 10.7, 24, zb, zt + 0.03, M_ASHLAR, math.pi / 24, 0.12)
    for r0, r1, n, a in ((10.7, 12.6, 20, 0.0), (12.6, 14.5, 24, math.pi / 24), (14.5, 16.4, 28, 0.0)):
        slab_ring(mb, c, r0, r1, n, zb, zt, lambda k: M_SLAB_A if k % 3 != 1 else M_SLAB_B, a, 0.12)
    slab_ring(mb, c, 16.4, 17.3, 32, zb, zt + 0.03, M_ASHLAR, 0.0, 0.12)
    rings = (17.3, 19.8, 22.3)
    for i, (r0, r1) in enumerate(zip(rings, rings[1:])):
        n = int(round(2 * math.pi * (r0 + r1) / 2 / 4.0))
        slab_ring(mb, c, r0, r1, n, zb, zt, M_SLAB_A if i % 2 == 0 else M_SLAB_B, (math.pi / n) * (i % 2), 0.12)
    n = int(round(2 * math.pi * 23.75 / 2.5))                                   # faixa de lajes radiais
    slab_ring(mb, c, 22.3, 25.2, n, zb, zt, lambda k: M_SLAB_B if k % 4 == 2 else M_SLAB_A, 0.0, 0.12)
    nb = int(round(2 * math.pi * 25.6 / 3.0))                                   # meio-fio em segmentos de 3
    slab_ring(mb, c, 25.2, R, nb, z - 0.1, zt + 0.16, M_ASHLAR, 0.0, 0.1)
    ring_prism(mb, c, 25.4, R - 0.14, 48, zt + 0.16, zt + 0.21, M_ASHLAR)                # capa recuada (chanfro)
    mb.finish()
    # colisao do calcamento elevado (a bacia e do sg_col)
    try:
        SL.IL.col_poly("SG_VilPave", SL.ccw(ngon(c, R, 24)), zt - 1.0, zt, step=4.0, mode="inter")
    except Exception:
        col_box("SG_VilPave", (2 * R - 2, 2 * R - 2, 1.0), (c[0], c[1], zt - 0.5))
    fountain(rng)


def fountain(rng):
    """FINESSE 3 (02.02): fonte com ESCALA DE PRACA (pegada R 9,6 em vez de 7,55) sem mexer nas cotas da agua
    (sg_core.FOUNTAIN_*): 2 DEGRAUS (o de baixo em 12 blocos com junta, o de cima com bordo em toro), bacia em
    CANTARIA (nucleo escuro + 2 fiadas de blocos desencontrados entre 12 pilastras com base, fuste, gola e capitel),
    coping em toro, fuste com gola e bojo, tacas de perfil continuo e CARRANCAS nas 8 bicas. Colisao propria so dos
    degraus (o resto e o SG_Fountain do sg_col)."""
    mf = MB("SG_Vil_Fountain", COLL, rng, detail="near")
    c = L.PLAZA_C
    cx, cy = c
    z = P1
    rot = 0.0
    B, (T1, T2) = CORE.FOUNTAIN_BASIN, CORE.FOUNTAIN_BOWLS
    mf.prism(SL.ccw(ngon(c, 9.62, 12, rot)), z - 0.3, z + 0.45, M_JOINT)
    slab_ring(mf, c, 7.4, 9.6, 12, z - 0.1, z + 0.55, M_ASHLAR, rot, 0.1)                 # degrau de baixo (12 blocos)
    mf.prism(SL.ccw(ngon(c, 8.5, 12, rot)), z + 0.45, z + 0.95, M_ASHLAR)                 # degrau de cima
    EM._lathe(mf, (cx, cy, z), [(8.46, 0.5), (8.7, 0.66), (8.7, 0.84), (8.5, 0.99), (8.2, 0.99), (8.2, 0.5)], M_CAP,
              12, rot, closed=True)                                                        # bordo em toro
    ring_prism(mf, c, 6.05, 7.1, 12, z + 0.95, z + 2.4, M_JOINT, rot)                      # nucleo da parede
    ap = 7.1 * math.cos(math.radians(15.0))
    half = 7.1 * math.sin(math.radians(15.0)) - 0.6                                        # meio vao livre entre pilastras
    for k in range(12):
        a = math.radians(rot + 30.0 * k)
        px, py = c[0] + 7.02 * math.cos(a), c[1] + 7.02 * math.sin(a)
        mf.box((1.14, 1.14, 0.34), (px, py, z + 1.12), (0, 0, a), M_ASHLAR, 0.0)           # base
        mf.box((0.9, 0.9, 1.34), (px, py, z + 1.95), (0, 0, a), M_ASHLAR, 0.0)             # fuste
        mf.box((1.02, 1.02, 0.12), (px, py, z + 2.68), (0, 0, a), M_CAP, 0.0)              # gola
        mf.box((1.22, 1.22, 0.26), (px, py, z + 2.87), (0, 0, a), M_CAP, 0.06)             # capitel
        am = a + math.radians(15.0)
        nx, ny = math.cos(am), math.sin(am)
        tx, ty = -ny, nx
        fx, fy = c[0] + (ap + 0.06) * nx, c[1] + (ap + 0.06) * ny
        for (u0, u1, z0b, z1b) in ((-half, -0.04, 0.95, 1.6), (0.04, half, 0.95, 1.6), (-half, half, 1.66, 2.36)):
            uc = (u0 + u1) / 2
            mf.box((u1 - u0 - 0.06, 0.24, z1b - z0b - 0.06), (fx + tx * uc, fy + ty * uc, z + (z0b + z1b) / 2),
                   (0, 0, am + math.pi / 2), M_ASHLAR, 0.0)
    EM._lathe(mf, (cx, cy, z), [(5.88, 2.4), (7.32, 2.4), (7.46, 2.56), (7.46, 2.7), (7.3, 2.82), (5.98, 2.82),
                                (5.88, 2.7)], M_CAP, 12, rot, closed=True)                 # coping em toro
    mf.prism(SL.ccw(ngon(c, 6.1, 12, rot)), z + 0.95, z + B["floor"], M_BASIN)
    low = [(1.60, B["floor"] - 0.05), (1.60, 2.30), (1.50, 2.60), (1.15, 2.90), (0.95, 3.30), (1.30, 3.95),
           (0.90, 4.70), (0.86, 4.95), (1.10, 5.15), (2.00, 5.40), (2.80, 5.70), (3.16, 6.05), (3.20, 6.30),
           (2.96, 6.36), (2.86, 6.10), (2.80, T1["floor"])]
    EM._lathe(mf, (cx, cy, z), low, M_CAP, 16, math.pi / 16)
    up = [(0.62, T1["floor"] - 0.02), (0.62, 6.30), (0.46, 6.70), (0.70, 7.20), (0.92, 7.50), (0.55, 8.00),
          (1.15, 8.40), (1.60, 8.74), (1.74, 8.92), (1.66, 9.10), (1.50, 9.06), (1.42, T2["floor"])]
    EM._lathe(mf, (cx, cy, z), up, M_CAP, 16, math.pi / 16)
    for bowl, deg, r_tip, r_land, dst in CORE.FOUNTAIN_SPOUTS:
        tb = CORE.FOUNTAIN_BOWLS[bowl - 1]
        a = math.radians(deg)
        r_in = tb["radius"] - 0.05
        wd = 0.56 if bowl == 1 else 0.4
        ln = r_tip - r_in
        rm_ = (r_in + r_tip) / 2
        zt2 = z + tb["level"] - 0.04
        ca, sa = math.cos(a), math.sin(a)
        mf.box((ln, wd, 0.16), (cx + ca * rm_, cy + sa * rm_, zt2 - 0.08), (0, 0, a), M_CAP, 0.03)
        for sd in (-1, 1):
            ox, oy = -sa * sd * (wd / 2 - 0.05), ca * sd * (wd / 2 - 0.05)
            mf.box((ln - 0.06, 0.1, 0.12), (cx + ca * (rm_ - 0.03) + ox, cy + sa * (rm_ - 0.03) + oy, zt2 + 0.05),
                   (0, 0, a), M_CAP, 0.02)
        # CARRANCA sob a bica: cabeca em bloco chanfrado na borda da taca, sobrancelha, 2 olhos e boca de obsidiana
        hs = 1.0 if bowl == 1 else 0.72
        rh = r_tip - 0.3 * hs
        hx, hy = cx + ca * rh, cy + sa * rh
        zh = zt2 - 0.3 * hs
        mf.box((0.5 * hs, 0.6 * hs, 0.5 * hs), (hx, hy, zh), (0, 0, a), M_CAP, 0.07 * hs)
        mf.box((0.2 * hs, 0.66 * hs, 0.1 * hs), (hx + ca * 0.18 * hs, hy + sa * 0.18 * hs, zh + 0.2 * hs), (0, 0, a),
               M_CAP, 0.02)
        for sd in (-1, 1):
            mf.box((0.08 * hs, 0.13 * hs, 0.09 * hs), (hx + ca * 0.24 * hs - sa * sd * 0.16 * hs,
                                                       hy + sa * 0.24 * hs + ca * sd * 0.16 * hs, zh + 0.08 * hs),
                   (0, 0, a), OBS, 0.0)
        mf.box((0.1 * hs, 0.3 * hs, 0.1 * hs), (hx + ca * 0.24 * hs, hy + sa * 0.24 * hs, zh - 0.15 * hs), (0, 0, a),
               OBS, 0.0)
    fountain_statue(mf, cx, cy, z + T2["floor"], -math.pi / 2, 0.88)
    mf.finish()
    # colisao propria dos 2 degraus (octogono: 4 caixas cada; a parede/bacia e o SG_Fountain do sg_col)
    SL.ngon_col("SG_VilFountStep", cx, cy, 8, 9.2, z - 1.0, z + 0.75)


# ------------------------------------------------------------------ ruas: lajes com junta, meio-fio, caminhos
AXIS_BY_VILLAGE = True          # o eixo no P1/P2 (x = 0) e desenhado aqui (o P3 e do patio, sg_court)
CURB_PROF = [(-0.3, -0.3), (0.3, -0.3), (0.3, 0.14), (-0.3, 0.3)]
# FINESSE 3 (03.02): 3 ou 4 lajes por fiada em MODULOS IRREGULARES DIRIGIDOS que mudam de fiada para fiada (nenhuma
# junta cai entre 0,44 e 0,56 da largura: nada de "faixa central de rodovia")
ROW_SPLITS = ((0.31, 0.62), (0.22, 0.57, 0.80), (0.41, 0.71), (0.27, 0.60), (0.36, 0.68), (0.43, 0.76))
ROW_SPLITS_WIDE = ((0.42,), (0.6,), (0.36, 0.7), (0.58,), (0.4,), (0.3, 0.64))     # P3 (lajes largas)
def _street_list():
    out = []
    for i, (pts, w, z) in enumerate(L.STREETS):
        pts = list(pts)
        axis = all(abs(p[0]) < 1e-6 for p in pts)
        if axis and (z == P3 or not AXIS_BY_VILLAGE):
            continue
        out.append((i, pts, w, z))
    return out


def _in_other_street(x, y, me, streets, pad=0.4):
    for i, pts, w, z in streets:
        if i == me:
            continue
        if L.polyline_dist(x, y, pts) < w / 2 + pad:
            return True
    return False


def _blocked_curb(x, y, z):
    if math.hypot(x - L.PLAZA_C[0], y - L.PLAZA_C[1]) < L.PLAZA_R + 0.3:
        return True
    if math.hypot(x - L.CRAFT_C[0], y - L.CRAFT_C[1]) < L.CRAFT_R + 0.5:
        return True
    for nm, foot, deg, w, n, tread, g in L.STAIRS:
        a = math.radians(deg)
        ux, uy = math.cos(a), math.sin(a)
        t = (x - foot[0]) * ux + (y - foot[1]) * uy
        dd = abs(-(x - foot[0]) * uy + (y - foot[1]) * ux)
        if -tread - 1.5 <= t <= tread * n + 1.5 and dd <= w / 2 + 1.4:
            return True
    for p in door_paths():
        if L.polyline_dist(x, y, [p[0], p[1]]) < p[2] / 2 + 0.6:
            return True
    zz = L.zone_of(x, y)
    return zz is None or abs(zz - z) > 0.1


def _offset_line(pts, off):
    out = []
    n = len(pts)
    for i in range(n):
        x, y = pts[i]
        if i == 0:
            dx, dy = pts[1][0] - x, pts[1][1] - y
        elif i == n - 1:
            dx, dy = x - pts[i - 1][0], y - pts[i - 1][1]
        else:
            ax, ay = x - pts[i - 1][0], y - pts[i - 1][1]
            bx, by = pts[i + 1][0] - x, pts[i + 1][1] - y
            la, lb = math.hypot(ax, ay) or 1, math.hypot(bx, by) or 1
            dx, dy = ax / la + bx / lb, ay / la + by / lb
        ln = math.hypot(dx, dy) or 1.0
        out.append((x - dy / ln * off, y + dx / ln * off))
    return out


def _simplify_line(pts, eps=0.02):
    """tira os pontos colineares de uma polilinha (a sarjeta e um prisma de poucos vertices)"""
    out = [pts[0]]
    for i in range(1, len(pts) - 1):
        ax, ay = pts[i][0] - out[-1][0], pts[i][1] - out[-1][1]
        bx, by = pts[i + 1][0] - pts[i][0], pts[i + 1][1] - pts[i][1]
        la, lb = math.hypot(ax, ay) or 1.0, math.hypot(bx, by) or 1.0
        if abs(ax * by - ay * bx) / (la * lb) > eps:
            out.append(pts[i])
    out.append(pts[-1])
    return out


def _resample(pts, step):
    out = [pts[0]]
    for a, b in zip(pts, pts[1:]):
        ln = math.hypot(b[0] - a[0], b[1] - a[1])
        k = max(1, int(ln / step))
        for i in range(1, k + 1):
            out.append((a[0] + (b[0] - a[0]) * i / k, a[1] + (b[1] - a[1]) * i / k))
    return out


def _row_poly(la, lb, ra, rb, t0, t1, g=0.05):
    def lerp(p, q, t):
        return (p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t)
    ln = max(0.2, math.hypot(lb[0] - la[0], lb[1] - la[1]))
    ga = g / ln
    a0, a1 = lerp(la, lb, ga), lerp(la, lb, 1 - ga)
    b0, b1 = lerp(ra, rb, ga), lerp(ra, rb, 1 - ga)
    return [lerp(a0, b0, t0), lerp(a1, b1, t0), lerp(a1, b1, t1), lerp(a0, b0, t1)]


def sett(mb, poly, z0, z1, m):
    """laje de calcamento: tampo + 4 faces (sem fundo)"""
    bm = mb.bm
    lo = [bm.verts.new((p[0], p[1], z0)) for p in poly]
    hi = [bm.verts.new((p[0], p[1], z1)) for p in poly]
    n = len(poly)
    bm.faces.new(hi)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((lo[i], lo[j], hi[j], hi[i]))
    mb._post(lo + hi, m, None, 0, 1)


_DOOR_PATHS = []


def door_paths():
    """caminho de lajes da rua ate a porta de cada casa: (ponto na rua, ponto na soleira, largura, z)"""
    if not hasattr(L, "HOUSES"):
        return []
    if _DOOR_PATHS:
        return _DOOR_PATHS
    out = _DOOR_PATHS
    for hrec in L.HOUSES:
        nm, tp, x, y, w, d, deg, z = hrec
        F = lot_frame(hrec)
        a = F.p(0.0, d / 2 + 0.45)
        fx, fy = math.cos(math.radians(deg)), math.sin(math.radians(deg))
        # anda ate a borda da rua mais proxima (qualquer rua do mesmo nivel)
        best = None
        for pts, sw, sz in L.STREETS:
            if abs(sz - z) > 0.1:
                continue
            for t in range(0, 60):
                px, py = a.x + fx * t, a.y + fy * t
                if L.polyline_dist(px, py, pts) < sw / 2:
                    if best is None or t < best:
                        best = t
                    break
        ln = (best if best is not None else 8) + 0.5
        out.append(((a.x + fx * ln, a.y + fy * ln), (a.x, a.y), 9.0, z))
    return out


def pave_strip(mb, pts, w, z, row=4.0, skip=None, tone=0, splits=ROW_SPLITS):
    """faixa de lajes ao longo de pts (largura w): fiadas transversais de ~row com 3 ou 4 lajes em modulos
    irregulares DIRIGIDOS (ROW_SPLITS, mudando a cada fiada: nunca uma junta central continua), 2 tons por laje
    (2/3 A, 1/3 B em ritmo fixo); topo em z + PAVE, junta de 0,12 de largura e JOINT_D (0,10) de fundo sobre o leito
    medio-escuro (03.02)"""
    core = _resample(pts, row)
    hw = w / 2
    Lo, Ro = _offset_line(core, hw), _offset_line(core, -hw)
    g = 0.12
    gt = (g / 2) / w
    for j in range(len(core) - 1):
        mx, my = (core[j][0] + core[j + 1][0]) / 2, (core[j][1] + core[j + 1][1]) / 2
        if skip and skip(mx, my):
            continue
        cuts = [0.0] + list(splits[(j + tone) % len(splits)]) + [1.0]
        for i, (t0, t1) in enumerate(zip(cuts, cuts[1:])):
            m = M_SLAB_A if ((j // 2) + i + tone) % 3 != 1 else M_SLAB_B
            a = t0 + (gt if t0 > 0.0 else 0.0)
            b = t1 - (gt if t1 < 1.0 else 0.0)
            sett(mb, SL.ccw(_row_poly(Lo[j], Lo[j + 1], Ro[j], Ro[j + 1], a, b, g / 2)), z + PAVE - JOINT_D, z + PAVE, m)


def street_col(pts, w, z):
    for a, b in zip(pts, pts[1:]):
        ln = math.hypot(b[0] - a[0], b[1] - a[1])
        if ln < 0.5:
            continue
        yaw = math.atan2(b[1] - a[1], b[0] - a[0])
        col_box("SG_VilPave", (ln + (w if len(pts) > 2 else 0.0), w, 1.0), ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2,
                                                                            z + PAVE - 0.5), (0, 0, yaw))


def streets():
    """ruas (03.02): lajes com junta rasa em modulos irregulares (pave_strip), leito medio-escuro 0,10 abaixo do topo,
    SARJETA rasa (0,52 de largura, 0,08 abaixo das lajes, tom B) e MEIO-FIO de cantaria chanfrado em pecas de ~6,6
    (0,16 acima das lajes) nas 2 bordas; caminhos de lajes da rua ate cada porta; colisao do calcamento elevado"""
    rng = random.Random(4102)
    sl = _street_list()
    objs = {P1: MB("SG_Vil_Streets_P1", COLL, rng, detail="near"), P2: MB("SG_Vil_Streets_P2", COLL, rng, detail="near"),
            P3: MB("SG_Vil_Streets_P3", COLL, rng, detail="near")}
    for i, pts, w, z in sl:
        mb = objs[z]
        base = SL.ccw(SL.ribbon_poly(pts, w / 2 - 0.05))
        mb.prism(base, z + PAVE - 0.3, z + PAVE - JOINT_D, M_JNT)
        hw = w / 2 - (1.15 if z != P3 else 0.1)

        pave_strip(mb, pts, 2 * hw, z, row=(8.0 if z == P3 else 6.2), splits=(ROW_SPLITS_WIDE if z == P3 else
                                                                               ROW_SPLITS), skip=lambda mx, my, i=i: (
            math.hypot(mx - L.PLAZA_C[0], my - L.PLAZA_C[1]) < L.PLAZA_R + 0.4 or
            math.hypot(mx - L.CRAFT_C[0], my - L.CRAFT_C[1]) < L.CRAFT_R + 0.4 or
            _in_other_street(mx, my, i, [s for s in sl if s[0] < i], pad=-0.5)), tone=i)
        street_col(pts, w, z)
        if z == P3:
            continue
        for side in (-1, 1):
            line = _resample(_offset_line(pts, side * (w / 2 - 0.3)), 1.1)
            runs, run = [], []
            for p in line:
                if _blocked_curb(p[0], p[1], z) or _in_other_street(p[0], p[1], i, sl, pad=0.2):
                    if len(run) > 1:
                        runs.append(run)
                    run = []
                else:
                    run.append(p)
            if len(run) > 1:
                runs.append(run)
            prof = list(CURB_PROF) if side > 0 else [(-a_, b_) for a_, b_ in CURB_PROF]
            prof = SL.ccw(prof)
            for run in runs:
                # sarjeta: faixa continua 0,6 para dentro do meio-fio, 0,08 abaixo das lajes
                gut = _offset_line(_simplify_line(run), -side * 0.6)
                if len(gut) >= 2:
                    mb.prism(SL.ccw(SL.ribbon_poly(gut, 0.26)), z + PAVE - 0.3, z + PAVE - 0.08, M_SLAB_B)
                k = 0
                while k < len(run) - 1:
                    j = min(len(run) - 1, k + 8)
                    if len(run) - 1 - j <= 3:
                        j = len(run) - 1
                    a, b = run[k], run[j]
                    ln = math.hypot(b[0] - a[0], b[1] - a[1])
                    if ln > 0.4:
                        ux, uy = (b[0] - a[0]) / ln, (b[1] - a[1]) / ln
                        pa = (a[0] + ux * 0.04, a[1] + uy * 0.04, z + PAVE - 0.14)
                        pb = (b[0] - ux * 0.04, b[1] - uy * 0.04, z + PAVE - 0.14)
                        mb.sweep([pa, pb], prof, M_DRESS, True, None)
                    k = j
    # caminhos das portas (lajes largas, 3 por fiada) + colisao
    for (pa, pb, pw, z) in door_paths():
        mb = objs[z] if z in objs else objs[P1]
        mb.prism(SL.ccw(SL.ribbon_poly([pa, pb], pw / 2 - 0.05)), z + PAVE - 0.3, z + PAVE - JOINT_D, M_JNT)
        pave_strip(mb, [pa, pb], pw - 0.2, z, row=4.4, tone=1)
        street_col([pa, pb], pw, z)
    for o in objs.values():
        o.finish()


def stairs_p1p2():
    """escada P1 -> P2 (so visual; a colisao e do sg_col): degraus do kit, BANZO continuo com capa e mureta de
    cantaria na borda do P2 dos 2 lados"""
    rng = random.Random(4105)
    ms = MB("SG_Vil_StairP1P2", COLL, rng, detail="near")
    SL.plan_stair(ms, "P1P2", m="Stone_SG_Block_B", side_m=M_ASH, stringers=False, riser_m=M_ASH)
    foot, deg, w, n, tread, g = L.stair_frame("P1P2")
    ytop = foot[1] + tread * n
    for s in (-1, 1):
        stair_banzo(ms, s)
        vil_parapet(ms, [(s * (w / 2 + 1.0), ytop + 0.55), (s * (w / 2 + 12.0), ytop + 0.55)], P2, ends=(False, True))
    ms.finish()


def stair_banzo(mb, s):
    import sg_entry as SE
    foot, deg, w, n, tread, g = L.stair_frame("P1P2")
    rise = (L.STAIR_TOP_Z["P1P2"] - foot[2]) / n
    ya, yb = foot[1], foot[1] + tread * n
    ta, tb = foot[2] + 1.25, L.STAIR_TOP_Z["P1P2"] + 1.25
    k = (tb - ta) / (yb - ya)
    x0, x1 = sorted((s * (w / 2), s * (w / 2 + 1.4)))
    zb = foot[2] - 0.3
    hs = (1.0, 0.8)
    c0, ci = zb, 0
    while c0 < tb - 0.05:
        c1 = min(c0 + hs[ci % 2], tb)
        if c1 <= ta:
            poly = [(ya, c0), (yb, c0), (yb, c1), (ya, c1)]
        else:
            ys0 = ya + max(0.0, (c0 - ta) / k)
            ys1 = ya + (c1 - ta) / k
            poly = [(ys0, c0), (yb, c0), (yb, c1), (ys1, c1)]
            if c0 < ta:
                poly.append((ya, ta))
        L0 = 3.4
        off = (0.0, 1.7)[ci % 2]
        cuts = [ya] + [ya + off + L0 * j for j in range(1, 9) if ya + off + L0 * j < yb - 0.8] + [yb]
        for u0, u1 in zip(cuts, cuts[1:]):
            bp = SE._dedupe(SE._clip_y(poly, u0 + 0.04, u1 - 0.04))
            if len(bp) >= 3 and abs(SL.area(bp)) > 0.2 and max(p[0] for p in bp) - min(p[0] for p in bp) > 0.3:
                SE.yz_block(mb, x0, x1, bp, M_ASH, 0.0)
        c0, ci = c1, ci + 1

    def zn(y):
        return foot[2] + rise + (y - ya) * rise / tread
    xr = s * (w / 2 + 0.06)
    ra, rb = ya + 0.1, yb - 0.1
    mb.beam((xr, ra, zn(ra) + 0.36), (xr, rb, zn(rb) + 0.36), 0.14, 0.5, M_DRESS, 0.0)

    def zl(y):
        return ta + k * (y - ya)
    xm = s * (w / 2 + 0.7)
    A = Vector((xm, ya - 0.2, zl(ya - 0.2)))
    B = Vector((xm, yb + 0.3, zl(yb + 0.3)))
    dd = B - A
    nseg = max(1, int(round(dd.length / 2.5)))
    for j in range(nseg):
        p0 = A + dd * (j / nseg) + dd.normalized() * (0.03 if j else 0.0)
        p1 = A + dd * ((j + 1) / nseg) - dd.normalized() * (0.03 if j < nseg - 1 else 0.0)
        mb.beam((p0.x, p0.y, p0.z + 0.26), (p1.x, p1.y, p1.z + 0.26), 1.75, 0.32, M_CAP, 0.06)
    mb.beam((xm, A.y + 0.1, A.z + 0.1 * k + 0.04), (xm, B.y - 0.1, B.z - 0.1 * k + 0.04), 1.56, 0.12, M_CAP, 0.0)
    SE._post(mb, s * (w / 2 + 1.0), ya - 0.1, foot[2] + PAVE, 1.5, 2.9, lamp=False)


def vil_parapet(mb, pts, z, h=1.35, th=0.95, ends=(True, True)):
    import sg_entry as SE
    n = len(pts)
    for i in range(n - 1):
        a, b = Vector((pts[i][0], pts[i][1], 0.0)), Vector((pts[i + 1][0], pts[i + 1][1], 0.0))
        d = (b - a).normalized()
        ea = a - d * (th / 2 if i > 0 else 0.0)
        eb = b + d * (th / 2 if i < n - 2 else 0.0)
        Ls = (eb - ea).length
        mb.beam((ea.x, ea.y, z + h / 2), (eb.x, eb.y, z + h / 2), th - 0.12, h, M_JNT, 0.0)
        mb.beam((ea.x, ea.y, z + 0.18), (eb.x, eb.y, z + 0.18), th + 0.28, 0.36, M_DRESS, 0.05)
        L0 = 2.4
        cuts = [0.0] + [L0 * j for j in range(1, 40) if 0.6 < L0 * j < Ls - 0.6] + [Ls]
        for u0, u1 in zip(cuts, cuts[1:]):
            p0 = ea + d * (u0 + (0.04 if u0 > 0 else 0.0))
            p1 = ea + d * (u1 - (0.04 if u1 < Ls else 0.0))
            mb.beam((p0.x, p0.y, z + (0.36 + h) / 2), (p1.x, p1.y, z + (0.36 + h) / 2), th, h - 0.36 - 0.07, M_ASH,
                    0.0)
        mb.beam((ea.x, ea.y, z + h + 0.05), (eb.x, eb.y, z + h + 0.05), th + 0.14, 0.1, M_CAP, 0.0)
        k = max(1, int(round(Ls / 2.4)))
        for j in range(k):
            p0 = ea + d * (Ls * j / k + (0.03 if j else 0.0))
            p1 = ea + d * (Ls * (j + 1) / k - (0.03 if j < k - 1 else 0.0))
            mb.beam((p0.x, p0.y, z + h + 0.24), (p1.x, p1.y, z + h + 0.24), th + 0.34, 0.28, M_CAP, 0.06)
    for e, p in zip(ends, (pts[0], pts[-1])):
        if e:
            SE._post(mb, p[0], p[1], z, 1.4, h + 0.5, lamp=False)


# ------------------------------------------------------------------ arco de ferro no topo da escada P1P2 (2 luzes)
def iron_arch(mb, cx, y, z, hs, post_h=10.0, rise=5.4, area="SG_VilLamp"):
    import sg_court as CT
    lan = []
    prof_sq = [(-0.05, -0.05), (0.05, -0.05), (0.05, 0.05), (-0.05, 0.05)]
    for s in (-1, 1):
        x = cx + s * hs
        mb.box((1.4, 1.4, 0.35), (x, y, z + 0.175), (0, 0, 0), OBS, 0.05)
        H = post_h - 0.35
        h1 = H * 0.36
        prof = [(0.55, 0.0), (0.55, 0.12), (0.46, 0.2), (0.5, 0.32), (0.34, 0.5), (0.24, 1.2),
                (0.22, h1 - 0.12), (0.3, h1 - 0.05), (0.3, h1 + 0.06), (0.21, h1 + 0.14), (0.18, H - 0.5),
                (0.26, H - 0.42), (0.26, H - 0.3), (0.2, H - 0.24), (0.3, H - 0.1), (0.42, H + 0.02),
                (0.42, H + 0.26), (0.3, H + 0.34)]
        _lathe(mb, (x, y, z + 0.35), prof, BIRON, 6, math.pi / 6, caps=(False, True))
        cxv, czv = x - s * 0.62, z + post_h - 0.55
        pts = []
        for i in range(11):
            a = math.pi * 1.5 * i / 10
            rr = 0.62 * (1 - 0.55 * i / 10)
            pts.append((cxv + s * rr * math.cos(a), y, czv + rr * math.sin(a)))
        mb.sweep(pts, prof_sq, BIRON, True, None, up=(0.0, 1.0, 0.0))
        ax = x - s * 1.25
        mb.beam((x - s * 0.2, y, z + 8.9), (ax + s * 0.1, y, z + 8.9), 0.12, 0.15, BIRON, 0.0)
        pts = []
        for i in range(6):
            a = (math.pi / 2) * i / 5
            pts.append((x - s * (0.22 + 0.8 * (1 - math.cos(a))), y, z + 8.15 + 0.7 * math.sin(a)))
        mb.sweep(pts, prof_sq, BIRON, True, None, up=(0.0, 1.0, 0.0))
        _lathe(mb, (ax, y, z + 8.95), [(0.08, 0.0), (0.12, 0.08), (0.08, 0.18), (0.0, 0.24)], BIRON, 6)
        sl = 0.62
        zb_ = z + 8.55 - 2.30 * sl
        mb.rod((ax, y, z + 8.9), (ax, y, z + 8.5), 0.04, BIRON, 4)
        lan.append(EM.lantern_head(mb, mb, (ax, y, zb_ + EM.LH_BASE * sl), 0.0, sl))
        col_box(area, (1.4, 1.4, post_h + 1.0), (x, y, z + (post_h + 1.0) / 2))
    zs = z + post_h + 0.35
    for off, rad in ((0.0, 0.18), (-0.95, 0.12)):
        for s in (-1, 1):
            p = CT.bez((cx + s * hs, off), (cx + s * hs, 0.52 * rise + off), (cx + s * 0.33 * hs, 0.86 * rise + off),
                       (cx, rise + off), 10)
            pr = [(rad * math.cos(2 * math.pi * i / 6), rad * math.sin(2 * math.pi * i / 6)) for i in range(6)]
            mb.sweep([(px, y, zs + pz) for px, pz in p], pr, BIRON, True, None, up=(0.0, 1.0, 0.0))
    for s in (-1, 1):
        o = CT.bez((cx + s * hs, 0.0), (cx + s * hs, 0.52 * rise), (cx + s * 0.33 * hs, 0.86 * rise), (cx, rise), 10)
        i_ = CT.bez((cx + s * hs, -0.95), (cx + s * hs, 0.52 * rise - 0.95), (cx + s * 0.33 * hs, 0.86 * rise - 0.95),
                    (cx, rise - 0.95), 10)
        for t in (3, 6, 8):
            mb.beam((o[t][0], y, zs + o[t][1] - 0.1), (i_[t][0], y, zs + i_[t][1] + 0.08), 0.1, 0.1, BIRON, 0.0)
    finial_iron(mb, (cx, y, zs + rise + 0.05), 0.75, BIRON)
    _lathe(mb, (cx, y, zs + rise - 2.3), [(0.0, 0.0), (0.16, 0.18), (0.24, 0.42), (0.18, 0.66), (0.06, 0.86),
                                           (0.05, 1.35)], "Metal_SG_Silver", 8)
    return lan


def lamps(mb=None):
    rng = random.Random(4103)
    own = mb is None
    mb = mb or MB("SG_Vil_Lamps", COLL, rng, detail="near")
    foot, deg, w, n, tread, g = L.stair_frame("P1P2")
    ya = foot[1] + tread * n + 2.85
    lan = iron_arch(mb, 0.0, ya, P2 + PAVE, w / 2 + 1.6)
    for i, (x, y, zc) in enumerate(lan):
        light("L_SGVil_Lamp_%02d" % i, "POINT", (x, y, zc), 260.0, (1.0, 0.7, 0.4), 0.4)
    if own:
        mb.finish()


# ------------------------------------------------------------------ canteiros de pedra na frente das casas (vazios)
def front_beds(mb, hrec, spec):
    """2 canteiros baixos de cantaria ladeando o caminho da porta (terra solta; a grama e as flores sao da onda 2).
    O lado da loja fica sem canteiro (o balcao sai 2,0 da fachada)."""
    nm, tp, x, y, w, d, deg, z = hrec
    F = lot_frame(hrec)
    v0, v1 = d / 2 + 1.3, d / 2 + 4.9
    if spec.get("jetty"):
        v0 = d / 2 + 1.3
    for side in (-1, 1):
        if spec.get("shop") is not None and (spec["shop"] > 0) == (side > 0):
            continue
        if spec.get("ground_kind") == "porch" and side > 0:
            continue
        u0, u1 = side * 6.2, side * (w / 2 - 1.6)
        if spec.get("turret") and side * spec["turret"][0] > 0:
            u1 = side * (w / 2 - 7.5)
        a, b = sorted((u0, u1))
        if b - a < 3.0:
            continue
        cu, cv = (a + b) / 2, (v0 + v1) / 2
        lu, lv = b - a, v1 - v0
        # meio-fio em 4 pecas (capa de remate) + terra 0,35 acima do patamar
        for (pu, pv, su, sv) in ((cu, v0 + 0.3, lu, 0.6), (cu, v1 - 0.3, lu, 0.6), (a + 0.3, cv, 0.6, lv - 1.2),
                                 (b - 0.3, cv, 0.6, lv - 1.2)):
            mb.box((su, sv, 0.78), F.p(pu, pv, 0.29), F.r(), M_CAP, 0.0)
        mb.box((lu - 1.2, lv - 1.2, 0.33), F.p(cu, cv, 0.02 + 0.165), F.r(), M_DIRT, 0.0)


def tavern_sign(mb, F, u, v, z):
    """placa da Estalagem da Lua Negra: braco de ferro com mao-francesa saindo da fachada, 2 correntes, tabua com
    moldura e o CRESCENTE de prata recortado (dos 2 lados)"""
    p0 = F.p(u, v, z)
    p1 = F.p(u, v + 4.4, z)
    mb.beam(p0, p1, 0.24, 0.3, IRON, 0.0)
    mb.beam(F.p(u, v, z - 2.4), F.p(u, v + 2.6, z - 0.05), 0.2, 0.2, IRON, 0.0)
    mb.box((0.9, 0.3, 1.9), F.p(u, v + 0.15, z - 1.0), F.r(), IRON, B_CAST)
    _lathe(mb, tuple(F.p(u, v + 4.5, z - 0.15)), [(0.2, 0.0), (0.2, 0.2), (0.0, 0.5)], IRON, 6)
    cy = v + 2.5
    bw, bh = 3.4, 2.4
    zc = z - 0.9 - bh / 2
    for k in (-1, 1):
        mb.rod(F.p(u, cy + k * 1.3, z - 0.15), F.p(u, cy + k * 1.3, zc + bh / 2), 0.05, IRON, 4)
    mb.box((0.36, bw, bh), F.p(u, cy, zc), F.r(), WOOD, 0.06)
    mb.box((0.46, bw + 0.2, 0.22), F.p(u, cy, zc + bh / 2), F.r(), WOOD, 0.03)
    mb.box((0.46, bw + 0.2, 0.22), F.p(u, cy, zc - bh / 2), F.r(), WOOD, 0.03)
    # crescente: arco externo menos arco interno deslocado (poligono), dos 2 lados da tabua
    R, r, off = 0.95, 0.8, 0.42
    pts = [(R * math.cos(math.radians(a)), R * math.sin(math.radians(a))) for a in range(40, 321, 20)]
    ins = []
    for a in range(300, 59, -20):
        ins.append((off + r * math.cos(math.radians(a)), r * math.sin(math.radians(a))))
    poly = pts + [q for q in ins if math.hypot(q[0], q[1]) <= R + 1e-3]
    for sd in (-1, 1):
        nv = Vector((0.0, 0.0, 0.0))
        o = F.p(u + sd * 0.19, cy, zc)
        eu = Vector((math.cos(F.a + math.pi / 2), math.sin(F.a + math.pi / 2), 0.0))
        nvec = Vector((math.cos(F.a), math.sin(F.a), 0.0)) * sd
        poly_slab(mb, [(-x_, y_) if sd > 0 else (x_, y_) for x_, y_ in poly], (o + nvec * 0.08, eu,
                                                                               Vector((0, 0, 1)), nvec), 0.08,
                  "Metal_SG_Silver")


# ------------------------------------------------------------------ build
def build():
    import sg_village_int as VI
    plaza()
    streets()
    stairs_p1p2()
    rng = random.Random(4100)
    LIFE[0] = MB("SG_Vil_HouseDress", COLL, random.Random(4104), detail="near")
    lamps(LIFE[0])
    beds = MB("SG_Vil_Beds", COLL, random.Random(4106), detail="near")
    recs = {h[0]: h for h in L.HOUSES}
    for gname, names in GROUPS:
        mb = MB("SG_Vil_Houses_%s" % gname, COLL, rng, detail="near")
        for nm in names:
            hrec = recs[nm]
            spec = SPECS[nm]
            F = lot_frame(hrec)
            GARDEN_HOUSE[0] = GARDEN_THEME.get(nm, 1)
            with KitXF([mb, LIFE[0]], F):
                info = kit_house(mb, hrec, spec)
            VI.interior(mb, hrec, spec, info)
            if nm == "H1":
                tavern_sign(LIFE[0], F, 8.4, hrec[5] / 2, 12.6)
            front_beds(beds, hrec, spec)
        mb.finish()
    LIFE[0].finish()
    LIFE[0] = None
    beds.finish()
