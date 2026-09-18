-- Authored Blender geometry, baked once per server through Roblox's DataModel content API.
-- The numeric mesh source persists in this project; opaque Content is recreated every session.
local AssetService=game:GetService('AssetService')
local RunService=game:GetService('RunService')
local SS=game:GetService('ServerStorage')
local HttpService=game:GetService('HttpService')
local M={}
local cached,oresInstalled

function M.buildAsset(name,data,palette)
 local editable=assert(AssetService:CreateEditableMesh(),'EditableMesh allocation failed: '..name)
 local ok,result=pcall(function()
  local lo,hi=Vector3.one*math.huge,-Vector3.one*math.huge
  for _,q in data.v do local v=Vector3.new(q[1],q[2],q[3]);lo=lo:Min(v);hi=hi:Max(v)end
  local center=(lo+hi)*.5
  local vertices,colors={},{}
  for i,q in data.v do vertices[i]=editable:AddVertex(Vector3.new(q[1],q[2],q[3])-center)end
  for i,q in palette do colors[i]=editable:AddColor(Color3.fromRGB(q[1],q[2],q[3]),1)end
  local triangles=0
  for i,t in data.f do
   local a,b,c=vertices[t[1]],vertices[t[2]],vertices[t[3]]
   local normal=(editable:GetPosition(b)-editable:GetPosition(a)):Cross(editable:GetPosition(c)-editable:GetPosition(a))
   if normal.Magnitude>1e-7 then
    local face=editable:AddTriangle(a,b,c);local color=assert(colors[t[4]],'Invalid palette index')
    editable:SetFaceColors(face,{color,color,color})
    local n=editable:AddNormal(normal.Unit);editable:SetFaceNormals(face,{n,n,n});triangles+=1
   end
   if i%1000==0 then task.wait()end
  end
  local status,content=AssetService:CreateDataModelContentAsync(Content.fromObject(editable))
  assert(status==Enum.CreateContentResult.Success,name..': '..tostring(status))
  local part=AssetService:CreateMeshPartAsync(content,{CollisionFidelity=Enum.CollisionFidelity.Box,RenderFidelity=Enum.RenderFidelity.Automatic})
  part.Name='Visual';part.Color=Color3.new(1,1,1);part.Material=Enum.Material.SmoothPlastic
  part.Anchored=true;part.CanCollide=false;part.CanTouch=false;part.CanQuery=false;part.DoubleSided=true
  part.CFrame=CFrame.new(center)
  local model=Instance.new('Model');model.Name=name;part.Parent=model;model.WorldPivot=CFrame.new()
  model:SetAttribute('BlenderTriangles',triangles);model:SetAttribute('AuthoredMesh',true)
  model:SetAttribute('AuthoredBoundsMin',lo);model:SetAttribute('AuthoredBoundsMax',hi)
  return model
 end)
 editable:Destroy()
 if not ok then error(result,2)end
 return result
end

function M.getKit()
 assert(RunService:IsRunning() and RunService:IsServer(),'Runtime kit is generated on the server')
 if cached and cached.Parent then return cached end
 local source=script.Parent:WaitForChild('ShadowGardenMeshData')
 local manifest=require(script.Parent.ShadowGardenLayout)
 local folder=Instance.new('Folder');folder.Name='ShadowGardenRuntimeKit'
 local began=os.clock()
 local ok,err=pcall(function()
  for _,name in manifest.assets do
   local item=assert(source:FindFirstChild(name),'Missing authored data: '..name)
   local data=HttpService:JSONDecode(item.Value)
   local model=M.buildAsset(name,data,manifest.palette);model.Parent=folder
  end
 end)
 if not ok then folder:Destroy();error(err,2)end
 folder:SetAttribute('GeneratedFromBlender',true);folder:SetAttribute('SessionGenerated',true)
 folder:SetAttribute('BuildSeconds',os.clock()-began);folder:SetAttribute('ModuleCount',#folder:GetChildren())
 folder.Parent=SS;cached=folder
 print(('[ShadowGarden] %d Blender meshes baked in %.2fs'):format(#folder:GetChildren(),os.clock()-began))
 return folder
end

function M.installOres(kit)
 if oresInstalled then return end
 local targets=SS:WaitForChild('Modelos')
 local mappings={comum={1,'Common'},incomum={2,'Uncommon'},raro={2,'Rare'},epica={3,'Epic'},lendaria={4,'Legendary'},chefe={5,'SuperLegendary'}}
 local replacements={}
 for variant,entry in mappings do
  local source=assert(kit:FindFirstChild('Minerio_'..entry[1]))
  local cf,size=source:GetBoundingBox();local scale=1/math.max(size.X,size.Y,size.Z)
  local result=Instance.new('Model');result.Name='minerio_sombra_'..variant
  for _,p in source:GetDescendants()do if p:IsA('MeshPart')then
   local copy=p:Clone();copy.Name='massa_minerio';copy.Size*=scale
   copy.CFrame=CFrame.new((p.Position-cf.Position+Vector3.new(0,size.Y/2,0))*scale)*p.CFrame.Rotation;copy.Parent=result
  end end
  result.WorldPivot=CFrame.new();result:SetAttribute('CoresProprias',true);result:SetAttribute('ShadowGardenPalette',true)
  result:SetAttribute('OreType','ShadowMana');result:SetAttribute('Rarity',entry[2]);table.insert(replacements,result)
 end
 for _,model in replacements do
  local old=targets:FindFirstChild(model.Name);if old then old:Destroy()end
  model.Parent=targets
 end
 oresInstalled=true
end
return M
