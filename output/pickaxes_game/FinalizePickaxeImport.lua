-- Run Finalize.run() after importing IMPORTAR_8_PICARETAS.fbx into Workspace.
local Finalize={}
local rows=game:GetService('HttpService'):JSONDecode(MANIFEST_JSON)
local function key(s) return s:lower():gsub('[^%w]','') end
function Finalize.run()
 local found,missing={},{}
 for _,row in ipairs(rows) do
  local matches={}
  for _,o in ipairs(workspace:GetDescendants()) do
   if o:IsA('MeshPart') and key(o.Name)==key(row.name) then table.insert(matches,o) end
  end
  assert(#matches<=1,'Duplicate imported mesh: '..row.name)
  if #matches==0 then table.insert(missing,row.name) else
   assert(matches[1].MeshId:match('^rbxassetid://%d+'),'Mesh must be uploaded: '..row.name)
   found[row.name]=matches[1]
  end
 end
 if #missing>0 then return {ready=false,missing=missing} end
 local storage=game:GetService('ServerStorage')
 local staged=Instance.new('Folder'); staged.Name='PicaretasBlender_Staging'
 for _,row in ipairs(rows) do
  local model=staged:FindFirstChild(row.slug)
  if not model then model=Instance.new('Model'); model.Name=row.slug; model.WorldPivot=CFrame.identity; model.Parent=staged end
  local part=found[row.name]:Clone()
  part.Name=row.name; part.Size=Vector3.new(unpack(row.size)); part.CFrame=CFrame.new(unpack(row.center))
  part.Color=Color3.new(unpack(row.color)); part.Material=Enum.Material[row.material]; part.TextureID=''
  for _,child in ipairs(part:GetChildren()) do if child:IsA('SurfaceAppearance') then child:Destroy() end end
  part.Anchored=true; part.CanCollide=false; part.CanTouch=false; part.CanQuery=false; part.Massless=true; part.DoubleSided=true
  part.Parent=model
 end
 for _,m in ipairs(staged:GetChildren()) do m:SetAttribute('ImportValidated',true); m:SetAttribute('VisualVersion','BlenderArsenalV1') end
 local old=storage:FindFirstChild('PicaretasBlender')
 if old then old.Name='PicaretasBlender_Previous_'..tostring(os.time()) end
 staged.Name='PicaretasBlender'; staged.Parent=storage
 local archive=Instance.new('Folder'); archive.Name='BlenderImportSources_'..tostring(os.time()); archive.Parent=storage
 for _,part in pairs(found) do part.Parent=archive end
 return {ready=true,models=#staged:GetChildren(),meshes=#rows}
end
return Finalize
