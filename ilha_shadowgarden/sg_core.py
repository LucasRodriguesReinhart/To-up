# sg_core - COMPARTILHADO E CONGELADO (dono: integracao). Roda SEMPRE, com blockout ou com os modulos de detalhe:
#   colisao de tudo que e andavel (sg_col.terrain_col)
#   TODOS os marcadores de gameplay, tirados da planta (os modulos de zona desenham em volta, nunca criam de novo):
#     mundo: WORLD_FROM_PREV (encaixe na Ilha 2), WORLD_ENTRY_ShadowGarden, PATH_ENTRY_CENTER(_nn),
#            ISLAND_EXIT_ShadowGarden, ISLAND_NEXT_ANCHOR_DemonSlayer
#     mineracao (Mining Hall): ORE_<RARIDADE>_<nn>, MiningZone_ShadowGarden, GP_Block_<nn>
#     invocacao: SUMMON_Main, SUMMON_Interact, SUMMON_PlayerPosition
#     craft: CRAFT_Station, PLAYER_INTERACT_Craft, NPC_Craft
#     dungeon: DUNGEON_Entrance, DUNGEON_Portal, DUNGEON_UI, DUNGEON_Return, DUNGEON_Spawn, DUNGEON_ExitPortal,
#              DUN_ROOM_<R>, DUN_ORE_<R>_<RARIDADE>_<nn>, DUN_SPAWN_<R>, DUN_LINK_<RaRb>, DUN_EXIT_R1 (ov09b)
#     audio: AUDIO_<Coisa> (familia + alcance); efeitos: FX_Fall_<n>_Lip/_Step(_Upper)/_Base
#     agua da fonte (feita no Roblox): WATER_Fountain_Basin, WATER_Fountain_Bowl_<n>, WATER_Fountain_Spout_<n>
#   portao de compra DEMON SLAYER: o asset APROVADO (ilha_naruto/il_gate_ds.build_gate), sem redesenho, no eixo da
#   ilhota da saida (NextAreaId = 4 depois da troca 3<->4, DECISOES.md D1).
import math
import sg_lib as SL
from sg_lib import mk, yaw_to
import sg_layout as L
import sg_col


def world_markers():
    mk("WORLD_FROM_PREV", (0.0, L.PREV_Y, L.DECK), (0, 0, 0), 4.0, "ARROWS",
       props={"width": L.DECK_W, "deck_z": L.DECK, "prev": "ISLAND_NEXT_ANCHOR_ShadowGarden (Ilha 2 Dragon Ball)",
              "note": "centro da borda do tabuleiro da ponte de chegada; avanco +Y (para dentro da ilha)"})
    sx, sy = L.ENTRY_SPAWN
    mk("WORLD_ENTRY_ShadowGarden", (sx, sy, L.P1 + 0.2), (0, 0, 0), 3.0, "ARROWS",
       props={"note": "chegada da ilha (depois do portico B, olhando a praca e o castelo)"})
    gt = L.stair_top("Gate")
    path = [(sx, sy, L.P1), (0.0, -142.0, L.P1), (-12.0, -118.0, L.P1), (0.0, -102.0, L.P1), (0.0, -80.0, L.P2),
            (0.0, -30.0, L.P2), (gt[0], gt[1] + 3.0, L.P3), (0.0, 30.0, L.P3), (0.0, 50.0, L.HALL), (0.0, 70.0, L.HALL)]
    for i, p in enumerate(path):
        mk("PATH_ENTRY_CENTER_%02d" % i, p, (0, 0, 0), 1.5, "SPHERE")
    mk("PATH_ENTRY_CENTER", path[-2], (0, 0, 0), 3.0, "ARROWS",
       props={"waypoints": ";".join("%.1f,%.1f,%.1f" % p for p in path)})
    ux, uy = L.exit_dir()
    yaw = yaw_to(ux, uy)
    mk("ISLAND_EXIT_ShadowGarden", (L.EXIT_START[0], L.EXIT_START[1], L.EXIT_Z), (0, 0, yaw), 4.0, "ARROWS",
       props={"width": L.EXIT_W, "deck_z": L.EXIT_Z, "heading_deg": L.EXIT_DEG})
    ap = L.anchor_pos()
    fr = L.dir_to_roblox(ux, uy)
    mk("ISLAND_NEXT_ANCHOR_DemonSlayer", (ap[0], ap[1], L.EXIT_Z), (0, 0, yaw), 4.0, "ARROWS",
       props={"width": L.DECK_W, "deck_z": L.EXIT_Z, "clear_h": 22.0, "heading_deg": L.EXIT_DEG,
              "next_area": L.NEXT_AREA_ID, "next_key": "DemonSlayer",
              "fwd_roblox": "%.4f,%.4f,%.4f" % fr,
              "guard": "PROVISORIO: COL_SGAnchorGuard_* (next_island_guard=True)",
              "guard_note": "a integracao da ilha Demon Slayer REMOVE o guarda quando a ponte seguinte encosta aqui"})


def ore_markers():
    for kind, i, x, y, r in L.ore_points():
        mk("ORE_%s_%02d" % (kind, i), (x, y, L.HALL), size=r, kind="SPHERE", props={"rarity": kind, "radius": r})
    x0, y0, x1, y1 = L.MINE_RECT
    mk("MiningZone_ShadowGarden", ((x0 + x1) / 2, (y0 + y1) / 2, L.HALL), size=(x1 - x0) / 2, kind="CUBE",
       props={"kind": "mining", "floor": L.HALL, "sx": x1 - x0, "sy": y1 - y0, "ceil": L.HALL_CEIL,
              "note": "Mining Hall (dentro do castelo); o jogo usa ORE_* + grade hexagonal + bloqueios GP_Block_*"})


def spawn_blocks():
    """bloqueios do SpawnMinerio (circulos) para o builder do Roblox: corredor da porta e anel junto as paredes do
    salao (kind='borda': o builder tira o tamanho da zona do min/max desses)"""
    n = 0

    def blk(x, y, r, kind):
        nonlocal n
        n += 1
        mk("GP_Block_%02d" % n, (x, y, L.HALL), size=r, kind="CIRCLE", props={"radius": round(r, 2), "kind": kind})
    lx, ly0, ly1, hw = L.MINE_DOOR_LANE
    y = ly0 + 2.0
    while y <= ly1:
        blk(lx, y, hw, "porta")
        y += 5.0
    x0, y0, x1, y1 = L.HALL_X0 + 3.0, L.HALL_Y0 + 3.0, L.HALL_X1 - 3.0, L.HALL_Y1 - 3.0
    k = 10
    for i in range(k + 1):
        t = i / k
        for x, y in ((x0 + (x1 - x0) * t, y0), (x0 + (x1 - x0) * t, y1), (x0, y0 + (y1 - y0) * t),
                     (x1, y0 + (y1 - y0) * t)):
            blk(x, y, 5.5, "borda")
    return n


def summon_markers():
    tx, ty = L.SUMMON_TOWER
    a = math.radians(L.SUMMON_FACE_DEG)
    ux, uy = math.cos(a), math.sin(a)
    mk("SUMMON_Main", (tx, ty, L.SUM), (0, 0, yaw_to(ux, uy)), 3.0, "ARROWS",
       props={"note": "torre de invocacao (familia das Ilhas 1 e 2), frente para +X (ponte)"})
    mk("SUMMON_Interact", (tx + ux * 7.0, ty + uy * 7.0, L.SUM), (0, 0, 0), 2.0, "SPHERE",
       props={"note": "gabinete invisivel do Gacha_sombra (prompt Invocar)"})
    mk("SUMMON_PlayerPosition", (tx + ux * 16.0, ty + uy * 16.0, L.SUM), (0, 0, yaw_to(-ux, -uy)), 2.0, "ARROWS",
       props={"note": "onde o jogador fica olhando a torre (pad do gacha)"})


def craft_markers():
    cx, cy = L.CRAFT_C
    a = math.radians(L.CRAFT_DOOR_DEG)
    ux, uy = math.cos(a), math.sin(a)
    mk("CRAFT_Station", (cx, cy, L.P2), (0, 0, yaw_to(ux, uy)), 2.5, "CUBE",
       props={"note": "caldeirao/bancada do alquimista: ProximityPrompt 'Craft' abre a pagina de receitas"})
    mk("PLAYER_INTERACT_Craft", (cx + ux * 5.0, cy + uy * 5.0, L.P2), (0, 0, yaw_to(-ux, -uy)), 2.0, "SPHERE",
       props={"radius": 8.0})
    mk("NPC_Craft", (cx - ux * 6.0, cy - uy * 6.0, L.P2), (0, 0, yaw_to(ux, uy)), 2.0, "ARROWS",
       props={"note": "alquimista atras do caldeirao, olhando a porta"})


def dungeon_markers():
    cx, cy, w, d = L.DUNGEON_HOUSE
    px, py = L.DUNGEON_PORTAL
    mk("DUNGEON_Portal", (px, py, L.P3), (0, 0, yaw_to(0, -1)), 3.0, "ARROWS",
       props={"note": "portal espiral no fundo da portaria (encara o sul)"})
    mk("DUNGEON_Entrance", (px, py - 6.0, L.P3), (0, 0, 0), 2.0, "SPHERE",
       props={"radius": 6.0, "note": "zona/prompt de entrada na corrida (so com ENTRY_OPEN)"})
    # centro da placa de contagem da fachada-portal (sg_dungeon: placa em P3+14..16,9, logo abaixo do vortice)
    mk("DUNGEON_UI", (cx, 58.1, L.P3 + 15.45), (0, 0, yaw_to(0, -1)), 2.0, "SINGLE_ARROW",
       props={"ui": "BillboardGui: estado e contagem da dungeon (XX:00 / XX:30)"})
    mk("DUNGEON_Return", (cx, cy - d / 2 - 8.0, L.P3 + 0.2), (0, 0, yaw_to(0, -1)), 2.0, "ARROWS",
       props={"note": "para onde o jogador volta ao sair/terminar (patio, em frente a porta)"})
    rooms = dict(L.DUN_ROOMS)
    for nm, (x0, y0, x1, y1) in L.DUN_ROOMS:
        mk("DUN_ROOM_%s" % nm, ((x0 + x1) / 2, (y0 + y1) / 2, L.DUN_Z), (0, 0, 0), (x1 - x0) / 2, "CUBE",
           props={"sx": x1 - x0, "sy": y1 - y0, "floor": L.DUN_Z, "ceil": L.DUN_CEIL})
    sx, sy = L.dun_spawn("R1")
    mk("DUNGEON_Spawn", (sx, sy, L.DUN_Z + 0.2), (0, 0, yaw_to(1, 0)), 2.0, "ARROWS")
    ex, ey = L.dun_exit_r3()
    mk("DUNGEON_ExitPortal", (ex, ey, L.DUN_Z), (0, 0, yaw_to(-1, 0)), 3.0, "ARROWS",
       props={"note": "portal de saida da R3 (a qualquer momento: sai com o que ja ganhou)"})
    # ov09b (masmorra infinita): spawn de cada ARENA (teleporte curto entre as salas), vaos de ligacao (o R2R3 e o
    # que o jogo sela durante a sala) e o portal de chegada da R1 como SEGUNDA saida (alcancavel com a R2 ativa)
    for nm in ("R2", "R3"):
        sx, sy = L.dun_spawn(nm)
        mk("DUN_SPAWN_%s" % nm, (sx, sy, L.DUN_Z + 0.2), (0, 0, yaw_to(1, 0)), 2.0, "ARROWS",
           props={"note": "spawn do grupo ao entrar nesta sala (espalhar em volta; sem minerio a menos de %.0f)"
                  % L.DUN_SPAWN_CLEAR})
    for nm, lx, ly in L.dun_links():
        mk("DUN_LINK_%s" % nm, (lx, ly, L.DUN_Z), (0, 0, yaw_to(1, 0)), 2.0, "CUBE",
           props={"w": L.DUN_LINK_W, "h": L.DUN_LINK_H, "t": L.DUN_WALL,
                  "note": "vao de ligacao (largura w ao longo de y, altura h); R2R3 = selo da masmorra infinita"})
    x0, y0, x1, y1 = rooms["R1"]
    mk("DUN_EXIT_R1", (x0 + 2.0, L.DUN_LY, L.DUN_Z), (0, 0, yaw_to(1, 0)), 3.0, "ARROWS",
       props={"note": "portal de chegada da R1 = saida alternativa (prompt 'Sair'), sempre alcancavel"})
    for room, kind, i, x, y, r in L.dun_ore_points():
        mk("DUN_ORE_%s_%s_%02d" % (room, kind, i), (x, y, L.DUN_Z), size=r, kind="SPHERE",
           props={"rarity": kind, "radius": r, "room": room})


def audio_markers():
    """pontos de audio (o AudioWorld/Som.RegisterEmitter usa familia + alcance): agua, fogo, energia, vento"""
    cx, cy = L.PLAZA_C
    pts = [("AUDIO_Fountain", (cx, cy, L.P1 + 2.0), "water", 40.0), ("AUDIO_HallAmbience", (0.0, 88.0, L.HALL + 6.0), "wind", 60.0),
           ("AUDIO_Summon", (L.SUMMON_TOWER[0], L.SUMMON_TOWER[1], L.SUM + 6.0), "energy", 36.0),
           ("AUDIO_Craft", (L.CRAFT_C[0], L.CRAFT_C[1], L.P2 + 3.0), "fire", 26.0),
           ("AUDIO_DungeonPortal", (L.DUNGEON_PORTAL[0], L.DUNGEON_PORTAL[1], L.P3 + 6.0), "energy", 34.0),
           ("AUDIO_DungeonRooms", (-4.0, L.DUN_LY, L.DUN_Z + 8.0), "wind", 92.0)]
    for i, (x, y, z, deg) in enumerate(L.WATERFALLS):
        pts.append(("AUDIO_Waterfall_%d" % (i + 1), (x, y, z - 10.0), "water", 60.0))
    for nm, p, fam, rng in pts:
        mk(nm, p, (0, 0, 0), 2.0, "SPHERE", props={"family": fam, "range": rng})


# ACABAMENTO 2 / AGUA NO ROBLOX (2026-09-30, pedido do usuario): a agua das 4 quedas e da fonte da praca e feita NO
# ROBLOX (Terrain Water / partes com textura e particulas) a partir destes marcadores; a malha d'agua saiu do export.
# QUEDAS: tabela MEDIDA pelo sg_water (bica de pedra + cortina por raio na rocha; na build ele confere, corrige e
# acrescenta src_pos/waypoints/widths/jump). Ordem de L.WATERFALLS: O, L, N, S.
#   (labio = borda da bica no nivel da pedra, largura da calha, saliencia de cima | None, degrau de basalto, pe)
FALL_FX = [
    ((-126.00, -52.00, 42.98), 5.4, None, (-129.23, -52.00, 20.00), (-130.48, -52.00, -53.00)),
    ((151.80, -112.00, 34.98), 5.4, None, (154.68, -112.00, 20.00), (156.45, -112.00, -53.00)),
    ((-52.68, 193.88, 50.98), 5.4, None, (-53.71, 196.71, 20.00), (-54.18, 197.98, -53.00)),
    ((-28.60, -190.95, 29.90), 3.8, None, (-30.82, -191.76, 20.00), (-31.96, -192.17, -53.00)),
]


def fx_markers():
    for i, (x, y, z, deg) in enumerate(L.WATERFALLS):
        a = math.radians(deg)
        yaw = yaw_to(math.cos(a), math.sin(a))          # frente local +Y = para fora da rocha (fwd_x/fwd_z no export)
        lip, w, up, step, base = FALL_FX[i]
        n = i + 1
        mk("FX_Fall_%d_Lip" % n, lip, (0, 0, yaw), 3.0, "SINGLE_ARROW",
           props={"fx": "nevoa_borda", "width": w, "note": "borda da bica de pedra (nivel da pedra); agua do Roblox"})
        if up is not None:
            mk("FX_Fall_%d_Step_Upper" % n, up, (0, 0, yaw), 2.0, "SPHERE", props={"fx": "espuma_degrau"})
        mk("FX_Fall_%d_Step" % n, step, (0, 0, yaw), 2.0, "SPHERE", props={"fx": "espuma_degrau"})
        mk("FX_Fall_%d_Base" % n, base, (0, 0, yaw), 6.0, "SPHERE", props={"fx": "nevoa_base"})


# FONTE DA PRACA (sg_village.plaza desenha a pedra com ESTAS cotas, relativas ao P1). Nivel = lamina d'agua; floor =
# fundo de pedra (estanque: sempre abaixo do nivel); radius = raio interno no nivel (vertice do poligono); hole_r =
# raio do que atravessa a agua (fuste / plinto da estatua).
FOUNTAIN_BASIN = dict(level=2.05, floor=1.55, radius=6.05, apothem=5.84, sides=12, vertex_deg=0.0, hole_r=1.60)
FOUNTAIN_BOWLS = [dict(level=6.24, floor=5.95, radius=2.90, sides=16, vertex_deg=11.25, hole_r=0.62),   # taca de baixo
                  dict(level=9.00, floor=8.80, radius=1.50, sides=16, vertex_deg=11.25, hole_r=1.17)]   # taca de cima
# bicas de pedra na borda das tacas: (taca de origem 1|2, angulo graus, raio da ponta, raio onde o jato cai, destino)
FOUNTAIN_SPOUTS = [(2, 0.0, 2.05, 2.45, "Bowl_1"), (2, 90.0, 2.05, 2.45, "Bowl_1"), (2, 180.0, 2.05, 2.45, "Bowl_1"),
                   (2, 270.0, 2.05, 2.45, "Bowl_1"), (1, 45.0, 3.60, 4.35, "Basin"), (1, 135.0, 3.60, 4.35, "Basin"),
                   (1, 225.0, 3.60, 4.35, "Basin"), (1, 315.0, 3.60, 4.35, "Basin")]


def fountain_markers():
    cx, cy = L.PLAZA_C
    z = L.P1
    B = FOUNTAIN_BASIN
    va = math.radians(B["vertex_deg"])
    mk("WATER_Fountain_Basin", (cx, cy, z + B["level"]), (0, 0, yaw_to(math.cos(va), math.sin(va))), 6.0, "CIRCLE",
       props={"radius": B["radius"], "apothem": B["apothem"], "sides": B["sides"], "depth": round(B["level"] - B["floor"], 2),
              "hole_r": B["hole_r"], "note": "bacia dodecagonal; fwd aponta para um vertice; agua do Roblox"})
    lv = {"Basin": B["level"]}
    for k, b in enumerate(FOUNTAIN_BOWLS):
        va = math.radians(b["vertex_deg"])
        lv["Bowl_%d" % (k + 1)] = b["level"]
        mk("WATER_Fountain_Bowl_%d" % (k + 1), (cx, cy, z + b["level"]), (0, 0, yaw_to(math.cos(va), math.sin(va))),
           b["radius"], "CIRCLE", props={"radius": b["radius"], "sides": b["sides"],
                                         "depth": round(b["level"] - b["floor"], 2), "hole_r": b["hole_r"]})
    for n, (bowl, deg, r0, r1, dst) in enumerate(FOUNTAIN_SPOUTS):
        a = math.radians(deg)
        ux, uy = math.cos(a), math.sin(a)
        z0 = z + FOUNTAIN_BOWLS[bowl - 1]["level"]
        z1 = z + lv[dst]
        mk("WATER_Fountain_Spout_%d" % (n + 1), (cx + ux * r0, cy + uy * r0, z0), (0, 0, yaw_to(ux, uy)), 0.6,
           "SINGLE_ARROW", props={"from": "Bowl_%d" % bowl, "to": dst, "drop": round(z0 - z1, 2),
                                  "land_pos": (round(cx + ux * r1, 3), round(cy + uy * r1, 3), round(z1, 3)),
                                  "note": "ponta da bica no nivel da agua; fwd = direcao do jato"})


def ds_gate():
    """portao APROVADO da galeria (il_gate_ds), sem redesenho, no eixo da ilhota; area_id = 4 (troca 3<->4)"""
    import il_gate_ds
    import bpy
    g = L.gate_ds_pos()
    il_gate_ds.build_gate(g[0], g[1], L.EXIT_Z, L.gate_yaw())
    for o in bpy.data.objects:
        if o.name.startswith("GATE_DemonSlayer") and "area_id" in o.keys():
            o["area_id"] = L.NEXT_AREA_ID
    for o in [o for o in bpy.data.objects if o.type == "CAMERA" and o.name.startswith(("CAM_Gate_", "CAM_Gates_"))]:
        bpy.data.objects.remove(o, do_unlink=True)
    for o in [o for o in bpy.data.objects if o.name.startswith("SCALE_Gate")]:
        o.hide_render = True


def build():
    sg_col.terrain_col()
    world_markers()
    ore_markers()
    spawn_blocks()
    summon_markers()
    craft_markers()
    dungeon_markers()
    audio_markers()
    fx_markers()
    fountain_markers()
    ds_gate()
