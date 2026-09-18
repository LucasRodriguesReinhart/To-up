-- AMS Audio V3: client-owned pooled mixer. No Instances or playback on the server.
local Run=game:GetService('RunService')
local SS=game:GetService('SoundService')
local Players=game:GetService('Players')
local CP=game:GetService('ContentProvider')
local Catalog=require(script.Parent:WaitForChild('AudioCatalog'))
local S={ID=Catalog.Assets,EVENTOS=Catalog.Events,Version=3}
if not Run:IsClient() then
 for _,name in {'tocar','coleta','drop','quebra','venda','hit','setArea','Duck','StopAll'} do S[name]=function() return false end end
 return S
end
local player=Players.LocalPlayer
local random=Random.new()
local connections={}
local destroyed=false
local groups={}
local pool,queue,cache,loaded,lastChoice,lastEvent={}, {}, {}, {}, {}, {}
local eventsActive={}
local metrics={requests=0,played=0,dropped=0,stolen=0,peak=0,created=0,history={},failed={},pending=0,events={}}
local folder=Instance.new('Folder') folder.Name='AMS_AudioRuntime' folder.Parent=SS
local function group(name,parent)
 local g=parent:FindFirstChild(name)
 if not (g and g:IsA('SoundGroup')) then g=Instance.new('SoundGroup') g.Name=name g.Parent=parent end
 return g
end
groups.Master=group('MASTER',SS)
groups.Music=group('MUSIC',groups.Master)
groups.SFX=group('SFX',groups.Master)
groups.Gameplay=group('SFX_GAMEPLAY',groups.SFX)
groups.Mining=group('SFX_MINING',groups.Gameplay)
groups.Rewards=group('SFX_REWARDS',groups.SFX)
groups.World=group('SFX_WORLD',groups.SFX)
groups.UI=group('SFX_UI',groups.SFX)
groups.Ambience=group('AMBIENCE',groups.Master)
local duckUntil,duckTarget,duckNow=0,1,1
local lastReward=-100
local function pref(name)
 local v=player:GetAttribute('Audio'..name..'Volume')
 return type(v)=='number' and v==v and math.clamp(v,0,1) or Catalog.Defaults[name]
end
local function mix()
 groups.Master.Volume=pref('Master')
 groups.SFX.Volume=pref('SFX')
 groups.Gameplay.Volume=1
 groups.Mining.Volume=player:GetAttribute('SomMineracaoEnabled')==false and 0 or 1
 groups.Rewards.Volume=.90
 groups.World.Volume=.75
 groups.UI.Volume=player:GetAttribute('SomInterfaceEnabled')==false and 0 or pref('UI')
 groups.Music.Volume=(player:GetAttribute('MusicEnabled')==false and 0 or pref('Music'))*duckNow
 groups.Ambience.Volume=pref('Ambience')*(.72+.28*duckNow)
end
for _,attr in {'AudioMasterVolume','AudioMusicVolume','AudioSFXVolume','AudioUIVolume','AudioAmbienceVolume','MusicEnabled','SomMineracaoEnabled','SomInterfaceEnabled'} do
 table.insert(connections,player:GetAttributeChangedSignal(attr):Connect(mix))
end
mix()
local compressor=groups.Master:FindFirstChild('PeakGuard') or Instance.new('CompressorSoundEffect')
compressor.Name='PeakGuard' compressor.Threshold=-7 compressor.Ratio=3 compressor.Attack=.01 compressor.Release=.12 compressor.GainMakeup=0 compressor.Parent=groups.Master
local eq=groups.Mining:FindFirstChild('MiningTone') or Instance.new('EqualizerSoundEffect')
eq.Name='MiningTone' eq.HighGain=-3 eq.MidGain=0 eq.LowGain=-1 eq.Parent=groups.Mining
local uiEQ=groups.UI:FindFirstChild('UITone') or Instance.new('EqualizerSoundEffect')
uiEQ.Name='UITone' uiEQ.HighGain=-4 uiEQ.MidGain=0 uiEQ.LowGain=-3 uiEQ.Parent=groups.UI
local musicEQ=groups.Music:FindFirstChild('GameplaySpace') or Instance.new('EqualizerSoundEffect')
musicEQ.Name='GameplaySpace' musicEQ.MidGain=-2 musicEQ.HighGain=-1 musicEQ.LowGain=-1 musicEQ.Parent=groups.Music
for i=1,Catalog.Budget.voices do
 local a=Instance.new('Attachment') a.Name='Voice_'..i a.Parent=workspace.Terrain
 local sound=Instance.new('Sound') sound.Name='AMS_Voice_'..i sound.Volume=0 sound.Parent=folder
 sound.RollOffMode=Enum.RollOffMode.InverseTapered sound.RollOffMinDistance=8 sound.RollOffMaxDistance=64
 pool[i]={sound=sound,attachment=a,active=false,generation=0}
 metrics.created+=1
end
local function prepare(id)
 if cache[id] then return cache[id] end
 local s=Instance.new('Sound') s.Name='Asset_'..id s.SoundId='rbxassetid://'..id s.Volume=0 s.Parent=folder cache[id]=s
 return s
end
local assetList={}
for _,name in ipairs({'stone','click','swing','metal','crack','coin','tone','glass','heavy','debris','fire','wind','water','energy'}) do
 for _,id in ipairs(Catalog.Assets[name] or {}) do if not cache[id] then table.insert(assetList,prepare(id)) end end
end
local initialTrack=Catalog.Music[player:GetAttribute('CurrentAreaId') or 0] or Catalog.Music[0]
table.insert(assetList,1,prepare(initialTrack.id))
for _,track in pairs(Catalog.Music) do if not cache[track.id] then table.insert(assetList,prepare(track.id)) end end
metrics.pending=#assetList
-- Batches prevent one slow asset blocking the entire sound bank; failures never produce late hits.
local nextAsset=1
for _=1,3 do task.spawn(function()
 while nextAsset<=#assetList do
  local start=nextAsset nextAsset+=4
  if destroyed then return end
  local batch={} for i=start,math.min(start+3,#assetList) do table.insert(batch,assetList[i]) end
  pcall(function() CP:PreloadAsync(batch,function(content,status)
   local id=tonumber(string.match(content,'%d+'))
   if id then loaded[id]=status==Enum.AssetFetchStatus.Success if not loaded[id] then metrics.failed[tostring(id)]=tostring(status) end end
  end) end)
  for _,s in ipairs(batch) do
   local id=tonumber(string.match(s.SoundId,'%d+'))
   loaded[id]=s.IsLoaded
   if s.IsLoaded then metrics.failed[tostring(id)]=nil else metrics.failed[tostring(id)]=metrics.failed[tostring(id)] or 'NotLoaded' end
   metrics.pending=math.max(0,metrics.pending-1)
  end
 end
end) end
local function choice(family)
 local list=Catalog.Assets[family] or {}
 local ready={}
 for _,id in ipairs(list) do if cache[id] and cache[id].IsLoaded then table.insert(ready,id) end end
 if #ready==0 then return nil end
 local idx=random:NextInteger(1,#ready)
 if #ready>1 and ready[idx]==lastChoice[family] then idx=idx%#ready+1 end
 local id=ready[idx] lastChoice[family]=id return id
end
local function release(slot)
 if not slot.active then return end
 slot.sound:Stop() slot.sound.Volume=0 slot.active=false
 eventsActive[slot.key]=math.max(0,(eventsActive[slot.key] or 1)-1)
end
local function activeCount(bus,remote)
 local n=0 for _,v in ipairs(pool) do if v.active and (not bus or v.bus==bus) and (not remote or v.remote) then n+=1 end end return n
end
local function allocate(bus,priority,remote)
 local free,victim=nil,nil
 local limited=activeCount(bus)>=Catalog.Budget[bus] or (remote and activeCount(nil,true)>=Catalog.Budget.remote)
 for _,slot in ipairs(pool) do
  if not slot.active then free=free or slot
  elseif slot.priority<priority and (not limited or (slot.bus==bus and (not remote or slot.remote))) then
   if not victim or slot.priority<victim.priority or (slot.priority==victim.priority and slot.started<victim.started) then victim=slot end
  end
 end
 if free and not limited then return free end
 if victim then release(victim) metrics.stolen+=1 return victim end
 return nil
end
local function reject() metrics.dropped+=1 return false end
local function playLayer(job)
 local ev,layer,opts=job.ev,job.layer,job.opts
 if destroyed then return end
 if opts.valid and not opts.valid() then return end
 local id=choice(layer.family)
 if not id then return reject() end
 local remote=opts.remote==true
 local priority=ev.priority-(remote and 35 or 0)
 local slot=allocate(ev.bus,priority,remote)
 if not slot then return reject() end
 local pos=opts.pos
 local s=slot.sound
 local pitch=math.clamp((layer.pitch or 1)*(opts.pitch or 1)*random:NextNumber(1-(layer.variation or 0),1+(layer.variation or 0)),.65,2.6)
 local trim=Catalog.Trim[id] or {}
 local offset=layer.offset or trim.offset or 0
 local volume=layer.volume*(trim.gain or 1)*random:NextNumber(.96,1.04)*(opts.volume or 1)*(remote and .36 or 1)
 if opts.auto then volume*=.82 end
 slot.generation+=1 slot.event=job.name slot.key=job.name..(remote and ':remote' or ':local') slot.priority=priority slot.bus=ev.bus slot.remote=remote
 slot.started=os.clock() slot.duration=math.min(layer.duration or .4,math.max(.03,(cache[id].TimeLength-offset)/pitch))
 slot.active=true slot.level=volume
 s.SoundId='rbxassetid://'..id s.SoundGroup=groups[ev.bus] s.Looped=false s.PlaybackSpeed=pitch
 s.RollOffMinDistance=remote and 5 or 8 s.RollOffMaxDistance=opts.maxDistance or (remote and 44 or 64)
 if typeof(pos)=='Vector3' then slot.attachment.WorldPosition=pos s.Parent=slot.attachment else s.Parent=folder end
 s.PlaybackRegionsEnabled=true
 s.PlaybackRegion=NumberRange.new(offset,math.min(cache[id].TimeLength,offset+slot.duration*pitch))
 s.TimePosition=offset s.Volume=volume s:Play()
 eventsActive[slot.key]=(eventsActive[slot.key] or 0)+1
 metrics.played+=1 metrics.peak=math.max(metrics.peak,activeCount())
 metrics.events[job.name]=(metrics.events[job.name] or 0)+1
 local h=metrics.history
 table.insert(h,{event=job.name,id=id,pitch=pitch,volume=volume,time=slot.started,remote=remote,duration=slot.duration,offset=offset})
 if #h>160 then table.remove(h,1) end
 return true
end
local function audible(opts)
 if typeof(opts.pos)~='Vector3' then return true end
 local cam=workspace.CurrentCamera
 return cam and (cam.CFrame.Position-opts.pos).Magnitude< (opts.maxDistance or (opts.remote and 44 or 70))
end
function S.Duck(amount,duration)
 duckTarget=math.min(duckTarget,math.clamp(amount or .7,.35,1))
 duckUntil=math.max(duckUntil,os.clock()+(duration or 1.3))
end
function S.tocar(name,options)
 if destroyed then return false end
 local ev=Catalog.Events[name] if not ev then return false end
 local opts=options or {}
 metrics.requests+=1
 if not audible(opts) then return reject() end
 if opts.remote and ev.bus=='Rewards' then return reject() end
 local now=os.clock()
 if name=='ui_notify' and now-lastReward<.65 then return false end
 local key=name..(opts.remote and ':remote' or ':local')
 if now-(lastEvent[key] or -100)<ev.gap or (eventsActive[key] or 0)>=ev.max*#ev.layers then return reject() end
 if pref('Master')<=0 or (ev.bus=='UI' and groups.UI.Volume<=0) or (ev.bus=='Mining' and groups.Mining.Volume<=0) then return false end
 lastEvent[key]=now
 if ev.bus=='Rewards' and ev.priority>=70 then lastReward=now end
 if ev.duck then S.Duck(ev.duck,1.5) end
 for i,layer in ipairs(ev.layers) do
  if opts.remote and i>1 then break end
  if opts.auto and i>1 and ev.bus=='Mining' and random:NextNumber()<.35 then continue end
  local job={name=name,ev=ev,layer=layer,opts=opts,at=now+(layer.delay or 0)}
  if layer.delay and layer.delay>0 then
   if #queue<48 then table.insert(queue,job) else metrics.dropped+=1 end
  else playLayer(job) end
 end
 return true
end
local pickupPending,pickupAt,combo,lastPickup=0,0,0,-100
local comboNotes={0,2,4,7,12}
function S.coleta(_pos)
 if player:GetAttribute('SomMineracaoEnabled')==false then return false end
 pickupPending=math.min(1000,pickupPending+1)
 if pickupAt==0 then pickupAt=os.clock()+.065 end
 return true
end
local rarity={comum='comum',common='comum',incomum='incomum',uncommon='incomum',raro='raro',rare='raro',epico='epico',epica='epico',epic='epico',lendario='lendario',lendaria='lendario',legendary='lendario',mitico='mitico',mitica='mitico',mythic='mitico',secreto='secreto',secret='secreto'}
function S.drop(r) return S.tocar('drop_'..(rarity[string.lower(tostring(r))] or 'comum')) end
function S.quebra(variant,pos)
 local key=variant=='chefe' and 'chefe' or (rarity[variant] or 'comum')
 if key=='mitico' or key=='secreto' then key='lendario' end
 return S.tocar('break_'..key,{pos=pos})
end
function S.saleTier(gain)
 gain=type(gain)=='number' and gain==gain and math.max(0,gain) or 0
 if gain>=10000000 then return 5 elseif gain>=1000000 then return 4 elseif gain>=10000 then return 3 elseif gain>=1000 then return 2 end
 return 1
end
function S.venda(gain,_items)
 return S.tocar(Catalog.SaleNames[S.saleTier(gain)])
end
function S.hit(rock,opts)
 opts=opts or {}
 local name='hit'
 if rock then
  local kind=string.lower(tostring(rock:GetAttribute('OreType') or ''))
  local area=rock:GetAttribute('AreaId')
  if string.find(kind,'lava') then name='hit_lava'
  elseif area==2 or area==6 then name='hit_metal'
  elseif area==3 then name='hit_crystal'
  elseif area==4 then name='hit_magic' end
 end
 S.tocar(name,opts)
 if not opts.remote and rock then
  local hp,max=rock:GetAttribute('HP'),rock:GetAttribute('HPMax')
  if hp and max and hp>0 and max>0 and hp/max<.28 then S.tocar('rock_crack',opts) end
  if opts.heavy and not opts.auto then S.tocar('hit_pesado',opts) end
 end
end
-- AreaAtmosphere owns lighting. This controller is the only owner of music playback.
local musicSlots={}
for i=1,2 do local s=Instance.new('Sound') s.Name='AMS_Music_'..i s.Looped=true s.Volume=0 s.SoundGroup=groups.Music s.Parent=folder musicSlots[i]={sound=s,level=0,target=0} end
local requestedArea,currentArea=0,nil
function S.setArea(area) requestedArea=Catalog.Music[area] and area or 0 end
local function updateMusic(dt)
 if requestedArea~=currentArea then
  local track=Catalog.Music[requestedArea]
  local ref=cache[track.id]
  if ref and ref.IsLoaded then
   local target=musicSlots[1].level<=musicSlots[2].level and musicSlots[1] or musicSlots[2]
   for _,slot in ipairs(musicSlots) do if slot.area==requestedArea and slot.sound.IsPlaying then target=slot break end end
   for _,slot in ipairs(musicSlots) do slot.target=0 end
   if target.area~=requestedArea then target.sound:Stop() target.sound.SoundId='rbxassetid://'..track.id target.sound.TimePosition=0 target.level=0 target.sound.Volume=0 end
   target.area=requestedArea target.target=track.volume
   if not target.sound.IsPlaying then target.sound:Play() end
   currentArea=requestedArea player:SetAttribute('AreaMusicTitle',track.name)
  end
 end
 for _,slot in ipairs(musicSlots) do
  slot.level+=(slot.target-slot.level)*math.min(1,dt*2.3)
  slot.sound.Volume=slot.level
  if slot.target==0 and slot.level<.001 and slot.sound.IsPlaying then slot.sound:Stop() slot.level=0 end
 end
end
-- Four persistent ambient voices, shared by region beds and nearby physical emitters.
local loops,emitters={},{}
for i=1,Catalog.Budget.loops do
 local a=Instance.new('Attachment') a.Name='AMS_Ambient_'..i a.Parent=workspace.Terrain
 local s=Instance.new('Sound') s.Name='AMS_Loop_'..i s.Volume=0 s.Looped=true s.SoundGroup=groups.Ambience s.RollOffMode=Enum.RollOffMode.InverseTapered s.RollOffMinDistance=7 s.RollOffMaxDistance=42 s.Parent=a
 loops[i]={sound=s,attachment=a,level=0,target=0}
end
function S.RegisterEmitter(key,family,position,range,volume)
 if typeof(position)~='Vector3' or not Catalog.Assets[family] then return end
 emitters[key]={key=key,family=family,pos=position,range=range or 42,volume=volume or .15}
end
function S.RemoveEmitter(key) emitters[key]=nil end
function S.MoveEmitter(key,position) if emitters[key] and typeof(position)=='Vector3' then emitters[key].pos=position end end
local ambientTimer=0
local function updateAmbience(dt)
 ambientTimer+=dt
 if ambientTimer>=.25 then
  ambientTimer=0
  local cam=workspace.CurrentCamera
  local candidates={}
  if cam then
   for _,e in pairs(emitters) do local d=(cam.CFrame.Position-e.pos).Magnitude if d<e.range then table.insert(candidates,{e=e,score=d/e.range}) end end
   table.sort(candidates,function(a,b) return a.score<b.score end)
  end
  local desired={}
  -- One quiet regional bed plus up to three nearest physical sources.
  local area=player:GetAttribute('CurrentAreaId') or 0
  local family=area==4 and 'energy' or 'wind'
  desired[1]={key='region:'..area,family=family,volume=area==4 and .06 or .10,global=true}
  for i=1,math.min(3,#candidates) do table.insert(desired,candidates[i].e) end
  for _,slot in ipairs(loops) do slot.target=0 end
  local used={}
  for _,e in ipairs(desired) do
   local slot
   for _,v in ipairs(loops) do if v.key==e.key then slot=v break end end
   if not slot then for _,v in ipairs(loops) do if not used[v] and v.level<.004 then slot=v break end end end
   if slot then
    local id=Catalog.Assets[e.family][1]
    if id and cache[id] and cache[id].IsLoaded then
     if slot.key~=e.key then
      slot.sound:Stop() slot.sound.SoundId='rbxassetid://'..id slot.key=e.key
      slot.sound.TimePosition=random:NextNumber(0,math.max(0,cache[id].TimeLength-1))
     end
     if e.global then slot.sound.Parent=folder else slot.attachment.WorldPosition=e.pos slot.sound.Parent=slot.attachment slot.sound.RollOffMaxDistance=e.range end
     slot.target=e.volume used[slot]=true
     if not slot.sound.IsPlaying then slot.sound:Play() end
    end
   end
  end
 end
 for _,slot in ipairs(loops) do
  slot.level+=(slot.target-slot.level)*math.min(1,dt*3)
  local length=slot.sound.TimeLength
  local seam=length>1 and math.clamp(math.min(slot.sound.TimePosition,length-slot.sound.TimePosition)/.22,0,1) or 1
  slot.sound.Volume=slot.level*seam
  if slot.target==0 and slot.level<.001 and slot.sound.IsPlaying then slot.sound:Stop() slot.key=nil end
 end
end
table.insert(connections,Run.Heartbeat:Connect(function(dt)
 local now=os.clock()
 for _,slot in ipairs(pool) do if slot.active then
  local age=now-slot.started
  if age>=slot.duration or (age>.12 and not slot.sound.IsPlaying) then release(slot)
  else slot.sound.Volume=slot.level*math.clamp((slot.duration-age)/.035,0,1) end
 end end
 for i=#queue,1,-1 do local j=queue[i] if j.at<=now then table.remove(queue,i) if now-j.at<.18 then playLayer(j) else metrics.dropped+=1 end end end
 if pickupAt>0 and now>=pickupAt then
  if now-lastPickup>1.0 then combo=0 end
  combo=combo%#comboNotes+1 lastPickup=now
  S.tocar('coleta',{pitch=2^(comboNotes[combo]/12),volume=pickupPending>5 and .85 or 1})
  pickupPending=0 pickupAt=0
 end
 if now>duckUntil then duckTarget=1 end
 duckNow+=(duckTarget-duckNow)*math.min(1,dt*(duckTarget<duckNow and 14 or 3.5))
 mix() updateMusic(dt) updateAmbience(dt)
end))
function S.Diagnostics()
 local out={version=S.Version,active=activeCount(),remoteActive=activeCount(nil,true),peak=metrics.peak,requests=metrics.requests,played=metrics.played,dropped=metrics.dropped,stolen=metrics.stolen,created=metrics.created,queue=#queue,pending=metrics.pending,failed=table.clone(metrics.failed),assets={},history=table.clone(metrics.history),musicArea=currentArea,loops=0}
 for id,v in pairs(cache) do out.assets[tostring(id)]={loaded=v.IsLoaded,length=v.TimeLength} end
 out.events=table.clone(metrics.events)
 for _,v in ipairs(loops) do if v.sound.IsPlaying then out.loops+=1 end end
 return out
end
function S.StopEffects()
 for _,slot in ipairs(pool) do release(slot) end table.clear(queue) pickupPending=0 pickupAt=0
end
S.StopAll=S.StopEffects -- compatibility: callers historically use this for transient effects
function S.Destroy()
 if destroyed then return end destroyed=true S.StopAll()
 for _,c in ipairs(connections) do c:Disconnect() end
 for _,s in ipairs(pool) do s.sound:Destroy() s.attachment:Destroy() end
 for _,s in ipairs(loops) do s.sound:Destroy() s.attachment:Destroy() end
 folder:Destroy()
end
return S
