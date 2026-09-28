# sg_core - COMPARTILHADO E CONGELADO (dono: integracao). Roda SEMPRE, com blockout ou com os modulos de detalhe:
#   colisao de tudo que e andavel (sg_col.terrain_col)
#   TODOS os marcadores de gameplay, tirados da planta (os modulos de zona desenham em volta, nunca criam de novo):
#     mundo: WORLD_FROM_PREV (encaixe na Ilha 2), WORLD_ENTRY_ShadowGarden, PATH_ENTRY_CENTER(_nn),
#            ISLAND_EXIT_ShadowGarden, ISLAND_NEXT_ANCHOR_DemonSlayer
#     mineracao (Mining Hall): ORE_<RARIDADE>_<nn>, MiningZone_ShadowGarden, GP_Block_<nn>
#     invocacao: SUMMON_Main, SUMMON_Interact, SUMMON_PlayerPosition
#     craft: CRAFT_Station, PLAYER_INTERACT_Craft, NPC_Craft
#     dungeon: DUNGEON_Entrance, DUNGEON_Portal, DUNGEON_UI, DUNGEON_Return, DUNGEON_Spawn, DUNGEON_ExitPortal,
#              DUN_ROOM_<R>, DUN_ORE_<R>_<RARIDADE>_<nn>
#     audio: AUDIO_<Coisa> (familia + alcance); efeitos: FX_Fall_<n>_Lip/_Base
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
    mk("DUNGEON_UI", (cx, cy - d / 2 - 1.5, L.P3 + L.DUNGEON_DOOR_H + 3.0), (0, 0, yaw_to(0, -1)), 2.0, "SINGLE_ARROW",
       props={"ui": "BillboardGui: estado e contagem da dungeon (XX:00 / XX:30)"})
    mk("DUNGEON_Return", (cx, cy - d / 2 - 8.0, L.P3 + 0.2), (0, 0, yaw_to(0, -1)), 2.0, "ARROWS",
       props={"note": "para onde o jogador volta ao sair/terminar (patio, em frente a porta)"})
    rooms = dict(L.DUN_ROOMS)
    for nm, (x0, y0, x1, y1) in L.DUN_ROOMS:
        mk("DUN_ROOM_%s" % nm, ((x0 + x1) / 2, (y0 + y1) / 2, L.DUN_Z), (0, 0, 0), (x1 - x0) / 2, "CUBE",
           props={"sx": x1 - x0, "sy": y1 - y0, "floor": L.DUN_Z, "ceil": L.DUN_CEIL})
    x0, y0, x1, y1 = rooms["R1"]
    mk("DUNGEON_Spawn", (x0 + 8.0, (y0 + y1) / 2, L.DUN_Z + 0.2), (0, 0, yaw_to(1, 0)), 2.0, "ARROWS")
    x0, y0, x1, y1 = rooms["R3"]
    mk("DUNGEON_ExitPortal", (x1 - 4.0, (y0 + y1) / 2, L.DUN_Z), (0, 0, yaw_to(-1, 0)), 3.0, "ARROWS",
       props={"note": "portal de volta (aparece em FINISHING/FINISHED)"})
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
           ("AUDIO_DungeonRooms", (0.0, 80.0, L.DUN_Z + 6.0), "wind", 70.0)]
    for i, (x, y, z, deg) in enumerate(L.WATERFALLS):
        pts.append(("AUDIO_Waterfall_%d" % (i + 1), (x, y, z - 10.0), "water", 60.0))
    for nm, p, fam, rng in pts:
        mk(nm, p, (0, 0, 0), 2.0, "SPHERE", props={"family": fam, "range": rng})


# pe REAL de cada cortina (medido pelo sg_water por raio na face do penhasco; ordem de L.WATERFALLS: O, L, N, S)
FALL_FEET = [(-130.1, -52.0, -60.0), (161.7, -112.0, -60.0), (-58.1, 208.7, -60.0), (-30.9, -191.8, -60.0)]


def fx_markers():
    for i, (x, y, z, deg) in enumerate(L.WATERFALLS):
        a = math.radians(deg)
        mk("FX_Fall_%d_Lip" % (i + 1), (x + math.cos(a) * 2.0, y + math.sin(a) * 2.0, z - 1.0), size=3.0, kind="SPHERE",
           props={"fx": "nevoa_borda"})
        mk("FX_Fall_%d_Base" % (i + 1), FALL_FEET[i], size=6.0, kind="SPHERE", props={"fx": "nevoa_base"})


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
    ds_gate()
