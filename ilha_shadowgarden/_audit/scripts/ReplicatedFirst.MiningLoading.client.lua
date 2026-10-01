-- Readiness-based loading. No fabricated percentage or minimum wait.
local RF=game:GetService('ReplicatedFirst')
local Players=game:GetService('Players')
local Tween=game:GetService('TweenService')
local player=Players.LocalPlayer
local gui=Instance.new('ScreenGui');gui.Name='MiningLoading';gui.IgnoreGuiInset=true;gui.DisplayOrder=10000;gui.ResetOnSpawn=false
gui.Parent=player:WaitForChild('PlayerGui');RF:RemoveDefaultLoadingScreen()
local root=Instance.new('CanvasGroup');root.Size=UDim2.fromScale(1,1);root.BackgroundColor3=Color3.fromRGB(7,12,22);root.BorderSizePixel=0;root.Parent=gui
local function text(name,value,pos,size,fontSize,color)
 local t=Instance.new('TextLabel');t.Name=name;t.Text=value;t.Position=pos;t.Size=size;t.BackgroundTransparency=1
 t.Font=Enum.Font.GothamBlack;t.TextColor3=color or Color3.fromRGB(249,244,227);t.TextSize=fontSize;t.TextStrokeTransparency=.3;t.TextWrapped=true;t.Parent=root;return t
end
local back=Instance.new('Frame');back.Size=UDim2.fromScale(1,1);back.BackgroundColor3=Color3.new(1,1,1);back.BorderSizePixel=0;back.Parent=root
local gradient=Instance.new('UIGradient');gradient.Color=ColorSequence.new(Color3.fromRGB(10,47,63),Color3.fromRGB(7,10,19));gradient.Rotation=65;gradient.Parent=back
for i=1,7 do
 local crystal=Instance.new('Frame');crystal.Name='Crystal'..i;crystal.AnchorPoint=Vector2.new(.5,.5);crystal.Position=UDim2.fromScale(i/8,.58+math.sin(i)*.18)
 crystal.Size=UDim2.fromScale(.08+.014*i,.30+.04*i);crystal.Rotation=25+(i%2)*-50;crystal.BackgroundColor3=Color3.fromRGB(35,142,170);crystal.BackgroundTransparency=.87;crystal.BorderSizePixel=0;crystal.Parent=root
 local line=Instance.new('UIStroke');line.Color=Color3.fromRGB(112,223,232);line.Transparency=.87;line.Thickness=1;line.Parent=crystal
end
text('Kicker','D E S P E R T E   S E U   P O D E R',UDim2.fromScale(.15,.23),UDim2.fromScale(.7,.05),14,Color3.fromRGB(115,216,229))
local anime=text('Anime','ANIME',UDim2.fromScale(.15,.30),UDim2.fromScale(.7,.11),48)
local mining=text('Mining','MINING',UDim2.fromScale(.12,.405),UDim2.fromScale(.76,.16),84,Color3.fromRGB(255,207,88))
text('Simulator','S I M U L A T O R',UDim2.fromScale(.15,.575),UDim2.fromScale(.7,.06),23)
local status=text('Status','Preparando sua expedição…',UDim2.fromScale(.15,.79),UDim2.fromScale(.7,.055),16,Color3.fromRGB(194,215,222))
local track=Instance.new('Frame');track.Size=UDim2.fromScale(.32,.004);track.Position=UDim2.fromScale(.34,.865);track.BackgroundColor3=Color3.fromRGB(34,66,78);track.BorderSizePixel=0;track.Parent=root
local pulse=Instance.new('Frame');pulse.Size=UDim2.fromScale(.22,1);pulse.BackgroundColor3=Color3.fromRGB(95,222,237);pulse.BorderSizePixel=0;pulse.Parent=track
local motion=Tween:Create(pulse,TweenInfo.new(.9,Enum.EasingStyle.Sine,Enum.EasingDirection.InOut,-1,true),{Position=UDim2.fromScale(.78,0)});motion:Play()
local skip=Instance.new('TextButton');skip.Text='Continuar';skip.Size=UDim2.fromOffset(130,36);skip.AnchorPoint=Vector2.new(.5,1);skip.Position=UDim2.fromScale(.5,.965);skip.BackgroundColor3=Color3.fromRGB(17,54,65);skip.TextColor3=Color3.new(1,1,1);skip.Font=Enum.Font.GothamBold;skip.TextSize=15;skip.Visible=false;skip.Parent=root
local closed=false
local function finish()
 if closed then return end;closed=true;motion:Cancel()
 local fade=Tween:Create(root,TweenInfo.new(.24),{GroupTransparency=1});fade:Play();fade.Completed:Wait();gui:Destroy()
end
skip.Activated:Connect(finish)
task.delay(12,function() if not closed then skip.Visible=true;status.Text='O carregamento está demorando. Você pode continuar.' end end)
task.spawn(function()
 if not game:IsLoaded() then game.Loaded:Wait() end
 if closed then return end
 status.Text='Carregando sua equipe…'
 local shell=player.PlayerGui:WaitForChild('ExpeditionUI',20)
 if shell then
  local deadline=os.clock()+20
  while shell.Parent and shell:GetAttribute('ProfileReady')~=true and os.clock()<deadline and not closed do task.wait(.1) end
 end
 if not closed then finish() end
end)
local function resize()
 local small=gui.AbsoluteSize.Y<500;anime.TextSize=small and 31 or 48;mining.TextSize=small and 58 or 84
end
gui:GetPropertyChangedSignal('AbsoluteSize'):Connect(resize);resize()
