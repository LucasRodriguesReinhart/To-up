# fm_pv3_demonslayer - portal DEMON SLAYER (pv3, passe final): "TSUBA E ESPADAS NICHIRIN"
# O ARO DO PORTAL E UMA TSUBA: disco de ferro negro FOSCO em contorno MOKKO (4 lobos, cuspides em V onde as espadas
# saem), aba (mimi) de LACA VERMELHO-ESCURA, colar interno em relevo e dois hitsu-ana pequenos (meias-luas) colados ao
# colar nos lobos das 3h e 9h. A espiral (vermelho Hinokami, so emissao: nao recebe sombra) fica no furo central.
# Atras dela, duas katanas nichirin cruzadas em X, cravadas nos penedos da pedra sagrada (iwakura) com shimenawa.
# Passe final (pendencias dos criticos):
#  - FACE DA TSUBA em faixas radiais de QUADS (sem leque de triangulos do triangle_fill); ferro com roughness 0.78,
#    metal 0.12 e especular baixo (le como ferro preto fosco); colar = peca propria de 32 lados apoiada na face.
#  - ABA: laca vermelho-escura (sem latao), 0.32 de largura visivel, passo de 5 graus, sombreamento suave; a parede
#    lateral e ferro. As costas repetem a aba e ganham um anel de laca na tampa (costas acabadas).
#  - MEIAS-LUAS ~40% menores (meia-altura 1.5, largura 0.9) coladas ao furo: a silhueta volta a ser guarda de espada.
#  - ESPIRAL: textura propria (T_swirl_ds_v5.png): fundo carmesim profundo, 2 linguas vermelho-vivo com filete
#    laranja, nucleo quente pequeno e aro vermelho (sem branco). Blender = so emissao (como o Roblox mostra a PNG):
#    o disco nao recebe sombra do colar/aro nem reflexo do sol; nada atras do furo aparece (disco opaco + tampa).
#  - LAMINAS de espada claras: 1.3 de largura (meia-largura 0.68 -> 0.62), 0.5 de espessura, hamon creme de 0.32 e
#    filete vermelho 0.09, giradas 30 graus no proprio eixo (o fio aparece de frente e a face larga nas costas);
#    habaki creme; boca no penedo com 3 lascas e 2 rachaduras escuras, livre das lanternas.
#  - GLICINIA (passe final 2): TRONCO LIDER retorcido (2 curvas em S, base 0.95 + raiz alargada) que sobe inteiro ate
#    dentro da massa do meio (a forquilha fica escondida na copa) + UM galho lateral mais fino (0.4 -> 0.25) saindo em
#    outra altura (T+9.8) para a massa da frente: nada de Y/estilingue. Copa em GUARDA-CHUVA: 4 massas lisas lilas
#    (coroa baixa) + 4 massas menores em lilas medio na borda (bico da frente, borda de fora, bico de tras, coroa do
#    lado do aro) quebrando o contorno. 16 CASCATAS finas (r0 0.45-0.58, 6 lados, sombreamento suave) em cone longo
#    liso SEM gomos (sem cintura) que afina ate ~0.13 e fecha em PONTA ARREDONDADA (anel da calota + polo), com 3
#    faixas de cor (lilas forte -> P_DS_GlicMid lilas medio -> lilas claro) trocando em aneis do cone. Cortina de fora
#    em 2 fileiras (lado a lado, sem se atravessar), frente e 4 curtas no lado do aro; cada cascata e encurtada ate nao
#    cruzar o aro nas cameras A_Hero (>= 1.2) e G_Far (>= 0.4) nem tocar tronco/galho. Tudo apoiado.
#  - ESTANDARTE removido (props: glicinia, lanternas, corda). Lanternas junto das lajes, com capuz preto, braco mais
#    grosso e luzes L_P_DemonSlayer_Lamp_*.
#  - COL: plataforma ate o fundo da pedra, anel de caixas na altura da shimenawa (frente, costas, pontas), lobos em
#    2 degraus; patio sem faces coplanares (cascalho recuado dos meios-fios, braco da lanterna abaixo do topo do poste).
#
# PLANO (studs; x relativo a px, y absoluto, z relativo a T):
#   espiral r7.5 em (0, PY, 11.2) (fixa) | tsuba: furo 7.58, colar 8.12, cuspides r9.3, lobos r10.8 (topo 10.45)
#   espadas a +-45 graus, cruzamento (0, 14.0), planos y = PY+2.8 / PY+3.7 (atras da tampa, que vai ate PY+2.25)
#     s (ao longo do eixo): saida do aro ~7.1 | habaki 9.1..10.0 | tsuba 10.0..10.35 | fuchi ..10.65 |
#     cabo ..16.3 | kashira ..16.9 (topo T+26.3) | embaixo: saida do aro s -11.2, boca no penedo, ponta enterrada
#   pedra: x +-11.9, y 109.4..118.4, plataforma T+3.08 | corda T+1.95 | degraus T+1.0 e T+2.0 (y 106.1..108.3)
#   glicinia: tronco (-13.0, 109.6) ate T+17.7 (dentro da copa), galho T+9.8, copa x -13.85..-8.8, y 104.5..116.5,
#     z 15.0..19.95; cascatas ate ~T+9.2
#   lanternas: postes (+-5.3, 104), chochin voltada para as lajes
import math
import os
import bmesh
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
import fm_lib
from fm_lib import D, S, col_box, col_box2, light, resample, path_len
import fm_mat_textures as TX
import fm_portal_kit as K
import fm_portals as PO
import fm_layout as L
import fm_veg_kit as VK  # (registra Bark_Dark antes de make_materials)

# ------------------------------------------------------------------ materiais (antes de make_materials)
_M = fm_lib.MATS.setdefault
fm_lib.MATS["P_DS_Iron"] = (S(24, 23, 28), 0.78, 0.12, 0, None, 0.03)   # ferro negro FOSCO (tsuba, laminas, cabo)
_M("P_DS_Lacquer", (S(112, 13, 19), 0.42, 0.0, 0, None, 0.03))          # laca vermelho-escura: aba, anel das costas
_M("P_DS_Red", (S(150, 18, 22), 0.65, 0.0, 0, None, 0.04))              # (ja existe em fm_lib: filete, papel da lanterna)
_M("Stone_DS_Rock", (S(92, 92, 100), 0.9, 0.0, 0, None, 0.08))          # pedra sagrada cinza escura e fria
_M("P_DS_Gravel", (S(186, 176, 150), 0.95, 0.0, 0, None, 0.05))         # cascalho claro (e a palha da shimenawa)
fm_lib.MATS["P_DS_Glicinia"] = (S(146, 84, 220), 0.72, 0.0, 0, None, 0.05)  # lilas forte (copa, alto das cascatas)
fm_lib.MATS["P_DS_GlicMid"] = (S(176, 112, 230), 0.72, 0.0, 0, None, 0.04)  # lilas medio (meio das cascatas, bordas)
fm_lib.MATS["P_DS_GlicTip"] = (S(214, 160, 238), 0.7, 0.0, 0, None, 0.03)   # lilas claro (ponta das cascatas)
# aro de energia do portal (fm_portals.swirl usa P_DS_Glow): vermelho saturado, emissao moderada. No Roblox e Neon com
# a cor calibrada de RBX_CAL (185,12,22), o mesmo vermelho.
fm_lib.MATS["P_DS_Glow"] = (S(232, 20, 14), 0.35, 0.0, 1.6, S(232, 20, 14), 0.0)
SWIRL_EMIT = 1.15           # espiral (so emissao no Blender)
GLOW_EMIT = 1.3             # aro de energia (so emissao no Blender)

C = "06_PORTALS"
A = "Portal"
KEY = "DemonSlayer"
T = L.TERR
PY = L.PORTAL_Y
Y0 = L.FLIGHT2_Y1
SZ = T + 2.0 + 9.2          # centro da espiral (fixo em fm_portals)
IRON, LAC, RED, CREAM = "P_DS_Iron", "P_DS_Lacquer", "P_DS_Red", "Emblem_Cream"
ROCK, GRAVEL, ROPE = "Stone_DS_Rock", "P_DS_Gravel", "P_DS_Gravel"
WIS, WIS_MID, WIS_TIP = "P_DS_Glicinia", "P_DS_GlicMid", "P_DS_GlicTip"
BARK, GLOW = "Bark_Dark", "P_DS_Glow"
CANOPY = WIS                # copa = massa de flores lilas (as cascatas nascem dela)
STEEL = CREAM               # faixa de fio da lamina (hamon claro; mesmo creme do cabo: 12 materiais no portal)


# ------------------------------------------------------------------ espiral propria (textura v5)
SWIRL_DS = dict(border=(38, 0, 5), bg_mid=(112, 3, 12), bg_in=(165, 8, 16), arm=(236, 26, 20),
                arm_hi=(255, 112, 52), core=(255, 178, 110), halo=(240, 58, 32), rim=(255, 58, 42),
                arms=2, twist=2.7, width=0.42, line=0.75, halo_r=0.16, core_r=0.07, style="ds_hinokami", seed=41)
SWIRL_FILE = "T_swirl_ds_v5.png"


def ds_swirl_tex(spec, n=None):
    """espiral do Demon Slayer (Hinokami Kagura): fundo carmesim que escurece ate quase preto na borda, 2 linguas de
    fogo vermelho-vivo (largura ondulante, frente de topo chato, rastro suave) com filete laranja na borda de ataque,
    nucleo quente pequeno e aro VERMELHO claro (sem branco). Alfa 0 fora do circulo."""
    n = n or TX.SWIRL_N
    rng = np.random.default_rng(spec.get("seed", 41))
    c = (np.arange(n) + 0.5) / n * 2 - 1
    X, Y = np.meshgrid(c, -c)                     # linha 0 = topo (mesma convencao de fm_mat_textures)
    r = np.sqrt(X * X + Y * Y)
    th = np.arctan2(Y, X)
    ss, mix = TX.smoothstep, TX._mix

    def col(v):
        return np.array(v, float) / 255.0
    BG_OUT, BG_MID, BG_IN = col(spec["border"]), col(spec["bg_mid"]), col(spec["bg_in"])
    ARM, ARM_HI, CORE, HALO, RIM = (col(spec[k]) for k in ("arm", "arm_hi", "core", "halo", "rim"))
    rgb = mix(mix(np.broadcast_to(BG_IN, r.shape + (3,)), BG_MID, ss(0.10, 0.55, r)), BG_OUT, ss(0.55, 0.97, r))
    na = spec["arms"]
    nz_w = TX._grid_noise(rng, 7, 5)
    warp = (nz_w(th / (2 * math.pi) * 7, r * 5) - 0.5) * 0.08
    ph = na * th / (2 * math.pi) + spec["twist"] * r ** 0.9 + warp
    s = ph % 1.0 - 0.5
    fl = TX._grid_noise(rng, na * 6, 9)
    wl = spec["width"] * (0.45 + 0.6 * np.clip(r, 0, 1)) * (0.78 + 0.44 * fl(ph * 6, r * 9))
    lead = np.exp(-(np.maximum(s, 0) / (wl * 0.34)) ** 4)
    trail = np.exp(-(np.maximum(-s, 0) / (wl * 0.95)) ** 2)
    env = ss(0.06, 0.22, r) * (1 - ss(0.86, 0.95, r))
    nz_s = TX._grid_noise(rng, 48 * na, 6)
    streak = nz_s(ph * 48, r * 6)
    arm = np.where(s >= 0, lead, trail) * env * (0.8 + 0.2 * streak)
    line = np.exp(-((s - wl * 0.18) / (wl * 0.12)) ** 2) * env
    rgb = mix(rgb, ARM, np.clip(arm, 0, 1))
    rgb = mix(rgb, ARM_HI, np.clip(line * spec["line"], 0, 1))
    rgb = mix(rgb, HALO, np.exp(-(r / spec["halo_r"]) ** 2) * 0.8)
    rgb = mix(rgb, CORE, np.exp(-(r / spec["core_r"]) ** 3))
    # aro: linha vermelha clara + brilho para dentro (nada de branco)
    rim = np.exp(-((r - 0.955) / 0.024) ** 2)
    glow = np.exp(-((r - 0.955) / 0.07) ** 2) * 0.45 * (r < 0.955)
    rgb = mix(rgb, RIM * 0.85, np.clip(glow, 0, 1))
    rgb = mix(rgb, RIM, np.clip(rim * 1.1, 0, 1))
    rgb = np.where((r > 0.955)[..., None], mix(rgb, np.broadcast_to(RIM, rgb.shape), 0.85 * np.ones_like(r)), rgb)
    alpha = (1 - ss(0.985, 1.0, r))[..., None]
    return np.concatenate([np.clip(rgb, 0, 1), alpha], axis=2)


def _patch_swirl():
    """registra o desenho novo do DS em fm_mat_textures (so em memoria, como o DB): SWIRL_SPEC/SWIRL_TEX apontam para a
    v5 e tex_swirl despacha o estilo 'ds_hinokami'. Blender (fm_lib._swirl_nodes), export_roblox e export_vfx leem a
    mesma PNG. Nome novo (v5): o 3D Importer nao reaproveita o cache da v4."""
    spec = dict(TX.SWIRL_SPEC["P_DS_Swirl"])
    spec.update(SWIRL_DS)
    TX.SWIRL_SPEC["P_DS_Swirl"] = spec
    TX.SWIRL_TEX["P_DS_Swirl"] = (SWIRL_FILE, spec["arm"], spec["core"])
    if not getattr(TX.tex_swirl, "_ds_hinokami", False):
        orig = TX.tex_swirl

        def tex_swirl(sp, n=None):
            return ds_swirl_tex(sp, n) if sp.get("style") == "ds_hinokami" else orig(sp, n)
        for a in dir(orig):
            if a.startswith("_") and not a.startswith("__"):
                setattr(tex_swirl, a, getattr(orig, a))
        tex_swirl._ds_hinokami = True
        TX.tex_swirl = tex_swirl
    p = os.path.join(TX.TEX_DIR, SWIRL_FILE)
    if not os.path.exists(p):
        os.makedirs(TX.TEX_DIR, exist_ok=True)
        TX.write_png(p, ds_swirl_tex(spec))


_patch_swirl()


def _unlit(name, strength, color=None):
    """previa no Blender = como o Roblox mostra (Neon / PNG sem luz): so emissao, sem difuso nem especular. Assim o
    disco da espiral nao recebe a sombra serrilhada do colar/aro nem o reflexo do sol. Nao afeta o export."""
    import bpy
    if fm_lib.PREVIEW == "roblox":
        return
    m = bpy.data.materials.get(name)
    if m is None or not m.use_nodes:
        return
    nt = m.node_tree
    bs = next((nd for nd in nt.nodes if nd.type == "BSDF_PRINCIPLED"), None)
    if bs is None:
        return
    for lk in list(bs.inputs["Base Color"].links):
        nt.links.remove(lk)
    bs.inputs["Base Color"].default_value = (0.0, 0.0, 0.0, 1.0)
    bs.inputs["Roughness"].default_value = 1.0
    if "Specular IOR Level" in bs.inputs:
        bs.inputs["Specular IOR Level"].default_value = 0.0
    if color is not None:
        for lk in list(bs.inputs["Emission Color"].links):
            nt.links.remove(lk)
        bs.inputs["Emission Color"].default_value = (*color, 1.0)
    bs.inputs["Emission Strength"].default_value = strength


def _spec(name, spec, rough=None):
    """Blender: especular menor no ferro fosco (a parede lateral da tsuba nao vira um filete rosa-claro em angulo
    rasante com o sol e a luz vermelha do portal)"""
    import bpy
    m = bpy.data.materials.get(name)
    if m is None or not m.use_nodes or fm_lib.PREVIEW == "roblox":
        return
    for nd in m.node_tree.nodes:
        if nd.type == "BSDF_PRINCIPLED" and "Specular IOR Level" in nd.inputs:
            nd.inputs["Specular IOR Level"].default_value = spec
            if rough is not None:
                nd.inputs["Roughness"].default_value = rough


# espadas (s = distancia ao cruzamento, ao longo do eixo)
LEAN = D(45.0)
HC = 2.8                    # cruzamento acima do centro da espiral
SW_Y = {1: PY + 2.8, -1: PY + 3.7}     # (0.9 entre os planos: as laminas giradas nao se tocam no cruzamento)
S_HAB = 9.1                 # inicio da habaki (o toco de lamina visivel vai da saida do aro ate aqui)
HAB_L = 0.9
TSU_T = 0.35                # espessura da tsuba
TSU_RE, TSU_RY = 1.75, 1.5  # raios da tsuba (no plano das espadas / em y)
FUCHI_L = 0.3
TSUKA_L = 5.65
KASH_L = 0.6
GRIP_A, GRIP_B = 0.78, 0.62   # meia-largura / meia-espessura do cabo
SORI = 0.0012               # curvatura da lamina: desvio para o dorso = SORI * d^2 (d = distancia a habaki)
BW_H, BW_T = 0.68, 0.62     # meia-largura da lamina na habaki / perto da ponta (1.3 de largura: le como lamina)
EDGE_W, FIL_W = 0.32, 0.09  # faixa de fio clara (hamon) / filete vermelho
BL_ROLL = D(30.0)           # giro da lamina no proprio eixo: nas costas (E_Back) a face larga aparece, na frente o fio
BL_TH = 0.25                # meia-espessura da lamina no shinogi (lamina cartoon robusta: nas costas nao vira espeto)
# tsuba (aro)
COL_R = 8.12                # raio externo do colar (seppa-dai)
R_B = 7.75                  # borda interna da face (escondida dentro do colar)
R_C = 9.3                   # raio das cuspides
R_L = (10.8, 10.45, 10.8, 10.8)   # pico dos lobos: direita, topo, esquerda, baixo
RIM_T = 0.32                # largura visivel da aba de laca
FACE_Y, LIP_Y = 0.62, 0.84  # meia-espessura da face / da aba (a aba sobe para fora)
HOLE_R, HOLE_W, HOLE_DL, HOLE_N = 8.5, 0.9, D(10.2), 8   # hitsu-ana: raio interno, largura, meia-abertura, colunas
RING_STEP = D(5.0)
# pedra
PYC = 113.9
ZG = 1.95                   # cintura (altura da shimenawa)
Z_BOT = -0.35
#            x     topo  frente costas
ROCK_ST = [(0.0, 3.08, 4.5, 4.5), (2.6, 3.06, 4.5, 4.5),
           (6.0, 2.84, 4.38, 4.5), (7.7, 2.62, 4.2, 4.45), (8.8, 2.55, 4.0, 4.4), (9.6, 2.6, 3.8, 4.3),
           (10.35, 3.3, 3.6, 4.2), (11.0, 4.05, 3.35, 4.0), (11.4, 4.3, 3.0, 3.75), (11.7, 3.85, 2.5, 3.3),
           (11.9, 2.4, 1.5, 2.1)]
# glicinia / lanternas
TRUNK_XY = (-13.0, 109.6)
LAMP_X = 5.3
_DBG = {}


def _px():
    return L.PORTAL_X[L.PORTAL_KEYS.index(KEY)]


# ------------------------------------------------------------------ utilidades
def post_faces(mb, faces, m, tint=None, smooth=False):
    """material/tint/UV para uma lista EXPLICITA de faces (o _post do MB pega todas as faces dos vertices)"""
    faces = [f for f in faces if f is not None and f.is_valid]
    if not faces:
        return faces
    mi = mb._mi_for(m)
    t = mb.rng.uniform(-1, 1) if tint is None else tint
    for f in faces:
        f.material_index = mi
        f[mb.tint] = t
        f.smooth = smooth
        f.normal_update()
    mb._uv(set(faces), m)
    return faces


def loft_rings(mb, rings_pts, m, caps=True, closed=False, smooth=False):
    """aneis de pontos (mesmo numero) -> casca; caps nas pontas; closed=True fecha o ultimo anel no primeiro"""
    bm = mb.bm
    rings = [[bm.verts.new(p) for p in r] for r in rings_pts]
    k = len(rings[0])
    pairs = list(zip(rings, rings[1:]))
    if closed:
        pairs.append((rings[-1], rings[0]))
    faces = []
    for r0, r1 in pairs:
        for j in range(k):
            j2 = (j + 1) % k
            try:
                faces.append(bm.faces.new((r0[j], r0[j2], r1[j2], r1[j])))
            except ValueError:
                pass
    if caps and not closed:
        for r in (rings[0], rings[-1]):
            if len(r) > 2:
                try:
                    faces.append(bm.faces.new(r))
                except ValueError:
                    pass
    post_faces(mb, faces, m, smooth=smooth)
    return rings, faces


def loft_sec(mb, rings_pts, emats, caps=(None, None), smooth=()):
    """loft com material POR ARESTA da secao (emats[j] = material da faixa entre os vertices j e j+1);
    caps = (material da tampa inicial, final) ou None; smooth = materiais com sombreamento suave"""
    bm = mb.bm
    R = [[bm.verts.new(p) for p in r] for r in rings_pts]
    k = len(R[0])
    by = {}
    for r0, r1 in zip(R, R[1:]):
        for j in range(k):
            j2 = (j + 1) % k
            try:
                by.setdefault(emats[j], []).append(bm.faces.new((r0[j], r0[j2], r1[j2], r1[j])))
            except ValueError:
                pass
    for r, m in ((R[0], caps[0]), (R[-1], caps[1])):
        if m is not None:
            try:
                by.setdefault(m, []).append(bm.faces.new(r))
            except ValueError:
                pass
    for m, fs in by.items():
        post_faces(mb, fs, m, smooth=m in smooth)
    return R


def fan_to(mb, ring, tip, m, smooth=False):
    """fecha um anel num ponto (ponta arredondada/abaulada)"""
    bm = mb.bm
    tv = bm.verts.new(tip)
    fs = []
    for j in range(len(ring)):
        j2 = (j + 1) % len(ring)
        try:
            fs.append(bm.faces.new((ring[j], ring[j2], tv)))
        except ValueError:
            pass
    post_faces(mb, fs, m, smooth=smooth)
    return fs


def oct_prof(W, Dp, c):
    """secao octogonal (retangulo W x Dp com quinas chanfradas c); u = lado, v = profundidade"""
    w, d = W / 2, Dp / 2
    return [(w, -d + c), (w, d - c), (w - c, d), (-w + c, d), (-w, d - c), (-w, -d + c), (-w + c, -d), (w - c, -d)]


def chaikin(pts, it=2):
    for _ in range(it):
        out = []
        n = len(pts)
        for i in range(n):
            a, b = pts[i], pts[(i + 1) % n]
            out += [a.lerp(b, 0.25), a.lerp(b, 0.75)]
        pts = out
    return pts


def chip(mb, base, up, side, size, m, rng):
    """lasca de pedra angulosa (prisma triangular torto, 8 tris): base enterrada, topo inclinado em 'up'"""
    up = Vector(up).normalized()
    side = Vector(side).normalized()
    fw = up.cross(side).normalized()
    bm = mb.bm
    b = []
    for k in range(3):
        a = math.tau * k / 3 + rng.uniform(-0.3, 0.3)
        r = size * rng.uniform(0.75, 1.1)
        b.append(base + (side * math.cos(a) + fw * math.sin(a)) * r - up * size * 0.45)
    top = []
    for k in range(3):
        a = math.tau * k / 3 + 0.5 + rng.uniform(-0.2, 0.2)
        r = size * rng.uniform(0.25, 0.45)
        top.append(base + up * size * rng.uniform(0.8, 1.1) + side * size * 0.25 + (side * math.cos(a) + fw * math.sin(a)) * r)
    vb = [bm.verts.new(p) for p in b]
    vt = [bm.verts.new(p) for p in top]
    fs = [bm.faces.new(vb[::-1]), bm.faces.new(vt)]
    for k in range(3):
        k2 = (k + 1) % 3
        fs.append(bm.faces.new((vb[k], vb[k2], vt[k2], vt[k])))
    post_faces(mb, fs, m)


def tube(mb, cen, radii, n, mat_of, smooth=True, cap0=True, tip=None, rot=0.0):
    """tubo liso ao longo de 'cen' (secao circular de n lados, raio por ponto); mat_of(i, j) = material da face do
    trecho i..i+1, lado j;
    cap0 fecha o primeiro anel; tip = ponto onde o ultimo anel fecha em leque (ponta arredondada)"""
    pts, Tn, Nn, Bn = K.frames(cen)
    bm = mb.bm
    R = []
    for p, nn, bb, r in zip(pts, Nn, Bn, radii):
        R.append([bm.verts.new(p + (nn * math.cos(rot + math.tau * j / n) + bb * math.sin(rot + math.tau * j / n)) * r)
                  for j in range(n)])
    by = {}
    for i, (r0, r1) in enumerate(zip(R, R[1:])):
        for j in range(n):
            j2 = (j + 1) % n
            by.setdefault(mat_of(i, j), []).append(bm.faces.new((r0[j], r0[j2], r1[j2], r1[j])))
    if cap0:
        by.setdefault(mat_of(0, 0), []).append(bm.faces.new(R[0][::-1]))
    if tip is not None:
        tv = bm.verts.new(tip)
        for j in range(n):
            j2 = (j + 1) % n
            by.setdefault(mat_of(len(R) - 2, j), []).append(bm.faces.new((R[-1][j], R[-1][j2], tv)))
    else:
        by.setdefault(mat_of(len(R) - 2, 0), []).append(bm.faces.new(R[-1]))
    for m, fs in by.items():
        post_faces(mb, fs, m, smooth=smooth)
    return R


# ------------------------------------------------------------------ eixo das espadas (com sori) e contorno mokko
def sw_basis(sg):
    a = Vector((sg * math.sin(LEAN), 0, math.cos(LEAN)))        # para o cabo
    e = Vector((-sg * math.cos(LEAN), 0, math.sin(LEAN)))       # lado do fio
    return a, e


def sw_axis(sg, s, px=0.0):
    """ponto do eixo e direcao do fio (normal no plano das espadas) em s; abaixo da habaki a lamina curva para o dorso"""
    a, e = sw_basis(sg)
    o = Vector((px, SW_Y[sg], SZ + HC))
    d = max(0.0, S_HAB - s)
    c = o + a * s - e * (SORI * d * d)
    t = (a + e * (2.0 * SORI * d)).normalized()
    n = (e - t * e.dot(t)).normalized()
    return c, t, n


def exit_s(sg, lower):
    """s em que o eixo cruza o circulo das cuspides (R_C) em cima (lower=False) ou embaixo"""
    def r(s):
        c, _t, _n = sw_axis(sg, s)
        return math.hypot(c.x, c.z - SZ)
    lo, hi = (0.0, 12.0) if not lower else (-16.0, 0.0)
    for _ in range(60):
        mid = (lo + hi) / 2
        inside = r(mid) < R_C
        if not lower:
            lo, hi = (mid, hi) if inside else (lo, mid)
        else:
            lo, hi = (lo, mid) if inside else (mid, hi)
    return (lo + hi) / 2


def sword_frame():
    """(s da saida de cima, DISTANCIA da saida de baixo) - a de baixo fica em s = -s_d"""
    return exit_s(1, False), -exit_s(1, True)


def lobes():
    """mokko = uniao de 4 discos; as cuspides caem EXATAMENTE onde as espadas saem do aro (cima e baixo)"""
    s_u, s_d = sword_frame()
    cu, _t, _n = sw_axis(1, s_u)
    cd, _t, _n = sw_axis(1, -s_d)
    au = math.atan2(cu.z - SZ, cu.x)                     # ~57 graus (sai em cima a direita)
    ad = math.pi - math.atan2(cd.z - SZ, cd.x)           # espelho da saida de baixo (~-36 graus)
    ad = (ad + math.pi) % math.tau - math.pi
    notch = [ad, au, math.pi - au, math.pi - ad, ad + math.tau]
    out = []
    for k in range(4):
        a0, a1 = notch[k], notch[k + 1]
        phi, beta = (a0 + a1) / 2, (a1 - a0) / 2
        rl = R_L[k]
        d = (rl * rl - R_C * R_C) / (2 * (rl - R_C * math.cos(beta)))
        out.append((phi, d, rl - d, a0, a1))
    return out


def contour_r(th, t, lb):
    """raio do contorno mokko na direcao th, recuado t (discos encolhidos)"""
    best = 0.0
    for phi, d, rho, a0, a1 in lb:
        dt = th - phi
        rr = rho - t
        disc = rr * rr - (d * math.sin(dt)) ** 2
        if disc < 0:
            continue
        best = max(best, d * math.cos(dt) + math.sqrt(disc))
    return best


def ring_columns(lb, step=RING_STEP):
    """colunas (angulo, u) do aro: passo ~step em cada lobo; nos lobos laterais (0 e 2) o hitsu-ana ganha HOLE_N+1
    colunas proprias (u = -1..1, pontas exatas). u = None fora do furo."""
    cols = []
    for k, (phi, d, rho, a0, a1) in enumerate(lb):
        if k in (0, 2):
            h0, h1 = phi - HOLE_DL, phi + HOLE_DL
            n0 = max(3, int(round((h0 - a0) / step)))
            cols += [(a0 + (h0 - a0) * i / n0, None) for i in range(n0)]
            cols += [(phi + HOLE_DL * (-1 + 2 * i / HOLE_N), -1 + 2 * i / HOLE_N) for i in range(HOLE_N + 1)]
            n1 = max(3, int(round((a1 - h1) / step)))
            cols += [(h1 + (a1 - h1) * i / n1, None) for i in range(1, n1)]
        else:
            n = max(10, int(round((a1 - a0) / step)))
            cols += [(a0 + (a1 - a0) * i / n, None) for i in range(n)]
    return cols


# ------------------------------------------------------------------ TSUBA (o aro do portal)
def tsuba_ring(mb, px):
    """face de ferro em faixas radiais de QUADS (colar -> hitsu-ana -> aba), aba de laca inclinada para fora nas duas
    faces, parede lateral de ferro, paredes dos hitsu-ana; colar (seppa-dai) = peca propria de 40 lados"""
    bm = mb.bm
    lb = lobes()
    cols = ring_columns(lb)
    N = len(cols)

    def P3(r, th, y):
        return Vector((px + math.cos(th) * r, PY + y, SZ + math.sin(th) * r))
    V = []                      # por coluna: dict de vertices (frente 'f' / costas 'b')
    for th, u in cols:
        rO = contour_r(th, 0.0, lb)
        rL = max(contour_r(th, RIM_T, lb), COL_R + 0.5)
        cv = {}
        for side, sy in (("f", -1), ("b", 1)):
            vB = bm.verts.new(P3(R_B, th, sy * FACE_Y))
            vHi = bm.verts.new(P3(HOLE_R, th, sy * FACE_Y))
            if u is not None and abs(u) < 0.999:
                w = HOLE_W * (1.0 - u * u) ** 0.6
                vHo = bm.verts.new(P3(HOLE_R + w, th, sy * FACE_Y))
            else:
                vHo = vHi
            vL = bm.verts.new(P3(rL, th, sy * FACE_Y))
            vO = bm.verts.new(P3(rO, th, sy * LIP_Y))
            cv[side] = (vB, vHi, vHo, vL, vO)
        V.append(cv)
    web, lip, wall = [], [], []
    for c in range(N):
        c2 = (c + 1) % N
        for side in ("f", "b"):
            B0, Hi0, Ho0, L0, O0 = V[c][side]
            B1, Hi1, Ho1, L1, O1 = V[c2][side]
            fs = [(B0, B1, Hi1, Hi0), (Ho0, Ho1, L1, L0)]
            for q in fs:
                web.append(bm.faces.new(q if side == "b" else q[::-1]))
            q = (L0, L1, O1, O0)
            lip.append(bm.faces.new(q if side == "b" else q[::-1]))
        Of0, Ob0 = V[c]["f"][4], V[c]["b"][4]
        Of1, Ob1 = V[c2]["f"][4], V[c2]["b"][4]
        wall.append(bm.faces.new((Of0, Of1, Ob1, Ob0)))
        # paredes dos hitsu-ana (entre duas colunas do mesmo furo)
        if cols[c][1] is not None and cols[c2][1] is not None and cols[c2][1] > cols[c][1]:
            for k in (1, 2):
                a0, a1 = V[c]["f"][k], V[c2]["f"][k]
                b0, b1 = V[c]["b"][k], V[c2]["b"][k]
                if a0 is a1:
                    continue
                q = (a0, a1, b1, b0)
                try:
                    wall.append(bm.faces.new(q if k == 2 else q[::-1]))
                except ValueError:
                    pass
    post_faces(mb, web, IRON)
    post_faces(mb, lip, LAC, smooth=True)
    post_faces(mb, wall, IRON)
    # colar (seppa-dai) em relevo: anel aberto de 40 lados, bordas enterradas na face
    NC = 32
    CP = [(COL_R + 0.02, -0.5), (7.94, -0.92), (7.58, -0.92), (7.58, 0.92), (7.94, 0.92), (COL_R + 0.02, 0.5)]
    crow = [[bm.verts.new(P3(r, math.tau * i / NC, y)) for i in range(NC)] for r, y in CP]
    fc = []
    for j in range(len(CP) - 1):
        for i in range(NC):
            i2 = (i + 1) % NC
            fc.append(bm.faces.new((crow[j][i], crow[j][i2], crow[j + 1][i2], crow[j + 1][i])))
    post_faces(mb, fc, IRON)
    _DBG["ring_cols"] = N
    _DBG["ring_rows"] = [[V[c]["f"][4].co.copy() for c in range(N)], [V[c]["b"][4].co.copy() for c in range(N)]]
    return lb


def back_ring(mb, px):
    """anel de laca nas costas da tampa (kamon simples): as costas deixam de ser um disco preto chapado"""
    y0 = PY + PO.DISH_D + 0.45
    n = 32
    prof = [(4.55, 0.0), (4.62, 0.16), (5.38, 0.16), (5.45, 0.0)]
    bm = mb.bm
    R = [[bm.verts.new(Vector((px + math.cos(math.tau * i / n) * r, y0 - 0.03 + h, SZ + math.sin(math.tau * i / n) * r)))
          for i in range(n)] for r, h in prof]
    fs = []
    for j in range(len(prof) - 1):
        for i in range(n):
            i2 = (i + 1) % n
            fs.append(bm.faces.new((R[j][i], R[j][i2], R[j + 1][i2], R[j + 1][i])))
    post_faces(mb, fs, LAC, smooth=False)


# ------------------------------------------------------------------ PEDRA SAGRADA (iwakura)
def rock_prof(top, hf, hb):
    """secao (y relativo a PYC, z relativo a T): base recolhida, cintura (mais larga) em ZG, ombro, topo plano"""
    zg = min(ZG, top - 0.5)
    sh = zg + 0.55 * (top - zg)
    kf, kb = min(0.5, 0.2 * hf), min(0.5, 0.2 * hb)
    return [(-(hf - 0.5), Z_BOT), (-(hf - 0.12), 0.55), (-hf, zg), (-(hf - 0.22), sh), (-(hf - kf), top),
            (hb - kb, top), (hb - 0.22, sh), (hb, zg), (hb - 0.12, 0.55), (hb - 0.5, Z_BOT)]


def rock_stations():
    return [(-x, t, f, b) for x, t, f, b in reversed(ROCK_ST[1:])] + list(ROCK_ST)


def rock(mb, px, rng):
    rings = []
    st = rock_stations()
    n = len(st)
    for i, (x, top, hf, hb) in enumerate(st):
        pr = rock_prof(top, hf, hb)
        end = i in (0, n - 1)
        ring = []
        for k, (yy, zz) in enumerate(pr):
            keep = k in (2, 7) or end            # cintura intacta (a corda encosta nela)
            jx = 0.0 if keep else rng.uniform(-0.1, 0.1)
            jy = 0.0 if keep else rng.uniform(-0.12, 0.12)
            jz = rng.uniform(-0.08, 0.08) if (k in (1, 3, 6, 8) and not end) else 0.0
            ring.append(Vector((px + x + jx, PYC + yy + jy, T + zz + jz)))
        rings.append(ring)
    _r, faces = loft_rings(mb, rings, ROCK, caps=True)
    bmesh.ops.recalc_face_normals(mb.bm, faces=faces)
    vs = list({v for f in faces for v in f.verts})
    idx = {v: i for i, v in enumerate(vs)}
    return BVHTree.FromPolygons([v.co.copy() for v in vs], [[idx[v] for v in f.verts] for f in faces])


def rope_path(px):
    """contorno da pedra na cintura (ZG), afastado 0.6; pontas arredondadas em elipse; comeca atras, no meio"""
    st = [s for s in rock_stations() if s[1] >= ZG + 0.35]
    off = 0.6
    front = [Vector((px + x, PYC - hf - off, T + ZG)) for x, t, hf, hb in st]
    back = [Vector((px + x, PYC + hb + off, T + ZG)) for x, t, hf, hb in st]

    def cap(x, hf, hb, sgn):
        yc = PYC + (hb - hf) / 2
        ry = (hf + hb) / 2 + off
        return [Vector((px + x + sgn * math.cos(-math.pi / 2 + math.pi * i / 8) * off,
                        yc + math.sin(-math.pi / 2 + math.pi * i / 8) * ry, T + ZG)) for i in range(1, 8)]
    xr, tr, hfr, hbr = st[-1]
    xl, tl, hfl, hbl = st[0]
    right = cap(xr, hfr, hbr, 1)
    left = cap(xl, hfl, hbl, -1)[::-1]
    loop = chaikin(front + right + back[::-1] + left, 1)
    i0 = min(range(len(loop)), key=lambda i: (loop[i] - Vector((px, PYC + 5.2, T + ZG))).length)
    return loop[i0:] + loop[:i0]


def shimenawa(mb, px):
    """2 pernas lisas torcidas, passo regular (numero inteiro de voltas no laco fechado: a emenda nao aparece)"""
    loop = rope_path(px)
    dense = resample(loop + [loop[0]], 0.25)
    Lr = path_len(dense)
    pitch = Lr / max(1, round(Lr / 5.4))
    nseg = int(round(Lr / pitch)) * 4
    pts = resample(dense, Lr / nseg)
    if len(pts) > nseg + 1:
        pts = pts[:nseg + 1]
    pts[-1] = pts[0].copy()
    pts_, Tn, Nn, Bn = K.frames(pts)
    arc = [0.0]
    for p0, p1 in zip(pts, pts[1:]):
        arc.append(arc[-1] + (p1 - p0).length)
    r = 0.55
    for k in range(2):
        cen = []
        for p, nn, bb, s in zip(pts, Nn, Bn, arc):
            ang = math.tau * s / pitch + math.pi * k
            cen.append(p + (nn * math.cos(ang) + bb * math.sin(ang)) * r * 0.44)
        nf = len(mb.bm.faces)
        K.taper_tube(mb, cen, [r * 0.62] * len(cen), ROPE, 5)
        mb.bm.faces.ensure_lookup_table()
        for i in range(nf, len(mb.bm.faces)):
            mb.bm.faces[i].smooth = True
    return loop


def shide(mb, p, h=1.5, w=0.46):
    """papel em zigue-zague (3 dobras), pendurado encostado na corda; p = ponto de fixacao (topo)"""
    cz = [(0.0, 0.0), (0.24, -0.38), (-0.04, -0.76), (0.24, -1.14), (0.02, -1.5)]
    cz = [(a * h / 1.5, b * h / 1.5) for a, b in cz]
    left = [(a - w / 2, b) for a, b in cz]
    right = [(a + w / 2, b) for a, b in cz]
    K.plate(mb, left + right[::-1], p, (1, 0, 0), (0, 0, 1), 0.07, CREAM)


# ------------------------------------------------------------------ KATANA NICHIRIN
def blade_sec(W):
    """secao da lamina (u = para o fio, v = espessura): dorso, shinogi, lamina preta, filete vermelho, fio claro"""
    th = BL_TH
    ur = -W + 0.62 * W
    uf0 = W - EDGE_W - FIL_W
    uf1 = W - EDGE_W

    def t(u):
        return th * (W - u) / (W - ur) * 0.9 + 0.015
    pts = [(-W, -0.12), (ur, -th), (uf0, -t(uf0)), (uf1, -t(uf1)), (W, 0.0), (uf1, t(uf1)), (uf0, t(uf0)),
           (ur, th), (-W, 0.12)]
    mats = [IRON, IRON, RED, STEEL, STEEL, RED, IRON, IRON, IRON]
    return pts, mats


GRIP_TH = [D(t) for t in (0, 28, 52, 90, 128, 152, 180, 208, 232, 270, 308, 332)]


def ell(A_, B_):
    return [(math.cos(t) * A_, math.sin(t) * B_) for t in GRIP_TH]


def tsuka(mb, P, s0, s1, nd=4, depth=0.12, waist=0.07):
    """cabo oval de 12 lados com cintura; fundo PRETO (as fitas) com LOSANGOS CREME rebaixados nas duas faces
    (+y e -y). Cada losango = 4 triangulos em volta de um vertice central afundado 'depth'."""
    bm = mb.bm
    Pd = (s1 - s0) / nd
    a = 0.36 * Pd
    rows, kinds = [s0], ["n"]
    for k in range(nd):
        c = s0 + Pd * (k + 0.5)
        rows += [c - a, c, c + a]
        kinds += ["lo", "c", "hi"]
    rows.append(s1)
    kinds.append("n")

    def rad(s):
        f = (s - s0) / (s1 - s0)
        w = 1.0 - waist * math.sin(math.pi * f)
        return GRIP_A * w, GRIP_B * w
    V = []
    for s, kd in zip(rows, kinds):
        A_, B_ = rad(s)
        row = []
        for j, t in enumerate(GRIP_TH):
            u, v = math.cos(t) * A_, math.sin(t) * B_
            if kd == "c" and j in (3, 9):
                v = math.copysign(B_ - depth, v)
            row.append(bm.verts.new(P(s, u, v)))
        V.append(row)
    dark, cream = [], []
    n = len(GRIP_TH)
    for i in range(len(rows) - 1):
        r0, r1 = V[i], V[i + 1]
        k0 = kinds[i]
        for j in range(n):
            j2 = (j + 1) % n
            if k0 == "lo" and j in (2, 3, 8, 9):
                if j in (2, 8):     # lado esquerdo do losango: diagonal lo[j+1] -> c[j]
                    dark.append(bm.faces.new((r0[j], r0[j2], r1[j])))
                    cream.append(bm.faces.new((r0[j2], r1[j2], r1[j])))
                else:               # lado direito: diagonal lo[j] -> c[j+1]
                    dark.append(bm.faces.new((r0[j], r0[j2], r1[j2])))
                    cream.append(bm.faces.new((r0[j], r1[j2], r1[j])))
            elif k0 == "c" and j in (2, 3, 8, 9):
                if j in (2, 8):     # diagonal c[j] -> hi[j+1]
                    cream.append(bm.faces.new((r0[j], r0[j2], r1[j2])))
                    dark.append(bm.faces.new((r0[j], r1[j2], r1[j])))
                else:               # diagonal c[j+1] -> hi[j]
                    cream.append(bm.faces.new((r0[j], r0[j2], r1[j])))
                    dark.append(bm.faces.new((r0[j2], r1[j2], r1[j])))
            else:
                dark.append(bm.faces.new((r0[j], r0[j2], r1[j2], r1[j])))
    post_faces(mb, dark, IRON)
    post_faces(mb, cream, CREAM)


def sword(mb, px, sg, rock_top):
    """sg=+1: cabo no alto-direita (lamina desce a esquerda); sg=-1 espelhada."""
    a, e = sw_basis(sg)
    yv = Vector((0, 1, 0))
    o = Vector((px, SW_Y[sg], SZ + HC))

    def Pst(s, u, v):           # parte reta (habaki para cima)
        return o + a * s + e * u + yv * v

    cr, sr = math.cos(BL_ROLL), math.sin(BL_ROLL)

    def Pbl(s, u, v):           # lamina curva, girada BL_ROLL no proprio eixo (costas da lamina voltadas para cima)
        c, t, nrm = sw_axis(sg, s, px)
        return c + (nrm * cr - yv * sr) * u + (yv * cr + nrm * sr) * v

    def Phb(s, u, v):           # habaki: acompanha o giro da lamina
        return o + a * s + (e * cr - yv * sr) * u + (yv * cr + e * sr) * v

    def W(s):
        d = max(0.0, S_HAB - s)
        return BW_H + (BW_T - BW_H) * min(1.0, d / 24.0)
    s_u, s_d = sword_frame()
    # entrada na pedra: primeiro s (lamina de baixo) em que o lado do fio fica 0.3 abaixo da superficie
    s_ent, s = None, -s_d
    while s > -26.0:
        q = Pbl(s, W(s), 0.0)
        zs = rock_top(q.x, q.y)
        if zs is not None and q.z < zs - 0.3:
            s_ent = s
            break
        s -= 0.05
    if s_ent is None:
        s_ent = -16.0
    s_ax = -s_d                 # onde o EIXO entra (boca, base das lascas)
    while s_ax > s_ent - 2.0:
        q = Pbl(s_ax, 0.0, 0.0)
        zs = rock_top(q.x, q.y)
        if zs is not None and q.z <= zs:
            break
        s_ax -= 0.05
    # lamina: da habaki (um pouco dentro dela) ate a ponta enterrada
    k0 = s_ent - 0.35
    st = [S_HAB + 0.3, S_HAB, S_HAB - 2.0, 3.0, -3.0, -8.0, -s_d - 1.2, s_ent + 0.8, k0]
    st = sorted({round(x, 3) for x in st if x >= k0}, reverse=True)
    rings = []
    for s_ in st:
        pts, mats = blade_sec(W(s_))
        rings.append([Pbl(s_, u, v) for u, v in pts])
    # kissaki (enterrada): afunila para um ponto perto do dorso
    tipc = (-0.55 * BW_T, 0.0)
    for s_, f in ((k0 - 0.7, 0.55), (k0 - 1.3, 0.06)):
        pts, mats = blade_sec(W(s_))
        rings.append([Pbl(s_, tipc[0] + (u - tipc[0]) * f, v * max(f, 0.15)) for u, v in pts])
    _pts, mats = blade_sec(BW_H)
    loft_sec(mb, rings, mats, caps=(IRON, IRON))
    # habaki creme (manga em volta da lamina), levemente conica: marca a juncao lamina/tsuba
    hb0, hb1 = S_HAB, S_HAB + HAB_L
    loft_rings(mb, [[Phb(s_, u, v) for u, v in oct_prof(2 * BW_H + w_, 2 * BL_TH + 0.14 + w_ * 0.4, 0.12)]
                    for s_, w_ in ((hb0, 0.2), (hb1, 0.3))], CREAM)
    # tsuba: UM disco oval de 16 lados, perpendicular ao eixo, com chanfro
    ts0, ts1 = hb1, hb1 + TSU_T
    ring = [(math.cos(math.tau * i / 16), math.sin(math.tau * i / 16)) for i in range(16)]
    tr = []
    for s_, f in ((ts0, 0.94), (ts0 + 0.07, 1.0), (ts1, 1.0)):
        tr.append([Pst(s_, cu * TSU_RE * f, sv * TSU_RY * f) for cu, sv in ring])
    loft_rings(mb, tr, IRON)
    _DBG.setdefault("tsuba_small", []).extend([p for r in tr for p in r])
    # fuchi (colar de ferro) + cabo + kashira (ferro arredondado com anel de laca)
    f0, f1 = ts1 - 0.02, ts1 + FUCHI_L
    loft_rings(mb, [[Pst(s_, u, v) for u, v in ell(GRIP_A * 1.06, GRIP_B * 1.06)] for s_ in (f0, f1)], IRON)
    g0, g1 = f1 - 0.04, f1 - 0.04 + TSUKA_L
    tsuka(mb, Pst, g0, g1)
    k_0 = g1 - 0.04
    KR = [(k_0, 1.07, IRON), (k_0 + 0.02, 1.09, LAC), (k_0 + 0.17, 1.07, IRON), (k_0 + 0.4, 0.93, IRON),
          (k_0 + 0.54, 0.56, None)]
    kr = [[Pst(s_, u, v) for u, v in ell(GRIP_A * f, GRIP_B * f)] for s_, f, _m in KR]
    bm = mb.bm
    R = [[bm.verts.new(p) for p in r] for r in kr]
    by = {}
    for i in range(len(R) - 1):
        m = KR[i][2]
        for j in range(12):
            j2 = (j + 1) % 12
            by.setdefault(m, []).append(bm.faces.new((R[i][j], R[i][j2], R[i + 1][j2], R[i + 1][j])))
    by[IRON].append(bm.faces.new(R[0][::-1]))
    for m, fs in by.items():
        post_faces(mb, fs, m)
    kt = Pst(k_0 + KASH_L, 0.0, 0.0)
    fan_to(mb, R[-1], kt, IRON)
    ent, _t, _n = sw_axis(sg, s_ax, px)
    _DBG.setdefault("blade", []).append([Pbl(s_, u, v) for s_ in (s_ent, s_ent - 0.5, k0, k0 - 0.7)
                                         for u, v in blade_sec(W(s_))[0]])
    vis_s = [-s_d - 0.25 * i for i in range(int((-s_ent - s_d) / 0.25) + 1)]
    _DBG.setdefault("blade_vis", []).extend([Pbl(s_, u, v) for s_ in vis_s for u, v in blade_sec(W(s_))[0]])
    _DBG.setdefault("sword", []).append({"s_u": s_u, "s_d": s_d, "s_ent": s_ent, "s_ax": s_ax, "top": kt,
                                         "ent": ent})
    return ent


def mouth_chips(mb, bvh, ent, side, rng):
    """3 lascas volumetricas na boca da lamina (pedra 'rachada pela espada') + 2 rachaduras escuras saindo da boca"""
    def snap(p):
        loc, nrm, _i, _d = bvh.find_nearest(p)
        return loc, nrm
    for dx, dy, sz in ((0.8, -0.6, 0.6), (-0.6, -0.75, 0.5), (0.15, 0.9, 0.45)):
        loc, nrm = snap(Vector((ent.x + side * dx, ent.y + dy, ent.z + 0.2)))
        if loc is None:
            continue
        away = (Vector((loc.x - ent.x, loc.y - ent.y, 0.0)))
        if away.length < 1e-3:
            away = Vector((side, 0, 0))
        up = (nrm * 1.0 + away.normalized() * 0.55).normalized()
        chip(mb, loc - nrm * 0.05, up, away.normalized().cross(Vector((0, 0, 1))) + Vector((0.01, 0, 0)), sz, ROCK, rng)
    # 2 rachaduras rentes a superficie: uma desce pela face da frente, outra corre para fora pelo topo
    bm = mb.bm
    for path, w0 in ((((0.0, -0.55, -0.05), (0.3, -1.3, -0.4), (0.1, -2.1, -0.65), (0.35, -2.9, -0.9)), 0.13),
                     (((0.5, -0.1, 0.0), (1.3, -0.35, -0.1), (2.0, -0.2, -0.2)), 0.1)):
        pts = []
        for dx, dy, dz in path:
            loc, nrm = snap(Vector((ent.x + side * dx, ent.y + dy, ent.z + dz)))
            if loc is not None:
                pts.append((loc, nrm))
        for i, ((p0, n0), (p1, n1)) in enumerate(zip(pts, pts[1:])):
            nn = (n0 + n1).normalized()
            td = p1 - p0
            if td.length < 1e-3:
                continue
            f0 = 1.0 - i / len(pts)
            f1 = 1.0 - (i + 1) / len(pts)
            sd = td.cross(nn).normalized() * w0
            vs = [bm.verts.new(p0 + sd * f0 + nn * 0.03), bm.verts.new(p0 - sd * f0 + nn * 0.03),
                  bm.verts.new(p0 - nn * 0.16),
                  bm.verts.new(p1 + sd * max(f1, 0.25) + nn * 0.03), bm.verts.new(p1 - sd * max(f1, 0.25) + nn * 0.03),
                  bm.verts.new(p1 - nn * 0.16)]
            fs = [bm.faces.new((vs[0], vs[1], vs[2])), bm.faces.new((vs[3], vs[5], vs[4])),
                  bm.faces.new((vs[0], vs[3], vs[4], vs[1])), bm.faces.new((vs[1], vs[4], vs[5], vs[2])),
                  bm.faces.new((vs[2], vs[5], vs[3], vs[0]))]
            post_faces(mb, fs, IRON)


# ------------------------------------------------------------------ GLICINIA
def blob(mb, c, rx, ry, rz, m, nu=14, nv=6, rot=0.0, smooth=True):
    """massa arredondada LISA (elipsoide), polos em leque"""
    bm = mb.bm
    rings = []
    for i in range(1, nv):
        ph = -math.pi / 2 + math.pi * i / nv
        cz, rr = math.sin(ph), math.cos(ph)
        rings.append([bm.verts.new((c.x + math.cos(rot + math.tau * j / nu) * rx * rr,
                                    c.y + math.sin(rot + math.tau * j / nu) * ry * rr, c.z + rz * cz))
                      for j in range(nu)])
    bot = bm.verts.new((c.x, c.y, c.z - rz))
    top = bm.verts.new((c.x, c.y, c.z + rz))
    fs = []
    for j in range(nu):
        j2 = (j + 1) % nu
        fs.append(bm.faces.new((rings[0][j2], rings[0][j], bot)))
        fs.append(bm.faces.new((rings[-1][j], rings[-1][j2], top)))
    for r0, r1 in zip(rings, rings[1:]):
        for j in range(nu):
            j2 = (j + 1) % nu
            fs.append(bm.faces.new((r0[j], r0[j2], r1[j2], r1[j])))
    post_faces(mb, fs, m, smooth=smooth)


def under(c, rx, ry, rz, x, y):
    """z da face de baixo do elipsoide em (x, y) (None fora)"""
    q = 1.0 - ((x - c.x) / rx) ** 2 - ((y - c.y) / ry) ** 2
    if q <= 0:
        return None
    return c.z - rz * math.sqrt(q)


CAS_N = 7                    # lados das camadas de petalas (laterais lisas, topo e fundo retos)
TIER_STEP = 0.85             # altura visivel de cada camada: o cacho tem 2-5 camadas conforme o comprimento visivel
TIER_R = (1.12, 0.6)         # raio da borda da 1a e da ultima camada (x r0): cheio no alto, afina ate a ponta
TIER_TOP = 0.4               # raio do topo de cada camada (x raio da borda): sino de petalas, nao cilindro
TIER_IN = 0.35               # quanto cada camada sobe para dentro da de cima (x altura visivel): petalas sobrepostas
ZIG = 0.1                    # zigue-zague lateral das camadas (alterna o lado): quebra o eixo reto de pingente
HIDE = 0.45                  # trecho do eixo escondido dentro da copa


def cascade_plan(r0, vis, top, sway, lat, hide=HIDE):
    """cacho de glicinia = pilha de 2-5 CAMADAS DE PETALAS em sino (borda larga embaixo, topo estreito escondido
    dentro da camada de cima), cheio no alto e afinando para a ponta, com eixo curvo (sway quadratico: pende reto
    junto da copa e abre na ponta) e leve zigue-zague (lat = direcao unitaria).
    Devolve (pontos, raios, n): pontos[0] = topo escondido na copa, pontos[k+1] = centro da borda da camada k."""
    n = max(2, min(5, int(round(vis / TIER_STEP))))
    total = vis + hide

    def at(u, off=0.0):
        f = (hide + u * vis) / total
        return top - Vector((0, 0, total * f)) + sway * (f * f) + lat * off
    pts, rad = [top], [r0 * TIER_R[0] * TIER_TOP]
    for k in range(n):
        pts.append(at((k + 1) / n, ZIG * (1 if k % 2 else -1)))
        rad.append(r0 * (TIER_R[0] + (TIER_R[1] - TIER_R[0]) * k / (n - 1)))
    return pts, rad, n


def bell(mb, a, b, ra, rb, m, n=CAS_N, rot=0.0):
    """tronco de cone fechado de a (raio ra) ate b (raio rb): laterais lisas, tampas retas (a borda fica viva)"""
    bm = mb.bm
    d = (b - a).normalized()
    u = d.orthogonal().normalized()
    v = d.cross(u)
    RA = [bm.verts.new(a + (u * math.cos(rot + math.tau * j / n) + v * math.sin(rot + math.tau * j / n)) * ra)
          for j in range(n)]
    RB = [bm.verts.new(b + (u * math.cos(rot + math.tau * j / n) + v * math.sin(rot + math.tau * j / n)) * rb)
          for j in range(n)]
    sides = [bm.faces.new((RA[j], RA[(j + 1) % n], RB[(j + 1) % n], RB[j])) for j in range(n)]
    caps = [bm.faces.new(RA), bm.faces.new(RB[::-1])]
    bmesh.ops.recalc_face_normals(bm, faces=sides + caps)
    post_faces(mb, sides, m, smooth=True)
    post_faces(mb, caps, m, smooth=False)


def cascade(mb, pts, radii, n, rot=0.0):
    """CACHO de glicinia: camadas de petalas em sino empilhadas (silhueta serrilhada de flor, nunca cone liso de
    gelo), cor por camada (lilas forte no alto -> medio -> claro rosado) e um BOTAO rombo na ponta"""
    cols = [WIS if t < 0.4 else (WIS_MID if t < 0.75 else WIS_TIP) for t in (k / (n - 1) for k in range(n))]
    for k in range(n):
        rim, rk = pts[k + 1], radii[k + 1]
        up = pts[k] - rim
        a = pts[0] if k == 0 else pts[k] + up * TIER_IN
        bell(mb, a, rim, rk * TIER_TOP, rk, cols[k], rot=rot + 0.45 * k)
    rim, rl = pts[-1], radii[-1]
    d = (pts[-1] - pts[-2]).normalized()
    tipp = rim + d * rl * 0.62
    bell(mb, rim - d * rl * 0.15, tipp, rl * 0.64, rl * 0.3, WIS_TIP, rot=rot)     # botao da ponta (rombo)
    return tipp


# cameras de avaliacao (as do estudio): a folga cascata-aro e medida nelas, projetando no plano do aro
def _cams(px):
    return {"A_Hero": (Vector((px, PY - 44.0, T + 9.0)), 1.2), "G_Far": (Vector((px * 0.35, -30.0, 18.0)), 0.4)}


def ring_outline(lb, n=240):
    return [(math.cos(math.tau * i / n) * contour_r(math.tau * i / n, 0.0, lb),
             math.sin(math.tau * i / n) * contour_r(math.tau * i / n, 0.0, lb)) for i in range(n)]


def ring_left(zr, poly):
    """x mais a esquerda do contorno do aro na altura zr (relativo ao centro); None fora do aro"""
    xs = []
    n = len(poly)
    for i in range(n):
        (x0, z0), (x1, z1) = poly[i], poly[(i + 1) % n]
        if (z0 - zr) * (z1 - zr) <= 0 and z0 != z1:
            xs.append(x0 + (x1 - x0) * (zr - z0) / (z1 - z0))
    return min(xs) if xs else None


def ring_gap(p, px, poly, cams):
    """menor folga (no plano da face do aro) entre o ponto p e a borda esquerda do aro, nas cameras de avaliacao,
    ja descontada a folga exigida de cada camera"""
    g = 99.0
    for cam, need in cams.values():
        t = (PY - LIP_Y - cam.y) / (p.y - cam.y)
        q = cam + (p - cam) * t
        xl = ring_left(q.z - SZ, poly)
        if xl is not None:
            g = min(g, (xl - (q.x - px)) - need)
    return g


def seg_dist(p, a, b):
    ab = b - a
    t = max(0.0, min(1.0, (p - a).dot(ab) / max(ab.length_squared, 1e-9)))
    return (p - (a + ab * t)).length


def wis_layout(px):
    """tronco lider, galho lateral, massas da copa (lilas forte), massas da borda (lilas medio) e pontos das cascatas"""
    def P(x, y, z):
        return Vector((px + x, y, T + z))
    tr = [P(-13.0, 109.6, -0.3), P(-12.35, 109.75, 2.8), P(-13.1, 110.05, 5.8), P(-12.15, 110.3, 8.6),
          P(-11.8, 110.45, 11.0), P(-11.55, 110.55, 13.4), P(-11.4, 110.6, 15.6), P(-11.3, 110.65, 17.7)]
    tr_r = [0.95, 0.84, 0.76, 0.68, 0.62, 0.56, 0.5, 0.44]
    br = [tr[3].lerp(tr[4], 0.5), P(-12.4, 108.95, 12.3), P(-12.2, 107.6, 16.1)]     # galho lateral unico
    br_r = [0.4, 0.32, 0.25]
    #          centro                      rx    ry    rz
    masses = [(P(-11.9, 107.5, 16.9), 1.9, 2.0, 1.35),       # frente
              (P(-11.3, 110.4, 17.9), 2.5, 2.7, 1.6),        # meio (largo: o guarda-chuva)
              (P(-11.9, 110.7, 18.85), 1.75, 2.0, 1.1),      # coroa (baixa: guarda-chuva, nao bola)
              (P(-12.0, 113.4, 17.0), 1.85, 2.1, 1.35)]      # tras
    edge = [(P(-12.3, 105.55, 16.2), 1.05, 1.0, 0.85),       # bico da frente
            (P(-12.95, 108.9, 15.75), 0.9, 1.1, 0.8),        # borda de fora
            (P(-12.35, 115.45, 16.3), 1.0, 1.05, 0.85),      # bico de tras
            (P(-10.55, 111.9, 18.95), 1.1, 1.2, 0.85)]       # coroa (lado do aro)
    #        x       y     visivel  r0    (cachos em grupos de 2-3 bem desiguais: cortina de fora, 2a fileira, frente e
    #                                    curtos no lado do aro)
    spots = [(-13.2, 105.75, 3.4, 0.52), (-13.2, 107.3, 1.9, 0.48),                                   # grupo da frente
             (-13.25, 108.45, 2.3, 0.46), (-13.25, 110.0, 5.6, 0.56), (-13.2, 111.4, 3.2, 0.54),     # grupo do meio
             (-13.2, 112.8, 4.8, 0.55), (-13.15, 114.2, 2.2, 0.5),                                 # grupo de tras
             (-12.1, 106.5, 2.7, 0.5), (-12.0, 109.3, 3.9, 0.5),                                   # 2a fileira
             (-12.2, 104.95, 2.6, 0.5), (-11.2, 105.9, 1.6, 0.46),                                  # frente
             (-10.9, 107.6, 1.3, 0.465), (-11.7, 112.1, 1.1, 0.465)]                               # lado do aro
    return tr, tr_r, br, br_r, masses, edge, spots


def wisteria(mb, px, rng, lb):
    """lateral esquerda, perto do plano do aro. TRONCO LIDER retorcido (2 curvas em S; base 0.95 + raiz alargada) que
    sobe inteiro ate dentro da massa do meio (a forquilha fica escondida na copa) e UM galho lateral mais fino saindo
    mais abaixo (T+9.8) para a massa da frente. Copa em GUARDA-CHUVA: 4 massas lisas lilas + 4 massas menores em lilas
    medio na borda (quebram o contorno: arvore em flor). CASCATAS finas (r0 0.45-0.6) em cone longo liso, 3 faixas de
    cor e ponta arredondada, pendendo de toda a borda (cortina de fora, frente, tras e curtas no lado do aro). Cada
    cascata e encurtada (ou descartada) ate nao cruzar o aro nas cameras A_Hero e G_Far nem tocar tronco/galho."""
    X, Yb = px + TRUNK_XY[0], TRUNK_XY[1]
    zg = T + 0.22
    tr, tr_r, br, br_r, masses, edge, spots = wis_layout(px)
    tube(mb, tr, tr_r, 8, lambda i, j: BARK, smooth=True, cap0=True)
    K.cone(mb, (X + 0.05, Yb, zg - 0.25), (X + 0.12, Yb + 0.03, zg + 1.25), 0.98, 0.8, BARK, 8)   # raiz alargada
    tube(mb, br, br_r, 6, lambda i, j: BARK, smooth=True, cap0=False)
    for c, rx, ry, rz in masses:
        blob(mb, c, rx, ry, rz, CANOPY, nu=12, nv=6, rot=rng.uniform(0, 1))
    for c, rx, ry, rz in edge:
        blob(mb, c, rx, ry, rz, WIS_MID, nu=10, nv=4, rot=rng.uniform(0, 1))
    allm = masses + edge
    trunk_segs = [(a, b, r) for a, b, r in zip(tr, tr[1:], tr_r)] + [(a, b, r) for a, b, r in zip(br, br[1:], br_r)]
    poly = ring_outline(lb)
    cams = _cams(px)
    placed, vis_pts = [], []
    for x, y, ln, r0 in spots:
        x, y = px + x + rng.uniform(-0.05, 0.05), y + rng.uniform(-0.08, 0.08)
        r0 *= rng.uniform(0.97, 1.03)
        x = max(x, px - 13.95 + r0 * TIER_R[0] + ZIG + 0.03)
        zs = [under(c, rx, ry, rz, x, y) for c, rx, ry, rz in allm]
        zs = [z for z in zs if z is not None]
        if not zs:
            _DBG.setdefault("cascade_skip", []).append((round(x - px, 2), round(y, 2), "sem copa"))
            continue
        zu = min(zs)
        ztop = zu + HIDE
        sx = rng.uniform(0.05, 0.2) if x - px < -12.8 else (rng.uniform(-0.2, -0.05) if x - px > -11.6 else 0.0)
        sway = Vector((sx, rng.choice((-1, 1)) * rng.uniform(0.2, 0.45), 0))    # ponta abre para a frente/tras
        a_ = rng.uniform(0, math.tau)
        lat = Vector((math.cos(a_), math.sin(a_), 0))
        ln += rng.uniform(-0.2, 0.2)

        def fail(pts_, rad_):
            for p, r in zip(pts_[1:], rad_[1:]):
                if p.x - r < px - 13.95:
                    return "lote"
                if ring_gap(Vector((p.x + r, p.y, p.z)), px, poly, cams) < 0.0:
                    return "aro"
                for a_, b_, rr in trunk_segs:
                    if p.z < zu - 0.3 and seg_dist(p, a_, b_) < r + rr + 0.08:   # (dentro da copa nao aparece)
                        return "tronco"
                if p.z > zu - 0.2:                # (o trecho que ainda esta dentro da copa nao conta)
                    continue
                for q, qr in vis_pts:
                    if (p - q).length < r + qr + 0.03:     # vizinhas lado a lado, sem se atravessar
                        return "cascata"
            return ""
        why = ""
        plan = None
        for _try in range(40):
            plan = cascade_plan(r0, ln, Vector((x, y, ztop)), sway, lat, ztop - zu)
            why = fail(plan[0], plan[1])
            if not why:
                break
            ln -= 0.2
            if ln < 1.0:
                break
        else:
            why = "tentativas"
        if why:
            _DBG.setdefault("cascade_skip", []).append((round(x - px, 2), round(y, 2), why))
            continue
        placed.append(plan)
        vis_pts += [(q, qr) for q, qr in zip(plan[0], plan[1]) if q.z < zu - 0.2]
    tips = [cascade(mb, pts, rad, n, rot=rng.uniform(0, math.tau)) for pts, rad, n in placed]
    _DBG["racemes"] = tips
    _DBG["cascades"] = [(p, r) for p, r, _c in placed]
    _DBG["masses"] = allm
    _DBG["trunk"] = trunk_segs
    print("GLICINIA: %d cascatas (visiveis %s) | descartadas %s" % (
        len(placed), ", ".join("%.1f" % (p[1].z - p[-1].z) for p, _r, _c in placed), _DBG.get("cascade_skip", [])))
    col_box(A, (1.7, 1.7, 11.0), (X + 0.1, Yb + 0.2, T + 5.5))


# ------------------------------------------------------------------ LANTERNA chochin
def lantern(mb, x, y, side, idx):
    """poste de ferro robusto com braco; chochin pendurada: capsula (1.1 x 1.55), 16 lados, lisa, aneis pretos e
    capuz preto (kasa) pequeno em cima"""
    zg = T + 0.22
    mb.box((1.2, 1.2, 0.5), (x, y, zg + 0.22), (0, 0, 0), ROCK, 0.12)
    top = T + 4.95
    mb.box((0.72, 0.72, top - zg - 0.45), (x, y, (zg + 0.45 + top) / 2), (0, 0, 0), IRON, 0.1)
    hx = x + side * 1.25
    mb.beam(Vector((x - side * 0.22, y, top - 0.28)), Vector((hx + side * 0.34, y, top - 0.28)), 0.5, 0.48, IRON, 0.08)
    zt = top - 0.48
    mb.box((0.14, 0.14, 0.3), (hx, y, zt - 0.08), (0, 0, 0), IRON, 0.0)
    H, Rw = 1.55, 0.55
    zt -= 0.2
    K.cone(mb, (hx, y, zt - 0.1), (hx, y, zt + 0.16), 0.74, 0.3, IRON, 12)      # capuz
    prof = [(0.0, 0.62, IRON), (0.12, 0.7, RED), (0.42, 0.96, RED), (0.84, 0.96, RED), (1.14, 0.7, IRON),
            (1.26, 0.62, None)]
    n = 12
    bm = mb.bm
    rings = [[bm.verts.new((hx + math.cos(math.tau * j / n) * Rw * k, y + math.sin(math.tau * j / n) * Rw * k,
                            zt - 0.1 - z * H / 1.26)) for j in range(n)] for z, k, _m in prof]
    by = {}
    for i in range(len(rings) - 1):
        m = prof[i][2]
        for j in range(n):
            j2 = (j + 1) % n
            by.setdefault(m, []).append(bm.faces.new((rings[i][j], rings[i][j2], rings[i + 1][j2], rings[i + 1][j])))
    by[IRON] += [bm.faces.new(rings[0]), bm.faces.new(rings[-1][::-1])]
    for m, fs in by.items():
        post_faces(mb, fs, m, smooth=(m == RED))
    zc = zt - 0.1 - 0.6 * H
    light("L_P_DemonSlayer_Lamp_%d" % idx, "POINT", (hx, y - 0.9, zc), 20, (1.0, 0.25, 0.12), 0.3)
    col_box(A, (1.1, 1.1, top - T + 0.2), (x, y, T + (top - T + 0.2) / 2))
    return zt


# ------------------------------------------------------------------ PISO: patio de cascalho liso, meio-fio, lajes
def court(mb, px):
    x0, x1, y0, y1 = px - 13.25, px + 13.25, Y0 + 0.3, PY + 8.6
    # frente do cascalho recuada 0.05 atras da face dos meios-fios (sem z-fighting)
    mb.box2((x0 + 0.03, y0 + 0.05, T - 0.3), (x1 - 0.03, y1, T + 0.22), GRAVEL, 0.0)
    cw, chh = 0.65, 0.5
    ty0, ty1 = TRUNK_XY[1] - 1.45, TRUNK_XY[1] + 1.35     # meio-fio esquerdo aberto no pe da glicinia
    for (a, b) in (((x0 - cw, y0), (x0, ty0)), ((x0 - cw, ty1), (x0, y1 + cw)), ((x1, y0), (x1 + cw, y1 + cw)),
                   ((x0, y1), (x1, y1 + cw)), ((x0, y0), (px - 3.4, y0 + cw)), ((px + 3.4, y0), (x1, y0 + cw))):
        mb.box2((a[0], a[1], T - 0.2), (b[0], b[1], T + chh), ROCK, 0.12)
    for (ya, yb_) in ((Y0 + 0.4, Y0 + 3.15), (Y0 + 3.35, Y0 + 6.1)):
        mb.box2((px - 3.0, ya, T - 0.2), (px + 3.0, yb_, T + 0.45), ROCK, 0.16)
    col_box2(A, (px - 3.0, Y0 + 0.4, T - 1.0), (px + 3.0, Y0 + 6.1, T + 0.45))
    # 2 degraus de pedra natural (topo plano) ate a plataforma; a shimenawa passa por tras do segundo
    pts = [(-1.0, -0.8), (-0.35, -1.0), (0.45, -0.95), (1.0, -0.6), (0.95, 0.75), (0.2, 1.0), (-0.6, 0.95), (-1.0, 0.5)]
    for (cx, cy, hw, hd, top, rot) in ((0.0, 106.72, 2.6, 0.58, 1.0, 0.03), (0.15, 107.72, 2.35, 0.52, 2.0, -0.04)):
        ca, sa = math.cos(rot), math.sin(rot)
        poly = [(px + cx + (u * hw) * ca - (v * hd) * sa, cy + (u * hw) * sa + (v * hd) * ca) for u, v in pts]
        mb.prism(poly, T - 0.2, T + top, ROCK, 0.15)
    col_box2(A, (px - 2.6, 106.1, T - 1.0), (px + 2.6, 107.3, T + 1.0))
    col_box2(A, (px - 2.3, 107.2, T - 1.0), (px + 2.3, 108.3, T + 2.0))


# ------------------------------------------------------------------ BUILD
def build(rng):
    px = _px()
    _DBG.clear()
    mb = K.LeanMB("PORTAL_%s_Tsuba" % KEY, C, rng, vcap=2)

    court(mb, px)
    bvh = rock(mb, px, rng)

    def rock_top(x, y):
        loc, _n, _i, _d = bvh.ray_cast(Vector((x, y, T + 30.0)), Vector((0, 0, -1)))
        return None if loc is None else loc.z
    _DBG["rock_bvh"] = bvh
    lb = tsuba_ring(mb, px)
    for sg in (1, -1):
        ent = sword(mb, px, sg, rock_top)
        mouth_chips(mb, bvh, ent, -sg, rng)

    # shimenawa na cintura + shide (4 na frente, 2 atras)
    loop = shimenawa(mb, px)
    _DBG["rope"] = resample(loop + [loop[0]], 0.3)

    def on_rope(x, front=True):
        cand = [p for p in loop if (p.y < PYC) == front]
        return min(cand, key=lambda q: abs(q.x - (px + x)))
    for xx in (-10.0, -6.6, 6.6, 10.0):
        p = on_rope(xx)
        shide(mb, Vector((p.x, p.y - 0.36, T + ZG - 0.12)))
    for xx in (-5.0, 5.0):
        p = on_rope(xx, False)
        shide(mb, Vector((p.x, p.y + 0.36, T + ZG - 0.12)))

    # lanternas ladeando o caminho, chochin voltada para as lajes (deixam livre a boca das laminas nos penedos)
    _DBG["lantern_top"] = []
    for sx, idx in ((-1, 1), (1, 2)):
        lantern(mb, px + sx * LAMP_X, 104.0, -sx, idx)
        _DBG["lantern_top"].append(Vector((px + sx * LAMP_X, 104.0, T + 5.1)))

    # glicinia (objeto proprio)
    mbw = K.LeanMB("PORTAL_%s_Wisteria" % KEY, C, rng, vcap=2)
    wisteria(mbw, px, rng, lb)
    mbw.finish()

    # colisoes: plataforma (ate o fundo da pedra), selas, penedos, anel da shimenawa, laterais do aro, laminas, costas
    col_box2(A, (px - 5.0, 109.6, T - 1.0), (px + 5.0, 117.9, T + 3.0))
    for sg in (-1, 1):
        col_box2(A, (px + sg * 5.0, 109.9, T - 1.0), (px + sg * 9.6, 117.9, T + 2.6))
        col_box2(A, (px + sg * 9.6, 110.2, T - 1.0), (px + sg * 10.8, 117.9, T + 3.3))
        col_box2(A, (px + sg * 10.8, 110.6, T - 1.0), (px + sg * 11.9, 117.6, T + 4.2))
        col_box2(A, (px + sg * 11.9, 108.9, T - 1.0), (px + sg * 13.1, 119.0, T + 2.55))     # ponta (corda)
        col_box2(A, (px + sg * 7.2, PY - 0.95, T + 5.2), (px + sg * 9.4, PY + 0.95, T + 8.2))    # lobo (baixo)
        col_box2(A, (px + sg * 8.0, PY - 0.95, T + 8.2), (px + sg * 10.8, PY + 0.95, T + 15.5))  # lobo lateral
        col_box2(A, (px + sg * 7.1, PY + 2.2, T + 2.6), (px + sg * 10.6, PY + 4.3, T + 6.6))    # lamina exposta
    col_box2(A, (px - 11.9, 108.2, T - 1.0), (px + 11.9, 109.9, T + 2.5))    # corda da frente (degrau 2.0->2.5->3.0)
    col_box2(A, (px - 11.9, 117.6, T - 1.0), (px + 11.9, 119.7, T + 2.55))   # corda de tras
    col_box2(A, (px - 7.6, PY + 0.4, T + 3.0), (px + 7.6, PY + 4.3, T + 19.0))

    back_ring(mb, px)
    PO.swirl(KEY, px, "P_DS_Swirl", mb, IRON, rim_y=-0.9)
    _unlit("P_DS_Swirl", SWIRL_EMIT)
    _unlit(GLOW, GLOW_EMIT, fm_lib.MATS[GLOW][4])
    _spec(IRON, 0.25)
    _spec(LAC, 0.2, 0.62)
    ob = mb.finish()
    return ob


# ------------------------------------------------------------------ ESCADA (dressing do lance 2)
# "a subida para Fujikasane": o lance 2 e ladeado por DOIS PARES de chochin vermelhas em postes negros (a lanterna do
# patio, menor: capuz preto, aneis de ferro, papel vermelho, braco para o lado da escada), um no pe e um na chegada.
# (Havia uma glicinia jovem no pe do lado direito; saiu na integracao: vista da roda d'agua a copa caia sobre a espiral
# e o portal ja tem 3 glicinias por perto - a propria e as duas do centro do terraco.)
# Faixa: y 85.5..99.6 e 7.8 <= |x - px| <= 13.9 no terraco (z = T, base enterrada no maximo ate T-0.4); nada no poco.
# Materiais: P_DS_Iron, P_DS_Red (so a paleta do portal). COL: os postes.
ST_XMIN, ST_XMAX = 7.8, 13.9            # |x - px| permitido
ST_YMIN, ST_YMAX = 85.5, 99.6
ST_POST = 0.6                           # secao do poste
ST_TOP = 4.3                            # topo do poste (T+): menor que as lanternas do patio (T+4.95)
ST_ARM = 1.2                            # braco para o lado da escada (a chochin pende sobre a borda do poco)
ST_H, ST_RW = 1.3, 0.47                 # chochin: altura / raio da barriga
ST_N = 10                               # lados da chochin e do capuz
ST_LAMPS = ((-1, 97.2, 10.1), (1, 97.2, 10.1),    # (lado, y, |x - px| do poste): o par da chegada
            (-1, 90.0, 10.1), (1, 90.0, 10.1))    # e o par do pe


def _st_chochin(mb, hx, y, zt, H=ST_H, Rw=ST_RW, n=ST_N):
    """chochin pendurada com o topo em zt: capuz preto, aneis de ferro e 3 faixas de papel vermelho (barriga lisa)"""
    K.cone(mb, (hx, y, zt - 0.09), (hx, y, zt + 0.13), Rw * 1.3, Rw * 0.5, IRON, n)
    prof = [(0.0, 0.62, IRON), (0.12, 0.72, RED), (0.42, 0.97, RED), (0.84, 0.97, RED), (1.14, 0.72, IRON),
            (1.26, 0.62, None)]
    bm = mb.bm
    z0 = zt - 0.09
    ang = [math.tau * (j + 0.5) / n for j in range(n)]
    rings = [[bm.verts.new((hx + math.cos(t) * Rw * k, y + math.sin(t) * Rw * k, z0 - z * H / 1.26)) for t in ang]
             for z, k, _m in prof]
    by = {}
    for i in range(len(rings) - 1):
        for j in range(n):
            j2 = (j + 1) % n
            by.setdefault(prof[i][2], []).append(
                bm.faces.new((rings[i][j], rings[i][j2], rings[i + 1][j2], rings[i + 1][j])))
    by[IRON] += [bm.faces.new(rings[0]), bm.faces.new(rings[-1][::-1])]
    for m, fs in by.items():
        post_faces(mb, fs, m, smooth=(m == RED))
    return z0 - H


def _st_lantern(mb, px, side, y, dx):
    """poste de ferro negro com braco para o lado da escada e chochin pendurada (a lanterna do patio, menor)"""
    x = px + side * dx
    zb, top = T - 0.3, T + ST_TOP
    mb.box((ST_POST, ST_POST, top - zb), (x, y, (zb + top) / 2), (0, 0, 0), IRON, 0.08)
    hx = x - side * ST_ARM
    za = top - 0.24
    mb.beam(Vector((x + side * 0.16, y, za)), Vector((hx - side * 0.3, y, za)), 0.4, 0.36, IRON, 0.0)
    _st_chochin(mb, hx, y, za - 0.18 - 0.1)          # (o capuz entra 0.03 no braco: sem faces coplanares)
    col_box(A, (0.9, 0.9, top - T + 0.3), (x, y, T + (top - T + 0.3) / 2))


def _st_check(mb, px):
    """confere que o dressing ficou todo na faixa (fora do poco, dentro do lote, base enterrada no maximo 0.4 e topo
    no maximo no acento de T+10)"""
    bad = [v.co for v in mb.bm.verts if not (ST_XMIN <= abs(v.co.x - px) <= ST_XMAX and ST_YMIN <= v.co.y <= ST_YMAX
                                             and T - 0.4 <= v.co.z <= T + 10.0)]
    if bad:
        print("ESCADA DS: %d vertices fora da faixa (ex.: %s)" % (len(bad), tuple(round(c, 2) for c in bad[0])))


def stairs(mb, px, rng):
    """dressing da faixa ao lado do lance 2 (objeto PORTAL_DemonSlayer_Stairs): dois pares de chochin (pe e chegada)"""
    for side, y, dx in ST_LAMPS:
        _st_lantern(mb, px, side, y, dx)
    _st_check(mb, px)
