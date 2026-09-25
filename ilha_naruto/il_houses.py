# il_houses - zona "houses" da Ilha 1 (Naruto / Vila da Folha). Substitui il_blockout.houses().
# RODADA 2 (critica: "hierarquia comprimida, tipologia aleatoria, casas competem com o trio do salao"):
#   * casas comuns BAIXAS de 1 pavimento: beiral ~8 e cumeeira <= 14,2 acima do chao (ponteiras <= 15), bem abaixo
#     dos predios redondos azuis (~25) e do salao (~33). UMA familia so: soco de pedra, reboco, madeira escura so
#     nos cunhais e na faixa do beiral, janelas de caixilho quente, telhado de 4 aguas com canais de telha em relevo
#     e espigoes escuros. A variacao vem do tamanho, de um anexo baixo, de alpendres de janela e da cor do telhado:
#     10 terracota + 2 verdes (T1 38,107 e leste 136,36), NENHUM azul (azul e so dos predios redondos da vila).
#     Uma unica casa com mirante: a do T2 oeste (-98,160).
#   * UM objeto por casa (VIL_House_T1_01.., VIL_House_T2_0x, VIL_House_East_0x, VIL_House_Upper_0x): cada um vira
#     um Model atomico no streaming (export_ilha.atomic).
#   * plato do paredao (patamar B do TER_Back_Massif, z 71,88): 2 casinhas agrupadas a oeste + 1 pagode a leste,
#     recuados para y 198-215 e desencontrados em y; nada atras do salao (x -30..30).
#   * MOINHO DE MINERIO / Posto do Minerador (ENTRAVEL) em L.MILL (ver secao do moinho).
# Casa NAO entravel: SEM PORTA nenhuma. Colisao em caixas simples (corpo + aguas do telhado).
# Regras tecnicas (HMB): chanfro 0 em peca com menor dimensao < 1,0 e <= 5% dela no resto; pecas com todas as
# dimensoes < 0,35 nao sao criadas; >= 0,1 de folga entre faces paralelas de materiais diferentes.
import math, random
from mathutils import Vector
import il_lib as IL
from il_lib import MB, S, col_box, col_box2, mk, light
import il_layout as L
import fm_lib
import fm_parts as FP

# ------------------------------------------------------------------ materiais novos da zona (<= 5)
_M = fm_lib.MATS
_M.setdefault("Plaster_HouPeach", (S(240, 206, 164), 0.9, 0.0, 0, None, 0.08))   # 2o tom de reboco

G = L.G
LIT = "Window_Warm"          # janela comum (FOLD_PROTECT: o export nunca funde)
RIDGE = "Wood_Dark"          # espigoes / cumeeira: a mesma madeira dos cunhais (1 malha a menos por casa)
STONE = "Stone_Wall_Dark"    # soco das casas
EAVE = 7.8                   # topo das paredes (beiral) acima do chao
RIDGE_TOP = 14.2             # topo da cumeeira acima do chao (as ponteiras chegam a ~14,9)
PLINTH = 1.0                 # soco de pedra acima do chao
MICRO = 0.35                 # peca com TODAS as dimensoes abaixo disso nao e criada
# materiais trocados na hora (menos MeshParts no moinho; Metal_Iron seria fundido no Metal_Dark pelo export)
REMAP = {"Metal_Iron": "Metal_Dark", "Crystal_Purple": "Crystal_Blue", "Wood_Light": "Wood_Plank",
         "Roof_HouRidge": "Wood_Dark", "Window_Dark": LIT}

# ------------------------------------------------------------------ cameras de revisao (360 graus + altura do jogador)
_MX, _MY = L.MILL[0], L.MILL[1]
CAMS = {
    # altura do jogador (5,3 acima do piso) em volta das casas
    "CAM_Houses_PlayerT1E": ((20.0, 92.0, L.T1 + 5.3), (60.0, 108.0, L.T1 + 6.0), 20),
    "CAM_Houses_PlayerT1W": ((-62.0, 88.0, L.T1 + 5.3), (-98.0, 100.0, L.T1 + 6.0), 20),
    "CAM_Houses_PlayerT1Exit": ((68.0, 90.0, L.T1 + 5.3), (86.0, 110.0, L.T1 + 6.0), 20),
    "CAM_Houses_PlayerT2W": ((-80.0, 138.0, L.T2 + 5.3), (-112.0, 152.0, L.T2 + 8.0), 20),
    "CAM_Houses_PlayerT2E": ((76.0, 136.0, L.T2 + 5.3), (96.0, 150.0, L.T2 + 6.0), 20),
    "CAM_Houses_PlayerEastN": ((128.0, 6.0, G + 5.3), (136.0, 36.0, G + 7.0), 20),
    "CAM_Houses_EastS": ((113.0, -42.0, G + 9.0), (134.0, -26.0, G + 8.0), 20),
    # plato do paredao (2 casinhas a oeste + pagode a leste)
    "CAM_Houses_Upper": ((0.0, 150.0, 104.0), (0.0, 205.0, L.CLIFF_TOP + 4.0), 16),
    "CAM_Houses_UpperW": ((-58.0, 168.0, 96.0), (-58.0, 206.0, L.CLIFF_TOP + 2.0), 20),
    "CAM_Houses_UpperE": ((55.0, 170.0, 96.0), (55.0, 205.0, L.CLIFF_TOP + 6.0), 20),
    # moinho: da escada do anel no eixo da porta, porta, dentro (3 lados), fora (360)
    "CAM_Houses_MillStair": ((80.5, 12.0, L.RING + 5.3), (96.0, 12.0, G + 8.0), 20),
    "CAM_Houses_MillDoor": ((90.0, 12.0, G + 5.3), (104.0, 12.0, G + 6.0), 18),
    "CAM_Houses_MillInterior": ((95.0, 5.0, G + 9.0), (103.0, 13.0, G + 5.0), 14),
    "CAM_Houses_MillMachine": ((97.5, 9.0, G + 6.0), (100.0, 19.0, G + 8.0), 16),
    "CAM_Houses_MillBack": ((103.0, 12.0, G + 6.0), (92.0, 12.0, G + 6.0), 16),
    "CAM_Houses_Mill34": ((74.0, -12.0, G + 16.0), (100.0, 12.0, G + 9.0), 20),
    "CAM_Houses_MillNE": ((124.0, 38.0, G + 15.0), (104.0, 13.0, G + 9.0), 20),
    # 360 da zona (de longe)
    "CAM_Houses_Back": ((20.0, 300.0, 150.0), (10.0, 118.0, 20.0), 24),
    "CAM_Houses_SideE": ((236.0, 30.0, 70.0), (112.0, 30.0, 12.0), 24),
    "CAM_Houses_SideW": ((-246.0, 100.0, 80.0), (-100.0, 110.0, 22.0), 24),
}

# rotas e sondas do QA (il_qa.module_routes): as 2 bordas da porta larga do moinho, a volta do balcao ate o lugar do
# vendedor e o guarda-corpo das maquinas (a 2 do piso, olhando para o norte, tem que bater numa colisao)
_FL = G + 0.3
EXTRA_ROUTES = {
    "MOINHO:porta_borda_sul->interacao": ([(90.5, 8.2), (95.0, 8.2), (97.5, 11.0), (97.5, 12.0)], G),
    "MOINHO:porta_borda_norte->interacao": ([(90.5, 15.8), (94.2, 15.8), (97.5, 12.8), (97.5, 12.0)], G),
    "MOINHO:volta_do_balcao->vendedor": ([(90.0, 12.0), (96.0, 12.0), (98.5, 6.8), (103.3, 6.8), (103.3, 11.2)], G),
}
EXTRA_PROBES = [("MOINHO_guarda_corpo_oeste", 96.5, 15.4, _FL, 0.0, 1.0),
                ("MOINHO_guarda_corpo_leste", 103.0, 15.4, _FL, 0.0, 1.0),
                ("MOINHO_canto_NO_pilao", 94.8, 15.4, _FL, 0.0, 1.0)]


# ------------------------------------------------------------------ construtor
class HMB(MB):
    """MB das casas: telhado, reboco e vidro com a cor pedida (sem sorteio de variante), no maximo 'vmax' variantes
    por familia (pedra/madeira) -> poucas MeshParts por objeto no Roblox; aplica as regras tecnicas da rodada 2
    (chanfro so em peca >= 1,0 e <= 5% da menor dimensao; nada com todas as dimensoes < MICRO)"""

    def __init__(self, name, coll, rng=None, detail="near", floor=None, vmax=0):
        MB.__init__(self, name, coll, rng, detail, floor)
        self.vmax = vmax
        self.n_micro = 0

    def _family(self, m):
        if self.vmax < 1 or m.startswith(("Roof_", "Plaster_", "Window_")):
            return None          # vmax 0: sempre o material base (mesma madeira/pedra em todas as casas)
        fam = MB._family(self, m)
        if fam is None:
            return None
        return (min(fam[0], self.vmax), fam[1])

    def _mi_for(self, m):
        return MB._mi_for(self, REMAP.get(m, m))

    def _uv(self, faces, m):
        """telha modelada (canais em relevo): cada peca amostra um ponto calmo da textura de telha (a mesma regra do
        fm_arch_kit.AMB) -> um tom por peca, sem xadrez claro/escuro nos telhados"""
        m = REMAP.get(m, m)
        if fm_lib.tex_key(m) == "roof" and faces:
            import fm_arch_kit
            return fm_arch_kit.AMB._uv(self, faces, m)
        return MB._uv(self, faces, m)

    @staticmethod
    def _bev(bevel, mn):
        if not bevel or mn < 1.0:
            return 0.0
        return min(bevel, 0.05 * mn)

    def box(self, size, loc, rot=(0, 0, 0), m="Stone_Light", bevel=0.0, seg=1, tint=None):
        sx, sy, sz = (abs(v) for v in size)
        if max(sx, sy, sz) < MICRO:
            self.n_micro += 1
            return
        MB.box(self, (sx, sy, sz), loc, rot, m, self._bev(bevel, min(sx, sy, sz)), seg, tint)

    def beam(self, a, b, w, h=None, m="Wood_Dark", bevel=0.0, roll=0.0, tint=None):
        h = h or w
        ln = (Vector(b) - Vector(a)).length
        if max(ln, w, h) < MICRO:
            self.n_micro += 1
            return
        MB.beam(self, a, b, w, h, m, self._bev(bevel, min(ln, w, h)), roll, tint)

    def cyl(self, r, h, loc, rot=(0, 0, 0), m="Metal_Iron", n=12, r2=None, bevel=0.0, seg=1, caps=True, tint=None,
            angle=0.5):
        rr = r if r2 is None else r2
        if max(2 * max(r, rr), h) < MICRO:
            self.n_micro += 1
            return
        MB.cyl(self, r, h, loc, rot, m, n, r2, self._bev(bevel, min(2 * min(r, rr), h)), seg, caps, tint, angle)

    def rod(self, a, b, r, m="Metal_Iron", n=8, bevel=0.0, tint=None, caps=True):
        if max(2 * r, (Vector(b) - Vector(a)).length) < MICRO:
            self.n_micro += 1
            return
        MB.rod(self, a, b, r, m, n, 0.0, tint, caps)

    def finish(self, *a, **k):
        MICRO_LOG[self.name] = self.n_micro
        return MB.finish(self, *a, **k)


MICRO_LOG = {}          # objeto -> pecas microscopicas descartadas (auditoria: il_houses_qa.py)


def V(x, y, z=0.0):
    return Vector((x, y, z))


def solid(mb, pts, faces, m, bevel=0.0):
    vs = [mb.bm.verts.new(Vector(p)) for p in pts]
    for f in faces:
        try:
            mb.bm.faces.new([vs[i] for i in f])
        except ValueError:
            pass
    mb._post(vs, m, None, bevel, 1)


def hexa(mb, bot, top, m):
    solid(mb, list(bot) + list(top),
          [(3, 2, 1, 0), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)], m)


def slab4(mb, top, thick, m):
    top = [Vector(p) for p in top]
    hexa(mb, [p - Vector((0, 0, thick)) for p in top], top, m)


class Face:
    """fachada de um bloco alinhado aos eixos, vista de fora: s = distancia ao longo dela (da esquerda para a
    direita de quem olha), out = distancia para fora da parede"""

    def __init__(self, x0, y0, x1, y1, side):
        if side == "S":
            self.o, self.t, self.n, self.L = (x0, y0), (1.0, 0.0), (0.0, -1.0), x1 - x0
        elif side == "N":
            self.o, self.t, self.n, self.L = (x1, y1), (-1.0, 0.0), (0.0, 1.0), x1 - x0
        elif side == "E":
            self.o, self.t, self.n, self.L = (x1, y0), (0.0, 1.0), (1.0, 0.0), y1 - y0
        else:
            self.o, self.t, self.n, self.L = (x0, y1), (0.0, -1.0), (-1.0, 0.0), y1 - y0
        self.yaw = math.atan2(self.t[1], self.t[0])

    def p(self, s, z, out=0.0):
        return V(self.o[0] + self.t[0] * s + self.n[0] * out, self.o[1] + self.t[1] * s + self.n[1] * out, z)

    def box(self, mb, s, z, sx, sy, sz, out, m, bevel=0.0):
        """caixa: sx ao longo da fachada, sy na normal (centro a 'out' da face), sz vertical"""
        mb.box((sx, sy, sz), self.p(s, z, out), (0, 0, self.yaw), m, bevel)

    def col(self, area, s, z, sx, sy, sz, out):
        col_box(area, (sx, sy, sz), self.p(s, z, out), (0, 0, self.yaw))


def faces4(x0, y0, x1, y1):
    return {k: Face(x0, y0, x1, y1, k) for k in "SENW"}


# ------------------------------------------------------------------ pecas das casas
def window(mb, f, s, zc, w, h, style="cross", glass=LIT, frame="Wood_Dark", sill=True, awning=None):
    """janela de caixilho: vidro quente a 0,15 da parede, caixilho em 4 travessas (frente a 0,33), montantes de
    secao 0,3 a 0,2 na frente do vidro, peitoril e alpendrinho opcional (telhado da casa em maos-francesas)"""
    fw = 0.4
    f.box(mb, s, zc, w + 0.3, 0.5, h + 0.3, -0.1, glass)
    for sg in (-1, 1):
        f.box(mb, s + sg * (w / 2 + fw / 2), zc, fw, 0.45, h + 2 * fw, 0.1, frame)
        f.box(mb, s, zc + sg * (h / 2 + fw / 2), w, 0.45, fw, 0.1, frame)
    if style == "cross":
        f.box(mb, s, zc, 0.3, 0.3, h, 0.2, frame)
        f.box(mb, s, zc, w, 0.3, 0.3, 0.2, frame)
    elif style == "two":
        f.box(mb, s, zc, 0.3, 0.3, h, 0.2, frame)
    elif style == "slats":
        k = max(3, int(round(w / 0.8)))
        for i in range(1, k):
            f.box(mb, s - w / 2 + w * i / k, zc, 0.3, 0.3, h, 0.2, frame)
    if sill:
        f.box(mb, s, zc - h / 2 - fw - 0.05, w + 2 * fw + 0.4, 0.75, 0.3, 0.3, frame)
    if awning:
        za = zc + h / 2 + fw + 0.75
        a0, a1 = s - w / 2 - fw - 0.5, s + w / 2 + fw + 0.5
        slab4(mb, [f.p(a0, za - 0.55, 1.35), f.p(a1, za - 0.55, 1.35), f.p(a1, za, -0.1), f.p(a0, za, -0.1)], 0.35,
              awning)
        for sg in (-1, 1):
            mb.beam(f.p(s + sg * (w / 2 + fw / 2), za - 1.3, 0.05), f.p(s + sg * (w / 2 + fw / 2), za - 0.7, 1.05),
                    0.3, 0.3, frame, 0.0)


def win_row(mb, f, zs, n, w=2.6, h=3.0, style="cross", margin=1.4, awning=None, skip=(), styles=None, s0=0.0,
            s1=None):
    """n janelas iguais distribuidas na fachada entre s0 e s1; zs = cota do peitoril (vao)"""
    s1 = f.L if s1 is None else s1
    for i in range(n):
        if i in skip:
            continue
        s = s0 + margin + (s1 - s0 - 2 * margin) * (i + 0.5) / n
        window(mb, f, s, zs + h / 2, w, h, (styles[i] if styles else style), awning=awning)


def plinth(mb, x0, y0, x1, y1, z0, h=PLINTH, out=0.45, m=STONE):
    """soco de pedra: da terra (z0 - 0,8) ate z0 + h, 0,45 para fora das paredes"""
    mb.box2((x0 - out, y0 - out, z0 - 0.8), (x1 + out, y1 + out, z0 + h), m, 0.08)


def walls(mb, x0, y0, x1, y1, z0, z1, wall_m="Plaster_Cream", band=0.7, post=0.8, zpost=None, posts=True):
    """corpo macico de reboco + cunhais de madeira + faixa escura sob o beiral (o madeiramento e SO isso).
    Faces de materiais diferentes nunca no mesmo plano: faixa 0,2 para fora e 0,1 acima do reboco (dentro do
    telhado), cunhais 0,4 para fora e com o topo dentro da faixa."""
    mb.box2((x0, y0, z0), (x1, y1, z1), wall_m, 0.0)
    zp = z0 if zpost is None else zpost
    for px, py in ((x0, y0), (x1, y0), (x1, y1), (x0, y1)) if posts else ():
        mb.box((post, post, z1 - 0.3 - zp), (px, py, (zp + z1 - 0.3) / 2), (0, 0, 0), "Wood_Dark", 0.0)
    if band:
        mb.box2((x0 - 0.2, y0 - 0.2, z1 - band), (x1 + 0.2, y1 + 0.2, z1 + 0.1), "Wood_Dark", 0.0)


# ------------------------------------------------------------------ telhados
def hip_roof(mb, x0, y0, x1, y1, z_w, m, g=0.55, over=2.0, thick=0.8, rib=1.5, ridge_m=RIDGE, tips=True,
             finial=False, clip=None):
    """4 aguas com testeira: forro rente ao topo da parede, canais de telha em relevo (rib = passo, 0 = sem),
    espigoes e cumeeira escuros com pontas levantadas. Devolve info (cotas, funcao de altura zf(x, y)).
    Alturas: topo da cumeeira = zr + 0,84; ponteiras = zr + 1,45."""
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    W, Dd = (x1 - x0) / 2 + over, (y1 - y0) / 2 + over
    zb = z_w - 0.05
    ze = zb + thick
    run = min(W, Dd)
    zr = ze + g * run
    X0, X1, Y0, Y1 = cx - W, cx + W, cy - Dd, cy + Dd
    E = [(X0, Y0), (X1, Y0), (X1, Y1), (X0, Y1)]
    if abs(W - Dd) < 0.05:
        R = [(cx, cy)]
        tops = [(4, 5, 8), (5, 6, 8), (6, 7, 8), (7, 4, 8)]
        ends = [0, 0, 0, 0]
    elif W > Dd:
        R = [(cx - (W - Dd), cy), (cx + (W - Dd), cy)]
        tops = [(4, 5, 9, 8), (5, 6, 9), (6, 7, 8, 9), (7, 4, 8)]
        ends = [0, 1, 1, 0]
    else:
        R = [(cx, cy - (Dd - W)), (cx, cy + (Dd - W))]
        tops = [(4, 5, 8), (5, 6, 9, 8), (6, 7, 9), (7, 4, 8, 9)]
        ends = [0, 0, 1, 1]
    pts = [V(px, py, zb) for px, py in E] + [V(px, py, ze) for px, py in E] + [V(px, py, zr) for px, py in R]
    solid(mb, pts, [(3, 2, 1, 0), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)] + tops, m)
    if rib:
        for k in range(4):
            ax, ay = E[k]
            bx, by = E[(k + 1) % 4]
            Lk = math.hypot(bx - ax, by - ay)
            tx, ty = (bx - ax) / Lk, (by - ay) / Lk
            nx, ny = -ty, tx
            nrm = Vector((-nx * g, -ny * g, 1.0)).normalized()
            n = max(2, int(Lk / rib))
            for i in range(n):
                s = (i + 0.5) * Lk / n
                ln = min(s, Lk - s, run) - 0.45
                if ln < 0.9:
                    continue
                p = V(ax + tx * s - nx * 0.15, ay + ty * s - ny * 0.15, ze - g * 0.15)
                q = V(ax + tx * s + nx * ln, ay + ty * s + ny * ln, ze + g * ln)
                mb.beam(p + nrm * 0.15, q + nrm * 0.15, 0.5, 0.3, m, 0.0)
    up = Vector((0, 0, 1))
    Rv = [V(px, py, zr) for px, py in R]

    def inside(q, pad=0.0):
        return clip and clip[0] - pad <= q.x <= clip[2] + pad and clip[1] - pad <= q.y <= clip[3] + pad
    for k in range(4):
        c = V(E[k][0], E[k][1], ze)
        r_ = Rv[ends[k]]
        if inside(r_):
            # o espigao morre na parede do mirante (sem o toco escuro saindo dela)
            lo, hi = 0.0, 1.0
            for _ in range(24):
                mid = (lo + hi) / 2
                if inside(c.lerp(r_, mid), 0.3):
                    hi = mid
                else:
                    lo = mid
            r_ = c.lerp(r_, hi)
        mb.beam(c + up * 0.2, r_ + up * 0.32, 0.74, 0.52, ridge_m, 0.0)
        if tips:
            dp = Vector((c.x - r_.x, c.y - r_.y, 0)).normalized()
            mb.beam(c + up * 0.05 - dp * 0.7, c + dp * 0.6 + up * 0.62, 0.84, 0.56, ridge_m, 0.0)
    if len(Rv) == 2 and inside(Rv[0]) and inside(Rv[1]):
        pass                                   # cumeeira inteira dentro do mirante
    elif len(Rv) == 2:
        d = (Rv[1] - Rv[0]).normalized()
        mb.beam(Rv[0] - d * 0.45 + up * 0.45, Rv[1] + d * 0.45 + up * 0.45, 0.98, 0.78, ridge_m, 0.0)
        if finial:
            for q, sg in ((Rv[0], -1), (Rv[1], 1)):
                mb.beam(q + d * sg * 0.1 + up * 0.5, q + d * sg * 1.1 + up * 1.15, 1.0, 0.8, ridge_m, 0.0)
    else:
        mb.cyl(0.8, 1.0, Rv[0] + up * 0.7, (0, 0, math.pi / 4), ridge_m, 4, r2=0.3, bevel=0.0)
        if finial:
            mb.cyl(0.36, 1.6, Rv[0] + up * 1.9, (0, 0, 0), ridge_m, 6, r2=0.1, bevel=0.0)

    def zf(px, py):
        return min(zr, ze + g * max(0.0, min(px - X0, X1 - px, py - Y0, Y1 - py)))
    return dict(cx=cx, cy=cy, W=W, D=Dd, g=g, zb=zb, ze=ze, zr=zr, zf=zf)


def pitch(x0, y0, x1, y1, z0, z_w, over=2.0, thick=0.8, top=RIDGE_TOP, lo=0.45, hi=0.72):
    """inclinacao que poe o topo da cumeeira em z0 + top"""
    run = min(x1 - x0, y1 - y0) / 2 + over
    ze = z_w - 0.05 + thick
    return max(lo, min(hi, (z0 + top - 0.84 - ze) / run))


def skirt_roof(mb, x0, y0, x1, y1, z_in, m, g=0.5, over=1.8, thick=0.55, rib=1.85, ridge_m=RIDGE, tips=True):
    """saia de telhado (aba entre pavimentos) em volta do bloco [x0,x1]x[y0,y1], nascendo na cota z_in"""
    ins = 0.3
    I = [(x0 + ins, y0 + ins), (x1 - ins, y0 + ins), (x1 - ins, y1 - ins), (x0 + ins, y1 - ins)]
    O = [(x0 - over, y0 - over), (x1 + over, y0 - over), (x1 + over, y1 + over), (x0 - over, y1 + over)]
    o = over + ins
    zo = z_in - g * o
    up = Vector((0, 0, 1))
    for k in range(4):
        j = (k + 1) % 4
        slab4(mb, [V(*O[k], zo), V(*O[j], zo), V(*I[j], z_in), V(*I[k], z_in)], thick, m)
        if rib:
            ax, ay = O[k]
            bx, by = O[j]
            Lk = math.hypot(bx - ax, by - ay)
            tx, ty = (bx - ax) / Lk, (by - ay) / Lk
            nx, ny = -ty, tx
            nrm = Vector((-nx * g, -ny * g, 1.0)).normalized()
            n = max(2, int(Lk / rib))
            for i in range(n):
                s = (i + 0.5) * Lk / n
                ln = min(s, Lk - s, o) - 0.4
                if ln < 0.7:
                    continue
                p = V(ax + tx * s - nx * 0.12, ay + ty * s - ny * 0.12, zo - g * 0.12)
                q = V(ax + tx * s + nx * ln, ay + ty * s + ny * ln, zo + g * ln)
                mb.beam(p + nrm * 0.14, q + nrm * 0.14, 0.44, 0.3, m, 0.0)
        c = V(*O[k], zo)
        ci = V(*I[k], z_in)
        mb.beam(c + up * 0.15, ci + up * 0.2, 0.62, 0.44, ridge_m, 0.0)
        if tips:
            dp = Vector((c.x - ci.x, c.y - ci.y, 0)).normalized()
            mb.beam(c + up * 0.02 - dp * 0.55, c + dp * 0.5 + up * 0.5, 0.72, 0.48, ridge_m, 0.0)


def col_roof(area, info):
    """colisao do telhado: 2 lajes inclinadas nas aguas compridas (quem cair no telhado nao entra na casa)"""
    a = math.atan(info["g"])
    cx, cy, W, Dd, ze, zr = info["cx"], info["cy"], info["W"], info["D"], info["ze"], info["zr"]
    run = min(W, Dd)
    hyp = run / math.cos(a)
    zc = (ze + zr) / 2 - 0.35
    if W >= Dd:
        for s in (-1, 1):
            col_box(area, (2 * W - run, hyp, 0.7), (cx, cy + s * run / 2, zc), (-s * a, 0, 0))
    else:
        for s in (-1, 1):
            col_box(area, (hyp, 2 * Dd - run, 0.7), (cx + s * run / 2, cy, zc), (0, s * a, 0))


# ------------------------------------------------------------------ a casa comum (uma familia so)
def block(mb, A, x0, y0, x1, y1, z0, roof, plaster="Plaster_Cream", eave=EAVE, top=RIDGE_TOP, over=2.0,
          rib=1.5, finial=False, stone=True, col=True, zbase=None, clip=None):
    """um volume de casa: soco, paredes, cunhais, faixa do beiral, telhado de 4 aguas (cumeeira em z0 + top) e
    colisao (corpo + aguas). zbase: onde o reboco comeca (padrao: z0)."""
    zw = z0 + eave
    if stone:
        plinth(mb, x0, y0, x1, y1, z0)
    walls(mb, x0, y0, x1, y1, z0 if zbase is None else zbase, zw, plaster,
          zpost=(z0 + PLINTH - 0.1) if stone else z0 + 0.2)
    g = pitch(x0, y0, x1, y1, z0, zw, over, top=top)
    info = hip_roof(mb, x0, y0, x1, y1, zw, roof, g=g, over=over, rib=rib, finial=finial, clip=clip)
    if col:
        col_box2(A, (x0 - 0.45, y0 - 0.45, z0 - 0.5), (x1 + 0.45, y1 + 0.45, zw))
        col_roof(A, info)
    return info


def annex_east(mb, A, x_in, y0, x1, y1, z0, roof, plaster="Plaster_Cream", z_hi=7.2, g=0.4, over=1.2,
               thick=0.5, rib=1.5):
    """anexo baixo encostado na parede LESTE (x = x_in) do bloco principal: paredes com o topo inclinado e
    meia-agua caindo para leste, nascendo 0,55 abaixo do forro do beiral principal (sem cruzar o telhado dele)"""
    zt_in = z0 + z_hi - 0.55
    zt_out = z0 + z_hi - g * (x1 - x_in) - 0.55
    plinth(mb, x_in - 0.45, y0, x1, y1, z0)
    bot = [V(x_in - 0.3, y0, z0), V(x1, y0, z0), V(x1, y1, z0), V(x_in - 0.3, y1, z0)]
    top = [V(x_in - 0.3, y0, zt_in), V(x1, y0, zt_out), V(x1, y1, zt_out), V(x_in - 0.3, y1, zt_in)]
    hexa(mb, bot, top, plaster)
    for py in (y0, y1):
        mb.box((0.8, 0.8, zt_out - 0.3 - (z0 + PLINTH - 0.1)), (x1, py, (zt_out - 0.3 + z0 + PLINTH - 0.1) / 2),
               (0, 0, 0), "Wood_Dark", 0.0)
    mb.box2((x1 - 0.2, y0 - 0.2, zt_out - 0.6), (x1 + 0.2, y1 + 0.2, zt_out + 0.1), "Wood_Dark", 0.0)
    # meia-agua: laje de telha + canais em relevo + testeira escura na aba baixa
    xa, xb = x_in - 0.1, x1 + over
    za = z0 + z_hi
    zb = za - g * (xb - xa)
    Y0, Y1 = y0 - over, y1 + over
    slab4(mb, [V(xa, Y0, za), V(xb, Y0, zb), V(xb, Y1, zb), V(xa, Y1, za)], thick, roof)
    nrm = Vector((g, 0.0, 1.0)).normalized()
    if rib:
        n = max(2, int((Y1 - Y0) / rib))
        for i in range(n):
            y = Y0 + (i + 0.5) * (Y1 - Y0) / n
            mb.beam(V(xb + 0.1, y, zb - g * 0.1) + nrm * 0.14, V(xa + 0.3, y, za - g * 0.3) + nrm * 0.14, 0.46,
                    0.32, roof, 0.0)
    mb.beam(V(xb, Y0 - 0.1, zb - 0.1), V(xb, Y1 + 0.1, zb - 0.1), 0.6, 0.6, RIDGE, 0.0)
    for py in (Y0, Y1):
        mb.beam(V(xa, py, za + 0.15), V(xb, py, zb + 0.15), 0.6, 0.45, RIDGE, 0.0)
    col_box2(A, (x_in, y0 - 0.45, z0 - 0.5), (x1 + 0.45, y1 + 0.45, (zt_in + zt_out) / 2))


def _box(h):
    x, y, w, d = h[0], h[1], h[2], h[3]
    return x - w / 2, y - d / 2, x + w / 2, y + d / 2


def new_house(name, seed):
    return HMB(name, "04_VILLAGE", random.Random(seed), detail="near")


ZW_OFF = PLINTH + 1.4        # peitoril das janelas acima do chao (vao de 3,0 -> topo do caixilho a ~6,2)
GREEN = "Roof_Green"
TERRA = "Roof_Terracotta"


def house_T1_01(mb):
    """(38,107) VERDE: bloco principal + anexo baixo a leste (o caminho do terreno chega no meio do bloco, x 35,5)"""
    A = "HousesT1"
    h = L.HOUSES_T1[0]
    z0 = L.zone_of(h[0], h[1])
    x0, y0, x1, y1 = _box(h)
    xm = x0 + 11.0
    ay0, ay1 = y0 + 1.8, y1 - 1.8
    block(mb, A, x0, y0, xm, y1, z0, GREEN)
    annex_east(mb, A, xm, ay0, x1, ay1, z0, GREEN, over=1.3)
    F = faces4(x0, y0, xm, y1)
    Fa = faces4(xm, ay0, x1, ay1)
    zs = z0 + ZW_OFF
    win_row(mb, F["S"], zs, 2, 2.8, 3.0, "cross", margin=1.6, awning=GREEN)
    win_row(mb, F["N"], zs, 2, 2.6, 3.0, "cross", margin=1.6)
    win_row(mb, F["W"], zs, 2, 2.4, 3.0, "two", margin=1.4)
    win_row(mb, Fa["S"], zs - 0.3, 1, 2.0, 2.4, "two", margin=0.9)
    win_row(mb, Fa["E"], zs - 0.3, 2, 2.2, 2.4, "cross", margin=1.0)


def house_T1_02(mb):
    """(-84,110) terracota, reboco pessego: retangulo simples, 3 janelas na frente com alpendrinhos"""
    A = "HousesT1"
    h = L.HOUSES_T1[1]
    z0 = L.zone_of(h[0], h[1])
    x0, y0, x1, y1 = _box(h)
    block(mb, A, x0, y0, x1, y1, z0, TERRA, "Plaster_HouPeach")
    F = faces4(x0, y0, x1, y1)
    zs = z0 + ZW_OFF
    win_row(mb, F["S"], zs, 3, 2.6, 3.0, styles=("cross", "slats", "cross"), margin=1.2, awning=TERRA)
    win_row(mb, F["N"], zs, 3, 2.4, 3.0, "cross", margin=1.4)
    win_row(mb, F["E"], zs, 2, 2.4, 3.0, "two", margin=1.6)
    win_row(mb, F["W"], zs, 2, 2.4, 3.0, "cross", margin=1.6)


def house_T1_03(mb):
    """(84,108) terracota: bloco principal ate x 88 + anexo baixo e estreito a leste (y 106..fundo, x ate 91, beiral
    bem abaixo de T1+7: livre dos pilones de lanterna da entrada da ponte de saida em (94.6,108.7))"""
    A = "HousesT1"
    h = L.HOUSES_T1[2]
    z0 = L.zone_of(h[0], h[1])
    x0, y0, x1, y1 = _box(h)
    xm = x0 + 12.0
    xa = x0 + 15.0
    ay0 = y0 + 4.5
    block(mb, A, x0, y0, xm, y1, z0, TERRA)
    annex_east(mb, A, xm, ay0, xa, y1 - 0.8, z0, TERRA, over=0.9)
    F = faces4(x0, y0, xm, y1)
    Fa = faces4(xm, ay0, xa, y1 - 0.8)
    zs = z0 + ZW_OFF
    win_row(mb, F["S"], zs, 2, 2.8, 3.0, styles=("slats", "cross"), margin=1.8)
    win_row(mb, F["W"], zs, 2, 2.6, 3.0, "cross", margin=1.8)
    win_row(mb, F["N"], zs, 2, 2.6, 3.0, "two", margin=1.8)
    win_row(mb, F["E"], zs, 1, 2.2, 2.6, "two", s0=0.0, s1=ay0 - y0 + 0.4, margin=0.6)
    win_row(mb, Fa["E"], zs - 0.4, 2, 1.6, 2.2, "two", margin=0.8)


def house_T1_04(mb):
    """(-112,84) terracota (era azul com torre): casa terrea comprida, alpendrinhos nas 2 janelas da frente"""
    A = "HousesT1"
    h = L.HOUSES_T1[3]
    z0 = L.zone_of(h[0], h[1])
    x0, y0, x1, y1 = _box(h)
    block(mb, A, x0, y0, x1, y1, z0, TERRA)
    F = faces4(x0, y0, x1, y1)
    zs = z0 + ZW_OFF
    win_row(mb, F["S"], zs, 2, 2.8, 3.0, "cross", margin=1.8, awning=TERRA)
    win_row(mb, F["E"], zs, 2, 2.4, 3.0, "two", margin=1.4)
    win_row(mb, F["W"], zs, 2, 2.4, 3.0, "cross", margin=1.4)
    win_row(mb, F["N"], zs, 2, 2.4, 3.0, "slats", margin=1.6)


def house_T2_01(mb):
    """(-98,160) terracota: a UNICA casa com mirante - casa terrea larga e um mirante quadrado de janelas corridas
    atravessando o telhado (topo 20,2 acima do T2; predios redondos azuis ~29, salao ~43)"""
    A = "HousesT2"
    h = L.HOUSES_T2[0]
    z0 = L.T2
    x0, y0, x1, y1 = _box(h)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    hw = 2.8
    block(mb, A, x0, y0, x1, y1, z0, TERRA, clip=(cx - hw, cy - hw, cx + hw, cy + hw))
    F = faces4(x0, y0, x1, y1)
    zs = z0 + ZW_OFF
    win_row(mb, F["S"], zs, 3, 2.6, 3.0, styles=("slats", "cross", "slats"), margin=1.4)
    win_row(mb, F["N"], zs, 3, 2.4, 3.0, "cross", margin=1.4)
    win_row(mb, F["E"], zs, 2, 2.4, 3.0, "two", margin=1.8)
    win_row(mb, F["W"], zs, 2, 2.4, 3.0, "cross", margin=1.8)
    # mirante: 5,6 x 5,6 saindo do telhado, janelas corridas, telhado piramidal proprio
    mx0, my0, mx1, my1 = cx - hw, cy - hw, cx + hw, cy + hw
    zb, zt = z0 + EAVE - 0.4, z0 + EAVE + 8.2       # o telhado da casa passa em ~12 ali: 4 de mirante visivel
    walls(mb, mx0, my0, mx1, my1, zb, zt, "Plaster_Cream", band=0.6, post=0.7, zpost=zb + 0.6)
    Fm = faces4(mx0, my0, mx1, my1)
    for side in "SENW":
        window(mb, Fm[side], Fm[side].L / 2, zt - 2.1, 3.4, 1.8, "slats", sill=False)
    im = hip_roof(mb, mx0, my0, mx1, my1, zt, TERRA, g=0.62, over=1.1, thick=0.6, rib=1.5, finial=False)
    col_box2(A, (mx0, my0, zb), (mx1, my1, zt))
    return im


def house_T2_02(mb):
    """(96,5; 149,5) terracota: pegada real da planta (13,5 x 12); caixa na frente sem porta, 3 janelas"""
    A = "HousesT2"
    h = L.HOUSES_T2[1]
    z0 = L.T2
    x0, y0, x1, y1 = _box(h)
    block(mb, A, x0, y0, x1, y1, z0, TERRA, "Plaster_HouPeach")
    F = faces4(x0, y0, x1, y1)
    zs = z0 + ZW_OFF
    win_row(mb, F["S"], zs, 3, 2.4, 3.0, styles=("cross", "slats", "cross"), margin=1.0)
    win_row(mb, F["W"], zs, 2, 2.4, 3.0, "two", margin=1.6)
    win_row(mb, F["N"], zs, 2, 2.4, 3.0, "cross", margin=1.6)
    win_row(mb, F["E"], zs, 2, 2.2, 2.8, "two", margin=1.6)


def house_T2_03(mb):
    """(-126,136) terracota: frente para LESTE (o caminho do terreno chega na fachada leste); alpendrinhos"""
    A = "HousesT2"
    h = L.HOUSES_T2[2]
    z0 = L.T2
    x0, y0, x1, y1 = _box(h)
    block(mb, A, x0, y0, x1, y1, z0, TERRA)
    F = faces4(x0, y0, x1, y1)
    zs = z0 + ZW_OFF
    win_row(mb, F["E"], zs, 2, 2.6, 3.0, "cross", margin=1.6, awning=TERRA)
    win_row(mb, F["S"], zs, 2, 2.4, 3.0, "slats", margin=1.6)
    win_row(mb, F["N"], zs, 2, 2.4, 3.0, "cross", margin=1.6)
    win_row(mb, F["W"], zs, 2, 2.2, 2.8, "two", margin=1.6)


def house_East_01(mb, rng):
    """(134,-26) terracota: casa na beira do penhasco leste sobre um embasamento de pedra que desce a encosta
    (a pegada da planta passa ~6 do topo do penhasco no canto SE); frente para oeste (trilha da margem)"""
    A = "HousesEast"
    h = L.EAST_HOUSES[0]
    z0 = L.G
    x0, y0, x1, y1 = _box(h)
    zp = z0 + 1.6
    # embasamento: nucleo escuro ate a prateleira do penhasco + fiadas de pedra clara nas faces L e S (as do mar)
    mb.box2((x0 - 0.9, y0 - 0.9, L.SHELF_Z - 2.0), (x1 + 0.9, y1 + 0.9, zp), STONE, 0.1)
    for side in "SE":
        f = Face(x0 - 0.9, y0 - 0.9, x1 + 0.9, y1 + 0.9, side)
        z = zp - 0.1
        row = 0
        while z > L.SHELF_Z - 1.0:
            hh = 1.5
            s = -rng.uniform(0.0, 1.2) if row % 2 else 0.0
            while s < f.L - 0.2:
                ln = rng.uniform(2.2, 3.6)
                a, b = max(s, 0.0), min(s + ln, f.L)
                if b - a > 0.6:
                    f.box(mb, (a + b) / 2, z - hh / 2, b - a - 0.2, 0.4, hh - 0.2, 0.1, "Stone_Wall_Light")
                s += ln
            z -= hh
            row += 1
    mb.box2((x0 - 1.1, y0 - 1.1, zp - 0.2), (x1 + 1.1, y1 + 1.1, zp + 0.35), "Stone_Wall_Light", 0.0)
    info = block(mb, A, x0, y0, x1, y1, zp, TERRA, stone=False, col=False, zbase=zp - 0.15)
    F = faces4(x0, y0, x1, y1)
    zs = zp + 2.2
    win_row(mb, F["W"], zs, 2, 2.8, 3.0, "cross", margin=1.6, awning=TERRA)
    win_row(mb, F["S"], zs, 2, 2.6, 3.0, "slats", margin=1.6)
    win_row(mb, F["N"], zs, 2, 2.6, 3.0, "two", margin=1.6)
    win_row(mb, F["E"], zs, 2, 2.6, 3.0, "cross", margin=1.6)
    col_box2(A, (x0 - 0.9, y0 - 0.9, z0 - 1.0), (x1 + 0.9, y1 + 0.9, zp + 0.35))
    col_box2(A, (x0 - 0.3, y0 - 0.3, zp), (x1 + 0.3, y1 + 0.3, zp + EAVE))
    col_roof(A, info)


def house_East_02(mb):
    """(136,36) VERDE: casa terrea com frente para oeste (a trilha da margem chega no meio da fachada oeste)"""
    A = "HousesEast"
    h = L.EAST_HOUSES[1]
    z0 = L.G
    x0, y0, x1, y1 = _box(h)
    block(mb, A, x0, y0, x1, y1, z0, GREEN, "Plaster_HouPeach")
    F = faces4(x0, y0, x1, y1)
    zs = z0 + ZW_OFF
    win_row(mb, F["W"], zs, 3, 2.2, 3.0, styles=("cross", "slats", "cross"), margin=1.0, awning=GREEN)
    win_row(mb, F["S"], zs, 2, 2.4, 3.0, "cross", margin=1.6)
    win_row(mb, F["N"], zs, 2, 2.4, 3.0, "two", margin=1.6)
    win_row(mb, F["E"], zs, 2, 2.4, 3.0, "cross", margin=1.6)


def houses_near():
    specs = [("VIL_House_T1_01", house_T1_01), ("VIL_House_T1_02", house_T1_02), ("VIL_House_T1_03", house_T1_03),
             ("VIL_House_T1_04", house_T1_04), ("VIL_House_T2_01", house_T2_01), ("VIL_House_T2_02", house_T2_02),
             ("VIL_House_T2_03", house_T2_03), ("VIL_House_East_02", house_East_02)]
    for i, (name, fn) in enumerate(specs):
        mb = new_house(name, 4410 + i)
        fn(mb)
        mb.finish()
    mb = new_house("VIL_House_East_01", 4420)
    house_East_01(mb, random.Random(4421))
    mb.finish()


# ------------------------------------------------------------------ plato do paredao (patamar B, "far")
UPPER_Z = 71.88               # patamar B do TER_Back_Massif (il_terrain_rock.H_B)
UPPER = [  # nome, x, y, w, d, beiral, telhado, reboco
    ("VIL_House_Upper_01", -64.0, 202.5, 9.0, 8.0, 6.4, TERRA, "Plaster_Cream"),
    ("VIL_House_Upper_02", -51.5, 208.5, 8.0, 7.5, 6.0, TERRA, "Plaster_HouPeach"),
]
PAGODA = ("VIL_House_Upper_03", 55.0, 205.0)


def far_window(mb, f, s, zc, w, h):
    """janela de longe: painel escuro saliente (sem vidro: a 60+ studs um material minusculo seria fundido)"""
    f.box(mb, s, zc, w, 0.4, h, 0.1, "Wood_Dark")


def houses_upper():
    """2 casinhas agrupadas a oeste (x -68..-47) + 1 pagode a leste (x ~55), recuados para y 198-213 e
    desencontrados em y; assentes no patamar B (z 71,88). 3 materiais cada (reboco, madeira, telha)."""
    A = "HousesUpper"
    z0 = UPPER_Z
    for name, x, y, w, d, eave, roof, plaster in UPPER:
        mb = HMB(name, "04_VILLAGE", random.Random(4402), detail="far", floor=z0)
        x0, y0, x1, y1 = x - w / 2, y - d / 2, x + w / 2, y + d / 2
        mb.box2((x0 - 0.4, y0 - 0.4, z0 - 0.8), (x1 + 0.4, y1 + 0.4, z0 + 0.7), "Wood_Dark", 0.0)
        walls(mb, x0, y0, x1, y1, z0, z0 + eave, plaster, band=0.6, post=0.8, zpost=z0 + 0.6)
        F = faces4(x0, y0, x1, y1)
        for side in "SENW":
            n = 2 if F[side].L > 7.5 else 1
            for k in range(n):
                far_window(mb, F[side], F[side].L * (k + 1) / (n + 1), z0 + eave * 0.55, 1.8, 2.2)
        g = pitch(x0, y0, x1, y1, z0, z0 + eave, 1.6, thick=0.7, top=eave + 4.6)
        hip_roof(mb, x0, y0, x1, y1, z0 + eave, roof, g=g, over=1.6, thick=0.7, rib=0, tips=True, finial=False)
        col_box2(A, (x0 - 0.4, y0 - 0.4, z0 - 0.5), (x1 + 0.4, y1 + 0.4, z0 + eave))
        mb.finish()
    pagoda(A)


def pagoda(A):
    """pagode de 3 andares (quadrado, cada andar menor), saias de telha, telhado piramidal e haste (sorin)"""
    name, x, y = PAGODA
    z0 = UPPER_Z
    mb = HMB(name, "04_VILLAGE", random.Random(4405), detail="far", floor=z0)
    tiers = [(4.0, 0.0, 5.2), (3.0, 4.6, 8.4), (2.2, 7.8, 10.9)]      # meia-largura, base, topo (acima de z0)
    mb.box2((x - 5.0, y - 5.0, z0 - 0.8), (x + 5.0, y + 5.0, z0 + 0.6), "Wood_Dark", 0.0)
    for i, (hw, zb, zt) in enumerate(tiers):
        x0, y0, x1, y1 = x - hw, y - hw, x + hw, y + hw
        walls(mb, x0, y0, x1, y1, z0 + zb, z0 + zt, "Plaster_Cream", band=0.5, post=0.7,
              zpost=z0 + 0.5, posts=(i == 0))
        F = faces4(x0, y0, x1, y1)
        for side in "SENW":
            far_window(mb, F[side], F[side].L / 2, z0 + (zb + zt) / 2 + 0.2, 1.6 if i else 2.2, 1.8 if i else 2.4)
        if i + 1 < len(tiers):
            nhw = tiers[i + 1][0]
            over = (hw - nhw) + 1.5
            g = 0.5
            z_in = z0 + zt + g * (over + 0.3) - 0.55
            skirt_roof(mb, x - nhw, y - nhw, x + nhw, y + nhw, z_in, TERRA, g=g, over=over, thick=0.5, rib=0,
                       tips=True)
    hw, zb, zt = tiers[-1]
    info = hip_roof(mb, x - hw, y - hw, x + hw, y + hw, z0 + zt, TERRA, g=0.8, over=1.5, thick=0.6, rib=0,
                    tips=True, finial=False)
    zr = info["zr"]
    mb.cyl(0.36, 3.2, (x, y, zr + 2.0), (0, 0, 0), "Wood_Dark", 8, r2=0.2, bevel=0.0)
    for k in range(3):
        mb.cyl(0.75 - 0.12 * k, 0.35, (x, y, zr + 1.0 + 0.8 * k), (0, 0, 0), "Wood_Dark", 8, bevel=0.0)
    col_box2(A, (x - 4.4, y - 4.4, z0 - 0.5), (x + 4.4, y + 4.4, z0 + tiers[0][2]))
    mb.finish()


# ------------------------------------------------------------------ MOINHO DE MINERIO / Posto do Minerador
# O ponto mais visitado do jogo (venda de minerio). Rodada 2:
#   * porta OESTE de 10 (y 7..17) com 12,2 livres ate a verga, alinhada a escada do anel (L.MILL_STAIR, y 8..16);
#   * venda NO EIXO da porta: balcao atravessado em x 100,4..101,6 / y 9..15, NPC_Mill em (103,5; 12) atras dele,
#     PLAYER_INTERACT_Mill em (97,5; 12), os 2 na cota do piso (G + 0,3); da escada o jogador ja ve o vendedor;
#   * maquinas na FAIXA NORTE (y >= 16,7) atras de um guarda-corpo de parede a parede em y 16,4: pilao de 3 socos,
#     arvore de cames e pinhao no alto; a roda de coroa fica no eixo da roda d'agua (y 12, fixo pela agua), no ALTO
#     da parede leste atras do vendedor (a 4,3 do piso, fora do caminho);
#   * piso livre (so o balcao no meio): x 94,2..104,6 x y 4,2..16,1 = 10,4 x 11,9;
#   * a roda (VFX_WATER_Wheel) e da agua: o eixo entra em x = 107, y 12, z G+8 (chapa de mancal mantida).
MX, MY, MW, MD = L.MILL
MX0, MX1 = MX - MW / 2, MX + MW / 2          # 93, 107
MY0, MY1 = MY - MD / 2, MY + MD / 2          # 3, 21
TW = 1.2                                     # espessura das paredes
IX0, IX1, IY0, IY1 = MX0 + TW, MX1 - TW, MY0 + TW, MY1 - TW     # 94,2 105,8 4,2 19,8
FL = G + 0.3                                 # piso de tabuas (cota dos marcadores)
ZS = G + 5.0                                 # topo da alvenaria (pedra) -> tabuado em cima
ZW = G + 16.0                                # topo das paredes (frechal)
CEIL = ZW - 0.8                              # forro -> pe-direito 14,9
AX_Z = G + 8.0                               # eixo da roda (L.WHEEL: raio 11, eixo L-O na cota G+8)
DY0, DY1 = MY - 5.0, MY + 5.0                # vao da porta oeste: 10 de largura (y 7..17)
DZ1 = FL + 12.2                              # verga: 12,2 livres acima do piso
WX = L.WHEEL[0]
GEAR_X = IX1 - 0.8                           # roda de coroa colada na parede leste (x 104,65..105,35)
GA_R, GB_R = 2.5, 1.2                        # raios (aro) das engrenagens
CAM_Y = MY + GA_R + GB_R + 1.2               # arvore de cames (paralela ao eixo da roda, ao norte, no alto): 16,9
STAMP_Y = CAM_Y + 1.6                        # socos do pilao (encostados no muro norte): 18,5
STAMPS_X = (96.8, 99.0, 101.2)
BED_Z = FL + 2.4                             # leito de minerio dentro do pilao
RAIL_Y = 16.8                                # guarda-corpo das maquinas (x 95,2 -> parede leste; a oeste o pilao fecha)
RAIL_X0 = 95.2
CX0, CX1, CY0, CY1 = 100.4, 101.6, 9.0, 15.0     # balcao atravessado no eixo da porta
NPC_XY = (103.5, MY)
PLAYER_XY = (97.5, MY)
WHEEL_RPM = -4.0                             # rpm do VFX_WATER_Wheel (agente de agua): a roda de coroa acompanha


def _wall_lines():
    """linhas de centro das paredes (a -> b) e a coordenada de mundo que mede o 's' de cada uma"""
    return {"S": (V(MX0, MY0 + TW / 2), V(MX1, MY0 + TW / 2), "x", MX0),
            "N": (V(MX0, MY1 - TW / 2), V(MX1, MY1 - TW / 2), "x", MX0),
            "W": (V(MX0 + TW / 2, IY0), V(MX0 + TW / 2, IY1), "y", IY0),
            "E": (V(MX1 - TW / 2, IY0), V(MX1 - TW / 2, IY1), "y", IY0)}


# aberturas do moinho: parede -> [(u0, u1, z0, z1, tipo)] com u = x (S/N) ou y (L/O) do mundo
MILL_OPEN = {
    "W": [(DY0 - 0.3, DY1 + 0.3, G - 0.7, DZ1 + 0.2, "door")],     # corte escondido nas ombreiras e na verga
    "E": [(5.4, 8.4, ZS + 4.4, ZS + 8.0, "win"), (15.6, 18.6, ZS + 4.4, ZS + 8.0, "win"),
          (MY - 0.75, MY + 0.75, AX_Z - 0.75, AX_Z + 0.75, "hole")],
    "N": [(95.0, 97.6, ZS + 4.0, ZS + 7.6, "win"), (102.4, 105.0, ZS + 4.0, ZS + 7.6, "win"),
          (98.4, 100.4, ZS + 0.7, ZS + 2.9, "hole")],
    "S": [(95.2, 97.8, ZS + 4.6, ZS + 8.2, "win"), (102.2, 104.8, ZS + 4.6, ZS + 8.2, "win")],
}


def lantern(mb, x, y, z_top, drop=1.0):
    """lanterna pendurada (pecas >= 0,3): haste, tampa, corpo aceso com 4 cantoneiras e base"""
    mb.box((0.3, 0.3, drop), (x, y, z_top - drop / 2), (0, 0, 0), "Metal_Dark", 0.0)
    c = z_top - drop - 1.0
    mb.box((1.4, 1.4, 0.35), (x, y, c + 0.92), (0, 0, 0), "Metal_Dark", 0.0)
    mb.box((1.0, 1.0, 1.5), (x, y, c), (0, 0, 0), "Lantern_Glow", 0.0)
    for sx in (-1, 1):
        for sy in (-1, 1):
            mb.box((0.3, 0.3, 1.5), (x + sx * 0.5, y + sy * 0.5, c), (0, 0, 0), "Metal_Dark", 0.0)
    mb.box((1.2, 1.2, 0.3), (x, y, c - 0.9), (0, 0, 0), "Metal_Dark", 0.0)
    return c


def mill_shell(mb, rng):
    A = "HousesMill"
    lines = _wall_lines()
    Fo = faces4(MX0, MY0, MX1, MY1)
    for side, (a, b, ax, u0) in lines.items():
        Lw = (b - a).length
        d = (b - a).normalized()
        ang = math.atan2(d.y, d.x)
        ops = [(o[0] - u0, o[1] - u0, o[2], o[3]) for o in MILL_OPEN[side]]
        # alvenaria de pedra ate ZS (blocos atravessam a parede: aparecem por dentro e por fora)
        FP.masonry_wall(mb, a, b, G - 0.6, ZS, TW, rng, m="Stone_Wall_Light", m2="Stone_Wall_Dark", course=1.45,
                        mix=0.1, openings=[o for o in ops if o[2] < ZS], blk=(2.2, 3.6),
                        quoins=(side in "SN", side in "SN"), core_m="Stone_Wall_Dark", bevel=0.0)
        # tabuado ate o frechal (laje de tabuas recortada nas aberturas)
        FP._masonry_core(mb, a, d, ang, Lw, ZS, ZW - 0.8, TW - 0.2, [o for o in ops if o[3] > ZS], "Wood_Plank")
        # mata-juntas por fora + montantes que atravessam a parede
        f = Fo[side]
        up = [o for o in MILL_OPEN[side]]
        for k in range(int(f.L / 1.45) + 1):
            s = 0.7 + k * 1.45
            if s > f.L - 0.6:
                break
            u = _face_u(side, s)
            spans = _vspans(u, ZS + 0.35, ZW - 0.8, up)
            for za, zb in spans:
                if zb - za > 0.5:
                    f.box(mb, s, (za + zb) / 2, 0.34, 0.3, zb - za, 0.1, "Wood_Dark")
        n = 3 if f.L > 15 else 2
        for k in range(1, n + 1):
            s = f.L * k / (n + 1)
            u = _face_u(side, s)
            if any(o[0] - 0.9 < u < o[1] + 0.9 and o[3] > ZS for o in up):
                continue
            f.box(mb, s, (ZS + ZW) / 2, 0.8, TW + 0.5, ZW - ZS, TW / 2, "Wood_Dark")
        # travessa de apoio do tabuado sobre a pedra (interrompida na porta)
        segs = [(0.0, f.L)]
        for o in up:
            if o[2] < ZS + 0.3 < o[3]:
                s0, s1 = sorted((_face_s(side, o[0]), _face_s(side, o[1])))
                segs = [(p, min(q, s0)) for p, q in segs if min(q, s0) - p > 0.3] + \
                       [(max(p, s1), q) for p, q in segs if q - max(p, s1) > 0.3]
        for s0, s1 in segs:
            f.box(mb, (s0 + s1) / 2, ZS + 0.3, s1 - s0, TW + 0.5, 0.6, TW / 2, "Wood_Dark")
        # janelas (vidro aceso: o moinho trabalha)
        for (ua, ub, za, zb, kind) in up:
            if kind != "win":
                continue
            sa, sb = sorted((_face_s(side, ua), _face_s(side, ub)))
            window(mb, f, (sa + sb) / 2, (za + zb) / 2, sb - sa, zb - za, "cross", sill=False)
    # cunhais de madeira (acima da pedra) e frechal/forro (laje: e o teto visto de dentro)
    for px, py in ((MX0, MY0), (MX1, MY0), (MX1, MY1), (MX0, MY1)):
        mb.box((1.1, 1.1, ZW - ZS + 0.3), (px, py, (ZS + ZW) / 2 - 0.15), (0, 0, 0), "Wood_Dark", 0.0)
    mb.box2((MX0 - 0.3, MY0 - 0.3, ZW - 0.8), (MX1 + 0.3, MY1 + 0.3, ZW), "Wood_Dark", 0.0)
    # vigotas do forro (de dentro)
    for k in range(5):
        y = IY0 + 1.6 + k * (IY1 - IY0 - 3.2) / 4
        mb.box2((IX0, y - 0.35, CEIL - 0.7), (IX1, y + 0.35, CEIL), "Wood_Plank", 0.0)
    # porta larga: ombreiras, verga, soleira de pedra (vao aberto, sem folha)
    xw = MX0 + TW / 2
    for y in (DY0 - 0.45, DY1 + 0.45):
        mb.box((TW + 0.5, 0.9, DZ1 + 1.0 - G), (xw, y, (G + DZ1 + 1.0) / 2), (0, 0, 0), "Wood_Dark", 0.0)
    mb.box((TW + 0.6, DY1 - DY0 + 2.4, 1.0), (xw, MY, DZ1 + 0.5), (0, 0, 0), "Wood_Dark", 0.0)
    mb.box2((MX0 - 1.0, DY0 - 0.3, FL - 0.3), (IX0 - 0.05, DY1 + 0.3, FL), "Stone_Wall_Light", 0.0)
    # placa redonda com a picareta sobre a verga (o jogador entende a funcao sem texto), sob o beiral
    pz = DZ1 + 2.12
    mb.cyl(1.2, 0.35, (MX0 - 0.45, MY, pz), (0, math.pi / 2, 0), "Wood_Dark", 16, bevel=0.0)
    mb.cyl(1.0, 0.3, (MX0 - 0.75, MY, pz), (0, math.pi / 2, 0), "Wood_Plank", 16, bevel=0.0)
    xa = MX0 - 1.02
    pa, pb = V(xa, MY - 0.5, pz - 0.62), V(xa, MY + 0.42, pz + 0.44)
    mb.beam(pa, pb, 0.3, 0.3, "Wood_Dark", 0.0)
    ax = (pb - pa).normalized()
    hd = Vector((0.0, -ax.z, ax.y)).normalized()
    for sg in (-1, 1):
        mb.beam(pb - ax * 0.05, pb + hd * sg * 0.75 - ax * 0.22, 0.5, 0.32, "Metal_Dark", 0.0)
    # telhado de 4 aguas + lanternim de ventilacao na cumeeira
    info = hip_roof(mb, MX0, MY0, MX1, MY1, ZW, "Roof_Terracotta", g=0.58, over=2.2, thick=1.0)
    zr = info["zr"]
    mb.box2((MX - 1.3, MY - 2.2, zr - 0.8), (MX + 1.3, MY + 2.2, zr + 1.6), "Wood_Dark", 0.0)
    for k in range(3):
        for sx in (-1, 1):
            mb.box((0.3, 4.0, 0.36), (MX + sx * 1.45, MY, zr - 0.1 + k * 0.55), (0, sx * 0.55, 0), "Wood_Plank", 0.0)
    hip_roof(mb, MX - 1.3, MY - 2.2, MX + 1.3, MY + 2.2, zr + 1.6, "Roof_Terracotta", g=0.6, over=0.8, thick=0.5,
             rib=0, finial=False, tips=False)
    col_roof(A, info)
    # piso de tabuas
    FP.plank_floor(mb, FP.Frame(MX, MY, 0.0, 0.0), IX1 - IX0, IY1 - IY0, G + 0.02, rng, m="Wood_Plank", pw=1.25,
                   m_alt=("Wood_Plank", "Wood_Dark"))
    # colisao da casca: paredes com o vao da porta, piso, forro
    col_box2(A, (MX0, MY0, G - 0.6), (MX1, MY0 + TW, ZW))
    col_box2(A, (MX0, MY1 - TW, G - 0.6), (MX1, MY1, ZW))
    col_box2(A, (MX1 - TW, MY0 + TW, G - 0.6), (MX1, MY1 - TW, ZW))
    col_box2(A, (MX0, MY0 + TW, G - 0.6), (MX0 + TW, DY0, ZW))
    col_box2(A, (MX0, DY1, G - 0.6), (MX0 + TW, MY1 - TW, ZW))
    col_box2(A, (MX0, DY0, DZ1), (MX0 + TW, DY1, ZW))
    col_box2(A, (MX0 - 0.6, DY0, G - 0.4), (IX0, DY1, FL))
    col_box2(A, (IX0, IY0, G - 0.4), (IX1, IY1, FL))
    col_box2(A, (IX0, IY0, CEIL), (IX1, IY1, ZW))
    return info


def _face_s(side, u):
    """coordenada de mundo (x ou y) -> s da fachada externa (Face)"""
    if side == "S":
        return u - MX0
    if side == "N":
        return MX1 - u
    if side == "E":
        return u - MY0
    return MY1 - u


def _face_u(side, s):
    if side == "S":
        return MX0 + s
    if side == "N":
        return MX1 - s
    if side == "E":
        return MY0 + s
    return MY1 - s


def _vspans(u, za, zb, ops):
    """trechos verticais [za, zb] na coordenada u que nao caem em nenhuma abertura"""
    spans = [(za, zb)]
    for o in ops:
        if o[0] - 0.3 < u < o[1] + 0.3:
            new = []
            for p, q in spans:
                if q <= o[2] - 0.2 or p >= o[3] + 0.2:
                    new.append((p, q))
                    continue
                if o[2] - 0.2 > p:
                    new.append((p, o[2] - 0.2))
                if o[3] + 0.2 < q:
                    new.append((o[3] + 0.2, q))
            spans = new
    return spans


def mill_exterior(mb, rng):
    """lado da roda (chapa de mancal; os pilares de apoio sao do WATER_Wheel_Frame), telheiro sul com caixotes,
    tremonha + calha de minerio ao norte, lanterna na porta"""
    A = "HousesMill"
    # chapa de mancal onde o eixo atravessa a parede leste
    mb.box((0.4, 3.2, 3.2), (MX1 + 0.2, MY, AX_Z), (0, 0, 0), "Metal_Dark", 0.0)
    for dy in (-1.15, 1.15):
        for dz in (-1.15, 1.15):
            mb.box((0.4, 0.5, 0.5), (MX1 + 0.5, MY + dy, AX_Z + dz), (0, 0, 0), "Metal_Dark", 0.0)
    # telheiro sul (meia-agua em 3 pilares) com caixotes de cristal, barril e ferramentas
    ys = MY0 - 5.2
    for x in (MX0 + 1.2, MX, MX1 - 1.2):
        mb.box((0.75, 0.75, 6.3), (x, ys + 0.4, G + 3.15), (0, 0, 0), "Wood_Dark", 0.0)
        mb.box((1.3, 1.3, 0.5), (x, ys + 0.4, G + 0.25), (0, 0, 0), "Stone_Wall_Dark", 0.0)
        col_box2(A, (x - 0.45, ys - 0.05, G - 0.3), (x + 0.45, ys + 0.85, G + 6.3))
    mb.beam(V(MX0 + 0.4, ys + 0.4, G + 6.1), V(MX1 - 0.4, ys + 0.4, G + 6.1), 0.7, 0.7, "Wood_Dark", 0.0)
    zh, zl = G + 8.6, G + 6.3
    slab4(mb, [V(MX0 - 0.6, ys - 0.9, zl), V(MX1 + 0.6, ys - 0.9, zl), V(MX1 + 0.6, MY0 + 0.1, zh),
               V(MX0 - 0.6, MY0 + 0.1, zh)], 0.42, "Roof_Terracotta")
    gg = (zh - zl) / (MY0 + 0.1 - ys + 0.9)
    nrm = Vector((0.0, -gg, 1.0)).normalized()
    for k in range(9):
        x = MX0 + (k + 0.5) * (MW + 1.2) / 9 - 0.6
        mb.beam(V(x, ys - 1.05, zl - 0.06) + nrm * 0.14, V(x, MY0 - 0.6, zh - 0.27) + nrm * 0.14, 0.44, 0.3,
                "Roof_Terracotta", 0.0)
    mb.beam(V(MX0 - 0.7, ys - 1.0, zl - 0.15), V(MX1 + 0.7, ys - 1.0, zl - 0.15), 0.5, 0.5, RIDGE, 0.0)
    for i, (x, y, s) in enumerate(((MX0 + 2.6, MY0 - 2.2, 2.2), (MX0 + 5.0, MY0 - 2.0, 2.0), (MX0 + 2.7, MY0 - 2.2, 1.6))):
        z = G + (2.2 if i == 2 else 0.0)
        crate(mb, (x, y, z), s, rng.uniform(-0.2, 0.2))
    _open_crate(mb, (MX + 2.4, MY0 - 2.3, G), 2.2, 0.15, rng)
    barrel(mb, (MX1 - 2.0, MY0 - 2.4, G), 1.0, 2.5)
    col_box2(A, (MX0 + 1.3, MY0 - 3.5, G - 0.3), (MX0 + 6.2, MY0 - 0.9, G + 3.9))
    col_box2(A, (MX + 1.2, MY0 - 3.5, G - 0.3), (MX1 - 0.8, MY0 - 1.2, G + 2.5))
    _pickaxes(mb, MX + 5.0, MY0 - 0.05, -1)
    # tremonha de minerio + calha que entra pelo muro norte e despeja no pilao
    hx, hy = 99.4, MY1 + 3.9
    for sx in (-1, 1):
        for sy in (-1, 1):
            mb.box((0.6, 0.6, 7.6), (hx + sx * 1.5, hy + sy * 1.5, G + 3.8), (0, 0, 0), "Wood_Dark", 0.0)
        mb.beam(V(hx + sx * 1.5, hy - 1.5, G + 1.2), V(hx + sx * 1.5, hy + 1.5, G + 6.4), 0.3, 0.3, "Wood_Dark", 0.0)
    FP.frustum(mb, (hx, hy, G + 7.4), 1.7, 1.7, 4.6, 4.6, 3.2, "Wood_Plank")
    for sx, sy, lx, ly in ((0, -1, 5.0, 0.5), (0, 1, 5.0, 0.5), (-1, 0, 0.5, 4.0), (1, 0, 0.5, 4.0)):
        mb.box((lx, ly, 0.55), (hx + sx * 2.3, hy + sy * 2.3, G + 10.75), (0, 0, 0), "Wood_Dark", 0.0)
    for k in range(5):
        a = k * math.tau / 5 + 0.4
        mb.rock((hx + math.cos(a) * 1.3, hy + math.sin(a) * 1.3, G + 10.7), (1.3, 1.1, 0.8), "Stone_Wall_Dark", 1)
    for k in range(2):
        a = k * math.pi + 1.1
        FP.crystal_cluster(mb, (hx + math.cos(a) * 0.8, hy + math.sin(a) * 0.8, G + 10.5), 0.55, "Crystal_Blue", rng, 3)
    _chute(mb, V(hx, hy - 0.5, G + 7.7), V(hx, STAMP_Y + 0.45, AX_Z - 2.4))
    col_box2(A, (hx - 2.5, hy - 2.5, G - 0.3), (hx + 2.5, hy + 2.5, G + 10.9))
    ore_cart(mb, (hx + 4.6, hy + 0.6, G), math.pi / 2, rng)
    col_box2(A, (hx + 3.3, hy - 1.3, G - 0.3), (hx + 5.9, hy + 2.5, G + 3.4))
    # lanterna na porta (braco de ferro na parede norte da porta)
    lz = G + 11.6
    ly = DY1 + 1.9
    mb.box((0.4, 1.0, 1.8), (MX0 - 0.2, ly, lz + 0.2), (0, 0, 0), "Wood_Dark", 0.0)
    mb.beam(V(MX0 - 0.3, ly, lz + 0.8), V(MX0 - 1.7, ly, lz + 0.8), 0.3, 0.3, "Metal_Dark", 0.0)
    c = lantern(mb, MX0 - 1.4, ly, lz + 0.65, 0.4)
    light("L_Houses_MillDoor", "POINT", (MX0 - 1.4, ly, c - 1.2), 140, (1.0, 0.62, 0.28), 0.4)


def crate(mb, loc, s, yaw):
    """caixote: corpo de tabuas, 2 cintas escuras (0,15 abaixo do tampo) e cantoneiras 0,1 acima dele"""
    x, y, z = loc
    F = FP.Frame(x, y, z, yaw)
    mb.box((s, s, s), F.p(0, 0, s / 2), F.r(), "Wood_Plank", 0.0)
    for dz in (0.35, s - 0.3):
        mb.box((s + 0.3, s + 0.3, 0.3), F.p(0, 0, dz), F.r(), "Wood_Dark", 0.0)
    for sx in (-1, 1):
        for sy in (-1, 1):
            mb.box((0.35, 0.35, s + 0.1), F.p(sx * s / 2, sy * s / 2, (s + 0.1) / 2), F.r(), "Wood_Dark", 0.0)


def barrel(mb, loc, r=1.0, h=2.5):
    """barril: 2 troncos de cone de aduelas + 2 aros de ferro 0,3 longe das tampas"""
    x, y, z = loc
    mb.cyl(r, h * 0.5, (x, y, z + h * 0.25), (0, 0, 0), "Wood_Plank", 10, r2=r * 1.12, bevel=0.0)
    mb.cyl(r * 1.12, h * 0.5, (x, y, z + h * 0.75), (0, 0, 0), "Wood_Plank", 10, r2=r, bevel=0.0)
    for zz in (0.5, h - 0.5):
        mb.cyl(r * 1.1, 0.3, (x, y, z + zz), (0, 0, 0), "Metal_Dark", 10, bevel=0.0)


def ore_cart(mb, loc, yaw, rng):
    """carrinho de minerio: cacamba de tabuas com aro de ferro, 4 rodas, cristais"""
    x, y, z = loc
    F = FP.Frame(x, y, z, yaw)
    mb.box((3.2, 2.0, 0.4), F.p(0, 0, 1.1), F.r(), "Metal_Dark", 0.0)
    FP.frustum(mb, tuple(F.p(0, 0, 1.3)), 2.6, 1.6, 3.4, 2.3, 1.6, "Wood_Plank", ang=yaw)
    mb.box((3.6, 2.5, 0.3), F.p(0, 0, 2.85), F.r(), "Metal_Dark", 0.0)      # aro 0,1 acima da cacamba
    mb.box((3.0, 1.9, 0.3), F.p(0, 0, 3.0), F.r(), "Stone_Wall_Dark", 0.0)    # minerio 0,15 acima do aro
    for sx in (-1, 1):
        for sy in (-1, 1):
            mb.cyl(0.62, 0.35, F.p(sx * 1.1, sy * 1.2, 0.62), F.r(math.pi / 2, 0, 0), "Metal_Dark", 10, bevel=0.0)
    FP.crystal_cluster(mb, tuple(F.p(0, 0, 3.05)), 0.7, "Crystal_Blue", rng, 5)


def _open_crate(mb, loc, s, yaw, rng, m="Crystal_Blue"):
    x, y, z = loc
    F = FP.Frame(x, y, z, yaw)
    th = 0.3
    mb.box((s, s, th), F.p(0, 0, th / 2), F.r(), "Wood_Plank", 0.0)
    for sx in (-1, 1):
        mb.box((th, s, s), F.p(sx * (s - th) / 2, 0, s / 2), F.r(), "Wood_Plank", 0.0)
        mb.box((s - 2 * th, th, s), F.p(0, sx * (s - th) / 2, s / 2), F.r(), "Wood_Plank", 0.0)
    for dz in (0.3, s - 0.3):
        mb.box((s + 0.3, s + 0.3, 0.3), F.p(0, 0, dz), F.r(), "Wood_Dark", 0.0)
    mb.box((s - 0.6, s - 0.6, 0.3), F.p(0, 0, s * 0.72), F.r(), "Stone_Wall_Dark", 0.0)
    FP.crystal_cluster(mb, tuple(F.p(0, 0, s * 0.8)), s * 0.42, m, rng, 4)


def _pickaxes(mb, x, y_face, out, z0=G, m_handle="Wood_Plank"):
    """duas picaretas encostadas na parede (y_face), inclinadas"""
    for i, dx in enumerate((0.0, 1.0)):
        a = V(x + dx, y_face + out * 1.1, z0 + 0.1)
        b = V(x + dx + 0.3, y_face + out * 0.35, z0 + 3.6)
        mb.beam(a, b, 0.3, 0.3, m_handle, 0.0)
        ax = (b - a).normalized()
        hd = V(1.0, 0.0, 0.0)
        hd = (hd - ax * hd.dot(ax)).normalized()
        for sg in (-1, 1):
            mb.beam(b, b + hd * sg * 1.05 - ax * 0.3, 0.5, 0.3, "Metal_Dark", 0.0)


def _chute(mb, a, b, w=1.4):
    """calha de tabuas (fundo + 2 bordas) de a ate b"""
    d = (b - a).normalized()
    side = d.cross(Vector((0, 0, 1))).normalized()
    upn = side.cross(d).normalized()
    if upn.z < 0:
        upn = -upn
    mb.beam(a, b, w, 0.3, "Wood_Plank", 0.0)
    for s in (-1, 1):
        mb.beam(a + side * s * (w / 2 + 0.15) + upn * 0.35, b + side * s * (w / 2 + 0.15) + upn * 0.35, 0.3, 0.8,
                "Wood_Dark", 0.0)


def gear_wheel(mb, cx, cy, cz, r, teeth, rim_w=0.62, depth=0.7, m="Wood_Dark", hub="Wood_Dark"):
    """engrenagem de madeira no plano YZ (eixo X): aro varrido, dentes radiais, raios cruzados e cubo"""
    n = 20 if r > 1.5 else 12
    pts = [V(cx, cy + math.cos(math.tau * k / n) * r, cz + math.sin(math.tau * k / n) * r) for k in range(n + 1)]
    mb.sweep(pts, [(-rim_w / 2, -depth / 2), (rim_w / 2, -depth / 2), (rim_w / 2, depth / 2), (-rim_w / 2, depth / 2)],
             m, True, up=(1, 0, 0), caps=False)
    for k in range(teeth):
        a = math.tau * k / teeth
        mb.box((depth * 0.9, 0.7, 0.5), (cx, cy + math.cos(a) * (r + rim_w / 2 + 0.3),
                                         cz + math.sin(a) * (r + rim_w / 2 + 0.3)), (a, 0, 0), m, 0.0)
    for a in (0.3, 0.3 + math.pi / 2):
        mb.beam(V(cx, cy - math.cos(a) * r, cz - math.sin(a) * r), V(cx, cy + math.cos(a) * r, cz + math.sin(a) * r),
                0.45, 0.5, m, 0.0)
    mb.cyl(0.66 if r > 1.5 else 0.52, depth + 0.3, (cx, cy, cz), (0, math.pi / 2, 0), hub, 10, bevel=0.0)


def mill_machine(rng):
    """eixo da roda -> roda de coroa (VFX, gira com a roda, no alto da parede leste) -> pinhao na arvore de cames
    (VFX, no alto da faixa norte) -> cames levantam 3 socos (VFX, sobe-e-desce) que batem o minerio no pilao.
    Cada peca movel e de UM material so (menos MeshParts; os VFX nao passam pelo fold do export), menos os socos."""
    # eixo da roda + roda de coroa
    ga = HMB("VFX_VIL_MillGear", "12_VFX_HELPERS", random.Random(4431), detail="near")
    # trecho INTERNO do eixo (o VFX_WATER_Wheel ja traz o eixo da face leste do moinho, x = MX1, ate a roda)
    x_end = MX1 + 0.05
    ga.cyl(0.62, x_end - (GEAR_X - 0.7), ((x_end + GEAR_X - 0.7) / 2, MY, AX_Z), (0, math.pi / 2, 0), "Wood_Dark", 10,
           bevel=0.0)
    gear_wheel(ga, GEAR_X, MY, AX_Z, GA_R, 20)
    oa = ga.finish()
    oa["pivot"] = (float(L.WHEEL[0]), MY, AX_Z)
    oa["axis"] = (1.0, 0.0, 0.0)
    oa["rpm"] = WHEEL_RPM
    oa["note"] = "mesmo eixo e mesmo rpm do VFX_WATER_Wheel (roda de baixo, -4 rpm em torno de +X)"
    # arvore de cames + pinhao (no alto, sobre o guarda-corpo)
    gb = HMB("VFX_VIL_MillCamshaft", "12_VFX_HELPERS", random.Random(4432), detail="near")
    gb.cyl(0.46, IX1 - 0.2 - (IX0 + 0.6), ((IX1 - 0.2 + IX0 + 0.6) / 2, CAM_Y, AX_Z), (0, math.pi / 2, 0),
           "Wood_Dark", 10, bevel=0.0)
    gear_wheel(gb, GEAR_X, CAM_Y, AX_Z, GB_R, 10, rim_w=0.5, depth=0.7)
    for i, x in enumerate(STAMPS_X):
        a0 = i * math.tau / 3
        for k in range(2):
            a = a0 + k * math.pi
            tip = V(x, CAM_Y + math.cos(a) * 1.45, AX_Z + math.sin(a) * 1.45)
            gb.beam(V(x, CAM_Y, AX_Z), tip, 0.55, 0.7, "Wood_Dark", 0.0)
        gb.cyl(0.66, 0.9, (x, CAM_Y, AX_Z), (0, math.pi / 2, 0), "Wood_Dark", 8, bevel=0.0)
    ob = gb.finish()
    ob["pivot"] = (GEAR_X, CAM_Y, AX_Z)
    ob["axis"] = (1.0, 0.0, 0.0)
    ob["rpm"] = -WHEEL_RPM * GA_R / GB_R
    ob["note"] = "pinhao engrenado na roda de coroa (razao %.2f, sentido contrario ao da roda)" % (GA_R / GB_R)
    # socos do pilao (sobe e desce): hastes de madeira, sapatas de ferro
    st = HMB("VFX_VIL_MillStamps", "12_VFX_HELPERS", random.Random(4433), detail="near")
    for x in STAMPS_X:
        st.box((0.7, 0.7, AX_Z + 4.5 - BED_Z - 1.6), (x, STAMP_Y, (AX_Z + 4.5 + BED_Z + 1.6) / 2), (0, 0, 0),
               "Wood_Dark", 0.0)
        st.box((1.4, 1.4, 1.6), (x, STAMP_Y, BED_Z + 0.8), (0, 0, 0), "Metal_Dark", 0.0)
        st.box((1.0, 1.4, 0.6), (x, STAMP_Y - 0.55, AX_Z + 0.9), (0, 0, 0), "Metal_Dark", 0.0)
        st.box((1.0, 1.0, 0.45), (x, STAMP_Y, AX_Z + 4.5), (0, 0, 0), "Metal_Dark", 0.0)
    os_ = st.finish()
    os_["pivot"] = (STAMPS_X[1], STAMP_Y, BED_Z)
    os_["axis"] = (0.0, 0.0, 1.0)
    os_["bob"] = 1.2
    os_["rate"] = 2.0 * abs(WHEEL_RPM * GA_R / GB_R) / 60.0
    os_["note"] = "socos sobem 1,2 e caem (1 batida por came: 2 por volta da arvore de cames), defasados de 1/3"


def mill_interior(mb, rng):
    A = "HousesMill"
    # ---- balcao de venda ATRAVESSADO no eixo da porta (face oeste para o jogador, vendedor a leste)
    mb.box2((CX0 + 0.15, CY0 + 0.1, FL), (CX1 - 0.1, CY1 - 0.1, FL + 3.1), "Wood_Plank", 0.0)
    mb.box2((CX0 - 0.2, CY0 - 0.2, FL + 3.1), (CX1 + 0.2, CY1 + 0.2, FL + 3.5), "Wood_Dark", 0.0)
    mb.box2((CX0 - 0.05, CY0 + 0.1, FL), (CX0 + 0.3, CY1 - 0.1, FL + 0.5), "Wood_Dark", 0.0)
    y = CY0 + 0.55
    while y < CY1 - 0.3:
        mb.box((0.3, 0.3, 2.5), (CX0 + 0.1, y, FL + 1.85), (0, 0, 0), "Wood_Dark", 0.0)
        y += 0.95
    for yy in (CY0 + 0.1, CY1 - 0.1):          # cabeceiras escuras (fecham as pontas do corpo de tabuas)
        mb.box2((CX0 - 0.05, yy - 0.2, FL), (CX1 + 0.05, yy + 0.2, FL + 3.1), "Wood_Dark", 0.0)
    bz = FL + 3.5
    # balanca de pratos (ferro) e bandeja de cristais no tampo
    bx = (CX0 + CX1) / 2
    mb.box((1.0, 1.0, 0.3), (bx, CY1 - 1.3, bz + 0.15), (0, 0, 0), "Metal_Dark", 0.0)
    mb.box((0.3, 0.3, 1.7), (bx, CY1 - 1.3, bz + 1.1), (0, 0, 0), "Metal_Dark", 0.0)
    mb.box((0.3, 2.5, 0.3), (bx, CY1 - 1.3, bz + 1.9), (0, 0, 0), "Metal_Dark", 0.0)
    for sy in (-1, 1):
        mb.cyl(0.6, 0.3, (bx, CY1 - 1.3 + sy * 1.1, bz + 1.0), (0, 0, 0), "Metal_Dark", 8, r2=0.45, bevel=0.0)
        mb.box((0.3, 0.3, 0.7), (bx, CY1 - 1.3 + sy * 1.1, bz + 1.5), (0, 0, 0), "Metal_Dark", 0.0)
    mb.box((1.1, 1.8, 0.6), (bx, CY0 + 1.4, bz + 0.3), (0, 0, 0), "Wood_Dark", 0.0)
    FP.crystal_cluster(mb, (bx, CY0 + 1.4, bz + 0.6), 0.5, "Crystal_Blue", rng, 3)
    col_box2(A, (CX0 - 0.2, CY0 - 0.2, FL), (CX1 + 0.2, CY1 + 0.2, FL + 3.5))
    # ---- estante baixa atras do vendedor (parede leste, lado sul: abaixo da roda de coroa)
    sx0, sx1, sy0, sy1 = IX1 - 1.0, IX1, IY0 + 0.6, 9.4
    for yy in (sy0, sy1):
        mb.box((1.0, 0.4, 4.2), ((sx0 + sx1) / 2, yy, FL + 2.1), (0, 0, 0), "Wood_Dark", 0.0)
    for i, z in enumerate((FL + 0.4, FL + 2.1, FL + 3.8)):
        mb.box2((sx0 + 0.1, sy0 + 0.2, z - 0.15), (sx1 - 0.15, sy1 - 0.2, z + 0.15), "Wood_Plank", 0.0)
        if i == 0:
            continue
        for j in range(3):
            yy = sy0 + 1.0 + j * (sy1 - sy0 - 2.0) / 2
            if (i + j) % 2:
                FP.crystal_cluster(mb, ((sx0 + sx1) / 2, yy, z + 0.15), 0.45, "Crystal_Blue", rng, 2)
            else:
                mb.cyl(0.42, 0.9, ((sx0 + sx1) / 2, yy, z + 0.6), (0, 0, 0), "Wood_Plank", 8, bevel=0.0)
    col_box2(A, (sx0, sy0 - 0.2, FL), (sx1, sy1 + 0.2, FL + 4.2))
    # ---- mancais do eixo da roda e da arvore de cames na parede leste (fixos)
    mb.box((0.8, 1.4, 1.4), (IX1 + 0.2, MY, AX_Z), (0, 0, 0), "Metal_Dark", 0.0)
    mb.box((0.8, 1.2, 1.2), (IX1 + 0.2, CAM_Y, AX_Z), (0, 0, 0), "Metal_Dark", 0.0)
    # ---- picaretas penduradas na parede sul (enfeite de parede: nao ocupa o piso)
    for i, x in enumerate((96.2, 97.6)):
        a, b = V(x, IY0 + 0.45, FL + 2.2), V(x + 0.5, IY0 + 0.45, FL + 5.4)
        mb.beam(a, b, 0.3, 0.3, "Wood_Plank", 0.0)
        ax = (b - a).normalized()
        hd = Vector((ax.z, 0.0, -ax.x)).normalized()
        for sg in (-1, 1):
            mb.beam(b, b + hd * sg * 1.0 - ax * 0.3, 0.5, 0.32, "Metal_Dark", 0.0)
    mb.box((3.4, 0.4, 0.4), (96.9, IY0 + 0.2, FL + 5.0), (0, 0, 0), "Wood_Dark", 0.0)
    # ---- FAIXA NORTE: pilao (almofariz) ao longo do muro norte: base de pedra, caixa de tabuas, leito de minerio
    px0, px1 = STAMPS_X[0] - 1.6, STAMPS_X[-1] + 1.6
    py0, py1 = STAMP_Y - 1.3, IY1
    mb.box2((px0 - 0.2, py0 - 0.2, FL - 0.1), (px1 + 0.2, py1, FL + 1.1), "Stone_Wall_Dark", 0.0)
    mb.box2((px0, py0, FL + 1.1), (px1, py1, BED_Z), "Wood_Plank", 0.0)
    for (a, b) in (((px0 - 0.1, py0 - 0.1), (px1 + 0.1, py0 + 0.3)), ((px0 - 0.1, py1 - 0.4), (px1 + 0.1, py1)),
                   ((px0 - 0.1, py0 - 0.1), (px0 + 0.3, py1)), ((px1 - 0.3, py0 - 0.1), (px1 + 0.1, py1))):
        mb.box2((a[0], a[1], BED_Z - 0.1), (b[0], b[1], BED_Z + 0.6), "Wood_Dark", 0.0)
    for x in (px0 + 0.8, (px0 + px1) / 2, px1 - 0.8):
        mb.box2((x - 0.2, py0 - 0.15, FL + 1.1), (x + 0.2, py1, BED_Z - 0.1), "Metal_Dark", 0.0)
    for x in (97.9, 100.1):
        FP.crystal_cluster(mb, (x, STAMP_Y - 0.1, BED_Z - 0.05), 0.45, "Crystal_Blue", rng, 3)
    # estrutura-guia dos socos + bracos que seguram a arvore de cames
    gx0, gx1 = px0 - 0.5, px1 + 0.5
    for x in (gx0, gx1):
        mb.box((0.8, 0.8, CEIL - FL - 1.1), (x, STAMP_Y, (FL + 1.1 + CEIL) / 2), (0, 0, 0), "Wood_Dark", 0.0)
        mb.beam(V(x, STAMP_Y - 0.3, AX_Z), V(x, CAM_Y, AX_Z), 0.6, 0.8, "Wood_Dark", 0.0)
        mb.box((0.9, 1.1, 1.2), (x, CAM_Y, AX_Z), (0, 0, 0), "Metal_Dark", 0.0)
    for z in (BED_Z + 3.4, AX_Z + 3.8):
        for dy in (-0.62, 0.62):
            mb.box2((gx0, STAMP_Y + dy - 0.2, z - 0.3), (gx1, STAMP_Y + dy + 0.2, z + 0.3), "Wood_Dark", 0.0)
    col_box2(A, (gx0 - 0.4, py0 - 0.3, FL), (gx1 + 0.4, IY1, CEIL))
    # bica de saida -> caixa de cristal moido (canto NE, atras do guarda-corpo)
    _chute(mb, V(px1 - 0.2, STAMP_Y - 1.0, BED_Z + 0.1), V(px1 + 1.9, STAMP_Y - 1.0, FL + 1.9), 0.9)
    _open_crate(mb, (IX1 - 1.3, STAMP_Y - 0.6, FL), 1.8, 0.0, rng)
    col_box2(A, (IX1 - 2.3, STAMP_Y - 1.6, FL), (IX1, IY1, FL + 2.0))
    # ---- guarda-corpo de parede a parede em y = RAIL_Y: o jogador olha as maquinas, nao entra
    a3, b3 = V(RAIL_X0, RAIL_Y, FL), V(IX1, RAIL_Y, FL)
    n = 4
    for i in range(n + 1):
        p = a3 + (b3 - a3) * (i / n)
        p.x = min(max(p.x, RAIL_X0 + 0.25), IX1 - 0.25)
        mb.box((0.5, 0.5, 3.8), (p.x, p.y, FL + 1.9), (0, 0, 0), "Wood_Dark", 0.0)
    for zz, hh in ((FL + 3.4, 0.4), (FL + 1.9, 0.3)):
        mb.box2((RAIL_X0 + 0.1, RAIL_Y - 0.15, zz - hh / 2), (IX1, RAIL_Y + 0.15, zz + hh / 2), "Wood_Plank", 0.0)
    for i in range(n):                          # balaustres entre os postes
        xa = RAIL_X0 + (IX1 - RAIL_X0) * i / n
        for k in (1, 2, 3):          # entre as 2 travessas (sem faces coplanares com elas)
            mb.box((0.3, 0.3, 1.15), (xa + (IX1 - RAIL_X0) / n * k / 4, RAIL_Y, FL + 2.625), (0, 0, 0), "Wood_Dark",
                   0.0)
    col_box2(A, (RAIL_X0, RAIL_Y - 0.3, FL), (IX1, RAIL_Y + 0.3, FL + 4.0))
    # ---- lanternas penduradas no forro + luzes internas (o jogador ve o vendedor de longe)
    lantern(mb, PLAYER_XY[0], MY - 3.5, CEIL, 3.4)
    light("L_Houses_MillInterior", "POINT", (PLAYER_XY[0], MY - 1.0, G + 10.0), 520, (1.0, 0.66, 0.32), 0.8)
    lantern(mb, NPC_XY[0] - 0.8, MY + 2.6, CEIL, 3.0)
    light("L_Houses_MillCounter", "POINT", (NPC_XY[0] - 1.0, MY, G + 10.5), 280, (1.0, 0.66, 0.32), 0.6)
    # ---- marcadores de jogo (cota do piso): NPC atras do balcao olhando a porta, jogador na frente dele
    mk("NPC_Mill", (NPC_XY[0], NPC_XY[1], FL), (0, 0, math.pi / 2), 2.0, "ARROWS",
       props={"note": "vendedor do posto do minerador (atras do balcao atravessado, olha para a porta oeste)"})
    mk("PLAYER_INTERACT_Mill", (PLAYER_XY[0], PLAYER_XY[1], FL), (0, 0, -math.pi / 2), 2.0, "SPHERE",
       props={"note": "frente do balcao, no eixo da porta (y 12), dentro do moinho"})


def mill():
    rng = random.Random(4403)
    mb = HMB("VIL_Mill", "04_VILLAGE", rng, detail="near")
    mill_shell(mb, rng)
    mill_exterior(mb, rng)
    mill_interior(mb, rng)
    mb.finish()
    mill_machine(rng)


def build():
    houses_near()
    houses_upper()
    mill()
