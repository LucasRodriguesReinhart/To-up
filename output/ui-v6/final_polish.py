from pathlib import Path
r=Path(__file__).parent/'src'
p=r/'ReplicatedStorage/ExpeditionUI/Menus.lua';s=p.read_text(encoding='utf-8')
a=s.index('  local iw=math.min(170,h*.34)');b=s.index('  return\n end',a)
s=s[:a]+'''  local low=h<320
  local iw=low and 90 or 130
  T.image(card,"OfficialPassIcon","rbxthumb://type=GamePass&id=1983332510&w=150&h=150",low and 22 or (w-iw)/2,18,iw,iw)
  T.text(card,"Title","Forja portátil",low and 130 or 16,low and 24 or iw+28,low and w-148 or w-32,36,28,P.ember,low and T.LEFT or T.CENTER,"title")
  T.para(card,"Requirement","Venda de qualquer ilha com o passe Portable Ignis Forge.",low and 130 or 24,low and 66 or iw+76,low and w-148 or w-48,58,18,P.text2,low and T.LEFT or T.CENTER)
  local bw=math.min(300,(w-60)/2)
  T.button(card,"GetForge","Ver gamepass",w/2-bw-7,h-72,bw,52,P.ember,function() ctx.invoke("ComprarRobux","PortableForge") end,{size=19})
  T.button(card,"VisitIgnis","Ir ao Ignis · grátis",w/2+7,h-72,bw,52,P.neutral,function() ctx.travel("ignis") end,{size=18})
''' + s[b:]
s=s.replace('local productTone = owned and P.success or ((def.boost == "sorte" or def.chave == "Lucky") and P.violet or P.accent)','local productTone = def.chave=="PortableForge" and P.ember or (def.chave=="VIP" and P.gold or ((def.boost == "sorte" or def.chave == "Lucky" or def.chave=="LuckyPlus") and P.success or P.accent))')
s=s.replace('local card = artSurface(scroll, "Product_" .. def.chave, ((i - 1) % cols) * (cardW + GAP), y + math.floor((i - 1) / cols) * 234, cardW, 222, productTone, nil)','local card = T.panel(scroll, "Product_" .. def.chave, ((i - 1) % cols) * (cardW + GAP), y + math.floor((i - 1) / cols) * 234, cardW, 222, {bg=P.bg1,strokeColor=productTone:Lerp(P.ink,.35)})\n            T.texture(card,"pattern",.95,productTone,220)\n            T.frame(card,"ColorEdge",3,3,cardW-6,2,productTone,.2)')
s=s.replace('T.slant(card, "IconPlate", 8, 8, 62, 58, productTone, { alpha = .7, tilt = 20 })','-- Official circular pass art supplies the card identity.')
s=s.replace('.."&w=150&h=150",6,6,66,66)','.."&w=150&h=150",8,8,80,80)')
s=s.replace('label(card, "Name", def.nome, 72, 14, cardW - 86, 26, 19)','label(card, "Name", def.nome, 96, 18, cardW - 108, 44, 18)')
s=s.replace('text(card, "State", state, 72, 42, cardW - 86, 20, 13','text(card, "State", state, 96, 63, cardW - 108, 20, 13')
s=s.replace('T.para(card, "Benefit", def.desc or "", 16, 76, cardW - 32, 74, 15','T.para(card, "Benefit", def.desc or "", 16, 96, cardW - 32, 56, 15')
p.write_text(s,encoding='utf-8')
p=r/'StarterPlayer/StarterPlayerScripts/ExpeditionClient.lua';s=p.read_text(encoding='utf-8')
s=s.replace('local function windowRect()','''local function windowRect()
 if ctx.page=="Forge" and ctx.forgeMode~="npc" and not(ctx.data and ctx.data.passes and ctx.data.passes.PortableForge) then
  local ww,wh=math.min(760,virtualW-28),math.min(470,virtualH-24)
  return ww,wh,(virtualW-ww)/2,(virtualH-wh)/2
 end''')
p.write_text(s,encoding='utf-8')
print('Compact forge lock and illustrated pass cards polished.')
