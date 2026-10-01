# sg_core - COMPARTILHADO E CONGELADO (dono: integracao). Roda SEMPRE, com blockout ou com os modulos de detalhe:
#   colisao de tudo que e andavel (sg_col.terrain_col)
#   TODOS os marcadores de gameplay, tirados da planta (os modulos de zona desenham em volta, nunca criam de novo):
#     mundo: WORLD_FROM_PREV (encaixe na Ilha 2), WORLD_ENTRY_ShadowGarden, PATH_ENTRY_CENTER(_nn),
#            ISLAND_EXIT_ShadowGarden, ISLAND_NEXT_ANCHOR_DemonSlayer
#     mineracao (Mining Hall): ORE_<RARIDADE>_<nn>, MiningZone_ShadowGarden, GP_Block_<nn>
#     invocacao: SUMMON_Main, SUMMON_Interact, SUMMON_PlayerPosition
#     craft: CRAFT_Station, PLAYER_INTERACT_Craft, NPC_Craft
#     dungeon (v4: portal no SALAO SOMBRIO): DUNGEON_Hall (= DUNGEON_Portal), DUNGEON_Entrance, DUNGEON_UI,
#              DUNGEON_Return, DUNGEON_Spawn, DUN_ROOM_<R>, DUN_ORE_<R>_<RARIDADE>_<nn>, DUN_SPAWN_<R>, DUN_LINK_<RaRb>,
#              DUN_NEXT_R2/R3 (portal da proxima sala DENTRO do vao/nicho), DUN_EXIT_R1/R3 (+ alias DUNGEON_ExitPortal)
#     trono e escada (v4): THRONE_Rest/Park/Interact/OpenZone/Stair_Top/Stair_Bottom/Return; CAVE_Zone, CAVE_Stair_Up
#     agua do salao sombrio e do patio (v4): WATER_CavePool, WATER_CaveFall_Lip/_Base, WATER_Court_L/R
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
    # v4: a ponte de chegada e CURVA; o WORLD_FROM_PREV fica na ancora com a frente no rumo do 1o trecho da ponte
    (ax, ay), (bx, by) = L.BRIDGE_PATH[0], L.BRIDGE_PATH[1]
    mk("WORLD_FROM_PREV", (L.PREV_X, L.PREV_Y, L.DECK), (0, 0, yaw_to(bx - ax, by - ay)), 4.0, "ARROWS",
       props={"width": L.DECK_W, "deck_z": L.DECK, "prev": "ISLAND_NEXT_ANCHOR_ShadowGarden (Ilha 2 Dragon Ball)",
              "bridge_len": round(L.BRIDGE_LEN, 1),
              "note": "centro da borda do tabuleiro da ponte de chegada (curva de 33 graus, 232); avanco = frente"})
    sx, sy = L.ENTRY_SPAWN
    mk("WORLD_ENTRY_ShadowGarden", (sx, sy, L.P1 + 0.2), (0, 0, 0), 3.0, "ARROWS",
       props={"note": "chegada da ilha (depois do portico B, olhando a praca e o castelo)"})
    gt = L.stair_top("Gate")
    cx, cy = L.PLAZA_C
    path = [(sx, sy, L.P1), (0.0, cy - L.PLAZA_R - 2.0, L.P1), (-14.0, cy - 12.0, L.P1), (-14.0, cy + 12.0, L.P1),
            (0.0, cy + L.PLAZA_R + 2.0, L.P1), (0.0, -130.0, L.P2), (0.0, -46.0, L.P2), (gt[0], gt[1] + 3.0, L.P3),
            (0.0, 40.0, L.P3), (0.0, 70.0, L.HALL), (0.0, 96.0, L.HALL)]
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
    """bloqueios do SpawnMinerio (circulos) para o builder do Roblox: corredor da porta e anel 'borda' em volta da
    MiningZone (v4: a zona e a nave central, nao o salao inteiro; o builder tira o tamanho da zona do min/max dos
    'borda')"""
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
    mx0, my0, mx1, my1 = L.MINE_RECT
    x0, y0, x1, y1 = mx0 - 3.0, my0 - 3.0, mx1 + 3.0, my1 + 3.0
    k = 12
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
    """v4: o portal da masmorra fica no FUNDO SUL do SALAO SOMBRIO (sob o castelo); as salas 3x ficam em fila no eixo
    +Y sob ele. Tudo o que o DungeonService cria (selo/portal da proxima sala, saidas, spawns) usa o CFrame do marcador
    (fwd_x/fwd_z do export): nada alinhado aos eixos do mundo."""
    px, py = L.CAVE_PORTAL
    zd = L.CAVE_DAIS[4]
    north = yaw_to(0, 1)
    for nm in ("DUNGEON_Hall", "DUNGEON_Portal"):
        mk(nm, (px, py + 4.0, zd), (0, 0, north), 3.0, "ARROWS",
           props={"radius": L.CAVE_PORTAL_R, "ring_y_local": py,
                  "note": "portal/vortice da masmorra no fundo sul do salao sombrio (frente = para o norte, quem chega)"
                  + (" [alias de DUNGEON_Hall para as particulas do JardimSombrasIsland]" if nm == "DUNGEON_Portal" else "")})
    mk("DUNGEON_Entrance", (px, py + 12.0, zd), (0, 0, north), 2.0, "SPHERE",
       props={"radius": 8.0, "note": "zona/prompt de entrada na corrida (so com ENTRY_OPEN); <= 14 do marcador"})
    mk("DUNGEON_UI", (px, py - 1.0, zd + 2.0 * L.CAVE_PORTAL_R + 6.0), (0, 0, north), 2.0, "SINGLE_ARROW",
       props={"ui": "BillboardGui/SurfaceGui: estado e contagem da dungeon (XX:00 / XX:30)", "w": 22.0, "h": 6.0})
    mk("DUNGEON_Return", (px, py + 34.0, L.CAVE_FLOOR + 0.2), (0, 0, north), 2.0, "ARROWS",
       props={"note": "para onde o jogador volta ao sair/terminar (salao sombrio, na frente do portal, olhando a escada)"})
    for nm, (x0, y0, x1, y1) in L.DUN_ROOMS:
        mk("DUN_ROOM_%s" % nm, ((x0 + x1) / 2, (y0 + y1) / 2, L.DUN_Z), (0, 0, north), (x1 - x0) / 2, "CUBE",
           props={"sx": x1 - x0, "sy": y1 - y0, "floor": L.DUN_Z, "ceil": L.DUN_CEIL,
                  "note": "frente = eixo da fila de salas (R1 -> R2 -> R3)"})
    sx, sy = L.dun_spawn("R1")
    mk("DUNGEON_Spawn", (sx, sy, L.DUN_Z + 0.2), (0, 0, north), 2.0, "ARROWS",
       props={"note": "chegada na R1 (frente = para a R2)"})
    for nm in ("R2", "R3"):
        sx, sy = L.dun_spawn(nm)
        mk("DUN_SPAWN_%s" % nm, (sx, sy, L.DUN_Z + 0.2), (0, 0, north), 2.0, "ARROWS",
           props={"note": "spawn do grupo ao entrar nesta sala (espalhar em volta; sem minerio a menos de %.0f)"
                  % L.DUN_SPAWN_CLEAR})
    for nm, lx, ly in L.dun_links():
        mk("DUN_LINK_%s" % nm, (lx, ly, L.DUN_Z), (0, 0, north), 2.0, "CUBE",
           props={"w": L.DUN_LINK_W, "h": L.DUN_LINK_H, "t": L.DUN_WALL,
                  "note": "vao de ligacao (largura w perpendicular a frente, altura h); centro no plano medio da parede"})
    for nm in ("R2", "R3"):
        nx, ny = L.dun_next(nm)
        mk("DUN_NEXT_%s" % nm, (nx, ny, L.DUN_Z), (0, 0, north), 2.0, "CUBE",
           props={"w": L.DUN_NEXT_W, "h": L.DUN_NEXT_H, "t": L.DUN_NEXT_T, "room": nm,
                  "note": "portal da PROXIMA sala (e o selo enquanto a sala nao limpa): Part (w, h, t) com "
                          "CFrame = marcador * (0, h/2, 0); DENTRO do plano medio do vao (R2) / nicho (R3)"})
    for nm in ("R1", "R3"):
        ex, ey = L.dun_exit(nm)
        f = (1, 0) if nm == "R3" else (0, 1)
        for mn in (("DUN_EXIT_%s" % nm,) + (("DUNGEON_ExitPortal",) if nm == "R3" else ())):
            mk(mn, (ex, ey, L.DUN_Z), (0, 0, yaw_to(*f)), 3.0, "ARROWS",
               props={"note": "saida por PROMPT ('Sair', hold 0,6); sem barreira de toque"
                      + (" [alias de DUN_EXIT_R3]" if mn == "DUNGEON_ExitPortal" else "")})
    for room, kind, i, x, y, r in L.dun_ore_points():
        mk("DUN_ORE_%s_%s_%02d" % (room, kind, i), (x, y, L.DUN_Z), size=r, kind="SPHERE",
           props={"rarity": kind, "radius": r, "room": room})


def throne_markers():
    """trono que desliza (servidor, TronoService): pivos de repouso/recolhido, prompt, zona de seguranca, patamares da
    escada caracol e o destino do atalho 'Subir'"""
    tx, ty = L.THRONE_REST
    z = L.CHANCEL_Z
    south = yaw_to(0, -1)
    w, d, h = L.THRONE_SIZE
    mk("THRONE_Rest", (tx, ty, z), (0, 0, south), 3.0, "ARROWS",
       props={"sx": w, "sy": d, "sz": h, "note": "pivo do trono em repouso (base no piso do presbiterio; frente = nave)"})
    px, py = L.THRONE_PARK
    mk("THRONE_Park", (px, py, z), (0, 0, south), 3.0, "ARROWS",
       props={"travel": L.THRONE_TRAVEL, "tween_s": 3.0, "note": "pivo do trono recolhido no bolso da parede leste"})
    mk("THRONE_Interact", (tx, ty - d / 2 - 4.5, z), (0, 0, south), 2.0, "SPHERE",
       props={"prompt": "Tocar o trono", "hold": 0.5, "dist": 10.0})
    oy0, oy1 = ty - d / 2 - 2.0, L.SPIRAL_C[1] - L.SPIRAL_R_IN + 4.0
    mk("THRONE_OpenZone", (tx, (oy0 + oy1) / 2, z), (0, 0, 0), 2.0, "CUBE",
       props={"sx": 18.0, "sy": round(oy1 - oy0, 2), "sz": 14.0,
              "note": "caixa (centro na base): nao fecha o trono com jogador dentro"})
    sy_top = L.SPIRAL_C[1] - L.SPIRAL_R_IN + 0.5
    mk("THRONE_Stair_Top", (0.0, sy_top, z), (0, 0, yaw_to(0, 1)), 2.0, "ARROWS",
       props={"prompt": "Abrir passagem", "note": "patamar de topo da escada caracol (dentro do arco secreto)"})
    mk("THRONE_Stair_Bottom", (0.0, L.SPIRAL_C[1] - L.SPIRAL_R_OUT - 2.0, L.SPIRAL_BOT_Z), (0, 0, south), 2.0, "ARROWS",
       props={"note": "saida da escada caracol na galeria do salao sombrio"})
    mk("THRONE_Return", (0.0, L.CHANCEL[1] + 14.0, z), (0, 0, south), 2.0, "ARROWS",
       props={"note": "destino do atalho 'Subir' (prompt em CAVE_Stair_Up), no presbiterio"})
    x0, y0, x1, y1 = L.CAVE
    mk("CAVE_Zone", ((x0 + x1) / 2, (y0 + y1) / 2, L.CAVE_FLOOR), (0, 0, yaw_to(0, 1)), 4.0, "CUBE",
       props={"sx": x1 - x0, "sy": y1 - y0, "h": L.CAVE_TOP - L.CAVE_FLOOR, "floor": L.CAVE_FLOOR,
              "note": "salao sombrio: reverb Cave e corte do SUBSOLO no cliente"})
    mk("CAVE_Stair_Up", (14.0, L.CAVE_PORTAL[1] + 28.0, L.CAVE_FLOOR), (0, 0, yaw_to(0, 1)), 2.0, "SPHERE",
       props={"prompt": "Subir ao salao", "to": "THRONE_Return", "optional": True})


def audio_markers():
    """pontos de audio (o AudioWorld/Som.RegisterEmitter usa familia + alcance): agua, fogo, energia, vento"""
    cx, cy = L.PLAZA_C
    mx0, my0, mx1, my1 = L.MINE_RECT
    pts = [("AUDIO_Fountain", (cx, cy, L.P1 + 2.0), "water", 40.0),
           ("AUDIO_HallAmbience", (0.0, (my0 + my1) / 2, L.HALL + 8.0), "wind", 110.0),
           ("AUDIO_Summon", (L.SUMMON_TOWER[0], L.SUMMON_TOWER[1], L.SUM + 6.0), "energy", 36.0),
           ("AUDIO_Craft", (L.CRAFT_C[0], L.CRAFT_C[1], L.P2 + 3.0), "fire", 26.0),
           ("AUDIO_DungeonPortal", (L.CAVE_PORTAL[0], L.CAVE_PORTAL[1] + 4.0, L.CAVE_FLOOR + 8.0), "energy", 44.0),
           ("AUDIO_DungeonRooms", (L.DUN_LX, 154.0, L.DUN_Z + 10.0), "wind", 160.0),
           ("AUDIO_Cave", (0.0, 212.0, L.CAVE_FLOOR + 14.0), "wind", 140.0),
           ("AUDIO_Forge", ((L.CAVE_FORGE[0] + L.CAVE_FORGE[2]) / 2, (L.CAVE_FORGE[1] + L.CAVE_FORGE[3]) / 2,
                            L.CAVE_FLOOR + 3.0), "fire", 34.0),
           ("AUDIO_CaveWater", (60.0, 208.0, L.CAVE_FLOOR), "water", 70.0)]
    for i, (x, y, z, deg) in enumerate(L.WATERFALLS):
        pts.append(("AUDIO_Waterfall_%d" % (i + 1), (x, y, z - 10.0), "water", 60.0))
    for nm, p, fam, rng in pts:
        mk(nm, p, (0, 0, 0), 2.0, "SPHERE", props={"family": fam, "range": rng})


# ACABAMENTO 2 / AGUA NO ROBLOX (2026-09-30, pedido do usuario): a agua das 4 quedas e da fonte da praca e feita NO
# ROBLOX (Terrain Water / partes com textura e particulas) a partir destes marcadores; a malha d'agua saiu do export.
# QUEDAS: na v3 a tabela era MEDIDA pelo sg_water (bica de pedra + cortina por raio na rocha; na build ele confere,
# corrige e acrescenta src_pos/waypoints/widths/jump). Ordem de L.WATERFALLS: O, L, N, S.
#   (labio = borda da bica no nivel da pedra, largura da calha, saliencia de cima | None, degrau de basalto, pe)
def _fall_fx():
    """v4 (onda 0): labio na borda da planta, degrau de basalto a 20 e pe a -53 (mesma familia de cotas da tabela medida
    da v3). A tabela e ESTIMADA: o sg_water mede na rocha e corrige quando rodar na planta v4 (onda 1)."""
    out = []
    for x, y, z, deg in L.WATERFALLS:
        a = math.radians(deg)
        ux, uy = math.cos(a), math.sin(a)
        w = 3.8 if z < L.P1 else 5.4
        out.append(((x, y, round(z - 0.22, 2)), w, None, (round(x + ux * 3.2, 2), round(y + uy * 3.2, 2), 20.0),
                    (round(x + ux * 4.5, 2), round(y + uy * 4.5, 2), -53.0)))
    return out


FALL_FX = _fall_fx()
# ONDA 2 (o2b, 2026-10-01): tabela MEDIDA pelo sg_water na rocha v4 (sg_terrain onda 1f): labio na borda real da bica
# (bancada +0,8 + bica 1,1 alem do ponto da planta; a sul sai da fenda), degrau no basalto (20) e pe (-53). O sg_water
# ainda confere e acrescenta waypoints/widths/src_pos no build; aqui fica o valor certo para quando ele nao roda.
_FALL_FX_V4 = [((-189.0, -60.0, 42.98), 5.4, None, (-191.8, -60.0, 20.0), (-193.48, -60.0, -53.0)),
               ((175.8, -200.0, 34.98), 5.4, None, (178.67, -200.0, 20.0), (180.45, -200.0, -53.0)),
               ((-60.52, 384.93, 50.98), 5.4, None, (-61.23, 387.59, 20.0), (-61.63, 389.1, -53.0)),
               ((-29.66, -297.04, 29.9), 3.8, None, (-31.75, -297.8, 20.0), (-32.76, -298.17, -53.0))]
if [tuple(w) for w in L.WATERFALLS] == [(-187.0, -60.0, L.P2 - 1.0, 180.0), (174.0, -200.0, L.P1 - 1.0, 0.0),
                                        (-60.0, 383.0, L.P3 - 1.0, 105.0), (-26.8, -296.0, L.DECK + 2.0, 200.0)]:
    FALL_FX = _FALL_FX_V4


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
              "hole_r": B["hole_r"], "shape": "poligono", "level": round(z + B["level"], 3),
              "floor": round(z + B["floor"], 3), "note": "bacia dodecagonal; fwd aponta para um vertice; agua do Roblox"})
    lv = {"Basin": B["level"]}
    for k, b in enumerate(FOUNTAIN_BOWLS):
        va = math.radians(b["vertex_deg"])
        lv["Bowl_%d" % (k + 1)] = b["level"]
        mk("WATER_Fountain_Bowl_%d" % (k + 1), (cx, cy, z + b["level"]), (0, 0, yaw_to(math.cos(va), math.sin(va))),
           b["radius"], "CIRCLE", props={"radius": b["radius"], "sides": b["sides"],
                                         "depth": round(b["level"] - b["floor"], 2), "hole_r": b["hole_r"],
                                         "shape": "poligono", "level": round(z + b["level"], 3),
                                         "floor": round(z + b["floor"], 3)})
    for n, (bowl, deg, r0, r1, dst) in enumerate(FOUNTAIN_SPOUTS):
        a = math.radians(deg)
        ux, uy = math.cos(a), math.sin(a)
        z0 = z + FOUNTAIN_BOWLS[bowl - 1]["level"]
        z1 = z + lv[dst]
        mk("WATER_Fountain_Spout_%d" % (n + 1), (cx + ux * r0, cy + uy * r0, z0), (0, 0, yaw_to(ux, uy)), 0.6,
           "SINGLE_ARROW", props={"from": "Bowl_%d" % bowl, "to": dst, "drop": round(z0 - z1, 2),
                                  "land_pos": (round(cx + ux * r1, 3), round(cy + uy * r1, 3), round(z1, 3)),
                                  "note": "ponta da bica no nivel da agua; fwd = direcao do jato"})


def water_markers_v4():
    """agua nova da v4 (feita no Roblox): rio escuro do salao sombrio, queda da fenda NE da caverna e os 2 espelhos
    d'agua do patio-jardim (o Blender so faz a pedra estanque)"""
    # ONDA 2 (o2b): valores MEDIDOS pelo sg_water na pedra do sg_cave / sg_court (ele confere de novo no build). Todos
    # no idioma da fonte: centro no NIVEL da lamina, sx = X local, sy = Y local (= fwd, aqui +Y), level/floor/depth.
    x0, y0, x1, y1, lev, bot = L.CAVE_POOL
    mk("WATER_CavePool", ((x0 + x1) / 2, (y0 + y1) / 2, lev), (0, 0, yaw_to(0, 1)), 4.0, "CUBE",
       props={"shape": "retangulo", "sx": round(x1 - x0 - 1.8, 2), "sy": round(y1 - y0 - 1.8, 2), "level": lev,
              "floor": bot, "depth": round(lev - bot, 2), "bridge_x0": -10.4, "bridge_x1": 10.4,
              "note": "rio escuro (lamina parada, quase preta) entre os meios-fios; o corpo da ponte do eixo corta a "
                      "lamina em x bridge_x0..bridge_x1 (local)"})
    lip = (72.0, 220.9, L.CAVE_TOP - 6.0)
    mk("WATER_CaveFall_Lip", lip, (0, 0, yaw_to(0, -1)), 2.0, "SINGLE_ARROW",
       props={"width": 2.8, "drop": round(lip[2] - lev, 2), "to": "WATER_CavePool", "kind": "fenda",
              "note": "queda da fenda NE da caverna: borda da bica no nivel da pedra"})
    mk("WATER_CaveFall_Base", (72.0, 217.64, lev), (0, 0, yaw_to(0, -1)), 3.0, "SPHERE",
       props={"fx": "nevoa_base", "level": lev})
    # espelhos do patio-jardim (sg_court, onda 2): bacias de 32 x 20 centradas em (+-58, 42)
    for nm, cx in (("L", -58.0), ("R", 58.0)):
        mk("WATER_Court_%s" % nm, (cx, 42.0, L.P3 + 0.6), (0, 0, yaw_to(0, 1)), 3.0, "CUBE",
           props={"shape": "retangulo", "sx": 32.0, "sy": 20.0, "level": L.P3 + 0.6, "floor": L.P3 + 0.1,
                  "depth": 0.5, "note": "espelho d'agua do patio-jardim (reflete a fachada); capa a P3+0,66"})


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
    throne_markers()
    audio_markers()
    fx_markers()
    fountain_markers()
    water_markers_v4()
    ds_gate()
