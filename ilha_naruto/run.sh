#!/usr/bin/env bash
# run.sh - atalhos do pipeline da ilha (bash do Git no Windows)
#   ./run.sh build [blockout]          reconstroi ilha_naruto.blend
#   ./run.sh render <pasta> [CAM...]    renderiza cameras (padrao: todas) em 1280x720 rapido
#   ./run.sh compare <pasta>            prancha referencia x render
#   ./run.sh qa                         navegacao + auditoria tecnica
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"
BL="/c/Program Files/Blender Foundation/Blender 5.2/blender.exe"
cd "$HERE"
case "$1" in
  build)   shift; "$BL" -b --factory-startup --python build_ilha.py -- "$@" 2>&1 | grep -E "BUILD|Error|Traceback|File \"|line [0-9]|il_|blockout|FALHA|AVISO" ;;
  render)  shift; OUTD="$(cd "$HERE" && mkdir -p "$1" && cd "$1" && pwd -W)"; shift
           "$BL" -b ilha_naruto.blend --python ../lobby_area/forja_mineradora/render.py -- "$OUTD" "$@" --res 1280x720 --fast 2>&1 | grep -E "RENDER|Error|Traceback"; python -c "import glob,os;from PIL import Image;[ (Image.open(p).convert(\"RGB\").save(p[:-4]+\".jpg\",quality=90), os.remove(p)) for p in glob.glob(os.path.join(r\"$OUTD\",\"CAM_*.png\"))]" ;;
  compare) python il_sheet.py compare "$2" "$2/_compare.jpg" ;;
  grid)    python il_sheet.py grid "$2" "$2/_grid.jpg" "${3:-4}" ;;
  qa)      shift; "$BL" -b ilha_naruto.blend --python il_qa.py -- "$@" 2>&1 | grep -E "OK |FAIL|TECH|COL|ROTA|MARKERS|ROTAS_EXTRA|SONDAS|LARGURA|ROTAS_MODULOS|Error|Traceback|line " ;;
esac
