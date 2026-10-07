-- Run after importing export/shadowgarden_kit.fbx as LSation. Does not save/publish the place.
local SS=game:GetService('ServerStorage')
local src=workspace:FindFirstChild('shadowgarden_kit') or SS:FindFirstChild('ShadowGardenImportSource')
assert(src,'Importe shadowgarden_kit.fbx no Studio primeiro')
local kit=Instance.new('Folder');kit.Name='ShadowGardenKit'
local count=0
for _,model in src:GetChildren()do
 if model:IsA('Model')and model.Name:sub(1,2)=='K_'then
  local m=model:Clone();m.Name=model.Name:sub(3)
  local origin
  for _,p in m:GetDescendants()do
   if p:IsA('BasePart')then
    p.Anchored=true;p.CanCollide=false;p.CanTouch=false;p.CanQuery=false
    if p.Name:find('__origem',1,true)then origin=p.Position;p:Destroy()
    elseif p:IsA('MeshPart')then p.Color=Color3.new(1,1,1);p.Material=Enum.Material.SmoothPlastic;p.DoubleSided=true end
   end
  end
  assert(origin,'Marcador de origem ausente: '..m.Name)
  local meshCount=0
  for _,p in m:GetDescendants()do if p:IsA('MeshPart')then
   local static=p.MeshId:match('^rbxassetid://%d+$') or p.MeshId:match('^https?://www%.roblox%.com/asset/%?id=%d+')
   assert(static,'Malha sem ID publicado: '..m.Name)
   meshCount+=1
  end end
  assert(meshCount>0,'Modelo sem MeshPart: '..m.Name)
  m.WorldPivot=CFrame.new(origin);m:PivotTo(CFrame.new());m.Parent=kit;count+=1
 end
end
assert(count==61,'Importacao diferente do kit esperado: '..count..'/61 modelos')
local old=SS:FindFirstChild('ShadowGardenKit');if old then old.Name='ShadowGardenKit_Previous_'..os.time()end
kit:SetAttribute('ImportedFromBlender',true);kit:SetAttribute('ModuleCount',count);kit.Parent=SS
src.Name='ShadowGardenImportSource';src.Parent=SS
-- Normalize ore visuals to the 1-unit template convention expected by AreaBuilder:ScaleTo.
local oldOres=Instance.new('Folder');oldOres.Name='BeforeShadowOres_'..os.time();oldOres.Parent=SS
local mappings={comum={1,'Common'},incomum={2,'Uncommon'},raro={2,'Rare'},epica={3,'Epic'},lendaria={4,'Legendary'},chefe={5,'SuperLegendary'}}
for variant,entry in mappings do
 local source=kit:FindFirstChild('Minerio_'..entry[1]);assert(source)
 local cf,size=source:GetBoundingBox();local scale=1/math.max(size.X,size.Y,size.Z)
 local result=Instance.new('Model');result.Name='minerio_sombra_'..variant
 for _,p in source:GetDescendants()do if p:IsA('MeshPart')then
  local copy=p:Clone();copy.Name='massa_minerio';copy.Size*=scale
  copy.CFrame=CFrame.new((p.Position-cf.Position+Vector3.new(0,size.Y/2,0))*scale)*p.CFrame.Rotation;copy.Parent=result
 end end
 result.WorldPivot=CFrame.new();result:SetAttribute('CoresProprias',true);result:SetAttribute('ShadowGardenPalette',true);result:SetAttribute('OreType','ShadowMana');result:SetAttribute('Rarity',entry[2])
 local old=SS.Modelos:FindFirstChild(result.Name);if old then old.Parent=oldOres end
 result.Parent=SS.Modelos
end
print('[ShadowGarden] kit estatico pronto:',count,'modelos. Inicie Play para validar a Area4.')
