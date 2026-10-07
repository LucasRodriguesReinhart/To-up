# db_blockout - BLOCKOUT da Ilha 2 (Dragon Ball), zona por zona, com a paleta final em formas simples.
# Cada zona cria: massas visuais (detail="far"), a colisao dos PROPRIOS volumes (predios, torres, rochas soltas) e os
# marcadores obrigatorios da zona. O chao, as escadas e as guardas sao do db_core/db_col (sempre).
# O modulo de detalhe de uma zona SUBSTITUI a funcao dela aqui (build(skip={...})).
import math, random
import db_lib as DL
from db_lib import MB, col_box, col_box2, mk, yaw_to, ring_band, dome, blob_poly, octo_col, prism, Frame
import db_layout as L
import db_col

ZONES = ["terrain", "mining", "entrance", "capsule", "village", "towers", "summon", "water", "exit", "dressing"]


# ------------------------------------------------------------------ terreno: massa da ilha, terracos, mesas
def _notch_r(a):
    """raio do recorte da escadaria da chegada na direcao a (graus)"""
    s = math.sin(math.radians(a))
    c = math.cos(math.radians(a))
    if s >= -0.2:
        return 1e9
    r = -L.ENTRY_STAIR_Y1 / -s if s < 0 else 1e9
    x = r * c
    hw = L.ENTRY_STAIR_W / 2 + 1.4
    return r if abs(x) <= hw else 1e9


def terrain():
    rng = random.Random(11)
    mb = MB("DB_Ter_Blockout_Ground", "02_TERRAIN", rng, detail="far", floor=-999)
    ring_band(mb, lambda a: L.arena_r(a) + 1.0, lambda a: min(DL.rim_r(a), _notch_r(a)), L.GROUND - 10.0, L.GROUND,
              "Sand_DB", step=2.0, wall_m="Cliff_Rock_DB")
    # canteiros verdes e caminhos radiais pavimentados
    for x, y, r in L.GARDENS:
        z = L.zone_of(x, y)
        mb.prism(DL.ccw(blob_poly(x, y, r, 12, rng, 0.22)), z - 0.2, z + 0.06, "Grass_DB")
    for pts, w in L.GROUND_PATHS:
        mb.prism(DL.ribbon_poly(pts, w / 2), L.GROUND - 0.2, L.GROUND + 0.1, "Stone_Paving_DB")
    # rochedos medios do plato
    for x, y, r, h in L.PLATEAU_ROCKS:
        z = L.zone_of(x, y)
        mb.prism(DL.ccw(blob_poly(x, y, r, 9, rng, 0.2)), z - 0.5, z + h * 0.7, "Cliff_Rock_DB")
        mb.prism(DL.ccw(blob_poly(x, y, r * 0.72, 8, rng, 0.2)), z + h * 0.7, z + h, "Cliff_Rock_DB_Top")
    mb.finish()
    # massa inferior (ilha flutuante): cones empilhados irregulares
    mu = MB("DB_Ter_Blockout_Under", "02_TERRAIN", rng, detail="far", floor=-999)
    rim = DL.rim()
    cx = sum(p[0] for p in rim) / len(rim)
    cy = sum(p[1] for p in rim) / len(rim)
    bands = [(L.GROUND - 10.0, 0.98, -14.0, "Cliff_Rock_DB"), (-14.0, 0.86, -44.0, "Cliff_Rock_DB_Dark"),
             (-44.0, 0.62, -78.0, "Cliff_Rock_DB"), (-78.0, 0.34, -104.0, "Cliff_Rock_DB_Dark")]
    for z1, f, z0, m in bands:
        pts = [(cx + (x - cx) * f * rng.uniform(0.97, 1.02), cy + (y - cy) * f * rng.uniform(0.97, 1.02))
               for x, y in rim[::2]]
        mu.prism(DL.ccw(pts), z0, z1, m)
    mu.finish()
    # terracos
    mt = MB("DB_Ter_Blockout_Terraces", "02_TERRAIN", rng, detail="far", floor=-999)
    prism(mt, DL.hub_poly(), L.GROUND - 10.0, L.HUB, "Stone_DB_Block", top_m="Grass_DB")
    prism(mt, DL.cap_poly(), L.HUB - 1.0, L.CAP, "Stone_DB_Block", top_m="Stone_Paving_DB")
    prism(mt, DL.summon_poly(), L.GROUND - 10.0, L.SUM, "Cliff_Rock_DB", top_m="Stone_Paving_DB")
    for rp in DL.exit_shelf_polys():
        prism(mt, rp, L.GROUND - 10.0, L.EXIT_Z, "Cliff_Rock_DB", top_m="Sand_DB")
    mt.finish()
    # mesas / pilares / agulhas: silhueta vertical (PRIMARY/SECONDARY) - 3 tambores afinando + tampo
    mm = MB("DB_Ter_Blockout_Mesas", "02_TERRAIN", rng, detail="far", floor=-999)
    for x, y, r, top, kind in L.MESAS:
        inside = DL.L.point_in_poly(x, y, L.ISLAND_RIM)
        z0 = -40.0 if not inside else L.GROUND - 10.0
        taper = {"mesa": (1.0, 0.94, 0.88), "pillar": (1.0, 0.86, 0.74), "spire": (1.0, 0.72, 0.48)}[kind]
        h = top - z0
        zs = [z0, z0 + h * 0.45, z0 + h * 0.8, top]
        for k in range(3):
            poly = blob_poly(x, y, r * taper[k], 10, rng, 0.14, rng.uniform(0, 6.28))
            mm.prism(DL.ccw(poly), zs[k], zs[k + 1], "Cliff_Rock_DB" if k != 1 else "Cliff_Rock_DB_Dark")
        cap = blob_poly(x, y, r * taper[2] * 1.02, 10, rng, 0.1)
        mm.prism(DL.ccw(cap), top - 0.8, top + 0.6, "Cliff_Rock_DB_Top")
        if kind == "mesa":
            mm.prism(DL.ccw(blob_poly(x, y, r * taper[2] * 0.8, 9, rng, 0.2)), top + 0.6, top + 1.2, "Grass_DB")
    mm.finish()


# ------------------------------------------------------------------ mineracao: bacia, promenade, acessos, rochas, pod
def mining():
    rng = random.Random(21)
    mb = MB("DB_Mine_Blockout", "03_MINING_ZONE", rng, detail="far", floor=-999)
    mb.prism(DL.arena(), L.ARENA - 6.0, L.ARENA, "Sand_DB")
    # muro de arrimo da bacia (visto de dentro da arena)
    ring_band(mb, lambda a: L.arena_r(a) - 0.2, lambda a: L.arena_r(a) + 1.2, L.ARENA - 0.2, L.GROUND + 0.05,
              "Stone_DB_Block", step=3.0)
    # promenade (calcamento claro)
    ring_band(mb, lambda a: L.arena_r(a) + 1.2, L.prom_r, L.GROUND - 0.3, L.GROUND + 0.08, "Stone_Paving_DB",
              step=3.0, walls=(False, True))
    # acessos
    for nm, base, ang, w, n, rise, tread, g in db_col.stair_list():
        if nm.startswith("Arena"):
            DL.vis_stairs(mb, base, ang, w, n, rise, tread, "Stone_Paving_DB", "Stone_DB_Block", stringers=False)
    for aa, w, kind in L.ARENA_ACCESS:
        if kind == "ramp":
            foot, top, d = L.access_frame(aa)
            a = math.atan2(-d[1], -d[0])
            Ln = L.RAMP_RUN
            c = ((foot[0] + top[0]) / 2, (foot[1] + top[1]) / 2)
            mb.box((Ln + 1.0, w, 1.0), (c[0], c[1], (L.ARENA + L.GROUND) / 2 - 0.4),
                   (0, -math.atan2(L.GROUND - L.ARENA, Ln), a), "Cliff_Rock_DB_Top", 0.0)
    # guarda baixa (visual) com os vaos dos acessos
    def gap(ang):
        for aa, w, kind in L.ARENA_ACCESS:
            if abs((ang - aa + 180) % 360 - 180) <= math.degrees((w / 2 + 0.5) / L.arena_r(aa)):
                return True
        return False
    run = []
    for i in range(181):
        a = i * 2.0
        r = L.arena_r(a) + 0.7
        p = (r * math.cos(math.radians(a)), r * math.sin(math.radians(a)), L.GROUND)
        if gap(a):
            if len(run) > 1:
                DL.vis_parapet(mb, run, h=1.3, w=0.9, m="Plaster_DB_White", cap_m="Roof_DB_Blue")
            run = []
        else:
            run.append(p)
    if len(run) > 1:
        DL.vis_parapet(mb, run, h=1.3, w=0.9, m="Plaster_DB_White", cap_m="Roof_DB_Blue")
    # rochas da arena
    for x, y, r, h in L.ARENA_ROCKS:
        mb.prism(DL.ccw(blob_poly(x, y, r, 9, rng, 0.2)), L.ARENA - 0.5, L.ARENA + h * 0.7, "Cliff_Rock_DB")
        mb.prism(DL.ccw(blob_poly(x, y, r * 0.75, 8, rng, 0.2)), L.ARENA + h * 0.7, L.ARENA + h, "Cliff_Rock_DB_Top")
    # pod de sondagem central
    x, y, r = L.CORE_POD
    mb.cyl(r, 2.0, (x, y, L.ARENA + 1.0), m="Plaster_DB_White", n=16, bevel=0.0)
    dome(mb, (x, y), r, L.ARENA + 2.0, "Plaster_DB_White", n=16, rings=5, squash=0.8)
    mb.cyl(r + 0.25, 0.5, (x, y, L.ARENA + 2.2), m="Roof_DB_Blue", n=16, bevel=0.0)
    mb.finish()


# ------------------------------------------------------------------ entrada: ponte, escadaria, portal Capsule
def entrance():
    rng = random.Random(31)
    mb = MB("DB_Ent_Blockout", "02_TERRAIN", rng, detail="far", floor=-999)
    hw = L.DECK_W / 2
    Ln = L.BRIDGE_Y1 - L.BRIDGE_Y0
    cy = (L.BRIDGE_Y0 + L.BRIDGE_Y1) / 2
    mb.box((L.DECK_W, Ln, 2.0), (0, cy, L.DECK - 1.0), m="Stone_Paving_DB", bevel=0.0)
    for s in (-1, 1):
        mb.box((1.0, Ln, 1.4), (s * (hw + 0.5), cy, L.DECK + 0.7), m="Stone_DB_Block", bevel=0.0)
    for k in range(3):
        y = L.BRIDGE_Y0 + 10.0 + k * (Ln - 20.0) / 2
        mb.box((6.0, 6.0, 40.0), (0, y, L.DECK - 22.0), m="Cliff_Rock_DB", bevel=0.0)
    # escadaria (chegada -> praca) + paredes do recorte
    for nm, base, ang, w, n, rise, tread, g in db_col.stair_list():
        if nm == "Entry":
            DL.vis_stairs(mb, base, ang, w, n, rise, tread, "Stone_Paving_DB", "Stone_DB_Block")
    # praca da entrada
    x0, y0, x1, y1 = L.ENTRY_PLAZA
    mb.box2((x0, y0, L.GROUND - 0.3), (x1, y1, L.GROUND + 0.08), m="Stone_Paving_DB", bevel=0.0)
    # portal Capsule: pilares azul-marinho + arco branco + emblema
    g = L.GATE_Y
    ow = L.GATE_OPEN_W
    for s in (-1, 1):
        mb.box((4.0, 5.0, L.GATE_OPEN_H + 2.0), (s * (ow / 2 + 2.0), g, L.GROUND + (L.GATE_OPEN_H + 2.0) / 2),
               m="Plaster_DB_Navy", bevel=0.0)
        mb.box((6.0, 7.0, 1.2), (s * (ow / 2 + 2.0), g, L.GROUND + 0.6), m="Stone_DB_Block", bevel=0.0)
        col_box("DB_EntGate", (4.2, 5.2, L.GATE_OPEN_H + 2.0), (s * (ow / 2 + 2.0), g, L.GROUND + (L.GATE_OPEN_H + 2.0) / 2))
    mb.box((ow + 12.0, 6.0, 4.0), (0, g, L.GROUND + L.GATE_OPEN_H + 2.0), m="Plaster_DB_White", bevel=0.0)
    mb.box((ow + 13.0, 6.4, 0.8), (0, g, L.GROUND + L.GATE_OPEN_H + 4.2), m="Roof_DB_Blue", bevel=0.0)
    mb.cyl(3.6, 0.8, (0, g - 3.2, L.GROUND + L.GATE_OPEN_H + 2.2), (math.pi / 2, 0, 0), "Roof_DB_Blue", 20, bevel=0.0)
    mb.finish()


# ------------------------------------------------------------------ Capsule (heroi, entravel)
def capsule():
    rng = random.Random(41)
    mb = MB("DB_Cap_Blockout", "04_CAPSULE_LANDMARK", rng, detail="far", floor=-999)
    cx, cy = L.CAPSULE_C
    R = L.CAPSULE_R
    z = L.CAP
    mb.cyl(R, 10.0, (cx, cy, z + 5.0), m="Plaster_DB_White", n=36, bevel=0.0)
    mb.cyl(R + 0.3, 2.0, (cx, cy, z + 9.0), m="Roof_DB_Blue", n=36, bevel=0.0)
    dome(mb, (cx, cy), R, z + 10.0, "Plaster_DB_White", n=36, rings=9, squash=0.75)
    dome(mb, (cx, cy), 8.0, z + 10.0 + R * 0.75 - 1.5, "Roof_DB_Blue", n=16, rings=4, squash=0.6)
    # pavilhao de entrada (foyer) com vao da porta
    x0, y0, x1, y1 = L.CAPSULE_FOYER
    dw = L.CAPSULE_DOOR_W / 2
    H = 14.0
    mb.box2((x0, y0, z), (x0 + 1.2, y1, z + H), m="Plaster_DB_White", bevel=0.0)       # parede oeste
    mb.box2((x1 - 1.2, y0, z), (x1, y1, z + H), m="Plaster_DB_White", bevel=0.0)       # parede leste
    mb.box2((x0, y0, z), (-dw, y0 + 1.2, z + H), m="Plaster_DB_White", bevel=0.0)      # frente, lado oeste do vao
    mb.box2((dw, y0, z), (x1, y0 + 1.2, z + H), m="Plaster_DB_White", bevel=0.0)       # frente, lado leste do vao
    mb.box2((x0, y0, z + L.CAPSULE_DOOR_H), (x1, y1, z + H + 1.0), m="Plaster_DB_White", bevel=0.0)
    mb.box2((x0 - 0.5, y0 - 0.5, z + H + 1.0), (x1 + 0.5, y1, z + H + 2.0), m="Roof_DB_Blue", bevel=0.0)
    # anexos
    for ax, ay, ar in L.CAPSULE_ANNEX:
        mb.cyl(ar, 8.0, (ax, ay, z + 4.0), m="Plaster_DB_White", n=24, bevel=0.0)
        dome(mb, (ax, ay), ar, z + 8.0, "Roof_DB_Blue", n=24, rings=6, squash=0.7)
        octo_col("DB_CapAnnex", ax, ay, ar, z, z + 14.0)
    mb.finish()
    # colisao entravel: foyer (paredes com vao), corredor, anel do salao e casca da cupula (vao no corredor)
    A = "DB_CapShell"
    col_box2(A, (x0, y0, z), (x0 + 1.2, y1, z + H))
    col_box2(A, (x1 - 1.2, y0, z), (x1, y1, z + H))
    col_box2(A, (x0, y0, z), (-dw, y0 + 1.2, z + H))
    col_box2(A, (dw, y0, z), (x1, y0 + 1.2, z + H))
    c0, c1 = L.CAPSULE_CORRIDOR[1], L.CAPSULE_CORRIDOR[3]
    cw = L.CAPSULE_CORRIDOR[2]
    for s in (-1, 1):
        col_box2(A, (s * cw, c0, z), (s * (cw + 1.2), c1 + 0.6, z + H))
    for rr, nseg in ((L.CAPSULE_HALL_R + 0.6, 36), (R - 0.6, 44)):
        for i in range(nseg):
            a0 = 2 * math.pi * i / nseg
            a1 = 2 * math.pi * (i + 1) / nseg
            am = (a0 + a1) / 2
            px, py = cx + rr * math.cos(am), cy + rr * math.sin(am)
            if py < cy and abs(px - cx) < cw + 0.2:
                continue                        # vao do corredor (frente sul)
            w = 2 * rr * math.sin((a1 - a0) / 2) + 0.4
            col_box(A, (1.2, w, 20.0), (px, py, z + 10.0), (0, 0, am))
    mk("NPC_Capsule", (cx, cy + 12.0, z), (0, 0, math.pi), 1.5, "SPHERE",
       props={"floor": z, "note": "balcao da recepcao Capsule (fundo do salao)"})
    mk("PLAYER_INTERACT_Capsule", (cx, cy + 6.0, z), (0, 0, 0), 1.5, "SPHERE", props={"floor": z})


# ------------------------------------------------------------------ vila tech: casas-capsula, mercado marcial, oficina, pods, dojo
def village():
    rng = random.Random(51)
    mb = MB("DB_Hub_Blockout", "05_TECH_VILLAGE", rng, detail="far", floor=-999)
    for x, y, r, kind in L.HUB_LOTS:
        z = L.HUB
        if kind.startswith("capsule_house"):
            mb.cyl(r, 7.0, (x, y, z + 3.5), m="Plaster_DB_White", n=24, bevel=0.0)
            mb.cyl(r + 0.2, 1.0, (x, y, z + 5.5), m="Roof_DB_Blue", n=24, bevel=0.0)
            dome(mb, (x, y), r, z + 7.0, "Plaster_DB_White" if kind.endswith("A") else "Roof_DB_Blue", n=24, rings=6,
                 squash=0.8)
            octo_col("DB_HubHouse", x, y, r, z, z + 12.0)
        elif kind == "martial_market":
            # pavilhao aberto (frente sul): postes, balcao, telhado laranja
            for sx in (-1, 1):
                for sy in (-1, 1):
                    mb.box((1.0, 1.0, 8.0), (x + sx * (r - 1.5), y + sy * (r * 0.6 - 1.0), z + 4.0), m="Wood_Lacquer_Red",
                           bevel=0.0)
                    col_box("DB_HubMarket", (1.2, 1.2, 8.0), (x + sx * (r - 1.5), y + sy * (r * 0.6 - 1.0), z + 4.0))
            mb.box((r * 1.4, 2.0, 3.0), (x, y - r * 0.2, z + 1.5), m="Wood_Dark", bevel=0.0)
            col_box("DB_HubMarket", (r * 1.4, 2.0, 3.0), (x, y - r * 0.2, z + 1.5))
            mb.gable_roof(x, y, r * 2.2, r * 1.4, z + 8.0, 4.0, m="Roof_DB_Orange", thick=0.8, over=1.2, axis="X")
            mk("NPC_Market", (x, y + 1.5, z), (0, 0, math.pi), 1.5, "SPHERE", props={"floor": z})
            mk("PLAYER_INTERACT_Market", (x, y - r * 0.2 - 3.0, z), (0, 0, 0), 1.5, "SPHERE", props={"floor": z})
        elif kind == "workshop":
            w, d, h = r * 2.0, r * 1.6, 10.0
            for s in (-1, 1):
                mb.box((1.2, d, h), (x + s * w / 2, y, z + h / 2), m="Plaster_DB_White", bevel=0.0)
                col_box("DB_HubWorkshop", (1.2, d, h), (x + s * w / 2, y, z + h / 2))
            mb.box((w, 1.2, h), (x, y + d / 2, z + h / 2), m="Plaster_DB_White", bevel=0.0)
            col_box("DB_HubWorkshop", (w, 1.2, h), (x, y + d / 2, z + h / 2))
            mb.box((w + 2.0, d + 2.0, 1.2), (x, y, z + h + 0.6), m="Roof_DB_Blue", bevel=0.0)
            mb.box((w * 0.6, 2.0, 3.2), (x, y + d / 2 - 2.0, z + 1.6), m="Metal_DB_Dark", bevel=0.0)
            mk("NPC_Workshop", (x, y + d / 2 - 4.0, z), (0, 0, math.pi), 1.5, "SPHERE", props={"floor": z})
            mk("PLAYER_INTERACT_Workshop", (x, y - d / 2 + 3.0, z), (0, 0, 0), 1.5, "SPHERE", props={"floor": z})
    for x, y, r in L.PODS:
        z = L.zone_of(x, y)
        mb.cyl(r, 3.0, (x, y, z + 1.5), m="Plaster_DB_White", n=16, bevel=0.0)
        dome(mb, (x, y), r, z + 3.0, "Roof_DB_Blue", n=16, rings=5, squash=0.85)
        octo_col("DB_HubPod", x, y, r, z, z + 8.0)
    for x, y, r, kind in L.GROUND_LOTS:
        if kind == "dojo":
            z = L.GROUND
            w, d = r * 2.0, r * 1.5
            mb.box((w, d, 1.0), (x, y, z + 0.5), m="Stone_DB_Block", bevel=0.0)
            for sx in (-1, 1):
                for sy in (-1, 1):
                    mb.box((1.2, 1.2, 9.0), (x + sx * (w / 2 - 1.0), y + sy * (d / 2 - 1.0), z + 5.5), m="Wood_Lacquer_Red",
                           bevel=0.0)
                    col_box("DB_HubDojo", (1.4, 1.4, 9.0), (x + sx * (w / 2 - 1.0), y + sy * (d / 2 - 1.0), z + 5.5))
            mb.box((w, 1.0, 9.0), (x + w * 0.0, y + d / 2 - 0.5, z + 5.5), m="Plaster_Cream", bevel=0.0)
            col_box("DB_HubDojo", (w, 1.2, 9.0), (x, y + d / 2 - 0.5, z + 5.5))
            mb.gable_roof(x, y, w + 3.0, d + 3.0, z + 10.0, 4.5, m="Roof_DB_Orange", thick=0.8, over=1.5, axis="Y")
    mb.finish()


# ------------------------------------------------------------------ torres, satelites, passarelas de vidro, heliponto
def towers():
    rng = random.Random(61)
    mb = MB("DB_Twr_Blockout", "05_TECH_VILLAGE", rng, detail="far", floor=-999)
    tops = {}
    for x, y, r, kind, walk in L.TOWER_SITES:
        z = L.GROUND if walk else L.zone_of(x, y)
        if walk:
            # plataforma satelite (andavel) sobre pilar de rocha + ponte curta
            mb.cyl(r, 1.2, (x, y, z - 0.6), m="Stone_Paving_DB", n=24, bevel=0.0)
            mb.cyl(r * 0.8, 40.0, (x, y, z - 21.0), m="Cliff_Rock_DB", n=12, r2=r * 0.3, bevel=0.0)
            a0, a1 = L.SAT_BRIDGES[kind]
            d = math.hypot(a1[0] - a0[0], a1[1] - a0[1])
            ang = math.atan2(a1[1] - a0[1], a1[0] - a0[0])
            mb.box((d + 2.0, L.SAT_BRIDGE_W, 1.2), ((a0[0] + a1[0]) / 2, (a0[1] + a1[1]) / 2, z - 0.6), (0, 0, ang),
                   "Stone_Paving_DB", 0.0)
            # torre-mirante na ponta de fora da plataforma
            ox, oy = x + (x - a1[0]) / max(1e-3, math.hypot(x - a1[0], y - a1[1])) * (r - 2.2), \
                y + (y - a1[1]) / max(1e-3, math.hypot(x - a1[0], y - a1[1])) * (r - 2.2)
            mb.cyl(1.2, 16.0, (ox, oy, z + 8.0), m="Plaster_DB_White", n=10, bevel=0.0)
            mb.cyl(3.4, 1.4, (ox, oy, z + 16.5), m="Roof_DB_Blue", n=16, bevel=0.0)
            octo_col("DB_TwrSat", ox, oy, 1.4, z, z + 16.0)
            continue
        H = {"comm": 52.0, "lookout": 40.0, "energy": 30.0}[kind]
        mb.cyl(r, 1.0, (x, y, z + 0.5), m="Stone_Paving_DB", n=20, bevel=0.0)
        mb.cyl(2.4, H, (x, y, z + H / 2), m="Plaster_DB_White", n=14, bevel=0.0)
        if kind == "comm":
            mb.cyl(5.0, 2.4, (x, y, z + H * 0.7), m="Roof_DB_Blue", n=18, bevel=0.0)
            mb.cyl(0.4, 10.0, (x, y, z + H + 5.0), m="Metal_DB_Steel", n=6, bevel=0.0)
            dome(mb, (x + 3.0, y), 3.5, z + H * 0.85, "Metal_DB_Steel", n=12, rings=3, squash=0.5)
        elif kind == "lookout":
            mb.cyl(7.5, 3.0, (x, y, z + H), m="Plaster_DB_White", n=24, bevel=0.0)
            dome(mb, (x, y), 7.5, z + H + 1.5, "Glass_DB_Blue", n=24, rings=5, squash=0.55)
            mb.cyl(7.8, 0.8, (x, y, z + H - 1.2), m="Roof_DB_Blue", n=24, bevel=0.0)
        else:
            mb.ico(4.0, (x, y, z + H + 3.0), "DB_Cyan_Glow", 2)
            for k in range(3):
                mb.cyl(3.2 - k * 0.5, 0.8, (x, y, z + H * (0.5 + 0.15 * k)), m="Metal_DB_Dark", n=14, bevel=0.0)
        octo_col("DB_Twr", x, y, 2.6, z, z + H)
        tops[kind] = (x, y, z)
    # passarelas de vidro (so visuais, no alto): anexos do Capsule -> torres
    for (ax, ay, ar), kind in zip(L.CAPSULE_ANNEX, ("comm", "lookout")):
        if kind in tops:
            tx, ty, tz = tops[kind]
            za = L.CAP + 10.0
            mb.tube([(ax, ay, za), ((ax + tx) / 2, (ay + ty) / 2, za + 3.0), (tx, ty, za)], 2.6, "Glass_DB_Blue", 12)
            for f in (0.33, 0.66):
                px, py = ax + (tx - ax) * f, ay + (ty - ay) * f
                mb.cyl(0.8, za - L.HUB, (px, py, (za + L.HUB) / 2), m="Metal_DB_Steel", n=8, bevel=0.0)
    # heliponto Capsule (chao)
    for x, y, r, kind in L.GROUND_LOTS:
        if kind == "landing_pad":
            mb.cyl(r, 0.6, (x, y, L.GROUND + 0.3), m="Metal_DB_Dark", n=28, bevel=0.0)
            mb.cyl(r * 0.7, 0.62, (x, y, L.GROUND + 0.32), m="Roof_DB_Blue", n=28, bevel=0.0)
            mb.cyl(r * 0.55, 0.64, (x, y, L.GROUND + 0.34), m="Metal_DB_Dark", n=28, bevel=0.0)
    mb.finish()


# ------------------------------------------------------------------ summon (a mesma familia da Ilha 1, area adaptada)
def summon_frame():
    face = math.radians(L.SUMMON_FACE_DEG)
    return Frame(L.SUMMON_TOWER[0], L.SUMMON_TOWER[1], L.SUM, face - math.pi / 2)


def summon():
    rng = random.Random(71)
    mb = MB("DB_Sum_Blockout", "06_SUMMON", rng, detail="far", floor=-999)
    cx, cy = L.SUMMON_C
    mb.cyl(L.SUMMON_R - 0.5, 0.3, (cx, cy, L.SUM + 0.15), m="Stone_Paving_DB", n=40, bevel=0.0)
    mb.cyl(L.SUMMON_R * 0.45, 0.32, (cx + 4.0, cy - 1.0, L.SUM + 0.17), m="Summon_Floor", n=32, bevel=0.0)
    F = summon_frame()
    mb.box((22.0, 14.0, 30.0), F.p(0, -2.0, 15.0), F.r(), "Stone_SumBlock" if "Stone_SumBlock" in DL.MATS else "Summon_Stone", 0.0)
    mb.box((10.0, 1.0, 12.0), F.p(0, 5.1, 7.0), F.r(), "Summon_Blue_Glow", 0.0)
    mb.ico(7.5, F.p(0, -2.0, 38.0), "Metal_Gold", 1, scale=(1, 1, 1))
    mb.ico(3.6, F.p(0, -2.0, 38.0), "Summon_Star_Glow", 1)
    mb.finish()
    col_box("DB_SumTower", (22.0, 14.0, 30.0), F.p(0, -2.0, 15.0), F.r())
    ux, uy = math.cos(math.radians(L.SUMMON_FACE_DEG)), math.sin(math.radians(L.SUMMON_FACE_DEG))
    yaw = yaw_to(ux, uy)
    base = F.p(0, 0, 0)
    mk("SUMMON_Main", (base.x, base.y, L.SUM), (0, 0, yaw), 3.0, "ARROWS",
       props={"face_deg": L.SUMMON_FACE_DEG, "note": "raiz da torre de invocacao (+Y local = frente)"})
    it = F.p(0, 7.5, 0)
    mk("SUMMON_Interact", (it.x, it.y, L.SUM + 0.1), (0, 0, yaw), 2.0, "SPHERE", props={"radius": 6.0})
    pp = F.p(0, 11.5, 0)
    mk("SUMMON_PlayerPosition", (pp.x, pp.y, L.SUM + 0.1), (0, 0, yaw + math.pi), 2.0, "ARROWS", props={})


# ------------------------------------------------------------------ agua: 3 pocos, 2 quedas pela borda, cascata NW
def water():
    rng = random.Random(81)
    mb = MB("DB_Water_Blockout", "07_WATER", rng, detail="far", floor=-999)
    for (px, py, pr), fall in ((L.POOL_SW, L.FALL_SW), (L.POOL_SE, L.FALL_SE)):
        zw = L.GROUND - L.WATER_DROP
        mb.cyl(pr, 1.0, (px, py, zw - 0.5), m="Water_DB", n=24, bevel=0.0)
        d = math.hypot(fall[0] - px, fall[1] - py)
        a = math.atan2(fall[1] - py, fall[0] - px)
        mb.box((d, 4.4, 1.0), ((px + fall[0]) / 2, (py + fall[1]) / 2, zw - 0.5), (0, 0, a), "Water_DB", 0.0)
        ox, oy = fall[0] + math.cos(a) * 2.0, fall[1] + math.sin(a) * 2.0
        mb.box((1.2, 5.0, zw + 70.0), (ox, oy, (zw - 70.0) / 2), (0, 0, a), "Water_Fall", 0.0)
    px, py, pr = L.POOL_NW
    zw = L.HUB - L.WATER_DROP
    mb.cyl(pr, 1.0, (px, py, zw - 0.5), m="Water_DB", n=24, bevel=0.0)
    tx, ty, tz = L.CASCADE_NW_TOP
    d = math.hypot(tx - px, ty - py)
    mb.beam((tx, ty, tz), (px + (tx - px) * 0.5, py + (ty - py) * 0.5, zw), 4.0, 1.0, "Water_Fall", 0.0)
    mb.finish()


# ------------------------------------------------------------------ saida: trilha, arco de rocha, ponte, ilhota, ancora
def exit_():
    rng = random.Random(91)
    mb = MB("DB_Exit_Blockout", "08_NEXT_ISLAND", rng, detail="far", floor=-999)
    for rp in DL.exit_shelf_polys():
        mb.prism(DL.ccw(rp), L.EXIT_Z - 0.3, L.EXIT_Z + 0.06, "Stone_Paving_DB")
    for nm, base, ang, w, n, rise, tread, g in db_col.stair_list():
        if nm == "Exit":
            DL.vis_stairs(mb, base, ang, w, n, rise, tread, "Stone_Paving_DB", "Stone_DB_Block")
    # arco natural de rocha sobre a trilha
    ax, ay, adeg = L.EXIT_ARCH
    a = math.radians(adeg)
    nx, ny = -math.sin(a), math.cos(a)
    off = L.EXIT_PATH_HW + 4.5
    for s in (-1, 1):
        lx, ly = ax + nx * off * s, ay + ny * off * s
        mb.prism(DL.ccw(blob_poly(lx, ly, 5.5, 9, rng, 0.2)), L.EXIT_Z - 2.0, L.EXIT_Z + 30.0, "Cliff_Rock_DB")
        octo_col("DB_ExitArch", lx, ly, 5.0, L.EXIT_Z - 2.0, L.EXIT_Z + 30.0)
    mb.box((6.0, 2 * off + 10.0, 7.0), (ax, ay, L.EXIT_Z + 27.0), (0, 0, a), "Cliff_Rock_DB", 0.0)
    # ponte de saida
    ux, uy = L.exit_dir()
    ang = math.atan2(uy, ux)
    Ln = L.EXIT_BRIDGE_LEN
    c = L.exit_point(Ln / 2)
    mb.box((Ln + 2.0, L.EXIT_W, 2.0), (c[0], c[1], L.EXIT_Z - 1.0), (0, 0, ang), "Stone_DB_Dusk", 0.0)
    for s in (-1, 1):
        q = (c[0] - uy * s * (L.EXIT_W / 2 + 0.5), c[1] + ux * s * (L.EXIT_W / 2 + 0.5))
        mb.box((Ln, 1.0, 1.4), (q[0], q[1], L.EXIT_Z + 0.7), (0, 0, ang), "Stone_DB_Block", 0.0)
    for k in range(3):
        p = L.exit_point(10.0 + k * (Ln - 20.0) / 2)
        mb.box((6.0, 6.0, 40.0), (p[0], p[1], L.EXIT_Z - 22.0), (0, 0, ang), "Cliff_Rock_DB_Dusk", 0.0)
    # ilhota (cone de rocha escura) + plataforma da ancora
    ic = L.islet_center()
    mb.cyl(L.GATE_ISLET_R, 3.0, (ic[0], ic[1], L.EXIT_Z - 1.5), m="Stone_DB_Dusk", n=32, bevel=0.0)
    mb.cyl(L.GATE_ISLET_R * 0.95, 34.0, (ic[0], ic[1], L.EXIT_Z - 20.0), m="Cliff_Rock_DB_Dusk", n=16,
           r2=L.GATE_ISLET_R * 0.25, bevel=0.0)
    ap = L.anchor_pos()
    pc = (ap[0] - ux * 5.0, ap[1] - uy * 5.0)
    mb.box((10.0, L.DECK_W, 2.0), (pc[0], pc[1], L.EXIT_Z - 1.0), (0, 0, ang), "Stone_DB_Dusk", 0.0)
    mb.finish()
    # guarda provisoria (visual): 2 pilones + corrente
    g = MB("DB_Exit_AnchorGuard", "08_NEXT_ISLAND", rng, detail="near")
    for s in (-1, 1):
        q = (ap[0] - uy * s * (L.DECK_W / 2 - 0.8), ap[1] + ux * s * (L.DECK_W / 2 - 0.8))
        g.box((1.4, 1.4, 5.0), (q[0], q[1], L.EXIT_Z + 2.5), (0, 0, ang), "Stone_DB_Dusk", 0.1)
    q0 = (ap[0] - uy * (L.DECK_W / 2 - 0.8), ap[1] + ux * (L.DECK_W / 2 - 0.8), L.EXIT_Z + 3.5)
    q1 = (ap[0] + uy * (L.DECK_W / 2 - 0.8), ap[1] - ux * (L.DECK_W / 2 - 0.8), L.EXIT_Z + 3.5)
    g.beam(q0, q1, 0.35, 0.35, "Metal_Dark", 0.0)
    ob = g.finish()
    ob["next_island_guard"] = True


# ------------------------------------------------------------------ vestir (so para escala no blockout)
def dressing():
    rng = random.Random(101)
    mb = MB("DB_Veg_Blockout", "10_VEGETATION", rng, detail="far", floor=-999)
    spots = [(-18.0, -96.0), (18.0, -96.0), (-20.0, -80.0), (20.0, -80.0), (-92.0, -76.0), (90.0, -74.0),
             (-120.0, 88.0), (-96.0, 108.0), (-140.0, 20.0), (-112.0, -24.0)]
    for x, y in spots:
        DL.FP.palm(mb, (x, y, L.zone_of(x, y)), rng.uniform(11.0, 15.0), rng)
    mb.finish()


FUNCS = {"terrain": terrain, "mining": mining, "entrance": entrance, "capsule": capsule, "village": village,
         "towers": towers, "summon": summon, "water": water, "exit": exit_, "dressing": dressing}


def build(skip=()):
    for z in ZONES:
        if z not in skip:
            FUNCS[z]()
