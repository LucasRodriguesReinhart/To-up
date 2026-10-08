# Ilha 5 Wano: brief da onda M6b (finesse)

## Base
- Fonte dos itens: `renders/m6/AUDITORIA_OP.md` (51 itens: 14 P, 37 L), com evidencias em `renders/m6/aud/` e a planta numerada `aud/A00_planta_itens.jpg`.
- `OP_BRIEF.md` continua valendo inteiro. O que vale e o Roblox: sem textura, bloom diurno, altura do jogador, `FM_MAT_PREVIEW=roblox`.

## Regras desta onda
- **Escopo:** so os itens do seu grupo, so nos arquivos do seu grupo. Todo P e obrigatorio; faca os L que couberem. Item de outro grupo: descreva no relatorio.
- **Nao mude** planta, cotas, rotas, marcadores nem colisoes de rota (exceto o item 36: piso invisivel no porto). QA: 15/15 rotas, PRACA_LIVRE/PISO OK.
- **Orcamento:** a ilha esta em ~615k de 640k / 503 de 650 MeshParts / col 1208 de 1300. Cada grupo pode crescer no maximo +5k tris (pague com cortes onde nao se ve).
- **Z-fight:** nenhuma face exposta a menos de 0,12 de outra de material diferente.
- **Builds de teste:** `OP_OUT=<scratchpad>/op_fin_<sigla>/teste.blend` — NUNCA sem OP_OUT (3 agentes ja sobrescreveram o oficial por engano). Build oficial so no fim; se outro agente estiver no meio de um, espere. Deterministico.
- **Proibido:** Roblox Studio MCP, Blender MCP ao vivo, computer-use, browser, commit, taskkill; mexer em `..\ilha_*` de outras ilhas, `fm_lib.py`, `export_roblox.py`; modelar minerios. O portao OPM (galeria) nao se redesenha.

## Entrega
- Minimo 3 voltas render → critica → correcao, nos 2 modos.
- Folhas em `renders/m6/fin_<sigla>/`, antes × depois de cada item com as MESMAS cameras da auditoria (runners em `scratchpad/op_aud/`).
- QA: build completo + `./run.sh qa` OK.
- Relatorio curto: item a item (feito / parcial / nao feito e por que), orcamento, pendencias.
