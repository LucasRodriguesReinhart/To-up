# vm_trecho.py - TRECHO DE QUALIDADE FINAL do lobby Vila Medieval (onda V1): da borda NORTE da praca ate a PONTE DE
# PEDRA do canal, com o kit final (vm_kit). Substitui o blockout do V0 nessa regiao (o vm_blockout nao e editado: este
# modulo apaga/recorta as pecas do V0 que caem no trecho e constroi as finais no lugar).
#
# Conteudo (coordenadas ROBLOX; X leste, Z sul):
#   - FRENTES CONTINUAS de rua (paredes-meias, alturas e recuos variando), 6 casas do kit:
#       oeste:  S0W (C2, estreita, oitao p/ rua, no canal) | S1W (A3, 3 andares, 2 aguas-furtadas) | PNW (F2, de frente
#               para a praca, encostada nos fundos da S1W)
#       leste:  S0E (D3, loja: vitrine + toldo + placa, no canal) | S1E (B2, oitao p/ rua + sacada) | PNE (E2, de
#               frente para a praca, agua-furtada)
#   - rua de PARALELEPIPEDO arredondado em geometria (x +-9) da praca ate o fim da ponte, meio-fio, borda de grama
#     com touceiras, pedras soltas e flores, caminhos de lajes ate as portas
#   - muros do canal em pedra arredondada (x -30..30) + MURETA de pedra seca por cima (onde nao ha casa)
#   - PONTE DE PEDRA: arco de aduelas, abobada, timpanos em pedra, cornija na rampa, guarda-corpo de pedra com capa,
#     pilares nas cabeceiras, tabuleiro de paralelepipedo nas rampas 6,0 -> 7,4 -> 7,0 (a colisao e a do V0)
#   - 2 postes de ferro com lanterna (luz NightOnly L_VM_Lamp_*), carroca, barris, caixotes
#   - MEDALHAO final da praca (picareta + bigorna, rebaixado 0,12, sem colisao)
# A envoltoria livre do Ignis fica longe (z < -52): nada aqui chega perto.
#
# uso (build): o build_vm.py chama build() depois do vm_blockout e cameras() depois do vm_scene.cameras().
# uso (so o trecho para validar no Studio):
#   blender -b --factory-startup lobby_vila_medieval.blend --python vm_trecho.py -- export [pasta]
#       (padrao lobby_area/vila_medieval/export_trecho; FM_ROOT_OFFSET="x, y, z" desloca o modelo no montar)
#   blender -b --factory-startup lobby_vila_medieval.blend --python vm_trecho.py -- report [arquivo.json]
import sys, os, math, json
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import vm_lib as VL
import bpy, bmesh
from mathutils import Vector
import vm_layout as L
import fm_lib
from fm_lib import MB, col_box
from fm_parts import Frame
import vm_kit as K

# ------------------------------------------------------------------ planta do trecho (Roblox)
STREET_X = 9.0                    # meia largura do paralelepipedo (= rua do eixo do V0 e colisao da ponte)
CANAL_X = 30.0                    # os muros do canal sao refeitos em x -30..30
REGION = (-44.0, 44.0, -22.0, 32.0)      # x0, x1, z0, z1: props/arvores do V0 que caem aqui saem
T_PREFIX = ("VM_House_S0W", "VM_House_S1W", "VM_House_PNW", "VM_House_S0E", "VM_House_S1E", "VM_House_PNE",
            "VM_Town_T", "VM_Town_Medallion", "VM_Ter_TCanal")


def _house(id_, preset, x, z, fx, fz, **kw):
    return dict(id=id_, preset=preset, x=x, z=z, fx=fx, fz=fz, kw=kw)


# (x, z) = centro da planta do TERREO; olha para (fx, fz). W = frente, D = fundo (do preset ou kw).
HOUSES = [
    # oeste (olham +X): S0W no canal (parede norte em z -5,5), S1W ate a borda da praca, PNW atras da S1W
    _house("S0W", "C2", -17.4, -1.2, 1, 0, W=8.6, D=10.0, party=("R",), flowers="yellow"),
    _house("S1W", "A3", -17.5, 9.5, 1, 0, W=13.0, D=11.0, party=("L", "B"), flowers="red"),
    _house("PNW", "F2", -28.95, 13.0, 0, 1, W=12.0, D=11.0, party=("L",), plaster="Plaster_VM_Peach",
           stone="Stone_VM_Warm", roof=("Roof_VM_Terracotta_C", "Roof_VM_Terracotta"), flowers="pink"),
    # leste (olham -X): S0E loja no canal, S1E oitao para a rua com sacada, PNE de frente para a praca
    _house("S0E", "D3", 17.3, -0.75, -1, 0, W=9.5, D=10.0, party=("L",), door=dict(side="F", x=-2.2)),
    _house("S1E", "B2", 18.1, 9.9, -1, 0, W=12.0, D=11.0, party=("R", "B"), flowers="pink"),
    _house("PNE", "E2", 30.25, 12.1, 0, 1, W=13.5, D=11.0, party=("R",), flowers="yellow"),
]


def house_spec(h):
    return K.spec_of(h["preset"], seed="T_" + h["id"], **h["kw"])


def house_frame(h):
    return K.frame_r(h["x"], h["z"], L.Y_PAVE, h["fx"], h["fz"])


# ------------------------------------------------------------------ recortes do V0
def _islands(bm):
    parent = {}

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a
    for v in bm.verts:
        parent[v.index] = v.index
    for e in bm.edges:
        a, b = find(e.verts[0].index), find(e.verts[1].index)
        if a != b:
            parent[a] = b
    groups = {}
    for f in bm.faces:
        groups.setdefault(find(f.verts[0].index), []).append(f)
    return list(groups.values())


def drop_islands(ob, pred):
    """apaga as ilhas de malha cujo centro do bbox (Roblox x, z) satisfaz pred"""
    me = ob.data
    bm = bmesh.new()
    bm.from_mesh(me)
    bm.verts.index_update()
    mw = ob.matrix_world
    kill = []
    for isl in _islands(bm):
        vs = {v for f in isl for v in f.verts}
        ps = [mw @ v.co for v in vs]
        cx = (min(p.x for p in ps) + max(p.x for p in ps)) / 2
        cy = (min(p.y for p in ps) + max(p.y for p in ps)) / 2
        if pred(cx, -cy):
            kill.extend(isl)
    if kill:
        bmesh.ops.delete(bm, geom=kill, context="FACES")
    bm.to_mesh(me)
    bm.free()
    return len(kill)


def cut_box(ob, x0, x1, z0, z1):
    """recorta (bisect + apaga + tampa) a malha na caixa Roblox x0..x1, z0..z1 (todas as alturas)"""
    me = ob.data
    bm = bmesh.new()
    bm.from_mesh(me)
    for xc in (x0, x1):
        geom = bm.verts[:] + bm.edges[:] + bm.faces[:]
        bmesh.ops.bisect_plane(bm, geom=geom, plane_co=(xc, 0, 0), plane_no=(1, 0, 0))
    yb0, yb1 = -z1, -z0
    kill = [f for f in bm.faces if x0 + 1e-3 < f.calc_center_median().x < x1 - 1e-3 and
            yb0 < f.calc_center_median().y < yb1]
    bmesh.ops.delete(bm, geom=kill, context="FACES")
    bnd = [e for e in bm.edges if e.is_boundary]
    if bnd:
        res = bmesh.ops.holes_fill(bm, edges=bnd, sides=0)
        for f in res.get("faces", []):
            for e in f.edges:
                for g in e.link_faces:
                    if g is not f:
                        f.material_index = g.material_index
                        break
    bmesh.ops.dissolve_degenerate(bm, dist=1e-4, edges=bm.edges[:])
    bm.to_mesh(me)
    bm.free()
    return len(kill)


def cut_top(ob, x0, x1, z0, z1):
    """fura o TOPO do chao (faces viradas para cima) na caixa Roblox x0..x1, z0..z1: o que o trecho poe por cima
    (leito da rua, medalhao) fica livre de face coplanar/rente a grama (5,8)"""
    me = ob.data
    bm = bmesh.new()
    bm.from_mesh(me)
    for co, no in (((x0, 0, 0), (1, 0, 0)), ((x1, 0, 0), (1, 0, 0)), ((0, -z0, 0), (0, 1, 0)), ((0, -z1, 0), (0, 1, 0))):
        geom = bm.verts[:] + bm.edges[:] + bm.faces[:]
        bmesh.ops.bisect_plane(bm, geom=geom, plane_co=co, plane_no=no)
    bm.normal_update()
    kill = []
    for f in bm.faces:
        c = f.calc_center_median()
        if f.normal.z > 0.9 and x0 + 1e-3 < c.x < x1 - 1e-3 and -z1 + 1e-3 < c.y < -z0 - 1e-3:
            kill.append(f)
    bmesh.ops.delete(bm, geom=kill, context="FACES_ONLY")
    bmesh.ops.dissolve_degenerate(bm, dist=1e-4, edges=bm.edges[:])
    bad = [f for f in bm.faces if f.calc_area() < 1e-6]
    if bad:
        bmesh.ops.delete(bm, geom=bad, context="FACES_ONLY")
    bm.to_mesh(me)
    bm.free()
    return len(kill)


def clear_v0():
    """tira do blockout o que o trecho substitui"""
    rep = {}
    old = ("VM_House_S1W", "VM_House_S1E", "VM_House_PNW", "VM_House_PNE", "VM_Town_Medallion", "VM_Town_Bridge")
    for n in old:
        o = bpy.data.objects.get(n)
        if o is not None:
            bpy.data.objects.remove(o, do_unlink=True)
            rep[n] = "removido"
    # colisao das casas antigas (caixas do vm_lib.house) com centro nas plantas antigas
    olds = [h for h in L.HOUSES if h["id"] in ("S1W", "S1E", "PNW", "PNE")]
    nc = 0
    for o in list(bpy.data.objects):
        if not o.name.startswith("COL_House_"):
            continue
        c = VL.R(o.matrix_world.translation)
        if any(math.hypot(c[0] - h["x"], c[2] - h["z"]) < 3.0 for h in olds):
            bpy.data.objects.remove(o, do_unlink=True)
            nc += 1
    rep["COL_House antigas"] = nc
    st = bpy.data.objects.get("VM_Town_Streets")
    if st:
        rep["ruas (ilhas)"] = drop_islands(st, lambda x, z: -12 < x < 12 and 0.0 < z < 17.0)
    pr = bpy.data.objects.get("VM_Town_Props")
    x0, x1, z0, z1 = REGION
    if pr:
        rep["props (faces)"] = drop_islands(pr, lambda x, z: x0 < x < x1 and z0 < z < z1)
    nv = 0
    for o in bpy.data.objects:
        if o.name.startswith("VM_Veg_Trees_"):
            nv += drop_islands(o, lambda x, z: x0 < x < x1 and -8.0 < z < z1)
    rep["arvores (faces)"] = nv
    tg = bpy.data.objects.get("VM_Ter_Ground")
    if tg:
        cx, cz = L.PLAZA_C
        rep["chao furado (rua, ponte, medalhao)"] = cut_top(tg, -STREET_X, STREET_X, -5.0, 16.6) + \
            cut_top(tg, cx - L.MEDAL_R, cx + L.MEDAL_R, cz - L.MEDAL_R, cz + L.MEDAL_R)
    cw = bpy.data.objects.get("VM_Ter_CanalWalls")
    if cw:
        rep["muros do canal (faces)"] = cut_box(cw, -CANAL_X, CANAL_X, -20.5, -3.5)
    print("TRECHO V0 recortado:", rep)
    return rep


# ------------------------------------------------------------------ rua
F0 = Frame(0.0, 0.0, 0.0, 0.0)          # referencial = Blender (x, y = -z Roblox)
DECK = [(-16.6, L.Y_PAVE), (-1.0, L.Y_PAVE), (10.0, L.BRIDGE_CROWN), (21.0, L.Y_NORTH)]   # (y Blender, topo)


def deck_z(yb):
    P = DECK
    if yb <= P[0][0]:
        return P[0][1]
    for (a, za), (b, zb) in zip(P, P[1:]):
        if a <= yb <= b:
            return za + (zb - za) * (yb - a) / (b - a)
    return P[-1][1]


def plaza_out(x, yb, pad=0.0):
    return math.hypot(x - L.PLAZA_C[0], -yb - L.PLAZA_C[1]) > L.PLAZA_R - 0.4 + pad


def street(mb, emb):
    """paralelepipedo (rua + tabuleiro da ponte), meio-fio, caminhos de lajes ate as portas"""
    K.cobbles(mb, F0, -STREET_X, STREET_X, DECK, seed="rua", keep=lambda x, y: plaza_out(x, y))
    for s in (-1, 1):
        K.curb(mb, F0, s * (STREET_X + 0.36), -15.1, -1.0,
               lambda qx, qy: L.Y_PAVE - 0.02, seed=("curb", s))
    # caminhos de lajes (cobble grande e baixo) das portas ate o meio-fio, e das casas da praca ate o anel
    for h in HOUSES:
        sp = house_spec(h)
        F = house_frame(h)
        dx = sp["door"].get("x", 0.0)
        y_front = sp["D"] / 2
        if h["id"].startswith("PN"):
            # da porta ate o anel da praca
            Fd = K.sub(F, dx, y_front + 1.0, 0.0)
            ln = 0.0
            while True:
                q = Fd.p(0.0, ln + 1.0, 0.0)
                if not plaza_out(q.x, q.y, pad=0.0) or ln > 16:
                    break
                ln += 1.0
            K.cobbles(mb, Fd, -1.7, 1.7, [(0.0, 0.1), (ln + 0.8, 0.1)],          # leito 0,13 acima da grama
                      seed=("path", h["id"]), row=(0.9, 1.3), sw=(1.0, 1.6), bed_m=K.PAVE_J, pB=0.45,
                      keep=lambda x, y, Fd=Fd: plaza_out(Fd.p(x, y, 0).x, Fd.p(x, y, 0).y, pad=0.25))
        else:
            # lajes da soleira ate o meio-fio (rua em x +-9,36)
            Fd = K.sub(F, dx, y_front + 1.05, 0.0)
            far = abs(h["x"] + h["fx"] * sp["D"] / 2) - (STREET_X + 0.75) - 1.05
            r = K.rng("lajes", h["id"])
            y = 0.0
            while y < far - 0.3:
                y2 = min(far, y + r.uniform(0.9, 1.3))
                w = r.uniform(1.4, 1.9)
                pts = [(-w + r.uniform(-0.1, 0.1), y + 0.06), (w + r.uniform(-0.1, 0.1), y + 0.06),
                       (w + r.uniform(-0.1, 0.1), y2 - 0.06), (-w + r.uniform(-0.1, 0.1), y2 - 0.06)]
                K.cobble(mb, Fd, pts, lambda qx, qy: L.Y_PAVE - F.o.z + 0.02, K.PAVE_E, bed=0.3, c1=0.08, c2=0.2)
                y = y2


def edges_dressing(emb, dmb):
    """borda de grama: touceiras, pedras soltas, flores (entre o meio-fio e as fachadas / muros)"""
    r = K.rng("borda")
    for s in (-1, 1):
        x0 = s * (STREET_X + 0.85)
        yb = -15.5
        k = 0
        while yb < -1.5:
            x = x0 + s * r.uniform(0.0, 2.0)
            # nao em cima dos caminhos das portas
            zz = -yb
            busy = False
            for h in HOUSES:
                if h["id"].startswith("PN") or (h["x"] > 0) != (s > 0):
                    continue
                sp = house_spec(h)
                cz = h["z"] + sp["door"].get("x", 0.0) * (1 if h["fx"] > 0 else -1)
                if abs(zz - cz) < 2.3:
                    busy = True
            if not busy:
                if r.random() < 0.55:
                    K.tuft(emb, F0, x, yb, L.Y_GRASS - 0.05, h=r.uniform(0.8, 1.4), k=k)
                if r.random() < 0.4:
                    K.pebble(emb, F0, x + s * r.uniform(0.2, 0.8), yb + r.uniform(-0.4, 0.4), L.Y_GRASS - 0.05,
                             r.uniform(0.5, 0.9), "Stone_VM_Grey", k)
                if r.random() < 0.18 and dmb is not None:
                    for j in range(3):
                        dmb.ico(0.2, F0.p(x + r.uniform(-0.4, 0.4), yb + r.uniform(-0.4, 0.4),
                                          L.Y_GRASS + 0.55 + r.uniform(0, 0.25)), K.FLOWERS[r.choice(["red", "yellow",
                                                                                                    "pink"])],
                                1, (1, 1, 0.8), jitter=0.1)
            yb += r.uniform(0.8, 1.6)
            k += 1
    # pe das fachadas que dao para a praca e pe dos muros do canal
    for (x, zr) in ((-24.5, 19.5), (-33.5, 19.6), (25.0, 18.8), (34.5, 18.9), (-21.0, 17.2), (21.5, 17.3),
                    (-26.0, -4.4), (-29.0, -4.3), (26.0, -4.4), (28.5, -4.3), (-13.4, 16.9), (13.6, 16.8)):
        for j in range(2):
            K.tuft(emb, F0, x + r.uniform(-0.6, 0.6), -zr + r.uniform(-0.3, 0.3), L.Y_GRASS - 0.05,
                   h=r.uniform(0.9, 1.5), k=("pe", x, j))
        K.pebble(emb, F0, x + r.uniform(-0.8, 0.8), -zr, L.Y_GRASS - 0.05, r.uniform(0.6, 1.0), "Stone_VM_Warm",
                 ("pe", x))


# ------------------------------------------------------------------ canal e ponte
def canal_walls(cm):
    """muros do canal (x -30..30, menos a ponte) em pedra arredondada sobre miolo escuro + mureta de pedra seca"""
    ys, yn = -L.CANAL_Z[1], -L.CANAL_Z[0]           # Blender y das faces: sul 6, norte 18
    for xa, xb in ((-CANAL_X, -11.0), (11.0, CANAL_X)):
        xm, ln = (xa + xb) / 2, xb - xa
        # sul: face em y 6 olhando +y (para a agua)
        Fs = K.sub(F0, xm, ys, 0.0, 0.0)
        K.bb(cm, F0, xa, xb, ys - 1.0, ys - K.CORE, L.Y_CANAL_BED, L.Y_PAVE - 0.02, K.MOR)
        K.stone_face(cm, Fs, -ln / 2, ln / 2, 2.0, L.Y_PAVE - 0.03, "Stone_VM_Grey", seed=("canalS", xa),
                     m2="Stone_VM_Warm", p2=0.3)
        # norte: face em y 18 olhando -y
        Fn = K.sub(F0, xm, yn, 0.0, math.pi)
        K.bb(cm, F0, xa, xb, yn + K.CORE, yn + 1.0, L.Y_CANAL_BED, L.Y_NORTH - 0.02, K.MOR)
        K.stone_face(cm, Fn, -ln / 2, ln / 2, 2.0, L.Y_NORTH - 0.03, "Stone_VM_Grey", seed=("canalN", xa),
                     m2="Stone_VM_Warm", p2=0.3)
    # muretas de pedra seca (sul: z -6..-5 Roblox; norte: z -19..-18), fora das casas do canal e da ponte
    south = [(-CANAL_X, -22.6), (22.5, CANAL_X)]
    north = [(-CANAL_X, -11.6), (11.6, CANAL_X)]
    for (xa, xb) in south:
        Fm = K.sub(F0, (xa + xb) / 2, ys - 0.5, L.Y_PAVE - 0.02)
        K.mureta(cm, Fm, xb - xa, h=1.2, w=1.0, m="Stone_VM_Grey", m2="Stone_VM_Trim", seed=("murS", xa))
    for (xa, xb) in north:
        Fm = K.sub(F0, (xa + xb) / 2, yn + 0.5, L.Y_NORTH - 0.02)
        K.mureta(cm, Fm, xb - xa, h=1.2, w=1.0, m="Stone_VM_Grey", m2="Stone_VM_Trim", seed=("murN", xa))


# arco da ponte (no plano da face; u = Blender y - 12, centrado no canal)
ARCH_C = 12.0          # Blender y do meio do canal
ARCH_HALF = 6.0        # vao (faces dos muros em y 6 e 18)
ARCH_SPRING = 3.0
ARCH_CROWN = 5.55
ARCH_T = 1.1


def _arch():
    rise = ARCH_CROWN - ARCH_SPRING
    R = (ARCH_HALF ** 2 + rise ** 2) / (2 * rise)
    zc = ARCH_CROWN - R
    return R, zc


def arch_z(u, outer=0.0):
    R, zc = _arch()
    rr = R + outer
    if abs(u) >= rr:
        return zc
    return zc + math.sqrt(rr * rr - u * u)


PILLAR_LIGHTS = []


def bridge(bm_, dmb):
    """PONTE DE PEDRA em arco (x -11..11, Blender y -1..21): abobada, aduelas salientes, timpanos de pedra, cornija
    acompanhando a rampa, guarda-corpo de pedra seca com capa e pilares nas 4 cabeceiras"""
    R, zc = _arch()
    th0 = math.atan2(ARCH_SPRING - zc, ARCH_HALF)
    n = 24
    # abobada (intradorso) - pedra escura, faixa de 0,6 de espessura entre as faces
    for i in range(n):
        a0 = th0 + (math.pi - 2 * th0) * i / n
        a1 = th0 + (math.pi - 2 * th0) * (i + 1) / n
        poly = [(ARCH_C + R * math.cos(a0), zc + R * math.sin(a0)), (ARCH_C + R * math.cos(a1), zc + R * math.sin(a1)),
                (ARCH_C + (R + 0.7) * math.cos(a1), zc + (R + 0.7) * math.sin(a1)),
                (ARCH_C + (R + 0.7) * math.cos(a0), zc + (R + 0.7) * math.sin(a0))]
        # poligono em (y, z) -> ext ao longo de x
        K.ext(bm_, F0, poly, "x", -10.15, 10.15, "Stone_VM_Dark")          # para antes das aduelas (x 10,2)
    for side in (-1, 1):
        # face do timpano em x = side*11, olhando +-x. Fs: +y local = +-x Blender; x local = Blender -y*side...
        Fs = K.sub(F0, side * 11.0, ARCH_C, 0.0, -side * math.pi / 2)
        # u local -> Blender y: p(u) = F0.y + rot... para side=+1 (a=-pi/2): x local -> (0,-1) => y = 12 - u
        def yb_of(u, side=side):
            return ARCH_C - u if side > 0 else ARCH_C + u
        # aduelas (Stone_VM_Trim) saindo 0,14 da face
        nv = 15
        for i in range(nv):
            a0 = th0 + (math.pi - 2 * th0) * i / nv + 0.008
            a1 = th0 + (math.pi - 2 * th0) * (i + 1) / nv - 0.008
            to = ARCH_T + (0.25 if i == nv // 2 else (0.12 if i % 2 else 0.0))
            pts = [(R * math.cos(a0), zc + R * math.sin(a0)), (R * math.cos(a1), zc + R * math.sin(a1)),
                   ((R + to) * math.cos(a1), zc + (R + to) * math.sin(a1)),
                   ((R + to) * math.cos(a0), zc + (R + to) * math.sin(a0))]
            K.ext(bm_, Fs, pts, "y", -0.8, 0.16, "Stone_VM_Trim")
        # miolo do timpano (escuro): faixas verticais entre o extradorso (ou o leito, sobre os muros) e o tabuleiro
        us = [-11.0, -ARCH_HALF] + [(-ARCH_HALF + 2 * ARCH_HALF * k / 12) for k in range(1, 12)] + [ARCH_HALF, 11.0]
        for ua, ub in zip(us, us[1:]):
            inside = abs((ua + ub) / 2) < ARCH_HALF
            za = arch_z(ua, ARCH_T - 0.1) if inside else L.Y_CANAL_BED
            zb = arch_z(ub, ARCH_T - 0.1) if inside else L.Y_CANAL_BED
            ta, tb = deck_z(yb_of(ua)) - 0.2, deck_z(yb_of(ub)) - 0.2
            K.ext(bm_, Fs, [(ua, za), (ub, zb), (ub, tb), (ua, ta)], "y", -1.6, -K.CORE, K.MOR)

        def zlim(u, side=side):
            if abs(u) < ARCH_HALF:
                lo = arch_z(u, ARCH_T + 0.05)
            elif abs(u) <= ARCH_HALF + 1.05:
                lo = 1.6                                   # face do muro do canal sob a ponte
            else:
                lo = (L.Y_GRASS if yb_of(u) < ARCH_C else L.Y_NORTH_GRASS) - 0.35     # abaixo disso e chao
            return (lo, deck_z(yb_of(u)) - 0.85)
        K.stone_face(bm_, Fs, -11.0, 11.0, 1.6, 7.5, "Stone_VM_Grey", seed=("timpano", side), zlim=zlim,
                     m2="Stone_VM_Warm", p2=0.35)
        # cornija na rampa (faixa de cantaria saliente sob o guarda-corpo)
        for (ya, za_), (yb2, zb_) in zip(DECK, DECK[1:]):
            if yb2 <= -1.0 or ya >= 21.0:
                continue
            ya, yb2 = max(ya, -1.0), min(yb2, 21.0)
            ua, ub = (ARCH_C - ya, ARCH_C - yb2) if side > 0 else (ya - ARCH_C, yb2 - ARCH_C)
            K.ext(bm_, Fs, [(ua, deck_z(ya) - 0.9), (ub, deck_z(yb2) - 0.9), (ub, deck_z(yb2) + 0.05),
                            (ua, deck_z(ya) + 0.05)], "y", -0.7, 0.24, "Stone_VM_Trim")
        # guarda-corpo de pedra seca acompanhando a rampa (x 9..11)
        Fp = K.sub(F0, side * 10.0, 10.0, 0.0, math.pi / 2)        # x local = Blender +y
        K.mureta(bm_, Fp, 22.0, h=1.45, w=1.9, m="Stone_VM_Grey", m2="Stone_VM_Trim", seed=("parapeito", side),
                 zfn=lambda lx: deck_z(10.0 + lx) - 0.02)
        # pilares das cabeceiras
        for yb in (-1.2, 21.2):
            z0 = deck_z(yb) - 0.4
            K.chimney(bm_, F0, side * 10.1, yb, z0, z0 + 3.0, "Stone_VM_Grey", seed=("pilar", side, yb), w=2.5,
                      crown="Stone_VM_Trim")
            if yb < 0:                                          # lanternas nos pilares da cabeceira sul
                p = K.lantern(bm_, K.sub(F0, side * 10.1, yb, 0.0), z0 + 3.3, hh=1.3, w=0.42)
                PILLAR_LIGHTS.append(("L_VM_Lamp_P%d" % (1 if side < 0 else 2), p))
    # tampa do tabuleiro sob o paralelepipedo (miolo escuro entre as faces, so p/ nao ver o vazio pelas frestas)
    for (ya, za_), (yb2, zb_) in zip(DECK, DECK[1:]):
        if yb2 <= -1.0 or ya >= 21.0:
            continue
        ya, yb2 = max(ya, -0.85), min(yb2, 20.85)
        K.ext(bm_, F0, [(ya, deck_z(ya) - 1.4), (yb2, deck_z(yb2) - 1.4), (yb2, deck_z(yb2) - 0.44),
                        (ya, deck_z(ya) - 0.44)], "x", -10.4, 10.4, K.MOR)


# ------------------------------------------------------------------ props
LAMPS = [("T1", -10.6, 17.8), ("T2", 10.6, 17.8),          # boca da rua na praca (fora dos balancos)
         ("T3", -27.0, 31.0), ("T4", 27.0, 31.0)]           # postes norte da praca (trocam os do blockout)


def props(pm):
    lights = []
    for nm, x, z in LAMPS:
        F = K.frame_r(x, z, L.Y_PAVE + 0.06, -1 if x > 0 else 1, 0)
        p = K.lamp_post(pm, F, stone="Stone_VM_Warm")
        lights.append(("L_VM_Lamp_" + nm, p))
        VL.colr("TProps", (x - 0.45, L.Y_PAVE, z - 0.45), (x + 0.45, L.Y_PAVE + 9.0, z + 0.45))
    # loja (S0E): barris e caixotes junto da vitrine; esquina da S1E
    for (x, z, kind) in ((11.2, 4.9, "b"), (11.5, 6.7, "b"), (10.95, 3.2, "c")):
        Fb = K.frame_r(x, z, L.Y_GRASS - 0.05, 1, 0)
        if kind == "b":
            K.barrel(pm, Fb, 0.0, 0.0, h=2.2, r=0.85)
        else:
            K.crate(pm, Fb, 0.0, 0.0, s=1.7, a=0.3)
    VL.colr("TProps", (10.0, L.Y_PAVE, 2.3), (12.4, L.Y_PAVE + 2.3, 7.6))
    # carroca no patio entre PNW e a praca, de lado para a rua (ref_01)
    Fc = K.frame_r(-20.6, 22.0, L.Y_GRASS - 0.05, -0.55, -1.0)
    K.cart(pm, K.sub(Fc, 0, 0, 0, 0))
    VL.colr_rot("TProps", -20.6, 22.0, L.Y_PAVE + 1.7, 7.0, 4.6, 3.4, -0.55, -1.0)
    for (x, z) in ((-25.6, 20.6), (-24.4, 21.4)):
        K.barrel(pm, K.frame_r(x, z, L.Y_GRASS - 0.05, 1, 0), 0.0, 0.0, h=2.2, r=0.85)
    K.crate(pm, K.frame_r(-34.0, 20.4, L.Y_GRASS - 0.05, 1, 0), 0.0, 0.0, s=1.8, a=0.15)
    K.crate(pm, K.frame_r(-34.1, 20.5, L.Y_GRASS - 0.05 + 1.8, 1, 0), 0.0, 0.0, s=1.3, a=0.5)
    VL.colr("TProps", (-26.6, L.Y_PAVE, 19.6), (-23.5, L.Y_PAVE + 2.3, 22.4))
    return lights


# ------------------------------------------------------------------ build
def build():
    PILLAR_LIGHTS.clear()
    rep = clear_v0()
    built = {}
    dmb = MB("VM_Town_TDress", "03_TOWN", detail="far", floor=-999)        # flores, toldo, placa, argolas
    for h in HOUSES:
        sp = house_spec(h)
        F = house_frame(h)
        mb = MB("VM_House_" + h["id"], "03_TOWN", detail="far", floor=-999)
        info = K.house(mb, F, sp, dmb=dmb)
        ob = mb.finish()
        ob["vm_trecho"] = 1
        K.house_col("House", F, sp, info)
        built[h["id"]] = (ob, info)
    sm = MB("VM_Town_TStreet", "03_TOWN", detail="far", floor=-999)
    street(sm, None)
    o = sm.finish()
    o["vm_trecho"] = 1
    em = MB("VM_Town_TEdges", "03_TOWN", detail="far", floor=-999)       # touceiras + pedras soltas
    edges_dressing(em, dmb)
    em.finish()["vm_trecho"] = 1
    cm = MB("VM_Ter_TCanal", "02_TERRAIN", detail="far", floor=-999)
    canal_walls(cm)
    cm.finish()["vm_trecho"] = 1
    bm_ = MB("VM_Town_TBridge", "03_TOWN", detail="far", floor=-999)
    bridge(bm_, dmb)
    bm_.finish()["vm_trecho"] = 1
    pm = MB("VM_Town_TProps", "03_TOWN", detail="far", floor=-999)
    lights = props(pm)
    pm.finish()["vm_trecho"] = 1
    for nm, p in lights + PILLAR_LIGHTS:
        fm_lib.light(nm, "POINT", p, 60.0, (1.0, 0.74, 0.42), 0.3)
    mm = MB("VM_Town_Medallion", "03_TOWN", detail="far", floor=-999)
    cx, cz = L.PLAZA_C
    top = L.Y_PAVE + 0.06 - 0.12                     # praca 6,06 -> medalhao 5,94 (relevo mais alto 6,05; chao furado)
    K.medallion(mm, Frame(cx, -cz, 0.0, 0.0), L.MEDAL_R, top)            # +y local = norte (forja): icone em pe
    mm.finish()["vm_trecho"] = 1
    d = dmb.finish()
    if d:
        d["vm_trecho"] = 1
    scale_dummies()
    r = report(print_=True)
    return r


def scale_dummies():
    for n, x, z, y, fx, fz in (("SCALE_T_PortaS1W", -10.9, 7.0, L.Y_PAVE, -1, 0.3),
                               ("SCALE_T_Ponte", -2.5, -10.0, L.BRIDGE_CROWN, 0, 1),
                               ("SCALE_T_Loja", 10.2, -2.6, L.Y_PAVE, -0.5, 1),
                               ("SCALE_T_Praca", -4.0, 30.0, L.Y_PAVE, 0.3, -1),
                               ("SCALE_T_Medal", 5.0, 48.0, L.Y_PAVE, 0, -1)):
        VL.dummy(n, x, z, y, fx, fz)


# ------------------------------------------------------------------ cameras (Roblox: pos, alvo, lente)
def cams():
    E = L.EYE
    c = {}
    c["CAM_VM_T_PracaPonte"] = ((2.5, L.Y_PAVE + E, 27.0), (-0.5, 11.0, -22.0), 17)
    c["CAM_VM_T_PontePraca"] = ((-1.5, L.BRIDGE_CROWN + E, -15.5), (0.5, 10.0, 40.0), 17)
    c["CAM_VM_T_Ref"] = ((5.5, L.Y_PAVE + 4.2, 23.0), (-3.0, 12.0, -24.0), 16)
    c["CAM_VM_T_MedalSpawn"] = ((0.0, L.Y_SPAWN + 6.0, 84.0), (0.0, 6.0, 50.0), 22)
    c["CAM_VM_T_C_Fachada"] = ((-3.0, L.Y_PAVE + E, 3.0), (-12.5, 13.5, 10.5), 18)
    c["CAM_VM_T_C_Porta"] = ((-5.5, L.Y_PAVE + 4.2, 12.5), (-12.0, 9.8, 9.0), 20)
    c["CAM_VM_T_C_Janela"] = ((-5.0, L.Y_PAVE + 9.5, 8.0), (-11.6, 17.0, 11.0), 22)
    c["CAM_VM_T_C_Telhado"] = ((5.5, L.Y_PAVE + E, 24.0), (14.0, 24.0, 8.0), 18)
    c["CAM_VM_T_C_Loja"] = ((4.0, L.Y_PAVE + E, -3.5), (12.5, 10.0, 2.0), 18)
    c["CAM_VM_T_C_Rua"] = ((4.5, L.Y_PAVE + 4.0, 13.0), (9.5, 6.2, 5.0), 22)
    c["CAM_VM_T_C_Ponte"] = ((-27.0, 8.6, -11.0), (0.0, 5.0, -12.0), 20)
    c["CAM_VM_T_C_Canal"] = ((-8.0, L.BRIDGE_CROWN + 5.0, -12.5), (-30.0, 5.5, -13.0), 20)
    c["CAM_VM_T_C_Praca"] = ((-6.0, L.Y_PAVE + E, 34.0), (-26.0, 12.0, 14.0), 18)
    c["CAM_VM_T_C_Poste"] = ((-5.0, L.Y_PAVE + 5.0, 20.0), (-11.0, 11.0, 14.2), 22)
    return c


def cameras():
    for n, (loc, tgt, lens) in cams().items():
        fm_lib.camera(n, VL.B(loc[0], loc[2], loc[1]), VL.B(tgt[0], tgt[2], tgt[1]), lens)
    # medalhao de cima (ortografica)
    cd = bpy.data.cameras.new("CAM_VM_T_MedalTop")
    cd.type = "ORTHO"
    cd.ortho_scale = 34.0
    ob = bpy.data.objects.new("CAM_VM_T_MedalTop", cd)
    ob.location = VL.B(L.PLAZA_C[0], L.PLAZA_C[1], 60.0)
    fm_lib.coll("00_REFERENCE").objects.link(ob)


# ------------------------------------------------------------------ relatorio (orcamento por casa)
def _tris(o):
    return sum(len(p.vertices) - 2 for p in o.data.polygons)


def report(print_=True, path=None):
    rows = {}
    for h in HOUSES:
        o = bpy.data.objects.get("VM_House_" + h["id"])
        if o is None:
            continue
        mats = sorted({o.data.materials[p.material_index].name for p in o.data.polygons})
        rows[h["id"]] = {"preset": h["preset"], "materiais": len(mats), "meshparts": len(mats), "tris": _tris(o),
                         "lista": mats}
    other = {}
    for o in bpy.data.objects:
        if o.type == "MESH" and o.get("vm_trecho") and not o.name.startswith("VM_House_"):
            mats = sorted({o.data.materials[p.material_index].name for p in o.data.polygons})
            other[o.name] = {"materiais": len(mats), "tris": _tris(o), "lista": mats}
    lod1 = {}
    for k in sorted(K.PRESETS):
        mb = MB("TMP_lod1_" + k, "00_REFERENCE", detail="far", floor=-999)
        sp = K.spec_of(k, seed="lod1_" + k, lod=1, party=("L", "B"))
        K.house(mb, Frame(0, 0, 0, 0), sp, dmb=None)
        lod1[k] = {"tris": sum(len(f.verts) - 2 for f in mb.bm.faces),
                   "materiais": len({f.material_index for f in mb.bm.faces})}
        mb.bm.free()
    tot_t = sum(v["tris"] for v in rows.values()) + sum(v["tris"] for v in other.values())
    tot_m = sum(v["meshparts"] for v in rows.values()) + sum(v["materiais"] for v in other.values())
    out = {"casas": rows, "outros": other, "total_tris": tot_t, "total_meshparts_est": tot_m,
           "lod1_geminada_LB": lod1}
    if print_:
        print("TRECHO orcamento (MeshParts = materiais por objeto, antes do fold do export):")
        for k, v in rows.items():
            print("   casa %-4s %-3s %d materiais / %d MeshParts / %6d tris" % (k, v["preset"], v["materiais"],
                                                                             v["meshparts"], v["tris"]))
        for k, v in sorted(other.items()):
            print("   %-22s %2d materiais / %6d tris" % (k, v["materiais"], v["tris"]))
        print("TRECHO total ~%d tris / ~%d MeshParts" % (tot_t, tot_m))
        print("TRECHO lod=1 (casa de fundo geminada L+B): " + ", ".join("%s %d tris" % (k, v["tris"])
                                                                         for k, v in lod1.items()))
    if path:
        json.dump(out, open(path, "w", encoding="utf-8"), indent=1)
    return out


# ------------------------------------------------------------------ export SO do trecho (validacao no Studio)
def export_trecho(out):
    """deixa so o trecho (+ chao, agua e colisoes da regiao) e chama o export_roblox compartilhado com raiz propria
    VM_TRECHO_V1 (nao toca no LOBBY_FORJA), sem contrato, sem rede de quedas"""
    x0, x1, z0, z1 = REGION
    keep_pref = T_PREFIX + ("VM_Town_TStreet", "VM_Town_TEdges", "VM_Town_TBridge", "VM_Town_TProps",
                            "VM_Town_TDress")
    for o in list(bpy.data.objects):
        if o.type == "MESH" and not o.name.startswith(("COL_", "QA_", "SCALE_", "PREVIEW_")):
            if not (o.get("vm_trecho") or o.name.startswith(keep_pref)):
                bpy.data.objects.remove(o, do_unlink=True)
        elif o.type == "MESH" and o.name.startswith(("QA_", "SCALE_", "PREVIEW_")):
            bpy.data.objects.remove(o, do_unlink=True)
        elif o.type == "EMPTY":
            bpy.data.objects.remove(o, do_unlink=True)
        elif o.type == "LIGHT" and not o.name.startswith(("L_VM_Lamp_T", "L_VM_Lamp_P")):
            bpy.data.objects.remove(o, do_unlink=True)
    # colisoes: so as que tocam a regiao (pisos do V0 sao faixas longas: recortadas pelo export? nao - ficam as
    # que cruzam a regiao, e o piso do trecho ganha caixas proprias)
    for o in list(bpy.data.objects):
        if o.name.startswith("COL_"):
            if o.name.startswith(("COL_Ground", "COL_Edge", "COL_Spawn", "COL_Court", "COL_Isle", "COL_Rank",
                                  "COL_Shop", "COL_Race")):
                bpy.data.objects.remove(o, do_unlink=True)
                continue
            c = VL.R(o.matrix_world.translation)
            if not (x0 < c[0] < x1 and z0 < c[2] < z1) and not o.name.startswith(("COL_Canal", "COL_Bridge")):
                bpy.data.objects.remove(o, do_unlink=True)
    # chao do trecho (grama sul/norte, leito e agua do canal) + piso de colisao
    g = MB("VM_Ter_TGround", "02_TERRAIN", detail="far", floor=-999)
    g.box2(VL.B(x0, -5.0, L.Y_GRASS - 1.0), VL.B(x1, z1 + 8.0, L.Y_GRASS), "Grass_VM", 0.0)
    g.box2(VL.B(x0, -40.0, L.Y_NORTH_GRASS - 1.0), VL.B(x1, -19.0, L.Y_NORTH_GRASS), "Grass_VM", 0.0)
    g.box2(VL.B(x0, -19.0, L.Y_CANAL_BED - 0.6), VL.B(x1, -5.0, L.Y_CANAL_BED), "Stone_VM_Dark", 0.0)
    g.box2(VL.B(-9.0, -40.0, L.Y_NORTH - 0.4), VL.B(9.0, -21.0, L.Y_NORTH - 0.001), "Stone_Paving_VM", 0.0)
    g.box2(VL.B(-28.0, 14.0, L.Y_PAVE - 0.34), VL.B(28.0, z1 + 8.0, L.Y_PAVE + 0.06), "Stone_Paving_VM", 0.0)
    g.finish()["vm_trecho"] = 1
    w = MB("VM_Water_TCanal", "08_WATER", detail="far", floor=-999)
    w.box2(VL.B(x0, -18.0, L.Y_CANAL_BED), VL.B(x1, -6.0, L.Y_WATER), "Water_VM", 0.0)
    w.finish()["vm_trecho"] = 1
    VL.colr("TGround", (x0, L.Y_PAVE - 4.0, -5.0), (x1, L.Y_PAVE, z1 + 8.0))
    VL.colr("TGround", (x0, L.Y_NORTH - 4.0, -40.0), (x1, L.Y_NORTH, -19.0))
    bpy.context.view_layer.update()            # matrix_world das COL criadas aqui (senao saem na origem)
    os.environ["FM_EXPORT_DIR"] = out
    os.environ.setdefault("FM_BUDGET", "warn")
    import export_roblox as ER
    import fm_portals  # noqa: F401 (materiais registrados)
    ER.OUT = out
    ER.BUDGET_MODE = "warn"
    ER.FBX_PREFIX = "VM_TRECHO"
    ER.ROOT_NAME = "VM_TRECHO_V1"
    ER.DATA_FILE = "vm_trecho_data.json"
    ER.LUA_FILE = "montar_vm_trecho.lua"
    ER.SERVER_SCRIPT = "VM_TRECHO_Servidor"
    ER.MARKER_COLL = "15_GAMEPLAY_MARKERS"
    ER.SPAWN_FALLBACK = False
    ER.TITLE = "trecho V1 da Vila Medieval (praca -> ponte)"
    ER.GROUPS = list(VL.EXPORT_GROUPS)
    ER.SKIP_PREFIX = ("COL_", "SCALE_", "BLK_", "QA_", "PREVIEW_", "CAM_", "NPC_", "TMP_")
    ER.SKIP_NAMES = set()
    ER.OWNERS = list(VL.OWNER_PREFIX)
    ER.BUDGET_OWNER = dict(L.BUDGET_OWNER)
    ER.BUDGET = dict(L.BUDGET)
    ER.FAR_GROUND = None
    ER.NET = False
    ER.EXTRA_LUA = ""
    ER.SAFE_CANDIDATES = lambda: []
    ER.SKYLINE_WHOLE = ("VM_Bg_",)
    ER.SKYLINE_MODEL = ("VM_Bg_",)
    ER.BACKGROUND = ("VM_Bg_",)
    ER.CARVED = ("__nenhum__",)
    ER.SHELL_OBJ = ("__nenhum__",)
    ER.CAM_COL_AREAS = {"House": 5.0}
    ER.NIGHT_ONLY = ER.NIGHT_ONLY + ("L_VM_Lamp",)
    ER.FOLD_PROTECT = ER.FOLD_PROTECT + ("Forge_Glow_VM", "Metal_VM_Bronze", "Cloth_VM", "Window_VM", "Flower_VM",
                                         "Roof_VM", "Stone_VM_Mortar")

    def atomic(name):
        import re
        m = re.match(r"^(VM_House_[A-Za-z0-9]+)", name)
        return m.group(1) if m else ""
    ER.atomic_model = atomic
    ER.main()


# ------------------------------------------------------------------ z-fight (faces paralelas proximas de materiais distintos)
def _tri_area_overlap(P, Q):
    """area da intersecao de 2 triangulos 2D (Sutherland-Hodgman, convexos)"""
    def clip(poly, a, b):
        out = []
        n = len(poly)
        for i in range(n):
            p, q = poly[i], poly[(i + 1) % n]
            cp = (b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0])
            cq = (b[0] - a[0]) * (q[1] - a[1]) - (b[1] - a[1]) * (q[0] - a[0])
            if cp >= 0:
                out.append(p)
            if (cp >= 0) != (cq >= 0):
                t = cp / (cp - cq)
                out.append((p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t))
        return out

    def ccw(t):
        a = (t[1][0] - t[0][0]) * (t[2][1] - t[0][1]) - (t[1][1] - t[0][1]) * (t[2][0] - t[0][0])
        return t if a > 0 else [t[0], t[2], t[1]]
    poly = ccw(list(P))
    Q = ccw(list(Q))
    for i in range(3):
        if not poly:
            return 0.0, None
        poly = clip(poly, Q[i], Q[(i + 1) % 3])
    if len(poly) < 3:
        return 0.0, None
    ar = 0.0
    for i in range(len(poly)):
        x0, y0 = poly[i]
        x1, y1 = poly[(i + 1) % len(poly)]
        ar += x0 * y1 - x1 * y0
    cx = sum(p[0] for p in poly) / len(poly)
    cy = sum(p[1] for p in poly) / len(poly)
    return abs(ar) / 2, (cx, cy)


def zfight(path=None, dist=0.12, min_area=0.02):
    """pares de triangulos com a MESMA orientacao (normais a < 2,5 graus), planos a < dist e materiais diferentes,
    sobrepostos > min_area (studs2), dentro de cada objeto do trecho e entre objetos do trecho e o chao/praca do V0.
    Nao ve se a face esta exposta: os pares sao CANDIDATOS (o relatorio mostra os maiores para conferir)."""
    import collections
    objs = [o for o in bpy.data.objects if o.type == "MESH" and o.get("vm_trecho")]
    extra = [bpy.data.objects.get(n) for n in ("VM_Ter_Ground", "VM_Town_Plaza", "VM_Town_Streets")]
    from mathutils.bvhtree import BVHTree
    tris = []
    allv, allp = [], []
    for o in objs + [e for e in extra if e]:
        me = o.data
        me.calc_loop_triangles()
        mw = o.matrix_world
        for lt in me.loop_triangles:
            vs = [mw @ me.vertices[i].co for i in lt.vertices]
            n = (vs[1] - vs[0]).cross(vs[2] - vs[0])
            if n.length < 1e-6:
                continue
            ar = n.length / 2
            n.normalize()
            m = me.materials[lt.material_index].name if me.materials else "?"
            tris.append((o.name, m, n, n.dot(vs[0]), vs, ar))
            k0 = len(allv)
            allv.extend(vs)
            allp.append((k0, k0 + 1, k0 + 2))
    bvh = BVHTree.FromPolygons(allv, allp, epsilon=0.0)

    AXES = [Vector(v) for v in ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1))]

    def exposed(p, n):
        """(1) raio de 0,6 livre a frente da face, saindo ALEM do parceiro (d < 0,12): so a face da frente cobre;
        (2) o ponto 0,3 a frente esta AO AR LIVRE: em pelo menos 1 dos 6 eixos o 1o obstaculo fica a > 16 studs
        (miolos, sotaos e frestas entre casas sao menores que isso; rua, praca e canal nao)"""
        loc, nrm, idx, d = bvh.ray_cast(p + n * (dist + 0.01), n, 0.6)
        if loc is not None:
            return False
        q = p + n * 0.3
        for ax in AXES:
            h = bvh.ray_cast(q, ax, 16.0)
            if h[0] is None:
                return True
        return False

    buckets = collections.defaultdict(list)
    for t in tris:
        n = t[2]
        buckets[(round(n.x * 20), round(n.y * 20), round(n.z * 20))].append(t)
    pairs = collections.defaultdict(float)
    where = {}
    for key, lst in buckets.items():
        lst.sort(key=lambda t: t[3])
        n0 = lst[0][2]
        u = n0.orthogonal().normalized()
        v = n0.cross(u)
        for i, a in enumerate(lst):
            j = i + 1
            while j < len(lst) and lst[j][3] - a[3] < dist:
                b = lst[j]
                j += 1
                if a[1] == b[1] or a[2].dot(b[2]) < 0.999:
                    continue
                if a[0] != b[0] and not (a[0] in [o.name for o in objs] or b[0] in [o.name for o in objs]):
                    continue
                P = [(p.dot(u), p.dot(v)) for p in a[4]]
                Q = [(p.dot(u), p.dot(v)) for p in b[4]]
                if max(x for x, _ in P) < min(x for x, _ in Q) or max(x for x, _ in Q) < min(x for x, _ in P) or \
                        max(y for _, y in P) < min(y for _, y in Q) or max(y for _, y in Q) < min(y for _, y in P):
                    continue
                ov, c2 = _tri_area_overlap(P, Q)
                if ov > 1e-4:
                    pa = u * c2[0] + v * c2[1]
                    if not (exposed(pa + a[2] * (a[3] - a[2].dot(pa)), a[2]) and
                            exposed(pa + b[2] * (b[3] - b[2].dot(pa)), b[2])):
                        continue
                    k = tuple(sorted(((a[0], a[1]), (b[0], b[1])))) + (round(abs(b[3] - a[3]), 3),)
                    pairs[k] += ov
                    if k not in where or ov > where[k][0]:
                        q = VL.R(pa + a[2] * (a[3] - a[2].dot(pa)))
                        where[k] = (ov, [round(c, 2) for c in q], [round(c, 2) for c in VL.R(a[2])])
    big = sorted(((ar, k) for k, ar in pairs.items() if ar >= min_area), reverse=True)
    print("ZFIGHT %d pares EXPOSTOS (>= %.2f studs2, d < %.2f, raio 0,6 livre a frente das 2 faces)" % (
        len(big), min_area, dist))
    for ar, k in big[:40]:
        w = where.get(k, (0, None, None))
        print("   %7.2f studs2  d=%.3f  %s/%s  x  %s/%s  em %s n %s" % (ar, k[2], k[0][0], k[0][1], k[1][0], k[1][1],
                                                                       w[1], w[2]))
    if path:
        json.dump([{"area": round(ar, 3), "d": k[2], "a": list(k[0]), "b": list(k[1]), "em_roblox": where[k][1],
                    "normal_roblox": where[k][2]} for ar, k in big],
                  open(path, "w", encoding="utf-8"), indent=1)
    return big


if __name__ == "__main__":
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    if argv and argv[0] == "export":
        out = os.path.abspath(argv[1]) if len(argv) > 1 else os.path.join(HERE, "export_trecho")
        export_trecho(out)
    elif argv and argv[0] == "report":
        report(True, argv[1] if len(argv) > 1 else None)
    elif argv and argv[0] == "zfight":
        zfight(argv[1] if len(argv) > 1 else None)
