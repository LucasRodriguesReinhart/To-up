# db_core - COMPARTILHADO E CONGELADO (dono: integracao). Roda SEMPRE, com blockout ou com os modulos de detalhe:
#   colisao de tudo que e andavel (db_col.terrain_col)
#   marcadores de mundo: WORLD_FROM_PREV (encaixe na Ilha 1), WORLD_ENTRY_DragonBall, PATH_ENTRY_CENTER(_nn),
#   ISLAND_EXIT_DragonBall, ISLAND_NEXT_ANCHOR_ShadowGarden
#   minerio: ORE_<RARIDADE>_<nn> (pontos de db_layout.ore_points) + MiningZone_DragonBall (zona do SpawnMinerio)
#   portao de compra SHADOW GARDEN: o asset APROVADO (ilha_naruto/il_gate_sg.build_gate), sem redesenho, no eixo da
#   ilhota da saida. A geografia em volta (ponte, ilhota, transicao) e da zona exit.
import math
import db_lib as DL
from db_lib import mk, yaw_to
import db_layout as L
import db_col


def world_markers():
    mk("WORLD_FROM_PREV", (0.0, L.PREV_Y, L.DECK), (0, 0, 0), 4.0, "ARROWS",
       props={"width": L.DECK_W, "deck_z": L.DECK, "prev": "ISLAND_NEXT_ANCHOR (Ilha 1 Naruto)",
              "note": "centro da borda do tabuleiro da ponte de chegada; avanco +Y (para dentro da ilha)"})
    sx, sy = L.ENTRY_SPAWN
    mk("WORLD_ENTRY_DragonBall", (sx, sy, L.GROUND + 0.2), (0, 0, 0), 3.0, "ARROWS",
       props={"note": "chegada da ilha (depois do portal de entrada, olhando a arena)"})
    foot, top, d = L.access_frame(270.0)
    path = [(sx, sy, L.GROUND), (0.0, -74.0, L.GROUND), (top[0], top[1] - 2.0, L.GROUND),
            (foot[0], foot[1] - 1.0, L.ARENA), (0.0, -30.0, L.ARENA), (0.0, -12.0, L.ARENA)]
    for i, p in enumerate(path):
        mk("PATH_ENTRY_CENTER_%02d" % i, p, (0, 0, 0), 1.5, "SPHERE")
    mk("PATH_ENTRY_CENTER", path[-2], (0, 0, 0), 3.0, "ARROWS",
       props={"waypoints": ";".join("%.1f,%.1f,%.1f" % p for p in path)})
    ux, uy = L.exit_dir()
    yaw = yaw_to(ux, uy)
    mk("ISLAND_EXIT_DragonBall", (L.EXIT_START[0], L.EXIT_START[1], L.EXIT_Z), (0, 0, yaw), 4.0, "ARROWS",
       props={"width": L.EXIT_W, "deck_z": L.EXIT_Z, "heading_deg": L.EXIT_DEG})
    ap = L.anchor_pos()
    mk("ISLAND_NEXT_ANCHOR_ShadowGarden", (ap[0], ap[1], L.EXIT_Z), (0, 0, yaw), 4.0, "ARROWS",
       props={"width": L.DECK_W, "deck_z": L.EXIT_Z, "clear_h": 22.0, "heading_deg": L.EXIT_DEG, "next_area": 4,
              "next_key": "ShadowGarden",
              "guard": "PROVISORIO: DB_Exit_AnchorGuard (visual) + COL_DBAnchorGuard_* (COL), next_island_guard=True",
              "guard_note": "a integracao da Ilha 3 REMOVE o guarda quando a ponte seguinte encosta aqui"})


def ore_markers():
    for kind, i, x, y, r in L.ore_points():
        mk("ORE_%s_%02d" % (kind, i), (x, y, L.ARENA), size=r, kind="SPHERE", props={"rarity": kind, "radius": r})
    # zona do SpawnMinerio: a arena ovalada (raio medio + semi-eixos), piso ARENA
    rx = max(L.arena_r(0.0), L.arena_r(180.0))
    ry = max(L.arena_r(90.0), L.arena_r(270.0))
    mk("MiningZone_DragonBall", (0.0, 0.0, L.ARENA), size=(rx + ry) / 2, kind="CIRCLE",
       props={"kind": "mining", "floor": L.ARENA, "rx": round(rx, 2), "ry": round(ry, 2),
              "rim_clear": L.ORE_RIM_CLEAR, "note": "arena oval; o jogo usa os ORE_* + zona retangular com bloqueios"})


def shadow_gate():
    """portao APROVADO da galeria (il_gate_sg), sem redesenho, no eixo da ilhota"""
    import il_gate_sg
    g = L.gate_sg_pos()
    il_gate_sg.build_gate(g[0], g[1], L.EXIT_Z, L.sg_yaw())


def build():
    db_col.terrain_col()
    world_markers()
    ore_markers()
    shadow_gate()
