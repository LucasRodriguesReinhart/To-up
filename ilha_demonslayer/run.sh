#!/usr/bin/env bash
# run.sh - atalhos do pipeline da Ilha 4 (bash do Git no Windows). Todo Blender roda com --factory-startup (sem os
#          add-ons do usuario: nada de servidor MCP subindo junto)
#   ./run.sh build [blockout] [proxies]  reconstroi ilha_demonslayer.blend
#   ./run.sh render <pasta> [CAM...]     renderiza cameras (padrao: todas as CAM_DS_*) em 1280x720 (DS_BLEND=<.blend>)
#   ./run.sh export <pasta>              export Roblox (padrao ilha_demonslayer/export; teste: pasta temporaria)
#   ./run.sh qa [nav|tech|markers|clear|budget|gate]
#   ./run.sh map                         planta 2D + conferencias (renders/onda0/_mapa_planta.png)
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"
BL="/c/Program Files/Blender Foundation/Blender 5.2/blender.exe"
cd "$HERE"
case "$1" in
  build)   shift; "$BL" -b --factory-startup --python build_ds.py -- "$@" 2>&1 | grep -E "BUILD|Error|Traceback|File \"|line [0-9]|ds_|AVISO|FALHA|SCENE" ;;
  render)  shift; OUTD="$(mkdir -p "$1" && cd "$1" && pwd -W)"; shift
           "$BL" -b --factory-startup "${DS_BLEND:-ilha_demonslayer.blend}" --python ds_render.py -- "$OUTD" "$@" 2>&1 | grep -E "RENDER|Error|Traceback" ;;
  export)  shift; "$BL" -b --factory-startup ilha_demonslayer.blend --python export_ds.py -- "$@" 2>&1 | grep -E "EXPORT|CONEXAO|BUDGET|FALHOU|ESTOUROU|Error|Traceback|LUZ_DS|COL:|LUZES|SEGURANCA" ;;
  qa)      shift; "$BL" -b --factory-startup ilha_demonslayer.blend --python ds_qa.py -- "$@" 2>&1 | grep -E "OK |FAIL|TECH|ROTA|ZF|MARKERS|SONDA|LARGURA|COL faces|BUDGET|GATE|AVISO|Error|Traceback|line " ;;
  map)     python ds_map.py ;;
esac
