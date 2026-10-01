# fm_konoha - TRANSICAO PARA A PRIMEIRA ILHA: moon gate do portal Naruto -> patio com o 2o torii -> Passo da Folha
# (canion de rocha com patamares de sakura/pinheiros e trepadeiras) -> ponte suspensa sobre a garganta (paredes
# invisiveis nas bordas + RESPAWN) -> Grande Portao de Konoha (WORLD_EXIT) -> mirante com parapeito, placa e janela.
# Tracado, largura caminhavel e posicoes (portao, ponte, marcadores) sao os mesmos; mudam acabamento e colisao:
#   * a colisao das paredes do canion SEGUE A ROCHA (raios contra a malha pronta: face interna e externa)
#   * piso: ~7 caixas longas (trechos com variacao de yaw < 3 graus) no lugar de 65 fatias de 2 studs
#   * arvores do fm_veg_kit (abeto, pinheiro jovem, sakura) em grupos nos patamares e bordas; no piso so onde a
#     rocha recua, fora da faixa do caminho e com COL de copa
import math, random
import bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from fm_lib import MB, D, col_box, col_ramp, marker, light, resample, bezier
from fm_parts import cliff_band, frustum
import fm_portal_kit as K
import fm_layout as L

C = "06_PORTALS"
T = L.TERR
W = 14.0            # largura do caminho de terra
FHW = 16.0          # meia-largura do piso (visual e COL): passa por baixo da rocha (face a 11-15.5), sem fresta
#                     entre a borda do piso e a COL da parede (antes 13: sobrava um poco de ate 2.5 studs)
WALL = W / 2 + 6.5  # linha das paredes do canion (a mesma de antes)
YAW_TOL = 3.0       # graus: trechos de piso fundidos numa caixa so
KP = "Konoha"


def path_pts():
    kp = [Vector((x, y, T)) for x, y in L.KONOHA_PATH]
    out = [kp[0]]
    for a, b, c in zip(kp, kp[1:], kp[2:]):
        out += bezier((a + b) / 2, b, b, (b + c) / 2, 6)[1:]
    out.append(kp[-1])
    return resample(out, 2.0)


def side_of(pts, i):
    j = min(i + 1, len(pts) - 1)
    k = max(i - 1, 0)
    t = (pts[j] - pts[k]).normalized()
    return t, Vector((-t.y, t.x, 0))


def _bvh(ob):
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    bm.transform(ob.matrix_world)
    tree = BVHTree.FromBMesh(bm)
    bm.free()
    return tree


def _runs(pts, g0, g1):
    """segmentos de piso (i -> i+1) fora da garganta, agrupados em trechos com variacao de yaw < YAW_TOL"""
    segs = [i for i in range(len(pts) - 1) if not (g0 - 1 < (pts[i].y + pts[i + 1].y) / 2 < g1 + 1)]
    runs, cur, a0 = [], [], 0.0
    for i in segs:
        d = pts[i + 1] - pts[i]
        a = math.degrees(math.atan2(d.y, d.x))
        if cur and (i != cur[-1] + 1 or abs(a - a0) > YAW_TOL):
            runs.append(cur)
            cur = []
        if not cur:
            a0 = a
        cur.append(i)
    if cur:
        runs.append(cur)
    return runs


# ------------------------------------------------------------------ patio atras do moon gate
def approach(ap, fl, tr, rng):
    """patio atras do portal Naruto ate a boca do canion: sando de lajes, segundo torii com varal de lanternas de
    papel, toro, bambuzal (profundidade: moon gate -> torii menor -> lanternas -> canion)"""
    x0 = L.KONOHA_PATH[0][0]
    y_back = L.PORTAL_Y + 5.4       # fundo da plataforma do portal Naruto
    K.flag_floor(fl, [(x0 - 4.2, y_back - 0.4), (x0 + 4.2, y_back - 0.4), (x0 + 4.2, 134.0), (x0 - 4.2, 134.0)], T - 0.2,
                 rng, "Stone_Paving", None, tile=3.2, h=0.42, bevel=0.0, base=False)
    for s in (-1, 1):
        for k in range(5):
            y = y_back + 1.2 + k * 3.1
            fl.box((0.5, 2.4, 0.3), (x0 + s * 4.55, y, T + 0.05), (0, 0, rng.uniform(-0.05, 0.05)), "Stone_Paving", 0.0)
    ty = 123.6
    for s in (-1, 1):
        x = x0 + s * 7.9
        ap.cyl(1.05, 0.9, (x, ty, T + 0.45), (0, 0, 0), "Stone_Dark", 10, bevel=0.1)
        ap.cyl(0.78, 14.2, (x, ty, T + 7.1), (0, 0, 0), "P_Naruto_Red", 10, r2=0.68, bevel=0.05)
        ap.cyl(0.9, 0.8, (x, ty, T + 1.3), (0, 0, 0), "Wood_Dark", 10, bevel=0.0)
        col_box(KP, (1.7, 1.7, 14.0), (x, ty, T + 7.0))
    ap.box((19.0, 0.9, 1.0), (x0, ty, T + 11.4), (0, 0, 0), "P_Naruto_Red", 0.1)
    kas = [Vector((x0 + x, ty, T + 14.4 + 0.02 * x * x)) for x in range(-11, 12, 2)]
    ap.sweep(kas, [(-0.9, -0.7), (0.9, -0.7), (1.0, 0.6), (-1.0, 0.6)], "Wood_Dark", True, up=(0, 0, 1))
    ap.sweep([p + Vector((0, 0, -1.3)) for p in kas[1:-1]], [(-0.7, -0.55), (0.7, -0.55), (0.7, 0.55), (-0.7, 0.55)],
             "P_Naruto_Red", True, up=(0, 0, 1))
    ap.box((1.6, 0.9, 2.0), (x0, ty - 0.1, T + 12.9), (0, 0, 0), "Wood_Dark", 0.1)
    for s in (-1, 1):
        x, y = x0 + s * 9.6, y_back + 2.8
        K.toro(ap, (x, y, T), 0.95, "Stone_Light", "Stone_Dark", glow="P_Naruto_Glow", name="L_Konoha_Toro_%d" % (s + 1))
        col_box(KP, (2.4, 2.4, 6.2), (x, y, T + 3.1))
    for dx in (-5.2, -2.6, 0.0, 2.6, 5.2):
        K.chochin(ap, (x0 + dx, ty - 0.2, T + 10.9), r=0.62, h=1.2, paper="P_Naruto_Glow", cap="P_Naruto_Red",
                  hang=0.35 + 0.25 * abs(dx) / 5.2, n=6, rod_m="Wood_Dark")
    light("L_Konoha_Festival", "POINT", (x0, ty - 1.5, T + 9.0), 260, (1.0, 0.6, 0.3), 1.0)
    K.bamboo(tr, (x0 - 10.4, 137.5, T), rng, n=5, h=(10.0, 15.0))
    col_box(KP, (2.6, 2.6, 8.0), (x0 - 10.4, 137.5, T + 4.0))


# ------------------------------------------------------------------ Grande Portao (>= 30 de altura)
def great_gate(gt, gp, t, s, a, rng):
    GW = W + 6.0
    red, blk, tl, wal = "P_Naruto_Red", "Wood_Dark", "P_Naruto_Tile", "P_Naruto_Wall"
    ZT = T + 30.0
    up = Vector((0, 0, 1))
    for k in (-1, 1):
        q = gp + s * k * (GW / 2 + 1.5)
        # torre: soco de pedra, fuste de madeira com faixas vermelhas, chapeu de telha de 4 aguas
        gt.box((4.8, 4.8, 4.0), (q.x, q.y, T + 2.0), (0, 0, a), "Stone_Dark", 0.2)
        gt.box((3.6, 3.6, ZT - T - 4.0), (q.x, q.y, (T + 4.0 + ZT) / 2), (0, 0, a), blk, 0.2)
        for zz in (T + 10.0, T + 20.0):
            gt.box((3.8, 3.8, 0.7), (q.x, q.y, zz), (0, 0, a), red, 0.05)
        gt.box((4.4, 4.4, 0.6), (q.x, q.y, ZT + 0.3), (0, 0, a), blk, 0.1)
        frustum(gt, (q.x, q.y, ZT + 0.6), 6.4, 6.4, 1.0, 1.0, 2.6, tl, ang=a)
        gt.ico(0.45, (q.x, q.y, ZT + 3.5), red, 1, (1, 1, 1.4))
        # folhas do portao entreabertas, PINTADAS: verde fosco, circulo vermelho e a folha-espiral em creme
        h = gp + s * k * (GW / 2 - 0.5) + t * 0.5
        leaf_c = h + t * 4.5 + s * k * -1.0
        la = a + k * D(15)
        gt.box((0.8, 9.0, 22.0), (leaf_c.x, leaf_c.y, T + 11.2), (0, 0, la), "P_Konoha_Door", 0.12)
        lt = Vector((math.cos(la), math.sin(la), 0))
        ln = Vector((-lt.y, lt.x, 0))
        for zz in (T + 3.2, T + 19.4):
            gt.box((1.0, 9.2, 0.7), (leaf_c.x, leaf_c.y, zz), (0, 0, la), blk, 0.05)
        disc = Vector((leaf_c.x, leaf_c.y, T + 11.5)) - lt * 0.48
        gt.cyl(2.8, 0.2, disc, (0, D(90), la), red, 18, bevel=0.0)
        # folha-espiral de Konoha pintada em creme no circulo vermelho (espelhada entre as duas folhas)
        g0 = disc - lt * 0.14
        gs = [g0 + ln * (k * math.cos(tt) * 0.2 * tt) + up * (math.sin(tt) * 0.2 * tt) for tt in
              [0.3 + i * 0.5 for i in range(19)]]
        gt.tube(gs, 0.17, wal, 5)
        K.cone(gt, gs[-1], gs[-1] + ln * (k * 0.6) - up * 0.9, 0.2, 0.0, wal, 4)
        col_box(KP, (4.4, 4.4, 30.0), (q.x, q.y, T + 15.0), (0, 0, a))
        col_box(KP, (1.0, 9.0, 22.0), (leaf_c.x, leaf_c.y, T + 11.2), (0, 0, la))
        # muralha lateral de reboco com telhadinho, entrando na rocha do canion
        m0 = gp + s * k * (GW / 2 + 3.3)
        m1 = gp + s * k * (WALL + 3.0)
        K.village_wall(gt, (m0.x, m0.y), (m1.x, m1.y), T, 13.0, rng, thick=1.6, post_step=3.0)
    # vigas e telhado de duas aguas em 2 niveis sobre o vao
    gt.box((2.4, GW + 6.0, 1.6), (gp.x, gp.y, T + 23.0), (0, 0, a), red, 0.12)
    gt.box((3.4, GW + 9.0, 2.4), (gp.x, gp.y, T + 27.4), (0, 0, a), blk, 0.2)
    gt.box((1.2, GW + 6.0, 0.6), (gp.x, gp.y, T + 25.0), (0, 0, a), blk, 0.0)
    frustum(gt, (gp.x, gp.y, T + 28.6), GW + 13.0, 9.0, GW + 7.0, 3.2, 3.0, tl, ang=a + math.pi / 2)
    frustum(gt, (gp.x, gp.y, T + 31.4), GW + 6.0, 4.4, GW + 3.0, 1.2, 2.4, tl, ang=a + math.pi / 2)
    gt.box((1.0, GW + 5.0, 0.9), (gp.x, gp.y, T + 34.0), (0, 0, a), blk, 0.1)
    for k in (-1, 1):
        e = Vector((gp.x, gp.y, T + 34.0)) + s * k * (GW / 2 + 2.4)
        K.cone(gt, e, e + s * k * 0.8 + up * 1.4, 0.45, 0.05, blk, 4)
    # emblema grande: disco creme com a folha-espiral vermelha, na frente das vigas (abaixo do beiral)
    ec = gp - t * 2.2 + up * 23.9
    gt.cyl(4.6, 0.6, ec, (D(90), 0, a - math.pi / 2), wal, 24, bevel=0.1)
    K.ring(gt, ec - t * 0.2, 4.7, s, up, 0.6, 0.8, red, n=28)
    spiral = [ec - t * 0.45 + s * math.cos(tt) * 0.3 * tt + up * (math.sin(tt) * 0.3 * tt) for tt in
              [i * 0.45 for i in range(24)]]
    gt.tube(spiral, 0.34, red, 6)
    K.cone(gt, spiral[-1], spiral[-1] + s * 0.9 - up * 1.4, 0.36, 0.0, red, 4)
    for k in (-1, 1):
        K.chochin(gt, tuple(gp + s * k * 6.8 - t * 1.0 + up * 22.1), r=1.0, h=2.0, paper="P_Naruto_Glow", cap=blk,
                  band=red, hang=1.0, rod_m=blk)
    light("L_Konoha_Gate", "POINT", tuple(gp - t * 6 + up * 8), 800, (1.0, 0.7, 0.4), 2.0)
    marker("WORLD_EXIT_Naruto", tuple(gp), (0, 0, a), 4, "ARROWS",
           props={"destino": "Konoha", "tipo": "saida_continua", "nota": "passar o portao = entrar na ilha 1"})


def overlook(gt, end, t, s, a, rng):
    """mirante alem do portao: parapeito de pedra (COL alta), placa e janela redonda de vista na direcao do vao"""
    marker("WORLD_ENTRY_Naruto", tuple(end + t * 4.0), (0, 0, a), 4, "ARROWS",
           props={"origem": "Lobby", "nota": "ponto de chegada vindo do lobby; alinhar com a entrada da Area 1"})
    hw = W / 2 + 3
    up = Vector((0, 0, 1))
    edges = [(end + t * 14 + s * hw, end + t * 14 - s * hw), (end + s * hw, end + t * 14 + s * hw),
             (end - s * hw, end + t * 14 - s * hw)]
    for (p0, p1) in edges:
        d = p1 - p0
        n = max(1, int(d.length / 2.6))
        ang = math.atan2(d.y, d.x)
        for i in range(n):
            c = p0 + d * ((i + 0.5) / n)
            hh = 2.9 + rng.uniform(-0.12, 0.12)
            gt.box((d.length / n - 0.1, 1.4, hh), (c.x, c.y, T + hh / 2), (0, 0, ang), "Stone_Light", 0.15)
        cc = (p0 + p1) / 2
        gt.box((d.length + 0.4, 1.7, 0.4), (cc.x, cc.y, T + 3.1), (0, 0, ang), "Stone_Dark", 0.08)
        col_box(KP, (d.length, 1.0, 8.0), (cc.x, cc.y, T + 4.0), (0, 0, ang))
    # janela de vista: aro redondo de madeira sobre um peitoril de pedra, com telhadinho, no canto NE do mirante,
    # GIRADA para o vao da cordilheira (a ~38 graus a leste do eixo: dali se ve o recorte de picos baixos e ceu;
    # de frente, so a encosta do pico mais proximo)
    av = D(38.0)
    nd = (t * math.cos(av) - s * math.sin(av)).normalized()      # -s = leste
    sd = Vector((nd.y, -nd.x, 0.0))
    ay = math.atan2(sd.y, sd.x)
    wp = end + t * 11.5 - s * 5.5
    wc = Vector((wp.x, wp.y, T + 7.2))
    K.ring(gt, wc, 3.6, sd, up, 0.7, 0.9, "Wood_Dark", n=28)
    for k in (-1, 1):
        p = wp + sd * k * 3.9
        gt.box((0.7, 0.7, 11.1), (p.x, p.y, T + 5.55), (0, 0, ay), "Wood_Dark", 0.05)
    gt.box((7.1, 1.0, 3.3), (wp.x, wp.y, T + 1.65), (0, 0, ay), "Stone_Light", 0.12)
    gt.box((7.5, 1.3, 0.35), (wp.x, wp.y, T + 3.35), (0, 0, ay), "Stone_Dark", 0.05)
    gt.box((9.4, 0.8, 0.5), (wc.x, wc.y, T + 11.1), (0, 0, ay), "Wood_Dark", 0.0)
    K.tile_coping(gt, tuple(wp + sd * 4.6), tuple(wp - sd * 4.6), T + 11.35, 0.9, over=0.6, rise=0.7)
    col_box(KP, (8.6, 1.2, 11.5), (wp.x, wp.y, T + 5.75), (0, 0, ay))
    # placa (icone da folha, sem texto) na entrada do mirante, de frente para quem chega
    sp = end + t * 3.0 + s * (hw - 1.6)
    for k in (-1, 1):
        q = sp + s * k * 1.5
        gt.box((0.5, 0.5, 4.6), (q.x, q.y, T + 2.3), (0, 0, a), "Wood_Dark", 0.05)
    gt.box((0.35, 3.4, 1.9), (sp.x, sp.y, T + 3.7), (0, 0, a), "Wood_Plank", 0.06)
    ic = sp - t * 0.25 + up * (T + 3.7 - sp.z)
    gt.cyl(0.62, 0.12, ic, (0, D(90), a), "P_Naruto_Red", 12, bevel=0.0)
    col_box(KP, (0.8, 3.6, 4.6), (sp.x, sp.y, T + 2.3), (0, 0, a))


# ------------------------------------------------------------------ vegetacao do canion
def _tree_spots(bvh_w, pts, rng, g0, g1):
    """patamares/topos de rocha perto da borda do canion (raio para baixo contra a malha do canion)"""
    spots = []
    for i in range(3, len(pts) - 3, 3):
        p = pts[i]
        if g0 - 5 < p.y < g1 + 5:
            continue
        t, s = side_of(pts, i)
        for k in (-1, 1):
            for dist in (14.5, 17.5, 20.5):
                q = p + s * k * (dist + rng.uniform(-1.0, 1.0)) + t * rng.uniform(-1.5, 1.5)
                hit = bvh_w.ray_cast(Vector((q.x, q.y, T + 90)), Vector((0, 0, -1)), 130)
                if hit[0] is None or hit[1].z < 0.72:
                    continue
                z = hit[0].z
                if T + 5.0 < z < T + 42.0:
                    spots.append((Vector((q.x, q.y, z)), k, s.copy(), t.copy(), z - T, dist))
    return spots


def vegetation(tr, bvh_w, pts, rng, g0, g1, face):
    import fm_veg_kit as VK
    pal = ("Leaf_Pine", "Leaf_Pine_Light")
    spots = _tree_spots(bvh_w, pts, rng, g0, g1)
    rng.shuffle(spots)
    used = []
    nsak = 0
    for (q, k, s, t, hz, dist) in spots:
        if any((q - u).length < 7.5 for u in used) or len(used) >= 20:
            continue
        used.append(q)
        edge = dist < 16.0
        r = rng.random()
        if r < 0.3 and nsak < 6:
            VK.sakura_tree(tr, tuple(q), rng.uniform(7.5, 10.0), rng, lod=1)
            nsak += 1
        elif r < 0.55:
            VK.young_pine(tr, tuple(q), rng.uniform(6.0, 8.5), rng, lod=1, pal=pal)
        else:
            wind = math.atan2(-s.y * k, -s.x * k) if edge else None     # abeto da borda pende para o canion
            VK.fir(tr, tuple(q), rng.uniform(10.0, 15.0), rng, lod=1, pal=pal, wind=wind, lean_amt=0.1 if edge else 0.0)
        # trepadeira caindo da borda do patamar pela face da rocha
        if edge and hz > 8.0 and rng.random() < 0.7:
            i0 = min(range(len(pts)), key=lambda j: abs(pts[j].y - q.y))
            d_face = face(i0, k)
            if d_face is not None:
                _, s0 = side_of(pts, i0)
                top = pts[i0] + s0 * k * (d_face + 0.5)
                ln = min(hz - 3.0, rng.uniform(5.0, 9.0))
                if ln > 2.5:
                    K.vine(tr, Vector((top.x, top.y, T + hz - 0.4)), ln, rng, "Leaf_Pine_Light", 0.6, 0.4)
    # pequenos grupos no piso onde a rocha recua (fora da faixa do caminho, com COL de copa)
    for i in range(8, len(pts) - 6, 10):
        p = pts[i]
        if g0 - 8 < p.y < g1 + 8:
            continue
        t, s = side_of(pts, i)
        for k in (-1, 1):
            d_face = face(i, k)
            if d_face is None:
                continue
            dist = min(d_face - 2.6, W / 2 + 4.5)
            if dist < W / 2 + 3.5:
                continue
            q = p + s * k * dist
            if rng.random() < 0.5:
                VK.young_pine(tr, (q.x, q.y, T), rng.uniform(4.4, 5.4), rng, lod=1, pal=pal)
            else:
                VK.sakura_tree(tr, (q.x, q.y, T), rng.uniform(6.0, 7.2), rng, lod=1)
            col_box(KP, (4.6, 4.6, 5.0), (q.x, q.y, T + 2.5))


def build():
    rng = random.Random(808)
    pts = path_pts()
    g0, g1 = L.KONOHA_GORGE
    ig = min(range(len(pts)), key=lambda k: abs(pts[k].y - L.KONOHA_GATE_Y))
    gp = pts[ig]
    tg, sg = side_of(pts, ig)
    ag = math.atan2(tg.y, tg.x)
    end = pts[-1]

    cv = MB("KONOHA_Canyon", "02_TERRAIN", rng)                      # paredes + piso + garganta
    dec = K.LeanMB("KONOHA_Pass_Decor", C, rng, vcap=1)               # torii, toro, lanternas
    trs = K.LeanMB("KONOHA_Trees", C, rng, vcap=1)                    # arvores, bambu, trepadeiras
    approach(dec, cv, trs, random.Random(809))

    # ---- piso: fita continua (grama + terra batida + corpo de rocha) interrompida na garganta
    runs = _runs(pts, g0, g1)
    before = [r for r in runs if pts[r[0]].y < g0]
    after = [r for r in runs if pts[r[0]].y > g1]
    for group in (before, after):
        idx = sorted(set(i for r in group for i in r))
        if not idx:
            continue
        ribbon = [pts[i] for i in idx] + [pts[idx[-1] + 1]]
        cv.sweep(ribbon, [(-FHW, -30.6), (FHW, -30.6), (FHW, -0.6), (-FHW, -0.6)], "Cliff_Rock_Dark", True, up=(0, 0, 1))
        cv.sweep(ribbon, [(-FHW, -0.6), (FHW, -0.6), (FHW, 0.0), (-FHW, 0.0)], "Grass", True, up=(0, 0, 1))
        cv.sweep(ribbon, [(-(W / 2 - 1), -0.1), (W / 2 - 1, -0.1), (W / 2 - 1, 0.2), (-(W / 2 - 1), 0.2)], "Dirt", True,
                 up=(0, 0, 1))
    for i in range(0, len(pts) - 1, 3):
        p = pts[i]
        if g0 - 2 < p.y < g1 + 2:
            continue
        t, s = side_of(pts, i)
        a = math.atan2(t.y, t.x)
        off = s * (1.6 if (i // 3) % 2 else -1.8) * rng.uniform(0.6, 1.4)
        cv.box((rng.uniform(2.0, 2.6), rng.uniform(1.6, 2.2), 0.35), (p.x + off.x, p.y + off.y, T + 0.25),
               (0, 0, a + rng.uniform(-0.3, 0.3)), "Stone_Paving", 0.0)
    # piso do mirante
    cv.box((14.0, W + 6, 1.0), (end.x + tg.x * 7, end.y + tg.y * 7, T - 0.5), (0, 0, ag), "Stone_Paving", 0.0)
    col_box(KP, (14.0, W + 6, 4.0), (end.x + tg.x * 7, end.y + tg.y * 7, T - 2.0), (0, 0, ag), "Floor")
    # COL do piso: uma caixa por trecho reto (juntas com 0.5 de sobreposicao; bordas da garganta exatas)
    last_before = before[-1] if before else None
    first_after = after[0] if after else None
    for r in runs:
        a, b = pts[r[0]], pts[r[-1] + 1]
        d = b - a
        dn = d.normalized()
        ext0 = 0.15 if r[0] == 0 else (0.0 if r is first_after else 0.5)
        ext1 = 0.15 if r[-1] + 1 == len(pts) - 1 else (0.0 if r is last_before else 0.5)
        a2, b2 = a - dn * ext0, b + dn * ext1
        c = (a2 + b2) / 2
        col_box(KP, ((b2 - a2).length, 2 * FHW, 4), (c.x, c.y, T - 2), (0, 0, math.atan2(d.y, d.x)), "Floor")
    edge_s = pts[last_before[-1] + 1] if last_before else None     # borda sul da garganta
    edge_n = pts[first_after[0]] if first_after else None          # borda norte

    # ---- paredes do canion (face para dentro, cristas irregulares) + paredes dentro da garganta
    for side in (-1, 1):
        wall = []
        for i, p in enumerate(pts):
            t, s = side_of(pts, i)
            wall.append(p + s * side * WALL)
        cliff_band(cv, wall, T - 40, 64, rng, depth=3, rmin=4.5, rmax=7.5, step=6.5, face_side=-side, var=3.2,
                   top_fn=lambda c: 60 + 10 * math.sin(c.y * 0.05))
    gc = [p for p in pts if g0 - 2 < p.y < g1 + 2]
    for side in (-1, 1):
        cp = []
        for p in gc:
            i = pts.index(p)
            t, s = side_of(pts, i)
            cp.append(p + s * side * WALL)
        cliff_band(cv, cp, T - 60, 62, rng, depth=2, rmin=5, rmax=8, step=6, face_side=-side, var=3.0)
    mid = gc[len(gc) // 2]
    for i in range(12):
        cv.ico(rng.uniform(4, 8), (mid.x + rng.uniform(-16, 16), mid.y + rng.uniform(-10, 10), T - 34 + rng.uniform(-4, 4)),
               "Foam", 1, (1.4, 1.0, 0.5), jitter=0.2)
    cvo = cv.finish()
    bvh_w = _bvh(cvo)

    # ---- COL das paredes SEGUINDO A ROCHA: raios do eixo para fora (face interna, recuo 0.5) e de fora para dentro
    # (face externa: quem vem do terraco atras dos portais tambem nao entra na rocha)
    faces = {}
    for i, p in enumerate(pts):
        t, s = side_of(pts, i)
        for k in (-1, 1):
            best = None
            for hz in (1.0, 3.0, 5.0, 7.0):
                h = bvh_w.ray_cast(Vector((p.x, p.y, T + hz)), s * k, 40.0)
                if h[0] is not None:
                    best = h[3] if best is None else min(best, h[3])
            faces[(i, k)] = best

    def face(i, k):
        return faces.get((i, k))

    def outer(i, k, far=34.0):
        p = pts[i]
        t, s = side_of(pts, i)
        best = None
        for hz in (1.0, 4.0):
            h = bvh_w.ray_cast(Vector((p.x, p.y, T + hz)) + s * k * far, -s * k, far - 6.0)
            if h[0] is not None:
                best = (far - h[3]) if best is None else max(best, far - h[3])
        return best

    step = 6
    for k in (-1, 1):
        for i0 in range(0, len(pts) - 1, step):
            i1 = min(i0 + step, len(pts) - 1)
            ds = [faces[(i, k)] for i in range(i0, i1 + 1) if faces[(i, k)] is not None]
            if not ds:
                continue
            d_in = max(W / 2 + 1.0, min(ds) - 0.5)
            outs = [o for o in (outer(i, k) for i in range(i0, i1 + 1, 2)) if o is not None]
            d_out = max(max(outs) + 0.3 if outs else WALL + 6.0, d_in + 3.0)
            a, b = pts[i0], pts[i1]
            d = b - a
            tt = d.normalized()
            sv = Vector((-tt.y, tt.x, 0))
            c = (a + b) / 2 + sv * k * ((d_in + d_out) / 2)
            col_box(KP, (d.length + 1.0, d_out - d_in, 50), (c.x, c.y, T + 20), (0, 0, math.atan2(d.y, d.x)))

    # ---- ponte suspensa (flecha 1.8, COL acompanhando) + bordas da garganta fechadas + respawn
    br = K.LeanMB("KONOHA_Rope_Bridge", C, rng, vcap=2)
    ia_ = min(range(len(pts)), key=lambda k: abs(pts[k].y - (g0 - 1.5)))
    ib_ = min(range(len(pts)), key=lambda k: abs(pts[k].y - (g1 + 1.5)))
    A_, B_ = pts[ia_], pts[ib_]
    d = B_ - A_
    Lb = d.length
    ang = math.atan2(d.y, d.x)
    side = Vector((-math.sin(ang), math.cos(ang), 0))
    bw = 7.0
    post = bw / 2 + 0.6
    sag = 1.8
    n = int(Lb / 1.1)
    deck = []
    for i in range(n + 1):
        f = i / n
        p = A_ + d * f
        p.z = T - sag * 4 * f * (1 - f)
        deck.append(p)
        br.box((0.9, bw, 0.35), (p.x, p.y, p.z - 0.15), (0, 0, ang + rng.uniform(-0.03, 0.03)), "Wood_Plank", 0.0)
    for k in (-1, 1):
        base = [p + side * k * (bw / 2) for p in deck]
        br.tube([p + Vector((0, 0, -0.4)) for p in base], 0.22, "Rope", 5)
        top = [p + Vector((0, 0, 3.4 + 1.2 * (1 - 4 * (i / n) * (1 - i / n)))) for i, p in enumerate(base)]
        br.tube(top, 0.26, "Rope", 5)
        for i in range(0, n + 1, 2):
            br.rod(base[i], top[i], 0.07, "Rope", 3)
        for P in (A_, B_):
            q = P + side * k * post
            br.box((1.2, 1.2, 6.5), (q.x, q.y, T + 3.2), (0, 0, ang), "Wood_Dark", 0.12)
            br.box((1.6, 1.6, 0.6), (q.x, q.y, T + 6.6), (0, 0, ang), "P_Naruto_Red", 0.1)
            col_box(KP, (1.4, 1.4, 7.0), (q.x, q.y, T + 3.5), (0, 0, ang))
    # pedras na boca da garganta, ao lado dos postes (ficam fora da malha do canion: nao entram na medicao da face
    # da rocha, que puxava a COL da parede para 8 studs do eixo nos dois trechos vizinhos a garganta)
    for e in (edge_s, edge_n):
        if e is None:
            continue
        t, s = side_of(pts, pts.index(e))
        for k in (-1, 1):
            q = e + s * k * (W / 2 + 2.6)
            br.rock((q.x, q.y, T + 0.6), (4.0, 3.5, 3.0), "Cliff_Rock", 1)
            col_box(KP, (3.2, 2.8, 3.0), (q.x, q.y, T + 1.5), (0, 0, math.atan2(t.y, t.x)))
    br.finish()
    k6 = 6
    for i in range(k6):
        f0, f1 = i / k6, (i + 1) / k6
        pa, pb = A_ + d * f0, A_ + d * f1
        pa.z = T - sag * 4 * f0 * (1 - f0)
        pb.z = T - sag * 4 * f1 * (1 - f1)
        col_ramp(KP, pa, pb, bw, 1.0)
    for k in (-1, 1):
        c = (A_ + B_) / 2 + side * k * (bw / 2 + 0.3)
        col_box(KP, (Lb + 2, 0.6, 10.0), (c.x, c.y, T + 2.0), (0, 0, ang))      # topo z37: nao da para pular
    # paredes invisiveis de altura 8 nas bordas da garganta (de x-114 ate o poste; do outro poste ate x-87), e no
    # minimo ate 1 stud alem da borda do piso (FHW), por dentro da COL da parede do canion: sem fresta nas pontas
    for e, base, sgn in ((edge_s, A_, -1.0), (edge_n, B_, 1.0)):
        if e is None:
            continue
        t, s = side_of(pts, pts.index(e))
        tp = (base - e).dot(s)
        tw = max((e.x + 114.0) / -s.x, FHW + 1.0)          # s aponta para oeste (x decresce)
        te = min((e.x + 87.0) / -s.x, -(FHW + 1.0))
        for (ta, tb) in ((tp + post + 0.6, tw), (te, tp - post - 0.6)):
            if tb - ta < 0.5:
                continue
            c = e + s * ((ta + tb) / 2) + t * (sgn * 0.4)
            col_box(KP, (tb - ta, 0.8, 10.0), (c.x, c.y, T + 3.0), (0, 0, math.atan2(s.y, s.x)))
    marker("RESPAWN_Konoha_Bridge", (-99.5, 190.0, 30.0), (0, 0, 0), 3, "SPHERE",
           props={"tipo": "respawn", "nota": "quem cair na garganta (VOID_CATCH) volta aqui, antes da ponte"})

    # ---- torii intermediarios e toro de pedra ao longo do caminho
    for yy in (150.0, 180.0, 250.0):
        idx = min(range(len(pts)), key=lambda k: abs(pts[k].y - yy))
        p = pts[idx]
        t, s = side_of(pts, idx)
        for k in (-1, 1):
            q = p + s * k * (W / 2 + 0.8)
            dec.cyl(0.7, 13.0, (q.x, q.y, T + 6.5), (0, 0, 0), "P_Naruto_Red", 10, bevel=0.05)
            dec.cyl(1.0, 0.8, (q.x, q.y, T + 0.4), (0, 0, 0), "Stone_Dark", 10, bevel=0.1)
            col_box(KP, (1.6, 1.6, 13.0), (q.x, q.y, T + 6.5))
        dec.beam(p - s * (W / 2 + 2.6) + Vector((0, 0, 11.0)), p + s * (W / 2 + 2.6) + Vector((0, 0, 11.0)),
                 1.1, 1.0, "P_Naruto_Red", 0.1)
        dec.beam(p - s * (W / 2 + 3.6) + Vector((0, 0, 13.3)), p + s * (W / 2 + 3.6) + Vector((0, 0, 13.3)), 1.4, 1.2,
                 "Wood_Dark", 0.12)
    for i in range(6, len(pts) - 4, 9):
        p = pts[i]
        if g0 - 4 < p.y < g1 + 4:
            continue
        t, s = side_of(pts, i)
        k = 1 if (i // 9) % 2 else -1
        q = p + s * k * (W / 2 + 2.0)
        K.toro(dec, (q.x, q.y, T), 0.8, "Stone_Light", "Stone_Dark", yaw=math.atan2(t.y, t.x), glow="P_Naruto_Glow",
               name="L_Konoha_%03d" % i)
        col_box(KP, (2.8, 2.8, 5.2), (q.x, q.y, T + 2.6))
    dec.finish()

    # ---- Grande Portao + mirante
    gt = K.LeanMB("KONOHA_Great_Gate", C, rng, vcap=1)
    great_gate(gt, gp, tg, sg, ag, rng)
    overlook(gt, end, tg, sg, ag, rng)
    gt.finish()
    vegetation(trs, bvh_w, pts, rng, g0, g1, face)
    trs.finish()
