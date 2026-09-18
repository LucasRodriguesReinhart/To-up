from pathlib import Path
p=Path(__file__).parent/'src'
f=p/'ReplicatedStorage/ExpeditionUI/Theme.lua';s=f.read_text(encoding='utf-8')
a='im.ImageRectOffset=cells[key];im.ImageRectSize=Vector2.new(512,512)\n  return im'
b='''im.ImageRectOffset=cells[key];im.ImageRectSize=Vector2.new(512,512)
  local index=T.IconIndex[key] or T.IconIndex[key=="dano" and "pickaxe" or "items"] or 0
  local fallback=T.image(im,"AssetFallback",T.Assets.icons,0,0,0,0)
  fallback.Size=UDim2.fromScale(1,1)
  fallback.ImageRectOffset=Vector2.new((index%4)*256,math.floor(index/4)*256)
  fallback.ImageRectSize=Vector2.new(256,256)
  local function sync() fallback.Visible=not im.IsLoaded end
  sync();im:GetPropertyChangedSignal("IsLoaded"):Connect(sync)
  return im'''
assert a in s;s=s.replace(a,b)
s=s.replace('frameCamera();v:GetPropertyChangedSignal("AbsoluteSize"):Connect(frameCamera)','frameCamera();v:GetPropertyChangedSignal("AbsoluteSize"):Connect(frameCamera)\n v.ImageTransparency=1;task.delay(.18,function() if v.Parent then T.tween(v,.16,{ImageTransparency=0}) end end)')
f.write_text(s,encoding='utf-8')
f=p/'ReplicatedStorage/ExpeditionUI/Notify.lua';s=f.read_text(encoding='utf-8')
for var,col,tail in [('f','k.col','90'),('f','col','0'),('root','col','90')]:
 a=f'T.gradient({var},{col}:Lerp(P.ink,.77),P.bg0,{tail})' if col=='k.col' else f'T.gradient({var},{col}:Lerp(P.ink,.80),P.bg0,{tail})'
 b=f'local bg=T.frame({var},"TintedBackdrop",0,0,0,0,Color3.new(1,1,1),0);bg.Size=UDim2.fromScale(1,1);T.corner(bg,6);T.gradient(bg,{col}:Lerp(P.ink,.65),P.bg0,{tail})'
 assert a in s,a;s=s.replace(a,b)
f.write_text(s,encoding='utf-8')
f=p/'ReplicatedStorage/ExpeditionUI/Menus.lua';s=f.read_text(encoding='utf-8').replace('thumbW - 18, 44, narrow and 19 or 23','thumbW - 18, thumbH-12, (narrow or ctx.compact) and 17 or 21')
f.write_text(s,encoding='utf-8')
f=p/'StarterPlayer/StarterPlayerScripts/ExpeditionClient.lua';s=f.read_text(encoding='utf-8')
# Travel already presents the destination; avoid a second notice underneath it.
s=s.replace('"Viagem concluída"','""')
f.write_text(s,encoding='utf-8')
print('Fallback, canvas tint and framing refinements complete')
