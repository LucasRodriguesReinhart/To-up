-- Temporary Studio-only regression harness. No transactions, RemoteFunctions, DataStores or damage.
local Run=game:GetService('RunService') if not Run:IsStudio() then return end
local RS=game:GetService('ReplicatedStorage') local Players=game:GetService('Players')
local H=game:GetService('HttpService') local player=Players.LocalPlayer
local result=Instance.new('StringValue') result.Name='AudioV3_QA' result.Parent=player:WaitForChild('PlayerGui')
local report={status='starting',errors={},phases={},auditoryApproval=false,realMultiplayer=false}
local function save() result.Value=H:JSONEncode(report) end
local function phase(name) report.status=name save() print('[AudioV3 QA] '..name) end
local ok,err=xpcall(function()
 local S=require(RS:WaitForChild('SomJogo'))
 local C=require(RS:WaitForChild('AudioCatalog'))
 local P=require(RS:WaitForChild('AudioPreferences'))
 phase('preload')
 local untilAt=os.clock()+35
 repeat task.wait(.25) until S.Diagnostics().pending==0 or os.clock()>untilAt
 local d=S.Diagnostics() report.assets=d.assets report.failed=d.failed report.preloadPending=d.pending save()
 assert(d.pending==0,'preload did not finish in 35s')
 for id,a in pairs(d.assets) do assert(a.loaded,'asset failed: '..id) end
 local q=P.sanitize({MusicEnabled=false,AudioMasterVolume=9,AudioMusicVolume=-9,AudioUIVolume=0/0,AudioSFXVolume=math.huge,NotAllowed=1})
 assert(q.MusicEnabled==false and q.AudioMasterVolume==1 and q.AudioMusicVolume==0 and q.AudioUIVolume==.65 and q.AudioSFXVolume==.85 and q.NotAllowed==nil,'preference sanitizer')
 assert(S.saleTier(100)==1 and S.saleTier(1000)==2 and S.saleTier(10000)==3 and S.saleTier(1000000)==4 and S.saleTier(10000000)==5,'sale tiers')
 report.preferenceSchema=true report.saleTiers=true
 phase('100 hits / fixed pool')
 S.StopEffects()
 local before=S.Diagnostics().played
 local start=os.clock()
 local unique,last,repeats={},nil,0
 for i=1,100 do
  S.tocar('hit',{auto=i>50})
  task.wait(.085)
  local history=S.Diagnostics().history
  for n=#history,1,-1 do local x=history[n] if x.event=='hit' then
   for _,id in ipairs(C.Assets.stone) do if x.id==id then unique[id]=true if x.id==last then repeats+=1 end last=x.id break end end
   if unique[x.id] then break end
  end end
 end
 task.wait(.6)
 d=S.Diagnostics()
 local count=0 for _ in pairs(unique) do count+=1 end
 report.phases.hits={requests=100,voicesPlayed=d.played-before,uniqueStone=count,adjacentRepeat=repeats,elapsed=os.clock()-start,activeAfter=d.active,created=d.created,peak=d.peak}
 assert(count>=4 and repeats==0,'anti repeat failure')
 assert(d.created==24 and d.active==0 and d.peak<=24,'pool bound/cleanup')
 phase('100 pickups + burst 100')
 local beforePickup=d.events.coleta or 0
 for i=1,100 do S.coleta() task.wait(.085) end
 task.wait(.4)
 local after100=S.Diagnostics().events.coleta or 0
 for _=1,100 do S.coleta() end
 task.wait(.4)
 d=S.Diagnostics()
 report.phases.pickups={requested=200,regularVoices=after100-beforePickup,burstVoices=(d.events.coleta or 0)-after100,activeAfter=d.active}
 assert((d.events.coleta or 0)-after100==1,'pickup aggregation')
 phase('chaos / remote priority')
 local cam=workspace.CurrentCamera local pos=cam and cam.CFrame.Position+cam.CFrame.LookVector*12
 for i=1,150 do
  for _=1,15 do S.tocar('hit',{pos=pos,remote=true}) end
  S.tocar('hit') S.coleta() S.tocar('ui_click')
  if i%20==0 then S.venda(1000000,1) S.drop('mitico') end
  task.wait(.025)
  d=S.Diagnostics() assert(d.active<=24 and d.remoteActive<=4,'voice budget')
 end
 task.wait(2)
 d=S.Diagnostics() report.phases.chaos={peak=d.peak,activeAfter=d.active,queuedAfter=d.queue,created=d.created,dropped=d.dropped,stolen=d.stolen}
 assert(d.active==0 and d.queue==0 and d.created==24,'cleanup after chaos')
 phase('procedural marker boundary + cancel')
 local Swing=require(RS.MiningSwing)
 local fixture=Instance.new('Model') fixture.Name='AudioQA_Fixture'
 local hum=Instance.new('Humanoid') hum.Parent=fixture
 local root=Instance.new('Part') root.Name='HumanoidRootPart' root.Anchored=true root.Position=Vector3.new(0,-2000,0) root.Parent=fixture
 local tool=Instance.new('Tool') tool.Name='Picareta' tool.RequiresHandle=false tool.Parent=fixture
 fixture.Parent=workspace
 local marks={}
 local connection=Swing.MarkerReached:Connect(function(c,name) if c==fixture then table.insert(marks,name) end end)
 assert(Swing.Play(fixture,nil,workspace:GetServerTimeNow()+1))
 Swing.Advance(fixture,.149) Swing.Advance(fixture,.15) Swing.Advance(fixture,.279) Swing.Advance(fixture,.28) Swing.Advance(fixture,.34) Swing.Advance(fixture,.34)
 task.wait(.04)
 tool.Parent=nil task.wait(.05)
 connection:Disconnect() tool:Destroy() fixture:Destroy()
 report.phases.markers=marks
 assert(marks[1]=='SwingStart' and marks[2]=='Hit' and marks[3]=='SwingEnd' and marks[4]=='Cancelled' and #marks==4,'marker sequence/dedup')
 phase('music area rapid transitions')
 for _,area in ipairs({1,2,4,5,0}) do S.setArea(area) task.wait(.2) end
 task.wait(2.7)
 local playing=0
 for _,s in ipairs(game.SoundService.AMS_AudioRuntime:GetChildren()) do if s:IsA('Sound') and s.Name:match('AMS_Music') and s.IsPlaying then playing+=1 end end
 report.musicPlayers=playing assert(playing==1,'music voice cleanup')
 S.setArea(player:GetAttribute('CurrentAreaId') or 0)
 report.final=S.Diagnostics() report.final.history=nil
 report.status='passed' save() print('[AudioV3 QA] PASSED automated regression')
end,debug.traceback)
if not ok then report.status='failed' table.insert(report.errors,tostring(err)) save() warn('[AudioV3 QA] '..tostring(err)) end
