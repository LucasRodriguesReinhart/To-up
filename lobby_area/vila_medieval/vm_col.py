# vm_col - COLISAO ANDAVEL e barreiras do lobby Vila Medieval (dono: V0/integracao). Tudo em caixas simples (COL_*,
# viram Parts invisiveis no montar). Pisos: sul do canal 6,0 | norte 7,0 | terraco do spawn 9,6 | loja e palco 6,4 |
# terraco dos portais 7,2 (degrau 6,6) | ponte da Ilha 1 6,0. Barreiras: muretas do canal/levada (ninguem cai na agua),
# contorno do plato (parede invisivel ate Y 18, aberta so no portao da ponte), guarda-corpos das pontes.
# As construcoes (casas, forja, loja, salao do ranking) criam a propria colisao no vm_blockout / vm_lib.house.
import math
import vm_lib as VL
from vm_lib import colr, colr_rot, col_poly_strips, B
import vm_layout as L
import fm_lib
from fm_lib import MB, col_ramp
import fm_parts as FP

BAR_H = 6.0          # altura das barreiras invisiveis acima do piso (pulo padrao ~7,2: a mureta do canal fica 6+1,1)


def south_poly():
    return VL.clip_box(L.PLATEAU, z0=L.CANAL_Z[1] + 1.0)        # z >= -5


def north_poly():
    return VL.clip_box(L.PLATEAU, z1=L.CANAL_Z[0] - 1.0)        # z <= -19


def ground():
    n = col_poly_strips("Ground", south_poly(), L.Y_PAVE, thick=4.0, step=8.0)
    race = (L.RACE_X[0] - 1.0, L.RACE_X[1] + 1.0, L.RACE_Z[1] - 1.0, L.RACE_Z[0])
    n += col_poly_strips("GroundN", north_poly(), L.Y_NORTH, thick=4.0, step=8.0, holes=[race])
    return n


def spawn():
    """terraco do spawn (9,6) + escadaria de 5 degraus para a praca (visual + rampa de colisao do fm_parts.stairs) +
    mureta em volta (aberta so na escada)"""
    col_poly_strips("Spawn", L.SPAWN_TERRACE, L.Y_SPAWN, thick=L.Y_SPAWN - L.Y_GRASS, step=4.0)
    st = L.SPAWN_STAIR
    mb = MB("VM_Town_SpawnStairs", "03_TOWN", detail="near")
    w = st["x1"] - st["x0"]
    FP.stairs(mb, "Spawn", tuple(B((st["x0"] + st["x1"]) / 2, st["z_foot"], L.Y_PAVE)), VL.yaw_b(0, 1), w, st["n"],
              st["rise"], st["run"], m="Stone_VM_Trim", side_m="Stone_VM_Base", stringers=True, col=True)
    mb.finish()
    pm = MB("VM_Town_SpawnParapet", "03_TOWN", detail="near")
    pts = [(st["x0"] - 1.2, 88), (-17, 88), (-20, 91), (-20, 109), (-17, 112), (17, 112), (20, 109), (20, 91), (17, 88),
           (st["x1"] + 1.2, 88)]
    # mureta 0,6 para DENTRO da borda (nada coplanar com a face do arrimo)
    inset = [(x * 0.97, 100 + (z - 100) * 0.95) for x, z in pts]
    FP.stone_parapet(pm, "SpawnPar", [tuple(B(x, z, L.Y_SPAWN)) for x, z in inset], h=1.4, w=1.0,
                     m="Stone_VM_Base", col=True)
    pm.finish()


def canal():
    """barreiras do canal (dos dois lados, menos na ponte) + rampas da ponte de pedra (6,0 -> 7,4 -> 7,0) + guarda-corpo"""
    z0, z1 = L.CANAL_Z
    x0, x1 = L.CANAL_X
    hw = L.STREET_HW + 2.0
    for a, b in ((x0, -hw), (hw, x1)):
        colr("Canal", (a, L.Y_PAVE, z1 + 0.0), (b, L.Y_PAVE + BAR_H, z1 + 1.0))          # muro sul (z -6 .. -5)
        colr("Canal", (a, L.Y_NORTH, z0 - 1.0), (b, L.Y_NORTH + BAR_H, z0))                 # muro norte (-19 .. -18)
    # levada da roda: muros dos dois lados e no fim
    rx0, rx1 = L.RACE_X
    colr("Race", (rx0 - 1.0, L.Y_NORTH, L.RACE_Z[1] - 1.0), (rx0, L.Y_NORTH + BAR_H, z0))
    colr("Race", (rx1, L.Y_NORTH, L.RACE_Z[1] - 1.0), (rx1 + 1.0, L.Y_NORTH + BAR_H, z0))
    colr("Race", (rx0 - 1.0, L.Y_NORTH, L.RACE_Z[1] - 1.0), (rx1 + 1.0, L.Y_NORTH + BAR_H, L.RACE_Z[1]))
    # ponte: duas rampas (metade sul sobe 1,4; metade norte desce 0,4) na largura da rua
    zs, zn = L.BRIDGE_Z
    zc = (zs + zn) / 2
    w = 2 * L.STREET_HW
    col_ramp("Bridge", B(0, zs, L.Y_PAVE), B(0, zc, L.BRIDGE_CROWN), w, thick=1.0)
    col_ramp("Bridge", B(0, zc, L.BRIDGE_CROWN), B(0, zn, L.Y_NORTH), w, thick=1.0)
    for s in (-1, 1):
        colr("Bridge", (s * L.STREET_HW if s > 0 else -hw, L.Y_PAVE, zn), (hw if s > 0 else -L.STREET_HW,
                                                                            L.BRIDGE_CROWN + BAR_H, zs))


def services():
    """pisos da loja (6,4) e do palco do ranking (6,4, girado)"""
    x0, x1, z0, z1 = L.SHOP
    colr("ShopFloor", (x0, L.Y_SHOP - 3.0, z0), (x1, L.Y_SHOP, z1))
    fx, fz = L.RANK_FACE
    n = math.hypot(fx, fz)
    fx, fz = fx / n, fz / n
    ox, oz = L.RANK_O
    c = (ox + fx * 7.0, oz + fz * 7.0)
    # caixa: comprimento ao longo da TANGENTE (58), profundidade ao longo do olhar (20)
    colr_rot("Rank", c[0], c[1], L.Y_RANK - 1.5, 58.0, 20.0, 3.0, -fz, fx)


def court():
    """terraco em semicirculo dos portais (7,2) e o degrau de 6,6 no pe (caixas giradas a cada 5 graus)"""
    cx, cz = L.COURT_C
    r0, r1, a0, a1 = L.COURT_RING
    a = a0
    while a < a1 - 0.01:
        b = min(a1, a + 5.0)
        am = math.radians((a + b) / 2)
        ux, uz = math.cos(am), math.sin(am)
        rm = (r0 + 1.0 + r1) / 2
        wt = 2 * r1 * math.sin(math.radians((b - a) / 2)) * 1.06
        colr_rot("Court", cx + ux * rm, cz + uz * rm, L.Y_PORTAL - 1.5, r1 - r0 - 1.0, wt, 3.0, ux, uz)
        wi = 2 * (r0 + 1.2) * math.sin(math.radians((b - a) / 2)) * 1.3
        colr_rot("CourtStep", cx + ux * (r0 + 0.5), cz + uz * (r0 + 0.5), L.Y_PORTAL - 0.6 - 1.5, 1.2, wi, 3.0, ux, uz)
        a = b


def isle_bridge():
    """ponte da Ilha 1: tabuleiro em 6,0 por trecho (caixas giradas), guarda-corpo invisivel ate Y 12 dos dois lados
    e o patamar final na largura da praca da ilha (x +-12, z 213..222)"""
    P = L.ISLE_BRIDGE[:-1]                      # o ultimo trecho (z 213..222) e o patamar
    w = L.ISLE_BRIDGE_W
    for (ax, az), (bx, bz) in zip(P, P[1:]):
        dx, dz = bx - ax, bz - az
        ln = math.hypot(dx, dz)
        ux, uz = dx / ln, dz / ln
        cx, cz = (ax + bx) / 2, (az + bz) / 2
        colr_rot("IsleBridge", cx, cz, L.Y_ISLE - 1.5, ln + 1.0, w, 3.0, ux, uz)
        for s in (-1, 1):
            nx, nz = -uz * s, ux * s
            colr_rot("IsleBridgeBar", cx + nx * (w / 2 + 0.6), cz + nz * (w / 2 + 0.6), L.Y_ISLE + 3.0, ln + 0.6, 1.2,
                     6.0, ux, uz)
    x0, x1, z0, z1 = L.ISLE_LANDING
    colr("IsleLanding", (x0, L.Y_ISLE - 3.0, z0 - 0.5), (x1, L.Y_ISLE, z1 + 0.5))
    for x in (x0 - 1.2, x1):
        colr("IsleLandingBar", (x, L.Y_ISLE, z0 - 0.5), (x + 1.2, L.Y_ISLE + 6.0, z1))


def perimeter():
    """parede invisivel no contorno do plato (Y -2 .. 18), com a abertura do portao (x 42..58 na borda sul)"""
    P = L.PLATEAU
    gx0, gx1 = L.GATE[0] - L.GATE_HW - 1.0, L.GATE[0] + L.GATE_HW + 1.0
    n = 0
    for i in range(len(P)):
        a, b = P[i], P[(i + 1) % len(P)]
        segs = [(a, b)]
        if abs(a[1] - b[1]) < 0.5 and min(a[0], b[0]) < gx0 and max(a[0], b[0]) > gx1 and a[1] > 140:
            lo, hi = (a, b) if a[0] < b[0] else (b, a)
            segs = [(lo, (gx0, lo[1])), ((gx1, hi[1]), hi)]
        for p, q in segs:
            dx, dz = q[0] - p[0], q[1] - p[1]
            ln = math.hypot(dx, dz)
            if ln < 0.5:
                continue
            colr_rot("Edge", (p[0] + q[0]) / 2, (p[1] + q[1]) / 2, 8.0, ln + 1.5, 2.0, 20.0, dx / ln, dz / ln)
            n += 1
    return n


def build():
    n = ground()
    spawn()
    canal()
    services()
    court()
    isle_bridge()
    e = perimeter()
    tot = sum(1 for o in fm_lib.bpy.data.objects if o.name.startswith("COL_"))
    print("COL: %d faixas de piso, %d trechos de contorno, %d COL no total (andavel + barreiras)" % (n, e, tot))
