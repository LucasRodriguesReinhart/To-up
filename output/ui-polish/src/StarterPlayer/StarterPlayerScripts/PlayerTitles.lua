local Players=game:GetService('Players')
local Run=game:GetService('RunService')
local entries={}
local function attach(p)
 local e=entries[p];if not e then return end
 if e.gui then e.gui:Destroy();e.gui=nil end
 local char=p.Character;local head=char and char:FindFirstChild('Head')
 if p:GetAttribute('VIPOwned')~=true or not head then return end
 local gui=Instance.new('BillboardGui');gui.Name='VIPTitle';gui.Adornee=head
 gui.Size=UDim2.fromOffset(150,51);gui.StudsOffsetWorldSpace=Vector3.new(0,2.45,0)
 gui.AlwaysOnTop=false;gui.MaxDistance=64;gui.LightInfluence=0;gui.Parent=char
 local title=Instance.new('TextLabel');title.Name='VIP';title.BackgroundTransparency=1;title.Size=UDim2.new(1,0,0,26)
 title.Text='✦ VIP ✦';title.TextColor3=Color3.fromRGB(255,213,85);title.TextStrokeColor3=Color3.fromRGB(44,23,7);title.TextStrokeTransparency=.12
 title.Font=Enum.Font.GothamBlack;title.TextSize=19;title.Parent=gui
 local name=title:Clone();name.Name='PlayerName';name.Text=p.DisplayName;name.TextSize=13;name.TextColor3=Color3.fromRGB(255,244,208)
 name.Position=UDim2.fromOffset(0,24);name.Size=UDim2.new(1,0,0,20);name.Parent=gui
 e.gui=gui
end
local function watch(p)
 entries[p]={connections={}}
 local c=entries[p].connections
 table.insert(c,p.CharacterAdded:Connect(function(char) char:WaitForChild('Head',10);attach(p) end))
 table.insert(c,p:GetAttributeChangedSignal('VIPOwned'):Connect(function() attach(p) end))
 attach(p)
end
for _,p in ipairs(Players:GetPlayers()) do watch(p) end
Players.PlayerAdded:Connect(watch)
Players.PlayerRemoving:Connect(function(p) local e=entries[p];if e then if e.gui then e.gui:Destroy() end;for _,c in ipairs(e.connections) do c:Disconnect() end end;entries[p]=nil end)
local timer=0
Run.Heartbeat:Connect(function(dt)
 timer+=dt;if timer<.15 then return end;timer=0
 local camera=workspace.CurrentCamera;if not camera then return end
 for p,e in pairs(entries) do
  local g=e.gui
  if g and g.Parent and g.Adornee then
   local distance=(camera.CFrame.Position-g.Adornee.Position).Magnitude
   local fade=math.clamp((distance-35)/25,0,1)
   g.Enabled=distance<60 and not (p==Players.LocalPlayer and distance<3)
   for _,t in ipairs(g:GetChildren()) do if t:IsA('TextLabel') then t.TextTransparency=fade;t.TextStrokeTransparency=.12+.88*fade end end
  end
 end
end)
