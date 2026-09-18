-- AMS Audio V3. Licensed Roblox library sources; see ASSET_CANDIDATES.json.
-- Short playback windows are envelopes, not new uploaded derivative assets.
local C = {}
C.Version = 3
C.Budget = {voices=24, Mining=10, Rewards=8, UI=3, World=4, remote=4, loops=4}
C.Defaults = {Master=.8, Music=.6, SFX=.85, UI=.65, Ambience=.55}
C.Assets = {
 stone={9118598279,9118598469,9118598729,9118598470,9118598240},
 metal={9116651255,9116652339}, heavy={9118617342},
 crack={9118612665,9125869797}, debris={9118690959},
 swing={9120972321,9120972444,9120972323},
 click={9119717523,9119717529}, tone={9125531715}, glass={9114619221}, coin={9125509503,9125444889},
 fire={9112780438}, wind={9116258071}, water={9112855484}, energy={9125515917},
}
-- Measured from Roblox AudioPlayer waveform data, 2026-09-17 (1500 points/asset).
-- Start just before the audible attack; compensate source loudness, not event importance.
C.Trim={
 [9118598279]={offset=0,gain=1.0}, [9118598469]={offset=0,gain=1.0},
 [9118598729]={offset=0,gain=.90}, [9118598470]={offset=0,gain=1.12}, [9118598240]={offset=.002,gain=.90},
 [9120972321]={offset=.065,gain=.90}, [9120972444]={offset=.016,gain=1.55}, [9120972323]={offset=.056,gain=1.15},
 [9125509503]={offset=.344,gain=1.25}, [9125444889]={offset=0,gain=.95},
 [9114619221]={offset=.108,gain=2.4}, [9125531715]={offset=.200,gain=2.0},
}
-- A coherent dry-metal/crystal voice; reward figures use C-D-E-G across octaves.
local A=C.Assets
local function L(family,vol,duration,pitch,delay)
 return {family=family,volume=vol,duration=duration,pitch=pitch or 1,delay=delay or 0,variation=(family=='tone' or family=='coin') and 0 or .035}
end
local E={}
local function event(name,bus,priority,gap,layers,max)
 E[name]={bus=bus,priority=priority,gap=gap,max=max or 3,layers=layers}
end
event('hit','Mining',75,.045,{L('stone',.44,.32),L('metal',.12,.17,1.04)},5)
event('hit_pesado','Mining',70,.13,{L('heavy',.17,.32,.94)},2)
event('hit_crystal','Mining',74,.045,{L('stone',.32,.27),L('glass',.12,.26,1.12)},4)
event('hit_metal','Mining',74,.045,{L('stone',.30,.24),L('metal',.17,.24,.97)},4)
event('hit_magic','Mining',74,.045,{L('stone',.34,.28),L('tone',.11,.30,1.26)},4)
event('hit_lava','Mining',74,.045,{L('stone',.35,.28),L('heavy',.13,.32,.90)},4)
event('rock_crack','Mining',68,.30,{L('crack',.14,.24,1.08)},2)
event('critical_hit','Mining',80,.20,{L('metal',.14,.2,1.12),L('tone',.10,.22,1.5)},2)
event('whoosh','Mining',50,.13,{L('swing',.17,.21,1.02)},3)
for i,name in ipairs({'comum','incomum','raro','epico','lendario','chefe'}) do
 local layers={L('crack',.43,.48+(i-1)*.035,1.03-(i-1)*.017),L('debris',.09,.35,1,.055)}
 if i>=3 then table.insert(layers,L('tone',.11,.33,({1,1,1.25,1.5,2,1})[i],.09)) end
 event('break_'..name,'Mining',85,.1,layers,2)
end
event('ore_drop','Rewards',40,.15,{L('tone',.07,.14,1.12)},2)
event('coleta','Rewards',58,.075,{L('tone',.14,.14,1)},3)
event('coin_tick','Rewards',35,.12,{L('coin',.09,.12,1.12)},2)
local saleNames={'venda_pequena','venda_media','venda_grande','venda_enorme','venda_jackpot'}
for i,name in ipairs(saleNames) do
 local layers={L('click',.16,.12,1),L('coin',.20,.20,1,.06)}
 if i>=2 then table.insert(layers,L('coin',.16,.20,1.25,.15)) end
 if i>=3 then table.insert(layers,L('tone',.18,.38,1.5,.24)) end
 if i>=4 then table.insert(layers,L('tone',.17,.50,2,.36)) end
 if i==5 then table.insert(layers,L('heavy',.12,.32,.9,.02)) end
 event(name,'Rewards',80,.65,layers,1)
end
local function motif(name,notes,priority,duration)
 local layers={}
 for i,n in ipairs(notes) do table.insert(layers,L('tone',.22-((i-1)*.014),duration or .34,2^(n/12),(i-1)*.105)) end
 event(name,'Rewards',priority or 80,.65,layers,1)
end
motif('upgrade',{0,4,7},80)
motif('upgrade_max',{0,4,7,12},86,.45)
motif('level_up',{0,2,7,12},88,.48)
motif('area_nova',{0,7,4,12},91,.55)
motif('quest_complete',{4,7,12},82)
motif('achievement',{0,4,12},83)
motif('boost',{0,7},72)
motif('reward_banner',{0,4,7},74)
motif('forge_success',{0,7,12},82)
event('forge_interact','World',54,.4,{L('metal',.15,.25,.95)},1)
event('forge_hammer','World',28,.50,{L('metal',.19,.27,.94),L('heavy',.06,.2,1)},1)
event('invocar_inicio','Rewards',65,.4,{L('swing',.16,.38,.95),L('tone',.10,.35,.75,.13)},1)
event('summon_reveal','Rewards',65,.18,{L('tone',.14,.23,1.12)},1)
motif('drop_comum',{0},65,.2)
motif('drop_incomum',{0,4},69,.26)
motif('drop_raro',{0,7},75,.36)
motif('drop_epico',{0,4,7},82,.42)
motif('drop_lendario',{0,4,7,12},90,.60)
motif('drop_mitico',{0,7,12,16},94,.64)
event('drop_secreto','Rewards',100,1.3,{
 L('swing',.14,.27,.78),L('heavy',.13,.27,.91,.21),
 L('tone',.24,.65,1,.28),L('tone',.19,.65,1.5,.40),L('tone',.18,.72,2,.54),L('tone',.14,.75,2.5,.67),
},1)
E.drop_lendario.duck=.75 E.drop_mitico.duck=.62 E.drop_secreto.duck=.48 E.area_nova.duck=.70
event('portal_saida','World',70,.6,{L('swing',.22,.40,.85),L('tone',.12,.45,.75,.09)},1)
event('portal_chegada','World',65,.6,{L('swing',.14,.30,1.04),L('tone',.10,.28,1.25)},1)
event('ui_click','UI',60,.055,{L('click',.17,.075,1)},2)
event('ui_hover','UI',15,.18,{L('click',.035,.04,1.04)},1)
event('ui_tab','UI',48,.075,{L('click',.11,.065,1.05)},1)
event('ui_toggle','UI',50,.075,{L('click',.12,.08,.94)},1)
event('ui_abrir','UI',53,.12,{L('swing',.12,.14,1.06),L('click',.07,.07,1)},1)
event('ui_fechar','UI',53,.12,{L('swing',.09,.12,.94)},1)
event('ui_popup','UI',49,.15,{L('swing',.09,.14,1.1)},1)
event('ui_notify','UI',40,.4,{L('tone',.085,.13,1.12)},1)
event('ui_equipar','UI',68,.16,{L('swing',.11,.13,1.02),L('metal',.16,.18,1,.04)},1)
event('ui_desequipar','UI',60,.16,{L('metal',.10,.13,.92)},1)
event('ui_compra','UI',68,.2,{L('click',.15,.09),L('tone',.14,.2,1.25,.07)},1)
event('ui_confirm','UI',62,.15,{L('tone',.11,.17,1),L('tone',.10,.19,1.25,.065)},1)
event('ui_cancel','UI',50,.15,{L('click',.1,.1,.9)},1)
event('ui_erro','UI',70,.32,{L('click',.14,.1,.84),L('click',.10,.11,.75,.10)},1)
C.Events=E
C.Music={
 [0]={id=112898538778548,name='Lobby',volume=.23},
 [1]={id=82061470648013,name='Hidden Lotus Pond',volume=.22},
 [2]={id=1845421369,name='Space Atmosphere',volume=.23},
 [3]={id=9048681794,name='Mysterious Forest',volume=.20},
 [4]={id=131334832939011,name='The Forgotten Crypt',volume=.20},
 [5]={id=1835322563,name='Pirate King',volume=.20},
 [6]={id=1845676363,name='Home Bound',volume=.21},
}
C.SaleNames=saleNames
return C
