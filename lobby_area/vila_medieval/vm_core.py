# vm_core - MARCADORES DE CONTRATO (LOBBY_FORJA.GAMEPLAY_MARKERS), volumes de QA (00_REFERENCE, nunca exportados) e
# proxies SO de previa (golem do Ignis, quadros do GlobalTop100, praca de chegada da Ilha 1). Coordenadas ROBLOX.
# Os marcadores PORTAL_<tema> nascem nos modulos dos portais aprovados (vm_portals) e o montar gera deles o
# Santuario.Portal1..6 (Disco + AreaId).
import math, random
import vm_lib as VL
from vm_lib import mk, qa_box, B
import vm_layout as L
from fm_lib import MB


def markers():
    sx, sz = L.SPAWN
    mk("SPAWN_Lobby", sx, sz, L.Y_SPAWN, 0, -1, {"kind": "spawn", "note": "terraco do spawn, olhando a forja (-Z)"})
    mk("SPAWNLOBBY_Part", *L.SPAWN_LOBBY_PART[::2], L.SPAWN_LOBBY_PART[1], 0, -1,
       {"alvo": "workspace['Mystical Spawn Point'].SpawnLobby (Position da placa 10x0,2x10)"})
    for k, (x, y, z) in L.LOBBY_LAYOUT.items():
        f = {"Spawn": (0, -1), "Shop": (1, 0), "ShopFacing": (-1, 0), "Ignis": (0, -1), "PortalIsland": (-1, 0)}[k]
        mk("LAYOUT_" + k, x, z, y, f[0], f[1], {"lobbylayout": k, "nota": "posicao de HRP do Core.LobbyLayout"})
    # correio (workspace.MailBox, prompt 'Enviar Feedback'): no terraco, de frente para quem nasce
    mx, mz = L.MAILBOX
    mk("MAILBOX_Correio", mx, mz, L.Y_SPAWN, 1, 0, {"alvo": "workspace.MailBox", "prompt": "Enviar Feedback"})
    # IGNIS (contrato do golem novo da sessao Ignis 3D - posicao EXATA)
    rx, ry, rz = L.IGNIS_ROOT
    mk("NPC_Ignis", rx, rz, ry, 0, 1, {"npc": "Ignis", "alvo": "workspace.NPCs.Ignis (Root)",
                                        "nota": "Root (-0,9; 7; -60,7) olhando +Z; bigorna a +5 em Z"})
    mk("INTERACT_Ignis", rx, rz + 0.5, L.IGNIS_BELLY_Y, 0, 1, {"prompt_range": 18, "server_range": 22,
                                                             "alvo": "belly (prompt do Main)"})
    mk("PLAYER_INTERACT_Ignis", -0.9, -44.0, L.Y_NORTH, 0, -1,
       {"note": "chao livre e plano na cota 7 de z -52,7 a -40 (envoltoria do golem)"})
    mk("IGNIS_Anvil", *L.IGNIS_ANVIL[::2], L.IGNIS_ANVIL[1], 0, 1, {"nota": "bigorna do golem (colisao da sessao Ignis)"})
    mk("LETREIRO_Ignis", rx, rz, L.LETREIRO_Y, 0, 1, {"alvo": "LetreiroIgnis"})
    # LOJA (npc vendedor ' ' + LojaPrompt do Main; PadLoja so marca)
    nx, nz = L.SHOP_NPC
    px, pz = L.SHOP_PLAYER
    mk("NPC_Shop", nx, nz, L.Y_SHOP, -1, 0, {"npc": "npc vendedor ", "prompt": "LojaPrompt (Comprar, 12/18)"})
    mk("INTERACT_Shop", nx, nz, L.Y_SHOP + 3.2, -1, 0, {"prompt_range": 12})
    mk("PLAYER_INTERACT_Shop", px, pz, L.Y_SHOP, 1, 0, {})
    mk("PADLOJA_Shop", px, pz, L.Y_SHOP + 0.05, 1, 0, {"alvo": "workspace.LojaMochilas.PadLoja (10x0,2x10, so marca)"})
    dx, dz = L.SHOP_DOOR
    mk("DOOR_Shop", dx, dz, L.Y_SHOP, -1, 0, {"largura": 6, "altura": 9})
    # RANKING: origem do GlobalTop100 (GroundPivot; +Z local = visitantes)
    ox, oz = L.RANK_O
    fx, fz = L.RANK_FACE
    mk("TOP100_Origin", ox, oz, L.Y_RANK, fx, fz, {"alvo": "LOBBY_FORJA.GlobalTop100 (OriginCF)",
                                                   "nota": "quadros em z 0 e podios em z 9,5 do referencial local"})
    # SAIDA para a Ilha 1
    gx, gz = L.GATE
    mk("LOBBY_GATE_Ilha1", gx, gz, L.Y_PAVE, 0, 1, {"nota": "portao da ponte da Ilha 1 (Vila da Folha)"})
    lx, ly, lz = L.ISLE_LINK
    mk("ISLE_LINK_Area1", lx, lz, ly, 0, 1, {"nota": "fim da ponte = borda da praca de chegada da Area 1 (z 222, piso 6)"})
    # forja: AudioWorld acha 'ForgeChimney' pelo nome; pontos de VFX (V3)
    cx, cz = L.CHIMNEY
    mk("ForgeChimney", cx, cz, L.CHIMNEY_TOP, 0, 1, {"nota": "AudioWorld: ambiente da chamine"})
    mk("VFX_Chimney_Smoke_Emitter", cx, cz, L.CHIMNEY_TOP + 0.5, 0, 1, {"particle": "smoke", "rate": 6})
    mk("VFX_Hearth_Fire", -0.9, -74.0, L.Y_NORTH + 2.5, 0, 1, {"particle": "fire"})
    wx, wy, wz = L.WHEEL
    mk("VFX_Waterwheel_Rotate", wx, wz, wy, 0, 1, {"axis": "X", "rpm": 6, "raio": L.WHEEL_R})
    mk("VFX_TripHammer", 24.0, -70.0, L.Y_NORTH + 1.0, 1, 0, {"anim": "martelo-pilao movido pela roda (V3)"})
    mk("REBIRTH_Spot", -26.0, 74.0, L.Y_PAVE, 1, -1, {"alvo": "workspace.Rebirth (sugestao: canto sudoeste da praca)"})


def safe_candidates():
    """pontos seguros da rede de quedas (export_roblox.SAFE_CANDIDATES): [(nome, (x, y) Blender, cota)]"""
    pts = [("SAFE_Spawn", (0, 98), L.Y_SPAWN), ("SAFE_Praca", (0, 66), L.Y_PAVE), ("SAFE_PracaOeste", (-26, 50), L.Y_PAVE),
           ("SAFE_RuaSul", (0, 8), L.Y_PAVE), ("SAFE_RuaNorte", (0, -28), L.Y_NORTH), ("SAFE_Largo", (0, -42), L.Y_NORTH),
           ("SAFE_Loja", (48, 43), L.Y_PAVE), ("SAFE_Ranking", (-60, 46), L.Y_PAVE), ("SAFE_RuaOeste", (-84, 64), L.Y_PAVE),
           ("SAFE_Patio", (-118, 72), L.Y_PAVE), ("SAFE_RuaSE", (48, 108), L.Y_PAVE), ("SAFE_Portao", (50, 140), L.Y_PAVE),
           ("SAFE_Ponte1", (45, 177), L.Y_ISLE), ("SAFE_Ponte2", (17, 202), L.Y_ISLE)]
    for i in range(6):
        (x, z), (fx, fz) = L.portal_pos(i)
        pts.append(("SAFE_Portal%d" % (i + 1), (x + fx * 9.0, z + fz * 9.0), L.Y_PORTAL))
    return [(n, (x, -z), y) for n, (x, z), y in pts]


def qa_volumes():
    lo, hi = L.IGNIS_ENV
    qa_box("QA_Env_Ignis", lo, hi)
    lo, hi = L.IGNIS_FRONT
    qa_box("QA_Free_IgnisFront", lo, hi)
    # GlobalTop100 (girado): caixa no referencial do ranking
    ox, oz = L.RANK_O
    fx, fz = L.RANK_FACE
    n = math.hypot(fx, fz)
    fx, fz = fx / n, fz / n
    z0, z1 = L.TOP100_DEPTH
    cz = (z0 + z1) / 2
    c = VL.B(ox + fx * cz, oz + fz * cz, L.Y_RANK + L.TOP100_H / 2 + 0.05)
    mb = MB("QA_Env_Top100", "00_REFERENCE", detail="far", floor=-999)
    mb.box((2 * L.TOP100_HALF_W, z1 - z0, L.TOP100_H - 0.1), (0, 0, 0), (0, 0, 0), "QA_Envelope", 0.0)
    ob = mb.finish()
    ob.location = c                                  # caixa GIRADA: malha local + matriz (o vm_qa usa o local)
    ob.rotation_euler = (0, 0, VL.yaw_b(-fz, fx))
    ob.display_type = "WIRE"
    ob.hide_render = True


def previews():
    """SO previa (00_REFERENCE, fora do export): golem do Ignis na envoltoria, quadros/podios do GlobalTop100 (geometria
    que o script do leaderboard cria) e a praca de chegada da Vila da Folha depois da ponte"""
    rng = random.Random(3)
    rx, ry, rz = L.IGNIS_ROOT
    g = MB("PREVIEW_Ignis", "00_REFERENCE", rng, detail="far", floor=-999)
    F = VL.face_frame(rx, rz, ry, 0, 1)
    for (x, y, z, s) in ((0, 0, 4.0, (5.0, 4.0, 8.0)), (0, 0, 11.0, (9.0, 6.0, 7.0)), (0, 0.6, 16.6, (5.0, 4.6, 4.2)),
                         (-6.0, 1.5, 11.5, (3.2, 3.2, 9.0)), (6.0, 1.5, 11.5, (3.2, 3.2, 9.0))):
        g.box(s, F.p(y, -x, z), F.r(), "Stone_VM_Dark", 0.0)
    g.box((3.0, 2.0, 3.6), F.p(5.0, 0, 3.6 / 2 + 0.0), F.r(), "Metal_VM_Iron", 0.0)        # bigorna a +5 em Z
    g.box((1.0, 1.0, 1.0), F.p(5.0, 0, 4.0), F.r(), "Forge_Glow_VM", 0.0)                  # lingote quente
    g.finish()
    t = MB("PREVIEW_Top100", "00_REFERENCE", rng, detail="far", floor=-999)
    ox, oz = L.RANK_O
    fx, fz = L.RANK_FACE
    n = math.hypot(fx, fz)
    fx, fz = fx / n, fz / n
    T = VL.face_frame(ox, oz, L.Y_RANK, -fz, fx)       # +x local = tangente, +y local = para os visitantes
    T = VL.Frame(T.o.x, T.o.y, T.o.z, T.a)
    for side in (-1, 1):
        bx = side * 13.4
        t.box((26.0, 3.4, 1.2), T.p(bx, -(0.0), 0.6), T.r(), "Stone_VM_Trim", 0.0)
        t.box((25.0, 1.6, 25.0), T.p(bx, 0.0, 13.0), T.r(), "Stone_VM_Trim", 0.0)
        t.box((23.6, 0.35, 23.8), T.p(bx, 1.0, 13.0), T.r(), "Window_VM_Dark", 0.0)
        for off, h in ((0.0, 2.4), (-8.0, 1.6), (8.0, 1.0)):
            t.box((6.6, 5.8, h), T.p(bx + off, 9.5, h / 2), T.r(), "Stone_VM_Base", 0.0)
    t.finish()
    # Ilha 1: praca de chegada (so a laje e uns volumes cinza) - le o encaixe da ponte nas vistas de saida
    p = MB("PREVIEW_Island1", "00_REFERENCE", rng, detail="far", floor=-999)
    VL.slab(p, [(-70, 222), (70, 222), (90, 330), (-90, 330)], -30.0, L.Y_ISLE, "PREVIEW_Island1")
    for (x, z, w, d, h) in ((-40, 250, 16, 14, 18), (42, 256, 18, 14, 22), (-8, 300, 30, 20, 34)):
        p.box((w, d, h), VL.B(x, z, L.Y_ISLE + h / 2), (0, 0, 0), "PREVIEW_Island1", 0.0)
    p.finish()


def build():
    markers()
    qa_volumes()
    previews()
