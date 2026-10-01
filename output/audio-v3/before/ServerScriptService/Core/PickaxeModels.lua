-- Clones the imported Blender templates. Damage and purchases remain in Config.
local ServerStorage=game:GetService('ServerStorage')
local Models={}
-- Empunhadura de destro: a mao direita e a mao DE CIMA (meio do couro, y=-0.05 no Handle); a esquerda fica abaixo,
-- na ponta, e desliza ate a direita no impacto (CharacterRig). A haste atravessa o punho (Handle +Y = -Z da mao)
-- e a lamina fica no plano do golpe (Handle +X = +Y da mao). RightGripAttachment tem rotacao Rx(-90).
-- Mesmo valor em PicaretaTool.
local R=CFrame.fromMatrix(Vector3.zero,Vector3.new(0,1,0),Vector3.new(0,0,-1),Vector3.new(-1,0,0))
local GRIP=CFrame.new(0,-0.05,0)*R:Inverse()*CFrame.Angles(math.rad(-90),0,0)
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


