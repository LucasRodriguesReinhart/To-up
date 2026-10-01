# il_lion - LEAO GUARDIAO (komainu cartoon, refs 13/14/18) COMPARTILHADO: entrada (il_entrance) e portao DB
# (il_gate_db.lion). Dono: zona entrance. Nao registra material nenhum: o chamador passa os materiais da zona dele.
#
# Forma (s = 1): sentado, ~8 de altura acima do ponto de apoio (z), pegada ~4,6 x 5,0.
#   - CABECA GRANDE (~40% do volume junto com a juba): cranio + focinho largo + boca ABERTA (interior escuro e
#     presas claras) + nariz, olhos e sobrancelhas bravas;
#   - JUBA de 10 lobos arredondados em arco em volta do rosto (aberta embaixo, no queixo), massa de juba atras da
#     cabeca e 3 cachos de barba no peito; cauda em chama de 3 lobos; tudo na cor CLARA (mane_m);
#   - corpo mais ESCURO (body_m): ancas redondas, peito estufado, uma pata dianteira reta e a outra POUSADA sobre a
#     esfera no canto da frente (lado 'side');
#   - massas lisas (sombreamento suave) e UV constante num texel neutro da textura de detalhe: cada material le
#     como UM tom (sem mosaico da textura em pecas pequenas). Nada com todas as dimensoes < 0,35.
#
# API:
#   lion(mb, x, y, z, yaw, s=1.0, side=1, ball_mat="Stone_Wall_Light", body_m="Stone_Wall_Dark",
#        mane_m="Stone_Wall_Light", dark_m="Stone_Grout", mouth_m=None, ball=None, col_area=None, ball_r=1.0) -> dict
#     (x, y, z) = centro da pegada no topo do pedestal; yaw = rotacao Z tal que o +Y local aponta para a FRENTE do
#     leao (il_lib.yaw_to(dx, dy) serve); side = +1/-1: lado local (+x = direita do leao) da pata sobre a esfera
#     (espelho). ball = funcao opcional ball(mb, centro, raio, frente) que desenha a esfera no lugar da esfera lisa
#     em ball_mat (ex.: a esfera do dragao do portao DB); ball_r = raio da esfera em unidades do leao (1,0 = ~1/8
#     da altura). col_area: se dado, cria a col_box sugerida nessa area.
#     Devolve dict(col=(tamanho, centro, rot), ball=(centro, raio), top=z_topo, head=centro_da_cabeca).
#   pedestal(mb, x, y, z, yaw, w=5.2, d=4.8, h=4.5, light_m=..., dark_m=...) -> z do topo (pedestal de pedra
#     com rodape, dado, almofadas rebaixadas e cornija). Opcional (o portao DB usa o pedestal proprio).
import math
import bmesh
from mathutils import Vector, Matrix, Euler
import fm_lib
import fm_portal_kit as K
from fm_parts import Frame

HEIGHT = 8.0          # altura nominal do leao (s = 1), do apoio ao alto da juba

# ------------------------------------------------------------------ UV constante num texel neutro
_UV = {}


def flat_uv(m):
    """(u, v) de um texel de alpha minimo (vizinhanca 5x5) da textura de detalhe do material: a peca inteira pega
    a cor base pura (UM tom). Materiais sem textura: (0.5, 0.5)."""
    tk = fm_lib.tex_key(m)
    if tk is None:
        return (0.5, 0.5)
    if tk in _UV:
        return _UV[tk]
    uv = (0.37, 0.61)
    try:
        import numpy as np
        im = fm_lib._tex_image(tk)
        w, h = im.size
        px = np.empty(w * h * 4, dtype=np.float32)
        im.pixels.foreach_get(px)
        a = px.reshape(h, w, 4)[..., 3]
        mx = a.copy()
        for dy in range(-2, 3):
            for dx in range(-2, 3):
                mx = np.maximum(mx, np.roll(np.roll(a, dy, 0), dx, 1))
        iy, ix = np.unravel_index(int(np.argmin(mx)), mx.shape)
        uv = ((ix + 0.5) / w, (iy + 0.5) / h)
    except Exception as e:           # sem textura (previa 'roblox'/'liso'): qualquer ponto serve
        print("il_lion: flat_uv(%s) padrao (%s)" % (m, e))
    _UV[tk] = uv
    return uv


def flatten(mb, faces, smooth=True):
    """UV constante (texel neutro do material de cada face) e sombreamento suave nas faces dadas"""
    uvl = mb.uvl
    for f in faces:
        if not f.is_valid:
            continue
        m = mb.mats[f.material_index]
        name = m[1] if isinstance(m, tuple) else m
        uv = flat_uv(name)
        if smooth:
            f.smooth = True
        for lp in f.loops:
            lp[uvl].uv = uv


class Flat:
    """bloco: as faces criadas dentro dele recebem UV constante (e sombreamento suave se smooth=True)"""

    def __init__(self, mb, smooth=True):
        self.mb, self.smooth = mb, smooth

    def __enter__(self):
        self.before = set(self.mb.bm.faces)
        return self

    def __exit__(self, *a):
        flatten(self.mb, [f for f in self.mb.bm.faces if f not in self.before], self.smooth)


# ------------------------------------------------------------------ primitivas no referencial do leao
def _blob(mb, F, s, p, r, m, res=(8, 6), rot=(0.0, 0.0, 0.0)):
    """elipsoide suave (esfera UV escalada): p e r em unidades do leao (x = direita, y = frente, z = cima)"""
    M = (Matrix.Translation(F.p(p[0] * s, p[1] * s, p[2] * s)) @ Matrix.Rotation(F.a, 4, "Z")
         @ Euler(rot).to_matrix().to_4x4() @ Matrix.Diagonal((r[0] * s, r[1] * s, r[2] * s, 1.0)))
    out = bmesh.ops.create_uvsphere(mb.bm, u_segments=res[0], v_segments=res[1], radius=1.0, matrix=M)
    mb._post(out["verts"], m, None, 0, 1)


def _limb(mb, F, s, a, b, r, m, n=8):
    """membro cilindrico de a ate b (unidades do leao)"""
    mb.rod(F.p(a[0] * s, a[1] * s, a[2] * s), F.p(b[0] * s, b[1] * s, b[2] * s), r * s, m, n)


def lion(mb, x, y, z, yaw, s=1.0, side=1, ball_mat="Stone_Wall_Light", body_m="Stone_Wall_Dark",
         mane_m="Stone_Wall_Light", dark_m="Stone_Grout", mouth_m=None, ball=None, col_area=None, ball_r=1.0):
    F = Frame(x, y, z, yaw)
    sd = 1 if side >= 0 else -1
    mouth_m = mouth_m or dark_m
    fwd = (F.p(0, 1, 0) - F.p(0, 0, 0)).normalized()
    rb = ball_r                                   # raio da esfera (unidades do leao)
    # esfera no canto da frente, do lado 'side' (esfera maior chega um pouco para fora e para a frente)
    bc = (sd * (1.3 + (rb - 1.0) * 0.5), 1.25 + (rb - 1.0) * 0.3, rb - 0.02)
    with Flat(mb):
        # ---- corpo (escuro): ancas, patas de tras, tronco inclinado para tras, peito estufado
        for k in (-1, 1):
            _blob(mb, F, s, (k * 1.2, -1.05, 1.15), (1.05, 1.45, 1.25), body_m, (9, 6))
            # cacho claro na coxa (espiral de pelo das refs): quebra a massa escura vista de lado
            _blob(mb, F, s, (k * 2.12, -1.0, 1.35), (0.3, 0.62, 0.62), mane_m, (6, 4), rot=(0.0, 0.0, 0.0))
            _blob(mb, F, s, (k * 1.38, 0.3, 0.36), (0.62, 0.9, 0.45), body_m, (6, 4))
        _blob(mb, F, s, (0.0, -0.25, 2.8), (1.3, 1.3, 1.95), body_m, (10, 7), rot=(0.22, 0.0, 0.0))
        _blob(mb, F, s, (0.0, 0.5, 2.55), (1.08, 0.95, 1.25), body_m, (8, 6))
        # ---- patas dianteiras: a de dentro reta ate o chao, a de fora POUSADA no alto da esfera
        _limb(mb, F, s, (-sd * 0.85, 0.7, 3.0), (-sd * 0.92, 1.05, 0.5), 0.52, body_m)
        _blob(mb, F, s, (-sd * 0.92, 1.4, 0.4), (0.62, 0.82, 0.42), body_m, (8, 5))
        top_b = (bc[0] - sd * 0.08, bc[1] + 0.05, bc[2] + rb + 0.05)
        _limb(mb, F, s, (sd * 0.9, 0.55, 3.05), (top_b[0] - sd * 0.02, top_b[1] - 0.1, top_b[2] + 0.2), 0.5, body_m)
        _blob(mb, F, s, (top_b[0], top_b[1] + 0.1, top_b[2] + 0.12), (0.66, 0.8, 0.4), body_m, (8, 5))
        # ---- juba (clara): massa atras da cabeca, arco de 10 lobos em volta do rosto, barba no peito, cauda
        hz = 5.35
        _blob(mb, F, s, (0.0, 0.15, hz + 0.05), (1.75, 1.15, 1.7), mane_m, (8, 6))
        for i in range(10):
            a = math.radians(-62.0 + 30.0 * i)                 # arco de -62 a 208 graus: aberto no queixo
            big = 0.8 if i in (4, 5) else 0.7
            _blob(mb, F, s, (1.82 * math.cos(a), 0.5, hz + 0.05 + 1.62 * math.sin(a)), (big, 0.62, big), mane_m,
                  (6, 5))
        for bx, by, bz in ((-0.62, 1.3, 3.7), (0.62, 1.3, 3.7), (0.0, 1.5, 3.45)):
            _blob(mb, F, s, (bx, by, bz), (0.56, 0.46, 0.62), mane_m, (6, 4))
        for ty, tz, tr in ((-2.2, 2.45, 0.72), (-2.4, 3.35, 0.6), (-2.2, 4.15, 0.48)):
            _blob(mb, F, s, (0.0, ty, tz), (tr, tr * 0.8, tr * 1.15), mane_m, (6, 5), rot=(0.35, 0.0, 0.0))
        # ---- cabeca GRANDE (escura como o corpo): cranio, focinho, mandibula
        _blob(mb, F, s, (0.0, 0.95, hz), (1.5, 1.3, 1.4), body_m, (12, 8))
        _blob(mb, F, s, (0.0, 2.02, hz - 0.4), (0.95, 0.7, 0.6), body_m, (8, 6))
        _blob(mb, F, s, (0.0, 2.0, hz - 1.25), (0.8, 0.62, 0.3), body_m, (8, 5))        # queixo (labio de baixo)
        # ---- boca aberta, nariz, olhos (escuros); sobrancelhas bravas e presas (claras)
        _blob(mb, F, s, (0.0, 2.08, hz - 0.9), (0.7, 0.48, 0.34), mouth_m, (8, 5))      # boca aberta (recuada)
        _blob(mb, F, s, (0.0, 2.68, hz + 0.02), (0.44, 0.3, 0.3), dark_m, (6, 4))
        for k in (-1, 1):
            _blob(mb, F, s, (k * 0.56, 1.98, hz + 0.5), (0.27, 0.22, 0.27), dark_m, (6, 4))
            _blob(mb, F, s, (k * 0.6, 1.95, hz + 0.92), (0.52, 0.34, 0.26), mane_m, (6, 4), rot=(0.0, -k * 0.38, 0.0))
    for k in (-1, 1):
        K.cone(mb, F.p(k * 0.4 * s, 2.46 * s, (hz - 0.62) * s), F.p(k * 0.37 * s, 2.52 * s, (hz - 1.08) * s),
               0.18 * s, 0.04 * s, mane_m, 5)
    # ---- esfera no canto da frente (lisa em ball_mat, ou a do chamador)
    c = F.p(bc[0] * s, bc[1] * s, bc[2] * s)
    if ball is not None:
        ball(mb, c, rb * s, fwd)
    else:
        with Flat(mb):
            _blob(mb, F, s, bc, (rb, rb, rb), ball_mat, (10, 7))
    col = ((4.4 * s, 4.8 * s, 7.6 * s), F.p(0.0, 0.0, 3.8 * s), (0.0, 0.0, yaw))
    if col_area:
        import il_lib
        il_lib.col_box(col_area, *col)
    return dict(col=col, ball=(c, rb * s), top=z + HEIGHT * s, head=F.p(0.0, 0.95 * s, hz * s))


def pedestal(mb, x, y, z, yaw, w=5.2, d=4.8, h=4.5, light_m="Stone_Wall_Light", dark_m="Stone_Wall_Dark",
             bevel=0.12):
    """pedestal de pedra (rodape escuro, dado claro, almofadas rebaixadas na frente e atras, cornija escura);
    (x, y, z) = centro da base; retorna o z do topo. Todas as pecas com menor dimensao >= 1,0 levam bevel <= 5%."""
    F = Frame(x, y, z, yaw)
    hb, hc = 0.8, 0.6                    # rodape e cornija (< 1,0: sem bevel)
    hd = h - hb - hc                     # dado
    mb.box((w, d, hb), F.p(0, 0, hb / 2), F.r(), dark_m, 0.0)
    mb.box((w - 0.7, d - 0.7, hd), F.p(0, 0, hb + hd / 2), F.r(), light_m, min(bevel, 0.05 * min(d - 0.7, hd)))
    mb.box((w - 0.2, d - 0.2, hc), F.p(0, 0, h - hc / 2), F.r(), dark_m, 0.0)
    for sy in (-1, 1):                   # almofada saliente 0,15 na frente e atras (sem z-fight)
        mb.box((w - 2.3, 0.3, hd - 1.2), F.p(0, sy * ((d - 0.7) / 2 + 0.15), hb + hd / 2), F.r(), dark_m, 0.0)
    return z + h
