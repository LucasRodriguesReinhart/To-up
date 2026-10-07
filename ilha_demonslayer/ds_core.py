# ds_core - COMPARTILHADO E CONGELADO (dono: integracao / onda 0). Roda SEMPRE, com blockout ou com os modulos de detalhe:
#   colisao de tudo que e andavel (ds_col.terrain_col)
#   TODOS os marcadores de gameplay, tirados da planta (os modulos de zona desenham em volta, nunca criam de novo):
#     mundo: WORLD_FROM_PREV (encaixe na Ilha 3), WORLD_ENTRY_DemonSlayer, PATH_ENTRY_CENTER(_nn),
#            ISLAND_EXIT_DemonSlayer, ISLAND_NEXT_ANCHOR_OnePiece
#     mineracao (clareira a ceu aberto): ORE_<RARIDADE>_<nn> (72), MiningZone_DemonSlayer, GP_Block_<nn>
#     invocacao: SUMMON_Main, SUMMON_Interact, SUMMON_PlayerPosition
#     pontos seguros: SAFE_*; audio: AUDIO_<Coisa> (familia + alcance)
#     efeitos e agua (feita no Roblox): FX_Fall_1_* (cascata), FX_Fall_2_* (sangradouro), FX_Forge_*, FX_Mist_*,
#            WATER_Pond, WATER_Flume, WATER_Tailrace, WATER_Channel
#   portao de compra ONE PIECE: o asset APROVADO (ilha_naruto/il_gate_op.build_gate), sem redesenho, na cabeceira de
#   pedra depois da ponte de saida (NextAreaId = 5); marcadores GATE_OnePiece* / PURCHASE_UI_ANCHOR_OnePiece e a
#   colisao de bloqueio COL_GateOnePieceLock_001 sao do il_gate_std.
import math
import ds_lib as DL
from ds_lib import mk, yaw_to
import ds_layout as L
import ds_col

T0, T1, T2, T3, T4 = L.T0, L.T1, L.T2, L.T3, L.T4


def world_markers():
    mk("WORLD_FROM_PREV", (L.PREV_X, L.PREV_Y, L.DECK), (0, 0, yaw_to(0, 1)), 4.0, "ARROWS",
       props={"width": L.DECK_W, "deck_z": L.DECK, "prev": "ISLAND_NEXT_ANCHOR_DemonSlayer (Ilha 3 Shadow Garden)",
              "bridge_len": L.BRIDGE_IN_LEN,
              "note": "centro da borda do tabuleiro da ponte de chegada (reta de 100, sobe 2 ate o patio T0); "
                      "avanco = frente; tem de cair EXATO na ancora da Ilha 3"})
    sx, sy = L.SPAWN
    mk("WORLD_ENTRY_DemonSlayer", (sx, sy, T0 + 0.2), (0, 0, yaw_to(0, 1)), 3.0, "ARROWS",
       props={"note": "chegada da ilha (patio do torii, olhando a escada da trilha e a clareira)"})
    path = [(0.0, 22.0, T0), (-12.0, 37.0, T0), (-12.0, 56.0, T1), (-6.0, 96.0, T1), (0.0, 140.0, T1),
            (30.0, 200.0, T1), (45.0, 255.0, T1), (16.0, 350.0, T1), (16.0, 376.0, T1), (16.0, 401.0, T3),
            (30.0, 412.0, T3), (30.0, 438.0, T4), (10.0, 452.0, T4), (0.0, 464.0, T4)]
    for i, p in enumerate(path):
        mk("PATH_ENTRY_CENTER_%02d" % i, p, (0, 0, 0), 1.5, "SPHERE")
    mk("PATH_ENTRY_CENTER", path[6], (0, 0, 0), 3.0, "ARROWS",
       props={"waypoints": ";".join("%.1f,%.1f,%.1f" % p for p in path),
              "note": "patio -> Trilha -> antecampo -> centro da clareira -> pe da subida -> patio da forja"})
    ux, uy = L.exit_dir()
    yaw = yaw_to(ux, uy)
    mk("ISLAND_EXIT_DemonSlayer", (L.EXIT_START[0], L.EXIT_START[1], T4), (0, 0, yaw), 4.0, "ARROWS",
       props={"width": L.EXIT_W, "deck_z": T4, "heading_deg": L.EXIT_DEG,
              "note": "cabeca da ponte de saida (56, T4), depois do torii de saida"})
    ap = L.anchor_op_pos()
    fr = L.dir_to_roblox(ux, uy)
    pr = L.to_roblox(ap[0], ap[1], T4)
    mk("ISLAND_NEXT_ANCHOR_OnePiece", (ap[0], ap[1], T4), (0, 0, yaw), 4.0, "ARROWS",
       props={"width": L.EXIT_W, "deck_z": T4, "clear_h": L.NEXT_CLEAR_H, "heading_deg": L.EXIT_DEG,
              "next_area": L.NEXT_AREA_ID, "next_key": "OnePiece",
              "fwd_roblox": "%.4f,%.4f,%.4f" % fr,
              "pos_roblox": "%.2f,%.2f,%.2f" % pr,
              "orientation_roblox": "0,%.1f,0" % (math.degrees(math.atan2(-fr[0], -fr[2])) % 360.0),
              "guard": "PROVISORIO: COL_DSAnchorGuard_* + DS_Exit_AnchorGuard (next_island_guard=True)",
              "guard_note": "a integracao da One Piece REMOVE a guarda quando a ponte seguinte encosta aqui"})


def ore_markers():
    for kind, i, x, y, r in L.ore_points():
        mk("ORE_%s_%02d" % (kind, i), (x, y, T1), size=r, kind="SPHERE", props={"rarity": kind, "radius": r})
    x0, y0, x1, y1 = L.MINE_RECT
    mk("MiningZone_DemonSlayer", ((x0 + x1) / 2, (y0 + y1) / 2, T1), (0, 0, yaw_to(0, 1)), size=(x1 - x0) / 2,
       kind="CUBE", props={"kind": "mining", "floor": T1, "sx": x1 - x0, "sy": y1 - y0, "open_sky": True,
                           "note": "clareira natural a CEU ABERTO (sem 'ceil': o script usa piso + 28); o jogo usa "
                                   "ORE_* + grade hexagonal + bloqueios GP_Block_*; frente = +Y local"})


def spawn_blocks():
    """bloqueios do SpawnMinerio (circulos): anel 'borda' a +3 do retangulo (o builder tira o tamanho da zona do
    min/max dos 'borda'), 'canto' = recorte dos 4 cantos (area util em elipse, nao retangulo), 'corredor' = chegadas da
    trilha e do bambuzal e o pe da subida livres"""
    n = 0

    def blk(x, y, r, kind):
        nonlocal n
        n += 1
        mk("GP_Block_%02d" % n, (x, y, T1), size=r, kind="CIRCLE", props={"radius": round(r, 2), "kind": kind})
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
    for x, y in ((6.0, 184.0), (14.0, 192.0), (60.0, 184.0), (16.0, 326.0), (16.0, 318.0)):
        blk(x, y, 5.0, "corredor")
    return n


def summon_markers():
    tx, ty = L.SUMMON_TOWER
    a = math.radians(L.SUMMON_FACE_DEG)
    ux, uy = math.cos(a), math.sin(a)
    mk("SUMMON_Main", (tx, ty, T3), (0, 0, yaw_to(ux, uy)), 3.0, "ARROWS",
       props={"note": "torre de invocacao AMS (estrela + aneis + torre + nucleo, familia da Ilha 1), frente para -X "
                      "local (oeste: clareira e entrada)"})
    d = L.SUMMON_INTERACT_D
    mk("SUMMON_Interact", (tx + ux * d, ty + uy * d, T3), (0, 0, 0), 2.0, "SPHERE",
       props={"note": "gabinete invisivel do Gacha_nichirin (prompt Invocar)"})
    d = L.SUMMON_PLAYER_D
    mk("SUMMON_PlayerPosition", (tx + ux * d, ty + uy * d, T3), (0, 0, yaw_to(-ux, -uy)), 2.0, "ARROWS",
       props={"note": "onde o jogador fica olhando a torre (pad do gacha)"})


def safe_markers():
    pc = L.exit_point(L.EXIT_BRIDGE_LEN + L.PIER[1] / 2)
    pts = [("SAFE_Entrada", (0.0, 24.0), T0), ("SAFE_Ponte_Chegada", (0.0, -60.0), L.DECK + 0.8),
           ("SAFE_Trilha", (-12.0, 80.0), T1), ("SAFE_Vila_Baixa", (-72.0, 160.0), T1),
           ("SAFE_Vila_Alta", (-80.0, 270.0), T2), ("SAFE_Clareira_S", (30.0, 160.0), T1),
           ("SAFE_Clareira_N", (40.0, 350.0), T1), ("SAFE_Summon", (166.0, 300.0), T3),
           ("SAFE_Patamar", (16.0, 406.0), T3), ("SAFE_Forja_Patio", (0.0, 452.0), T4),
           ("SAFE_Patio_Carvao", (-100.0, 410.0), T4), ("SAFE_Saida", (-106.0, 556.0), T4),
           ("SAFE_Cabeceira", pc, T4)]
    for nm, (x, y), z in pts:
        mk(nm, (x, y, z), (0, 0, 0), 2.0, "SPHERE", props={"note": "ponto seguro da rede de quedas"})


def audio_markers():
    fx, fy = L.FURNACE_MOUTH[:2]
    pts = [("AUDIO_Forge", (fx, fy - 2.0, T4 + 4.0), "fire", 40.0, None),
           ("AUDIO_Waterwheel", (L.WHEEL[0], L.WHEEL[1], L.WHEEL_AXLE_Z), "water", 30.0, None),
           ("AUDIO_Cascade", (L.CASCADE[0], L.CASCADE[1] - 4.0, T1 + 6.0), "water", 50.0, None),
           ("AUDIO_Pond", (L.POND_C[0], L.POND_C[1] - 8.0, T1 + 1.0), "water", 30.0, None),
           ("AUDIO_Bamboo", (50.0, 80.0, L.bamboo_z(50.0, 80.0) + 4.0), "wind", 50.0, None),
           ("AUDIO_Summon", (L.SUMMON_TOWER[0], L.SUMMON_TOWER[1], T3 + 6.0), "energy", 36.0, None),
           ("AUDIO_Clearing", (L.MINE_C[0], L.MINE_C[1], T1 + 8.0), "wind", 120.0, None),
           ("AUDIO_Village", (-100.0, 240.0, T2 + 4.0), "wind", 60.0, "baixo")]
    for nm, p, fam, rng, vol in pts:
        props = {"family": fam, "range": rng}
        if vol:
            props["volume"] = vol
        mk(nm, p, (0, 0, 0), 2.0, "SPHERE", props=props)


def _wp(pts):
    return ";".join("%.2f,%.2f,%.2f" % p for p in pts)


def fx_markers():
    """agua e efeitos (feitos no Roblox a partir destes marcadores; no Blender so a pedra estanque). Valores da onda 0
    ESTIMADOS na planta: o ds_water (onda 2c) mede na pedra e corrige."""
    cx, cy, ztop, zbot = L.CASCADE
    south = yaw_to(0, -1)
    mk("FX_Fall_1_Lip", (cx, cy, ztop - 0.2), (0, 0, south), 3.0, "SINGLE_ARROW",
       props={"fx": "nevoa_borda", "width": 6.0, "drop": round(ztop - zbot, 2),
              "note": "cascata unica: borda do canal no muro do terraco da forja -> lagoa (20); agua do Roblox"})
    mk("FX_Fall_1_Step", (cx, cy - 1.6, (ztop + zbot) / 2), (0, 0, south), 2.0, "SPHERE", props={"fx": "espuma_degrau"})
    mk("FX_Fall_1_Base", (cx, cy - 3.0, zbot - 0.4), (0, 0, south), 6.0, "SPHERE", props={"fx": "nevoa_base"})
    sx, sy = L.SPILL
    east = yaw_to(1, 0.3)
    mk("FX_Fall_2_Lip", (sx + 2.0, sy + 1.0, L.SHOULDER - 0.2), (0, 0, east), 2.0, "SINGLE_ARROW",
       props={"fx": "nevoa_borda", "width": 2.6, "note": "sangradouro fino pela ravina leste (unica queda para fora)"})
    mk("FX_Fall_2_Base", (sx + 7.0, sy + 2.5, 8.0), (0, 0, east), 4.0, "SPHERE", props={"fx": "nevoa_base"})
    chx, chy, s = L.CHIMNEY
    mk("FX_Forge_Smoke", (chx, chy, L.CHIMNEY_TOP + 0.5), (0, 0, 0), 3.0, "SPHERE",
       props={"fx": "fumaca", "Dist": 400.0, "note": "topo da chamine (fumaca controlada)"})
    fx, fy, fw, fh = L.FURNACE_MOUTH
    mk("FX_Forge_Embers", (fx, fy - 1.0, T4 + 3.0), (0, 0, south), 2.0, "SPHERE",
       props={"fx": "brasas", "Dist": 120.0, "width": fw, "height": fh})
    mk("FX_Mist_Bamboo", (48.0, 84.0, L.bamboo_z(48.0, 84.0) + 1.0), (0, 0, 0), 4.0, "SPHERE",
       props={"fx": "nevoa_baixa", "radius": 30.0})
    mk("FX_Mist_Ravine", (142.0, 214.0, L.SHOULDER + 1.0), (0, 0, 0), 4.0, "SPHERE",
       props={"fx": "nevoa_baixa", "radius": 24.0})
    px, py = L.POND_C
    xs = [p[0] for p in L.POND]
    ys = [p[1] for p in L.POND]
    mk("WATER_Pond", (px, py, T1 - 0.4), (0, 0, yaw_to(0, 1)), 4.0, "CUBE",
       props={"shape": "poligono", "level": T1 - 0.4, "floor": T1 - 1.6, "depth": 1.2,
              "sx": round(max(xs) - min(xs), 2), "sy": round(max(ys) - min(ys), 2),
              "waypoints": _wp([(x, y, T1 - 0.4) for x, y in L.POND]),
              "note": "lagoa ao pe da cascata (contorno em waypoints); agua do Roblox"})
    f = L.FLUME
    zs = [L.SPRING[2] - 0.5, L.SPRING[2] - 1.6, L.WHEEL_AXLE_Z + L.WHEEL[2] / 2 + 0.6]
    mk("WATER_Flume", (f[0][0], f[0][1], zs[0]), (0, 0, 0), 2.0, "SINGLE_ARROW",
       props={"waypoints": _wp([(x, y, z) for (x, y), z in zip(f, zs)]), "widths": "2.0,2.0,2.0",
              "note": "aqueduto de madeira: nascente -> topo da roda d'agua"})
    t = L.TAILRACE
    mk("WATER_Tailrace", (t[0][0], t[0][1], T4 - 0.6), (0, 0, 0), 2.0, "SINGLE_ARROW",
       props={"waypoints": _wp([(x, y, T4 - 0.6) for x, y in t]), "widths": ",".join("3.0" for _ in t),
              "note": "canal de pedra da roda ate a borda da cascata"})
    c = L.CHANNEL
    mk("WATER_Channel", (c[0][0], c[0][1], T1 - 0.6), (0, 0, 0), 2.0, "SINGLE_ARROW",
       props={"waypoints": _wp([(x, y, T1 - 0.6) for x, y in c]), "widths": ",".join("3.0" for _ in c),
              "note": "canal da lagoa pela margem leste da clareira (sob a pontezinha do summon) ate o sangradouro"})
    _water_measured()


def _water_measured():
    """ACRESCIMO ONDA 2c (ds_water): os FX_Fall_1/2_*, FX_Mist_Ravine, WATER_Pond/_Tailrace/_Channel passam a ser os da
    PEDRA do ds_water (ds_water.water_markers(): as mesmas constantes que desenham a pedra; o ds_water.build() ainda
    confere por raios na cena). Posicao, rumo e props sao SUBSTITUIDOS. Sem o modulo ficam as estimativas acima.
    WATER_Flume (aqueduto de madeira) nao e tocado: e do ds_forge (onda 2b)."""
    try:
        import ds_water
    except ImportError:
        return
    import bpy
    for nm, (loc, yaw, props) in ds_water.water_markers().items():
        o = bpy.data.objects.get(nm)
        if o is None:
            continue
        o.location = loc
        o.rotation_euler = (0.0, 0.0, yaw)
        for k in list(o.keys()):
            del o[k]
        for k, v in props.items():
            o[k] = v


def op_gate():
    """portao APROVADO da galeria (il_gate_op, 'portao do timao'), sem redesenho, na cabeceira; area_id = 5"""
    import il_gate_op
    import bpy
    g = L.gate_op_pos()
    il_gate_op.build_gate(g[0], g[1], T4, L.gate_yaw())
    for o in bpy.data.objects:
        if o.name.startswith("GATE_OnePiece") and "area_id" in o.keys():
            o["area_id"] = L.NEXT_AREA_ID
    for o in [o for o in bpy.data.objects if o.type == "CAMERA" and o.name.startswith(("CAM_Gate_", "CAM_Gates_"))]:
        bpy.data.objects.remove(o, do_unlink=True)
    for o in [o for o in bpy.data.objects if o.name.startswith("SCALE_Gate")]:
        o.hide_render = True


def build():
    ds_col.terrain_col()
    world_markers()
    ore_markers()
    spawn_blocks()
    summon_markers()
    safe_markers()
    audio_markers()
    fx_markers()
    op_gate()
