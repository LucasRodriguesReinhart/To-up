from pathlib import Path
root=Path(__file__).parent/'src'
p=root/'ReplicatedStorage/ExpeditionUI/Theme.lua';s=p.read_text(encoding='utf-8')
a=s.index('function T.headerOrnament(');b=s.index('\nfunction T.scaleOf',a)
s=s[:a]+'''function T.headerOrnament(p,w,h,col)
 local dark=col:Lerp(P.ink,.65)
 T.slant(p,"HeaderShadow",-8,4,w+3,h+4,P.ink,{tilt=18})
 T.slant(p,"HeaderRim",-9,-3,w+5,h+6,dark,{tilt=18})
 local plate=T.slant(p,"TitlePlate",-6,0,w,h,col,{top=col:Lerp(WHITE,.28),bottom=col:Lerp(P.ink,.18),tilt=18})
 T.texture(plate,"pattern",.90,dark,130)
 T.frame(p,"UpperLight",2,2,w-18,2,col:Lerp(WHITE,.60),.12)
 T.frame(p,"LowerShade",2,h-3,w-18,2,dark,.15)
 local gem=T.frame(p,"CrystalTip",w-20,h*.5-8,16,16,col:Lerp(WHITE,.22),0);gem.Rotation=45;T.stroke(gem,dark,2)
 return plate
end
'''+s[b:]
s=s.replace('Thickness=opts.selected and 2 or 1.25','Thickness=opts.selected and 3 or 2').replace('T.corner(inner,3);T.stroke(inner,opts.dim and P.lineSoft or col:Lerp(WHITE,.48),.7,.22)','T.corner(inner,5);T.stroke(inner,opts.dim and P.lineSoft or col:Lerp(WHITE,.62),1,.10)')
p.write_text(s,encoding='utf-8')
p=root/'StarterPlayer/StarterPlayerScripts/ExpeditionClient.lua';s=p.read_text(encoding='utf-8').replace('ctx.summonBusy=false;ctx.revealCommitted=true\n','ctx.summonBusy=false;ctx.revealCommitted=true\n   ctx.toast(result and result.msg or "Falha ao abrir estrela.",nil,"error")\n');p.write_text(s,encoding='utf-8')
p=root/'ReplicatedStorage/ExpeditionUI/Menus.lua';s=p.read_text(encoding='utf-8')
needle='local function passesStore(ctx, p, w, h)'
bundle='''local function starterBundle(ctx,parent,w)
 local product=Mon.produto("Starter");if not product then return 0 end
 local compact=w<660;local height=compact and 330 or 250
 local hero=T.panel(parent,"StarterBundle",0,0,w,height,{bg=P.bg1,strokeColor=P.gold,strokeWidth=2,radius=8})
 hero.ClipsDescendants=true
 T.texture(hero,"pattern",.96,P.gold,210)
 local heading=T.frame(hero,"Heading",10,10,math.min(340,w-24),44,nil,1);T.headerOrnament(heading,math.min(340,w-24),44,P.gold)
 T.text(heading,"Title","KIT DO EXPLORADOR",12,0,math.min(306,w-48),44,23,P.text,T.LEFT,"title")
 local items={{icon="coins",name="Pack de moedas M",detail="30 min de renda da sua ilha"},{icon="coins",name="Moedas ×2",detail="30 minutos"},{icon="potion",name="Sorte ×1,5",detail="15 minutos"}}
 local left=compact and 12 or 174;local itemWidth=(w-left-24)/3
 if not compact then T.icon(hero,"pickaxe",26,82,126,126) end
 for i,item in ipairs(items) do
  local x=left+(i-1)*(itemWidth+4)
  local f=T.tile(hero,"Included_"..i,x,70,itemWidth-8,116,i==3 and "epico" or "lendario",{})
  T.icon(f,item.icon,(itemWidth-64)/2,6,50,50)
  T.text(f,"Name",item.name,6,61,itemWidth-20,23,15,P.text,T.CENTER,"title")
  T.para(f,"Amount",item.detail,6,84,itemWidth-20,28,12,P.text2,T.CENTER)
 end
 local purchased=ctx.data.compras and (ctx.data.compras.Starter or 0)>0
 local info=ctx.marketInfo and ctx.marketInfo.Starter
 local live=product.id>0 and info and info.IsForSale~=false
 local caption=purchased and "Adquirido" or (live and info.PriceInRobux and (info.PriceInRobux.." Robux") or "Ver conteúdo")
 T.text(hero,"Policy","Uma vez por conta · benefícios detalhados",16,compact and 200 or 202,compact and w-32 or w-240,24,13,P.text2,T.LEFT)
 T.button(hero,"BundleCTA",caption,compact and 16 or w-216,compact and 248 or 194,compact and w-32 or 200,44,P.gold,function()
  if purchased then ctx.toast("Este bundle já está na sua conta.",nil,"info");return end
  ctx.popup("Kit do Explorador",function(p,pw,ph)
   T.para(p,"Contents","• Moedas equivalentes a 30 minutos de renda da sua ilha.\\n• Moedas ×2 nas vendas por 30 minutos.\\n• Sorte ×1,5 por 15 minutos.\\n• Cosmético Kunai de Ignis incluído no perfil.",8,8,pw-16,160,17,P.text,T.LEFT)
   T.para(p,"Availability",live and "Os benefícios são entregues após a confirmação do Roblox." or "Conteúdo preparado. Este bundle ainda não está à venda.",8,170,pw-16,52,14,P.text2,T.LEFT)
   T.button(p,"BuyBundle",live and caption or "Entendi",0,ph-48,pw,48,live and P.gold or P.neutral,function() if live then ctx.invoke("ComprarRobux","Starter") else ctx.closePopup() end end)
  end,560,400,{color=P.gold})
 end,{size=18})
 return height+18
end

'''
s=s.replace(needle,bundle+needle)
s=s.replace('local cw, y = w - 14, 0\n\tlocal groups','local cw, y = w - 14, 0\n y=starterBundle(ctx,scroll,cw)\n local products={};for _,def in ipairs(Mon.PRODUTOS) do if not def.starter then table.insert(products,def) end end\n\tlocal groups')
s=s.replace('defs = Mon.PRODUTOS }','defs = products }')
p.write_text(s,encoding='utf-8')
print('Shared components and integrated bundle refined')
