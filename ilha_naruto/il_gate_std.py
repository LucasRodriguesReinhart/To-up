# il_gate_std - PADRAO TECNICO COMUM dos portoes de compra (COMPARTILHADO E CONGELADO; dono: integracao).
# Todos os portoes (Dragon Ball na ilha; Shadow Garden, Demon Slayer, One Piece e One Punch Man na galeria) usam:
#   - o MESMO vao livre (OPEN_W x OPEN_H), a mesma largura de piso (DECK_W) e a mesma profundidade de referencia;
#   - a MESMA logica de interacao e os MESMOS marcadores (relativos ao eixo do portao);
#   - o MESMO par de estados: LOCKED (barreira de energia + cadeado + colisao) e UNLOCKED (tudo isso some; sobra a
#     moldura com a passagem limpa e o efeito de abertura no marcador GATE_<k>_OpenFX).
# Cada portao desenha a PROPRIA moldura (silhueta, materiais, ornamento) em volta disto.
#
# Referencial do portao (G): origem = centro do vao no nivel do piso; +Y = direcao de quem ATRAVESSA (sai da ilha),
# -Y = lado de quem chega (onde fica a interacao), +X = direita de quem atravessa, Z para cima.
# Use gate_frame(gx, gy, gz, yaw).p(x, y, z) para converter local -> mundo.
#
# Contrato com o jogo (Roblox):
#   GATE_<k>_Barrier (MeshPart, Neon)  atributo gate_part="barrier" -> Transparency 1 ao desbloquear
#   GATE_<k>_Lock    (MeshPart)        atributo gate_part="lock"    -> some ao desbloquear
#   COL_Gate<k>Lock_001 (Part invisivel, col_kind="GateLock", gate=<k>) -> CanCollide false ao desbloquear
#   GATE_<k>_OpenFX  (marcador)        ponto dos efeitos de abertura (VFX diferente do bloqueado)
#   GATE_<k>_INTERACT (marcador)       ProximityPrompt / zona de compra (raio no atributo radius)
#   PURCHASE_UI_ANCHOR_<k> (marcador)  ancora do painel de preco (BillboardGui) - NADA de placa 3D com preco
import math
from mathutils import Vector
import il_lib as IL
from il_lib import MB, col_box, mk
from fm_parts import Frame

OPEN_W = 16.0        # vao livre
OPEN_H = 18.0        # altura livre
DECK_W = 18.0        # largura do piso/ponte que chega ao portao
DEPTH = 10.0         # profundidade de referencia da moldura (pode variar por portao)
INTERACT_D = 7.0     # interacao: 7 studs antes do plano da barreira
EXIT_D = 12.0        # saida: 12 depois
UI_UP = 8.0          # painel de preco: 8 acima do topo do vao
KEYS = {"DB": "DragonBall", "ShadowGarden": "ShadowGarden", "DemonSlayer": "DemonSlayer", "OnePiece": "OnePiece",
        "OnePunchMan": "OnePunchMan"}
AREA_ID = {"DB": 2, "DemonSlayer": 3, "ShadowGarden": 4, "OnePiece": 5, "OnePunchMan": 6}
GALLERY_X0 = 640.0   # galeria dos portoes (fora da ilha, so para modelar/renderizar/exportar)
GALLERY_STEP = 130.0
GALLERY_Z = 16.2
GALLERY_ORDER = ["ShadowGarden", "DemonSlayer", "OnePiece", "OnePunchMan"]


def gate_frame(gx, gy, gz, yaw):
    """yaw: rotacao Z tal que o +Y local aponta para quem atravessa"""
    return Frame(gx, gy, gz, yaw)


def gallery_slot(key):
    i = GALLERY_ORDER.index(key)
    return (GALLERY_X0 + GALLERY_STEP * i, 0.0, GALLERY_Z, 0.0)


def barrier(key, F, mat, shape="arch", thick=0.5, lock_mat="Metal_Gold", rng=None):
    """barreira de energia (LOCKED) no plano y=0 do portao + cadeado dos dois lados + colisao de bloqueio.
    shape: 'rect' | 'arch' (retangulo + meio circulo no topo) | 'circle' (disco no vao; os cantos de baixo ficam
    fechados por uma soleira de energia)"""
    hw, h = OPEN_W / 2, OPEN_H
    mb = MB("GATE_%s_Barrier" % key, "08_PURCHASE_GATES", rng, detail="hero")
    if shape == "rect":
        mb.box((OPEN_W, thick, h), F.p(0, 0, h / 2), F.r(), mat, 0.0)
    elif shape == "arch":
        rs = hw
        zs = h - rs
        mb.box((OPEN_W, thick, zs), F.p(0, 0, zs / 2), F.r(), mat, 0.0)
        n = 14
        for i in range(n):
            a0 = math.pi * i / n
            a1 = math.pi * (i + 1) / n
            pts = [F.p(0, 0, zs), F.p(rs * math.cos(a0), 0, zs + rs * math.sin(a0)),
                   F.p(rs * math.cos(a1), 0, zs + rs * math.sin(a1))]
            _slab_tri(mb, pts, F, thick, mat)
    else:  # circle
        r = min(hw, h / 2)
        zc = h / 2
        n = 24
        for i in range(n):
            a0 = 2 * math.pi * i / n
            a1 = 2 * math.pi * (i + 1) / n
            pts = [F.p(0, 0, zc), F.p(r * math.cos(a0), 0, zc + r * math.sin(a0)),
                   F.p(r * math.cos(a1), 0, zc + r * math.sin(a1))]
            _slab_tri(mb, pts, F, thick, mat)
        mb.box((OPEN_W, thick, 1.2), F.p(0, 0, 0.6), F.r(), mat, 0.0)
    ob = mb.finish()
    ob["gate"] = key
    ob["gate_part"] = "barrier"
    ob["gate_state"] = "locked"
    # cadeado estilizado (corpo + alca), nos dois lados da barreira
    lk = MB("GATE_%s_Lock" % key, "08_PURCHASE_GATES", rng, detail="hero")
    for s in (-1, 1):
        y = s * (thick / 2 + 0.35)
        c = F.p(0, y, h * 0.46)
        lk.box((3.2, 0.7, 2.7), c, F.r(), lock_mat, 0.25)
        for sx in (-1, 1):
            lk.box((0.55, 0.55, 2.0), F.p(sx * 1.05, y, h * 0.46 + 2.1), F.r(), lock_mat, 0.1)
        lk.box((2.65, 0.55, 0.55), F.p(0, y, h * 0.46 + 3.0), F.r(), lock_mat, 0.1)
        lk.box((0.5, 0.8, 1.0), F.p(0, y, h * 0.46 - 0.2), F.r(), "Metal_Dark", 0.05)
    lo = lk.finish()
    lo["gate"] = key
    lo["gate_part"] = "lock"
    lo["gate_state"] = "locked"
    col = col_box("Gate%sLock" % key, (OPEN_W + 0.6, 1.4, h), F.p(0, 0, h / 2), F.r(), kind="GateLock")
    col["gate"] = key
    return ob, lo, col


def _slab_tri(mb, pts, F, thick, mat):
    """triangulo com espessura (normal = eixo Y do portao)"""
    ny = Vector(F.p(0, 1, 0)) - Vector(F.p(0, 0, 0))
    a = [Vector(p) - ny * (thick / 2) for p in pts]
    b = [Vector(p) + ny * (thick / 2) for p in pts]
    for i in range(3):
        j = (i + 1) % 3
        mb.quad(a[i], a[j], b[j], b[i], mat)
    mb.tri(a[0], a[2], a[1], mat)
    mb.tri(b[0], b[1], b[2], mat)


def markers(key, F, yaw, area_id=None):
    """os 5 marcadores obrigatorios + o do efeito de abertura, sempre nas mesmas posicoes relativas"""
    area_id = area_id if area_id is not None else AREA_ID.get(key, 0)
    mk("GATE_%s" % key, F.p(0, 0, 0), (0, 0, yaw), 4.0, "ARROWS",
       props={"open_w": OPEN_W, "open_h": OPEN_H, "deck_w": DECK_W, "area_id": area_id, "key": key})
    mk("GATE_%s_LOCKED" % key, F.p(0, 0, OPEN_H / 2), (0, 0, yaw), 2.0, "CUBE",
       props={"gate": key, "state_default": "locked"})
    mk("GATE_%s_INTERACT" % key, F.p(0, -INTERACT_D, 0.2), (0, 0, yaw), 2.0, "SPHERE",
       props={"gate": key, "radius": 10.0})
    mk("GATE_%s_EXIT" % key, F.p(0, EXIT_D, 0.2), (0, 0, yaw), 2.0, "ARROWS", props={"gate": key})
    mk("PURCHASE_UI_ANCHOR_%s" % key, F.p(0, -2.0, OPEN_H + UI_UP), (0, 0, yaw + math.pi), 2.0, "SINGLE_ARROW",
       props={"gate": key, "faces": "approach", "ui": "BillboardGui preco/requisito"})
    mk("GATE_%s_OpenFX" % key, F.p(0, 0, OPEN_H / 2), (0, 0, yaw), 3.0, "SPHERE",
       props={"gate": key, "state": "unlocked", "fx": "abertura"})     # vai no export como marcador


def showcase_platform(key, F, length=46.0, width=38.0, z_top=0.0, m="Stone_Paving_Warm", side_m="Stone_Wall_Dark"):
    """plataforma neutra da galeria (so para modelar/renderizar os portoes fora da ilha); nao vai para a ilha.
    Topo do tabuleiro EXATAMENTE no nivel do portao (gz); a base tem 38 x 46 (os portoes tem ~34 de base)."""
    mb = MB("GATEGAL_%s_Platform" % key, "08_PURCHASE_GATES", None, detail="near")
    mb.box((width, length, 3.0), F.p(0, 0, z_top - 1.9), F.r(), side_m, 0.2)
    mb.box((DECK_W, length + 0.2, 0.4), F.p(0, 0, z_top - 0.2), F.r(), m, 0.05)
    mb.finish()
    col_box("GateGal%s" % key, (width, length, 3.0), F.p(0, 0, z_top - 1.5), F.r())
