-- Temporary, isolated test; creates no static asset uploads or progression changes.
if not game:GetService('RunService'):IsStudio() then return end
task.wait(8)
local results=Instance.new('Folder');results.Name='__ShadowRuntimeProbe';results.Parent=workspace
local ok,err=pcall(function()
 local C=game.ServerScriptService.Core
 local runtime=require(C.ShadowGardenMeshRuntime)
 local layout=require(C.ShadowGardenLayout)
 local data=game:GetService('HttpService'):JSONDecode(C.ShadowGardenMeshData.Arvore_1.Value)
 local model=runtime.buildAsset('TreeProbe',data,layout.palette)
 model:PivotTo(CFrame.new(0,8,40));model.ModelStreamingMode=Enum.ModelStreamingMode.Persistent;model.Parent=results
 results:SetAttribute('MeshCount',1);results:SetAttribute('Triangles',model:GetAttribute('BlenderTriangles'))
end)
results:SetAttribute('OK',ok);results:SetAttribute('Error',ok and '' or tostring(err))
print('[ShadowRuntimeProbe]',ok,err)
