from pathlib import Path
root=Path(__file__).parent/'src'
def edit(p,fn):
 q=root/p;s=q.read_text(encoding='utf-8');q.write_text(fn(s),encoding='utf-8')
def replace(s,a,b):
 assert a in s,a[:80]
 return s.replace(a,b)
def theme(s):
 s=replace(s,'local poses={RightShoulder=Vector3.new(8,0,-5),LeftShoulder=Vector3.new(13,0,6),RightElbow=Vector3.new(18,0,0),LeftElbow=Vector3.new(28,0,0),Waist=Vector3.new(0,5,0),Neck=Vector3.new(-3,-5,0)}','''-- Articulated display poses, evaluated in the joint hierarchy. No floating whole-body loop.
 local profiles={
  muzan={right=7,left=-16,re=18,le=67,turn=-7,head=9},
  goku={right=-27,left=-19,re=58,le=48,turn=7,head=-7},
  vegeta={right=-23,left=-28,re=63,le=57,turn=-8,head=8},
  saitama={right=4,left=-8,re=12,le=32,turn=-4,head=5},
  tanjiro={right=-19,left=-12,re=41,le=33,turn=6,head=-6},
 }
 local function poseFor(id)
  local p=profiles[id] or {right=4,left=-12,re=16,le=36,turn=-5,head=6}
  return {RightShoulder=Vector3.new(p.right,0,-7),LeftShoulder=Vector3.new(p.left,0,9),RightElbow=Vector3.new(p.re,0,0),LeftElbow=Vector3.new(p.le,0,0),Waist=Vector3.new(-1,p.turn,0),Neck=Vector3.new(-2,p.head,0)}
 end''')
 s=replace(s,'local model=original:Clone();model.Name=id','local model=original:Clone();model.Name=id\n   local poses=poseFor(id)')
 s=replace(s,'d.Anchored=d==root;d.CanCollide=false;d.CanTouch=false;d.CanQuery=false','d.Anchored=true;d.CanCollide=false;d.CanTouch=false;d.CanQuery=false')
 start=s.index('   for _,d in ipairs(model:GetDescendants()) do\n    if d:IsA("AnimationConstraint")',s.index('function T.characterViewport'))
 end=s.index('   local range=',start)
 s=s[:start]+'''   -- Anchor the display rig and solve FK explicitly. AnimationConstraint simulation is not
   -- reliable in every ViewportFrame; evaluating both rig formats produces the same pose.
   local unordered={}
   for _,joint in ipairs(model:GetDescendants()) do
    local p0,p1,c0,c1
    if joint:IsA("Motor6D") or joint:IsA("Weld") then
     p0,p1,c0,c1=joint.Part0,joint.Part1,joint.C0,joint.C1
    elseif joint:IsA("AnimationConstraint") and joint.Attachment0 and joint.Attachment1 then
     p0,p1,c0,c1=joint.Attachment0.Parent,joint.Attachment1.Parent,joint.Attachment0.CFrame,joint.Attachment1.CFrame
     joint.Enabled=false
    end
    if p0 and p1 and p0:IsA("BasePart") and p1:IsA("BasePart") then
     local a=poses[joint.Name] or Vector3.zero
     table.insert(unordered,{name=joint.Name,p0=p0,p1=p1,c0=c0,c1=c1:Inverse(),pose=CFrame.Angles(math.rad(a.X),math.rad(a.Y),math.rad(a.Z))})
    end
   end
   local known={[root]=true};local ordered={}
   for _=1,20 do
    local progress=false
    for i=#unordered,1,-1 do
     local j=unordered[i]
     if known[j.p0] then known[j.p1]=true;table.insert(ordered,j);table.remove(unordered,i);progress=true end
    end
    if not progress then break end
   end
   -- Accessory meshes follow their attachment welds after their parent bone.
   for _,j in ipairs(ordered) do j.p1.CFrame=j.p0.CFrame*j.c0*j.pose*j.c1 end
   table.insert(animatedModels,{model=model,root=root,joints=ordered,phase=index*.85})
''' + s[end:]
 start=s.index('   local t=elapsed*1.65+entry.phase',s.index('local idle=Run.RenderStepped'))
 end=s.index('\n  end\n end)',start)
 s=s[:start]+'''   local t=elapsed+entry.phase
   local motion=T.motionEnabled()
   local breath=motion and math.sin(t*1.45) or 0
   local glance=motion and math.sin(t*.34)*math.sin(t*.34) or 0
   for _,j in ipairs(entry.joints) do
    local delta=CFrame.identity
    if j.name=="Waist" then delta=CFrame.Angles(math.rad(breath*.65),0,0)
    elseif j.name=="Neck" then delta=CFrame.Angles(math.rad(-breath*.35),math.rad(glance*3.5),0)
    elseif j.name=="LeftShoulder" then delta=CFrame.Angles(math.rad(breath*.8),0,math.rad(breath*.3))
    elseif j.name=="RightShoulder" then delta=CFrame.Angles(math.rad(breath*.55),0,math.rad(-breath*.3))
    elseif j.name=="LeftElbow" then delta=CFrame.Angles(math.rad(breath*.9),0,0) end
    if j.p0.Parent and j.p1.Parent then j.p1.CFrame=j.p0.CFrame*j.c0*j.pose*delta*j.c1 end
   end''' + s[end:]
 s=s.replace('v:SetAttribute("IdleAnimation","BreathingPose")','v:SetAttribute("IdleAnimation","ArticulatedDisplayPose")')
 # Use the reference's luminous dark borders and layered header instead of a flat sticker.
 a=s.index(' local ring=T.image(p,"MiningCrest"',s.index('function T.headerOrnament'))
 b=s.index('\n return plate',a)
 s=s[:a]+''' local dark=col:Lerp(P.ink,.70)
 local rim=T.image(p,"CrestOutline",T.Assets.crest,-17,-15,h+30,h+30,P.ink,0)
 local ring=T.image(p,"MiningCrest",T.Assets.crest,-14,-12,h+24,h+24,col:Lerp(P.ink,.38),0)
 local shadow=T.slant(p,"HeaderOutline",-8,-2,w+4,h+4,P.ink,{tilt=18})
 local plate=T.slant(p,"TitlePlate",-6,0,w,h,col,{top=col:Lerp(WHITE,.12),bottom=col:Lerp(P.ink,.38),tilt=18})
 T.slant(p,"TitleInset",-3,3,w-9,h-6,col,{top=col,bottom=col:Lerp(P.ink,.28),tilt=18,alpha=.35})
 T.frame(p,"TitleEdge",6,1,w-24,1,col:Lerp(WHITE,.48),.12)
 local tail=T.image(p,"WindTailOutline",T.Assets.pattern,w-82,h-36,88,60,P.ink,.05);tail.Rotation=-12
 local curl=T.image(p,"WindTail",T.Assets.pattern,w-79,h-33,82,54,dark,.02);curl.Rotation=-12
''' + s[b:]
 s=s.replace('T.gradient(f,col:Lerp(P.ink,.20),col:Lerp(P.ink,.46),90)','T.gradient(f,col:Lerp(WHITE,.10),col:Lerp(P.ink,.32),90)')
 s=s.replace('T.texture(f,"pattern",.61,col:Lerp(WHITE,.38),128)','T.texture(f,"pattern",.48,col:Lerp(WHITE,.45),128)')
 # Reference bevel: restrained charcoal face, clear inner keyline, short lower ledge.
 s=s.replace('local light=T.frame(face,"TopLight",3,2,w-6,1,WHITE,.65)','local light=T.frame(face,"TopLight",3,2,w-6,1,WHITE,.50)\n local lower=T.frame(face,"LowerEdge",3,h-4,w-6,2,P.ink,.15)')
 s=s.replace('ColorSequenceKeypoint.new(.47,used:Lerp(P.ink,.18))','ColorSequenceKeypoint.new(.48,used:Lerp(P.ink,.12)),ColorSequenceKeypoint.new(.51,used:Lerp(P.ink,.25))')
 return s
edit('ReplicatedStorage/ExpeditionUI/Theme.lua',theme)
edit('ReplicatedStorage/ExpeditionUI/Inventory.lua',lambda s:s.replace('P.bg0:Lerp(r.cor,.18)','P.bg0:Lerp(r.cor,.48)').replace('T.texture(wash,"pattern",.96,r.cor:Lerp(WHITE,.3),260)','T.texture(wash,"pattern",.975,r.cor:Lerp(WHITE,.3),260)'))
edit('ReplicatedStorage/ExpeditionUI/Menus.lua',lambda s:s.replace('require(RS.UIPreferences)','require(game.ReplicatedStorage.UIPreferences)'))
edit('StarterPlayer/StarterPlayerScripts/ExpeditionClient.lua',lambda s:s.replace('AutoSell = { "Mochila cheia", "Teleporte grátis até o Ignis para vender, ou deixe o Auto Sell vender sozinho.", "AutoSell"','PortableForge = { "Mochila cheia", "Venda gratuitamente no Ignis ou use a forja portátil onde estiver.", "PortableForge"').replace('ou aumente o inventário para 100.','ou adicione mais espaços ao inventário.'))
print('Articulated previews and visual treatment ready.')
