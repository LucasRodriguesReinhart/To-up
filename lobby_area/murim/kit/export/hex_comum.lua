-- hex_comum.lua : constants + helpers shared by hex_fase0..9 (returns H). No accents.
local H = {}
local SS = game:GetService("ServerStorage")
local CHS = game:GetService("ChangeHistoryService")
local L = workspace:WaitForChild("LOBBY_MURIM")
local Y = Vector3.yAxis
H.L, H.SS, H.Y = L, SS, Y
H.LIB = SS:WaitForChild("BIBLIOTECA_MURIM")
H.COL = L:WaitForChild("Colisao")
local rgb = Color3.fromRGB
H.C = {pav=rgb(220,198,166), junta=rgb(168,148,120), borda=rgb(160,146,138), faixa=rgb(156,143,128),
 linha=rgb(238,209,174), anel=rgb(123,111,102), ouro=rgb(224,176,74), creme=rgb(216,204,191), cremeS=rgb(203,191,178),
 laca=rgb(184,50,42), muro=rgb(165,48,47), vinho=rgb(124,37,44), grade=rgb(167,59,60), teal=rgb(30,75,83),
 pedra=rgb(140,140,140), terra=rgb(91,70,54), leito=rgb(31,78,85), agua=rgb(46,150,168), madeira=rgb(90,58,42),
 fora=rgb(143,133,112), carpete=rgb(168,38,42), luz=rgb(255,176,96), orbe=rgb(255,179,71), musgo=rgb(110,157,72),
 leao=rgb(142,144,150), lirio=rgb(111,179,92), pilar=rgb(128,124,118), cascata=rgb(207,239,245),
 janela=rgb(58,30,30), treino=rgb(198,155,120)}
H.PAVING_MATERIAL = Enum.Material.Pavement   -- F2 capture test may switch to SmoothPlastic (+ secondary rings)

-- hexagon faces: apothem 150, flat faces at +/-Z; s along t, d = inward distance from wall centre line
local function face(th) local c,s=math.cos(math.rad(th)),math.sin(math.rad(th))
  return {th=th, M=Vector3.new(150*c,0,150*s), n=Vector3.new(c,0,s), t=Vector3.new(-s,0,c), inw=Vector3.new(-c,0,-s)} end
H.FACES = {FR=face(30), F=face(90), FL=face(150), BL=face(210), B=face(270), BR=face(330)}
function H.fp(f,s,d,y) local F=H.FACES[f] return F.M+F.t*s+F.inw*d+Vector3.new(0,y or 0,0) end
function H.faceCF(f,s,d,y) local F=H.FACES[f] return CFrame.fromMatrix(H.fp(f,s,d,y),F.t,Y) end -- local X=along, local +Z=inward

function H.folder(p,n) local f=p:FindFirstChild(n) if not f then f=Instance.new("Folder") f.Name=n f.Parent=p end return f end
function H.clear(f) for _,c in ipairs(f:GetChildren()) do c:Destroy() end end -- ONLY HEX_* folders
function H.clearColliders(pre) for _,c in ipairs(H.COL:GetChildren()) do
  if c.Name:sub(1,#pre)==pre and c:GetAttribute("HexCollider") then c:Destroy() end end end
local function copy(o) local q={} for k,v in pairs(o) do q[k]=v end return q end
function H.part(o,parent)
  local p=Instance.new(o.Class or "Part") p.Anchored=true
  if o.Shape then p.Shape=o.Shape end
  p.Material=o.Material or Enum.Material.SmoothPlastic
  p.TopSurface=Enum.SurfaceType.Smooth p.BottomSurface=Enum.SurfaceType.Smooth
  p.Size=o.Size p.CFrame=o.CFrame p.Color=o.Color or Color3.new(1,1,1)
  p.Transparency=o.Transparency or 0 p.Reflectance=o.Reflectance or 0
  p.CanCollide=o.CanCollide==true p.CanQuery=o.CanCollide==true p.CanTouch=false
  p.CastShadow=o.CastShadow==true p.Name=o.Name or "hx" p:SetAttribute("HexGen",true) p.Parent=parent return p end
function H.collider(name,size,cf,class)
  local p=Instance.new(class or "Part") p.Name=name p.Anchored=true p.Size=size p.CFrame=cf
  p.Transparency=1 p.CanCollide=true p.CanTouch=false p.CanQuery=false p.CastShadow=false
  p:SetAttribute("HexCollider",true) p.Parent=H.COL return p end

-- WedgePart orientation self-test (temporary part, destroyed immediately)
function H.selfTest()
  local t=Instance.new("WedgePart") t.Anchored=true t.Size=Vector3.new(4,2,6) t.CFrame=CFrame.new(0,500,0) t.Parent=workspace
  local rp=RaycastParams.new() rp.FilterType=Enum.RaycastFilterType.Include rp.FilterDescendantsInstances={t}
  local hb=workspace:Raycast(Vector3.new(0,510,2.5),Vector3.new(0,-20,0),rp)
  local hf=workspace:Raycast(Vector3.new(0,510,-2.5),Vector3.new(0,-20,0),rp)
  t:Destroy() assert(hb and hf,"wedge self-test: raycast missed")
  H.SIGN=(hb.Position.Y>hf.Position.Y) and 1 or -1 -- 1 = tall at local +Z (expected)
  return H.SIGN end
-- flat right triangle: right angle at C, leg a (unit, horizontal) length la, leg b length lb
function H.rightTri(parent,o,C,a,la,b,lb,topY,thick)
  assert(H.SIGN,"call H.selfTest() first")
  local c=C+a*(la/2)+b*(lb/2) local q=copy(o)
  q.Class="WedgePart" q.Size=Vector3.new(thick,la,lb)
  q.CFrame=CFrame.fromMatrix(Vector3.new(c.X,topY-thick/2,c.Z), -H.SIGN*a:Cross(b), a)
  return H.part(q,parent) end
function H.checkTri(w,C,a,la,b,lb,topY)
  local prev=w.CanQuery w.CanQuery=true
  local rp=RaycastParams.new() rp.FilterType=Enum.RaycastFilterType.Include rp.FilterDescendantsInstances={w}
  local pi=C+a*(0.25*la)+b*(0.25*lb) local po=C+a*(0.75*la)+b*(0.75*lb)
  local hi=workspace:Raycast(Vector3.new(pi.X,topY+5,pi.Z),Vector3.new(0,-20,0),rp)
  local ho=workspace:Raycast(Vector3.new(po.X,topY+5,po.Z),Vector3.new(0,-20,0),rp)
  if not w.CanCollide then w.CanQuery=prev end
  return hi~=nil and math.abs(hi.Position.Y-topY)<0.05 and ho==nil end
function H.hexPrism(parent,o,ap,y0,y1,cx,cz)
  cx,cz=cx or 0,cz or 0 local R=ap/0.8660254 local h=y1-y0
  local q=copy(o) q.Size=Vector3.new(R,h,2*ap) q.CFrame=CFrame.new(cx,(y0+y1)/2,cz) H.part(q,parent)
  for _,sx in ipairs({1,-1}) do for _,sz in ipairs({1,-1}) do
    H.rightTri(parent,o,Vector3.new(cx+sx*R/2,0,cz),Vector3.new(sx,0,0),R/2,Vector3.new(0,0,sz),ap,y1,h) end end end
local T30=math.tan(math.rad(30))
function H.hexRing(parent,o,a1,a2,y0,y1,gaps) -- gaps[theta]={{s1,s2},...}
  local h,w=y1-y0,a2-a1
  for _,th in ipairs({30,90,150,210,270,330}) do
    local c,s=math.cos(math.rad(th)),math.sin(math.rad(th)) local n,t=Vector3.new(c,0,s),Vector3.new(-s,0,c)
    local half=a1*T30 local cuts={{-half,half}}
    for _,g in ipairs((gaps or {})[th] or {}) do local nc={} for _,iv in ipairs(cuts) do
      if g[2]<=iv[1] or g[1]>=iv[2] then table.insert(nc,iv) else
        if g[1]>iv[1] then table.insert(nc,{iv[1],g[1]}) end
        if g[2]<iv[2] then table.insert(nc,{g[2],iv[2]}) end end end cuts=nc end
    for _,iv in ipairs(cuts) do local q=copy(o) local mid=n*((a1+a2)/2)+t*((iv[1]+iv[2])/2)
      q.Size=Vector3.new(iv[2]-iv[1],h,w) q.CFrame=CFrame.fromMatrix(mid+Vector3.new(0,(y0+y1)/2,0),t,Y) H.part(q,parent) end
    for _,sg in ipairs({1,-1}) do H.rightTri(parent,o,n*a2+t*(sg*half),t*sg,w*T30,-n,w,y1,h) end end end
function H.faceRect(parent,o,f,s1,s2,d1,d2,y0,y1)
  local q=copy(o) q.Size=Vector3.new(s2-s1,y1-y0,d2-d1) q.CFrame=H.faceCF(f,(s1+s2)/2,(d1+d2)/2,(y0+y1)/2)
  return H.part(q,parent) end

-- originals, placement, removal
function H.remember(i)
  if i:GetAttribute("CF0")==nil then i:SetAttribute("CF0", i:IsA("Model") and i:GetPivot() or i.CFrame) end
  if i:IsA("BasePart") and i:GetAttribute("S0")==nil then i:SetAttribute("S0", i.Size) end end
function H.cf0(i) H.remember(i) return i:GetAttribute("CF0") end
function H.s0(i) H.remember(i) return i:GetAttribute("S0") end
function H.setCF(i,cf) if i:IsA("Model") then i:PivotTo(cf) else i.CFrame=cf end end
function H.placeRigid(i,T,pre) H.setCF(i, T*(pre or CFrame.identity)*H.cf0(i)) end
H.REM=H.folder(SS,"LOBBY_REMOVIDOS_HEX")
function H.remove(i,fase) if not i or i:IsDescendantOf(H.REM) then return false end
  if i:GetAttribute("OrigemPath")==nil then i:SetAttribute("OrigemPath", i.Parent:GetFullName()) end
  H.remember(i) i.Parent=H.folder(H.REM,fase) return true end
local function posOf(i) local cf=i:GetAttribute("CF0") if cf then return cf.Position end
  return i:IsA("Model") and i:GetPivot().Position or i.Position end
function H.findAll(parents,name,pos,tol) tol=tol or 0.3 local r={}
  for _,p in ipairs(parents) do for _,c in ipairs(p:GetChildren()) do
    if c.Name==name and (posOf(c)-pos).Magnitude<=tol then table.insert(r,c) end end end return r end
function H.find(parents,name,pos,tol) local r=H.findAll(parents,name,pos,tol)
  assert(#r==1,("find %s @%s -> %d"):format(name,tostring(pos),#r)) return r[1] end
function H.libClone(fam,name,parent) local c=H.LIB[fam][name]:Clone() c.Anchored=true
  c.CanCollide=false c.CanTouch=false c.CanQuery=false
  for k in pairs(c:GetAttributes()) do c:SetAttribute(k,nil) end c:SetAttribute("HexGen",true) c.Parent=parent return c end
function H.fixBal(seg) local cf0,s0=H.cf0(seg),H.s0(seg) -- balustrade 3.4 tall, same bottom
  seg.Size=Vector3.new(s0.X,3.4,s0.Z) seg.CFrame=seg.CFrame+Vector3.new(0,(cf0.Y-s0.Y/2+1.7)-seg.CFrame.Y,0) end
H.TG=CFrame.new(114.43,0,-52.21)*CFrame.Angles(0,math.rad(30),0)*CFrame.new(-125,0,0)
H.TS=CFrame.new(-121.35,0,-56.21)*CFrame.Angles(0,math.rad(-30),0)*CFrame.new(117,0,4)
H.TT=CFrame.new(-135,1.2,0)*CFrame.Angles(0,math.rad(-90),0)*CFrame.new(86,0,-38)
function H.shopOrig(u,y,v) return CFrame.new(-117+u,y,-4+v) end
function H.ramp(name,center,width,rise,run,dirLow,T) -- invisible stair/ramp collider
  local look=(H.SIGN==1) and dirLow or -dirLow
  local cf=CFrame.lookAt(center,center+look) if T then cf=T*cf end
  return H.collider(name,Vector3.new(width,rise,run),cf,"WedgePart") end
function H.boxLantern(parent,name,base) -- base = floor point; total height ~6.4
  local m=Instance.new("Model") m.Name=name m.Parent=parent local y=base.Y
  local function P(n,sz,dy,col,mat,coll,shape) return H.part({Name=n,Size=sz,CFrame=CFrame.new(base.X,y+dy,base.Z),
    Color=col,Material=mat,CanCollide=coll,Shape=shape},m) end
  P("Plinto",Vector3.new(1.8,1.3,1.8),0.55,H.C.pedra,Enum.Material.Slate,true)
  P("Poste",Vector3.new(0.9,2.4,0.9),2.4,H.C.creme)
  local body=P("Corpo",Vector3.new(1.8,1.6,1.8),4.4,H.C.luz,Enum.Material.Neon)
  for _,o in ipairs({{0.85,0.85},{0.85,-0.85},{-0.85,0.85},{-0.85,-0.85}}) do
    H.part({Name="Haste",Size=Vector3.new(0.25,1.6,0.25),CFrame=CFrame.new(base.X+o[1],y+4.4,base.Z+o[2]),Color=rgb(74,42,30)},m) end
  P("Capa",Vector3.new(2.4,0.3,2.4),5.35,H.C.teal) P("Topo",Vector3.new(1.2,0.4,1.2),5.7,H.C.teal)
  P("Botao",Vector3.new(0.5,0.5,0.5),6.15,H.C.ouro,Enum.Material.Metal,false,Enum.PartType.Ball)
  local l=Instance.new("PointLight") l.Range=12 l.Brightness=1.2 l.Color=H.C.luz l.Shadows=false l.Parent=body
  return m end
function H.begin(n) local ok,id=pcall(function() return CHS:TryBeginRecording(n) end) return ok and id or nil end
function H.commit(id) if id then CHS:FinishRecording(id,Enum.FinishRecordingOperation.Commit) end end

-- master layout constants
H.LAY = {
 PONDS = {
  FL={face="FL", s1=-52, s2=12, d1=10, d2=34, bridgeS=0,  benchS=-30, benchD=39},
  FR={face="FR", s1=4,   s2=52, d1=10, d2=32, bridgeS=16, benchS=34,  benchD=37} },
 PLANTERS = {Vector3.new(23.5,0,40.7),Vector3.new(-23.5,0,40.7),Vector3.new(-23.5,0,-40.7),Vector3.new(23.5,0,-40.7)}, -- FR,FL,BL,BR
 FORGE_BEDS = {Vector3.new(47,0,-86.9),Vector3.new(-47,0,-86.9)},
 FORGE_LIONS = {Vector3.new(31,0,-69),Vector3.new(-31,0,-69)}, GATE_LIONS = {Vector3.new(38,0,172),Vector3.new(-38,0,172)},
 FLOOR_LANTERNS = {H.TG*Vector3.new(86.9,0,13.6),H.TG*Vector3.new(86.9,0,-13.6),H.TS*Vector3.new(-73.8,0,-13.4),H.TS*Vector3.new(-73.8,0,5.4)},
}
-- segment clipping against oriented rectangles (joints)
function H.zoneRect(cf,hx,hz,m) m=m or 0.3 return {cf=cf,hx=hx+m,hz=hz+m} end
function H.clipSegment(p0,p1,zones) local iv={}
  for _,z in ipairs(zones) do
    local a=z.cf:PointToObjectSpace(Vector3.new(p0.X,z.cf.Y,p0.Z)) local b=z.cf:PointToObjectSpace(Vector3.new(p1.X,z.cf.Y,p1.Z))
    local t0,t1,ok=0,1,true
    for _,ax in ipairs({{a.X,b.X,z.hx},{a.Z,b.Z,z.hz}}) do local s,e,h=ax[1],ax[2],ax[3] local d=e-s
      if math.abs(d)<1e-9 then if math.abs(s)>h then ok=false end
      else local ta,tb=(-h-s)/d,(h-s)/d if ta>tb then ta,tb=tb,ta end t0=math.max(t0,ta) t1=math.min(t1,tb) end end
    if ok and t0<t1 then table.insert(iv,{t0,t1}) end end
  table.sort(iv,function(u,v) return u[1]<v[1] end)
  local out,cur={},0 for _,v in ipairs(iv) do if v[1]>cur then table.insert(out,{cur,v[1]}) end cur=math.max(cur,v[2]) end
  if cur<1 then table.insert(out,{cur,1}) end return out end
function H.jointStrip(parent,p0,p1,zones) local len=(p1-p0).Magnitude local dir=(p1-p0).Unit
  for _,iv in ipairs(H.clipSegment(p0,p1,zones)) do local Ls=(iv[2]-iv[1])*len
    if Ls>=2 then local a=p0+dir*(iv[1]*len) local b=p0+dir*(iv[2]*len) local mid=(a+b)/2
      H.part({Name="Junta",Size=Vector3.new(0.5,0.15,Ls),CFrame=CFrame.lookAt(Vector3.new(mid.X,0.025,mid.Z),Vector3.new(b.X,0.025,b.Z)),
        Color=H.C.junta},parent) end end end
function H.zones() local Z={} local function add(cf,hx,hz) table.insert(Z,H.zoneRect(cf,hx,hz)) end
  add(CFrame.new(0,0,92),15,58) add(CFrame.new(0,0,-47.5),15,13.5) add(CFrame.new(0,0,-75.65),25,14.65)
  add(CFrame.fromMatrix(Vector3.new(59.13,0,-20.28),Vector3.new(0.5,0,0.866025),Y),7.5,27.35)
  add(CFrame.fromMatrix(Vector3.new(-60.08,0,-20.83),Vector3.new(0.5,0,-0.866025),Y),7.5,28.45)
  add(CFrame.new(0,0,-121.05),62.5,31.45) add(H.TG*CFrame.new(125,0,0),21.5,45.5) add(H.TG*CFrame.new(96.3,0,0),7.8,11.4)
  add(H.TG*CFrame.new(100,0,48),1.8,1.8) add(H.TG*CFrame.new(100,0,-48),1.8,1.8)
  add(H.TS*CFrame.new(-117,0,-4),13.5,20.5) add(H.TS*CFrame.new(-98.6,0,-4),5.45,13) add(H.TS*CFrame.new(-84.2,0,-4),9.5,7.6)
  add(H.TS*H.shopOrig(16,0,22),1.4,1.4) add(H.TS*H.shopOrig(16,0,-22),1.4,1.4) add(CFrame.new(-135,0,0),20,16)
  for _,P in pairs(H.LAY.PONDS) do
    add(H.faceCF(P.face,(P.s1+P.s2)/2,(P.d1+P.d2)/2,0),(P.s2-P.s1)/2,(P.d2-P.d1)/2)
    add(H.faceCF(P.face,P.bridgeS,(P.d2+10)/2,0),6.5,(P.d2-2)/2+1.5)
    add(H.faceCF(P.face,P.benchS,P.benchD,0),4.15,1.2) end
  for _,p in ipairs(H.LAY.PLANTERS) do add(CFrame.lookAt(p,Vector3.zero),3.7,3.7) end
  for _,p in ipairs(H.LAY.FORGE_BEDS) do add(CFrame.new(p),13,2.5) end
  for _,p in ipairs(H.LAY.FORGE_LIONS) do add(CFrame.new(p),3,3.3) end
  for _,p in ipairs(H.LAY.FLOOR_LANTERNS) do add(CFrame.new(p.X,0,p.Z),0.9,0.9) end
  return Z end
return H
