# fm_arch_house - casca generica das construcoes secundarias (loja, cabanas, casa da roda).
# Referencial local F: porta na face -Y (oitao da frente), cumeeira no eixo local Y, paredes laterais em +-X.
# Arestas: 0 = frente (-Y), 1 = direita (+X), 2 = fundo (+Y), 3 = esquerda (-X); em cada aresta, s = distancia
# a partir do canto inicial (sentido anti-horario) e o lado de fora e -y do referencial da aresta.
# Especificacao V (cotas relativas ao piso z0):
#   zs/ze/rise, door=(s0, s1, altura, flecha_do_arco), jet=(f, d, t, e) balanco do andar de cima (so se zs >= 6.4),
#   gjet=(f, t) oitao projetado no beiral, wins={aresta: [(s0, s1, zlo, zhi)]}, holes_t={...} furos sem vidro,
#   roof={m, m2, alt, sag, over=(esq, dir), ends=(f, t), hips=(f, t), cx, rafters, tile, course},
#   gables={0|1: {style, window=(l, a, dz_do_beiral)}}, chimneys=[...], dormers=[...], lean=[...], porch=...,
#   outshot=..., bays=[...], shutters=[...], flowers=[...], leaves, ties, plinth
import math
from mathutils import Vector
from fm_lib import MB, D, col_box, marker, light
from fm_parts import Frame, masonry_wall, timber_wall, window_glow, arch
import fm_arch_kit as K


def edge_frames(F, w, d):
    c = [F.p(-w / 2, -d / 2), F.p(w / 2, -d / 2), F.p(w / 2, d / 2), F.p(-w / 2, d / 2)]
    EF = []
    for e in range(4):
        a, b = c[e], c[(e + 1) % 4]
        dv = b - a
        EF.append((Frame(a.x, a.y, 0.0, math.atan2(dv.y, dv.x)), dv.length))
    return c, EF


def hearth(mb, F, x, y, rot, z0, rng, w=3.2, glow=True):
    """lareira encostada na parede: rot = angulo relativo tal que o -y local aponta para dentro da sala"""
    Fh = K.sub(F, x, y, rot)
    K.lbox(mb, Fh, (w, 1.3, 3.2), 0, 0.3, z0 + 1.6, "Stone_Dark", 0.15)
    K.lbox(mb, Fh, (w - 1.3, 0.5, 1.5), 0, -0.25, z0 + 1.05, "Forge_Emissive" if glow else "Metal_Dark", 0.0)
    K.lbox(mb, Fh, (w + 0.7, 1.0, 0.5), 0, -0.1, z0 + 3.3, "Wood_Dark", 0.08)
    K.lbox(mb, Fh, (w - 0.8, 1.0, 1.6), 0, 0.4, z0 + 4.3, "Stone_Light", 0.12)
    for sx in (-1, 1):
        K.lbox(mb, Fh, (0.35, 0.4, 0.5), sx * 0.5, -0.2, z0 + 3.7, "Metal_Brass", 0.03)


def fanlight(mb, Fe, s0, s1, z_spring, rise, y, thick=0.3):
    """bandeira semicircular acesa dentro do arco da porta"""
    cx = (s0 + s1) / 2
    rx = (s1 - s0) / 2 - 0.1
    pts = [(cx + rx * math.cos(math.pi * i / 8), z_spring + (rise - 0.1) * math.sin(math.pi * i / 8)) for i in range(9)]
    K.vprism(mb, Fe, pts, y - thick / 2, y + thick / 2, "Lantern_Glow", "y")
    K.lbox(mb, Fe, (s1 - s0, thick + 0.25, 0.35), cx, y, z_spring, "Wood_Dark", 0.03)
    K.lbox(mb, Fe, (0.25, thick + 0.2, rise - 0.2), cx, y, z_spring + (rise - 0.2) / 2, "Wood_Dark", 0.0)


def house(mb, F, w, d, z0, rng, V, area=None, name="House"):
    t = V.get("t", 1.4)
    tt = t * 0.8
    zs, ze = z0 + V["zs"], z0 + V["ze"]
    rise = V["rise"]
    ds0, ds1, dh, darch = V["door"]
    jet = list(V.get("jet", (0.0, 0.0, 0.0, 0.0))) if V["zs"] >= 6.4 else [0.0] * 4
    gj = V.get("gjet", (0.0, 0.0))
    m_p = V.get("plaster", "Plaster")
    R = V.get("roof", {})
    rm, rm2 = R.get("m", "Roof"), R.get("m2")
    c, EF = edge_frames(F, w, d)
    info = {"c": c, "EF": EF, "jet": jet}
    # ---------------------------------------------------------------- base + fundacao irregular + soleira
    mb.prism([(p.x, p.y) for p in (F.p(-w / 2 - 0.5, -d / 2 - 0.5), F.p(w / 2 + 0.5, -d / 2 - 0.5),
                                   F.p(w / 2 + 0.5, d / 2 + 0.5), F.p(-w / 2 - 0.5, d / 2 + 0.5))],
             z0 - 1, z0 + 0.3, "Stone_Dark", bevel=0.2)
    ph = V.get("plinth", 0.9)
    if ph > 0:
        K.stone_plinth(mb, [(p.x, p.y) for p in c], z0 - 0.5, z0 + ph, rng,
                       skip=[(0, ds0 - 0.4, ds1 + 0.4)] + list(V.get("plinth_skip", [])), step=(2.7, 4.4))
    Fe0, _ = EF[0]
    K.lbox(mb, Fe0, (ds1 - ds0 + 1.4, 1.7, 0.42), (ds0 + ds1) / 2, -0.55, z0 + 0.09, "Stone_Light", 0.12,
           rz=rng.uniform(-0.03, 0.03))
    # ---------------------------------------------------------------- paredes (pedra embaixo, enxaimel em cima)
    wins = V.get("wins", {})
    holes_t = V.get("holes_t", {})
    bays = V.get("bays", [])
    glass = []
    # porta em arco mais alta que o terreo de pedra: moldura de pedra (portal) sobe ate cobrir o arco e o
    # enxaimel abre em volta dela (antes o arco atravessava o reboco e a verga de madeira)
    surround = bool(darch) and z0 + dh + 0.3 > zs
    sr0, sr1, sz1 = max(0.1, ds0 - 1.3), min(w - 0.1, ds1 + 1.3), z0 + dh + 0.9
    for e in range(4):
        Fe, Le = EF[e]
        je, jp, jn = jet[e], jet[(e - 1) % 4], jet[(e + 1) % 4]
        om, ot = [], []
        if e == 0:
            if darch:
                om.append((ds0, ds1, z0, z0 + dh, darch))
            else:
                om.append((ds0, ds1, z0, min(z0 + dh, zs)))
            if surround:
                ot.append((sr0 + jp, sr1 + jp, zs, sz1))
                masonry_wall(mb, Fe.p(sr0, t / 2), Fe.p(sr1, t / 2), zs, sz1, t + 0.25, rng,
                             openings=[(ds0 - sr0, ds1 - sr0, z0, z0 + dh, darch)], course=1.25, mix=0.35,
                             blk=(1.5, 2.6))
                K.lbox(mb, Fe, (sr1 - sr0 + 0.5, t + 0.6, 0.55), (sr0 + sr1) / 2, t / 2, sz1 + 0.2, "Stone_Dark", 0.12)
            elif z0 + dh > zs:
                ot.append((ds0 + jp, ds1 + jp, zs, z0 + dh))
        for (s0, s1, zl, zh) in wins.get(e, []):
            if z0 + zh <= zs + 0.01:
                om.append((s0, s1, z0 + zl, z0 + zh))
                glass.append((e, "m", s0, s1, z0 + zl, z0 + zh))
            else:
                ot.append((s0 + jp, s1 + jp, z0 + zl, z0 + zh))
                glass.append((e, "t", s0 + jp, s1 + jp, z0 + zl, z0 + zh))
        for (s0, s1, zl, zh) in holes_t.get(e, []):
            ot.append((s0 + jp, s1 + jp, z0 + zl, z0 + zh))
        for bw in bays:
            if bw["edge"] == e:
                ot.append((bw["s"] - bw["wd"] / 2 + 0.35 + jp, bw["s"] + bw["wd"] / 2 - 0.35 + jp,
                           z0 + bw["z0"] + 0.1, z0 + bw["z1"] - 0.2))
        a2, b2 = Fe.p(0, t / 2), Fe.p(Le, t / 2)
        masonry_wall(mb, a2, b2, z0, zs, t, rng, openings=om, course=V.get("course", 1.75),
                     blk=V.get("blk", (2.6, 4.3)))
        au, bu = Fe.p(-jp, -je + t / 2), Fe.p(Le + jn, -je + t / 2)
        timber_wall(mb, au, bu, zs, ze, tt, rng, openings=ot, post=V.get("post", 4.1), m_p=m_p,
                    wobble=V.get("wobble", 0.04), inner=1, brace_bevel=0.0, cut_plates=True)
        if je > 0:
            K.jetty_band(mb, Fe, -jp, Le + jn, 0.0, je, zs, rng, -1, depth_in=t, brackets=3 if Le > 12 else 2)
    for (e, kind, s0, s1, zl, zh) in glass:
        Fe, Le = EF[e]
        je, jp, jn = jet[e], jet[(e - 1) % 4], jet[(e + 1) % 4]
        if kind == "m":
            window_glow(mb, Fe.p(0, t / 2), Fe.p(Le, t / 2), s0, s1, zl, zh, t, sill=True, sill_m="Stone_Light")
        else:
            window_glow(mb, Fe.p(-jp, -je + t / 2), Fe.p(Le + jn, -je + t / 2), s0, s1, zl, zh, tt, sill=True,
                        panes=2 if s1 - s0 > 3.6 else None)
    if darch:
        arch(mb, Fe0.p((ds0 + ds1) / 2, t / 2), Fe0.a, ds1 - ds0, z0 + dh - darch, darch, t + 0.3, n=7, band=1.0)
        fanlight(mb, Fe0, ds0, ds1, z0 + dh - darch, darch, t / 2)
    # ---------------------------------------------------------------- oitoes
    x_l, x_r = -w / 2 - jet[3], w / 2 + jet[1]
    yF = -d / 2 - jet[0] - gj[0] + t / 2
    yB = d / 2 + jet[2] + gj[1] - t / 2
    cxr = R.get("cx", 0.0)
    z_r = ze + rise
    hips = R.get("hips", (0.0, 0.0))
    G = V.get("gables", {})
    for k, (yy, outs) in enumerate(((yF, -1), (yB, 1))):
        gs = G.get(k, {})
        win = gs.get("window")
        K.gable_infill(mb, F, yy, x_l, x_r, cxr, ze, z_r, tt, rng, m_p, style=gs.get("style", "king"),
                       window=(win[0], win[1], ze + win[2]) if win else None,
                       z_clip=(z_r - hips[k]) if hips[k] > 0 else None, out_sign=outs)
        if gj[k] > 0:
            K.gable_jetty(mb, F, x_l, x_r, (-d / 2 - jet[0]) if k == 0 else (d / 2 + jet[2]), gj[k], ze, rng, outs,
                          nbr=3 if (x_r - x_l) > 13 else 2)
    # ---------------------------------------------------------------- volumes que furam o telhado
    ov = R.get("over", (1.2, 1.2))
    hw_l, hw_r = cxr - x_l, x_r - cxr
    sides = [(hw_l, ze, ov[0]), (hw_r, ze, ov[1])]
    OS = V.get("outshot")
    if OS:
        g = rise / hw_r
        sides[1] = (hw_r + OS["depth"], z_r - g * (hw_r + OS["depth"]), ov[1])
    holes = [list(R.get("holes_l", [])), list(R.get("holes_r", []))]
    for ch in V.get("chimneys", []):
        if ch["kind"] == "side":
            sd = ch["side"]
            js = jet[1] if sd > 0 else jet[3]
            x_c = sd * (w / 2 + js + 1.15)
            yc = ch["y"]
            top = z_r + ch.get("top", 0.4)
            K.chimney(mb, F, x_c, yc, z0 - 0.4, top, rng, w=2.3, d=3.1, w2=1.6, d2=2.0, z_sh=ze - 1.8,
                      off=(-sd * 0.12, ch.get("off", 0.0)), name=ch.get("name"))
            if js > 0:
                # andar de cima em balanco: bloco de pedra fecha o vao entre a parede de baixo e a chamine
                K.lbox(mb, F, (js + 0.3, 2.7, zs - z0 + 0.3), sd * (w / 2 + (js + 0.3) / 2 - 0.1), yc,
                       (z0 + zs) / 2 - 0.1, "Stone_Light", 0.14)
            hwk = hw_l if sd < 0 else hw_r
            holes[0 if sd < 0 else 1].append((yc - 1.35, yc + 1.35, hwk + 0.15, hwk + 30))
            if area:
                q = F.p(x_c, yc)
                col_box(area, (2.4, 3.2, top - z0), (q.x, q.y, (top + z0) / 2), F.r())
                if js > 0:
                    q = F.p(sd * (w / 2 + js / 2), yc)
                    col_box(area, (js + 0.2, 2.7, zs - z0), (q.x, q.y, (zs + z0) / 2), F.r())
            if ch.get("hearth", True):
                hearth(mb, F, sd * (w / 2 - t - 0.35), yc, D(-90) if sd > 0 else D(90), z0 + 0.3, rng)
                if area:
                    q = F.p(sd * (w / 2 - t - 0.65), yc)
                    col_box(area, (1.3, 3.4, 3.2), (q.x, q.y, z0 + 1.6), F.r())
        elif ch["kind"] == "ridge":
            yc = ch["y"]
            top = z_r + ch.get("top", 1.8)
            K.chimney(mb, F, cxr + ch.get("dx", 0.0), yc, z0 + 0.3, top, rng, w=3.2, d=2.2, w2=1.8, d2=1.6,
                      z_sh=ze - 0.8, off=(0.0, 0.0), name=ch.get("name"))
            for k in (0, 1):
                holes[k].append((yc - 1.2, yc + 1.2, 0.0, 1.35 + abs(ch.get("dx", 0.0))))
            # boca da lareira virada para a frente da casa
            Fh = K.sub(F, cxr + ch.get("dx", 0.0), yc - 1.1, 0.0)
            K.lbox(mb, Fh, (1.9, 0.4, 1.4), 0, -0.05, z0 + 1.1, "Forge_Emissive", 0.0)
            K.lbox(mb, Fh, (3.8, 0.9, 0.45), 0, -0.2, z0 + 2.4, "Wood_Dark", 0.06)
            if area:
                q = F.p(cxr + ch.get("dx", 0.0), yc)
                col_box(area, (3.3, 2.3, ze - z0), (q.x, q.y, (ze + z0) / 2), F.r())
    for dm in V.get("dormers", []):
        sd = dm["side"]
        hwk = hw_l if sd < 0 else hw_r
        h = K.dormer(mb, F, sd, cxr, hwk, ze, z_r, dm["y"], dm.get("wd", 3.4), rng, inset=dm.get("inset", 1.3),
                     h=dm.get("h", 2.8), m_roof=rm, m_roof2=rm2, m_p=m_p, style=dm.get("style", "king"),
                     front_jet=dm.get("jet", 0.0), over=dm.get("over", 0.6))
        if h:
            holes[0 if sd < 0 else 1].append(h)
    # ---------------------------------------------------------------- telhado principal
    ends = R.get("ends", (1.0, 1.0))
    ya, yb = yF - tt / 2, yB + tt / 2
    rinfo = K.gable_roof(mb, F, cxr, ya, yb, z_r, rng, sides=sides, ends=((ends[0], hips[0]), (ends[1], hips[1])),
                         m=rm, m2=rm2, alt=R.get("alt", 0.22), sag=R.get("sag", 0.3), holes=holes,
                         tile=R.get("tile", (2.1, 3.3)), course=R.get("course", 1.7), rafters=R.get("rafters", 0.0),
                         horns=R.get("horns", (True, True)), th=R.get("th", 0.44), lip=R.get("lip", 0.32))
    info.update(z_r=z_r, x_l=x_l, x_r=x_r, ya=ya, yb=yb, roof=rinfo, zs=zs, ze=ze)
    # ---------------------------------------------------------------- anexos
    for lt in V.get("lean", []):
        Fe, Le = EF[lt["edge"]]
        je = jet[lt["edge"]]
        s0, s1 = lt["s0"], lt["s1"]
        dep = lt["depth"]
        yb_, zb_ = K.lean_to(mb, Fe, s0, s1, 0.0, dep, z0 + lt["z_hi"], z0 + lt["z_lo"], rng, -1, m=rm, m2=rm2,
                             area=area, z_ground=z0, sag=lt.get("sag", 0.12))
        what = lt.get("content", "logs")
        if what == "logs":
            L_ = s1 - s0
            npile = max(1, int(L_ / 3.2))
            for i in range(npile):
                xx = s0 + L_ * (i + 0.5) / npile
                K.log_pile(mb, Fe, xx, -dep * 0.42, z0 + 0.05, min(2.8, L_ / npile - 0.4), 3, rng)
            if area:
                q = Fe.p((s0 + s1) / 2, -dep * 0.42)
                col_box(area, (s1 - s0 - 0.6, 2.4, 2.4), (q.x, q.y, z0 + 1.2), (0, 0, Fe.a))
            K.chopping_block(mb, Fe, s1 + 1.0, -dep - 0.8, z0, rng)
        elif what == "barrels":
            from fm_parts import barrel, crate
            barrel(mb, tuple(Fe.p(s0 + 1.4, -dep * 0.45, z0)))
            barrel(mb, tuple(Fe.p(s0 + 3.6, -dep * 0.5, z0)))
            crate(mb, tuple(Fe.p(s1 - 1.6, -dep * 0.45, z0)), 2.0, Fe.a + 0.15, rng)
            if area:
                q = Fe.p((s0 + s1) / 2, -dep * 0.45)
                col_box(area, (s1 - s0 - 0.6, 2.4, 2.6), (q.x, q.y, z0 + 1.3), (0, 0, Fe.a))
    P = V.get("porch")
    if P:
        Fe, Le = EF[0]
        K.lean_to(mb, Fe, P["s0"], P["s1"], 0.0, P["depth"], z0 + P["z_hi"], z0 + P["z_lo"], rng, -1, m=rm, m2=rm2,
                  area=area, z_ground=z0, sag=0.1)
        # deck de tabuas sob o alpendre
        K.lbox(mb, Fe, (P["s1"] - P["s0"], P["depth"] - 0.2, 0.35), (P["s0"] + P["s1"]) / 2, -P["depth"] / 2 - 0.1,
               z0 + 0.12, "Wood_Plank", 0.06)
        if P.get("bench"):
            bs0, bs1 = P["bench"]
            K.lbox(mb, Fe, (bs1 - bs0, 1.3, 0.35), (bs0 + bs1) / 2, -0.9, z0 + 1.9, "Wood_Plank", 0.06)
            for bx in (bs0 + 0.4, bs1 - 0.4):
                K.lbox(mb, Fe, (0.4, 1.1, 1.7), bx, -0.9, z0 + 1.0, "Wood_Dark", 0.05)
            if area:
                q = Fe.p((bs0 + bs1) / 2, -0.9)
                col_box(area, (bs1 - bs0, 1.4, 2.2), (q.x, q.y, z0 + 1.1), (0, 0, Fe.a))
    if OS:
        # anexo baixo sob o prolongamento da agua (saltbox): parede de tabuas, sem porta
        g = rise / hw_r
        xo = w / 2 + OS["depth"]

        def zroof(x):
            return z_r - g * (x - cxr) - 0.45
        y0o, y1o = OS["y0"], OS["y1"]
        K.vprism(mb, F, [(y0o, z0), (y1o, z0), (y1o, zroof(xo)), (y0o, zroof(xo))], xo - 0.5, xo, "Wood_Plank", "x")
        for yy in (y0o, y1o - 0.5):
            K.vprism(mb, F, [(w / 2, z0), (xo, z0), (xo, zroof(xo)), (w / 2, zroof(w / 2))], yy, yy + 0.5,
                     "Wood_Plank", "y")
        # ripas verticais e cantoneiras
        y = y0o + 0.9
        while y < y1o - 0.6:
            K.lbox(mb, F, (0.22, 0.3, zroof(xo) - z0 - 0.3), xo + 0.05, y, (z0 + zroof(xo)) / 2 - 0.1, "Wood_Dark", 0.0)
            y += 1.25
        for yy in (y0o, y1o):
            K.lbox(mb, F, (0.7, 0.7, zroof(xo) - z0 + 0.2), xo - 0.2, yy, (z0 + zroof(xo)) / 2, "Wood_Dark", 0.08)
        K.lbox(mb, F, (0.5, y1o - y0o, 0.5), xo - 0.1, (y0o + y1o) / 2, z0 + 0.55, "Stone_Dark", 0.1)
        if OS.get("window"):
            yw = OS["window"]
            K.lbox(mb, F, (0.3, 1.6, 1.2), xo + 0.02, yw, z0 + 2.4, "Lantern_Glow", 0.0)
            K.lbox(mb, F, (0.4, 2.2, 0.35), xo + 0.1, yw, z0 + 1.7, "Wood_Dark", 0.04)
        if area:
            q = F.p((w / 2 + xo) / 2, (y0o + y1o) / 2)
            col_box(area, (OS["depth"], y1o - y0o, zroof(xo) - z0), (q.x, q.y, (z0 + zroof(xo)) / 2), F.r())
    for bw in bays:
        e = bw["edge"]
        Fe, Le = EF[e]
        je, jp = jet[e], jet[(e - 1) % 4]
        K.bay_window(mb, Fe, bw["s"] + jp, -je + t / 2 - tt / 2, z0 + bw["z0"], z0 + bw["z1"], bw["wd"], bw["out"], rng,
                     -1, roof_m=rm)
    for (e, s0, s1, zl, zh) in V.get("shutters", []):
        Fe, Le = EF[e]
        je, jp = jet[e], jet[(e - 1) % 4]
        timber = z0 + zh > zs + 0.01
        K.shutters(mb, Fe, s0 - 0.38 + (jp if timber else 0), s1 + 0.38 + (jp if timber else 0),
                   (-je if timber else -0.05), z0 + zl, z0 + zh, rng, -1, m=V.get("paint", "Wood_Teal"))
    for (e, s0, s1, zl) in V.get("flowers", []):
        Fe, Le = EF[e]
        je, jp = jet[e], jet[(e - 1) % 4]
        timber = z0 + zl > zs + 0.01
        K.flower_box(mb, Fe, s0 + (jp if timber else 0), s1 + (jp if timber else 0), (-je - 0.15 if timber else -0.1),
                     z0 + zl - 0.2, rng)
    if V.get("apron", False):
        # pedras de passo diante da porta + colisao rasa (pisavel): a vegetacao (que evita COL_) nao nasce na porta
        y_st = -(P["depth"] + 0.9) if P else -1.9
        mid = (ds0 + ds1) / 2
        for i in range(3):
            yy = y_st - i * 1.55
            xx = mid + rng.uniform(-0.6, 0.6) + (0.5 if i % 2 else -0.4)
            K.lbox(mb, Fe0, (rng.uniform(2.3, 3.0), 1.25, 0.3), xx, yy, z0 + 0.06, "Stone_Light" if i % 2 else "Stone_Dark",
                   0.1, rz=rng.uniform(-0.25, 0.25))
        if area:
            q = Fe0.p(mid, (y_st - 3.1 - 0.7) / 2)
            col_box(area, (ds1 - ds0 + 1.0, abs(y_st - 3.1 - 0.7), 0.2), (q.x, q.y, z0 + 0.1), (0, 0, Fe0.a))
    if V.get("leaves", True):
        hl = (dh - darch - 0.35) if darch else (dh - 0.4)
        K.door_leaves(mb, Fe0, ds0, ds1, -0.12, z0 + 0.3, hl, rng, -1)
    if V.get("ties", True):
        for f in (-0.25, 0.25):
            K.lbox(mb, F, (w - 2 * t + 0.4, 0.7, 0.8), 0, d * f, ze - 0.55, "Wood_Dark", 0.06)
    # ---------------------------------------------------------------- colisao da casca
    if area:
        for e in range(4):
            Fe, Le = EF[e]
            segs = [(0.0, Le)]
            if e == 0:
                segs = [(0.0, ds0), (ds1, Le)]
                cc = Fe.p((ds0 + ds1) / 2, t / 2)
                col_box(area, (ds1 - ds0, t, ze - (z0 + dh)), (cc.x, cc.y, (z0 + dh + ze) / 2), (0, 0, Fe.a))
            for s0, s1 in segs:
                if s1 - s0 < 0.05:
                    continue
                cc = Fe.p((s0 + s1) / 2, t / 2)
                col_box(area, (s1 - s0, t, ze - z0), (cc.x, cc.y, (z0 + ze) / 2), (0, 0, Fe.a))
        ctr = F.p(0, 0)
        col_box(area, (w + 2, d + 2, 3), (ctr.x, ctr.y, ze + 2.0), F.r())
        # piso interno na altura do assoalho (tambem impede vegetacao de nascer dentro da casa)
        ft = V.get("floor_top", 0.55)
        col_box(area, (w - 2 * t, d - 2 * t, ft), (ctr.x, ctr.y, z0 + ft / 2), F.r())
    return info
