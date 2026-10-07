import json, math, subprocess, wave
from pathlib import Path
import imageio_ffmpeg

ROOT=Path(__file__).resolve().parent
FF=imageio_ffmpeg.get_ffmpeg_exe()
chapters=json.loads((ROOT/'chapters.json').read_text(encoding='utf-8'))
cursor=0.0
vtt=['WEBVTT','']
def stamp(t):
    ms=round(t*1000);h,ms=divmod(ms,3600000);m,ms=divmod(ms,60000);s,ms=divmod(ms,1000)
    return f'{h:02}:{m:02}:{s:02}.{ms:03}'
def run(args):
    p=subprocess.run([FF,'-hide_banner','-loglevel','error','-y',*args],cwd=ROOT,capture_output=True,text=True)
    if p.returncode: raise RuntimeError(p.stderr[-4000:])
for c in chapters:
    with wave.open(str(ROOT/'audio'/f'{c["id"]}.wav'),'rb') as w: d=w.getnframes()/w.getframerate()
    duration=math.ceil((d+1.2)*24)/24
    c.update(start=cursor,end=cursor+duration,duration=duration)
    title=f'{c["number"]:02} / {len(chapters)}   {c["title"]}'
    (ROOT/'segments'/f'{c["id"]}-title.txt').write_text(title,encoding='utf-8')
    foot='Prévia visual da interface' if c['demo'] else 'Captura real da interface no Roblox Studio'
    foot+='   •   Avalie esta tela no questionário'
    (ROOT/'segments'/f'{c["id"]}-footer.txt').write_text(foot,encoding='utf-8')
    filt=("scale=1200:660:force_original_aspect_ratio=decrease:flags=lanczos,setsar=1,"
          "pad=1280:800:(ow-iw)/2:78:color=0x0c0914,"
          "drawbox=x=0:y=0:w=1280:h=62:color=0x1c1231:t=fill,"
          "drawbox=x=0:y=62:w=1280:h=3:color=0xaa65ff:t=fill,"
          f"drawtext=fontfile=render-bold.ttf:textfile=segments/{c['id']}-title.txt:fontcolor=white:fontsize=27:x=32:y=17,"
          f"drawtext=fontfile=render-regular.ttf:textfile=segments/{c['id']}-footer.txt:fontcolor=0xd2c5e4:fontsize=17:x=32:y=767,"
          "format=yuv420p")
    run(['-loop','1','-framerate','24','-i',c['image'],'-i',f'audio/{c["id"]}.wav',
         '-vf',filt,'-af',f'apad,afade=t=out:st={duration-.25}:d=0.25','-t',str(duration),
         '-c:v','libx264','-preset','fast','-tune','stillimage','-crf','19','-pix_fmt','yuv420p',
         '-c:a','aac','-b:a','160k','-ar','48000','-ac','2','-movflags','+faststart',f'segments/{c["id"]}.mp4'])
    # Sentence-sized subtitles follow the narration approximately; chapters remain exact.
    sentences=[s.strip()+'.' for s in c['narration'].split('.') if s.strip()]
    weights=[len(s) for s in sentences];off=cursor
    for s,wgt in zip(sentences,weights):
        length=d*wgt/sum(weights)
        vtt.extend([f'{stamp(off)} --> {stamp(off+length)}',s,'']);off+=length
    cursor+=duration
    print(f'{c["number"]}/{len(chapters)} rendered: {c["title"]}',flush=True)
(ROOT/'chapters.json').write_text(json.dumps(chapters,ensure_ascii=False,indent=2),encoding='utf-8')
(ROOT/'legendas.vtt').write_text('\n'.join(vtt),encoding='utf-8')
(ROOT/'segments/list.txt').write_text('\n'.join(f"file '{c['id']}.mp4'" for c in chapters),encoding='utf-8')
meta=[';FFMETADATA1','title=Anime Mining Simulator - Apresentação da UI','comment=Apresentação narrada com capturas reais e prévias visuais identificadas.']
for c in chapters:
    meta.extend(['[CHAPTER]','TIMEBASE=1/1000',f'START={round(c["start"]*1000)}',f'END={round(c["end"]*1000)}',f'title={c["title"]}'])
(ROOT/'metadata.txt').write_text('\n'.join(meta),encoding='utf-8')
run(['-f','concat','-safe','0','-i','segments/list.txt','-i','metadata.txt','-map_metadata','1','-map_chapters','1','-c','copy','-movflags','+faststart','Apresentacao-UI.mp4'])
(ROOT/'capitulos.txt').write_text('\n'.join(f'{stamp(c["start"])}  {c["number"]:02}. {c["title"]}' for c in chapters),encoding='utf-8')
print(f'VIDEO COMPLETE: {cursor:.2f}s / {(ROOT/"Apresentacao-UI.mp4").stat().st_size/1e6:.1f} MB',flush=True)
