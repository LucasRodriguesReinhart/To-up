-- Temporary final integration smoke; no transactions or profile writes.
if not game:GetService('RunService'):IsStudio() then return end
local H=game:GetService('HttpService')
local RS=game:GetService('ReplicatedStorage')
local p=game:GetService('Players').LocalPlayer
local output=Instance.new('StringValue') output.Name='AudioV3_FinalSmoke' output.Parent=p:WaitForChild('PlayerGui')
local report={status='loading',realTransactions=false}
output.Value=H:JSONEncode(report)
local ok,err=xpcall(function()
 local S=require(RS:WaitForChild('SomJogo'))
 local stop=os.clock()+35
 repeat task.wait(.2) until S.Diagnostics().pending==0 or os.clock()>stop
 local d=S.Diagnostics() local assets=0
 for id,a in pairs(d.assets) do assert(a.loaded,'Not loaded: '..id) assets+=1 end
 assert(assets==31 and d.pending==0,'asset bank')
 assert(RS:WaitForChild('Remotes',30):WaitForChild('AtualizarAudioProfile',30),'preference endpoint missing')
 local master=game.SoundService:FindFirstChild('MASTER')
 assert(master and master.SFX.SFX_GAMEPLAY.SFX_MINING,'audio group tree missing')
 local count=1 for _,v in ipairs(master:GetDescendants()) do if v:IsA('SoundGroup') then count+=1 end end
 assert(count==9,'duplicate audio groups')
 S.StopEffects()
 local before=d.events.coleta or 0
 for _=1,100 do S.coleta() end
 task.wait(.4)
 local after=S.Diagnostics()
 assert((after.events.coleta or 0)-before==1,'pickup regression')
 S.tocar('ui_equipar') S.drop('epico')
 task.wait(1.1)
 d=S.Diagnostics()
 local beforeCleanup={active=d.active,queued=d.queue}
 report.beforeCleanup=beforeCleanup report.created=d.created report.peak=d.peak
 assert(d.active<=24 and d.created==24 and d.queue<=48,'pool/queue bounds')
 S.StopEffects() d=S.Diagnostics()
 assert(d.active==0 and d.queue==0,'explicit cleanup')
 report.beforeCleanup=beforeCleanup
 report={status='passed',cleanupMethod='StopEffects',beforeCleanup=report.beforeCleanup,assetsLoaded=assets,audioGroups=count,created=d.created,active=d.active,queued=d.queue,remotePreferenceExists=true,uiLoaded=p.PlayerGui:FindFirstChild('ExpeditionUI')~=nil,realTransactions=false}
end,debug.traceback)
if not ok then report.status='failed' report.error=tostring(err) end
output.Value=H:JSONEncode(report)
print('[AudioV3 FinalSmoke] '..report.status)
