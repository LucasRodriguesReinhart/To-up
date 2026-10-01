# fm_pv3_naruto - PORTAL NARUTO v3 "BANDANA DA FOLHA" (passe final)
# Um objeto iconico: a BANDANA NINJA gigante amarrada em dois postes laqueados; a placa de aco com a folha de
# Konoha GRAVADA (espiral + ponta + talo) pousa na aduela-chave de um ANEL DE PEDRA quente (arenito ocre) com
# filete de ferro no extradorso, que emoldura a espiral e recorta a silhueta contra o penhasco cinza
# (atravessavel: e a passagem para Konoha, o corredor comeca atras do portal). Em cada poste a faixa da uma volta
# (colar), fecha num no de pano liso curvado contra o colar, com cintura, e solta duas caudas finas em rabo de
# andorinha. Props: kunai gigante cravado (esq.), pergaminhos ao pe do poste direito (um desenrolado), moitas baixas
# lisas atras dos pes dos postes; piso de lajes com medalhao da folha no alto da escada, no eixo da passagem.
# Paleta: laca carmim, azul-marinho (pano), arenito ocre; acento aco; espiral laranja viva com nucleo creme.
# Espiral: textura propria (T_swirl_naruto_v5.png, gerada aqui como o fm_pv3_dragonball faz): fundo laranja vivo
# que aprofunda para laranja-avermelhado na borda (nunca marrom), 3 bracos amarelo-laranja com filete creme, o traco
# da espiral de Konoha no centro e nucleo amarelo-creme. A MESMA PNG vai para o Blender e para o export.
import math
import os
import bmesh
import numpy as np
import fm_lib
from fm_lib import D, S, col_box, col_box2
import fm_portal_kit as K
from fm_portal_kit import V
import fm_layout as L
import fm_mat_textures as TX

DEBUG = bool(os.environ.get("FM_PV3_DEBUG"))

_M = fm_lib.MATS.setdefault
_M("P_Naruto_Cloth", ((0.014, 0.032, 0.14), 0.85, 0.0, 0, None, 0.05))     # azul-marinho da bandana
_M("P_Naruto_Paper", ((0.66, 0.50, 0.28), 0.9, 0.0, 0, None, 0.04))       # papel de pergaminho
_M("P_Naruto_Steel", ((0.62, 0.66, 0.72), 0.30, 0.70, 0, None, 0.02))     # placa de aco polido
_M("P_Naruto_Lacquer", ((0.34, 0.02, 0.03), 0.42, 0.0, 0, None, 0.05))    # laca carmim (so do portal)
_M("P_Naruto_Stone", (S(190, 136, 86), 0.85, 0.0, 0, None, 0.05))        # arenito ocre do anel (quente)
# aro de brilho da espiral: laranja saturado com emissao contida (o P_Naruto_Glow compartilhado estoura em salmao)
_M("P_Naruto_Rim_Glow", (S(255, 100, 12), 0.4, 0.0, 0.7, S(255, 92, 10), 0.0))


# ------------------------------------------------------------------ espiral propria (textura v5)
def _ss(a, b, x):
    t = np.clip((x - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)


def _mix(a, b, t):
    t = np.asarray(t)[..., None]
    return a * (1 - t) + b * t


def naruto_swirl_tex(spec, n=None):
    """espiral do Naruto (chakra laranja): fundo laranja vivo que aprofunda para laranja-avermelhado na borda,
    vales entre os bracos em laranja-avermelhado saturado (nada de marrom), 3 bracos amarelo-laranja com filete creme
    na borda de ataque, o traco da espiral de Konoha saindo do nucleo (mesmo sentido dos bracos) e nucleo pequeno
    amarelo-creme com halo amarelo. Aro claro na borda. Alfa 0 fora do circulo."""
    n = n or TX.SWIRL_N
    c = (np.arange(n) + 0.5) / n * 2 - 1
    X, Y = np.meshgrid(c, -c)                     # linha 0 = topo (mesma convencao de fm_mat_textures)
    r = np.sqrt(X * X + Y * Y)
    th = np.arctan2(Y, X)

    def col(v):
        return np.array(v, float) / 255.0
    BG_OUT, BG_MID, BG_IN, DEEP = col(spec["border"]), col(spec["bg_mid"]), col(spec["bg_in"]), col(spec["deep"])
    ARM, ARM_HI, LEAF = col(spec["arm"]), col(spec["arm_hi"]), col(spec["leaf"])
    CORE, HALO, RIMC = col(spec["core"]), col(spec["halo"]), col(spec["rim"])
    rgb = _mix(_mix(np.broadcast_to(BG_IN, r.shape + (3,)), BG_MID, _ss(0.08, 0.50, r)), BG_OUT, _ss(0.50, 0.97, r))
    ph = spec["arms"] * th / (2 * math.pi) + spec["twist"] * r ** 0.9
    s = ph % 1.0 - 0.5
    wl = spec["width"] * (0.5 + 0.6 * np.clip(r, 0, 1))
    lead = np.exp(-(np.maximum(s, 0) / (wl * 0.26)) ** 2)
    trail = np.exp(-(np.maximum(-s, 0) / (wl * 0.90)) ** 2)
    env = _ss(0.06, 0.22, r) * (1 - _ss(0.86, 0.975, r))
    arm = np.where(s >= 0, lead, trail) * env
    rgb = _mix(rgb, DEEP, np.clip((1 - arm) * env * spec["trough"], 0, 1))      # vales: vermelho-alaranjado vivo
    rgb = _mix(rgb, ARM, np.clip(arm, 0, 1))
    line = np.exp(-((s - wl * 0.02) / (wl * 0.11)) ** 2) * env
    rgb = _mix(rgb, ARM_HI, np.clip(line * spec["line"], 0, 1))
    # traco da espiral de Konoha: sai do nucleo e da ~1,5 volta no MESMO sentido dos bracos (encaixa neles)
    phi = (-th + 0.9) % (2 * math.pi)
    best = np.full_like(r, 9.0)
    for k in range(3):
        a = phi + 2 * math.pi * k
        rr = 0.05 * a
        ok = a <= 1.5 * 2 * math.pi
        best = np.minimum(best, np.where(ok, np.abs(r - rr), 9.0))
    thick = 0.020 * (1 - np.clip(r / 0.50, 0, 1)) + 0.008
    m = np.exp(-(best / thick) ** 2) * (1 - _ss(0.40, 0.49, r))
    rgb = _mix(rgb, LEAF, np.clip(m, 0, 1))
    rgb = _mix(rgb, HALO, np.exp(-(r / spec["halo_r"]) ** 2) * 0.70)
    rgb = _mix(rgb, CORE, np.exp(-(r / spec["core_r"]) ** 3))
    # aro: linha clara + brilho para dentro
    rim = np.exp(-((r - 0.955) / 0.024) ** 2)
    glow = np.exp(-((r - 0.955) / 0.075) ** 2) * 0.45 * (r < 0.955)
    rgb = _mix(rgb, _mix(ARM, RIMC, 0.5), np.clip(glow, 0, 1))
    rgb = _mix(rgb, RIMC, np.clip(rim * 1.15, 0, 1))
    rgb = np.where((r > 0.955)[..., None], _mix(rgb, np.broadcast_to(RIMC, rgb.shape), 0.85), rgb)
    alpha = (1 - _ss(0.985, 1.0, r))[..., None]
    return np.concatenate([np.clip(rgb, 0, 1), alpha], axis=2)


# chakra laranja: cores saturadas (nada pastel); a luminancia dos bracos fica abaixo do creme do nucleo
SWIRL_NARUTO = dict(border=(172, 34, 0), bg_mid=(228, 72, 0), bg_in=(252, 122, 10), deep=(186, 38, 0),
                    arm=(255, 150, 14), arm_hi=(255, 212, 100), leaf=(255, 228, 140), core=(255, 244, 200),
                    halo=(255, 200, 70), rim=(255, 214, 120), arms=3, twist=3.4, width=0.30, trough=0.6,
                    line=0.8, halo_r=0.19, core_r=0.085, style="naruto_v5")
SWIRL_FILE = "T_swirl_naruto_v5.png"


def _patch_swirl():
    """registra o desenho novo do Naruto em fm_mat_textures (so em memoria): SWIRL_SPEC/SWIRL_TEX apontam para a v5 e
    tex_swirl despacha o estilo 'naruto_v5' para naruto_swirl_tex (encadeia com outros patches, ex. o do DB).
    Nome novo (v5): o 3D Importer nao reaproveita o cache da v4."""
    spec = dict(TX.SWIRL_SPEC["P_Naruto_Swirl"])
    spec.update(SWIRL_NARUTO)
    TX.SWIRL_SPEC["P_Naruto_Swirl"] = spec
    TX.SWIRL_TEX["P_Naruto_Swirl"] = (SWIRL_FILE, spec["arm"], spec["core"])
    if not getattr(TX.tex_swirl, "_naruto_v5", False):
        orig = TX.tex_swirl

        def tex_swirl(sp, n=None):
            return naruto_swirl_tex(sp, n) if sp.get("style") == "naruto_v5" else orig(sp, n)
        for a in dir(orig):
            if a.startswith("_") and not a.startswith("__"):
                setattr(tex_swirl, a, getattr(orig, a))       # preserva marcas de outros patches (ex.: _db_ki)
        tex_swirl._naruto_v5 = True
        TX.tex_swirl = tex_swirl
    p = os.path.join(TX.TEX_DIR, SWIRL_FILE)
    if not os.path.exists(p):
        os.makedirs(TX.TEX_DIR, exist_ok=True)
        TX.write_png(p, naruto_swirl_tex(spec))


_patch_swirl()


def _swirl_preview():
    """previa da espiral no Blender = como o Roblox mostra a PNG (Neon, sem luz): so emissao da textura, sem difuso
    nem especular (com difuso + sol, os vales ficavam marrons na sombra do anel). Nao afeta o export."""
    import bpy
    m = bpy.data.materials.get("P_Naruto_Swirl")
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


C = "06_PORTALS"
T = L.TERR
PY = L.PORTAL_Y
Y0 = L.FLIGHT2_Y1
SZ = T + 2.0 + 9.2
A = "Portal"

RED, NAVY, SL, SD = "P_Naruto_Lacquer", "P_Naruto_Cloth", "Stone_Light", "Stone_Dark"
STEEL, IRON, PAPER = "P_Naruto_Steel", "Metal_Dark", "P_Naruto_Paper"
RIM, STONE, BUSH = "P_Naruto_Rim_Glow", "P_Naruto_Stone", "Leaf_Pine"

FZ = T + 0.4            # topo do piso de lajes (degraus do estrado de 0.95: o corpo passa)
YC = PY + 0.75          # eixo (y) do anel, dos postes e do estrado
RI, RO = 7.75, 9.4      # anel de pedra (raio interno / externo); + aro de ferro ate RO + FIL
RD = 1.75               # meia-profundidade do anel
PXP = 11.8              # postes em px +- PXP
SILL = SZ - RI          # topo da soleira = fundo interno do anel (T+3.45): o pe nao entra na pedra ao atravessar

# bandana: a placa (9 x 4.5) fica centrada na faixa, no meio do vao; a aduela-chave sobe 1.0 por tras da placa
PLATE_W, PLATE_H, PLATE_T = 9.0, 4.5, 0.6
SAG = 1.1               # barriga da faixa (z) no meio
BOW = 1.1               # arco da faixa para a frente (y) no meio
BH = 1.6                # meia-altura da faixa
BT = 0.36               # espessura da faixa
KTOP = T + 22.35        # topo da aduela-chave (atras da placa)
ZC_PLATE = KTOP - 1.0 + PLATE_H / 2     # placa cobre 1.0 do topo da chave
ZB = ZC_PLATE + SAG     # cota da faixa nos postes
Y_MID = PY - 1.34       # centro (y) da faixa no meio: verso encosta 0.24 na frente da chave
KEY_HD = 2.15           # meia-profundidade da chave (frente em PY-1.40)
PLATE_YB = PY - 1.33    # verso da placa (embutida na faixa: 0.2 no meio, 0.03 nas bordas)

P_Z0, P_Z1 = FZ + 1.2, ZB + 2.6


POST_R0, POST_R1 = 1.2, 1.0     # raio do fuste na base / no topo (mais esguio que a r2: area frontal na regra)


def post_r(z):
    return POST_R0 + (POST_R1 - POST_R0) * (z - P_Z0) / (P_Z1 - P_Z0)


# ------------------------------------------------------------------ simbolo da Folha (espiral + ponta)
def leaf_strokes(turns=2.0, r_in=0.10, cx=0.22, cz=-0.10, tip=(-1.45, 1.25), join_a=200.0, res=18, stem=0.5,
                 sd=(-0.8, -0.6)):
    """linhas-guia (u, v) do simbolo, raio externo da espiral = 1: espiral anti-horaria do centro ate o topo,
    tangente reta ate a ponta da folha; 2o traco da ponta de volta a volta externa (esquerda-baixo) e o talo curto
    que sai dessa juncao para baixo-esquerda (como no simbolo de Konoha)"""
    th_end = math.pi / 2 + 4 * math.pi
    th0 = th_end - turns * 2 * math.pi
    n = int(turns * res)
    sp = []
    for i in range(n + 1):
        f = i / n
        th = th0 + (th_end - th0) * f
        r = r_in + (1.0 - r_in) * f
        sp.append((cx + math.cos(th) * r, cz + math.sin(th) * r))
    tipp = (cx + tip[0], cz + tip[1])
    a = math.radians(join_a)
    th_j = th_end - ((math.pi / 2 - a) % (2 * math.pi))
    rj = r_in + (1 - r_in) * (th_j - th0) / (th_end - th0)
    jp = (cx + math.cos(th_j) * rj, cz + math.sin(th_j) * rj)
    ln = math.hypot(*sd)
    se = (jp[0] + sd[0] / ln * stem, jp[1] + sd[1] / ln * stem)
    return sp, tipp, jp, se


def leaf_symbol(mb, origin, u, v, s, m, w=0.2, h=0.07, res=18):
    """simbolo em relevo: tracos de largura w*s, altura h, no plano (u, v) a partir de origin (normal u x v)"""
    o, u, v = V(*origin), V(*u).normalized(), V(*v).normalized()
    nrm = u.cross(v).normalized()
    sp, tipp, jp, se = leaf_strokes(res=res)

    def P(q):
        return o + u * (q[0] * s) + v * (q[1] * s)
    ww = w * s
    prof = [(0.0, -ww / 2), (h, -ww / 2), (h, ww / 2), (0.0, ww / 2)]
    tp = V(tipp[0], tipp[1], 0)
    t1 = V(sp[-1][0], sp[-1][1], 0)
    jv = V(jp[0], jp[1], 0)
    d1 = (t1 - tp).normalized()
    d2 = (jv - tp).normalized()
    lt = 0.42     # trecho de cada traco coberto pelo canto mitrado (unidades do simbolo)
    s1 = [P(q) for q in sp] + [P((tp + d1 * (lt * 0.8)).xy)]
    s2 = [P((tp + d2 * (lt * 0.8)).xy), P((jv + d2 * (w * 0.35)).xy)]
    ds = (V(se[0], se[1], 0) - jv).normalized()
    s3 = [P((jv - ds * (w * 0.3)).xy), P(se)]          # talo: nasce dentro do traco 2 e sai para baixo-esquerda
    K.loft(mb, s1, [prof] * len(s1), m, True, up=tuple(nrm))
    K.loft(mb, s2, [prof] * len(s2), m, True, up=tuple(nrm))
    K.loft(mb, s3, [prof] * len(s3), m, True, up=tuple(nrm))
    # canto da ponta mitrado (2 quadrilateros convexos)
    half = math.acos(max(-1.0, min(1.0, d1.dot(d2)))) / 2
    bis = -(d1 + d2).normalized()
    mo = tp + bis * (w / 2) / max(0.2, math.sin(half))
    mi = tp - bis * (w / 2) / max(0.2, math.sin(half))

    def perp_out(d, other):
        p = V(-d.y, d.x, 0)
        return p if p.dot(other) < 0 else -p
    o1, o2 = perp_out(d1, d2), perp_out(d2, d1)
    p1o, p1i = tp + d1 * lt + o1 * (w / 2), tp + d1 * lt - o1 * (w / 2)
    p2o, p2i = tp + d2 * lt + o2 * (w / 2), tp + d2 * lt - o2 * (w / 2)
    orig = o + nrm * (h / 2)
    for quad in ([mo, p1o, p1i, mi], [mo, mi, p2i, p2o]):
        pts = [(q.x * s, q.y * s) for q in quad]
        ar = sum(pts[i][0] * pts[(i + 1) % 4][1] - pts[(i + 1) % 4][0] * pts[i][1] for i in range(4))
        if ar < 0:
            pts.reverse()
        K.plate(mb, pts, orig, u, v, h, m)


# ------------------------------------------------------------------ utilidades
def rounded_rect(w, h, r, n=5):
    pts = []
    for cx, cy, a0 in ((w / 2 - r, -h / 2 + r, -90), (w / 2 - r, h / 2 - r, 0), (-w / 2 + r, h / 2 - r, 90),
                       (-w / 2 + r, -h / 2 + r, 180)):
        for i in range(n + 1):
            a = D(a0 + 90.0 * i / n)
            pts.append((cx + math.cos(a) * r, cy + math.sin(a) * r))
    return pts


def smooth01(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)


def paint(mb, faces, m, tint=None):
    """material/tinta/UV num conjunto de faces ja criadas no bmesh do MB (mesma logica do MB._post, sem chanfro)"""
    faces = [f for f in faces if f.is_valid]
    if not faces:
        return
    mi = mb._mi_for(m)
    t = mb.rng.uniform(-1, 1) if tint is None else tint
    for f in faces:
        f.material_index = mi
        f[mb.tint] = t
        f.smooth = False
        f.normal_update()
    mb._uv(set(faces), m)


# ------------------------------------------------------------------ pecas
def post(mb, x, y):
    """poste laqueado: sapata de pedra, colarinho preto, fuste levemente conico (18 lados, lateral com sombreamento
    suave: laca lisa, sem listras de facetas), anel fino preto no terco de cima do fuste, colar e capitel pretos"""
    mb.box((3.0, 3.0, 1.2), (x, y, FZ + 0.6), (0, 0, 0), SD, 0.2)
    res = bmesh.ops.create_cone(mb.bm, cap_ends=True, cap_tris=False, segments=18, radius1=POST_R0, radius2=POST_R1,
                                depth=P_Z1 - P_Z0, matrix=fm_lib.Matrix.Translation((x, y, (P_Z0 + P_Z1) / 2)))
    for f in mb._post(res["verts"], RED, None, 0.08, 1, angle=0.5):
        if abs(f.normal.z) < 0.3:
            f.smooth = True
    zr = SZ + 4.6       # anel fino: acima do ponto em que o anel de pedra chega mais perto do poste
    res = bmesh.ops.create_cone(mb.bm, cap_ends=True, cap_tris=False, segments=18, radius1=post_r(zr) + 0.12,
                                radius2=post_r(zr) + 0.12, depth=0.55, matrix=fm_lib.Matrix.Translation((x, y, zr)))
    for f in mb._post(res["verts"], IRON, None, 0, 1):
        f.smooth = abs(f.normal.z) < 0.3
    mb.cyl(POST_R0 + 0.22, 1.3, (x, y, P_Z0 + 0.65), (0, 0, 0), IRON, 12, bevel=0.1)
    mb.cyl(POST_R1 + 0.2, 0.6, (x, y, P_Z1 - 0.3), (0, 0, 0), IRON, 12, bevel=0.06)
    mb.cyl(POST_R1 + 0.34, 0.9, (x, y, P_Z1 + 0.45), (0, 0, 0), IRON, 12, r2=POST_R1 - 0.16, bevel=0.1)


FIL = 0.34              # filete de ferro no extradorso (quanto passa do raio externo das aduelas)
HOOP_HD = 0.55          # meia-largura (em y) do aro de ferro


def stone_ring(mb, px):
    """anel de aduelas de ARENITO OCRE (quente: separa do penhasco cinza) com juntas escuras sobre um nucleo de ferro
    (recuado 0.3 da face) e um ARO DE FERRO estreito no meio do extradorso que sai FIL alem da pedra: de frente e o
    filete escuro que recorta a silhueta contra o penhasco; de lado, uma cinta de 1.1. Aduela-chave em cunha estreita,
    da mesma pedra, sobe por tras da placa da bandana (a placa pousa nela, cobrindo 1.0 do topo). No perfil da
    varredura (up=+Y) o 1o eixo aponta para DENTRO do anel."""
    rm = (RI + RO) / 2
    hr = (RO - RI) / 2
    c = 0.22
    prof = [(-hr, -RD + c), (-hr + c, -RD), (hr - c, -RD), (hr, -RD + c), (hr, RD - c), (hr - c, RD), (-hr + c, RD),
            (-hr, RD - c)]
    ka = 6.8            # meia-abertura da chave (graus): ~30% mais estreita que a r2
    n = 11
    gap = 1.2
    span = (360.0 - 2 * ka) / n
    for i in range(n):
        a0 = 90.0 + ka + span * i + gap / 2
        a1 = a0 + span - gap
        pts = [V(px + math.cos(D(a0 + (a1 - a0) * k / 4)) * rm, YC, SZ + math.sin(D(a0 + (a1 - a0) * k / 4)) * rm)
               for k in range(5)]
        mb.sweep(pts, prof, STONE, True, up=(0, 1, 0))
    core = [V(px + math.cos(D(a)) * rm, YC, SZ + math.sin(D(a)) * rm) for a in range(0, 361, 18)]
    fd = RD - 0.3
    mb.sweep(core, [(-hr + 0.05, -fd), (hr - 0.12, -fd), (hr - 0.12, fd), (-hr + 0.05, fd)], IRON, True, up=(0, 1, 0))
    # aro de ferro (filete) no meio do extradorso: de frente e o contorno escuro; de lado, uma cinta estreita
    hoop = [V(px + math.cos(D(a)) * RO, YC, SZ + math.sin(D(a)) * RO) for a in range(0, 361, 12)]
    mb.sweep(hoop, [(-FIL, -HOOP_HD), (0.15, -HOOP_HD), (0.15, HOOP_HD), (-FIL, HOOP_HD)], IRON, True, up=(0, 1, 0))
    t = math.tan(D(ka - gap / 2))
    zb = RI + 0.03
    zt = KTOP - SZ
    pts = [(zb * t, zb), (zt * t, zt), (-zt * t, zt), (-zb * t, zb)]
    K.plate(mb, pts, V(px, YC, SZ), (1, 0, 0), (0, 0, 1), KEY_HD * 2, STONE, bevel=0.18)


def ring_cols(px):
    """colisao do anel seguindo o arco (raio medio 8.55, secao 2.0 radial x 3.5): 4 caixas por lado, de -78 a +26
    graus (lado direito) e o espelho no esquerdo. O vao entre anel e poste fica livre (e aberto na malha)."""
    rm, rw = (RI - 0.2 + RO) / 2, RO - (RI - 0.2)
    for s in (-1, 1):
        for a0, a1 in ((-78, -52), (-52, -26), (-26, 0), (0, 26)):
            th = D((a0 + a1) / 2)
            if s < 0:
                th = math.pi - th
            ln = 2 * RO * math.sin(D(a1 - a0) / 2) + 0.2
            c = (px + math.cos(th) * rm, YC, SZ + math.sin(th) * rm)
            col_box(A, (ln, RD * 2, rw), c, (0, math.pi / 2 - th, 0))


def band(mb, px):
    """faixa de pano entre os postes: cede no meio (SAG), arqueia para a frente (BOW), aperta nos postes; 3 dobras
    longitudinais suaves em todo o comprimento, franzido extra perto dos nos e borda de baixo ondulada entre a placa
    e os nos"""
    n, k = 24, 8
    pts, profs = [], []
    span = PXP - 0.3
    for i in range(n + 1):
        uu = -1.0 + 2.0 * i / n
        x = px + uu * span
        y = Y_MID + BOW * uu * uu
        z = ZB - SAG * (1 - uu * uu)
        g = max(0.0, abs(uu) - 0.5) / 0.5              # 0 no meio .. 1 no no
        h = BH * (1.0 - 0.45 * g * g)
        xa = abs(uu) * span
        wv = 0.0
        if PLATE_W / 2 + 0.1 < xa < span - 1.9:
            q = (xa - PLATE_W / 2 - 0.1) / (span - 1.9 - PLATE_W / 2 - 0.1)
            wv = 0.16 * math.sin(q * math.pi * 2.0) * math.sin(q * math.pi)
        front, back = [], []
        for j in range(k + 1):
            f = j / k
            a = -h + 2 * h * f + wv * (1 - f) ** 2
            fold = 0.1 * math.sin(math.pi * (3.0 * f + 0.2 * math.sin(uu * 2.6))) * math.sin(math.pi * f) ** 0.5
            fold += 0.16 * g * math.sin(math.pi * (f * 2.0 + uu * 3.0))       # franzido junto aos nos
            front.append((a, BT / 2 + fold))
            back.append((a, -BT / 2 + fold * 0.7))
        back = [back[0], back[k // 2], back[-1]]          # verso liso (3 pontos): economiza tris
        profs.append(front + list(reversed(back)))
        pts.append(V(x, y, z))
    K.loft(mb, pts, profs, NAVY, True, up=(0, 0, 1))
    for s in (-1, 1):
        x = px + s * PXP
        mb.cyl(post_r(ZB) + 0.3, 2.1, (x, YC, ZB), (0, 0, 0), NAVY, 16, bevel=0.1)


def ribbon(mb, center, wdir, L_, width, t, notch, m, n=12, cols=2):
    """fita de pano (espessura t) ao longo de center(f), f em 0..1; largura width(f) na direcao wdir(f);
    ponta em rabo de andorinha (o meio recua 'notch')"""
    def frame(f):
        e = 1e-3
        a, b = center(max(0.0, f - e)), center(min(1.0, f + e))
        tg = (b - a).normalized()
        w = wdir(f)
        w = (w - tg * w.dot(tg)).normalized()
        return center(f), w, tg.cross(w).normalized()
    bm = mb.bm
    F, B = [], []
    for i in range(n + 1):
        rf, rb = [], []
        for j in range(cols + 1):
            c = -1.0 + 2.0 * j / cols
            f = i / n
            if i == n:
                f = 1.0 - (notch / L_) * (1.0 - abs(c))
            p, w, nn = frame(f)
            q = p + w * (c * width(f) / 2)
            rf.append(bm.verts.new(q + nn * (t / 2)))
            rb.append(bm.verts.new(q - nn * (t / 2)))
        F.append(rf)
        B.append(rb)
    for i in range(n):
        for j in range(cols):
            bm.faces.new((F[i][j], F[i][j + 1], F[i + 1][j + 1], F[i + 1][j]))
            bm.faces.new((B[i][j], B[i + 1][j], B[i + 1][j + 1], B[i][j + 1]))
        for j in (0, cols):
            bm.faces.new((F[i][j], F[i + 1][j], B[i + 1][j], B[i][j]))
    for i in (0, n):
        for j in range(cols):
            bm.faces.new((F[i][j], B[i][j], B[i][j + 1], F[i][j + 1]))
    mb._post([v for r in F + B for v in r], m, None, 0, 1)


KNOT_A = 30.0           # posicao do no no poste: graus da frente (-Y) para fora


def knot_tails(mb, px, s):
    """no de pano achatado contra o poste (elipsoide liso 14x8 + cinta de 0.5 que faz a cintura) na face
    frontal-externa do colar, e duas caudas finas em rabo de andorinha: a curta (8) na frente, caindo para a frente;
    a longa (11) atras, caindo para fora. Mesma fase de onda: nao se cruzam."""
    x = px + s * PXP
    a = D(KNOT_A)
    n0 = V(s * math.sin(a), -math.cos(a), 0)          # normal do no (para fora do poste)
    t0 = V(s * math.cos(a), math.sin(a), 0)           # tangente horizontal ao poste
    rc = post_r(ZB) + 0.3
    rk = rc + 0.22                                    # raio (a partir do eixo do poste) do centro do no
    kc = V(x, YC, ZB) + n0 * rk
    # no: elipsoide liso (tangente 1.3, normal 0.6, vertical 1.0) CURVADO em volta do colar: cada vertice e
    # enrolado no cilindro de raio rk (o no abraca o poste e nao descola nas pontas)
    res = bmesh.ops.create_uvsphere(mb.bm, u_segments=14, v_segments=8, radius=1.0)
    axis = V(x, YC, ZB)
    a_n0 = math.atan2(n0.y, n0.x)
    for vv in res["verts"]:
        lx, ly, lz = vv.co.x * 1.3, vv.co.y * 0.6, vv.co.z * 1.0
        # lx: arco ao longo do colar; ly: para fora (sentido horario: preserva a orientacao das faces)
        phi = a_n0 - lx / rk
        rr = rk + ly
        vv.co = axis + V(math.cos(phi) * rr, math.sin(phi) * rr, lz)
    for f in mb._post(res["verts"], NAVY, None, 0, 1):
        f.smooth = True
    # cintura: cinta de 0.5 abracando o meio do no (plano normal x vertical)
    loop = []
    for i in range(9):
        th = math.tau * i / 8
        loop.append(kc + n0 * (math.cos(th) * 0.66) + V(0, 0, math.sin(th) * 1.05))
    mb.sweep(loop, [(-0.07, -0.25), (0.07, -0.25), (0.07, 0.25), (-0.07, 0.25)], NAVY, True, up=tuple(t0))
    # caudas
    fwd = V(0, -1, 0)
    out = V(s, 0, 0)
    for (ln, lay, toff, drift, tw) in ((8.0, 0.30, -0.18, fwd * 0.8 + out * (-0.25), 0.22),
                                       (11.0, -0.02, 0.18, out * 0.32 + fwd * 0.1, -0.18)):
        top = kc + V(0, 0, -0.4) + n0 * lay + t0 * toff

        def center(f, top=top, ln=ln, drift=drift):
            off = (fwd * 0.75 + out * 0.2) * f + fwd * (0.6 * math.sin(f * math.pi * 1.5) * min(1.0, f * 2.5))
            return top + V(0, 0, -ln * f) + off + drift * (f * f)

        def wdir(f, tw=tw):
            ang = tw * f
            return V(t0.x * math.cos(ang) - t0.y * math.sin(ang), t0.x * math.sin(ang) + t0.y * math.cos(ang), 0)

        def width(f):
            if f < 0.15:
                return 0.72 + (1.0 - 0.72) * smooth01(f / 0.15)
            if f < 0.6:
                return 1.0
            return 1.0 + 0.32 * smooth01((f - 0.6) / 0.4)
        ribbon(mb, center, wdir, ln, width, 0.14, 0.5, NAVY, n=10)


def engraved_plate(mb, px, zc, yb):
    """placa de aco (9 x 4.5 x 0.6, cantos arredondados, chanfro) com a folha GRAVADA de verdade: boolean de
    diferenca com os tracos (w 0.3); o fundo e as paredes do sulco ficam em ferro escuro. Falha -> relevo."""
    import bpy
    yf = yb - PLATE_T
    depth = 0.14
    tp = fm_lib.MB("TMP_NarutoPlate", C)
    K.plate(tp, rounded_rect(PLATE_W, PLATE_H, 0.85, 4), V(px, yb - PLATE_T / 2, zc), (1, 0, 0), (0, 0, 1), PLATE_T,
            STEEL, bevel=0.15)
    ob = tp.finish()
    tc = fm_lib.MB("TMP_NarutoCut", C)
    so = (px - 0.1, yf + depth, zc - 0.05)
    leaf_symbol(tc, so, (1, 0, 0), (0, 0, 1), 1.45, IRON, w=0.3, h=depth + 0.25)
    cut = tc.finish()
    ok = False
    try:
        md = ob.modifiers.new("eng", "BOOLEAN")
        md.operation = "DIFFERENCE"
        md.object = cut
        md.solver = "EXACT"
        md.use_self = True
        bpy.context.view_layer.update()
        dg = bpy.context.evaluated_depsgraph_get()
        ev = ob.evaluated_get(dg)
        me = ev.to_mesh()
        if len(me.polygons) > len(ob.data.polygons) + 20:
            bm = mb.bm
            vs = [bm.verts.new(ob.matrix_world @ v.co) for v in me.vertices]
            plate_f, groove_f = [], []
            for p in me.polygons:
                try:
                    f = bm.faces.new([vs[i] for i in p.vertices])
                except ValueError:
                    continue
                c = p.center
                g = (yf + 0.004 < c.y < yf + depth + 0.004 and abs(c.x - px) < PLATE_W / 2 - 0.4
                     and abs(c.z - zc) < PLATE_H / 2 - 0.35)
                (groove_f if g else plate_f).append(f)
            paint(mb, plate_f, STEEL)
            paint(mb, groove_f, IRON)
            ok = bool(groove_f)
            # lascas degeneradas do boolean (vertice no meio da aresta oposta, area ~0): funde o vertice do meio no
            # vizinho mais proximo (no plano do fundo do sulco): some a lasca e a malha continua fechada
            for f in [f for f in plate_f + groove_f if f.is_valid and f.calc_area() < 1e-6]:
                if not f.is_valid:
                    continue
                vs_ = list(f.verts)
                ang = [l.calc_angle() for l in f.loops]
                b = f.loops[ang.index(max(ang))].vert
                a = min((v for v in vs_ if v is not b), key=lambda v: (v.co - b.co).length)
                try:
                    bmesh.ops.pointmerge(bm, verts=[b, a], merge_co=a.co.copy())
                except Exception as e:
                    print("lasca da gravura:", e)
        ev.to_mesh_clear()
    except Exception as e:
        print("placa gravada falhou:", e)
    for o in (ob, cut):
        me_ = o.data
        bpy.data.objects.remove(o, do_unlink=True)
        bpy.data.meshes.remove(me_)
    if not ok:
        K.plate(mb, rounded_rect(PLATE_W, PLATE_H, 0.85, 4), V(px, yb - PLATE_T / 2, zc), (1, 0, 0), (0, 0, 1),
                PLATE_T, STEEL, bevel=0.15)
        leaf_symbol(mb, (px - 0.1, yf + 0.01, zc - 0.05), (1, 0, 0), (0, 0, 1), 1.45, IRON, w=0.3, h=0.06)
    # 4 rebites (cabeca abaulada)
    for sx in (-1, 1):
        for sz in (-1, 1):
            mb.cyl(0.3, 0.18, (px + sx * 3.8, yf - 0.06, zc + sz * 1.55), (D(90), 0, 0), IRON, 10, r2=0.22, bevel=0.0)
    return ok


def kunai(mb, entry, d, wv, blade=6.0, bury=1.4, handle=3.0):
    """kunai gigante cravado no piso: lamina losango em aco claro com aresta central alta (secao ate 0.9: as duas
    faces de cada lado pegam luz diferente e a lamina le em dois tons), cabo enfaixado de marinho, argola lisa (16)"""
    d, wv = V(*d).normalized(), V(*wv)
    wv = (wv - d * wv.dot(d)).normalized()
    bn = d.cross(wv).normalized()
    tip = V(*entry) - d * bury
    prof_w = [(0.0, 0.08), (0.18, 0.9), (0.42, 1.55), (0.66, 2.0), (0.84, 1.55), (0.95, 0.85), (1.0, 0.7)]
    pts, profs = [], []
    for f, w in prof_w:
        pts.append(tip + d * (blade * f))
        t = 0.16 + 0.74 * min(1.0, w / 2.0)
        profs.append([(w / 2, 0.0), (0.0, t / 2), (-w / 2, 0.0), (0.0, -t / 2)])
    K.loft(mb, pts, profs, STEEL, True, up=tuple(wv))
    g = tip + d * blade
    mb.rod(g - d * 0.1, g + d * handle, 0.36, IRON, 10)
    for k in range(4):
        a = g + d * (0.25 + k * 0.7)
        mb.rod(a, a + d * 0.58, 0.47, NAVY, 10)
    e = g + d * (handle + 0.85)
    K.ring(mb, e, 0.85, d, wv, 0.3, 0.3, IRON, n=16)


def scroll(mb, c, ax, ln, r, n=14):
    """pergaminho enrolado: papel; na tampa um disco interno laqueado (miolo) e pino redondo curto"""
    a, b = c - ax * (ln / 2), c + ax * (ln / 2)
    mb.rod(a, b, r, PAPER, n)
    for e, sg in ((a, -1), (b, 1)):
        mb.rod(e - ax * (sg * 0.03), e + ax * (sg * 0.09), r * 0.6, RED, 10)
        K.cone(mb, e + ax * (sg * 0.09), e + ax * (sg * 0.42), r * 0.3, r * 0.2, RED, 8)


def scrolls(mb, base, yaw, ln=4.8, r=0.8):
    """2 rolos no piso (o da frente desenrolando uma aba de papel no chao) e 1 cruzado por cima (35 graus),
    apoiado nos dois (eixo a 3r do piso)"""
    ax = V(math.cos(yaw), math.sin(yaw), 0)
    side = V(-ax.y, ax.x, 0)
    b = V(*base)
    d = r * 1.02
    c0 = b - side * d + V(0, 0, r)
    c1 = b + side * d + V(0, 0, r) + ax * 0.35
    scroll(mb, c0, ax, ln, r)
    scroll(mb, c1, ax, ln, r)
    a2 = yaw + D(35)
    ax2 = V(math.cos(a2), math.sin(a2), 0)
    scroll(mb, b + V(0, 0, 3 * r) + ax * 0.15, ax2, ln * 0.92, r)
    # aba desenrolada: sai de baixo do rolo da frente e se estende no piso, com a ponta levemente enrolada
    w = ln - 0.5
    o = c0 - V(0, 0, r)             # linha de contato do rolo da frente com o piso (FZ)
    lift = V(0, 0, 0.07)            # folha de 0.06: 0.04 acima das lajes (nada coplanar)
    path = [o + lift] + [o - side * q + lift for q in (0.6, 1.3, 2.0, 2.5)]
    path += [o - side * 2.85 + lift + V(0, 0, 0.1), o - side * 3.05 + lift + V(0, 0, 0.32),
             o - side * 3.1 + lift + V(0, 0, 0.55)]
    K.loft(mb, path, [[(-0.03, -w / 2), (0.03, -w / 2), (0.03, w / 2), (-0.03, w / 2)]] * len(path), PAPER, True,
           up=(0, 0, 1))
    return b, ax, side


def dome(mb, c, rx, ry, rz, m, n=10, lats=(62, 30, 0, -28)):
    """calota lisa (esferoide cortado abaixo do equador, fundo plano enterrado): polo + aneis nas latitudes dadas;
    sombreamento suave (le como moita arredondada, nunca como cristal)"""
    bm = mb.bm
    c = V(*c)
    top = bm.verts.new(c + V(0, 0, rz))
    rings = []
    for la in lats:
        cl, sl = math.cos(D(la)), math.sin(D(la))
        rings.append([bm.verts.new(c + V(math.cos(math.tau * i / n) * rx * cl, math.sin(math.tau * i / n) * ry * cl,
                                         sl * rz)) for i in range(n)])
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((top, rings[0][i], rings[0][j]))
    for r0, r1 in zip(rings, rings[1:]):
        for i in range(n):
            j = (i + 1) % n
            bm.faces.new((r0[i], r1[i], r1[j], r0[j]))
    bm.faces.new(list(reversed(rings[-1])))          # fundo (enterrado): malha fechada
    for f in mb._post([top] + [v for r in rings for v in r], m, None, 0, 1):
        f.smooth = f.normal.z > -0.9


def bush(mb, base, lumps):
    """moita baixa: 2-3 calotas lisas verde-escuras sobrepostas; base = (x, y) do centro; lumps = (dx, dy, rx, ry, rz)
    (centro das calotas 0.25 abaixo do piso: a borda enterra nas lajes e na grama)"""
    for dx, dy, rx, ry, rz in lumps:
        dome(mb, (base[0] + dx, base[1] + dy, FZ - 0.25), rx, ry, rz, BUSH)


def paving(mb, x0, x1, y0, y1, z, rng, skip, depth=3.1, gap=0.16, h=0.34):
    mb.box2((x0, y0, z - 0.9), (x1, y1, z - 0.1), SD, 0.0)
    y = y0
    row = 0
    while y < y1 - 0.3:
        rh = min(depth * rng.uniform(0.85, 1.0), y1 - y)
        if y1 - (y + rh) < 1.2:
            rh = y1 - y
        x = x0 - (rng.uniform(0.8, 1.8) if row % 2 else 0.0)
        while x < x1 - 0.2:
            w = rng.uniform(2.8, 4.4)
            xa, xb = max(x, x0), min(x + w, x1)
            if xb - xa > 0.7 and not skip(xa, xb, y, y + rh):
                mb.box((xb - xa - gap, rh - gap, h), ((xa + xb) / 2, y + rh / 2, z - h / 2), (0, 0, 0), SL, 0.0)
            x += w
        y += rh
        row += 1


# ------------------------------------------------------------------ portal
def _tris(mb):
    return sum(len(f.verts) - 2 for f in mb.bm.faces)


def build(rng):
    import fm_portals
    px = L.PORTAL_X[0]

    def X(dx):
        return px + dx
    mb = K.LeanMB("PORTAL_Naruto_Bandana", C, rng, vcap=2)
    y0, y1 = Y0 + 0.2, PY + 9.6
    log = []

    def mark(name, _n=[0]):
        if DEBUG:
            t = _tris(mb)
            log.append((name, t - _n[0]))
            _n[0] = t

    # --- piso de lajes + medalhao da folha no alto da escada, no eixo da passagem (a borda de tras entra 0.3 sob
    # o estrado; a da frente fica 0.35 atras do bordo do piso)
    R1, R2 = 7.6, 6.5
    MR = 2.95
    MC = (px, YC - R1 + 0.3 - MR)

    def skip(xa, xb, ya, yb):
        inside = all(math.hypot(xx - px, yy - YC) < R1 - 0.2 for xx in (xa, xb) for yy in (ya, yb))
        med = all(math.hypot(xx - MC[0], yy - MC[1]) < MR for xx in (xa, xb) for yy in (ya, yb))
        return inside or med
    paving(mb, X(-13.6), X(13.6), y0, y1, FZ, rng, skip)
    col_box2(A, (X(-13.6), y0, T - 1.0), (X(13.6), y1, FZ))
    mark("piso")
    # medalhao: disco escuro (topo FZ+0.07) < aro claro (FZ+0.14) < folha vermelha (FZ+0.20): nada coplanar,
    # e a ponta da folha fica dentro do aro
    mb.cyl(MR, 0.14, (MC[0], MC[1], FZ), (0, 0, 0), SD, 24, bevel=0.0)
    K.ring(mb, V(MC[0], MC[1], FZ + 0.06), MR - 0.2, (1, 0, 0), (0, 1, 0), 0.3, 0.16, SL, n=20)
    leaf_symbol(mb, (MC[0] - 0.05, MC[1], FZ + 0.06), (1, 0, 0), (0, 1, 0), 1.32, RED, w=0.26, h=0.14, res=12)
    mark("medalhao")

    # --- estrado redondo escuro (2 degraus) + soleira de arenito (bloco inteiro do chao ate a soleira = fundo
    # interno do anel: a soleira continua a pedra do anel ate o chao)
    zt1, zt2 = FZ + 1.02, FZ + 2.05       # degraus ~1.0 ate a soleira (T+3.45): passa no teste de corpo da rota
    mb.cyl(R1, zt1 - FZ + 0.2, (px, YC, (zt1 + FZ - 0.2) / 2), (0, 0, 0), SD, 28, bevel=0.12)
    mb.cyl(R2, zt2 - zt1 + 0.1, (px, YC, (zt2 + zt1 - 0.1) / 2), (0, 0, 0), SD, 24, bevel=0.12)
    fm_portals.col_disc(px, YC, R1, T - 1.0, zt1)
    fm_portals.col_disc(px, YC, R2, T - 1.0, zt2)
    mb.box((11.2, 5.2, SILL - FZ + 0.2), (px, YC, (SILL + FZ - 0.2) / 2), (0, 0, 0), STONE, 0.2)
    col_box2(A, (X(-5.6), YC - 2.6, T - 1.0), (X(5.6), YC + 2.6, SILL))
    mark("estrado")

    # --- anel de pedra (colisao seguindo o arco)
    stone_ring(mb, px)
    ring_cols(px)
    mark("anel")

    # --- postes + bandana
    for s in (-1, 1):
        post(mb, X(s * PXP), YC)
        col_box(A, (2.8, 2.8, P_Z1 + 1.0 - FZ), (X(s * PXP), YC, (P_Z1 + 1.0 + FZ) / 2))
    mark("postes")
    band(mb, px)
    mark("faixa")
    for s in (-1, 1):
        knot_tails(mb, px, s)
    mark("nos")
    engraved_plate(mb, px, ZC_PLATE, PLATE_YB)
    mark("placa")

    # --- kunai gigante cravado a esquerda (com lajes quebradas pelo impacto): 1.5 mais para fora e 1.0 mais para
    # tras que na r2, inclinado para fora-e-para-tras (na B_34L o cabo fica a esquerda do anel; argola em x >= -13.7)
    ke = V(X(-10.8), Y0 + 5.2, FZ)
    dk = V(-0.22, 0.25, 0.94).normalized()
    kunai(mb, ke, dk, (0.94, 0.0, 0.22))
    for k, (dx, dy, rz, tl) in enumerate(((-1.5, -0.6, 0.3, 0.12), (1.3, -0.9, -0.5, -0.1), (0.2, 1.4, 1.2, 0.09))):
        mb.box((1.7, 1.2, 0.34), (ke.x + dx, ke.y + dy, FZ + 0.12), (tl, -tl * 0.6, rz), SL, 0.0)
    kc = ke + dk * 3.8
    col_box(A, (1.8, 1.8, 9.0), tuple(kc), tuple(dk.to_track_quat("Z", "Y").to_euler()))
    mark("kunai")

    # --- pergaminhos ao pe do poste direito (fora da subida e do primeiro plano da C_34R)
    yaw = D(8)
    sb, ax, side = scrolls(mb, (X(9.4), YC - 4.1, FZ), yaw)
    col_box(A, (5.6, 3.6, 3.2), (sb.x, sb.y, FZ + 1.6), (0, 0, yaw))
    mark("pergaminhos")

    # --- moitas baixas e lisas atras dos pes dos postes, montadas na borda lateral do piso (amaciam o corte reto
    # lajes/grama sem ruido); dentro do lote (x <= px +- 13.9)
    # esquerda: 3 calotas (frente-fora, lado e tras do pe do poste); direita: 2 (o canto da frente e dos pergaminhos)
    bush(mb, (X(-12.3), YC), ((-0.45, -2.3, 1.0, 1.1, 1.1), (-0.4, 1.7, 1.2, 1.9, 1.75), (0.35, 4.3, 1.5, 1.5, 1.45)))
    bush(mb, (X(12.3), YC), ((0.4, 1.7, 1.2, 1.9, 1.75), (-0.35, 4.3, 1.5, 1.5, 1.45)))
    mark("moitas")

    # --- espiral (contrato) + verso: folha em vermelho na tampa traseira (quem volta de Konoha ve o simbolo); a
    # tampa traseira assenta no intradorso do anel (cup_r = RI + 0.05: nada solto)
    fm_portals.swirl("Naruto", px, "P_Naruto_Swirl", mb, SD, rim_y=YC - PY - RD + 0.05, cup_r=RI + 0.05)
    mb.mats = [RIM if m == "P_Naruto_Glow" else m for m in mb.mats]
    leaf_symbol(mb, (px + 0.3, PY + 2.25 + 0.02, SZ), (-1, 0, 0), (0, 0, 1), 2.6, RED, w=0.26, h=0.1, res=12)
    mark("espiral+verso")
    if DEBUG:
        print("TRIS por parte:", ", ".join("%s=%d" % x for x in log), "total", _tris(mb))
    mb.finish()
    _swirl_preview()


# ------------------------------------------------------------------ dressing da escada (lance 2)
# "A bandana conduz ao portal": no alto da escada um PAR de lanternas de pedra (arenito ocre do anel, janela com o
# brilho laranja, telhado de ferro) "usa a bandana": colar de pano azul-marinho no fuste com o no e as duas caudas em
# rabo de andorinha dos postes do portal. Do lado direito a bandana DESCE da lanterna e fica ESTENDIDA sobre um
# MEIO-FIO baixo de arenito (o parapeito do poco, em 3 blocos com juntas escuras como as aduelas do anel): sai do colar
# da lanterna torcendo ate deitar no topo do meio-fio, cai em abas pelos dois lados e dobra sobre a ponta de baixo,
# onde fecha no mesmo no com caudas (um no em cada ponta, como no portal). Sem postes nem corda pendurada.
# Assimetrico por causa do terreno: do lado esquerdo a rocha da cachoeira e o penhasco encostam no poco ate y ~96.5
# (so o alto fica livre -> so a lanterna). Tudo baixo (<= T+4.6): nao compete com o portal na praca.
# Paleta: arenito, pano, ferro, brilho (4 materiais, todos do portal). Geometria deterministica (nao usa o rng: o
# estudio e o lobby saem iguais e o rng compartilhado do fm_portals.build nao e consumido aqui).
ST_TORO_DX = 8.95                   # lanternas no alto da escada (|x - px|): sapata 1.8 -> face interna em 8.05
ST_TORO_Y = 98.45
ST_TORO_ZC = T + 1.85               # colar de pano no fuste da lanterna
ST_TORO_RC = 0.52                   # raio do colar (8 lados girado 22.5: face interna plana a 0.48 do eixo)
ST_CURB_DX = 8.45                   # eixo do meio-fio (|x - px|): face interna em 8.10
ST_CURB_Y = (87.6, 97.6)            # de baixo ate encostar na sapata da lanterna (face em 97.55)
ST_CURB_W, ST_CURB_H = 0.7, 1.0     # secao do meio-fio (topo chanfrado 0.14)
ST_KNOT_ZC = T + 0.74               # no de baixo, na face da ponta do meio-fio


def _st_knot(mb, c, rc, zc, s, ang=40.0, tails=(1.15, 0.9)):
    """no de pano achatado contra um colar (eixo c, raio rc, cota zc) na face frontal-externa e duas caudas em rabo
    de andorinha caindo para a frente (a receita do knot_tails do portal, em miniatura)"""
    a = D(ang)
    n0 = V(s * math.sin(a), -math.cos(a), 0)          # para fora do colar (frente-fora)
    t0 = V(s * math.cos(a), math.sin(a), 0)           # tangente horizontal
    kc = V(c[0], c[1], zc) + n0 * (rc + 0.04)
    res = bmesh.ops.create_uvsphere(mb.bm, u_segments=8, v_segments=5, radius=1.0)
    for vv in res["verts"]:
        l = vv.co.copy()
        vv.co = kc + t0 * (l.x * 0.38) + n0 * (l.y * 0.17) + V(0, 0, l.z * 0.28)
    for f in mb._post(res["verts"], NAVY, None, 0, 1):
        f.smooth = True
    fwd = V(0, -1, 0)
    for ln, lay, toff, tw in ((tails[0], 0.05, -0.11, 0.22), (tails[1], -0.03, 0.12, -0.2)):
        top = kc + V(0, 0, -0.1) + n0 * lay + t0 * toff

        def center(f, top=top, ln=ln):
            return top + V(0, 0, -ln * f) + (fwd * 0.2 + n0 * 0.12) * f + fwd * (0.1 * math.sin(f * math.pi * 1.5))

        def wdir(f, tw=tw):
            ang_ = tw * f
            return V(t0.x * math.cos(ang_) - t0.y * math.sin(ang_), t0.x * math.sin(ang_) + t0.y * math.cos(ang_), 0)

        def width(f):
            return 0.28 + 0.12 * smooth01(f)
        ribbon(mb, center, wdir, ln, width, 0.07, 0.15, NAVY, n=3, cols=2)


def _st_toro(mb, x, y, s):
    """lanterna de pedra baixa (T+4.6) no arenito do anel: sapata chanfrada, fuste octogonal com o colar de pano e o
    no, prato, camara com a janela de brilho laranja entre 4 pilaretes, telhado piramidal de ferro com beiral e
    pinaculo"""
    mb.box((1.8, 1.8, 0.6), (x, y, T + 0.2), (0, 0, 0), STONE, 0.12)
    mb.cyl(0.46, 1.8, (x, y, T + 1.4), (0, 0, D(22.5)), STONE, 8, r2=0.38, bevel=0.0)
    rc = ST_TORO_RC
    mb.cyl(rc, 0.44, (x, y, ST_TORO_ZC), (0, 0, D(22.5)), NAVY, 8, bevel=0.0)
    _st_knot(mb, (x, y), rc, ST_TORO_ZC, s)
    mb.box((1.36, 1.36, 0.3), (x, y, T + 2.45), (0, 0, 0), STONE, 0.0)
    mb.box((0.8, 0.8, 0.84), (x, y, T + 3.02), (0, 0, 0), RIM, 0.0)
    for sx in (-1, 1):
        for sy in (-1, 1):
            mb.box((0.26, 0.26, 0.84), (x + sx * 0.44, y + sy * 0.44, T + 3.02), (0, 0, 0), STONE, 0.0)
    mb.box((1.8, 1.8, 0.16), (x, y, T + 3.52), (0, 0, 0), IRON, 0.0)
    mb.cyl(1.2, 0.62, (x, y, T + 3.91), (0, 0, D(45)), IRON, 4, r2=0.2, bevel=0.0)
    mb.cyl(0.15, 0.4, (x, y, T + 4.37), (0, 0, 0), IRON, 6, r2=0.07, bevel=0.0)
    return rc


def _st_curb(mb, x, y0, y1, n=3, gap=0.08):
    """meio-fio de arenito ao longo do poco: n blocos (varredura com o topo chanfrado, 20 tris cada) separados por
    juntas; um nucleo de ferro recuado aparece nas juntas como linha escura (a mesma leitura das aduelas do anel)"""
    hw, h, c = ST_CURB_W / 2, ST_CURB_H, 0.14
    prof = [(-hw, -0.12), (hw, -0.12), (hw, h - c), (hw - c, h), (-hw + c, h), (-hw, h - c)]
    ln = (y1 - y0 - gap * (n - 1)) / n
    for i in range(n):
        ya = y0 + i * (ln + gap)
        mb.sweep([(x, ya, T), (x, ya + ln, T)], prof, STONE, True)
    mb.box((ST_CURB_W - 0.24, y1 - y0 - 0.3, h - 0.25), (x, (y0 + y1) / 2, T + (h - 0.25) / 2 - 0.1), (0, 0, 0), IRON,
           0.0)


def _st_cloth_prof(W, h_in, h_out, tw=0.0, k=1.0, t=0.06):
    """secao do pano (a: normal do caminho, 'para cima'; b: lateral, b > 0 = lado do poco): topo chato sobre o
    meio-fio e abas que caem h_in / h_out abrindo para fora (aba mais comprida abre mais: barra de pano, nao
    tampa). tw gira a secao (torce a faixa) e k afina a espessura (a ponta que entra no colar)"""
    top, tin = 0.05 * k, -0.01 * k
    wi, wo = W + 0.1 * (h_in - 0.3), W + 0.1 * (h_out - 0.3)
    pts = [(-h_out, -wo), (top, -W + 0.08), (top, W - 0.08), (-h_in, wi),
           (-h_in, wi - t), (tin, W - t - 0.06), (tin, -W + t + 0.06), (-h_out, -wo + t)]
    c, s = math.cos(tw), math.sin(tw)
    return [(a * c - b * s, a * s + b * c) for a, b in pts]


def _st_drape(mb, px):
    """a bandana do guarda-corpo: UMA peca de pano do colar da lanterna direita ate a ponta de baixo do meio-fio.
    Sai rente a face interna do colar (em pe, de frente para a escada), desce torcendo ate deitar no topo do
    meio-fio, corre sobre ele com abas de barra ondulada e dobra sobre a quina da ponta de baixo (o no cobre)."""
    x = px + ST_CURB_DX
    xf = px + ST_TORO_DX - ST_TORO_RC * math.cos(D(22.5))       # face interna do colar
    zt = T + ST_CURB_H
    y0 = ST_CURB_Y[0]
    # (y, z, x, torcao, meia-largura, aba do lado do poco, aba de fora, espessura)
    spec = [(ST_TORO_Y, ST_TORO_ZC, xf + 0.005, 90, 0.18, 0.07, 0.07, 0.25),
            (98.12, ST_TORO_ZC - 0.06, xf - 0.01, 84, 0.2, 0.07, 0.07, 1.0),
            (97.75, T + 1.58, x + 0.01, 62, 0.24, 0.08, 0.08, 1.0),
            (97.3, T + 1.28, x, 34, 0.29, 0.1, 0.1, 1.0),
            (96.8, zt + 0.08, x, 12, 0.35, 0.15, 0.15, 1.0),
            (96.2, zt + 0.005, x, 0, 0.41, 0.24, 0.26, 1.0)]
    # barra ondulada: as abas dos dois lados alternam comprida/curta (fase oposta)
    for y, hi, ho in ((95.3, 0.36, 0.28), (94.0, 0.24, 0.4), (92.7, 0.4, 0.25), (91.4, 0.26, 0.38),
                      (90.1, 0.38, 0.24), (88.8, 0.3, 0.34)):
        spec.append((y, zt, x, 0, 0.43, hi, ho, 1.0))
    spec += [(y0 + 0.02, zt - 0.01, x, 0, 0.43, 0.14, 0.14, 1.0),
             (y0, ST_KNOT_ZC - 0.12, x, 0, 0.42, 0.08, 0.08, 1.0)]
    pts = [V(xx, y, z) for (y, z, xx, _tw, _w, _hi, _ho, _k) in spec]
    profs = [_st_cloth_prof(w, hi, ho, D(tw), k) for (_y, _z, _x, tw, w, hi, ho, k) in spec]
    K.loft(mb, pts, profs, NAVY, True, up=(0, 0, 1))


def stairs(mb, px, rng):
    """dressing da faixa ao lado do lance 2 (terraco z=T, y 86..99.4, 7.8 <= |x-px| <= 13.9) no MB recebido
    (PORTAL_Naruto_Stairs). 3 colisoes: as 2 lanternas e o meio-fio (cobre o pano ate a sapata da lanterna).
    `rng` nao e usado (geometria deterministica)."""
    for s in (-1, 1):
        tx = px + s * ST_TORO_DX
        _st_toro(mb, tx, ST_TORO_Y, s)
        col_box(A, (1.8, 1.8, 4.6), (tx, ST_TORO_Y, T + 2.3))
    # guarda-corpo (direita): meio-fio de arenito com a bandana estendida, amarrada no colar da lanterna e com o no
    # e as caudas na ponta de baixo
    x = px + ST_CURB_DX
    _st_curb(mb, x, ST_CURB_Y[0], ST_CURB_Y[1])
    _st_drape(mb, px)
    _st_knot(mb, (x, ST_CURB_Y[0]), 0.0, ST_KNOT_ZC, 1, ang=0.0, tails=(0.58, 0.46))
    y0, y1 = ST_CURB_Y[0] - 0.3, ST_CURB_Y[1]
    col_box(A, (0.9, y1 - y0, 1.3), (x, (y0 + y1) / 2, T + 0.6))
