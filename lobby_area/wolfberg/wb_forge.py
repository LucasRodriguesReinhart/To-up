# wb_forge.py - FORJA DO IGNIS (marco do lobby Wolfberg). Bloco central alto com o oitao para a praca e o vao do
# Ignis ABERTO (sem parede ate os tirantes em Y 33, acima da envoltoria 31 do golem), duas alas de pedra com
# FORNALHAS EM ARCO abertas para a praca (fogo, brasa, luz), meia-agua sobre as alas, 2 chamines de pedra, letreiro
# "FORJA DE WOLFBERG" na viga alta. Contrato: Root do Ignis (-0.9, 7, -60.7) olhando +Z; envoltoria livre
# X -9,9..6,1 / Y 7..31 / Z -64,7..-52,7; chao plano na cota 7 ate z -40. A bigorna/estacao e do golem (nao se repete).
import math

import fm_lib
import wb_lib as W
import wb_layout as L
from wb_kit import (Fr, bx, bb, beam, cyl, poly_wall, lathe, text, window, timber_face, roof, chimney, lantern,
                    barrel, crate, sack, ST, STD, TB, PK, PKL, RF, RFD, PL, PLO, IR, TXT, RAD)
from mathutils import Matrix, Vector

HB = L.FORGE_BAY_HALF          # 13: meia largura do bloco central
XW = 27.0                      # borda externa das alas
ZF, ZB = -46.0, -86.0          # frente / fundo (Roblox)
EAVE, RIDGE = L.FORGE_EAVE_Y - L.Y_PAVE, L.FORGE_RIDGE_Y - L.Y_PAVE      # 29 / 47,6 (locais, piso = 0)
WEAVE = L.FORGE_WING_EAVE_Y - L.Y_PAVE                                 # 17,5
TIE = L.FORGE_TIE_Y - L.Y_PAVE                                         # 26
GH = 10.0                      # terreo de pedra das alas
DEPTH = ZF - ZB                # 40


def poly_wall_xz(b, F, pts, y0, y1, m):
    """poligono no plano (x, z) local extrudado de y0 a y1 (paredes de frente com topo inclinado)"""
    import bmesh
    bm = bmesh.new()
    a = [bm.verts.new(F.p(x, y0, z)) for (x, z) in pts]
    c = [bm.verts.new(F.p(x, y1, z)) for (x, z) in pts]
    n = len(pts)
    bm.faces.new(a)
    bm.faces.new(list(reversed(c)))
    for i in range(n):
        bm.faces.new((a[i], c[i], c[(i + 1) % n], a[(i + 1) % n]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    b.mesh(bm, m)


def wing_slope(x):
    """altura (local) da meia-agua da ala em |x| (de EAVE em HB a WEAVE em XW+1,5)"""
    t = (abs(x) - HB) / (XW + 1.5 - HB)
    return EAVE - (EAVE - WEAVE) * max(0.0, min(1.0, t))


def hearth(b, F, x, zf):
    """fornalha de pedra em arco na parede da frente da ala (centro x, face em y = zf local): vao 8 x 9, recuo 4,
    fogo, brasa, lenha, fundo escuro, capa interna; luz e marcador de VFX"""
    w, h, d = L.HEARTH_W, L.HEARTH_H, 4.5
    Ff = Fr(F.p(x, zf, 0), (F.f.x, F.f.y))
    # aduelas do arco (pedra escura) + ombreiras
    import bmesh
    bm = bmesh.new()
    n = 10
    ro, ri = w / 2 + 1.3, w / 2
    zc = h - w / 2
    for k in range(n):
        a0, a1 = math.pi * k / n, math.pi * (k + 1) / n
        quad = [(ro * math.cos(a0), zc + ro * math.sin(a0)), (ro * math.cos(a1), zc + ro * math.sin(a1)),
                (ri * math.cos(a1), zc + ri * math.sin(a1)), (ri * math.cos(a0), zc + ri * math.sin(a0))]
        v0 = [bm.verts.new(Ff.p(px, 0.5, pz)) for (px, pz) in quad]
        v1 = [bm.verts.new(Ff.p(px, -0.6, pz)) for (px, pz) in quad]
        bm.faces.new(v0)
        bm.faces.new(list(reversed(v1)))
        for i in range(4):
            bm.faces.new((v0[i], v1[i], v1[(i + 1) % 4], v0[(i + 1) % 4]))
    bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=0.001)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    b.mesh(bm, STD)
    for s in (-1, 1):
        bb(b, Ff, s * (w / 2 + 0.65) - 0.65, s * (w / 2 + 0.65) + 0.65, -0.6, 0.5, 0.0, zc, STD)
    # camara: paredes laterais, fundo e teto (vista pelo arco), chao de pedra escura
    bb(b, Ff, -w / 2 - 1.0, w / 2 + 1.0, -d - 1.0, -d, 0.0, h + 2.0, STD)
    for s in (-1, 1):
        bb(b, Ff, s * (w / 2 + 0.5) - 0.5, s * (w / 2 + 0.5) + 0.5, -d - 1.0, -0.3, 0.0, h + 2.0, STD)
    bb(b, Ff, -w / 2 - 1.0, w / 2 + 1.0, -d - 1.0, -0.3, h + 1.0, h + 2.0, STD)
    bb(b, Ff, -w / 2, w / 2, -d, -0.2, -0.3, 0.3, "WB_Dark")
    bb(b, Ff, -w / 2 + 0.3, w / 2 - 0.3, -d + 0.1, -0.5, h - 0.4, h + 1.0, "WB_Dark")      # fundo da garganta
    # grelha de ferro, lenha, brasa e chamas
    bb(b, Ff, -w / 2 + 1.0, w / 2 - 1.0, -d + 0.8, -1.0, 0.9, 1.2, IR)
    for k, (lx, ly, ang) in enumerate(((-1.4, -2.4, 20), (1.2, -2.0, -15), (0.0, -3.0, 5), (-0.4, -1.6, 40))):
        b.cyl(Ff.p(lx - 1.6 * math.cos(RAD(ang)), ly - 1.6 * math.sin(RAD(ang)), 1.5 + k * 0.35),
              Ff.p(lx + 1.6 * math.cos(RAD(ang)), ly + 1.6 * math.sin(RAD(ang)), 1.5 + k * 0.35), 0.42, "WB_Bark", seg=7)
    bb(b, Ff, -w / 2 + 1.2, w / 2 - 1.2, -d + 1.0, -1.2, 1.2, 1.9, "WB_Ember")
    for (fx, fy, fh, fr) in ((0.0, -2.4, 3.4, 1.5), (-1.3, -2.0, 2.4, 1.0), (1.4, -2.6, 2.6, 1.0), (0.4, -1.5, 1.8, 0.8)):
        lathe(b, Ff, fx, fy, [(fr, 0.0), (fr * 0.8, fh * 0.45), (fr * 0.3, fh * 0.8), (0.0, fh)], "WB_Fire", 8, z0=1.8)
    # ferramentas encostadas na ombreira: tenaz e atiçador
    for s, tool in ((-1, "tenaz"), (1, "atic")):
        b.cyl(Ff.p(s * (w / 2 + 1.0), 0.9, 0.0), Ff.p(s * (w / 2 + 1.3), 0.3, 4.6), 0.1, IR, seg=6)
    fm_lib.light("L_WB_Hearth_%s" % ("L" if x < 0 else "R"), "POINT", Ff.p(0, -2.0, 3.8), 2200.0, (1.0, 0.5, 0.18), 1.0)
    fm_lib.marker("VFX_Hearth_Fire_%s" % ("L" if x < 0 else "R"), Ff.p(0, -2.2, 2.4), (0, 0, 0), 1.0, "PLAIN_AXES",
                  "15_GAMEPLAY_MARKERS", {"particle": "fire", "rate": 14, "size": 3.0})
    fm_lib.marker("VFX_Hearth_Ember_%s" % ("L" if x < 0 else "R"), Ff.p(0, -2.2, 2.8), (0, 0, 0), 1.0, "PLAIN_AXES",
                  "15_GAMEPLAY_MARKERS", {"particle": "ember", "rate": 6})


def build(coll="04_FORGE"):
    b = W.Build("WB_Frg_Hall", coll)
    F = Fr.rbx(0.0, (ZF + ZB) / 2, L.Y_PAVE, 0.0, 1.0)        # origem no centro do salao, +y local = frente (praca)
    hd = DEPTH / 2                                             # 20: frente em y = +20, fundo em y = -20
    # ---------------------------------------------------------------- piso de lajes (salao + soleira ate z -40)
    bb(b, F, -XW, XW, -hd, hd + 6.0, -1.0, 0.0, ST)
    # ---------------------------------------------------------------- alas de pedra (terreo) com fornalhas na frente
    for s in (-1, 1):
        x0, x1 = s * HB, s * XW
        lo, hi = min(x0, x1), max(x0, x1)
        bb(b, F, lo, hi, -hd, -hd + 2.0, 0.0, GH, ST)                      # fundo
        bb(b, F, min(x1, x1 + s * 0.0) - (2.0 if s > 0 else 0.0), max(x1, x1) + (0.0 if s > 0 else 2.0), -hd, hd, 0.0, GH, ST) if False else None
        bb(b, F, s * XW - 1.0, s * XW + 1.0, -hd, hd, 0.0, GH, ST)         # parede externa
        # parede da frente: pedra ate GH com o vao da fornalha (em 3 pecas: 2 lados + verga acima do arco)
        hx = s * 19.0
        wv = L.HEARTH_W / 2 + 1.3
        bb(b, F, min(lo, hx - wv), max(lo, hx - wv) if s > 0 else hx - wv, hd - 2.0, hd, 0.0, GH, ST) if False else None
        a0, a1 = sorted((lo, hx - wv))
        bb(b, F, a0, a1, hd - 2.0, hd, 0.0, GH, ST)
        a0, a1 = sorted((hx + wv, hi))
        bb(b, F, a0, a1, hd - 2.0, hd, 0.0, GH, ST)
        bb(b, F, hx - wv - 0.2, hx + wv + 0.2, hd - 2.0, hd, L.HEARTH_H + 1.2, GH, ST)
        hearth(b, F, hx, hd)
        # parede interna da ala (divide do vao central) em pedra ate GH
        bb(b, F, s * HB - 1.0, s * HB + 1.0, -hd, hd, 0.0, GH, ST)
        # andar enxaimel da ala (ocre) ate a meia-agua, nas 3 faces visiveis (frente, lado, fundo)
        pts_front = [(lo, GH), (hi + 1.5 * s if s > 0 else hi, GH)]
        # topo inclinado: segue wing_slope
        xs = [lo, hi] if s > 0 else [hi, lo]
        poly = [(lo, GH), (hi, GH), (hi, wing_slope(hi) - 0.4), (lo, wing_slope(lo) - 0.4)]
        poly_wall_xz(b, F, poly, hd - 1.6, hd - 0.2, PLO)                     # frente (reboco)
        poly_wall_xz(b, F, poly, -hd + 0.2, -hd + 1.6, PLO)                   # fundo
        # lateral externa (reboco + vigas)
        Fs = F.face("R" if s > 0 else "L", 2 * XW, DEPTH)
        bb(b, Fs, -hd, hd, -1.6, -0.2, GH, WEAVE - 0.4, PLO)
        timber_face(b, Fs, -hd + 0.3, hd - 0.3, GH, WEAVE - 0.4, bays=[-hd + 0.3 + (2 * hd - 0.6) * k / 5 for k in range(6)],
                    skip={1, 3})
        for k in (1, 3):
            cx = -hd + 0.3 + (2 * hd - 0.6) * (k + 0.5) / 5
            window(b, Fs, cx, GH + 3.6, 2.4, 2.8, shutters=True, flowers="WB_FlowerRed", seed=k)
        # vigas da frente da ala (enxaimel na faixa de reboco) + janela alta sobre a fornalha
        Ff = F.face("F", 2 * XW, DEPTH)
        xa, xb = sorted((s * (HB + 0.3), s * (XW - 0.3)))
        # no Ff, +x local = -x de F (olha para fora): converte
        xa, xb = -xb, -xa
        timber_face(b, Ff, xa, xb, GH, min(wing_slope(xa), wing_slope(xb)) - 0.4,
                    bays=[xa + (xb - xa) * k / 4 for k in range(5)], skip={1, 2})
        window(b, Ff, (xa + xb) / 2, GH + 3.4, 3.0, 2.8, shutters=True, flowers="WB_FlowerRed", seed=s + 7)
        # meia-agua da ala: laje inclinada de (HB, EAVE) a (XW+1.5, WEAVE)
        x_in, x_out = s * HB, s * (XW + 1.8)
        run = abs(x_out - x_in)
        rise = EAVE - WEAVE
        slen = math.hypot(run, rise)
        ang = math.degrees(math.atan2(rise, run))
        cx_, cz_ = (x_in + x_out) / 2, (EAVE + WEAVE) / 2
        R = F.R() @ Matrix.Rotation(RAD(s * ang), 3, "Y")
        nrm = F.R() @ Vector((-s * math.sin(RAD(ang)), 0, math.cos(RAD(ang))))
        b.box(F.p(cx_, 0.0, cz_) + nrm * 0.35, (slen + 0.6, DEPTH + 3.0, 0.7), RF, rot=R)
        bb(b, F, min(x_out, x_out - s * 0.3) - 0.2, max(x_out, x_out - s * 0.3) + 0.2, -hd - 1.5, hd + 1.5, WEAVE - 0.9, WEAVE - 0.1, TB)
        # chamine da ala
        cxm, czm = L.CHIMNEYS[0 if s < 0 else 1]
        chimney(b, F, s * abs(cxm), -(czm - (ZF + ZB) / 2), GH - 2.0, L.CHIMNEY_TOP - L.Y_PAVE, w=3.0)
        fm_lib.marker("VFX_Chimney_Smoke_%s" % ("L" if s < 0 else "R"), F.p(s * abs(cxm), -(czm - (ZF + ZB) / 2), L.CHIMNEY_TOP - L.Y_PAVE + 1.2),
                      (0, 0, 0), 1.0, "PLAIN_AXES", "15_GAMEPLAY_MARKERS", {"particle": "smoke_heavy", "rate": 8})
        # colisao da ala
        fm_lib.col_box("Forge", (XW - HB + 1.0, DEPTH, WEAVE), F.p(s * (HB + XW) / 2, 0, WEAVE / 2), (0, 0, F.yaw()))
    # ---------------------------------------------------------------- bloco central: colunas, vigas, fundo, oitao
    for (x, y) in ((-HB, hd - 1.2), (HB, hd - 1.2), (-HB, 0.0), (HB, 0.0)):
        bb(b, F, x - 1.4, x + 1.4, y - 1.4, y + 1.4, 0.0, TIE + 1.0, ST)
        bb(b, F, x - 1.8, x + 1.8, y - 1.8, y + 1.8, -0.3, 1.2, STD)
        bb(b, F, x - 1.7, x + 1.7, y - 1.7, y + 1.7, TIE - 0.2, TIE + 1.0, STD)
    # fundo do vao: parede de pedra com a fornalha-mae (arco grande) e prateleiras
    bb(b, F, -HB - 1.0, HB + 1.0, -hd, -hd + 2.0, 0.0, TIE + 1.0, ST)
    Fb = F.face("B", 2 * HB, DEPTH).sub(0, 0, 0, 180)        # olhando para a frente (para dentro do salao)
    Fb = Fr(F.p(0, -hd + 2.0, 0), (F.f.x, F.f.y))
    big = 12.0
    bb(b, Fb, -big / 2 - 1.2, big / 2 + 1.2, -0.6, 0.6, 0.0, 14.0, STD)
    bb(b, Fb, -big / 2, big / 2, -0.4, 0.7, 0.0, 12.0, "WB_Dark")
    bb(b, Fb, -big / 2 + 0.6, big / 2 - 0.6, 0.0, 0.9, 0.0, 2.2, "WB_Ember")
    for (fx, fh, fr) in ((-2.5, 4.0, 1.6), (0.0, 5.0, 2.0), (2.6, 3.6, 1.5)):
        lathe(b, Fb, fx, 0.3, [(fr, 0.0), (fr * 0.75, fh * 0.45), (fr * 0.3, fh * 0.8), (0.0, fh)], "WB_Fire", 8, z0=1.6)
    fm_lib.light("L_WB_Furnace", "POINT", Fb.p(0, 2.0, 5.0), 3200.0, (1.0, 0.45, 0.15), 1.4)
    fm_lib.marker("VFX_Furnace_Fire", Fb.p(0, 0.4, 2.2), (0, 0, 0), 1.0, "PLAIN_AXES", "15_GAMEPLAY_MARKERS",
                  {"particle": "fire", "rate": 18, "size": 4.0})
    # prateleiras de lingotes e ferramentas nas paredes laterais do vao (fora da envoltoria: y < -4,7 local)
    for s in (-1, 1):
        Fs = Fr(F.p(s * (HB - 1.0), 0, 0), (-s * F.t.x, -s * F.t.y))      # olhando para dentro do salao
        for zz in (4.0, 7.5, 11.0):
            bb(b, Fs, -hd + 2.5, -5.0, 0.0, 2.2, zz, zz + 0.3, PK)
            for k in range(5):
                xx = -hd + 3.5 + k * 2.6
                bb(b, Fs, xx - 0.8, xx + 0.8, 0.4, 1.8, zz + 0.3, zz + 1.0, "WB_Ingot" if (k + int(zz)) % 3 == 0 else IR)
        for k in range(4):
            xx = -hd + 4.0 + k * 3.2
            bb(b, Fs, xx - 0.15, xx + 0.15, 0.2, 0.5, 13.5, 20.0, TB)
            bb(b, Fs, xx - 0.9, xx + 0.9, 0.2, 0.6, 19.4, 20.0, IR)
            bb(b, Fs, xx - 0.12, xx + 0.12, 0.2, 0.5, 14.0, 19.6, PK)
        barrel(b, F, s * (HB - 3.0), -hd + 4.0, 1.2, 2.8)
        crate(b, F, s * (HB - 3.2), -hd + 8.0, 2.4, turn=15 * s)
        sack(b, F, s * (HB - 5.6), -hd + 3.2, 1.4)
    # bancada com ferramentas (lado esquerdo, fundo)
    bb(b, F, -HB + 1.4, -HB + 9.0, -hd + 2.2, -hd + 5.0, 3.6, 4.0, PK)
    for xx in (-HB + 2.4, -HB + 5.0, -HB + 8.0):
        bb(b, F, xx - 0.4, xx + 0.4, -hd + 2.4, -hd + 4.8, 0.0, 3.6, TB)
    for k in range(4):
        bb(b, F, -HB + 2.6 + k * 1.6, -HB + 2.6 + k * 1.6 + 0.5, -hd + 3.0, -hd + 3.5, 4.0, 5.2, IR)
    # tirantes (vigas) no topo do vao: frente, meio, fundo + travessas longitudinais
    for y in (hd - 1.2, 0.0, -hd + 1.5):
        bb(b, F, -HB - 1.0, HB + 1.0, y - 0.9, y + 0.9, TIE, TIE + 1.6, TB)
    for x in (-HB, HB):
        bb(b, F, x - 0.9, x + 0.9, -hd, hd, TIE, TIE + 1.6, TB)
    # maos-francesas
    for (x, y) in ((-HB, hd - 1.2), (HB, hd - 1.2), (-HB, 0.0), (HB, 0.0)):
        sx = -1 if x < 0 else 1
        beam(b, F, (x - sx * 0.4, y, TIE - 4.5), (x - sx * 4.0, y, TIE + 0.2), 0.7, 0.7, TB)
    # andar alto do bloco central (reboco ocre + vigas) acima dos tirantes ate o beiral, nas 2 laterais
    for s in (-1, 1):
        Fs = F.face("R" if s > 0 else "L", 2 * HB + 2.0, DEPTH)
        bb(b, Fs, -hd, hd, -1.4, 0.0, TIE + 1.6, EAVE, PLO)
        timber_face(b, Fs, -hd + 0.3, hd - 0.3, TIE + 1.6, EAVE, bays=[-hd + 0.3 + (2 * hd - 0.6) * k / 6 for k in range(7)],
                    skip={1, 4})
        for k in (1, 4):
            cx = -hd + 0.3 + (2 * hd - 0.6) * (k + 0.5) / 6
            window(b, Fs, cx, TIE + 1.6 + 1.6, 1.8, 1.6, shutters=False, flowers=None, box=False)
    # frente do bloco central: reboco acima dos tirantes + oitao (o roof faz o oitao); viga-letreiro
    Ff = F.face("F", 2 * HB + 2.0, DEPTH)
    bb(b, Ff, -HB - 1.0, HB + 1.0, -1.4, 0.0, TIE + 1.6, EAVE, PLO)
    timber_face(b, Ff, -HB - 0.7, HB + 0.7, TIE + 1.6, EAVE, bays=[-HB - 0.7 + (2 * HB + 1.4) * k / 4 for k in range(5)],
                braces=False, mid=False)
    bb(b, Ff, -HB - 1.6, HB + 1.6, -0.2, 1.1, TIE - 0.1, TIE + 1.7, TB, bevel=0.08)            # viga-letreiro
    text(b, Ff, "FORJA DE WOLFBERG", 1.25, TXT, 0.0, 1.12, TIE + 0.8, 0.14, bold=True)
    # fundo do bloco central acima dos tirantes
    Fbk = F.face("B", 2 * HB + 2.0, DEPTH)
    bb(b, Fbk, -HB - 1.0, HB + 1.0, -1.4, 0.0, TIE + 1.6, EAVE, PLO)
    timber_face(b, Fbk, -HB - 0.7, HB + 0.7, TIE + 1.6, EAVE, bays=[-HB - 0.7 + (2 * HB + 1.4) * k / 4 for k in range(5)])
    # telhado do bloco central: cumeeira ao longo de y (oitao para a praca) -> frame girado 90
    Fr90 = F.sub(0, 0, 0, 90)
    zr = roof(b, Fr90, DEPTH + 2.0, 2 * HB + 2.0, EAVE, 55.0, over=1.6, thick=0.8, m=RF, mr=RFD, pl=PLO, gable=True,
              gable_timber=True, fascia=True)
    # janelas extras no oitao da frente (o roof fez 1 central): 2 laterais
    rise_w = (HB + 1.0) * math.tan(RAD(55.0))
    for s in (-1, 1):
        window(b, Ff, s * 6.5, EAVE + rise_w * 0.2, 2.0, 2.2, shutters=True, flowers=None, box=False)
    # lanternas nas colunas da frente e estandartes
    for s in (-1, 1):
        Fc = Fr(F.p(s * HB, hd - 1.2 + 1.4, 0), (F.f.x, F.f.y))
        lantern(b, Fc, 0.0, 0.9, 9.0, "L_WB_Lamp_Forge_%s" % ("L" if s < 0 else "R"))
        bb(b, Fc, -0.15, 0.15, 0.0, 1.0, 9.1, 9.4, IR)
    # colisao do bloco central: colunas, fundo (parede + fornalha-mae), prateleiras laterais
    for (x, y) in ((-HB, hd - 1.2), (HB, hd - 1.2), (-HB, 0.0), (HB, 0.0)):
        fm_lib.col_box("Forge", (3.0, 3.0, TIE), F.p(x, y, TIE / 2), (0, 0, F.yaw()))
    fm_lib.col_box("Forge", (2 * HB + 2.0, 3.4, TIE), F.p(0, -hd + 1.7, TIE / 2), (0, 0, F.yaw()))
    fm_lib.col_box("Forge", (2 * HB + 2.0, 5.5, 4.2), F.p(0, -hd + 4.0, 2.1), (0, 0, F.yaw()))          # bancada/barris
    for s in (-1, 1):
        fm_lib.col_box("Forge", (2.6, hd - 5.0, 12.0), F.p(s * (HB - 1.3), (-hd + 2.0 - 5.0) / 2, 6.0), (0, 0, F.yaw()))
    objs = b.finish()
    # marcadores de contrato do Ignis
    rx, ry, rz = L.IGNIS_ROOT
    W_ = W
    fm_lib.marker("NPC_Ignis", RB(rx, rz, ry), (0, 0, 0), 2.0, "PLAIN_AXES", "15_GAMEPLAY_MARKERS",
                  {"npc": "Ignis", "alvo": "workspace.NPCs.Ignis (Root)", "face_x": 0.0, "face_z": 1.0, "yaw_deg": 180.0,
                   "nota": "Root (-0,9; 7; -60,7) olhando +Z; bigorna a +5 em Z"})
    fm_lib.marker("INTERACT_Ignis", RB(rx, rz + 0.5, L.IGNIS_BELLY_Y), (0, 0, 0), 2.0, "PLAIN_AXES",
                  "15_GAMEPLAY_MARKERS", {"prompt_range": 18, "server_range": 22, "alvo": "belly (prompt do Main)"})
    fm_lib.marker("PLAYER_INTERACT_Ignis", RB(-0.9, -46.0, L.Y_PAVE), (0, 0, 0), 2.0, "PLAIN_AXES",
                  "15_GAMEPLAY_MARKERS", {"note": "chao livre e plano na cota 7 de z -52,7 a -40", "face_x": 0.0,
                                          "face_z": -1.0, "yaw_deg": 0.0})
    fm_lib.marker("IGNIS_Anvil", RB(L.IGNIS_ANVIL[0], L.IGNIS_ANVIL[2], L.IGNIS_ANVIL[1]), (0, 0, 0), 2.0,
                  "PLAIN_AXES", "15_GAMEPLAY_MARKERS", {"nota": "bigorna do golem (colisao da sessao Ignis)"})
    fm_lib.marker("LETREIRO_Ignis", RB(rx, rz, L.LETREIRO_Y), (0, 0, 0), 2.0, "PLAIN_AXES", "15_GAMEPLAY_MARKERS",
                  {"alvo": "LetreiroIgnis"})
    fm_lib.marker("ForgeChimney", RB(L.CHIMNEYS[1][0], L.CHIMNEYS[1][1], L.CHIMNEY_TOP), (0, 0, 0), 2.0, "PLAIN_AXES",
                  "15_GAMEPLAY_MARKERS", {"nota": "AudioWorld: ambiente da chamine"})
    return objs


from wb_lib import RB  # noqa: E402  (usado nos marcadores)
