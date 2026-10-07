# fm_arch_house - casca das construcoes secundarias (loja, cabanas, casa da roda) com LINGUAGEM POR FUNCAO.
# Referencial local F: porta na face -Y (oitao da frente), cumeeira no eixo local Y, paredes laterais em +-X.
# Arestas: 0 = frente (-Y), 1 = direita (+X), 2 = fundo (+Y), 3 = esquerda (-X); em cada aresta, s = distancia
# a partir do canto inicial (sentido anti-horario) e o lado de fora e -y do referencial da aresta.
# Especificacao V (cotas relativas ao piso z0):
#   zs/ze, rise (ou pitch em graus), door=(s0, s1, altura, flecha_do_arco)
#   lower = 'stone' (terreo de alvenaria ate zs) | 'none' (so a fundacao de pedra ate zs)
#   upper = 'timber' (enxaimel + reboco) | 'log' (toras) | 'board' (tabua e mata-junta), de zs ate ze
#   jet=(f, d, t, e) balanco do andar de cima (so enxaimel e zs >= 6.4), gjet=(f, t) oitao projetado
#   wins={aresta: [(s0, s1, zlo, zhi[, 'estilo+lit+ore+shut'])]}: estilo cross|two|grid|slit, lit = acesa
#         (Window_Warm; senao Window_Dark), ore = amostras de minerio no peitoril, shut = postigos; sem 'lit'/'dark'
#         a janela acende pelo sorteio lit_frac (padrao 0 = apagada: as acesas sao escolhidas a dedo nas specs;
#         no conjunto ~35% das janelas acesas de dia, contando bandeiras, oitoes e lucarnas)
#   roof={kind: gable|hip, m, m2, alt, sag, over=(esq, dir), ends=(f, t), hips=(f, t), cx, rafters, tile, course,
#         skew=(dx_f, dx_t, dz_f, dz_t), patches, bevel}
#   gables={0|1: {style, window=(l, a, dz_do_beiral[, 'round']), lit}}, chimneys=[{kind: side|ridge|rubble, ...}],
#   dormers=[...], door_gable={...} (empena cruzada sobre a porta em telhado de 4 aguas), lean=[...], porch=...,
#   outshot=..., bays=[...], shutters=[...], flowers=[...] (so a loja), tools=[{edge, s, kinds}], back=(2,),
#   plinth, leaves, ties, apron, floor_top, win_m (vidro aceso: Window_Warm; a loja usa Lantern_Glow)
# mbi = MB do interior (linhas do teto): o chamador cria BLD_<nome>_Interior separado; a lareira fica na casca
# (ja tem a pedra da chamine: um material a menos no interior).
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
    K.lbox(mb, Fh, (w, 1.3, 3.2), 0, 0.3, z0 + 1.6, "Stone_Dark", 0.0)
    K.lbox(mb, Fh, (w - 1.3, 0.5, 1.5), 0, -0.25, z0 + 1.05, "Forge_Emissive" if glow else "Metal_Dark", 0.0)
    K.lbox(mb, Fh, (w + 0.7, 1.0, 0.5), 0, -0.1, z0 + 3.3, "Wood_Dark", 0.0)
    K.lbox(mb, Fh, (w - 0.8, 1.0, 1.6), 0, 0.4, z0 + 4.3, "Stone_Dark", 0.0)


def fanlight(mb, Fe, s0, s1, z_spring, rise, y, thick=0.3, m="Window_Warm"):
    """bandeira semicircular dentro do arco da porta"""
    cx = (s0 + s1) / 2
    rx = (s1 - s0) / 2 - 0.1
    pts = [(cx + rx * math.cos(math.pi * i / 8), z_spring + (rise - 0.1) * math.sin(math.pi * i / 8)) for i in range(9)]
    K.vprism(mb, Fe, pts, y - thick / 2, y + thick / 2, m, "y")
    K.lbox(mb, Fe, (s1 - s0, thick + 0.25, 0.35), cx, y, z_spring, "Wood_Dark", 0.0)
    K.lbox(mb, Fe, (0.25, thick + 0.2, rise - 0.2), cx, y, z_spring + (rise - 0.2) / 2, "Wood_Dark", 0.0)


def _opts(o):
    st, lit, ore, shut = "cross", None, False, False
    for p in (o or "").split("+"):
        if p in ("cross", "two", "grid", "slit"):
            st = p
        elif p == "lit":
            lit = True
        elif p == "glow":
            lit = "glow"
        elif p == "dark":
            lit = False
        elif p == "ore":
            ore = True
        elif p == "shut":
            shut = True
    return st, lit, ore, shut


def _inv(F, p):
    """mundo -> local de F (2D)"""
    dx, dy = p.x - F.o.x, p.y - F.o.y
    c, s = math.cos(-F.a), math.sin(-F.a)
    return dx * c - dy * s, dx * s + dy * c


def house(mb, F, w, d, z0, rng, V, area=None, name="House", mbi=None):
    mbi = mbi or mb
    t = V.get("t", 1.4)
    tt = t * 0.8
    lower = V.get("lower", "stone")
    upper = V.get("upper", "timber")
    zs, ze = z0 + V["zs"], z0 + V["ze"]
    ds0, ds1, dh, darch = V["door"]
    jet = list(V.get("jet", (0.0, 0.0, 0.0, 0.0))) if (V["zs"] >= 6.4 and upper == "timber") else [0.0] * 4
    gj = V.get("gjet", (0.0, 0.0)) if upper == "timber" else (0.0, 0.0)
    m_p = V.get("plaster", "Plaster")
    R = V.get("roof", {})
    fam = R.get("family")
    rm, rm2 = (K.ROOF_AGED[fam] if fam else (R.get("m", "Roof"), R.get("m2")))
    rbev = R.get("bevel", 0.0)
    win_lit = V.get("win_m", "Window_Warm")
    lit_frac = V.get("lit_frac", 0.0)
    back = V.get("back", (2,))
    c, EF = edge_frames(F, w, d)
    info = {"c": c, "EF": EF, "jet": jet}
    lr = K.lrng(F.o.x, F.o.y, w, d)
    # geometria da parede de cima por tipo: centro (y), espessura, face externa, face interna
    r_log = V.get("log_r", 0.56)
    if upper == "log":
        yc_u, th_u, yf_u = t / 2, 2 * r_log, t / 2 - r_log
    elif upper == "board":
        yc_u, th_u, yf_u = 0.35, 0.6, 0.05
    else:
        yc_u, th_u, yf_u = t / 2, tt, t / 2 - tt / 2
    t_in = yc_u + th_u / 2 if lower == "none" else t
    info["t_in"] = t_in
    # ---------------------------------------------------------------- base + fundacao irregular + soleira
    mb.prism([(p.x, p.y) for p in (F.p(-w / 2 - 0.5, -d / 2 - 0.5), F.p(w / 2 + 0.5, -d / 2 - 0.5),
                                   F.p(w / 2 + 0.5, d / 2 + 0.5), F.p(-w / 2 - 0.5, d / 2 + 0.5))],
             z0 - 1, z0 + 0.3, "Stone_Dark", bevel=0.0)
    # fundacao de pedras soltas so nas casas de toras/tabuas: com terreo de alvenaria a fiada de base escura ja faz
    # esse papel (eram ~800 tris a mais por casa)
    ph = V.get("plinth", 0.9 if lower == "none" else 0.0)
    if lower == "none":
        ph = max(ph, V["zs"])
    if ph > 0:
        K.stone_plinth(mb, [(p.x, p.y) for p in c], z0 - 0.5, z0 + ph, rng,
                       skip=[(0, ds0 - 0.4, ds1 + 0.4)] + list(V.get("plinth_skip", [])), step=(3.0, 4.8))
    Fe0, _ = EF[0]
    K.lbox(mb, Fe0, (ds1 - ds0 + 1.4, 1.7, 0.42), (ds0 + ds1) / 2, -0.55, z0 + 0.09, "Stone_Light", 0.12,
           rz=rng.uniform(-0.03, 0.03))
    # ---------------------------------------------------------------- paredes
    wins = V.get("wins", {})
    holes_t = V.get("holes_t", {})
    bays = V.get("bays", [])
    glass = []
    surround = bool(darch) and z0 + dh + 0.3 > zs and lower == "stone"
    sr0, sr1, sz1 = max(0.1, ds0 - 1.3), min(w - 0.1, ds1 + 1.3), z0 + dh + 0.9
    for e in range(4):
        Fe, Le = EF[e]
        je, jp, jn = jet[e], jet[(e - 1) % 4], jet[(e + 1) % 4]
        om, ot = [], []
        if e == 0:
            if lower == "stone":
                if darch:
                    om.append((ds0, ds1, z0, z0 + dh, darch))
                else:
                    om.append((ds0, ds1, z0, min(z0 + dh, zs)))
                if surround:
                    ot.append((sr0 + jp, sr1 + jp, zs, sz1))
                    masonry_wall(mb, Fe.p(sr0, t / 2), Fe.p(sr1, t / 2), zs, sz1, t + 0.25, rng,
                                 openings=[(ds0 - sr0, ds1 - sr0, z0, z0 + dh, darch)], course=1.25, mix=0.1,
                                 blk=(1.5, 2.6), quoins=(False, False), base_dark=False, core_m="Stone_Dark")
                    K.lbox(mb, Fe, (sr1 - sr0 + 0.5, t + 0.6, 0.55), (sr0 + sr1) / 2, t / 2, sz1 + 0.2, "Stone_Dark",
                           0.12)
                elif z0 + dh > zs:
                    ot.append((ds0 + jp, ds1 + jp, zs, z0 + dh))
            else:
                ot.append((ds0, ds1, z0, z0 + dh))
        for wv in wins.get(e, []):
            s0, s1, zl, zh = wv[:4]
            st, lit, ore, shut = _opts(wv[4] if len(wv) > 4 else "")
            if lit is None:
                lit = K.lrng(F.o.x, F.o.y, e, s0, zl).random() < lit_frac
            if lower == "stone" and z0 + zh <= zs + 0.01:
                om.append((s0, s1, z0 + zl, z0 + zh))
                glass.append((e, "m", s0, s1, z0 + zl, z0 + zh, st, lit, ore, shut))
            elif lower == "stone" and z0 + zl < zs - 0.01:
                # vitrine que atravessa a linha do terreo (loja): recorta as duas paredes
                om.append((s0, s1, z0 + zl, zs))
                ot.append((s0 + jp, s1 + jp, zs, z0 + zh))
                glass.append((e, "x", s0, s1, z0 + zl, z0 + zh, st, lit, ore, shut))
            else:
                ot.append((s0 + jp, s1 + jp, z0 + zl, z0 + zh))
                glass.append((e, "t", s0 + jp, s1 + jp, z0 + zl, z0 + zh, st, lit, ore, shut))
        for (s0, s1, zl, zh) in holes_t.get(e, []):
            ot.append((s0 + jp, s1 + jp, z0 + zl, z0 + zh))
        for bw in bays:
            if bw["edge"] == e:
                ot.append((bw["s"] - bw["wd"] / 2 + 0.35 + jp, bw["s"] + bw["wd"] / 2 - 0.35 + jp,
                           z0 + bw["z0"] + 0.1, z0 + bw["z1"] - 0.2))
        if lower == "stone":
            zd = z0 + V.get("damp", 0.0)
            if zd > z0 + 0.3:
                # faixa de umidade: as fiadas de baixo escuras (respingo do rio / capilaridade)
                masonry_wall(mb, Fe.p(0, t / 2), Fe.p(Le, t / 2), z0, zd, t + 0.08, rng, openings=om,
                             course=zd - z0 + 0.01, blk=V.get("blk", (2.6, 4.3)), m="Stone_Dark",
                             m2="Stone_Dark", bevel=V.get("stone_bev", 0.12), core_m="Stone_Dark")
            masonry_wall(mb, Fe.p(0, t / 2), Fe.p(Le, t / 2), max(z0, zd), zs, t, rng, openings=om,
                         course=V.get("course", 1.75), blk=V.get("blk", (2.6, 4.3)), m=V.get("stone_m", "Stone_Light"),
                         bevel=V.get("stone_bev", 0.12), base_dark=zd <= z0 + 0.3, core_m="Stone_Dark")
        detail = "near" if e in back else "full"
        if upper == "timber":
            au, bu = Fe.p(-jp, -je + t / 2), Fe.p(Le + jn, -je + t / 2)
            timber_wall(mb, au, bu, zs, ze, tt, rng, openings=ot, post=V.get("post", 4.1), m_p=m_p,
                        wobble=V.get("wobble", 0.04), inner=1, brace_bevel=0.0, cut_plates=True, detail=detail)
            if je > 0:
                K.jetty_band(mb, Fe, -jp, Le + jn, 0.0, je, zs, rng, -1, depth_in=t, brackets=3 if Le > 12 else 2)
        elif upper == "log":
            # toras: paredes 0/2 nas fiadas pares, 1/3 nas impares (entalhe de sela nos cantos). Nas paredes de
            # oitao (0/2) as cabecas das toras de cima entram embaixo das aguas: encurtam pela inclinacao
            slope = None
            if e in (0, 2) and R.get("kind", "gable") == "gable":
                rise_ = math.tan(D(V["pitch"])) * w / 2 if "pitch" in V else V["rise"]
                cx_ = R.get("cx", 0.0)
                g_l, g_r = rise_ / max(cx_ + w / 2, 0.5), rise_ / max(w / 2 - cx_, 0.5)
                slope = (g_l, g_r) if e == 0 else (g_r, g_l)
            K.log_wall(mb, Fe, 0.0, Le, zs, ze, yc_u, rng, openings=[o[:4] for o in ot], r=r_log,
                       phase=0.0 if e % 2 == 0 else 0.5, ext=(0.9, 0.9), slope=slope)
        else:
            K.board_wall(mb, Fe, -0.2, Le + 0.2, zs, ze, yc_u, th_u, rng, openings=[o[:4] for o in ot],
                         inner=(detail == "full"))
            # cantoneiras
            for s_ in (-0.1, Le + 0.1):
                K.lbox(mb, Fe, (0.55, 0.55, ze - zs), s_, yf_u - 0.15, (zs + ze) / 2, "Wood_Dark", 0.0)
        if upper in ("log", "board"):
            for o in ot:
                door = e == 0 and abs(o[0] - ds0) < 0.01 and abs(o[1] - ds1) < 0.01
                if o[3] - o[2] > 0.5:
                    K.opening_frame(mb, Fe, o[0], o[1], max(o[2], zs if not door else z0), o[3], yc_u, th_u,
                                    door=door)
    for (e, kind, s0, s1, zl, zh, st, lit, ore, shut) in glass:
        Fe, Le = EF[e]
        je, jp, jn = jet[e], jet[(e - 1) % 4], jet[(e + 1) % 4]
        gm = "Lantern_Glow" if lit == "glow" else (win_lit if lit else "Window_Dark")
        if kind in ("m", "x"):
            window_glow(mb, Fe.p(0, t / 2), Fe.p(Le, t / 2), s0, s1, zl, zh, t, m=gm, style=st, sill=True,
                        sill_m="Stone_Light")
            yface = 0.0
        elif upper == "timber":
            window_glow(mb, Fe.p(-jp, -je + t / 2), Fe.p(Le + jn, -je + t / 2), s0, s1, zl, zh, tt, m=gm, style=st,
                        sill=True, panes=2 if (s1 - s0 > 3.6 and st == "cross") else None)
            yface = -je
        else:
            window_glow(mb, Fe.p(0, yc_u), Fe.p(Le, yc_u), s0, s1, zl, zh, th_u, m=gm, style=st, sill=False)
            yface = yf_u - 0.1
        if ore:
            K.ore_sill(mb, Fe, s0, s1, yface - 0.2, zl - 0.05, rng)
        if shut:
            K.shutters(mb, Fe, s0 - 0.38, s1 + 0.38, yface - 0.05, zl, zh, rng, -1, m=V.get("paint", "Wood_Plank"))
    if darch:
        arch(mb, Fe0.p((ds0 + ds1) / 2, t / 2), Fe0.a, ds1 - ds0, z0 + dh - darch, darch, t + 0.3, n=7, band=1.0)
        fanlight(mb, Fe0, ds0, ds1, z0 + dh - darch, darch, t / 2, m=V.get("fan_m", win_lit))
    # ---------------------------------------------------------------- oitoes (so em telhado de 2 aguas)
    x_l, x_r = -w / 2 - jet[3], w / 2 + jet[1]
    yF = -d / 2 - jet[0] - gj[0] + yc_u
    yB = d / 2 + jet[2] + gj[1] - yc_u
    th_g = th_u
    kind = R.get("kind", "gable")
    cxr = R.get("cx", 0.0)
    if "pitch" in V:
        rise = math.tan(D(V["pitch"])) * (x_r - x_l) / 2
    else:
        rise = V["rise"]
    z_r = ze + rise
    hips = R.get("hips", (0.0, 0.0))
    skew = R.get("skew", (0.0, 0.0, 0.0, 0.0))
    G = V.get("gables", {})
    gstyle_def = "boards" if upper in ("log", "board") else "king"
    if kind == "gable":
        for k, (yy, outs) in enumerate(((yF, -1), (yB, 1))):
            gs = G.get(k, {})
            win = gs.get("window")
            wz = None
            if win:
                wz = (win[0], win[1], ze + win[2]) + tuple(win[3:])
            K.gable_infill(mb, F, yy, x_l, x_r, cxr + skew[k], ze, z_r + skew[2 + k], th_g, rng,
                           m_p if upper == "timber" else "Wood_Plank", style=gs.get("style", gstyle_def), window=wz,
                           z_clip=(z_r - hips[k]) if hips[k] > 0 else None, out_sign=outs, both=(k == 0 or upper == "timber"),
                           win_m=(win_lit if gs.get("lit") else "Window_Dark"))
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
    plan_skip = []           # retangulos (x0, x1, y0, y1) em planta local: sem telha (telhado de 4 aguas)
    tri_skip = []            # triangulos de empena cruzada (xc, y_front, meia_largura, profundidade)
    for ch in V.get("chimneys", []):
        sd = ch.get("side", 1)
        js = jet[1] if sd > 0 else jet[3]
        hwk = hw_l if sd < 0 else hw_r
        yc = ch.get("y", 0.0)
        if ch["kind"] == "side":
            x_c = sd * (w / 2 + js + 1.15)
            top = z_r + ch.get("top", 0.4)
            K.chimney(mb, F, x_c, yc, z0 - 0.4, top, rng, w=2.3, d=3.1, w2=1.6, d2=2.0, z_sh=ze - 1.8,
                      off=(-sd * 0.12, ch.get("off", 0.0)), name=ch.get("name"))
            if js > 0:
                K.lbox(mb, F, (js + 0.3, 2.7, zs - z0 + 0.3), sd * (w / 2 + (js + 0.3) / 2 - 0.1), yc,
                       (z0 + zs) / 2 - 0.1, "Stone_Light", 0.14)
            holes[0 if sd < 0 else 1].append((yc - 1.35, yc + 1.35, hwk + 0.15, hwk + 30))
            plan_skip.append((sd * (w / 2 + js) - 0.2 if sd > 0 else sd * (w / 2 + js + 2.6),
                              sd * (w / 2 + js + 2.6) if sd > 0 else sd * (w / 2 + js) + 0.2, yc - 1.4, yc + 1.4))
            if area:
                q = F.p(x_c, yc)
                col_box(area, (2.4, 3.2, top - z0), (q.x, q.y, (top + z0) / 2), F.r())
                if js > 0:
                    q = F.p(sd * (w / 2 + js / 2), yc)
                    col_box(area, (js + 0.2, 2.7, zs - z0), (q.x, q.y, (zs + z0) / 2), F.r())
        elif ch["kind"] == "rubble":
            dep = ch.get("depth", 3.0)
            x_c = sd * (w / 2 + js + dep / 2 - 0.25)
            top = (z_r if kind == "gable" else ze + rise) + ch.get("top", 0.8)
            K.rubble_chimney(mb, F, x_c, yc, z0 - 0.4, ze - ch.get("sh", 1.2), top, rng, w=dep, d=ch.get("wd", 3.8),
                             w2=dep * 0.66, d2=ch.get("wd", 3.8) * 0.62, out=(sd, 0), name=ch.get("name"))
            holes[0 if sd < 0 else 1].append((yc - 1.5, yc + 1.5, hwk + 0.1, hwk + 30))
            x_in = sd * (w / 2 + js) - sd * 0.3
            x_out = sd * (w / 2 + js + dep + 0.3)
            plan_skip.append((min(x_in, x_out), max(x_in, x_out), yc - 1.5, yc + 1.5))
            if area:
                q = F.p(x_c, yc)
                col_box(area, (dep, ch.get("wd", 3.8), top - z0), (q.x, q.y, (top + z0) / 2), F.r())
        elif ch["kind"] == "ridge":
            top = z_r + ch.get("top", 1.8)
            K.chimney(mb, F, cxr + ch.get("dx", 0.0), yc, z0 + 0.3, top, rng, w=3.2, d=2.2, w2=1.8, d2=1.6,
                      z_sh=ze - 0.8, off=(0.0, 0.0), name=ch.get("name"))
            for k in (0, 1):
                holes[k].append((yc - 1.2, yc + 1.2, 0.0, 1.35 + abs(ch.get("dx", 0.0))))
            if area:
                q = F.p(cxr + ch.get("dx", 0.0), yc)
                col_box(area, (3.3, 2.3, ze - z0), (q.x, q.y, (ze + z0) / 2), F.r())
        if ch.get("hearth", True):
            if ch["kind"] == "ridge":
                Fh = K.sub(F, cxr + ch.get("dx", 0.0), yc - 1.1, 0.0)
                K.lbox(mb, Fh, (1.9, 0.4, 1.4), 0, -0.05, z0 + 1.1, "Forge_Emissive", 0.0)
                K.lbox(mb, Fh, (3.8, 0.9, 0.45), 0, -0.2, z0 + 2.4, "Wood_Dark", 0.0)
            else:
                hearth(mb, F, sd * (w / 2 - t_in - 0.35), yc, D(-90) if sd > 0 else D(90), z0 + 0.3, rng)
                if area:
                    q = F.p(sd * (w / 2 - t_in - 0.65), yc)
                    col_box(area, (1.3, 3.4, 3.2), (q.x, q.y, z0 + 1.6), F.r())
    for dm in V.get("dormers", []):
        sd = dm["side"]
        hwk = hw_l if sd < 0 else hw_r
        if kind == "hip":
            z_top_d = ze + rise * (hwk / ((x_r - x_l) / 2))
        else:
            z_top_d = z_r
        h = K.dormer(mb, F, sd, cxr, hwk, ze, z_top_d, dm["y"], dm.get("wd", 3.4), rng, inset=dm.get("inset", 1.3),
                     h=dm.get("h", 2.8), m_roof=rm, m_roof2=rm2, m_p=(m_p if upper == "timber" else "Wood_Plank"),
                     style=dm.get("style", "king"), front_jet=dm.get("jet", 0.0), over=dm.get("over", 0.6),
                     win_m=(win_lit if dm.get("lit", True) else "Window_Dark"), bevel=rbev)
        if h:
            holes[0 if sd < 0 else 1].append(h)
            y0h, y1h, d0h, d1h = h
            xa_, xb_ = cxr + sd * d0h, cxr + sd * min(d1h, hwk + 3.0)
            plan_skip.append((min(xa_, xb_), max(xa_, xb_), y0h, y1h))
    DG = V.get("door_gable")
    if DG:
        # empena cruzada sobre a porta (a fachada da porta sobe como um oitao dentro do telhado de 4 aguas)
        xd = -w / 2 + (ds0 + ds1) / 2 + DG.get("dx", 0.0)
        Fd = K.sub(F, 0.0, 0.0, D(-90))
        hwf = d / 2 + jet[0]
        z_top_f = ze + rise * (hwf / ((x_r - x_l) / 2)) if kind == "hip" else z_r
        wd = DG.get("wd", 7.0)
        hg = DG.get("h", 0.0)
        K.dormer(mb, Fd, 1, 0.0, hwf, ze, z_top_f, xd, wd, rng, inset=0.0, h=hg, rise=DG.get("rise"),
                 m_roof=rm, m_roof2=rm2, m_p=m_p, style=DG.get("style", "cross"), front_jet=DG.get("jet", 0.0),
                 over=DG.get("over", 0.8), win_m=(win_lit if DG.get("lit", True) else "Window_Dark"), bevel=rbev,
                 window=DG.get("window", True), wall_style=DG.get("style", "cross"), front_wall=not surround)
        g_ = rise / ((x_r - x_l) / 2)
        rise_g = DG.get("rise") or wd / 2 * 0.95
        z_dr = min(ze + hg + rise_g, z_top_f - 0.6)
        tri_skip.append((xd, -hwf, wd / 2 + DG.get("over", 0.8) + 0.35, (z_dr - ze) / g_ + 0.4, R.get("over", (1.2,))[0]))
    # ---------------------------------------------------------------- telhado principal
    ends = R.get("ends", (1.0, 1.0))
    ya, yb = yF - th_g / 2, yB + th_g / 2

    def skip_tri(p):
        lx, ly = _inv(F, p)
        for (xc_, yf_, hw_, dep_, ovf) in tri_skip:
            q = ly - yf_ + ovf
            if -0.2 <= q <= dep_ + ovf:
                if abs(lx - xc_) <= hw_ * (1 - q / (dep_ + ovf)):
                    return True
        return False

    def skip(p):
        lx, ly = _inv(F, p)
        for (x0_, x1_, y0_, y1_) in plan_skip:
            if x0_ <= lx <= x1_ and y0_ <= ly <= y1_:
                return True
        return skip_tri(p)
    if kind == "hip":
        hx = (x_r - x_l) / 2
        hy = (d / 2 + jet[0] + d / 2 + jet[2]) / 2
        cy = (-(d / 2 + jet[0]) + (d / 2 + jet[2])) / 2
        g_ = rise / hx
        rinfo = K.hip_roof(mb, F, (x_l + x_r) / 2, cy, hx, hy, ze, g_, rng, over=ov[0], m=rm, m2=rm2,
                           alt=R.get("alt", 0.04), sag=R.get("sag", 0.3), course=R.get("course", 1.7),
                           tile=R.get("tile", (2.1, 3.3)), bevel=rbev, patches=R.get("patches", True),
                           skip=skip if (plan_skip or tri_skip) else None, end_over=ends[0],
                           under_skip=skip_tri if tri_skip else None)
        z_r = rinfo["z_r"]
    else:
        rinfo = K.gable_roof(mb, F, cxr, ya, yb, z_r, rng, sides=sides, ends=((ends[0], hips[0]), (ends[1], hips[1])),
                             m=rm, m2=rm2, alt=R.get("alt", 0.04), sag=R.get("sag", 0.3), holes=holes,
                             tile=R.get("tile", (2.1, 3.3)), course=R.get("course", 1.7), rafters=R.get("rafters", 0.0),
                             horns=R.get("horns", (True, True)), th=R.get("th", 0.44), lip=R.get("lip", 0.32),
                             bevel=rbev, skew=skew, patches=R.get("patches", True), row_jit=R.get("row_jit", 0.25))
    info.update(z_r=z_r, x_l=x_l, x_r=x_r, ya=ya, yb=yb, roof=rinfo, zs=zs, ze=ze)
    # ---------------------------------------------------------------- anexos
    for lt in V.get("lean", []):
        Fe, Le = EF[lt["edge"]]
        s0, s1 = lt["s0"], lt["s1"]
        dep = lt["depth"]
        yb_, zb_ = K.lean_to(mb, Fe, s0, s1, 0.0, dep, z0 + lt["z_hi"], z0 + lt["z_lo"], rng, -1, m=rm, m2=rm2,
                             area=area, z_ground=z0, sag=lt.get("sag", 0.12), bevel=rbev, alt=0.05)
        what = lt.get("content", "logs")
        if what == "logs":
            L_ = s1 - s0
            npile = max(1, int(L_ / 3.4))
            for i in range(npile):
                xx = s0 + L_ * (i + 0.5) / npile
                K.log_pile(mb, Fe, xx, -dep * 0.42, z0 + 0.05, min(2.8, L_ / npile - 0.4), 3, rng)
            if area:
                q = Fe.p((s0 + s1) / 2, -dep * 0.42)
                col_box(area, (s1 - s0 - 0.6, 2.4, 2.4), (q.x, q.y, z0 + 1.2), (0, 0, Fe.a))
            K.chopping_block(mb, Fe, s1 + 1.0, -dep - 0.8, z0, rng)
        elif what == "ore":
            # telheiro de minerio: carrinho de mao + monte de pedra com cristal (o mineiro traz amostras para casa)
            from fm_parts import crystal_cluster
            for i in range(3):
                q = Fe.p(s0 + 1.4 + i * 1.3, -dep * 0.45)
                mb.rock((q.x, q.y, z0 + 0.5), (1.6, 1.4, 1.1), "Stone_Dark", 1)
            crystal_cluster(mb, tuple(Fe.p(s0 + 2.6, -dep * 0.45, z0 + 0.8)), 0.32, "Crystal_Blue", rng, 3)
            if area:
                q = Fe.p((s0 + s1) / 2, -dep * 0.45)
                col_box(area, (s1 - s0 - 0.6, 2.4, 2.0), (q.x, q.y, z0 + 1.0), (0, 0, Fe.a))
    P = V.get("porch")
    if P:
        Fe, Le = EF[0]
        K.lean_to(mb, Fe, P["s0"], P["s1"], 0.0, P["depth"], z0 + P["z_hi"], z0 + P["z_lo"], rng, -1, m=rm, m2=rm2,
                  area=area, z_ground=z0, sag=0.1, bevel=rbev, alt=0.05)
        K.lbox(mb, Fe, (P["s1"] - P["s0"], P["depth"] - 0.2, 0.35), (P["s0"] + P["s1"]) / 2, -P["depth"] / 2 - 0.1,
               z0 + 0.12, "Wood_Plank", 0.0)
        if P.get("bench"):
            bs0, bs1 = P["bench"]
            K.lbox(mb, Fe, (bs1 - bs0, 1.3, 0.35), (bs0 + bs1) / 2, -0.9, z0 + 1.9, "Wood_Plank", 0.0)
            for bx in (bs0 + 0.4, bs1 - 0.4):
                K.lbox(mb, Fe, (0.4, 1.1, 1.7), bx, -0.9, z0 + 1.0, "Wood_Dark", 0.0)
            if area:
                q = Fe.p((bs0 + bs1) / 2, -0.9)
                col_box(area, (bs1 - bs0, 1.4, 2.2), (q.x, q.y, z0 + 1.1), (0, 0, Fe.a))
    if OS:
        # anexo baixo sob o prolongamento da agua (saltbox / catslide): parede de tabuas, sem porta
        g = rise / hw_r
        xo = w / 2 + OS["depth"]

        def zroof(x):
            return z_r - g * (x - cxr) - 0.45
        y0o, y1o = OS["y0"], OS["y1"]
        K.vprism(mb, F, [(y0o, z0), (y1o, z0), (y1o, zroof(xo)), (y0o, zroof(xo))], xo - 0.5, xo, "Wood_Plank", "x")
        for yy in (y0o, y1o - 0.5):
            K.vprism(mb, F, [(w / 2, z0), (xo, z0), (xo, zroof(xo)), (w / 2, zroof(w / 2))], yy, yy + 0.5,
                     "Wood_Plank", "y")
        y = y0o + 0.9
        while y < y1o - 0.6:
            K.lbox(mb, F, (0.22, 0.3, zroof(xo) - z0 - 0.3), xo + 0.05, y, (z0 + zroof(xo)) / 2 - 0.1, "Wood_Dark", 0.0)
            y += 1.25
        for yy in (y0o, y1o):
            K.lbox(mb, F, (0.7, 0.7, zroof(xo) - z0 + 0.2), xo - 0.2, yy, (z0 + zroof(xo)) / 2, "Wood_Dark", 0.0)
        K.lbox(mb, F, (0.5, y1o - y0o, 0.5), xo - 0.1, (y0o + y1o) / 2, z0 + 0.55, "Stone_Dark", 0.0)
        if OS.get("window"):
            yw = OS["window"]
            K.lbox(mb, F, (0.3, 1.6, 1.2), xo + 0.02, yw, z0 + 2.4, "Window_Dark", 0.0)
            K.lbox(mb, F, (0.4, 2.2, 0.35), xo + 0.1, yw, z0 + 1.7, "Wood_Dark", 0.0)
        if area:
            q = F.p((w / 2 + xo) / 2, (y0o + y1o) / 2)
            col_box(area, (OS["depth"], y1o - y0o, zroof(xo) - z0), (q.x, q.y, (z0 + zroof(xo)) / 2), F.r())
    for bw in bays:
        e = bw["edge"]
        Fe, Le = EF[e]
        je, jp = jet[e], jet[(e - 1) % 4]
        K.bay_window(mb, Fe, bw["s"] + jp, -je + t / 2 - tt / 2, z0 + bw["z0"], z0 + bw["z1"], bw["wd"], bw["out"], rng,
                     -1, roof_m=rm, glass_m=(win_lit if bw.get("lit", True) else "Window_Dark"))
    for (e, s0, s1, zl, zh) in V.get("shutters", []):
        Fe, Le = EF[e]
        je, jp = jet[e], jet[(e - 1) % 4]
        timber = z0 + zh > zs + 0.01 and upper == "timber"
        K.shutters(mb, Fe, s0 - 0.38 + (jp if timber else 0), s1 + 0.38 + (jp if timber else 0),
                   (-je if timber else -0.05), z0 + zl, z0 + zh, rng, -1, m=V.get("paint", "Wood_Plank"))
    for (e, s0, s1, zl) in V.get("flowers", []):
        Fe, Le = EF[e]
        je, jp = jet[e], jet[(e - 1) % 4]
        timber = z0 + zl > zs + 0.01
        K.flower_box(mb, Fe, s0 + (jp if timber else 0), s1 + (jp if timber else 0), (-je - 0.15 if timber else -0.1),
                     z0 + zl - 0.2, rng)
    for tl in V.get("tools", []):
        Fe, Le = EF[tl["edge"]]
        yfa = (yf_u if lower == "none" else 0.0) - 0.05
        K.tool_rack(mb, Fe, tl["s"], yfa, z0, rng, -1, kinds=tl.get("kinds", ("pick", "shovel")))
        if area:
            q = Fe.p(tl["s"], yfa - 0.7)
            col_box(area, (2.0 * len(tl.get("kinds", (1, 1))), 1.0, 5.8), (q.x, q.y, z0 + 2.9), (0, 0, Fe.a))
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
        K.door_leaves(mb, Fe0, ds0, ds1, -0.12 + (yf_u if lower == "none" else 0.0), z0 + 0.3, hl, rng, -1)
    if V.get("ties", True):
        for f in (-0.25, 0.25):
            K.lbox(mbi, F, (w - 2 * t_in + 0.4, 0.7, 0.8), 0, d * f, ze - 0.55, "Wood_Dark", 0.0)
    # ---------------------------------------------------------------- colisao da casca
    if area:
        yc_c, th_c = (yc_u, th_u) if lower == "none" else (t / 2, t)
        for e in range(4):
            Fe, Le = EF[e]
            segs = [(0.0, Le)]
            if e == 0:
                segs = [(0.0, ds0), (ds1, Le)]
                cc = Fe.p((ds0 + ds1) / 2, yc_c)
                col_box(area, (ds1 - ds0, th_c, ze - (z0 + dh)), (cc.x, cc.y, (z0 + dh + ze) / 2), (0, 0, Fe.a))
            for s0, s1 in segs:
                if s1 - s0 < 0.05:
                    continue
                cc = Fe.p((s0 + s1) / 2, yc_c)
                col_box(area, (s1 - s0, th_c, ze - z0), (cc.x, cc.y, (z0 + ze) / 2), (0, 0, Fe.a))
        ctr = F.p(0, 0)
        col_box(area, (w + 2, d + 2, 3), (ctr.x, ctr.y, ze + 2.0), F.r())
        ft = V.get("floor_top", 0.55)
        col_box(area, (w - 2 * t_in, d - 2 * t_in, ft), (ctr.x, ctr.y, z0 + ft / 2), F.r())
    return info
