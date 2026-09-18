-- Diagnóstico somente leitura, para execute_luau no Client Play.
-- Não cria instâncias, não escreve preferências e não chama remotes.
local p=game:GetService('Players').LocalPlayer
local screen=p and p.PlayerGui:FindFirstChild('ExpeditionUI')
if not screen then return {ready=false} end
local function rect(o)
 return {x=o.AbsolutePosition.X,y=o.AbsolutePosition.Y,w=o.AbsoluteSize.X,h=o.AbsoluteSize.Y}
end
local function shown(o)
 local n=o
 while n and n~=screen do
  if n:IsA('GuiObject') and not n.Visible then return false end
  n=n.Parent
 end
 return true
end
local r={ready=true,page=screen:GetAttribute('OpenPage'),popup=screen:GetAttribute('PopupOpen'),viewport=tostring(workspace.CurrentCamera.ViewportSize),screen=rect(screen),screens={},buttons={},smallTouchTargets={},textOverflow={},images={}}
for _,g in ipairs(p.PlayerGui:GetChildren()) do if g:IsA('ScreenGui') then table.insert(r.screens,{name=g.Name,enabled=g.Enabled}) end end
local touch=game:GetService('UserInputService').TouchEnabled
local layer=screen.Canvas.ModalLayer:FindFirstChild('Window')
if layer then r.window=rect(layer);r.body=rect(layer.Body) end
for _,o in ipairs(screen:GetDescendants())do
 if o:IsA('GuiObject') and shown(o) then
  if o:IsA('GuiButton') then
   local v=rect(o);v.name=o.Name;v.disabled=o:GetAttribute('Disabled');table.insert(r.buttons,v)
   if touch and not v.disabled and math.min(v.w,v.h)<43.5 then table.insert(r.smallTouchTargets,v) end
  elseif o:IsA('ImageLabel') and o.Image~='' then
   table.insert(r.images,{name=o.Name,loaded=o.IsLoaded})
  elseif o:IsA('TextLabel') and o.Text~='' and not o.TextScaled and not o.TextWrapped then
   if o.TextBounds.X>o.AbsoluteSize.X+2 or o.TextBounds.Y>o.AbsoluteSize.Y+2 then table.insert(r.textOverflow,{name=o.Name,text=o.Text,bounds=tostring(o.TextBounds),size=tostring(o.AbsoluteSize)}) end
  end
 end
end
return r
