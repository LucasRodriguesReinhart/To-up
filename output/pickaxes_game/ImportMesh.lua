local data = game:GetService('HttpService'):JSONDecode(DATA_JSON)
local storage = game:GetService('ServerStorage')
local folder = storage:FindFirstChild('PicaretasBlender')
if not folder then folder=Instance.new('Folder'); folder.Name='PicaretasBlender'; folder.Parent=storage end
local model=folder:FindFirstChild(data.slug)
if not model then model=Instance.new('Model'); model.Name=data.slug; model.WorldPivot=CFrame.identity; model.Parent=folder end
local existing=model:FindFirstChild(data.name)
if existing then return {name=existing.Name,id=existing.MeshId,skipped=true} end
local assets=game:GetService('AssetService')
local mesh=assert(assets:CreateEditableMesh(),'Could not allocate EditableMesh')
local v,n,u={},{},{}
for i,p in ipairs(data.vertices) do v[i]=mesh:AddVertex(Vector3.new(unpack(p))) end
for i,p in ipairs(data.normals) do n[i]=mesh:AddNormal(Vector3.new(unpack(p))) end
for i,p in ipairs(data.uvs) do u[i]=mesh:AddUV(Vector2.new(unpack(p))) end
for _,t in ipairs(data.triangles) do
 local a,b=t[1],t[2]
 local face=mesh:AddTriangle(v[a[1]+1],v[a[2]+1],v[a[3]+1])
 mesh:SetFaceNormals(face,{n[b[1]+1],n[b[2]+1],n[b[3]+1]})
 mesh:SetFaceUVs(face,{u[b[1]+1],u[b[2]+1],u[b[3]+1]})
end
mesh:RemoveUnused()
local center=mesh:GetCenter()
local size=mesh:GetSize()
local params={Name='Mining Pickaxe '..data.name,Description='Original Blender pickaxe mesh for Anime Mining Simulator',CreatorId=game.CreatorId,CreatorType=game.CreatorType==Enum.CreatorType.Group and Enum.AssetCreatorType.Group or Enum.AssetCreatorType.User}
local ok,result,id=pcall(function() return assets:CreateAssetAsync(mesh,Enum.AssetType.Mesh,params) end)
if not ok or result~=Enum.CreateAssetResult.Success then mesh:Destroy(); error('Mesh upload failed: '..tostring(result)..' '..tostring(id)) end
-- Persist upload ID before loading, so a load failure cannot lose the receipt.
local receipt=Instance.new('StringValue'); receipt.Name=data.name..'_UploadReceipt'; receipt.Value=tostring(id); receipt.Parent=model
local part=assets:CreateMeshPartAsync(Content.fromUri('rbxassetid://'..id),{CollisionFidelity=Enum.CollisionFidelity.Box,RenderFidelity=Enum.RenderFidelity.Precise})
part.Name=data.name; part.Size=size; part.CFrame=CFrame.new(center)
part.Color=Color3.new(unpack(data.color)); part.Material=Enum.Material[data.material]
part.Anchored=true; part.CanCollide=false; part.CanTouch=false; part.CanQuery=false; part.Massless=true; part.DoubleSided=true
part:SetAttribute('BlenderMaterial',data.material); part:SetAttribute('SourceTriangles',#data.triangles)
part.Parent=model
mesh:Destroy()
return {name=part.Name,id=part.MeshId,size=tostring(part.Size),center=tostring(center)}
