#!/usr/bin/env bash
# run.sh - atalhos do pipeline do lobby Vila Medieval (bash do Git no Windows). Todo Blender com --factory-startup.
#   ./run.sh build                     reconstroi lobby_vila_medieval.blend (VM_OUT=<.blend> muda a saida)
#   ./run.sh qa [nav env link markers budget tech] [--json f]   QA sobre o .blend
#   ./run.sh render <pasta> [CAM...] [--roblox]                 cameras CAM_VM_* em 960x540 (planta 960x912)
#   ./run.sh export [pasta]            FBX LOBBY_VM_*_<id>.fbx + montar_lobby_vila_medieval.lua (padrao ./export)
#   ./run.sh sheets <pasta_previa> <pasta_roblox>               folhas em renders/v0 (ref_01, planta, jogador, aereo)
#   ./run.sh all <pasta_tmp>           build + qa + renders nos 2 modos + folhas + export
# V1 (trecho praca -> ponte + kit; vm_kit.py / vm_trecho.py):
#   ./run.sh trecho-export [pasta]     SO o trecho -> VM_TRECHO_*_<id>.fbx + montar_vm_trecho.lua (padrao ./export_trecho)
#   ./run.sh trecho-report [json]      orcamento por casa (materiais / MeshParts / tris) + estimativa lod=1
#   ./run.sh trecho-zfight [json]      faces paralelas < 0,12 de materiais distintos, expostas (candidatas a z-fight)
#   ./run.sh studio <pasta> [--roblox] estudio do kit (presets + pecas com boneco 5,2), renders 960x540
#   ./run.sh sheets1 <prev> <rbx> <studio_prev> <studio_rbx>   folhas em renders/v1
# V2b (a vila; vm_town.py):
#   ./run.sh town-report [json]        tris / materiais por objeto e por dono da vila (casas, praca, ruas, loja...)
#   ./run.sh sheets2 <prev> <rbx>      folhas em renders/v2/vila (aerea x planta, spawn->forja, praca 360, loja...)
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"
BL="/c/Program Files/Blender Foundation/Blender 5.2/blender.exe"
cd "$HERE"
win() { mkdir -p "$1" && (cd "$1" && pwd -W); }
case "$1" in
  build)  "$BL" -b --factory-startup --python build_vm.py 2>&1 | grep -E "BUILD|COL:|CASAS|PORTAL|VEGETACAO|TRECHO|FORJA|TOWN (dono|stats)|   casa|   VM_|Error|Traceback|line [0-9]" ;;
  town-report) shift; "$BL" -b --factory-startup lobby_vila_medieval.blend --python vm_town.py -- report ${1:+"$1"} 2>&1 | grep -E "TOWN|   VM_|Error|Traceback" ;;
  sheets2) python -B vm_sheet.py v2vila "$2" "$3" renders/v2/vila ;;
  trecho-export) shift; OUTX="${1:-$HERE/export_trecho}"
          "$BL" -b --factory-startup lobby_vila_medieval.blend --python vm_trecho.py -- export "$OUTX" 2>&1 | grep -E "EXPORT|FBX |ORCAMENTO|COL:|LUZES|Error|Traceback" ;;
  trecho-report) shift; "$BL" -b --factory-startup lobby_vila_medieval.blend --python vm_trecho.py -- report ${1:+"$1"} 2>&1 | grep -E "TRECHO|   casa|   VM_|Error|Traceback" ;;
  trecho-zfight) shift; "$BL" -b --factory-startup lobby_vila_medieval.blend --python vm_trecho.py -- zfight ${1:+"$1"} 2>&1 | grep -E "ZFIGHT|studs2|Error|Traceback" ;;
  studio) shift; OUTD="$(win "$1")"; shift
          "$BL" -b --factory-startup --python vm_kit.py -- studio "$OUTD" "$@" 2>&1 | grep -E "STUDIO|RENDER|MODO|Error|Traceback" ;;
  sheets1) mkdir -p renders/v1
          python -B vm_sheet.py v1jogador "$2" "$3" renders/v1/FOLHA_trecho_jogador.jpg
          python -B vm_sheet.py v1ref "$2" "$3" renders/v1/FOLHA_ref01.jpg
          python -B vm_sheet.py v1closes "$3" renders/v1/FOLHA_closes_roblox.jpg ROBLOX
          python -B vm_sheet.py v1closes "$2" renders/v1/FOLHA_closes_previa.jpg PREVIA
          python -B vm_sheet.py v1medal "$3" renders/v1/FOLHA_medalhao.jpg
          python -B vm_sheet.py v1kit "$5" renders/v1/FOLHA_kit_roblox.jpg ROBLOX
          python -B vm_sheet.py v1kit "$4" renders/v1/FOLHA_kit_previa.jpg PREVIA ;;
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
