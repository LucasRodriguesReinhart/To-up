from pathlib import Path
p=Path(__file__).parent/'src'
def edit(path,changes):
 f=p/path;s=f.read_text(encoding='utf-8')
 for a,b in changes:
  assert a in s,a[:80]
  s=s.replace(a,b)
 f.write_text(s,encoding='utf-8')
edit('ReplicatedStorage/ExpeditionUI/Theme.lua',[
 ('math.max(18,opts.size or 22)','math.max(14,opts.size or 22)'),
 # Roblox image assets use a 1024 pixel atlas after processing larger uploads.
 ('627','512'),
])
edit('StarterPlayer/StarterPlayerScripts/ExpeditionClient.lua',[
 ('local tw=math.min(#items*140,ww-40)','local tw=math.min(#items*(ctx.compact and 174 or 160),ww-40)'),
 ('title=ctx.eventsTab=="Index" and "Coleção" or "Recompensas diárias"','title=ctx.eventsTab=="Index" and "Coleção" or ctx.compact and "Diário" or "Recompensas diárias"'),
 ('hudRefs.bag.Text = "MOCHILA  " .. T.format','hudRefs.bag.Text = T.format'),
 ('it.id=="Inventory" and "Inventário" or it.label','it.id=="Inventory" and (compact and "Equipe" or "Inventário") or it.label'),
])
edit('ReplicatedStorage/ExpeditionUI/Inventory.lua',[
 ('local filterButtonW = 78','local filterButtonW = ctx.compact and 92 or 78'),
 ('.. " equipados", gridW * .55','.. (ctx.compact and "" or " equipados"), gridW * .55'),
 ('local tone=color and color~=P.text and color or P.neutral','local tones={UpgradeSelected=P.violet,FavoriteToggle=P.gold:Lerp(P.ink,.35),LockToggle=P.info:Lerp(P.ink,.30),RenameSelected=P.neutral}\n local tone=tones[name] or (color and color~=P.text and color or P.neutral)'),
 ('local label = T.text(labels, "Label", stat[1], 44, 0, cw * .48 - 40, 45, cw >= 310 and 20 or 17','local label = T.text(labels, "Label", ctx.compact and (stat[4]=="dano" and "Dano" or stat[4]=="nivel" and "Nível" or stat[1]=="Bônus de nível" and "Nível" or stat[1]=="Velocidade" and "Veloc." or stat[1]) or stat[1], 44, 0, cw * .48 - 40, 45, cw >= 310 and 20 or 15'),
 ('"Favoritos e proteção valem nesta sessão e impedem o consumo pela interface."','"Favoritos e protegidos não são consumidos nesta sessão."'),
 ('total .. " cópia(s) deste item no inventário"','total .. " cópia(s)"'),
])
# Each menu already has a bounded scroll. Avoid nesting a 620px desktop canvas on phones.
edit('ReplicatedStorage/ExpeditionUI/Menus.lua',[
 ('if h < 380 and ctx.page ~= "Summon" then','if h < 380 and ctx.page ~= "Summon" and not ctx.compact then'),
])
print('Refinements applied')
