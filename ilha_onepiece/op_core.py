# op_core - COMPARTILHADO E CONGELADO (dono: integracao / M1). Roda SEMPRE, com blockout ou com os modulos de detalhe:
#   colisao de tudo que e andavel (op_col.terrain_col)
#   TODOS os marcadores de gameplay, tirados da planta (os modulos de zona desenham em volta, nunca criam de novo):
#     mundo: WORLD_FROM_PREV (encaixe na Ilha 4), WORLD_ENTRY_OnePiece, PATH_ENTRY_CENTER(_nn),
#            ISLAND_EXIT_OnePiece, ISLAND_NEXT_ANCHOR_OnePunchMan
#     mineracao (PRACA a ceu aberto): ORE_<RARIDADE>_<nn> (72), MiningZone_OnePiece, GP_Block_<nn>
#     invocacao: SUMMON_Main, SUMMON_Interact, SUMMON_PlayerPosition
#     pontos seguros: SAFE_*; audio: AUDIO_<Coisa> (familia + alcance)
#     agua e efeitos (feitos no Roblox): WATER_Sea (mar local, so cliente na area 5), WATER_Basin, WATER_CanalE,
#            WATER_CanalW, FX_Fall_Castle_*, FX_Fall_E_*, FX_Fall_W_*, FX_Weir_*, FX_Petals_Tree, FX_Mist_*
#   portao de compra ONE PUNCH MAN: o asset da galeria (ilha_naruto/il_gate_opm.build_gate, mesma familia do portao One
#   Piece aprovado), sem redesenho, no promontorio depois da ponte vermelha de saida (NextAreaId = 6);
#   marcadores GATE_OnePunchMan* / PURCHASE_UI_ANCHOR_OnePunchMan e COL_GateOnePunchManLock_001 sao do il_gate_std.
#   A ENTRADA de Wano NAO tem portao de compra: o GATE_OnePiece (aprovado) fica na Demon Slayer, antes da ancora.
import math
import op_lib as DL
from op_lib import mk, yaw_to
import op_layout as L
import op_col

T0, T1, P, CF, CC = L.T0, L.T1, L.P, L.CF, L.CC


def world_markers():
    mk("WORLD_FROM_PREV", (L.PREV_X, L.PREV_Y, L.DECK), (0, 0, yaw_to(0, 1)), 4.0, "ARROWS",
       props={"width": L.DECK_W, "deck_z": L.DECK, "prev": "ISLAND_NEXT_ANCHOR_OnePiece (Ilha 4 Demon Slayer, 9cc4bef4)",
              "bridge_len": L.BRIDGE_IN_LEN,
              "note": "centro da borda do tabuleiro da ponte de chegada (reta de 120, sobe 4 ate o patio do torii); "
                      "avanco = frente; tem de cair EXATO na ancora da Ilha 4"})
    sx, sy = L.SPAWN
    mk("WORLD_ENTRY_OnePiece", (sx, sy, T0 + 0.2), (0, 0, yaw_to(0, 1)), 3.0, "ARROWS",
       props={"note": "chegada da ilha (patio do grande torii, olhando a rua de chegada e o castelo)"})
    path = [(0.0, 24.0, T0), (0.0, 33.0, T0), (0.0, 46.0, T1), (0.0, 100.0, T1), (0.0, 108.0, T1), (0.0, 122.0, P),
            (0.0, 160.0, P), (L.MINE_C[0], L.MINE_C[1], P), (0.0, 300.0, P), (0.0, 311.0, P), (0.0, 330.0, CF)]
    for i, p in enumerate(path):
        mk("PATH_ENTRY_CENTER_%02d" % i, p, (0, 0, 0), 1.5, "SPHERE")
    mk("PATH_ENTRY_CENTER", path[7], (0, 0, 0), 3.0, "ARROWS",
       props={"waypoints": ";".join("%.1f,%.1f,%.1f" % p for p in path),
              "note": "patio do torii -> rua de chegada -> escadaria -> centro da praca -> adro do castelo"})
    ux, uy = L.exit_dir()
    yaw = yaw_to(ux, uy)
    mk("ISLAND_EXIT_OnePiece", (L.EXIT_START[0], L.EXIT_START[1], T1), (0, 0, yaw), 4.0, "ARROWS",
       props={"width": L.EXIT_W, "deck_z": T1, "heading_deg": L.EXIT_DEG,
              "note": "cabeca da ponte vermelha de saida (88, T1) na borda leste do terraco do summon"})
    ap = L.anchor_opm_pos()
    fr = L.dir_to_roblox(ux, uy)
    pr = L.to_roblox(ap[0], ap[1], T1)
    mk("ISLAND_NEXT_ANCHOR_OnePunchMan", (ap[0], ap[1], T1), (0, 0, yaw), 4.0, "ARROWS",
       props={"width": L.EXIT_W, "deck_z": T1, "clear_h": L.NEXT_CLEAR_H, "heading_deg": L.EXIT_DEG,
              "next_area": L.NEXT_AREA_ID, "next_key": L.NEXT_KEY,
              "fwd_roblox": "%.4f,%.4f,%.4f" % fr,
              "pos_roblox": "%.2f,%.2f,%.2f" % pr,
              "orientation_roblox": "0,%.1f,0" % (math.degrees(math.atan2(-fr[0], -fr[2])) % 360.0),
              "guard": "PROVISORIO: COL_OPAnchorGuard_* + OP_Exit_AnchorGuard (next_island_guard=True)",
              "guard_note": "One Punch Man (area 6) ainda nao existe: termino SEGURO. A integracao da area 6 REMOVE a "
                            "guarda quando a ponte seguinte encosta aqui (nao ha passagem que leva a queda)"})


def ore_markers():
    for kind, i, x, y, r in L.ore_points():
        mk("ORE_%s_%02d" % (kind, i), (x, y, P), size=r, kind="SPHERE", props={"rarity": kind, "radius": r})
    x0, y0, x1, y1 = L.MINE_RECT
    mk("MiningZone_OnePiece", ((x0 + x1) / 2, (y0 + y1) / 2, P), (0, 0, yaw_to(0, 1)), size=(x1 - x0) / 2,
       kind="CUBE", props={"kind": "mining", "floor": P, "sx": x1 - x0, "sy": y1 - y0, "open_sky": True,
                           "note": "PRACA central a CEU ABERTO (sem 'ceil': o script usa piso + 28); o jogo usa ORE_* + "
                                   "grade hexagonal + bloqueios GP_Block_*; frente = +Y local (castelo); emblema de "
                                   "chao RENTE no centro (sem colisao)"})


def spawn_blocks():
    """bloqueios do SpawnMinerio (circulos): anel 'borda' a +3 do retangulo (o builder tira o tamanho da zona do
    min/max dos 'borda'), 'canto' = recorte dos 4 cantos (area util em elipse, nao retangulo)"""
    n = 0

    def blk(x, y, r, kind):
        nonlocal n
        n += 1
        mk("GP_Block_%02d" % n, (x, y, P), size=r, kind="CIRCLE", props={"radius": round(r, 2), "kind": kind})
    mx0, my0, mx1, my1 = L.MINE_RECT
    x0, y0, x1, y1 = mx0 - 3.0, my0 - 3.0, mx1 + 3.0, my1 + 3.0
    k = 12
    pts = []
    for i in range(k + 1):
        t = i / k
        for p in ((x0 + (x1 - x0) * t, y0), (x0 + (x1 - x0) * t, y1), (x0, y0 + (y1 - y0) * t), (x1, y0 + (y1 - y0) * t)):
            if not any(abs(p[0] - q[0]) < 0.01 and abs(p[1] - q[1]) < 0.01 for q in pts):
                pts.append(p)
    for x, y in pts:
        blk(x, y, 5.5, "borda")
    cx, cy = L.MINE_C
    hx, hy = (mx1 - mx0) / 2 - 3.0, (my1 - my0) / 2 - 3.0
    gx = mx0 + 5.0
    while gx <= mx1 - 5.0 + 1e-6:
        gy = my0 + 5.0
        while gy <= my1 - 5.0 + 1e-6:
            if ((gx - cx) / hx) ** 2 + ((gy - cy) / hy) ** 2 > 1.16:
                blk(gx, gy, 6.0, "canto")
            gy += 10.0
        gx += 10.0
    return n


def summon_markers():
    tx, ty = L.SUMMON_TOWER
    a = math.radians(L.SUMMON_FACE_DEG)
    ux, uy = math.cos(a), math.sin(a)
    mk("SUMMON_Main", (tx, ty, T1), (0, 0, yaw_to(ux, uy)), 3.0, "ARROWS",
       props={"note": "torre de invocacao AMS (estrela + aneis + torre + nucleo, familia da Ilha 1), frente para -X "
                      "local (oeste: praca); terraco lateral na transicao para o porto"})
    d = L.SUMMON_INTERACT_D
    mk("SUMMON_Interact", (tx + ux * d, ty + uy * d, T1), (0, 0, 0), 2.0, "SPHERE",
       props={"note": "gabinete invisivel do Gacha_mare (prompt Invocar)"})
    d = L.SUMMON_PLAYER_D
    mk("SUMMON_PlayerPosition", (tx + ux * d, ty + uy * d, T1), (0, 0, yaw_to(-ux, -uy)), 2.0, "ARROWS",
       props={"note": "onde o jogador fica olhando a torre (pad do gacha)"})


def safe_markers():
    pts = [("SAFE_Entrada", (0.0, 24.0), T0), ("SAFE_Ponte_Chegada", (0.0, -60.0), L.DECK + 2.0),
           ("SAFE_Rua_Chegada", (0.0, 70.0), T1), ("SAFE_Praca_S", (0.0, 136.0), P), ("SAFE_Praca_N", (0.0, 296.0), P),
           ("SAFE_Praca_O", (-96.0, 216.0), P), ("SAFE_Praca_L", (96.0, 216.0), P), ("SAFE_Summon", (150.0, 244.0), T1),
           ("SAFE_Bairro_Canal", (-130.0, 80.0), T1), ("SAFE_Oeste_Alem", (-190.0, 230.0), P),
           ("SAFE_Terraco_Alto", (-120.0, 350.0), L.W3), ("SAFE_Adro", (40.0, 324.0), CF),
           ("SAFE_Castelo", (-30.0, 440.0), CC), ("SAFE_Porto_Alto", (170.0, 104.0), L.HMID),
           ("SAFE_Cais", (190.0, 70.0), L.HARBOR), ("SAFE_NE", (150.0, 274.0), P),
           ("SAFE_Promontorio", L.exit_point(L.EXIT_BRIDGE_LEN + 8.0), T1)]
    for nm, (x, y), z in pts:
        mk(nm, (x, y, z), (0, 0, 0), 2.0, "SPHERE", props={"note": "ponto seguro da rede de quedas"})


def audio_markers():
    pts = [("AUDIO_Plaza", (L.MINE_C[0], L.MINE_C[1], P + 8.0), "wind", 130.0, None),
           ("AUDIO_Street", (0.0, 76.0, T1 + 4.0), "wind", 50.0, "baixo"),
           ("AUDIO_CastleFall", (0.0, 340.0, CF + 4.0), "water", 60.0, None),
           ("AUDIO_FallE", (L.FALL_E[0], L.FALL_E[1], 70.0), "water", 60.0, None),
           ("AUDIO_FallW", (L.FALL_W[0], L.FALL_W[1], 70.0), "water", 55.0, None),
           ("AUDIO_Wheel", (L.WHEEL[0], L.WHEEL[1], L.WHEEL_AXLE_Z), "water", 30.0, None),
           ("AUDIO_Harbor", (220.0, 120.0, L.HARBOR + 4.0), "water", 80.0, None),
           ("AUDIO_Summon", (L.SUMMON_TOWER[0], L.SUMMON_TOWER[1], T1 + 6.0), "energy", 36.0, None),
           ("AUDIO_Castle", (0.0, 380.0, CC + 6.0), "wind", 60.0, None)]
    for nm, p, fam, rng, vol in pts:
        props = {"family": fam, "range": rng}
        if vol:
            props["volume"] = vol
        mk(nm, p, (0, 0, 0), 2.0, "SPHERE", props=props)


def _wp(pts):
    return ";".join("%.2f,%.2f,%.2f" % p for p in pts)


def fx_markers():
    """agua e efeitos (feitos no Roblox a partir destes marcadores; no Blender so a pedra estanque). Valores M1
    ESTIMADOS na planta: o modulo de agua (M3/M4) mede na pedra e corrige."""
    x, y, ztop, zbot = L.CASTLE_FALL
    south = yaw_to(0, -1)
    mk("FX_Fall_Castle_Lip", (x, y, ztop), (0, 0, south), 3.0, "SINGLE_ARROW",
       props={"fx": "nevoa_borda", "width": 7.0, "drop": round(ztop - zbot, 2),
              "note": "CACHOEIRA DO CASTELO: nasce na rocha sob a varanda vermelha e cai na bacia do adro (agua do Roblox)"})
    mk("FX_Fall_Castle_Base", (x, y - 6.0, zbot - 0.3), (0, 0, south), 6.0, "SPHERE", props={"fx": "nevoa_base"})
    for nm, (fx, fy, zt, zb), ang in (("E", L.FALL_E, yaw_to(0.6, -0.8)), ("W", L.FALL_W, yaw_to(0, -1))):
        mk("FX_Fall_%s_Lip" % nm, (fx, fy, zt), (0, 0, ang), 3.0, "SINGLE_ARROW",
           props={"fx": "nevoa_borda", "width": 6.0, "drop": round(zt - zb, 2),
                  "note": "queda %s: canal -> %s" % (nm, "enseada do porto" if nm == "E" else "mar (falesia SO)")})
        mk("FX_Fall_%s_Base" % nm, (fx, fy - 4.0, zb + 0.4), (0, 0, ang), 6.0, "SPHERE", props={"fx": "espuma_mar"})
    for nm, (wx, wy, zt, zb) in L.WEIRS:
        mk("FX_%s" % nm, (wx, wy, zt), (0, 0, 0), 2.0, "SINGLE_ARROW",
           props={"fx": "degrau_agua", "drop": round(zt - zb, 2)})
    tr = L.TREE_CANOPY[0][0]
    mk("FX_Petals_Tree", tr, (0, 0, 0), 4.0, "SPHERE",
       props={"fx": "petalas", "Dist": 320.0, "radius": 40.0, "note": "UM emissor de petalas na copa (discreto)"})
    mk("FX_Mist_CastleFall", (0.0, 340.0, CF + 1.0), (0, 0, 0), 4.0, "SPHERE", props={"fx": "nevoa_baixa", "radius": 14.0})
    mk("WATER_Sea", (L.SEA_C[0], L.SEA_C[1], L.SEA), (0, 0, 0), 20.0, "CUBE",
       props={"shape": "quadrado", "level": L.SEA, "size": L.SEA_SIZE, "client_only": True, "area": 5,
              "color": "48,176,196",
              "note": "mar LOCAL turquesa de Wano: so no cliente e so com o jogador na area 5 (como o mar de nuvens da "
                      "DS); esconde a quilha; vista de Wano, a DS aparece como ilha saindo do mar (topo da quilha DS "
                      "53,6 > 46)"})
    bx = [p[0] for p in L.BASIN]
    by = [p[1] for p in L.BASIN]
    mk("WATER_Basin", (0.0, 342.0, L.BASIN_Z), (0, 0, yaw_to(0, 1)), 4.0, "CUBE",
       props={"shape": "poligono", "level": L.BASIN_Z, "floor": L.BASIN_Z - 1.6, "sx": round(max(bx) - min(bx), 2),
              "sy": round(max(by) - min(by), 2), "waypoints": _wp([(x_, y_, L.BASIN_Z) for x_, y_ in L.BASIN]),
              "note": "bacia do adro ao pe da cachoeira do castelo"})
    for nm, pts, w in (("WATER_CanalE", L.CANAL_E, 6.0), ("WATER_CanalW", L.CANAL_W, 8.0)):
        mk(nm, pts[0], (0, 0, 0), 2.0, "SINGLE_ARROW",
           props={"waypoints": _wp(pts), "widths": ",".join("%.1f" % w for _ in pts),
                  "note": "canal de pedra (agua do Roblox); degraus nos FX_Weir_*"})
    sx, sy, sz = L.SPRING_W
    mk("FX_Spring_W", (sx, sy, sz), (0, 0, south), 2.0, "SINGLE_ARROW",
       props={"fx": "bica", "note": "nascente do canal oeste: bica no arrimo do terraco alto"})


def opm_gate():
    """portao da galeria (il_gate_opm, 'portao do heroi', mesma familia do One Piece aprovado), sem redesenho, no
    promontorio; area_id = 6"""
    import il_gate_opm
    import bpy
    g = L.gate_opm_pos()
    il_gate_opm.build_gate(g[0], g[1], T1, L.gate_yaw())
    for o in bpy.data.objects:
        if o.name.startswith("GATE_OnePunchMan") and "area_id" in o.keys():
            o["area_id"] = L.NEXT_AREA_ID
    for o in [o for o in bpy.data.objects if o.type == "CAMERA" and o.name.startswith(("CAM_Gate_", "CAM_Gates_"))]:
        bpy.data.objects.remove(o, do_unlink=True)
    for o in [o for o in bpy.data.objects if o.name.startswith("SCALE_Gate")]:
        o.hide_render = True


def build():
    op_col.terrain_col()
    world_markers()
    ore_markers()
    spawn_blocks()
    summon_markers()
    safe_markers()
    audio_markers()
    fx_markers()
    opm_gate()
