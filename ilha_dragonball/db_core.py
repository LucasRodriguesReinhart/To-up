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
              "guard": "PROVISORIO: DB_Exit_AnchorGuard (visual) + COL_DBAnchorGuard_* e COL_DB_ExitAnchorPylon_* (COL), next_island_guard=True",
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


def spawn_blocks():
    """bloqueios do SpawnMinerio (circulos, em coordenadas da ilha) para o builder do Roblox: rochas da arena, pod
    central, faixas dos acessos (escadas/rampa) e um anel junto ao muro da bacia (folga do minerio ate a parede).
    Marcadores GP_Block_<nn> com atributo radius; o chao GROUND fica fora pela janela de altura da zona."""
    n = 0

    def blk(x, y, r, kind):
        nonlocal n
        n += 1
        mk("GP_Block_%02d" % n, (x, y, L.ARENA), size=r, kind="CIRCLE", props={"radius": round(r, 2), "kind": kind})
    for x, y, r, h in L.ARENA_ROCKS:
        blk(x, y, r + 3.0, "rocha")
    x, y, r = L.CORE_POD
    blk(x, y, r + 4.0, "pod")
    for aa, w, kind in L.ARENA_ACCESS:
        foot, top, d = L.access_frame(aa)
        run = math.hypot(top[0] - foot[0], top[1] - foot[1])
        k = max(2, int(run / 5.0) + 1)
        for i in range(k + 1):
            t = i / k
            blk(foot[0] + (top[0] - foot[0]) * t - d[0] * 0.0, foot[1] + (top[1] - foot[1]) * t, w / 2 + 2.0, "acesso")
    step = 8.0
    per = sum(math.hypot(L.arena_r(a + 1) * math.cos(math.radians(a + 1)) - L.arena_r(a) * math.cos(math.radians(a)),
                         L.arena_r(a + 1) * math.sin(math.radians(a + 1)) - L.arena_r(a) * math.sin(math.radians(a)))
              for a in range(360))
    k = int(per / step)
    for i in range(k):
        a = 360.0 * i / k
        rr = L.arena_r(a) + 2.0
        blk(rr * math.cos(math.radians(a)), rr * math.sin(math.radians(a)), 7.0, "borda")
    return n


def fx_markers():
    """pontos de efeito do jogo (o builder do Roblox cria nevoa/borrifo neles): labio e pe das quedas pela borda e o
    ponto onde a cascata NW cai no poco. Os pes/impacto foram medidos pela zona water (a cortina segue a face real do
    penhasco, raycast nas malhas DB_Ter_*); o labio sai da planta."""
    base = {"FX_Fall_SW": (-96.5, -118.3, -60.0), "FX_Fall_SE": (89.9, -106.4, -60.0)}
    ledge = {"FX_Fall_SW": (-95.2, -115.4, -4.5), "FX_Fall_SE": (88.9, -103.9, -6.0)}   # degrau onde a queda bate
    for nm, (fx, fy), (px, py, _) in (("FX_Fall_SW", L.FALL_SW, L.POOL_SW), ("FX_Fall_SE", L.FALL_SE, L.POOL_SE)):
        a = math.atan2(fy - py, fx - px)
        mk(nm + "_Lip", (fx + math.cos(a) * 3.0, fy + math.sin(a) * 3.0, L.GROUND - 2.0), size=3.0, kind="SPHERE",
           props={"fx": "nevoa_borda"})
        mk(nm + "_Base", base[nm], size=6.0, kind="SPHERE", props={"fx": "nevoa_base"})
        mk(nm + "_Ledge", ledge[nm], size=4.0, kind="SPHERE", props={"fx": "borrifo"})
    mk("FX_Fall_NW_Pool", (-113.0, 105.6, L.HUB - L.WATER_DROP + 0.5), size=4.0, kind="SPHERE", props={"fx": "borrifo"})


def shadow_gate():
    """portao APROVADO da galeria (il_gate_sg), sem redesenho, no eixo da ilhota"""
    import il_gate_sg
    g = L.gate_sg_pos()
    il_gate_sg.build_gate(g[0], g[1], L.EXIT_Z, L.sg_yaw())
    # as cameras do kit de portoes vem nas coordenadas da Ilha 1 (renderizam mar vazio aqui): fora; o portao desta
    # ilha tem CAM_DB_ShadowGate / CAM_DB_PlayerHeight_ShadowGate / CAM_DB_Ref_Gate (db_scene)
    import bpy
    for o in [o for o in bpy.data.objects if o.type == "CAMERA" and o.name.startswith(("CAM_Gate_", "CAM_Gates_"))]:
        bpy.data.objects.remove(o, do_unlink=True)


def build():
    db_col.terrain_col()
    world_markers()
    ore_markers()
    spawn_blocks()
    fx_markers()
    shadow_gate()
