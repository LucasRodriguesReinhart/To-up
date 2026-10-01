#!/usr/bin/env bash
# run.sh - atalhos do pipeline da Ilha 2 (bash do Git no Windows)
#   ./run.sh build [blockout]          reconstroi ilha_dragonball.blend
#   ./run.sh render <pasta> [CAM...]    renderiza cameras (padrao: todas as CAM_DB_*) em 1280x720 rapido
#   ./run.sh qa [nav|tech|markers]      navegacao + auditoria tecnica
#   ./run.sh map                        planta 2D (renders/_mapa_planta.png)
#   ./run.sh cols                       colisoes por area (conta)
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"
BL="/c/Program Files/Blender Foundation/Blender 5.2/blender.exe"
cd "$HERE"
case "$1" in
  build)   shift; "$BL" -b --factory-startup --python build_db.py -- "$@" 2>&1 | grep -E "BUILD|Error|Traceback|File \"|line [0-9]|db_|AVISO|FALHA" ;;
  render)  shift; OUTD="$(mkdir -p "$1" && cd "$1" && pwd -W)"; shift
           "$BL" -b ilha_dragonball.blend --python ../lobby_area/forja_mineradora/render.py -- "$OUTD" "$@" --res 1280x720 --fast 2>&1 | grep -E "RENDER|Error|Traceback"
           python -c "import glob,os;from PIL import Image;[ (Image.open(p).convert('RGB').save(p[:-4]+'.jpg',quality=90), os.remove(p)) for p in glob.glob(os.path.join(r'$OUTD','CAM_*.png'))]" ;;
  qa)      shift; "$BL" -b ilha_dragonball.blend --python db_qa.py -- "$@" 2>&1 | grep -E "OK |FAIL|TECH|ROTA|MARKERS|SONDA|LARGURA|COL faces|Error|Traceback|line " ;;
  map)     python db_map.py ;;
  cols)    "$BL" -b ilha_dragonball.blend --python-expr "import bpy,collections,re;c=collections.Counter(re.sub(r'_\d+$','',o.name) for o in bpy.data.objects if o.name.startswith('COL_'));print('COLS',sum(c.values()));[print('COL',k,v) for k,v in c.most_common()]" 2>&1 | grep -E "^COL" ;;
esac
