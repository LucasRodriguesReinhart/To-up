# il_core - COMPARTILHADO E CONGELADO (dono: integracao). Roda SEMPRE, com blockout ou com os modulos de detalhe:
#   colisao do chao da ilha inteira + parede invisivel da borda (il_col.terrain_col)
#   marcadores de mundo: WORLD_FROM_LOBBY, WORLD_ENTRY_Naruto, PATH_ENTRY_CENTER(_nn)
#   minerio: ORE_<RARIDADE>_<nn> (pontos de il_layout.ore_points) + GP_Zone_Pit (zona do SpawnMinerio)
import math
import il_lib as IL
from il_lib import mk
import il_layout as L
import il_col


def world_markers():
    mk("WORLD_FROM_LOBBY", (0.0, L.LOBBY_Y, L.G), (0, 0, 0), 4.0, "ARROWS",
       props={"width": L.BRIDGE_W, "deck_z": L.G, "note": "ponta do patamar da ponte do lobby (Roblox z 222)"})
    mk("WORLD_ENTRY_Naruto", (0.0, -100.0, L.G + 0.2), (0, 0, 0), 3.0, "ARROWS",
       props={"note": "chegada da ilha (logo depois do portao, olhando o fosso)"})
    path = [(0.0, -100.0, L.G), (0.0, -86.0, L.RING), (0.0, -64.0, L.RING), (0.0, -44.0, L.PIT),
            (0.0, -18.0, L.PIT)]
    for i, p in enumerate(path):
        mk("PATH_ENTRY_CENTER_%02d" % i, p, (0, 0, 0), 1.5, "SPHERE")
    mk("PATH_ENTRY_CENTER", path[-2], (0, 0, 0), 3.0, "ARROWS",
       props={"waypoints": ";".join("%.1f,%.1f,%.1f" % p for p in path)})


def ore_markers():
    for kind, i, x, y, r in L.ore_points():
        mk("ORE_%s_%02d" % (kind, i), (x, y, L.PIT), size=r, kind="SPHERE", props={"rarity": kind, "radius": r})
    mk("GP_Zone_Pit", (0, 0, L.PIT), size=L.PIT_R - 4.0, kind="CIRCLE",
       props={"radius": L.PIT_R - 4.0, "floor": L.PIT, "kind": "mining"})


def build():
    il_col.terrain_col()
    world_markers()
    ore_markers()
