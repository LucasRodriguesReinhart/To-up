from pathlib import Path
import json, zipfile
ROOT=Path(__file__).resolve().parent
chapters=json.loads((ROOT/'chapters.json').read_text(encoding='utf-8'))
assert all('start' in c for c in chapters),'Render video first for exact chapter timings'
template=(ROOT/'questionario.template.html').read_text(encoding='utf-8')
(ROOT/'Questionario-UI.html').write_text(template.replace('__CHAPTERS__',json.dumps(chapters,ensure_ascii=False).replace('</','<\\/')),encoding='utf-8')
readme='''APRESENTAÇÃO E QUESTIONÁRIO — ANIME MINING SIMULATOR

1. Abra Questionario-UI.html no navegador.
2. Assista ao vídeo ou escolha um dos 28 capítulos.
3. Avalie as telas que quiser: Manter, Ajustar ou Refazer.
4. Marque o que mudaria e deixe um comentário por tela.
5. Clique em Baixar respostas e envie o arquivo nesta conversa.

As respostas ficam no navegador. Nada é enviado automaticamente.
Ao usar o arquivo HTML local, mantenha o vídeo e a pasta captures juntos.
Alguns navegadores bloqueiam legendas externas em arquivos locais; o vídeo possui narração em português e títulos visíveis.

O vídeo é uma apresentação editada de capturas reais da UI atual do Roblox Studio, com narração sintética em português. Não é uma gravação contínua de gameplay.
As telas de transição, avisos, conquista e revelação são prévias visuais identificadas, sem concessão de recompensas.
Nenhuma compra, invocação, alimentação, venda ou retirada de recompensa foi realizada para montar a apresentação.
Os scripts temporários de demonstração foram removidos. Studio voltou ao modo Edit.
'''
(ROOT/'LEIA-ME.txt').write_text(readme,encoding='utf-8')
files=['Questionario-UI.html','Apresentacao-UI.mp4','legendas.vtt','chapters.json','capitulos.txt','LEIA-ME.txt']+[c['image'] for c in chapters]
archive=ROOT.parent/'Apresentacao-e-Questionario-UI.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=3) as z:
    for f in files:z.write(ROOT/f,arcname=f)
print(f'Questionnaire ready, {len(chapters)} screens. ZIP: {archive.stat().st_size/1e6:.1f} MB')
