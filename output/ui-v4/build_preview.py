from pathlib import Path
import subprocess,shutil,json,html,zipfile

base=Path(__file__).resolve().parent
out=base/'preview'
ff=Path(r'C:/Users/lucas/AppData/Local/Programs/Python/Python314/Lib/site-packages/imageio_ffmpeg/binaries/ffmpeg-win-x86_64-v7.1.exe')
shutil.copyfile(base.parent/'ui-review-video/render-bold.ttf',out/'caption.ttf')
shots=[('hud','HUD e novos ícones'),('inventory','Inventário de unidades'),('hats','Itens e acessórios'),('filters','Busca e filtros'),('quests','Missões por ilha'),('Events','Recompensas diárias'),('Settings','Configurações'),('Areas','Áreas e viagens'),('bags','Equipamentos de Ignis'),('celebration','Celebrações'),('reveal','Revelação de unidade'),('phone_hud','Celular horizontal — HUD'),('phone_inventory','Celular horizontal — inventário'),('phone_feed','Celular horizontal — alimentação')]
parts=[]
for i,(key,title) in enumerate(shots,1):
    (out/f'caption-{i:02}.txt').write_text(f'{i:02}/14  •  {title}',encoding='utf-8')
    target=f'part-{i:02}.mp4'
    filt=f"scale=1280:622:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:58+(622-ih)/2:color=0x090912,setsar=1,drawtext=fontfile=caption.ttf:textfile=caption-{i:02}.txt:fontcolor=white:fontsize=25:x=28:y=17,drawtext=fontfile=caption.ttf:text='UI V4 - capturas reais de teste - sem audio':fontcolor=0xbfbfce:fontsize=15:x=28:y=692"
    cmd=[str(ff),'-y','-loglevel','error','-loop','1','-framerate','24','-i',key+'.png','-t','4','-vf',filt,'-c:v','libx264','-preset','fast','-crf','22','-pix_fmt','yuv420p','-threads','2',target]
    subprocess.run(cmd,cwd=out,check=True)
    parts.append(target)
    print(title,flush=True)
(out/'concat.txt').write_text(''.join(f"file '{p}'\n" for p in parts),encoding='utf-8')
video=base/'Previa-UI-V4.mp4'
subprocess.run([str(ff),'-y','-loglevel','error','-f','concat','-safe','0','-i','concat.txt','-c','copy','-movflags','+faststart',str(video)],cwd=out,check=True)
subprocess.run([str(ff),'-v','error','-i',str(video),'-f','null','-'],check=True)
cards=''.join(f'<figure><figcaption>{i:02}. {html.escape(title)}</figcaption><a href="{key}.png"><img loading="lazy" src="{key}.png" alt="{html.escape(title)}"></a></figure>' for i,(key,title) in enumerate(shots,1))
(out/'Revisao-UI-V4.html').write_text('<!doctype html><html lang="pt-br"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Revisão UI V4</title><style>body{background:#0d0b16;color:#f7f4ff;font:16px system-ui;margin:24px auto;max-width:1280px;padding:0 16px}h1{font-size:28px}p{color:#c5bfd5;line-height:1.6}figure{margin:36px 0}figcaption{font-weight:bold;margin-bottom:12px}img{width:100%;border-radius:8px}a{color:#bcabff}</style><h1>Anime Mining Simulator — UI V4</h1><p>14 capturas reais da revisão no Roblox Studio. Celular em modo horizontal. Esta prévia mostra telas estáticas; as animações devem ser avaliadas dentro do jogo. Os ícones oficiais dos passes aguardam seu envio.</p><p>A grade aprovada do diário foi mantida. O atalho de equipamentos na tela de viagem agora leva ao Ignis; a captura dessa tela foi feita antes de atualizar o rótulo.</p>'+cards,encoding='utf-8')
bundle=base/'Revisao-UI-V4.zip'
with zipfile.ZipFile(bundle,'w',zipfile.ZIP_DEFLATED) as z:
    z.write(video,video.name)
    z.write(base/'QA.md','LEIA-ME.md')
    z.write(out/'Revisao-UI-V4.html','capturas/Revisao-UI-V4.html')
    for key,_ in shots:z.write(out/(key+'.png'),'capturas/'+key+'.png')
print(json.dumps({'video_bytes':video.stat().st_size,'zip_bytes':bundle.stat().st_size,'seconds':56,'captures':14}),flush=True)
