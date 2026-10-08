#!/usr/bin/env bash
# run.sh - atalhos do pipeline da Ilha 5 ONE PIECE / WANO (bash do Git no Windows). Todo Blender roda com
#          --factory-startup (sem os add-ons do usuario: nada de servidor MCP subindo junto)
#   ./run.sh build [blockout] [proxies]  reconstroi ilha_onepiece.blend (OP_OUT=<.blend> muda a saida)
#   ./run.sh render <pasta> [CAM...]     renderiza cameras (padrao: todas as CAM_OP_*) em 960x540 (OP_BLEND=<.blend>)
#   ./run.sh export <pasta>              export Roblox (padrao ilha_onepiece/export; teste: pasta temporaria)
#   ./run.sh qa [nav|tech|markers|clear|budget|gate]
#   ./run.sh map                         planta 2D + mundo + conferencias (plano/planta_op.png, plano/mundo_op.png)
#   ./run.sh sheet ...                   folhas (tools_sheet.py)
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"
BL="/c/Program Files/Blender Foundation/Blender 5.2/blender.exe"
cd "$HERE"
case "$1" in
  build)   shift; "$BL" -b --factory-startup --python build_op.py -- "$@" 2>&1 | grep -E "BUILD|Error|Traceback|File \"|line [0-9]|op_|AVISO|FALHA|SCENE" ;;
  render)  shift; OUTD="$(mkdir -p "$1" && cd "$1" && pwd -W)"; shift
           "$BL" -b --factory-startup "${OP_BLEND:-ilha_onepiece.blend}" --python op_render.py -- "$OUTD" "$@" 2>&1 | grep -E "RENDER|Error|Traceback" ;;
  export)  shift; "$BL" -b --factory-startup "${OP_BLEND:-ilha_onepiece.blend}" --python export_op.py -- "$@" 2>&1 | grep -E "EXPORT|CONEXAO|BUDGET|FALHOU|ESTOUROU|Error|Traceback|LUZ_OP|COL:|LUZES|SEGURANCA" ;;
  qa)      shift; "$BL" -b --factory-startup "${OP_BLEND:-ilha_onepiece.blend}" --python op_qa.py -- "$@" 2>&1 | grep -E "OK |FAIL|TECH|ROTA|MARKERS|SONDA|LARGURA|COL faces|BUDGET|GATE|AVISO|Error|Traceback|line " ;;
  map)     python op_map.py ;;
  sheet)   shift; python tools_sheet.py "$@" ;;
esac
