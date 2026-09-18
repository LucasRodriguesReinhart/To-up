from pathlib import Path
import subprocess, shutil, html, zipfile, json
base=Path(__file__).resolve().parent
out=base/'preview'
ff=Path(r'C:/Users/lucas/AppData/Local/Programs/Python/Python314/Lib/site-packages/imageio_ffmpeg/binaries/ffmpeg-win-x86_64-v7.1.exe')
shutil.copyfile(base.parent/'ui-review-video/render-bold.ttf',out/'caption.ttf')
shots=[('Before','ANTES — inventário V4'),('Inventory','AGORA — inventário V5'),('Inventory_hat','Itens e acessórios'),('Feed','Alimentação e seleção por raridade'),('Summon','Invocações'),('HUD','HUD — organização preservada'),('Events','Recompensas diárias'),('Areas','Viagens'),('Settings','Configurações'),('Equipment_Mochilas','Equipamentos de Ignis'),('Mobile_Inventory_pet','Celular horizontal — inventário'),('Mobile_Summon','Celular horizontal — invocações'),('Mobile_Events_Diario','Celular horizontal — diário')]
parts=[]
for i,(key,title) in enumerate(shots,1):
    (out/f'caption-{i:02}.txt').write_text(f'{i:02}/{len(shots)}  •  {title}',encoding='utf-8')
    target=f'part-{i:02}.mp4'
    filt=f"scale=1280:622:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:58+(622-ih)/2:color=0x071014,setsar=1,drawtext=fontfile=caption.ttf:textfile=caption-{i:02}.txt:fontcolor=white:fontsize=25:x=28:y=17,drawtext=fontfile=caption.ttf:text='UI V5 - sequencia de capturas reais - sem audio':fontcolor=0xaac1c9:fontsize=15:x=28:y=692"
    subprocess.run([str(ff),'-y','-loglevel','error','-loop','1','-framerate','24','-i',key+'.png','-t','4','-vf',filt,'-c:v','libx264','-preset','fast','-crf','21','-pix_fmt','yuv420p','-threads','2',target],cwd=out,check=True)
    parts.append(target)
(out/'concat.txt').write_text(''.join(f"file '{p}'\n" for p in parts),encoding='utf-8')
video=base/'Previa-UI-V5.mp4'
subprocess.run([str(ff),'-y','-loglevel','error','-f','concat','-safe','0','-i','concat.txt','-c','copy','-movflags','+faststart',str(video)],cwd=out,check=True)
subprocess.run([str(ff),'-v','error','-i',str(video),'-f','null','-'],check=True)
cards=''.join(f'<figure><figcaption>{i:02}. {html.escape(title)}</figcaption><a href="{key}.png"><img loading="lazy" src="{key}.png" alt="{html.escape(title)}"></a></figure>' for i,(key,title) in enumerate(shots,1))
(out/'Revisao-UI-V5.html').write_text('<!doctype html><html lang="pt-br"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>UI V5</title><style>body{background:#071014;color:#fff;font:16px system-ui;max-width:1280px;margin:24px auto;padding:0 16px}p{color:#b8cbd0;line-height:1.5}figure{margin:32px 0}figcaption{font-weight:bold;margin-bottom:10px}img{width:100%}a{color:#29c5ed}</style><h1>Anime Mining Simulator — UI V5</h1><p>Comparação visual com a versão anterior. Layout preservado, novo acabamento inspirado em Anime Expeditions. As imagens abaixo são capturas reais do Roblox Studio; celular em modo horizontal.</p>'+cards,encoding='utf-8')
bundle=base/'Revisao-UI-V5.zip'
with zipfile.ZipFile(bundle,'w',zipfile.ZIP_DEFLATED) as z:
    z.write(video,video.name);z.write(base/'QA.md','LEIA-ME.md')
    z.write(out/'Revisao-UI-V5.html','capturas/Revisao-UI-V5.html')
    for key,_ in shots:z.write(out/(key+'.png'),'capturas/'+key+'.png')
print(json.dumps({'video_bytes':video.stat().st_size,'zip_bytes':bundle.stat().st_size,'seconds':52,'captures':13}),flush=True)
