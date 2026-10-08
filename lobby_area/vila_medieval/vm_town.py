# vm_town.py - A VILA do lobby VILA MEDIEVAL (onda V2b): praca, casas, loja, ranking, patio dos portais, rua de saida,
# portao + ponte da Ilha 1 e canal. Multiplica o kit V1 (vm_kit), ja validado no Roblox, em volta do trecho V1
# (vm_trecho continua dono do trecho praca -> ponte: este modulo so integra ao redor e trata as pendencias do V1).
#
# Coordenadas ROBLOX (X leste, Z sul, Y cima); Blender = (X, -Z, Y). Tudo deterministico (K.rng / K.h01 = crc32 +
# fmix32 do murmur3; ordem fixa). Volumes do blockout V0 que este modulo substitui sao apagados no clear_v0().
#
# CONTEUDO
#   praca        paralelepipedo em ANEIS (geometria: pedras arredondadas por anel, 2 tons alternando por anel), aneis de
#                cantaria em r 9 / 20 / 35 (o anel interno do V0 a 0,04 do piso - z-fight - saiu), leito de junta 0,11
#                abaixo do topo e 0,15 acima da grama; borda: canteiros em arco (meio-fio de pedra, terra, arbustos,
#                flores) com folga nas portas, bancos e postes; medalhao do V1 no centro (vm_trecho)
#   spawn        terraco de pedra arredondada (kit) com escadaria larga (x +-13) de cantaria, pedestais com lanterna,
#                BALAUSTRADA (pilares + balaustres torneados + corrimao), lajes em volta do anel de bronze, quiosque
#                do correio (telhadinho sobre o MailBox)
#   casas        frentes CONTINUAS do kit (paredes-meias automaticas entre vizinhas), lod=1 nas frentes e lod=2 nos
#                fundos/canal, JUNTADAS POR QUADRA (1 objeto VM_House_Q<quadra>, <= 8 materiais por quadra);
#                enfeites (flores, toldo, placas) num objeto por regiao com 1 cor de flor
#   ruas         rua oeste, rua da loja, rua curva de saida e rua norte em paralelepipedo (faixa curva em geometria),
#                meio-fio, adro de lajes do ranking
#   loja         LOJA DE MOCHILAS (leste): terreo de pedra, andar enxaimel, oitao para a rua, porta larga 6 x 9 com
#                folhas abertas, VITRINES abertas com mochilas, toldo listrado, placa grande com mochila em relevo;
#                INTERIOR: piso de tabuas, reboco, vigas, balcao (x 74..76) com o vendedor atras (78, 43), prateleiras
#                com mochilas, lustre de ferro (2 luzes de dia)
#   ranking      palco de pedra (6,4) com borda, mastros com estandartes azuis, SALAO DA GUILDA enxaimel atras (fora
#                da envoltoria do GlobalTop100), adro de lajes ate a rua
#   patio        disco de lajes em aneis (2 tons) + rosa dos ventos, degrau e terraco (7,2) dos 6 portais APROVADOS (nao
#                mexidos), mureta no lado leste, ARCO de pedra discreto na entrada, postes e bancos entre os eixos dos
#                portais, arvores emoldurando
#   saida        portao de vila (2 torres de pedra com telhado conico de telha, verga de madeira com telhadinho, folhas
#                abertas) e ponte de pedra ate a praca da Ilha 1 (encaixe em (0, 6, 222) mantido)
#   canal        muros de pedra arredondada alem de x +-30 (ate as cachoeiras, boca da levada x 32..40 livre), capa de
#                pedra e 2 pontezinhas de pedra em arco (andaveis)
#
# uso: o build_vm.py chama vm_town.build() depois do vm_trecho.build() e vm_town.cameras() no fim.
import sys, os, math, bisect, json
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
import fm_parts as FP
import vm_kit as K

F0 = Frame(0.0, 0.0, 0.0, 0.0)
PCX, PCZ = L.PLAZA_C
CCX, CCZ = L.COURT_C
Y = L.Y_PAVE
PLAZA_TOP = Y + 0.06          # topo das pedras da praca (= blockout); leito 5,95
ROAD_TOP = Y                  # topo das pedras das ruas (= trecho); leito 5,92
BED_P, BED_R = 5.95, 5.92     # leitos: >= 0,12 acima da grama (5,8) -> nada rente
FLOOR_ALL = 60.0              # MB de piso: toda primitiva fechada perde a face de baixo (nunca vista; -10% de tris)
LAMPS = []                    # (nome, ponto) das luzes NightOnly dos postes novos
DAY_LIGHTS = []
STATS = {}


# ================================================================== geometria 2D (Roblox x, z)
def _chaikin(P, closed):
    out = []
    n = len(P)
    rng_ = range(n) if closed else range(n - 1)
    if not closed:
        out.append(P[0])
    for i in rng_:
        a, b = P[i], P[(i + 1) % n]
        out.append((a[0] * 0.75 + b[0] * 0.25, a[1] * 0.75 + b[1] * 0.25))
        out.append((a[0] * 0.25 + b[0] * 0.75, a[1] * 0.25 + b[1] * 0.75))
    if not closed:
        out.append(P[-1])
    return out


class Path:
    """polilinha (Roblox x, z) parametrizada pelo comprimento: at(s) -> (ponto, tangente); pt(s, t) = ponto deslocado
    t para a NORMAL n = (-tz, tx) (para quem anda em +x, n = +z)"""

    def __init__(self, pts, closed=False, smooth=0):
        P = [tuple(map(float, p)) for p in pts]
        for _ in range(smooth):
            P = _chaikin(P, closed)
        if closed:
            P = P + [P[0]]
        self.P = P
        self.S = [0.0]
        for a, b in zip(P, P[1:]):
            self.S.append(self.S[-1] + math.hypot(b[0] - a[0], b[1] - a[1]))
        self.L = self.S[-1]

    def at(self, s):
        s = max(0.0, min(self.L, s))
        i = min(max(0, bisect.bisect_right(self.S, s) - 1), len(self.P) - 2)
        a, b = self.P[i], self.P[i + 1]
        ln = (self.S[i + 1] - self.S[i]) or 1e-9
        u = (s - self.S[i]) / ln
        return (a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u), ((b[0] - a[0]) / ln, (b[1] - a[1]) / ln)

    def pt(self, s, t=0.0):
        (x, z), (tx, tz) = self.at(s)
        return (x - tz * t, z + tx * t)

    def project(self, q):
        best = (1e18, 0.0)
        for i, (a, b) in enumerate(zip(self.P, self.P[1:])):
            dx, dz = b[0] - a[0], b[1] - a[1]
            ln2 = dx * dx + dz * dz or 1e-9
            u = max(0.0, min(1.0, ((q[0] - a[0]) * dx + (q[1] - a[1]) * dz) / ln2))
            d = math.hypot(q[0] - a[0] - dx * u, q[1] - a[1] - dz * u)
            if d < best[0]:
                best = (d, self.S[i] + u * math.sqrt(ln2))
        return best[1]


def circle_path(cx, cz, r, n=180):
    return Path([(cx + r * math.cos(2 * math.pi * i / n), cz + r * math.sin(2 * math.pi * i / n)) for i in range(n)],
                closed=True)


def arc_path(cx, cz, r, a0, a1, step=1.5):
    n = max(2, int(abs(a1 - a0) * math.pi / 180 * r / step))
    return Path([(cx + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)),
                  cz + r * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)])


def rp(x, z):
    return math.hypot(x - PCX, z - PCZ)


def rc(x, z):
    return math.hypot(x - CCX, z - CCZ)


def ang_p(x, z):
    return math.degrees(math.atan2(z - PCZ, x - PCX))


def in_poly(x, z, poly):
    return VL.in_poly(x, z, poly)


# ================================================================== pedras em faixa (praca, ruas, ponte, meio-fio)
def band(mb, path, t0, t1, row, sw, ztop, seed, mats=(K.PAVE_A, K.PAVE_B), pB=0.35, keep=None, gap=0.12, s0=0.0,
         s1=None, c=(0.13, 0.36), jit=0.06, bed=0.2):
    """PEDRAS ARREDONDADAS (K.cobble) numa faixa curva: fiadas transversais ao longo de s (comprimento 'row'),
    cada fiada partida em t (largura 'sw'; sw=None = uma pedra so na largura), fiadas desencontradas. keep(x, z)
    Roblox recorta pelo centro da pedra. ztop = topo (numero ou fn(x_blender, y_blender))."""
    r = K.rng("band", seed)
    s1 = path.L if s1 is None else s1
    zf = ztop if callable(ztop) else (lambda x, y, v=ztop: v)
    s, k, n = s0, 0, 0
    while s < s1 - 0.3:
        h = r.uniform(*row)
        s2 = min(s1, s + h)
        if s1 - s2 < row[0] * 0.5:
            s2 = s1
        ts = [t0]
        if sw is not None:
            if k % 2:
                x = t0 + r.uniform(0.3, 0.6) * sw[0]
                if t1 - x > 0.4:
                    ts.append(x)
            while ts[-1] < t1 - 0.3:
                nx = ts[-1] + r.uniform(*sw)
                if t1 - nx < sw[0] * 0.5:
                    nx = t1
                ts.append(min(nx, t1))
        else:
            ts.append(t1)
        g = gap / 2
        for ta, tb in zip(ts, ts[1:]):
            q = [path.pt(s + g, ta + g), path.pt(s2 - g, ta + g), path.pt(s2 - g, tb - g), path.pt(s + g, tb - g)]
            q = [(x + r.uniform(-jit, jit), z + r.uniform(-jit, jit)) for x, z in q]
            cx = sum(p[0] for p in q) / 4
            cz = sum(p[1] for p in q) / 4
            dz = r.uniform(-0.03, 0.04)
            m = mats[1] if r.random() < pB else mats[0]
            if keep is not None and not keep(cx, cz):
                continue
            K.cobble(mb, F0, [(x, -z) for x, z in q], lambda qx, qy, dz=dz: zf(qx, qy) + dz, m, bed=bed,
                     c1=c[0], c2=c[1])
            n += 1
        s = s2
        k += 1
    return n


def band_bed(mb, path, t0, t1, ytop, m=K.PAVE_J, step=2.0, keep=None, thick=0.3, s0=0.0, s1=None):
    """leito (junta) sob uma faixa: prismas quadrilaterais a cada 'step' (keep: algum canto dentro)"""
    s1 = path.L if s1 is None else s1
    n = max(1, int(math.ceil((s1 - s0) / step)))
    for i in range(n):
        sa, sb = s0 + (s1 - s0) * i / n, s0 + (s1 - s0) * (i + 1) / n
        q = [path.pt(sa, t0), path.pt(sb, t0), path.pt(sb, t1), path.pt(sa, t1)]
        if keep is not None and not any(keep(x, z) for x, z in q):
            continue
        mb.prism(VL.bpoly(q), ytop - thick, ytop, m)


def stone_row(mb, path, t, w, y0, h, seed, m="Stone_VM_Trim", ln=(1.6, 2.4), s0=0.0, s1=None, keep=None, c=0.16):
    """fiada de pedras atravessadas (as 2 faces chanfradas) ao longo do caminho: meio-fio alto, capa de muro, degrau
    curvo, borda de canteiro. Cada pedra = K.through_stone (28 tris) num Frame local alinhado a tangente."""
    r = K.rng("row", seed)
    s1 = path.L if s1 is None else s1
    s = s0
    while s < s1 - 0.2:
        s2 = min(s1, s + r.uniform(*ln))
        if s1 - s2 < ln[0] * 0.5:
            s2 = s1
        sm = (s + s2) / 2
        (x, z), (tx, tz) = path.at(sm)
        p = path.pt(sm, t)
        if keep is None or keep(*p):
            Fs = K.frame_r(p[0], p[1], y0, -tz, tx)            # +y local = normal (-tz, tx); +x local = tangente
            Fs = Frame(Fs.o.x, Fs.o.y, Fs.o.z, Fs.a)
            L_ = s2 - s - 0.08
            # +x local = R = (-fz, fx) com f = n = (-tz, tx) -> R = (-tx, -tz): tangente invertida (indiferente)
            K.through_stone(mb, Fs, -L_ / 2, L_ / 2, -w / 2, w / 2, -0.2, h + r.uniform(-0.03, 0.04), m, c=c,
                            jit=[(r.uniform(-0.05, 0.05), r.uniform(-0.04, 0.04)) for _ in range(4)])
        s = s2


def merge_mats(ob, mapping):
    """remapeia materiais de um objeto (ex.: cores de flor -> 1 so): menos MeshParts"""
    if ob is None:
        return
    me = ob.data
    names = [m.name for m in me.materials]
    for a, b in mapping.items():
        if a not in names:
            continue
        if b not in names:
            me.materials.append(fm_lib.mat(b))
            names.append(b)
    idx = {n: i for i, n in enumerate(names)}
    mi = []
    for p in me.polygons:
        n = names[p.material_index]
        mi.append(idx[mapping[n]] if n in mapping else p.material_index)
    used = sorted(set(mi))
    remap = {o: i for i, o in enumerate(used)}
    keep = [me.materials[i] for i in used]
    me.materials.clear()                       # (zera os indices das faces: regrava depois)
    for m in keep:
        me.materials.append(m)
    me.polygons.foreach_set("material_index", [remap[i] for i in mi])
    me.update()


# ================================================================== recorte do blockout V0
V0_DEL = ("VM_Town_Plaza", "VM_Town_Spawn", "VM_Town_SpawnStairs", "VM_Town_SpawnParapet", "VM_Shop_Building",
          "VM_Rank_Stage", "VM_Rank_Hall", "VM_Court_Floor", "VM_Exit_Gate", "VM_Exit_Bridge")


def clear_v0():
    import vm_trecho as TR
    rep = {}
    for o in list(bpy.data.objects):
        if o.name in V0_DEL or (o.name.startswith("VM_House_") and not o.get("vm_trecho")):
            bpy.data.objects.remove(o, do_unlink=True)
            rep["obj"] = rep.get("obj", 0) + 1
    olds = [h for h in L.HOUSES if h["id"] not in ("S1W", "S1E", "PNW", "PNE")]
    for o in list(bpy.data.objects):
        n = o.name
        kill = False
        if n.startswith("COL_House_"):
            c = VL.R(o.matrix_world.translation)
            kill = any(math.hypot(c[0] - h["x"], c[2] - h["z"]) < 3.0 for h in olds)
        elif n.startswith(("COL_Shop_", "COL_RankHall_", "COL_CourtPillar_", "COL_Gate_", "COL_SpawnPar_")):
            kill = True
        elif n.startswith("COL_Spawn_"):
            kill = VL.R(o.matrix_world.translation)[2] < 88.0          # rampa e meia pisada da escadaria antiga
        elif n.startswith("COL_Canal_"):
            kill = True                                                 # refeitos com as pontezinhas (canal_cols)
        if kill:
            bpy.data.objects.remove(o, do_unlink=True)
            rep["col"] = rep.get("col", 0) + 1
    st = bpy.data.objects.get("VM_Town_Streets")
    if st:       # fica SO o largo da forja (dono V2a)
        rep["ruas"] = TR.drop_islands(st, lambda x, z: not (-27 < x < 25 and -51 < z < -36.5))
        if not st.data.polygons:                 # (a forja V2a ja refez o largo: sobra objeto vazio)
            bpy.data.objects.remove(st, do_unlink=True)
    pr = bpy.data.objects.get("VM_Town_Props")
    if pr:
        rep["props"] = TR.drop_islands(pr, lambda x, z: z > -36.0)
    cw = bpy.data.objects.get("VM_Ter_CanalWalls")
    if cw:       # muros do canal fora do trecho (a levada x 32..40 ao norte fica)
        n = TR.cut_box(cw, -140.0, -29.9, -20.5, -3.5) + TR.cut_box(cw, 29.9, 32.0, -20.5, -3.5)
        n += TR.cut_box(cw, 40.0, 180.0, -20.5, -3.5) + TR.cut_box(cw, 31.9, 40.1, -6.6, -3.5)
        rep["canal"] = n
    print("TOWN V0 recortado:", rep)


def drop_trees(boxes, circles):
    """arvores do blockout que caem nas construcoes novas saem (o V3 refaz a vegetacao)"""
    import vm_trecho as TR
    n = 0

    def bad(x, z):
        for (x0, x1, z0, z1) in boxes:
            if x0 < x < x1 and z0 < z < z1:
                return True
        for (cx, cz, r) in circles:
            if math.hypot(x - cx, z - cz) < r:
                return True
        return False
    for o in bpy.data.objects:
        if o.name.startswith("VM_Veg_Trees_"):
            n += TR.drop_islands(o, bad)
    return n


# ================================================================== pecas pequenas
def bench(mb, F, L_=4.4, seed=0):
    """BANCO de tabuas sobre 2 pes de pedra, com encosto (F: +y = para onde se olha sentado; assento ao longo de x)"""
    r = K.rng("bench", seed)
    for s in (-1, 1):
        K.through_stone(mb, F, s * (L_ / 2 - 0.45) - 0.32, s * (L_ / 2 - 0.45) + 0.32, -0.75, 0.6, -0.2, 1.25,
                        "Stone_VM_Trim", c=0.12)
        K.bb(mb, F, s * (L_ / 2 - 0.45) - 0.16, s * (L_ / 2 - 0.45) + 0.16, -0.95, -0.7, 1.2, 3.3, K.T)
    for k, y in enumerate((-0.45, 0.05, 0.55)):
        K.bb(mb, F, -L_ / 2, L_ / 2, y - 0.22, y + 0.22, 1.25, 1.52 + r.uniform(-0.02, 0.02), K.PLK)
    for z in (2.15, 2.85):
        K.bb(mb, F, -L_ / 2 + 0.1, L_ / 2 - 0.1, -0.98, -0.74, z - 0.24, z + 0.24, K.PLK)


def lamp_lite(mb, F, h=9.6, stone="Stone_VM_Warm"):
    """POSTE DE FERRO (mesma silhueta do K.lamp_post do V1, ~150 tris em vez de ~350: sem as grades da lanterna)"""
    K.through_stone(mb, F, -0.72, 0.72, -0.72, 0.72, -0.25, 0.52, stone, c=0.15)
    mb.cyl(0.44, 1.0, F.p(0, 0, 1.0), F.r(), K.IRON, 6, r2=0.28, bevel=0.0)
    mb.cyl(0.19, h - 2.5, F.p(0, 0, 1.45 + (h - 2.5) / 2), F.r(), K.IRON, 6, bevel=0.0)
    zb = h - 1.0
    mb.cyl(0.88, 0.22, F.p(0, 0, zb), F.r(0, 0, math.pi / 4), K.IRON, 4, bevel=0.0)
    K.bb(mb, F, -0.5, 0.5, -0.5, 0.5, zb + 0.1, zb + 1.7, K.GLASS_LAMP)
    for sx in (-1, 1):
        for sy in (-1, 1):
            K.bb(mb, F, sx * 0.62 - 0.09, sx * 0.62 + 0.09, sy * 0.62 - 0.09, sy * 0.62 + 0.09, zb + 0.1, zb + 1.8,
                 K.IRON)
    mb.cyl(1.08, 0.95, F.p(0, 0, zb + 2.25), F.r(0, 0, math.pi / 4), K.IRON, 4, r2=0.14, bevel=0.0)
    return F.p(0, 0, zb + 0.9)


def lamp(mb, name, x, z, y, h=9.6, face=(0.0, 1.0), stone="Stone_VM_Warm"):
    F = K.frame_r(x, z, y, face[0], face[1])
    p = lamp_lite(mb, F, h=h, stone=stone)
    LAMPS.append(("L_VM_Lamp_" + name, p))
    VL.colr("TownProps", (x - 0.5, y, z - 0.5), (x + 0.5, y + h, z + 0.5))
    return p


def backpack(mb, F, x, y, z, s=1.0, body="Cloth_VM_Red", trim=K.PLK, a=0.0):
    """MOCHILA (produto da loja): corpo, aba, bolso, alcas e alca de mao (F: +y = frente da mochila)"""
    Fb = K.sub(F, x, y, z, a)
    w, d, h = 1.0 * s, 0.6 * s, 1.25 * s
    K.bb(mb, Fb, -w / 2, w / 2, -d / 2, d / 2, 0.0, h, body)
    K.bb(mb, Fb, -w / 2 - 0.04 * s, w / 2 + 0.04 * s, -d / 2 - 0.04 * s, d / 2 + 0.1 * s, h - 0.05 * s, h + 0.12 * s,
         trim)
    K.bb(mb, Fb, -w / 2 + 0.06 * s, w / 2 - 0.06 * s, d / 2, d / 2 + 0.13 * s, h * 0.62, h + 0.02 * s, trim)  # aba
    K.bb(mb, Fb, -w * 0.32, w * 0.32, d / 2, d / 2 + 0.22 * s, h * 0.12, h * 0.5, body)                      # bolso
    for sx in (-1, 1):
        K.bb(mb, Fb, sx * w * 0.28 - 0.08 * s, sx * w * 0.28 + 0.08 * s, -d / 2 - 0.12 * s, -d / 2, 0.15 * s,
             h * 0.95, trim)
    K.bb(mb, Fb, -0.18 * s, 0.18 * s, -0.06 * s, 0.06 * s, h + 0.12 * s, h + 0.3 * s, trim)


# ================================================================== PRACA
def NORTH_SECTOR(x, z):
    return abs(x) < 9.7 and z < PCZ and rp(x, z) > 34.5          # pedras do trecho (rua do eixo)


STAIR_BOX = (-14.8, 14.8, 79.6, 90.0)                              # escadaria do spawn (sobre a praca)
ARCS = {"NW": (-165.0, -141.0), "NE": (-43.0, -27.0), "SE": (6.0, 27.0), "SW": (126.0, 156.0)}
R_PL0, R_PL1 = 36.4, 39.3


def plaza():
    mb = MB("VM_Town_Plaza", "03_TOWN", detail="far", floor=FLOOR_ALL)
    ztop = PLAZA_TOP + 0.04            # topo das pedras ~6,12: 0,15 acima do leito (5,95) - sem z-fight

    def keep(x, z):
        return not NORTH_SECTOR(x, z) and not (STAIR_BOX[0] < x < STAIR_BOX[1] and z > STAIR_BOX[2])
    bands = [(9.0, 9.95, "edge")]
    r = 9.95
    while r < 19.9:
        bands.append((r, min(20.0, r + 1.68), "in"))
        r += 1.68
    bands.append((20.0, 21.0, "edge"))
    r = 21.0
    while r < 34.7:
        bands.append((r, min(34.8, r + 2.6), "out"))
        r += 2.6
    bands.append((34.8, 36.0, "edge"))
    n = 0
    for i, (r0, r1, kind) in enumerate(bands):
        hw = (r1 - r0) / 2
        path = circle_path(PCX, PCZ, (r0 + r1) / 2, n=200)
        if kind == "edge":
            n += band(mb, path, -hw, hw, (2.5, 3.3), None, ztop, ("pedge", i), mats=(K.PAVE_E, K.PAVE_E), keep=keep,
                      c=(0.08, 0.2))
        else:
            row = (2.2, 2.9) if kind == "in" else (3.3, 4.3)
            pB = 0.62 if i % 2 else 0.18                     # aneis alternando o tom (le o desenho de longe)
            n += band(mb, path, -hw, hw, row, None, ztop, ("pring", i), pB=pB, keep=keep)
    for a0, a1 in ((0, 180), (180, 360)):
        VL.slab(mb, VL.sector_r(PCX, PCZ, 9.0, 36.0, a0, a1, 40), BED_P - 0.3, BED_P, K.PAVE_J)
    mb.finish()
    STATS["pedras_praca"] = n


def door_angles():
    """angulos (graus, em volta da praca) das portas que dao para a praca -> folga nos canteiros"""
    out = []
    for h in HOUSE_INFO:
        d = h.get("door_r")
        if d and rp(*d) < 46:
            out.append(ang_p(*d))
    return out


def plaza_border(dmb):
    """canteiros em arco na borda da praca (meio-fio de pedra, terra, arbustos e flores), com folga nas portas, bancos
    voltados para o centro e postes nas pontas dos arcos"""
    mb = MB("VM_Town_PlazaBorder", "03_TOWN", detail="far", floor=-999)
    doors = door_angles()
    rr = K.rng("border")
    for key, (a0, a1) in sorted(ARCS.items()):
        cuts = [a0]
        for d in sorted(doors):
            if a0 < d < a1:
                cuts += [d - 4.4, d + 4.4]
        cuts.append(a1)
        pieces = [(cuts[i], cuts[i + 1]) for i in range(0, len(cuts) - 1, 2) if cuts[i + 1] - cuts[i] > 4.0]
        for k, (b0, b1) in enumerate(pieces):
            for rr_, w in ((R_PL0 + 0.35, 0.7), (R_PL1 - 0.35, 0.7)):
                stone_row(mb, arc_path(PCX, PCZ, rr_, b0, b1, 1.0), 0.0, w, Y - 0.2, 0.95, ("pl", key, k, rr_),
                          m="Stone_VM_Warm", ln=(1.5, 2.2))
            for b in (b0, b1):
                a = math.radians(b)
                ux, uz = math.cos(a), math.sin(a)
                rm = (R_PL0 + R_PL1) / 2
                Fe = K.frame_r(PCX + ux * rm, PCZ + uz * rm, Y - 0.2, ux, uz)      # +y = radial
                K.through_stone(mb, Fe, -0.45, 0.45, -(R_PL1 - R_PL0) / 2, (R_PL1 - R_PL0) / 2, -0.2, 1.0,
                                "Stone_VM_Warm", c=0.14)
            VL.slab(mb, VL.sector_r(PCX, PCZ, R_PL0 + 0.55, R_PL1 - 0.55, b0 + 0.6, b1 - 0.6, 8), Y - 0.25, Y + 0.55,
                    K.PAVE_J)                     # terra do canteiro = tom da junta (teto de materiais)
            span = math.radians(b1 - b0) * (R_PL0 + R_PL1) / 2
            nb = max(1, int(span / 3.4))
            for j in range(nb):
                a = math.radians(b0 + (b1 - b0) * (j + 0.5) / nb + rr.uniform(-1.0, 1.0))
                rm = (R_PL0 + R_PL1) / 2 + rr.uniform(-0.25, 0.25)
                x, z = PCX + math.cos(a) * rm, PCZ + math.sin(a) * rm
                s = rr.uniform(0.85, 1.15)
                mb.ico(0.95 * s, tuple(VL.B(x, z, Y + 1.2 * s)), "Leaf_VM_Round", 1, (1.0, 1.0, 0.85), jitter=0.12)
                if dmb is not None:
                    for q in range(3):
                        aa = a + rr.uniform(0.04, 0.07) * (1 if q % 2 else -1)
                        r2 = rm + rr.uniform(-0.5, 0.5)
                        dmb.ico(0.2, tuple(VL.B(PCX + math.cos(aa) * r2, PCZ + math.sin(aa) * r2,
                                                Y + 0.72 + rr.uniform(0, 0.2))), "Flower_VM_Red", 1, (1, 1, 0.8),
                                jitter=0.1)
            nseg = max(1, int(span / 6.0) + 1)
            for j in range(nseg):
                c0 = math.radians(b0 + (b1 - b0) * j / nseg)
                c1 = math.radians(b0 + (b1 - b0) * (j + 1) / nseg)
                cm = (c0 + c1) / 2
                rm = (R_PL0 + R_PL1) / 2
                ln = 2 * rm * math.sin((c1 - c0) / 2)
                VL.colr_rot("PlazaBorder", PCX + math.cos(cm) * rm, PCZ + math.sin(cm) * rm, Y + 0.5, ln,
                            R_PL1 - R_PL0, 1.0, -math.sin(cm), math.cos(cm))
        am = math.radians((a0 + a1) / 2)
        ux, uz = math.cos(am), math.sin(am)
        bx_, bz_ = PCX + ux * 34.2, PCZ + uz * 34.2
        bench(mb, K.frame_r(bx_, bz_, PLAZA_TOP, -ux, -uz), 4.4, seed=key)
        VL.colr_rot("PlazaBench", bx_, bz_, Y + 0.8, 4.4, 1.8, 1.6, -uz, ux)
    for nm, a in (("P1", -24.0), ("P2", 4.0), ("P3", 31.0), ("P4", 160.0)):
        r_ = math.radians(a)
        lamp(mb, nm, PCX + math.cos(r_) * 34.9, PCZ + math.sin(r_) * 34.9, PLAZA_TOP, 9.6,
             (-math.cos(r_), -math.sin(r_)))
    mb.finish()


# ================================================================== TERRACO DO SPAWN
ST_X = 13.0          # meia largura da escadaria nova (V0: 10)
ST_N, ST_RISE, ST_RUN, ST_FOOT = 5, 0.72, 1.6, 80.0


def spawn_terrace(dmb):
    mb = MB("VM_Town_Spawn", "03_TOWN", detail="far", floor=-999)
    T = L.SPAWN_TERRACE
    yb, yt = Y - 0.4, L.Y_SPAWN
    cen = (0.0, 100.0)
    inset = [(cen[0] + (x - cen[0]) * 0.975, cen[1] + (z - cen[1]) * 0.96) for x, z in T]
    VL.slab(mb, inset, yb, yt - 0.35, K.MOR)
    VL.slab(mb, [(cen[0] + (x - cen[0]) * 0.99, cen[1] + (z - cen[1]) * 0.985) for x, z in T], yt - 0.45, yt - 0.2,
            K.PAVE_J)
    n = len(T)
    for i in range(n):
        a, b = T[i], T[(i + 1) % n]
        dx, dz = b[0] - a[0], b[1] - a[1]
        ln = math.hypot(dx, dz)
        nx, nz = dz / ln, -dx / ln
        if (nx * ((a[0] + b[0]) / 2 - cen[0]) + nz * ((a[1] + b[1]) / 2 - cen[1])) < 0:
            nx, nz = -nx, -nz
        segs = [(0.0, ln)]
        if abs(a[1] - 88.0) < 0.1 and abs(b[1] - 88.0) < 0.1:       # frente: vao da escadaria
            ua = (-ST_X - 1.6 - a[0]) / (dx / ln)
            ub = (ST_X + 1.6 - a[0]) / (dx / ln)
            lo, hi = min(ua, ub), max(ua, ub)
            segs = [(0.0, lo), (hi, ln)]
        for (u0, u1) in segs:
            if u1 - u0 < 0.5:
                continue
            um = (u0 + u1) / 2
            mx, mz = a[0] + dx / ln * um, a[1] + dz / ln * um
            Ff = K.frame_r(mx, mz, 0.0, nx, nz)
            K.stone_face(mb, Ff, -(u1 - u0) / 2, (u1 - u0) / 2, Y - 0.5, yt - 0.3, "Stone_VM_Warm",
                         seed=("spawnwall", i, round(u0, 1)), lod=1 if nz < -0.5 else 2, m2="Stone_VM_Grey", p2=0.3)
    for i, (x, z) in enumerate(T):                                 # quinas de cantaria
        K.chimney(mb, F0, x, -z, Y - 0.5, yt - 0.25, "Stone_VM_Trim", seed=("quina", i), w=1.5, crown=None)
    r = K.rng("spawnfloor")
    ins2 = [(cen[0] + (x - cen[0]) * 0.955, cen[1] + (z - cen[1]) * 0.93) for x, z in T]
    zt = yt - 0.02
    s = 3.5
    zz = 88.2
    k = 0
    while zz < 111.8:
        z2 = zz + s
        xx = -20.0 + (s / 2 if k % 2 else 0.0)
        while xx < 20.0:
            x2 = xx + s * r.uniform(0.9, 1.25)
            q = [(xx + 0.07, zz + 0.07), (x2 - 0.07, zz + 0.07), (x2 - 0.07, z2 - 0.07), (xx + 0.07, z2 - 0.07)]
            cx, cz = (xx + x2) / 2, (zz + z2) / 2
            if VL.in_poly(cx, cz, ins2) and math.hypot(cx - L.SPAWN[0], cz - L.SPAWN[1]) > 8.2:
                m = K.PAVE_B if r.random() < 0.35 else K.PAVE_A
                K.cobble(mb, F0, [(x_, -z_) for x_, z_ in q], lambda qx, qy, d=r.uniform(-0.02, 0.03): zt + d, m,
                         c1=0.08, c2=0.24)
            xx = x2
        zz = z2
        k += 1
    sx, sz = L.SPAWN
    band(mb, circle_path(sx, sz, 7.55, 64), -0.6, 0.6, (1.6, 2.1), None, zt, "spawnring", mats=(K.PAVE_E, K.PAVE_E),
         c=(0.08, 0.2))
    band(mb, circle_path(sx, sz, 6.55, 64), -0.4, 0.4, (2.2, 2.6), None, zt + 0.03, "spawnbronze",
         mats=(K.BRONZE, K.BRONZE), c=(0.06, 0.12))
    VL.slab(mb, VL.circle_r(sx, sz, 6.1, 32), yt - 0.4, yt - 0.01, "Stone_VM_Trim")
    # ESCADARIA (x +-13): degraus de cantaria em blocos, pe na praca (z 80) ate o terraco (z 88)
    for i in range(ST_N):
        z0 = ST_FOOT + ST_RUN * i - 0.12
        z1 = ST_FOOT + ST_RUN * (i + 1)
        top = Y + ST_RISE * (i + 1)
        xs = [-ST_X]
        while xs[-1] < ST_X - 0.5:
            xs.append(min(ST_X, xs[-1] + r.uniform(2.4, 3.6)))
            if ST_X - xs[-1] < 1.4:
                xs[-1] = ST_X
        for xa, xb in zip(xs, xs[1:]):
            Fs = K.frame_r((xa + xb) / 2, (z0 + z1) / 2, 0.0, 0, -1)
            K.through_stone(mb, Fs, -(xb - xa) / 2 + 0.05, (xb - xa) / 2 - 0.05, -(z1 - z0) / 2, (z1 - z0) / 2,
                            Y - 0.4, top + r.uniform(-0.01, 0.02), "Stone_VM_Trim", c=0.1)
    pm = mb
    for sgn in (-1, 1):
        xc = sgn * (ST_X + 0.8)
        for i in range(ST_N):
            z0 = ST_FOOT + ST_RUN * i
            Fs = K.frame_r(xc, z0 + ST_RUN / 2, 0.0, 0, -1)
            K.through_stone(mb, Fs, -0.8, 0.8, -ST_RUN / 2 - 0.02, ST_RUN / 2 + 0.02, Y - 0.4,
                            Y + ST_RISE * (i + 1) + 1.1, "Stone_VM_Warm", c=0.14)
        K.chimney(mb, F0, xc, -(ST_FOOT - 0.9), Y - 0.3, Y + 2.2, "Stone_VM_Trim", seed=("ped", sgn), w=2.0,
                  crown="Stone_VM_Trim")
        lamp(pm, "Spawn%s" % ("W" if sgn < 0 else "E"), xc, ST_FOOT - 0.9, Y + 2.2, 6.6, (0, -1),
             stone="Stone_VM_Trim")
        VL.colr("SpawnCheek", (xc - 0.8, Y, ST_FOOT - 1.9), (xc + 0.8, yt + 1.6, 88.0))
    # colisao da escadaria nova (mesma regra do fm_parts.stairs: rampa pelo meio dos pisos + meia pisada final)
    base = VL.B(0.0, ST_FOOT, Y)
    F = Frame(base.x, base.y, base.z, VL.yaw_b(0, 1))
    fm_lib.col_ramp("Spawn", F.p(-ST_RUN / 2, 0, 0), F.p(ST_RUN * ST_N - ST_RUN / 2, 0, ST_RISE * ST_N), 2 * ST_X)
    q = F.p(ST_RUN * ST_N - ST_RUN / 4 + 0.15, 0, ST_RISE * ST_N - 0.5)
    col_box("Spawn", (ST_RUN / 2 + 0.3, 2 * ST_X, 1.0), (q.x, q.y, q.z), F.r())
    # BALAUSTRADA (frente, diagonais e lados) e parapeito de pedra seca nos fundos
    pts = [(-ST_X - 1.6, 88.0), (-17.0, 88.0), (-20.0, 91.0), (-20.0, 109.0), (-17.0, 112.0), (17.0, 112.0),
           (20.0, 109.0), (20.0, 91.0), (17.0, 88.0), (ST_X + 1.6, 88.0)]
    inner = []
    for (x, z) in pts:
        ix = x - math.copysign(0.55, x) if abs(x) > 16.5 else x
        iz = z + 0.55 if z < 100 else z - 0.55
        inner.append((ix, iz))
    for i, (a, b) in enumerate(zip(inner, inner[1:])):
        dx, dz = b[0] - a[0], b[1] - a[1]
        ln = math.hypot(dx, dz)
        fx, fz = dx / ln, dz / ln
        mx, mz = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
        back = a[1] > 108 and b[1] > 108
        Fb = K.frame_r(mx, mz, yt, fz, -fx)            # +x local = R = (fx, fz): ao longo do trecho
        if back:
            K.mureta(mb, Fb, ln + 0.6, h=1.45, w=0.95, m="Stone_VM_Warm", m2="Stone_VM_Trim", seed=("parb", i), lod=1)
        else:
            balustrade(mb, Fb, ln, seed=("bal", i))
        VL.colr_rot("SpawnRail", mx, mz, yt + 1.6, ln + 0.4, 1.0, 3.2, fx, fz)
    for i, (x, z) in enumerate(inner):                # pilares nos vertices
        K.chimney(mb, F0, x, -z, yt - 0.1, yt + 2.0, "Stone_VM_Trim", seed=("bp", i), w=1.15, crown="Stone_VM_Trim")
    mb.finish()
    mail_kiosk()


def balustrade(mb, F, L_, seed=0, h=1.55):
    """BALAUSTRADA ao longo de x local (-L/2..L/2) com base em z=0: plinto, balaustres torneados (6 lados), corrimao"""
    r = K.rng("bal", seed)
    K.through_stone(mb, F, -L_ / 2, L_ / 2, -0.5, 0.5, -0.12, 0.22, "Stone_VM_Trim", c=0.08)
    n = max(2, int(L_ / 1.45))
    for i in range(n):
        x = -L_ / 2 + L_ * (i + 0.5) / n
        K.lathe(mb, F, (x, 0.0, 0.2), [(0.21, 0.0), (0.31, 0.4), (0.16, 0.9), (0.24, h - 0.3)], 6,
                "Stone_VM_Trim")
    K.through_stone(mb, F, -L_ / 2 - 0.05, L_ / 2 + 0.05, -0.42, 0.42, h - 0.32, h + 0.05 + r.uniform(0, 0.02),
                    "Stone_VM_Trim", c=0.1)


def mail_kiosk():
    """CORREIO junto ao spawn: telhadinho de 4 pilares sobre o lugar do MailBox (o modelo do jogo fica embaixo),
    placa com envelope em relevo"""
    mx, mz = L.MAILBOX
    yt = L.Y_SPAWN
    mb = MB("VM_Mail_Kiosk", "05_SERVICES", detail="far", floor=-999)
    F = K.frame_r(mx, mz, yt, 1, 0)                   # +y = olha +X (para quem nasce)
    W, D, H = 5.0, 4.2, 8.2
    for sx in (-1, 1):
        for sy in (-1, 1):
            K.through_stone(mb, F, sx * W / 2 - 0.45, sx * W / 2 + 0.45, sy * D / 2 - 0.45, sy * D / 2 + 0.45, -0.1,
                            0.6, "Stone_VM_Trim", c=0.1)
            K.bb(mb, F, sx * W / 2 - 0.22, sx * W / 2 + 0.22, sy * D / 2 - 0.22, sy * D / 2 + 0.22, 0.5, H, K.T)
            K.beam(mb, F, (sx * W / 2, sy * D / 2 - sy * 0.1, H - 1.6), (sx * W / 2, sy * (D / 2 - 1.1), H - 0.1),
                   0.3, 0.3)
    for sy in (-1, 1):
        K.bb(mb, F, -W / 2 - 0.3, W / 2 + 0.3, sy * D / 2 - 0.25, sy * D / 2 + 0.25, H - 0.4, H + 0.05, K.T)
    for sx in (-1, 1):
        K.bb(mb, F, sx * W / 2 - 0.25, sx * W / 2 + 0.25, -D / 2 - 0.3, D / 2 + 0.3, H - 0.4, H + 0.05, K.T)
    RF = K.sub(F, 0.0, 0.0, H, math.pi / 2)            # cumeeira ao longo de y (frente-fundo)
    ri = K.roof(mb, RF, D, W, 50.0, 0.8, (0.6, 0.6), "Roof_VM_Terracotta", "Roof_VM_Terracotta_B", seed="kiosk",
                rafters=False)
    for g in (-1, 1):
        Fg = K.sub(RF, g * D / 2, 0.0, 0.0, -g * math.pi / 2)
        K.gable_wall(mb, Fg, W, ri["rise"], "Plaster_VM_Cream", window_=False)
    Fs = K.sub(F, 0.0, D / 2 + 0.35, 0.0)
    K.bb(mb, Fs, -1.6, 1.6, -0.12, 0.12, H - 2.7, H - 0.9, K.PLK)
    K.bb(mb, Fs, -1.75, 1.75, -0.2, 0.2, H - 2.85, H - 2.65, K.T)
    K.bb(mb, Fs, -1.0, 1.0, 0.1, 0.22, H - 2.4, H - 1.2, K.BRONZE)
    K.beam(mb, Fs, (-1.0, 0.26, H - 1.25), (0.0, 0.26, H - 1.85), 0.08, 0.16, K.T)
    K.beam(mb, Fs, (1.0, 0.26, H - 1.25), (0.0, 0.26, H - 1.85), 0.08, 0.16, K.T)
    mb.finish()
    for sx in (-1, 1):
        for sy in (-1, 1):
            p = F.p(sx * W / 2, sy * D / 2, 0)
            VL.colr("Kiosk", (p.x - 0.45, yt, -p.y - 0.45), (p.x + 0.45, yt + H, -p.y + 0.45))


# ================================================================== CASAS (kit V1 multiplicado; juncao por quadra)
# paleta por quadra: (rebocos, pedras, telhas) - 2 de cada -> <= 8 materiais (MeshParts) por quadra
PAL = {
    "NW": (("Plaster_VM_Cream", "Plaster_VM_Ochre"), ("Stone_VM_Warm", "Stone_VM_Grey"),
           ("Roof_VM_Terracotta", "Roof_VM_Terracotta_B")),
    "SW": (("Plaster_VM_Peach", "Plaster_VM_Cream"), ("Stone_VM_Grey", "Stone_VM_Warm"),
           ("Roof_VM_Terracotta_C", "Roof_VM_Terracotta")),
    "NE": (("Plaster_VM_Ochre", "Plaster_VM_Peach"), ("Stone_VM_Warm", "Stone_VM_Base"),
           ("Roof_VM_Terracotta", "Roof_VM_Terracotta_C")),
    "SE": (("Plaster_VM_Cream", "Plaster_VM_Peach"), ("Stone_VM_Grey", "Stone_VM_Warm"),
           ("Roof_VM_Terracotta_B", "Roof_VM_Terracotta")),
    "EE": (("Plaster_VM_Peach", "Plaster_VM_Cream"), ("Stone_VM_Warm", "Stone_VM_Grey"),
           ("Roof_VM_Terracotta", "Roof_VM_Terracotta_B")),
    "EW": (("Plaster_VM_Ochre", "Plaster_VM_Cream"), ("Stone_VM_Grey", "Stone_VM_Base"),
           ("Roof_VM_Terracotta_C", "Roof_VM_Terracotta")),
    "SB": (("Plaster_VM_Ochre", "Plaster_VM_Peach"), ("Stone_VM_Warm", "Stone_VM_Grey"),
           ("Roof_VM_Terracotta_B", "Roof_VM_Terracotta_C")),
    "N": (("Plaster_VM_Cream", "Plaster_VM_Peach"), ("Stone_VM_Warm", "Stone_VM_Grey"),
          ("Roof_VM_Terracotta_B", "Roof_VM_Terracotta_C")),
}
REGION = {"NW": "W", "SW": "W", "NE": "E", "SE": "E", "EE": "S", "EW": "S", "N": "W", "SB": "S"}
FLOWER = {"W": "red", "E": "pink", "S": "yellow", "N": "red", "P": "red"}
HOUSE_INFO = []


def _h(id_, preset, W=None, D=10.0, **kw):
    return dict(id=id_, preset=preset, W=W, D=D, kw=kw)


def GAP(g):
    return dict(gap=g)


# fileiras: (quadra, pontos (Roblox), lado (+1: a casa olha para n=(-tz, tx) da fileira; -1: o contrario),
#            deslocamento da frente, ponto de inicio (projetado), opcoes, casas). preset "FILL" = casa de fundo barata.
def rows():
    exitp = L.EXIT_ROAD
    return [
        # praca: oeste-norte (de costas para o adro do ranking) e oeste-sul
        ("NW", [(-35.2, 18.9), (-40.4, 40.6)], -1, 0.0, None, dict(party_start=True, open_back=("NW2",)),
         [_h("NW1", "F2", 10.6), _h("NW2", "B2", 11.6)]),
        ("SW", [(-39.5, 64.6), (-23.6, 86.0)], -1, 0.0, None, {},
         [_h("SW1", "B2", 13.0), _h("SW2", "E2", 13.4)]),
        # rua oeste, lado sul (olham a rua; o lado norte e o adro do ranking)
        ("SW", [(-50.6, 65.4), (-76.2, 71.5)], 1, 0.0, None, {},
         [_h("WS1", "E2", 13.5), _h("WS2", "FILL", 12.0, h=13.5)]),
        # canal oeste (olham o canal): kit lod 2 + casa de fundo
        ("NW", [(-36.0, -3.6), (-60.0, -3.6)], 1, 0.0, None, dict(lod=2),
         [_h("CW1", "FILL", 12.0, h=14.5), _h("CW2", "FILL", 9.0, h=13.0)]),
        # praca: leste-norte, rua da loja (lado norte), canal leste
        ("NE", [(37.4, 18.0), (41.2, 36.0)], 1, 0.0, None, dict(party_start=True),
         [_h("NE1", "D3", 9.6), _h("NE2", "C2", 8.6)]),
        ("NE", [(51.4, 35.6), (61.6, 35.6)], 1, 0.0, None, dict(party_start=True),
         [_h("SN1", "FILL", 10.2, h=14.0)]),
        ("NE", [(23.0, -3.6), (47.4, -3.6)], -1, 0.0, None, dict(lod=2),
         [_h("CE1", "FILL", 12.0, h=15.0), _h("CE2", "FILL", 11.0, h=12.5)]),
        # praca: leste-sul e rua da loja (lado sul)
        ("SE", [(40.9, 52.2), (35.4, 70.0)], 1, 0.0, None, {},
         [_h("SE1", "F2", 10.0), _h("SE2", "C2", 8.6)]),
        ("SE", [(52.0, 50.4), (61.0, 50.4)], -1, 0.0, None, dict(party_start=True),
         [_h("SS1", "FILL", 9.0, h=13.0)]),
        # rua curva de saida: casas dos DOIS lados (enquadramento da ref_01)
        ("EE", exitp, 1, -8.4, (41.0, 79.0), dict(smooth=2),
         [_h("E1", "A3", 13.0, dormers=1), _h("E2", "B2", 12.0), GAP(5.0), _h("E3", "F2", 11.5),
          _h("E4", "FILL", 9.0, h=12.5)]),
        ("EW", exitp, -1, 8.4, (32.0, 96.0), dict(smooth=2),
         [_h("W0", "E2", 13.5), _h("W1", "FILL", 8.6, h=13.5), GAP(3.0), _h("W2", "D3", 9.6)]),
        # fundo do terraco do spawn (olham o terraco): casas de fundo
        ("SB", [(-27.0, 117.5), (25.0, 117.5)], -1, 0.0, None, {},
         [_h("SB1", "FILL", 10.0, h=13.0), GAP(1.2), _h("SB2", "FILL", 9.0, h=15.5), GAP(4.5),
          _h("SB3", "FILL", 12.0, h=14.0), GAP(1.2), _h("SB4", "FILL", 9.0, h=12.5)]),
        # rua norte (canal -> largo da forja), piso 7
        ("N", [(-10.4, -21.2), (-10.4, -35.0)], 1, 0.0, None, dict(y=L.Y_NORTH),
         [_h("N1W", "F2", 13.8)]),
        ("N", [(10.4, -21.2), (10.4, -35.0)], -1, 0.0, None, dict(y=L.Y_NORTH),
         [_h("N1E", "B2", 13.8)]),
    ]


def layout():
    """lista de casas (dados puros): id, quadra, x, z, fx, fz, W, D, y, lod, party, preset, kw"""
    out = []
    for blk, pts, side, off, start, opt, items in rows():
        path = Path(pts, smooth=opt.get("smooth", 0))
        s = path.project(start) if start else 0.0
        prev = None
        row_h = []
        for it in items:
            if "gap" in it:
                s += it["gap"]
                prev = None
                continue
            W = it["W"] or K.spec_of(it["preset"])["W"]
            D = it["D"]
            sm = s + W / 2
            (x, z), (tx, tz) = path.at(sm)
            fx, fz = -tz * side, tx * side
            px, pz = path.pt(sm, off)
            h = dict(id=it["id"], block=blk, preset=it["preset"], x=px - fx * D / 2, z=pz - fz * D / 2, fx=fx, fz=fz,
                     W=W, D=D, y=opt.get("y", Y), lod=opt.get("lod", 1), party=set(), kw=dict(it["kw"]))
            Rx, Rz = -fz, fx
            nextR = (tx * Rx + tz * Rz) > 0          # a proxima casa da fileira fica do lado R desta
            if prev is not None:
                prev["party"].add("R" if nextR else "L")
                h["party"].add("L" if nextR else "R")
            elif opt.get("party_start") and not row_h:
                h["party"].add("L" if nextR else "R")
            if it["id"] not in opt.get("open_back", ()):
                h["party"].add("B")
            row_h.append(h)
            out.append(h)
            prev = h
            s += W
    return out


def house_spec(h, i):
    pl, st, rf = PAL[h["block"]]
    k = K.h01("pal", h["id"])
    kw = dict(seed="V2_" + h["id"], W=h["W"], D=h["D"], lod=h["lod"], party=tuple(sorted(h["party"])),
              plaster=pl[i % 2], stone=st[(i + (1 if k > 0.5 else 0)) % 2],
              roof=(rf[0], rf[1]) if i % 2 == 0 else (rf[1], rf[0]), flowers=FLOWER[REGION[h["block"]]])
    kw.update({k_: v for k_, v in h["kw"].items() if k_ != "h"})
    return K.spec_of(h["preset"] if h["preset"] != "FILL" else None, **kw)


def _vol(F, W, D, yF, eave, gh=None):
    """caixas da casa no referencial F: terreo (ate a face do terreo) + andares (ate a frente do balanco)"""
    if gh is None:
        return [(F, -W / 2, W / 2, -D / 2, yF, -0.6, eave)]
    return [(F, -W / 2, W / 2, -D / 2, D / 2, -0.6, gh), (F, -W / 2, W / 2, -D / 2, yF, gh - 0.3, eave)]


def trecho_volumes():
    """volumes (aproximados) das casas do trecho V1: so para a ocultacao de faces das casas novas encostadas"""
    import vm_trecho as TR
    out = []
    for h in TR.HOUSES:
        sp = TR.house_spec(h)
        jet = list(sp["jetty"]) + [0.0, 0.0]
        yF = sp["D"] / 2 + sum(jet[:sp["floors"] - 1])
        for v in _vol(TR.house_frame(h), sp["W"], sp["D"], yF, sp["gh"] + sp["fh"] * (sp["floors"] - 1), sp["gh"]):
            out.append(("T_" + h["id"], v))
    return out


def _inside(p, vol, shrink=0.1):
    F, x0, x1, y0, y1, z0, z1 = vol
    qx, qy = p.x - F.o.x, p.y - F.o.y
    ca, sa = math.cos(F.a), math.sin(F.a)
    lx, ly, lz = qx * ca + qy * sa, -qx * sa + qy * ca, p.z - F.o.z
    return x0 + shrink < lx < x1 - shrink and y0 + shrink < ly < y1 - shrink and z0 + shrink < lz < z1 - shrink


def cull_hidden(mb, layer, vols):
    """apaga as faces das casas novas que ficam DENTRO da casa vizinha (paredes-meias, fundos encostados): o ponto
    0,35 a frente da face cai no volume (terreo + andares ate o beiral) de OUTRA casa -> face invisivel"""
    kill = []
    for f in mb.bm.faces:
        hid = f[layer]
        if hid == 0:
            continue
        c = f.calc_center_median()
        p = c + f.normal * 0.35
        for vid, vol in vols:
            if vid != hid and _inside(p, vol):
                kill.append(f)
                break
    if kill:
        bmesh.ops.delete(mb.bm, geom=kill, context="FACES")
    return len(kill)


def houses(dress):
    HOUSE_INFO.clear()
    hs = layout()
    blocks = {}
    for h in hs:
        blocks.setdefault(h["block"], []).append(h)
    # volumes de todas as casas (novas + trecho) para a ocultacao
    vols = [(k, v) for k, v in trecho_volumes()]
    plan = []
    for blk in sorted(blocks):
        for i, h in enumerate(blocks[blk]):
            sp = house_spec(h, i)
            F = K.frame_r(h["x"], h["z"], h["y"], h["fx"], h["fz"])
            plan.append((blk, i, h, sp, F))
    hid_of = {}
    for n, (blk, i, h, sp, F) in enumerate(plan, 1):
        hid_of[h["id"]] = n
        if h["preset"] == "FILL":
            vols += [(n, v) for v in _vol(F, sp["W"], sp["D"], sp["D"] / 2, h["kw"].get("h", 13.0))]
        else:
            jet = list(sp["jetty"]) + [0.0, 0.0]
            yF = sp["D"] / 2 + sum(jet[:sp["floors"] - 1])
            vols += [(n, v) for v in _vol(F, sp["W"], sp["D"], yF, sp["gh"] + sp["fh"] * (sp["floors"] - 1), sp["gh"])]
    culled = 0
    for blk in sorted(blocks):
        mb = MB("VM_House_Q" + blk, "03_TOWN", detail="far", floor=-999)
        layer = mb.bm.faces.layers.int.new("hid")
        for (b2, i, h, sp, F) in plan:
            if b2 != blk:
                continue
            n0 = len(mb.bm.faces)
            if h["preset"] == "FILL":
                hh = h["kw"].get("h", 13.0)
                fill_house(mb, F, sp["W"], sp["D"], hh, sp["plaster"], sp["stone"], sp["roof"], ("fill", h["id"]))
                col_box("House", (sp["W"] + 0.2, sp["D"] + 0.2, hh + 1.5), (F.o.x, F.o.y, F.o.z + (hh + 1.5) / 2 - 0.15),
                        F.r())
                HOUSE_INFO.append(dict(h, door_r=None, ridge=hh))
            else:
                info = K.house(mb, F, sp, dmb=dress[REGION[h["block"]]])
                K.house_col("House", F, sp, info)
                d = info.get("door")
                HOUSE_INFO.append(dict(h, door_r=(d[0], -d[1]) if d else None, ridge=info["ridge_z"]))
            hid = hid_of[h["id"]]
            for f in mb.bm.faces:
                if f[layer] == 0:
                    f[layer] = hid
        culled += cull_hidden(mb, layer, vols)
        ob = mb.finish()
        ob["vm_town"] = 1
    STATS["casas"] = len(hs)
    STATS["faces_ocultas_apagadas"] = culled


def fill_house(mb, F, W, D, h, pl, st, roof, seed):
    """CASA DE FUNDO barata (~1,5k tris; o kit lod 1 custa 4-6k): base de pedra com quinas de cantaria, corpo de
    reboco em balanco, enxaimel nas 4 fachadas (frechais, montantes, janelas escuras com verga e peitoril, cruzes),
    porta de tabuas na frente, telhado do kit (lod 1) e oitoes com pendural e diagonais, chamine.
    Para as frentes secundarias e para fechar o fundo das quadras (silhueta de telhados como no AE)."""
    r = K.rng("fill", seed)
    o = 0.4
    K.bb(mb, F, -W / 2, W / 2, -D / 2, D / 2, -0.5, 3.0, st)
    for sx in (-1, 1):
        for sy in (-1, 1):
            K.bb(mb, F, sx * W / 2 - 0.42, sx * W / 2 + 0.42, sy * D / 2 - 0.42, sy * D / 2 + 0.42, -0.5, 3.0,
                 "Stone_VM_Trim")
    K.bb(mb, F, -W / 2, W / 2, -D / 2 - o, D / 2 + o, 3.0, h, pl)      # balanco so na frente e nos fundos
    faces = [(K.sub(F, 0.0, D / 2 + o, 0.0, 0.0), W, "F"), (K.sub(F, 0.0, -D / 2 - o, 0.0, math.pi), W, "B"),
             (K.sub(F, W / 2, 0.0, 0.0, -math.pi / 2), D + 2 * o, "S"),
             (K.sub(F, -W / 2, 0.0, 0.0, math.pi / 2), D + 2 * o, "S")]
    zw = 3.45 + (h - 3.9) * 0.28
    for Fs, Ln, kind in faces:
        e = 0.14 if kind != "S" else -0.13         # frechais dos lados param antes dos da frente (sem sobrepor)
        K.bb(mb, Fs, -Ln / 2 - e, Ln / 2 + e, -0.12, 0.2, 3.0, 3.45, K.T)
        K.bb(mb, Fs, -Ln / 2 - e, Ln / 2 + e, -0.12, 0.2, h - 0.45, h, K.T)
        n = max(2, int(round(Ln / 3.1)))
        xs = [-Ln / 2 + Ln * i / n for i in range(n + 1)]
        for i, x in enumerate(xs):
            ex = -0.13 if kind == "S" else 0.14      # quinas: o montante da frente passa 0,14 do lado (sem coplanar)
            x0 = -Ln / 2 - ex if i == 0 else (Ln / 2 - 0.45 + ex if i == n else x - 0.21)
            K.bb(mb, Fs, x0, x0 + (0.45 if i in (0, n) else 0.42), -0.12, 0.18, 3.45, h - 0.45, K.T)
        for k, (a, b) in enumerate(zip(xs, xs[1:])):
            c = (a + b) / 2
            win = (k % 2 == 1) if kind != "S" else (k == n // 2 and n >= 3)
            if kind == "F" and n == 2:
                win = True
            if win and (b - a) > 2.0:
                K.bb(mb, Fs, c - 0.68, c + 0.68, -0.2, 0.14, zw, zw + 1.95, K.MOR)
                K.bb(mb, Fs, c - 0.95, c + 0.95, -0.12, 0.24, zw + 1.95, zw + 2.3, K.T)
                K.bb(mb, Fs, c - 0.95, c + 0.95, -0.12, 0.34, zw - 0.32, zw, K.T)
            else:
                K.beam(mb, Fs, (a + 0.32, 0.03, 3.55), (b - 0.32, 0.03, h - 0.55), 0.3, 0.32)
                if kind != "S" or r.random() < 0.5:
                    K.beam(mb, Fs, (b - 0.32, 0.03, 3.55), (a + 0.32, 0.03, h - 0.55), 0.3, 0.32)
    Ff = K.sub(F, 0.0, D / 2, 0.0, 0.0)              # porta de tabuas no terreo da frente
    dx = (r.random() - 0.5) * W * 0.4
    K.bb(mb, Ff, dx - 1.5, dx + 1.5, -0.1, 0.18, -0.1, 2.55, K.PLK)
    K.bb(mb, Ff, dx - 1.9, dx + 1.9, -0.1, 0.3, 2.55, 2.95, K.T)
    RF = K.sub(F, 0.0, 0.0, h, 0.0)
    ri = K.roof(mb, RF, W, D + 2 * o, 52.0, 1.0, (0.6, 0.6), roof[0], roof[1], seed=seed, lod=1,
                rafters=False, barge=False)
    for g in (-1, 1):
        Fg = K.sub(RF, g * W / 2, 0.0, 0.0, -g * math.pi / 2)
        K.gable_wall(mb, Fg, D + 2 * o, ri["rise"], pl, party=True)
        hw = (D + 2 * o) / 2
        K.bb(mb, Fg, -0.22, 0.22, -0.12, 0.2, 0.45, ri["rise"] - 0.6, K.T)
        for sg in (-1, 1):
            K.beam(mb, Fg, (sg * (hw - 0.8), 0.04, 0.5), (sg * 0.5, 0.04, ri["rise"] * 0.62), 0.3, 0.32)
    if r.random() < 0.75:
        cx = (r.random() - 0.5) * W * 0.5
        K.chimney(mb, F, cx, -D / 4, h - 1.0, h + ri["rise"] * 0.62 + 1.6, st, seed=seed, w=1.8)


# ================================================================== RUAS (paralelepipedo em geometria, meio-fio)
def in_house(x, z, pad=0.0):
    for h in HOUSE_INFO:
        dx, dz = x - h["x"], z - h["z"]
        u = dx * (-h["fz"]) + dz * h["fx"]           # ao longo da frente
        v = dx * h["fx"] + dz * h["fz"]             # para a frente
        if abs(u) < h["W"] / 2 + pad and -h["D"] / 2 - pad < v < h["D"] / 2 + 1.6 + pad:
            return True
    return False


def road(mb, path, hw, ztop, seed, keep, curb=True, row=(1.6, 2.1), sw=(2.3, 3.3), bed_y=None):
    n = band(mb, path, -hw, hw, row, sw, ztop + 0.06, (seed, "cob"), keep=keep)       # pedras 0,16 acima do leito
    if curb:
        for s in (-1, 1):
            t0, t1 = (hw, hw + 0.72) if s > 0 else (-hw - 0.72, -hw)
            n += band(mb, path, t0, t1, (2.3, 3.3), None, ztop + 0.18, (seed, "curb", s), mats=(K.PAVE_E, K.PAVE_E),
                      keep=keep, c=(0.07, 0.17), bed=0.55)
    band_bed(mb, path, -hw - 0.72, hw + 0.72, bed_y if bed_y is not None else ztop - 0.08, keep=keep)
    return n


def west_path():
    return Path(L.WEST_ROAD, smooth=2)


def forecourt_poly():
    """adro do ranking: da borda do palco ate a borda norte da rua oeste, a oeste da NW2"""
    ox, oz = L.RANK_O
    fx, fz = L.RANK_FACE
    n = math.hypot(fx, fz)
    fx, fz = fx / n, fz / n
    Tx, Tz = -fz, fx
    fc = (ox + fx * 17.2, oz + fz * 17.2)
    E = (fc[0] - Tx * 29.0, fc[1] - Tz * 29.0)
    Wp = (fc[0] + Tx * 29.0, fc[1] + Tz * 29.0)
    pw = west_path()
    edge = []
    k = 60
    for i in range(k + 1):
        s = pw.L * (k - i) / k
        x, z = pw.pt(s, 7.0)                       # n da rua oeste aponta para o norte
        if -104.5 <= x <= -50.6:
            edge.append((x, z))
    return [E, Wp] + edge


def streets(dress):
    def ok_out(x, z):
        return rp(x, z) > 36.3 and not in_house(x, z, 0.3)
    # rua oeste + adro de lajes do ranking
    mw = MB("VM_Town_RoadW", "03_TOWN", detail="far", floor=FLOOR_ALL)
    pw = west_path()
    n = road(mw, pw, 6.3, ROAD_TOP, "west", lambda x, z: ok_out(x, z) and rc(x, z) > 40.8)
    FC = forecourt_poly()
    ox, oz = L.RANK_O
    fx, fz = L.RANK_FACE
    nn = math.hypot(fx, fz)
    fx, fz = fx / nn, fz / nn
    Tx, Tz = -fz, fx
    fc = (ox + fx * 17.2, oz + fz * 17.2)
    r = K.rng("adro")
    v = 0.25
    k = 0
    while v < 42.0:
        v2 = v + r.uniform(2.8, 3.4)
        u = -36.0 + (1.3 if k % 2 else 0.0)
        while u < 36.0:
            u2 = u + r.uniform(3.0, 3.8)
            q = [(fc[0] + Tx * a + fx * b, fc[1] + Tz * a + fz * b) for a, b in
                 ((u + 0.07, v + 0.07), (u2 - 0.07, v + 0.07), (u2 - 0.07, v2 - 0.07), (u + 0.07, v2 - 0.07))]
            cx, cz = sum(p[0] for p in q) / 4, sum(p[1] for p in q) / 4
            inside = VL.in_poly(cx, cz, FC)
            if inside and ok_out(cx, cz):
                m = "Stone_Paving_VM_Edge" if r.random() < 0.35 else "Stone_VM_Trim"
                K.cobble(mw, F0, [(x_, -z_) for x_, z_ in q], lambda qx, qy, d=r.uniform(-0.02, 0.03): ROAD_TOP + 0.06 + d,
                         m, c1=0.07, c2=0.2)
                n += 1
            u = u2
        v = v2
        k += 1
    VL.slab(mw, FC, BED_R - 0.3, BED_R, K.PAVE_J)
    mw.finish()
    # rua da loja + rua norte
    me = MB("VM_Town_RoadE", "03_TOWN", detail="far", floor=FLOOR_ALL)
    n += road(me, Path([(30.0, 43.0), (61.9, 43.0)]), 5.3, ROAD_TOP, "shop", ok_out)
    n += road(me, Path([(0.0, -21.0), (0.0, -36.4)]), 8.98, L.Y_NORTH, "north", lambda x, z: z > -36.4,
              bed_y=L.Y_NORTH - 0.08)
    me.finish()
    # rua curva de saida (praca -> portao)
    ms = MB("VM_Town_RoadS", "03_TOWN", detail="far", floor=FLOOR_ALL)
    n += road(ms, Path(L.EXIT_ROAD, smooth=2), 6.3, ROAD_TOP, "exit", lambda x, z: ok_out(x, z) and z < 145.9)
    ms.finish()
    STATS["pedras_ruas"] = n
    street_props(dress)


def street_props(dress):
    """postes das ruas (baixos: a lanterna passa por baixo dos balancos), carroca da rua de saida (ref_01), barris,
    caixotes, touceiras na borda de grama"""
    pm = MB("VM_Town_StreetProps", "03_TOWN", detail="far", floor=-999)
    pw = west_path()
    for nm, s, t in (("W1", 16.0, -7.6), ("W3", 56.0, -7.6)):
        x, z = pw.pt(s, t)
        lamp(pm, nm, x, z, Y, 7.8)
    pe = Path(L.EXIT_ROAD, smooth=2)
    for nm, s, t in (("S1", 24.0, 7.6), ("S3", 62.0, -7.6)):
        x, z = pe.pt(s, t)
        lamp(pm, nm, x, z, Y, 7.8)
    for nm, x, z in (("L1", 60.0, 36.2), ("L2", 60.0, 49.8)):
        lamp(pm, nm, x, z, Y, 7.8)
    for nm, x in (("N1", -9.9), ("N2", 9.9)):
        lamp(pm, nm, x, -35.2, L.Y_NORTH, 7.8)
    # carroca + barris + caixotes na rua de saida (lado leste, na boca do beco entre E2 e E3)
    s_c = 47.0
    x, z = pe.pt(s_c, -7.9)
    (px, pz), (tx, tz) = pe.at(s_c)
    Fc = K.frame_r(x, z, Y - 0.05, tz, -tx)           # +x local (varais) ao longo da rua
    K.cart(pm, Fc)
    VL.colr_rot("StreetProps", x, z, Y + 1.7, 7.0, 4.6, 3.4, tx, tz)
    rr = K.rng("sprops")
    for i, (s, t) in enumerate(((s_c + 5.0, -8.0), (s_c + 6.3, -8.4), (30.0, 8.0), (31.4, 8.3))):
        bx_, bz_ = pe.pt(s, t)
        K.barrel(pm, K.frame_r(bx_, bz_, Y - 0.05, 1, 0), 0.0, 0.0, h=2.2, r=0.85)
        VL.colr("StreetProps", (bx_ - 0.9, Y, bz_ - 0.9), (bx_ + 0.9, Y + 2.3, bz_ + 0.9))
    for i, (s, t, a) in enumerate(((s_c + 7.8, -8.1, 0.3), (65.0, 8.2, 0.1))):
        bx_, bz_ = pe.pt(s, t)
        K.crate(pm, K.frame_r(bx_, bz_, Y - 0.05, 1, 0), 0.0, 0.0, s=1.8, a=a)
        VL.colr("StreetProps", (bx_ - 1.0, Y, bz_ - 1.0), (bx_ + 1.0, Y + 1.9, bz_ + 1.0))
    pm.finish()
    # touceiras e pedras soltas na borda de grama das ruas (entre o meio-fio e as fachadas)
    em = MB("VM_Town_Edges2", "03_TOWN", detail="far", floor=-999)
    k = 0
    for path, hw, ss in ((pw, 7.0, (8.0, 76.0)), (pe, 7.0, (12.0, 80.0))):
        s = ss[0]
        while s < ss[1]:
            for sgn in (-1, 1):
                if rr.random() < 0.55:
                    x, z = path.pt(s, sgn * (hw + rr.uniform(0.3, 1.1)))
                    if not in_house(x, z, 0.2) and rp(x, z) > 40:
                        K.tuft(em, F0, x, -z, L.Y_GRASS - 0.05, h=rr.uniform(0.8, 1.4), k=("t2", k))
                        if rr.random() < 0.3:
                            K.pebble(em, F0, x + 0.6, -z, L.Y_GRASS - 0.05, rr.uniform(0.5, 0.9), "Stone_VM_Grey", k)
                k += 1
            s += rr.uniform(3.4, 5.0)
    em.finish()


# ================================================================== LOJA DE MOCHILAS (leste)
SHOP_GH = 9.8         # terreo de pedra (porta 6 x 9)
SHOP_FH = 6.2         # andar enxaimel -> beiral a 16 do piso (paredes de 16)


def shop(dress):
    x0, x1, z0, z1 = L.SHOP
    y0 = L.Y_SHOP
    FS = K.frame_r((x0 + x1) / 2, (z0 + z1) / 2, y0, -1, 0)      # +y = oeste (fachada), +x = norte (-Z)
    W, D = (z1 - z0), (x1 - x0)                                   # 26 de frente, 28 de fundo
    hw, hd = W / 2, D / 2
    GH, FH = SHOP_GH, SHOP_FH
    ST, PL = "Stone_VM_Warm", "Plaster_VM_Cream"
    mb = MB("VM_Shop_Building", "05_SERVICES", detail="far", floor=-999)
    dmb = dress["E"]
    # ---------------- terreo de pedra (4 lados): face externa de pedra, miolo escuro, reboco por dentro
    VC = 7.7                                                      # vitrines em x = +-7.7
    door = (-3.0, 3.0, -0.7, 9.0)
    vits = [(-VC - 2.5, -VC + 2.5, 1.4, 5.9), (VC - 2.5, VC + 2.5, 1.4, 5.9)]
    sides = {"F": (K.sub(FS, 0.0, hd, 0.0, 0.0), W), "B": (K.sub(FS, 0.0, -hd, 0.0, math.pi), W),
             "R": (K.sub(FS, hw, 0.0, 0.0, -math.pi / 2), D), "L": (K.sub(FS, -hw, 0.0, 0.0, math.pi / 2), D)}
    for side, (Ff, Ln) in sides.items():
        holes = [door] + vits if side == "F" else ([K.ground_window_hole(0.0, 2.9, 1.7, 2.3)] if side in "RL" else [])
        ext = 0.12 if side in "FB" else 0.0
        lod = {"F": 1, "R": 1, "L": 2, "B": 2}[side]
        K.stone_face(mb, Ff, -Ln / 2 - ext, Ln / 2 + ext, -0.7, GH - 0.02, ST, holes, seed=("shop", side), lod=lod)
        K.panel(mb, Ff, -Ln / 2 + 0.02, Ln / 2 - 0.02, -0.7, GH, -K.CORE, -0.98, holes, K.MOR)
        K.panel(mb, Ff, -Ln / 2 + 1.0, Ln / 2 - 1.0, 0.0, GH - 0.3, -0.98, -1.12, holes, PL)      # reboco interno
        if side in "RL":
            K.window_ground(mb, Ff, 0.0, 2.9, 1.7, 2.3, ST, dmb=None, shutters=True, flowers=None, seed=("sw", side))
    Ff = sides["F"][0]
    # porta larga: ombreiras e verga de madeira grossa, soleira, folhas de tabua abertas para dentro
    for s in (-1, 1):
        K.bb(mb, Ff, s * 3.0 - 0.45, s * 3.0 + 0.45, -1.15, 0.32, -0.3, 9.0, K.T)
    K.bb(mb, Ff, -3.9, 3.9, -1.15, 0.36, 9.0, 9.9, K.T)
    K.bb(mb, Ff, -3.5, 3.5, -0.9, 1.0, -0.42, 0.0, ST)
    for s in (-1, 1):
        Fl = K.sub(Ff, s * 2.6, -1.15, 0.0, s * math.radians(-72))
        for k in range(3):
            xa, xb = (-s * (0.05 + k * 0.92), -s * (0.05 + (k + 1) * 0.92))
            K.bb(mb, Fl, min(xa, xb) + 0.03, max(xa, xb) - 0.03, -0.22, 0.0, 0.1, 8.7, K.PLK)
        for zz in (1.2, 4.4, 7.6):
            K.bb(mb, Fl, min(0.0, -s * 2.76), max(0.0, -s * 2.76), -0.34, -0.2, zz - 0.2, zz + 0.2, K.T)
    # vitrines abertas em balanco: base de pedra, tabuleiro, montantes, mainel e mochilas expostas
    bodies = ("Cloth_VM_Red", "Cloth_VM_Blue", "Cloth_VM_Red")
    for sv in (-1, 1):
        c = sv * VC
        K.bb(mb, Ff, c - 2.85, c + 2.85, -0.9, 1.5, -0.6, 1.4, ST)
        K.bb(mb, Ff, c - 2.55, c + 2.55, -1.2, 1.35, 1.4, 1.62, K.PLK)
        for xx in (c - 2.6, c, c + 2.6):
            K.bb(mb, Ff, xx - 0.22, xx + 0.22, 1.0, 1.42, 1.6, 6.25, K.T)
        K.bb(mb, Ff, c - 2.85, c + 2.85, -0.2, 1.55, 5.9, 6.5, K.T)
        for j, xx in enumerate((c - 1.6, c + 1.4)):
            backpack(mb, Ff, xx, -0.2, 1.62, s=1.05, body=bodies[(j + (sv > 0)) % 3], a=0.15 * (1 if j else -1))
    # ---------------- andar enxaimel em balanco (frente) + oitao para a rua
    yF = hd + 0.8
    z0f = GH
    K.bb(mb, FS, -hw + K.CORE, hw - K.CORE, -hd + K.CORE, yF - K.CORE, z0f, z0f + FH, PL)
    K.bb(mb, FS, -hw, hw, hd - 0.3, yF, z0f - 0.26, z0f + 0.02, K.T)                  # forro do balanco
    for x in K.even(-hw + 0.5, hw - 0.5, 1.55):
        K.bb(mb, FS, x - 0.21, x + 0.21, hd - 0.3, yF + 0.16, z0f - 0.66, z0f - 0.2, K.T)
    for x in (-hw + 0.35, -4.0, 4.0, hw - 0.35):
        K.beam(mb, FS, (x, hd - 0.25, z0f - 2.3), (x, yF - 0.2, z0f - 0.5), 0.38, 0.4)
    for side in "FBRL":
        if side == "F":
            Fu, Ln = K.sub(FS, 0.0, yF, z0f, 0.0), W
        elif side == "B":
            Fu, Ln = K.sub(FS, 0.0, -hd, z0f, math.pi), W
        else:
            yc = (yF - hd) / 2
            sg = 1 if side == "R" else -1
            Fu, Ln = K.sub(FS, sg * hw, yc, z0f, -sg * math.pi / 2), yF + hd
        xs, ks = K.bays_for(Ln, "F" if side == "F" else ("B" if side == "B" else "S"), K.rng("shopbays", side))
        K.upper_wall(mb, Fu, Ln, FH, PL, xs, ks, dmb=dmb if side == "F" else None, flowers="pink",
                     seed=("shopup", side), lod=0 if side == "F" else (2 if side == "B" else 1))
    eave = z0f + FH
    yc = (yF - hd) / 2
    Dt = yF + hd
    RF = K.sub(FS, 0.0, yc, eave, math.pi / 2)
    ri = K.roof(mb, RF, Dt, W, 47.0, 1.3, (1.0, 1.2), "Roof_VM_Terracotta", "Roof_VM_Terracotta_B", seed="shoproof",
                lod=1, rafters=False)
    for g in (-1, 1):
        Fg = K.sub(RF, g * Dt / 2, 0.0, 0.0, -g * math.pi / 2)
        K.gable_wall(mb, Fg, W, ri["rise"], PL, window_=(g < 0), dmb=None, seed=("shopg", g))
    K.chimney(mb, FS, hw * 0.5, -hd + 4.0, eave - 1.0, eave + ri["rise"] * 0.75 + 2.0, ST, seed="shopch")
    # ---------------- PLACA GRANDE com mochila em relevo (no oitao, sobre o andar)
    Fp = K.sub(FS, 0.0, yF + 0.35, eave + 0.7, 0.0)
    K.bb(mb, Fp, -4.4, 4.4, -0.2, 0.15, 0.0, 4.0, K.PLK)
    for zz in (-0.12, 3.92):
        K.bb(mb, Fp, -4.6, 4.6, -0.25, 0.32, zz, zz + 0.3, K.T)
    for xx in (-4.55, 4.55):
        K.bb(mb, Fp, xx - 0.15, xx + 0.15, -0.25, 0.32, -0.1, 4.2, K.T)
    backpack(mb, Fp, 0.0, 0.62, 0.45, s=2.55, body="Cloth_VM_Red")
    for xx in (-3.3, 3.3):                                          # mochilas pequenas dos lados (azul)
        backpack(mb, Fp, xx, 0.42, 0.9, s=1.15, body="Cloth_VM_Blue")
    # ---------------- INTERIOR: piso de tabuas, teto de tabuas com barrotes, balcao, prateleiras, lustre
    ih, idp = hw - 1.12, hd - 1.12
    xk = -ih
    k = 0
    while xk < ih - 0.1:
        xb = min(ih, xk + 1.25)
        K.bb(mb, FS, xk + 0.03, xb - 0.03, -idp, idp, -0.3, 0.0 + (0.01 if k % 2 else 0.0), K.PLK)
        xk = xb
        k += 1
    K.bb(mb, FS, -ih, ih, -idp, idp, GH - 0.3, GH, K.PLK)
    for yy in K.even(-idp + 0.6, idp - 0.6, 2.4):
        K.bb(mb, FS, -ih, ih, yy - 0.25, yy + 0.25, GH - 0.95, GH - 0.3, K.T)
    for xx in (-6.5, 6.5):
        K.bb(mb, FS, xx - 0.4, xx + 0.4, -idp, idp, GH - 1.4, GH - 0.95, K.T)
    # balcao: Roblox x 74..76 -> y local 0..2; z 37..49 -> x local -6..6 (o vendedor fica atras, em y = -2)
    K.bb(mb, FS, -6.2, 6.2, -0.15, 2.25, 3.2, 3.55, K.PLK)
    K.bb(mb, FS, -6.0, 6.0, 0.1, 1.9, 0.0, 0.35, K.T)
    for xx in (-5.85, -2.0, 2.0, 5.85):
        K.bb(mb, FS, xx - 0.25, xx + 0.25, 1.6, 2.1, 0.0, 3.2, K.T)
    for (xa, xb) in ((-5.6, -2.25), (-1.75, 1.75), (2.25, 5.6)):
        K.bb(mb, FS, xa, xb, 1.7, 1.95, 0.35, 3.1, K.PLK)
    for s in (-1, 1):
        K.bb(mb, FS, s * 6.0 - 0.15, s * 6.0 + 0.15, 0.1, 1.9, 0.0, 3.2, K.PLK)
    backpack(mb, FS, -3.6, 1.0, 3.55, s=0.8, body="Cloth_VM_Blue", a=0.4)
    # estante dos fundos (Roblox x ~88) e estantes laterais com mochilas
    yb0 = -idp
    for xx in (-10.0, -5.0, 0.0, 5.0, 10.0):
        K.bb(mb, FS, xx - 0.25, xx + 0.25, yb0, yb0 + 1.5, 0.0, 8.6, K.T)
    for zz in (1.0, 3.6, 6.2):
        K.bb(mb, FS, -10.2, 10.2, yb0, yb0 + 1.45, zz - 0.18, zz, K.PLK)
    r = K.rng("shopbp")
    for zz in (1.0, 3.6, 6.2):
        for xx in (-7.5, -2.5, 2.5, 7.5):
            if r.random() < 0.8:
                backpack(mb, FS, xx + r.uniform(-0.6, 0.6), yb0 + 0.7, zz, s=r.uniform(0.85, 1.1),
                         body=bodies[int(r.random() * 3) % 3], a=r.uniform(-0.2, 0.2))
    for sg in (-1, 1):
        Fsd = K.sub(FS, sg * (ih - 0.7), 0.0, 0.0, -sg * math.pi / 2)   # +y local = para o meio da loja
        Fsd = K.sub(Fsd, 0.0, 0.0, 0.0, math.pi)
        for zz in (2.2, 4.8):
            K.bb(mb, Fsd, -5.5, 5.5, -0.7, 0.7, zz - 0.18, zz, K.PLK)
        for xx in (-5.3, 5.3):
            K.bb(mb, Fsd, xx - 0.2, xx + 0.2, -0.7, 0.7, 0.0, 6.6, K.T)
        for j, xx in enumerate((-3.5, 0.0, 3.5)):
            backpack(mb, Fsd, xx, 0.0, 4.8, s=0.95, body=bodies[(j + (sg > 0)) % 3])
            backpack(mb, Fsd, xx + 1.6, 0.0, 2.2, s=0.9, body=bodies[(j + 1) % 3])
    # lustre de ferro (madeira escura no Roblox) com 4 lanternas
    Fl = K.sub(FS, 0.0, 4.0, GH - 3.0)
    mb.cyl(2.2, 0.25, Fl.p(0, 0, 0), Fl.r(), K.T, 10, bevel=0.0)
    for k in range(4):
        a = k * math.pi / 2 + math.pi / 4
        p = Fl.p(math.cos(a) * 2.2, math.sin(a) * 2.2, 0.0)
        mb.rod(p, Fl.p(0, 0, 2.7), 0.06, K.T, 4)
        mb.box((0.55, 0.55, 0.8), (p.x, p.y, p.z + 0.5), (0, 0, 0), K.GLASS_LAMP, 0.0)
    ob = mb.finish()
    ob["vm_town"] = 1
    for nm, yy in (("A", 6.0), ("B", -6.0)):
        p = FS.p(0.0, yy, GH - 2.6)
        fm_lib.light("L_VM_ShopIn_" + nm, "POINT", p, 90.0, (1.0, 0.82, 0.6), 0.4)
        DAY_LIGHTS.append("L_VM_ShopIn_" + nm)
    # toldo listrado sobre porta e vitrines (enfeites)
    K.awning(dmb, Ff, -hw + 0.6, hw - 0.6, GH - 0.25, depth=2.4, drop=1.0)
    K.hanging_sign(dmb, sides["F"][0], hw - 0.9, GH + 1.6, out=2.4, emblem="pack")
    # ---------------- colisao (vao da porta 6 x 9)
    H = SHOP_GH + 0.2
    VL.colr("Shop", (x0, y0, z0), (x0 + 1.0, y0 + H, 40.0))
    VL.colr("Shop", (x0, y0, 46.0), (x0 + 1.0, y0 + H, z1))
    VL.colr("Shop", (x0, y0 + 9.0, 40.0), (x0 + 1.0, y0 + H, 46.0))
    VL.colr("Shop", (x0, y0, z0), (x1, y0 + H, z0 + 1.0))
    VL.colr("Shop", (x0, y0, z1 - 1.0), (x1, y0 + H, z1))
    VL.colr("Shop", (x1 - 1.0, y0, z0), (x1, y0 + H, z1))
    VL.colr("Shop", (x0, y0 + SHOP_GH - 0.3, z0), (x1, y0 + SHOP_GH + SHOP_FH, z1))           # forro / andar
    VL.colr("Shop", (74.0, y0, 36.8), (76.25, y0 + 3.55, 49.2))                                # balcao
    VL.colr("Shop", (x1 - 2.62, y0, 32.8), (x1 - 1.0, y0 + 8.6, 53.2))                         # estante fundos
    for zc in (43.0 - (ih - 0.7), 43.0 + (ih - 0.7)):
        VL.colr("Shop", (70.5, y0, zc - 0.7), (81.5, y0 + 6.6, zc + 0.7))                     # estantes laterais
    for zc in (43.0 - VC, 43.0 + VC):
        VL.colr("Shop", (x0 - 1.5, Y, zc - 2.85), (x0, y0 + 6.5, zc + 2.85))                  # vitrines


# ================================================================== RANKING (palco + salao da guilda)
def rank_frame():
    ox, oz = L.RANK_O
    fx, fz = L.RANK_FACE
    n = math.hypot(fx, fz)
    return ox, oz, fx / n, fz / n


def ranking(dress):
    ox, oz, fx, fz = rank_frame()
    TF = K.frame_r(ox, oz, L.Y_RANK, fx, fz)          # +y = visitantes, +x = tangente (o GlobalTop100 fica em y 0..12,4)
    mb = MB("VM_Rank_Stage", "05_SERVICES", detail="far", floor=-999)
    # palco: miolo, laje de topo (6,4) sob os quadros, faixa de lajes na frente, borda de cantaria
    K.bb(mb, TF, -29.0, 29.0, -3.0, 17.0, -0.75, -0.42, K.MOR)
    K.bb(mb, TF, -28.6, 28.6, -2.6, 13.0, -0.42, 0.0, "Stone_VM_Trim")
    K.bb(mb, TF, -28.6, 28.6, 12.9, 16.2, -0.42, -0.2, K.PAVE_J)
    r = K.rng("stage")
    y = 13.0
    while y < 16.0:
        y2 = min(16.1, y + 1.55)
        x = -28.6 + (0.9 if r.random() < 0.5 else 0.0)
        xs = [-28.6] + ([x] if x > -28.4 else [])
        while xs[-1] < 28.4:
            xs.append(min(28.6, xs[-1] + r.uniform(2.2, 3.2)))
        for xa, xb in zip(xs, xs[1:]):
            q = [(xa + 0.06, y + 0.06), (xb - 0.06, y + 0.06), (xb - 0.06, y2 - 0.06), (xa + 0.06, y2 - 0.06)]
            pts = [tuple(TF.p(a, b, 0))[:2] for a, b in q]
            K.cobble(mb, F0, pts, lambda qx, qy: L.Y_RANK - 0.03, "Stone_Paving_VM_Edge" if r.random() < 0.4
                     else "Stone_VM_Trim", c1=0.07, c2=0.2)
        y = y2
    for (xa, xb, ya, yb) in ((-29.6, 29.6, 16.1, 17.4), (-29.6, -28.4, -3.2, 16.1), (28.4, 29.6, -3.2, 16.1)):
        horiz = (xb - xa) > (yb - ya)
        a, b = (xa, xb) if horiz else (ya, yb)
        xx = a
        while xx < b - 0.2:
            x2 = min(b, xx + r.uniform(2.0, 3.0))
            if b - x2 < 1.0:
                x2 = b
            if horiz:
                K.through_stone(mb, TF, xx + 0.04, x2 - 0.04, ya, yb, -0.8, 0.05, "Stone_VM_Warm", c=0.12)
            else:
                K.through_stone(mb, TF, xa, xb, xx + 0.04, x2 - 0.04, -0.8, 0.05, "Stone_VM_Warm", c=0.12)
            xx = x2
    # mastros com estandartes azuis (trofeu em relevo)
    for s in (-1, 1):
        xm = s * 30.6
        K.through_stone(mb, TF, xm - 0.9, xm + 0.9, 13.1, 14.9, -0.6, 0.9, "Stone_VM_Warm", c=0.14)
        K.bb(mb, TF, xm - 0.42, xm + 0.42, 13.58, 14.42, 0.9, 21.5, K.T)
        mb.ico(0.55, TF.p(xm, 14.0, 21.9), K.BRONZE, 1)
        K.bb(mb, TF, xm - 2.9, xm + 2.9, 13.7, 14.3, 19.4, 19.8, K.T)
        K.ext(mb, TF, [(xm - 2.5, 19.4), (xm + 2.5, 19.4), (xm + 2.5, 8.6), (xm, 10.2), (xm - 2.5, 8.6)], "y", 14.32,
              14.52, "Cloth_VM_Blue")
        cup = [(xm - 1.1, 17.6), (xm + 1.1, 17.6), (xm + 0.7, 15.9), (xm + 0.25, 15.4), (xm - 0.25, 15.4),
               (xm - 0.7, 15.9)]
        K.ext(mb, TF, cup, "y", 14.5, 14.62, K.BRONZE)
        K.ext(mb, TF, [(xm - 0.25, 15.45), (xm + 0.25, 15.45), (xm + 0.25, 14.4), (xm - 0.25, 14.4)], "y", 14.5,
              14.62, K.BRONZE)
        K.ext(mb, TF, [(xm - 0.9, 14.45), (xm + 0.9, 14.45), (xm + 0.9, 13.9), (xm - 0.9, 13.9)], "y", 14.5, 14.62,
              K.BRONZE)
        p = TF.p(xm, 14.0, 0.0)
        VL.colr("RankMast", (p.x - 1.0, Y, -p.y - 1.0), (p.x + 1.0, L.Y_RANK + 21.5, -p.y + 1.0))
    for s, nm in ((-1, "R1"), (1, "R2")):                 # postes nas pontas do palco
        p = TF.p(s * 27.0, 19.2, 0.0)
        lamp(mb, nm, p.x, -p.y, Y, 9.6, (fx, fz))
    ob = mb.finish()
    ob["vm_town"] = 1
    # SALAO DA GUILDA enxaimel atras dos quadros (frente + balancos + beiral antes de y -1,2: envoltoria livre)
    hm = MB("VM_Rank_Hall", "05_SERVICES", detail="far", floor=-999)
    sp = K.spec_of("A3", seed="V2_Hall", W=30.0, D=10.0, floors=3, gh=8.0, dormers=1, plaster="Plaster_VM_Ochre",
                   stone="Stone_VM_Warm", roof=("Roof_VM_Terracotta_B", "Roof_VM_Terracotta"), lod=2, flowers="red")
    cy = -9.7
    Fh = K.frame_r(ox + fx * cy, oz + fz * cy, Y, fx, fz)
    info = K.house(hm, Fh, sp, dmb=dress["W"])
    K.house_col("RankHall", Fh, sp, info)
    hm.finish()["vm_town"] = 1


# ================================================================== PATIO DOS PORTAIS (portais aprovados intocados)
COURT_ENTRY = (-9.5, 13.0)        # angulo do centro da entrada (graus) e meia abertura do arco


def court(dress):
    cx, cz = L.COURT_C
    r0, r1, a0, a1 = L.COURT_RING
    mb = MB("VM_Court_Floor", "06_PORTALS", detail="far", floor=-999)
    r = K.rng("court")
    # disco de lajes em aneis (2 tons alternando) + rosa dos ventos no centro
    rings = [(4.6, 10.0), (10.0, 16.4), (16.4, 22.8), (22.8, 29.2), (29.2, 35.0), (35.0, 39.9)]
    ztop = PLAZA_TOP + 0.04
    for i, (ra, rb) in enumerate(rings):
        n = max(8, int(math.ceil(2 * math.pi * rb / 7.4)))
        off = r.uniform(0, 1)
        for j in range(n):
            ta = 2 * math.pi * (j + off) / n + 0.06 / rb
            tb = 2 * math.pi * (j + 1 + off) / n - 0.06 / rb
            q = [(cx + (ra + 0.06) * math.cos(ta), cz + (ra + 0.06) * math.sin(ta)),
                 (cx + (rb - 0.06) * math.cos(ta), cz + (rb - 0.06) * math.sin(ta)),
                 (cx + (rb - 0.06) * math.cos(tb), cz + (rb - 0.06) * math.sin(tb)),
                 (cx + (ra + 0.06) * math.cos(tb), cz + (ra + 0.06) * math.sin(tb))]
            m = "Stone_VM_Trim" if (i + j) % 2 == 0 else "Stone_Paving_VM_Edge"
            K.cobble(mb, F0, [(x, -z) for x, z in q], lambda qx, qy, d=r.uniform(-0.02, 0.02): ztop + d, m,
                     c1=0.07, c2=0.2)
    VL.slab(mb, VL.circle_r(cx, cz, 4.6, 24), BED_P - 0.3, ztop + 0.02, "Stone_VM_Trim")
    star = []
    for k in range(16):
        rr_ = 4.2 if k % 2 == 0 else 1.5
        a = math.pi * k / 8 + math.pi / 2
        star.append((cx + rr_ * math.cos(a), cz + rr_ * math.sin(a)))
    VL.slab(mb, star, ztop, ztop + 0.15, K.BRONZE)
    VL.slab(mb, VL.circle_r(cx, cz, 39.95, 72), BED_P - 0.3, BED_P, K.PAVE_J)
    # degrau (6,6) e frente do terraco (7,2) em cantaria, lajes do terraco, faixa de grama atras dos portais,
    # mureta externa (r 74)
    stone_row(mb, arc_path(cx, cz, r0 + 0.5, a0, a1, 1.0), 0.0, 1.0, L.Y_GRASS, L.Y_PORTAL - 0.6 - L.Y_GRASS,
              "cstep", m="Stone_VM_Trim", ln=(3.2, 4.4))
    stone_row(mb, arc_path(cx, cz, r0 + 1.5, a0, a1, 1.0), 0.0, 1.0, L.Y_GRASS, L.Y_PORTAL - L.Y_GRASS + 0.02,
              "criser", m="Stone_VM_Warm", ln=(4.2, 5.4))
    VL.slab(mb, VL.sector_r(cx, cz, r0 + 1.95, 69.0, a0, a1, 64), L.Y_GRASS - 0.4, L.Y_PORTAL, "Stone_Paving_VM_Edge")
    VL.slab(mb, VL.sector_r(cx, cz, 69.0, r1 - 0.9, a0, a1, 64), L.Y_GRASS - 0.4, L.Y_PORTAL, "Grass_VM")
    VL.slab(mb, VL.sector_r(cx, cz, r1 - 0.95, r1 + 0.05, a0 - 1.0, a1 + 1.0, 64), L.Y_GRASS - 0.5,
            L.Y_PORTAL + 0.95, "Stone_VM_Warm")
    VL.slab(mb, VL.sector_r(cx, cz, r1 - 1.15, r1 + 0.25, a0 - 1.2, a1 + 1.2, 64), L.Y_PORTAL + 0.95,
            L.Y_PORTAL + 1.3, "Stone_VM_Trim")
    for a in (a0, a1):                                  # pontas do terraco (paredes radiais)
        rad = math.radians(a)
        p = Path([(cx + math.cos(rad) * (r0 + 1.0), cz + math.sin(rad) * (r0 + 1.0)),
                  (cx + math.cos(rad) * r1, cz + math.sin(rad) * r1)])
        stone_row(mb, p, 0.0, 1.0, L.Y_GRASS - 0.3, L.Y_PORTAL - L.Y_GRASS + 1.2, ("cend", a), m="Stone_VM_Warm",
                  ln=(2.2, 3.2))
    # mureta baixa no lado leste do disco (abre na entrada do arco)
    e0, e1 = COURT_ENTRY[0] - COURT_ENTRY[1], COURT_ENTRY[0] + COURT_ENTRY[1]
    # (a ponta oeste da envoltoria do GlobalTop100 entra no disco entre -72 e -40 graus: ali nao ha mureta)
    for (b0, b1) in ((-85.0, -75.0), (-38.0, e0 - 1.2), (e1 + 1.2, 85.0)):
        p = arc_path(cx, cz, r0 + 0.5, b0, b1, 1.0)
        stone_row(mb, p, 0.0, 0.95, Y - 0.2, 0.75, ("cm", b0), m="Stone_VM_Warm", ln=(2.6, 3.4))
        stone_row(mb, p, 0.0, 1.2, Y + 0.55, 0.3, ("cmc", b0), m="Stone_VM_Trim", ln=(2.4, 3.2))
        span = math.radians(b1 - b0) * (r0 + 0.5)
        nseg = max(1, int(span / 6.0) + 1)
        for j in range(nseg):
            c0 = math.radians(b0 + (b1 - b0) * j / nseg)
            c1 = math.radians(b0 + (b1 - b0) * (j + 1) / nseg)
            cm = (c0 + c1) / 2
            ln = 2 * (r0 + 0.5) * math.sin((c1 - c0) / 2)
            VL.colr_rot("CourtWall", cx + math.cos(cm) * (r0 + 0.5), cz + math.sin(cm) * (r0 + 0.5), Y + 0.6, ln,
                        1.2, 1.2, -math.sin(cm), math.cos(cm))
    # postes entre os portais (borda do disco) e bancos olhando os portais
    pm = mb
    for k in range(7):
        b = math.radians(180.0 + (k - 3.0) * L.PORTAL_STEP_DEG)
        if k in (0, 6):
            continue
        lamp(pm, "C%d" % k, cx + math.cos(b) * 38.2, cz + math.sin(b) * 38.2, PLAZA_TOP, 9.6,
             (-math.cos(b), -math.sin(b)))
        if 0 < k < 6:
            bx_, bz_ = cx + math.cos(b) * 30.0, cz + math.sin(b) * 30.0
            bench(pm, K.frame_r(bx_, bz_, PLAZA_TOP, math.cos(b), math.sin(b)), 4.4, seed=("cb", k))
            VL.colr_rot("CourtBench", bx_, bz_, Y + 0.8, 4.4, 1.8, 1.6, -math.sin(b), math.cos(b))
    mb.finish()["vm_town"] = 1
    court_arch()
    court_trees()


def court_arch():
    """ARCO de pedra discreto na entrada do patio (sobre a rua oeste): 2 pilares de pedra arredondada, arco
    segmentado de aduelas, capa de cantaria e lanterna pendurada na chave"""
    cx, cz = L.COURT_C
    ac, ah = COURT_ENTRY
    ra = L.COURT_RING[0] + 0.5
    P = [(cx + ra * math.cos(math.radians(ac + s * ah)), cz + ra * math.sin(math.radians(ac + s * ah))) for s in (-1, 1)]
    mx, mz = (P[0][0] + P[1][0]) / 2, (P[0][1] + P[1][1]) / 2
    dx, dz = P[1][0] - P[0][0], P[1][1] - P[0][1]
    span = math.hypot(dx, dz)
    ux, uz = dx / span, dz / span
    mb = MB("VM_Court_Arch", "06_PORTALS", detail="far", floor=-999)
    F = K.frame_r(mx, mz, Y, uz, -ux)                 # +x local = (ux, uz): de um pilar ao outro
    pw, H = 2.6, 10.4
    for s in (-1, 1):
        xc = s * span / 2
        K.bb(mb, F, xc - pw / 2 + K.CORE, xc + pw / 2 - K.CORE, -pw / 2 + K.CORE, pw / 2 - K.CORE, -0.3, H, K.MOR)
        for ang in range(4):
            Fp = K.sub(F, xc, 0.0, 0.0, ang * math.pi / 2)
            Ff = K.sub(Fp, 0.0, pw / 2, 0.0, 0.0)
            K.stone_face(mb, Ff, -pw / 2 - 0.1, pw / 2 + 0.1, -0.3, H - 0.6, "Stone_VM_Warm", seed=("arch", s, ang),
                         lod=1)
        K.through_stone(mb, F, xc - pw / 2 - 0.3, xc + pw / 2 + 0.3, -pw / 2 - 0.3, pw / 2 + 0.3, H - 0.65, H + 0.1,
                        "Stone_VM_Trim", c=0.12)
        p = F.p(xc, 0.0, 0.0)
        VL.colr("CourtArch", (p.x - pw / 2, Y, -p.y - pw / 2), (p.x + pw / 2, Y + H + 4.0, -p.y + pw / 2))
    inner = span / 2 - pw / 2
    rise = 3.2
    R = (inner * inner + rise * rise) / (2 * rise)
    zc = H + 0.1 + rise - R
    th0 = math.atan2(H + 0.1 - zc, inner)
    nv = 13
    for i in range(nv):
        t0 = th0 + (math.pi - 2 * th0) * i / nv + 0.01
        t1 = th0 + (math.pi - 2 * th0) * (i + 1) / nv - 0.01
        to = 1.25 + (0.3 if i == nv // 2 else (0.12 if i % 2 else 0.0))
        poly = [(R * math.cos(t0), zc + R * math.sin(t0)), (R * math.cos(t1), zc + R * math.sin(t1)),
                ((R + to) * math.cos(t1), zc + (R + to) * math.sin(t1)), ((R + to) * math.cos(t0), zc + (R + to) * math.sin(t0))]
        K.ext(mb, F, poly, "y", -1.05, 1.05, "Stone_VM_Trim")
    top = H + 0.1 + rise + 1.4
    for s in (-1, 1):                                    # timpanos (pedra escura) entre o arco e a capa
        K.ext(mb, F, [(s * inner, H + 0.1), (s * (span / 2 + pw / 2), H + 0.1), (s * (span / 2 + pw / 2), top),
                      (s * 0.0, top), (0.0, zc + R + 1.2)], "y", -0.9, 0.9, "Stone_VM_Warm")
    xx = -span / 2 - pw / 2 - 0.2
    r = K.rng("archcap")
    while xx < span / 2 + pw / 2 + 0.1:
        x2 = min(span / 2 + pw / 2 + 0.2, xx + r.uniform(1.8, 2.6))
        K.through_stone(mb, F, xx + 0.04, x2 - 0.04, -1.25, 1.25, top - 0.05, top + 0.5, "Stone_VM_Trim", c=0.12)
        xx = x2
    p = K.lantern(mb, K.sub(F, 0.0, 0.0, zc + R - 3.2), 0.0, hh=1.2, w=0.4)
    mb.rod(F.p(0.0, 0.0, zc + R - 1.9), F.p(0.0, 0.0, zc + R), 0.06, K.IRON, 4)
    LAMPS.append(("L_VM_Lamp_Arch", p))
    mb.finish()["vm_town"] = 1


def court_trees():
    """arvores emoldurando o patio: copas redondas entre os portais (atras, na faixa de grama) e pinheiros nas pontas"""
    cx, cz = L.COURT_C
    mb = MB("VM_Veg_Court", "09_VEGETATION", detail="far", floor=-999)
    r = K.rng("ctrees")
    for k in range(7):
        b = math.radians(180.0 + (k - 3.0) * L.PORTAL_STEP_DEG)
        rr_ = 71.2
        VL.tree_round(mb, cx + math.cos(b) * rr_, cz + math.sin(b) * rr_, L.Y_PORTAL, r.uniform(17, 21), r)
    for (x, z, kind) in ((-121.0, 20.0, "p"), (-98.0, 122.0, "p"), (-92.0, 113.0, "r"),
                         (-205.0, 72.0, "p"), (-200.0, 40.0, "p"), (-200.0, 104.0, "p")):
        if kind == "p":
            VL.tree_pine(mb, x, z, L.Y_GRASS, r.uniform(22, 28), r)
        else:
            VL.tree_round(mb, x, z, L.Y_GRASS, r.uniform(15, 19), r)
    mb.finish()


# ================================================================== SAIDA: portao + ponte da Ilha 1
def gate(dress):
    gx, gz = L.GATE
    hw = L.GATE_HW
    mb = MB("VM_Exit_Gate", "07_EXIT", detail="far", floor=-999)
    F = K.frame_r(gx, gz, Y, 0, 1)                   # +y = sul (ilhas), +x = R = (-1, 0) -> oeste
    tw, H = 6.4, 15.0
    for s in (-1, 1):
        xc = s * (hw + 3.2)
        K.bb(mb, F, xc - tw / 2 + K.CORE, xc + tw / 2 - K.CORE, -tw / 2 + K.CORE, tw / 2 - K.CORE, -0.4, H, K.MOR)
        for ang in range(4):
            Fp = K.sub(F, xc, 0.0, 0.0, ang * math.pi / 2)
            Ff = K.sub(Fp, 0.0, tw / 2, 0.0, 0.0)
            holes = [(-0.35, 0.35, 8.0, 10.2)] if ang in (0, 2) else []
            K.stone_face(mb, Ff, -tw / 2 - 0.1, tw / 2 + 0.1, -0.4, H - 0.5, "Stone_VM_Warm", holes,
                         seed=("gate", s, ang), lod=1 if ang == 2 else 2, m2="Stone_VM_Grey", p2=0.3)
            if holes:
                K.bb(mb, Ff, -0.35, 0.35, -K.CORE - 0.2, -K.CORE + 0.1, 8.0, 10.2, K.MOR)
        for ang in range(4):                         # cornija
            Fp = K.sub(F, xc, 0.0, 0.0, ang * math.pi / 2)
            K.through_stone(mb, Fp, -tw / 2 - 0.45, tw / 2 + 0.45, tw / 2 - 0.6, tw / 2 + 0.45, H - 0.6, H + 0.1,
                            "Stone_VM_Trim", c=0.12)
        p = F.p(xc, 0.0, H + 0.1)
        FP.frustum(mb, (p.x, p.y, p.z), tw + 1.6, tw + 1.6, 0.5, 0.5, 8.5, "Roof_VM_Terracotta")
        mb.ico(0.6, F.p(xc, 0.0, H + 8.9), K.BRONZE, 1)
        q = F.p(xc, 0.0, 0.0)
        VL.colr("Gate", (q.x - tw / 2, Y, -q.y - tw / 2), (q.x + tw / 2, Y + H, -q.y + tw / 2))
    # verga de madeira com telhadinho e placa (seta em bronze para o sul / Ilha 1)
    zb = 12.4
    K.bb(mb, F, -hw - 0.2, hw + 0.2, -1.0, 1.0, zb, zb + 1.3, K.T)
    for s in (-1, 1):
        K.beam(mb, F, (s * (hw - 0.1), 0.0, zb - 3.2), (s * (hw - 2.6), 0.0, zb + 0.05), 0.6, 0.6)
    RF = K.sub(F, 0.0, 0.0, zb + 1.3, 0.0)
    ri = K.roof(mb, RF, 2 * hw + 0.4, 2.6, 45.0, 0.7, (0.3, 0.3), "Roof_VM_Terracotta", "Roof_VM_Terracotta_B",
                seed="gateroof", rafters=False, barge=False)
    for g in (-1, 1):
        Fg = K.sub(RF, g * (hw + 0.2), 0.0, 0.0, -g * math.pi / 2)
        K.gable_wall(mb, Fg, 2.6, ri["rise"], "Plaster_VM_Cream", party=True)
    for sy in (1, -1):
        Fs = K.sub(F, 0.0, sy * 1.15, 0.0, 0.0 if sy > 0 else math.pi)
        K.bb(mb, Fs, -3.4, 3.4, -0.1, 0.14, zb - 2.4, zb - 0.1, K.PLK)
        K.ext(mb, Fs, [(-0.32, zb - 2.15), (0.32, zb - 2.15), (0.32, zb - 1.15), (-0.32, zb - 1.15)], "y", 0.14,
              0.26, K.BRONZE)
        K.ext(mb, Fs, [(-0.95, zb - 1.2), (0.95, zb - 1.2), (0.0, zb - 0.3)], "y", 0.14, 0.26, K.BRONZE)
        for xx in (-2.4, 2.4):                       # 2 losangos (as ilhas) dos lados da seta
            K.ext(mb, Fs, [(xx, zb - 1.9), (xx + 0.55, zb - 1.25), (xx, zb - 0.6), (xx - 0.55, zb - 1.25)], "y", 0.14,
                  0.26, K.BRONZE)
    # folhas do portao abertas contra as torres (lado de dentro, fora do tabuleiro)
    for s in (-1, 1):
        Fl = K.sub(F, s * (hw + 0.25), -0.4, 0.0, -s * math.pi / 2)
        for k in range(4):
            K.bb(mb, Fl, -0.6 - k * 1.55, -0.6 - (k + 1) * 1.55 + 0.06, -0.22, 0.0, 0.1, 9.6 - abs(k - 1.5) * 0.12,
                 K.PLK)
        for zz in (1.4, 5.0, 8.4):
            K.bb(mb, Fl, -6.8, -0.6, -0.36, -0.2, zz - 0.25, zz + 0.25, K.T)
        q = Fl.p(-3.7, -0.15, 0.0)
        VL.colr("Gate", (q.x - 0.35, Y, -q.y - 3.2), (q.x + 0.35, Y + 9.6, -q.y + 3.2))
    mb.finish()["vm_town"] = 1
    isle_bridge()


def isle_bridge():
    """ponte de pedra ate a praca de chegada da Vila da Folha: tabuleiro de paralelepipedo SOBRE o mesmo traco da
    colisao do vm_col (polilinha reta), guarda-corpo de pedra com capa, pilares, postes; patamar final na largura da
    praca da ilha (x +-12, z 213..222) com soleira de cantaria em 6,0 exato (encaixe em (0, 6, 222))"""
    P = L.ISLE_BRIDGE[:-1]
    w = L.ISLE_BRIDGE_W
    path = Path(P)
    mb = MB("VM_Exit_Bridge", "07_EXIT", detail="far", floor=-999)
    zt = L.Y_ISLE + 0.04                # pedras ~6,06 (leito 5,9); a soleira final fica em 6,0 exato
    x0, x1, z0, z1 = L.ISLE_LANDING
    keep = lambda x, z: z < z0 - 0.05 or abs(x) > x1          # o patamar tem lajes proprias
    band(mb, path, -w / 2 + 0.85, w / 2 - 0.85, (2.0, 2.6), (3.0, 4.2), zt, "isle", keep=keep)
    band_bed(mb, path, -w / 2 + 0.8, w / 2 - 0.8, L.Y_ISLE - 0.1, step=3.0, thick=0.5)
    VL.slab(mb, VL.ribbon_r(P, w + 2.4), L.Y_ISLE - 3.4, L.Y_ISLE - 0.6, "Stone_VM_Base")
    for s in (-1, 1):
        edge = [path.pt(sv, s * (w / 2 - 0.15)) for sv in path.S]
        VL.slab(mb, VL.ribbon_r(edge, 1.0), L.Y_ISLE - 0.6, L.Y_ISLE + 1.12, "Stone_VM_Grey")
        stone_row(mb, path, s * (w / 2 - 0.15), 1.4, L.Y_ISLE + 1.1, 0.32, ("ibc", s), m="Stone_VM_Trim",
                  ln=(2.6, 3.4), s1=path.L - 0.3)
    # patamar
    r = K.rng("landing")
    zz = z0
    while zz < z1 - 1.6:
        z2 = zz + r.uniform(2.2, 2.7)
        if z2 > z1 - 1.6:
            z2 = z1 - 1.6
        xx = x0
        while xx < x1 - 0.2:
            x2 = min(x1, xx + r.uniform(2.4, 3.2))
            if x1 - x2 < 1.2:
                x2 = x1
            q = [(xx + 0.07, zz + 0.07), (x2 - 0.07, zz + 0.07), (x2 - 0.07, z2 - 0.07), (xx + 0.07, z2 - 0.07)]
            K.cobble(mb, F0, [(a, -b) for a, b in q], lambda qx, qy: zt, "Stone_VM_Trim" if r.random() < 0.6 else
                     "Stone_Paving_VM_Edge", c1=0.07, c2=0.2)
            xx = x2
        zz = z2
    xx = x0
    while xx < x1 - 0.2:                              # soleira: topo EXATO em 6,0 ate z 222
        x2 = min(x1, xx + 3.0)
        mb.box2(VL.B(xx + 0.05, z1 - 1.55, L.Y_ISLE - 0.6), VL.B(x2 - 0.05, z1, L.Y_ISLE), "Stone_VM_Trim", 0.0)
        xx = x2
    mb.box2(VL.B(x0, z0, L.Y_ISLE - 0.5), VL.B(x1, z1 - 1.6, L.Y_ISLE - 0.12), K.PAVE_J, 0.0)   # leito ate a soleira
    mb.box2(VL.B(x0 - 1.2, z0, L.Y_ISLE - 3.4), VL.B(x1 + 1.2, z1, L.Y_ISLE - 0.5), "Stone_VM_Base", 0.0)
    for s in (-1, 1):
        pl = Path([(s * (x1 + 0.6), z0 - 0.4), (s * (x1 + 0.6), z1)])
        stone_row(mb, pl, 0.0, 1.1, L.Y_ISLE - 0.4, 1.55, ("lp", s), m="Stone_VM_Grey", ln=(2.4, 3.2))
        stone_row(mb, pl, 0.0, 1.4, L.Y_ISLE + 1.1, 0.32, ("lc", s), m="Stone_VM_Trim", ln=(1.8, 2.4))
        pn = Path([(s * 8.0, z0 + 0.0), (s * (x1 + 0.6), z0 + 0.0)])
        stone_row(mb, pn, 0.0, 1.1, L.Y_ISLE - 0.4, 1.55, ("ln", s), m="Stone_VM_Grey", ln=(1.5, 2.2))
        VL.colr("IsleNotch", (min(s * 8.4, s * 12.0), L.Y_ISLE, z0 - 0.6), (max(s * 8.4, s * 12.0), L.Y_ISLE + 6.0,
                                                                               z0 + 0.5))
    # pilares de apoio nos vertices
    for i, (x, z) in enumerate(P[1:], 1):
        p = VL.B(x, z, 0)
        mb.box((7.0, 7.0, 40.0), (p.x, p.y, L.Y_ISLE - 3.4 - 20.0), (0, 0, 0), "Stone_VM_Base", 0.0)
        mb.box((8.2, 8.2, 1.2), (p.x, p.y, L.Y_ISLE - 3.8), (0, 0, 0), "Stone_VM_Trim", 0.0)
        mb.box((5.0, 5.0, 16.0), (p.x, p.y, L.Y_ISLE - 3.4 - 48.0), (0, 0, 0), "Stone_VM_Dark", 0.0)
    # postes sobre o guarda-corpo
    pm = mb
    for k, (s, t) in enumerate(((14.0, -1), (14.0, 1), (path.L - 3.0, -1), (path.L - 3.0, 1))):
        x, z = path.pt(s, t * (w / 2 - 0.15))
        F = K.frame_r(x, z, L.Y_ISLE + 1.42, 0, 1)
        p = lamp_lite(pm, F, h=6.8, stone="Stone_VM_Trim")
        LAMPS.append(("L_VM_Lamp_I%d" % (k + 1), p))
    mb.finish()["vm_town"] = 1


# ================================================================== CANAL: muros alem de x +-30 + pontezinhas
FOOT_X = (-116.0, 100.0)          # pontezinhas de pedra (andaveis)
FOOT_HW = 2.6


def canal():
    z0, z1 = L.CANAL_Z                 # agua -18 .. -6
    xa, xb = L.CANAL_X
    mb = MB("VM_Ter_Canal2", "02_TERRAIN", detail="far", floor=-999)
    gapsF = [(fx_ - FOOT_HW - 0.4, fx_ + FOOT_HW + 0.4) for fx_ in FOOT_X]

    def spans(a, b, extra=()):
        cuts = sorted([g for g in gapsF + list(extra) if g[1] > a and g[0] < b])
        out, x = [], a
        for g0, g1 in cuts:
            if g0 > x + 0.5:
                out.append((x, g0))
            x = max(x, g1)
        if b > x + 0.5:
            out.append((x, b))
        return out
    south = spans(xa - 0.5, -30.0) + spans(30.0, xb + 0.5)
    north = spans(xa - 0.5, -30.0) + spans(30.0, xb + 0.5, extra=[(32.0, 40.0)])
    for side, segs, zf, nz, ytop in (("S", south, z1, -1, L.Y_PAVE), ("N", north, z0, 1, L.Y_NORTH)):
        for (a, b) in segs:
            xm, ln = (a + b) / 2, b - a
            Ff = K.frame_r(xm, zf, 0.0, 0, nz)          # face virada para a agua
            K.stone_face(mb, Ff, -ln / 2, ln / 2, 2.0, ytop - 0.03, "Stone_VM_Grey", seed=("cn", side, a), lod=2,
                         m2="Stone_VM_Warm", p2=0.3)
            K.bb(mb, Ff, -ln / 2, ln / 2, -0.85, -K.CORE, L.Y_CANAL_BED, ytop - 0.02, K.MOR)
            p = Path([(a, zf - nz * 0.5), (b, zf - nz * 0.5)])
            stone_row(mb, p, 0.0, 1.15, ytop - 0.2, 0.92, ("cc", side, a), m="Stone_VM_Trim", ln=(3.4, 4.6))
    mb.finish()["vm_town"] = 1
    # barreiras invisiveis (refeitas: as da V0 nao tinham as pontezinhas)
    bar = 6.0
    for (a, b) in spans(xa, -L.STREET_HW - 2.0) + spans(L.STREET_HW + 2.0, xb):
        VL.colr("Canal", (a, L.Y_PAVE, z1), (b, L.Y_PAVE + bar, z1 + 1.0))
    for (a, b) in spans(xa, -L.STREET_HW - 2.0) + spans(L.STREET_HW + 2.0, L.RACE_X[0] - 1.0) + \
            spans(L.RACE_X[1] + 1.0, xb):
        VL.colr("Canal", (a, L.Y_NORTH, z0 - 1.0), (b, L.Y_NORTH + bar, z0))
    for fx_ in FOOT_X:
        footbridge(fx_)


def footbridge(xc):
    """PONTEZINHA de pedra em arco (5 de largura): rampas 6,0 -> 7,7 -> 7,0, guarda-corpo de pedra com capa"""
    hw = FOOT_HW
    mb = MB("VM_Town_Foot%d" % int(abs(xc)), "03_TOWN", detail="far", floor=-999)
    prof = [(-2.2, L.Y_PAVE), (-6.2, L.Y_PAVE + 0.7), (-12.0, 7.7), (-17.8, L.Y_NORTH + 0.4), (-21.6, L.Y_NORTH)]

    def yz(z):
        if z >= prof[0][0]:
            return prof[0][1]
        for (za, ya), (zb, yb) in zip(prof, prof[1:]):
            if zb <= z <= za:
                return ya + (yb - ya) * (za - z) / (za - zb)
        return prof[-1][1]
    path = Path([(xc, prof[0][0]), (xc, prof[-1][0])])     # anda para -Z (norte)
    band(mb, path, -hw + 0.7, hw - 0.7, (1.2, 1.6), (1.4, 2.0), lambda x, y: yz(-y) - 0.02, ("fb", xc))
    n = 8
    for i in range(n):
        za, zb = prof[0][0] + (prof[-1][0] - prof[0][0]) * i / n, prof[0][0] + (prof[-1][0] - prof[0][0]) * (i + 1) / n
        for s in (-1, 1):
            Fp = K.frame_r(xc + s * (hw - 0.35), (za + zb) / 2, 0.0, s, 0)
            a, b = min(za, zb), max(za, zb)
            ya, yb = yz(a), yz(b)
            ym = (ya + yb) / 2
            K.through_stone(mb, Fp, -(b - a) / 2 - 0.02, (b - a) / 2 + 0.02, -0.4, 0.4, ym - 0.8, ym + 1.25,
                            "Stone_VM_Grey", c=0.12)
            K.through_stone(mb, Fp, -(b - a) / 2 - 0.02, (b - a) / 2 + 0.02, -0.55, 0.55, ym + 1.2, ym + 1.5,
                            "Stone_VM_Trim", c=0.1)
        K.ext(mb, F0, [(-(za), yz(za) - 0.9), (-(zb), yz(zb) - 0.9), (-(zb), yz(zb) - 0.1), (-(za), yz(za) - 0.1)],
              "x", xc - hw + 0.65, xc + hw - 0.65, K.PAVE_J)
    # arco: aduelas nas 2 faces + abobada escura + timpanos
    zc_, half = -12.0, 6.0
    spring, crown = 3.2, 6.0
    rise = crown - spring
    R = (half * half + rise * rise) / (2 * rise)
    yc0 = crown - R
    th0 = math.atan2(spring - yc0, half)
    for s in (-1, 1):
        Fs = K.frame_r(xc + s * hw, zc_, 0.0, s, 0)     # +x local = R = (0, s) -> eixo Z (sinal conforme o lado)
        for i in range(9):
            t0 = th0 + (math.pi - 2 * th0) * i / 9 + 0.01
            t1 = th0 + (math.pi - 2 * th0) * (i + 1) / 9 - 0.01
            poly = [(R * math.cos(t0), yc0 + R * math.sin(t0)), (R * math.cos(t1), yc0 + R * math.sin(t1)),
                    ((R + 0.9) * math.cos(t1), yc0 + (R + 0.9) * math.sin(t1)),
                    ((R + 0.9) * math.cos(t0), yc0 + (R + 0.9) * math.sin(t0))]
            K.ext(mb, Fs, poly, "y", -0.7, 0.12, "Stone_VM_Trim")
        for u0, u1 in ((-9.6, -half), (half, 9.6)):
            K.ext(mb, Fs, [(u0, L.Y_CANAL_BED), (u1, L.Y_CANAL_BED), (u1, yz(zc_ + u1 * s) - 0.8),
                           (u0, yz(zc_ + u0 * s) - 0.8)], "y", -0.6, 0.05, "Stone_VM_Grey")
        us = [-half + 2 * half * k / 8 for k in range(9)]
        for ua, ub in zip(us, us[1:]):
            ya = yc0 + math.sqrt(max(0.0, (R + 0.85) ** 2 - ua * ua))
            yb = yc0 + math.sqrt(max(0.0, (R + 0.85) ** 2 - ub * ub))
            K.ext(mb, Fs, [(ua, ya), (ub, yb), (ub, yz(zc_ + ub * s) - 0.8), (ua, yz(zc_ + ua * s) - 0.8)], "y", -0.6,
                  0.0, "Stone_VM_Grey")
    for i in range(10):
        t0 = th0 + (math.pi - 2 * th0) * i / 10
        t1 = th0 + (math.pi - 2 * th0) * (i + 1) / 10
        poly = [(-(zc_ + R * math.cos(t0)), yc0 + R * math.sin(t0)), (-(zc_ + R * math.cos(t1)), yc0 + R * math.sin(t1)),
                (-(zc_ + (R + 0.6) * math.cos(t1)), yc0 + (R + 0.6) * math.sin(t1)),
                (-(zc_ + (R + 0.6) * math.cos(t0)), yc0 + (R + 0.6) * math.sin(t0))]
        K.ext(mb, F0, poly, "x", xc - hw + 0.75, xc + hw - 0.75, "Stone_VM_Dark")
    mb.finish()["vm_town"] = 1
    # colisao: 2 rampas + guarda-corpos
    a = VL.B(xc, prof[0][0] + 0.6, L.Y_PAVE)
    b = VL.B(xc, -12.0, 7.7)
    c = VL.B(xc, prof[-1][0] - 0.6, L.Y_NORTH)
    fm_lib.col_ramp("Foot", a, b, 2 * hw - 1.2, thick=1.0)
    fm_lib.col_ramp("Foot", b, c, 2 * hw - 1.2, thick=1.0)
    for s in (-1, 1):
        VL.colr("FootBar", (xc + s * (hw - 0.7) - 0.4, L.Y_PAVE, prof[-1][0]), (xc + s * (hw - 0.7) + 0.4, 13.5,
                                                                                  prof[0][0]))


# ================================================================== BUILD
DRESS_MERGE = {"Metal_VM_Iron": "Wood_VM_Timber", "Metal_VM_Bronze": "Wood_VM_Timber"}


def build():
    LAMPS.clear()
    DAY_LIGHTS.clear()
    STATS.clear()
    clear_v0()
    dress = {k: MB("VM_Town_Dress%s" % k, "03_TOWN", detail="far", floor=-999) for k in ("W", "E", "S")}
    houses(dress)
    plaza()
    plaza_border(dress["W"])
    spawn_terrace(dress["W"])
    streets(dress)
    shop(dress)
    ranking(dress)
    court(dress)
    gate(dress)
    canal()
    for k, d in dress.items():
        ob = d.finish()
        if ob is None:
            continue
        fl = K.FLOWERS[FLOWER[k]]
        mp = dict(DRESS_MERGE)
        for f in K.FLOWERS.values():
            if f != fl:
                mp[f] = fl
        merge_mats(ob, mp)
        ob["vm_town"] = 1
    # pendencia V1: enfeites do trecho (9 MeshParts) -> 1 cor de flor, ferragens na madeira
    td = bpy.data.objects.get("VM_Town_TDress")
    if td is not None:
        mp = dict(DRESS_MERGE)
        mp.update({"Flower_VM_Yellow": "Flower_VM_Red", "Flower_VM_Pink": "Flower_VM_Red"})
        merge_mats(td, mp)
    for nm, p in LAMPS:
        fm_lib.light(nm, "POINT", p, 60.0, (1.0, 0.74, 0.42), 0.3)
    # arvores do blockout que caem nas construcoes novas
    boxes = [(-110.0, 75.0, -8.0, 150.0)]                    # vila inteira (o V3 refaz a vegetacao da vila)
    circles = [(L.COURT_C[0], L.COURT_C[1], 80.0)]
    STATS["arvores_fora"] = drop_trees(boxes, circles)
    scale_dummies()
    bpy.context.view_layer.update()
    return report(print_=True)


def scale_dummies():
    for n, x, z, y, fx, fz in (("SCALE_V2_Loja", 68.0, 41.0, L.Y_SHOP, 1, 0.2),
                               ("SCALE_V2_Balcao", 78.0, 43.0, L.Y_SHOP, -1, 0),
                               ("SCALE_V2_Escada", 4.0, 84.0, Y + 2.88, 0, -1),
                               ("SCALE_V2_RuaSaida", 44.0, 112.0, Y, -0.3, -1),
                               ("SCALE_V2_Adro", -70.0, 44.0, Y, -0.4, -0.9),
                               ("SCALE_V2_Arco", -92.0, 66.0, Y, -1, 0),
                               ("SCALE_V2_Ponte", 30.0, 196.0, L.Y_ISLE, -0.6, 0.8)):
        VL.dummy(n, x, z, y, fx, fz)


# ================================================================== cameras (Roblox: pos, alvo, lente)
def cams():
    E = L.EYE
    c = {}
    c["CAM_VM_V2_SpawnPraca"] = ((0.0, L.Y_SPAWN + E + 1.5, 106.0), (0.0, 14.0, 20.0), 20)
    c["CAM_VM_V2_PracaForja"] = ((3.0, Y + E, 58.0), (-1.0, 22.0, -60.0), 20)
    c["CAM_VM_V2_RuaForja"] = ((2.0, Y + E, 6.0), (-1.0, 20.0, -62.0), 22)
    for k, a in enumerate((0, 90, 180, 270)):
        r_ = math.radians(a)
        p = (PCX + math.cos(r_) * 6.0, Y + E, PCZ + math.sin(r_) * 6.0)
        t = (PCX + math.cos(r_) * 60.0, 13.0, PCZ + math.sin(r_) * 60.0)
        c["CAM_VM_V2_Praca360_%d" % k] = (p, t, 16)
    c["CAM_VM_V2_LojaFora"] = ((35.0, Y + E, 44.0), (76.0, 15.0, 42.5), 17)
    c["CAM_VM_V2_LojaDentro"] = ((65.0, L.Y_SHOP + 5.6, 47.5), (86.0, 9.0, 40.0), 15)
    c["CAM_VM_V2_Ranking"] = ((-58.0, Y + E, 54.0), (-86.0, 17.0, 16.0), 18)
    c["CAM_VM_V2_Portais"] = ((-80.0, Y + E, 66.0), (-170.0, 18.0, 74.0), 16)
    c["CAM_VM_V2_PortaisDentro"] = ((-118.0, Y + E, 72.0), (-180.0, 20.0, 72.0), 14)
    c["CAM_VM_V2_RuaSaida"] = ((28.0, Y + E, 76.0), (52.0, 12.0, 140.0), 18)
    c["CAM_VM_V2_Portao"] = ((48.0, Y + E, 126.0), (50.0, 12.0, 160.0), 20)
    c["CAM_VM_V2_Ponte"] = ((50.0, L.Y_ISLE + E, 150.0), (8.0, 8.0, 214.0), 18)
    c["CAM_VM_V2_Canal"] = ((7.5, L.BRIDGE_CROWN + E, -12.0), (90.0, 6.0, -11.0), 18)
    c["CAM_VM_V2_CanalOeste"] = ((-7.5, L.BRIDGE_CROWN + E, -12.0), (-95.0, 6.0, -11.0), 18)
    c["CAM_VM_V2_Ref01"] = ((53.0, Y + 7.0, 140.0), (30.0, Y + 14.0, 64.0), 20)
    c["CAM_VM_V2_Air_SE"] = ((150.0, 110.0, 190.0), (-10.0, 0.0, 40.0), 24)
    c["CAM_VM_V2_Air_W"] = ((-230.0, 95.0, 150.0), (-60.0, 0.0, 40.0), 24)
    return c


def cameras():
    for n, (loc, tgt, lens) in cams().items():
        fm_lib.camera(n, VL.B(loc[0], loc[2], loc[1]), VL.B(tgt[0], tgt[2], tgt[1]), lens)


# ================================================================== relatorio (orcamento da vila)
def _tris(o):
    return sum(len(p.vertices) - 2 for p in o.data.polygons)


def report(print_=True, path=None):
    rows = {}
    for o in sorted(bpy.data.objects, key=lambda o: o.name):
        if o.type != "MESH" or not o.name.startswith("VM_") or not (o.get("vm_town") or o.get("vm_trecho") or
                                                                    o.name.startswith(("VM_Town_Dress", "VM_Mail_",
                                                                                       "VM_Town_Plaza", "VM_Town_Spawn",
                                                                                       "VM_Town_Road", "VM_Town_Street",
                                                                                       "VM_Town_Edges2", "VM_Exit_",
                                                                                       "VM_Court_", "VM_Rank_",
                                                                                       "VM_Veg_Court"))):
            continue
        mats = sorted({o.data.materials[p.material_index].name for p in o.data.polygons}) if o.data.materials else []
        own = "outros"
        for p_, ow in VL.OWNER_PREFIX:
            if o.name.startswith(p_):
                own = ow
                break
        rows[o.name] = {"dono": own, "tris": _tris(o), "materiais": len(mats)}
    own = {}
    for k, v in rows.items():
        t = own.setdefault(v["dono"], [0, 0])
        t[0] += v["tris"]
        t[1] += v["materiais"]
    out = {"objetos": rows, "por_dono": own, "stats": STATS, "luzes_noite": len(LAMPS), "luzes_dia": DAY_LIGHTS}
    if print_:
        print("TOWN objetos (tris / materiais):")
        for k, v in rows.items():
            print("   %-28s %-10s %6d tris %2d mat" % (k, v["dono"], v["tris"], v["materiais"]))
        for k, v in sorted(own.items()):
            print("TOWN dono %-10s %7d tris  ~%3d MeshParts (antes do fold/celulas)" % (k, v[0], v[1]))
        print("TOWN stats", STATS, "lampioes", len(LAMPS))
    if path:
        json.dump(out, open(path, "w", encoding="utf-8"), indent=1)
    return out


if __name__ == "__main__":
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    if argv and argv[0] == "report":
        report(True, argv[1] if len(argv) > 1 else None)
    elif argv and argv[0] == "plan":
        # planta 2D das casas novas sobre a planta aprovada (sem Blender pesado): python fora do blender nao roda
        pass
