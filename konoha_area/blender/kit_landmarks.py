# KONOHA_LANDMARKS kit: the pieces that make the island read as Konoha from far away.
import math
from mathutils import Euler, Vector, Matrix
from klib import *
from kit_parts import *

PI = math.pi
C = 'KONOHA_LANDMARKS'

def _rot(*mats):
    R = Matrix.Identity(3)
    for m in mats: R = R @ m
    return tuple(R.to_euler('XYZ'))

def tri(cx, cy, cz, w, h, depth, ang, m, name='Mecha', tilt=0.0):
    """Isosceles triangular prism pointing +Z, lying in the XZ plane, rotated by ang about Y."""
    Ry = Euler((0, ang, 0), 'XYZ').to_matrix()
    Rx = Euler((tilt, 0, 0), 'XYZ').to_matrix()
    for side, rz in ((1, PI/2), (-1, -PI/2)):
        off = Rx @ Ry @ Vector((side*w/4, 0, 0))
        e = _rot(Rx, Ry, Euler((0, 0, rz), 'XYZ').to_matrix())
        wedge(name, (cx+off.x, cy+off.y, cz+off.z), (depth, w/2, h), m, e, col=False)

# ---------------------------------------------------------------- HOKAGE FACES
def face_base(stone='face_stone', shade='face_shadow'):
    box('Cranio', (0, -4, 17), (18, 8, 13), stone, col=True)
    box('RostoInferior', (0, -4.3, 7.5), (12, 7.6, 8), stone, col=False)
    box('Queixo', (0, -4.5, 1.8), (8.4, 7.2, 4), stone, col=False)
    for s in (-1, 1):
        box('Maxilar', (s*6.1, -4.2, 6.2), (3.4, 7.4, 12), stone, (0, s*.42, 0), col=False)
        box('Maca', (s*6.2, -8.0, 9.9), (2.6, .9, 1.5), stone, (0, s*-.3, 0), col=False)
        box('Orelha', (s*9.5, -3, 13), (2, 3.6, 5.5), stone, col=False)
        box('Orbita', (s*4.1, -8.1, 13.4), (4.4, .5, 2.0), shade, col=False)
        box('Palpebra', (s*4.1, -8.45, 14.2), (4.6, .6, .7), stone, (0, s*-.12, 0), col=False)
        box('Sobrancelha', (s*4.3, -8.6, 15.8), (4.8, 1.2, 1.0), stone, (0, s*.14, 0), col=False)
        box('Sulco', (s*3.6, -8.1, 7.2), (.5, .5, 3.6), shade, (0, s*-.35, 0), col=False)
    box('Nariz', (0, -8.7, 11), (2.4, 2.4, 5.4), stone, (-.3, 0, 0), col=False)
    box('BaseNariz', (0, -8.9, 8.6), (3.4, 1.8, 1.2), stone, col=False)
    box('Boca', (0, -8.15, 5.6), (4.6, .5, .6), shade, col=False)
    box('Labio', (0, -8.35, 4.9), (3.4, .6, .7), stone, col=False)
    box('Pescoco', (0, -2, -2), (10, 5, 6), stone, col=False)

def rosto_1():   # spiky swept hair (fourth-hokage-like silhouette)
    asset(C, 'Rosto_Hokage_1'); face_base()
    for i, a in enumerate((-1.25, -.85, -.45, -.1, .25, .6, 1.0, 1.35)):
        r = 10.5
        tri(math.sin(a)*r*.95, -3.6, 18 + math.cos(a)*r*.75, 6.5, 9 + (i % 2)*2.5, 7.4, a, 'face_stone', 'MechaEspetada')
    for x, a in ((-5, -.25), (-1.5, .1), (2, -.1), (5.5, .3)):
        tri(x, -7.6, 18.2, 3.6, 5.5, 2.4, PI + a, 'face_stone', 'Franja')
    box('Topo', (0, -3.5, 23.5), (17, 7.5, 3), 'face_stone', col=False)

def rosto_2():   # long straight hair, centre parting
    asset(C, 'Rosto_Hokage_2'); face_base()
    box('TopoCabelo', (0, -3.6, 24.2), (20, 8.4, 4), 'face_stone', col=False)
    for s in (-1, 1):
        box('Cortina', (s*10.6, -3.8, 12), (4.4, 8.6, 26), 'face_stone', col=False)
        box('FranjaLateral', (s*6.4, -7.9, 21.6), (6.4, 1.4, 2.4), 'face_stone', (0, s*-.3, 0), col=False)
        box('SombraCortina', (s*8.3, -8.0, 9), (.8, .5, 16), 'face_shadow', col=False)
    box('Risca', (0, -7.9, 23.3), (.5, 1.8, 3), 'face_shadow', col=False)

def rosto_3():   # short rugged hair, goatee, lined brow
    asset(C, 'Rosto_Hokage_3'); face_base()
    box('TopoCabelo', (0, -3.6, 23.6), (19, 8.2, 3.4), 'face_stone', col=False)
    for i, x in enumerate((-8, -5, -2, 1, 4, 7)):
        tri(x, -3.8, 26.3, 4.2, 3.6 + (i % 3), 7.6, (x/10)*.6, 'face_stone', 'MechaCurta')
    box('Rugas', (0, -8.3, 19.4), (8, .4, .5), 'face_shadow', col=False)
    box('Rugas', (0, -8.3, 18.4), (6, .4, .5), 'face_shadow', col=False)
    tri(0, -8.3, 1.2, 3.4, 3.6, 1.6, PI, 'face_stone', 'Cavanhaque')
    for s in (-1, 1):
        box('Costeleta', (s*8.6, -5.5, 16), (2, 4.5, 8), 'face_stone', col=False)

def rosto_4():   # bangs + side locks + forehead mark (fifth-hokage-like silhouette)
    asset(C, 'Rosto_Hokage_4'); face_base()
    box('TopoCabelo', (0, -3.4, 24), (19.6, 8.4, 3.6), 'face_stone', col=False)
    for x in (-6.8, -3.4, 0, 3.4, 6.8):
        tri(x, -7.6, 19.8, 3.8, 4.2, 2.2, PI, 'face_stone', 'Franja')
    for s in (-1, 1):
        box('MechaLateral', (s*10.2, -5.2, 10), (3.6, 5.6, 24), 'face_stone', col=False)
        box('Mecha', (s*10.8, -5.2, -3), (2.8, 4, 6), 'face_stone', (0, s*.25, 0), col=False)
    box('Marca', (0, -8.35, 17.6), (1.3, .5, 1.3), 'face_shadow', (0, PI/4, 0), col=False)

# ---------------------------------------------------------------- HOKAGE RESIDENCE
def residencia_hokage():
    asset(C, 'Residencia_Hokage')
    cyl('Plinto', (0, 0, .6), 21, 1.2, 'stone', col=True)
    floors = [(17, 10.5, 'hokage_red', 12), (14.5, 8.5, 'wall_peach', 10), (11.5, 6.5, 'hokage_red', 8)]
    z = 1.2
    for i, (r, h, m, nw) in enumerate(floors):
        cyl('Andar%d' % (i+1), (0, 0, z+h/2), r, h, m, col=True)
        cyl('FaixaBase', (0, 0, z+.5), r+.15, 1.0, 'wall_cream', col=False)
        for k in range(nw):
            a = (k+.5)/nw*2*PI - PI/2
            if i == 0 and abs(a + PI/2) < .35: continue
            x, y = math.cos(a)*(r+.05), math.sin(a)*(r+.05)
            box('MolduraJanela', (x, y, z+h*.56), (.3, 3.4, 3.6), 'wood_dark', (0, 0, a), col=False)
            box('Janela', (x*1.004, y*1.004, z+h*.56), (.3, 2.6, 2.8), 'window_lit' if (k+i) % 4 == 0 else 'glass', (0, 0, a), col=False)
        z += h
        cyl('Beiral', (0, 0, z+.35), r+3.4, .7, 'hokage_roof', col=True)
        cyl('BeiralDegrau', (0, 0, z+.95), r+2.2, .6, 'hokage_roof', col=False)
        cyl('BeiralTopo', (0, 0, z+1.45), r+1.0, .5, 'hokage_roof', col=False)
        z += 1.2
    cyl('Cobertura', (0, 0, z+.3), 12.6, .6, 'wall_tan', col=True)
    cyl('AroTeto', (0, 0, z+.8), 12.6, .5, 'hokage_roof', col=False)
    cyl('SimboloTeto', (0, 0, z+.7), 6, .2, 'cloth_red', col=False)
    box('CasaTopo', (5, 5, z+2.6), (4, 4, 4), 'wall_cream', col=False)
    cyl('CupulaTopo', (5, 5, z+5), 2.6, 1, 'hokage_roof', col=False)
    # entrance porch facing -Y
    box('Portico', (0, -18.2, 5.5), (12, 5, 11), 'wall_cream', col=True)
    box('PortaPrincipal', (0, -20.8, 4.6), (7, .5, 8), 'wood', col=False)
    box('MolduraPorta', (0, -20.7, 5), (8.4, .4, 9), 'wood_dark', col=False)
    skirt(Body(0, -18.2, 0, 12, 5, 11), 11.6, 2.4, 1.6, 'hokage_roof')
    box('TetoPortico', (0, -18.2, 11.9), (12.4, 5.4, .6), 'hokage_roof', col=False)
    for i in range(4):
        box('Degrau', (0, -21.5 - i*1.1, .9 - i*.3), (12 + i, 1.2, 1.8 - i*.6), 'stone', col=True)
    box('PlacaHokage', (0, -15.3, 16.2), (9, .4, 2.6), 'wood', col=False, text='HOKAGE')
    box('EmblemaFrente', (0, -12.3, 22.5), (6.5, .5, 6.5), 'wall_cream', (0, 0, 0), col=False, emblem='leaf')
    # annex tower east
    cyl('Anexo', (19.5, 6, 12), 5, 24, 'wall_cream', col=True)
    for zz in (8, 16, 24.3):
        cyl('AnelAnexo', (19.5, 6, zz), 6.3, .7, 'roof_blue', col=False)
    cyl('TopoAnexo', (19.5, 6, 25.4), 4.2, 1.4, 'roof_blue', col=False)
    box('AntenaAnexo', (19.5, 6, 29), (.3, .3, 6), 'metal', col=False)
    rod('Passarela', (13, 3, 14), (16, 4.5, 14), 2.6, 'wall_tan', h=2.4)

# ---------------------------------------------------------------- MAIN GATE
def portao_principal():
    asset(C, 'Portao_Principal')   # opening 24 wide along X, village at +Y
    for s in (-1, 1):
        box('BasePilar', (s*15, 0, 1.8), (8, 9, 3.6), 'stone', col=True)
        box('Pilar', (s*15, 0, 17), (5.4, 6.4, 30), 'wood', col=True)
        box('FaixaPilar', (s*15, 0, 26), (5.8, 6.8, 1), 'wood_dark', col=False)
        # door leaves swung inward ~70 degrees
        a = s * math.radians(-92)
        hx, hy = s*12.2, 2.5
        cx, cy = hx - s*7*math.cos(math.radians(92)), hy + 7*math.sin(math.radians(92))
        box('FolhaPortao', (cx, cy, 13.5), (14, 1.3, 26), 'wood_light', (0, 0, a), col=True)
        for zz in (4, 13.5, 23):
            box('Reforco', (cx, cy, zz), (14.2, 1.5, 1), 'wood_dark', (0, 0, a), col=False)
        box('Caractere', (cx + math.sin(a)*.72, cy - math.cos(a)*.72, 15), (8, .2, 8), 'wood_light', (0, 0, a), col=False,
            text=('あ' if s < 0 else 'ん'), textcolor='58,140,84')
    box('Viga', (0, 0, 32.5), (38, 7, 3), 'wood_dark', col=True)
    box('VigaInferior', (0, -.5, 29.2), (26, 5, 1.6), 'wood', col=False)
    for sy, r in ((-1, 0), (1, PI)):
        wedge('Telhado', (0, sy*2.6, 35.3), (42, 5.2, 2.6), 'gate_green', (0, 0, r), col=False)
    box('Cumeeira', (0, 0, 36.8), (43, 1, .7), 'trim_dark', col=False)
    box('Placa', (0, -3.8, 32.6), (16, .5, 2.4), 'wood_light', col=False, text='VILA DA FOLHA')
    box('EmblemaPortao', (0, -3.9, 38.8), (5, .4, 5), 'cloth_red', col=False, emblem='leaf')
    box('SuporteEmblema', (0, -3.6, 37.3), (1, .6, 2.4), 'wood_dark', col=False)

# ---------------------------------------------------------------- GREAT MINE FACADE
def grande_mina():
    asset(C, 'Grande_Mina')      # opening 20 wide x 17 tall at origin, tunnel runs +Y
    rs = rng(71)
    for s in (-1, 1):
        box('RochaPilar', (s*16, 3, 14), (12, 14, 28), 'cliff_dark', (0, 0, s*.08), col=True)
        box('FacetaPilar', (s*13.5, -3.5, 9), (7, 6, 18), 'cliff', (s*.1, 0, s*.3), col=False)
        box('FacetaPilar', (s*18, -2, 22), (8, 6, 12), 'cliff', (0, s*.15, s*-.2), col=False)
        box('Escora', (s*10.2, -1.5, 8.5), (2.2, 2.2, 17), 'wood', col=True)
        rod('MaoFrancesa', (s*10.2, -1.5, 12.5), (s*6.5, -1.5, 16.4), 1.1, 'wood_dark')
    box('Lintel', (0, 3, 24.5), (44, 14, 11), 'cliff_dark', col=True)
    box('LintelFaceta', (-6, -3.6, 22.5), (20, 5, 6), 'cliff', (0, .06, .05), col=False)
    box('LintelFaceta', (9, -3.2, 26), (18, 5, 6), 'cliff', (0, -.1, -.06), col=False)
    box('VigaPortal', (0, -1.5, 17.6), (24, 2.6, 2.6), 'wood', col=True)
    box('VigaPortal2', (0, -1.2, 19.8), (21, 2, 1.6), 'wood_dark', col=False)
    box('PlacaMina', (0, -3.4, 21.2), (16, .6, 3.6), 'wood_dark', col=False, text='GRANDE MINA')
    for x in (-5.5, 5.5):
        rod('CorrentePlaca', (x, -3, 19), (x, -3.2, 23), .2, 'metal')
    box('Escuridao', (0, 14, 8.5), (20, 1, 17), 'dark_void', col=False)

# ---------------------------------------------------------------- FOUNTAIN / ARENA / PORTAL / SHRINE
def fonte_folha():
    asset(C, 'Fonte_Folha')
    cyl('Bacia', (0, 0, .9), 9.5, 1.8, 'stone', col=True)
    cyl('Agua', (0, 0, 1.75), 8.6, .2, 'water', col=False, fx='fountain')
    cyl('Base2', (0, 0, 3), 4, 3, 'stone_dark', col=True)
    cyl('Agua2', (0, 0, 4.45), 3.4, .15, 'water', col=False)
    cyl('Borda2', (0, 0, 4.3), 4.4, .4, 'stone', col=False)
    box('Coluna', (0, 0, 7.5), (2.4, 2.4, 6), 'stone', col=True)
    for r in (0, PI):
        box('Emblema', (0, 0, 13), (7, .5, 7), 'wall_cream', (0, 0, r), col=False, emblem='leaf')
    box('MolduraEmblema', (0, 0, 13), (7.8, .3, 7.8), 'gold', col=False)
    for k in range(8):
        a = k/8*2*PI
        box('Banco', (math.cos(a)*13.5, math.sin(a)*13.5, .7), (1.8, 5, 1.4), 'wood', (0, 0, a), col=False)

def arena_chefe():
    asset(C, 'Arena_Chefe')
    cyl('PisoExterno', (0, 0, .15), 18, .3, 'paving', col=False)
    cyl('PisoInterno', (0, 0, .2), 14.5, .3, 'stone', col=False)
    cyl('Anel', (0, 0, .25), 9, .3, 'cloth_red', col=False)
    cyl('Centro', (0, 0, .3), 8, .3, 'stone_dark', col=False)
    for k in range(8):
        a = (k+.5)/8*2*PI
        box('MuretaArena', (math.cos(a)*18, math.sin(a)*18, 1.2), (2, 9, 2.4), 'stone', (0, 0, a), col=True)
        box('TopoMureta', (math.cos(a)*18, math.sin(a)*18, 2.55), (2.6, 9.4, .4), 'stone_dark', (0, 0, a), col=False)
    for k in range(4):
        a = k/4*2*PI + PI/4
        x, y = math.cos(a)*21.5, math.sin(a)*21.5
        box('Braseiro', (x, y, 2.5), (1.6, 1.6, 5), 'stone_dark', col=False)
        box('BaciaFogo', (x, y, 5.3), (2.8, 2.8, .8), 'metal', col=False)
        box('Fogo', (x, y, 6.2), (1.8, 1.8, 1.4), 'cr_fire', (0, 0, .7), col=False, fx='fire', light='255,140,70,16,1')

def portal_progressao():
    """Space-time portal to the next island (Namek). Front (approach) faces -Y; ring stands in the XZ plane."""
    asset(C, 'Portal_Progressao')
    from kit_env import crystal
    # stepped circular dais
    cyl('Degrau1', (0, 0, .35), 15, .7, 'stone', col=True)
    cyl('Degrau2', (0, 0, 1.05), 12.5, .7, 'paving', col=True)
    cyl('SeloAnel', (0, -1, 1.43), 9.5, .06, 'namek_glow', col=False)
    cyl('SeloFundo', (0, -1, 1.46), 8.9, .06, 'paving', col=False)
    for k in range(8):
        a = k/8*2*PI
        box('RunaSelo', (math.cos(a)*11, -1 + math.sin(a)*11, 1.44), (1.4, 1.4, .06), 'namek_glow', (0, 0, a + PI/4), col=False)
    # ring gate: stone voussoirs, glowing inner rim and gold keystones
    R, zc, n = 9.6, 12.4, 20
    for k in range(n):
        a = k/n*2*PI
        x, z = math.sin(a)*R, zc + math.cos(a)*R
        if z < 1.6: continue
        key = k % 5 == 0
        box('Aduela', (x, 0, z), (3.2 if not key else 3.8, 3.2 if not key else 4.2, 2.6 if not key else 3.2),
            'gold' if key else 'stone_dark', (0, a, 0), col=False)
        xi, zi = math.sin(a)*(R-1.9), zc + math.cos(a)*(R-1.9)
        if zi > 1.6:
            box('AroBrilho', (xi, 0, zi), (3.1, 1.2, .5), 'namek_glow', (0, a, 0), col=False)
    cyl('Energia', (0, 0, zc), R-2.3, .35, 'namek_glow', axis='Y', col=False, fx='portal', swirl=1,
        light='120,255,170,36,1.6')
    cyl('EnergiaNucleo', (0, -.3, zc), 3.2, .4, 'cr_wind', axis='Y', col=False)
    ball('OrbeDestino', (0, -1.4, zc), 2.4, 'cr_earth')
    for (x, z) in ((-.5, .5), (.6, -.3), (-.2, -.6)):
        ball('EstrelaOrbe', (x, -2.6, zc + z), .45, 'cloth_red')
    # flanking pillars with lanterns and scroll banners
    for s in (-1, 1):
        box('BasePilar', (s*13.5, 0, 2.6), (4.6, 4.6, 3), 'stone', col=True)
        box('Pilar', (s*13.5, 0, 12.5), (3, 3, 17), 'stone_dark', col=True)
        box('CapitelPilar', (s*13.5, 0, 21.3), (4, 4, .8), 'stone', col=False)
        box('LanternaPilar', (s*13.5, 0, 22.8), (2.2, 2.2, 2.2), 'namek_glow', col=False)
        wedge('TetoLanterna', (s*13.5, -.9, 24.4), (3.2, 1.8, 1), 'stone_dark', (0, 0, 0), col=False)
        wedge('TetoLanterna', (s*13.5, .9, 24.4), (3.2, 1.8, 1), 'stone_dark', (0, 0, PI), col=False)
        box('Pergaminho', (s*13.5, -1.65, 12), (2.2, .2, 9), 'cloth_white', col=False, text='PORTAL', textcolor='40,120,70')
        box('RoloPergaminho', (s*13.5, -1.7, 16.7), (2.8, .5, .5), 'roof_red', col=False)
        # space-time kunai stuck in the dais
        kx, ky = s*9.5, -9
        box('Kunai', (kx, ky, 3), (.35, .35, 3.4), 'metal', (0, s*.25, 0), col=False)
        box('CaboKunai', (kx - s*.2, ky, 5.1), (.5, .5, 1.6), 'trim_dark', (0, s*.25, 0), col=False)
        cyl('AroKunai', (kx - s*.45, ky, 6.2), .45, .2, 'metal', axis='Y', col=False)
        for d in (-1, 1):
            box('PontaKunai', (kx + d*.5, ky, 1.9), (.25, .25, 1.3), 'metal', (0, d*.5, 0), col=False)
        crystal(s*18, -3, 0, 4.5, 1.3, 'namek_glow', (0, s*.25), .4)
        crystal(s*6, 5, 1.4, 3.2, 1.0, 'cr_wind', (.3, -s*.3), 1.1)
    # torii lintel with destination sign
    box('Kasagi', (0, 0, 26.2), (34, 3.4, 1.6), 'trim_dark', col=False)
    for s in (-1, 1):
        wedge('PontaKasagi', (s*17.9, 0, 27.4), (3.4, 1.8, 1.4), 'trim_dark', (0, 0, -s*PI/2), col=False)
    box('Nuki', (0, 0, 23.4), (29, 2, 1), 'stone', col=False)
    box('PlacaDestino', (0, -1.6, 29.4), (16, .5, 3.4), 'wood', col=False, text='PLANETA NAMEKUSEI', textcolor='150,255,190')
    box('PlacaProxima', (0, -1.3, 24.9), (10, .4, 1.8), 'wood_dark', col=False, text='PROXIMA ILHA')
    for x in (-5, 5):
        box('CorrentePlaca', (x, -1.4, 27.6), (.2, .2, 1.8), 'metal', col=False)

def torii_pequeno():
    asset(C, 'Torii_Santuario')
    for s in (-1, 1):
        cyl('Coluna', (s*4.5, 0, 5.5), .7, 11, 'roof_red', col=True)
        box('Base', (s*4.5, 0, .5), (1.8, 1.8, 1), 'trim_dark', col=False)
    box('Kasagi', (0, 0, 11.5), (13, 1.6, 1.1), 'trim_dark', col=False)
    box('Nuki', (0, 0, 9.4), (11, .9, .8), 'roof_red', col=False)
    box('Gakuzuka', (0, -.2, 10.4), (.8, .6, 1.4), 'roof_red', col=False)
    box('Oferendas', (0, 5, 1.4), (4, 2.4, 2.8), 'wood', col=True)
    box('Corda', (0, 0, 8.2), (9, .5, .5), 'rope', col=False)
    for x in (-2.5, 0, 2.5):
        box('Shide', (x, -.3, 7.3), (.6, .1, 1.6), 'cloth_white', col=False)

def _toro(x, y, z=0.0, s=1.0):
    box('BaseToro', (x, y, z+.4*s), (2.4*s, 2.4*s, .8*s), 'stone', col=False)
    cyl('HasteToro', (x, y, z+2.2*s), .55*s, 2.8*s, 'stone', col=False)
    box('LuzToro', (x, y, z+4.4*s), (1.5*s, 1.5*s, 1.6*s), 'glow', col=False)
    wedge('TetoToro', (x, y-.8*s, z+5.6*s), (2.9*s, 1.6*s, .9*s), 'stone_dark', (0, 0, 0), col=False)
    wedge('TetoToro', (x, y+.8*s, z+5.6*s), (2.9*s, 1.6*s, .9*s), 'stone_dark', (0, 0, PI), col=False)

def _sapo(x, y, z, s=1.0):
    box('Pedestal', (x, y, z+1.5*s), (7*s, 7*s, 3*s), 'stone', col=True)
    box('FrisoPedestal', (x, y, z+3.1*s), (7.6*s, 7.6*s, .4*s), 'stone_dark', col=False)
    ball('CorpoSapo', (x, y+.5*s, z+7*s), 8*s, 'face_stone')
    ball('CabecaSapo', (x, y-2*s, z+10.4*s), 5.6*s, 'face_stone')
    for sx in (-1, 1):
        ball('OlhoSapo', (x+sx*1.9*s, y-2.6*s, z+12.8*s), 2.2*s, 'face_stone')
        ball('PupilaSapo', (x+sx*1.9*s, y-3.6*s, z+13*s), .9*s, 'trim_dark')
        ball('PataSapo', (x+sx*2.6*s, y-3.4*s, z+4*s), 2.6*s, 'face_stone')
        ball('CoxaSapo', (x+sx*3.6*s, y+1.5*s, z+4.6*s), 3.6*s, 'face_shadow')
    box('BocaSapo', (x, y-4.7*s, z+9.6*s), (3.6*s, .3*s, .35*s), 'trim_dark', col=False)
    box('ColarSapo', (x, y-1.2*s, z+8*s), (6*s, 5*s, .8*s), 'cloth_red', col=False)

def santuario_invocacao():
    """Summoning sanctuary. Entrance at -Y, gacha machine on the seal centre (0,0,1.2)."""
    asset(C, 'Santuario_Invocacao')
    cyl('PlataformaBase', (0, 0, .3), 28, .6, 'stone', col=True)
    cyl('Plataforma', (0, 0, .9), 25, .6, 'paving', col=True)
    for i, w in enumerate((14, 12)):
        box('DegrauEntrada', (0, -27.8 - i*1.6, .3 - i*.15), (w, 2, .6 - i*.3), 'stone', col=True)
    # summoning seal
    cyl('SeloAnelExt', (0, 0, 1.24), 16, .08, 'cr_rare', col=False)
    cyl('SeloFundoExt', (0, 0, 1.27), 15.1, .08, 'paving', col=False)
    cyl('SeloAnelInt', (0, 0, 1.30), 9.5, .08, 'cr_rare', col=False)
    cyl('SeloFundoInt', (0, 0, 1.33), 8.7, .08, 'paving', col=False)
    for k in range(8):
        a = k/8*2*PI
        box('SeloRaio', (math.cos(a)*12.3, math.sin(a)*12.3, 1.30), (6, .45, .06), 'cr_rare', (0, 0, a), col=False)
        b = a + PI/8
        box('SeloGlifo', (math.cos(b)*12.3, math.sin(b)*12.3, 1.30), (1.6, 1.6, .06), 'cr_rare', (0, 0, b + PI/4), col=False)
    box('LuzSelo', (0, 0, 9), (.5, .5, .5), 'cr_rare', col=False, light='200,120,255,34,1.2', fx='summon')
    # giant hanging scroll at the back
    for sx in (-1, 1):
        box('PosteRolo', (sx*10, 21, 13.5), (1.2, 1.2, 27), 'wood_dark', col=True)
    box('VigaRolo', (0, 21, 27.4), (23, 1.4, 1.4), 'wood_dark', col=False)
    cyl('RoloSuperior', (0, 20.5, 24.8), 1.2, 17, 'roof_red', axis='X', col=False)
    cyl('RoloInferior', (0, 20.5, 5.2), 1.2, 17, 'roof_red', axis='X', col=False)
    box('Pergaminho', (0, 20.5, 15), (14.5, .4, 19), 'cloth_white', col=False, text='INVOCACAO', textcolor='120,40,160')
    for sx in (-1, 1):
        box('BordaPergaminho', (sx*7.5, 20.4, 15), (.8, .45, 19), 'cloth_red', col=False)
    # guardian frogs
    _sapo(-17, 14, 1.2)
    _sapo(17, 14, 1.2)
    # lanterns and crystals around the ring
    for (x, y) in ((-24, -3), (24, -3), (-9, -23), (9, -23)):
        _toro(x, y, 1.2)
    from kit_env import crystal
    for (x, y) in ((-20, -16), (20, -16), (-23, 8), (23, 8)):
        crystal(x, y, 1.2, 5.5, 1.6, 'cr_rare', (0, 0), .3)
        crystal(x + 1.4, y + .8, 1.2, 3, 1.1, 'cr_rare', (.35, -.3), 1.2)
    # entrance torii + incense burner + banners
    for sx in (-1, 1):
        cyl('ColunaTorii', (sx*12, -31, 10.5), 1.1, 21, 'roof_red', col=True)
        box('BaseTorii', (sx*12, -31, .6), (2.8, 2.8, 1.2), 'trim_dark', col=False)
    box('Kasagi', (0, -31, 21.6), (31, 2.6, 1.8), 'trim_dark', col=False)
    for sx in (-1, 1):
        wedge('PontaKasagi', (sx*16.4, -31, 22.8), (2.6, 2.4, 1.2), 'trim_dark', (0, 0, -sx*PI/2), col=False)
    box('Nuki', (0, -31, 17.6), (27, 1.4, 1.2), 'roof_red', col=False)
    box('PlacaTorii', (0, -31.9, 19.6), (9, .5, 2.8), 'trim_dark', col=False, text='INVOCACAO', textcolor='255,210,120')
    box('Incensario', (0, -18, 2.4), (3, 3, 2.4), 'metal', col=False)
    box('TampaIncensario', (0, -18, 3.9), (3.8, 3.8, .6), 'trim_dark', col=False, fx='smoke')
    for sx in (-1, 1):
        box('MastroEstandarte', (sx*19, -24, 8), (.5, .5, 14), 'wood_dark', col=False)
        box('Estandarte', (sx*19, -24.4, 10), (3.6, .15, 7), 'cr_rare' if False else 'cloth_red', col=False, emblem='leaf', sway=1)

def build_all():
    for fn in (rosto_1, rosto_2, rosto_3, rosto_4, residencia_hokage, portao_principal, grande_mina,
               fonte_folha, arena_chefe, portal_progressao, torii_pequeno, santuario_invocacao):
        fn()
