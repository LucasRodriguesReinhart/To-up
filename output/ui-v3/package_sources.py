from pathlib import Path
import hashlib, json, zlib, zipfile
root=Path(__file__).resolve().parent
rows=[]
for p in sorted((root/'src').rglob('*.lua')):
    source=p.read_text(encoding='utf-8').rstrip()
    data=source.encode('utf-8')
    relative=p.relative_to(root/'src')
    old=(root/'before'/relative).read_text(encoding='utf-8').rstrip()
    rows.append(dict(path=relative.as_posix(),bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),adler32=zlib.adler32(data),changed=source!=old))
(root/'source-manifest.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')
selected=[]
for folder in ['src','before']:
    selected.extend((root/folder).rglob('*.lua'))
selected.extend(root.glob('*.md'))
selected.append(root/'source-manifest.json')
selected.extend((root/'qa').glob('*.png'))
selected.extend((root/'qa').glob('*.json'))
out=root.parent/'UIV3_Fontes_Backup_20260917.zip'
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as archive:
    for path in selected: archive.write(path,path.relative_to(root).as_posix())
print(json.dumps(dict(files=rows,archive=str(out),archiveFiles=len(selected)),indent=2))
