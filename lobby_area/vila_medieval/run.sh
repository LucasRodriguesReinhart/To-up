#!/usr/bin/env bash
# run.sh - atalhos do pipeline do lobby Vila Medieval (bash do Git no Windows). Todo Blender com --factory-startup.
#   ./run.sh build                     reconstroi lobby_vila_medieval.blend (VM_OUT=<.blend> muda a saida)
#   ./run.sh qa [nav env link markers budget tech] [--json f]   QA sobre o .blend
#   ./run.sh render <pasta> [CAM...] [--roblox]                 cameras CAM_VM_* em 960x540 (planta 960x912)
#   ./run.sh export [pasta]            FBX LOBBY_VM_*_<id>.fbx + montar_lobby_vila_medieval.lua (padrao ./export)
#   ./run.sh sheets <pasta_previa> <pasta_roblox>               folhas em renders/v0 (ref_01, planta, jogador, aereo)
#   ./run.sh all <pasta_tmp>           build + qa + renders nos 2 modos + folhas + export
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"
BL="/c/Program Files/Blender Foundation/Blender 5.2/blender.exe"
cd "$HERE"
win() { mkdir -p "$1" && (cd "$1" && pwd -W); }
case "$1" in
  build)  "$BL" -b --factory-startup --python build_vm.py 2>&1 | grep -E "BUILD|COL:|CASAS|PORTAL|VEGETACAO|Error|Traceback|line [0-9]" ;;
  qa)     shift; "$BL" -b --factory-startup lobby_vila_medieval.blend --python vm_qa.py -- "$@" 2>&1 | grep -E "ROTA|ENV|LINK|MARKERS|   |BUDGET|TECH|QA json|Error|Traceback|line [0-9]" ;;
  render) shift; OUTD="$(win "$1")"; shift
          "$BL" -b --factory-startup lobby_vila_medieval.blend --python vm_render.py -- "$OUTD" "$@" 2>&1 | grep -E "RENDER|MODO|Error|Traceback" ;;
  export) shift; "$BL" -b --factory-startup lobby_vila_medieval.blend --python export_vm.py -- "${1:-$HERE/export}" 2>&1 | grep -E "EXPORT|FBX |ORCAMENTO|METAS|ESTOUROU|FALHOU|COL:|LUZES|SEGURANCA|Error|Traceback" ;;
  sheets) mkdir -p renders/v0
          python -B vm_sheet.py ref "$2" "$3" renders/v0/FOLHA_ref01.jpg
          python -B vm_sheet.py plan "$2" renders/v0/FOLHA_planta.jpg
          python -B vm_sheet.py jogador "$2" "$3" renders/v0/FOLHA_jogador.jpg
          python -B vm_sheet.py aereo "$2" "$3" renders/v0/FOLHA_aereo.jpg ;;
  all)    T="$(win "$2")"; "$0" build; "$0" qa --json renders/v0/qa_v0.json; "$0" render "$T/prev"; "$0" render "$T/rbx" --roblox
          "$0" sheets "$T/prev" "$T/rbx"; "$0" export ;;
esac
