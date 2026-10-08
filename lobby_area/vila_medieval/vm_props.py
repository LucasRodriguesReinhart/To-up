# vm_props.py - PROPS da vila do lobby VILA MEDIEVAL (onda V3a): carrocas com roda raiada, barris, caixotes, lenha
# empilhada, vasos e floreiras de terracota, bancos, PLACAS DE DIRECAO de madeira nos cruzamentos (sem texto: icones
# de bigorna, mochila, portal e trofeu em relevo), cestos, varais com tecido, sacos e muretas de pedra seca nos
# arredores. Meta = ref/ref_01_estilo_vila.jpg (a rua viva: carroca, barris, caixotes, lenha, vasos).
#
# Coordenadas ROBLOX (X leste, Z sul, Y cima); Blender = (X, -Z, Y). Deterministico (K.rng / K.h01).
#
# REGRAS (lead, V3a)
#   - nada dentro da envoltoria do Ignis nem do largo da forja (dono V2a); nada nas rotas, portas, escadas, disco dos
#     portais, palco do ranking (envoltoria do Top100): cada prop e SONDADO contra o construido (vm_veg.Probe: todas as
#     malhas do export + volumes de QA + caixas de exclusao), contra as rotas do QA (folga), as portas (folhas de tabua
#     achadas na malha) e os troncos do vm_veg; recusado -> procura ate 3,2 studs em volta; senao fica fora (relatorio);
#   - colisao SO nos props grandes (carroca, lenha, mureta, grupo de barris/caixotes, banco, poste de placa e do varal);
#   - vasos: a terracota e o vaso ficam aqui; as PLANTAS dentro (moita, flores, capim) vao para o objeto de vegetacao
#     da celula (vm_veg) -> o material de folha/flor nao vira MeshPart a mais nos props.
# MATERIAIS: so os existentes (Wood_VM_Plank / Wood_VM_Timber, Roof_VM_Terracotta (vasos), Stone_VM_Grey (mureta),
#   Cloth_VM_Cream / Red / Blue (varal, sacos)). Ferro do kit (aros, cubo da roda) vira madeira escura (merge_mats).
# OBJETOS: 1 por celula (VM_Prop_<col><lin>, mesmas celulas do vm_veg). ORCAMENTO: props <= 25k tris / 25 MeshParts.
#
# uso: o build_vm.py chama vm_props.build() entre vm_veg.build() e vm_veg.after_props(FOOT).
import sys, os, math
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import bpy
from mathutils import Vector
import vm_lib as VL
import vm_layout as L
import fm_lib
from fm_lib import MB, col_box
import vm_kit as K
import vm_veg as VG
from vm_veg import B, h01, cell_of

PLK, T, TERRA, STONE = "Wood_VM_Plank", "Wood_VM_Timber", "Roof_VM_Terracotta", "Stone_VM_Grey"
CREAM, RED, BLUE = "Cloth_VM_Cream", "Cloth_VM_Red", "Cloth_VM_Blue"
MERGE = {"Metal_VM_Iron": T, "Metal_VM_Bronze": T, "Stone_VM_Mortar": T, "Stone_VM_Trim": STONE,
         "Stone_VM_Base": STONE}
FOOT = []            # (x, z, r) pegadas (o vm_veg.after_props nao poe tufo em cima)
STATS = {}
TAU = math.tau


# ================================================================== pecas
def frame(x, z, y, fx, fz):
    return K.frame_r(x, z, y, fx, fz)


def log(mb, F, a, b, r, n=6):
    """tora deitada de a ate b (pontos LOCAIS): casca escura (Timber) + topos claros (Plank) - 4n tris"""
    pa, pb = Vector(F.p(*a)), Vector(F.p(*b))
    d = (pb - pa).normalized()
    up = Vector((0, 0, 1)) if abs(d.z) < 0.9 else Vector((1, 0, 0))
    u = d.cross(up).normalized()
    v = u.cross(d).normalized()
    bm = mb.bm
    ra = [pa + (u * math.cos(TAU * i / n) + v * math.sin(TAU * i / n)) * r for i in range(n)]
    rb = [pb + (u * math.cos(TAU * i / n) + v * math.sin(TAU * i / n)) * r * 0.94 for i in range(n)]
    vs = [bm.verts.new(p) for p in ra + rb]
    VG._faces(mb, vs, [(i, (i + 1) % n, n + (i + 1) % n, n + i) for i in range(n)], T)
    for ring, rev in ((ra, True), (rb, False)):
        vs = [bm.verts.new(p) for p in ring]
        f = list(range(n))
        VG._faces(mb, vs, [tuple(reversed(f)) if rev else tuple(f)], PLK)
    return 4 * n


def woodpile(mb, F, L_=4.2, rows=(4, 3, 2)):
    """LENHA EMPILHADA: toras em fiadas (piramide) entre 2 estacas, sobre 2 calcos"""
    r = K.rng("wood", round(F.o.x, 1), round(F.o.y, 1))
    rad = 0.36
    t = 0
    for sx in (-1, 1):
        K.bb(mb, F, sx * (L_ / 2 - 0.3) - 0.18, sx * (L_ / 2 - 0.3) + 0.18, -1.0, 1.0, 0.0, 0.3, T)
    z = 0.3 + rad
    for k, n in enumerate(rows):
        w = n * rad * 2.05
        for i in range(n):
            y = -w / 2 + rad * 1.02 + i * rad * 2.05
            off = r.uniform(-0.18, 0.18)
            t += log(mb, F, (-L_ / 2 + 0.2 + off, y, z), (L_ / 2 - 0.2 + off, y, z), rad * r.uniform(0.88, 1.08))
        z += rad * 1.75
    for sy in (-1, 1):
        y = sy * (rows[0] * rad * 1.05 + 0.15)
        K.bb(mb, F, -0.12, 0.12, y - 0.12, y + 0.12, -0.3, z + 0.3, T)
    return z


def pot(mb, F, x, y, r=0.75, h=1.25):
    """VASO de terracota (lathe 8 lados: pe, bojo, boca com aba)"""
    prof = [(r * 0.62, 0.0), (r * 0.9, h * 0.3), (r, h * 0.7), (r * 0.9, h * 0.92), (r * 1.08, h * 0.95),
            (r * 1.06, h)]
    K.lathe(mb, F, (x, y, 0.0), prof, 8, TERRA)


def bench(mb, F, L_=4.0):
    """BANCO rustico: tampo de 2 tabuas sobre 2 cavaletes, encosto de 1 tabua"""
    for sx in (-1, 1):
        K.bb(mb, F, sx * (L_ / 2 - 0.5) - 0.2, sx * (L_ / 2 - 0.5) + 0.2, -0.75, 0.75, 0.0, 1.25, T)
        K.bb(mb, F, sx * (L_ / 2 - 0.5) - 0.16, sx * (L_ / 2 - 0.5) + 0.16, -0.95, -0.7, 1.2, 2.9, T)
    for y in (-0.36, 0.36):
        K.bb(mb, F, -L_ / 2, L_ / 2, y - 0.34, y + 0.34, 1.25, 1.5, PLK)
    K.bb(mb, F, -L_ / 2 + 0.1, L_ / 2 - 0.1, -1.0, -0.76, 2.1, 2.8, PLK)


def basket(mb, F, x, y, r=0.7, h=0.8):
    """CESTO de vime (lathe aberto em cima + aro)"""
    K.lathe(mb, F, (x, y, 0.0), [(r * 0.7, 0.0), (r * 0.95, h * 0.5), (r, h)], 8, PLK)
    K.lathe(mb, F, (x, y, 0.0), [(r + 0.08, h - 0.12), (r + 0.08, h + 0.06)], 8, T)


def sack(mb, F, x, y, z=0.0, s=1.0, m=CREAM, a=0.0):
    """SACO de graos (almofada alta de pano com a boca amarrada)"""
    rng = K.rng("sack", round(F.o.x, 1), round(x, 1), round(y, 1))
    c = Vector(F.p(x, y, z))
    VG.cushion(mb, c, 0.62 * s, 0.5 * s, 1.35 * s, m, m, rng, n=6, rot=a, jit=0.05,
               prof=((0.0, 0.85), (0.4, 1.0), (0.8, 0.55)))


# ------------------------------------------------------------------ PLACA DE DIRECAO (icones em relevo, sem texto)
def _icon(mb, Fb, kind, x0, side):
    """icone em relevo (Timber) na face da tabua: Fb local x = ao longo da seta, y = normal da face, z = altura.
    side = +1 / -1 (face da frente / de tras). Desenho em ~1,1 x 0,8."""
    y0, y1 = (0.14, 0.26) if side > 0 else (-0.26, -0.14)

    def poly(pts):
        K.ext(mb, Fb, [(x0 + px, pz) for px, pz in pts], "y", y0, y1, T)
    if kind == "anvil":          # bigorna: base, cintura, corpo com chifre
        poly([(-0.36, -0.36), (0.36, -0.36), (0.22, -0.22), (-0.22, -0.22)])
        poly([(-0.14, -0.22), (0.14, -0.22), (0.14, 0.02), (-0.14, 0.02)])
        poly([(-0.38, 0.02), (0.30, 0.02), (0.56, 0.16), (0.30, 0.26), (-0.38, 0.26)])
    elif kind == "pack":         # mochila: corpo, aba, bolso, alca de mao
        poly([(-0.3, -0.36), (0.3, -0.36), (0.32, 0.18), (-0.32, 0.18)])
        poly([(-0.34, 0.12), (0.34, 0.12), (0.26, 0.32), (-0.26, 0.32)])
        poly([(-0.1, 0.32), (0.1, 0.32), (0.1, 0.4), (-0.1, 0.4)])
    elif kind == "portal":       # portal: aro octogonal + miolo
        n = 6
        for i in range(n):
            a0, a1 = TAU * i / n, TAU * (i + 1) / n
            ro, ri = 0.38, 0.27
            poly([(ro * math.cos(a0), ro * math.sin(a0)), (ro * math.cos(a1), ro * math.sin(a1)),
                  (ri * math.cos(a1), ri * math.sin(a1)), (ri * math.cos(a0), ri * math.sin(a0))])
        poly([(-0.09, -0.09), (0.09, -0.09), (0.09, 0.09), (-0.09, 0.09)])
    elif kind == "trophy":       # trofeu: taca, alcas, haste, base
        poly([(-0.28, 0.02), (0.28, 0.02), (0.36, 0.38), (-0.36, 0.38)])
        for s in (-1, 1):
            poly([(s * 0.3, 0.12), (s * 0.46, 0.14), (s * 0.46, 0.3), (s * 0.34, 0.3)])
        poly([(-0.06, -0.24), (0.06, -0.24), (0.06, 0.02), (-0.06, 0.02)])
        poly([(-0.26, -0.38), (0.26, -0.38), (0.2, -0.24), (-0.2, -0.24)])


SIGN_H = 7.8
ARROW_L = 3.4


def sign_levels(arrows, h=SIGN_H):
    """setas por NIVEL (de cima para baixo, 1,15 entre niveis): 2 setas dividem o nivel se abrem >= 70 graus. O nivel
    mais baixo tem a borda de baixo a 5,25 do chao (acima da cabeca do avatar de 5,2: nao ha colisao nas setas)."""
    lv = []
    out = []
    for (dx, dz), icon in arrows:
        a = math.degrees(math.atan2(dz, dx))
        for k in range(3):
            if all(abs((a - b + 180.0) % 360.0 - 180.0) >= 70.0 for b in (lv[k] if k < len(lv) else [])):
                if k >= len(lv):
                    lv.append([])
                lv[k].append(a)
                out.append(((dx, dz), icon, h - 0.9 - 1.15 * k))
                break
    return out


def signpost(mb, F, arrows, h=SIGN_H):
    """PLACA DE DIRECAO: poste de madeira com capa, setas de tabua (ponta em V, cauda recortada) apontando o caminho
    e o ICONE do destino em relevo nas 2 faces. arrows = [(direcao Roblox (dx, dz), icone)]."""
    K.bb(mb, F, -0.32, 0.32, -0.32, 0.32, 0.0, h, T)
    mb.cyl(0.55, 0.5, F.p(0, 0, h + 0.2), F.r(0, 0, math.pi / 4), T, 4, r2=0.12, bevel=0.0)
    K.bb(mb, F, -0.55, 0.55, -0.55, 0.55, 0.0, 0.5, STONE)
    for (dx, dz), icon, z in sign_levels(arrows, h):
        yaw = math.atan2(-dz, dx)                 # direcao Roblox -> angulo Blender
        Fb = type(F)(F.o.x, F.o.y, F.o.z, yaw)
        Ln, hb = ARROW_L, 0.5
        outline = [(0.3, -hb), (Ln - 0.55, -hb), (Ln, 0.0), (Ln - 0.55, hb), (0.3, hb), (0.62, 0.0)]
        K.ext(mb, Fb, [(px, z + pz) for px, pz in outline], "y", -0.13, 0.13, PLK)
        _icon(mb, type(F)(F.o.x, F.o.y, F.o.z + z, yaw), icon, 1.75, 1)
        _icon(mb, type(F)(F.o.x, F.o.y, F.o.z + z, yaw), icon, 1.75, -1)


def clothesline(mb, F, L_=9.0, cloths=(CREAM, RED, CREAM, BLUE)):
    """VARAL: 2 postes em T, corda (ripa fina) com barriga, panos pendurados com dobra (2 placas)"""
    r = K.rng("varal", round(F.o.x, 1), round(F.o.y, 1))
    hgt = 5.6
    for sx in (-1, 1):
        x = sx * L_ / 2
        K.bb(mb, F, x - 0.2, x + 0.2, -0.2, 0.2, -0.3, hgt, T)
        K.bb(mb, F, x - 0.15, x + 0.15, -0.8, 0.8, hgt - 0.35, hgt - 0.05, T)
    n = 8
    pts = [(-L_ / 2 + L_ * i / n, 0.0, hgt - 0.45 - 0.55 * math.sin(math.pi * i / n)) for i in range(n + 1)]
    for a, b in zip(pts, pts[1:]):
        K.beam(mb, F, a, b, 0.07, 0.07, T)
    x = -L_ / 2 + 1.0
    for k, m in enumerate(cloths):
        w = r.uniform(1.3, 2.0)
        if x + w > L_ / 2 - 0.6:
            break
        xm = x + w / 2
        zc = hgt - 0.45 - 0.55 * math.sin(math.pi * (xm + L_ / 2) / L_)
        hh = r.uniform(1.6, 2.5)
        ang = r.uniform(-0.12, 0.12)
        K.bx(mb, F, xm, 0.0, zc - hh * 0.3, w, 0.07, hh * 0.6, m, rx=ang)
        K.bx(mb, F, xm, 0.06, zc - hh * 0.78, w * 0.96, 0.07, hh * 0.42, m, rx=-ang * 1.6 + 0.08)
        x += w + r.uniform(0.35, 0.8)


def mureta(mb, F, L_):
    K.mureta(mb, F, L_, h=1.3, w=1.2, m=STONE, m2=STONE, seed=("vm3", round(F.o.x, 1), round(F.o.y, 1)), lod=1,
             core=False)


# ================================================================== plano: (tipo, x, z, frente (dx, dz), opcoes)
def plan():
    s = []
    A = s.append
    E = L.EXIT_ROAD
    # --- PLACAS DE DIRECAO nos cruzamentos (bigorna = forja, mochila = loja, portal = patio, trofeu = ranking)
    A(("sign", -17.5, 78.0, (0, -1), dict(arrows=[((0, -1), "anvil"), ((1, -0.55), "pack"), ((-1, -0.25), "portal"),
                                                 ((-0.7, -0.75), "trophy")])))       # pe da escadaria do spawn
    A(("sign", 12.5, 17.0, (0, -1), dict(arrows=[((0, -1), "anvil")])))              # boca da rua norte
    A(("sign", -31.0, 61.5, (-1, 0), dict(arrows=[((-1, 0.25), "portal"), ((-0.55, -0.85), "trophy")])))  # rua oeste
    A(("sign", 32.0, 49.0, (1, 0), dict(arrows=[((1, 0), "pack")])))                # rua da loja
    A(("sign", -95.0, 79.0, (-1, 0), dict(arrows=[((-1, 0), "portal")])))            # arco do patio
    A(("sign", 20.0, 84.0, (0, -1), dict(arrows=[((-0.3, -1), "anvil"), ((0.55, 0.85), "portal")])))   # rua de saida
    # --- RUA CURVA DE SAIDA (o quadro da ref_01): barris, caixotes, lenha, vasos, cesto, banco
    A(("barrels", 43.6, 86.0, (0.8, -0.6), dict(n=3)))
    A(("crates", 57.5, 121.0, (-1, 0.1), dict(n=3)))
    A(("woodpile", 41.0, 117.5, (1, -0.2), dict(L=4.6)))
    A(("cart", -14.0, 143.0, (1, 0.2), dict()))
    A(("barrels", 46.0, 138.0, (1, 0), dict(n=2)))
    A(("crates", 56.0, 140.0, (-1, 0), dict(n=2)))
    A(("basket", 38.5, 95.0, (0.9, -0.4), dict(n=2)))
    A(("bench", 25.0, 92.0, (0.9, -0.4), dict()))
    # --- PRACA / SPAWN: vasos nos cantos do terraco e no pe da escadaria
    for x, z in ((-15.5, 91.0), (15.5, 91.0), (-15.5, 109.0), (15.5, 109.0)):
        A(("potgroup", x, z, (0, -1), dict(n=2, y=L.Y_SPAWN)))
    A(("potgroup", 18.5, 76.5, (0, -1), dict(n=2)))
    # --- RUA OESTE / RANKING / PATIO
    A(("barrels", -62.0, 64.0, (0.2, -1), dict(n=3)))
    A(("crates", -75.0, 67.0, (0.2, -1), dict(n=2)))
    A(("cart", -80.0, 108.0, (1, 0.3), dict()))
    A(("barrels", -72.0, -2.0, (0, 1), dict(n=2)))
    A(("crates", -66.0, 6.0, (1, 0.2), dict(n=3)))
    A(("woodpile", -110.0, 22.0, (1, 0), dict(L=5.0)))
    # --- SUDOESTE (prado atras das casas da rua oeste): varal, cestos, mureta de campo, lenha
    A(("line", -60.0, 104.0, (0, -1), dict(L=10.0, cloths=(CREAM, RED, CREAM, RED, CREAM))))
    A(("basket", -54.0, 101.0, (0, -1), dict(n=3)))
    A(("woodpile", -70.0, 86.0, (0, -1), dict(L=5.0)))
    A(("wall", -102.0, 122.0, (1, 0.1), dict(L=22.0)))
    A(("wall", -80.0, 133.0, (1, -0.2), dict(L=16.0)))
    A(("bench", -45.0, 108.0, (0.3, -1), dict()))
    # --- FUNDO DO SPAWN (quintais das casas de fundo)
    A(("line", 2.0, 137.0, (0, 1), dict(L=9.0, cloths=(RED, CREAM, RED, CREAM))))
    A(("woodpile", -24.0, 134.0, (0, 1), dict(L=4.4)))
    A(("sacks", 12.0, 129.5, (0, 1), dict(n=3)))
    # --- LOJA e leste: carga na lateral, carroca, cerca de pedra do pasto, banco
    A(("crates", 70.0, 61.5, (0, 1), dict(n=3)))
    A(("barrels", 85.0, 61.0, (0, 1), dict(n=3)))
    A(("cart", 100.0, 48.0, (0, 1), dict()))
    A(("sacks", 93.0, 30.0, (1, 0), dict(n=4)))
    A(("wall", 128.0, 20.0, (0.1, 1), dict(L=22.0)))
    A(("wall", 140.0, 78.0, (1, 0.25), dict(L=20.0)))
    A(("bench", 112.0, 66.0, (-1, -0.2), dict()))
    # --- NORTE: flanco oeste da forja (fora do largo), canal, pontezinhas
    A(("woodpile", -44.0, -50.0, (1, 0), dict(L=5.4, rows=(5, 4, 3))))
    A(("cart", -54.0, -38.0, (1, -0.3), dict(load="logs")))
    A(("sacks", -40.0, -40.0, (0, 1), dict(n=3)))
    A(("bench", 64.0, -25.0, (0, 1), dict()))
    A(("bench", -64.0, -25.0, (0, 1), dict()))
    A(("barrels", 106.0, -27.0, (0, 1), dict(n=2)))
    A(("wall", 90.0, -70.0, (1, 0.1), dict(L=24.0)))
    A(("wall", -84.0, -88.0, (1, -0.15), dict(L=20.0)))
    A(("line", 70.0, -40.0, (0, 1), dict(L=9.0, cloths=(CREAM, BLUE, CREAM))))
    # --- PORTAO: barris e caixotes encostados nas torres (do lado de dentro)
    A(("barrels", 37.0, 136.0, (1, 0), dict(n=2)))
    return s


# raio da pegada, altura (para a sondagem), colisao
KIND = {"sign": (0.9, 8.0, True), "barrels": (2.0, 2.4, True), "crates": (2.0, 2.6, True), "woodpile": (2.9, 2.4, True),
        "cart": (4.6, 3.6, True), "basket": (1.4, 1.0, False), "bench": (2.3, 2.6, True), "potgroup": (2.0, 1.4, False),
        "line": (5.4, 5.6, True), "wall": (0.0, 1.3, True), "sacks": (1.6, 1.4, False), "pot": (1.25, 1.3, False)}


def site(P, kind, x, z, fx, fz, opt):
    """(y, motivo): pegada livre (construido, rotas, portas, troncos, tufos ja nao contam)"""
    r, hgt, _ = KIND[kind]
    if kind == "wall":
        Ln = opt["L"]
        n = math.hypot(fx, fz) or 1.0
        ux, uz = fx / n, fz / n
        ys = []
        for k in range(7):
            f = -0.5 + k / 6
            px, pz = x + ux * Ln * f, z + uz * Ln * f
            y = P.natural(px, pz)
            if y is None:
                return None, "chao"
            if P.route_dist(px, pz) < 4.0 or VG.d_way(px, pz) < 2.0:
                return None, "rota"
            if not P.clear_r(px, pz, y + 0.8, 1.0):
                return None, "construido"
            if any(math.hypot(px - a, pz - b) < c + 0.9 for a, b, c in VG.TRUNKS):
                return None, "tronco"
            ys.append(y)
        if max(ys) - min(ys) > 0.6:
            return None, "desnivel"
        return min(ys), None
    if opt.get("y") is not None:
        fl = P.floor_y(x, z, opt["y"])
        if fl is None or abs(fl[0] - opt["y"]) > 0.3:
            return None, "piso"
        y = fl[0]
    else:
        y = P.natural(x, z)
        if y is None:
            fl = P.floor_y(x, z)
            if fl is None or not (5.7 < fl[0] < 7.5) or not fl[2].startswith(("Stone_Paving", "Stone_VM", "Grass")):
                return None, "piso"
            y = fl[0]
    if kind != "sign" and P.route_dist(x, z) < r + 2.0:
        return None, "rota"
    if kind == "sign":
        if P.route_dist(x, z) < 2.6:
            return None, "rota"
        for (dx, dz), icon, zl in sign_levels(opt["arrows"]):
            n = math.hypot(dx, dz) or 1.0
            for dz_ in (-0.45, 0.0, 0.45):
                h = P.built.ray_cast(B(x, z, y + zl + dz_), Vector((dx / n, -dz / n, 0.0)), ARROW_L + 0.3)
                if h[0] is not None:
                    return None, "seta x construido"
    if VG.near_door(x, z, 3.0 if opt.get("door_ok") else r + 2.6):
        return None, "porta"
    if any(math.hypot(x - a, z - b) < c + r * 0.7 for a, b, c in VG.TRUNKS):
        return None, "tronco"
    if any(math.hypot(x - a, z - b) < c + r * 0.8 for a, b, c in FOOT):
        return None, "outro prop"
    # construido: 8 raios horizontais (a 0,45 e a meia altura, alcance = pegada) + coluna livre ate o topo + esfera
    # no meio (o piso / calcamento logo abaixo nao conta: os raios correm acima dele)
    rr = r * 0.85
    for hz in (0.45, max(0.6, hgt * 0.6)):
        o = B(x, z, y + hz)
        for k in range(8):
            a = TAU * k / 8
            h = P.built.ray_cast(o, Vector((math.cos(a), math.sin(a), 0.0)), rr)
            if h[0] is not None:
                return None, "construido"
    h = P.built.ray_cast(B(x, z, y + 0.3), Vector((0.0, 0.0, 1.0)), hgt + 0.5)
    if h[0] is not None:
        return None, "teto"
    if not P.clear_r(x, z, y + max(hgt * 0.6, 0.9), min(rr, max(hgt * 0.6, 0.9) - 0.3)):
        return None, "construido"
    return y, None


class PCells:
    def __init__(self):
        self.mb = {}

    def get(self, x, z):
        k = cell_of(x, z)
        if k not in self.mb:
            self.mb[k] = MB("VM_Prop_" + k, "03_TOWN", K.rng("prop", k), detail="far", floor=-999)
        return self.mb[k]

    def finish(self):
        import vm_town as TW
        out = []
        for k in sorted(self.mb):
            ob = self.mb[k].finish()
            if ob is None:
                continue
            TW.merge_mats(ob, MERGE)
            ob["vm_v3a"] = 1
            out.append(ob)
        return out


def plant_in_pot(x, z, ytop, key):
    """planta do vaso (no objeto de VEGETACAO da celula): moita redonda, capim ou flores"""
    mb = VG.CELLS[0].get(x, z) if VG.CELLS[0] is not None else None
    if mb is None:
        return 0
    rng = K.rng("potplant", key)
    k = h01("pk", key)
    if k < 0.45:
        return VG.cushion(mb, B(x, z, ytop - 0.25), 0.8, 0.75, 1.1, VG.MID if k < 0.3 else VG.LIGHT, VG.DARK, rng, n=6)
    if k < 0.7:
        return VG.tuft(mb, x, z, ytop, rng, s=0.9, m=VG.LIGHT)
    return VG.flower_patch(mb, x, z, ytop, rng, K.FLOWERS[VG.CELL_FLOWER[cell_of(x, z)]], n=5, r=0.45)


def emit(P, cells, kind, x, z, y, fx, fz, opt, key):
    mb = cells.get(x, z)
    F = frame(x, z, y - 0.02, fx, fz)
    r, hgt, col = KIND[kind]
    n = math.hypot(fx, fz) or 1.0
    ux, uz = fx / n, fz / n
    if kind == "sign":
        signpost(mb, F, opt["arrows"])
        VL.colr("PropSign", (x - 0.45, y, z - 0.45), (x + 0.45, y + SIGN_H, z + 0.45))
    elif kind == "barrels":
        rr = K.rng("bar", key)
        pts = [(0.0, 0.0), (1.95, 0.25), (0.95, 1.7), (-1.6, 0.9)][:opt.get("n", 3)]
        for i, (a, b) in enumerate(pts):
            K.barrel(mb, F, a - 0.4, b - 0.6, 0.0, h=rr.uniform(2.0, 2.4), r=rr.uniform(0.82, 0.92))
        VL.colr_rot("PropGroup", x, z, y + 1.2, 4.4, 3.4, 2.4, -uz, ux)
    elif kind == "crates":
        rr = K.rng("crt", key)
        nn = opt.get("n", 3)
        K.crate(mb, F, -0.9, 0.0, 0.0, s=1.9, a=rr.uniform(-0.1, 0.1))
        if nn >= 2:
            K.crate(mb, F, 1.15, 0.2, 0.0, s=1.7, a=rr.uniform(-0.2, 0.2))
        if nn >= 3:
            K.crate(mb, F, -0.7, 0.1, 1.9, s=1.5, a=rr.uniform(-0.3, 0.3))
        VL.colr_rot("PropGroup", x, z, y + 1.3, 4.2, 2.4, 2.6, -uz, ux)
    elif kind == "woodpile":
        top = woodpile(mb, F, opt.get("L", 4.4), opt.get("rows", (4, 3, 2)))
        VL.colr_rot("PropGroup", x, z, y + top / 2, opt.get("L", 4.4), 4.2, top, -uz, ux)
    elif kind == "cart":
        Fc = frame(x, z, y - 0.05, uz, -ux)            # +x local (varais) ao longo de (fx, fz)
        K.cart(mb, Fc, load=opt.get("load", True) is True)
        if opt.get("load") == "logs":
            for i in range(4):
                log(mb, Fc, (-2.6, -0.9 + i * 0.6, 2.75), (2.4, -0.9 + i * 0.6, 2.75), 0.28)
            for i in range(3):
                log(mb, Fc, (-2.5, -0.6 + i * 0.6, 3.25), (2.3, -0.6 + i * 0.6, 3.25), 0.28)
        VL.colr_rot("PropCart", x, z, y + 1.7, 7.0, 4.6, 3.4, ux, uz)
    elif kind == "basket":
        for i in range(opt.get("n", 2)):
            a, b = (i * 1.5 - 0.7, 0.25 * (i % 2))
            basket(mb, F, a, b)
            p = Vector(F.p(a, b, 0.0))
            VG.cushion(VG.CELLS[0].get(x, z), Vector((p.x, p.y, y + 0.35)), 0.55, 0.5, 0.55,
                       VG.LIGHT if i % 2 else VG.MID, VG.MID, K.rng("bk", key, i), n=6)
    elif kind == "bench":
        bench(mb, F)
        VL.colr_rot("PropBench", x, z, y + 0.7, 4.0, 1.6, 1.4, -uz, ux)
    elif kind == "potgroup":
        for i in range(opt.get("n", 2)):
            a = (i - (opt.get("n", 2) - 1) / 2) * 1.75
            rr = 0.62 + 0.2 * h01("pr", key, i)
            hh = 1.0 + 0.45 * h01("ph", key, i)
            pot(mb, F, a, 0.1 * (i % 2), rr, hh)
            p = Vector(F.p(a, 0.1 * (i % 2), 0.0))
            plant_in_pot(p.x, -p.y, y + hh - 0.08, (key, i))
    elif kind == "line":
        Fl = frame(x, z, y - 0.02, fx, fz)
        clothesline(mb, Fl, opt.get("L", 9.0), opt.get("cloths", (CREAM, RED, CREAM, BLUE)))
        for sx in (-1, 1):
            p = Vector(Fl.p(sx * opt.get("L", 9.0) / 2, 0.0, 0.0))
            VL.colr("PropPost", (p.x - 0.3, y, -p.y - 0.3), (p.x + 0.3, y + 5.6, -p.y + 0.3))
    elif kind == "sacks":
        for i in range(opt.get("n", 3)):
            a = (i - (opt.get("n", 3) - 1) / 2) * 1.15
            sack(mb, F, a, 0.15 * (i % 2), 0.0, 0.9 + 0.2 * h01("sk", key, i), CREAM, a=i)
        if opt.get("n", 3) >= 3:
            sack(mb, F, 0.0, 0.1, 1.15, 0.85, CREAM, a=0.7)
    elif kind == "wall":
        Ln = opt["L"]
        Fw = frame(x, z, y, -uz, ux)                   # +x local da mureta ao longo de (fx, fz)
        mureta(mb, Fw, Ln)
        VL.colr_rot("PropWall", x, z, y + 0.7, Ln, 1.3, 1.4, ux, uz)
    if kind == "wall":
        for k in range(7):
            f = -0.5 + k / 6
            FOOT.append((x + ux * opt["L"] * f, z + uz * opt["L"] * f, 1.0))
    else:
        FOOT.append((x, z, r))


def build():
    FOOT.clear()
    STATS.clear()
    for o in list(bpy.data.objects):
        if o.name.startswith(("VM_Prop_", "COL_Prop")):
            bpy.data.objects.remove(o, do_unlink=True)
    for k in list(fm_lib._COL_COUNT):
        if k.startswith("Prop"):
            fm_lib._COL_COUNT.pop(k)
    P = VG.Probe()
    cells = PCells()
    rep = {"ok": 0, "fora": {}}
    for i, (kind, x0, z0, (fx, fz), opt) in enumerate(plan()):
        done = None
        why = None
        for k in range(24):
            a = k * 2.39
            d = 0.0 if k == 0 else 0.8 + 0.18 * k
            x, z = x0 + math.cos(a) * d, z0 + math.sin(a) * d
            y, why = site(P, kind, x, z, fx, fz, opt)
            if y is not None:
                done = (x, z, y)
                break
        if done is None:
            rep["fora"]["%d_%s(%s)" % (i, kind, why)] = (x0, z0)
            continue
        x, z, y = done
        emit(P, cells, kind, x, z, y, fx, fz, opt, ("p", i))
        rep["ok"] += 1
        if kind == "sign" and "CAM_VM_V3_Close_Placa" not in VG.CLOSES and z > 70:
            VG.CLOSES["CAM_VM_V3_Close_Placa"] = ((x + 6.0, y + 5.5, z + 7.0), (x, y + 5.0, z), 26)
        if kind == "cart" and "CAM_VM_V3_Close_Props1" not in VG.CLOSES and x > 0:
            VG.CLOSES["CAM_VM_V3_Close_Props1"] = ((x + 9.0 * fx - 6.0 * fz, y + 5.0, z + 9.0 * fz + 6.0 * fx),
                                                   (x, y + 1.6, z), 24)
        if kind == "woodpile" and "CAM_VM_V3_Close_Props2" not in VG.CLOSES:
            VG.CLOSES["CAM_VM_V3_Close_Props2"] = ((x + 8.0 * fx + 4.0 * fz, y + 4.5, z + 8.0 * fz - 4.0 * fx),
                                                   (x, y + 1.2, z), 26)
    # vasos nas portas (2 de 5 portas, sorteio fixo): ao lado da folha, encostados na fachada
    nd = 0
    for j, d in enumerate(VG.doors()):
        x0, z0 = d[0], d[1]
        best = None
        for (hx, hz, fx, fz, W, D) in VG.HOUSES:
            v = (x0 - hx) * fx + (z0 - hz) * fz
            u = (x0 - hx) * (-fz) + (z0 - hz) * fx
            if abs(u) < W / 2 + 0.5 and D / 2 - 1.5 < v < D / 2 + 1.8:
                best = (fx, fz)
                break
        if best is None or h01("doorpot", j) > 0.4:
            continue
        fx, fz = best
        for s in (-1, 1):
            if h01("doorpot_s", j, s) < 0.3:
                continue
            x, z = x0 + (-fz) * s * 3.6 + fx * 1.2, z0 + fx * s * 3.6 + fz * 1.2
            y, why = site(P, "pot", x, z, fx, fz, {"door_ok": True})
            if y is None:
                continue
            emit(P, cells, "potgroup", x, z, y, fx, fz, dict(n=1), ("dp", j, s))
            nd += 1
    rep["vasos_portas"] = nd
    # vasos nas QUINAS das fachadas das ruas (1 em 2 casas, sorteio fixo): flor e folha na base da parede (ref_01)
    import vm_town as TW
    nq = 0
    for h in TW.layout():
        if h["preset"] == "FILL" or h01("qpot", h["id"]) > 0.55:
            continue
        fx, fz = h["fx"], h["fz"]
        s = 1 if h01("qpot_s", h["id"]) < 0.5 else -1
        for s_ in (s, -s):
            u = s_ * (h["W"] / 2 - 1.0)
            x = h["x"] + fx * (h["D"] / 2 + 1.3) + (-fz) * u
            z = h["z"] + fz * (h["D"] / 2 + 1.3) + fx * u
            y, why = site(P, "pot", x, z, fx, fz, {})
            if y is None:
                continue
            emit(P, cells, "potgroup", x, z, y, fx, fz, dict(n=1 + (h01("qpot_n", h["id"]) < 0.4)), ("qp", h["id"]))
            nq += 1
            break
    rep["vasos_quinas"] = nq
    obs = cells.finish()
    STATS.update(rep)
    print("PROPS: %d colocados, %d vasos de porta, %d de quina; fora: %s" % (rep["ok"], nd, nq, rep["fora"]))
    return obs
