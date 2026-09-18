-- Clones the imported Blender templates. Damage and purchases remain in Config.
local ServerStorage=game:GetService('ServerStorage')
local Models={}
local GRIP=CFrame.new(0,0.1,0,0.4328632354736328,0.3389130234718323,-0.8353247046470642,-0.8923119902610779,0.02941453456878662,-0.45046013593673706,-0.1280960887670517,0.9403578639030457,0.31514862179756165)
function Models.create(id,definition)
 local folder=ServerStorage:FindFirstChild('PicaretasBlender')
 local template=folder and folder:FindFirstChild(id)
 if not template or template:GetAttribute('ImportValidated')~=true then return nil end
 local tool=Instance.new('Tool')
 tool.Name='Picareta'; tool.ToolTip=definition and definition.nome or id
 tool.RequiresHandle=true; tool.CanBeDropped=false; tool.Grip=GRIP
 tool:SetAttribute('PicaretaId',id); tool:SetAttribute('VisualVersion','BlenderArsenalV1')
 local handle=Instance.new('Part')
 handle.Name='Handle'; handle.Size=Vector3.new(.3,2.4,.3); handle.Transparency=1
 handle.CanCollide=false; handle.CanTouch=false; handle.CanQuery=false; handle.Massless=true; handle.Anchored=false
 handle.Parent=tool
 for _,source in ipairs(template:GetChildren()) do
  if source:IsA('MeshPart') then
   local part=source:Clone(); part.Anchored=false; part.CanCollide=false; part.CanTouch=false; part.CanQuery=false; part.Massless=true
   part.CFrame=handle.CFrame*source.CFrame; part.Parent=tool
   local weld=Instance.new('WeldConstraint'); weld.Part0=handle; weld.Part1=part; weld.Parent=part
  end
 end
 return tool
end
return Models
