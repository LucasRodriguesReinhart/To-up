# fm_props - props de ambientacao com proposito:
#  - luz por NO (pe de escada, portas, cruzamentos, portais), nao em fila: postes so onde fazem falta, arandelas nas
#    paredes das cabanas, toro de pedra no lado do Naruto, varal de lampioes nos cruzamentos (PROP_Lanterns_<trecho>)
#  - chegada assimetrica e baixa (nada tampa a visada spawn -> portais): gantry de madeira com corda e lanterna a
#    esquerda do spawn, pilha de caixotes com cristais a direita; no topo da escadaria, poste baixo de um lado e arco
#    de madeira baixo com carrinho de minerio do outro
#  - historia da mineracao e da vila (PROP_Story_*): carrinhos carregados, cristais junto ao balcao, lingotes, rack de
#    picaretas e armas, baia de carvao, carrinho de mao, poco, horta, varal, fogueira, ferramentas nas portas, e
#    cargas por receita de lugar (mina, forja, rio, patio)
#  - placas de direcao (sem texto) e fumaca da torre (helper do Blender; no Roblox e ParticleEmitter)
import math, random
import bpy
from mathutils import Vector
from fm_lib import MB, D, col_box, marker, light, resample, point_in_poly
from fm_parts import Frame, banner
import fm_layout as L
import fm_props_kit as K
from fm_props_kit import PMB, V

F0 = L.FLOOR
SCONCE_Z = 8.2        # ponto da arandela na parede: a lanterna pendura com o fundo >= 6 acima do passeio


def building_boxes(margin=1.5):
    """pegadas xy das construcoes (lanternas e cargas nunca nascem dentro de alas, torre ou casas)"""
    out = []
    for o in bpy.data.objects:
        if o.type != "MESH" or not o.name.startswith(("FORGE_", "BLD_", "WATER_Waterwheel", "MINE_Entrance")):
            continue
        if o.name.startswith("BLD_Bridges"):
            continue
        cs = [o.matrix_world @ Vector(c) for c in o.bound_box]
        out.append((min(c.x for c in cs) - margin, min(c.y for c in cs) - margin,
                    max(c.x for c in cs) + margin, max(c.y for c in cs) + margin))
    return out


def inside_any(x, y, boxes):
    return any(x0 < x < x1 and y0 < y < y1 for (x0, y0, x1, y1) in boxes)


def wall_hit(obname, origin, direction, maxd=12.0):
    """raio contra a malha de uma construcao: (ponto, normal) da parede em coords de mundo, ou None"""
    ob = bpy.data.objects.get(obname)
    if ob is None:
        return None
    mi = ob.matrix_world.inverted()
    o = mi @ Vector(origin)
    d = (mi.to_3x3() @ Vector(direction)).normalized()
    ok, loc, nrm, idx = ob.ray_cast(o, d, distance=maxd)
    if not ok:
        return None
    n = (ob.matrix_world.to_3x3().inverted().transposed() @ nrm).normalized()
    if n.dot(Vector(direction)) > 0:
        n = -n
    return ob.matrix_world @ loc, n


def door_frame(name):
    """marcador DOOR_*: posicao e normal para fora (confirmada por raio contra a cabana)"""
    mk = bpy.data.objects.get("DOOR_Cabin_" + name)
    if mk is None:
        return None
    p = mk.location.copy()
    rz = mk.rotation_euler.z
    for n in (Vector((math.cos(rz), math.sin(rz), 0)), Vector((-math.cos(rz), -math.sin(rz), 0))):
        h = wall_hit("BLD_Cabin_" + name, p + n * 4.0 + Vector((0, 0, 2.0)), -n, 6.0)
        if h and (h[0].xy - p.xy).length < 1.5:
            return p, n
    return p, Vector((math.cos(rz), math.sin(rz), 0))


# ================================================================== LUZ POR NO
def lanterns(rng, site):
    """postes so nos nos (topo/pe de escada, cruzamentos, portais); o resto vira arandela, toro ou varal"""
    C = PMB("PROP_Lanterns_Center", "08_PROPS", rng,
            remap={"Coal_Rock": "Stone_Dark", "Cliff_Rock_Dark": "Stone_Dark"})
    W = PMB("PROP_Lanterns_West", "08_PROPS", rng, remap={"Metal_Iron": "Metal_Dark"})
    E = PMB("PROP_Lanterns_East", "08_PROPS", rng, remap={"Metal_Iron": "Metal_Dark"})

    # --- centro: escadaria do spawn (um poste so, do lado direito; o esquerdo e o gantry da chegada)
    K.post_lamp(C, 12.0, -73.0, L.SPAWN_Z, math.pi, "L_Path_Spawn_R", h=5.4, arm=0.0)
    col_box("Props", (1.4, 1.4, 8.0), (12.0, -73.0, L.SPAWN_Z + 4.0))
    site.reserve(12.0, -73.0, 1.0)
    # topo da escadaria: poste BAIXO a direita (topo z10, fica entre as visadas SG/DS e DB/OP)
    K.low_post_lamp(C, 13.6, -57.8, F0, 0.3, "L_Path_StairTop_R", z_top=F0 + 6.0)
    col_box("Props", (1.6, 1.6, 6.0), (13.6, -57.8, F0 + 3.0))
    site.reserve(13.6, -57.8, 1.0)
    # cruzamento praca -> estrada da mina / estrada oeste: varal de lampioes atravessando a estrada da mina
    a = site.place("varal_W_a", -33.0, -38.6, 0.8, 3.0)
    b = site.place("varal_W_b", -36.0, -51.6, 0.8, 3.0)
    if a and b:
        K.string_lights(C, a, b, F0, h=9.4, sag=1.3, n=5, name="L_Path_MineRoad_Garland", rng=rng)
        for q in (a, b):
            col_box("Props", (1.3, 1.3, 9.6), (q[0], q[1], F0 + 4.8))

    # --- oeste: pe das escadas dos portais (Naruto = toros de pedra; DB e SG = um poste so, lados alternados)
    y = L.FLIGHT1_Y0 - 0.5
    px = L.PORTAL_X
    for sgn in (-1, 1):
        x = px[0] + sgn * 9.2
        K.toro(W, (x, y, F0), 0.0, "L_StairFoot_0_%d" % (sgn + 1), s=0.85)
        col_box("Props", (2.6, 2.6, 5.4), (x, y, F0 + 2.7))
    for j, sgn in ((1, 1), (2, -1)):
        x = px[j] + sgn * 9.2
        K.post_lamp(W, x, y, F0, math.pi if sgn > 0 else 0.0, "L_StairFoot_%d_%d" % (j, sgn + 1), h=6.2, arm=1.9)
        col_box("Props", (1.4, 1.4, 8.6), (x, y, F0 + 4.3))
    # cruzamento do trilho com a estrada oeste (lado oeste da estrada, braco para a estrada)
    p = site.place("poste_cruz_trilho", -50.6, 22.0, 0.8, 3.0, rail=1.8)
    if p:
        K.post_lamp(W, p[0], p[1], F0, 0.0, "L_Path_RailCrossing", h=6.2, arm=1.9)
        col_box("Props", (1.4, 1.4, 8.6), (p[0], p[1], F0 + 4.3))
    # arandelas nas paredes das cabanas voltadas para o patio dos fundos
    for nm, x0 in (("West_C", -63.0), ("West_B", -95.5)):
        h = wall_hit("BLD_Cabin_" + nm, (x0, 40.0, F0 + SCONCE_Z), (0, -1, 0), 14.0)
        if h:
            K.sconce(W, h[0], h[1], "L_Path_Sconce_%s" % nm)
        else:
            print("PLACE arandela %s -> sem parede" % nm)

    # --- leste: pe das escadas DS/OP (um poste, do lado de fora do tanque), OPM com varal sobre o pe da escada
    for j, sgn in ((3, -1), (4, 1)):
        x = px[j] + sgn * 9.2
        K.post_lamp(E, x, y, F0, math.pi if sgn > 0 else 0.0, "L_StairFoot_%d_%d" % (j, sgn + 1), h=6.2, arm=1.9)
        col_box("Props", (1.4, 1.4, 8.6), (x, y, F0 + 4.3))
    K.string_lights(E, (px[5] - 9.2, y), (px[5] + 9.2, y), F0, h=9.6, sag=1.1, n=6, name="L_StairFoot_5_1", rng=rng)
    for sgn in (-1, 1):
        col_box("Props", (1.3, 1.3, 10.0), (px[5] + sgn * 9.2, y, F0 + 5.0))
    # patio dos fundos (lado leste da torre) e margem leste (lanterna pendura com fundo >= 6 acima do passeio)
    K.post_lamp(E, 17.0, 46.0, F0, 0.0, "L_Path_BackCourt", h=6.2, arm=0.0)
    col_box("Props", (1.4, 1.4, 8.6), (17.0, 46.0, F0 + 4.3))
    p = site.place("poste_margem_leste", 102.0, 34.6, 0.8, 3.0)      # no da esquina margem leste / fundos
    if p:
        K.post_lamp(E, p[0], p[1], F0, math.pi, "L_Path_EastBank", h=6.4, arm=1.9)
        col_box("Props", (1.4, 1.4, 8.8), (p[0], p[1], F0 + 4.4))
    for nm, yy in (("East_A", -3.0), ("East_B", 20.0)):
        h = wall_hit("BLD_Cabin_" + nm, (99.0, yy, F0 + SCONCE_Z), (1, 0, 0), 14.0)
        if h:
            K.sconce(E, h[0], h[1], "L_Path_Sconce_%s" % nm)
        else:
            print("PLACE arandela %s -> sem parede" % nm)
    return C, W, E


# ================================================================== CHEGADA (baixa e assimetrica)
def arrival(C, rng, site):
    z = L.SPAWN_Z
    # gantry de madeira (guincho de carga) a esquerda do spawn: torre de 2 montantes com cruz de santo andre,
    # lanca para a avenida, roldana, sarilho com manivela; balde de cristais e lanterna pendurados entram no quadro
    F = Frame(-19.4, -95.2, z, 0.0)
    for sy in (-1, 1):
        C.box((1.7, 1.7, 0.8), F.p(0, sy * 1.8, 0.4), F.r(0, 0, 0.3), "Stone_Dark", 0.1)
        C.box((0.95, 0.95, 12.6), F.p(0, sy * 1.8, 6.9), F.r(sy * 0.035, 0, 0), "Wood_Dark", 0.08)
        C.beam(F.p(0, sy * 1.8, 2.2), F.p(0, -sy * 1.8, 8.6), 0.4, 0.4, "Wood_Dark", 0.0)
        C.beam(F.p(0, sy * 1.75, 9.8), F.p(0, sy * 0.3, 12.2), 0.45, 0.45, "Wood_Dark", 0.0)
    C.box((1.0, 4.9, 0.9), F.p(0, 0, 12.6), F.r(), "Wood_Dark", 0.08)
    C.beam(F.p(-0.9, 0, 12.1), F.p(5.8, 0, 12.1), 0.8, 0.9, "Wood_Dark", 0.06)
    C.beam(F.p(0.3, 0, 8.2), F.p(3.8, 0, 11.75), 0.5, 0.5, "Wood_Dark", 0.0)
    C.cyl(0.62, 0.3, F.p(5.2, 0, 11.3), F.r(D(90), 0, 0), "Metal_Dark", 8, bevel=0.0)
    for sy in (-0.28, 0.28):
        C.box((1.1, 0.12, 1.25), F.p(5.2, sy, 11.55), F.r(), "Metal_Dark", 0.0)
    # sarilho (tambor com corda) entre os montantes + manivela
    C.cyl(0.6, 3.0, F.p(0.9, 0, 3.0), F.r(D(90), 0, 0), "Wood_Plank", 8, bevel=0.0)
    C.cyl(0.66, 1.4, F.p(0.9, 0, 3.0), F.r(D(90), 0, 0), "Rope", 8, bevel=0.0)
    C.beam(F.p(0.9, -1.6, 3.0), F.p(0.9, -1.75, 2.1), 0.18, 0.18, "Metal_Dark", 0.0)
    C.beam(F.p(0.9, -1.75, 2.1), F.p(0.9, -2.3, 2.1), 0.16, 0.16, "Wood_Dark", 0.0)
    C.tube([F.p(1.3, 0, 3.4), F.p(0.7, 0, 11.4), F.p(4.6, 0, 11.75)], 0.08, "Rope", 4)
    # carga pendurada na roldana: balde de cristais (acento frio no primeiro plano)
    C.rod(F.p(5.2, 0, 10.7), F.p(5.2, 0, 7.6), 0.08, "Rope", 4)
    K.keg(C, tuple(F.p(5.2, 0, 5.9)), 0.75, 1.5, "Wood_Plank", "Metal_Dark")
    C.beam(F.p(4.5, 0, 7.4), F.p(5.2, 0, 7.8), 0.1, 0.1, "Metal_Dark", 0.0)
    C.beam(F.p(5.9, 0, 7.4), F.p(5.2, 0, 7.8), 0.1, 0.1, "Metal_Dark", 0.0)
    K.crystals(C, F.p(5.2, 0, 7.3), 0.42, rng, 4, "Crystal_Blue")
    # lanterna pendurada da lanca (fundo ~7,5 acima do patamar)
    K.hang_lamp(C, F.p(2.9, 0, 11.65), 2.1, "L_Path_Spawn_Gantry", 190)
    K.rope_coil(C, tuple(F.p(1.2, -3.0, 0.0)), 0.75)
    K.crate(C, tuple(F.p(1.7, 3.0, 0.0)), 1.7, 0.4)
    col_box("Props", (2.4, 5.2, 12.8), tuple(F.p(0.4, 0, 6.4)), F.r())
    # pilha de caixotes com cristais a direita, encostada no parapeito da frente do patamar: a coluna de 3 caixotes
    # com o caixote aberto de cristais no topo (<= z8) entra no canto inferior direito do quadro do spawn, como no
    # concept; fica longe das visadas (x >= 12,8 na altura do parapeito)
    G = Frame(14.0, -94.5, z, D(-6))
    K.crate(C, tuple(G.p(0, 0, 0)), 2.4, G.a)
    K.crate(C, tuple(G.p(0.15, 0.05, 2.4)), 2.0, G.a + 0.22)
    K.open_crate_crystals(C, tuple(G.p(-0.05, 0.0, 4.4)), 1.9, G.a - 0.12, rng)
    K.crystals(C, G.p(-0.3, -0.2, 5.8), 0.72, rng, 5, "Crystal_Blue", spread=0.9)
    K.crate(C, tuple(G.p(2.5, -0.3, 0)), 1.8, G.a - 0.2)
    K.crystals(C, G.p(2.5, -0.3, 1.8), 0.5, rng, 4, "Crystal_Blue")
    K.open_crate_crystals(C, tuple(G.p(-0.5, -2.7, 0)), 1.9, G.a + 0.15, rng)
    K.keg(C, tuple(G.p(2.3, -2.6, 0)), 0.85, 2.0)
    col_box("Props", (5.6, 5.6, 6.4), tuple(G.p(0.9, -1.3, 3.2)), G.r())
    site.reserve(14.9, -95.8, 3.4)
    # topo da escadaria, lado esquerdo: arco de madeira baixo (topo z<=10) com carrinho de minerio saindo dele
    x, y0, y1 = -15.6, -59.9, -55.1
    for yy in (y0, y1):
        C.box((1.2, 1.2, 0.7), (x, yy, F0 + 0.35), (0, 0, 0.2), "Stone_Dark", 0.08)
        C.box((0.9, 0.9, 5.3), (x, yy, F0 + 3.0), (0, 0, 0), "Wood_Dark", 0.08)
        C.cyl(0.62, 0.45, (x, yy, F0 + 3.9), (0, 0, 0), "Rope", 6, bevel=0.0)
    C.box((1.1, 6.6, 0.8), (x, (y0 + y1) / 2, F0 + 5.55), (0, 0, 0), "Wood_Dark", 0.08)
    for yy, sg in ((y0, 1), (y1, -1)):
        C.beam((x, yy, F0 + 3.6), (x, yy + sg * 1.5, F0 + 5.2), 0.4, 0.4, "Wood_Dark", 0.0)
    banner(C, (x + 0.62, (y0 + y1) / 2, F0 + 5.1), D(90), w=1.7, h=2.0, cloth="Cloth_Navy", trim="Wood_Dark",
           emblem="pickaxe")
    rp = [V(x - 5.4, -57.5, F0), V(x + 2.4, -57.5, F0)]
    K.rail_stub(C, rp, z=F0 + 0.02, rng=rng)
    K.bumper(C, rp[1], (1, 0))
    K.cart(C, (x - 2.6, -57.5, F0 + 0.3), 0.0, rng, "crystal")
    col_box("Props", (8.4, 6.6, 3.6), (x - 1.6, -57.5, F0 + 1.8))
    col_box("Props", (1.2, 6.6, 6.4), (x, -57.5, F0 + 3.2))
    site.reserve(x - 1.5, -57.5, 4.0)


# ================================================================== HISTORIA DA MINERACAO E DA VILA
def signpost(mb, x, y, arrows):
    mb.box((0.9, 0.9, 8.5), (x, y, F0 + 4.25), (0, 0, 0), "Wood_Dark", 0.08)
    icons = {"pick": "Crystal_Blue", "portal": "Crystal_Purple", "forge": "Lantern_Glow"}
    for j, (deg, icon) in enumerate(arrows):
        a = D(deg)
        z = F0 + 7.0 - j * 1.8
        c = Vector((x + math.cos(a) * 2.0, y + math.sin(a) * 2.0, z))
        mb.box((4.0, 0.3, 1.3), c, (0, 0, a), "Wood_Plank", 0.06)
        tip = Vector((x + math.cos(a) * 4.3, y + math.sin(a) * 4.3, z))
        mb.cyl(0.9, 0.3, tip, (D(90), 0, a + math.pi / 2), "Wood_Plank", 3, bevel=0.0)
        ic = Vector((x + math.cos(a) * 2.4, y + math.sin(a) * 2.4, z))
        mb.ico(0.45, ic + Vector((math.sin(a) * 0.3, -math.cos(a) * 0.3, 0)), icons[icon], 1)
    col_box("Props", (1.2, 1.2, 8.5), (x, y, F0 + 4.25))


def cargo(mb, rng, site, kind, x, y, a):
    """pilha de carga por RECEITA do lugar, com contagem e escala sorteadas"""
    s = rng.uniform(0.85, 1.12)
    F = Frame(x, y, F0, a)
    if kind == "mine":            # sacos de minerio + carrinho de mao de minerio
        for i in range(rng.randint(3, 5)):
            K.sack(mb, tuple(F.p(rng.uniform(-1.6, 1.6), rng.uniform(-1.2, 1.2), 0)), rng, s * rng.uniform(0.85, 1.1),
                   lying=rng.random() < 0.3)
        K.cart(mb, tuple(F.p(0.3, 2.9, 0.3)), a + D(90), rng, "ore")
        return (6.0, 7.0)
    if kind == "forge":           # carvao ensacado + lingotes
        K.ingot_pallet(mb, tuple(F.p(0, 0, 0)), a, rng, rng.randint(2, 3))
        for i in range(rng.randint(2, 4)):
            K.sack(mb, tuple(F.p(2.4 + rng.uniform(-0.4, 0.4), -1.2 + i * 1.1, 0)), rng, s * 0.95, m="Cloth_Canvas")
        K.ore_bits(mb, tuple(F.p(2.3, 1.8, 0.0)), 0.9, 4, rng, "Coal_Rock", 0.3, 0.6)
        return (6.0, 4.6)
    if kind == "river":           # barris + rolos de corda
        n = rng.randint(2, 3)
        for i in range(n):
            K.keg(mb, tuple(F.p(i * 2.1 - 1.0, rng.uniform(-0.3, 0.3), 0)), 0.9 * s, 2.1 * s)
        if rng.random() < 0.6:
            K.keg(mb, tuple(F.p(0.1, 0.3, 2.1 * s)), 0.85 * s, 1.9 * s)
        for i in range(rng.randint(1, 2)):
            K.rope_coil(mb, tuple(F.p(-1.4 + i * 2.6, 2.0, 0)), 0.75)
        return (2.1 * n + 1.5, 5.0)
    if kind == "yard":            # pilha de toras
        K.log_pile(mb, tuple(F.p(0, 0, 0)), a, rng, rng.randint(4, 6), 4.4 * s)
        mb.cyl(0.8, 0.9, F.p(3.2, 1.2, 0.45), F.r(), "Bark", 7, bevel=0.0)
        return (6.4, 4.6)
    if kind == "shed":            # caixotes abertos com cristais refinados
        for i in range(rng.randint(2, 3)):
            K.open_crate_crystals(mb, tuple(F.p(i * 2.4 - 1.2, rng.uniform(-0.3, 0.3), 0)), 1.9 * s,
                                  a + rng.uniform(-0.2, 0.2), rng)
        K.crate(mb, tuple(F.p(0.0, 2.2, 0)), 2.0, a + 0.2)
        return (7.0, 5.0)
    return (4.0, 4.0)


def cargo_at(mb, rng, site, kind, x, y, a, r=3.6):
    p = site.place("carga_" + kind, x, y, r, 6.0)
    if not p:
        return
    w, d = cargo(mb, rng, site, kind, p[0], p[1], a)
    col_box("Props", (w, d, 3.6), (p[0], p[1], F0 + 1.8), (0, 0, a))


def story_west(rng, site):
    # dois objetos (cada MeshPart <= 150 studs): borda da praca/forja e margem oeste (trilho, cabanas, patio)
    mb = PMB("PROP_Story_Plaza", "08_PROPS", rng,
              remap={"Cliff_Rock_Dark": "Coal_Rock", "Metal_Brass": "Metal_Iron", "Metal_Dark": "Metal_Iron",
                     "Emblem_Cream": "Rope", "Cloth_Canvas": "Rope"})
    # fogueira com toras-banco no gramado sudoeste da praca
    p = site.place("fogueira", -24.5, -56.6, 4.2, 4.0)
    if p:
        K.campfire(mb, (p[0], p[1], F0), rng, "L_Campfire")
        for k, ang in enumerate((D(95), D(210), D(330))):
            c = (p[0] + math.cos(ang) * 3.4, p[1] + math.sin(ang) * 3.4, F0)
            K.bench_log(mb, c, ang + math.pi / 2, 3.4 - k * 0.3)
            col_box("Props", (3.4, 1.3, 1.2), (c[0], c[1], F0 + 0.6), (0, 0, ang + math.pi / 2))
        col_box("Props", (3.4, 3.4, 1.6), (p[0], p[1], F0 + 0.8))
    signpost(mb, -30.0, -50.0, ((-150, "pick"), (60, "portal")))
    site.reserve(-30.0, -50.0, 1.0)
    # balcao de venda: caixotes abertos com cristais + lingotes + rack de picaretas e armas
    for tag, x, y, s in (("cristais_balcao_a", 21.0, -4.6, 1.9), ("cristais_balcao_b", 33.0, -3.4, 2.0)):
        q = site.place(tag, x, y, 1.6, 3.0)
        if q:
            K.open_crate_crystals(mb, (q[0], q[1], F0), s, rng.uniform(-0.3, 0.3), rng)
            if tag.endswith("a"):
                K.crate(mb, (q[0] - 0.6, q[1] + 2.1, F0), 1.7, 0.3)
            col_box("Props", (2.4, 2.4 if tag.endswith("b") else 4.6, 2.4),
                    (q[0], q[1] + (0 if tag.endswith("b") else 1.0), F0 + 1.2))
    q = site.place("lingotes", 34.0, -7.4, 1.9, 3.0)
    if q:
        K.ingot_pallet(mb, (q[0], q[1], F0), D(15), rng, 3)
        col_box("Props", (3.2, 2.6, 2.2), (q[0], q[1], F0 + 1.1), (0, 0, D(15)))
    q = site.place("rack_armas", 17.6, -9.2, 2.6, 3.0)
    if q:
        Fr = Frame(q[0], q[1], F0, D(200))
        K.tool_rack(mb, Fr, rng, ("pick", "pick", "shovel"), swords=2)
        col_box("Props", (6.0, 1.6, 3.8), tuple(Fr.p(0, 0.3, 1.9)), Fr.r())
    # carrinho de mao com picaretas prontas entre a forja e a loja
    q = site.place("carrinho_de_mao", 30.5, -11.2, 1.8, 3.0)
    if q:
        K.wheelbarrow(mb, (q[0], q[1], F0), D(160), rng)
        col_box("Props", (4.0, 2.0, 2.2), (q[0], q[1], F0 + 1.1), (0, 0, D(160)))
    # baia de carvao com sacos no canto sudoeste da ala esquerda (no lugar da carga generica)
    q = site.place("baia_carvao", -34.6, -5.0, 2.9, 6.0, boxes=-5.0)   # a caixa do loft e folgada deste lado
    if q:
        Fb = Frame(q[0], q[1], F0, D(40))            # aberta para a praca (o carvao aparece)
        K.coal_bay(mb, Fb, rng, w=4.6, d=3.2)
        for i in range(3):
            K.sack(mb, tuple(Fb.p(-3.9 + rng.uniform(-0.2, 0.2), -0.8 + i * 1.2, 0)), rng, 0.95, "Cloth_Canvas",
                   lying=(i == 2))
        col_box("Props", (1.8, 3.8, 1.8), tuple(Fb.p(-3.9, 0.4, 0.9)), Fb.r())
    # bordas da praca: entrega de cristais no gramado sudeste (a caminho da loja) e no noroeste (a caminho da forja)
    for tag, x, y, yaw in (("entrega_se", 17.0, -50.5, D(15)), ("entrega_nw", -30.5, -18.5, D(60))):
        q = site.place(tag, x, y, 2.8, 3.5)
        if q:
            Fq = Frame(q[0], q[1], F0, yaw)
            K.cart(mb, tuple(Fq.p(0, 0, 0.3)), yaw, rng, "crystal")
            K.open_crate_crystals(mb, tuple(Fq.p(-0.6, 2.4, 0)), 1.8, yaw + 0.2, rng)
            K.crate(mb, tuple(Fq.p(1.8, 2.3, 0)), 1.6, yaw - 0.15)
            col_box("Props", (4.0, 5.6, 3.6), tuple(Fq.p(0.3, 1.2, 1.8)), Fq.r())
    mb.finish()
    mb = PMB("PROP_Story_West", "08_PROPS", rng,
              remap={"Cliff_Rock_Dark": "Coal_Rock", "Metal_Brass": "Metal_Iron", "Metal_Dark": "Metal_Iron",
                     "Emblem_Cream": "Rope", "Cloth_Canvas": "Rope", "Stone_Dark": "Coal_Rock"})
    # carrinho carregado estacionado ao lado do trilho, perto do cruzamento com a estrada oeste
    q = site.place("carrinho_trilho_n", -52.4, 7.0, 1.9, 2.5, rail=1.0)
    if q:
        K.cart(mb, (q[0], q[1], F0 + 0.3), D(92), rng, "crystal")
        col_box("Props", (3.6, 2.6, 3.4), (q[0], q[1], F0 + 1.7), (0, 0, D(92)))
    # ferramentas encostadas nas portas das cabanas (so em duas: nao e carimbo)
    for nm, side, kinds in (("West_A", 1, ("pick", "shovel")), ("West_C", -1, ("shovel", "pick"))):
        df = door_frame(nm)
        if df:
            p0, n = df
            t = Vector((-n.y, n.x, 0))
            K.leaning_tools(mb, p0 + t * side * 2.6, n, rng, kinds)
    # cargas por receita: carvao e lingotes atras da forja, minerio ensacado junto ao trilho, toras no patio oeste
    cargo_at(mb, rng, site, "mine", -67.5, 9.0, D(20), 3.6)
    cargo_at(mb, rng, site, "yard", -113.0, 25.0, D(8), 3.6)
    mb.finish()


def story_east(rng, site):
    mb = PMB("PROP_Story_East", "08_PROPS", rng,
              remap={"Stone_Light": "Stone_Dark", "Water": "Metal_Dark", "Metal_Iron": "Metal_Dark",
                     "Coal_Rock": "Wood_Dark", "Cliff_Rock_Dark": "Wood_Dark", "Cloth_Navy": "Cloth_Red",
                     "Emblem_Cream": "Cloth_Canvas", "Crystal_Purple": "Crystal_Blue", "Metal_Brass": "Metal_Dark"})
    # poco com sarilho e horta cercada na margem leste
    q = site.place("poco", 84.0, 8.0, 3.0, 3.0)
    if q:
        K.well(mb, (q[0], q[1], F0), D(20), rng)
        col_box("Props", (5.0, 5.0, 5.0), (q[0], q[1], F0 + 2.5), (0, 0, D(20)))
    gx0, gy0, gx1, gy1 = 76.0, 20.0, 88.0, 30.0
    if site.why((gx0 + gx1) / 2, (gy0 + gy1) / 2, 5.5, route=1.8) is None:
        K.garden(mb, gx0, gy0, gx1, gy1, rng, "W")
        site.reserve((gx0 + gx1) / 2, (gy0 + gy1) / 2, 7.0)
        mb.box((0.35, 0.35, 5.2), (gx1 - 1.6, gy1 - 1.4, F0 + 2.6), (0, 0, 0.2), "Wood_Dark", 0.0)   # espantalho
        mb.box((3.0, 0.3, 0.3), (gx1 - 1.6, gy1 - 1.4, F0 + 4.1), (0, 0, 0.2), "Wood_Dark", 0.0)
        mb.box((1.3, 0.7, 1.7), (gx1 - 1.6, gy1 - 1.4, F0 + 3.6), (0, 0, 0.2), "Cloth_Canvas", 0.0)
        mb.cyl(0.9, 0.6, (gx1 - 1.6, gy1 - 1.4, F0 + 5.3), (0, 0, 0.2), "Wood_Plank", 6, r2=0.3, bevel=0.0)
    else:
        print("PLACE horta -> bloqueada (%s)" % site.why((gx0 + gx1) / 2, (gy0 + gy1) / 2, 5.5, route=1.8))
    # varal na frente do vao entre as cabanas East_A e East_B (roupa virada para o passeio da margem)
    K.clothesline(mb, (103.3, 1.2), (103.5, 14.2), rng, h=7.6)
    site.reserve(103.4, 7.7, 1.0)
    # bancos de frente para a roda d'agua (lugar de parada, fora das rotas)
    for (bx, by) in ((L.RIVER_X[1] + 7.0, L.WHEEL_C[1] - 16.0), (L.RIVER_X[1] + 7.0, L.WHEEL_C[1] - 25.0)):
        F = Frame(bx, by, F0 + 0.35, D(90))
        mb.box((5.0, 1.4, 0.35), F.p(0, 0, 1.6), F.r(), "Wood_Plank", 0.05)
        mb.box((5.0, 0.3, 1.2), F.p(0, 0.65, 2.6), F.r(), "Wood_Plank", 0.05)
        for sx in (-2.0, 2.0):
            mb.box((0.4, 1.4, 1.6), F.p(sx, 0, 0.8), F.r(), "Stone_Dark", 0.05)
        col_box("Props", (5.0, 1.6, 2.2), (bx, by, F0 + 1.45), F.r())
        site.reserve(bx, by, 2.6)
    signpost(mb, 74.0, -24.0, ((90, "portal"), (180, "forge")))
    site.reserve(74.0, -24.0, 1.0)
    df = door_frame("East_B")
    if df:
        p0, n = df
        K.leaning_tools(mb, p0 + Vector((-n.y, n.x, 0)) * 2.6, n, rng, ("pick",))
    # cargas por receita: rio (barris + corda) nas duas margens, cristais junto ao galpao, toras atras das cabanas
    cargo_at(mb, rng, site, "river", 71.4, -30.5, D(90), 3.2)
    cargo_at(mb, rng, site, "river", 50.5, -26.0, D(80), 3.0)
    cargo_at(mb, rng, site, "shed", 122.0, -20.5, D(5), 3.6)
    cargo_at(mb, rng, site, "yard", 106.0, 29.5, D(-12), 3.6)
    mb.finish()


# ================================================================== FUMACA DA TORRE (helper do Blender)
def smoke_mats():
    out = []
    for i, (c, a) in enumerate((((0.20, 0.19, 0.18), 0.62), ((0.36, 0.35, 0.34), 0.48), ((0.56, 0.55, 0.54), 0.36),
                                ((0.78, 0.78, 0.78), 0.24))):
        name = "Smoke_Puff_%d" % i
        m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
        m.use_nodes = True
        bs = m.node_tree.nodes.get("Principled BSDF")
        if bs:
            bs.inputs["Base Color"].default_value = (c[0], c[1], c[2], 1.0)
            bs.inputs["Roughness"].default_value = 1.0
            bs.inputs["Alpha"].default_value = a
        m.diffuse_color = (c[0], c[1], c[2], a)
        try:
            m.surface_render_method = "DITHERED"
        except Exception:
            pass
        out.append(name)
    return out


def smoke(rng):
    """pluma em 4 volumes (cada um um cacho de bolhas): coluna escura e estreita saindo da boca, abrindo e clareando
    para cima, derivando com o vento (+x +y). Semitransparente: nao le como pedra no topo das cameras."""
    names = smoke_mats()
    sm = MB("VFX_Chimney_Smoke", "12_VFX_HELPERS", rng)
    cx, cy = L.CHIMNEY
    z0 = L.CHIMNEY_TOP + 0.5
    wind = Vector((0.82, 0.57, 0.0))
    vols = ((0.0, 3.0, 3, 0, 1.5), (0.26, 5.5, 4, 1, 1.15), (0.58, 8.0, 5, 2, 1.0), (1.0, 11.0, 5, 3, 0.9))
    for f, r, nb, m, sz in vols:
        c = Vector((cx, cy, z0)) + wind * (f * f * 38.0 + f * 5.0) + Vector((0, 0, f * 48.0 + r * 0.9))
        for j in range(nb):
            a = j / nb * math.tau + rng.uniform(-0.4, 0.4)
            rad = 0.0 if j == 0 else r * rng.uniform(0.45, 0.7)
            off = Vector((math.cos(a) * rad, math.sin(a) * rad, rng.uniform(-0.35, 0.45) * r))
            if m == 0:
                off = Vector((rng.uniform(-0.6, 0.6), rng.uniform(-0.6, 0.6), j * r * 0.9))
            rr = r * (1.0 if j == 0 else rng.uniform(0.6, 0.85))
            sm.ico(rr, c + off + wind * (j * r * 0.18), names[m], 2, (1.0, 1.0, sz), jitter=0.25)
    ob = sm.finish()
    if ob:
        for pl in ob.data.polygons:
            pl.use_smooth = True


# ================================================================== BUILD
def build():
    rng = random.Random(1111)
    site = K.Site()
    C, W, E = lanterns(rng, site)
    arrival(C, rng, site)
    C.finish()
    W.finish()
    E.finish()
    story_west(rng, site)
    story_east(rng, site)
    smoke(rng)
    marker("VFX_Chimney_Smoke_Emitter", (L.CHIMNEY[0], L.CHIMNEY[1], L.CHIMNEY_TOP), (0, 0, 0), 4,
           props={"particle": "smoke", "rate": 6})
    marker("VFX_Forge_Sparks", (L.ANVIL[0], L.ANVIL[1], L.FL + 6), (0, 0, 0), 2, props={"particle": "sparks"})
    for key, px in zip(L.PORTAL_KEYS, L.PORTAL_X):
        marker("VFX_Portal_Swirl_%s" % key, (px, L.PORTAL_Y, L.TERR + 11.2), (0, 0, 0), 3,
               props={"anim": "girar espiral em Y, 30 graus/s"})
