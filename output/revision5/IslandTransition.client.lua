local player=game.Players.LocalPlayer
local TweenService=game:GetService('TweenService')
local Config=require(game.ReplicatedStorage.Config)
local gui=Instance.new('ScreenGui') gui.Name='IslandTransition' gui.IgnoreGuiInset=true gui.ResetOnSpawn=false gui.DisplayOrder=1000 gui.Parent=player:WaitForChild('PlayerGui')
local panel=Instance.new('Frame') panel.Size=UDim2.fromScale(1,1) panel.BackgroundColor3=Color3.fromRGB(14,19,29) panel.BackgroundTransparency=1 panel.BorderSizePixel=0 panel.Visible=false panel.Parent=gui
local title=Instance.new('TextLabel') title.Size=UDim2.fromScale(.8,.1) title.Position=UDim2.fromScale(.1,.44) title.BackgroundTransparency=1 title.TextColor3=Color3.fromRGB(242,231,205) title.TextSize=27 title.Font=Enum.Font.GothamBold title.TextTransparency=1 title.Parent=panel
local tween,revision= nil,0
local function update()
 revision+=1 local mine=revision local id=player:GetAttribute('AreaTransition')
 if tween then tween:Cancel() end
 if id~=nil then
  local area=Config.areaPorId(id) title.Text=area and area.nome or 'Lobby' panel.Visible=true
  title.TextTransparency=0
  tween=TweenService:Create(panel,TweenInfo.new(.18),{BackgroundTransparency=.06}) tween:Play()
 else
  title.TextTransparency=1
  tween=TweenService:Create(panel,TweenInfo.new(.35),{BackgroundTransparency=1}) tween:Play()
  tween.Completed:Once(function() if revision==mine then panel.Visible=false end end)
 end
end
player:GetAttributeChangedSignal('AreaTransition'):Connect(update) update()
