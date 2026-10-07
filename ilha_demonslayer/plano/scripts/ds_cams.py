# ds_cams.py - cameras de QA da Ilha 4 (referencial LOCAL do ds_geo; Z absoluto). (loc, alvo, lente mm)
# As PlayerHeight ficam com o olho a 5,5 acima do piso (avatar ~5). As CAM_DS_Ref_0n reproduzem as 5 referencias
# aprovadas (estimadas pela posicao relativa entrada / vila / clareira / forja / summon em cada imagem).
import sys
sys.dont_write_bytecode = True
from ds_geo import T0, T1, T2, T3, T4, DECK, exit_point, gate_op

EYE = 5.5
_g = gate_op()
_e = exit_point(20.0)
CAMS = {
    # gerais
    "CAM_DS_Entry": ((8.0, -45.0, 62.0), (-4.0, 90.0, 66.0), 22),
    "CAM_DS_Front": ((40.0, -260.0, 220.0), (20.0, 300.0, 70.0), 28),
    "CAM_DS_Left": ((-460.0, 300.0, 230.0), (20.0, 300.0, 70.0), 30),
    "CAM_DS_Right": ((520.0, 280.0, 230.0), (20.0, 300.0, 70.0), 30),
    "CAM_DS_Back": ((-20.0, 900.0, 260.0), (20.0, 280.0, 70.0), 30),
    "CAM_DS_BirdEye": ((25.0, 300.0, 1100.0), (25.0, 302.0, 60.0), 32),
    "CAM_DS_Clearing": ((24.0, 404.0, T3 + 10.0), (40.0, 200.0, T1), 24),
    "CAM_DS_Village": ((-20.0, 150.0, 100.0), (-110.0, 260.0, 68.0), 26),
    "CAM_DS_Forge": ((30.0, 300.0, 96.0), (10.0, 480.0, 102.0), 26),
    "CAM_DS_Summon": ((70.0, 230.0, 84.0), (180.0, 300.0, 92.0), 28),
    "CAM_DS_OnePieceGate": ((-110.0, 548.0, 92.0), (_g[0], _g[1], 90.0), 24),
    # altura do jogador
    "CAM_DS_PlayerHeight_Entry": ((0.0, -40.0, DECK + 1.2 + EYE), (0.0, 120.0, 64.0), 22),
    "CAM_DS_PlayerHeight_Clearing": ((-20.0, 140.0, T1 + EYE), (50.0, 280.0, 63.0), 22),
    "CAM_DS_PlayerHeight_Village": ((-44.0, 130.0, T1 + EYE), (-84.0, 210.0, 66.0), 22),
    "CAM_DS_PlayerHeight_Forge": ((16.0, 360.0, T1 + EYE), (10.0, 480.0, 96.0), 22),
    "CAM_DS_PlayerHeight_Summon": ((112.0, 300.0, T1 + EYE), (184.0, 300.0, 82.0), 22),
    "CAM_DS_PlayerHeight_OnePieceGate": ((_e[0], _e[1], T4 + EYE), (_g[0], _g[1], T4 + 9.0), 24),
    # referencias aprovadas (estimadas)
    "CAM_DS_Ref_01": ((30.0, -300.0, 380.0), (25.0, 280.0, 62.0), 28),     # frontal alta: ponte de entrada no centro
    "CAM_DS_Ref_02": ((330.0, -160.0, 300.0), (20.0, 280.0, 62.0), 30),    # sudeste: summon a direita, entrada embaixo-esq
    "CAM_DS_Ref_03": ((-30.0, 820.0, 320.0), (20.0, 260.0, 62.0), 28),     # norte: forja na frente, entrada ao fundo
    "CAM_DS_Ref_04": ((-90.0, -260.0, 430.0), (30.0, 270.0, 60.0), 26),    # sul-sudoeste alta e aberta
    "CAM_DS_Ref_05": ((-200.0, -150.0, 200.0), (40.0, 220.0, 70.0), 30),   # sudoeste baixa: torii na frente, vila a esq
}
