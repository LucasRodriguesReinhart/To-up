# fm_buildings - praca + caminhos pavimentados, loja (interior completo), cabanas de mineiros (entraveis),
# estacao de carga sobre o trilho, galpao aberto de cristais na margem leste.
# Passe de acabamento: a casca das construcoes vem de fm_arch_house/fm_arch_kit (telhado em fiadas com cumeeira
# arqueada, oitoes com enxaimel, balancos, lucarnas, empenas cruzadas, chamines, meias-aguas, fundacao irregular)
# e cada cabana e uma variante propria (nao a mesma saida do gerador).
import math, random
from mathutils import Vector
from fm_lib import MB, D, col_box, col_box2, marker, light, resample, bezier, point_in_poly
from fm_parts import (Frame, masonry_wall, timber_wall, window_glow, arch, lantern, hanging_lantern, crate, barrel,
                      crystal_cluster, pave_poly, pave_ring, banner, emblem_pickaxe, fence, mine_cart, P3, frustum,
                      stone_parapet, plank_floor)
import fm_arch_kit as K
from fm_arch_house import house
import fm_layout as L

F0 = L.FLOOR


def ribbon(pts, w):
    """poligono de uma faixa de largura w ao longo da polilinha"""
    pts = [Vector((p[0], p[1], 0)) for p in pts]
    left, right = [], []
    for i, p in enumerate(pts):
        j = min(i + 1, len(pts) - 1)
        k = max(i - 1, 0)
        t = (pts[j] - pts[k]).normalized()
        s = Vector((-t.y, t.x, 0))
        left.append(p + s * w / 2)
        right.append(p - s * w / 2)
    return [(p.x, p.y) for p in left + list(reversed(right))]


# ------------------------------------------------------------------ praca e caminhos
PATHS = {
    # nome: (pontos, largura)
    "Avenue": ([(0, -62.2), (0, -52)], 20.0),
    "West_Road": ([(-24, -36), (-38, -24), (-44, -8), (-44, 34)], 10.0),
    "Mine_Road": ([(-22, -44), (-40, -46), (-54, -40), (-60, -38)], 10.0),
    "Back_Court": ([(-116, 41), (50, 41)], 10.0),
    "East_Lane": ([(38, -8), (38, 36)], 7.0),
    "East_Road": ([(24, -20), (40, -18), (54, -18)], 10.0),
    "East_Bank": ([(70, -18), (96, -18), (96, 36), (70, 41)], 9.0),
    "East_Back": ([(70, 41), (116, 41)], 9.0),
    "Shop_Apron": ([(18, -40), (26, -39)], 8.0),
    "Mill_Apron": ([(38, 4), (L.MILL[0] + 9.0, 6), (L.MILL[0] + 9.0, 11)], 6.0),
}


PLAZA_C = (0.0, -30.0)
PLAZA_RR = 25.0


def _slab(mb, pts, z0, z1, m, tint=None):
    """prisma SEM a face de baixo (lajota, meio-fio): 2 tris no topo + 2 por lado - ninguem ve o fundo"""
    vb = [mb.bm.verts.new((p[0], p[1], z0)) for p in pts]
    vt = [mb.bm.verts.new((p[0], p[1], p[2] if len(p) > 2 else z1)) for p in pts]
    n = len(pts)
    try:
        mb.bm.faces.new(vt)
    except ValueError:
        pass
    for i in range(n):
        j = (i + 1) % n
        try:
            mb.bm.faces.new((vb[i], vb[j], vt[j], vt[i]))
        except ValueError:
            pass
    mb._post(vb + vt, m, tint, 0, 1)


def _seg_dist(px, py, a, b, cap0=True, cap1=True):
    """distancia ao segmento; cap0/cap1 = False: ponta RETA (alem da ponta o ponto nao pertence ao segmento)"""
    ax, ay = a
    bx, by = b
    dx, dy = bx - ax, by - ay
    ll = dx * dx + dy * dy
    t = 0.0 if ll < 1e-9 else ((px - ax) * dx + (py - ay) * dy) / ll
    if (t < 0.0 and not cap0) or (t > 1.0 and not cap1):
        return 1e9
    t = max(0.0, min(1.0, t))
    return math.hypot(px - (ax + dx * t), py - (ay + dy * t))


def _patios():
    return [(px - 8.0, 38.0, px + 8.0, L.FLIGHT1_Y0) for px in L.PORTAL_X]


_CAPS = {}


def _path_caps():
    """por caminho: (ponta0_arredondada, ponta1_arredondada) - so onde a ponta encosta em outra faixa ou na praca"""
    if _CAPS:
        return _CAPS
    for name, (pts, w) in PATHS.items():
        res = []
        for p in (pts[0], pts[-1]):
            joined = math.hypot(p[0] - PLAZA_C[0], p[1] - PLAZA_C[1]) < PLAZA_RR + 2.0
            for n2, (pts2, w2) in PATHS.items():
                if n2 == name or joined:
                    continue
                joined = any(_seg_dist(p[0], p[1], a, b) <= w2 / 2 + w / 2 + 1.0 for a, b in zip(pts2, pts2[1:]))
            res.append(joined)
        _CAPS[name] = tuple(res)
    return _CAPS


def _covered(x, y, margin=0.0, skip_path=None):
    """ponto dentro da UNIAO das faixas ou de um patio. Juncoes arredondadas (sem cunha no joelho nem entre faixas
    que se encontram); pontas LIVRES da polilinha sao retas - capsula na ponta avancava w/2 alem dela (a Avenue punha
    lajotas a z4.35 flutuando sobre a escada frontal)"""
    caps = _path_caps()
    for name, (pts, w) in PATHS.items():
        if name == skip_path:
            continue
        nseg = len(pts) - 1
        c0, c1 = caps[name]
        for i, (a, b) in enumerate(zip(pts, pts[1:])):
            if _seg_dist(x, y, a, b, cap0=(i > 0 or c0), cap1=(i < nseg - 1 or c1)) <= w / 2 + margin:
                return True
    for (x0, y0, x1, y1) in _patios():
        if x0 - margin <= x <= x1 + margin and y0 - margin <= y <= y1 + margin:
            return True
    return False


def _in_plaza(x, y, r):
    return math.hypot(x - PLAZA_C[0], y - PLAZA_C[1]) < r


def plaza_and_paths(rng):
    """praca circular + caminhos. Passe fix2:
    - os caminhos sao UMA grade global de lajotas sobre a uniao das faixas (capsulas): nada de cunha de rejunte no
      joelho das polilinhas (o 'buraco preto' do East_Bank) nem lajotas de dois caminhos sobrepostas nas juncoes;
    - nenhuma lajota de caminho dentro da praca (acabou o z-fighting entre TER_Path_Paving e TER_Plaza_Paving);
    - lajotas e meio-fio sem a face de baixo e sem chanfro, pedras da praca idem: ~16k tris no lugar de ~49k;
    - dois tons EXPLICITOS de lajota (Stone_Paving / _B) no lugar das variantes sorteadas: 10 MeshParts em vez de 16."""
    lr = random.Random(4242)
    cx, cy = PLAZA_C
    R = PLAZA_RR
    mb = K.AMB("TER_Plaza_Paving", "02_TERRAIN", rng)
    # praca circular: rejunte + aneis de pedra + anel escuro de borda + medalhao central
    mb.cyl(R + 1.2, 0.8, (cx, cy, F0 - 0.2), (0, 0, 0), "Stone_Grout", 48, bevel=0.0)

    def ring(r0, r1, ring_w, h, m, gap=0.22):
        r = r0
        k = 0
        while r < r1 - 0.3:
            rr = min(r + ring_w, r1)
            n = max(6, int(math.tau * (r + rr) / 2 / 2.8))
            da = math.tau / n
            off = da * 0.5 if k % 2 else 0.0
            for i in range(n):
                a0, a1 = off + da * i, off + da * (i + 1)
                g = gap / max(r, 1.0)
                pts = []
                for f in (0.0, 0.5, 1.0):
                    t = a0 + g + (a1 - a0 - 2 * g) * f
                    pts.append((cx + math.cos(t) * (rr - gap / 2), cy + math.sin(t) * (rr - gap / 2)))
                for f in (1.0, 0.5, 0.0):
                    t = a0 + g + (a1 - a0 - 2 * g) * f
                    pts.append((cx + math.cos(t) * (r + gap / 2), cy + math.sin(t) * (r + gap / 2)))
                hh = h + lr.uniform(-0.05, 0.04)
                mm = (m + "_B") if (m == "Stone_Paving" and lr.random() < 0.35) else m
                _slab(mb, pts, F0 + 0.05, F0 + 0.02 + hh, mm)
            r = rr
            k += 1
    ring(5.0, R - 1.4, 2.6, 0.33, "Stone_Paving")
    ring(R - 1.4, R + 0.8, 2.2, 0.38, "Stone_Dark")
    # desenho central: medalhao escuro, disco claro, raios de latao com picareta cruzada no meio
    mb.cyl(5.0, 0.4, (cx, cy, F0 + 0.2), (0, 0, 0), "Stone_Dark", 24, bevel=0.0)
    mb.cyl(4.2, 0.45, (cx, cy, F0 + 0.25), (0, 0, 0), "Stone_Light", 24, bevel=0.0)
    for a in range(0, 360, 45):
        p = Vector((cx + math.cos(D(a)) * 3.2, cy + math.sin(D(a)) * 3.2, F0 + 0.5))
        mb.box((1.6, 0.5, 0.12), p, (0, 0, D(a)), "Metal_Brass", 0.0)
    # (as lajotas sem fundo ja saem com o topo anti-horario: recalcular normais numa casca aberta pode inverter)
    mb.finish(recalc=False)
    pv = K.AMB("TER_Path_Paving", "02_TERRAIN", rng)
    # rejunte: um retangulo por trecho + octogono em cada vertice (a juncao fica sempre fechada)
    zg = F0 + 0.12
    caps = _path_caps()
    kg = 0
    for name, (pts, w) in PATHS.items():
        for a, b in zip(pts, pts[1:]):
            A, B = Vector((a[0], a[1], 0)), Vector((b[0], b[1], 0))
            t = (B - A).normalized()
            s = Vector((-t.y, t.x, 0)) * (w / 2 + 0.15)
            quad = [A - s, B - s, B + s, A + s]
            # cada trecho numa cota propria (milimetrica): trechos que se sobrepoem nas juncoes nao ficam coplanares
            pv.prism([(q.x, q.y) for q in quad], F0 - 0.3, zg - 0.002 * (kg % 6), "Stone_Grout", 0.0)
            kg += 1
        # octogono de rejunte em cada vertice interno e nas pontas arredondadas (juncao com outra faixa)
        ends = [p for p, c in zip((pts[0], pts[-1]), caps[name]) if c]
        for p in list(pts[1:-1]) + ends:
            rr = w / 2 + 0.15
            pv.prism([(p[0] + math.cos(k * math.tau / 8) * rr, p[1] + math.sin(k * math.tau / 8) * rr) for k in range(8)],
                     F0 - 0.3, zg - 0.013 - 0.002 * (kg % 4), "Stone_Grout", 0.0)
            kg += 1
    for (x0, y0, x1, y1) in _patios():
        pv.prism([(x0 - 0.1, y0 - 0.1), (x1 + 0.1, y0 - 0.1), (x1 + 0.1, y1 + 0.1), (x0 - 0.1, y1 + 0.1)], F0 - 0.3,
                 zg - 0.003, "Stone_Grout", 0.0)
    # lajotas: grade global (fiadas desencontradas), cantos com leve irregularidade (assentamento a mao)
    tile, gap = 2.6, 0.2
    xs, ys = [], []
    for (pts, w) in PATHS.values():
        xs += [p[0] for p in pts]
        ys += [p[1] for p in pts]
    for (x0, y0, x1, y1) in _patios():
        xs += [x0, x1]
        ys += [y0, y1]
    X0, X1, Y0, Y1 = min(xs) - 10, max(xs) + 10, min(ys) - 10, max(ys) + 10
    row = 0
    y = Y0
    while y < Y1:
        x = X0 + (tile / 2 if row % 2 else 0.0)
        while x < X1:
            xc, yc = x + tile / 2, y + tile / 2
            if _covered(xc, yc, -0.35) and not _in_plaza(xc, yc, R + 1.6):
                hw = (tile - gap) / 2
                zt = F0 + 0.35 + lr.uniform(-0.04, 0.03)
                pts = []
                for (ux, uy) in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
                    pts.append((xc + ux * hw + lr.uniform(-0.07, 0.07), yc + uy * hw + lr.uniform(-0.07, 0.07),
                                zt + lr.uniform(-0.025, 0.025)))
                _slab(pv, pts, F0 + 0.05, zt, "Stone_Paving_B" if lr.random() < 0.35 else "Stone_Paving")
            x += tile
        y += tile
        row += 1
    # meio-fio: pedras ao longo das duas bordas de cada trecho, cortadas onde outra faixa (ou a praca) continua,
    # e uma pedra de quina no lado de fora de cada vertice
    for name, (pts, w) in PATHS.items():
        for a, b in zip(pts, pts[1:]):
            A, B = Vector((a[0], a[1], 0)), Vector((b[0], b[1], 0))
            L_ = (B - A).length
            t = (B - A) / L_
            s = Vector((-t.y, t.x, 0))
            ang = math.atan2(t.y, t.x)
            n = max(1, int(round(L_ / 2.8)))
            for k in (-1, 1):
                for i in range(n):
                    c = A + t * (L_ * (i + 0.5) / n) + s * k * (w / 2 + 0.35)
                    if _in_plaza(c.x, c.y, R + 1.4):
                        continue
                    if _covered(c.x, c.y, -0.05):
                        continue
                    if lr.random() > 0.9:
                        continue
                    hl = L_ / n / 2 - 0.1
                    hh = 0.55 + lr.uniform(-0.05, 0.05)
                    yaw = ang + lr.uniform(-0.02, 0.02)
                    ct, st_ = math.cos(yaw), math.sin(yaw)
                    corners = [(-hl, -0.35), (hl, -0.35), (hl, 0.35), (-hl, 0.35)]
                    _slab(pv, [(c.x + u * ct - v * st_, c.y + u * st_ + v * ct) for u, v in corners], F0 - 0.1,
                          F0 + 0.2 + hh / 2, "Stone_Light")
        for i in range(1, len(pts) - 1):
            p0, p1, p2 = (Vector((q[0], q[1], 0)) for q in (pts[i - 1], pts[i], pts[i + 1]))
            t0, t1 = (p1 - p0).normalized(), (p2 - p1).normalized()
            turn = t0.x * t1.y - t0.y * t1.x
            if abs(turn) < 0.05:
                continue
            bis = (t0 - t1).normalized() if (t0 - t1).length > 1e-6 else Vector((-t0.y, t0.x, 0))
            c = p1 + bis * (w / 2 + 0.45)
            if _in_plaza(c.x, c.y, R + 1.4) or _covered(c.x, c.y, -0.05):
                continue
            a_ = math.atan2(bis.y, bis.x)
            ct, st_ = math.cos(a_), math.sin(a_)
            _slab(pv, [(c.x + u * ct - v * st_, c.y + u * st_ + v * ct) for u, v in
                       ((-0.5, -0.8), (0.5, -0.8), (0.5, 0.8), (-0.5, 0.8))], F0 - 0.1, F0 + 0.5, "Stone_Light")
    pv.finish(recalc=False)


# ------------------------------------------------------------------ loja
# Passe fix2: a loja sai da frente do One Piece e do One Punch Man e para de competir com a forja.
# Casa BAIXA e larga (terreo de pedra + faixa de enxaimel rica ate 7.4), telhado de QUATRO AGUAS a 27 graus em telha
# envelhecida marrom-avermelhada com remendos de musgo (pico em z ~16), empena cruzada sobre a porta com o oitao
# em balanco. O chamariz desce para o terreo: toldo listrado sobre a vitrine, placa vermelha pendurada, postigos.
# Linha de visada spawn (0,-104,5.5) -> discos OP/OPM: o telhado fica abaixo dela em toda a planta que ela cruza.
SHOP_V = dict(
    t=1.5, lower="stone", upper="timber", zs=2.6, ze=7.0, pitch=27.0, door=(3.5, 8.5, 8.0, 2.5), course=1.7, post=3.0,
    blk=(2.4, 3.8),
    wins={0: [(11.8, 16.3, 1.4, 5.8, "grid+glow")],
          1: [(2.4, 5.0, 3.8, 6.0, "two+dark"), (8.2, 9.2, 3.6, 6.2, "slit"), (12.4, 15.6, 3.7, 6.1, "grid+lit")],
          2: [(7.0, 9.6, 4.0, 6.0, "two")],
          3: [(3.0, 5.4, 3.8, 6.0, "cross"), (10.4, 11.4, 3.6, 6.2, "slit")]},
    roof=dict(kind="hip", family="tile", over=(1.1, 1.1), ends=(1.1, 1.1), sag=0.3, alt=0.05, course=1.55,
              tile=(1.9, 2.8)),
    door_gable=dict(wd=7.6, h=2.0, rise=2.0, style="cross", over=0.9, lit=True),
    dormers=[dict(side=1, y=4.2, wd=3.4, inset=1.7, h=2.2, lit=False)],
    chimneys=[dict(kind="side", side=-1, y=4.0, name="Shop", top=1.2)],
    shutters=[(1, 12.4, 15.6, 3.7, 6.1)],
    paint="Wood_Teal", floor_top=0.55, win_m="Window_Warm", fan_m="Window_Warm", back=(2, 3),
    ties=False,     # casa baixa (frechal a 6.45 do piso): sem tirantes cruzando a altura da cabeca/camera
)


def shop(rng):
    x0, y0, x1, y1 = L.SHOP
    t = SHOP_V["t"]
    cxs, cys = (x0 + x1) / 2, (y0 + y1) / 2
    # referencial: local -y = oeste (fachada para a praca), local +x = sul
    FS = Frame(cxs, cys, 0.0, D(-90))
    mb = K.AMB("BLD_Shop", "07_BUILDINGS", rng)
    mi = K.AMB("BLD_Shop_Interior", "07_BUILDINGS", rng)
    A = "Shop"
    info = house(mb, FS, x1 - x0, y1 - y0, F0, rng, SHOP_V, area=A, name="Shop", mbi=mi)
    ze = info["ze"]
    # toldo listrado so sobre a vitrine (acima dela, abaixo da faixa de enxaimel), sanefa recortada, maos-francesas
    za = F0 + 6.9
    for i in range(4):
        yy = y1 - 11.3 - i * 1.3
        mm = "Cloth_Red" if i % 2 else "Cloth_Canvas"
        mb.box((3.2, 1.3, 0.26), (x0 - 1.5, yy, za), (0, D(-17), 0), mm, 0.0)
        mb.box((0.22, 1.3, 0.7), (x0 - 3.05, yy, za - 0.8), (0, 0, 0), "Cloth_Canvas" if i % 2 else "Cloth_Red", 0.0)
    for yy in (y1 - 10.9, y1 - 16.1):
        mb.beam((x0 - 0.1, yy, za - 1.2), (x0 - 2.9, yy, za - 0.45), 0.28, 0.28, "Wood_Dark", 0.0)
    mb.beam((x0 - 3.0, y1 - 10.8, za - 0.4), (x0 - 3.0, y1 - 16.2, za - 0.4), 0.28, 0.28, "Wood_Dark", 0.0)
    # placa pendurada (fundo vermelho, picareta e gema) num braco de ferro ao lado da porta
    ys = y1 - 1.3
    mb.beam((x0 - 0.2, ys, F0 + 8.6), (x0 - 4.2, ys, F0 + 8.6), 0.34, 0.34, "Wood_Dark", 0.0)
    mb.beam((x0 - 0.2, ys, F0 + 6.6), (x0 - 2.4, ys, F0 + 8.5), 0.26, 0.26, "Wood_Dark", 0.0)
    for dy in (-1.1, 1.1):
        mb.rod((x0 - 3.3, ys + dy, F0 + 8.45), (x0 - 3.3, ys + dy, F0 + 7.85), 0.06, "Metal_Dark", 4)
    mb.box((0.4, 3.4, 2.6), (x0 - 3.3, ys, F0 + 6.6), (0, 0, D(3)), "Wood_Dark", 0.08)
    mb.box((0.46, 2.8, 2.0), (x0 - 3.3, ys, F0 + 6.6), (0, 0, D(3)), "Cloth_Red", 0.0)
    emblem_pickaxe(mb, Vector((x0 - 3.56, ys, F0 + 6.6)), D(-90), s=0.3, m="Cloth_Canvas", normal_off=0.0)
    crystal_cluster(mb, (x0 - 3.3, ys, F0 + 7.95), 0.3, "Crystal_Blue", rng, 3)
    # colisao fina encostada na fachada sul (postigos/floreira na altura da cabeca: o jogador nao atravessa)
    col_box2(A, (x0, y0 - 1.0, F0), (x1, y0, F0 + 6.8))
    # ---------------------------------------------------------------- interior (BLD_Shop_Interior)
    plank_floor(mi, Frame(cxs, cys, 0, 0.0), x1 - x0 - 2 * t, y1 - y0 - 2 * t, F0 + 0.3, rng, m_alt=("Wood_Dark", "Wood_Dark"))
    cx = x0 + 10.5
    mi.box2((cx - 0.8, y0 + 3.0, F0), (cx + 0.8, y1 - 5.5, F0 + 3.2), "Wood_Plank", 0.0)
    mi.box2((cx - 1.1, y0 + 2.8, F0 + 3.2), (cx + 1.1, y1 - 5.3, F0 + 3.6), "Wood_Dark", 0.05)
    for yy in (y0 + 4.0, (y0 + y1) / 2 - 1.0, y1 - 7.0):
        mi.box((1.9, 0.35, 2.6), (cx, yy, F0 + 1.6), (0, 0, 0), "Wood_Dark", 0.0)
    for zz in (F0 + 1.8, F0 + 3.5, F0 + 5.2):
        mi.box2((x1 - 2.6, y0 + 2.0, zz), (x1 - 1.6, y1 - 2.0, zz + 0.3), "Wood_Plank", 0.0)
        for k in range(8):
            yy = y0 + 3.0 + k * 1.7
            if k % 3 == 0:
                mi.beam((x1 - 2.1, yy, zz + 0.3), (x1 - 2.1, yy + 0.4, zz + 1.5), 0.25, 0.25, "Wood_Plank", 0.0)
                mi.box((0.4, 1.4, 0.4), (x1 - 2.1, yy + 0.5, zz + 1.45), (0, 0, 0), "Metal_Dark", 0.0)
            else:
                crystal_cluster(mi, (x1 - 2.1, yy, zz + 0.3), 0.3, "Crystal_Blue" if k % 2 else "Crystal_Purple", rng, 2)
    for yy in (y0 + 3.5, y1 - 3.5):
        mi.box2((x0 + 3.0, yy - 1.2, F0), (x0 + 6.0, yy + 1.2, F0 + 2.8), "Wood_Dark", 0.0)
        crystal_cluster(mi, (x0 + 4.5, yy, F0 + 2.8), 0.45, "Crystal_Blue", rng, 4)
    # lampiao pendurado do forro do pico (4 aguas: apice no centro), com o fundo a ~7 do piso (acima da cabeca)
    z_att = info["z_r"] - 0.5
    hanging_lantern(mi, ((x0 + x1) / 2, (y0 + y1) / 2, z_att), name="L_Shop_In",
                    chain=max(0.6, z_att - (F0 + 7.2) - 2.1))
    mi.finish()
    light("L_Shop_Fill", "POINT", ((x0 + x1) / 2, (y0 + y1) / 2, F0 + 6.0), 700, (1.0, 0.72, 0.45), 3.0)
    lantern(mb, (x0 - 2.0, y0 + 2.0, F0), D(180), name="L_Shop_Door", h=6.0)
    mb.finish()
    # colisao do mobiliario (a casca ja foi criada por house())
    col_box2(A, (cx - 1.1, y0 + 2.8, F0), (cx + 1.1, y1 - 5.3, F0 + 3.6))
    col_box2(A, (x1 - 2.6, y0 + 2.0, F0), (x1 - 1.6, y1 - 2.0, F0 + 7.0))
    for yy in (y0 + 3.5, y1 - 3.5):
        col_box2(A, (x0 + 3.0, yy - 1.2, F0), (x0 + 6.0, yy + 1.2, F0 + 2.8))
    marker("NPC_Shop", (cx + 2.5, (y0 + y1) / 2, F0 + 0.3), (0, 0, D(90)), 2, "ARROWS", props={"npc": "Lojista"})
    marker("INTERACT_Shop", (cx, (y0 + y1) / 2, F0 + 3.6), (0, 0, 0), 1.5, "SPHERE")
    marker("PLAYER_INTERACT_Shop", (cx - 4.0, (y0 + y1) / 2, F0 + 0.3), (0, 0, 0), 2, "CIRCLE")
    marker("DOOR_Shop", (x0, y1 - 6.0, F0), (0, 0, 0), 1.5)
    shop_stall(rng)


def shop_stall(rng):
    """banca da loja no bolsao gramado entre a escadaria do spawn e a loja: carrinho de mercador com toldo
    listrado, caixotes de cristal, barril e placa-seta apontando a porta. E o chamariz no nivel do chao (quem sobe
    a escadaria ve a banca antes do telhado) e abre a visada do spawn para os portais da direita (nada alto nasce
    no bolsao). Tudo abaixo de 6 studs."""
    F = Frame(23.0, -57.0, 0.0, D(20))          # local -y = sudoeste (vira para quem sobe a escadaria)
    mb = K.AMB("BLD_Shop_Stall", "07_BUILDINGS", rng)
    A = "Shop"
    # carrinho: caixa de tabuas sobre 2 rodas, varais apoiados no chao
    K.lbox(mb, F, (4.6, 2.6, 0.35), 0, 0, F0 + 1.6, "Wood_Dark", 0.0)
    K.lbox(mb, F, (4.4, 2.4, 1.0), 0, 0, F0 + 2.25, "Wood_Plank", 0.0)
    for sy in (-1, 1):
        mb.cyl(1.05, 0.3, F.p(0.6, sy * 1.45, F0 + 1.05), F.r(D(90), 0, 0), "Wood_Dark", 10, bevel=0.0)
        mb.cyl(0.3, 0.45, F.p(0.6, sy * 1.45, F0 + 1.05), F.r(D(90), 0, 0), "Metal_Dark", 6, bevel=0.0)
        K.lbeam(mb, F, (-2.2, sy * 0.9, F0 + 1.6), (-4.6, sy * 0.7, F0 + 0.2), 0.25, 0.25, "Wood_Dark", 0.0)
    K.lbox(mb, F, (0.4, 2.6, 1.9), -1.9, 0, F0 + 0.95, "Wood_Dark", 0.0)
    # mercadoria: caixotes abertos com cristais e minerio
    for i, (x, m) in enumerate(((-1.1, "Crystal_Blue"), (0.2, "Crystal_Purple"), (1.5, "Crystal_Blue"))):
        K.lbox(mb, F, (1.2, 1.5, 0.7), x, -0.2, F0 + 3.05, "Wood_Dark", 0.0, rz=rng.uniform(-0.1, 0.1))
        crystal_cluster(mb, tuple(F.p(x, -0.2, F0 + 3.3)), 0.34, m, rng, 3)
    # toldo listrado em 2 postes
    for sx in (-2.1, 2.1):
        K.lbox(mb, F, (0.3, 0.3, 3.4), sx, 1.2, F0 + 3.9, "Wood_Dark", 0.0)
    for k in range(5):
        x = -2.3 + k * 1.15
        K.lbox(mb, F, (1.15, 3.0, 0.2), x + 0.575, -0.1, F0 + 5.35, "Cloth_Red" if k % 2 else "Cloth_Canvas", 0.0,
               rx=0.32)
    # barril e placa-seta (tabua vermelha com a picareta) apontando para a porta da loja
    barrel(mb, tuple(F.p(3.4, 0.6, F0)), r=0.8, h=2.0)
    Fs = Frame(F.p(-3.2, -2.4).x, F.p(-3.2, -2.4).y, 0.0, math.atan2(-39.0 - F.p(-3.2, -2.4).y, 26.0 - F.p(-3.2, -2.4).x))
    K.lbox(mb, Fs, (0.35, 0.35, 4.6), 0, 0, F0 + 2.3, "Wood_Dark", 0.0)
    K.vprism(mb, Fs, [(-0.6, F0 + 3.2), (1.8, F0 + 3.2), (2.6, F0 + 3.75), (1.8, F0 + 4.3), (-0.6, F0 + 4.3)], -0.12, 0.12,
             "Cloth_Red", "y")
    K.lbox(mb, Fs, (0.25, 0.3, 1.3), -0.5, 0, F0 + 3.75, "Wood_Dark", 0.0)
    # adro da banca: lajes soltas no gramado entre a banca e a quina da loja + colisao rasa pisavel (mesmo idioma
    # das portas das cabanas: a vegetacao, que evita COL_, nao nasce no corredor de visada spawn -> OP/OPM)
    lr = random.Random(5757)
    for i in range(16):
        x = lr.uniform(18.0, 29.5)
        y = lr.uniform(-61.0, -49.0)
        if (x - 23.0) ** 2 + (y + 57.0) ** 2 < 10.0:
            continue
        a = lr.uniform(0, math.pi)
        hw, hd = lr.uniform(0.8, 1.3), lr.uniform(0.6, 1.0)
        ca, sa = math.cos(a), math.sin(a)
        pts = [(x + u * ca - v * sa, y + u * sa + v * ca) for u, v in ((-hw, -hd), (hw, -hd), (hw, hd), (-hw, hd))]
        _slab(mb, pts, F0 - 0.1, F0 + 0.12 + lr.uniform(0.0, 0.06), "Stone_Paving" if i % 3 else "Stone_Paving_B")
    mb.finish()
    col_box2(A, (17.0, -62.0, F0 - 0.1), (30.0, -47.6, F0 + 0.12))
    q = F.p(0, 0)
    col_box(A, (5.2, 3.2, 5.6), (q.x, q.y, F0 + 2.8), F.r())
    q = F.p(3.4, 0.6)
    col_box(A, (1.8, 1.8, 2.2), (q.x, q.y, F0 + 1.1), F.r())
    q = Fs.p(0, 0)
    col_box(A, (0.6, 0.6, 4.6), (q.x, q.y, F0 + 2.3), Fs.r())


# ------------------------------------------------------------------ cabanas de mineiros (entraveis)
# Passe fix2: linguagem por FUNCAO. As cabanas sao casas de trabalhador - parede BAIXA de toras ou de tabua e
# mata-junta sobre fundacao de pedra, chamine externa grossa de pedra bruta num dos lados, telhado envelhecido
# (ardosia com musgo ou tabuinha escura; so o sobrado tem telha queimada) e, no lugar da floreira, a vida do
# mineiro: cabide com picareta e pa, capacete com lanterna no gancho, amostras de minerio no peitoril.
# Cada uma sorteia 2-3 tracos: oitao truncado, catslide (cumeeira deslocada), quatro aguas, puxado, telheiro,
# balanco de um lado so, cumeeira torcida. Pegadas, portas e marcadores nao mudaram.
CABINS = {
    # oeste, porta para o penhasco (oeste). TORAS + ardosia com musgo; oitao TRUNCADO no fundo (leste, visto da
    # praca), telheiro de lenha ao norte, chamine de pedra bruta ao sul, cumeeira torcida (casa assentada).
    "West_A": dict(
        pos=(-84.0, -4.0, -90), w=14.0, d=12.0,
        V=dict(lower="none", upper="log", zs=1.0, ze=7.6, pitch=40.0, door=(4.2, 9.8, 7.0, 0.0),
               wins={1: [(3.2, 5.4, 3.2, 5.8, "cross+lit+ore"),
                                                            (9.4, 10.3, 2.8, 6.0, "slit")],
                     2: [(4.0, 7.0, 3.2, 5.8, "two+ore+dark")], 3: [(8.8, 10.6, 3.4, 5.6, "cross")]},
               roof=dict(family="slate", over=(1.8, 1.8), ends=(1.3, 1.6), hips=(0.0, 2.6), sag=0.45,
                         skew=(0.2, -0.16, 0.0, -0.3), course=1.6),
               gables={0: dict(window=(1.6, 1.6, 2.2, "round")), 1: dict(window=(1.8, 1.3, 1.1), lit=True)},
               chimneys=[dict(kind="rubble", side=1, y=2.4, name="Cabin_West_A")],
               lean=[dict(edge=3, s0=1.2, s1=7.8, depth=3.2, z_hi=6.3, z_lo=4.6, content="logs")],
               tools=[dict(edge=3, s=10.0, kinds=("pick", "shovel")), dict(edge=0, s=13.3, kinds=("lamp",))]),
        inner=[("bed", -3.6, 1.8, 0), ("table", 1.6, -0.6, ((-2.4, 0.0), (2.4, 0.0))), ("shelf", -4.6, -2.6, 1),
               ("crate", 4.2, -3.0), ("rug", 0.8, 1.2)]),
    # oeste: SOBRADO do capataz - terreo de pedra, andar de enxaimel com reboco ocre claro em balanco SO a leste
    # (para a praca), telhado ingreme (52 graus) de telha queimada com remendos, oculo no oitao, chamine de pedra
    # bruta ao norte, capacete no gancho junto a porta, jirau interno.
    "West_B": dict(
        pos=(-94.0, 20.0, -90), w=12.0, d=11.0,
        V=dict(lower="stone", upper="timber", zs=7.0, ze=12.4, pitch=52.0, door=(3.2, 8.8, 6.8, 1.7),
               jet=(0.0, 0.0, 0.9, 0.0), plaster="Plaster_Ochre_Light", course=2.3, blk=(3.4, 5.4), post=5.0,
               back=(0, 1, 3), stone_bev=0.0,
               wins={0: [(4.2, 7.6, 8.6, 11.2, "two+lit")], 1: [(3.0, 5.0, 2.8, 5.4, "two+ore"),
                                                               (3.6, 7.0, 8.6, 11.2, "grid+dark")],
                     2: [(2.8, 6.0, 8.6, 11.2, "two+lit+shut")], 3: [(6.6, 8.2, 8.8, 11.0, "cross")]},
               roof=dict(family="tile", over=(1.6, 1.9), ends=(1.2, 1.4), sag=0.5, course=1.75, tile=(2.1, 3.1)),
               gables={0: dict(style="collar", window=(1.9, 1.9, 2.6, "round")),
                       1: dict(style="king", window=(2.0, 1.7, 2.0))},
               chimneys=[dict(kind="rubble", side=-1, y=-1.0, name="Cabin_West_B", sh=1.6, top=0.6)],
               tools=[dict(edge=1, s=8.0, kinds=("pick", "shovel", "lamp"))],
               paint="Wood_Plank"),
        inner=[("bed", 2.6, 1.3, 0), ("table", -2.0, 2.4, ((0.0, -1.9),)), ("crate", 3.4, -2.9),
               ("crate", -3.4, -3.0), ("rug", 0.0, -0.6), ("loft", 0.6, 4.1)]),
    # oeste, porta para o sul: TABUA-E-MATA-JUNTA, CATSLIDE - cumeeira deslocada para oeste e a agua leste descendo
    # ate um anexo baixo; tabuinha escura com musgo, alpendre com banco na frente, chamine de pedra bruta a oeste.
    "West_C": dict(
        pos=(-64.0, 26.0, 0), w=12.0, d=10.0,
        V=dict(lower="none", upper="board", zs=0.9, ze=7.4, rise=4.8, door=(3.6, 9.0, 6.8, 0.0),
               wins={2: [(3.8, 6.4, 3.2, 5.8, "cross+ore+lit")],
                     3: [(2.2, 4.0, 3.2, 5.6, "two")]},
               roof=dict(family="shingle", cx=-1.8, over=(1.6, 1.5), ends=(1.5, 1.5), sag=0.35, course=1.45,
                         tile=(1.7, 2.6)),
               outshot=dict(depth=3.2, y0=-4.4, y1=4.4, window=0.4),
               gables={0: dict(window=(1.4, 1.2, 1.6, "round")), 1: dict()},
               chimneys=[dict(kind="rubble", side=-1, y=1.2, name="Cabin_West_C", wd=3.4)],
               porch=dict(s0=0.8, s1=11.2, depth=3.2, z_hi=7.3, z_lo=6.3, bench=(0.9, 3.3)),
               tools=[dict(edge=3, s=8.0, kinds=("lamp",))], lantern="hang"),
        inner=[("bed", -2.8, 0.9, 0), ("table", 1.0, -1.4, ((2.2, 0.0), (0.0, 1.9))), ("crate", -3.6, -2.7),
               ("shelf", 2.4, 3.1, 0), ("rug", 0.4, 1.0)]),
    # leste, porta para o penhasco (leste): TORAS, PUXADO (saltbox) ao norte, janela saliente ao sul, chamine de
    # pedra bruta ao sul, ardosia com musgo, cumeeira torcida.
    "East_A": dict(
        pos=(114.0, -6.0, 90), w=14.0, d=12.0,
        V=dict(lower="none", upper="log", zs=1.0, ze=7.8, pitch=42.0, door=(4.2, 9.8, 7.0, 0.0),
               wins={2: [(2.4, 4.8, 3.2, 5.8, "cross+lit+ore"),
                                                               (9.4, 10.3, 2.8, 6.0, "slit")]},
               bays=[dict(edge=3, s=8.6, wd=3.8, z0=2.8, z1=6.0, out=1.1, lit=True)],
               roof=dict(family="slate", over=(1.9, 1.5), ends=(1.3, 1.5), sag=0.4, skew=(-0.18, 0.14, -0.25, 0.0)),
               outshot=dict(depth=2.8, y0=-4.8, y1=4.6, window=0.0),
               gables={0: dict(window=(1.5, 1.3, 1.6)), 1: dict(window=(1.7, 1.7, 2.2, "round"))},
               chimneys=[dict(kind="rubble", side=-1, y=3.2, name="Cabin_East_A")],
               tools=[dict(edge=2, s=7.1, kinds=("pick", "shovel")), dict(edge=0, s=13.3, kinds=("lamp",))]),
        inner=[("bed", -3.8, 1.6, 0), ("table", 2.6, -0.8, ((-2.4, 0.0), (2.2, 0.0))), ("crate", -4.4, -3.4),
               ("shelf", 4.6, 2.6, 1), ("rug", 0.0, -1.0)]),
    # leste: TABUA-E-MATA-JUNTA, QUATRO AGUAS de tabuinha escura, chamine de pedra bruta ao norte, telheiro de
    # minerio nos fundos (voltado para o caminho), capacete e ferramentas na parede sul.
    "East_B": dict(
        pos=(116.0, 18.0, 90), w=12.0, d=11.0,
        V=dict(lower="none", upper="board", zs=0.9, ze=7.4, pitch=38.0, door=(3.2, 8.8, 7.0, 0.0),
               wins={1: [(6.6, 9.0, 3.2, 5.8, "cross+ore")],
                     3: [(4.4, 7.4, 3.2, 5.8, "grid+lit+shut"), (9.4, 10.2, 2.6, 6.0, "slit")]},
               roof=dict(kind="hip", family="shingle", over=(1.7, 1.7), ends=(1.7, 1.7), sag=0.35, course=1.45,
                         tile=(1.7, 2.6)),
               chimneys=[dict(kind="rubble", side=1, y=-2.4, name="Cabin_East_B")],
               lean=[dict(edge=2, s0=0.6, s1=5.4, depth=3.0, z_hi=6.0, z_lo=4.6, content="ore")],
               tools=[dict(edge=3, s=2.0, kinds=("pick", "lamp"))]),
        inner=[("bed", -2.8, 1.4, 0), ("table", 1.4, 1.6, ((0.0, -1.9), (2.2, 0.0))), ("crate", -3.6, -3.1),
               ("shelf", 3.9, -0.4, 1), ("rug", 0.2, -1.4)]),
}


def cabin_interior(mb, F, w, d, rng, items, A, name):
    """mobilia (vai para BLD_Cabin_<nome>_Interior): paleta curta - tabua, madeira escura, lona, pano vermelho,
    ferro, cristal e a luz da vela"""
    zf = F0 + 0.55
    for it in items:
        kind = it[0]
        if kind == "bed":
            _, x, y, rot = it
            sx, sy = (3.6, 5.4) if not rot else (5.4, 3.6)
            p = F.p(x, y)
            mb.box((sx, sy, 1.2), (p.x, p.y, zf + 0.6), F.r(), "Wood_Dark", 0.0)
            mb.box((sx - 0.4, sy - 0.4, 0.6), (p.x, p.y, zf + 1.45), F.r(), "Cloth_Canvas", 0.1)
            head = F.p(x, y + sy / 2 - 1.0) if not rot else F.p(x + sx / 2 - 1.0, y)
            mb.box((sx - 0.8, 1.3, 0.6) if not rot else (1.3, sy - 0.8, 0.6), (head.x, head.y, zf + 1.95), F.r(),
                   "Cloth_Canvas", 0.15)
            blk = F.p(x, y - sy * 0.18) if not rot else F.p(x - sx * 0.18, y)
            mb.box((sx - 0.2, sy * 0.58, 0.35) if not rot else (sx * 0.58, sy - 0.2, 0.35), (blk.x, blk.y, zf + 1.8),
                   F.r(), "Cloth_Red", 0.0)
            hb = F.p(x, y + sy / 2 + 0.1) if not rot else F.p(x + sx / 2 + 0.1, y)
            mb.box((sx + 0.2, 0.45, 3.0) if not rot else (0.45, sy + 0.2, 3.0), (hb.x, hb.y, zf + 1.5), F.r(),
                   "Wood_Dark", 0.0)
            col_box(A, (sx, sy, 2.4), (p.x, p.y, F0 + 1.2), F.r())
        elif kind == "table":
            _, x, y, stools = it
            p = F.p(x, y)
            mb.box((3.4, 2.4, 0.3), (p.x, p.y, zf + 2.5), F.r(0, 0, rng.uniform(-0.04, 0.04)), "Wood_Plank", 0.0)
            for sx in (-1, 1):
                for sy in (-1, 1):
                    q = F.p(x + sx * 1.3, y + sy * 0.9)
                    mb.box((0.35, 0.35, 2.4), (q.x, q.y, zf + 1.2), F.r(), "Wood_Dark", 0.0)
            xs, ys = [x - 1.7, x + 1.7], [y - 1.2, y + 1.2]
            for (dx, dy) in stools:
                q = F.p(x + dx, y + dy)
                mb.cyl(0.6, 1.6, (q.x, q.y, zf + 0.8), F.r(), "Wood_Plank", 8, bevel=0.0)
                xs += [x + dx - 0.6, x + dx + 0.6]
                ys += [y + dy - 0.6, y + dy + 0.6]
            mb.box((0.5, 0.5, 0.7), F.p(x - 0.5, y + 0.2, zf + 3.0), F.r(), "Lantern_Glow", 0.0)
            mb.cyl(0.4, 0.2, F.p(x - 0.5, y + 0.2, zf + 2.72), F.r(), "Wood_Dark", 8, bevel=0.0)
            mb.cyl(0.35, 0.6, F.p(x + 0.8, y - 0.3, zf + 2.95), F.r(), "Wood_Dark", 8, bevel=0.0)
            c = F.p((min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2)
            col_box(A, (max(xs) - min(xs), max(ys) - min(ys), 3.2), (c.x, c.y, F0 + 1.6), F.r())
        elif kind == "shelf":
            _, x, y, rot = it
            L_ = 3.4
            for zz in (zf + 1.8, zf + 3.6):
                mb.box((0.9, L_, 0.25) if rot else (L_, 0.9, 0.25), F.p(x, y, zz), F.r(), "Wood_Plank", 0.0)
                for k in range(3):
                    off = -L_ / 2 + 0.6 + k * 1.1
                    q = F.p(x, y + off) if rot else F.p(x + off, y)
                    if rng.random() < 0.5:
                        mb.cyl(0.3, 0.8, (q.x, q.y, zz + 0.52), F.r(), "Wood_Dark", 8, bevel=0.0)
                    else:
                        crystal_cluster(mb, (q.x, q.y, zz + 0.12), 0.22, "Crystal_Blue", rng, 2)
            for k in (-1, 1):
                q = F.p(x, y + k * (L_ / 2 - 0.1)) if rot else F.p(x + k * (L_ / 2 - 0.1), y)
                mb.box((0.25, 0.25, 4.2), (q.x, q.y, zf + 2.1), F.r(), "Wood_Dark", 0.0)
        elif kind == "crate":
            # bau de mineiro com cintas (madeira escura: o interior fica sem MeshPart de metal)
            _, x, y = it
            a = rng.uniform(-0.25, 0.25)
            q = F.p(x, y)
            mb.box((2.2, 1.4, 1.2), (q.x, q.y, zf + 0.6), F.r(0, 0, a), "Wood_Plank", 0.0)
            mb.box((2.35, 1.55, 0.4), (q.x, q.y, zf + 1.35), F.r(0, 0, a), "Wood_Dark", 0.0)
            Fc = Frame(q.x, q.y, 0.0, F.a + a)
            for sx in (-0.65, 0.65):
                mb.box((0.22, 1.62, 1.6), Fc.p(sx, 0, zf + 0.82), Fc.r(), "Wood_Dark", 0.0)
            col_box(A, (2.4, 1.6, 2.0), (q.x, q.y, F0 + 1.0), F.r(0, 0, a))
        elif kind == "barrel":
            _, x, y = it
            barrel(mb, tuple(F.p(x, y, zf)), r=0.9, h=2.2)
            q = F.p(x, y)
            col_box(A, (2.0, 2.0, 2.4), (q.x, q.y, F0 + 1.2), F.r())
        elif kind == "rug":
            _, x, y = it
            mb.box((4.2, 3.0, 0.08), F.p(x, y, zf + 0.04), F.r(0, 0, rng.uniform(-0.08, 0.08)), "Cloth_Red", 0.0)
            mb.box((3.4, 2.2, 0.1), F.p(x, y, zf + 0.06), F.r(0, 0, rng.uniform(-0.08, 0.08)), "Cloth_Canvas", 0.0)
        elif kind == "loft":
            # jirau de tabuas no fundo do sobrado + escada de mao
            _, x, y_back = it
            zl = F0 + 8.2
            Fl = Frame(F.p(0, y_back - 1.8).x, F.p(0, y_back - 1.8).y, 0.0, F.a)
            plank_floor(mb, Fl, w - 2.8, 3.6, zl, rng, m_alt=("Wood_Dark", "Wood_Dark"))
            mb.box((w - 2.8, 0.5, 0.7), F.p(0, y_back - 3.7, zl - 0.35), F.r(), "Wood_Dark", 0.0)
            yl = y_back - 4.1
            zm = (zl + F0) / 2 + 0.2
            for sx in (-1, 1):
                mb.box((0.25, 0.25, zl - F0 - 0.5), F.p(x + sx * 0.8, yl, zm), F.r(-0.12, 0, 0), "Wood_Plank", 0.0)
            for k in range(6):
                zz = F0 + 1.3 + k * 1.2
                mb.box((1.6, 0.2, 0.2), F.p(x, yl + (zz - zm) * 0.12, zz), F.r(), "Wood_Plank", 0.0)
            for k, sx in enumerate((-2.8, -1.7)):
                mb.ico(0.85, F.p(sx, y_back - 1.5 + k * 0.4, zl + 0.95), "Cloth_Canvas", 1, (1.0, 0.8, 1.0),
                       jitter=0.15)
            # caixote no jirau (no lugar do barril: o interior fica sem MeshPart de metal e ~200 tris mais leve)
            mb.box((1.6, 1.3, 1.1), F.p(-0.4, y_back - 1.4, zl + 0.85), F.r(0, 0, 0.2), "Wood_Plank", 0.0)
            mb.box((1.75, 1.45, 0.3), F.p(-0.4, y_back - 1.4, zl + 1.45), F.r(0, 0, 0.2), "Wood_Dark", 0.0)


def cabin(name, rng):
    spec = CABINS[name]
    cx, cy, ang = spec["pos"]
    w, d = spec["w"], spec["d"]
    V = dict(spec["V"])
    V.setdefault("apron", True)     # pedras de passo + area livre de vegetacao diante da porta
    V.setdefault("back", (2,))
    F = Frame(cx, cy, 0.0, D(ang))
    A = "Cabin"
    mb = K.AMB("BLD_Cabin_" + name, "07_BUILDINGS", rng)
    mi = K.AMB("BLD_Cabin_" + name + "_Interior", "07_BUILDINGS", rng)
    info = house(mb, F, w, d, F0, rng, V, area=A, name=name, mbi=mi)
    t_in = info["t_in"]
    # piso e mobilia (objeto de interior separado: sem sombra no Roblox, Model da casa)
    plank_floor(mi, F, w - 2 * t_in, d - 2 * t_in, F0 + 0.3, rng, m_alt=("Wood_Dark", "Wood_Dark"))
    cabin_interior(mi, F, w, d, rng, spec["inner"], A, name)
    mi.finish()
    ds0, ds1, dh, darch = V["door"]
    Fe0 = info["EF"][0][0]
    if V.get("lantern") == "hang":
        P = V["porch"]
        hanging_lantern(mb, tuple(Fe0.p(P["s1"] - 1.6, -P["depth"] + 0.9, F0 + P["z_lo"] - 0.2)), name="L_Cabin_" + name,
                        chain=0.6)
    else:
        lantern(mb, tuple(F.p(w / 2 - 1.0, -d / 2 - 2.2, F0)), F.a - math.pi / 2, name="L_Cabin_" + name, h=5.5)
        q = F.p(w / 2 - 1.0, -d / 2 - 2.2)
        col_box(A, (1.4, 1.4, 7.0), (q.x, q.y, F0 + 3.5), F.r())
    light("L_Cabin_In_" + name, "POINT", tuple(F.p(0, 1.0, F0 + 5.5)), 90, (1.0, 0.6, 0.3), 0.5)
    mb.finish()
    marker("DOOR_Cabin_" + name, tuple(F.p(0, -d / 2, F0)), F.r(0, 0, -math.pi / 2), 1.5)


# ------------------------------------------------------------------ estacao de carga sobre o trilho + galpao leste
def open_truss(mb, F, y, hw, z0, z_r, rng, m="Wood_Dark"):
    """tesoura aberta (linha + pendural + escoras) no plano local y - oitao de telheiro sem parede"""
    K.lbox(mb, F, (0.6, 0.6, z_r - z0 - 0.4), 0, y, (z0 + z_r - 0.4) / 2, m, 0.06)
    for sx in (-1, 1):
        K.lbeam(mb, F, (sx * hw * 0.62, y, z0 + 0.3), (sx * 0.3, y, z0 + (z_r - z0) * 0.55), 0.45, 0.45, m, 0.05)


def weigh_station(rng):
    """telheiro aberto sobre o trilho (balanca de vagonetes, caixas, lanterna) - nao cria expectativa de porta"""
    import fm_mine
    pts = fm_mine.rail_path(fm_mine.tunnel_frame())
    fine = resample(pts, 1.0)
    # ponto do trilho na praca oeste
    idx = min(range(len(fine)), key=lambda k: (fine[k] - Vector((-54, -8, F0))).length)
    p = fine[idx]
    tdir = (fine[idx + 1] - fine[idx - 1]).normalized()
    a = math.atan2(tdir.y, tdir.x)
    F = Frame(p.x, p.y, 0, a)
    mb = K.AMB("BLD_Rail_Weigh_Station", "07_BUILDINGS", rng)
    for sx in (-5.0, 5.0):
        for sy in (-5.5, 5.5):
            q = F.p(sx, sy)
            lean = rng.uniform(-0.025, 0.025)
            mb.box((1.0, 1.0, 9.6), (q.x, q.y, F0 + 5.4), F.r(lean, rng.uniform(-0.02, 0.02), 0), "Wood_Dark", 0.12)
            mb.box((1.9, 1.9, 1.0), (q.x, q.y, F0 + 0.45), F.r(rng.uniform(-0.04, 0.04), 0, rng.uniform(-0.3, 0.3)),
                   "Stone_Dark", 0.18)
            mb.box((1.3, 1.3, 0.5), (q.x, q.y, F0 + 1.1), F.r(0, 0, rng.uniform(-0.2, 0.2)), "Stone_Light", 0.12)
            col_box("Station", (1.2, 1.2, 10.0), (q.x, q.y, F0 + 5.0), F.r())
            # maos-francesas nos dois sentidos
            K.lbeam(mb, F, (sx, sy, F0 + 7.6), (sx * 0.62, sy, F0 + 9.8), 0.45, 0.5, "Wood_Dark", 0.05)
            K.lbeam(mb, F, (sx, sy, F0 + 7.8), (sx, sy * 0.66, F0 + 9.8), 0.45, 0.5, "Wood_Dark", 0.05)
    for sy in (-5.5, 5.5):
        mb.beam(F.p(-6.2, sy, F0 + 10.2), F.p(6.2, sy, F0 + 10.2 + rng.uniform(-0.08, 0.08)), 0.95, 1.05, "Wood_Dark",
                0.08)
    for sx in (-5.0, 5.0):
        mb.beam(F.p(sx, -6.4, F0 + 10.2), F.p(sx, 6.4, F0 + 10.2), 0.9, 1.0, "Wood_Dark", 0.08)
    # telhado de 2 aguas (cumeeira ao longo do trilho) em ripas de madeira, com tesouras abertas nas pontas
    Fr = K.sub(F, 0, 0, D(-90))
    z_r = F0 + 14.0
    K.gable_roof(mb, Fr, 0.0, -5.6, 5.6, z_r, rng, sides=((6.0, F0 + 10.8, 1.3), (6.0, F0 + 10.8, 1.3)),
                 ends=((1.1, 0.0), (1.4, 0.0)), m="Roof_Shingle_Dark", m2="Roof_Shingle_Moss", alt=0.04, sag=0.35,
                 tile=(1.6, 2.6), course=1.45, rafters=2.0, bevel=0.0, patches=True, row_jit=0.25)
    for yy in (-5.0, 5.0):
        open_truss(mb, Fr, yy, 6.0, F0 + 10.7, z_r, rng)
    # balanca (plataforma de ferro sob o trilho) e mostrador
    q = F.p(0, 0)
    mb.box((6.0, 4.6, 0.25), (q.x, q.y, F0 + 0.02), F.r(), "Metal_Iron", 0.03)
    for sx in (-1, 1):
        mb.box((6.2, 0.35, 0.3), F.p(0, sx * 2.35, F0 + 0.15), F.r(), "Metal_Dark", 0.02)
    q2 = F.p(0, 4.4)
    mb.box((1.2, 1.2, 4.6), (q2.x, q2.y, F0 + 2.3), F.r(), "Wood_Dark", 0.1)
    mb.cyl(1.2, 0.4, (q2.x, q2.y, F0 + 5.2), F.r(D(90), 0, 0), "Metal_Brass", 16, bevel=0.05)
    mb.cyl(0.9, 0.45, F.p(0, 4.2, F0 + 5.2), F.r(D(90), 0, 0), "Emblem_Cream", 16, bevel=0.0)
    mb.beam(F.p(0, 4.0, F0 + 5.2), F.p(0.55, 4.0, F0 + 5.8), 0.12, 0.12, "Metal_Dark", 0.0)
    col_box("Station", (1.4, 1.4, 5.0), (q2.x, q2.y, F0 + 2.5), F.r())
    for i, (sx, sy) in enumerate(((3.5, -4.2), (-3.5, -4.4), (-3.0, 4.6))):
        crate(mb, tuple(F.p(sx, sy, F0)), 2.2, a + rng.uniform(-0.3, 0.3), rng)
        q3 = F.p(sx, sy)
        col_box("Station", (2.4, 2.4, 2.4), (q3.x, q3.y, F0 + 1.2), F.r())
    crystal_cluster(mb, tuple(F.p(3.5, -4.2, F0 + 2.2)), 0.45, "Crystal_Blue", rng, 4)
    hanging_lantern(mb, tuple(F.p(0, 0, F0 + 10.0)), name="L_Station", chain=1.5)
    mb.finish()
    marker("RAIL_Weigh_Station", (p.x, p.y, F0), F.r(), 2)


def crystal_shed(rng):
    """DEPOSITO da margem leste: combustivel da forja (baias de carvao, sacos, pa, carrinho de mao) + cristais
    refinados aguardando o carrinho. Aberto para o norte (caminho). Passe fix2: deixa de ser um caixote cego -
    tabua-e-mata-junta com faixa de RIPAS VAZADAS de ventilacao no alto (sul e oeste), telheiro com sacos e pa na
    face sul, placa e pilha de caixotes vazios sob o telheiro da face oeste (a que se ve do caminho)."""
    F = Frame(112.0, -34.0, 0, D(180))     # local -y = norte (frente aberta); +y = sul; +x = oeste
    mb = K.AMB("BLD_Crystal_Shed", "07_BUILDINGS", rng)
    w, d = 16.0, 10.0
    t = 0.7
    zv0, zv1 = F0 + 5.6, F0 + 7.9           # faixa de ripas vazadas
    # paredes: fundo (sul), oeste, leste - base de pedra + tabuas ate zv0 + ripas ate o frechal
    walls = ((F.p(w / 2, d / 2), F.p(-w / 2, d / 2), True),      # sul (vista por fora pela direita)
             (F.p(w / 2, -d / 2), F.p(w / 2, d / 2), True),      # oeste
             (F.p(-w / 2, d / 2), F.p(-w / 2, -d / 2), False))   # leste (encostada no penhasco)
    for (a, b, vent) in walls:
        dv = b - a
        Lw = dv.length
        ang = math.atan2(dv.y, dv.x)
        Fw = Frame(a.x, a.y, 0.0, ang)
        masonry_wall(mb, a, b, F0 - 0.2, F0 + 1.0, t + 0.5, rng, course=1.2, mix=0.1, core=False)
        K.board_wall(mb, Fw, 0.0, Lw, F0 + 1.0, zv0 if vent else zv1, 0.0, t, rng, step=1.4, out_sign=-1)
        if vent:
            # ripas horizontais com vao entre elas: a luz passa, o galpao respira (e le como deposito)
            for k in range(4):
                zz = zv0 + 0.35 + k * 0.6
                K.lbox(mb, Fw, (Lw, 0.25, 0.3), Lw / 2, 0.0, zz, "Wood_Plank", 0.0, rx=0.35)
            for s_ in [Lw * f / 4 for f in range(1, 4)]:
                K.lbox(mb, Fw, (0.4, 0.5, zv1 - zv0), s_, 0.0, (zv0 + zv1) / 2, "Wood_Dark", 0.0)
        K.lbox(mb, Fw, (Lw + 0.6, 0.6, 0.6), Lw / 2, 0.0, zv1 + 0.2, "Wood_Dark", 0.0)
        for s_ in (0.0, Lw):
            K.lbox(mb, Fw, (0.9, 0.9, zv1 - F0), s_, 0.0, (F0 + zv1) / 2, "Wood_Dark", 0.0)
        cc = (a + b) / 2
        col_box("Shed", (Lw, t + 0.2, 8.0), (cc.x, cc.y, F0 + 4.0), (0, 0, ang))
    zf_, zb_ = F0 + 11.0, F0 + 8.4
    for sx in (-w / 2, w / 2):
        q = F.p(sx, -d / 2)
        mb.box((1.1, 1.1, 10.4), (q.x, q.y, F0 + 5.2), F.r(), "Wood_Dark", 0.0)
        mb.box((1.8, 1.8, 0.9), (q.x, q.y, F0 + 0.4), F.r(0, 0, rng.uniform(-0.3, 0.3)), "Stone_Dark", 0.0)
        K.lbeam(mb, F, (sx, -d / 2, F0 + 6.8), (sx * 0.7, -d / 2, F0 + 9.8), 0.5, 0.55, "Wood_Dark", 0.0)
        K.vprism(mb, F, [(d / 2, zv1), (-d / 2, zv1), (-d / 2, zf_ - 0.45), (d / 2, zb_ - 0.35)],
                 sx - 0.3, sx + 0.3, "Wood_Plank", "x")
    mb.beam(F.p(-w / 2 - 0.6, -d / 2, F0 + 10.0), F.p(w / 2 + 0.6, -d / 2, F0 + 10.15), 0.95, 1.05, "Wood_Dark", 0.0)
    # agua unica: alta na frente aberta, baixa no fundo - ardosia com musgo
    g = (zf_ - zb_) / d
    E0, E1 = F.p(w / 2 + 0.9, d / 2 + 1.0, zb_ - g * 1.0), F.p(-w / 2 - 0.9, d / 2 + 1.0, zb_ - g * 1.0)
    R0, R1 = F.p(w / 2 + 0.9, -d / 2 - 1.2, zf_ + g * 1.2), F.p(-w / 2 - 0.9, -d / 2 - 1.2, zf_ + g * 1.2)
    P, N, Lr = K.roof_plane(mb, E0, E1, R0, R1, rng, "Roof", "Roof_Moss", 0.04, 0.42, 0.3, 1.5, (1.8, 2.8),
                            0.13, 0.3, bevel=0.0, patches=True, row_jit=0.25)
    for u in (0.0, 1.0):
        pts = [P(Lr * f / 3, u) for f in range(4)]
        for pa, pb in zip(pts, pts[1:]):
            dd = (pb - pa).normalized()
            mb.beam(pa - dd * 0.1 - N * 0.1 + N * (0.5 if u else 0.0), pb + dd * 0.1 - N * 0.1 + N * (0.5 if u else 0.0),
                    0.45, 0.8, "Wood_Dark", 0.0)
    for s in (0.0, Lr):
        mb.beam(P(s, 0.0) + N * 0.25, P(s, 1.0) + N * 0.25, 0.5, 1.1, "Wood_Dark", 0.0)
    for k in range(4):
        x = -w / 2 + 2.0 + k * 4.0
        K.lbeam(mb, F, (x, d / 2, zb_ - 0.4), (x, -d / 2, zf_ - 0.5), 0.5, 0.6, "Wood_Dark", 0.0)
    # dentro: tres baias de carvao em chapa de ferro encostadas no fundo (combustivel da fornalha)
    for k in range(3):
        bx = -w / 2 + 2.8 + k * 3.6
        by = d / 2 - 2.0
        for sx in (-1, 1):
            K.lbox(mb, F, (0.3, 3.2, 2.0), bx + sx * 1.65, by, F0 + 1.0, "Metal_Dark", 0.0)
        K.lbox(mb, F, (3.6, 0.3, 1.3), bx, by - 1.55, F0 + 0.65, "Metal_Dark", 0.0)
        for j in range(2):
            q = F.p(bx + (j - 0.5) * 1.2 + rng.uniform(-0.3, 0.3), by + rng.uniform(-0.4, 0.6))
            mb.rock((q.x, q.y, F0 + 0.9 + j * 0.3), (2.2, 2.0, 1.4), "Metal_Dark", 1)
    q = F.p(-w / 2 + 6.4, d / 2 - 2.0)
    col_box("Shed", (11.0, 3.4, 2.2), (q.x, q.y, F0 + 1.1), F.r())
    # pa encostada na baia e carrinho de mao
    K.lbeam(mb, F, (-w / 2 + 8.5, d / 2 - 3.8, F0 + 0.3), (-w / 2 + 8.9, d / 2 - 3.5, F0 + 4.2), 0.2, 0.2,
            "Wood_Light", 0.0)
    K.lbox(mb, F, (0.9, 0.14, 1.1), -w / 2 + 8.45, d / 2 - 3.85, F0 + 0.6, "Metal_Dark", 0.0, rx=0.3)
    Fw_ = K.sub(F, 2.6, 1.0, D(20))
    K.lbox(mb, Fw_, (2.0, 1.6, 0.9), 0.0, 0.0, F0 + 1.3, "Wood_Plank", 0.0)
    mb.cyl(0.55, 0.3, Fw_.p(-1.3, 0.0, F0 + 0.55), Fw_.r(D(90), 0, D(90)), "Metal_Dark", 8, bevel=0.0)
    for sy in (-0.6, 0.6):
        K.lbeam(mb, Fw_, (-0.9, sy, F0 + 0.9), (2.4, sy * 1.1, F0 + 1.4), 0.2, 0.2, "Wood_Dark", 0.0)
    for ky, kz in ((1.8, 1.0), (1.2, 2.1)):
        mb.rock(tuple(Fw_.p(ky - 1.8, 0.0, F0 + kz)), (0.9, 0.8, 0.6), "Metal_Dark", 1)
    q = F.p(2.6, 1.0)
    col_box("Shed", (3.4, 2.4, 2.4), (q.x, q.y, F0 + 1.2), F.r(0, 0, D(20)))
    # cristais refinados aguardando o carrinho + o carrinho
    for k in range(2):
        q = F.p(w / 2 - 2.4 - k * 3.4, d / 2 - 2.2, 0)
        mb.box((3.0, 2.8, 2.2), (q.x, q.y, F0 + 1.1), F.r(0, 0, rng.uniform(-0.06, 0.06)), "Wood_Plank", 0.0)
        mb.box((3.2, 0.35, 0.4), (q.x, q.y, F0 + 1.9), F.r(0, 0, 0), "Wood_Dark", 0.0)
        crystal_cluster(mb, (q.x, q.y, F0 + 2.2), 0.6, "Crystal_Blue", rng, 5)
        col_box("Shed", (3.0, 2.8, 3.4), (q.x, q.y, F0 + 1.7), F.r())
    mine_cart(mb, tuple(F.p(-3.0, -1.6, F0)), F.a, "Crystal_Blue", rng)
    q = F.p(-3.0, -1.6)
    col_box("Shed", (3.6, 2.6, 3.4), (q.x, q.y, F0 + 1.7), F.r())
    # face SUL: telheiro com sacos de carvao empilhados
    Fs = Frame(F.p(w / 2, d / 2).x, F.p(w / 2, d / 2).y, 0.0, F.a + math.pi)   # x ao longo da face sul, -y = fora
    K.lean_to(mb, Fs, 3.0, 11.0, 0.0, 2.6, F0 + 5.3, F0 + 4.4, rng, -1, m="Roof", m2="Roof_Moss", area="Shed",
              z_ground=F0, sag=0.1, bevel=0.0, alt=0.05, braces=False)
    for i in range(4):
        p = Fs.p(4.2 + i * 1.8 + rng.uniform(-0.2, 0.2), -1.3 + rng.uniform(-0.2, 0.2), F0 + 0.75)
        mb.ico(0.95, p, "Cloth_Canvas", 1, (1.0, 0.75, 0.8), jitter=0.12)
        if i == 1:
            mb.ico(0.85, p + Vector((0.6, 0.1, 1.2)), "Cloth_Canvas", 1, (1.0, 0.75, 0.8), jitter=0.12)
    q = Fs.p(7.0, -1.3)
    col_box("Shed", (8.0, 2.2, 2.4), (q.x, q.y, F0 + 1.2), Fs.r())
    # face OESTE (vista do caminho): telheiro sobre a pilha de caixotes vazios + placa
    Fo = Frame(F.p(w / 2, -d / 2).x, F.p(w / 2, -d / 2).y, 0.0, F.a + D(90))  # x ao longo da face oeste, -y = fora
    K.lean_to(mb, Fo, 1.2, 8.6, 0.0, 2.8, F0 + 6.0, F0 + 4.9, rng, -1, m="Roof", m2="Roof_Moss", area="Shed",
              z_ground=F0, sag=0.1, bevel=0.0, alt=0.05, braces=False)
    for (cx_, cy_, cz_, s_) in ((2.6, -1.3, 0.0, 2.0), (4.7, -1.2, 0.0, 2.0), (3.5, -1.3, 2.0, 1.8), (6.8, -1.1, 0.0, 1.6)):
        # caixote vazio (tampa aberta encostada): caixa + 2 cintas, sem chanfro
        Fc = K.sub(Fo, cx_, cy_, rng.uniform(-0.25, 0.25))
        K.lbox(mb, Fc, (s_, s_, s_ * 0.9), 0, 0, F0 + cz_ + s_ * 0.45, "Wood_Plank", 0.0)
        for zz in (0.15, 0.75):
            K.lbox(mb, Fc, (s_ + 0.1, s_ + 0.1, 0.22), 0, 0, F0 + cz_ + s_ * 0.9 * zz, "Wood_Dark", 0.0)
    q = Fo.p(4.5, -1.3)
    col_box("Shed", (6.2, 2.4, 4.0), (q.x, q.y, F0 + 2.0), Fo.r())
    # placa: tabua com cristal pintado + martelos (deposito da forja), pregada na parede oeste
    K.lbox(mb, Fo, (3.6, 0.3, 1.6), 4.4, -0.45, F0 + 7.4, "Wood_Dark", 0.0)
    K.lbox(mb, Fo, (3.1, 0.34, 1.15), 4.4, -0.5, F0 + 7.4, "Wood_Plank", 0.0)
    crystal_cluster(mb, tuple(Fo.p(4.4, -0.75, F0 + 6.95)), 0.24, "Crystal_Blue", rng, 3)
    # placa da frente (pendurada na viga)
    for sx in (-1.1, 1.1):
        mb.rod(F.p(sx, -d / 2, F0 + 8.0), F.p(sx, -d / 2, F0 + 6.9), 0.07, "Metal_Dark", 4)
    mb.box((3.2, 0.35, 1.5), F.p(0, -d / 2, F0 + 6.2), F.r(), "Wood_Plank", 0.0)
    crystal_cluster(mb, tuple(F.p(0, -d / 2 - 0.25, F0 + 5.7)), 0.3, "Crystal_Blue", rng, 3)
    hanging_lantern(mb, tuple(F.p(0, 0, F0 + 9.3)), name="L_Shed", chain=1.5)
    mb.finish()


def build():
    rng = random.Random(909)
    plaza_and_paths(rng)
    shop(rng)
    # cabanas: oeste (entre trilho e penhasco) e leste (margem) - cada uma com variante propria
    for name in ("West_A", "West_B", "West_C", "East_A", "East_B"):
        cabin(name, rng)
    weigh_station(rng)
    crystal_shed(rng)
