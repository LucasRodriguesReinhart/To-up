# fm_pv3_dragonball - portal DRAGON BALL (v3, rodada 5 - passe final): "ESFERA DE 4 ESTRELAS".
# Um objeto iconico so, como uma JOIA: a moldura e a LENTE de uma esfera do dragao (vidro laranja-ambar ABAULADO,
# liso, com UM reflexo branco em crescente no alto-esquerda - a mesma linguagem da esfera do topo e da calota)
# cravada num aro de ouro claro de borda meia-cana; UM anel de energia azul Kamehameha ACESO (Neon) encosta direto
# na espiral: o portal le como ligado de longe. No alto, a esfera de 4 estrelas (maior, inteira no quadro do hero)
# CRAVADA no aro como a pedra de um anel: sem taca (nenhuma borda curva atravessa a frente da esfera); 6 dedos
# grossos de ouro de ponta redonda saem de dentro do aro e sobem colados na esfera - de frente leem 4 dedos
# distintos e espalhados, livres das estrelas (coroa/joia, nao bigode). As estrelas da frente olham um pouco para
# baixo (para quem esta na praca).
# Por tras, uma calota ambar com 4 estrelas coladas e o reflexo classico: de costas, uma esfera do dragao gigante.
# O aro assenta num BERCO branco Capsule Corp: dois bracos em crescente na frente (boca plana com filete e colar
# azul onde o aro entra) que se fecham atras num bloco em U - de lado e de costas o berco cobre toda a profundidade
# do aro e da calota (nada laranja abaixo da boca). As faixas laranja/azul sao faces do proprio berco (rentes).
# Plataforma limpa em estadio de 2 degraus com cantos de raio grande; estrela vermelha rasa alinhada com a escada.
# Props (2 grupos, assimetricos, com ar entre eles e o berco na vista frontal): capsula Hoi-Poi deitada (esq.,
# pilula de pontas redondas, costura azul fina, botao em cima) e expositor baixo com as esferas de 1-2-3 estrelas
# em leque (dir.). Sem luminarias (liam como batom): o portal se sustenta sozinho, como a regua do One Piece.
# Paleta: branco, laranja-ambar, ouro claro + azul de acento; vermelho so nas estrelas. Sem dragao (pedido do usuario).
# Espiral: textura propria (T_swirl_db_v6.png, gerada aqui): ki azul do Kamehameha - nucleo branco aceso, 4 bracos
# ciano-claros, fundo azul-royal que escurece na borda. A MESMA PNG vai para o Blender e para o export.
import math, os
import bmesh
import numpy as np
from mathutils import Vector, Matrix, Euler
import fm_lib
from fm_lib import D, col_box, col_box2

# ------------------------------------------------------------------ materiais novos (antes do make_materials)
_M = fm_lib.MATS.setdefault
_M("P_DB_Amber", (fm_lib.S(246, 110, 12), 0.2, 0.0, 0.0, None, 0.0))                         # lente / calota
_M("P_DB_Ball_Amber", (fm_lib.S(255, 150, 12), 0.22, 0.0, 0.15, fm_lib.S(255, 150, 12), 0.0))  # esferas (FOLD_PROTECT)
_M("P_DB_Star_Red", (fm_lib.S(178, 16, 12), 0.7, 0.0, 0.0, None, 0.0))                       # estrelas (FOLD_PROTECT)
_M("P_DB_Floor", (fm_lib.S(168, 180, 198), 0.8, 0.0, 0, None, 0.0))                          # piso cinza-azulado
# ouro de desenho: claro e quente, pouco metalico (com metallic alto refletia a rocha e saia mostarda/oliva);
# no Roblox continua Metal (regra P_DB_Gold) com a mesma cor clara
_M("P_DB_Gold_Bright", (fm_lib.S(255, 196, 60), 0.35, 0.32, 0.0, None, 0.0))
# anel aceso (Neon): azul Kamehameha saturado, emissao <= 3 (regra da familia); so o anel usa este material
_M("P_DB_Rim_Glow", (fm_lib.S(60, 172, 255), 0.4, 0.0, 2.6, fm_lib.S(30, 148, 255), 0.0))
# reflexos (crescentes) da lente, da esfera do topo e da calota: branco liso (nao pulsa com o aro no export_vfx)
_M("P_DB_Shine", (fm_lib.S(255, 255, 255), 0.25, 0.0, 0.6, fm_lib.S(255, 255, 255), 0.0))

import fm_portal_kit as K
from fm_portal_kit import V
import fm_layout as L
import fm_portals as FP
import fm_mat_textures as TX

C = "06_PORTALS"
A = "Portal"
T = L.TERR
PY = L.PORTAL_Y
Y0 = L.FLIGHT2_Y1
SZ = T + 2.0 + 9.2          # centro da espiral (= fm_portals.SZ)
KEY = "DragonBall"
DEBUG = bool(os.environ.get("FM_PV3_DEBUG"))

W, AM, G, B, FL = "P_DB_White", "P_DB_Amber", "P_DB_Gold_Bright", "P_DB_Blue", "P_DB_Floor"
ST, BALL, RIM, SH = "P_DB_Star_Red", "P_DB_Ball_Amber", "P_DB_Rim_Glow", "P_DB_Shine"

# (raio central, meia largura radial, meia profundidade[, deslocamento em y])
RB_R, RB_A, RB_B, RB_DY = 7.52, 0.3, 0.55, -0.5    # anel aceso: r 7.22..7.82, y -1.05..+0.05 (sela a borda do disco)
GA_R, GA_A, GA_B = 8.70, 1.08, 0.95                # lente laranja: r 7.62..9.78 (18% mais estreita que a r4)
LENS_BULGE, LENS_UC = 0.28, -0.1                   # abaulado da face da lente (crista 0.13 a frente do ouro)
BZ_R, BZ_A, BZ_B = 10.40, 0.70, 1.1                # aro de ouro: r 9.70..11.1, borda externa meia-cana
R_OUT = BZ_R + BZ_A                                # raio externo total (11.1)
CROWN_R = 3.3                                      # esfera do topo (r4: 3.0, meio escondida pela taca)
NSEG = 48                                          # lados dos aneis da moldura
CAM_IN = V(0.0, 96.0, T + 6.5)                     # olho de quem chega da escada (x = px)

# ------------------------------------------------------------------ espiral propria (textura v6)
def _ss(a, b, x):
    t = np.clip((x - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)


def _mix(a, b, t):
    t = np.asarray(t)[..., None]
    return a * (1 - t) + b * t


def db_swirl_tex(spec, n=None):
    """espiral do DB (ki do Kamehameha): nucleo branco grande e aceso (a bola de energia), 4 bracos ciano-claros com
    filete branco na borda de ataque, fundo que desce de azul-celeste para azul-royal escuro na borda (le como
    FURO dentro da lente laranja: azul x laranja, as cores do Goku). Sem riscos radiais. Alfa 0 fora do circulo."""
    n = n or TX.SWIRL_N
    c = (np.arange(n) + 0.5) / n * 2 - 1
    X, Y = np.meshgrid(c, -c)                     # linha 0 = topo (mesma convencao de fm_mat_textures)
    r = np.sqrt(X * X + Y * Y)
    th = np.arctan2(Y, X)

    def col(v):
        return np.array(v, float) / 255.0
    BG_OUT, BG_MID, BG_IN = col(spec["border"]), col(spec["bg_mid"]), col(spec["bg_in"])
    ARM, ARM_HI = col(spec["arm"]), col(spec["arm_hi"])
    CORE, HALO = col(spec["core"]), col(spec["halo"])
    rgb = _mix(_mix(np.broadcast_to(BG_IN, r.shape + (3,)), BG_MID, _ss(0.10, 0.55, r)), BG_OUT, _ss(0.50, 0.97, r))
    ph = spec["arms"] * th / (2 * math.pi) + spec["twist"] * r ** 0.85
    s = ph % 1.0 - 0.5
    wl = spec["width"] * (0.45 + 0.65 * np.clip(r, 0, 1))
    lead = np.exp(-(np.maximum(s, 0) / (wl * 0.24)) ** 2)
    trail = np.exp(-(np.maximum(-s, 0) / (wl * 0.85)) ** 2)
    env = _ss(0.05, 0.20, r) * (1 - _ss(0.88, 0.985, r))
    arm = np.where(s >= 0, lead, trail) * env * (1.0 - 0.25 * _ss(0.6, 0.98, r))
    line = np.exp(-((s + wl * 0.04) / (wl * 0.10)) ** 2) * env
    rgb = _mix(rgb, ARM, np.clip(arm, 0, 1))
    rgb = _mix(rgb, ARM_HI, np.clip(line * spec["line"], 0, 1))
    rgb = _mix(rgb, HALO, np.exp(-(r / spec["halo_r"]) ** 2) * 0.85)
    rgb = _mix(rgb, CORE, np.exp(-(r / spec["core_r"]) ** 3))          # ponto branco pequeno e definido
    alpha = (1 - _ss(0.985, 1.0, r))[..., None]
    return np.concatenate([np.clip(rgb, 0, 1), alpha], axis=2)


# ki azul (Kamehameha): o azul de acento da paleta, complementar ao laranja da lente; 4 bracos (a esfera de 4)
SWIRL_DB = dict(border=(10, 40, 140), bg_mid=(25, 105, 220), bg_in=(55, 150, 250), arm=(150, 235, 255),
                arm_hi=(235, 252, 255), core=(255, 255, 255), halo=(200, 244, 255), arms=4, twist=3.0, width=0.44,
                line=0.8, halo_r=0.17, core_r=0.08, style="db_ki")
SWIRL_FILE = "T_swirl_db_v6.png"


def _patch_swirl():
    """registra o desenho novo do DB em fm_mat_textures (so em memoria): SWIRL_SPEC/SWIRL_TEX apontam para a v6 e
    tex_swirl despacha o estilo 'db_ki' para db_swirl_tex. Blender (fm_lib._swirl_nodes), export_roblox e
    export_vfx leem a mesma PNG. Nome novo (v6): o 3D Importer nao reaproveita o cache da v5."""
    spec = dict(TX.SWIRL_SPEC["P_DB_Swirl"])
    spec.update(SWIRL_DB)
    TX.SWIRL_SPEC["P_DB_Swirl"] = spec
    TX.SWIRL_TEX["P_DB_Swirl"] = (SWIRL_FILE, spec["arm"], spec["core"])
    if not getattr(TX.tex_swirl, "_db_ki", False):
        orig = TX.tex_swirl

        def tex_swirl(sp, n=None):
            return db_swirl_tex(sp, n) if sp.get("style") == "db_ki" else orig(sp, n)
        tex_swirl._db_ki = True
        TX.tex_swirl = tex_swirl
    p = os.path.join(TX.TEX_DIR, SWIRL_FILE)
    if not os.path.exists(p):
        os.makedirs(TX.TEX_DIR, exist_ok=True)
        TX.write_png(p, db_swirl_tex(spec))


_patch_swirl()


# ------------------------------------------------------------------ utilidades
def _tris(mb):
    return sum(len(f.verts) - 2 for f in mb.bm.faces)


def _smooth(faces):
    for f in faces:
        if f.is_valid:
            f.smooth = True


def superellipse(a, b, n, p, a0=0.0):
    """secao arredondada: n pontos (u radial, v profundidade)"""
    out = []
    for i in range(n):
        t = a0 + math.tau * i / n
        c, s = math.cos(t), math.sin(t)
        out.append((a * math.copysign(abs(c) ** (2.0 / p), c), b * math.copysign(abs(s) ** (2.0 / p), s)))
    return out


def ring_loft(mb, c, angs, profs, m, smooth=True, closed=False, cap=True, flat_y=False):
    """aneis no plano XZ em torno de c: angs (graus) e profs [(raio, dy), ...] por anel; closed = volta completa.
    flat_y: faces de frente/costas (normal +-Y, coplanares) ficam lisas (face plana de lente, sem gradiente)"""
    bm = mb.bm
    c = Vector(c)
    rings = []
    for a, prof in zip(angs, profs):
        co, si = math.cos(D(a)), math.sin(D(a))
        rings.append([bm.verts.new((c.x + r * co, c.y + dy, c.z + r * si)) for r, dy in prof])
    k = len(rings[0])
    quads = []
    pairs = list(zip(rings, rings[1:]))
    if closed:
        pairs.append((rings[-1], rings[0]))
    for r0, r1 in pairs:
        for j in range(k):
            j2 = (j + 1) % k
            try:
                quads.append(bm.faces.new((r0[j], r0[j2], r1[j2], r1[j])))
            except ValueError:
                pass
    if cap and not closed:
        for r in (rings[0], rings[-1]):
            try:
                bm.faces.new(r)
            except ValueError:
                pass
    mb._post([v for r in rings for v in r], m, None, 0, 1)
    if smooth:
        for f in quads:
            if not f.is_valid:
                continue
            f.normal_update()
            f.smooth = not (flat_y and abs(f.normal.y) > 0.995)
    return rings


def torus(mb, c, rc, prof, m, n=NSEG, smooth=True, dy=0.0, flat_y=False):
    """anel completo no plano XZ: secao prof [(du, dv)] em torno do raio rc"""
    angs = [360.0 * i / n for i in range(n)]
    p = [(rc + u, dy + v) for u, v in prof]
    ring_loft(mb, c, angs, [p] * n, m, smooth, closed=True, flat_y=flat_y)


def lathe(mb, base, axis, prof, m, n=16, smooth=True, a0=0.0, caps=True):
    """solido de revolucao: prof = [(raio, altura ao longo do eixo)], raio 0 = polo"""
    base = Vector(base)
    ax = Vector(axis).normalized()
    u = ax.orthogonal().normalized()
    w = ax.cross(u)
    bm = mb.bm
    rings = []
    for r, h in prof:
        c = base + ax * h
        if r < 1e-4:
            rings.append([bm.verts.new(c)])
        else:
            rings.append([bm.verts.new(c + (u * math.cos(a0 + math.tau * i / n) + w * math.sin(a0 + math.tau * i / n)) * r)
                          for i in range(n)])
    faces = []
    for r0, r1 in zip(rings, rings[1:]):
        if len(r0) == 1 and len(r1) == 1:
            continue
        for i in range(n):
            j = (i + 1) % n
            if len(r0) == 1:
                faces.append(bm.faces.new((r0[0], r1[i], r1[j])))
            elif len(r1) == 1:
                faces.append(bm.faces.new((r0[i], r0[j], r1[0])))
            else:
                faces.append(bm.faces.new((r0[i], r0[j], r1[j], r1[i])))
    if caps:
        for r in (rings[0], rings[-1]):
            if len(r) > 1:
                try:
                    bm.faces.new(r)
                except ValueError:
                    pass
    mb._post([v for r in rings for v in r], m, None, 0, 1)
    if smooth:
        _smooth(faces)


def sphere(mb, c, r, m, us=24, vs=14, scale=(1, 1, 1), rot=(0, 0, 0), smooth=True):
    M = Matrix.LocRotScale(Vector(c), Euler(rot), Vector(scale))
    res = bmesh.ops.create_uvsphere(mb.bm, u_segments=us, v_segments=vs, radius=r, matrix=M)
    faces = mb._post(res["verts"], m, None, 0, 1)
    if smooth:
        _smooth(faces)


def rrect(cx, cy, hx, hy, r, nc=6):
    """retangulo arredondado (anti-horario); r = min(hx, hy) vira estadio"""
    pts = []
    for sx, sy, a0 in ((1, -1, -90), (1, 1, 0), (-1, 1, 90), (-1, -1, 180)):
        ccx, ccy = cx + sx * (hx - r), cy + sy * (hy - r)
        for i in range(nc + 1):
            a = D(a0 + 90.0 * i / nc)
            p = (ccx + math.cos(a) * r, ccy + math.sin(a) * r)
            if not pts or math.hypot(p[0] - pts[-1][0], p[1] - pts[-1][1]) > 1e-3:
                pts.append(p)
    if math.hypot(pts[0][0] - pts[-1][0], pts[0][1] - pts[-1][1]) < 1e-3:
        pts.pop()
    return pts


def offset_poly(poly, d):
    """offset simples de poligono convexo anti-horario (d > 0 = para fora)"""
    n = len(poly)
    out = []
    for i in range(n):
        p0, p1, p2 = Vector(poly[i - 1]), Vector(poly[i]), Vector(poly[(i + 1) % n])
        e0 = (p1 - p0).normalized()
        e1 = (p2 - p1).normalized()
        n0 = Vector((e0.y, -e0.x))
        n1 = Vector((e1.y, -e1.x))
        bis = (n0 + n1)
        if bis.length < 1e-6:
            bis = n0
        bis.normalize()
        k = d / max(0.3, bis.dot(n0))
        out.append((p1.x + bis.x * k, p1.y + bis.y * k))
    return out


def star2d(ro, ri=None, spin=0.0):
    ri = ro * 0.45 if ri is None else ri
    return [((ro if i % 2 == 0 else ri) * math.cos(D(90 + spin + 36 * i)),
             (ro if i % 2 == 0 else ri) * math.sin(D(90 + spin + 36 * i))) for i in range(10)]


def _frame_on(n, up=(0, 0, 1)):
    """base tangente (direita, cima) de quem olha a superficie de fora, na direcao -n"""
    n = Vector(n).normalized()
    u = Vector(up) - n * Vector(up).dot(n)
    if u.length < 1e-4:
        u = Vector((1, 0, 0)) - n * n.x
    u.normalize()
    side = u.cross(n).normalized()
    return n, side, u


def _on_sphere(c, R, n, side, u, a, b, h):
    """ponto 2D (a, b) no plano tangente, projetado ORTOGONALMENTE (ao longo de n) na esfera, a R + h do centro"""
    t = side * a + u * b
    dep = math.sqrt(max(0.0, R * R - t.length_squared))
    d = (t + n * dep).normalized()
    return c + d * (R + h)


def sphere_decal(mb, c, R, n, pts2d, m, off=0.05, depth=0.12, up=(0, 0, 1)):
    """poligono 2D estrelado em relacao a (0, 0) colado na esfera (centro c, raio R) em volta da direcao n:
    face de cima a R + off (leque do centro), parede ate R - depth (dentro da esfera; sem fundo).
    Segue a curvatura: nenhuma quina reta sai do contorno da esfera."""
    c = Vector(c)
    n, side, u = _frame_on(n, up)
    bm = mb.bm
    top = [bm.verts.new(_on_sphere(c, R, n, side, u, a, b, off)) for a, b in pts2d]
    bot = [bm.verts.new(_on_sphere(c, R, n, side, u, a, b, -depth)) for a, b in pts2d]
    ct = bm.verts.new(_on_sphere(c, R, n, side, u, 0.0, 0.0, off))
    k = len(pts2d)
    for i in range(k):
        j = (i + 1) % k
        bm.faces.new((ct, top[i], top[j]))
        bm.faces.new((top[j], top[i], bot[i], bot[j]))
    mb._post(top + bot + [ct], m, None, 0, 1)


def sphere_crescent(mb, c, R, n, rr, a0, a1, w, m, k=8, off=0.05, depth=0.1, up=(0, 0, 1)):
    """reflexo classico: crescente (arco de raio rr no plano tangente, de a0 a a1 graus, meia largura w no meio,
    pontas finas) colado na esfera"""
    c = Vector(c)
    n, side, u = _frame_on(n, up)
    bm = mb.bm
    rows = []
    for i in range(k + 1):
        f = i / k
        a = D(a0 + (a1 - a0) * f)
        ww = w * (0.12 + 0.88 * math.sin(math.pi * f))
        ca, sa = math.cos(a), math.sin(a)
        row = []
        for rad, h in ((rr - ww, off), (rr + ww, off), (rr + ww, -depth), (rr - ww, -depth)):
            row.append(bm.verts.new(_on_sphere(c, R, n, side, u, ca * rad, sa * rad, h)))
        rows.append(row)
    for r0, r1 in zip(rows, rows[1:]):
        bm.faces.new((r0[0], r0[1], r1[1], r1[0]))           # topo
        bm.faces.new((r0[1], r0[2], r1[2], r1[1]))           # parede externa
        bm.faces.new((r0[3], r0[0], r1[0], r1[3]))           # parede interna
    bm.faces.new((rows[0][3], rows[0][2], rows[0][1], rows[0][0]))
    bm.faces.new((rows[-1][0], rows[-1][1], rows[-1][2], rows[-1][3]))
    mb._post([v for r in rows for v in r], m, None, 0, 1)


def col_obb(ctr, ax, ay, az_, size):
    """caixa de colisao orientada: centro, eixos locais unitarios (destro: ax x ay = az_) e tamanho"""
    M = Matrix((tuple(ax), tuple(ay), tuple(az_))).transposed()
    col_box(A, size, tuple(ctr), M.to_euler("XYZ"))


def lens_front_v(u):
    """y (relativo a PY) da face da frente da lente a u do raio central GA_R: abaulada (lente de vidro), crista um
    pouco para dentro; nas bordas volta a -GA_B (fica atras da face do ouro)"""
    q = 1.0 - ((u - LENS_UC) / (GA_A + 0.08)) ** 2
    return -(GA_B + LENS_BULGE * max(0.0, q))


def lens_section():
    """secao da lente (u radial, v = y), anti-horaria no plano (u, v): frente abaulada (7 pontos, lisa), lado de
    fora (dentro do ouro), costas planas (dentro da calota), lado de dentro (sob o anel aceso)"""
    k = GA_A / 1.08
    sec = [(u * k, lens_front_v(u * k)) for u in (-0.98, -0.66, -0.3, 0.06, 0.42, 0.74, 0.98)]
    sec += [(GA_A, -0.62), (GA_A, 0.6), (GA_A - 0.3, GA_B), (-GA_A + 0.3, GA_B), (-GA_A, 0.6), (-GA_A, -0.66)]
    return sec


def lens_crescent(mb, c, a0, a1, uc, w, m, k=10, off=0.035, depth=0.07):
    """reflexo em crescente colado na face abaulada da lente: arco de a0 a a1 graus (plano XZ) em volta do raio
    GA_R + uc, meia largura w no meio e pontas finas; segue a curvatura da face (ilha fechada, rasa)"""
    bm = mb.bm
    rows = []
    for i in range(k + 1):
        f = i / k
        a = D(a0 + (a1 - a0) * f)
        ww = w * (0.14 + 0.86 * math.sin(math.pi * f))
        ca, sa = math.cos(a), math.sin(a)
        row = []
        for u, h in ((uc - ww, -off), (uc + ww, -off), (uc + ww, depth), (uc - ww, depth)):
            r = GA_R + u
            row.append(bm.verts.new((c.x + r * ca, c.y + lens_front_v(u) + h, c.z + r * sa)))
        rows.append(row)
    for r0, r1 in zip(rows, rows[1:]):
        bm.faces.new((r0[0], r0[1], r1[1], r1[0]))
        bm.faces.new((r0[1], r0[2], r1[2], r1[1]))
        bm.faces.new((r0[3], r0[0], r1[0], r1[3]))
        bm.faces.new((r0[2], r0[3], r1[3], r1[2]))
    bm.faces.new((rows[0][3], rows[0][2], rows[0][1], rows[0][0]))
    bm.faces.new((rows[-1][0], rows[-1][1], rows[-1][2], rows[-1][3]))
    mb._post([v for r in rows for v in r], m, None, 0, 1)


def ball_stars(mb, c, r, k, size, facing=(0, -1, 0), spread=None, off=0.05):
    """k estrelas (1..4) coladas no hemisferio voltado para 'facing' (4 = losango)"""
    f = Vector(facing).normalized()
    sp = spread if spread is not None else r * 0.36
    lay = {1: [(0, 0)], 2: [(-0.55, 0.0), (0.55, 0.0)], 3: [(0, 0.55), (-0.55, -0.4), (0.55, -0.4)],
           4: [(0, 1.0), (-1.0, 0), (1.0, 0), (0, -1.0)]}[k]
    n, side, u = _frame_on(f)
    for a, b in lay:
        d = _on_sphere(Vector((0, 0, 0)), r, n, side, u, a * sp, b * sp, 0.0).normalized()
        sphere_decal(mb, c, r, d, star2d(size), ST, off=off, depth=min(0.12, r * 0.1))




# ------------------------------------------------------------------ partes
def platform(mb, px):
    """estadio em 2 degraus, limpo: degrau 1 = piso cinza-azulado sobre rodape branco, cantos de raio grande (mesma
    linguagem arredondada das capsulas); degrau 2 = estadio branco sobre faixa azul (o aro e o berco assentam nele)
    com uma estrela vermelha rasa alinhada com a escada"""
    z1, z2 = T + 0.9, T + 1.8
    t1 = rrect(px, 110.9, 13.4, 10.7, 6.5, 8)          # cantos mais redondos (r4: 5 lados facetavam)
    mb.prism(offset_poly(t1, -0.1), T - 0.6, z1 - 0.3, W, bevel=0.0)
    mb.prism(t1, z1 - 0.32, z1, FL, bevel=0.2, seg=1)
    t2 = rrect(px, PY, 11.4, 6.0, 6.0, 7)
    mb.prism(t2, z1 - 0.1, z2 - 0.3, B, bevel=0.0)
    mb.prism(offset_poly(t2, 0.12), z2 - 0.34, z2, W, bevel=0.22, seg=1)
    # emblema: estrela de 5 pontas rasa no degrau 2 (conduz o olhar da escada ao disco)
    K.plate(mb, star2d(1.7), V(px, 109.25, z2 + 0.005), (1, 0, 0), (0, 1, 0), 0.08, ST)
    # colisao andavel: degrau 1 em 2 caixas (dentro dos cantos de raio 6.5), degrau 2 (estadio) em 3
    col_box2(A, (px - 13.1, 104.8, T - 1.0), (px + 13.1, 117.0, z1))
    col_box2(A, (px - 7.4, 100.2, T - 1.0), (px + 7.4, 121.6, z1))
    col_box2(A, (px - 10.8, 110.4, z1 - 0.5), (px + 10.8, 115.6, z2))
    col_box2(A, (px - 8.6, 108.3, z1 - 0.5), (px + 8.6, 117.7, z2))
    col_box2(A, (px - 5.4, 107.0, z1 - 0.5), (px + 5.4, 119.0, z2))
    return z1, z2


DOME_AB, DOME_H, DOME_Y0 = 9.4, 3.0, 0.85          # calota: raio da base, altura, y da base (relativo a PY)
DOME_RS = (DOME_AB ** 2 + DOME_H ** 2) / (2 * DOME_H)          # raio da esfera da calota (16.2)


def dome_y(r):
    """y (relativo a PY) da superficie da calota a r do eixo da espiral"""
    if r >= DOME_AB:
        return DOME_Y0
    return DOME_Y0 + math.sqrt(DOME_RS ** 2 - r * r) - (DOME_RS - DOME_H)


def frame(mb, px):
    """anel aceso azul + lente laranja ABAULADA com reflexo em crescente + aro de ouro meia-cana; calota ambar atras
    com 4 estrelas coladas e o reflexo classico"""
    c = V(px, PY, SZ)
    # anel de energia (Neon): sela a borda do disco e cobre a quina interna da lente
    torus(mb, c, RB_R, superellipse(RB_A, RB_B, 6, 2.2, a0=math.pi / 6), RIM, n=48, dy=RB_DY)
    # lente de vidro: face abaulada e lisa (o sombreamento suave escurece para a borda do ouro) + UM reflexo branco
    # em crescente no alto-esquerda, na encosta de fora (a que olha para a luz)
    torus(mb, c, GA_R, lens_section(), AM)
    lens_crescent(mb, c, 114.0, 160.0, 0.3, 0.18, SH)
    # aro de ouro: face plana na frente/atras, borda externa em meia-cana
    a, b = BZ_A, BZ_B
    sec = [(-a, -b), (0.0, -b)] + [(a * math.sin(D(t)), -b * math.cos(D(t))) for t in (30, 60, 90, 120, 150)]
    sec += [(0.0, b), (-a, b)]
    torus(mb, c, BZ_R, sec, G, flat_y=True)
    # calota traseira ambar = calota de esfera; sem tampa na base (fica dentro da lente); a parte de baixo mergulha
    # no bloco traseiro do berco
    prof = [(rr, dome_y(rr) - DOME_Y0) for rr in (DOME_AB, 8.3, 7.0, 5.6, 4.2, 2.8, 1.4, 0.0)]
    lathe(mb, V(px, PY + DOME_Y0, SZ), (0, 1, 0), prof, AM, 28, caps=False)
    dc = V(px, PY + DOME_Y0 + DOME_H - DOME_RS, SZ)          # centro da esfera da calota
    back = (0, 1, 0)
    # 4 estrelas em quadrado (acima do topo do bloco traseiro; fora do meridiano x = px)
    for ang in (45, 135, 225, 315):
        d = _on_sphere(Vector((0, 0, 0)), DOME_RS, *(_frame_on(back)), 3.4 * math.cos(D(ang)), 3.4 * math.sin(D(ang)),
                       0.0).normalized()
        sphere_decal(mb, dc, DOME_RS, d, star2d(1.8), ST, off=0.06, depth=0.12)
    sphere_crescent(mb, dc, DOME_RS, back, 6.9, 100, 150, 0.32, SH, k=8, off=0.05)


CR_TOP = 27.1           # topo da esfera acima de T: cabe inteira no quadro do A_Hero (com pescoco saia cortada)
CR_TILT = 8.0           # estrelas da frente olham um pouco para baixo (para a praca e a escada)
# dedos: 4 no hemisferio da frente (de frente leem 4 distintos, x ~ +-0.47R e +-0.87R, livres das estrelas; os
# que ficassem no plano do aro sumiriam dentro do ouro) + 2 atras (para as costas e as vistas 3/4)
CR_AZ = (-150, -118, -62, -30, 60, 120)


def crown_center():
    """centro da esfera do topo: assentada no alto do aro (o ouro do aro entra no polo de baixo, como a pedra
    cravada num anel), com o topo em T + CR_TOP"""
    return T + CR_TOP - CROWN_R


def crown(mb, px):
    """esfera de 4 estrelas CRAVADA no alto do aro como a pedra de um anel (nada de taca: nenhuma borda curva
    atravessa a frente da esfera). A pega sao 4 dedos GROSSOS de ouro de ponta redonda que saem de dentro do aro e
    sobem colados na esfera ate ~25 graus abaixo do equador; azimutes -60/-120 (frente) e 30/150 (atras): de frente
    leem 4 dedos distintos (x ~ +-0.5R e +-0.87R), livres das estrelas. A esfera fica inteira acima do disco."""
    R = CROWN_R
    cz = crown_center()
    cb = V(px, PY, cz)
    sphere(mb, cb, R, BALL, 22, 12)
    tl = D(CR_TILT)
    front = (0.0, -math.cos(tl), -math.sin(tl))
    for fdir in (front, (0, 1, 0)):
        ball_stars(mb, cb, R, 4, 0.24 * R, facing=fdir, spread=0.28 * R, off=0.06)
    for fdir in ((0.0, -1.0, 0.0), (0, 1, 0)):
        sphere_crescent(mb, cb, R, fdir, R * 0.8, 100, 132, 0.2, SH, k=7, off=0.04)
    # dedos: secao eliptica (w de lado, t na normal) 0.46 x 0.31 na base -> ponta arredondada; o eixo corre a
    # 0.8 t da superficie (a face de dentro encosta na esfera): acompanham a curva e fecham para dentro. A base
    # (lat -78) fica dentro da lente/ouro do aro.
    spec = ((-78, 0.46, 0.31), (-68, 0.45, 0.30), (-58, 0.42, 0.29), (-49, 0.37, 0.265), (-41, 0.31, 0.235),
            (-34.5, 0.25, 0.2), (-30.2, 0.19, 0.16), (-27.6, 0.12, 0.11), (-26.5, 0.045, 0.045))
    n0 = len(mb.bm.faces)
    for az in CR_AZ:
        hv = V(math.cos(D(az)), math.sin(D(az)), 0)
        pts, profs = [], []
        for lat, w, t in spec:
            la = D(lat)
            rr = R + 0.8 * t
            pts.append(cb + hv * (math.cos(la) * rr) + V(0, 0, math.sin(la) * rr))
            profs.append([(math.cos(math.tau * i / 6) * t, math.sin(math.tau * i / 6) * w) for i in range(6)])
        K.loft(mb, pts, profs, G, True)
    mb.bm.faces.ensure_lookup_table()
    _smooth(mb.bm.faces[n0:])


# ------------------------------------------------------------------ berco Capsule Corp
CR_RI, CR_A0, CR_A1, CR_RC, CR_DB = 9.3, 206.0, 334.0, 0.55, 3.6   # raio interno, arco, canto, costas (y)
CR_ZTOP = T + 6.3                                                  # topo do bloco traseiro (abaixo da boca)
CR_LIP = 0.55                                                      # filete da boca


def _cr_shape(u):
    """u em [-1, 1] ao longo do arco (0 = fundo): espessura radial, profundidade da frente"""
    q = 1 - u * u
    return 2.45 + 0.7 * q, 1.8 + 0.15 * q


def _cr_u(a):
    return -1 + 2 * (a - CR_A0) / (CR_A1 - CR_A0)


def _cr_rb(a):
    """raio interno das COSTAS no angulo a: o bloco traseiro tem topo horizontal em CR_ZTOP"""
    s = -math.sin(D(a))
    if s <= 1e-3:
        return CR_RI
    return min(CR_RI, (SZ - CR_ZTOP) / s)


def _cr_section(th, df, rb, o):
    """secao do berco: 24 pontos (r, y relativo a PY, material do segmento ate o proximo). Retangulo arredondado
    (frente y = -df, costas y = +CR_DB, r de CR_RI a CR_RI + th) cujo lado interno DAS COSTAS desce ate rb (bloco
    traseiro de topo horizontal); E e F ficam escondidos dentro da calota/lente. As faixas sao faces da propria
    secao (rentes). o = recuo do filete da boca."""
    ri, ro = CR_RI + o, CR_RI + th - o
    f, b = -df + o, CR_DB - o
    rbi = rb + o
    rc = max(0.05, CR_RC - o)
    out = []

    def corner(cu, cv, a0):
        for i in range(3):
            a = D(a0 + 45.0 * i)
            out.append((cu + rc * math.cos(a), cv + rc * math.sin(a), W))
    lo, hi = CR_RI + CR_RC + 0.03, CR_RI + th - CR_RC - 0.03

    def cl(r):
        return min(hi, max(lo, r))
    fr = [cl(CR_RI + k * th) for k in (0.25, 0.38, 0.60, 0.73)]
    corner(ri + rc, f + rc, 180)                                            # A: interno-frente
    out += [(fr[0], f, AM), (fr[1], f, W), (fr[2], f, B), (fr[3], f, W)]      # faixas laranja e azul (frente)
    corner(ro - rc, f + rc, 270)                                            # B: externo-frente
    vm = 0.5 * (f + b)
    out += [(ro, vm - 0.45, B), (ro, vm + 0.45, W)]                          # faixa azul na face de fora
    corner(ro - rc, b - rc, 0)                                              # C: externo-costas
    tr = min(rbi + rc + 0.45, fr[2] - 0.3)
    out += [(fr[3], b, B), (fr[2], b, W), (tr, b, AM), (rbi + rc + 0.08, b, W)]   # azul + friso laranja do topo
    corner(rbi + rc, b - rc, 90)                                            # D: interno-costas (borda do topo)
    ye = min(2.0, dome_y(rb) - 0.15)
    out += [(rbi, ye, W), (ri, 0.6, W)]                                     # E, F (dentro da calota / lente)
    return out


def _arc_loft(mb, c, secs, smooth=True, cap_m=W):
    """secs = [(angulo, [(r, y, material), ...]), ...]: aneis no plano XZ em volta de c, material por segmento da
    secao; tampas planas nas duas pontas (no plano radial: o aro que atravessa a tampa corta limpo)"""
    bm = mb.bm
    rings = []
    for a, sec in secs:
        co, si = math.cos(D(a)), math.sin(D(a))
        rings.append([bm.verts.new((c.x + r * co, c.y + y, c.z + r * si)) for r, y, _ in sec])
    k = len(rings[0])
    tags = [m for _, _, m in secs[0][1]]
    quads = []
    for r0, r1 in zip(rings, rings[1:]):
        for j in range(k):
            j2 = (j + 1) % k
            quads.append((bm.faces.new((r0[j], r0[j2], r1[j2], r1[j])), tags[j]))
    caps = [bm.faces.new(rings[0]), bm.faces.new(list(reversed(rings[-1])))]
    mb._post([v for r in rings for v in r], cap_m, None, 0, 1)
    for f, m in quads:
        if m != cap_m:
            f.material_index = mb._mi_for(m)
        f.smooth = smooth
    for f in caps:
        f.smooth = False
    return rings


def _rr_pts(u0, u1, v0, v1, rc):
    """retangulo arredondado (12 pontos) no plano (r, y)"""
    out = []
    for cu, cv, a0 in ((u0 + rc, v0 + rc, 180), (u1 - rc, v0 + rc, 270), (u1 - rc, v1 - rc, 0), (u0 + rc, v1 - rc, 90)):
        for i in range(3):
            a = D(a0 + 45.0 * i)
            out.append((cu + rc * math.cos(a), cv + rc * math.sin(a), B))
    return out


def cradle(mb, px, z2):
    """berco branco Capsule Corp: dois bracos em crescente que abracam a parte de baixo do aro (7-8h e 4-5h) e se
    fecham ATRAS num bloco de topo horizontal (U visto de costas): de lado e de costas o berco cobre toda a
    profundidade da lente e da calota. Boca: ponta com filete arredondado e tampa plana no plano radial (o aro sai
    limpo) + colar azul em volta do tubo. Faixas laranja/azul pintadas nas faces do proprio berco."""
    c = V(px, PY, SZ)
    ast = 180.0 + math.degrees(math.asin((SZ - CR_ZTOP) / CR_RI))        # onde o topo do bloco encontra os bracos
    angs = sorted(set([206.0, 210.0, 214.0, 218.0, 222.0, 226.0, 234.0, 246.0, 258.0, 270.0, 282.0, 294.0, 306.0,
                       314.0, 318.0, 322.0, 326.0, 330.0, 334.0, round(ast, 2), round(540.0 - ast, 2)]))
    th0 = _cr_shape(-1.0)[0]
    rmid = CR_RI + th0 / 2
    lips = []
    for ph in (30.0, 60.0, 90.0):
        lips.append((CR_LIP * (1 - math.cos(D(ph))), math.degrees(CR_LIP * math.sin(D(ph)) / rmid)))
    secs = []

    def add(a, o):
        th, df = _cr_shape(max(-1.0, min(1.0, _cr_u(a))))
        secs.append((a, _cr_section(th, df, _cr_rb(a), o)))
    for o, da in reversed(lips):
        add(CR_A0 - da, o)
    for a in angs:
        add(a, 0.0)
    for o, da in lips:
        add(CR_A1 + da, o)
    _arc_loft(mb, c, secs)
    # colar azul na boca: abraca lente + latao onde saem do berco (esconde a costura)
    cap_da = lips[-1][1]
    for a_cap, sg in ((CR_A0 - cap_da, -1.0), (CR_A1 + cap_da, 1.0)):
        csec = []
        for d_ang, o in ((-0.5, 0.0), (1.6, 0.0), (2.0, 0.14)):
            r0, r1, h = CR_RI + 0.45 + o, R_OUT + 0.25 - o, BZ_B + 0.23 - o
            csec.append((a_cap + sg * d_ang, _rr_pts(r0, r1, -h, h, max(0.05, 0.3 - o))))
        _arc_loft(mb, c, csec, cap_m=B)
    # colisao: bracos (2 caixas giradas por lado, raio CR_RI..externo, frente ate as costas) + parte de baixo da
    # lente entre o braco e a soleira (1 por lado; a de cima virou a caixa baixa da lateral do aro, ring_side_cols)
    for s in (-1, 1):
        for ang0, ang1 in ((205.0, 231.0), (231.0, 257.0)):
            am = 0.5 * (ang0 + ang1)
            th, df = _cr_shape(_cr_u(am))
            th_ = D(am) if s < 0 else D(540.0 - am)
            ro = CR_RI + th - 0.1
            rm = 0.5 * (CR_RI + ro)
            chord = 2 * rm * math.sin(D(0.5 * (ang1 - ang0))) + 0.3
            col_box(A, (ro - CR_RI, df + CR_DB, chord),
                    (px + math.cos(th_) * rm, PY + 0.5 * (CR_DB - df), SZ + math.sin(th_) * rm), (0, -th_, 0))
            if ang0 < 230.0:
                continue
            # parte de baixo da lente fora dos bracos (r 7.45..CR_RI; y da crista abaulada ate as costas)
            rl = 0.5 * (7.45 + CR_RI)
            chl = 2 * rl * math.sin(D(0.5 * (ang1 - ang0))) + 0.3
            col_box(A, (CR_RI - 7.45, LENS_Y1 - LENS_Y0, chl),
                    (px + math.cos(th_) * rl, PY + 0.5 * (LENS_Y0 + LENS_Y1), SZ + math.sin(th_) * rl), (0, -th_, 0))
    ring_side_cols(px)


LENS_Y0, LENS_Y1 = -1.25, 1.0          # colisao do aro em y: da crista da lente (-1.23) ate as costas da lente/ouro


def ring_box(px, th_t, th_a, th_b, d_i, d_o, y0=LENS_Y0, y1=1.2):
    """caixa girada no plano XZ que segue o aro: eixo radial em th_t (graus), face de dentro a d_i e de fora a d_o do
    centro da espiral; comprimento = de th_a a th_b medido na face de fora (quinas a d_o / cos)"""
    tr = D(th_t)
    er = V(math.cos(tr), 0, math.sin(tr))
    et = V(-math.sin(tr), 0, math.cos(tr))
    sa, sb = d_o * math.tan(D(th_a - th_t)), d_o * math.tan(D(th_b - th_t))
    ctr = V(px, PY, SZ) + er * (0.5 * (d_i + d_o)) + et * (0.5 * (sa + sb)) + V(0, 0.5 * (y0 + y1), 0)
    col_obb(ctr, er, V(0, 1, 0), et, (d_o - d_i, y1 - y0, abs(sb - sa)))


def ring_side_cols(px):
    """laterais do aro acima da boca do berco: 2 caixas giradas por lado que seguem o aro. A de baixo (de dentro do
    degrau ate ~188 graus) tem a face de fora rente ao ouro onde o corpo alcanca (topo dos bracos ate a cabeca) e
    engole a parte de baixo da lente; a de cima cobre o topo da de baixo e termina com a quina de dentro em ~T+15.6
    (fora do alcance do pulo: nenhum patamar invisivel dentro do aro)"""
    for s in (-1, 1):
        def ang(a):
            return a if s < 0 else 180.0 - a
        ring_box(px, ang(200.0), ang(234.0), ang(188.0), 7.5, 11.08)
        ring_box(px, ang(172.0), ang(189.0), ang(158.0), 7.5, 11.05, -1.15, 1.15)


# calota vista de tras: caixa central (rente ao topo achatado) + 2 caixas TANGENTES por lado (baixa e alta), cada
# uma com a face de tras no plano tangente a esfera da calota no meio da regiao, recuada 'ins' (desvio <= ~0.25).
# Cobrem do topo do bloco traseiro ate acima do alcance do pulo: quem sobe no bloco nao afunda na esfera.
DOME_TAN = ((3.4, 8.3, -5.2, -1.0, 0.16), (3.4, 8.1, -1.2, 3.9, 0.2))    # (|x|0, |x|1, dz0, dz1, recuo)
DOME_TAN_T = 1.6                                                        # espessura (para dentro)


def _dome_tan_box(px, x0, x1, dz0, dz1, ins, s):
    yc = DOME_Y0 + DOME_H - DOME_RS                                  # centro da esfera da calota (relativo a PY)
    xm, zm = s * 0.5 * (x0 + x1), 0.5 * (dz0 + dz1)
    P0 = Vector((xm, dome_y(math.hypot(xm, zm)), zm))
    n = Vector((xm, P0.y - yc, zm)).normalized()
    a1 = (Vector((1, 0, 0)) - n * n.x).normalized()
    a2 = n.cross(a1)
    loc = []
    for xx in (s * x0, s * x1):
        for zz in (dz0, dz1):
            yy = P0.y - (n.x * (xx - P0.x) + n.z * (zz - P0.z)) / n.y
            q = Vector((xx, yy, zz)) - P0
            loc.append((q.dot(a1), q.dot(a2)))
    u0, u1 = min(p[0] for p in loc), max(p[0] for p in loc)
    v0, v1 = min(p[1] for p in loc), max(p[1] for p in loc)
    ctr = P0 + a1 * (0.5 * (u0 + u1)) + a2 * (0.5 * (v0 + v1)) - n * (ins + 0.5 * DOME_TAN_T)
    col_obb(V(px, PY, SZ) + ctr, a1, a2, n, (u1 - u0, v1 - v0, DOME_TAN_T))


def ring_cols(px, z2):
    """soleira (pe da lente, degrau ate o disco), bloco traseiro do berco e a calota vista de tras (central + 4
    tangentes). A frente da caixa central (y PY+0.7) e a antiga parede de toque atras do disco."""
    col_box2(A, (px - 6.8, PY + LENS_Y0, z2 - 0.2), (px + 6.8, PY + 1.1, SZ - 7.55))
    col_box2(A, (px - 8.0, PY + 0.9, z2 - 0.2), (px + 8.0, PY + CR_DB, CR_ZTOP))
    col_box2(A, (px - 3.6, PY + 0.7, SZ - 3.6), (px + 3.6, PY + 3.22, SZ + 3.6))
    for s in (-1, 1):
        for x0, x1, dz0, dz1, ins in DOME_TAN:
            _dome_tan_box(px, x0, x1, dz0, dz1, ins, s)


def capsule_prop(mb, px, z1):
    """capsula Hoi-Poi deitada (esq.): pilula de pontas REDONDAS (nada de pilha), metade branca e metade laranja,
    costura azul fina e o botao em cima da metade laranja"""
    r, hl = 1.2, 2.6
    cx, cy = px - 9.0, 103.7          # r4: -7.2 (encostava no berco na vista frontal)
    yaw = D(165)                      # ponta laranja recua junto com o canto redondo da plataforma
    d = V(math.cos(yaw), math.sin(yaw), 0)
    c = V(cx, cy, z1 + r - 0.04)
    k = 4
    hc = hl - r
    s0, s1 = 0.12, 0.34                             # costura azul (ao longo de d, a partir do centro)
    prof_w = [(0.0, -hl)] + [(r * math.sin(D(90 * i / k)), -hc - r * math.cos(D(90 * i / k))) for i in range(1, k + 1)]
    prof_w += [(r, s0 + 0.03)]
    lathe(mb, c, d, prof_w, W, 14, caps=False)
    lathe(mb, c, d, [(r - 0.03, s0), (r + 0.05, s0 + 0.04), (r + 0.05, s1 - 0.04), (r - 0.03, s1)], B, 14, caps=False)
    prof_o = [(r, s1 - 0.03), (r, hc)] + [(r * math.cos(D(90 * i / k)), hc + r * math.sin(D(90 * i / k)))
                                          for i in range(1, k)] + [(0.0, hl)]
    lathe(mb, c, d, prof_o, AM, 14, caps=False)
    # botao azul em cima da metade laranja
    bp = c + d * (0.5 * (s1 + hc)) + V(0, 0, r - 0.06)
    lathe(mb, bp, (0, 0, 1), [(0.0, 0.0), (0.34, 0.0), (0.34, 0.16), (0.27, 0.26), (0.0, 0.28)], B, 12)
    col_box(A, (2 * hl - 0.3, 2.0, 2.2), (cx, cy, z1 + 1.1), (0, 0, yaw))


def ball_stand(mb, px, z1):
    """expositor baixo (estadio branco sobre faixa azul) com as esferas de 1, 2 e 3 estrelas em tacas de latao;
    as estrelas abrem em leque (da diagonal esquerda a direita): aparecem de frente e nas vistas 3/4"""
    cx, cy = px + 8.0, 103.8          # r4: +6.8 (encostava no braco direito do berco na vista frontal)
    yaw = D(-15)
    ca, sa = math.cos(yaw), math.sin(yaw)

    def P(dx, dy):
        return (cx + dx * ca - dy * sa, cy + dx * sa + dy * ca)
    loc = [P(x, y) for x, y in rrect(0, 0, 3.1, 1.15, 1.15, 4)]
    h = 1.25
    mb.prism(loc, z1 - 0.1, z1 + h - 0.3, B, bevel=0.0)
    mb.prism(offset_poly(loc, 0.1), z1 + h - 0.34, z1 + h, W, bevel=0.18, seg=1)
    rb = 1.0
    for i, (dx, fa) in enumerate(((-2.0, -128.0), (0.0, -105.0), (2.0, -82.0))):
        x, y = P(dx, 0.0)
        lathe(mb, V(x, y, z1 + h - 0.05), (0, 0, 1), [(0.0, 0.0), (0.48, 0.0), (0.68, 0.28), (0.53, 0.34)], G, 10)
        cbl = V(x, y, z1 + h + 0.18 + rb)
        sphere(mb, cbl, rb, BALL, 12, 8)
        ball_stars(mb, cbl, rb, i + 1, 0.3, facing=(math.cos(D(fa)), math.sin(D(fa)), 0.2), spread=0.6, off=0.035)
    # colisao coerente: uma caixa com a pegada da fileira das esferas e o topo no topo delas (z1 + 3.43)
    col_box(A, (6.0, 2.0, h + 2.28), (cx, cy, z1 + 0.5 * (h + 2.28) - 0.05), (0, 0, yaw))


def _strip_swirl_extras(mb, n0):
    """FP.swirl poe no objeto do portal um aro de brilho (P_DB_Glow, 32 lados) e a tampa traseira (K.cup): os dois
    saem - o anel aceso de NSEG lados ja cobre a borda da espiral e a calota ja fecha as costas (a tampa furava a
    calota num degrau concentrico). O slot do aro vira o anel aceso (sem material vazio no objeto)."""
    mb.bm.faces.ensure_lookup_table()
    fs = list(mb.bm.faces[n0:])
    bmesh.ops.delete(mb.bm, geom=fs, context="FACES")
    if "P_DB_Glow" in mb.mats:
        mb.mats[mb.mats.index("P_DB_Glow")] = RIM
    return len(fs)


# ------------------------------------------------------------------ portal
def build(rng):
    px = L.PORTAL_X[1]
    mb = K.LeanMB("PORTAL_DragonBall_Frame", C, rng, vcap=2)
    log = []

    def step(name, fn, *a):
        t0 = _tris(mb)
        r = fn(*a)
        log.append((name, _tris(mb) - t0))
        return r
    z1, z2 = step("plataforma", platform, mb, px)
    step("aro", frame, mb, px)
    step("coroa", crown, mb, px)
    step("berco", cradle, mb, px, z2)
    step("capsula", capsule_prop, mb, px, z1)
    step("expositor", ball_stand, mb, px, z1)
    ring_cols(px, z2)
    n0 = len(mb.bm.faces)
    FP.swirl(KEY, px, "P_DB_Swirl", mb, AM, -0.7)
    nx = _strip_swirl_extras(mb, n0)
    if DEBUG:
        print("TRIS por parte:", ", ".join("%s=%d" % x for x in log), "total", _tris(mb), "| extras FP removidos:", nx)
    mb.finish()
    _swirl_preview()


def _swirl_preview():
    """previa da espiral no Blender = como o Roblox mostra a PNG (sem luz): so emissao da textura, sem difuso nem
    especular (com difuso + sol a espiral ganha a sombra do aro). Nao afeta o export (export_roblox monta o
    material RBX_SWIRL_* direto da PNG)."""
    import bpy
    m = bpy.data.materials.get("P_DB_Swirl")
    if m is None or not m.use_nodes:
        return
    nt = m.node_tree
    bs = next((n for n in nt.nodes if n.type == "BSDF_PRINCIPLED"), None)
    if bs is None:
        return
    for l in list(bs.inputs["Base Color"].links):
        nt.links.remove(l)
    bs.inputs["Base Color"].default_value = (0.0, 0.0, 0.0, 1.0)
    bs.inputs["Emission Strength"].default_value = 1.5
    if "Specular IOR Level" in bs.inputs:
        bs.inputs["Specular IOR Level"].default_value = 0.0


# ------------------------------------------------------------------ dressing da escada (lance 2): AS SETE ESFERAS
# "Cada escada anuncia o seu mundo": o portal ja mostra a esfera de 4 (coroa) e as de 1-2-3 (expositor); a escada
# COMPLETA AS SETE - as esferas de 5, 6 e 7 estrelas sobem ao lado do lance 2 em pedestais Capsule Corp (fuste
# branco conico, colar azul e taca de ouro de labio plano - o mesmo par azul + ouro da boca do berco), em zigue-zague
# (esq., dir., esq.) e cada uma mais alta que a anterior. Mesmo acabamento das esferas do expositor: ambar liso
# (P_DB_Ball_Amber), estrelas vermelhas coladas que seguem a curvatura (sphere_decal). So o motivo das esferas: nada
# mais na faixa (receita do One Piece).
# Duas esferas ficam na esquerda (a unica faixa que a praca enxerga: a direita some atras dos pilares do muro).
# Alturas: a 5 baixa como o expositor (topo T+3.5), a 6 no meio (T+5.8), a 7 e o unico acento vertical (T+8.0):
# do ledge (H_Stairs) a 7 aparece INTEIRA acima da 5 e da praca le a subida 5 -> 7.
# Orcamento: 1196 tris (as 18 estrelas sao 540), 5 materiais da paleta, 3 colisoes.
ST_R = 1.25                          # raio das esferas (expositor: 1.0; aqui ficam mais longe do pad)
ST_N, ST_NP = 12, 10                 # lados da esfera (= expositor) e do pedestal
# (lado, |x - px| do eixo, y, z do labio da taca de ouro acima de T, estrelas). Faixa: 7.8 <= |x - px| <= 13.9
# (poco < 7.7). A 5 fica rente ao poco (mais para fora some atras do pilar do muro no H_Stairs); a 7 abre para
# fora: no A_Hero fica com ar ate a capsula deitada atras dela.
ST_BALLS = ((-1, 9.9, 88.6, 1.26, 5), (1, 9.9, 92.9, 3.51, 6), (-1, 11.3, 97.2, 5.76, 7))
ST_FACE = (0.48, -0.86, -0.16)       # estrelas olham para a escada e para a praca, um pouco para baixo (x com o lado)
# taca de ouro (como as tacas de latao do expositor): cone que abre do raio rc ate a borda externa ro, e um LABIO
# PLANO que volta ate ri. O plano horizontal do labio corta a esfera (lathe de aneis horizontais) num poligono limpo,
# sem serrilhado; a borda externa fica FORA da esfera e o topo do labio pega luz.
ST_CUP = (0.86, 0.45, 1.15, 0.62)    # (rc, altura do cone, ro, ri)
ST_SEAT = 1.0                        # centro da esfera acima do labio: a esfera cruza o labio em r ~0.70 (entre ri e
#                                      ro) e a estrela mais baixa (a da 7) fica 0.11 acima do labio
ST_BAND = 0.38                       # colar azul (logo abaixo da taca)
ST_STRIPE = (2.3, 0.12)              # friso azul no fuste alto (da 7): meio acima da base, meia altura - quebra a
#                                      leitura de poste da praca (G_Far) com a listra do berco
ST_COL = 2.5                         # pegada da colisao = diametro da esfera (o pe tem 2.4)
ST_LAT = (30.0, 55.0, 80.0, 105.0, 130.0, 155.0)   # latitudes da esfera (graus desde o polo de baixo); o que fica
#                                                    abaixo de 30 esta dentro do colar (sem faces escondidas)


def _st_center(hr):
    """centro da esfera: assentada na taca de ouro (labio em z = T + hr)"""
    return T + hr + ST_SEAT


def _st_layout(k):
    """posicoes das estrelas no plano tangente (unidades de 'spread'): 5 = pentagono, 6 = pentagono + centro,
    7 = hexagono + centro"""
    if k == 5:
        return [(math.cos(D(90 + 72 * i)), math.sin(D(90 + 72 * i))) for i in range(5)]
    if k == 6:
        return [(0.0, 0.0)] + [(math.cos(D(90 + 72 * i)), math.sin(D(90 + 72 * i))) for i in range(5)]
    return [(0.0, 0.0)] + [(math.cos(D(90 + 60 * i)), math.sin(D(90 + 60 * i))) for i in range(6)]


def _st_stars(mb, c, r, k, facing):
    """as k estrelas (5..7) coladas na esfera, como ball_stars (mesmo decal, mesma orientacao 'ponta para cima')"""
    size, spread = {5: (0.27, 0.52), 6: (0.25, 0.56), 7: (0.23, 0.55)}[k]
    n, side, u = _frame_on(Vector(facing).normalized())
    for a, b in _st_layout(k):
        d = _on_sphere(Vector((0, 0, 0)), r, n, side, u, a * spread, b * spread, 0.0).normalized()
        sphere_decal(mb, c, r, d, star2d(size), ST, off=0.04, depth=min(0.12, r * 0.1))


def _st_pedestal(mb, x, y, hr):
    """pedestal Capsule Corp: fuste branco conico (largo no terraco), colar azul e taca de ouro com labio plano
    (tubos abertos empilhados, anel com anel: o fundo fica no terraco e o labio corta a esfera)"""
    base = V(x, y, T - 0.15)
    rc, hc, ro, ri = ST_CUP
    zt = hr + 0.15                                   # labio da taca (relativo a base)
    zb = zt - hc - ST_BAND
    rs = rc - 0.04                                   # raio do fuste no topo
    lathe(mb, base, (0, 0, 1), [(1.2, 0.0), (rs, zb)], W, ST_NP, caps=False)
    lathe(mb, base, (0, 0, 1), [(rs, zb), (rc, zt - hc)], B, ST_NP, caps=False)
    lathe(mb, base, (0, 0, 1), [(rc, zt - hc), (ro, zt), (ri, zt)], G, ST_NP, caps=False)
    if zb > 4.0:
        # friso azul so no fuste alto: tubo 0.025 para fora do cone branco
        zm, hh = ST_STRIPE
        prof = [(1.2 + (rs - 1.2) * z / zb + 0.025, z) for z in (zm - hh, zm + hh)]
        lathe(mb, base, (0, 0, 1), prof, B, ST_NP, caps=False)


def _st_ball(mb, c, r):
    """esfera lisa sem a calota de baixo (fica dentro da taca de ouro): 12 lados como a esfera do expositor"""
    prof = [(r * math.sin(D(t)), -r * math.cos(D(t))) for t in ST_LAT] + [(0.0, r)]
    lathe(mb, c, (0, 0, 1), prof, BALL, ST_N, caps=False)


def stairs(mb, px, rng):
    """dressing da faixa ao lado do lance 2 (terraco z = T, y 86..99.4, 7.8 <= |x - px| <= 13.9): as esferas de 5,
    6 e 7 estrelas em pedestais que sobem com a escada"""
    fx, fy, fz = ST_FACE
    for s, dx, y, hr, k in ST_BALLS:
        x = px + s * dx
        _st_pedestal(mb, x, y, hr)
        c = V(x, y, _st_center(hr))
        _st_ball(mb, c, ST_R)
        _st_stars(mb, c, ST_R, k, (-s * fx, fy, fz))
        top = c.z + ST_R - T
        col_box(A, (ST_COL, ST_COL, top), (x, y, T + 0.5 * top))
