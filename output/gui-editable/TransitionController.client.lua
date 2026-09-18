local player=game.Players.LocalPlayer
local TweenService=game:GetService('TweenService')
local Config=require(game.ReplicatedStorage.Config)
local gui=script.Parent
local panel=gui:WaitForChild("Fundo")
local title=panel:WaitForChild("Titulo")
local targetTransparency=panel.BackgroundTransparency
local tween,revision= nil,0
local function update()
 revision+=1 local mine=revision local id=player:GetAttribute('AreaTransition')
 if tween then tween:Cancel() end
 if id~=nil then
  local area=Config.areaPorId(id) title.Text=area and area.nome or 'Lobby' panel.Visible=true
  title.TextTransparency=0
  tween=TweenService:Create(panel,TweenInfo.new(.18),{BackgroundTransparency=targetTransparency}) tween:Play()
 else
  title.TextTransparency=1
  tween=TweenService:Create(panel,TweenInfo.new(.35),{BackgroundTransparency=1}) tween:Play()
  tween.Completed:Once(function() if revision==mine then panel.Visible=false end end)
 end
end
player:GetAttributeChangedSignal('AreaTransition'):Connect(update) update()
