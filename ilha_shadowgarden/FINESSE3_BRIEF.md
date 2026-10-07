# Onda FINESSE 3 (2026-10-05): oito agentes, um por arquivo

Continuam valendo `AGENT_BRIEF.md`, `ACABAMENTO_BRIEF.md` e `ACABAMENTO2_BRIEF.md` (planta travada, marcadores, rotas,
salão livre, dungeon limpa, orçamentos, elegância escura, sem "visual de IA"). A lista de problemas é a
**`AUDITORIA3.md`** (151 itens, 38 críticos): corrija TODOS os itens do seu arquivo, na ordem crítico → Tier A → B → C,
e procure o que a auditoria não viu. A pergunta de cada item é **"está realmente bom de perto, na altura do jogador,
no Roblox sem textura?"**.

Já feito antes desta onda (não refazer): **P** (paleta com escala de valor em `sg_lib.SMATS`, `plan_stair` com pedras,
focinho, espelho escuro e juntas desencontradas: itens 15.02, 15.04, 15.05, 03.03-materiais, 16.03, 01.02, 03.04) e
**L** (luz no jogo: 15.01, 09.01-jogo, 10.11). Use a paleta nova: o chão andável (`Stone_Paving_SG`) é claro e quente,
muro (`Stone_SG_Block`) médio frio, castelo (`Stone_SG_Castle`) médio-escuro, remate (`Stone_SG_Trim` / `_TrimLow`)
o mais claro, junta (`Stone_SG_Floor`) escura. Degrau: chame `sg_lib.plan_stair` (já certo) ou copie a linguagem dele
(pedras em módulos irregulares, focinho 0,12 chanfrado, espelho recuado 0,12 um tom abaixo, junta 0,14).

## Agentes desta onda (arquivos que NÃO se cruzam)

| Agente | Arquivo (só este) | Itens da AUDITORIA3 |
|---|---|---|
| **T** terreno | `sg_terrain.py` | 01.01 (EntryHigh em lajes), 02.01 (chão do P1), 03.05, 02.06, 06.09, 14.01, 14.02, 14.03, 16.08 (rodapé), 01.11 (meio-fio) |
| **E** entrada | `sg_entry.py` | 01.03 a 01.10 |
| **V** vila | `sg_village.py` | 02.02 a 02.04, 03.02 (ruas sem faixa), 03.08 a 03.12, 03.16, 14.04 |
| **I** interiores | `sg_village_int.py` | 03.13, 04.01 a 04.11 |
| **K** castelo | `sg_castle.py` | 05.05 a 05.08, 06.01, 06.02, 06.04 a 06.07, 06.10 a 06.13 |
| **H** salão | `sg_hall.py` | 06.06 (piso do salão), 07.01 a 07.10, 08.01 a 08.03, 08.05 |
| **C** Salão Sombrio | `sg_cave.py` | 08.04, 08.06, 09.01 (material e luzes), 09.02 a 09.09, 09.11 a 09.14, 15.07 |
| **D** masmorra | `sg_dungeon.py` | 10.01 a 10.10 |

Depois desta onda (não é seu trabalho; não invada): J pátio/estátuas (`sg_court.py`), G vegetação, A alquimia,
S invocação, X saída, R props e vida nas ruas, W água.

**Cuidados entre agentes (da auditoria):**
- T × V no chão do P1: T emite o chão (lajes ou grama com borda); V NÃO pavimenta fora de praça e ruas.
- I × V na fresta das casas (03.13): fica com I (forro e piso). V não mexe no `socle`.
- V × J na estátua da fonte (02.03): J (próxima onda) cria a figura; V só prepara a chamada/escala e melhora a fonte.
- K × H na porta: K fica com porta, nártex e guardas na escala nova; H fica com o piso do salão.
- C cria as luzes `L_SGCave_*`; o Range no export já é tratado pelo `export_sg` (L).
- Nenhum agente edita `sg_lib.py`, `sg_layout.py`, `sg_col.py`, `sg_core.py`, `sg_scene.py`, `build_sg.py`,
  `studio_sg.py`, `sg_qa.py`, `export_sg.py`, `fm_lib.py`, `fm_parts.py`, kits do lobby ou módulos de outro agente.
  Precisa de algo compartilhado? Escreva o pedido em `requests` no relatório e siga com o que dá para fazer no seu
  arquivo.

## Regras desta onda
- Forma antes de material: SILHUETA → PROPORÇÃO → ESTRUTURA → ENCAIXE → ESPESSURA → BEVEL → MATERIAL → DETALHE → LUZ.
- Grandes superfícies que o jogador vê (chão, paredes de 0 a 20, abóbadas, falésia) precisam ler SOZINHAS, sem textura:
  fiadas, juntas, relevo real (≥ 0,12), 2 valores (corpo × relevo). Nada de rebaixo raso que some no Roblox.
- Variação DIRIGIDA (módulos irregulares, ritmo), nunca aleatória.
- Emissivo: só onde a magia tem função. Neon claro vira branco com o bloom: use Neon médio/escuro. Luz quente só dentro
  de moldura (janela, lanterna), nunca um bloco inteiro.
- Menos e melhor: se algo piora a composição, remova.
- Orçamento: `studio_sg.BUDGET` da zona (tris, MeshParts, materiais novos, colisões, luzes). Total da ilha ≤ 870k
  tris / 870 MeshParts (hoje 856k). Ganhe por forma, bevel e material; onde entrar geometria, tire de outro lugar do seu
  arquivo. Geometria de hero só em Tier A.
- Determinístico, sem `bpy.ops`, build da zona abaixo de 20 s. Nomes `SG_<Zona>_<Coisa>` únicos.
- Colisão: só dos seus volumes (`col_box`, `col_box2`, `octo_col`, `ngon_col`, `box_walls_col`), caixas simples. Nada
  colidível dentro de `MINE_RECT` entre piso+0,3 e piso+12. Nada que bloqueie rota.
- Não faça `git commit` nem `git push`. Não edite o `.blend` da raiz à mão (o build regenera).

## Ambiente desta sessão (Linux, sem Blender instalado: módulo `bpy` 5.0 em venv; render EEVEE por software)
Variáveis que TODO comando de render precisa (exporte no início de cada shell):
```
export LIBGL_ALWAYS_SOFTWARE=1 EGL_PLATFORM=surfaceless GALLIUM_DRIVER=llvmpipe
BPY=/tmp/claude-0/-home-user-To-up/1f4fd017-283e-51a6-a93d-09fc804c759b/scratchpad/bpy5env/bin/python
RUN=/tmp/claude-0/-home-user-To-up/1f4fd017-283e-51a6-a93d-09fc804c759b/scratchpad/qa_run.py
cd /home/user/To-up/ilha_shadowgarden
```
- **Estúdio da sua zona** (build da zona em detalhe + vizinhos, métricas, rotas, render das câmeras):
  `$BPY studio_sg.py -- <zona> /home/user/To-up/ilha_shadowgarden/renders/finesse3/<AGENTE>/depois --all-detail --cams CAM_A,CAM_B --res 960x540 --samples 8`
  Zonas: `terrain entry village castle hall cave dungeon` (I usa `village`). O render por software é LENTO (minutos
  por câmera): peça poucas câmeras por vez (3 a 6), nunca "todas". Use `--no-render` para só medir.
  Com `FM_MAT_PREVIEW=roblox` na frente do comando, o render mostra a cor que o Roblox recebe (sem textura, Neon
  brilhando): a folha final precisa dos DOIS modos.
- **Câmeras:** as `CAM_SG_*` da zona (`studio_sg.ZONE_CAMS`), as `CAM_A3_*` da auditoria (ver `sg_scene.a3_cams()`:
  o nome do arquivo da auditoria é a câmera sem `CAM_A3_`) e as `CAMS` do seu módulo. As `CAM_A3_*` só existem se o
  studio as criar: se faltarem, adicione as que precisar ao dicionário `CAMS` do SEU módulo (mesma convenção
  `(loc, alvo, lente)`, olho a 5,5 acima do piso nas vistas de jogador).
- **ANTES:** os renders da auditoria em `renders/auditoria3/previa/` e `.../roblox/` já são o ANTES. Não refaça.
- **Folha antes/depois:** `python3 tools_sheet.py <antes> <depois> renders/finesse3/<AGENTE>/folha.jpg CAM_A,CAM_B "ANTES" "DEPOIS"`
  (as imagens precisam ter o mesmo nome nas duas pastas; renomeie cópias se preciso).
- **Veja as imagens com Read** e itere. Avalie a imagem DEPOIS isolada: ainda parece blockout? Então não acabou.
- **Build completo + QA (no fim, obrigatório):**
  `$BPY build_sg.py 2>&1 | grep -E "BUILD|Error|Traceback|File \"|line [0-9]|AVISO|FALHA"` (≈ 80 s; precisa terminar
  em `BUILD OK`), depois `$BPY $RUN $PWD/ilha_shadowgarden.blend $PWD/sg_qa.py 2>&1 | grep -E "ROTAS|SONDAS|SALAO|DUNGEON|FAIL|TECH|MARKERS"`
  (tudo OK; baseline: ROTAS_MODULOS 46/46, SONDAS 29/29).
- São 8 agentes na mesma máquina de 4 núcleos: renderize com parcimônia (poucas câmeras, 960×540, 8 samples) e não
  rode dois studios seus ao mesmo tempo.

## Relatório final (no chat, curto)
1. Itens resolvidos (número da auditoria → o que mudou, função), itens não resolvidos e por quê.
2. Métricas da zona ANTES → DEPOIS (tris, MeshParts, materiais novos, colisões, luzes) e BUILD OK + QA.
3. Caminho da folha antes/depois e das pastas de render.
4. `requests`: o que precisa de arquivo compartilhado ou de outro agente.

## Fechamento da onda (2026-10-06)

Os 8 agentes concluíram. Build completo OK com 869.129 tris (teto 870k), 1663 colisões, 2183 objetos.
QA: ROTAS 27/27, ROTAS_ABERTAS 3/3, ROTAS_MODULOS 46/46, SONDAS 29/29, SALAO_LIVRE, DUNGEON_LIMPA, CAVE_LIVRE e TECH OK.
Folhas antes/depois (prévia e roblox) em `renders/finesse3/<AGENTE>/folha*.jpg`.

| Zona | Tris / orçamento | Itens parciais |
|---|---|---|
| terrain | 69.654 / 72.000 | 14.01 (quilha limitada pelo subsolo) |
| entry | 39.812 / 40.000 | 01.10 sem bevel nas lajes (orçamento) |
| village (V + I) | 109.948 / 110.000 | 02.02 (taças presas às cotas da água), 02.03 (figura com J), 14.04 (campanário não cabe) |
| castle | 169.944 / 170.000 | 06.13 confirmar no Play |
| hall | 87.926 / 88.000 | 08.05 bolso aberto não revisado (studio não move o trono) |
| cave | 69.858 / 70.000 | 09.14 cristais sem luz própria (teto de 6 luzes) |
| dungeon | 77.906 / 78.000 | — |

Todas as zonas desta onda estão no teto: a próxima onda não tem folga nelas.

### Pendências para as próximas ondas
- **J (`sg_court.py`):**
  - figura própria da fonte em `sg_village.fountain_figure(mb, F, s, z0)` (s 0,88, ~6,4 de altura, tom claro, ≤ 2k tris);
  - figura dos guardas na escala 1,5 (`hooded_figure(..., kind="guard")`, ~11 de altura, seções de mais lados);
  - tirar `statue()` dos pontos `STATUES` (±21; 34,5), que duplica os guardas no eixo;
  - tirar o fio Neon do caminho nobre (05.01).
- **G (vegetação):**
  - floreiras da vila ficaram VAZIAS depois da troca das trepadeiras (H2, H7 e outras): plantar ou remover as caixas;
  - touceiras contra os parapeitos (01.11), trepadeiras só nos tramos centrais do arrimo (03.05);
  - sebes e trepadeiras no pé da muralha e da fachada cobrem a arcada nova do castelo.
- **R (props):** pilha de lenha e banco nos panos laterais (03.09), forja de mão sob o alpendre do H2, quintais (03.01).
- **Coordenação / arquivos compartilhados:**
  - `studio_sg`: modo que põe `SG_Hall_ThroneMov` no `THRONE_Park` antes do render; ler o `CAMS` dos submódulos (`sg_village_int`) e criar as `CAM_A3_*` sem cópia nos módulos;
  - decidir teto de luzes da zona cave (6 → 8 para os cristais);
  - opcional: `Stone_SGEntPave` como alias sem variante de `Stone_Paving_SG`; `Window_Warm_SG` em `sg_lib`; `flame()` do `sg_cave` como chama do kit.
- **Conferir no Play:**
  - fresta de luz na base das casas (no Roblox a PointLight não faz sombra);
  - vão do portão da muralha (06.13);
  - escuridão do salão (`Stone_SG_MarbleBlack` pode precisar clarear em `sg_lib`).
