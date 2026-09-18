from pathlib import Path
r=Path(__file__).parent/'src'
def edit(p,fn):
 f=r/p;s=f.read_text(encoding='utf-8');f.write_text(fn(s),encoding='utf-8')
edit('ReplicatedStorage/ExpeditionUI/Theme.lua',lambda s:s.replace('size = math.max(minimum, size or 16)','local physicalMinimum=(font=="caption" or font=="footer") and 9 or (font=="display" and 16 or 11)\n\tsize = math.max(minimum, size or 16, physicalMinimum / math.max(.4,T.uiScale))').replace('T.new("UITextSizeConstraint", { MinTextSize = size, MaxTextSize = size }, t)','-- TextScaled=false already fixes the authored font size. A fixed UITextSizeConstraint\n\t-- incorrectly clamps the final rendered glyphs after UIScale and causes overflow.').replace('muzan={right=7,left=-16,re=18,le=67,turn=-7,head=9}','muzan={right=3,left=-22,re=9,le=88,turn=-7,head=9}'))
edit('ReplicatedStorage/ExpeditionUI/Inventory.lua',lambda s:s.replace('local filterButtonW = ctx.compact and 92 or 78','local filterButtonW = 92').replace('T.text(rowText, "Label", stat[1],','T.text(rowText, "Label", stat[1]=="Bônus de nível" and "Nível" or stat[1]=="Velocidade" and "Veloc." or stat[1],'))
edit('StarterPlayer/StarterPlayerScripts/ExpeditionClient.lua',lambda s:s.replace('and 6 or 0\n\tT.tween(blur','and 15 or 0\n\tT.tween(blur').replace('(compact and "Equipe" or "Inventário")','(compact and "Equipe" or "Unidades")'))
print('Typography now scales correctly with the interface.')
