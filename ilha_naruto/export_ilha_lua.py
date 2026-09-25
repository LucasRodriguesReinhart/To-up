# export_ilha_lua - bloco Lua comum da ilha e dos portoes avulsos (usado por export_ilha.py e export_portoes.py):
#   - pecas moveis VFX_* -> tag IlhaMovel + LocalScript ILHA_NARUTO_Movel (gira em volta do pivo / flutua)
#   - portoes de compra -> tag PortaoCompra (barreira, cadeado, brilho de abertura, colisao de bloqueio) +
#     ModuleScript ReplicatedStorage.PortoesCompra com Estado(chave, desbloqueado)
import bpy
from mathutils import Vector


def neon_rules():
    """todo material com 'Glow' no nome vira Neon (o prefixo Crystal_ do lobby ganharia do 'glow' e sairia SmoothPlastic)"""
    import fm_lib
    have = {r[0] for r in fm_lib.RBX_RULES}
    n = 0
    for m in bpy.data.materials:
        if "Glow" in m.name and m.name not in have:
            fm_lib.RBX_RULES.insert(0, (m.name, "Neon", 0.0, False))
            n += 1
    return n


def vfx_list(ER):
    out = []
    for o in bpy.data.objects:
        if o.type == "MESH" and o.name.startswith("VFX_"):
            piv = o.get("pivot")
            if piv is None:
                bb = [o.matrix_world @ Vector(c) for c in o.bound_box]
                piv = tuple(sum(bb, Vector()) / 8.0)
            ax = o.get("axis", (0.0, 0.0, 1.0))
            out.append({"name": o.name, "pivot": ER.to_rbx(piv), "axis": ER.to_rbx(ax),
                        "rpm": float(o.get("rpm", 0.0)), "bob": float(o.get("bob", 0.0)),
                        "rate": float(o.get("rate", 0.0))})
    return out


def extra_lua(ER, vfx, root_pivot=False):
    Lx = []
    A = Lx.append
    # pivo fixo do Model: origem do export (+ ROOT_OFFSET). Portao avulso: centro do vao no piso, use
    # root:PivotTo(CFrame.lookAt(pos, pos + avanco)). As pecas moveis sao relativas a este pivo.
    A("root.WorldPivot = CFrame.new(ROOT_OFFSET)")
    A("-- ===== pecas moveis (VFX_*) =====")
    A("local VFX = {")
    for v in vfx:
        A("  [%s] = {p = Vector3.new(%.3f,%.3f,%.3f), a = Vector3.new(%.4f,%.4f,%.4f), rpm = %.3f, bob = %.3f, rate = %.3f}," % (
            ER.lua_str(v["name"]), *v["pivot"], *v["axis"], v["rpm"], v["bob"], v["rate"]))
    A("}")
    A("local nV = 0")
    A("for _, d in ipairs(root:GetDescendants()) do")
    A("  if d:IsA('MeshPart') then local o = string.match(d.Name, '^(VFX_[%w_]-)__')")
    A("    local v = o and VFX[o]")
    A("    if v then local rel = root:GetPivot():ToObjectSpace(CFrame.new(v.p + ROOT_OFFSET))")
    A("      d:SetAttribute('pivot_rel', rel.Position); d:SetAttribute('axis_rel', v.a); d:SetAttribute('rpm', v.rpm)")
    A("      d:SetAttribute('bob', v.bob); d:SetAttribute('rate', v.rate); d:SetAttribute('cf0_rel', root:GetPivot():ToObjectSpace(d.CFrame))")
    A("      d:SetAttribute('movel_de', root.Name); CS:AddTag(d, 'IlhaMovel'); nV += 1 end end")
    A("end")
    A("do local SPS = game:GetService('StarterPlayer'):FindFirstChildOfClass('StarterPlayerScripts')")
    A("  local s = SPS:FindFirstChild('ILHA_NARUTO_Movel') or Instance.new('LocalScript'); s.Name = 'ILHA_NARUTO_Movel'")
    A("  s.Source = [==[")
    A("-- gerado pelo montar da ilha/portoes: gira/flutua as pecas com a tag IlhaMovel (so visual, no cliente).")
    A("-- Tudo e relativo ao pivo do Model dono (atributo movel_de): o Model pode ser movido com PivotTo.")
    A("local CS = game:GetService('CollectionService'); local RS = game:GetService('RunService')")
    A("local t0 = os.clock()")
    A("RS.RenderStepped:Connect(function()")
    A("  local t = os.clock() - t0")
    A("  for _, d in ipairs(CS:GetTagged('IlhaMovel')) do")
    A("    local dono = d:FindFirstAncestor(d:GetAttribute('movel_de') or '')")
    A("    local cf0, p, a = d:GetAttribute('cf0_rel'), d:GetAttribute('pivot_rel'), d:GetAttribute('axis_rel')")
    A("    if dono and cf0 and p and a and a.Magnitude > 0 then")
    A("      local ang = t * (d:GetAttribute('rpm') or 0) * math.pi / 30")
    A("      local amp, rate = d:GetAttribute('bob') or 0, d:GetAttribute('rate') or 0")
    A("      local bob")
    A("      if rate > 0 then  -- pilao: sobe devagar (70% do ciclo) e cai rapido (30%)")
    A("        local f = (t * rate) % 1")
    A("        bob = amp * ((f < 0.7) and (f / 0.7) or (1 - (f - 0.7) / 0.3))")
    A("      else")
    A("        bob = math.sin(t * 1.6 + p.X * 0.1) * amp")
    A("      end")
    A("      local r = CFrame.fromAxisAngle(a.Unit, ang)")
    A("      d.CFrame = dono:GetPivot() * (CFrame.new(p + Vector3.new(0, bob, 0)) * r * CFrame.new(-p) * cf0)")
    A("    end")
    A("  end")
    A("end)")
    A("]==]")
    A("  s.Parent = SPS end")
    A("print(string.format('%d pecas moveis marcadas (IlhaMovel)', nV))")
    A("-- ===== portoes de compra (LOCKED/UNLOCKED) =====")
    A("local nP = 0")
    A("for _, d in ipairs(root:GetDescendants()) do")
    A("  if d:IsA('MeshPart') then")
    A("    local k, part = string.match(d.Name, '^GATE_(%w+)_(%a+)')")
    A("    if k and (part == 'Barrier' or part == 'Lock' or part == 'OpenGlow') then")
    A("      if part == 'Barrier' then d.Transparency = 0.2 end   -- energia: da para ver o outro lado")
    A("      d:SetAttribute('gate', k); d:SetAttribute('gate_part', string.lower(part)); d:SetAttribute('t0', d.Transparency)")
    A("      if part == 'OpenGlow' then d.Transparency = 1 end")
    A("      CS:AddTag(d, 'PortaoCompra'); nP += 1 end")
    A("  elseif d:IsA('Part') and d.Parent == COLF then")
    A("    local k = string.match(d.Name, '^COL_Gate(%w-)Lock_')")
    A("    if k then d:SetAttribute('gate', k); d:SetAttribute('gate_part', 'lockcol'); CS:AddTag(d, 'PortaoCompra'); nP += 1")
    A("      local mdl = root:FindFirstChild('GATE_' .. k)   -- Model atomico do portao: bloqueio carrega junto")
    A("      if mdl and mdl:IsA('Model') then d.Parent = mdl end end")
    A("  end")
    A("end")
    A("do local RepS = game:GetService('ReplicatedStorage')")
    A("  local m = RepS:FindFirstChild('PortoesCompra') or Instance.new('ModuleScript'); m.Name = 'PortoesCompra'")
    A("  m.Source = [==[")
    A("-- gerado pelo montar da ilha/portoes. Estado de um portao de compra (DB, ShadowGarden, DemonSlayer, OnePiece,")
    A("-- OnePunchMan). No SERVIDOR vale para todos; num LocalScript vale so para aquele jogador (quem pagou).")
    A("--   require(game.ReplicatedStorage.PortoesCompra).Estado('DB', true)   -- desbloqueia")
    A("local CS = game:GetService('CollectionService')")
    A("local M = {}")
    A("local estado = {}   -- chave -> desbloqueado (sobrevive ao streaming: pecas que chegam depois recebem o estado)")
    A("local function aplicar(d)")
    A("  local chave = d:GetAttribute('gate'); local desb = estado[chave]")
    A("  if desb == nil then return end")
    A("  local p = d:GetAttribute('gate_part')")
    A("  if p == 'barrier' or p == 'lock' then d.Transparency = desb and 1 or (d:GetAttribute('t0') or 0)")
    A("  elseif p == 'openglow' then d.Transparency = desb and 0 or 1")
    A("  elseif p == 'lockcol' then d.CanCollide = not desb end")
    A("end")
    A("function M.Estado(chave, desbloqueado)")
    A("  estado[chave] = desbloqueado and true or false")
    A("  for _, d in ipairs(CS:GetTagged('PortaoCompra')) do if d:GetAttribute('gate') == chave then aplicar(d) end end")
    A("end")
    A("function M.Reaplicar() for _, d in ipairs(CS:GetTagged('PortaoCompra')) do aplicar(d) end end")
    A("CS:GetInstanceAddedSignal('PortaoCompra'):Connect(aplicar)")
    A("function M.Chaves() local s = {} for _, d in ipairs(CS:GetTagged('PortaoCompra')) do s[d:GetAttribute('gate')] = true end return s end")
    A("return M")
    A("]==]")
    A("  m.Parent = RepS end")
    A("print(string.format('%d pecas de portao de compra marcadas (PortaoCompra)', nP))")
    A("-- ===== guarda provisoria da ancora: a integracao da Ilha 2 APAGA estas pecas ao encostar a ponte seguinte =====")
    A("local nG = 0")
    A("for _, d in ipairs(root:GetDescendants()) do")
    A("  if (d:IsA('BasePart') or d:IsA('Model')) and (string.match(d.Name, '^EXIT_AnchorGuard') or string.match(d.Name, '^COL_ExitAnchorGuard_')) then")
    A("    d:SetAttribute('next_island_guard', true)")
    A("    d:SetAttribute('removed_by', 'integracao da Ilha 2 (ponte seguinte encosta em ISLAND_NEXT_ANCHOR)')")
    A("    CS:AddTag(d, 'GuardaProximaIlha'); nG += 1 end")
    A("end")
    A("print(string.format('%d pecas da guarda da ancora marcadas (GuardaProximaIlha)', nG))")
    return "\n".join(Lx)
