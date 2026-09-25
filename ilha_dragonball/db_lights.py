# db_lights - VESTIR (onda 3), LUZES de dia da Ilha 2 (Dragon Ball): nomes L_DBLit_*, colecao 11_LIGHTING (o
# fm_lib.light ja poe la). Teto de dia do vestir inteiro = 12; aqui <= 10.
# So luz pontual QUENTE (laranja / branco quente) onde ela aquece a ALTURA DO JOGADOR e nenhuma zona ja acendeu:
#   praca de entrada (os 2 lampioes Capsule da praca do db_entrance nao tinham luz), rua do mercado (entre os postes
#   de lanterna da entrada do mercado e o carrinho de feira; o L_DBHub_Market fica DENTRO do pavilhao), comeco da
#   trilha da saida (os 2 lampioes do topo da escada nao tinham luz), aproximacao do summon (postes do pe da escada
#   sem luz) + as luzes das pecas que o db_props montou (db_props.LAMP_SPOTS, so as que couberam): os postes Capsule
#   dos cruzamentos trilha x promenade e a lanterna marcial do patio de treino do dojo (o L_DBHub_Dojo e interno).
# Regra: a luz planejada que cair a menos de 9 studs (e 7 de altura) de uma luz de outra zona e PULADA (impresso).
import math
import db_layout as L
from db_lib import light
import bpy

G, H, EZ = L.GROUND, L.HUB, L.EXIT_Z
WARM = (1.0, 0.62, 0.3)          # ambar dos lampioes
WARM_W = (1.0, 0.76, 0.52)       # branco quente (patio de treino)

# (nome, posicao, energia W, cor, raio)
PLAN = [
    ("L_DBLit_EntryPlaza_W", (-8.8, -76.4, G + 4.6), 300.0, WARM, 1.2),
    ("L_DBLit_EntryPlaza_E", (8.8, -76.4, G + 4.6), 300.0, WARM, 1.2),
    ("L_DBLit_MarketStreet", (-86.0, 110.5, H + 5.2), 360.0, WARM, 1.5),
    ("L_DBLit_ExitTrail", (80.3, 31.4, EZ + 4.2), 300.0, WARM, 1.2),
    ("L_DBLit_SummonApproach", (-86.5, -2.0, G + 5.4), 320.0, WARM, 1.2),
]
MIN_D, MIN_DZ = 9.0, 7.0


def build():
    mine = []
    others = [(o.name, o.location.copy()) for o in bpy.data.objects
              if o.type == "LIGHT" and not o.name.startswith(("L_DBLit_", "SUN_"))]
    try:
        import db_props
        lamps = [(n, tuple(p), e, col, 0.5) for n, p, e, col in db_props.LAMP_SPOTS]
    except Exception as ex:
        print("LIGHTS aviso: sem postes do db_props (%s)" % ex)
        lamps = []
    for name, p, e, col, rad in PLAN + lamps:
        near = [n for n, q in others if math.hypot(q.x - p[0], q.y - p[1]) < MIN_D and abs(q.z - p[2]) < MIN_DZ]
        if near:
            print("LIGHTS pulada %s (ja iluminado por %s)" % (name, near[0]))
            continue
        mine.append(light(name, "POINT", p, e, col, rad))
    print("LIGHTS montadas=%d (teto de dia do vestir 12)" % len(mine))
    return mine
