# fm_terrain_detail - nivel de detalhe das caixas do terreno (orcamento de triangulos)
# TMB = MB com 'detail': as primitivas box() de escadas, alvenaria, pavimento e muretas seguem o nivel:
#   None   -> igual ao MB (chanfro em todas as arestas)
#   'near' -> sem face de baixo; chanfro so nas 4 arestas de cima (quina do degrau / da pedra)
#   'far'  -> sem face de baixo e sem chanfro (vista de longe: o chanfro so custava triangulos)
# O sorteio de rng e de variantes e o mesmo do MB (geometria e cores iguais, so menos triangulos).
import bmesh
from mathutils import Vector, Matrix, Euler
from fm_lib import MB


class TMB(MB):
    def __init__(self, name, collection, rng=None, detail=None, bottom=False):
        MB.__init__(self, name, collection, rng)
        self.detail = detail
        self.bottom = bottom

    def box(self, size, loc, rot=(0, 0, 0), m="Stone_Light", bevel=0.12, seg=1, tint=None):
        d = self.detail
        if d not in ("near", "far"):
            return MB.box(self, size, loc, rot, m, bevel, seg, tint)
        sx, sy, sz = size
        M = Matrix.LocRotScale(Vector(loc), Euler(rot), Vector((sx, sy, sz)))
        r = bmesh.ops.create_cube(self.bm, size=1.0, matrix=M)
        vs = r["verts"]
        faces = {f for v in vs for f in v.link_faces}
        for f in faces:
            f.normal_update()
        bot = min(faces, key=lambda f: f.normal.z)
        top = max(faces, key=lambda f: f.normal.z)
        bev = min(bevel, min(sx, sy, sz) * 0.3) if bevel else 0.0
        new = set()
        if d == "near" and bev > 0.02 and top.normal.z > 0.9:
            res = bmesh.ops.bevel(self.bm, geom=list(top.edges), offset=bev, offset_type="OFFSET", segments=1,
                                  profile=0.5, affect="EDGES", clamp_overlap=True)
            new = set(res.get("faces", ()))
            for v in res.get("verts", ()):
                new |= set(v.link_faces)
        if not self.bottom and bot.is_valid and bot.normal.z < -0.9:
            bmesh.ops.delete(self.bm, geom=[bot], context="FACES_ONLY")
        faces = {f for f in faces if f.is_valid} | {f for f in new if f.is_valid}
        for v in vs:
            if v.is_valid:
                faces |= set(v.link_faces)
        # mesmo consumo de rng / variante do MB._post
        mi = self._mi_for(m)
        t = self.rng.uniform(-1, 1) if tint is None else tint
        for f in faces:
            f.material_index = mi
            f[self.tint] = t
            f.smooth = False
            f.normal_update()
        self._uv(faces, m)
