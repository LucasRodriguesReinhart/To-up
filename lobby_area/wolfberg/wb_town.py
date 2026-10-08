# wb_town.py - a VILA: casas da planta, mobiliario da praca (fonte, barracas, carroca, barris, caixotes, postes, cerca,
# placa de boas-vindas, poste de setas, correio), poco, luzes. Tudo pela planta (wb_layout) e pelo kit (wb_kit).
import math
import random

import fm_lib
import wb_lib as W
import wb_layout as L
from wb_kit import (Fr, bb, bx, lantern_post, fence, welcome_sign, signpost, barrel, crate, sack, cart, stall, fountain,
                    well, banner, house, text, STD, ST, TB, PK, IR, TXT)
from wb_lib import RB


def houses(ids=None, coll="03_TOWN"):
    out = []
    for spec in L.HOUSES:
        if ids and spec["id"] not in ids:
            continue
        b, zr = house(spec, coll)
        out += b.objects
    return out


def plaza_furniture(coll="03_TOWN"):
    """fonte, barracas, carroca, barris/caixotes encostados, postes, cerca + placa, setas, correio"""
    r = random.Random(7)
    b = W.Build("WB_Town_Plaza", coll)
    Y = L.Y_PAVE
    # fonte
    fountain(b, Fr(RB(L.FOUNTAIN[0], L.FOUNTAIN[1], Y), (0, 1)), L.FOUNTAIN_R)
    # barracas
    goods = ["bread", "fruit", "cloth"]
    for i, (x, z, (fx, fz), canvas) in enumerate(L.STALLS):
        stall(b, Fr.rbx(x, z, Y, fx, fz), canvas, goods[i % 3], seed=i)
        fm_lib.col_box("Town", (9.0, 6.0, 3.4), RB(x, z, Y + 1.7), (0, 0, Fr.rbx(x, z, Y, fx, fz).yaw()))
    # carroca
    cx, cz, (fx, fz) = L.CART
    cart(b, Fr.rbx(cx, cz, Y, fx, fz), 0, 0)
    fm_lib.col_box("Town", (7.0, 8.0, 5.0), RB(cx, cz, Y + 2.5), (0, 0, Fr.rbx(cx, cz, Y, fx, fz).yaw()))
    # barris e caixotes encostados nas bordas (nunca no eixo nem perto de portais)
    F0 = Fr(RB(0, 0, Y), (0, 1))
    for (x, z, kind) in ((-38.0, -36.0, "b"), (-36.5, -33.5, "b"), (-37.5, -30.5, "c"), (46.0, -30.0, "b"), (48.5, -28.0, "b"),
                         (47.0, 36.0, "c"), (44.0, 37.0, "s"), (-30.0, 38.3, "b"), (-27.4, 38.3, "b"), (52.0, -6.0, "c"), (52.0, -3.0, "b")):
        Fp = Fr(RB(x, z, Y), (0, 1))
        if kind == "b":
            barrel(b, Fp, 0, 0, 1.1, 2.6)
            fm_lib.col_box("Town", (2.4, 2.4, 2.6), RB(x, z, Y + 1.3))
        elif kind == "c":
            crate(b, Fp, 0, 0, 2.2, turn=r.uniform(-20, 20))
            fm_lib.col_box("Town", (2.4, 2.4, 2.2), RB(x, z, Y + 1.1))
        else:
            sack(b, Fp, 0, 0, 1.3)
    # postes de lanterna: abertura da cerca, cantos da praca, frente da loja e do mural
    posts = [(-L.FENCE_GAP - 2.5, L.FENCE_Z - 1.2), (L.FENCE_GAP + 2.5, L.FENCE_Z - 1.2), (-36.0, -8.0), (36.0, -34.0),
             (-20.0, 30.0), (22.0, 32.0), (46.0, 14.0), (-36.0, 26.0)]
    for i, (x, z) in enumerate(posts):
        Fp = Fr.rbx(x, z, Y, -x, -z)      # braco virado para o centro da praca
        lantern_post(b, Fp, 0, 0, "L_WB_Lamp_Plaza_%d" % i)
        fm_lib.col_box("Town", (1.4, 1.4, 9.0), RB(x, z, Y + 4.5))
    # cerca sul com abertura + placa de boas-vindas (2 faces) + correio
    Ff = Fr(RB(0, L.FENCE_Z, Y), (0, 1))          # ao longo de x Roblox: +x local = ... (f = +Z Roblox -> t = -X)
    Ff = Fr(RB(0, L.FENCE_Z, Y), (0, -1))         # f = -Z Roblox (olha a praca); t = +X Roblox
    fence(b, Ff, L.FENCE_X[0], -L.FENCE_GAP)
    fence(b, Ff, L.FENCE_GAP, L.FENCE_X[1])
    for (x0, x1) in ((L.FENCE_X[0], -L.FENCE_GAP), (L.FENCE_GAP, L.FENCE_X[1])):
        fm_lib.col_box("Town", (x1 - x0, 0.8, 3.4), RB((x0 + x1) / 2, L.FENCE_Z, Y + 1.7))
    Fs = Fr.rbx(L.SIGN[0], L.SIGN[1], Y, 0.0, 1.0)          # a face principal olha +Z (quem chega da ponte)
    welcome_sign(b, Fs, [("BEM-VINDO A", 1.05), ("WOLFBERG", 1.9), ("VILA DA FORJA", 1.05)])
    fm_lib.col_box("Town", (16.0, 1.6, 10.0), RB(L.SIGN[0], L.SIGN[1], Y + 5.0))
    Fsp = Fr.rbx(L.SIGNPOST[0], L.SIGNPOST[1], Y, 0.0, -1.0)
    signpost(b, Fsp, [("FORJA", 0), ("LOJA", -90), ("CAMPEOES", 90), ("MUNDOS", 135), ("ILHAS", 180)])
    fm_lib.col_box("Town", (1.2, 1.2, 9.0), RB(L.SIGNPOST[0], L.SIGNPOST[1], Y + 4.5))
    # correio (o objeto do jogo e o workspace.MailBox; aqui so um pedestal de pedra + marcador)
    bb(b, Fr.rbx(L.MAILBOX[0], L.MAILBOX[1], Y, 1, 0), -1.2, 1.2, -1.2, 1.2, -0.3, 0.4, STD, bevel=0.1)
    mx, mz = L.MAILBOX
    fm_lib.marker("MAILBOX_Correio", RB(mx, mz, Y + 0.4), (0, 0, 0), 2.0, "PLAIN_AXES", "15_GAMEPLAY_MARKERS",
                  {"alvo": "workspace.MailBox", "prompt": "Enviar Feedback", "face_x": 1.0, "face_z": 0.0, "yaw_deg": -90.0})
    # estandartes nos postes da abertura da cerca
    for s in (-1, 1):
        Fb = Fr(RB(s * (L.FENCE_GAP + 2.5), L.FENCE_Z + 1.2, Y), (0, -1))
        banner(b, Fb, 0.0, 0.0, 8.4, "WB_Cloth_Red" if s < 0 else "WB_Cloth_Blue", 2.2, 5.6, pole=True)
    # poco do largo sul
    well(b, Fr.rbx(L.WELL[0], L.WELL[1], Y, 1, 0))
    objs = b.finish()
    # placas flutuantes (BillboardGui pelo montar): LETREIRO_* com atributo texto/icone
    for (name, x, y, z, txt, icon) in (("LETREIRO_Loja", 54.0, Y + 17.0, -9.0, "LOJA DE MOCHILAS", "mochila"),
                                       ("LETREIRO_Mural", -50.0, L.Y_RANK + 36.0, -11.0, "CAMPEOES", "trofeu"),
                                       ("LETREIRO_Mundos", -93.0, Y + 18.0, 62.0, "CAMINHO DOS MUNDOS", "portal"),
                                       ("LETREIRO_Correio", L.MAILBOX[0], Y + 8.0, L.MAILBOX[1], "CORREIO", "carta")):
        fm_lib.marker(name, RB(x, z, y), (0, 0, 0), 2.0, "PLAIN_AXES", "15_GAMEPLAY_MARKERS",
                      {"texto": txt, "icone": icon, "alcance": 170})
    # marcadores de spawn/layout
    sx, sz = L.SPAWN
    fm_lib.marker("SPAWN_Lobby", RB(sx, sz, Y), (0, 0, 0), 2.0, "PLAIN_AXES", "15_GAMEPLAY_MARKERS",
                  {"kind": "spawn", "face_x": 0.0, "face_z": -1.0, "yaw_deg": 0.0, "note": "na praca, atras da cerca, olhando a forja"})
    fm_lib.marker("SPAWNLOBBY_Part", RB(L.SPAWN_LOBBY_PART[0], L.SPAWN_LOBBY_PART[2], L.SPAWN_LOBBY_PART[1]), (0, 0, 0), 2.0,
                  "PLAIN_AXES", "15_GAMEPLAY_MARKERS", {"alvo": "workspace['Mystical Spawn Point'].SpawnLobby", "face_x": 0.0, "face_z": -1.0, "yaw_deg": 0.0})
    for k, (x, y, z) in L.LOBBY_LAYOUT.items():
        f = {"Spawn": (0, -1), "Shop": (1, 0), "ShopFacing": (-1, 0), "Ignis": (0, -1), "PortalIsland": (-1, 0)}[k]
        fm_lib.marker("LAYOUT_" + k, RB(x, z, y), (0, 0, 0), 2.0, "PLAIN_AXES", "15_GAMEPLAY_MARKERS",
                      {"lobbylayout": k, "face_x": float(f[0]), "face_z": float(f[1]),
                       "yaw_deg": round(math.degrees(math.atan2(-f[0], -f[1])), 2)})
    return objs
