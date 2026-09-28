# sg_emblem - SISTEMA DE IDENTIDADE da Ilha 3 (Shadow Garden). COMPARTILHADO E CONGELADO (dono: integracao).
# Um UNICO simbolo da ordem, original (nao e logo de obra nenhuma): a LUA EM ECLIPSE atravessada por uma LAMINA.
#   - anel externo de prata (a moldura nobre)
#   - disco violeta luminoso (a lua) parcialmente coberto por um disco NEGRO deslocado -> crescente (a sombra que come a
#     luz: "a eminencia nas sombras")
#   - lamina vertical de prata atravessando o simbolo (a espada de Shadow), guarda negra
#   - 8 raios curtos de prata fora do anel (so na versao 'monumental')
# Todo lugar que fala pela ordem usa ESTE simbolo: fachada do castelo, estandartes, portoes, piso do salao, dungeon,
# porticos da entrada. Nada de tridente/estrela/lua soltos (ornamento sem sistema = cara de IA).
#
# API (todas desenham em MBs que o modulo chamador ja criou; nada de colisao aqui):
#   emblem(mb_metal, mb_glow, mb_dark, c, yaw, r, depth=0.6, monumental=False)
#       c = (x, y, z) centro; yaw = rumo (rad) para onde o simbolo OLHA; r = raio do anel externo
#   banner(mb_cloth, mb_metal, mb_glow, mb_dark, top, yaw, w, h, tails=True)
#       estandarte da ordem: tecido roxo profundo com barra negra e borda de prata, emblema em cima, ponta em V
#   plaque(mb_stone, mb_metal, mb_glow, mb_dark, c, yaw, r)
#       medalhao de pedra obsidiana com o emblema (portais, pedestais, fontes)
# Materiais: Metal_SG_Silver (prata), SG_Rune_Glow (lua), Stone_SG_Obsidian (sombra/guarda), Cloth_SG_Purple (tecido).
import math

SILVER, MOON, SHADOW, CLOTH, TRIM = "Metal_SG_Silver", "SG_Rune_Glow", "Stone_SG_Obsidian", "Cloth_SG_Purple", "Stone_SG_Obsidian"


def _frame(c, yaw):
    """eixos do plano do emblema: f = normal (para onde olha), u = direita, z = cima"""
    fx, fy = math.cos(yaw), math.sin(yaw)
    ux, uy = math.sin(yaw), -math.cos(yaw)       # direita de quem OLHA o emblema de frente
    return (fx, fy), (ux, uy)


def _p(c, f, u, a, b, d):
    """ponto no plano: a = lateral (u), b = altura, d = profundidade (ao longo de f)"""
    return (c[0] + u[0] * a + f[0] * d, c[1] + u[1] * a + f[1] * d, c[2] + b)


def _disc(mb, c, f, r, thick, m, n=24):
    """disco (cilindro raso) com o eixo na normal f"""
    yaw = math.atan2(f[1], f[0])
    mb.cyl(r, thick, c, (0.0, math.pi / 2, yaw), m=m, n=n, bevel=0.0)


def _ring(mb, c, f, u, r, w, m, n=28, d=0.0):
    pts = []
    for i in range(n + 1):
        t = 2 * math.pi * i / n
        pts.append(_p(c, f, u, r * math.cos(t), r * math.sin(t), d))
    mb.tube(pts, w, m, 6)


def emblem(mb_metal, mb_glow, mb_dark, c, yaw, r, depth=0.6, monumental=False):
    f, u = _frame(c, yaw)
    # lua (disco luminoso) e a sombra (disco negro deslocado para a direita e um pouco para cima)
    _disc(mb_glow, _p(c, f, u, 0, 0, depth * 0.10), f, r * 0.74, depth * 0.30, MOON)
    _disc(mb_dark, _p(c, f, u, r * 0.26, r * 0.10, depth * 0.34), f, r * 0.64, depth * 0.30, SHADOW)
    # anel de prata duplo
    _ring(mb_metal, c, f, u, r * 0.90, max(0.12, r * 0.07), SILVER, d=depth * 0.40)
    _ring(mb_metal, c, f, u, r * 0.78, max(0.06, r * 0.025), SILVER, d=depth * 0.42)
    # lamina vertical (a espada de Shadow): lamina de prata, guarda e cabo negros
    bh = r * 2.3
    mb_metal.box((max(0.10, depth * 0.35), max(0.12, r * 0.10), bh * 0.62), _p(c, f, u, 0, r * 0.28, depth * 0.62),
                 (0, 0, yaw), SILVER, 0.0)
    tip = _p(c, f, u, 0, r * 0.28 + bh * 0.31, depth * 0.62)
    mb_metal.cyl(max(0.07, r * 0.05), r * 0.22, (tip[0], tip[1], tip[2] + r * 0.11), m=SILVER, n=4, r2=0.0, bevel=0.0)
    mb_dark.box((max(0.14, depth * 0.40), r * 0.62, max(0.10, r * 0.09)), _p(c, f, u, 0, -r * 0.05, depth * 0.66),
                (0, 0, yaw), SHADOW, 0.0)
    mb_dark.box((max(0.12, depth * 0.38), max(0.12, r * 0.09), r * 0.46), _p(c, f, u, 0, -r * 0.34, depth * 0.64),
                (0, 0, yaw), SHADOW, 0.0)
    if monumental:
        for k in range(8):
            t = 2 * math.pi * k / 8 + math.pi / 8
            a, b = math.cos(t), math.sin(t)
            L = r * (0.34 if k % 2 == 0 else 0.22)
            mid = _p(c, f, u, a * (r * 0.98 + L / 2), b * (r * 0.98 + L / 2), depth * 0.3)
            ang = math.atan2(b, a)
            # raio no plano: caixa longa na direcao (a, b) do plano: inclina em Y e gira para o eixo u
            mb_metal.box((L, max(0.12, depth * 0.3), max(0.14, r * 0.07)), mid,
                         (0, -ang, yaw - math.pi / 2), SILVER, 0.0)


def plaque(mb_stone, mb_metal, mb_glow, mb_dark, c, yaw, r):
    f, u = _frame(c, yaw)
    _disc(mb_stone, _p(c, f, u, 0, 0, -0.25), f, r * 1.12, 0.5, TRIM)
    emblem(mb_metal, mb_glow, mb_dark, _p(c, f, u, 0, 0, 0.05), yaw, r * 0.92, depth=0.45)


def banner(mb_cloth, mb_metal, mb_glow, mb_dark, top, yaw, w, h, tails=True):
    """estandarte pendurado por uma verga de ferro/prata em 'top' (centro da verga), olhando para yaw"""
    f, u = _frame(top, yaw)
    th = 0.22
    mb_metal.box((w + 1.0, 0.28, 0.28), _p(top, f, u, 0, 0, 0), (0, 0, yaw + math.pi / 2), "Metal_SG_BlackIron", 0.0)
    for s in (-1, 1):
        mb_metal.ico(0.26, _p(top, f, u, s * (w / 2 + 0.5), 0, 0), SILVER, 1)
    body_h = h * (0.84 if tails else 1.0)
    mb_cloth.box((w, th, body_h), _p(top, f, u, 0, -body_h / 2 - 0.15, 0.05), (0, 0, yaw + math.pi / 2), CLOTH, 0.0)
    # barra negra no alto e bordas de prata
    mb_dark.box((w + 0.02, th + 0.04, h * 0.08), _p(top, f, u, 0, -h * 0.09, 0.07), (0, 0, yaw + math.pi / 2), SHADOW, 0.0)
    for s in (-1, 1):
        mb_metal.box((0.14, th + 0.06, body_h), _p(top, f, u, s * (w / 2 - 0.07), -body_h / 2 - 0.15, 0.08),
                     (0, 0, yaw + math.pi / 2), SILVER, 0.0)
    if tails:
        zb = -body_h - 0.15
        for s in (-1, 1):
            a = _p(top, f, u, s * w / 2, zb, 0.05)
            b = _p(top, f, u, 0, zb - h * 0.16, 0.05)
            cc = _p(top, f, u, 0, zb, 0.05)
            mb_cloth.tri(a, b, cc, CLOTH)
            mb_cloth.tri(cc, b, a, CLOTH)
    er = min(w * 0.36, h * 0.16)
    emblem(mb_metal, mb_glow, mb_dark, _p(top, f, u, 0, -h * 0.36, th / 2 + 0.12), yaw, er, depth=0.25)
