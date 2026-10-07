# sg_relocate - ONDA 0 (planta v4): roda modulos de detalhe da v3 que so MUDAM DE LUGAR (entrada, invocacao, alquimia,
# saida e a praca/fonte da vila) no referencial DELES (sg_layout_v3) e leva o resultado para a planta v4 com uma
# transformacao rigida (translacao + giro em Z + desnivel). Nada no codigo de detalhe muda; so a chamada e desviada.
# Quando a onda 1 refizer um modulo na planta v4, ele sai de LEGACY (build_sg) e roda direto.
import sys, math, importlib
import bpy
from mathutils import Matrix, Vector
import sg_layout as L

_V3 = None
_LOADED = {}


def v3():
    global _V3
    if _V3 is None:
        _V3 = importlib.import_module("sg_layout_v3")
    return _V3


def xform(old_xy, new_xy, dyaw_deg=0.0, dz=0.0):
    """matriz 4x4: T(new) . Rz(dyaw) . T(-old), com desnivel dz"""
    return (Matrix.Translation(Vector((new_xy[0], new_xy[1], dz))) @ Matrix.Rotation(math.radians(dyaw_deg), 4, "Z")
            @ Matrix.Translation(Vector((-old_xy[0], -old_xy[1], 0.0))))


def shift(dxy):
    return xform((0.0, 0.0), dxy)


# modulo -> (matriz, funcoes a chamar). A praca (sg_village.plaza) e chamada pelo blockout da vila.
def legacy_table():
    return {
        "sg_entry": (shift(L.ENTRY_SHIFT), ("build",)),
        "sg_summon": (shift(L.SUMMON_SHIFT), ("build",)),
        "sg_craft": (shift(L.CRAFT_SHIFT), ("build",)),
        "sg_exit": (xform(L.EXIT_OLD_START, L.EXIT_START, L.EXIT_DEG - L.EXIT_OLD_DEG, L.EXIT_Z - L.EXIT_OLD_Z), ("build",)),
        "sg_village": (shift(L.PLAZA_SHIFT), ("plaza",)),
    }


def _swap_layout(to):
    """troca o 'sg_layout' visto pelos modulos sg_* ja carregados; devolve o que desfazer"""
    undo = []
    cur = sys.modules.get("sg_layout")
    for name, mod in list(sys.modules.items()):
        if not name.startswith("sg_") or mod is None or name in ("sg_layout", "sg_layout_v3", "sg_relocate"):
            continue
        if getattr(mod, "L", None) is cur:
            undo.append((mod, cur))
            mod.L = to
    return undo


def load(name):
    """importa o modulo antigo com o 'sg_layout' = v3 (as constantes de modulo saem na v3)"""
    if name in _LOADED:
        return _LOADED[name]
    old = sys.modules["sg_layout"]
    sys.modules["sg_layout"] = v3()
    undo = _swap_layout(v3())
    try:
        if name in sys.modules:
            mod = importlib.reload(sys.modules[name])
        else:
            mod = importlib.import_module(name)
    finally:
        sys.modules["sg_layout"] = old
        for m, cur in undo:
            m.L = cur
    _LOADED[name] = mod
    return mod


def _apply(M, objs):
    R3 = M.to_3x3()
    for o in objs:
        if o.parent is not None:
            continue
        if o.type == "MESH" and not o.name.startswith("COL_") and o.data.users == 1:
            o.data.transform(M @ o.matrix_world)
            o.matrix_world = Matrix.Identity(4)
        else:
            o.matrix_world = M @ o.matrix_world
        if "pivot" in o.keys():
            o["pivot"] = tuple(M @ Vector(o["pivot"]))
        if "axis" in o.keys():
            o["axis"] = tuple(R3 @ Vector(o["axis"]))


def run(name, fns=None):
    """roda o modulo antigo no referencial v3 e transforma TUDO o que ele criou para a planta v4"""
    M, dflt = legacy_table()[name]
    mod = load(name)
    before = {o.name for o in bpy.data.objects}
    old = sys.modules["sg_layout"]
    sys.modules["sg_layout"] = v3()
    undo = _swap_layout(v3())
    try:
        for fn in fns or dflt:
            getattr(mod, fn)()
    finally:
        sys.modules["sg_layout"] = old
        for m, cur in undo:
            m.L = cur
    made = [o for o in bpy.data.objects if o.name not in before]
    # cameras dos modulos antigos: fora (estao no referencial velho; a onda 1 refaz)
    for o in [o for o in made if o.type == "CAMERA"]:
        bpy.data.objects.remove(o, do_unlink=True)
    made = [o for o in bpy.data.objects if o.name not in before]
    bpy.context.view_layer.update()            # matrix_world das pecas recem-criadas (col_box so poe loc/rot/escala)
    _apply(M, made)
    bpy.context.view_layer.update()
    return mod, made


def map_route(name, pts, z0):
    """leva uma rota EXTRA_ROUTES do modulo antigo (xy + z inicial) para a planta v4"""
    M = legacy_table()[name][0]
    out = [tuple((M @ Vector((x, y, 0.0)))[:2]) for x, y in pts]
    return out, z0 + M.translation.z


def map_probe(name, pr):
    M = legacy_table()[name][0]
    nm, x, y, z, dx, dy = pr[:6]
    p = M @ Vector((x, y, z))
    d = M.to_3x3() @ Vector((dx, dy, 0.0))
    return (nm, p.x, p.y, p.z, d.x, d.y) + tuple(pr[6:])
