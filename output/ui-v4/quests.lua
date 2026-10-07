function M.progress(ctx,p,w,h)
 local d=ctx.data
 local selected=ctx.questArea or Players.LocalPlayer:GetAttribute("CurrentAreaId") or 1
 if not Config.areaPorId(selected) then selected=1 end
 ctx.questArea=selected
 local railW=w<900 and 170 or 240
 local gutter=20
 local rw=w-railW-gutter
 local rail=T.scroll(p,"QuestIslands",0,0,railW,h,P.violet)
 for i,a in ipairs(Config.Areas) do
  local y=(i-1)*82
  local col=Config.Temas[a.tema].cor
  local b=T.new("TextButton",{Name="Island_"..a.id,Text="",Position=UDim2.fromOffset(3,y+3),Size=UDim2.fromOffset(railW-16,70),BackgroundColor3=P.ink,BorderSizePixel=0,ClipsDescendants=true},rail)
  T.corner(b,7);T.stroke(b,selected==a.id and P.text or col,selected==a.id and 3 or 1.5)
  local art=T.image(b,"Island",T.areaImage(a.id),0,0,railW-16,70);art.ScaleType=Enum.ScaleType.Crop;art.ImageColor3=Color3.fromRGB(115,110,130)
  T.frame(b,"Shade",0,0,railW-16,70,P.ink,.52)
  T.para(b,"Name",a.nome,10,8,railW-36,40,w<900 and 19 or 22,P.text,T.LEFT,"title")
  local done,total=0,0
  for _,q in ipairs(Config.Missoes[a.id] or {}) do total+=1;if d.missoes and d.missoes[q.id] and d.missoes[q.id].r then done+=1 end end
  T.text(b,"Progress",hasArea(ctx,a.id) and (done.." / "..total.." concluídas") or "Bloqueada",10,47,railW-36,18,12,hasArea(ctx,a.id) and col or P.text3,T.LEFT,"label",1)
  T.bindInteraction(b,function() ctx.questArea=a.id;ctx.refresh() end)
 end
 rail.CanvasSize=UDim2.fromOffset(0,#Config.Areas*82)
 local a=Config.areaPorId(selected)
 local col=Config.Temas[a.tema].cor
 local content=T.frame(p,"MissionBoard",railW+gutter,0,rw,h,nil,1)
 T.text(content,"IslandTitle",a.nome,0,0,rw-200,42,30,P.text,T.LEFT,"title",2)
 local ready,list={},{}
 for i,q in ipairs(Config.Missoes[selected] or {}) do
  local state=d.missoes and d.missoes[q.id] or {p=0,r=false}
  local rank=state.r and 3 or state.p>=q.meta and 1 or 2
  table.insert(list,{def=q,state=state,rank=rank,index=i})
  if rank==1 then table.insert(ready,q) end
 end
 table.sort(list,function(x,y) if x.rank~=y.rank then return x.rank<y.rank end;return x.index<y.index end)
 action(ctx,content,"ClaimAll","Resgatar todas",rw-190,0,190,46,function()
  local received=0;ctx.batchQuestAudio=true
  local ok,err=pcall(function() for _,q in ipairs(ready) do local result=ctx.invoke("ResgatarMissao",q.id);if result and result.ok then received+=q.premio end end end)
  ctx.batchQuestAudio=false
  if received>0 then T.som("quest_complete");ctx.coinBurst(received) end
  ctx.refresh();if not ok then error(err) end
 end,hasArea(ctx,selected) and #ready>0,"Complete uma missão para resgatar.",P.success,"ClaimQuests")
 local scroll=T.scroll(content,"Quests",0,62,rw,h-62,col)
 local cw=rw-14
 if not hasArea(ctx,selected) then
  T.lock(scroll,28,28,58,col)
  T.para(scroll,"Locked","Desbloqueie "..a.nome.." para começar estas missões.",106,25,cw-130,85,23,P.text,T.LEFT,"title")
  T.button(scroll,"ViewIsland","Ver ilha",106,124,240,52,col,function() ctx.open("Areas") end)
  scroll.CanvasSize=UDim2.fromOffset(0,210);return
 end
 for i,item in ipairs(list) do
  local q,state=item.def,item.state
  local claimed,readyNow=item.rank==3,item.rank==1
  local rowH=138
  local tone=claimed and P.neutral or readyNow and P.success or col
  local row=T.panel(scroll,"Quest_"..q.id,3,(i-1)*(rowH+14)+3,cw-6,rowH,{bg=P.bg1,strokeColor=tone,strokeWidth=2})
  T.texture(row,"halftone",.89,tone,180)
  T.frame(row,"Accent",0,10,4,rowH-20,tone,0)
  local iconBG=T.panel(row,"Medallion",14,16,56,56,{bg=tone:Lerp(P.ink,.76),strokeColor=tone,strokeWidth=1.5})
  T.icon(iconBG,QUEST_ICON[q.tipo] or "quests",2,2,52,52)
  local tw=cw-264
  T.para(row,"Title",q.texto,84,12,tw,56,21,claimed and P.text3 or P.text,T.LEFT,"title")
  T.progress(row,"Progress",84,84,tw,23,math.min(state.p or 0,q.meta)/math.max(1,q.meta),tone,{text=T.format(math.min(state.p or 0,q.meta)).." / "..T.format(q.meta),textSize=15,segments=4})
  T.text(row,"State",claimed and "CONCLUÍDA" or readyNow and "RECOMPENSA LIBERADA" or "EM ANDAMENTO",84,113,tw,18,12,tone,T.LEFT,"label",1)
  local rx=cw-164
  T.icon(row,"coins",rx+10,8,46,46)
  T.text(row,"Reward",T.format(q.premio),rx+58,12,98,40,22,P.gold,T.LEFT,"number",2)
  if claimed then T.text(row,"Claimed","✓ Resgatada",rx,66,150,46,20,P.success,T.CENTER,"title",1.5)
  else
   action(ctx,row,"Claim_"..q.id,readyNow and "Resgatar" or "Em curso",rx,68,150,50,function()
    local res=ctx.invoke("ResgatarMissao",q.id)
    if res and res.ok then ctx.coinBurst(q.premio);ctx.refresh() end
   end,readyNow,"Complete o objetivo para resgatar.",readyNow and P.success or P.neutral,"ClaimQuests")
  end
 end
 scroll.CanvasSize=UDim2.fromOffset(0,#list*152+4)
 if #list==0 then T.emptyState(scroll,"Empty","Nenhuma missão","Esta ilha ainda não tem objetivos disponíveis.",0,0,cw,200) end
end
