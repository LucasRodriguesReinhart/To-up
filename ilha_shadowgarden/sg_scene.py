# sg_scene - mundo NOTURNO (luar), mar, ilhotas flutuantes, nuvens, cameras de QA e referencia de escala da Ilha 3.
# O Roblox faz a noite pelo AreaAtmosphere (perfil da area sombra); aqui a previa do Blender imita: lua fria de noroeste,
# ceu navy/roxo, ambiente frio fraco, interiores e janelas quentes.
import math, random
import bpy
from mathutils import Vector
import sg_lib as SL
from sg_lib import MB, camera, dome
import sg_layout as L
import fm_scene
import il_scene
import fm_water_kit as WK

MOON_DIR = Vector((-0.45, 0.55, 0.70)).normalized()     # aponta PARA a lua (noroeste, alta: contraluz na fachada)


def setup(res=(1600, 900), samples=32):
    fm_scene.setup_render(res, samples)
    fm_scene.AMB_COLOR = (0.30, 0.36, 0.62)
    fm_scene.AMB_POWER = 0.42
    fm_scene.setup_world()
    w = bpy.context.scene.world
    for nd in w.node_tree.nodes:
        if nd.bl_idname == "ShaderNodeValToRGB":
            cr = nd.color_ramp
            cols = {0: (0.080, 0.085, 0.20, 1), 1: (0.010, 0.012, 0.045, 1)}
            els = sorted(cr.elements, key=lambda e: e.position)
            els[0].color = (0.115, 0.085, 0.26, 1)       # horizonte roxo (referencia v2)
            els[-1].color = (0.012, 0.010, 0.055, 1)     # zenite roxo-preto
            if len(els) > 2:
                els[1].color = (0.045, 0.036, 0.150, 1)
        if nd.bl_idname == "ShaderNodeBackground" and nd.inputs["Color"].is_linked:
            nd.inputs["Strength"].default_value = 0.55       # ceu visto pela camera: noite (a luz ambiente e a outra)
    fm_scene.SUN_DIR = MOON_DIR
    fm_scene.SUN_COLOR = (0.62, 0.72, 1.0)
    fm_scene.SUN_POWER = 1.6
    fm_scene.FOG.update(start=380.0, depth=1600.0, factor=0.30, color=(0.10, 0.11, 0.24))
    fm_scene.setup_sun()
    vs = bpy.context.scene.view_settings
    vs.view_transform = "Standard"
    try:
        vs.look = "None"
    except Exception:
        pass
    vs.exposure = 0.55
    ng = bpy.data.node_groups.get("CMP_Lobby")
    if ng:
        for nd in ng.nodes:
            if nd.bl_idname == "CompositorNodeGlare":
                for nm, val in (("Threshold", 0.7), ("Strength", 0.5), ("Size", 0.7)):
                    if nm in nd.inputs:
                        nd.inputs[nm].default_value = val


def tone_emissives():
    il_scene.ENERGY = tuple(il_scene.ENERGY) + ("SG_Violet_Glow", "SG_Moon_Glow", "SG_VioletDeep_Glow", "SG_Rune_Glow",
                                                "SG_Crystal_Glow", "SG_VioletSoft_Glow")
    il_scene.tone_emissives()
    import os
    if os.environ.get("SG_SEM_EMISSAO"):
        # teste do passe de acabamento: TODO brilho quase desligado (a ilha tem de funcionar so com forma e material)
        for m in bpy.data.materials:
            if m.use_nodes:
                for nd in m.node_tree.nodes:
                    if nd.bl_idname == "ShaderNodeBsdfPrincipled" and nd.inputs["Emission Strength"].default_value > 0:
                        nd.inputs["Emission Strength"].default_value = 0.03
                        bc = nd.inputs["Base Color"]
                        if not bc.is_linked:     # a cor clara do Neon tambem "brilha" sob luz: vira um tom medio
                            c = bc.default_value
                            bc.default_value = (c[0] * 0.35, c[1] * 0.35, c[2] * 0.35, 1.0)
        bpy.context.scene.render.use_compositing = False     # sem glare
        nl = 0
        for ob in bpy.data.objects:
            if ob.type == "LIGHT":
                ob.data.energy *= 0.15
                nl += 1
        print("SEM_EMISSAO: emissao quase zero em todos os materiais, %d luzes a 15%%" % nl)


def sea():
    import fm_lib
    fm_lib.MATS.setdefault("Water_SG_Sea", (fm_lib.S(16, 20, 44), 0.2, 0.0, 0, None, 0.0))
    # so o material do mar: make_materials() reconstruia TODOS e desfazia o tone_emissives (brilhos estourados na previa)
    if "Water_SG_Sea" not in bpy.data.materials:
        fm_lib.mat("Water_SG_Sea")
    mb = MB("SG_Sky_Sea", "02_TERRAIN", random.Random(3), detail="far", floor=-999)
    mb.box((4200.0, 4200.0, 1.0), (0, 0, L.SEA - 0.5), (0, 0, 0), "Water_SG_Sea", 0.0)
    mb.finish()


# ACABAMENTO 2 (2026-09-30, pedido do usuario: "tire tambem essas ilhas em volta de todos os mapas"): as ilhotas
# flutuantes decorativas NAO sao mais construidas nem exportadas. Codigo mantido; para voltar: ISLETS = True
# (ou SG_ISLETS=1 no ambiente).
import os as _os
ISLETS = _os.environ.get("SG_ISLETS", "0") == "1"

# a Ilha 2 fica ao SUL/SUDESTE no referencial desta ilha: nada de ilhota no setor 240..300 graus (a ponte de chegada)
# refinamento v2: +4 ilhotas pequenas ao fundo (norte/leste/oeste) para adensar o ceu, longe das pontes
ISLET_SPOTS = [(-300.0, 60.0, 52.0, 20.0), (-260.0, 260.0, 80.0, 16.0), (40.0, 360.0, 64.0, 22.0),
               (300.0, 200.0, 90.0, 14.0), (340.0, 40.0, 30.0, 18.0), (-340.0, -140.0, 40.0, 14.0),
               (200.0, 380.0, 110.0, 12.0), (-150.0, 400.0, 34.0, 18.0), (380.0, -170.0, 60.0, 12.0),
               (-430.0, 40.0, 46.0, 10.0), (150.0, 470.0, 96.0, 11.0), (440.0, 250.0, 72.0, 9.0),
               (-300.0, 390.0, 58.0, 10.0)]


def _loft(mb, rings, apex, mats, top_m=None):
    """solido de aneis [(pontos xy, z)] com o mesmo numero de pontos, fechado no topo (top_m) e numa ponta (apex);
    mats = material de cada faixa entre aneis (a ponta usa o ultimo)"""
    import bmesh
    bm = mb.bm
    vr = [[bm.verts.new((x, y, z)) for x, y in pts] for pts, z in rings]
    n = len(vr[0])
    groups = {}
    top = bm.faces.new(vr[0]) if top_m else None
    for (r0, r1), mm in zip(zip(vr, vr[1:]), mats):
        for k in range(n):
            groups.setdefault(mm, []).append(bm.faces.new((r0[(k + 1) % n], r0[k], r1[k], r1[(k + 1) % n])))
    av = bm.verts.new(apex)
    for k in range(n):
        groups.setdefault(mats[-1], []).append(bm.faces.new((vr[-1][(k + 1) % n], vr[-1][k], av)))
    allf = [f for fs in groups.values() for f in fs] + ([top] if top else [])
    bmesh.ops.recalc_face_normals(bm, faces=allf)
    mb._post([v for r in vr for v in r] + [av], mats[0], None, 0, 1)
    for mm, fs in groups.items():
        mi = mb._mi_for(mm)
        for f in fs:
            f.material_index = mi
    if top:
        top.material_index = mb._mi_for(top_m)


def islets():
    """ilhotas flutuantes (13.04): fragmentos de Shadow Garden - rocha em 3 ESTRATOS (a familia do penhasco e da
    dungeon: faixa canelada, degrau ao luar, faixa escura) fechando numa ponta com o cristal-coracao embaixo,
    pinheiros do kit da vegetacao em LOD2 (sg_veg.pine, 1 a 3 conforme o tamanho) e, em metade delas, a cachoeira do
    13.02 em miniatura (lamina em arco + faixa clara). Contorno com lobos DIRIGIDOS (senoides), sem sorteio de forma.
    Antes: 4 icosferas empilhadas + pinheiro de 3 cones + cachoeira em caixa + 4-5 cristais soltos. Sem colisao.
    DESLIGADO (acabamento 2): so constroi com ISLETS = True."""
    if not ISLETS:
        return None
    import sg_veg as VG
    import fm_veg_kit as VK
    mb = MB("SG_Sky_Islets", "02_TERRAIN", random.Random(3909), detail="far", floor=-999)
    old_sun = VK.SUN
    VK.SUN = VG.MOON_DIR
    ROCK, DARK, TOPM = "Cliff_Rock_SG", "Cliff_Rock_SG_Dark", "Cliff_Rock_SG_Top"
    try:
        for idx, (x, y, z, r) in enumerate(ISLET_SPOTS):
            ph = idx * 1.7
            n = 8

            def outline(sc, amp=1.0, fl=0.0):
                pts = []
                for k in range(n):
                    a = 2 * math.pi * k / n + ph
                    kk = 1.0 + amp * (0.14 * math.sin(3 * a + ph) + 0.06 * math.sin(5 * a))
                    rr = r * sc * kk + (fl if k % 2 == 0 else -fl)
                    pts.append((x + rr * math.cos(a), y + rr * math.sin(a)))
                return pts
            rings = [(outline(1.0, fl=0.4), z), (outline(0.93, fl=0.4), z - 0.45 * r),
                     (outline(0.80), z - 0.45 * r), (outline(0.66, fl=0.3), z - 1.0 * r),
                     (outline(0.52), z - 1.0 * r), (outline(0.30, 0.6), z - 1.45 * r)]
            _loft(mb, rings, (x, y, z - 1.85 * r), [ROCK, TOPM, ROCK, TOPM, DARK], top_m="Grass_SG")
            # cristal-coracao na ponta (o unico cristal da ilhota)
            ax = Vector((0.12 * math.cos(ph), 0.12 * math.sin(ph), -1.0)).normalized()
            b = Vector((x, y, z - 1.7 * r))
            yaw, pitch = math.atan2(ax.y, ax.x), math.acos(max(-1.0, min(1.0, ax.z)))
            ln, cr = r * 0.95, r * 0.18
            mb.cyl(cr, ln * 0.7, b + ax * (ln * 0.35), (0.0, pitch, yaw), m="SG_Crystal_Glow", n=6, r2=cr * 0.8,
                   bevel=0.0)
            mb.cyl(cr * 0.8, ln * 0.3, b + ax * (ln * 0.85), (0.0, pitch, yaw), m="SG_Crystal_Glow", n=6, r2=0.03,
                   bevel=0.0)
            # pinheiros LOD2 do kit: 1 (pequena), 2 (media), 3 (grande); o mais alto no miolo, dirigidos
            nt = 1 if r < 13 else (2 if r < 18 else 3)
            g = random.Random(4100 + idx)
            for j in range(nt):
                a = ph + 2.1 * j
                d = 0.0 if j == 0 else r * 0.42
                h = r * (0.85 if j == 0 else 0.6)
                VG.pine(mb, x + d * math.cos(a), y + d * math.sin(a), z, h, g, "fir" if j != 1 else "spire",
                        lod=2)
            # metade verte a cachoeira do 13.02 em miniatura: lamina em arco (corpo) + uma faixa clara
            if idx % 2 == 0:
                a = ph + 3.6
                ox, oy = math.cos(a), math.sin(a)
                ex, ey = x + ox * r * 0.9, y + oy * r * 0.9
                drop = 26.0 + r
                w = 1.4 + r * 0.06
                side = (-oy, ox, 0.0)
                pts = [(ex - ox * 0.8, ey - oy * 0.8, z + 0.05), (ex + ox * 0.6, ey + oy * 0.6, z - 0.3),
                       (ex + ox * 1.4, ey + oy * 1.4, z - drop * 0.3), (ex + ox * 1.9, ey + oy * 1.9, z - drop)]
                WK.ribbon(mb, pts, [w, w * 1.05, w * 0.9, w * 0.3], "Water_SG", side, thick=0.3, bulge=0.25)
                pts2 = [(px + ox * 0.14, py + oy * 0.14, pz - 0.02) for px, py, pz in pts[1:]]
                WK.ribbon(mb, pts2, [w * 0.35, w * 0.38, w * 0.12], "Water_Fall", side, thick=0.1, flat=True)
    finally:
        VK.SUN = old_sun
    mb.finish()


def _slab(mb, c, r, h, m, n=12, ph=0.0, sx=1.0):
    """disco de nuvem MUITO achatado (lente): borda fina, topo levemente abaulado, fundo quase plano; contorno com
    lobos dirigidos (senoides)"""
    x, y, z = c
    rings = []
    for f, dz in ((0.72, h * 0.55), (1.0, 0.0), (0.78, -h * 0.35)):
        pts = []
        for k in range(n):
            a = 2 * math.pi * k / n
            kk = 1.0 + 0.1 * math.sin(3 * a + ph) + 0.05 * math.sin(5 * a + ph * 2)
            pts.append((x + r * f * kk * sx * math.cos(a), y + r * f * kk * math.sin(a)))
        rings.append((pts, z + dz))
    _loft(mb, rings, (x, y, z - h * 0.45), [m, m], top_m=m)


def clouds():
    """mar de nuvens (13.03): CAMADAS horizontais de discos muito achatados sobrepostos - em cada banco, o disco de
    baixo largo e escuro, o do meio no tom base, o de cima menor e mais claro (luar por cima); 2 camadas de altura
    (a de perto da borda mais alta). Tamanhos e posicoes em ritmo dirigido ao redor da ilha. Previa: nao exporta.
    (2 discos por banco: o de baixo largo e escuro, o de cima menor e claro, deslocado)"""
    import fm_lib
    fm_lib.MATS.setdefault("Cloud_SGLight", (fm_lib.S(132, 122, 196), 0.9, 0.0, 0.22, fm_lib.S(150, 136, 220), 0.0))
    fm_lib.MATS.setdefault("Cloud_SGShade", (fm_lib.S(64, 56, 112), 0.9, 0.0, 0.12, fm_lib.S(80, 70, 140), 0.0))
    for nm in ("Cloud_SGLight", "Cloud_SGShade"):
        if nm not in bpy.data.materials:
            fm_lib.mat(nm)
    mb = MB("SG_Sky_Clouds", "02_TERRAIN", random.Random(1313), detail="far", floor=-999)
    NB = 22
    for i in range(NB):
        a = math.radians(i * 360.0 / NB + 7.0 * math.sin(i * 1.3))
        near = i % 3 != 2
        R = SL.ray_poly(L.ISLAND_RIM, math.degrees(a), 0.0, -20.0) + (8.0 if near else 30.0) + 6.0 * math.sin(i * 2.1)
        cx, cy = math.cos(a) * R, -20.0 + math.sin(a) * R
        zc = (-46.0 if near else -60.0) + 4.0 * math.sin(i * 0.9)
        rr = 30.0 + 8.0 * math.sin(i * 1.7 + 0.5)
        ang = a + math.pi / 2
        ux, uy = math.cos(ang), math.sin(ang)
        # banco: largo/escuro embaixo, base no meio (deslocado ao longo da borda), claro e menor em cima
        _slab(mb, (cx, cy, zc - 2.6), rr * 1.1, 3.2, "Cloud_SGShade", n=10, ph=i * 0.7)
        _slab(mb, (cx - ux * rr * 0.22, cy - uy * rr * 0.22, zc + 1.2), rr * 0.68, 3.4, "Cloud_SGLight", n=10,
              ph=i * 0.7 + 2.3)
    mb.finish()


def moon():
    """SO previa (o Roblox usa a lua do Sky): LUA ENORME no noroeste (referencia v2: ela ocupa o fundo do castelo)
    + estrelas espalhadas. Colecao 00_REFERENCE: fora do export."""
    rng = random.Random(5)
    mb = MB("PREVIEW_Moon", "00_REFERENCE", rng, detail="far", floor=-999)
    d = MOON_DIR
    c = Vector((d.x, d.y, 0.0)).normalized() * 1500.0
    mb.ico(220.0, (c.x, c.y, 640.0), "SG_MoonDisc_Glow", 3, jitter=0.03)
    for i in range(90):
        a = rng.uniform(0, 2 * math.pi)
        r = rng.uniform(700.0, 1700.0)
        z = rng.uniform(180.0, 900.0)
        if (Vector((math.cos(a), math.sin(a), 0)) - Vector((d.x, d.y, 0)).normalized()).length < 0.35 and z > 400:
            continue                                    # nao cobre a lua
        mb.ico(rng.uniform(1.6, 4.2), (math.cos(a) * r, math.sin(a) * r, z), "SG_Moon_Glow", 1)
    mb.finish()


P1, P2, P3, SUM, H = L.P1, L.P2, L.P3, L.SUM, L.HALL
# v4 (ONDA 0, plano mestre): cameras refeitas para a planta nova (castelo 2x, salao sombrio, salas 3x, vila visitavel)
_CZ = L.CHANCEL_Z
_CX, _CY = L.CRAFT_C
_SX, _SY = L.SUMMON_TOWER
CAMS = {
    # visoes pedidas (secao de QA da missao)
    "CAM_SG_Entry": ((0.0, -358.0, L.DECK + 12.0), (0.0, -222.0, P1 + 16.0), 20),
    "CAM_SG_Front": ((30.0, -820.0, 300.0), (0.0, 0.0, 90.0), 24),
    "CAM_SG_Left": ((-760.0, 20.0, 260.0), (0.0, 20.0, 90.0), 24),
    "CAM_SG_Right": ((780.0, 0.0, 260.0), (0.0, 20.0, 90.0), 24),
    "CAM_SG_Back": ((0.0, 1000.0, 360.0), (0.0, 40.0, 110.0), 24),
    "CAM_SG_BirdEye": ((-80.0, -110.0, 1150.0), (0.0, -110.0, 0.0), 24),
    "CAM_SG_World": ((520.0, -380.0, 820.0), (-90.0, -560.0, 0.0), 24),
    "CAM_SG_Castle": ((0.0, -128.0, P2 + 14.0), (0.0, 150.0, P3 + 100.0), 18),
    "CAM_SG_MiningHall": ((0.0, 72.0, H + 9.0), (0.0, 220.0, H + 26.0), 16),
    "CAM_SG_Throne": ((-15.0, 270.0, _CZ + 7.0), (0.0, 302.0, _CZ + 9.0), 20),
    "CAM_SG_ThroneWide": ((0.0, 230.0, H + 10.0), (0.0, 300.0, _CZ + 12.0), 18),
    "CAM_SG_Spiral": ((0.0, 309.5, _CZ + 15.0), (1.0, 326.0, L.SPIRAL_BOT_Z + 8.0), 14),
    "CAM_SG_SpiralCave": ((46.0, 262.0, L.CAVE_GALLERY_Z + 8.0), (0.0, 322.0, 20.0), 18),
    "CAM_SG_Cave": ((0.0, 298.0, L.CAVE_GALLERY_Z + 7.0), (0.0, 120.0, L.CAVE_FLOOR + 6.0), 14),
    "CAM_SG_CavePortal": ((12.0, 160.0, L.CAVE_FLOOR + 6.0), (0.0, 100.0, L.CAVE_FLOOR + 14.0), 18),
    "CAM_SG_Summon": ((_SX + 60.0, _SY + 16.0, P1 + 12.0), (_SX, _SY, SUM + 14.0), 18),
    "CAM_SG_Craft": ((_CX - 46.0, _CY + 22.0, P2 + 14.0), (_CX, _CY, P2 + 22.0), 16),
    "CAM_SG_CraftInterior": ((_CX - 8.5, _CY, P2 + 5.2), (_CX + 8.0, _CY, P2 + 4.0), 14),
    "CAM_SG_Dungeon": ((0.0, 190.0, L.CAVE_FLOOR + 12.0), (0.0, 100.0, L.CAVE_FLOOR + 10.0), 18),
    "CAM_SG_DungeonInterior": ((0.0, 130.0, L.CAVE_FLOOR + 5.2), (0.0, 100.0, L.CAVE_FLOOR + 10.0), 18),
    "CAM_SG_DungeonRooms": ((0.0, 98.0, L.DUN_Z + 9.0), (0.0, 197.0, L.DUN_Z + 9.0), 16),
    "CAM_SG_Village": ((0.0, -196.0, P1 + 16.0), (-92.0, -262.0, P1 + 8.0), 18),
    "CAM_SG_ExitGate": None,          # calculada (frente do portao DS, na ponte de saida)
    # altura do jogador (olho ~5,2 acima do piso)
    "CAM_SG_PlayerHeight_Entry": ((0.0, -328.0, L.DECK + 5.2), (0.0, -250.0, P1 + 6.0), 22),
    "CAM_SG_PlayerHeight_Plaza": ((0.0, -254.0, P1 + 5.2), (0.0, -150.0, P2 + 14.0), 22),
    "CAM_SG_PlayerHeight_Village": ((-30.0, -86.0, P2 + 5.2), (-100.0, -86.0, P2 + 6.0), 22),
    "CAM_SG_PlayerHeight_Castle": ((0.0, 8.0, P3 + 5.2), (0.0, 61.0, P3 + 28.0), 20),
    "CAM_SG_PlayerHeight_MiningHall": ((0.0, 70.0, H + 5.2), (0.0, 200.0, H + 3.0), 20),
    "CAM_SG_PlayerHeight_Summon": ((_SX + 30.0, _SY, SUM + 5.2), (_SX, _SY, SUM + 10.0), 22),
    "CAM_SG_PlayerHeight_Craft": ((_CX - 26.0, _CY + 6.0, P2 + 5.2), (_CX, _CY, P2 + 5.0), 22),
    "CAM_SG_PlayerHeight_Dungeon": ((0.0, 132.0, L.CAVE_FLOOR + 5.2), (0.0, 100.0, L.CAVE_FLOOR + 9.0), 22),
    "CAM_SG_PlayerHeight_DungeonRoom": ((10.0, 222.0, L.DUN_Z + 5.2), (0.0, 303.0, L.DUN_Z + 10.0), 18),
    "CAM_SG_PlayerHeight_House": ((-100.0, -206.0, P1 + 5.2), (-100.0, -176.0, P1 + 5.0), 20),
    "CAM_SG_PlayerHeight_ExitGate": None,
    # cameras gerais de comparacao
    "CAM_SG_Ref_Main": ((120.0, -760.0, 420.0), (0.0, 0.0, 60.0), 26),
    "CAM_SG_Ref_Top": ((0.0, -60.0, 1400.0), (0.0, -59.0, 0.0), 26),
    "CAM_SG_Ref_Front": ((0.0, -640.0, 150.0), (0.0, 40.0, 90.0), 24),
    "CAM_SG_Ref_Side": ((-700.0, -200.0, 220.0), (0.0, 40.0, 70.0), 24),
    "CAM_SG_Ref_Castle": ((0.0, -40.0, P2 + 24.0), (0.0, 160.0, P3 + 110.0), 20),
    "CAM_SG_Ref_Village": ((40.0, -270.0, P1 + 10.0), (-60.0, -150.0, P2 + 8.0), 20),
}


def neighbors():
    """SO previa (00_REFERENCE, fora do export): silhuetas da Ilha 2 (com a ponte e a ilhota da ancora), da Ilha 1 e dos
    picos/montanhas do lobby, levadas para o referencial local desta ilha - para as vistas do mundo mostrarem a FOLGA"""
    import importlib, fm_lib
    fm_lib.MATS.setdefault("PREVIEW_Neighbor", (fm_lib.S(120, 110, 90), 0.9, 0.0, 0, None, 0.0))
    fm_lib.MATS.setdefault("PREVIEW_Lobby", (fm_lib.S(90, 96, 104), 0.9, 0.0, 0, None, 0.0))
    for nm in ("PREVIEW_Neighbor", "PREVIEW_Lobby"):
        if nm not in bpy.data.materials:
            fm_lib.mat(nm)
    mb = MB("PREVIEW_Neighbors", "00_REFERENCE", random.Random(9), detail="far", floor=-999)
    try:
        DB = importlib.import_module("db_layout")
        loc = lambda p: L.local_of_world(*DB.to_world_xy(*p))
        rim = [loc(p) for p in DB.ISLAND_RIM]
        mb.prism(SL.ccw(rim), -40.0, 24.0, "PREVIEW_Neighbor")
        ex = [loc(DB.exit_point(d)) for d in (0.0, DB.EXIT_BRIDGE_LEN)]
        mb.prism(SL.ribbon_poly(ex, 9.0), L.DECK - 2.0, L.DECK, "PREVIEW_Neighbor")
        ic = loc(DB.islet_center())
        mb.cyl(DB.GATE_ISLET_R, 4.0, (ic[0], ic[1], L.DECK - 2.0), m="PREVIEW_Neighbor", n=24, bevel=0.0)
    except Exception as ex:
        print("AVISO neighbors: Ilha 2 fora da previa (%s)" % ex)
    try:
        IL = importlib.import_module("il_layout")
        rim = [L.local_of_world(-x, -(420.0 + y)) for x, y in IL.ISLAND_RIM]
        mb.prism(SL.ccw(rim), -40.0, 16.0, "PREVIEW_Neighbor")
    except Exception as ex:
        print("AVISO neighbors: Ilha 1 fora da previa (%s)" % ex)
    # lobby: montanhas proximas (bloco) e a bbox dos picos do fundo (moldura baixa)
    rb = lambda x, z: L.local_of_world(x, -z)
    mont = [rb(-225.0, -208.0), rb(245.0, -208.0), rb(245.0, 182.0), rb(-225.0, 182.0)]
    mb.prism(SL.ccw(mont), -70.0, 60.0, "PREVIEW_Lobby")
    pk = [rb(-650.0, -710.0), rb(660.0, -710.0), rb(660.0, 408.0), rb(-650.0, 408.0)]
    for a, b in zip(pk, pk[1:] + pk[:1]):
        mb.prism(SL.ribbon_poly([a, b], 3.0), -70.0, 20.0, "PREVIEW_Lobby")
    mb.finish()


def cameras():
    for n, v in CAMS.items():
        if v is None:
            continue
        loc, tgt, lens = v
        camera(n, loc, tgt, lens)
    gp = L.gate_ds_pos()
    ux, uy = L.exit_dir()
    z = L.EXIT_Z
    camera("CAM_SG_ExitGate", (gp[0] - ux * 38.0 - uy * 9.0, gp[1] - uy * 38.0 + ux * 9.0, z + 11.0),
           (gp[0], gp[1], z + 16.0), 18)
    camera("CAM_SG_PlayerHeight_ExitGate", (gp[0] - ux * 40.0 - uy * 5.0, gp[1] - uy * 40.0 + ux * 5.0, z + 5.2),
           (gp[0], gp[1], z + 9.0), 24)
    bpy.context.scene.camera = bpy.data.objects["CAM_SG_Ref_Main"]


def scale_reference(visible=True):
    gp = L.gate_ds_pos()
    ux, uy = L.exit_dir()
    spots = [("SCALE_Dummy_Entry", 3.0, -272.0, P1), ("SCALE_Dummy_Plaza", 10.0, -196.0, P1),
             ("SCALE_Dummy_Village", -40.0, -86.0, P2), ("SCALE_Dummy_Castle", 6.0, 40.0, P3),
             ("SCALE_Dummy_Door", -6.0, 58.0, P3), ("SCALE_Dummy_House", -96.0, -196.0, P1),
             ("SCALE_Dummy_Hall", 6.0, 90.0, H), ("SCALE_Dummy_Throne", -8.0, 284.0, L.CHANCEL_Z),
             ("SCALE_Dummy_Spiral", L.stair_point(60.0)[0], L.stair_point(60.0)[1], L.stair_z(60.0)), ("SCALE_Dummy_Gallery", -4.0, 284.0, L.CAVE_GALLERY_Z),
             ("SCALE_Dummy_Summon", L.SUMMON_C[0] + 10.0, L.SUMMON_C[1], SUM + 0.05),
             ("SCALE_Dummy_Craft", L.CRAFT_C[0] - 20.0, L.CRAFT_C[1], P2), ("SCALE_Dummy_Dungeon", 4.0, 130.0, L.CAVE_FLOOR),
             ("SCALE_Dummy_DunRoom", 4.0, 110.0, L.DUN_Z),
             ("SCALE_Dummy_DSGate", gp[0] - ux * 9.0 - uy * 4.0, gp[1] - uy * 9.0 + ux * 4.0, L.EXIT_Z)]
    for n, x, y, z in spots:
        SL.dummy(n, x, y, z, visible=visible)


# ------------------------------------------------------------------ AUDITORIA 3 (2026-10-01): cameras do passe de finesse
# Acrescimo (so cameras, nada de geometria): olho do jogador a ~5,5 acima do piso (avatar ~5), em todos os lugares por
# onde ele anda, mais vistas medias e de longe. Prefixo CAM_A3_<setor>_<lugar>. As que tem "_Open" no nome pedem o trono
# recolhido no bolso (o script de render desloca SG_Hall_ThroneMov* de THRONE_REST para THRONE_PARK so para elas).
# Nao entram no build (cameras() nao chama): crie com cameras_a3() num .blend montado.
EYE = 5.5


def _bridge_at(s, v=0.0):
    """ponto da ponte de chegada a 's' studs da ancora (L.BRIDGE_PATH) com afastamento lateral 'v' (+v = esquerda de
    quem chega); devolve (x, y, tx, ty)"""
    pts = L.BRIDGE_PATH
    acc = 0.0
    n = len(pts)
    for i in range(n - 1):
        a, b = pts[i], pts[i + 1]
        ln = math.hypot(b[0] - a[0], b[1] - a[1]) or 1e-9
        if acc + ln >= s or i == n - 2:
            t = max(0.0, min(1.0, (s - acc) / ln))
            tx, ty = (b[0] - a[0]) / ln, (b[1] - a[1]) / ln
            x, y = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
            return (x - ty * v, y + tx * v, tx, ty)
        acc += ln


def _bcam(s0, v0, z0, s1, v1, z1, lens):
    a, b = _bridge_at(s0, v0), _bridge_at(s1, v1)
    return ((a[0], a[1], z0), (b[0], b[1], z1), lens)


def _house_cams():
    """por casa (referencial do lote: +v = frente, porta no meio da frente; piso interno 0,30 acima da cota da casa):
    exterior de frente em 3/4 e de lado; porta de fora; sala/taverna; escada e quarto/mezanino (2 andares) ou oficina e
    forro (terrea)"""
    out = {}
    for nm, tp, x, y, w, d, deg, z in L.HOUSES:
        a = math.radians(deg) - math.pi / 2

        def P(u, v, h, x=x, y=y, z=z, a=a):
            return (x + u * math.cos(a) - v * math.sin(a), y + u * math.sin(a) + v * math.cos(a), z + h)
        iw, idp = w - 2.0, d - 2.0
        T = L.HOUSE_TYPES[tp]
        zf = T["h0"] + 1.0
        e = 0.3 + EYE
        k = "CAM_A3_04_%s_" % nm
        out["CAM_A3_03_%s_Frente" % nm] = (P(w * 0.45, d / 2 + 20.0, EYE), P(-2.0, 0.0, 9.0), 20)
        out["CAM_A3_03_%s_Lado" % nm] = (P(-w / 2 - 16.0, d / 2 + 8.0, EYE), P(0.0, -2.0, 8.0), 20)
        out[k + "Porta"] = (P(1.5, d / 2 + 9.0, EYE), P(0.0, 0.0, 5.0), 22)
        if tp == "B":
            out[k + "Taverna"] = (P(iw / 2 - 4.0, idp / 2 - 3.0, e), P(-iw / 2 + 2.0, 0.0, 6.0), 16)
            out[k + "Escada"] = (P(iw / 2 - 6.0, -1.0, e), P(-iw / 2 + 6.0, -idp / 2 + 3.0, 10.0), 16)
            out[k + "Mezanino"] = (P(iw / 2 - 5.0, idp / 2 - 6.0, zf + e), P(-iw / 2 + 6.0, 2.0, zf - 3.0), 16)
            out[k + "Quarto"] = (P(-iw / 2 + 4.0, -idp / 2 + 9.0, zf + e), P(iw / 2 - 3.0, idp / 2 - 4.0, zf + 2.0), 16)
        elif tp == "A":
            out[k + "Sala"] = (P(iw / 2 - 7.0, idp / 2 - 3.0, e), P(-iw / 2, 1.0, 4.5), 16)
            out[k + "Escada"] = (P(iw / 2 - 5.0, -1.0, e), P(-iw / 2 + 5.0, -idp / 2 + 3.0, 9.0), 16)
            out[k + "Quarto"] = (P(-iw / 2 + 5.0, 2.0, zf + e), P(iw / 2 - 2.7, idp / 2 - 4.6, zf + 1.5), 16)
        else:
            out[k + "Sala"] = (P(iw / 2 - 3.0, idp / 2 - 2.5, e), P(-iw / 2, 1.0, 4.5), 16)
            out[k + "Oficina"] = (P(-iw / 2 + 4.0, idp / 2 - 2.5, e), P(iw / 2 - 3.0, -idp / 2 + 2.0, 3.0), 16)
            out[k + "Forro"] = (P(0.0, idp / 2 - 2.0, e), P(0.0, -3.0, T["h0"] + 6.0), 15)
    return out


def _spiral_cam(a0, a1, dz1=4.0, lens=15):
    x0, y0 = L.stair_point(a0)
    x1, y1 = L.stair_point(a1)
    return ((x0, y0, L.stair_z(a0) + EYE), (x1, y1, L.stair_z(a1) + dz1), lens)


def _exit_cam(d0, v0, z0, d1, v1, z1, lens):
    ux, uy = L.exit_dir()
    a = L.exit_point(d0)
    b = L.exit_point(d1)
    return ((a[0] - uy * v0, a[1] + ux * v0, z0), (b[0] - uy * v1, b[1] + ux * v1, z1), lens)


def a3_cams():
    E = EYE
    D, Z1, Z2, Z3, ZS = L.DECK, P1, P2, P3, SUM
    CZ, GZ, FZ, DZ = L.CHANCEL_Z, L.CAVE_GALLERY_Z, L.CAVE_FLOOR, L.DUN_Z
    cx, cy = L.CRAFT_C
    tx, ty = L.SUMMON_TOWER
    SL_ = L.BRIDGE_LEN
    c = {
        # 01 ponte de chegada, encontro, patio baixo, porticos e escadaria
        "CAM_A3_01_Ponte_Ancora": _bcam(4.0, 0.0, D + E, 60.0, 0.0, D + 4.0, 20),
        "CAM_A3_01_Ponte_Curva": _bcam(62.0, -3.0, D + E, 120.0, 2.0, D + 5.0, 20),
        "CAM_A3_01_Ponte_Reta": _bcam(140.0, 0.0, D + E, SL_, 0.0, D + 22.0, 20),
        "CAM_A3_01_Ponte_Parapeito": _bcam(124.0, -4.0, D + E, 130.0, 8.6, D + 1.4, 22),
        "CAM_A3_01_Ponte_Lajes": _bcam(176.0, 3.0, D + E, 184.0, -2.0, D, 22),
        "CAM_A3_01_Ponte_Lado": _bcam(150.0, -90.0, D + 12.0, 150.0, 0.0, D - 14.0, 22),
        "CAM_A3_01_Ponte_Encontro": _bcam(196.0, -42.0, D - 2.0, SL_ - 4.0, 0.0, D - 10.0, 20),
        "CAM_A3_01_PatioBaixo": ((8.0, -331.0, D + E), (0.0, -296.0, Z1 + 10.0), 20),
        "CAM_A3_01_PorticoA_CU": ((-4.0, -328.0, D + E), (-12.0, -322.0, D + 7.0), 20),
        "CAM_A3_01_Escada": ((6.0, -315.0, D + E), (0.0, -294.0, Z1 + 4.0), 20),
        "CAM_A3_01_PorticoB": ((5.0, -291.0, Z1 + E), (0.0, -276.0, Z1 + 14.0), 18),
        "CAM_A3_01_Spawn_Volta": ((0.0, -270.0, Z1 + E), (0.0, -340.0, D + 2.0), 20),
        # 02 praca e fonte
        "CAM_A3_02_Praca_Chegada": ((0.0, -262.0, Z1 + E), (0.0, -222.0, Z1 + 6.0), 20),
        "CAM_A3_02_Fonte_CU": ((10.0, -237.0, Z1 + E), (0.0, -222.0, Z1 + 5.0), 20),
        "CAM_A3_02_Praca_Piso": ((-17.0, -210.0, Z1 + E), (-2.0, -232.0, Z1), 22),
        "CAM_A3_02_Praca_Norte": ((-4.0, -200.0, Z1 + E), (0.0, -260.0, Z1 + 6.0), 20),
        "CAM_A3_02_Praca_Alta": ((44.0, -284.0, Z1 + 42.0), (0.0, -222.0, Z1), 22),
        # 03 vila: ruas P1/P2, eixo, escada P1P2, arrimo, gramados, vista media (as casas por fora: _house_cams)
        "CAM_A3_03_RuaP1_W": ((-30.0, -222.0, Z1 + E), (-150.0, -222.0, Z1 + 8.0), 20),
        "CAM_A3_03_RuaP1_E": ((30.0, -222.0, Z1 + E), (150.0, -222.0, Z1 + 8.0), 20),
        "CAM_A3_03_RuaP1_W_Volta": ((-150.0, -221.0, Z1 + E), (-50.0, -222.0, Z1 + 10.0), 20),
        "CAM_A3_03_RuaP2_W": ((-10.0, -86.0, Z2 + E), (-160.0, -86.0, Z2 + 8.0), 20),
        "CAM_A3_03_RuaP2_E": ((10.0, -86.0, Z2 + E), (96.0, -86.0, Z2 + 10.0), 20),
        "CAM_A3_03_RuaP2_W_Volta": ((-160.0, -85.0, Z2 + E), (-40.0, -86.0, Z2 + 10.0), 20),
        "CAM_A3_03_EixoP2": ((0.0, -140.0, Z2 + E), (0.0, -40.0, Z3 + 20.0), 20),
        "CAM_A3_03_EscP1P2_Pe": ((6.0, -184.0, Z1 + E), (0.0, -150.0, Z2 + 6.0), 20),
        "CAM_A3_03_EscP1P2_Topo": ((-4.0, -145.0, Z2 + E), (0.0, -200.0, Z1 + 4.0), 20),
        "CAM_A3_03_Arrimo_W": ((-62.0, -162.0, Z1 + E), (-20.0, -149.0, Z1 + 5.0), 20),
        "CAM_A3_03_Arrimo_E": ((62.0, -162.0, Z1 + E), (20.0, -149.0, Z1 + 5.0), 20),
        "CAM_A3_03_Arrimo_Frente": ((-30.0, -200.0, Z1 + E), (-40.0, -148.0, Z1 + 6.0), 20),
        "CAM_A3_03_Gramado_P2": ((30.0, -62.0, Z2 + E), (96.0, -126.0, Z2), 22),
        "CAM_A3_03_Gramado_P1": ((40.0, -200.0, Z1 + E), (140.0, -250.0, Z1), 22),
        "CAM_A3_03_Vila_Media": ((70.0, -310.0, Z1 + 55.0), (-30.0, -170.0, Z1), 20),
        "CAM_A3_03_VilaAlta_Media": ((60.0, -150.0, Z2 + 45.0), (-70.0, -80.0, Z2), 20),
        # 05 muralha, portao, patio-jardim
        "CAM_A3_05_Muralha_P2": ((-44.0, -62.0, Z2 + E), (-14.0, -18.0, Z2 + 18.0), 20),
        "CAM_A3_05_Portao_Fora": ((6.0, -54.0, Z2 + E), (0.0, -18.0, Z3 + 14.0), 20),
        "CAM_A3_05_Portao_Vao": ((3.0, -19.0, Z3 + E), (0.0, 24.0, Z3 + 8.0), 20),
        "CAM_A3_05_Patio_Eixo": ((0.0, -6.0, Z3 + E), (0.0, 61.0, Z3 + 20.0), 18),
        "CAM_A3_05_Patio_Caminho": ((3.0, 2.0, Z3 + E), (0.0, 30.0, Z3), 22),
        "CAM_A3_05_Patio_W": ((-18.0, 8.0, Z3 + E), (-92.0, 30.0, Z3 + 4.0), 20),
        "CAM_A3_05_Patio_E": ((18.0, 8.0, Z3 + E), (92.0, 30.0, Z3 + 4.0), 20),
        "CAM_A3_05_Patio_Volta": ((0.0, 50.0, Z3 + E), (0.0, -20.0, Z3 + 12.0), 20),
        "CAM_A3_05_Muralha_Dentro": ((-60.0, 4.0, Z3 + E), (-62.0, -23.0, Z3 + 14.0), 20),
        "CAM_A3_05_Passagem_Leste": ((150.0, -52.0, Z2 + E), (150.0, -10.0, Z3 + 8.0), 20),
        "CAM_A3_05_Patio_Alto": ((0.0, -76.0, Z3 + 72.0), (0.0, 25.0, Z3), 20),
        # 06 castelo por fora
        "CAM_A3_06_Fachada_Patio": ((22.0, 8.0, Z3 + E), (0.0, 61.0, Z3 + 26.0), 18),
        "CAM_A3_06_Porta": ((6.0, 40.0, Z3 + E), (0.0, 61.0, Z3 + 16.0), 18),
        "CAM_A3_06_Porta_Folha": ((2.0, 57.0, Z3 + E), (-13.0, 68.0, Z3 + 8.0), 18),
        "CAM_A3_06_Guardas": ((16.0, 44.0, Z3 + E), (-20.0, 58.0, Z3 + 8.0), 20),
        "CAM_A3_06_Fachada_Base": ((40.0, 50.0, Z3 + E), (62.0, 62.0, Z3 + 9.0), 20),
        "CAM_A3_06_Torre_Pe": ((92.0, 44.0, Z3 + E), (116.0, 72.0, Z3 + 30.0), 18),
        "CAM_A3_06_Flanco_W": ((-132.0, 96.0, Z3 + E), (-104.0, 180.0, Z3 + 30.0), 18),
        "CAM_A3_06_Flanco_E": ((140.0, 116.0, Z3 + E), (104.0, 200.0, Z3 + 30.0), 18),
        "CAM_A3_06_Coroa_Norte": ((56.0, 368.0, Z3 + E), (0.0, 303.0, Z3 + 80.0), 18),
        "CAM_A3_06_Castelo_Vila": ((20.0, -110.0, Z2 + E), (0.0, 150.0, Z3 + 120.0), 20),
        "CAM_A3_06_Castelo_Alto": ((280.0, -120.0, Z3 + 130.0), (0.0, 170.0, Z3 + 80.0), 22),
        # 07 salao
        "CAM_A3_07_Nave_Porta": ((4.0, 70.0, Z3 + E), (0.0, 262.0, Z3 + 30.0), 18),
        "CAM_A3_07_Nave_Meio": ((14.0, 160.0, Z3 + E), (-6.0, 262.0, Z3 + 26.0), 18),
        "CAM_A3_07_Nave_Volta": ((0.0, 240.0, Z3 + E), (0.0, 66.0, Z3 + 30.0), 18),
        "CAM_A3_07_Lateral_W": ((-79.0, 80.0, Z3 + E), (-79.0, 250.0, Z3 + 20.0), 18),
        "CAM_A3_07_Lateral_E_Parede": ((74.0, 150.0, Z3 + E), (92.0, 160.0, Z3 + 16.0), 20),
        "CAM_A3_07_Pilar_CU": ((52.0, 125.0, Z3 + E), (66.0, 145.0, Z3 + 12.0), 20),
        "CAM_A3_07_Teto": ((0.0, 140.0, Z3 + E), (0.0, 186.0, Z3 + 84.0), 14),
        "CAM_A3_07_Piso": ((-20.0, 110.0, Z3 + E), (-10.0, 128.0, Z3), 20),
        "CAM_A3_07_Presbiterio": ((0.0, 238.0, Z3 + E), (0.0, 290.0, Z3 + 30.0), 18),
        # 08 trono e caracol
        "CAM_A3_08_Trono_Fechado": ((0.0, 272.0, CZ + E), (0.0, 294.0, CZ + 9.0), 20),
        "CAM_A3_08_Trono_34": ((-12.0, 276.0, CZ + E), (2.0, 296.0, CZ + 8.0), 20),
        "CAM_A3_08_Trono_Open": ((-9.0, 268.0, CZ + 8.0), (2.0, 304.0, CZ + 7.0), 18),
        "CAM_A3_08_Arco_Open": ((-3.0, 287.0, CZ + E), (0.0, 312.0, CZ + 3.0), 16),
        "CAM_A3_08_Bolso_Open": ((4.0, 282.0, CZ + E), (28.0, 294.0, CZ + 8.0), 18),
        "CAM_A3_08_Caracol_Topo_Open": ((0.0, 304.0, CZ + E), (6.0, 322.0, CZ - 8.0), 14),
        "CAM_A3_08_Caracol_Patamar": _spiral_cam(-90.0, -30.0, 3.0, 14),
        "CAM_A3_08_Caracol_Meio": _spiral_cam(285.0, 335.0, 3.0, 14),
        "CAM_A3_08_Caracol_Meio_Cima": _spiral_cam(300.0, 250.0, 12.0, 14),
        "CAM_A3_08_Caracol_Fundo": _spiral_cam(585.0, 630.0, 1.0, 14),
        "CAM_A3_08_Torre_Poco": ((22.0, 288.0, GZ + E), (0.0, 322.0, 40.0), 16),
        # 09 salao sombrio
        "CAM_A3_09_Galeria_Chegada": ((0.0, 298.0, GZ + E), (0.0, 150.0, -2.0), 16),
        "CAM_A3_09_Galeria_Lateral": ((-56.0, 290.0, GZ + E), (50.0, 286.0, GZ + 2.0), 18),
        "CAM_A3_09_Escadaria_Topo": ((4.0, 276.0, GZ + E), (0.0, 224.0, FZ), 18),
        "CAM_A3_09_Escadaria_Pe": ((5.0, 212.0, FZ + E), (0.0, 262.0, GZ + 4.0), 18),
        "CAM_A3_09_Passarela_W": ((-85.0, 268.0, GZ + E), (-85.0, 160.0, GZ + 2.0), 18),
        "CAM_A3_09_Ponte_Suspensa": ((-74.0, 200.0, GZ + E), (40.0, 200.0, GZ + 2.0), 18),
        "CAM_A3_09_Ponte_De_Baixo": ((30.0, 232.0, FZ + E), (0.0, 200.0, GZ), 18),
        "CAM_A3_09_Rio": ((-40.0, 228.0, FZ + E), (-62.0, 208.0, FZ - 2.0), 20),
        "CAM_A3_09_Forja": ((-46.0, 176.0, FZ + E), (-78.0, 150.0, FZ + 3.0), 16),
        "CAM_A3_09_Forja_2": ((-56.0, 138.0, FZ + E), (-80.0, 180.0, FZ + 6.0), 16),
        "CAM_A3_09_Mapa": ((47.0, 178.0, FZ + 8.0), (73.0, 160.0, FZ + 3.5), 17),
        "CAM_A3_09_Mapa_2": ((56.0, 138.0, FZ + E), (72.0, 176.0, FZ + 4.0), 16),
        "CAM_A3_09_Portal": ((6.0, 158.0, FZ + E), (0.0, 100.0, 7.5), 17),
        "CAM_A3_09_Portal_CU": ((8.0, 126.0, FZ + E), (0.0, 100.0, FZ + 12.0), 18),
        "CAM_A3_09_Volta": ((0.0, 124.0, FZ + E), (0.0, 300.0, 12.0), 16),
        "CAM_A3_09_Abobada": ((0.0, 176.0, FZ + E), (0.0, 224.0, 41.0), 14),
        "CAM_A3_09_Visao_Geral": ((50.0, 294.0, 24.0), (-12.0, 150.0, -6.0), 13),
        "CAM_A3_09_Rocha_CU": ((-66.0, 246.0, FZ + E), (-90.0, 254.0, FZ + 6.0), 20),
        # 10 masmorra
        "CAM_A3_10_R1_Chegada": ((3.0, 16.0, DZ + E), (0.0, 90.0, DZ + 11.0), 18),
        "CAM_A3_10_R1_Fundo": ((30.0, 80.0, DZ + E), (-14.0, 6.0, DZ + 9.0), 18),
        "CAM_A3_10_R1_Saida": ((-26.0, 26.0, DZ + E), (-30.0, 6.0, DZ + 5.0), 20),
        "CAM_A3_10_Vao_R1R2": ((2.0, 78.0, DZ + E), (0.0, 104.0, DZ + 10.0), 18),
        "CAM_A3_10_R2_Entrada": ((4.0, 100.0, DZ + E), (0.0, 196.0, DZ + 11.0), 18),
        "CAM_A3_10_R2_Diagonal": ((44.0, 188.0, DZ + E), (-32.0, 104.0, DZ + 11.0), 18),
        "CAM_A3_10_R2_Portal": ((0.0, 160.0, DZ + E), (0.0, 196.0, DZ + 12.0), 18),
        "CAM_A3_10_R2_Parede": ((-38.0, 140.0, DZ + E), (-52.0, 150.0, DZ + 10.0), 20),
        "CAM_A3_10_R3_Entrada": ((4.0, 206.0, DZ + E), (0.0, 302.0, DZ + 11.0), 18),
        "CAM_A3_10_R3_Diagonal": ((42.0, 294.0, DZ + E), (-52.0, 212.0, DZ + 9.0), 18),
        "CAM_A3_10_R3_Portal": ((0.0, 266.0, DZ + E), (0.0, 303.0, DZ + 12.0), 18),
        "CAM_A3_10_R3_Retabulo": ((36.0, 250.0, DZ + E), (52.0, 250.0, DZ + 6.0), 20),
        "CAM_A3_10_R3_Teto": ((0.0, 250.0, DZ + E), (0.0, 262.0, DZ + 44.0), 14),
        # 11 alquimia
        "CAM_A3_11_Rua": ((40.0, -89.0, Z2 + E), (cx, cy, Z2 + 17.0), 20),
        "CAM_A3_11_Porta": ((cx - 30.0, cy + 2.0, Z2 + E), (cx, cy, Z2 + 10.0), 20),
        "CAM_A3_11_Leste": ((150.0, -44.0, Z2 + E), (cx, cy, Z2 + 20.0), 20),
        "CAM_A3_11_DoP1": ((60.0, -168.0, Z1 + E), (cx, cy, Z2 + 22.0), 20),
        "CAM_A3_11_Fundo": ((cx + 30.0, cy - 30.0, Z2 + E), (cx, cy, Z2 + 16.0), 20),
        "CAM_A3_11_In_Caldeirao": ((cx - 11.8, cy - 2.8, Z2 + 6.2), (cx + 7.0, cy + 1.0, Z2 + 5.0), 16),
        "CAM_A3_11_In_Prateleiras": ((cx - 8.5, cy - 6.5, Z2 + 6.0), (cx + 3.0, cy + 13.5, Z2 + 6.0), 16),
        "CAM_A3_11_In_Porta": ((cx + 9.0, cy - 1.0, Z2 + 5.8), (cx - 14.0, cy, Z2 + 7.0), 16),
        "CAM_A3_11_In_Cima": ((cx - 9.4, cy, Z2 + 3.2), (cx + 3.0, cy, Z2 + 18.0), 14),
        # 12 invocacao
        "CAM_A3_12_Ponte": ((-150.0, -224.0, Z1 + E), (tx, ty, ZS + 14.0), 20),
        "CAM_A3_12_Ponte_Parapeito": ((-169.0, -218.0, Z1 + E), (-175.0, -228.5, Z1 + 1.5), 22),
        "CAM_A3_12_Ponte_Lado": ((-172.0, -176.0, Z1 - 4.0), (-172.0, -222.0, Z1 - 6.0), 20),
        "CAM_A3_12_Plataforma": ((-194.0, -210.0, ZS + E), (tx, ty, ZS + 10.0), 18),
        "CAM_A3_12_Borda": ((-198.0, -236.0, ZS + E), (-226.0, -240.0, ZS + 1.0), 20),
        "CAM_A3_12_Torre_Cima": ((-198.0, -226.0, ZS + E), (tx, ty, ZS + 34.0), 16),
        "CAM_A3_12_Media": ((-120.0, -176.0, ZS + 40.0), (-208.0, -222.0, ZS + 10.0), 20),
        # 13 saida noroeste, portao DS, jardim-mirante
        "CAM_A3_13_Beco_W1": ((-88.0, 30.0, Z3 + E), (-150.0, 46.0, Z3 + 6.0), 20),
        "CAM_A3_13_Beco_W2": ((-148.0, 96.0, Z3 + E), (-136.0, 200.0, Z3 + 8.0), 20),
        "CAM_A3_13_Beco_W3": ((-136.0, 240.0, Z3 + E), (-118.0, 334.0, Z3 + 6.0), 20),
        "CAM_A3_13_Terraco_Norte": ((10.0, 358.0, Z3 + E), (-116.0, 342.0, Z3 + 6.0), 20),
        "CAM_A3_13_Saida_Cabeceira": _exit_cam(-16.0, 2.0, Z3 + E, 70.0, 0.0, Z3 + 10.0, 20),
        "CAM_A3_13_Saida_Ponte": _exit_cam(28.0, -3.0, Z3 + E, 76.0, 0.0, Z3 + 12.0, 20),
        "CAM_A3_13_PortaoDS": _exit_cam(54.0, 5.0, Z3 + E, 76.0, 0.0, Z3 + 14.0, 20),
        "CAM_A3_13_Saida_Volta": _exit_cam(70.0, 2.0, Z3 + E, -40.0, 0.0, Z3 + 30.0, 20),
        "CAM_A3_13_Saida_Lado": _exit_cam(40.0, -80.0, Z3 + 14.0, 40.0, 0.0, Z3 - 6.0, 22),
        "CAM_A3_13_Mirante_Caminho": ((150.0, 0.0, Z3 + E), (140.0, 120.0, Z3 + 5.0), 20),
        "CAM_A3_13_Mirante": ((133.0, 142.0, Z3 + E), (136.0, 176.0, Z3 + 3.5), 20),
        "CAM_A3_13_Mirante_Vista": ((120.0, 166.0, Z3 + E), (190.0, 176.0, Z3), 20),
        # 14 silhueta (4 lados, 3/4 alto, quilha e a vista da Ilha 2)
        "CAM_A3_14_Sul": ((0.0, -920.0, 240.0), (0.0, 0.0, 80.0), 24),
        "CAM_A3_14_Norte": ((0.0, 1020.0, 300.0), (0.0, 40.0, 100.0), 24),
        "CAM_A3_14_Leste": ((820.0, 20.0, 220.0), (0.0, 20.0, 80.0), 24),
        "CAM_A3_14_Oeste": ((-820.0, 20.0, 220.0), (0.0, 20.0, 80.0), 24),
        "CAM_A3_14_Alto_34": ((560.0, -540.0, 520.0), (0.0, 0.0, 40.0), 24),
        "CAM_A3_14_Quilha": ((320.0, -320.0, -130.0), (0.0, 40.0, -30.0), 24),
    }
    c.update(_house_cams())
    # vista da Ilha 2: atras da ancora (WORLD_FROM_PREV), no rumo inverso da ponte, olhando a ilha inteira
    (x0, y0), (x1, y1) = L.BRIDGE_PATH[0], L.BRIDGE_PATH[1]
    ln = math.hypot(x1 - x0, y1 - y0) or 1.0
    ux, uy = (x1 - x0) / ln, (y1 - y0) / ln
    c["CAM_A3_14_Ilha2"] = ((x0 - ux * 140.0, y0 - uy * 140.0, D + 60.0), (0.0, -20.0, 90.0), 24)
    c["CAM_A3_14_Ilha2_Perto"] = ((x0 - ux * 20.0, y0 - uy * 20.0, D + E), (0.0, -60.0, 110.0), 22)
    return c


def cameras_a3():
    """cria as cameras CAM_A3_* (auditoria 3) na cena atual"""
    for n, v in a3_cams().items():
        loc, tgt, lens = v
        camera(n, loc, tgt, lens)
