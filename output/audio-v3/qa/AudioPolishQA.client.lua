-- Temporary Studio-only polish audit. No profile/economy writes.
local Run=game:GetService('RunService') if not Run:IsStudio() then return end
local RS=game:GetService('ReplicatedStorage') local Players=game:GetService('Players') local H=game:GetService('HttpService')
local player=Players.LocalPlayer
local output=Instance.new('StringValue') output.Name='AudioV3_PolishQA' output.Parent=player:WaitForChild('PlayerGui')
local report={status='starting',errors={},waveforms={},auditoryApproval=false}
local function save() output.Value=H:JSONEncode(report) end
local ok,err=xpcall(function()
 local S=require(RS.SomJogo) local C=require(RS.AudioCatalog)
 local deadline=os.clock()+30 repeat task.wait(.2) until S.Diagnostics().pending==0 or os.clock()>deadline
 report.status='waveform metrics' save()
 local ap=Instance.new('AudioPlayer') ap.Name='AudioQA_Waveform' ap.Volume=0 ap.Parent=game.SoundService
 for _,family in ipairs({'stone','metal','swing','tone','coin','click'}) do
  for _,id in ipairs(C.Assets[family]) do
   ap.Asset='rbxassetid://'..id
   local due=os.clock()+3 repeat task.wait(.05) until ap.IsReady or os.clock()>due
   local success,data=pcall(function() return ap:GetWaveformAsync(NumberRange.new(0,math.min(ap.TimeLength,3)),1500) end)
   if success and #data>0 then
    local peak,sum,onset=0,0,nil
    for _,v in ipairs(data) do peak=math.max(peak,math.abs(v)) sum+=v*v end
    for i,v in ipairs(data) do if math.abs(v)>peak*.08 then onset=(i-1)/#data*math.min(ap.TimeLength,3) break end end
    report.waveforms[tostring(id)]={family=family,peak=peak,rms=math.sqrt(sum/#data),onset=onset,samples=#data}
   else report.waveforms[tostring(id)]={error=tostring(data),family=family} end
   save()
  end
 end
 ap:Destroy()
 report.status='playback region caps / A-B-C presentation' save()
 local before=S.Diagnostics().played
 for _,ev in ipairs({'hit_metal','hit','hit_crystal'}) do
  for _=1,10 do S.tocar(ev) task.wait(.27) end
  task.wait(.6)
 end
 report.ABC={events={'hit_metal','hit','hit_crystal'},plays=30,voices=S.Diagnostics().played-before,subjectiveWinner='unconfirmed'}
 local passed=0
 for _,v in ipairs(game.SoundService:GetDescendants()) do
  if v:IsA('Sound') and v.Name:match('^AMS_Voice') and v.PlaybackRegionsEnabled then passed+=1 end
 end
 report.regionSlotsUsed=passed assert(passed>0,'playback regions not active')
 report.status='spatial culling / controls' save()
 local beforeFar=S.Diagnostics().played
 S.tocar('hit',{remote=true,pos=Vector3.new(1e6,1e6,1e6)})
 assert(S.Diagnostics().played==beforeFar,'distance culling')
 local attrs={} for _,key in ipairs({'AudioMasterVolume','AudioMusicVolume','AudioSFXVolume','AudioUIVolume','AudioAmbienceVolume','MusicEnabled','SomMineracaoEnabled','SomInterfaceEnabled'}) do attrs[key]=player:GetAttribute(key) end
 player:SetAttribute('AudioMasterVolume',0) task.wait(.1)
 assert(game.SoundService.MASTER.Volume==0,'master mute')
 player:SetAttribute('AudioMasterVolume',attrs.AudioMasterVolume)
 player:SetAttribute('SomMineracaoEnabled',false) task.wait(.1)
 beforeFar=S.Diagnostics().played S.tocar('hit') S.coleta() task.wait(.2)
 assert(S.Diagnostics().played==beforeFar,'mining + pickup mute')
 for key,value in pairs(attrs) do player:SetAttribute(key,value) end
 report.muteAndCulling=true
 report.status='rarity and economy sequence' save()
 for _,rarity in ipairs({'comum','incomum','raro','epico','lendario','mitico','secreto'}) do S.drop(rarity) task.wait(1.5) end
 for _,gain in ipairs({100,1000,10000,1000000,10000000}) do S.venda(gain,1) task.wait(1.2) end
 task.wait(2)
 report.final=S.Diagnostics() report.final.history=nil
 assert(report.final.active==0 and report.final.queue==0 and report.final.created==24,'polish cleanup')
 report.status='passed' save() print('[AudioV3 PolishQA] PASSED')
end,debug.traceback)
if not ok then report.status='failed' table.insert(report.errors,tostring(err)) save() warn('[AudioV3 PolishQA] '..tostring(err)) end
