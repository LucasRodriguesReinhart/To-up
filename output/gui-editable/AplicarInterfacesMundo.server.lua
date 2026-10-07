-- Os layouts originais ficam em StarterGui.InterfacesMundo.PlacasExistentes.
-- As cópias ficam ligadas às peças do cenário para respeitar streaming e iluminação.
local templates=game.StarterGui:WaitForChild("InterfacesMundo"):WaitForChild("PlacasExistentes")
local function apply(gui)
 if not gui:IsA("LayerCollector") then return end
 local key=gui:GetAttribute("ModeloStarterGui")
 local template=key and templates:FindFirstChild(key)
 if not template or not gui.Parent then return end
 local parent=gui.Parent
 local copy=template:Clone()
 copy.Name=template:GetAttribute("NomeNoMundo") or gui.Name
 copy.Enabled=template:GetAttribute("AtivarNoMundo")~=false
 copy.Adornee=gui.Adornee or (parent:IsA("BasePart") and parent or nil)
 copy:SetAttribute("ModeloStarterGui",nil)
 copy.Parent=parent
 gui:Destroy()
end
workspace.DescendantAdded:Connect(function(gui)
 if gui:IsA("LayerCollector") and gui:GetAttribute("ModeloStarterGui") then task.defer(apply,gui) end
end)
for _,gui in workspace:GetDescendants() do apply(gui) end

