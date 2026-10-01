# Procedural sculpted shapes (real meshes, not primitives) for the Dragon Ball rocks and terrain.
# Every face gets a palette swatch through its UVs, so a whole rock is a single textured MeshPart.
import bpy, bmesh, math, random
from mathutils import Vector, noise
import klib
from meshkit import palette_uv

PI = math.pi

def n3(x, y, z, scale=1.0, seed=0.0):
    return noise.noise(Vector((x*scale + seed*13.1, y*scale + seed*7.7, z*scale + seed*3.3)))

def paint(bm, fn):
    """fn(face) -> palette key; writes per-face UVs."""
    uv = bm.loops.layers.uv.get('UVMap') or bm.loops.layers.uv.new('UVMap')
    for f in bm.faces:
        u = palette_uv(fn(f))
        for l in f.loops: l[uv].uv = u

def to_object(name, bm, target, smooth=False, sharp=35):
    me = bpy.data.meshes.new(name)
    bm.normal_update()
    bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth = smooth
    if smooth:
        try: me.set_sharp_from_angle(angle=math.radians(sharp))
        except Exception: pass
    me.materials.append(bpy.data.materials['DB_Palette'])
    ob = bpy.data.objects.new(name, me)
    ob['pal'] = True
    target.objects.link(ob)
    return ob

def _ring_loft(bm, rings, closed_top=True, closed_bottom=True):
    """rings: list of lists of Vector (same count). Builds side quads + caps."""
    vs = [[bm.verts.new(p) for p in ring] for ring in rings]
    n = len(rings[0])
    for a, b in zip(vs, vs[1:]):
        for i in range(n):
            j = (i+1) % n
            bm.faces.new((a[i], a[j], b[j], b[i]))
    if closed_bottom: bm.faces.new(list(reversed(vs[0])))
    if closed_top:
        top = vs[-1]
        c = sum((v.co for v in top), Vector())/n
        cv = bm.verts.new(c + Vector((0, 0, 0)))
        for i in range(n):
            bm.faces.new((top[i], top[(i+1) % n], cv))
    return vs

# ------------------------------------------------------------------ battle spire
def spire(name, target, height=60, r0=9, r1=6, tiers=4, seed=1, segs=22, lean=(0, 0), top='grass'):
    rs = random.Random(seed)
    bm = bmesh.new()
    rings, meta = [], []
    tier_h = height/tiers
    z = 0.0
    step = 2.2
    cuts = [tier_h*(k+1) for k in range(tiers-1)]
    zs = []
    while z < height - .01:
        zs.append(z); z += step
    zs.append(height)
    for z in zs:
        t = z/height
        base_r = r0 + (r1 - r0)*t
        # ledge bulge right at each tier cut, slight pinch just above it
        bump = 0.0
        for c in cuts:
            d = z - c
            if -1.2 < d <= 0: bump += 1.0
            elif 0 < d < 2.6: bump -= .6
        ring = []
        for i in range(segs):
            a = i/segs*2*PI
            nn = n3(math.cos(a)*1.6, math.sin(a)*1.6, z*.09, 1.0, seed)*base_r*.22 + n3(math.cos(a)*4, math.sin(a)*4, z*.3, 1.0, seed + 5)*base_r*.06
            r = max(1.0, base_r + nn + bump)
            ring.append(Vector((math.cos(a)*r + lean[0]*z, math.sin(a)*r + lean[1]*z, z)))
        rings.append(ring); meta.append(z)
    # domed top: two shrinking rings
    last = rings[-1]
    cxy = sum((v for v in last), Vector())/len(last)
    for k, (f, dz) in enumerate(((.82, 1.4), (.5, 2.3))):
        rings.append([cxy + (v - cxy)*f + Vector((0, 0, dz + rs.uniform(-.3, .3))) for v in last])
    _ring_loft(bm, rings)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=.01)
    tones = ['db_rock', 'db_rock_light']
    def col(f):
        c = f.calc_center_median()
        if f.normal.z > .55 and c.z > height - .5: return top == 'grass' and 'db_grass' or 'db_rock_light'
        for cc in cuts:
            if -1.3 < c.z - cc < .4: return 'db_rock_dark'
        return tones[int(c.z // tier_h) % 2]
    paint(bm, col)
    return to_object(name, bm, target, smooth=False)

# ------------------------------------------------------------------ faceted boulder
def boulder(name, target, size=(8, 7, 6), seed=1, sub=2, tone='db_rock', flat_bottom=True, loc=(0, 0, 0)):
    rs = random.Random(seed)
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=sub, radius=1.0)
    for v in bm.verts:
        p = v.co
        k = 1 + n3(p.x, p.y, p.z, 1.3, seed)*.28 + n3(p.x, p.y, p.z, 3.1, seed + 2)*.08
        p *= k
        p.x *= size[0]/2; p.y *= size[1]/2; p.z *= size[2]/2
        if flat_bottom and p.z < -size[2]*.15: p.z = -size[2]*.15 + (p.z + size[2]*.15)*.15
        p.z += size[2]*.15
        p += Vector(loc)
    light = {'db_rock': 'db_rock_light', 'db_rock_dark': 'db_rock', 'db_crater': 'db_rock_dark'}.get(tone, tone)
    paint(bm, lambda f: light if f.normal.z > .6 else tone)
    return bm

def boulder_obj(name, target, **kw):
    return to_object(name, boulder(name, target, **kw), target, smooth=False)

# ------------------------------------------------------------------ layered massif / mesa / cliff
def _blob_poly(w, d, n, seed, z, rough=.12):
    pts = []
    for i in range(n):
        a = i/n*2*PI
        c, s = math.cos(a), math.sin(a)
        # superellipse (boxy but rounded) + noise
        r = 1/((abs(c)/(w/2))**3 + (abs(s)/(d/2))**3)**(1/3)
        r *= 1 + n3(c*1.5, s*1.5, z*.05, 1.0, seed)*rough*2 + n3(c*5, s*5, z*.2, 1.0, seed + 3)*rough*.5
        pts.append(Vector((c*r, s*r, z)))
    return pts

def massif(name, target, w=40, d=34, h=60, layers=3, seed=1, grass=True, segs=28):
    bm = bmesh.new()
    rings = []
    z = 0.0
    shrink = [1.0, .86, .72, .6, .5]
    lh = h/layers
    for L in range(layers):
        k = shrink[L]
        z0, z1 = L*lh, (L+1)*lh
        steps = max(2, int(lh/3))
        for s in range(steps + 1):
            zz = z0 + (z1 - z0)*s/steps
            taper = 1 - .06*(s/steps)
            ring = _blob_poly(w*k*taper, d*k*taper, segs, seed + L*11, zz, .1)
            if s == steps and L < layers - 1:
                rings.append(ring)
                # ledge: step inward to the next layer's footprint
                nk = shrink[L+1]
                rings.append(_blob_poly(w*nk, d*nk, segs, seed + (L+1)*11, zz + .6, .1))
            else:
                rings.append(ring)
    last = rings[-1]
    cxy = sum((v for v in last), Vector())/len(last)
    rings.append([cxy + (v - cxy)*.93 + Vector((0, 0, 1.2)) for v in last])
    _ring_loft(bm, rings)
    tones = ['db_rock', 'db_rock_light', 'db_rock', 'db_rock_light', 'db_rock']
    def col(f):
        c = f.calc_center_median()
        if f.normal.z > .7:
            return 'db_grass' if (grass and c.z > h - .5) else 'db_rock_light'
        L = min(layers - 1, int(c.z // lh))
        if (c.z % lh) > lh - 2.2: return 'db_rock_dark'
        if (c.z % 7.5) < 1.0: return 'db_rock_red'
        return tones[L]
    paint(bm, col)
    return to_object(name, bm, target, smooth=False)

# ------------------------------------------------------------------ natural arch
def arch(name, target, span=38, leg_r=7, height=28, seed=4):
    bm = bmesh.new()
    segs = 14
    path = []
    R = span/2
    # legs up, then semicircle over the top
    for z in range(0, int(height - 2), 3):
        path.append(Vector((R, 0, z)))
    for i in range(0, 17):
        a = i/16*PI
        path.append(Vector((math.cos(a)*R, 0, height + math.sin(a)*R*.55)))
    for z in range(int(height - 2) - 3, -1, -3):
        path.append(Vector((-R, 0, z)))
    rings = []
    for k, p in enumerate(path):
        prev = path[max(0, k-1)]; nxt = path[min(len(path)-1, k+1)]
        tdir = (nxt - prev).normalized()
        side = Vector((0, 1, 0))
        up = tdir.cross(side).normalized()
        thick = leg_r*(1.15 if p.z < 4 else 1.0)*(.8 if p.z > height else 1)
        ring = []
        for i in range(segs):
            a = i/segs*2*PI
            rr = thick*(1 + n3(p.x*.12, p.z*.12, a, 1.0, seed)*.25)
            ring.append(p + side*math.cos(a)*rr*.9 + up*math.sin(a)*rr)
        rings.append(ring)
    _ring_loft(bm, rings, closed_top=True, closed_bottom=True)
    def col(f):
        c = f.calc_center_median()
        if f.normal.z > .75 and c.z > height + R*.4: return 'db_grass'
        if (c.z % 9) < 1.2: return 'db_rock_dark'
        return 'db_rock' if (c.z % 18) < 9 else 'db_rock_light'
    paint(bm, col)
    return to_object(name, bm, target, smooth=False)

# ------------------------------------------------------------------ floating islet
def islet(name, target, r=16, depth=34, seed=6):
    bm = bmesh.new()
    rings = []
    for k, (f, z) in enumerate(((1.0, 0), (1.04, -1.5), (.9, -6), (.7, -14), (.45, -22), (.22, -30), (.06, -depth))):
        rings.append(_blob_poly(2*r*f, 2*r*f*.9, 20, seed + k, z, .14))
    rings = list(reversed(rings))
    _ring_loft(bm, rings, closed_top=True, closed_bottom=True)
    def col(f):
        c = f.calc_center_median()
        if c.z > -1.2: return 'db_grass'
        return ['db_rock', 'db_rock_dark', 'db_rock_red', 'db_rock_deep'][min(3, int(-c.z // 8))]
    paint(bm, col)
    return to_object(name, bm, target, smooth=False)

# ------------------------------------------------------------------ impact crater bowl
def crater_bowl(name, target, cx, cy, r_floor=17, r_rim=30, depth=6, lip=2.6, seed=8, segs=48):
    bm = bmesh.new()
    prof = [(0, -depth), (r_floor*.5, -depth), (r_floor, -depth + .2), (r_floor + (r_rim - r_floor)*.5, -depth*.55),
            (r_rim - 1, -.6), (r_rim + 1.5, lip*.8), (r_rim + 3.2, lip), (r_rim + 5.5, lip*.35), (r_rim + 8, -.4)]
    rings = []
    for (r, z) in prof[1:]:
        ring = []
        for i in range(segs):
            a = i/segs*2*PI
            jr = n3(math.cos(a)*2, math.sin(a)*2, r*.05, 1.0, seed)*(1.8 if r > r_floor else .6)
            jz = n3(math.cos(a)*3, math.sin(a)*3, r*.1, 1.0, seed + 4)*(1.2 if r > r_rim else .3)
            ring.append(Vector((cx + math.cos(a)*(r + jr), cy + math.sin(a)*(r + jr), z + jz)))
        rings.append(ring)
    vs = [[bm.verts.new(p) for p in ring] for ring in rings]
    c = bm.verts.new(Vector((cx, cy, -depth)))
    for i in range(segs):
        bm.faces.new((c, vs[0][i], vs[0][(i+1) % segs]))
    for a, b in zip(vs, vs[1:]):
        for i in range(segs):
            j = (i+1) % segs
            bm.faces.new((a[i], b[i], b[j], a[j]))
    for f in bm.faces:
        f.normal_update()
        if f.normal.z < -.2: f.normal_flip()
    def col(f):
        cc = f.calc_center_median()
        r = math.hypot(cc.x - cx, cc.y - cy)
        if r < r_floor*.55: return 'db_scorch'
        if r < r_floor + 2: return 'db_crater'
        if r < r_rim: return 'db_rock_dark'
        if cc.z > lip*.5: return 'db_rock'
        return 'db_dirt'
    paint(bm, col)
    return to_object(name, bm, target, smooth=True, sharp=45)

# ------------------------------------------------------------------ swept tube (trunks, branches, roots)
def tube(bm, pts, radii, segs=10, seed=0, cap_end=True):
    pts = [Vector(p) for p in pts]
    rings = []
    prev_side = None
    for k, p in enumerate(pts):
        a = pts[max(0, k-1)]; b = pts[min(len(pts)-1, k+1)]
        t = (b - a).normalized()
        ref = Vector((0, 0, 1)) if abs(t.z) < .9 else Vector((1, 0, 0))
        side = t.cross(ref).normalized()
        if prev_side is not None and side.dot(prev_side) < 0: side = -side
        prev_side = side
        up = t.cross(side).normalized()
        ring = []
        for i in range(segs):
            ang = i/segs*2*PI
            rr = radii[k]*(1 + n3(math.cos(ang)*2, math.sin(ang)*2, k*.7, 1.0, seed)*.12)
            ring.append(p + side*math.cos(ang)*rr + up*math.sin(ang)*rr)
        rings.append(ring)
    vs = [[bm.verts.new(q) for q in ring] for ring in rings]
    faces = []
    for a, b in zip(vs, vs[1:]):
        for i in range(segs):
            j = (i+1) % segs
            faces.append(bm.faces.new((a[i], a[j], b[j], b[i])))
    if cap_end:
        c = bm.verts.new(pts[-1] + (pts[-1] - pts[-2]).normalized()*radii[-1]*.5)
        for i in range(segs):
            faces.append(bm.faces.new((vs[-1][i], vs[-1][(i+1) % segs], c)))
    return faces

def trunk_mesh(name, target, height, r0, r1, lean=(0, 0), branches=3, roots=4, seed=1, bark='db_trunk', bark_dark=None):
    """Curved tapered trunk with flared roots and branches reaching into the crown. Returns (object, crown_center)."""
    rs = random.Random(seed)
    bm = bmesh.new()
    n = 7
    pts, rad = [], []
    for k in range(n + 1):
        t = k/n
        s = math.sin(t*PI)*.08*height
        pts.append((lean[0]*t*height + s*rs.uniform(-.5, .5), lean[1]*t*height + s*rs.uniform(-.5, .5), t*height))
        rad.append(r0 + (r1 - r0)*t**.8)
    rad[0] *= 1.25
    tube(bm, pts, rad, 12, seed)
    top = Vector(pts[-1])
    for k in range(roots):
        a = k/roots*2*PI + rs.uniform(-.3, .3)
        L = r0*rs.uniform(2.2, 3.2)
        tube(bm, [(0, 0, r0*1.6), (math.cos(a)*L*.55, math.sin(a)*L*.55, r0*.5), (math.cos(a)*L, math.sin(a)*L, -.2)],
             [r0*.55, r0*.4, r0*.18], 8, seed + k)
    tips = []
    for k in range(branches):
        a = k/branches*2*PI + rs.uniform(-.4, .4)
        z0 = height*rs.uniform(.55, .78)
        base = Vector((lean[0]*z0, lean[1]*z0, z0))
        L = height*rs.uniform(.32, .45)
        tip = base + Vector((math.cos(a)*L*.8, math.sin(a)*L*.8, L*.7))
        mid = base.lerp(tip, .5) + Vector((0, 0, L*.12))
        tube(bm, [base, mid, tip], [r1*.9, r1*.6, r1*.35], 8, seed + 10 + k)
        tips.append(tip)
    dark = bark_dark or bark
    paint(bm, lambda f: dark if (f.calc_center_median().z < height*.12 or f.normal.z < -.3) else bark)
    ob = to_object(name, bm, target, smooth=True, sharp=60)
    return ob, top, tips

# ------------------------------------------------------------------ leaf-card foliage (Genshin/Ghibli style canopy)
LEAF_CELLS = {'light': 0, 'mid': 1, 'dark': 2, 'teal': 3}

def leaves_material():
    m = bpy.data.materials.get('DB_Leaves')
    if m: return m
    m = bpy.data.materials.new('DB_Leaves')
    m.use_nodes = True
    nt = m.node_tree
    bsdf = next((n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED'), None)
    if bsdf is None:
        bsdf = nt.nodes.new('ShaderNodeBsdfPrincipled')
        out = next((n for n in nt.nodes if n.type == 'OUTPUT_MATERIAL'), None) or nt.nodes.new('ShaderNodeOutputMaterial')
        nt.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    img = bpy.data.images.get('folhas') or bpy.data.images.load(r"C:\Users\lucas\OneDrive\Desktop\To up\dragonball_area\export\tex\folhas.png")
    tex = nt.nodes.new('ShaderNodeTexImage'); tex.image = img
    nt.links.new(tex.outputs['Color'], bsdf.inputs['Base Color'])
    nt.links.new(tex.outputs['Alpha'], bsdf.inputs['Alpha'])
    try: m.surface_render_method = 'DITHERED'
    except Exception: pass
    return m

def foliage(name, target, clumps, crown_center, seed=1, palette=('light', 'mid', 'dark'), density=1.0):
    """clumps: [(center Vector, radius)]. Builds double-sided leaf cards with sphere-like custom normals."""
    rs = random.Random(seed)
    cc = Vector(crown_center)
    verts, faces, uvs, nrms = [], [], [], []
    zs = [c[0].z for c in clumps]
    zmin, zmax = min(zs), max(zs)
    for (p, r) in clumps:
        p = Vector(p)
        n = int((14 + r*2.2)*density)
        golden = PI*(3 - math.sqrt(5))
        for i in range(n):
            yv = 1 - (i + .5)/n*2
            rad = math.sqrt(1 - yv*yv)
            th = golden*i + rs.uniform(-.3, .3)
            d = Vector((math.cos(th)*rad, math.sin(th)*rad, yv)).normalized()
            if d.z < -.75 and rs.random() < .6: continue          # thinner underside
            depth = rs.uniform(.55, .95)
            pos = p + d*r*depth
            s = r*rs.uniform(.85, 1.25)
            # card basis facing d
            ref = Vector((0, 0, 1)) if abs(d.z) < .95 else Vector((1, 0, 0))
            t1 = d.cross(ref).normalized(); t2 = d.cross(t1).normalized()
            roll = rs.uniform(0, 2*PI)
            ax = t1*math.cos(roll) + t2*math.sin(roll); ay = d.cross(ax).normalized()
            # tone: top/outer = light, low/inner = dark
            h = (pos.z - zmin)/max(zmax - zmin, 1)
            score = .55*d.z + .35*(h*2 - 1) + rs.uniform(-.25, .25)
            tone = palette[0] if score > .3 else (palette[2] if score < -.25 else palette[1])
            cell = LEAF_CELLS[tone]
            u0, v0 = (cell % 2)*.5, 1 - (cell//2 + 1)*.5
            corners = [(-1, -1), (1, -1), (1, 1), (-1, 1)]
            base = len(verts)
            for (a, b) in corners:
                q = pos + ax*a*s*.5 + ay*b*s*.5
                verts.append(q)
                uvs.append((u0 + (a + 1)*.25, v0 + (b + 1)*.25))
                nn = ((q - cc).normalized()*.65 + (q - p).normalized()*.35).normalized()
                nrms.append(nn)
            faces.append((base, base + 1, base + 2, base + 3))
            base2 = len(verts)
            for k in range(4):
                verts.append(verts[base + k]); uvs.append(uvs[base + k]); nrms.append(nrms[base + k])
            faces.append((base2 + 3, base2 + 2, base2 + 1, base2))
    me = bpy.data.meshes.new(name)
    me.from_pydata([tuple(v) for v in verts], [], faces)
    me.update()
    lay = me.uv_layers.new(name='UVMap')
    loop_normals = []
    for poly in me.polygons:
        for li in poly.loop_indices:
            vi = me.loops[li].vertex_index
            lay.data[li].uv = uvs[vi]
            loop_normals.append(tuple(nrms[vi]))
    for p in me.polygons: p.use_smooth = True
    try:
        me.normals_split_custom_set(loop_normals)
    except Exception as e:
        print('normals', e)
    me.materials.append(leaves_material())
    ob = bpy.data.objects.new(name, me)
    ob['leaf'] = True
    target.objects.link(ob)
    return ob
