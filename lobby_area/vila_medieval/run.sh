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
# V3a (vegetacao + props; vm_veg.py / vm_props.py, registrados no build antes da luz):
#   ./run.sh veg-report [json]         tris / materiais / extensao por objeto VM_Veg_* / VM_Prop_* + intersecao x construido
#   ./run.sh veg <pasta_tmp>           renders nos 2 modos + folhas em renders/v3/veg_props
# V3b (luz + VFX; vm_lights.py / export_vm_vfx.py - o export ja gera o VFX junto):
#   ./run.sh luz-qa [json]             luzes de dia (<= 30) / NightOnly, sol do Roblox (ClockTime/latitude), proxies
#   ./run.sh luz <pasta_tmp>           renders dia/noite/closes nos 2 modos + folhas em renders/v3/luz_vfx
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"
BL="/c/Program Files/Blender Foundation/Blender 5.2/blender.exe"
cd "$HERE"
win() { mkdir -p "$1" && (cd "$1" && pwd -W); }
case "$1" in
  build)  "$BL" -b --factory-startup --python build_vm.py 2>&1 | grep -E "BUILD|COL:|CASAS|PORTAL|VEGETACAO|TRECHO|FORJA|TOWN (dono|stats)|VEG |PROPS|V3A|   casa|   VM_|Error|Traceback|line [0-9]" ;;
  veg-report) shift; "$BL" -b --factory-startup lobby_vila_medieval.blend --python vm_veg.py -- report ${1:+"$1"} 2>&1 | grep -E "V3A|ISECT|   VM_|Error|Traceback" ;;
  veg)    T="$2"; mkdir -p "$T"; TW="$(win "$T")"
          C="CAM_VM_Plan CAM_VM_V2_Ref01 CAM_VM_V2_RuaSaida CAM_VM_V2_SpawnPraca CAM_VM_V2_PracaForja CAM_VM_V2_RuaForja CAM_VM_V2_Praca360_0 CAM_VM_V2_Praca360_1 CAM_VM_V2_Praca360_2 CAM_VM_V2_Praca360_3 CAM_VM_V2_Portais CAM_VM_V2_PortaisDentro CAM_VM_V2_Ranking CAM_VM_V2_LojaFora CAM_VM_V2_Portao CAM_VM_V2_Ponte CAM_VM_V2_Air_SE CAM_VM_V2_Air_W CAM_VM_V3_Air_Norte CAM_VM_V3_Arredor_SO CAM_VM_V3_Arredor_Loja CAM_VM_V3_Arredor_Norte CAM_VM_V3_Close_Arvore CAM_VM_V3_Close_Pinheiro CAM_VM_V3_Close_Hera CAM_VM_V3_Close_Props1 CAM_VM_V3_Close_Props2 CAM_VM_V3_Close_Placa"
          "$0" render "$T/prev" $C; "$0" render "$T/rbx" $C --roblox
          python -B vm_veg.py sheets "$T/prev" "$T/rbx" renders/v3/veg_props ;;
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
  export) shift; "$BL" -b --factory-startup lobby_vila_medieval.blend --python export_vm.py -- "${1:-$HERE/export}" 2>&1 | grep -E "EXPORT|FBX |ORCAMENTO|METAS|ESTOUROU|FALHOU|COL:|LUZES|SEGURANCA|export_vm_vfx|Error|Traceback" ;;
  luz-qa) shift; "$BL" -b --factory-startup lobby_vila_medieval.blend --python vm_lights.py -- qa ${1:+"$1"} 2>&1 | grep -E "LUZES|Error|Traceback" ;;
  luz)    T="$2"; mkdir -p "$T"; TW="$(win "$T")"
          R() { "$BL" -b --factory-startup lobby_vila_medieval.blend --python vm_lights.py -- render "$@" 2>&1 | grep -E "RENDER|MODO|PILAO|Error|Traceback"; }
          for m in prev rbx; do f=""; [ $m = rbx ] && f="--roblox"
            R "$TW/dia_$m" CAM_VM_P_Spawn CAM_VM_P_Praca CAM_VM_P_Rua CAM_VM_P_Forja CAM_VM_Ref_01 --vfx $f
            R "$TW/noite_$m" CAM_VM_L_NoiteRua CAM_VM_L_NoitePraca CAM_VM_L_NoiteCurva CAM_VM_P_Spawn --vfx --noite $f
            R "$TW/closes_$m" CAM_VM_L_Boca CAM_VM_L_Roda CAM_VM_L_Pilao CAM_VM_L_Chamine --vfx --sem-golem $f
            R "$TW/alto_$m" CAM_VM_L_Pilao --vfx --pilao-alto --sem-golem $f
            cp "$T/alto_$m/CAM_VM_L_Pilao.jpg" "$T/closes_$m/CAM_VM_L_Pilao_ALTO.jpg"; done
          python -B vm_lights.py sheet "$T/dia_prev" "$T/dia_rbx" "$T/noite_prev" "$T/noite_rbx" "$T/closes_prev" "$T/closes_rbx" renders/v3/luz_vfx ;;
  sheets) mkdir -p renders/v0
          python -B vm_sheet.py ref "$2" "$3" renders/v0/FOLHA_ref01.jpg
          python -B vm_sheet.py plan "$2" renders/v0/FOLHA_planta.jpg
          python -B vm_sheet.py jogador "$2" "$3" renders/v0/FOLHA_jogador.jpg
          python -B vm_sheet.py aereo "$2" "$3" renders/v0/FOLHA_aereo.jpg ;;
  all)    T="$(win "$2")"; "$0" build; "$0" qa --json renders/v0/qa_v0.json; "$0" render "$T/prev"; "$0" render "$T/rbx" --roblox
          "$0" sheets "$T/prev" "$T/rbx"; "$0" export ;;
esac
