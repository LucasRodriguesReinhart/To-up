# sn_shop.py - TEMPLO DOS MERCADORES (loja de mochilas), leste da praca, olhando para ela.
# Historia: um templo pequeno do deus-ferreiro que os mercadores restauraram - pedra antiga em fiadas (cada bloco uma
# peca, juntas fundas), portico de 4 colunas com frontao e o emblema da mochila em ouro, telhado novo de telha-canal
# terracota sobre caibros de madeira; dentro, um armazem de viajante bem arrumado.
# Planta (frame local: +y = frente/praca, x ao longo da fachada, z a partir da praca Y 7; piso interno z 1,2 = Y 8,2):
#   estilobato 2 degraus | cella x +-14, y -11,2..4,6 (paredes 1,6) | porta em arco 7 x 9 | portico y 4,6..12,4
#   balcao em y -2,6 (x -7..5, passagem do vendedor em x 5..7) | vendedor y -4,5 | jogador/PadLoja y +1,5
#   fundo: 3 prateleiras com mochilas | lado oeste: ganchos com bolsas + manequim | lado leste: vitrine da mochila
#   lendaria (cristal) | 2 janelas em arco | vigas do teto com 2 lanternas penduradas | tapete na entrada
import math

import bmesh
import fm_lib
import sn_lib as SL
import sn_layout as L
from mathutils import Matrix, Vector
from sn_kit import column, worn_block, moss_patch, ivy, rng, brazier, crystal_cluster, flower_bed
from wb_kit import Fr, bb, beam, cyl, lathe, poly_prism, text, barrel, crate, sack, banner, lantern
from wb_lib import RB

V = Vector
COLL = "05_SERVICES"
AREA = "Shop"
FL = 1.2                       # piso interno (local z) = Y_SHOP
WALL_T = 1.6
CX = 14.0                      # meia largura externa da cella
YB, YF = -11.2, 4.6            # fundo / frente da cella (faces externas)
COL_Y = 10.8
TOP = 14.6                     # topo das paredes / arquitrave
EAVE = 18.1                    # beiral (arquitrave 14,6..15,8 + friso 15,8..17,6 + cornija)
PITCH = 0.42
CANVAS = ("SN_CanvasRed", "SN_CanvasBlue", "SN_CanvasGreen", "SN_CanvasOchre")


# ------------------------------------------------------------------ parede de cantaria (bloco a bloco)
def ashlar_wall(b, F, x0, x1, z0, z1, y0, y1, holes=(), mat="SN_Ashlar", seed=0, course=1.35, gap=0.09,
                core="SN_Ashlar_Dark"):
    """parede no plano x-z do frame, espessura y0..y1: miolo recuado (juntas escuras) + blocos em fiadas desencontradas
    com chanfro; os vaos (x0, x1, z0, z1) cortam os blocos. Face externa = y1."""
    r = rng("aw", seed)
    # miolo (aparece nas juntas)
    from wb_house import wall_holes
    wall_holes(b, F, x0, x1, z0, z1, y0 + 0.12, y1 - 0.12, list(holes), core)
    n = max(1, int(round((z1 - z0) / course)))
    ch = (z1 - z0) / n
    for k in range(n):
        za, zb = z0 + k * ch + gap / 2, z0 + (k + 1) * ch - gap / 2
        x = x0 - (r.uniform(0.4, 1.2) if k % 2 else 0.0)
        while x < x1 - 0.05:
            ln = r.uniform(1.9, 3.3)
            xa, xb = max(x0, x), min(x1, x + ln)
            x += ln
            # recorta pelos vaos (divide o bloco)
            segs = [(xa, xb)]
            for (hx0, hx1, hz0, hz1) in holes:
                if hz1 <= za or hz0 >= zb:
                    continue
                nsegs = []
                for (sa, sb) in segs:
                    if sb <= hx0 or sa >= hx1:
                        nsegs.append((sa, sb))
                        continue
                    if sa < hx0:
                        nsegs.append((sa, hx0))
                    if sb > hx1:
                        nsegs.append((hx1, sb))
                segs = nsegs
            for (sa, sb) in segs:
                if sb - sa < 0.35:
                    continue
                d = r.uniform(-0.04, 0.05)
                bb(b, F, sa + gap / 2, sb - gap / 2, y0 + d, y1 + d, za, zb, mat, bevel=0.1)


def roof_tiles(b, F, x0, x1, y0, y1, z_e, pitch, side, mat="SN_RoofTile", step=1.25):
    """agua do telhado (cumeeira ao longo de y, em x = 0): telha-canal em colunas descendo para o beiral em x0/x1"""
    xe = x1 if side > 0 else x0
    run = abs(xe)
    zr = z_e + run * pitch
    # tabuado por baixo (forro visto de dentro) e telhas-canal por cima
    nrm = V((side * pitch, 0, 1)).normalized()
    for k in range(int((y1 - y0) / step) + 1):
        yy = y0 + k * step
        if yy > y1:
            break
        a = F.p(0.0, yy, zr + 0.25) + V((0, 0, 0))
        c = F.p(xe, yy, z_e + 0.25)
        b.cyl(a, c, step * 0.52, mat, seg=6, r1=step * 0.5)
    # ripas de beiral e tabua inferior
    p0, p1 = (0.0, y0 - 0.3, zr - 0.15), (xe, y0 - 0.3, z_e - 0.15)
    for (yy0, yy1) in ((y0 - 0.4, y1 + 0.4),):
        bm = bmesh.new()
        q = [F.p(0.0, yy0, zr - 0.1), F.p(xe, yy0, z_e - 0.1), F.p(xe, yy1, z_e - 0.1), F.p(0.0, yy1, zr - 0.1)]
        q2 = [v + V((0, 0, -0.35)) for v in q]
        vs = [bm.verts.new(v) for v in q]
        vs2 = [bm.verts.new(v) for v in q2]
        bm.faces.new(vs)
        bm.faces.new(list(reversed(vs2)))
        for i in range(4):
            bm.faces.new((vs[i], vs2[i], vs2[(i + 1) % 4], vs[(i + 1) % 4]))
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
        b.mesh(bm, "SN_WoodAged")
    return zr


# ------------------------------------------------------------------ mercadoria
def backpack(b, F, x, y, z, s=1.0, col="SN_CanvasRed", seed=0, turn=0.0, roll="SN_CanvasCream", trim="SN_Gold"):
    """mochila de viajante: corpo arredondado, aba de couro, bolso frontal, bolsos laterais, alcas com fivelas de
    ouro e saco de dormir enrolado em cima. (x, y, z) = centro da base; frente para +y do frame (girada por turn)."""
    Fm = F.sub(x, y, z, turn)
    worn_block(b, Fm, 0.0, 0.0, 1.0 * s, (1.6 * s, 1.0 * s, 2.0 * s), col, seed=("bp", seed), chips=0, bevel=0.28 * s)
    worn_block(b, Fm, 0.0, 0.08 * s, 1.92 * s, (1.68 * s, 1.1 * s, 0.42 * s), "SN_Leather", seed=("bpf", seed), chips=0,
               bevel=0.14 * s)
    worn_block(b, Fm, 0.0, 0.62 * s, 0.62 * s, (1.15 * s, 0.34 * s, 0.85 * s), col, seed=("bpp", seed), chips=0,
               bevel=0.12 * s)
    for sx in (-1, 1):
        cyl(b, Fm, (sx * 0.92 * s, 0.05 * s, 0.25 * s), (sx * 0.92 * s, 0.05 * s, 1.15 * s), 0.26 * s, col, seg=8)
        beam(b, Fm, (sx * 0.38 * s, 0.53 * s, 0.4 * s), (sx * 0.38 * s, 0.6 * s, 1.95 * s), 0.12 * s, 0.2 * s, "SN_Leather")
        bb(b, Fm, sx * 0.38 * s - 0.14 * s, sx * 0.38 * s + 0.14 * s, 0.62 * s, 0.72 * s, 1.18 * s, 1.36 * s, trim)
    cyl(b, Fm, (-0.95 * s, -0.05 * s, 2.42 * s), (0.95 * s, -0.05 * s, 2.42 * s), 0.34 * s, roll, seg=10)
    for sx in (-0.55, 0.55):
        cyl(b, Fm, (sx * s - 0.07 * s, -0.05 * s, 2.42 * s), (sx * s + 0.07 * s, -0.05 * s, 2.42 * s), 0.37 * s,
            "SN_Leather", seg=10)


def scale_(b, F, x, y, z):
    """balanca de bronze sobre o balcao"""
    cyl(b, F, (x, y, z), (x, y, z + 0.15), 0.45, "SN_Bronze", seg=10)
    cyl(b, F, (x, y, z + 0.15), (x, y, z + 1.7), 0.08, "SN_Bronze", seg=6)
    beam(b, F, (x - 1.0, y, z + 1.68), (x + 1.0, y, z + 1.68), 0.1, 0.1, "SN_Bronze")
    for sx in (-1, 1):
        for d in ((0.25, 0), (-0.25, 0), (0, 0.25)):
            beam(b, F, (x + sx * 1.0, y, z + 1.66), (x + sx * 1.0 + d[0], y + d[1], z + 0.82), 0.03, 0.03, "SN_Gold")
        cyl(b, F, (x + sx * 1.0, y, z + 0.72), (x + sx * 1.0, y, z + 0.82), 0.42, "SN_Bronze", seg=10, r1=0.36)


def coins(b, F, x, y, z, seed=0):
    r = rng("coin", seed)
    for k in range(4):
        cx, cy = x + r.uniform(-0.5, 0.5), y + r.uniform(-0.3, 0.3)
        h = r.uniform(0.2, 0.6)
        cyl(b, F, (cx, cy, z), (cx, cy, z + h), 0.22, "SN_Gold", seg=8)


def book(b, F, x, y, z, turn=10.0):
    Fb = F.sub(x, y, z, turn)
    bb(b, Fb, -0.6, 0.6, -0.45, 0.45, 0.0, 0.16, "SN_Leather")
    bb(b, Fb, -0.55, 0.55, -0.4, 0.4, 0.16, 0.22, "SN_Paper")
    beam(b, Fb, (0.0, -0.4, 0.22), (0.0, 0.4, 0.22), 0.06, 0.03, "SN_Leather")


def mannequin(b, F, x, y, z, col, seed, turn=0.0):
    Fm = F.sub(x, y, z, turn)
    cyl(b, Fm, (0, 0, 0), (0, 0, 0.12), 0.7, "SN_WoodAged", seg=10)
    cyl(b, Fm, (0, 0, 0.12), (0, 0, 2.4), 0.09, "SN_WoodAged", seg=6)
    lathe(b, Fm, 0.0, 0.0, [(0.0, 0.0), (0.55, 0.05), (0.62, 0.5), (0.5, 1.1), (0.7, 1.6), (0.32, 1.9), (0.0, 1.95)],
          "SN_CanvasCream", 12, z0=2.3)
    backpack(b, Fm, 0.0, -0.95, 2.45, 0.85, col, seed, turn=180.0)


# ------------------------------------------------------------------ o templo
def temple(b, F):
    # estilobato: 2 degraus + soleira
    bb(b, F, -16.0, 16.0, -13.0, 14.2, -0.8, 0.6, "SN_Ashlar_Dark", bevel=0.12)
    bb(b, F, -15.0, 15.0, -12.2, 12.8, 0.6, FL, "SN_Ashlar", bevel=0.12)
    # piso do portico em lajes
    for k in range(10):
        x0 = -14.4 + k * 2.88
        bb(b, F, x0 + 0.05, x0 + 2.83, YF + 0.05, 12.7, FL - 0.1, FL + 0.02, "SN_Plaza", bevel=0.06)
    # paredes da cella: fundo, laterais (com janela em arco) e frente (porta em arco)
    from wb_house import arch_holes, voussoirs
    win = arch_holes(-3.0, 3.2, FL + 5.0, 5.2)
    ashlar_wall(b, F.sub(0, YB + WALL_T / 2, 0, 180), -CX, CX, FL, TOP, -WALL_T / 2, WALL_T / 2, seed="back")
    for s in (-1, 1):
        Fs = F.sub(s * (CX - WALL_T / 2), (YB + YF) / 2, 0, -90 * s)
        ashlar_wall(b, Fs, -(YF - YB) / 2, (YF - YB) / 2, FL, TOP, -WALL_T / 2, WALL_T / 2,
                    holes=[(hx0 * -s if False else hx0, hx1, hz0, hz1) for (hx0, hx1, hz0, hz1) in win], seed=("side", s))
        voussoirs(b, Fs, -3.0, FL + 5.0 + 5.2 - 1.6, 1.6, ring=0.7, n=7, y0=WALL_T / 2 - 0.1, y1=WALL_T / 2 + 0.22,
                  mat="SN_Carved")
        bb(b, Fs, -3.0 - 2.0, -3.0 + 2.0, WALL_T / 2 - 0.1, WALL_T / 2 + 0.45, FL + 4.6, FL + 5.0, "SN_Carved")
        # postigos de madeira abertos
        for sx in (-1, 1):
            bb(b, Fs, -3.0 + sx * 1.6 + (sx * 0.02), -3.0 + sx * 3.3, WALL_T / 2 + 0.05, WALL_T / 2 + 0.25, FL + 5.1,
               FL + 9.0, "SN_WoodAged")
    door = arch_holes(0.0, 7.0, FL, 9.0)
    Ff = F.sub(0, YF - WALL_T / 2, 0, 0)
    ashlar_wall(b, Ff, -CX, CX, FL, TOP, -WALL_T / 2, WALL_T / 2, holes=door, seed="front")
    voussoirs(b, Ff, 0.0, FL + 9.0 - 3.5, 3.5, ring=1.1, n=11, y0=WALL_T / 2 - 0.1, y1=WALL_T / 2 + 0.3, mat="SN_Carved")
    # pilastras nos cantos da cella
    for (sx, sy) in ((-1, 1), (1, 1), (-1, -1), (1, -1)):
        yy = YF if sy > 0 else YB
        bb(b, F, sx * CX - 0.9, sx * CX + 0.9, yy - 0.9, yy + 0.9, FL, TOP, "SN_Carved", bevel=0.12)
    # portico: 4 colunas + arquitrave + friso com o letreiro + cornija
    for xx in (-11.6, -4.4, 4.4, 11.6):
        column(b, F, xx, COL_Y, FL, TOP - FL - 1.85, r0=1.05, seed=("shc", xx), moss=False)
    bb(b, F, -14.8, 14.8, COL_Y - 1.4, COL_Y + 1.4, TOP - 0.05, TOP + 1.2, "SN_Carved", bevel=0.12)
    bb(b, F, -14.4, 14.4, COL_Y - 1.2, COL_Y + 1.15, TOP + 1.2, EAVE - 0.5, "SN_Ashlar", bevel=0.1)
    bb(b, F, -15.4, 15.4, COL_Y - 1.7, COL_Y + 1.8, EAVE - 0.5, EAVE, "SN_Carved", bevel=0.12)
    Ft = Fr(F.p(0, COL_Y + 1.25, 0), (F.f.x, F.f.y))
    text(b, Ft, "LOJA DE MOCHILAS", 1.0, "SN_Gold", 0.0, -0.05, TOP + 2.1, thick=0.24, bold=True)
    # vigas do portico ligando arquitrave a parede
    for xx in (-11.6, -4.4, 4.4, 11.6):
        bb(b, F, xx - 0.5, xx + 0.5, YF, COL_Y - 1.0, TOP + 0.3, TOP + 1.1, "SN_WoodAged")
    # topo das paredes laterais/fundo (cornija ate o beiral)
    bb(b, F, -CX - 0.4, CX + 0.4, YB - 0.4, YF + 0.4, TOP, EAVE - 0.5, "SN_Ashlar", bevel=0.1)
    bb(b, F, -CX - 1.0, CX + 1.0, YB - 1.0, YB + 1.0, EAVE - 0.5, EAVE, "SN_Carved", bevel=0.12)
    for s in (-1, 1):
        bb(b, F, s * CX - 1.0, s * CX + 1.0, YB - 1.0, COL_Y + 1.8, EAVE - 0.5, EAVE, "SN_Carved", bevel=0.12)
    # frontao (triangulo) com moldura e o emblema da mochila em ouro
    half = CX + 1.0
    rise = half * PITCH
    for (yy0, yy1, m) in ((COL_Y + 0.6, COL_Y + 1.2, "SN_Ashlar"),):
        bm = bmesh.new()
        pts = [(-half + 0.8, EAVE), (half - 0.8, EAVE), (0.0, EAVE + rise - 0.6)]
        a = [bm.verts.new(F.p(x, yy0, z)) for (x, z) in pts]
        c = [bm.verts.new(F.p(x, yy1, z)) for (x, z) in pts]
        bm.faces.new(a)
        bm.faces.new(list(reversed(c)))
        for i in range(3):
            bm.faces.new((a[i], c[i], c[(i + 1) % 3], a[(i + 1) % 3]))
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
        b.mesh(bm, m)
    for s in (-1, 1):
        beam(b, F, (s * half, COL_Y + 1.6, EAVE + 0.1), (0.0, COL_Y + 1.6, EAVE + rise + 0.1), 0.9, 0.7, "SN_Carved")
    backpack(b, F, 0.0, COL_Y + 1.25, EAVE + 0.6, 1.6, "SN_Gold", "emb", roll="SN_Gold", trim="SN_Bronze")
    # telhado: duas aguas de telha-canal (cumeeira ao longo de y) + cumeeira
    y0r, y1r = YB - 1.2, COL_Y + 1.9
    for s in (-1, 1):
        roof_tiles(b, F, -half - 0.6, half + 0.6, y0r, y1r, EAVE, PITCH, s)
    beam(b, F, (0.0, y0r - 0.3, EAVE + (half + 0.6) * PITCH + 0.45), (0.0, y1r + 0.3, EAVE + (half + 0.6) * PITCH + 0.45),
         1.1, 0.8, "SN_RoofTileDark")
    # musgo e hera (o templo e antigo)
    moss_patch(b, F, -13.0, -11.6, FL + 0.02, 3.0, 2.0, seed="shm1")
    ivy(b, Fr(F.p(-CX - 0.05, -6.0, 0), (-F.t.x, -F.t.y)), 0.0, 0.0, TOP, 7.0, 3.0, seed="shiv1")
    ivy(b, Fr(F.p(0, YB - 0.05, 0), (-F.f.x, -F.f.y)), 6.0, 0.0, TOP, 9.0, 4.0, seed="shiv2")


def interior(b, F):
    # assoalho de tabuas (ao longo de y) + tapete redondo na entrada
    n = 16
    for k in range(n):
        x0 = -(CX - WALL_T) + k * (2 * (CX - WALL_T)) / n
        x1 = x0 + (2 * (CX - WALL_T)) / n - 0.06
        bb(b, F, x0, x1, YB + WALL_T, YF - WALL_T, FL, FL + 0.15, "SN_WoodAged", bevel=0.03)
    cyl(b, F, (0.0, 1.0, FL + 0.15), (0.0, 1.0, FL + 0.2), 2.9, "SN_CanvasRed", seg=24)
    cyl(b, F, (0.0, 1.0, FL + 0.15), (0.0, 1.0, FL + 0.24), 2.3, "SN_CanvasOchre", seg=24)
    cyl(b, F, (0.0, 1.0, FL + 0.15), (0.0, 1.0, FL + 0.27), 1.6, "SN_CanvasRed", seg=24)
    # balcao: base de pedra, frente de tabuas com friso dourado, tampo de madeira; passagem do vendedor em x 5..7
    yc0, yc1 = -3.5, -1.7
    bb(b, F, -7.0, 5.0, yc0, yc1, FL + 0.15, FL + 3.0, "SN_Ashlar", bevel=0.08)
    for k in range(8):
        xa = -7.0 + k * 1.5
        bb(b, F, xa + 0.04, xa + 1.46, yc1, yc1 + 0.2, FL + 0.5, FL + 2.9, "SN_WoodAged")
    beam(b, F, (-7.0, yc1 + 0.25, FL + 2.75), (5.0, yc1 + 0.25, FL + 2.75), 0.12, 0.18, "SN_Gold")
    bb(b, F, -7.3, 5.3, yc0 - 0.2, yc1 + 0.35, FL + 3.0, FL + 3.35, "SN_WoodAged", bevel=0.05)
    zt = FL + 3.35
    scale_(b, F, -5.0, -2.6, zt)
    coins(b, F, -2.4, -2.5, zt, 1)
    book(b, F, 0.6, -2.6, zt)
    lantern(b, F, 3.6, -2.9, zt + 1.6, "L_SN_ShopCounter", s=0.8)
    cyl(b, F, (3.6, -2.9, zt), (3.6, -2.9, zt + 0.2), 0.35, "SN_Bronze", seg=8)
    backpack(b, F, -6.2, -2.7, zt, 0.55, "SN_CanvasBlue", "cnt", turn=20.0)
    # portinhola da passagem
    bb(b, F, 5.15, 6.85, yc1 - 0.1, yc1 + 0.1, FL + 0.3, FL + 2.4, "SN_WoodAged")
    # estantes do fundo: 3 prateleiras com mochilas variadas
    yb_in = YB + WALL_T
    for k, zz in enumerate((FL + 3.2, FL + 6.4, FL + 9.6)):
        bb(b, F, -11.5, 11.5, yb_in, yb_in + 1.5, zz - 0.25, zz, "SN_WoodAged", bevel=0.04)
        for xx in (-11.2, -3.8, 3.8, 11.2):
            bb(b, F, xx - 0.15, xx + 0.15, yb_in, yb_in + 1.2, zz - 1.0, zz - 0.25, "SN_WoodAged")
        r = rng("shelf", k)
        x = -10.4
        j = 0
        while x < 10.0:
            s = r.uniform(0.6, 0.85)
            if x > -1.6 and x < 1.6 and k == 2:
                x += 1.0
                continue
            backpack(b, F, x, yb_in + 0.75, zz, s, CANVAS[(k + j) % 4], ("sh", k, j), turn=r.uniform(-12, 12),
                     roll=r.choice(("SN_CanvasCream", "SN_CanvasBlue", "SN_CanvasCream")))
            x += 1.9 * s + r.uniform(0.35, 0.8)
            j += 1
    # montante central das estantes
    for xx in (-11.5, 11.5):
        bb(b, F, xx - 0.3, xx + 0.3, yb_in, yb_in + 1.5, FL + 0.15, FL + 10.0, "SN_WoodAged")
    # relevo da bigorna do deus na parede do fundo, acima das prateleiras
    Fw = Fr(F.p(0, yb_in + 0.02, 0), (F.f.x, F.f.y))
    anv = [(-2.6, 0.6), (-1.3, 0.9), (2.0, 0.9), (2.3, 0.6), (1.8, 0.4), (0.9, 0.05), (0.8, -0.65), (1.5, -1.1),
           (-1.5, -1.1), (-0.8, -0.65), (-0.9, 0.05), (-1.4, 0.4)]
    bm = bmesh.new()
    a = [bm.verts.new(Fw.p(x, 0.0, FL + 12.2 + z)) for (x, z) in anv]
    c = [bm.verts.new(Fw.p(x, 0.25, FL + 12.2 + z)) for (x, z) in anv]
    bm.faces.new(list(reversed(a)))
    bm.faces.new(c)
    for i in range(len(anv)):
        bm.faces.new((a[i], a[(i + 1) % len(anv)], c[(i + 1) % len(anv)], c[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    b.mesh(bm, "SN_Gold")
    # lado oeste (x < 0): ganchos com bolsas penduradas + manequim
    xw = -(CX - WALL_T)
    bb(b, F, xw, xw + 0.25, -8.0, 1.5, FL + 6.5, FL + 6.8, "SN_WoodAged")
    for k in range(5):
        yy = -7.2 + k * 2.0
        bb(b, F, xw + 0.25, xw + 0.7, yy - 0.06, yy + 0.06, FL + 6.4, FL + 6.55, "SN_Bronze")
        backpack(b, F, xw + 0.85, yy, FL + 4.1, 0.6, CANVAS[(k + 1) % 4], ("hk", k), turn=-90.0)
    mannequin(b, F, -9.0, -6.5, FL + 0.15, "SN_CanvasGreen", "mq1", turn=35.0)
    bb(b, F, -11.6, -9.6, 0.2, 2.2, FL + 0.15, FL + 2.0, "SN_WoodAged", bevel=0.08)
    backpack(b, F, -10.6, 1.2, FL + 2.0, 0.6, "SN_CanvasOchre", "crt", turn=60.0)
    # lado leste (x > 0): vitrine da MOCHILA LENDARIA (pedestal de pedra, aro de bronze, cristal aceso)
    xe = CX - WALL_T - 3.2
    lathe(b, F, xe, -6.0, [(1.6, 0.0), (1.6, 0.4), (1.2, 0.6), (1.0, 2.6), (1.4, 2.9), (1.45, 3.2)], "SN_Carved", 16,
          z0=FL + 0.15)
    cyl(b, F, (xe, -6.0, FL + 3.35), (xe, -6.0, FL + 3.5), 1.5, "SN_Bronze", seg=16)
    backpack(b, F, xe, -6.0, FL + 3.5, 0.9, "SN_CanvasViolet", "leg", turn=-60.0, roll="SN_CanvasCream", trim="SN_Gold")
    crystal_cluster(b, F, xe + 0.9, -5.2, FL + 3.5, 0.6, "SN_CrystalBlue", seed="legc")
    fm_lib.light("L_SN_ShopLegend", "POINT", F.p(xe, -6.0, FL + 7.0), 90.0, (0.55, 0.75, 1.0), 0.5)
    # barris e sacos no canto leste da frente
    cyl(b, F, (CX - WALL_T - 1.4, 1.4, FL + 0.15), (CX - WALL_T - 1.4, 1.4, FL + 2.6), 0.95, "SN_WoodAged", seg=12)
    for zz in (FL + 0.6, FL + 2.1):
        cyl(b, F, (CX - WALL_T - 1.4, 1.4, zz), (CX - WALL_T - 1.4, 1.4, zz + 0.18), 1.0, "SN_Iron", seg=12)
    # vigas do teto + 2 lanternas penduradas
    for k in range(5):
        yy = YB + WALL_T + 1.0 + k * 3.0
        bb(b, F, -CX + WALL_T, CX - WALL_T, yy - 0.35, yy + 0.35, TOP - 0.8, TOP, "SN_WoodAged", bevel=0.04)
    for (lx, ly) in ((-5.0, -0.5), (5.0, -0.5)):
        beam(b, F, (lx, ly, TOP - 0.8), (lx, ly, FL + 11.2), 0.08, 0.08, "SN_Chain")
        lantern(b, F, lx, ly, FL + 11.2, "L_SN_ShopLamp_%d" % int(lx))
    # forro (tabuado) entre o topo das paredes e o telhado: fecha a vista de dentro
    bb(b, F, -CX + WALL_T, CX - WALL_T, YB + WALL_T, YF - WALL_T, TOP - 0.1, TOP + 0.15, "SN_WoodAged")


def exterior_dressing(b, F):
    # cavaletes com mochilas dos dois lados da porta, no portico
    for s in (-1, 1):
        x0 = s * 7.8
        for k in range(2):
            beam(b, F, (x0 - 1.6, 7.0 + k * 0.01, FL + 0.1), (x0, 7.0, FL + 4.2), 0.18, 0.18, "SN_WoodAged")
            beam(b, F, (x0 + 1.6, 7.0, FL + 0.1), (x0, 7.0, FL + 4.2), 0.18, 0.18, "SN_WoodAged")
        for k, zz in enumerate((FL + 0.9, FL + 2.6)):
            beam(b, F, (x0 - 1.4, 7.25, zz), (x0 + 1.4, 7.25, zz), 0.12, 0.2, "SN_WoodAged")
            backpack(b, F, x0 + (k - 0.5) * 0.9, 7.6, zz, 0.55, CANVAS[(k + (1 if s > 0 else 2)) % 4], ("cv", s, k))
    # caixas, barril e sacos nos cantos do portico
    for (xx, yy, sd) in ((-13.0, 6.2, 1), (12.6, 6.6, 2)):
        bb(b, F, xx - 1.0, xx + 1.0, yy - 1.0, yy + 1.0, FL + 0.02, FL + 2.0, "SN_WoodAged", bevel=0.08)
        bb(b, F, xx - 0.7 + 0.2, xx + 0.7 + 0.2, yy - 0.7, yy + 0.7, FL + 2.0, FL + 3.4, "SN_WoodAged", bevel=0.08)
        worn_block(b, F, xx + 1.6 * (1 if xx < 0 else -1), yy + 0.8, FL + 0.6, (1.3, 1.1, 1.2), "SN_CanvasCream",
                   seed=("sk", sd), chips=0, bevel=0.4)
    # placa pendurada "MOCHILAS" no canto do portico (le-se de lado, de quem chega pela praca)
    xs = -CX - 0.9
    beam(b, F, (xs, COL_Y + 1.4, FL + 10.5), (xs - 3.4, COL_Y + 1.4, FL + 10.5), 0.25, 0.25, "SN_Iron")
    for d in (-0.9, 0.9):
        beam(b, F, (xs - 1.7 + d, COL_Y + 1.4, FL + 10.4), (xs - 1.7 + d, COL_Y + 1.4, FL + 9.6), 0.06, 0.06, "SN_Chain")
    Fs = Fr(F.p(xs - 1.7, COL_Y + 1.4, 0), (F.t.x, F.t.y))
    bb(b, Fs, -1.9, 1.9, -0.15, 0.15, FL + 7.7, FL + 9.6, "SN_WoodAged", bevel=0.06)
    text(b, Fs, "MOCHILAS", 0.42, "SN_Gold", 0.0, 0.17, FL + 8.65, thick=0.08, bold=True)
    Fs2 = Fr(F.p(xs - 1.7, COL_Y + 1.4, 0), (-F.t.x, -F.t.y))
    text(b, Fs2, "MOCHILAS", 0.42, "SN_Gold", 0.0, 0.17, FL + 8.65, thick=0.08, bold=True)
    # estandartes nas colunas de fora
    for xx in (-11.6, 11.6):
        banner(b, Fr(F.p(xx, COL_Y + 1.25, 0), (F.f.x, F.f.y)), 0.0, 0.0, TOP - 0.4, "SN_CanvasRed", 2.0, 6.0, pole=False,
               emblem=False)
    # vasos com flores azuis e braseiros no pe da escada
    for s in (-1, 1):
        lathe(b, F, s * 13.6, 13.6, [(0.7, 0.0), (0.95, 0.3), (1.0, 1.0), (0.85, 1.4), (0.95, 1.55)], "SN_Terracotta", 12,
              z0=0.6)
        flower_bed(b, F, s * 13.6, 13.6, 2.15, 1.4, 1.4, 9, seed=("vf", s))
        brazier(b, F, s * 9.0, 15.4, 0.0, 3.6, "L_SN_Brazier_Shop_%d" % s)
    # mesa-banca de feira no lado sul externo do templo, com toldo listrado
    Fk = F.sub(CX + 5.5, 0.0, 0.0, 0.0)
    for (px, py) in ((-2.2, -3.0), (2.2, -3.0), (-2.2, 3.0), (2.2, 3.0)):
        cyl(b, Fk, (px, py, 0.0), (px, py, 7.4), 0.16, "SN_WoodAged", seg=6)
    bb(b, Fk, -2.5, 2.5, -3.3, 3.3, 2.6, 2.9, "SN_WoodAged", bevel=0.04)
    for k in range(6):
        y0 = -3.6 + k * 1.2
        bm = bmesh.new()
        q = [(-2.9, y0, 7.6), (2.9, y0, 6.4), (2.9, y0 + 1.2, 6.4), (-2.9, y0 + 1.2, 7.6)]
        vs = [bm.verts.new(Fk.p(*v)) for v in q]
        vs2 = [bm.verts.new(Fk.p(v[0], v[1], v[2] - 0.08)) for v in q]
        bm.faces.new(vs)
        bm.faces.new(list(reversed(vs2)))
        for i in range(4):
            bm.faces.new((vs[i], vs2[i], vs2[(i + 1) % 4], vs[(i + 1) % 4]))
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
        b.mesh(bm, "SN_CanvasRed" if k % 2 == 0 else "SN_CanvasCream")
    for k in range(3):
        backpack(b, Fk, 0.0, -2.2 + k * 2.2, 2.9, 0.62, CANVAS[k], ("st", k), turn=90.0)


def collisions(F):
    def box(dx, dy, dz, cx, cy, cz):
        fm_lib.col_box(AREA, (dx, dy, dz), F.p(cx, cy, cz), (0, 0, F.yaw()))
    box(32.0, 27.2, 1.4, 0.0, 0.6, -0.1)                         # estilobato (degrau baixo)
    box(30.0, 25.0, 0.6, 0.0, 0.3, 0.9)                          # degrau de cima
    box(2 * CX, WALL_T, TOP - FL, 0.0, YB + WALL_T / 2, (TOP + FL) / 2)
    for s in (-1, 1):
        box(WALL_T, YF - YB, TOP - FL, s * (CX - WALL_T / 2), (YB + YF) / 2, (TOP + FL) / 2)
        # frente: dois trechos ao lado da porta + verga acima
        box(CX - 3.5, WALL_T, TOP - FL, s * (3.5 + (CX - 3.5) / 2), YF - WALL_T / 2, (TOP + FL) / 2)
    box(7.0, WALL_T, TOP - FL - 9.0, 0.0, YF - WALL_T / 2, (TOP + FL + 9.0) / 2)
    box(12.6, 2.2, 3.4, -1.0, -2.6, FL + 1.7)                    # balcao
    box(23.0, 1.6, 10.0, 0.0, YB + WALL_T + 0.8, FL + 5.0)        # estantes
    for xx in (-11.6, -4.4, 4.4, 11.6):
        box(2.4, 2.4, TOP - FL, xx, COL_Y, (TOP + FL) / 2)
    box(3.4, 3.4, 3.6, CX - WALL_T - 3.2, -6.0, FL + 1.8)        # pedestal da vitrine
    box(31.0, 26.0, 2.0, 0.0, -0.5, EAVE + 2.0)                  # telhado (camera)


# ------------------------------------------------------------------ LOJA-MOCHILA (v2, feedback 09/10: o templo parecia
# um banco dos anos 70). O predio E uma mochila de aventureiro gigante: corpo de lona com cantos arredondados, aba de
# couro com fivelas de ouro descendo pela frente, o BOLSO DA FRENTE e a entrada, bolsos laterais, saco de dormir enrolado
# no topo, alcas nas costas, uma picareta gigante amarrada na lateral, lampiao e corda. O interior (balcao, prateleiras,
# vitrine) e o mesmo de antes, dentro do corpo (x +-14, y -11.2..4.6).
R_ = 1.8                                       # raio dos cantos/bordas arredondados do corpo
POCKET = (9.0, 6.0, 10.3)                      # meia largura, profundidade, altura do bolso da frente (entrada)


def _round_box(b, F, x0, x1, y0, y1, z0, z1, r, mat, seg=16):
    """caixa com cantos verticais e bordas de cima arredondadas (lona estufada)"""
    bb(b, F, x0 + r, x1 - r, y0, y1, z0, z1 - r, mat)
    bb(b, F, x0, x1, y0 + r, y1 - r, z0, z1 - r, mat)
    bb(b, F, x0 + r, x1 - r, y0 + r, y1 - r, z1 - r, z1, mat)
    for (cx, cy) in ((x0 + r, y0 + r), (x1 - r, y0 + r), (x0 + r, y1 - r), (x1 - r, y1 - r)):
        cyl(b, F, (cx, cy, z0), (cx, cy, z1 - r), r, mat, seg=seg)
        b.sphere(F.p(cx, cy, z1 - r), r, mat, seg=seg)
    for (ya, yb_, xx) in ((y0 + r, y1 - r, x0 + r), (y0 + r, y1 - r, x1 - r)):
        cyl(b, F, (xx, ya, z1 - r), (xx, yb_, z1 - r), r, mat, seg=seg)
    for (xa, xb_, yy) in ((x0 + r, x1 - r, y0 + r), (x0 + r, x1 - r, y1 - r)):
        cyl(b, F, (xa, yy, z1 - r), (xb_, yy, z1 - r), r, mat, seg=seg)


def half_dome(b, F, cx, cy, z0, rx, ry, rz, mat, seg=28, rings=8):
    """meia elipsoide (so a metade de cima, base plana em z0) - a de baixo furaria o forro do interior"""
    bm = bmesh.new()
    rows = []
    for i in range(rings):
        ph = (math.pi / 2) * i / rings
        rows.append([bm.verts.new(F.p(cx + rx * math.cos(ph) * math.cos(2 * math.pi * j / seg),
                                      cy + ry * math.cos(ph) * math.sin(2 * math.pi * j / seg), z0 + rz * math.sin(ph)))
                     for j in range(seg)])
    top = bm.verts.new(F.p(cx, cy, z0 + rz))
    for i in range(rings - 1):
        a_, c_ = rows[i], rows[i + 1]
        for j in range(seg):
            bm.faces.new((a_[j], a_[(j + 1) % seg], c_[(j + 1) % seg], c_[j]))
    for j in range(seg):
        bm.faces.new((rows[-1][j], rows[-1][(j + 1) % seg], top))
    bm.faces.new(list(reversed(rows[0])))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    b.mesh(bm, mat)


def backpack_house(b, F):
    from wb_house import arch_holes, wall_holes
    from sn_kit import pickaxe
    # base de pedra em 2 degraus
    bb(b, F, -17.0, 17.0, -14.0, 13.6, -0.8, 0.6, "SN_Ashlar_Dark", bevel=0.12)
    bb(b, F, -16.0, 16.0, -13.0, 11.8, 0.6, FL, "SN_Ashlar", bevel=0.12)
    TOPB = TOP + R_                            # topo do corpo (o forro interno fica em TOP)
    # CORPO: paredes de lona (miolo oco para o interior) + casca arredondada por fora
    door = arch_holes(0.0, 7.0, FL, 9.0)
    Ff = F.sub(0, YF - WALL_T / 2, 0, 0)
    wall_holes(b, Ff, -CX + R_, CX - R_, FL, TOP, -WALL_T / 2, WALL_T / 2, door, "SN_CanvasTan")
    bb(b, F, -CX + R_, CX - R_, YB, YB + WALL_T, FL, TOP, "SN_CanvasTan")
    for sx in (-1, 1):
        bb(b, F, sx * (CX - WALL_T), sx * CX, YB + R_, YF - R_, FL, TOP, "SN_CanvasTan")
    for (cx, cy) in ((-CX + R_, YB + R_), (CX - R_, YB + R_), (-CX + R_, YF - R_), (CX - R_, YF - R_)):
        cyl(b, F, (cx, cy, FL), (cx, cy, TOP), R_, "SN_CanvasTan", seg=16)
    bb(b, F, -CX + R_, CX - R_, YB + R_, YF - R_, TOP, TOPB, "SN_CanvasTan")
    for (ya, yb_, xx) in ((YB + R_, YF - R_, -CX + R_), (YB + R_, YF - R_, CX - R_)):
        cyl(b, F, (xx, ya, TOP), (xx, yb_, TOP), R_, "SN_CanvasTan", seg=16)
    for (xa, xb_, yy) in ((-CX + R_, CX - R_, YB + R_), (-CX + R_, CX - R_, YF - R_)):
        cyl(b, F, (xa, yy, TOP), (xb_, yy, TOP), R_, "SN_CanvasTan", seg=16)
    for (cx, cy) in ((-CX + R_, YB + R_), (CX - R_, YB + R_), (-CX + R_, YF - R_), (CX - R_, YF - R_)):
        b.sphere(F.p(cx, cy, TOP), R_, "SN_CanvasTan", seg=16)
    # costuras (pespontos claros) nas quinas verticais da frente
    for sx in (-1, 1):
        for k in range(9):
            zz = FL + 0.8 + k * 1.5
            beam(b, F, (sx * (CX - 0.25), YF - 0.3, zz), (sx * (CX - 0.25), YF - 0.3, zz + 0.8), 0.14, 0.14, "SN_CanvasCream")
    # ABA de couro: tampa por cima + caimento na frente ate acima do bolso, borda arredondada, fivelas
    # tampa ABAULADA (meia elipsoide de couro): da a silhueta redonda de mochila vista da praca
    half_dome(b, F, 0.0, (YB + YF) / 2 + 0.25, TOPB - 0.25, CX + 0.6, (YF - YB) / 2 + 0.55, 4.6, "SN_Leather")
    bb(b, F, -CX - 0.3, CX + 0.3, YB + 0.3, YF + 0.5, TOPB - 0.45, TOPB - 0.05, "SN_LeatherDark", bevel=0.1)
    fz0 = FL + POCKET[2] + 0.6
    bb(b, F, -CX + 1.0, CX - 1.0, YF + 0.05, YF + 0.75, fz0, TOPB + 0.6, "SN_Leather", bevel=0.25)
    cyl(b, F, (-CX + 1.0, YF + 0.4, fz0), (CX - 1.0, YF + 0.4, fz0), 0.45, "SN_Leather", seg=10)
    for sx in (-1, 1):
        x = sx * 6.0
        # tira da aba descendo pela frente do bolso ate a base, fivela de ouro
        beam(b, F, (x, YF + 0.85, TOPB - 0.5), (x, YF + 0.85, fz0 - 0.1), 1.3, 0.25, "SN_Leather")
        beam(b, F, (x, YF + POCKET[1] + 0.15, FL + POCKET[2] - 0.2), (x, YF + POCKET[1] + 0.15, FL + 0.6), 1.3, 0.25,
             "SN_Leather")
        bb(b, F, x - 1.0, x + 1.0, YF + POCKET[1] + 0.2, YF + POCKET[1] + 0.55, FL + 4.6, FL + 6.0, "SN_Gold", bevel=0.08)
        bb(b, F, x - 0.55, x + 0.55, YF + POCKET[1] + 0.5, YF + POCKET[1] + 0.65, FL + 4.95, FL + 5.65, "SN_Leather")
    # BOLSO DA FRENTE (entrada): paredes de lona vermelha com porta em arco, tampa arredondada e aba
    px, pd, ph = POCKET
    pdoor = arch_holes(0.0, 7.2, FL, 8.4)
    Fp = F.sub(0, YF + pd - 0.5, 0, 0)
    wall_holes(b, Fp, -px + 1.0, px - 1.0, FL, FL + ph - 1.0, -0.5, 0.5, pdoor, "SN_CanvasRed")
    for sx in (-1, 1):
        bb(b, F, sx * (px - 1.0), sx * px, YF, YF + pd - 1.0, FL, FL + ph - 1.0, "SN_CanvasRed")
        cyl(b, F, (sx * (px - 1.0), YF + pd - 1.0, FL), (sx * (px - 1.0), YF + pd - 1.0, FL + ph - 1.0), 1.0, "SN_CanvasRed",
            seg=12)
    bb(b, F, -px + 1.0, px - 1.0, YF, YF + pd - 1.0, FL + ph - 1.0, FL + ph, "SN_CanvasRed")
    cyl(b, F, (-px + 1.0, YF + pd - 1.0, FL + ph - 1.0), (px - 1.0, YF + pd - 1.0, FL + ph - 1.0), 1.0, "SN_CanvasRed", seg=12)
    for sx in (-1, 1):
        b.sphere(F.p(sx * (px - 1.0), YF + pd - 1.0, FL + ph - 1.0), 1.0, "SN_CanvasRed", seg=12)
        cyl(b, F, (sx * (px - 1.0), YF, FL + ph - 1.0), (sx * (px - 1.0), YF + pd - 1.0, FL + ph - 1.0), 1.0, "SN_CanvasRed",
            seg=12)
    bb(b, F, -px + 0.8, px - 0.8, YF + pd - 0.3, YF + pd + 0.35, FL + ph - 2.0, FL + ph + 0.3, "SN_Leather", bevel=0.2)
    b.sphere(F.p(0.0, YF + pd + 0.45, FL + ph - 1.6), 0.45, "SN_Gold", seg=10)
    # moldura do vao da porta do bolso (couro) e capacho
    for sx in (-1, 1):
        beam(b, F, (sx * 3.85, YF + pd + 0.05, FL), (sx * 3.85, YF + pd + 0.05, FL + 4.8), 0.5, 0.35, "SN_Leather")
    cyl(b, F, (0.0, YF + pd + 1.6, FL - 0.02), (0.0, YF + pd + 1.6, FL + 0.08), 2.2, "SN_CanvasOchre", seg=20)
    # BOLSOS LATERAIS (cilindros de lona com tampa de couro e botao)
    for sx in (-1, 1):
        xx = sx * (CX + 1.9)
        cyl(b, F, (xx, -3.0, FL + 0.6), (xx, -3.0, FL + 9.0), 2.6, "SN_CanvasRed", seg=16)
        b.sphere(F.p(xx, -3.0, FL + 0.6), 2.6, "SN_CanvasRed", seg=16, scale=(1, 1, 0.35))
        cyl(b, F, (xx, -3.0, FL + 8.6), (xx, -3.0, FL + 9.6), 2.75, "SN_Leather", seg=16)
        b.sphere(F.p(xx + sx * 2.7, -3.0, FL + 8.9), 0.35, "SN_Gold", seg=8)
        for zz in (FL + 3.0, FL + 6.4):
            cyl(b, F, (xx, -3.0, zz), (xx, -3.0, zz + 0.5), 2.68, "SN_Leather", seg=16)
    # SACO DE DORMIR enrolado no topo, com tiras e listras
    RR, XR = 2.7, 9.6                               # raio e meia largura do saco (cabe no alto da tampa)
    yr = (YB + YF) / 2 + 0.25
    zr = TOPB - 0.25 + 4.6 + RR - 0.75
    cyl(b, F, (-XR, yr, zr), (XR, yr, zr), RR, "SN_CanvasCream", seg=20)
    for xx in (-XR, XR):
        sg = 1 if xx > 0 else -1
        cyl(b, F, (xx, yr, zr), (xx + 0.3 * sg, yr, zr), RR - 0.6, "SN_CanvasBlue", seg=20)
    for xx in (-7.2, 7.2):
        cyl(b, F, (xx - 0.35, yr, zr), (xx + 0.35, yr, zr), RR + 0.08, "SN_CanvasRed", seg=20)
    for xx in (-4.2, 4.2):
        cyl(b, F, (xx - 0.45, yr, zr), (xx + 0.45, yr, zr), RR + 0.2, "SN_Leather", seg=20)
        bb(b, F, xx - 0.6, xx + 0.6, yr + RR, yr + RR + 0.5, zr - 0.6, zr + 0.6, "SN_Gold")
        # tiras descendo pela tampa ate a borda da frente
        beam(b, F, (xx, yr + RR * 0.7, zr - RR * 0.7), (xx, YF + 0.55, TOPB + 0.2), 0.9, 0.2, "SN_Leather")
    # ALCAS nas costas (curvas acolchoadas) e argolas de bronze
    for sx in (-1, 1):
        x = sx * 6.5
        pts = [(x, YB - 0.3, TOPB - 1.0), (x, YB - 2.2, TOP - 4.0), (x, YB - 2.6, FL + 6.0), (x, YB - 1.6, FL + 2.6),
               (x, YB - 0.3, FL + 1.4)]
        for p0, p1 in zip(pts, pts[1:]):
            beam(b, F, p0, p1, 2.2, 0.9, "SN_Leather")
        cyl(b, F, (x, YB - 0.4, FL + 1.4), (x, YB - 1.2, FL + 1.4), 0.9, "SN_Bronze", seg=10)
    # PICARETA gigante amarrada na lateral oeste (tema do jogo) e corda enrolada na leste
    pickaxe(b, F, -CX - 0.9, 3.0, FL + 2.0, turn=90.0, lean=-20.0, s=2.4, head="WB_Steel", handle="SN_WoodAged",
            gem="SN_CrystalAmber")
    for zz in (FL + 4.0, FL + 8.0):
        cyl(b, F, (-CX - 0.2, 1.2, zz), (-CX - 0.2, 5.0, zz), 0.25, "SN_Leather", seg=8)
    n = 14
    for ring_ in range(3):
        rr_ = 1.5 - ring_ * 0.25
        for k in range(n):
            a0, a1 = 2 * math.pi * k / n, 2 * math.pi * (k + 1) / n
            beam(b, F, (CX + 0.35 + ring_ * 0.22, -7.5 + rr_ * math.cos(a0), FL + 8.0 + rr_ * math.sin(a0)),
                 (CX + 0.35 + ring_ * 0.22, -7.5 + rr_ * math.cos(a1), FL + 8.0 + rr_ * math.sin(a1)), 0.3, 0.3, "SN_Rope")
    # lampiao pendurado no canto da frente (leste) e janelinhas redondas nas laterais
    beam(b, F, (CX - 0.5, YF + 0.5, TOP - 1.0), (CX + 2.0, YF + 0.5, TOP - 1.0), 0.25, 0.25, "SN_Iron")
    lantern(b, F, CX + 2.0, YF + 0.5, TOP - 1.2, "L_SN_ShopLantern", s=1.1)
    for sx in (-1, 1):
        Fw = Fr(F.p(sx * (CX + 0.02), 0, 0), (sx * F.t.x, sx * F.t.y))
        for yy in (-8.0, 1.0):
            cyl(b, Fw, (yy * -sx, -0.05, FL + 7.5), (yy * -sx, 0.3, FL + 7.5), 1.3, "SN_Bronze", seg=16)
            cyl(b, Fw, (yy * -sx, 0.0, FL + 7.5), (yy * -sx, 0.36, FL + 7.5), 0.95, "WB_Window", seg=16)


def backpack_dressing(b, F):
    """frente da loja: cavaletes com mochilas, caixas, barris, sacos, vasos com flores e a banca de feira com toldo"""
    for s in (-1, 1):
        x0 = s * 12.4
        y0 = 9.0
        for k in range(2):
            beam(b, F, (x0 - 1.6, y0, FL + 0.1), (x0, y0, FL + 4.2), 0.18, 0.18, "SN_WoodAged")
            beam(b, F, (x0 + 1.6, y0, FL + 0.1), (x0, y0, FL + 4.2), 0.18, 0.18, "SN_WoodAged")
        for k, zz in enumerate((FL + 0.9, FL + 2.6)):
            beam(b, F, (x0 - 1.4, y0 + 0.25, zz), (x0 + 1.4, y0 + 0.25, zz), 0.12, 0.2, "SN_WoodAged")
            backpack(b, F, x0 + (k - 0.5) * 0.9, y0 + 0.6, zz, 0.55, CANVAS[(k + (1 if s > 0 else 2)) % 4], ("cv", s, k))
    for (xx, yy, sd) in ((-15.0, 3.0, 1), (15.0, 6.0, 2)):
        bb(b, F, xx - 1.0, xx + 1.0, yy - 1.0, yy + 1.0, FL + 0.02, FL + 2.0, "SN_WoodAged", bevel=0.08)
        bb(b, F, xx - 0.5, xx + 0.9, yy - 0.7, yy + 0.7, FL + 2.0, FL + 3.4, "SN_WoodAged", bevel=0.08)
        worn_block(b, F, xx, yy + 2.0, FL + 0.6, (1.3, 1.1, 1.2), "SN_CanvasCream", seed=("sk", sd), chips=0, bevel=0.4)
    for s in (-1, 1):
        lathe(b, F, s * 15.4, 12.6, [(0.7, 0.0), (0.95, 0.3), (1.0, 1.0), (0.85, 1.4), (0.95, 1.55)], "SN_Terracotta", 12,
              z0=0.6)
        flower_bed(b, F, s * 15.4, 12.6, 2.15, 1.4, 1.4, 9, seed=("vf", s))
    # banca de feira com toldo listrado no lado sul externo
    Fk = F.sub(CX + 8.0, -1.0, 0.0, 0.0)
    for (px_, py_) in ((-2.2, -3.0), (2.2, -3.0), (-2.2, 3.0), (2.2, 3.0)):
        cyl(b, Fk, (px_, py_, 0.0), (px_, py_, 7.4), 0.16, "SN_WoodAged", seg=6)
    bb(b, Fk, -2.5, 2.5, -3.3, 3.3, 2.6, 2.9, "SN_WoodAged", bevel=0.04)
    for k in range(6):
        y0 = -3.6 + k * 1.2
        bm = bmesh.new()
        q = [(-2.9, y0, 7.6), (2.9, y0, 6.4), (2.9, y0 + 1.2, 6.4), (-2.9, y0 + 1.2, 7.6)]
        vs = [bm.verts.new(Fk.p(*v)) for v in q]
        vs2 = [bm.verts.new(Fk.p(v[0], v[1], v[2] - 0.08)) for v in q]
        bm.faces.new(vs)
        bm.faces.new(list(reversed(vs2)))
        for i in range(4):
            bm.faces.new((vs[i], vs2[i], vs2[(i + 1) % 4], vs[(i + 1) % 4]))
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
        b.mesh(bm, "SN_CanvasRed" if k % 2 == 0 else "SN_CanvasCream")
    for k in range(3):
        backpack(b, Fk, 0.0, -2.2 + k * 2.2, 2.9, 0.62, CANVAS[k], ("st", k), turn=90.0)


def collisions2(F):
    def box(dx, dy, dz, cx, cy, cz):
        fm_lib.col_box(AREA, (dx, dy, dz), F.p(cx, cy, cz), (0, 0, F.yaw()))
    box(34.0, 27.6, 1.4, 0.0, -0.2, -0.1)
    box(32.0, 24.8, 0.6, 0.0, -0.6, 0.9)
    box(2 * CX, WALL_T, TOP - FL, 0.0, YB + WALL_T / 2, (TOP + FL) / 2)
    for s_ in (-1, 1):
        box(WALL_T, YF - YB, TOP - FL, s_ * (CX - WALL_T / 2), (YB + YF) / 2, (TOP + FL) / 2)
        box(CX - 3.5, WALL_T, TOP - FL, s_ * (3.5 + (CX - 3.5) / 2), YF - WALL_T / 2, (TOP + FL) / 2)
        # bolso: laterais e frente (ao lado da porta)
        box(1.0, POCKET[1], POCKET[2], s_ * (POCKET[0] - 0.5), YF + POCKET[1] / 2, FL + POCKET[2] / 2)
        box(POCKET[0] - 3.6, 1.0, POCKET[2], s_ * (3.6 + (POCKET[0] - 3.6) / 2), YF + POCKET[1] - 0.5, FL + POCKET[2] / 2)
        box(5.4, 5.4, 9.0, s_ * (CX + 1.9), -3.0, FL + 4.6)
    box(7.0, WALL_T, TOP - FL - 9.0, 0.0, YF - WALL_T / 2, (TOP + FL + 9.0) / 2)
    box(2 * POCKET[0], POCKET[1], 1.2, 0.0, YF + POCKET[1] / 2, FL + POCKET[2] - 0.4)
    box(7.2, 1.0, POCKET[2] - 8.4, 0.0, YF + POCKET[1] - 0.5, FL + 8.4 + (POCKET[2] - 8.4) / 2)
    box(12.6, 2.2, 3.4, -1.0, -2.6, FL + 1.7)
    box(23.0, 1.6, 10.0, 0.0, YB + WALL_T + 0.8, FL + 5.0)
    box(3.4, 3.4, 3.6, CX - WALL_T - 3.2, -6.0, FL + 1.8)
    box(2 * CX + 1.0, YF - YB + 1.0, 8.0, 0.0, (YB + YF) / 2, TOP + 4.0)


def build():
    SL.register()
    extra = {"SN_CanvasRed": (178, 52, 40), "SN_CanvasBlue": (58, 92, 160), "SN_CanvasGreen": (70, 120, 70),
             "SN_CanvasOchre": (204, 150, 60), "SN_CanvasCream": (226, 212, 180), "SN_CanvasViolet": (120, 70, 170),
             "SN_Leather": (120, 76, 46), "SN_Paper": (238, 228, 200), "SN_RoofTile": (196, 98, 60),
             "SN_RoofTileDark": (150, 70, 46), "SN_Terracotta": (186, 100, 64)}
    for k, c in extra.items():
        fm_lib.MATS.setdefault(k, (fm_lib.S(*c), 0.85, 0.0, 0, None, 0.0))
    fm_lib.make_materials()
    sx, sz = L.SHOP_C
    fx, fz = L.SHOP_FACE
    F = Fr.rbx(sx, sz, L.Y_PLAZA, fx, fz)
    b = SL.Build("WB_Shop_Temple", COLL)
    backpack_house(b, F)
    backpack_dressing(b, F)
    objs = b.finish()
    bi = SL.Build("WB_Shop_Inside", COLL)
    interior(bi, F)
    objs += bi.finish()
    collisions2(F)
    fm_lib.marker("LETREIRO_Loja", F.p(0, 12.0, EAVE + 9.0), (0, 0, 0), 1.0, "PLAIN_AXES", "15_GAMEPLAY_MARKERS",
                  {"texto": "LOJA DE MOCHILAS", "alcance": 170})
    fm_lib.marker("NPC_Vendedor", F.p(0, -4.5, FL), (0, 0, F.yaw()), 1.0, "PLAIN_AXES", "15_GAMEPLAY_MARKERS",
                  {"kind": "npc", "olha": "porta"})
    fm_lib.marker("PLAYER_Loja", F.p(0, 1.5, FL), (0, 0, F.yaw()), 1.0, "PLAIN_AXES", "15_GAMEPLAY_MARKERS",
                  {"kind": "padloja"})
    return objs
